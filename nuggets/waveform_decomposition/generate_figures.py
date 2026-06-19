"""Generate static figures for the waveform-decomposition nugget.

Produces:
    figures/synthetic_decomposition.png    — recovery on a known synthetic signal
    figures/synthetic_pattern_windows.png  — residual windows + pattern averaging
    figures/pkctrl3_block_comparison.png   — bar chart of SNDR / SDR / SNR

The pkctrl3-derived plots (`pkctrl3_from_symbols_*`, `pkctrl3_per_block_*`)
are produced directly by ``examples/waveform_decomposition_demo.py`` in the
optical-serdes repo and copied in from
``runs/pkctrl3_waveform_decomposition/``.

Run with the optical-serdes venv active (which provides plotly + kaleido)::

    cd /home/patrick/optical-serdes && source .venv/bin/activate
    python /home/patrick/mydocs/nuggets/waveform_decomposition/generate_figures.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from optical_serdes.analysis import decompose_waveform
from optical_serdes.analysis.waveform_decomposition import _pattern_average_distortion
from optical_serdes.channel.electrical import skin_dielectric_channel_ir
from optical_serdes.tx.waveform import generate_prbs

OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SYNTHETIC_LINEAR_MODE: Literal["wiener", "exact"] = "exact"

# Synthetic channel loss budget (dB at the baud Nyquist) for the causal
# skin-effect + dielectric-loss pulse.  See
# ``optical_serdes.channel.electrical.skin_dielectric_channel_ir``.
SYNTHETIC_SKIN_LOSS_DB = 4.0
SYNTHETIC_DIELECTRIC_LOSS_DB = 2.0


# ─────────────────────────────────────────────────────────────────────────────
# Figure 1 — synthetic recovery on a known signal
# ─────────────────────────────────────────────────────────────────────────────


def _synthesise(
    n_sym: int = 6000,
    sps: int = 8,
    distortion_gain: float = 1.1,
    noise_sigma: float = 0.02,
    seed: int = 7,
    pulse_span_ui: int = 8,
    prbs_order: int = 13,
    skin_loss_db: float = SYNTHETIC_SKIN_LOSS_DB,
    dielectric_loss_db: float = SYNTHETIC_DIELECTRIC_LOSS_DB,
    source: Literal["prbs", "iid"] = "prbs",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build a synthetic waveform with a known LTI + distortion + noise split."""
    rng = np.random.default_rng(seed)
    if source == "iid":
        # IID random ±1 symbols: no finite source state (entropy order N → ∞),
        # so the only route to a noise-floor collapse is "cover the memory".
        symbols = rng.choice([-1.0, 1.0], size=n_sym).astype(np.float64)
    elif source == "prbs":
        # Deterministic PRBS source sequence with requested length/order.
        prbs_bits = generate_prbs(order=int(prbs_order), n_bits=n_sym)
        symbols = (2.0 * prbs_bits.astype(np.float64)) - 1.0
    else:
        raise ValueError(f"Unsupported source={source!r}; use 'prbs' or 'iid'.")

    # Causal skin-effect + dielectric-loss electrical channel.  A symmetric
    # linear-phase FIR (sinc/raised-cosine) rings and never settles for a long
    # run of identical symbols (Gibbs-type ripple), which is non-physical for a
    # dissipative electrical link.  Instead we synthesise the minimum-phase
    # impulse response of a skin-effect (∝√f) + dielectric-loss (∝f) channel:
    # it is one-sided (no pre-cursor), decays monotonically, and its step
    # response settles to a flat level — i.e. it behaves like a real PCB/cable.
    channel_ir = skin_dielectric_channel_ir(
        samples_per_symbol=sps,
        n_ui_span=float(pulse_span_ui),
        skin_loss_db=float(skin_loss_db),
        dielectric_loss_db=float(dielectric_loss_db),
    )
    # NRZ transmit waveform: upsample the symbols and apply a one-UI zero-order
    # hold (each symbol held for the full bit period), then drive the linear
    # channel filter.  This is the physical NRZ model — a dirac/impulse-train
    # drive would instead look return-to-zero.  The effective linear pulse that
    # maps one symbol to the output is the NRZ single-bit response (the channel
    # impulse response convolved with the 1-UI hold); we return it as `pulse`
    # so the exact-baseline reconstruction conv(dirac(symbols), pulse)
    # reproduces y exactly.
    channel_h = np.asarray(channel_ir.h, dtype=np.float64)
    nrz_hold = np.ones(sps, dtype=np.float64)
    single_bit_response = np.convolve(channel_h, nrz_hold)
    pulse_norm = float(np.max(np.abs(single_bit_response)))
    pulse = single_bit_response / pulse_norm

    x_nrz = np.repeat(symbols, sps)
    y_linear = np.convolve(x_nrz, channel_h)[: len(x_nrz)] / pulse_norm
    if abs(distortion_gain) < 1e-12:
        y_nonlinear = y_linear.copy()
    else:
        y_nonlinear = np.tanh(distortion_gain * y_linear) / np.tanh(distortion_gain)
    distortion_true = y_nonlinear - y_linear
    noise_true = rng.normal(0.0, noise_sigma, size=len(y_nonlinear))
    y = y_nonlinear + noise_true
    return symbols, y, distortion_true, noise_true, pulse


