"""
Reproduction of key figures from:

  Bae, Nikolic, Jeong (2017) — IEEE Trans. VLSI Syst., vol. 25, no. 12
  "Use of Phase Delay Analysis for Evaluating Wideband Circuits:
   An Alternative to Group Delay Analysis"
  DOI: 10.1109/TVLSI.2017.2747157

Figures reproduced (from first principles, no SPICE):
  Fig 2  — Linear phase shifter: C=0 (undistorted) vs C=−π/2 (distorted)
  Fig 3  — Polynomial phase shifter: equal PD vs equal GD at 100/200 MHz
  Fig 5  — RC LPF vs HPF: identical GD, different PD, different waveform fidelity
  Fig 7  — RLC GD and PD vs frequency for L = 100–500 nH
  Fig 8  — RLC NRZ eye diagrams at L = 300 nH and L = 400 nH (800 Mb/s PRBS-7)
  Fig 9  — RLC summary: BW, ΔGD, ΔPD, P2P jitter vs inductance

Circuit parameters (all from the paper):
  R = 1 kΩ,  C = 1 pF  →  RC = 1 ns,  f_LPF,3dB = 159 MHz
  L swept 100–500 nH  →  BW 176–225 MHz

Usage:
  python scripts/phase_delay/bae2017_reproduction.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import plotly.graph_objects as go            # noqa: E402
from plotly.subplots import make_subplots    # noqa: E402

from optical_serdes.tx.waveform import generate_prbs  # noqa: E402

# ── Output directory ──────────────────────────────────────────────────────────
OUT = Path("/home/patrick/mydocs/nuggets/group_delay_variation/bae2017")
OUT.mkdir(parents=True, exist_ok=True)

# ── Circuit / simulation parameters ──────────────────────────────────────────
R   = 1e3     # 1 kΩ
C   = 1e-12   # 1 pF

FS  = 20e9    # 20 GHz sample rate (>> all frequencies of interest)
DT  = 1.0 / FS

# Two-tone test frequencies (Figs 2, 3, 5)
F1  = 100e6
F2  = 200e6
W1  = 2 * np.pi * F1
W2  = 2 * np.pi * F2

# PRBS simulation (Figs 8, 9)
DATA_RATE = 800e6          # 800 Mb/s
SPS       = 25             # FS / DATA_RATE = 25 samples/symbol
TB        = 1.0 / DATA_RATE  # 1.25 ns

# Inductance sweep
L_VALUES_NH = [100, 200, 300, 400, 500]
L_VALUES    = [l * 1e-9 for l in L_VALUES_NH]

# Colour palette
C_100 = "#0070d4"
C_200 = "#5ba0e8"
C_300 = "#228B22"
C_400 = "#e07020"
C_500 = "#cc2200"
GREY  = "#888888"
BLACK = "#111111"

L_COLOURS = dict(zip(L_VALUES, [C_100, C_200, C_300, C_400, C_500]))


# ═════════════════════════════════════════════════════════════════════════════
# Utility
# ═════════════════════════════════════════════════════════════════════════════

def save(fig: go.Figure, name: str, w: int = 1100, h: int = 550) -> None:
    fig.write_html(str(OUT / f"{name}.html"))
    fig.write_image(str(OUT / f"{name}.png"), width=w, height=h, scale=2)
    print(f"  {name}.png")


def _grid_layout(fig: go.Figure) -> None:
    fig.update_xaxes(gridcolor="#eeeeee", zerolinecolor="#cccccc")
    fig.update_yaxes(gridcolor="#eeeeee", zerolinecolor="#cccccc")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")


# ═════════════════════════════════════════════════════════════════════════════
# Transfer functions
# ═════════════════════════════════════════════════════════════════════════════

def H_rc_lpf(omega: np.ndarray) -> np.ndarray:
    """H(jω) = 1 / (1 + jωRC)"""
    return 1.0 / (1.0 + 1j * omega * R * C)


def H_rc_hpf(omega: np.ndarray) -> np.ndarray:
    """H(jω) = jωRC / (1 + jωRC)"""
    jrc = 1j * omega * R * C
    return jrc / (1.0 + jrc)


def H_rlc(omega: np.ndarray, L: float) -> np.ndarray:
    """
    Series-peaking RLC lowpass.
    H(jω) = ω₀² / (ω₀² − ω² + j·2ζω₀ω)
    """
    omega0 = 1.0 / np.sqrt(L * C)
    zeta   = (R / 2.0) * np.sqrt(C / L)
    return omega0**2 / (omega0**2 - omega**2 + 1j * 2.0 * zeta * omega0 * omega)


def delays(omega: np.ndarray, H: np.ndarray,
           f_eval_min: float = 1e6,
           f_eval_max: float = 1e9
           ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns (f_eval, tau_g_ps, tau_p_ps) over the evaluation band.
    Uses np.unwrap on the phase before differentiating to avoid gradient artefacts.
    """
    phi   = np.unwrap(np.angle(H))
    tau_g = -np.gradient(phi, omega)
    with np.errstate(divide="ignore", invalid="ignore"):
        tau_p = np.where(omega > 0, -phi / omega, np.nan)
    f_bins = omega / (2 * np.pi)
    mask   = (f_bins >= f_eval_min) & (f_bins <= f_eval_max)
    return f_bins[mask], tau_g[mask] * 1e12, tau_p[mask] * 1e12


