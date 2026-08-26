#!/usr/bin/env python3
"""Render Gizmo TP1 TX eye masks at 2.0 Vppd and 3.0 Vppd, plus the
horizontal dual-Dirac budget decomposition at raw BER 1e-12.

Coordinates follow gizmo.md §2 and §3-2, in two tap-configuration variants (§3-4):
  X1  = TJ(1e-12)/2  (FIR-included baseline: DJ = 0.123 UI; no-FIR: DJ = 0.073 UI)
  X2  = X1 + Y1 / SR_min, SR_min from the 4.0 ps (0.42 UI) 20–80% hard-max edge
  Y1  = 400 mV (MRM ER ≥ 3.5 dB static floor)
  Y2  = Vpp/2
Mask figures render both hexagons (FIR operative baseline solid, no-FIR dashed);
the JSON carries both variants.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon, Rectangle

    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False

OUT = Path(__file__).resolve().parent

UI_PS = 9.412
Q_1E12 = 7.034
SIGMA_RJ = 0.011  # JH4u-bound (gizmo.md §2-3 tougher-spec rule); supersedes 0.015
DCD = 0.025
ISI = 0.012
BUJ = 0.036
DJ = DCD + ISI + BUJ  # 0.073
TJ = DJ + 2.0 * Q_1E12 * SIGMA_RJ
X1_EXACT = TJ / 2.0
X1 = 0.114  # polygon coordinate in gizmo.md §2 / §3-4 (X1_EXACT ≈ 0.114)
FIR_SLICE_DCD = 0.05  # §3-2: slice-DCD booked only by the FIR-included configuration
DJ_FIR = DJ + FIR_SLICE_DCD  # 0.123
TJ_FIR = DJ_FIR + 2.0 * Q_1E12 * SIGMA_RJ
X1_FIR_EXACT = TJ_FIR / 2.0
X1_FIR = 0.139  # polygon coordinate in gizmo.md §3-4 (X1_FIR_EXACT ≈ 0.139)
Y1 = 0.400
T2080_HARD_MAX_PS = 4.0  # §3-2
T01_PS = T2080_HARD_MAX_PS / 0.6  # linear-ramp 0–100% equivalent

HORIZ = {
    "ISI/2": ISI / 2.0,
    "DCD/2": DCD / 2.0,
    "BUJ/2": BUJ / 2.0,
    "RJ = Q(1e-12)·σ_RJ": Q_1E12 * SIGMA_RJ,
}


def x2_from_slew(vpp: float, x1_exact: float = X1_EXACT) -> float:
    """Minimum X2 that a legal hard-max 20–80% edge can still clear Y1."""
    sr_v_per_ps = vpp / T01_PS
    dt_ui = (Y1 / sr_v_per_ps) / UI_PS
    return round(x1_exact + dt_ui, 3)


def hexagon(x1: float, x2: float, y1: float) -> list[tuple[float, float]]:
    return [
        (x1, 0.0),
        (x2, y1),
        (1.0 - x2, y1),
        (1.0 - x1, 0.0),
        (1.0 - x2, -y1),
        (x2, -y1),
    ]


SWINGS = {
    "2v": {"vpp": 2.0, "y2": 1.0, "label": "2.0 Vppd"},
    "3v": {"vpp": 3.0, "y2": 1.5, "label": "3.0 Vppd"},
}


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.grid(True, which="major", ls=":", lw=0.6, color="#b0b0b0")
    ax.set_axisbelow(True)


def draw_mask(ax, vpp: float, y2: float, title: str) -> float:
    x2 = x2_from_slew(vpp)
    x2_fir = x2_from_slew(vpp, X1_FIR_EXACT)
    y_lim = y2 + 0.35

    ax.add_patch(
        Rectangle((-0.05, y2), 1.10, y_lim - y2, facecolor="#f4c7c3", edgecolor="none", zorder=0)
    )
    ax.add_patch(
        Rectangle((-0.05, -y_lim), 1.10, y_lim - y2, facecolor="#f4c7c3", edgecolor="none", zorder=0)
    )
    ax.axhline(y2, color="#c0392b", lw=1.2, ls="--")
    ax.axhline(-y2, color="#c0392b", lw=1.2, ls="--")

    keep = Polygon(
        hexagon(X1_FIR, x2_fir, Y1),
        closed=True,
        facecolor="#f5b7b1",
        edgecolor="#922b21",
        lw=1.6,
        hatch="///",
        zorder=2,
        label=f"FIR keep-out (operative baseline): $X_1$={X1_FIR:.3f}, $X_2$={x2_fir:.3f} UI",
    )
    ax.add_patch(keep)
    nofir = Polygon(
        hexagon(X1, x2, Y1),
        closed=True,
        facecolor="none",
        edgecolor="#1a5276",
        lw=1.4,
        ls="--",
        zorder=3,
        label=f"no-FIR keep-out (removal study): $X_1$={X1:.3f}, $X_2$={x2:.3f} UI",
    )
    ax.add_patch(nofir)
    ax.legend(loc="lower center", fontsize=7.5, frameon=True, fancybox=False)

    # Nominal rails and an illustrative equalized-eye outline (not a waveform).
    ax.axhline(vpp / 2.0, color="#2c3e50", lw=0.8, ls=":", alpha=0.8)
    ax.axhline(-vpp / 2.0, color="#2c3e50", lw=0.8, ls=":", alpha=0.8)
    ax.axhline(0.0, color="#7f8c8d", lw=0.6)
    ax.axvline(0.5, color="#7f8c8d", lw=0.5, ls=":")

    # Dimension callouts (FIR operative hexagon)
    ax.annotate(
        f"$X_1$={X1_FIR:.3f} UI",
        xy=(X1_FIR, 0.0),
        xytext=(X1_FIR + 0.02, -0.22 * y2),
        fontsize=8,
        color="#922b21",
        arrowprops=dict(arrowstyle="-", color="#922b21", lw=0.7),
    )
    ax.annotate(
        f"$X_2$={x2_fir:.3f} UI",
        xy=(x2_fir, Y1),
        xytext=(x2_fir + 0.03, Y1 + 0.18 * y2),
        fontsize=8,
        color="#922b21",
        arrowprops=dict(arrowstyle="-", color="#922b21", lw=0.7),
    )
    ax.annotate(f"$Y_1$={Y1*1e3:.0f} mV", xy=(0.5, Y1), xytext=(0.52, Y1 + 0.08 * y2), fontsize=8, color="#1a5276")
    ax.annotate(
        f"$Y_2$={y2*1e3:.0f} mV",
        xy=(0.08, y2),
        xytext=(0.08, y2 + 0.08),
        fontsize=8,
        color="#c0392b",
    )

    ax.text(0.50, 0.0, "keep-out", ha="center", va="center", fontsize=8, color="#922b21", zorder=3)
    ax.text(0.50, 0.55 * (Y1 + y2), "open eye", ha="center", va="center", fontsize=8, color="#1e8449")
    ax.text(0.97, y2 + 0.06, r"$|v|>Y_2$", ha="right", va="bottom", fontsize=8, color="#c0392b")

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-y_lim, y_lim)
    ax.set_xlabel("Time (UI)")
    ax.set_ylabel("Differential voltage at TP1 (V)")
    ax.set_title(title, fontsize=11, pad=8)
    style_axes(ax)
    return x2


def save_mask(key: str, cfg: dict) -> float:
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=160)
    x2 = draw_mask(ax, cfg["vpp"], cfg["y2"], f"TP1 TX electrical eye mask — {cfg['label']}")
    fig.tight_layout()
    path = OUT / f"tx_eye_mask_{key}.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return x2


def save_budget() -> None:
    labels = list(HORIZ.keys())
    values = np.array(list(HORIZ.values()))
    colors = ["#2471a3", "#1abc9c", "#8e44ad", "#e67e22"]
    fig, ax = plt.subplots(figsize=(7.4, 3.6), dpi=160)
    left = 0.0
    for lab, val, col in zip(labels, values, colors):
        ax.barh(0, val, left=left, height=0.45, color=col, edgecolor="white", lw=0.6, label=f"{lab}  {val:.4f} UI")
        cx = left + val / 2.0
        if val > 0.02:
            ax.text(cx, 0.0, f"{val:.3f}", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        left += val

    ax.axvline(X1_EXACT, color="#1a252f", lw=1.4, ls="--", label=f"$X_1$ = {X1:.3f} UI  (= $TJ/2$)")
    ax.set_yticks([])
    ax.set_xlim(0, 0.20)
    ax.set_xlabel("Horizontal closure per eye side at BER $10^{-12}$ (UI)")
    ax.set_title("Mask-margin decomposition — dual-Dirac, no-FIR variant", fontsize=11, pad=8)
    ax.legend(loc="upper right", fontsize=8, frameon=True, fancybox=False)
    style_axes(ax)
    ax.spines["left"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "tx_eye_mask_budget.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_json(x2s: dict[str, float], x2s_fir: dict[str, float]) -> None:
    variants = {}
    for key, cfg in SWINGS.items():
        x2 = x2s[key]
        x2_fir = x2s_fir[key]
        verts = hexagon(X1, x2, Y1)
        variants[key] = {
            "vpp_v": cfg["vpp"],
            "coordinates": {
                "X1_ui": X1,
                "X2_ui": round(x2, 6),
                "Y1_v": Y1,
                "Y2_v": cfg["y2"],
            },
            "derived": {
                "eye_width_guarantee_ui": round(1.0 - 2.0 * X1, 6),
                "eye_width_guarantee_ps": round((1.0 - 2.0 * X1) * UI_PS, 4),
                "inner_opening_pp_v": round(2.0 * Y1, 4),
                "amplitude_bound_pp_v": cfg["vpp"],
            },
            "polygons": {
                "inner_keepout_hexagon_t_ui_v_volts": [[round(t, 6), round(v, 6)] for t, v in verts],
                "upper_forbidden_region": f"v > +{cfg['y2']} V for all t",
                "lower_forbidden_region": f"v < -{cfg['y2']} V for all t",
            },
            "fir_retained": {
                "applies": (
                    "Operative baseline while the FIR is in the mission path (gizmo.md §3/§3-4); "
                    "tap banks exercised at tap-code extrema against this hexagon"
                ),
                "DJ_pp_ui": round(DJ_FIR, 6),
                "TJ_pp_ui": round(TJ_FIR, 6),
                "X1_ui": X1_FIR,
                "X2_ui": round(x2_fir, 6),
                "Y1_v": Y1,
                "Y2_v": cfg["y2"],
                "eye_width_guarantee_ui": round(1.0 - 2.0 * X1_FIR, 6),
                "eye_width_guarantee_ps": round((1.0 - 2.0 * X1_FIR) * UI_PS, 4),
                "inner_keepout_hexagon_t_ui_v_volts": [
                    [round(t, 6), round(v, 6)] for t, v in hexagon(X1_FIR, x2_fir, Y1)
                ],
            },
        }

    payload = {
        "name": "Gizmo OCI-MSA TX electrical eye mask at TP1",
        "spec_reference": "tx_eye_mask.md (normative text; gizmo.md §3-4 is a pointer stub)",
        "compliance_note": "Internal mask; geometry follows the OIF-CEI TX hexagon construction but this is not a CEI compliance claim.",
        "test_point": "TP1, electrical input to the MRM modulator (V_TXP − V_TXN), extracted 60 fF MRM-plus-pad load present",
        "alignment": "Eye folded over 1 UI against the ideal (jitter-free) serializer symbol clock; mean 0 V crossing at t = 0 UI.",
        "ber_convention": "Raw BER 1e-12 (FEC-free internal spec). Q = 7.034, transition density ρ = 1.",
        "ui_ps": UI_PS,
        "x2_construction": (
            "X2 = X1 + Y1/SR_min. SR_min is the linear-ramp slew of the §3-2 hard-max "
            "20–80% edge (4.0 ps) at the stated Vpp: T01 = 4.0/0.6 ps, SR = Vpp/T01."
        ),
        "status": {
            "X1": "normative — TJ(1e-12)/2 per variant (gizmo.md §2): no-FIR in 'coordinates', FIR-included in 'fir_retained'",
            "X2": "derived from §3-2 4.0 ps hard-max 20–80% edge and Y1; TBD_from_sim_sweep vs extracted two-pole edges",
            "Y1": "model-derived static ER ≥ 3.5 dB floor (399.2 mV at Q=5000), rounded to 400 mV; TBD_from_link_budget for PVT/TDEC",
            "Y2": "exact — Vpp/2 at the 2.0 Vppd and 3.0 Vppd sign-off swings",
        },
        "tap_configuration": (
            "Each swing carries two hexagon variants (gizmo.md §3-4): 'fir_retained' is the operative baseline while "
            "the FIR is in the mission path (X1 = TJ_FIR/2, DJ includes the ~0.05 UI FIR slice-DCD of §3-2; tap banks "
            "at tap-code extrema); 'coordinates'/'polygons' are the no-FIR variant for the FIR-removal study, signed "
            "off with all tap weights forced to zero. The Y2 amplitude bound applies in every configuration."
        ),
        "variants": variants,
        "budget_decomposition": {
            "note": "Horizontal dual-Dirac from §2 no-FIR allocations at BER 1e-12. X1 equals total closure by construction.",
            "internal_raw_ber": 1e-12,
            "Q": Q_1E12,
            "sigma_RJ_ui_rms": SIGMA_RJ,
            "DJ_pp_ui": DJ,
            "TJ_pp_ui": round(TJ, 6),
            "X1_ui_polygon": X1,
            "X1_ui_exact": round(X1_EXACT, 6),
            "horizontal_per_side_ui": {k: round(v, 6) for k, v in HORIZ.items()},
            "horizontal_total_ui": round(sum(HORIZ.values()), 6),
            "horizontal_margin_ui": 0.0,
            "vertical_status": "Y1 not decomposed arithmetically; MRM P(V) static floor. Y2 = Vpp/2 per variant.",
            "fir_retained": {
                "note": "FIR-enabled variant: DJ adds the ~0.05 UI FIR slice-DCD booked in gizmo.md §3-2.",
                "DJ_pp_ui": round(DJ_FIR, 6),
                "TJ_pp_ui": round(TJ_FIR, 6),
                "X1_ui_polygon": X1_FIR,
                "X1_ui_exact": round(X1_FIR_EXACT, 6),
            },
        },
    }
    (OUT / "tx_eye_mask.json").write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    x2s = {key: x2_from_slew(cfg["vpp"]) for key, cfg in SWINGS.items()}
    x2s_fir = {key: x2_from_slew(cfg["vpp"], X1_FIR_EXACT) for key, cfg in SWINGS.items()}
    if HAVE_MPL:
        for key, cfg in SWINGS.items():
            save_mask(key, cfg)
        save_budget()
        figures_note = "wrote tx_eye_mask_2v.png, tx_eye_mask_3v.png, tx_eye_mask_budget.png (FIR solid + no-FIR dashed), "
    else:
        figures_note = "matplotlib unavailable — figures skipped (baseline hexagons unchanged), "
    write_json(x2s, x2s_fir)
    print(f"baseline:     X1 = {X1:.6f} UI  TJ = {TJ:.6f} UI  DJ = {DJ:.6f} UI")
    print(f"fir_retained: X1 = {X1_FIR:.6f} UI  TJ = {TJ_FIR:.6f} UI  DJ = {DJ_FIR:.6f} UI")
    for key in SWINGS:
        print(f"  {key}: X2 = {x2s[key]:.6f} / {x2s_fir[key]:.6f} UI (baseline / fir)  Y2 = {SWINGS[key]['y2']} V")
    print(figures_note + "wrote tx_eye_mask.json")


if __name__ == "__main__":
    main()