def figure_synthetic_recovery(
    *,
    linear_mode: Literal["wiener", "exact"] = SYNTHETIC_LINEAR_MODE,
) -> None:
    """Plot synthetic decomposition using either Wiener or exact linear baseline."""
    if linear_mode not in {"wiener", "exact"}:
        raise ValueError(f"Unsupported linear_mode={linear_mode!r}; use 'wiener' or 'exact'.")

    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    ir_plot_ui = 3
    n_pre = ir_ui
    n_post = ir_ui
    pattern_n_pre = 2
    pattern_n_post = 2
    pattern_min_hits = 4
    guard_ui = 20
    symbols, y, dist_true, noise_true, pulse_true = _synthesise(
        n_sym=n_sym,
        sps=sps,
        pulse_span_ui=2 * ir_ui,
        distortion_gain=0.15,
        noise_sigma=0.0,
    )
    decomp = decompose_waveform(
        y,
        symbols,
        sps=sps,
        n_pre=n_pre,
        n_post=n_post,
        pattern_n_pre=pattern_n_pre,
        pattern_n_post=pattern_n_post,
        pattern_min_hits=pattern_min_hits,
        guard_ui=guard_ui,
    )

    def _align_truth_trace(
        trace: np.ndarray,
        *,
        lag_samples: int,
        n_out: int,
    ) -> np.ndarray:
        """Align a synthetic ground-truth trace to decomp.y_aligned timeline."""
        if lag_samples < 0:
            raise ValueError("Negative lag is not supported for synthetic truth alignment.")
        out = np.zeros(n_out, dtype=np.float64)
        if lag_samples >= len(trace):
            return out
        n_copy = min(len(trace) - lag_samples, n_out)
        out[:n_copy] = trace[lag_samples : lag_samples + n_copy]
        return out

    # Compare planted synthetic pulse vs recovered Wiener filter.
    h_est = decomp.channel_estimate.h_win * decomp.channel_estimate.norm
    cursor = n_pre * sps
    h_true = np.zeros_like(h_est)
    n_copy = min(len(pulse_true), len(h_true) - cursor)
    h_true[cursor : cursor + n_copy] = pulse_true[:n_copy]

    # Align planted pulse to the estimated filter by max correlation lag
    # (no wrap-around). Keep both traces in raw amplitude units so the
    # overlay and delta panels reflect the same unnormalized quantities.
    corr = np.correlate(h_est, h_true, mode="full")
    lag = int(np.argmax(np.abs(corr)) - (len(h_true) - 1))
    h_true_aligned = np.zeros_like(h_true)
    if lag >= 0:
        src = h_true[: len(h_true) - lag]
        h_true_aligned[lag : lag + len(src)] = src
    else:
        src = h_true[-lag:]
        h_true_aligned[: len(src)] = src

    h_true_plot = h_true_aligned
    ir_sl = slice(cursor - ir_plot_ui * sps, cursor + ir_plot_ui * sps + 1)
    h_t_ui = ((np.arange(ir_sl.stop - ir_sl.start) + ir_sl.start - cursor) / sps).tolist()

    g = 200 * sps
    plot_len = 120 * sps
    sl = slice(g, g + plot_len)
    t_ui = (np.arange(plot_len) / sps).tolist()

    lag_samples = int(decomp.channel_estimate.lag_samples)
    dist_true_aligned = _align_truth_trace(
        dist_true,
        lag_samples=lag_samples,
        n_out=len(decomp.y_aligned),
    )
    noise_true_aligned = _align_truth_trace(
        noise_true,
        lag_samples=lag_samples,
        n_out=len(decomp.y_aligned),
    )
    # Exact-linear experiment: use the planted Bessel pulse to construct y_hat,
    # then run the same residual pattern-averaging decomposition.
    x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
    x_dirac[::sps] = symbols
    y_linear_true = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
    y_hat_exact = _align_truth_trace(
        y_linear_true,
        lag_samples=lag_samples,
        n_out=len(decomp.y_aligned),
    )
    residual_exact = decomp.y_aligned - y_hat_exact
    symbol_cursor = int(decomp.channel_estimate.cursor)
    y_distortion_exact, _, _, _ = _pattern_average_distortion(
        residual_exact,
        np.asarray(symbols, dtype=np.float64),
        sps=sps,
        cursor_phase=int(symbol_cursor) % sps,
        cursor_ui_offset=int(symbol_cursor) // sps,
        pattern_n_pre=pattern_n_pre,
        pattern_n_post=pattern_n_post,
        pattern_min_hits=pattern_min_hits,
    )
    y_noise_exact = residual_exact - y_distortion_exact

    if linear_mode == "exact":
        y_hat_plot = y_hat_exact
        y_dist_plot = y_distortion_exact
        y_noise_plot = y_noise_exact
        h_ref_plot = h_true_aligned.copy()
        h_ref_name = "h_exact (forced)"
        h_delta_name = "Δh = h_true - h_exact"
        y_hat_name = "ŷ_exact (planted Bessel)"
        row2_title = "Linear filter check:  h_true vs h_exact (forced equal, raw units)"
    else:
        y_hat_plot = decomp.y_hat
        y_dist_plot = decomp.y_distortion
        y_noise_plot = decomp.y_noise
        h_ref_plot = h_est
        h_ref_name = "h_est (Wiener)"
        h_delta_name = "Δh = h_true - h_est"
        y_hat_name = "ŷ (linear fit, Wiener)"
        row2_title = "Linear filter check:  h_true vs h_est (Wiener, raw units)"

    h_delta_arr = h_true_plot[ir_sl] - h_ref_plot[ir_sl]
    delta_rms = float(np.sqrt(np.mean(h_delta_arr**2)))

    # Estimation errors and recovered-component distributions, measured over the
    # guard-trimmed interior (same convention as the SNDR/SDR/SNR metrics).
    # Note d̂ + n̂ = residual = d_true + n_true exactly, so the distortion-
    # estimate error is the exact negative of the noise-estimate error.
    n_al = len(decomp.y_aligned)
    g_hist = guard_ui * sps
    region = slice(g_hist, n_al - g_hist) if 2 * g_hist < n_al else slice(0, n_al)
    d_err = y_dist_plot - dist_true_aligned
    n_err = y_noise_plot - noise_true_aligned
    d_err_rms = float(np.sqrt(np.mean(d_err[region] ** 2)))
    n_err_rms = float(np.sqrt(np.mean(n_err[region] ** 2)))
    d_hist = y_dist_plot[region]
    n_hist = y_noise_plot[region]

    # Metrics consistent with the *plotted* baseline (exact or Wiener), so the
    # title matches the panels rather than always reporting the internal Wiener
    # decomposition stats.
    res_plot = y_dist_plot + y_noise_plot
    closure_plot = decomp.y_aligned - (y_hat_plot + y_dist_plot + y_noise_plot)
    p_y_plot = float(np.mean(decomp.y_aligned[region] ** 2))
    p_res_plot = float(np.mean(res_plot[region] ** 2))
    p_dis_plot = float(np.mean(y_dist_plot[region] ** 2))
    p_noi_plot = float(np.mean(y_noise_plot[region] ** 2))
    _db = lambda num, den: 10.0 * float(np.log10(num / den)) if den > 0.0 else float("inf")
    sndr_plot = _db(p_y_plot, p_res_plot)
    sdr_plot = _db(p_y_plot, p_dis_plot)
    snr_plot = _db(p_y_plot, p_noi_plot)
    closure_rms_plot = float(np.sqrt(np.mean(closure_plot[region] ** 2)))

    fig = make_subplots(
        rows=6,
        cols=2,
        shared_xaxes=False,
        vertical_spacing=0.05,
        horizontal_spacing=0.08,
        specs=[
            [{"colspan": 2}, None],
            [{}, {}],
            [{"colspan": 2}, None],
            [{"colspan": 2}, None],
            [{"colspan": 2}, None],
            [{}, {}],
        ],
        subplot_titles=[
            f"Captured y vs linear prediction ŷ  ({linear_mode})",
            row2_title,
            f"Linear-filter delta ({linear_mode}): RMS={delta_rms:.3e}",
            "Distortion: actual nonlinear waveform vs recovered estimate",
            "Noise:         recovered (green)   vs   true (grey)",
            f"Estimation error:  d̂−d_true (crimson) and n̂−n_true (green)  "
            f"— mirror images;  RMS={d_err_rms:.3e}",
            f"Histogram: recovered distortion d̂  (interior, std={d_hist.std():.2e})",
            f"Histogram: recovered noise n̂  (interior, std={n_hist.std():.2e})",
        ],
    )

    fig.add_trace(
        go.Scatter(x=t_ui, y=decomp.y_aligned[sl].tolist(),
                   mode="lines", name="y (measured)",
                   line={"color": "steelblue", "width": 1}),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_ui, y=y_hat_plot[sl].tolist(),
                   mode="lines", name=y_hat_name,
                   line={"color": "darkorange", "width": 1, "dash": "dash"}),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(x=h_t_ui, y=h_true_plot[ir_sl].tolist(),
                   mode="lines", name="h_true (synthetic pulse)",
                   line={"color": "black", "width": 1.4}),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(x=h_t_ui, y=h_ref_plot[ir_sl].tolist(),
                   mode="lines", name=h_ref_name,
                   line={"color": "darkorange", "width": 1.4, "dash": "dash"}),
        row=2, col=1,
    )
    fig.add_vline(x=0.0, line={"color": "gray", "width": 1.0, "dash": "dot"}, row=2, col=1)
    h_delta = h_delta_arr.tolist()
    fig.add_trace(
        go.Scatter(
            x=h_t_ui,
            y=h_delta,
            mode="lines",
            name=h_delta_name,
            line={"color": "mediumpurple", "width": 1.2},
        ),
        row=2,
        col=2,
    )
    fig.add_hline(y=0.0, line={"color": "gray", "width": 1.0, "dash": "dot"}, row=2, col=2)
    fig.add_vline(x=0.0, line={"color": "gray", "width": 1.0, "dash": "dot"}, row=2, col=2)

    fig.add_trace(
        go.Scatter(x=t_ui, y=y_dist_plot[sl].tolist(),
                   mode="lines", name=f"d̂(t) recovered ({linear_mode})",
                   line={"color": "crimson", "width": 1.2}),
        row=3, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_ui, y=dist_true_aligned[sl].tolist(),
                   mode="lines", name="d_true(t) actual nonlinear",
                   line={"color": "black", "width": 0.6}, opacity=0.55),
        row=3, col=1,
    )

    fig.add_trace(
        go.Scatter(x=t_ui, y=y_noise_plot[sl].tolist(),
                   mode="lines", name=f"n̂(t) recovered ({linear_mode})",
                   line={"color": "mediumseagreen", "width": 0.7}),
        row=4, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_ui, y=noise_true_aligned[sl].tolist(),
                   mode="lines", name="n(t) true",
                   line={"color": "black", "width": 0.5}, opacity=0.5),
        row=4, col=1,
    )

    fig.add_trace(
        go.Scatter(x=t_ui, y=d_err[sl].tolist(),
                   mode="lines", name="d̂ − d_true",
                   line={"color": "crimson", "width": 1.0}),
        row=5, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_ui, y=n_err[sl].tolist(),
                   mode="lines", name="n̂ − n_true",
                   line={"color": "mediumseagreen", "width": 1.0, "dash": "dot"}),
        row=5, col=1,
    )

    fig.add_trace(
        go.Histogram(x=d_hist.tolist(), nbinsx=140, marker_color="crimson",
                     opacity=0.85, name="d̂ histogram", showlegend=False),
        row=6, col=1,
    )
    fig.add_trace(
        go.Histogram(x=n_hist.tolist(), nbinsx=140, marker_color="mediumseagreen",
                     opacity=0.85, name="n̂ histogram", showlegend=False),
        row=6, col=2,
    )

    fig.update_xaxes(title_text="time (UI)", row=4, col=1)
    fig.update_xaxes(title_text="impulse time (UI)", row=2, col=1)
    fig.update_xaxes(title_text="impulse time (UI)", row=2, col=2)
    fig.update_xaxes(range=[-ir_plot_ui, ir_plot_ui], row=2, col=1)
    fig.update_xaxes(range=[-ir_plot_ui, ir_plot_ui], row=2, col=2)
    fig.update_xaxes(title_text="time (UI)", row=5, col=1)
    fig.update_xaxes(title_text="distortion amplitude", row=6, col=1)
    fig.update_xaxes(title_text="noise amplitude", row=6, col=2)
    fig.update_yaxes(title_text="amplitude", row=1, col=1)
    fig.update_yaxes(title_text="amplitude", row=2, col=1)
    fig.update_yaxes(title_text="amplitude", row=2, col=2)
    fig.update_yaxes(title_text="amplitude", row=3, col=1)
    fig.update_yaxes(title_text="amplitude", row=4, col=1)
    fig.update_yaxes(title_text="error amplitude", row=5, col=1)
    fig.update_yaxes(title_text="count (log)", type="log", row=6, col=1)
    fig.update_yaxes(title_text="count (log)", type="log", row=6, col=2)

    fig.update_layout(
        title=(
            f"Synthetic decomposition recovery ({linear_mode})   |   SNDR={sndr_plot:.1f} dB    "
            f"SDR={sdr_plot:.1f} dB    SNR={snr_plot:.1f} dB    "
            f"closure={closure_rms_plot:.1e}"
        ),
        template="plotly_white",
        height=1500,
        width=1200,
        showlegend=True,
        legend={"orientation": "h", "y": -0.05},
    )

    out = OUT_DIR / "synthetic_decomposition.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_synthetic_pattern_windows() -> None:
    """Visualise window extraction + pattern averaging on the residual."""
    sps = 8
    pattern_n_pre = 2
    pattern_n_post = 2
    symbols, y, _, _, _ = _synthesise(n_sym=9000, sps=sps)
    decomp = decompose_waveform(
        y,
        symbols,
        sps=sps,
        n_pre=4,
        n_post=8,
        pattern_n_pre=pattern_n_pre,
        pattern_n_post=pattern_n_post,
        pattern_min_hits=4,
        guard_ui=20,
    )

    residual = decomp.residual
    n_ui = len(residual) // sps

    pattern_bins: dict[tuple[int, ...], list[tuple[int, int, np.ndarray]]] = {}
    sym_lo = int(pattern_n_pre)
    sym_hi = len(symbols) - int(pattern_n_post) - 1
    ui_lo = max(sym_lo, int(decomp.cursor_ui_offset))
    ui_hi = min(sym_hi, int(decomp.cursor_ui_offset) + n_ui - 1)
    for m_sym in range(ui_lo, ui_hi + 1):
        start = (m_sym - int(decomp.cursor_ui_offset)) * sps
        chunk = residual[start : start + sps]
        if len(chunk) != sps:
            continue
        ctx = symbols[m_sym - pattern_n_pre : m_sym + pattern_n_post + 1]
        key = tuple(int(v) for v in ctx.tolist())
        pattern_bins.setdefault(key, []).append((m_sym, start, chunk.copy()))

    if not pattern_bins:
        raise RuntimeError("No pattern windows found for synthetic diagnostic figure.")

    target_pattern, entries = max(pattern_bins.items(), key=lambda kv: len(kv[1]))
    n_hits = len(entries)
    n_show = min(14, n_hits)
    sample_idx = np.linspace(0, n_hits - 1, n_show, dtype=int)
    selected = [entries[int(i)] for i in sample_idx]

    chunks = np.stack([v[2] for v in selected], axis=0)
    chunk_mean = chunks.mean(axis=0)
    chunk_std = chunks.std(axis=0)
    chunk_noise = chunks - chunk_mean[None, :]

    sel_ui_idx = np.array([v[1] // sps for v in selected], dtype=int)
    ui_center = int(np.median(sel_ui_idx))
    seg_ui_pre = 55
    seg_ui_post = 130
    seg_lo = max(0, ui_center - seg_ui_pre)
    seg_hi = min(n_ui - 1, ui_center + seg_ui_post)
    sl = slice(seg_lo * sps, (seg_hi + 1) * sps)

    t_long = (np.arange(sl.stop - sl.start) / sps) + seg_lo
    t_zoom = np.arange(sps) / sps

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.07,
        subplot_titles=[
            "Long segment: residual e(t) = y(t) - ŷ(t), with selected UI windows highlighted",
            "Extracted residual windows for one symbol pattern (thin) + pattern mean d̂ (bold)",
            "Window residual after mean removal: n̂ = e_window - d̂ (noise-like remainder)",
        ],
    )

    fig.add_trace(
        go.Scatter(
            x=t_long.tolist(),
            y=residual[sl].tolist(),
            mode="lines",
            name="e(t) = y - ŷ",
            line={"color": "steelblue", "width": 1.0},
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=t_long.tolist(),
            y=decomp.y_distortion[sl].tolist(),
            mode="lines",
            name="d̂(t) from pattern averaging",
            line={"color": "crimson", "width": 1.2, "dash": "dash"},
        ),
        row=1,
        col=1,
    )

    for ui_idx in sel_ui_idx.tolist():
        if seg_lo <= ui_idx <= seg_hi:
            fig.add_vrect(
                x0=float(ui_idx),
                x1=float(ui_idx + 1),
                fillcolor="rgba(255,165,0,0.14)",
                line_width=0,
                row=1,
                col=1,
            )

    for i in range(n_show):
        fig.add_trace(
            go.Scatter(
                x=t_zoom.tolist(),
                y=chunks[i].tolist(),
                mode="lines",
                showlegend=False,
                line={"color": "rgba(70,70,70,0.30)", "width": 1.0},
                hovertemplate="sample=%{x:.2f} UI<br>e=%{y:.4f}<extra></extra>",
            ),
            row=2,
            col=1,
        )
    fig.add_trace(
        go.Scatter(
            x=t_zoom.tolist(),
            y=chunk_mean.tolist(),
            mode="lines",
            name="pattern mean d̂(window)",
            line={"color": "crimson", "width": 2.6},
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=t_zoom.tolist(),
            y=(chunk_mean + chunk_std).tolist(),
            mode="lines",
            name="mean ± 1σ",
            line={"color": "rgba(220,20,60,0.40)", "width": 1.0, "dash": "dot"},
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=t_zoom.tolist(),
            y=(chunk_mean - chunk_std).tolist(),
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(220,20,60,0.12)",
            line={"color": "rgba(220,20,60,0.40)", "width": 1.0, "dash": "dot"},
            showlegend=False,
            hoverinfo="skip",
        ),
        row=2,
        col=1,
    )

    for i in range(n_show):
        fig.add_trace(
            go.Scatter(
                x=t_zoom.tolist(),
                y=chunk_noise[i].tolist(),
                mode="lines",
                showlegend=False,
                line={"color": "rgba(46,139,87,0.30)", "width": 1.0},
                hovertemplate="sample=%{x:.2f} UI<br>n=%{y:.4f}<extra></extra>",
            ),
            row=3,
            col=1,
        )
    fig.add_hline(y=0.0, line={"color": "gray", "width": 1.0, "dash": "dot"}, row=3, col=1)

    fig.update_xaxes(title_text="UI index", row=1, col=1)
    fig.update_xaxes(title_text="within-UI sample index (UI)", row=2, col=1)
    fig.update_xaxes(title_text="within-UI sample index (UI)", row=3, col=1)
    for r in (1, 2, 3):
        fig.update_yaxes(title_text="amplitude", row=r, col=1)

    pattern_text = ", ".join(str(v) for v in target_pattern)
    fig.update_layout(
        title=(
            "Pattern-window decomposition diagnostic   |   "
            f"pattern=[{pattern_text}], hits={n_hits}, shown={n_show}, sps={sps}"
        ),
        template="plotly_white",
        height=980,
        width=1220,
        showlegend=True,
        legend={"orientation": "h", "y": -0.08},
        margin={"t": 90},
    )

    out = OUT_DIR / "synthetic_pattern_windows.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_pattern_00110_window_selection() -> None:
    """Show how pattern 00110 windows are selected and averaged."""
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    pattern_n_pre = 2
    pattern_n_post = 2
    pattern_min_hits = 4

    # 00110 in NRZ symbols (0 -> -1, 1 -> +1)
    target_pattern = (-1, -1, +1, +1, -1)

    symbols, y, _, _, pulse_true = _synthesise(
        n_sym=n_sym,
        sps=sps,
        pulse_span_ui=2 * ir_ui,
        distortion_gain=0.0,
        noise_sigma=0.0,
    )
    decomp = decompose_waveform(
        y,
        symbols,
        sps=sps,
        n_pre=ir_ui,
        n_post=ir_ui,
        pattern_n_pre=pattern_n_pre,
        pattern_n_post=pattern_n_post,
        pattern_min_hits=pattern_min_hits,
        guard_ui=20,
    )

    # Use the planted pulse (exact linear baseline) rather than Wiener y_hat
    # so the residual isolates decomposition behavior instead of fit error.
    y_aligned = decomp.y_aligned
    lag_samples = int(decomp.channel_estimate.lag_samples)
    x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
    x_dirac[::sps] = symbols
    y_linear_true = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
    y_hat_exact = np.zeros(len(y_aligned), dtype=np.float64)
    if lag_samples < len(y_linear_true):
        n_copy = min(len(y_linear_true) - lag_samples, len(y_hat_exact))
        y_hat_exact[:n_copy] = y_linear_true[lag_samples : lag_samples + n_copy]
    residual = y_aligned - y_hat_exact
    n_samples = len(residual)
    cursor_phase = int(decomp.channel_estimate.cursor) % sps
    cursor_ui_offset = int(decomp.cursor_ui_offset)
    window_start = int(cursor_phase) - sps // 2

    if window_start < 0:
        ui_lo = (-window_start + sps - 1) // sps
    else:
        ui_lo = 0
    ui_hi = (n_samples - sps - window_start) // sps

    sym_lo = int(pattern_n_pre)
    sym_hi = len(symbols) - int(pattern_n_post) - 1
    ui_lo_total = max(ui_lo, sym_lo + cursor_ui_offset)
    ui_hi_total = min(ui_hi, sym_hi + cursor_ui_offset)

    hits: list[tuple[int, int, np.ndarray, np.ndarray]] = []
    for m_ui in range(ui_lo_total, ui_hi_total + 1):
        m_sym = m_ui - cursor_ui_offset
        ctx = symbols[m_sym - pattern_n_pre : m_sym + pattern_n_post + 1]
        key = tuple(int(round(float(v))) for v in ctx)
        if key != target_pattern:
            continue
        start = m_ui * sps + window_start
        end = start + sps
        if start < 0 or end > n_samples:
            continue
        hits.append((m_ui, start, y_aligned[start:end].copy(), residual[start:end].copy()))

    if not hits:
        raise RuntimeError("No windows found for pattern 00110.")

    y_chunks = np.stack([h[2] for h in hits], axis=0)
    r_chunks = np.stack([h[3] for h in hits], axis=0)
    r_mean = r_chunks.mean(axis=0)
    n_hits = len(hits)

    # Null-case sanity check: with the exact pulse baseline, zero distortion and
    # zero noise, the residual windows must collapse to machine epsilon.
    interior = residual[lag_samples : n_samples - lag_samples]
    print(
        "[pattern_00110] exact-baseline residual: "
        f"full RMS={float(np.sqrt(np.mean(residual**2))):.3e}, "
        f"interior RMS={float(np.sqrt(np.mean(interior**2))):.3e}, "
        f"window RMS={float(np.sqrt(np.mean(r_chunks**2))):.3e}, "
        f"pattern-mean RMS={float(np.sqrt(np.mean(r_mean**2))):.3e}, "
        f"max|e|(windows)={float(np.max(np.abs(r_chunks))):.3e}"
    )
    n_show = min(200, n_hits)
    sample_idx = np.linspace(0, n_hits - 1, n_show, dtype=int)
    y_show = y_chunks[sample_idx]
    r_show = r_chunks[sample_idx]

    ui_hits = np.array([h[0] for h in hits], dtype=int)
    ui_center = int(np.median(ui_hits))
    seg_ui_pre = 40
    seg_ui_post = 70
    seg_lo = max(0, ui_center - seg_ui_pre)
    seg_hi = min((n_samples // sps) - 1, ui_center + seg_ui_post)
    sl = slice(seg_lo * sps, (seg_hi + 1) * sps)
    t_long = (np.arange(sl.stop - sl.start) / sps) + seg_lo
    t_zoom = np.arange(sps) / sps

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.08,
        subplot_titles=[
            "Aligned y(t): matched 1-UI windows for pattern 00110 highlighted",
            "Extracted residual windows e(t)=y-ŷ for pattern 00110 (thin) + pattern mean (bold)",
        ],
    )

    fig.add_trace(
        go.Scatter(
            x=t_long.tolist(),
            y=y_aligned[sl].tolist(),
            mode="lines",
            name="y_aligned(t)",
            line={"color": "steelblue", "width": 1.0},
        ),
        row=1,
        col=1,
    )
    for ui_idx in ui_hits.tolist():
        if seg_lo <= ui_idx <= seg_hi:
            fig.add_vrect(
                x0=float(ui_idx),
                x1=float(ui_idx + 1),
                fillcolor="rgba(220,20,60,0.16)",
                line_width=0,
                row=1,
                col=1,
            )

    for i in range(n_show):
        fig.add_trace(
            go.Scatter(
                x=t_zoom.tolist(),
                y=r_show[i].tolist(),
                mode="lines",
                showlegend=False,
                line={"color": "rgba(70,70,70,0.25)", "width": 1.0},
                hovertemplate="within-UI=%{x:.2f}<br>e=%{y:.4e}<extra></extra>",
            ),
            row=2,
            col=1,
        )
    fig.add_trace(
        go.Scatter(
            x=t_zoom.tolist(),
            y=r_mean.tolist(),
            mode="lines",
            name="pattern mean (distortion template)",
            line={"color": "crimson", "width": 2.8},
        ),
        row=2,
        col=1,
    )

    fig.update_xaxes(title_text="UI index", row=1, col=1)
    fig.update_xaxes(title_text="within-UI sample index (UI)", row=2, col=1)
    fig.update_yaxes(title_text="amplitude", row=1, col=1)
    fig.update_yaxes(title_text="residual amplitude", row=2, col=1)
    fig.update_layout(
        title=(
            "Pattern-window selection demo   |   target bits=00110   "
            f"(NRZ key={target_pattern}), hits={n_hits}, shown={n_show}"
        ),
        template="plotly_white",
        height=820,
        width=1220,
        showlegend=True,
        legend={"orientation": "h", "y": -0.08},
        margin={"t": 90},
    )

    out = OUT_DIR / "pattern_00110_window_selection.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2 — pkctrl3 per-block bar chart
# ─────────────────────────────────────────────────────────────────────────────


def figure_pkctrl3_block_comparison() -> None:
    """Bar chart of SNDR / SDR / SNR for the three per-block pairs."""
    blocks = [
        ("MZM<br>(IN→Pout)", 35.36, 36.84, 40.73, "distortion-dominated  (SDR < SNR)"),
        ("PD + TIA<br>(Pin→TIA_OUT)", 22.78, 32.60, 23.26, "noise-dominated  (SNR < SDR)"),
        ("RX channel<br>(TIA→RX_CH_OUT)", 26.55, 48.02, 26.58, "noise-dominated  (SNR ≪ SDR)"),
    ]
    labels = [b[0] for b in blocks]
    sndr = [b[1] for b in blocks]
    sdr = [b[2] for b in blocks]
    snr = [b[3] for b in blocks]
    notes = [b[4] for b in blocks]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=sndr, name="SNDR — LTI-fit floor",
        marker_color="steelblue",
        text=[f"{v:.1f}" for v in sndr], textposition="outside", textfont_size=11,
    ))
    fig.add_trace(go.Bar(
        x=labels, y=sdr, name="SDR  — deterministic floor",
        marker_color="crimson",
        text=[f"{v:.1f}" for v in sdr], textposition="outside", textfont_size=11,
    ))
    fig.add_trace(go.Bar(
        x=labels, y=snr, name="SNR  — random-noise floor",
        marker_color="mediumseagreen",
        text=[f"{v:.1f}" for v in snr], textposition="outside", textfont_size=11,
    ))
    for i, note in enumerate(notes):
        fig.add_annotation(
            x=labels[i], y=3.0, text=note, showarrow=False,
            font={"size": 11, "color": "dimgray"},
        )

    fig.update_layout(
        barmode="group",
        title="Per-block decomposition: SNDR / SDR / SNR  (Pkctrl3 PAM4 at 106.25 GBaud)",
        yaxis_title="dB",
        template="plotly_white",
        height=560,
        width=1150,
        legend={"orientation": "h", "y": 1.08},
        yaxis_range=[0, max(max(sdr), max(snr)) + 8.0],
    )

    out = OUT_DIR / "pkctrl3_block_comparison.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_distortion_sigma_vs_noise_sigma() -> None:
    """Sweep injected noise and plot recovered distortion sigma."""
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    pattern_n_pre = 2
    pattern_n_post = 2
    pattern_min_hits = 4
    guard_ui = 20

    exponents = np.arange(-8, -2, 1, dtype=int)  # -8, -7, ..., -3
    noise_sigmas = np.power(10.0, exponents, dtype=np.float64)
    dist_sigmas: list[float] = []

    for ns in noise_sigmas:
        symbols, y, _, _, pulse_true = _synthesise(
            n_sym=n_sym,
            sps=sps,
            pulse_span_ui=2 * ir_ui,
            distortion_gain=0.0,
            noise_sigma=float(ns),
        )
        decomp = decompose_waveform(
            y,
            symbols,
            sps=sps,
            n_pre=n_pre,
            n_post=n_post,
            pattern_n_pre=pattern_n_pre,
            pattern_n_post=pattern_n_post,
            pattern_min_hits=pattern_min_hits,
            guard_ui=guard_ui,
        )

        lag_samples = int(decomp.channel_estimate.lag_samples)
        x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
        x_dirac[::sps] = symbols
        y_linear_true = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
        y_hat_exact = np.zeros(len(decomp.y_aligned), dtype=np.float64)
        if lag_samples < len(y_linear_true):
            n_copy = min(len(y_linear_true) - lag_samples, len(y_hat_exact))
            y_hat_exact[:n_copy] = y_linear_true[lag_samples : lag_samples + n_copy]

        residual_exact = decomp.y_aligned - y_hat_exact
        symbol_cursor = int(decomp.channel_estimate.cursor)
        y_distortion_exact, _, _, _ = _pattern_average_distortion(
            residual_exact,
            np.asarray(symbols, dtype=np.float64),
            sps=sps,
            cursor_phase=int(symbol_cursor) % sps,
            cursor_ui_offset=int(symbol_cursor) // sps,
            pattern_n_pre=pattern_n_pre,
            pattern_n_post=pattern_n_post,
            pattern_min_hits=pattern_min_hits,
        )
        dist_sigmas.append(float(np.std(y_distortion_exact)))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=noise_sigmas.tolist(),
            y=dist_sigmas,
            mode="lines+markers",
            name="sigma(distortion estimate)",
            line={"color": "crimson", "width": 2},
            marker={"size": 8},
        )
    )
    fig.update_xaxes(type="log", title_text="injected noise sigma")
    fig.update_yaxes(type="log", title_text="recovered distortion sigma")
    fig.update_layout(
        title="Distortion sigma vs noise sigma (nonlinearity off, exact linear baseline)",
        template="plotly_white",
        height=560,
        width=980,
        showlegend=True,
    )

    out = OUT_DIR / "distortion_sigma_vs_noise_sigma.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_prbs13_5ui_histogram() -> None:
    """Histogram of 5-UI sequence hit counts over the PRBS13 bitstream."""
    n_bits = 500 * 512
    bits = generate_prbs(order=13, n_bits=n_bits).astype(np.int64)

    # Sliding 5-bit windows. Bin index is binary code:
    # 00000->0, 00001->1, ..., 11111->31.
    n_win = len(bits) - 5 + 1
    if n_win <= 0:
        raise ValueError("Bitstream too short for 5-UI histogram.")
    weights = np.array([16, 8, 4, 2, 1], dtype=np.int64)
    codes = np.empty(n_win, dtype=np.int64)
    for i in range(n_win):
        codes[i] = int(np.dot(bits[i : i + 5], weights))

    counts = np.bincount(codes, minlength=32)
    x_bins = np.arange(32, dtype=np.int64)
    expected = float(n_win) / 32.0

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x_bins.tolist(),
            y=counts.tolist(),
            name="5-UI window count",
            marker_color="steelblue",
            hovertemplate="bin=%{x}<br>count=%{y}<extra></extra>",
        )
    )
    fig.add_hline(
        y=expected,
        line={"color": "crimson", "width": 1.2, "dash": "dash"},
        annotation_text=f"uniform reference = {expected:.1f}",
        annotation_position="top left",
    )
    fig.update_xaxes(title_text="5-bit sequence bin (00000->0 ... 11111->31)", dtick=1)
    fig.update_yaxes(title_text="count over sliding 5-UI windows")
    fig.update_layout(
        title=(
            "PRBS13 5-UI sequence histogram "
            f"(n_bits={n_bits}, n_windows={n_win}, sequence=500*512 bits)"
        ),
        template="plotly_white",
        height=560,
        width=1200,
        showlegend=True,
    )

    out = OUT_DIR / "prbs13_5ui_sequence_histogram.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")
    print(f"bin 0 (00000) count = {int(counts[0])}")
    print(f"bin 1 (00001) count = {int(counts[1])}")