def find_bw_3db(f_bins: np.ndarray, H: np.ndarray) -> float:
    """Interpolated −3 dB bandwidth (Hz)."""
    mag_db = 20 * np.log10(np.maximum(np.abs(H), 1e-30))
    target = mag_db[0] - 3.0
    for i in range(1, len(mag_db)):
        if mag_db[i] <= target:
            f0, f1 = f_bins[i - 1], f_bins[i]
            m0, m1 = mag_db[i - 1], mag_db[i]
            return float(f0 + (target - m0) / (m1 - m0) * (f1 - f0))
    return float(f_bins[-1])


# ═════════════════════════════════════════════════════════════════════════════
# Impulse response synthesis & filtering
# ═════════════════════════════════════════════════════════════════════════════

_N_FFT = 2**18   # 262 144 pts at 20 GHz → Δf ≈ 76 kHz


def make_ir(H_fn, tau_L: float) -> np.ndarray:
    """
    Build a causal real-valued discrete IR from an analog transfer function.
    H_fn(omega) must return complex H for positive omega.
    tau_L: linear pre-delay (s) to push the peak into the causal window.
    """
    f_bins = np.fft.rfftfreq(_N_FFT, d=DT)
    omega  = 2 * np.pi * f_bins
    H      = H_fn(omega) * np.exp(-1j * tau_L * omega)
    return np.fft.irfft(H, n=_N_FFT)


