"""
Phase delay analysis on measured Colossus S4P channels.

Loads two 4-port Touchstone files, extracts Sdd21 (13_24 convention),
and applies the same GD/PD + eye diagram analysis used in the primer
(phase_delay_report.py) to show what the abstract phase families look
like in a real, measured channel.

Output: /home/patrick/mydocs/nuggets/group_delay_variation/channels/
  channels_gd_pd.{png,html}   — GD and PD vs frequency, both channels
  channels_ir.{png,html}       — impulse response overlay
  channels_eyes.{png,html}     — side-by-side eye diagrams

Usage:
  python scripts/phase_delay/colossus_channel_phase_analysis.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import plotly.graph_objects as go            # noqa: E402
from plotly.subplots import make_subplots    # noqa: E402

from optical_serdes.channel.fd_channel import fd_channel_from_touchstone   # noqa: E402
from optical_serdes.channel.to_discrete_ir import discrete_impulse_response  # noqa: E402
from optical_serdes.tx.waveform import generate_prbs                        # noqa: E402

# ── Channels ──────────────────────────────────────────────────────────────────
CHANNELS = {
    "IL15 (v2)": Path("/lm/analog/colossus/channels/l20_il15_rl17_90ohms_100ports_v2.s4p"),
    "IL18 (v1)": Path("/lm/analog/colossus/channels/l20_il18_rl15_90ohms_100ports_v1.s4p"),
}

COLOURS = {
    "IL15 (v2)": "#0070d4",
    "IL18 (v1)": "#e07020",
}

# ── Simulation constants (matching phase_delay_report.py) ────────────────────
DATA_RATE  = 106.25e9
UI         = 1.0 / DATA_RATE
F_NYQ      = DATA_RATE / 2.0          # 53.125 GHz
SPS        = 32
FS         = DATA_RATE * SPS           # 3.4 THz
DT         = 1.0 / FS
N_FFT      = 2**18
F_EVAL_MIN = 5e9

# ── Output ────────────────────────────────────────────────────────────────────
OUT = Path("/home/patrick/mydocs/nuggets/group_delay_variation/channels")
OUT.mkdir(parents=True, exist_ok=True)


# ═════════════════════════════════════════════════════════════════════════════
# Utilities
# ═════════════════════════════════════════════════════════════════════════════

def save(fig: go.Figure, stem: str, w: int = 1200, h: int = 600) -> str:
    fig.write_html(str(OUT / f"{stem}.html"))
    fig.write_image(str(OUT / f"{stem}.png"), width=w, height=h, scale=2)
    print(f"  {stem}.png")
    return f"channels/{stem}.png"


def _grid(fig: go.Figure) -> None:
    fig.update_xaxes(gridcolor="#eeeeee", zerolinecolor="#cccccc")
    fig.update_yaxes(gridcolor="#eeeeee", zerolinecolor="#cccccc")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")


def interpolate_onto_rfft_grid(
    f_src: np.ndarray,
    h_src: np.ndarray,
    n_fft: int = N_FFT,
    fs: float = FS,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Interpolate complex H onto the uniform rfft frequency grid used by
    the primer.  Below the source's f_min hold the first value; above
    f_max hold zero (beyond measurement bandwidth).
    """
    f_dst = np.fft.rfftfreq(n_fft, d=1.0 / fs)
    h_re  = np.interp(f_dst, f_src, h_src.real,
                      left=h_src[0].real, right=0.0)
    h_im  = np.interp(f_dst, f_src, h_src.imag,
                      left=h_src[0].imag, right=0.0)
    return f_dst, h_re + 1j * h_im


