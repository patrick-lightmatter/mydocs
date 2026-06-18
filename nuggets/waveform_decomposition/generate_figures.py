"""Generate static figures for the waveform-decomposition nugget.

Produces:
    figures/synthetic_decomposition.png    — recovery on a known synthetic signal
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
    figure_pkctrl3_block_comparison()