def figure_distortion_error_heatmap() -> None:
    """2D sweep: distortion RMS error vs noise sigma and context length."""
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    guard_ui = 20
    distortion_gain = 0.15

    # User-selected sweep setup.
    noise_sigmas = np.logspace(-8, -2, 13)
    contexts = np.arange(2, 15, dtype=int)  # pre=post=2..14

    # Fixed PRBS13 symbols and exact linear pulse baseline.
    symbols, _, _, _, pulse_true = _synthesise(
        n_sym=n_sym,
        sps=sps,
        pulse_span_ui=2 * ir_ui,
        distortion_gain=distortion_gain,
        noise_sigma=0.0,
    )
    x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
    x_dirac[::sps] = symbols
    y_linear_true = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]

    # Heatmap matrix: rows=context, cols=noise sigma.
    z_rms = np.zeros((len(contexts), len(noise_sigmas)), dtype=np.float64)

    for j, ns in enumerate(noise_sigmas):
        _, y, dist_true, _, _ = _synthesise(
            n_sym=n_sym,
            sps=sps,
            pulse_span_ui=2 * ir_ui,
            distortion_gain=distortion_gain,
            noise_sigma=float(ns),
        )
        decomp = decompose_waveform(
            y,
            symbols,
            sps=sps,
            n_pre=n_pre,
            n_post=n_post,
            pattern_n_pre=2,
            pattern_n_post=2,
            pattern_min_hits=4,
            guard_ui=guard_ui,
        )

        lag_samples = int(decomp.channel_estimate.lag_samples)
        symbol_cursor = int(decomp.channel_estimate.cursor)

        y_hat_exact = np.zeros(len(decomp.y_aligned), dtype=np.float64)
        if lag_samples < len(y_linear_true):
            n_copy = min(len(y_linear_true) - lag_samples, len(y_hat_exact))
            y_hat_exact[:n_copy] = y_linear_true[lag_samples : lag_samples + n_copy]

        dist_true_aligned = np.zeros(len(decomp.y_aligned), dtype=np.float64)
        if lag_samples < len(dist_true):
            n_copy = min(len(dist_true) - lag_samples, len(dist_true_aligned))
            dist_true_aligned[:n_copy] = dist_true[lag_samples : lag_samples + n_copy]

        residual_exact = decomp.y_aligned - y_hat_exact

        for i, ctx in enumerate(contexts):
            y_dist, _, _, _ = _pattern_average_distortion(
                residual_exact,
                np.asarray(symbols, dtype=np.float64),
                sps=sps,
                cursor_phase=symbol_cursor % sps,
                cursor_ui_offset=symbol_cursor // sps,
                pattern_n_pre=int(ctx),
                pattern_n_post=int(ctx),
                pattern_min_hits=4,
            )
            err = y_dist - dist_true_aligned
            z_rms[i, j] = float(np.sqrt(np.mean(err**2)))

    fig = go.Figure(
        data=go.Heatmap(
            z=np.log10(np.maximum(z_rms, 1e-20)),
            x=[f"{v:.1e}" for v in noise_sigmas],
            y=[f"{c}+1+{c}" for c in contexts],
            colorscale="Viridis",
            colorbar={"title": "log10(RMS error)"},
            hovertemplate=(
                "noise_sigma=%{x}<br>"
                "context=%{y}<br>"
                "log10 RMS err=%{z:.3f}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=(
            "Distortion estimation error heatmap "
            "(exact linear baseline, PRBS13, distortion_gain=0.15)"
        ),
        xaxis_title="noise sigma",
        yaxis_title="bit-sequence context length (pre+1+post)",
        template="plotly_white",
        height=620,
        width=1150,
    )

    out = OUT_DIR / "distortion_error_heatmap_noise_vs_context.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_distortion_error_vs_sequence_no_noise() -> None:
    """1D sweep: distortion RMS error vs bit-sequence window length at zero noise."""
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    guard_ui = 20
    distortion_gain = 0.15
    noise_sigma = 0.0

    contexts = np.arange(2, 15, dtype=int)  # pre=post=2..14
    total_bits = 2 * contexts + 1
    rms_errs: list[float] = []
    noise_sigmas_est: list[float] = []

    symbols, y, dist_true, _, pulse_true = _synthesise(
        n_sym=n_sym,
        sps=sps,
        pulse_span_ui=2 * ir_ui,
        distortion_gain=distortion_gain,
        noise_sigma=noise_sigma,
    )
    decomp = decompose_waveform(
        y,
        symbols,
        sps=sps,
        n_pre=n_pre,
        n_post=n_post,
        pattern_n_pre=2,
        pattern_n_post=2,
        pattern_min_hits=4,
        guard_ui=guard_ui,
    )

    lag_samples = int(decomp.channel_estimate.lag_samples)
    symbol_cursor = int(decomp.channel_estimate.cursor)

    x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
    x_dirac[::sps] = symbols
    y_linear_true = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
    y_hat_exact = np.zeros(len(decomp.y_aligned), dtype=np.float64)
    if lag_samples < len(y_linear_true):
        n_copy = min(len(y_linear_true) - lag_samples, len(y_hat_exact))
        y_hat_exact[:n_copy] = y_linear_true[lag_samples : lag_samples + n_copy]

    dist_true_aligned = np.zeros(len(decomp.y_aligned), dtype=np.float64)
    if lag_samples < len(dist_true):
        n_copy = min(len(dist_true) - lag_samples, len(dist_true_aligned))
        dist_true_aligned[:n_copy] = dist_true[lag_samples : lag_samples + n_copy]

    residual_exact = decomp.y_aligned - y_hat_exact

    for ctx in contexts:
        y_dist, _, _, _ = _pattern_average_distortion(
            residual_exact,
            np.asarray(symbols, dtype=np.float64),
            sps=sps,
            cursor_phase=symbol_cursor % sps,
            cursor_ui_offset=symbol_cursor // sps,
            pattern_n_pre=int(ctx),
            pattern_n_post=int(ctx),
            pattern_min_hits=4,
        )
        # Use only the interior region where the pattern-conditioned estimate
        # is valid for this context (exclude edge samples by construction).
        window_start = (symbol_cursor % sps) - sps // 2
        if window_start < 0:
            ui_lo = (-window_start + sps - 1) // sps
        else:
            ui_lo = 0
        ui_hi = (len(residual_exact) - sps - window_start) // sps
        sym_lo = int(ctx)
        sym_hi = len(symbols) - int(ctx) - 1
        ui_lo_total = max(ui_lo, sym_lo + symbol_cursor // sps)
        ui_hi_total = min(ui_hi, sym_hi + symbol_cursor // sps)
        start = ui_lo_total * sps + window_start
        stop = ui_hi_total * sps + window_start + sps

        y_noise = residual_exact - y_dist
        err = y_dist - dist_true_aligned
        rms_errs.append(float(np.sqrt(np.mean(err[start:stop] ** 2))))
        noise_sigmas_est.append(float(np.std(y_noise[start:stop])))

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=[
            "Distortion RMS error vs window length (interior only, noise_sigma = 0)",
            "Estimated noise sigma vs window length (interior only, noise_sigma = 0)",
        ],
    )
    fig.add_trace(
        go.Scatter(
            x=total_bits.tolist(),
            y=rms_errs,
            mode="lines+markers",
            name="distortion RMS error",
            line={"color": "crimson", "width": 2},
            marker={"size": 8},
            hovertemplate=(
                "bit-sequence length=%{x}<br>"
                "RMS error=%{y:.3e}<extra></extra>"
            ),
        )
    ,
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=total_bits.tolist(),
            y=noise_sigmas_est,
            mode="lines+markers",
            name="estimated noise sigma",
            line={"color": "mediumseagreen", "width": 2},
            marker={"size": 8},
            hovertemplate=(
                "bit-sequence length=%{x}<br>"
                "noise sigma est=%{y:.3e}<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )
    fig.update_xaxes(
        title_text="bit-sequence window length (pre + 1 + post)",
        dtick=2,
        row=2,
        col=1,
    )
    fig.update_yaxes(title_text="distortion error RMS", type="log", row=1, col=1)
    fig.update_yaxes(title_text="estimated noise sigma", type="log", row=2, col=1)
    fig.update_layout(
        title=(
            "Distortion/noise estimates vs bit-sequence window length "
            "(PRBS13, exact linear baseline, interior analyzed region, noise_sigma=0)"
        ),
        template="plotly_white",
        height=760,
        width=980,
        showlegend=True,
    )

    out = OUT_DIR / "distortion_error_vs_bit_sequence_no_noise.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_nonlinearity_gain_sweep(
    *,
    prbs_order: int = 13,
    context_uis: list[int] | None = None,
) -> None:
    """Sweep static (memoryless) tanh nonlinearity strength × context window.

    For a set of ``tanh`` distortion gains ``α`` the synthetic generator
    applies ``y_nl = tanh(α·y_lin)/tanh(α)`` — a purely *static*
    compression (no added memory).  For each gain we re-run the
    pattern-context sweep (5..15 UI) on the **exact-baseline** residual
    and record the recovered-distortion / leftover-noise split.

    Hypothesis under test
    ---------------------
    Stronger static nonlinearity scales (i) the recovered distortion
    magnitude and (ii) the pre-collapse leftover-noise floor, **but** the
    context length at which the noise floor collapses stays pinned at the
    PRBS order (13 for PRBS13).  The collapse is set by source-state
    identifiability (when the symbol context resolves the LFSR state),
    not by nonlinearity strength.

    Running with ``prbs_order=31`` is the falsification test: the
    identifiability order (31 UI) sits far outside the 5..15 UI sweep
    window (and is unreachable at this record length anyway), so the
    collapse should vanish and the leftover noise should only decline
    gently — exactly as for the 5..11 UI pre-collapse region of PRBS13.
    """
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    pattern_min_hits = 4
    guard_ui = 20
    prbs_order = int(prbs_order)

    gains = [0.05, 0.1, 0.2, 0.3, 0.4]
    default_ctx = [5, 7, 9, 11, 13, 15]
    contexts = list(default_ctx if context_uis is None else context_uis)
    for c in contexts:
        if c < 1 or c % 2 == 0:
            raise ValueError(f"context window must be a positive odd UI count, got {c}")
    ks = [(c - 1) // 2 for c in contexts]  # pre = post = (ctx-1)/2

    # Light→dark severity ramp (weak gain = light blue, strong = dark red).
    gain_colors = ["#74add1", "#4daf4a", "#fdae61", "#f46d43", "#d73027"]

    noise_rms: dict[float, list[float]] = {}
    dist_rms: dict[float, list[float]] = {}

    for gain in gains:
        symbols, y, dist_true, _, pulse_true = _synthesise(
            n_sym=n_sym,
            sps=sps,
            pulse_span_ui=2 * ir_ui,
            distortion_gain=gain,
            noise_sigma=0.0,
            prbs_order=prbs_order,
        )
        decomp = decompose_waveform(
            y,
            symbols,
            sps=sps,
            n_pre=n_pre,
            n_post=n_post,
            pattern_n_pre=2,
            pattern_n_post=2,
            pattern_min_hits=pattern_min_hits,
            guard_ui=guard_ui,
        )

        ya = decomp.y_aligned
        n = len(ya)
        lag = int(decomp.channel_estimate.lag_samples)
        cursor = int(decomp.channel_estimate.cursor)

        x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
        x_dirac[::sps] = symbols
        y_linear_true = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]

        def _align(trace: np.ndarray, *, _n: int = n, _lag: int = lag) -> np.ndarray:
            out = np.zeros(_n, dtype=np.float64)
            if _lag < len(trace):
                n_copy = min(len(trace) - _lag, _n)
                out[:n_copy] = trace[_lag : _lag + n_copy]
            return out

        yhat = _align(y_linear_true)
        residual = ya - yhat
        dist_true_al = _align(dist_true)

        g = guard_ui * sps
        region = slice(g, n - g)
        ms = lambda arr: float(np.mean(arr[region] ** 2))  # noqa: E731
        p_y = ms(ya)
        p_dt = ms(dist_true_al)
        sym = np.asarray(symbols, dtype=np.float64)

        nr: list[float] = []
        dr: list[float] = []
        for k, ctx_ui in zip(ks, contexts, strict=True):
            y_dist, n_pat, n_kept, n_anal = _pattern_average_distortion(
                residual,
                sym,
                sps=sps,
                cursor_phase=cursor % sps,
                cursor_ui_offset=cursor // sps,
                pattern_n_pre=k,
                pattern_n_post=k,
                pattern_min_hits=pattern_min_hits,
            )
            y_noise = residual - y_dist
            p_dis = ms(y_dist)
            p_noi = ms(y_noise)
            nr.append(float(np.sqrt(p_noi)))
            dr.append(float(np.sqrt(p_dis)))
            snr = 10.0 * np.log10(p_y / p_noi) if p_noi > 0 else float("inf")
            sdr = 10.0 * np.log10(p_y / p_dis) if p_dis > 0 else float("inf")
            cap = 100.0 * p_dis / p_dt if p_dt > 0 else float("nan")
            cov = 100.0 * n_kept / max(n_anal, 1)
            print(
                f"PRBS{prbs_order} gain={gain:.2f} ctx={ctx_ui:2d} UI  "
                f"patterns={n_pat:6d} cover={cov:5.1f}%  "
                f"noiseRMS={np.sqrt(p_noi):.3e}  distRMS={np.sqrt(p_dis):.3e}  "
                f"captured={cap:6.2f}%  SNR={snr:6.1f} dB  SDR={sdr:5.1f} dB"
            )
        noise_rms[gain] = nr
        dist_rms[gain] = dr

    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.10,
        subplot_titles=[
            "Leftover noise RMS vs context window  (per static tanh gain)",
            "Recovered distortion RMS vs context window  (per static tanh gain)",
        ],
    )

    for gain, color in zip(gains, gain_colors, strict=True):
        fig.add_trace(
            go.Scatter(
                x=contexts,
                y=noise_rms[gain],
                mode="lines+markers",
                name=f"gain={gain:.2f}",
                legendgroup=f"gain={gain:.2f}",
                line={"color": color, "width": 2},
                marker={"size": 8},
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=contexts,
                y=dist_rms[gain],
                mode="lines+markers",
                name=f"gain={gain:.2f}",
                legendgroup=f"gain={gain:.2f}",
                showlegend=False,
                line={"color": color, "width": 2},
                marker={"size": 8},
            ),
            row=1,
            col=2,
        )

    # The collapse needs BOTH (a) context ≥ prbs_order so the pattern resolves
    # the LFSR state, AND (b) each order-length state to recur ≥ min_hits times
    # so its conditional mean is well defined.  For an m-sequence each full
    # 1-bit state window recurs ≈ n_sym / (2**order − 1) times in the record.
    hits_at_order = n_sym / float(2**prbs_order - 1)
    identifiable = hits_at_order >= pattern_min_hits
    if prbs_order <= max(contexts):
        for col in (1, 2):
            fig.add_vline(
                x=prbs_order,
                line={"color": "gray", "dash": "dash", "width": 1},
                row=1,
                col=col,
            )
        fig.add_annotation(
            x=prbs_order,
            y=0.0,
            xref="x1",
            yref="paper",
            text=f"PRBS{prbs_order} order = {prbs_order}",
            showarrow=False,
            yshift=10,
            font={"color": "gray", "size": 11},
        )
        if identifiable:
            collapse_note = (
                f"noise-floor collapse pinned at PRBS order ({prbs_order}); "
                f"~{hits_at_order:.0f} hits/state"
            )
        else:
            collapse_note = (
                f"PRBS{prbs_order} state ({prbs_order} UI) is in-window but "
                f"data-starved (~{hits_at_order:.1e} hits/state &lt; "
                f"min_hits={pattern_min_hits}): bins never recur, so no collapse"
            )
    elif identifiable:
        collapse_note = (
            f"no collapse: PRBS{prbs_order} identifiability order "
            f"({prbs_order} UI) lies beyond the {max(contexts)} UI sweep window"
        )
    else:
        collapse_note = (
            f"no collapse: PRBS{prbs_order} state is both beyond the "
            f"{max(contexts)} UI window and data-starved (~{hits_at_order:.1e} "
            f"hits/state)"
        )

    fig.update_yaxes(title_text="leftover noise RMS (log)", type="log", row=1, col=1)
    fig.update_yaxes(title_text="recovered distortion RMS (log)", type="log", row=1, col=2)
    fig.update_xaxes(title_text="context window (UI)", dtick=2, row=1, col=1)
    fig.update_xaxes(title_text="context window (UI)", dtick=2, row=1, col=2)
    fig.update_layout(
        title=(
            "Static nonlinearity (tanh gain) × context-window sweep  |  "
            f"exact channel, no noise, PRBS{prbs_order}<br>"
            "<sup>distortion + leftover noise floor scale with gain; "
            f"{collapse_note}</sup>"
        ),
        template="plotly_white",
        height=500,
        width=1250,
        margin={"t": 90},
        legend={"orientation": "h", "y": -0.18, "title": {"text": "static tanh gain  "}},
    )

    prbs_part = "" if prbs_order == 13 else f"_prbs{prbs_order}"
    ctx_part = "" if contexts == default_ctx else f"_ctx{contexts[0]}-{contexts[-1]}"
    out = OUT_DIR / f"nonlinearity_gain_context_sweep{prbs_part}{ctx_part}.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_prbs_order_context_sweep(
    *,
    distortion_gain: float = 0.05,
    prbs_orders: list[int] | None = None,
    context_uis: list[int] | None = None,
) -> None:
    """Show the PRBS-order dependence of the noise-floor collapse context.

    At a fixed (weak) static tanh nonlinearity and zero noise, sweep the
    pattern context window over **every** integer length 5..17 UI for a
    family of PRBS orders {7, 9, 11, 13, 15}.  Each curve is the leftover
    "noise" RMS (the share of the deterministic distortion *not* captured
    by the finite context) on the exact-baseline residual.

    Expected behaviour
    ------------------
    The collapse is set by source-state identifiability: an order-``N``
    LFSR state is resolved once the context spans ``N`` consecutive
    symbols, so each PRBS``N`` curve declines gently for context ``< N``
    and crashes to its data floor exactly at context ``= N`` (then stays
    low, because for context ``> N`` the extra symbols are deterministic
    functions of the already-resolved state and add no new pattern
    splits).  The collapse therefore marches right as the PRBS order
    grows, independent of the nonlinearity strength.

    Even context lengths use an asymmetric split
    ``pre = ⌊(L-1)/2⌋, post = L-1-pre``; identifiability depends only on
    the total consecutive-symbol span ``L``, so the collapse still
    triggers at ``L = N``.
    """
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    pattern_min_hits = 4
    guard_ui = 20

    prbs_orders = list(prbs_orders if prbs_orders is not None else [7, 9, 11, 13, 15])
    contexts = list(context_uis if context_uis is not None else range(5, 18))  # 5..17
    for c in contexts:
        if c < 1:
            raise ValueError(f"context window must be ≥ 1 UI, got {c}")

    # Cool→warm ramp ordered by PRBS order (low order = blue, high = red).
    order_colors = ["#4575b4", "#74add1", "#fdae61", "#f46d43", "#d73027"]
    if len(prbs_orders) > len(order_colors):
        order_colors = order_colors * (len(prbs_orders) // len(order_colors) + 1)

    noise_rms: dict[int, list[float]] = {}
    cap_pct: dict[int, list[float]] = {}

    for order in prbs_orders:
        symbols, y, dist_true, _, pulse_true = _synthesise(
            n_sym=n_sym,
            sps=sps,
            pulse_span_ui=2 * ir_ui,
            distortion_gain=distortion_gain,
            noise_sigma=0.0,
            prbs_order=order,
        )
        decomp = decompose_waveform(
            y,
            symbols,
            sps=sps,
            n_pre=n_pre,
            n_post=n_post,
            pattern_n_pre=2,
            pattern_n_post=2,
            pattern_min_hits=pattern_min_hits,
            guard_ui=guard_ui,
        )

        ya = decomp.y_aligned
        n = len(ya)
        lag = int(decomp.channel_estimate.lag_samples)
        cursor = int(decomp.channel_estimate.cursor)

        x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
        x_dirac[::sps] = symbols
        y_linear_true = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]

        def _align(trace: np.ndarray, *, _n: int = n, _lag: int = lag) -> np.ndarray:
            out = np.zeros(_n, dtype=np.float64)
            if _lag < len(trace):
                n_copy = min(len(trace) - _lag, _n)
                out[:n_copy] = trace[_lag : _lag + n_copy]
            return out

        residual = ya - _align(y_linear_true)
        dist_true_al = _align(dist_true)

        g = guard_ui * sps
        region = slice(g, n - g)
        ms = lambda arr: float(np.mean(arr[region] ** 2))  # noqa: E731
        p_y = ms(ya)
        p_dt = ms(dist_true_al)
        sym = np.asarray(symbols, dtype=np.float64)

        nr: list[float] = []
        cp: list[float] = []
        for L in contexts:
            pre = (L - 1) // 2
            post = (L - 1) - pre
            y_dist, n_pat, n_kept, n_anal = _pattern_average_distortion(
                residual,
                sym,
                sps=sps,
                cursor_phase=cursor % sps,
                cursor_ui_offset=cursor // sps,
                pattern_n_pre=pre,
                pattern_n_post=post,
                pattern_min_hits=pattern_min_hits,
            )
            y_noise = residual - y_dist
            p_dis = ms(y_dist)
            p_noi = ms(y_noise)
            nr.append(float(np.sqrt(p_noi)))
            cp.append(100.0 * p_dis / p_dt if p_dt > 0 else float("nan"))
            cov = 100.0 * n_kept / max(n_anal, 1)
            snr = 10.0 * np.log10(p_y / p_noi) if p_noi > 0 else float("inf")
            print(
                f"PRBS{order:2d} ctx={L:2d} UI (pre={pre},post={post})  "
                f"patterns={n_pat:6d} cover={cov:5.1f}%  "
                f"noiseRMS={np.sqrt(p_noi):.3e}  captured={cp[-1]:6.2f}%  SNR={snr:6.1f} dB"
            )
        noise_rms[order] = nr
        cap_pct[order] = cp

    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.10,
        subplot_titles=[
            "Leftover noise RMS vs context window  (per PRBS order)",
            "Distortion captured % vs context window  (per PRBS order)",
        ],
    )

    for order, color in zip(prbs_orders, order_colors[: len(prbs_orders)], strict=True):
        fig.add_trace(
            go.Scatter(
                x=contexts,
                y=noise_rms[order],
                mode="lines+markers",
                name=f"PRBS{order}",
                legendgroup=f"PRBS{order}",
                line={"color": color, "width": 2},
                marker={"size": 7},
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=contexts,
                y=cap_pct[order],
                mode="lines+markers",
                name=f"PRBS{order}",
                legendgroup=f"PRBS{order}",
                showlegend=False,
                line={"color": color, "width": 2},
                marker={"size": 7},
            ),
            row=1,
            col=2,
        )
        # Colour-matched marker of where this order's state becomes identifiable.
        if min(contexts) <= order <= max(contexts):
            for col in (1, 2):
                fig.add_vline(
                    x=order,
                    line={"color": color, "dash": "dot", "width": 1},
                    row=1,
                    col=col,
                )

    fig.update_yaxes(title_text="leftover noise RMS (log)", type="log", row=1, col=1)
    fig.update_yaxes(title_text="distortion captured %", row=1, col=2)
    fig.update_xaxes(title_text="context window (UI)", dtick=2, row=1, col=1)
    fig.update_xaxes(title_text="context window (UI)", dtick=2, row=1, col=2)
    fig.update_layout(
        title=(
            "PRBS-order dependence of the noise-floor collapse  |  "
            f"exact channel, no noise, weak tanh (gain={distortion_gain:.2f})<br>"
            "<sup>dotted line = each PRBS state-identifiability order; "
            "the noise floor collapses exactly when context = PRBS order</sup>"
        ),
        template="plotly_white",
        height=520,
        width=1250,
        margin={"t": 95},
        legend={"orientation": "h", "y": -0.18, "title": {"text": "source  "}},
    )

    out = OUT_DIR / "prbs_order_context_collapse_sweep.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_context_identifiability_intuition(
    *,
    prbs_order: int = 7,
    distortion_gain: float = 0.05,
) -> None:
    """Visualise *why* the collapse happens exactly at context = PRBS order.

    The recovery groups UIs by their local symbol context and averages the
    residual per group.  Using PRBS``order`` (so the step is at
    ``order`` UI), we pick one ambiguous ``order−1``-symbol context bin
    and show that it secretly contains **two** distinct deterministic
    distortion waveforms — because the single unresolved *past* symbol
    still drives the causal channel.  Their conditional average therefore
    leaves a residual (the "noise" floor).  Extending the context to the
    full ``order`` symbols pins the LFSR state, splitting the bin into two
    pure groups that each collapse onto a single waveform (residual → 0).

    Left panel  : context = order−1 symbols  → 1 bin, 2 waveforms, mean
                  leaves spread.
    Right panel : context = order   symbols  → 2 bins, each a single
                  waveform, spread → 0.
    """
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    guard_ui = 20
    pattern_min_hits = 4
    win_ui = 2  # UI shown on each side of the cursor

    symbols, y, _, _, pulse_true = _synthesise(
        n_sym=n_sym,
        sps=sps,
        pulse_span_ui=2 * ir_ui,
        distortion_gain=distortion_gain,
        noise_sigma=0.0,
        prbs_order=prbs_order,
    )
    decomp = decompose_waveform(
        y,
        symbols,
        sps=sps,
        n_pre=ir_ui,
        n_post=ir_ui,
        pattern_n_pre=2,
        pattern_n_post=2,
        pattern_min_hits=pattern_min_hits,
        guard_ui=guard_ui,
    )

    ya = decomp.y_aligned
    n = len(ya)
    lag = int(decomp.channel_estimate.lag_samples)
    cursor = int(decomp.channel_estimate.cursor)
    x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
    x_dirac[::sps] = symbols
    y_lin = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
    y_hat = np.zeros(n, dtype=np.float64)
    if lag < len(y_lin):
        n_copy = min(len(y_lin) - lag, n)
        y_hat[:n_copy] = y_lin[lag : lag + n_copy]
    residual = ya - y_hat
    sym = np.asarray(symbols, dtype=np.float64)

    cursor_phase = cursor % sps
    cursor_ui_offset = cursor // sps
    window_start = cursor_phase - sps // 2

    # Condition on the (order−1) consecutive symbols m-(k-1)..m+k_post and
    # leave the most-past symbol m-k_pre free.  A *past* free symbol is
    # essential: the channel is causal, so a free *future* symbol would not
    # change the cursor distortion and the two groups would not separate.
    k_full = prbs_order  # full state span (symbols)
    pre_full = k_full // 2  # e.g. 3 for order 7  → window m-3..m+3
    post_full = k_full - 1 - pre_full
    # 6-symbol context drops the most-past symbol (offset -pre_full).
    off_lo6 = -pre_full + 1
    off_hi6 = post_full
    free_off = -pre_full  # the dropped (free) past symbol

    # Pass 1: per (context6, free_bit) accumulate cursor-UI chunk sum / sumsq.
    sum_v: dict[tuple, np.ndarray] = {}
    sumsq_v: dict[tuple, np.ndarray] = {}
    cnt: dict[tuple, int] = {}
    m_sym_lo = pre_full
    m_sym_hi = n_sym - 1 - post_full
    for m_ui in range(n // sps):
        m_sym = m_ui - cursor_ui_offset
        if m_sym < m_sym_lo or m_sym > m_sym_hi:
            continue
        start = m_ui * sps + window_start
        if start < 0 or start + sps > n:
            continue
        ctx6 = tuple(int(v) for v in sym[m_sym + off_lo6 : m_sym + off_hi6 + 1])
        free_bit = int(sym[m_sym + free_off])
        key = (ctx6, free_bit)
        chunk = residual[start : start + sps]
        if key in cnt:
            sum_v[key] += chunk
            sumsq_v[key] += chunk * chunk
            cnt[key] += 1
        else:
            sum_v[key] = chunk.copy()
            sumsq_v[key] = chunk * chunk
            cnt[key] = 1

    # Pick the 6-symbol context whose two free-bit groups have the most
    # different cursor distortion (largest visible separation).
    ctx6_set = {k[0] for k in cnt}
    best_ctx = None
    best_sep = -1.0
    for c in ctx6_set:
        kp, km = (c, +1), (c, -1)
        if cnt.get(kp, 0) < 100 or cnt.get(km, 0) < 100:
            continue
        mean_p = sum_v[kp] / cnt[kp]
        mean_m = sum_v[km] / cnt[km]
        sep = float(np.sqrt(np.mean((mean_p - mean_m) ** 2)))
        if sep > best_sep:
            best_sep = sep
            best_ctx = c
    if best_ctx is None:
        raise RuntimeError("No ambiguous 6-symbol context with both completions found.")

    kp, km = (best_ctx, +1), (best_ctx, -1)
    cnt_p, cnt_m = cnt[kp], cnt[km]
    mean_p = sum_v[kp] / cnt_p
    mean_m = sum_v[km] / cnt_m
    mean6 = (sum_v[kp] + sum_v[km]) / (cnt_p + cnt_m)
    var6 = (sumsq_v[kp] + sumsq_v[km]) / (cnt_p + cnt_m) - mean6**2
    leftover6 = float(np.sqrt(np.mean(np.maximum(var6, 0.0))))
    var_p = sumsq_v[kp] / cnt_p - mean_p**2
    var_m = sumsq_v[km] / cnt_m - mean_m**2
    var7 = (cnt_p * var_p + cnt_m * var_m) / (cnt_p + cnt_m)
    leftover7 = float(np.sqrt(np.mean(np.maximum(var7, 0.0))))

    print(
        f"PRBS{prbs_order} intuition: context6={best_ctx}, free m{free_off:+d}∈{{-1,+1}}, "
        f"hits +1={cnt_p}, -1={cnt_m}"
    )
    print(
        f"  cursor-chunk leftover RMS:  {k_full-1}-sym context = {leftover6:.3e}   "
        f"{k_full}-sym context = {leftover7:.3e}"
    )

    # Pass 2: collect a subsample of multi-UI residual windows for plotting.
    n_show = 70
    plot_p: list[np.ndarray] = []
    plot_m: list[np.ndarray] = []
    starts: list[int] = []
    for m_ui in range(n // sps):
        m_sym = m_ui - cursor_ui_offset
        if m_sym < m_sym_lo or m_sym > m_sym_hi:
            continue
        ctx6 = tuple(int(v) for v in sym[m_sym + off_lo6 : m_sym + off_hi6 + 1])
        if ctx6 != best_ctx:
            continue
        start = m_ui * sps + window_start
        lo = start - win_ui * sps
        hi = start + (win_ui + 1) * sps
        if lo < 0 or hi > n:
            continue
        free_bit = int(sym[m_sym + free_off])
        chunk = residual[lo:hi]
        if free_bit > 0 and len(plot_p) < n_show:
            plot_p.append(chunk)
        elif free_bit < 0 and len(plot_m) < n_show:
            plot_m.append(chunk)
        starts.append(start)
        if len(plot_p) >= n_show and len(plot_m) >= n_show:
            break

    win_len = (2 * win_ui + 1) * sps
    t_ui = ((np.arange(win_len) - (win_ui * sps + sps // 2)) / sps).tolist()

    # Multi-UI group means for the bold overlays.
    mean_p_plot = np.mean(np.stack(plot_p, axis=0), axis=0)
    mean_m_plot = np.mean(np.stack(plot_m, axis=0), axis=0)
    mean6_plot = np.mean(np.stack(plot_p + plot_m, axis=0), axis=0)

    c_plus = "crimson"
    c_minus = "steelblue"
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.09,
        subplot_titles=[
            f"{k_full - 1}-symbol context: 1 bin holds 2 waveforms "
            f"(leftover {leftover6:.1e})",
            f"{k_full}-symbol context = full state: 2 pure bins "
            f"(leftover {leftover7:.1e})",
        ],
    )

    # Left panel: thin windows coloured by the free past bit + the single
    # 6-symbol conditional mean (what the method computes for this bin).
    for arr in plot_p:
        fig.add_trace(
            go.Scatter(
                x=t_ui, y=arr.tolist(), mode="lines", showlegend=False,
                line={"color": "rgba(220,20,60,0.18)", "width": 1},
                hoverinfo="skip",
            ),
            row=1, col=1,
        )
    for arr in plot_m:
        fig.add_trace(
            go.Scatter(
                x=t_ui, y=arr.tolist(), mode="lines", showlegend=False,
                line={"color": "rgba(70,130,180,0.18)", "width": 1},
                hoverinfo="skip",
            ),
            row=1, col=1,
        )
    fig.add_trace(
        go.Scatter(
            x=t_ui, y=mean6_plot.tolist(), mode="lines",
            name=f"{k_full - 1}-symbol bin mean  (what the method keeps)",
            line={"color": "black", "width": 3, "dash": "dash"},
        ),
        row=1, col=1,
    )

    # Right panel: same windows, now split into the two full-state bins,
    # each collapsing onto its own mean.
    for arr in plot_p:
        fig.add_trace(
            go.Scatter(
                x=t_ui, y=arr.tolist(), mode="lines", showlegend=False,
                line={"color": "rgba(220,20,60,0.18)", "width": 1},
                hoverinfo="skip",
            ),
            row=1, col=2,
        )
    for arr in plot_m:
        fig.add_trace(
            go.Scatter(
                x=t_ui, y=arr.tolist(), mode="lines", showlegend=False,
                line={"color": "rgba(70,130,180,0.18)", "width": 1},
                hoverinfo="skip",
            ),
            row=1, col=2,
        )
    fig.add_trace(
        go.Scatter(
            x=t_ui, y=mean_p_plot.tolist(), mode="lines",
            name=f"state with free m{free_off:+d} = +1",
            line={"color": c_plus, "width": 3},
        ),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=t_ui, y=mean_m_plot.tolist(), mode="lines",
            name=f"state with free m{free_off:+d} = −1",
            line={"color": c_minus, "width": 3},
        ),
        row=1, col=2,
    )

    for col in (1, 2):
        fig.add_vrect(
            x0=-0.5, x1=0.5, fillcolor="rgba(120,120,120,0.08)", line_width=0,
            row=1, col=col,
        )
        fig.add_vline(
            x=0.0, line={"color": "gray", "width": 1, "dash": "dot"},
            row=1, col=col,
        )
        fig.update_xaxes(title_text="time relative to cursor (UI)", row=1, col=col)
        fig.update_yaxes(title_text="residual = distortion amplitude", row=1, col=col)

    fig.update_layout(
        title=(
            f"Why context = PRBS order:  one unresolved past symbol = two hidden waveforms  |  "
            f"PRBS{prbs_order}, weak tanh (gain={distortion_gain:.2f}), no noise<br>"
            "<sup>the only missing symbol still drives the causal channel, so the "
            f"{k_full - 1}-symbol average blends two states; the {k_full}-th symbol "
            "pins the state and the bins collapse</sup>"
        ),
        template="plotly_white",
        height=560,
        width=1300,
        margin={"t": 100},
        legend={"orientation": "h", "y": -0.16},
    )

    out = OUT_DIR / "context_identifiability_intuition.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def _pulse_memory_ui(
    pulse: np.ndarray, *, sps: int, max_ui: int, tol: float = 1e-6
) -> int:
    """Symmetric context length (UI) covering ``1 − tol`` of the SBR energy.

    Bins the single-bit-response energy into UI-wide bins relative to its peak
    (phase-robust — integrates the whole UI rather than a single phase sample)
    and returns the smallest odd window ``2W+1`` whose ``±W`` UI bins hold at
    least ``1 − tol`` of the total energy.  This is the channel memory ``M``
    (in context-UI units) the conditional-average estimator must span to
    resolve the linear ISI by "covering the memory".  ``tol = 1e-6`` was tuned
    so ``M`` matches the empirically observed cover-the-memory collapse
    context for short-memory channels.
    """
    p = np.asarray(pulse, dtype=np.float64)
    pk = int(np.argmax(np.abs(p)))
    ui_off = np.round((np.arange(len(p)) - pk) / sps).astype(int)
    energy = p**2
    total = float(energy.sum())
    if total <= 0.0:
        return 1
    for w in range(0, max_ui + 1):
        if energy[np.abs(ui_off) <= w].sum() / total >= 1.0 - tol:
            return 2 * w + 1
    return 2 * max_ui + 1


def figure_channel_memory_context_prbs9(
    *,
    distortion_gain: float = 0.05,
    loss_scales: list[float] | None = None,
    context_uis: list[int] | None = None,
) -> None:
    """Show how channel memory M and source order N interact (fixed PRBS9).

    Holds the source fixed at PRBS9 (state order N = 9), weak static tanh, and
    zero noise, then varies the **channel memory** M by scaling the
    skin-effect + dielectric loss budget.  For each channel the pattern-context
    window is swept and the leftover "noise" (fraction of the deterministic
    distortion *not* captured) is recorded on the exact-baseline residual.

    Prediction
    ----------
    The context length needed to drive the leftover to the floor is
    ``min(M, N)``:

    * short-memory channels (M < 9) collapse early, at context ≈ M — the window
      covers the entire linear memory, so the distortion is fully resolved even
      though the PRBS9 state is not yet identified;
    * long-memory channels (M ≥ 9) collapse at 9 — the window can no longer
      cover the memory, so the *source-state* identification (PRBS order) is
      what finally resolves it.

    This is the experiment that exposes the IR's role: it sets the ceiling M,
    and the collapse tracks M whenever M < N.
    """
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    pattern_min_hits = 4
    guard_ui = 20
    prbs_order = 9

    # Loss scales chosen (via a memory probe) to span M ≈ 3 → ≫ 9 around N = 9.
    loss_scales = list(
        loss_scales if loss_scales is not None else [0.10, 0.20, 0.22, 0.28, 0.33, 1.0]
    )
    contexts = list(
        context_uis if context_uis is not None else [3, 5, 7, 9, 11, 13, 15, 17]
    )
    for c in contexts:
        if c < 1 or c % 2 == 0:
            raise ValueError(f"context window must be a positive odd UI count, got {c}")

    collapse_frac = 1e-3  # leftover/distortion ratio defining "collapsed"

    records: list[dict] = []
    for scale in loss_scales:
        skin = 4.0 * scale
        diel = 2.0 * scale
        symbols, y, dist_true, _, pulse_true = _synthesise(
            n_sym=n_sym,
            sps=sps,
            pulse_span_ui=2 * ir_ui,
            distortion_gain=distortion_gain,
            noise_sigma=0.0,
            prbs_order=prbs_order,
            skin_loss_db=skin,
            dielectric_loss_db=diel,
        )
        m_ui = _pulse_memory_ui(pulse_true, sps=sps, max_ui=ir_ui, tol=1e-6)

        decomp = decompose_waveform(
            y, symbols, sps=sps, n_pre=n_pre, n_post=n_post,
            pattern_n_pre=2, pattern_n_post=2,
            pattern_min_hits=pattern_min_hits, guard_ui=guard_ui,
        )
        ya = decomp.y_aligned
        n = len(ya)
        lag = int(decomp.channel_estimate.lag_samples)
        cursor = int(decomp.channel_estimate.cursor)
        x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
        x_dirac[::sps] = symbols
        y_lin = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
        y_hat = np.zeros(n, dtype=np.float64)
        if lag < len(y_lin):
            n_copy = min(len(y_lin) - lag, n)
            y_hat[:n_copy] = y_lin[lag : lag + n_copy]
        residual = ya - y_hat
        sym = np.asarray(symbols, dtype=np.float64)
        g = guard_ui * sps
        region = slice(g, n - g)
        ms = lambda arr: float(np.mean(arr[region] ** 2))  # noqa: E731
        p_dt = ms(dist_true) if ms(dist_true) > 0 else ms(residual)

        fracs: list[float] = []
        for L in contexts:
            pre = (L - 1) // 2
            post = (L - 1) - pre
            y_dist, _, _, _ = _pattern_average_distortion(
                residual, sym, sps=sps,
                cursor_phase=cursor % sps, cursor_ui_offset=cursor // sps,
                pattern_n_pre=pre, pattern_n_post=post,
                pattern_min_hits=pattern_min_hits,
            )
            y_noise = residual - y_dist
            fracs.append(float(np.sqrt(ms(y_noise) / p_dt)) if p_dt > 0 else float("nan"))

        collapse_L = next((L for L, f in zip(contexts, fracs) if f < collapse_frac), None)
        records.append(
            {"scale": scale, "skin": skin, "M": m_ui, "fracs": fracs,
             "collapse_L": collapse_L, "dist_rms": float(np.sqrt(p_dt))}
        )
        print(
            f"scale={scale:4.2f} skin={skin:4.1f}dB  M={m_ui:2d} UI  "
            f"distRMS={np.sqrt(p_dt):.2e}  collapse@={collapse_L}  "
            f"leftover_frac={['%.1e' % f for f in fracs]}"
        )

    order_colors = ["#4575b4", "#74add1", "#66bd63", "#fdae61", "#f46d43", "#d73027"]
    if len(records) > len(order_colors):
        order_colors = order_colors * (len(records) // len(order_colors) + 1)

    fig = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.10,
        subplot_titles=[
            "Leftover distortion fraction vs context  (fixed PRBS9, varied channel memory M)",
            "Collapse context vs channel memory M  →  collapse = min(M, N=9)",
        ],
    )

    for rec, color in zip(records, order_colors[: len(records)], strict=True):
        fig.add_trace(
            go.Scatter(
                x=contexts, y=rec["fracs"], mode="lines+markers",
                name=f"M={rec['M']} UI  (skin={rec['skin']:.1f} dB)",
                line={"color": color, "width": 2}, marker={"size": 7},
            ),
            row=1, col=1,
        )
    fig.add_vline(
        x=prbs_order, line={"color": "gray", "dash": "dash", "width": 1.2}, row=1, col=1,
    )
    fig.add_annotation(
        x=prbs_order, y=0.0, xref="x1", yref="paper",
        text="PRBS9 order N = 9", showarrow=False, yshift=10,
        font={"color": "gray", "size": 11},
    )

    # Panel 2: collapse context vs M with the min(M, N) reference.
    m_axis = np.linspace(0, max(20, prbs_order + 2), 200)
    ref = np.minimum(m_axis, prbs_order)
    fig.add_trace(
        go.Scatter(
            x=m_axis.tolist(), y=ref.tolist(), mode="lines",
            name="min(M, N=9) prediction",
            line={"color": "black", "width": 1.5, "dash": "dash"},
        ),
        row=1, col=2,
    )
    m_clip = 19
    for rec, color in zip(records, order_colors[: len(records)], strict=True):
        if rec["collapse_L"] is None:
            continue
        mx = min(rec["M"], m_clip)
        fig.add_trace(
            go.Scatter(
                x=[mx], y=[rec["collapse_L"]], mode="markers",
                name=f"M={rec['M']}", legendgroup=f"M={rec['M']}", showlegend=False,
                marker={"size": 13, "color": color, "line": {"color": "black", "width": 1}},
                hovertemplate=f"M={rec['M']} UI<br>collapse={rec['collapse_L']} UI<extra></extra>",
            ),
            row=1, col=2,
        )
        if rec["M"] > m_clip:
            fig.add_annotation(
                x=mx, y=rec["collapse_L"], xref="x2", yref="y2",
                text=f"M={rec['M']} (≫N)", showarrow=False, yshift=-16,
                font={"color": color, "size": 10},
            )

    fig.update_yaxes(title_text="leftover / distortion RMS (log)", type="log", row=1, col=1)
    fig.update_xaxes(title_text="context window (UI)", dtick=2, row=1, col=1)
    fig.update_yaxes(title_text="collapse context (UI)", dtick=2, row=1, col=2)
    fig.update_xaxes(title_text="channel memory M (UI, taps clipped at 19)", dtick=2, row=1, col=2)
    fig.update_layout(
        title=(
            "Channel memory M vs source order N:  collapse context = min(M, N)  |  "
            f"PRBS9, weak tanh (gain={distortion_gain:.2f}), no noise<br>"
            "<sup>short-memory channels collapse at ≈M (window covers the ISI); "
            "long-memory channels collapse at N=9 (source-state identification)</sup>"
        ),
        template="plotly_white", height=540, width=1300, margin={"t": 110},
        legend={"orientation": "h", "y": -0.18, "title": {"text": "channel  "}},
    )

    out = OUT_DIR / "channel_memory_vs_context_prbs9.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def _figure_channel_memory_context_random(
    *,
    source: Literal["iid", "prbs"],
    prbs_order: int = 31,
    distortion_gain: float = 0.05,
    loss_scales: list[float] | None = None,
    context_uis: list[int] | None = None,
) -> None:
    """M-vs-N sweep for a *high-entropy* source (IID or a long PRBS).

    Identical to :func:`figure_channel_memory_context_prbs9` (same channels,
    contexts, gain, exact baseline, no noise) **except the source has no
    in-window state**:

    * ``source="iid"`` — IID random ±1, generating-state order N → ∞;
    * ``source="prbs"`` — PRBS of order ``prbs_order`` (e.g. 31).  With only a
      few hundred-k symbols (≪ the ``2**N − 1`` period) and a context sweep that
      tops out well below ``N``, the N-bit state is never identifiable in-window,
      so the PRBS looks statistically IID over the record.

    Either way the source-state identification route to collapse is unreachable,
    so the only remaining route is "cover the memory".

    Prediction
    ----------
    The collapse law ``min(M, N)`` degenerates to ``collapse = M`` (since the
    in-reach ``N`` is effectively ∞), bounded above by **data starvation**:
    conditioning on ``L`` symbols creates ``2**L`` distinct patterns, each
    recurring ``≈ n_sym / 2**L`` times.  Once ``2**L`` approaches
    ``n_sym / pattern_min_hits`` the bins stop recurring often enough to be
    estimated, so memory that needs a window past that wall can never be covered.

    * short-memory channels (M below the starvation wall) still collapse, now at
      exactly ``M`` — and *only* at ``M`` (no early collapse, since there is no
      state to identify in-window);
    * the long-memory channel that collapsed at 9 under PRBS9 **does not collapse
      at all** here — without an in-window state there is no shortcut, and
      covering its memory would need an unreachable context.
    """
    sps = 8
    n_sym = 500 * 512
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    pattern_min_hits = 4
    guard_ui = 20

    src_label = "IID" if source == "iid" else f"PRBS{prbs_order}"

    loss_scales = list(
        loss_scales if loss_scales is not None else [0.10, 0.20, 0.22, 0.28, 0.33, 1.0]
    )
    contexts = list(
        context_uis if context_uis is not None else [3, 5, 7, 9, 11, 13, 15, 17]
    )
    for c in contexts:
        if c < 1 or c % 2 == 0:
            raise ValueError(f"context window must be a positive odd UI count, got {c}")

    collapse_frac = 1e-3
    # Context past which patterns stop recurring ≥ pattern_min_hits times.
    starve_L = float(np.log2(n_sym / pattern_min_hits))

    records: list[dict] = []
    for scale in loss_scales:
        skin = 4.0 * scale
        diel = 2.0 * scale
        symbols, y, dist_true, _, pulse_true = _synthesise(
            n_sym=n_sym,
            sps=sps,
            pulse_span_ui=2 * ir_ui,
            distortion_gain=distortion_gain,
            noise_sigma=0.0,
            source=source,
            prbs_order=prbs_order,
            skin_loss_db=skin,
            dielectric_loss_db=diel,
        )
        m_ui = _pulse_memory_ui(pulse_true, sps=sps, max_ui=ir_ui, tol=1e-6)

        decomp = decompose_waveform(
            y, symbols, sps=sps, n_pre=n_pre, n_post=n_post,
            pattern_n_pre=2, pattern_n_post=2,
            pattern_min_hits=pattern_min_hits, guard_ui=guard_ui,
        )
        ya = decomp.y_aligned
        n = len(ya)
        lag = int(decomp.channel_estimate.lag_samples)
        cursor = int(decomp.channel_estimate.cursor)
        x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
        x_dirac[::sps] = symbols
        y_lin = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
        y_hat = np.zeros(n, dtype=np.float64)
        if lag < len(y_lin):
            n_copy = min(len(y_lin) - lag, n)
            y_hat[:n_copy] = y_lin[lag : lag + n_copy]
        residual = ya - y_hat
        sym = np.asarray(symbols, dtype=np.float64)
        g = guard_ui * sps
        region = slice(g, n - g)
        ms = lambda arr: float(np.mean(arr[region] ** 2))  # noqa: E731
        p_dt = ms(dist_true) if ms(dist_true) > 0 else ms(residual)

        fracs: list[float] = []
        for L in contexts:
            pre = (L - 1) // 2
            post = (L - 1) - pre
            y_dist, _, _, _ = _pattern_average_distortion(
                residual, sym, sps=sps,
                cursor_phase=cursor % sps, cursor_ui_offset=cursor // sps,
                pattern_n_pre=pre, pattern_n_post=post,
                pattern_min_hits=pattern_min_hits,
            )
            y_noise = residual - y_dist
            fracs.append(float(np.sqrt(ms(y_noise) / p_dt)) if p_dt > 0 else float("nan"))

        collapse_L = next((L for L, f in zip(contexts, fracs) if f < collapse_frac), None)
        records.append(
            {"scale": scale, "skin": skin, "M": m_ui, "fracs": fracs,
             "collapse_L": collapse_L, "dist_rms": float(np.sqrt(p_dt))}
        )
        print(
            f"scale={scale:4.2f} skin={skin:4.1f}dB  M={m_ui:2d} UI  "
            f"distRMS={np.sqrt(p_dt):.2e}  collapse@={collapse_L}  "
            f"leftover_frac={['%.1e' % f for f in fracs]}"
        )

    order_colors = ["#4575b4", "#74add1", "#66bd63", "#fdae61", "#f46d43", "#d73027"]
    if len(records) > len(order_colors):
        order_colors = order_colors * (len(records) // len(order_colors) + 1)

    col2_title = (
        "Collapse context vs channel memory M  →  collapse = M  (no source-state cap)"
        if source == "iid"
        else f"Collapse context vs channel memory M  →  collapse = min(M, N={prbs_order})"
    )
    fig = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.10,
        subplot_titles=[
            f"Leftover distortion fraction vs context  ({src_label} source, varied channel memory M)",
            col2_title,
        ],
    )

    for rec, color in zip(records, order_colors[: len(records)], strict=True):
        fig.add_trace(
            go.Scatter(
                x=contexts, y=rec["fracs"], mode="lines+markers",
                name=f"M={rec['M']} UI  (skin={rec['skin']:.1f} dB)",
                line={"color": color, "width": 2}, marker={"size": 7},
            ),
            row=1, col=1,
        )
    fig.add_vline(
        x=starve_L, line={"color": "purple", "dash": "dot", "width": 1.2}, row=1, col=1,
    )
    fig.add_annotation(
        x=starve_L, y=1.0, xref="x1", yref="paper",
        text="data-starvation wall<br>2<sup>L</sup> ≈ N_sym/min_hits",
        showarrow=False, yshift=-2, xshift=-4, xanchor="right",
        font={"color": "purple", "size": 10},
    )

    # Panel 2: collapse context vs M with the collapse = min(M, N) reference.
    # For IID, N → ∞ so the reference is the bare diagonal y = M.  For a long
    # PRBS, N = prbs_order; within the plotted x-range (≤19 ≪ 31) this is also
    # just y = M, so a high-order PRBS reproduces the IID behaviour.
    m_axis = np.linspace(0, 19, 200)
    ref_y = m_axis if source == "iid" else np.minimum(m_axis, float(prbs_order))
    ref_name = "collapse = M  (N → ∞)" if source == "iid" else f"collapse = min(M, N={prbs_order})"
    fig.add_trace(
        go.Scatter(
            x=m_axis.tolist(), y=np.asarray(ref_y).tolist(), mode="lines",
            name=ref_name,
            line={"color": "black", "width": 1.5, "dash": "dash"},
        ),
        row=1, col=2,
    )
    fig.add_hline(
        y=starve_L, line={"color": "purple", "dash": "dot", "width": 1.2}, row=1, col=2,
    )
    fig.add_annotation(
        x=0.0, y=starve_L, xref="x2", yref="y2",
        text="starvation wall", showarrow=False, yshift=9, xanchor="left",
        font={"color": "purple", "size": 10},
    )
    m_clip = 19
    for rec, color in zip(records, order_colors[: len(records)], strict=True):
        mx = min(rec["M"], m_clip)
        if rec["collapse_L"] is None:
            # No collapse within the sweep: park it at the top, annotate.
            fig.add_trace(
                go.Scatter(
                    x=[mx], y=[max(contexts) + 1.5], mode="markers",
                    name=f"M={rec['M']}", showlegend=False,
                    marker={"size": 13, "color": color, "symbol": "x-thin",
                            "line": {"color": color, "width": 2}},
                    hovertemplate=f"M={rec['M']} UI<br>no collapse<extra></extra>",
                ),
                row=1, col=2,
            )
            fig.add_annotation(
                x=mx, y=max(contexts) + 1.5, xref="x2", yref="y2",
                text=f"M={rec['M']}<br>no collapse", showarrow=False, yshift=0, xshift=-12,
                xanchor="right", font={"color": color, "size": 10},
            )
            continue
        fig.add_trace(
            go.Scatter(
                x=[mx], y=[rec["collapse_L"]], mode="markers",
                name=f"M={rec['M']}", showlegend=False,
                marker={"size": 13, "color": color, "line": {"color": "black", "width": 1}},
                hovertemplate=f"M={rec['M']} UI<br>collapse={rec['collapse_L']} UI<extra></extra>",
            ),
            row=1, col=2,
        )

    fig.update_yaxes(title_text="leftover / distortion RMS (log)", type="log", row=1, col=1)
    fig.update_xaxes(title_text="context window (UI)", dtick=2, row=1, col=1)
    fig.update_yaxes(title_text="collapse context (UI)", dtick=2, row=1, col=2)
    fig.update_xaxes(title_text="channel memory M (UI, taps clipped at 19)", dtick=2, row=1, col=2)
    if source == "iid":
        title = (
            "IID source (N → ∞): the PRBS shortcut is gone, so collapse = M  |  "
            f"weak tanh (gain={distortion_gain:.2f}), no noise<br>"
            "<sup>collapse now happens only by covering the memory (at exactly M), "
            "bounded above by data starvation; the long-memory channel never collapses</sup>"
        )
        out_name = "channel_memory_vs_context_iid.png"
    else:
        title = (
            f"PRBS{prbs_order} (N={prbs_order} ≫ window): behaves like IID, so collapse = M  |  "
            f"weak tanh (gain={distortion_gain:.2f}), no noise<br>"
            f"<sup>with only {n_sym // 1000}k symbols the {prbs_order}-bit state is never "
            "identifiable in-window; collapse is set by the memory M and bounded by "
            "data starvation, just like IID</sup>"
        )
        out_name = f"channel_memory_vs_context_prbs{prbs_order}.png"
    fig.update_layout(
        title=title,
        template="plotly_white", height=540, width=1300, margin={"t": 110},
        legend={"orientation": "h", "y": -0.18, "title": {"text": "channel  "}},
    )

    out = OUT_DIR / out_name
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


def figure_channel_memory_context_iid(
    *,
    distortion_gain: float = 0.05,
    loss_scales: list[float] | None = None,
    context_uis: list[int] | None = None,
) -> None:
    """IID-source M-vs-N sweep (N → ∞): collapse = M, capped by data starvation."""
    _figure_channel_memory_context_random(
        source="iid",
        distortion_gain=distortion_gain,
        loss_scales=loss_scales,
        context_uis=context_uis,
    )


def figure_channel_memory_context_prbs31(
    *,
    distortion_gain: float = 0.05,
    loss_scales: list[float] | None = None,
    context_uis: list[int] | None = None,
) -> None:
    """PRBS31 M-vs-N sweep: N=31 ≫ window, so it reproduces the IID behaviour."""
    _figure_channel_memory_context_random(
        source="prbs",
        prbs_order=31,
        distortion_gain=distortion_gain,
        loss_scales=loss_scales,
        context_uis=context_uis,
    )


def figure_predicted_floor_vs_ir(
    *,
    distortion_gain: float = 0.05,
    loss_scales: list[float] | None = None,
    context_uis: list[int] | None = None,
    n_sym: int = 500 * 512,
    out_suffix: str = "",
) -> None:
    """Predict the pre-collapse noise floor from the IR taps alone.

    The leftover "noise" before the collapse is the first-order distortion
    response to the **uncovered ISI**.  At context ``L = 2W+1`` the symbols
    outside the window contribute a linear component

        u_W(t) = Σ_{|k|>W} a[m−k] · p_k

    which is exactly ``conv(symbols, pulse)`` computed with the pulse's central
    ``±W`` UI zeroed.  A first-order expansion of the static nonlinearity
    ``g(y) = tanh(α y)/tanh(α) − y`` about the covered value gives

        leftover(L) ≈ RMS( g'(y_lin) · u_W ),   g'(y) = (α/tanh α) sech²(α y) − 1.

    This prediction uses only the planted IR and the known nonlinearity — no
    fit.  It should overlay the measured leftover across the whole descent and
    the collapse (``u_W → 0`` once the window covers the memory), and diverge
    only where **data starvation** (not the IR) drives the measured floor back
    up.  An IID source is used so no PRBS state-identification confounds the
    descent.
    """
    sps = 8
    n_sym = int(n_sym)
    ir_ui = 25
    n_pre = ir_ui
    n_post = ir_ui
    pattern_min_hits = 4
    guard_ui = 20

    # Three memories spanning the regime: short, medium, long.
    loss_scales = list(loss_scales if loss_scales is not None else [0.20, 0.33, 1.0])
    contexts = list(
        context_uis if context_uis is not None else [3, 5, 7, 9, 11, 13, 15, 17]
    )
    for c in contexts:
        if c < 1 or c % 2 == 0:
            raise ValueError(f"context window must be a positive odd UI count, got {c}")

    alpha = float(distortion_gain)
    tanh_a = float(np.tanh(alpha))
    starve_L = float(np.log2(n_sym / pattern_min_hits))

    records: list[dict] = []
    for scale in loss_scales:
        skin = 4.0 * scale
        diel = 2.0 * scale
        symbols, y, dist_true, _, pulse_true = _synthesise(
            n_sym=n_sym, sps=sps, pulse_span_ui=2 * ir_ui,
            distortion_gain=alpha, noise_sigma=0.0, source="iid",
            skin_loss_db=skin, dielectric_loss_db=diel,
        )
        m_ui = _pulse_memory_ui(pulse_true, sps=sps, max_ui=ir_ui, tol=1e-6)

        decomp = decompose_waveform(
            y, symbols, sps=sps, n_pre=n_pre, n_post=n_post,
            pattern_n_pre=2, pattern_n_post=2,
            pattern_min_hits=pattern_min_hits, guard_ui=guard_ui,
        )
        ya = decomp.y_aligned
        n = len(ya)
        lag = int(decomp.channel_estimate.lag_samples)
        cursor = int(decomp.channel_estimate.cursor)
        x_dirac = np.zeros(len(symbols) * sps, dtype=np.float64)
        x_dirac[::sps] = symbols

        def _align(full: np.ndarray) -> np.ndarray:
            out = np.zeros(n, dtype=np.float64)
            if lag < len(full):
                nc = min(len(full) - lag, n)
                out[:nc] = full[lag : lag + nc]
            return out

        y_lin_full = np.convolve(x_dirac, pulse_true)[: len(x_dirac)]
        y_hat = _align(y_lin_full)
        residual = ya - y_hat
        sym = np.asarray(symbols, dtype=np.float64)
        g = guard_ui * sps
        region = slice(g, n - g)
        ms = lambda arr: float(np.mean(arr[region] ** 2))  # noqa: E731

        # First-order distortion slope g'(y_lin) on the aligned grid.
        gprime = (alpha / tanh_a) / np.cosh(alpha * y_hat) ** 2 - 1.0

        # Symbol-spaced tap profile for the IR panel.
        pk = int(np.argmax(np.abs(pulse_true)))
        ks = np.arange(-2, ir_ui + 1)
        taps = np.array(
            [pulse_true[pk + k * sps] if 0 <= pk + k * sps < len(pulse_true) else 0.0
             for k in ks],
            dtype=np.float64,
        )
        ui_off_pulse = np.round((np.arange(len(pulse_true)) - pk) / sps).astype(int)

        measured: list[float] = []
        predicted: list[float] = []
        for L in contexts:
            W = (L - 1) // 2
            pre = W
            post = (L - 1) - pre
            # Measured leftover (absolute RMS).
            y_dist, _, _, _ = _pattern_average_distortion(
                residual, sym, sps=sps,
                cursor_phase=cursor % sps, cursor_ui_offset=cursor // sps,
                pattern_n_pre=pre, pattern_n_post=post,
                pattern_min_hits=pattern_min_hits,
            )
            measured.append(float(np.sqrt(ms(residual - y_dist))))
            # Predicted leftover from the uncovered ISI: zero central ±W UI.
            pulse_tail = pulse_true.copy()
            pulse_tail[np.abs(ui_off_pulse) <= W] = 0.0
            u = _align(np.convolve(x_dirac, pulse_tail)[: len(x_dirac)])
            predicted.append(float(np.sqrt(ms(gprime * u))))

        records.append(
            {"scale": scale, "skin": skin, "M": m_ui,
             "measured": measured, "predicted": predicted,
             "ks": ks.tolist(), "taps": np.abs(taps).tolist()}
        )
        print(
            f"scale={scale:4.2f} skin={skin:4.1f}dB M={m_ui:2d}  "
            f"measured={['%.1e' % v for v in measured]}  "
            f"predicted={['%.1e' % v for v in predicted]}"
        )

    colors = ["#66bd63", "#f46d43", "#d73027"]
    if len(records) > len(colors):
        colors = colors * (len(records) // len(colors) + 1)

    fig = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.11,
        subplot_titles=[
            "Leftover noise RMS: measured vs predicted-from-IR (IID, no noise)",
            "Symbol-spaced IR tap magnitude |p_k| (sets the floor decay)",
        ],
    )

    for rec, color in zip(records, colors[: len(records)], strict=True):
        fig.add_trace(
            go.Scatter(
                x=contexts, y=rec["measured"], mode="markers",
                name=f"M={rec['M']} UI measured",
                marker={"size": 10, "color": color,
                        "line": {"color": "black", "width": 1}},
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=contexts, y=rec["predicted"], mode="lines",
                name=f"M={rec['M']} UI predicted (IR)",
                line={"color": color, "width": 2, "dash": "dash"},
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=rec["ks"], y=rec["taps"], mode="lines",
                name=f"M={rec['M']} UI", showlegend=False,
                line={"color": color, "width": 2},
            ),
            row=1, col=2,
        )

    fig.add_vline(
        x=starve_L, line={"color": "purple", "dash": "dot", "width": 1.2}, row=1, col=1,
    )
    fig.add_annotation(
        x=starve_L, y=1.0, xref="x1", yref="paper",
        text="starvation wall<br>(IR model breaks)", showarrow=False,
        yshift=-2, xshift=-4, xanchor="right", font={"color": "purple", "size": 10},
    )

    fig.update_yaxes(
        title_text="leftover noise RMS (log)", type="log",
        range=[-6.5, -3.3], row=1, col=1,
    )
    fig.update_xaxes(title_text="context window (UI)", dtick=2, row=1, col=1)
    fig.update_yaxes(title_text="|p_k|  (log)", type="log", row=1, col=2)
    fig.update_xaxes(
        title_text="symbol offset k from cursor (UI)", dtick=4,
        range=[-2.5, 16], row=1, col=2,
    )
    fig.add_annotation(
        x=0.0, y=0.0, xref="x domain", yref="paper",
        text="(collapsed points fall below axis → 0)", showarrow=False,
        yshift=14, xshift=4, xanchor="left", font={"color": "gray", "size": 9},
    )
    fig.update_layout(
        title=(
            "Pre-collapse noise floor is predicted by the IR taps  |  "
            f"weak tanh (gain={alpha:.2f}), no noise, IID, N_sym={n_sym/1000:g}k<br>"
            "<sup>predicted = RMS(g'(y_lin)·u_W), u_W = ISI from symbols outside the "
            f"±W-UI window; measured tracks it until the starvation wall (~{starve_L:.0f} UI)</sup>"
        ),
        template="plotly_white", height=540, width=1300, margin={"t": 110},
        legend={"orientation": "h", "y": -0.18},
    )

    out = OUT_DIR / f"predicted_floor_vs_ir{out_suffix}.png"
    fig.write_image(str(out), scale=1.6)
    print(f"saved → {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    figure_synthetic_recovery(linear_mode=SYNTHETIC_LINEAR_MODE)
    figure_synthetic_pattern_windows()
    figure_pattern_00110_window_selection()
    figure_pkctrl3_block_comparison()
    figure_distortion_sigma_vs_noise_sigma()
    figure_prbs13_5ui_histogram()
    figure_distortion_error_heatmap()
    figure_distortion_error_vs_sequence_no_noise()
    figure_nonlinearity_gain_sweep()
    figure_prbs_order_context_sweep()
    figure_context_identifiability_intuition()
    figure_channel_memory_context_prbs9()
    figure_channel_memory_context_iid()
    figure_channel_memory_context_prbs31()
    figure_predicted_floor_vs_ir()
