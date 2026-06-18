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
from scipy import signal
from plotly.subplots import make_subplots

from optical_serdes.analysis import decompose_waveform
from optical_serdes.analysis.waveform_decomposition import _pattern_average_distortion
from optical_serdes.tx.waveform import generate_prbs

OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SYNTHETIC_LINEAR_MODE: Literal["wiener", "exact"] = "exact"


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
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build a synthetic waveform with a known LTI + distortion + noise split."""
    rng = np.random.default_rng(seed)
    # Use a deterministic PRBS13 source sequence with requested length.
    prbs_bits = generate_prbs(order=13, n_bits=n_sym)
    symbols = (2.0 * prbs_bits.astype(np.float64)) - 1.0

    # Smooth, low-ripple pulse from a digital Bessel LPF impulse response.
    # Frequencies are in cycles/UI because fs = sps [samples/UI].
    pulse_order = 5
    f3db_cyc_per_ui = 0.42
    b, a = signal.bessel(
        pulse_order,
        f3db_cyc_per_ui,
        btype="lowpass",
        analog=False,
        norm="mag",
        fs=float(sps),
    )
    n_imp = pulse_span_ui * sps + 1
    _, h_imp = signal.dimpulse((b, a, 1.0 / float(sps)), n=n_imp)
    pulse = np.asarray(h_imp[0], dtype=np.float64).ravel()
    pulse = pulse / np.max(np.abs(pulse))

    x = np.zeros(n_sym * sps, dtype=np.float64)
    x[::sps] = symbols
    y_linear = np.convolve(x, pulse)[: len(x)]
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
    m = decomp.metrics

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

    fig = make_subplots(
        rows=4,
        cols=2,
        shared_xaxes=False,
        vertical_spacing=0.06,
        horizontal_spacing=0.08,
        specs=[
            [{"colspan": 2}, None],
            [{}, {}],
            [{"colspan": 2}, None],
            [{"colspan": 2}, None],
        ],
        subplot_titles=[
            f"Captured y vs linear prediction ŷ  ({linear_mode})",
            row2_title,
            f"Linear-filter delta ({linear_mode}): RMS={delta_rms:.3e}",
            "Distortion: actual nonlinear waveform vs recovered estimate",
            "Noise:         recovered (green)   vs   true (grey)",
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

    fig.update_xaxes(title_text="time (UI)", row=4, col=1)
    fig.update_xaxes(title_text="impulse time (UI)", row=2, col=1)
    fig.update_xaxes(title_text="impulse time (UI)", row=2, col=2)
    fig.update_xaxes(range=[-ir_plot_ui, ir_plot_ui], row=2, col=1)
    fig.update_xaxes(range=[-ir_plot_ui, ir_plot_ui], row=2, col=2)
    fig.update_yaxes(title_text="amplitude", row=1, col=1)
    fig.update_yaxes(title_text="amplitude", row=2, col=1)
    fig.update_yaxes(title_text="amplitude", row=2, col=2)
    fig.update_yaxes(title_text="amplitude", row=3, col=1)
    fig.update_yaxes(title_text="amplitude", row=4, col=1)

    fig.update_layout(
        title=(
            f"Synthetic decomposition recovery ({linear_mode})   |   SNDR={m.sndr_db:.1f} dB    "
            f"SDR={m.sdr_db:.1f} dB    SNR={m.snr_db:.1f} dB    "
            f"closure={m.closure_rms:.1e}"
        ),
        template="plotly_white",
        height=1000,
        width=1200,
        showlegend=True,
        legend={"orientation": "h", "y": -0.08},
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


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    figure_synthetic_recovery(linear_mode=SYNTHETIC_LINEAR_MODE)
    figure_synthetic_pattern_windows()
    figure_pkctrl3_block_comparison()
    figure_distortion_sigma_vs_noise_sigma()
    figure_prbs13_5ui_histogram()
    figure_distortion_error_heatmap()