def compute_delays(
    f: np.ndarray,
    H: np.ndarray,
    f_min: float = F_EVAL_MIN,
    f_max: float = F_NYQ,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (f_eval_ghz, tau_g_ps, tau_p_ps) over [f_min, f_max]."""
    omega = 2 * np.pi * f
    phi   = np.unwrap(np.angle(H))
    tau_g = -np.gradient(phi, omega)
    with np.errstate(divide="ignore", invalid="ignore"):
        tau_p = np.where(omega > 0, -phi / omega, np.nan)

    mask  = (f >= f_min) & (f <= f_max)
    return f[mask] / 1e9, tau_g[mask] * 1e12, tau_p[mask] * 1e12


def baud_tap(h: np.ndarray, peak: int, offset_ui: int, sps: int = SPS) -> float:
    idx = peak + offset_ui * sps
    if 0 <= idx < len(h):
        return float(abs(h[idx]) / abs(h[peak]))
    return 0.0


# ═════════════════════════════════════════════════════════════════════════════
# Figure 1 — GD and PD vs frequency  (2 rows × 2 cols, one channel per row)
# ═════════════════════════════════════════════════════════════════════════════

def plot_gd_pd(channel_data: dict) -> str:
    labels = list(channel_data.keys())
    titles = []
    for lbl in labels:
        titles += [f"{lbl} — Group Delay  τ_g(f)", f"{lbl} — Phase Delay  τ_p(f)"]

    fig = make_subplots(
        rows=len(labels), cols=2,
        subplot_titles=titles,
        horizontal_spacing=0.10,
        vertical_spacing=0.14,
    )
    for row_n, label in enumerate(labels, start=1):
        f_ghz, tg, tp = channel_data[label]
        col = COLOURS[label]
        fig.add_trace(go.Scatter(x=f_ghz, y=tg, name=label,
                                 line=dict(color=col, width=2),
                                 showlegend=False), row=row_n, col=1)
        fig.add_trace(go.Scatter(x=f_ghz, y=tp, name=label,
                                 line=dict(color=col, width=2),
                                 showlegend=False), row=row_n, col=2)
        for c in (1, 2):
            fig.add_vline(x=F_NYQ / 1e9, line_dash="dot",
                          line_color="#999999", line_width=1.5,
                          row=row_n, col=c)

    for row_n in range(1, len(labels) + 1):
        fig.update_yaxes(title_text="Delay (ps)", row=row_n, col=1)
        fig.update_yaxes(title_text="Delay (ps)", row=row_n, col=2)
    for c in (1, 2):
        fig.update_xaxes(title_text="Frequency (GHz)",
                         row=len(labels), col=c)

    fig.update_layout(
        title="Measured Colossus channels: group delay and phase delay (Sdd21, 13_24 convention)",
        height=700,
    )
    _grid(fig)
    return save(fig, "channels_gd_pd", w=1300, h=700)


# ═════════════════════════════════════════════════════════════════════════════
# Figure 1b — Magnitude response
# ═════════════════════════════════════════════════════════════════════════════

def plot_mag(fd_data: dict) -> str:
    fig = go.Figure()
    for label, fd in fd_data.items():
        col   = COLOURS[label]
        f_ghz = fd.f_hz / 1e9
        mag   = 20 * np.log10(np.abs(fd.h) + 1e-30)
        mask  = f_ghz <= 70
        fig.add_trace(go.Scatter(x=f_ghz[mask], y=mag[mask], name=label,
                                 line=dict(color=col, width=2)))

    fig.add_vline(x=F_NYQ / 1e9, line_dash="dot", line_color="#999999",
                  line_width=1.5,
                  annotation_text=f"Nyquist {F_NYQ/1e9:.1f} GHz",
                  annotation_position="top left")
    fig.update_layout(
        title="Measured Colossus channels: Sdd21 magnitude (13_24 convention)",
        xaxis_title="Frequency (GHz)",
        yaxis_title="|Sdd21| (dB)",
    )
    _grid(fig)
    return save(fig, "channels_mag", w=1100, h=520)


# ═════════════════════════════════════════════════════════════════════════════
# Figure 2 — Impulse response overlay
# ═════════════════════════════════════════════════════════════════════════════

def plot_ir(ir_data: dict) -> str:
    fig = go.Figure()
    for label, ir in ir_data.items():
        col  = COLOURS[label]
        h    = ir.h / np.max(np.abs(ir.h))          # normalise to peak = 1
        pk   = ir.peak_index
        t_ui = (np.arange(len(h)) - pk) / SPS       # time axis in UI
        mask = (t_ui >= -4) & (t_ui <= 10)
        fig.add_trace(go.Scatter(x=t_ui[mask], y=h[mask], name=label,
                                 line=dict(color=col, width=2)))

    for k in range(-4, 11):
        fig.add_vline(x=k, line_dash="dot", line_color="#cccccc", line_width=1)
    fig.update_layout(
        title="Measured Colossus channels: normalised impulse response",
        xaxis_title="Time (UI)",
        yaxis_title="Amplitude (normalised)",
    )
    _grid(fig)
    return save(fig, "channels_ir", w=1100, h=520)


# ═════════════════════════════════════════════════════════════════════════════
# Figure 3 — Side-by-side eye diagrams
# ═════════════════════════════════════════════════════════════════════════════

def eye_traces(rx: np.ndarray, sps: int = SPS,
               skip_sym: int = 512, max_folds: int = 1500,
               n_ui: int = 2) -> tuple[np.ndarray, np.ndarray]:
    seg    = n_ui * sps
    t_ui   = np.linspace(0, n_ui, seg)
    start  = skip_sym * sps
    usable = rx[start:]
    n_f    = min(len(usable) // seg, max_folds)
    segs   = usable[: n_f * seg].reshape(n_f, seg)
    all_x  = np.tile(np.append(t_ui, np.nan), n_f)
    all_y  = np.concatenate([np.append(row, np.nan) for row in segs])
    return all_x, all_y


def fold_start(ir: "DiscreteChannelIR") -> int:  # noqa: F821
    pk = ir.peak_index
    return (pk - SPS) % (2 * SPS)


def plot_eyes(rx_data: dict, ir_data: dict) -> str:
    labels = list(rx_data.keys())
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=list(rx_data.keys()),
        horizontal_spacing=0.08,
    )
    for col_n, label in enumerate(labels, start=1):
        col_c = COLOURS[label]
        h_hex = col_c.lstrip("#")
        r_, g_, b_ = int(h_hex[0:2], 16), int(h_hex[2:4], 16), int(h_hex[4:6], 16)
        fill  = f"rgba({r_},{g_},{b_},0.05)"

        t_ui, all_y = eye_traces(rx_data[label])
        fig.add_trace(go.Scatter(x=t_ui, y=all_y, mode="lines",
                                 line=dict(color=fill, width=1),
                                 name=label, showlegend=False), row=1, col=col_n)

    fig.update_xaxes(title_text="Time (UI)")
    fig.update_yaxes(title_text="Amplitude (norm.)", row=1, col=1)
    fig.update_layout(
        title="Measured Colossus channels: NRZ eye diagrams (PRBS-15, 106.25 Gbps)",
        plot_bgcolor="white",
    )
    _grid(fig)
    return save(fig, "channels_eyes", w=1300, h=560)


# ═════════════════════════════════════════════════════════════════════════════
# Metrics
# ═════════════════════════════════════════════════════════════════════════════

def compute_metrics(label: str,
                    f_ghz: np.ndarray, tg: np.ndarray, tp: np.ndarray,
                    ir: "DiscreteChannelIR") -> dict:  # noqa: F821
    gdv = float(np.max(tg) - np.min(tg))
    pdv = float(np.max(tp) - np.min(tp))
    pk  = ir.peak_index
    t2  = baud_tap(ir.h, pk, +2)
    t3  = baud_tap(ir.h, pk, +3)
    print(f"  {label}: GDV={gdv:.1f}ps  PDV={pdv:.1f}ps  "
          f"+2UI={t2:.4f}  +3UI={t3:.4f}")
    return dict(gdv_ps=gdv, pdv_ps=pdv, tap2=t2, tap3=t3)


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # ── Generate PRBS-15 input ───────────────────────────────────────────────
    bits = np.tile(generate_prbs(order=15, n_bits=2**15 - 1), 4)
    syms = 2.0 * bits.astype(np.float64) - 1.0
    x    = np.repeat(syms, SPS)

    delay_data: dict  = {}   # label → (f_ghz, tg, tp)
    fd_data:    dict  = {}   # label → FrequencyDomainChannel
    ir_data:    dict  = {}   # label → DiscreteChannelIR
    rx_data:    dict  = {}   # label → filtered waveform
    metrics:    dict  = {}   # label → dict

    for label, path in CHANNELS.items():
        print(f"Loading {path.name} …")
        fd = fd_channel_from_touchstone(path, convention="13_24")
        fd_data[label] = fd

        # Interpolate onto the primer's rfft grid
        f_grid, H_grid = interpolate_onto_rfft_grid(fd.f_hz, fd.h)
        f_ghz, tg, tp  = compute_delays(f_grid, H_grid)
        delay_data[label] = (f_ghz, tg, tp)

        # Synthesise IR with measured phase
        # extrapolate_high="zero" avoids Gibbs ringing from the step
        # discontinuity at the 120 GHz band edge when the default "hold"
        # would extend the end-of-band value across all frequencies up to FS/2.
        ir = discrete_impulse_response(
            fd, dt=DT, r_baud=DATA_RATE,
            method="ifft", phase="measured",
            n_ui_span=128.0,
            extrapolate_high="zero",
        )
        ir_data[label] = ir

        # Filter PRBS
        rx_data[label] = ir.filter(x)

        metrics[label] = compute_metrics(label, f_ghz, tg, tp, ir)

    print("Plotting …")
    p_mag   = plot_mag(fd_data)
    p_gd_pd = plot_gd_pd(delay_data)
    p_ir    = plot_ir(ir_data)
    p_eyes  = plot_eyes(rx_data, ir_data)

    print(f"\nAll figures → {OUT}")
    return metrics, p_mag, p_gd_pd, p_ir, p_eyes


if __name__ == "__main__":
    main()
