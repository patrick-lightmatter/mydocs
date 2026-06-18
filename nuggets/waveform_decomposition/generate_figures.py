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

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from optical_serdes.analysis import decompose_waveform

OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Figure 1 — synthetic recovery on a known signal
# ─────────────────────────────────────────────────────────────────────────────


def _synthesise(
    n_sym: int = 6000,
    sps: int = 8,
    distortion_gain: float = 1.1,
    noise_sigma: float = 0.02,
    seed: int = 7,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build a synthetic waveform with a known LTI + distortion + noise split."""
    rng = np.random.default_rng(seed)
    symbols = rng.choice([-1.0, 1.0], size=n_sym)
    half = 2 * sps
    t = np.arange(-half, half + 1) / sps
    pulse = np.sinc(t) * np.exp(-((t / 2.0) ** 2))
    x = np.zeros(n_sym * sps, dtype=np.float64)
    x[::sps] = symbols
    y_linear = np.convolve(x, pulse)[: len(x)]
    y_nonlinear = np.tanh(distortion_gain * y_linear) / np.tanh(distortion_gain)
    distortion_true = y_nonlinear - y_linear
    noise_true = rng.normal(0.0, noise_sigma, size=len(y_nonlinear))
    y = y_nonlinear + noise_true
    return symbols, y, distortion_true, noise_true


def figure_synthetic_recovery() -> None:
    sps = 8
    symbols, y, dist_true, noise_true = _synthesise(sps=sps)
    decomp = decompose_waveform(
        y,
        symbols,
        sps=sps,
        n_pre=4,
        n_post=8,
        pattern_n_pre=2,
        pattern_n_post=2,
        pattern_min_hits=4,
        guard_ui=20,
    )
    m = decomp.metrics

    g = 200 * sps
    plot_len = 120 * sps
    sl = slice(g, g + plot_len)
    t_ui = (np.arange(plot_len) / sps).tolist()

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=[
            "Captured y vs linear prediction ŷ",
            "Linear split:  y_desired = h₀·ZOH(a)   vs   y_ISI = ŷ − y_desired",
            "Distortion:    recovered (red)   vs   true (grey)",
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
        go.Scatter(x=t_ui, y=decomp.y_hat[sl].tolist(),
                   mode="lines", name="ŷ (linear fit)",
                   line={"color": "darkorange", "width": 1, "dash": "dash"}),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(x=t_ui, y=decomp.y_desired[sl].tolist(),
                   mode="lines", name="y_desired",
                   line={"color": "steelblue", "width": 1}),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_ui, y=decomp.y_isi[sl].tolist(),
                   mode="lines", name="y_ISI",
                   line={"color": "darkorange", "width": 1}),
        row=2, col=1,
    )

    fig.add_trace(
        go.Scatter(x=t_ui, y=decomp.y_distortion[sl].tolist(),
                   mode="lines", name="d̂(t) recovered",
                   line={"color": "crimson", "width": 1.2}),
        row=3, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_ui, y=dist_true[sl].tolist(),
                   mode="lines", name="d(t) true",
                   line={"color": "black", "width": 0.6}, opacity=0.55),
        row=3, col=1,
    )

    fig.add_trace(
        go.Scatter(x=t_ui, y=decomp.y_noise[sl].tolist(),
                   mode="lines", name="n̂(t) recovered",
                   line={"color": "mediumseagreen", "width": 0.7}),
        row=4, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_ui, y=noise_true[sl].tolist(),
                   mode="lines", name="n(t) true",
                   line={"color": "black", "width": 0.5}, opacity=0.5),
        row=4, col=1,
    )

    fig.update_xaxes(title_text="time (UI)", row=4, col=1)
    for r in (1, 2, 3, 4):
        fig.update_yaxes(title_text="amplitude", row=r, col=1)

    fig.update_layout(
        title=(
            f"Synthetic decomposition recovery   |   SNDR={m.sndr_db:.1f} dB    "
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
    symbols, y, _, _ = _synthesise(n_sym=9000, sps=sps)
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


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    figure_synthetic_recovery()
    figure_synthetic_pattern_windows()
    figure_pkctrl3_block_comparison()