def fft_filter(h: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Linear (non-circular) convolution via FFT; returns first len(x) samples."""
    N = len(x) + len(h) - 1
    Y = np.fft.rfft(h, n=N) * np.fft.rfft(x, n=N)
    return np.fft.irfft(Y, n=N)[: len(x)]


# ═════════════════════════════════════════════════════════════════════════════
# Eye diagram helpers
# ═════════════════════════════════════════════════════════════════════════════

def fold_eye(rx: np.ndarray, sps: int,
             skip_sym: int = 127, max_folds: int = 2000,
             n_ui: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """
    Fold rx into a 2-UI eye.  Returns (t_ui, all_y) with NaN separators.
    """
    seg     = n_ui * sps
    t_ui    = np.linspace(0, n_ui, seg)
    start   = skip_sym * sps
    usable  = rx[start:]
    n_folds = min(len(usable) // seg, max_folds)
    segs    = usable[: n_folds * seg].reshape(n_folds, seg)
    all_x   = np.tile(np.append(t_ui, np.nan), n_folds)
    all_y   = np.concatenate([np.append(row, np.nan) for row in segs])
    return all_x, all_y


def p2p_jitter_ps(rx: np.ndarray, sps: int, skip_sym: int = 127) -> float:
    """
    P2P DDJ measured from zero-crossing timing deviations.
    Ideal transitions are at integer multiples of sps samples.
    Returns P2P jitter in picoseconds.
    """
    sig = rx[skip_sym * sps :]
    # Sub-sample zero-crossing locations (in sample units)
    crossings: list[float] = []
    for i in range(len(sig) - 1):
        if sig[i] * sig[i + 1] < 0:
            t_frac = i + (-sig[i]) / (sig[i + 1] - sig[i])
            crossings.append(t_frac)
    if len(crossings) < 4:
        return 0.0
    c = np.array(crossings)
    # Ideal: each transition is at the nearest symbol boundary
    ideal = np.round(c / sps) * sps
    deviations_ps = (c - ideal) / FS * 1e12
    return float(np.max(deviations_ps) - np.min(deviations_ps))


# ═════════════════════════════════════════════════════════════════════════════
# Fig 2 — Linear phase shifter  (paper Fig. 2)
# ═════════════════════════════════════════════════════════════════════════════

def fig2_linear_phase_shifter() -> None:
    """
    Transfer function: H(jω) = exp(j(−kω + C)).
    With C = 0: every tone shifted by the same time k → waveform replica.
    With C = −π/2: each tone shifted by k − C/ω → tones de-synchronised.

    For two tones at f1 = 100 MHz and f2 = 200 MHz:
      τ_p(ω) = −(−kω + C)/ω = k − C/ω

    The output is computed analytically (unity-magnitude filter):
      y(t) = sin(2π·f1·(t − τ_p(W1))) + sin(2π·f2·(t − τ_p(W2)))
    """
    k  = 8.33e-9          # bulk propagation delay (s)
    C_zero     =  0.0
    C_nonzero  = -np.pi / 2.0

    t  = np.linspace(0, 30e-9, 3000)      # 30 ns window
    x  = np.sin(W1 * t) + np.sin(W2 * t)  # two-tone input

    def output(C_val: float) -> np.ndarray:
        tau_p1 = k - C_val / W1
        tau_p2 = k - C_val / W2
        return np.sin(W1 * (t - tau_p1)) + np.sin(W2 * (t - tau_p2))

    y0 = output(C_zero)
    y1 = output(C_nonzero)

    # Shift input by k for the overlay comparison
    x_shifted = np.sin(W1 * (t - k)) + np.sin(W2 * (t - k))

    t_ns = t * 1e9

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            "C = 0  →  output = input shifted by k (no distortion)",
            "C = −π/2  →  tones de-synchronised (distorted)",
        ],
        horizontal_spacing=0.10,
    )
    kw = dict(mode="lines", line=dict(width=1.8))
    # C = 0 panel
    fig.add_trace(go.Scatter(x=t_ns, y=x_shifted, name="input (shifted by k)",
                             line=dict(color=GREY, dash="dot", width=1.5), **{k2: v for k2, v in kw.items() if k2 != "line"}), row=1, col=1)
    fig.add_trace(go.Scatter(x=t_ns, y=y0, name="output  C = 0",
                             line=dict(color=C_300, width=2)), row=1, col=1)
    # C = -π/2 panel
    fig.add_trace(go.Scatter(x=t_ns, y=x_shifted, name="input (shifted by k)",
                             line=dict(color=GREY, dash="dot", width=1.5),
                             showlegend=False), row=1, col=2)
    fig.add_trace(go.Scatter(x=t_ns, y=y1, name="output  C = −π/2",
                             line=dict(color=C_500, width=2)), row=1, col=2)

    fig.update_xaxes(title_text="Time (ns)")
    fig.update_yaxes(title_text="Amplitude (norm.)", row=1, col=1)
    fig.update_layout(
        title="Fig 2 — Linear Phase Shifter: flat GD cannot prevent distortion when C ≠ 0",
    )
    _grid_layout(fig)
    save(fig, "fig2_linear_phase_shifter", w=1300, h=520)


# ═════════════════════════════════════════════════════════════════════════════
# Fig 3 — Polynomial phase shifter  (paper Fig. 3)
# ═════════════════════════════════════════════════════════════════════════════

def fig3_polynomial_phase_shifter() -> None:
    """
    Phase: φ(ω) = −k3·ω³ − k2·ω² − k1·ω

    Case (a)  equal phase delays at 100 and 200 MHz:
      k3_a = −5e-25 / (12π²),  k2_a = 5e-17 / (2π),  k1_a = 5e-9
      → τ_p(W1) = τ_p(W2) = 8.33 ns
      → output = input shifted by 8.33 ns  (no distortion)

    Case (b)  equal group delays at 100 and 200 MHz:
      k3_b = −5e-25 / (36π²),  k2_b = 5e-17 / (4π),  k1_b = 5e-9
      → τ_g(W1) = τ_g(W2) = 8.33 ns
      → τ_p(W1) ≈ 6.95 ns,  τ_p(W2) ≈ 7.78 ns  → de-synchronised
    """
    # Coefficients from paper (verified analytically)
    k3_a = -5e-25 / (12 * np.pi**2)
    k2_a =  5e-17 / (2  * np.pi)
    k1_a =  5e-9

    k3_b = -5e-25 / (36 * np.pi**2)
    k2_b =  5e-17 / (4  * np.pi)
    k1_b =  5e-9

    # Analytical phase delay τ_p(ω) = k3·ω² + k2·ω + k1
    def tau_p_fn(k3, k2, k1, omega):
        return k3 * omega**2 + k2 * omega + k1

    # Verify
    for name, k3, k2, k1 in [("a (same PD)", k3_a, k2_a, k1_a),
                               ("b (same GD)", k3_b, k2_b, k1_b)]:
        tp1 = tau_p_fn(k3, k2, k1, W1) * 1e9
        tp2 = tau_p_fn(k3, k2, k1, W2) * 1e9
        tg1 = (3*k3*W1**2 + 2*k2*W1 + k1) * 1e9
        tg2 = (3*k3*W2**2 + 2*k2*W2 + k1) * 1e9
        print(f"    case {name}: τ_p(100MHz)={tp1:.3f}ns  τ_p(200MHz)={tp2:.3f}ns"
              f"  |  τ_g(100MHz)={tg1:.3f}ns  τ_g(200MHz)={tg2:.3f}ns")

    t   = np.linspace(0, 40e-9, 4000)   # 40 ns
    x   = np.sin(W1 * t) + np.sin(W2 * t)

    def output_poly(k3, k2, k1):
        d1 = tau_p_fn(k3, k2, k1, W1)
        d2 = tau_p_fn(k3, k2, k1, W2)
        return np.sin(W1 * (t - d1)) + np.sin(W2 * (t - d2))

    y_a = output_poly(k3_a, k2_a, k1_a)   # same PD → matches input shifted by 8.33ns
    y_b = output_poly(k3_b, k2_b, k1_b)   # same GD → distorted

    t_ref_a = tau_p_fn(k3_a, k2_a, k1_a, W1)   # 8.33 ns
    t_ref_b = tau_p_fn(k3_b, k2_b, k1_b, W1)   # 6.95 ns
    x_ref_a = np.sin(W1*(t - t_ref_a)) + np.sin(W2*(t - t_ref_a))
    x_ref_b = np.sin(W1*(t - t_ref_b)) + np.sin(W2*(t - t_ref_b))

    t_ns = t * 1e9

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            "(a) Equal phase delay at 100 & 200 MHz  →  perfect replica",
            "(b) Equal group delay at 100 & 200 MHz  →  waveform distortion",
        ],
        horizontal_spacing=0.10,
    )
    for col, y_out, x_ref, label, col_c in [
        (1, y_a, x_ref_a, "output (same PD)", C_100),
        (2, y_b, x_ref_b, "output (same GD)", C_500),
    ]:
        fig.add_trace(go.Scatter(x=t_ns, y=x_ref, name="input (shifted)",
                                 line=dict(color=GREY, dash="dot", width=1.5),
                                 showlegend=(col == 1)), row=1, col=col)
        fig.add_trace(go.Scatter(x=t_ns, y=y_out, name=label,
                                 line=dict(color=col_c, width=2.0)), row=1, col=col)

    fig.update_xaxes(title_text="Time (ns)")
    fig.update_yaxes(title_text="Amplitude (norm.)", row=1, col=1)
    fig.update_layout(
        title="Fig 3 — Polynomial Phase Shifter: equal PD → no distortion; equal GD → distortion",
    )
    _grid_layout(fig)
    save(fig, "fig3_polynomial_phase_shifter", w=1300, h=520)


# ═════════════════════════════════════════════════════════════════════════════
# Fig 4 / Fig 5 — RC LPF vs HPF  (paper Figs 4 & 5)
# ═════════════════════════════════════════════════════════════════════════════

def fig4_rc_lpf_hpf_metrics() -> None:
    """
    Frequency-domain metrics: |H|, GD, PD for LPF and HPF.
    Both have identical GD; their PD differs by π/(2ω).
    """
    N = _N_FFT
    f_bins = np.fft.rfftfreq(N, d=DT)
    omega  = 2 * np.pi * f_bins
    mask   = (f_bins >= 1e6) & (f_bins <= 1e9)

    H_lpf = H_rc_lpf(omega)
    H_hpf = H_rc_hpf(omega)

    f_ghz = f_bins[mask] / 1e9

    mag_lpf = 20 * np.log10(np.abs(H_lpf[mask]))
    mag_hpf = 20 * np.log10(np.abs(H_hpf[mask]))

    _, tg_lpf, tp_lpf = delays(omega, H_lpf)
    _, tg_hpf, tp_hpf = delays(omega, H_hpf)
    f_eval = f_bins[mask] / 1e9  # same mask as delays()

    # Numerical verification at 100 MHz and 200 MHz
    idx100 = np.argmin(np.abs(f_bins - 100e6))
    idx200 = np.argmin(np.abs(f_bins - 200e6))
    for name, H_arr in [("LPF", H_lpf), ("HPF", H_hpf)]:
        phi_arr = np.unwrap(np.angle(H_arr))
        tg_arr  = -np.gradient(phi_arr, omega)
        tp_arr  = -phi_arr / omega
        print(f"    {name}: GD@100MHz={tg_arr[idx100]*1e12:.0f}ps "
              f"PD@100MHz={tp_arr[idx100]*1e12:.0f}ps  "
              f"GD@200MHz={tg_arr[idx200]*1e12:.0f}ps "
              f"PD@200MHz={tp_arr[idx200]*1e12:.0f}ps")

    fig = make_subplots(rows=3, cols=1,
                        subplot_titles=["|H(f)| (dB)", "Group Delay (ps)", "Phase Delay (ps)"],
                        vertical_spacing=0.10)
    for name, mag, tg, tp, col in [
        ("LPF", mag_lpf, tg_lpf, tp_lpf, C_100),
        ("HPF", mag_hpf, tg_hpf, tp_hpf, C_500),
    ]:
        fig.add_trace(go.Scatter(x=f_ghz, y=mag, name=name,
                                 line=dict(color=col, width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=f_eval, y=tg, name=name, showlegend=False,
                                 line=dict(color=col, width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=f_eval, y=tp, name=name, showlegend=False,
                                 line=dict(color=col, width=2)), row=3, col=1)

    fig.update_xaxes(title_text="Frequency (GHz)", row=3, col=1)
    fig.update_yaxes(title_text="dB", row=1, col=1)
    fig.update_yaxes(title_text="ps", row=2, col=1)
    fig.update_yaxes(title_text="ps", row=3, col=1)
    fig.update_layout(
        title="Fig 4 — RC LPF vs HPF: identical group delay, divergent phase delay",
        height=750,
    )
    _grid_layout(fig)
    save(fig, "fig4_rc_lpf_hpf_metrics", w=900, h=750)


def fig5_rc_waveforms() -> None:
    """
    Two-tone (100 + 200 MHz) filtered through RC LPF and HPF.
    LPF output should track the input more faithfully (smaller PD variation).
    HPF has +π/2 offset in phase → larger distortion despite equal GD.
    """
    tau_L = 20e-9    # 20 ns pre-delay for causal IR synthesis

    h_lpf = make_ir(H_rc_lpf, tau_L=tau_L)
    h_hpf = make_ir(H_rc_hpf, tau_L=tau_L)

    # Build two-tone input (200 ns, enough to show beat envelope)
    N_SIG = int(200e-9 * FS)
    t_sig = np.arange(N_SIG) * DT
    x     = np.sin(W1 * t_sig) + np.sin(W2 * t_sig)

    y_lpf = fft_filter(h_lpf, x)
    y_hpf = fft_filter(h_hpf, x)

    # Expected delay: for LPF, τ_p ≈ RC = 1 ns at low freq
    # For display, shift input by tau_L + 1 ns so it overlaps the filtered outputs
    # The filtered output peak is near tau_L samples into the output
    delay_samp = int(tau_L * FS)
    # Trim to a 30 ns window centred on the steady-state output
    t_start_samp = delay_samp - int(5e-9 * FS)
    t_end_samp   = t_start_samp + int(30e-9 * FS)
    t_start_samp = max(0, t_start_samp)
    t_end_samp   = min(N_SIG, t_end_samp)

    sl  = slice(t_start_samp, t_end_samp)
    t_w = (t_sig[sl] - tau_L) * 1e9   # relative time in ns (zero at filter "start")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_w, y=x[sl], name="input",
                             line=dict(color=BLACK, dash="dot", width=1.5)))
    fig.add_trace(go.Scatter(x=t_w, y=y_lpf[sl], name="LPF output",
                             line=dict(color=C_100, width=2)))
    fig.add_trace(go.Scatter(x=t_w, y=y_hpf[sl], name="HPF output",
                             line=dict(color=C_500, width=2, dash="dash")))

    fig.update_layout(
        title="Fig 5 — RC LPF vs HPF waveforms (two-tone 100+200 MHz): "
              "HPF shows greater distortion despite equal group delay",
        xaxis_title="Time (ns, relative)",
        yaxis_title="Amplitude (norm.)",
    )
    _grid_layout(fig)
    save(fig, "fig5_rc_waveforms", w=1100, h=500)


# ═════════════════════════════════════════════════════════════════════════════
# Fig 7 — RLC group delay and phase delay  (paper Fig. 7)
# ═════════════════════════════════════════════════════════════════════════════

def fig7_rlc_delays() -> None:
    """
    GD and PD of the series-peaking RLC circuit for L = 100–500 nH.
    """
    N      = _N_FFT
    f_bins = np.fft.rfftfreq(N, d=DT)
    omega  = 2 * np.pi * f_bins

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["(a) Group Delay  τ_g(f)", "(b) Phase Delay  τ_p(f)"],
                        horizontal_spacing=0.10)

    for L, col in zip(L_VALUES, [C_100, C_200, C_300, C_400, C_500]):
        L_nH   = int(L * 1e9)
        H      = H_rlc(omega, L)
        f_eval, tg, tp = delays(omega, H, f_eval_min=1e6, f_eval_max=1e9)
        f_ghz  = f_eval / 1e9
        label  = f"{L_nH} nH"
        fig.add_trace(go.Scatter(x=f_ghz, y=tg, name=label,
                                 line=dict(color=col, width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=f_ghz, y=tp, name=label, showlegend=False,
                                 line=dict(color=col, width=2)), row=1, col=2)

    for col_n in (1, 2):
        fig.update_xaxes(title_text="Frequency (GHz)", row=1, col=col_n)
    fig.update_yaxes(title_text="Delay (ps)", row=1, col=1)
    fig.update_yaxes(title_text="Delay (ps)", row=1, col=2)
    fig.update_layout(
        title="Fig 7 — RLC series-peaking: GD varies widely with L; PD stays in a narrow band",
        height=520,
    )
    _grid_layout(fig)
    save(fig, "fig7_rlc_delays", w=1200, h=520)


# ═════════════════════════════════════════════════════════════════════════════
# Fig 8 — Eye diagrams at L = 300 nH and L = 400 nH  (paper Fig. 8)
# ═════════════════════════════════════════════════════════════════════════════

def fig8_rlc_eyes() -> None:
    """
    800 Mb/s PRBS-7 filtered through RLC for L = 300 nH and L = 400 nH.
    GD variations differ by ~9 %; PDV differ by <0.2 %.
    Eye / P2P jitter should track PDV, not GDV.
    """
    n_periods = 16
    bits      = np.tile(generate_prbs(order=7, n_bits=127), n_periods)
    syms      = 2.0 * bits.astype(np.float64) - 1.0
    x         = np.repeat(syms, SPS)

    tau_L = 50 * SPS * DT   # 50 symbols of pre-delay

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=[
                            "L = 300 nH  (ΔGD = 874 ps, ΔPD = 504 ps)",
                            "L = 400 nH  (ΔGD = 950 ps, ΔPD = 505 ps)",
                        ],
                        horizontal_spacing=0.08)

    for col_n, L_nH, col_c in [(1, 300, C_300), (2, 400, C_400)]:
        L = L_nH * 1e-9
        h = make_ir(lambda w, L=L: H_rlc(w, L), tau_L=tau_L)
        rx = fft_filter(h, x)

        jitter = p2p_jitter_ps(rx, SPS, skip_sym=2 * 127)
        print(f"    L={L_nH}nH  P2P jitter = {jitter:.1f} ps")

        t_ui, all_y = fold_eye(rx, SPS, skip_sym=2 * 127)
        # Eye colour with transparency
        h_c   = col_c.lstrip("#")
        r_, g_, b_ = int(h_c[0:2], 16), int(h_c[2:4], 16), int(h_c[4:6], 16)
        fill  = f"rgba({r_},{g_},{b_},0.06)"

        fig.add_trace(go.Scatter(x=t_ui, y=all_y, mode="lines",
                                 line=dict(color=fill, width=1),
                                 showlegend=False), row=1, col=col_n)
        fig.add_vline(x=1.0, line_dash="dash", line_color="black", line_width=1,
                      annotation_text=f"P2P={jitter:.0f} ps", col=col_n)

    fig.update_xaxes(title_text="Time (UI)")
    fig.update_yaxes(title_text="Amplitude (norm.)", row=1, col=1)
    fig.update_layout(
        title="Fig 8 — 800 Mb/s PRBS-7 eye: GD variations differ by 9 %; P2P jitter nearly equal",
        plot_bgcolor="white",
    )
    _grid_layout(fig)
    save(fig, "fig8_rlc_eyes", w=1300, h=560)


# ═════════════════════════════════════════════════════════════════════════════
# Fig 9 — RLC summary: BW / ΔGD / ΔPD / jitter vs L  (paper Fig. 9)
# ═════════════════════════════════════════════════════════════════════════════

def fig9_rlc_summary() -> None:
    """
    For each inductance value, compute:
      - 3-dB bandwidth
      - ΔGD  (peak-to-peak GD over signal band 1 MHz → 800 MHz)
      - ΔPD  (peak-to-peak PD over same band)
      - P2P DDJ (800 Mb/s PRBS-7)

    Paper result: DDJ tracks ΔPD tightly and is insensitive to ΔGD.
    """
    n_periods = 16
    bits      = np.tile(generate_prbs(order=7, n_bits=127), n_periods)
    syms      = 2.0 * bits.astype(np.float64) - 1.0
    x         = np.repeat(syms, SPS)
    tau_L     = 50 * SPS * DT

    N      = _N_FFT
    f_bins = np.fft.rfftfreq(N, d=DT)
    omega  = 2 * np.pi * f_bins

    L_nH_arr, bw_arr, dgd_arr, dpd_arr, jit_arr = [], [], [], [], []

    for L in L_VALUES:
        L_nH = int(L * 1e9)
        H    = H_rlc(omega, L)

        bw   = find_bw_3db(f_bins, H) / 1e6   # MHz
        f_ev, tg_ps, tp_ps = delays(omega, H, f_eval_min=1e6, f_eval_max=800e6)
        dgd  = float(np.max(tg_ps) - np.min(tg_ps))
        dpd  = float(np.max(tp_ps) - np.min(tp_ps))

        h    = make_ir(lambda w, L=L: H_rlc(w, L), tau_L=tau_L)
        rx   = fft_filter(h, x)
        jit  = p2p_jitter_ps(rx, SPS, skip_sym=2 * 127)

        print(f"    L={L_nH}nH  BW={bw:.0f}MHz  ΔGD={dgd:.0f}ps  "
              f"ΔPD={dpd:.0f}ps  jitter={jit:.0f}ps")

        L_nH_arr.append(L_nH)
        bw_arr.append(bw)
        dgd_arr.append(dgd)
        dpd_arr.append(dpd)
        jit_arr.append(jit)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=L_nH_arr, y=bw_arr,  name="BW (MHz)",
                             line=dict(color=C_100, width=2, dash="solid"), mode="lines+markers"),
                 secondary_y=False)
    fig.add_trace(go.Scatter(x=L_nH_arr, y=dgd_arr, name="ΔGD (ps)",
                             line=dict(color=C_500, width=2, dash="dash"), mode="lines+markers"),
                 secondary_y=True)
    fig.add_trace(go.Scatter(x=L_nH_arr, y=dpd_arr, name="ΔPD (ps)",
                             line=dict(color=C_300, width=2, dash="dot"), mode="lines+markers"),
                 secondary_y=True)
    fig.add_trace(go.Scatter(x=L_nH_arr, y=jit_arr, name="P2P jitter (ps)",
                             line=dict(color=BLACK, width=2.5), mode="lines+markers",
                             marker=dict(size=8, symbol="circle")),
                 secondary_y=True)

    fig.update_xaxes(title_text="Inductance (nH)")
    fig.update_yaxes(title_text="Bandwidth (MHz)", secondary_y=False)
    fig.update_yaxes(title_text="Delay / Jitter (ps)", secondary_y=True)
    fig.update_layout(
        title="Fig 9 — RLC summary: P2P jitter tracks ΔPD (not ΔGD) across the inductance sweep",
    )
    _grid_layout(fig)
    save(fig, "fig9_rlc_summary", w=1000, h=560)


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("Fig 2: Linear phase shifter …")
    fig2_linear_phase_shifter()

    print("Fig 3: Polynomial phase shifter …")
    print("  Coefficients check:")
    fig3_polynomial_phase_shifter()

    print("Fig 4: RC LPF vs HPF frequency metrics …")
    print("  Metrics at 100/200 MHz:")
    fig4_rc_lpf_hpf_metrics()

    print("Fig 5: RC LPF vs HPF waveforms …")
    fig5_rc_waveforms()

    print("Fig 7: RLC group and phase delay …")
    fig7_rlc_delays()

    print("Fig 8: RLC eye diagrams …")
    fig8_rlc_eyes()

    print("Fig 9: RLC summary …")
    fig9_rlc_summary()

    print(f"\nAll figures → {OUT}")


if __name__ == "__main__":
    main()
