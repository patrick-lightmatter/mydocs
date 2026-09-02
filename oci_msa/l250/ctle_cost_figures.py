#!/usr/bin/env python3
"""Render the two CTLE cost-function cartoons referenced in gizmo.md §7-6.

Figure 1 (ctle_postcursor_regimes.png): baud-spaced pulse-response cursors in
the three CTLE regimes — under-boosted (positive post-cursor tail), converged
(post-cursors inside the dead-band), over-boosted (negative / ringing tail) —
with the sign-sign vote each regime produces.

Figure 2 (ctle_cost_functions.png): the signed window correlation
corr = Σ⟨d(k−m)·e(k)⟩ vs. the magnitude cost J = Σ|h_m| as functions of the
peaking code: the signed metric crosses zero at the optimum (one reading gives
the step direction), the magnitude cost is V-shaped (blind to which side of
the optimum you are on without dithering the code).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent

# ----------------------------------------------------------------------------
# Figure 1 — post-cursor regimes
# ----------------------------------------------------------------------------

REGIMES = [
    (
        "Under-boosted   (corr > 0)",
        {-1: 0.05, 0: 1.0, 1: 0.25, 2: 0.12, 3: 0.06},
        "slow settling tail:\npositive post-cursors\n→ vote +1 (raise peaking)",
        "tab:red",
    ),
    (
        "Converged   (corr ≈ 0)",
        {-1: 0.02, 0: 1.0, 1: 0.02, 2: 0.01, 3: 0.005},
        "post-cursors nulled:\nvotes land inside\ncorr_deadband → hold",
        "tab:green",
    ),
    (
        "Over-boosted   (corr < 0)",
        {-1: 0.04, 0: 1.0, 1: -0.20, 2: -0.07, 3: -0.02},
        "overshoot / ringing:\nnegative post-cursors\n→ vote −1 (lower peaking)",
        "tab:blue",
    ),
]

DEADBAND = 0.05  # cartoon dead-band on cursor amplitude


def fig_regimes() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8), sharey=True)
    for ax, (title, cursors, note, color) in zip(axes, REGIMES):
        lags = np.array(sorted(cursors))
        vals = np.array([cursors[m] for m in lags])
        # dead-band shading around zero
        ax.axhspan(-DEADBAND, DEADBAND, color="0.92", zorder=0)
        ax.axhline(0.0, color="0.4", lw=0.8, zorder=1)
        # stems
        ml, sl, bl = ax.stem(lags, vals, basefmt=" ")
        plt.setp(sl, color=color, lw=2.0)
        plt.setp(ml, color=color, markersize=7)
        # cursor labels
        for m, v in zip(lags, vals):
            name = "h₀" if m == 0 else (f"h₊{m}" if m > 0 else f"h₋{-m}")
            dy = 0.06 if v >= 0 else -0.10
            va = "bottom" if v >= 0 else "top"
            if m == 0:
                ax.annotate(name, (m, v), xytext=(m + 0.15, 0.52),
                            fontsize=10, fontweight="bold")
            else:
                ax.annotate(name, (m, v + dy), ha="center", va=va, fontsize=9)
        ax.set_title(title, fontsize=11)
        ax.text(0.03, 0.97, note, transform=ax.transAxes, fontsize=8.5,
                va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.7"))
        ax.set_xticks(lags)
        ax.set_xticklabels(["−1", "0", "+1", "+2", "+3"])
        ax.set_xlabel("cursor lag m (UI)")
        ax.set_xlim(-1.7, 3.7)
        ax.set_ylim(-0.42, 1.18)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("baud-spaced cursor amplitude (norm.)")
    axes[1].text(2.6, 0.12, "corr_deadband", fontsize=7.5, color="0.45",
                 ha="center", va="bottom")
    fig.suptitle(
        "CTLE sign-sign adaptation — residual post-cursors on either side of the optimum (§7-6)",
        fontsize=12, y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT / "ctle_postcursor_regimes.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------
# Figure 2 — signed correlation vs magnitude cost over the peaking code
# ----------------------------------------------------------------------------


def cursors_vs_code(code: np.ndarray) -> list[np.ndarray]:
    """Cartoon plant: each post-cursor slides monotonically through zero as
    peaking increases, with slightly different zero crossings per lag."""
    h1 = 0.25 * (1.0 - code / 8.0)
    h2 = 0.12 * (1.0 - code / 8.6)
    h3 = 0.06 * (1.0 - code / 7.4)
    return [h1, h2, h3]


def fig_costs() -> None:
    code = np.linspace(0, 15, 601)
    h = cursors_vs_code(code)
    corr = np.sqrt(2.0 / np.pi) * sum(h)          # signed sign-sign metric
    j_abs = sum(np.abs(hm) for hm in h)           # magnitude cost

    # equilibria
    i_zero = int(np.argmin(np.abs(corr)))
    i_min = int(np.argmin(j_abs))
    db = 0.02  # corr_deadband

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.0))

    # -- left: signed correlation --------------------------------------------
    ax1.axhspan(-db, db, color="0.92", zorder=0)
    ax1.axhline(0.0, color="0.4", lw=0.8)
    ax1.plot(code, corr, color="tab:red", lw=2.2)
    ax1.axvline(code[i_zero], color="0.5", ls="--", lw=1.0)
    ax1.annotate("zero crossing =\nloop equilibrium",
                 (code[i_zero], 0.0), xytext=(code[i_zero] + 1.6, 0.14),
                 fontsize=9, arrowprops=dict(arrowstyle="->", color="0.35"))
    ax1.text(1.2, 0.205, "corr > 0 → vote +1\n(under-boost: raise peaking)",
             fontsize=8.5, color="tab:red")
    ax1.text(8.6, -0.16, "corr < 0 → vote −1\n(over-boost: lower peaking)",
             fontsize=8.5, color="tab:blue")
    ax1.text(14.6, db + 0.008, "corr_deadband", fontsize=7.5, color="0.45",
             ha="right", va="bottom")
    ax1.set_title("Signed metric (what the loop uses)\ncorr = Σ⟨d(k−m)·e(k)⟩", fontsize=10.5)
    ax1.set_xlabel("CTLE peaking code")
    ax1.set_ylabel("window-mean correlation")
    ax1.set_xlim(0, 15)
    ax1.spines[["top", "right"]].set_visible(False)

    # -- right: magnitude cost -----------------------------------------------
    ax2.plot(code, j_abs, color="tab:purple", lw=2.2)
    ax2.axvline(code[i_min], color="0.5", ls="--", lw=1.0)
    ax2.annotate("minimum ≈ same code,\nbut J alone gives no\nstep direction",
                 (code[i_min], j_abs[i_min]),
                 xytext=(1.0, 0.30),
                 fontsize=9, arrowprops=dict(arrowstyle="->", color="0.35"))
    # equal-J markers on both sides of the minimum
    j_ref = j_abs[i_min] + 0.09
    left = np.argmin(np.abs(j_abs[: i_min] - j_ref))
    right = i_min + np.argmin(np.abs(j_abs[i_min:] - j_ref))
    ax2.plot(code[[left, right]], j_abs[[left, right]], "o", color="tab:purple",
             mfc="white", markersize=7)
    ax2.annotate("", xy=(code[right], j_ref), xytext=(code[left], j_ref),
                 arrowprops=dict(arrowstyle="<->", color="0.45", lw=1.0))
    ax2.text(0.5 * (code[left] + code[right]), j_ref + 0.012,
             "same J on both sides —\nmust dither the code to find downhill",
             fontsize=8.5, ha="center", color="0.35")
    ax2.set_title("Magnitude cost (not used by the loop)\nJ = Σ|h_m|", fontsize=10.5)
    ax2.set_xlabel("CTLE peaking code")
    ax2.set_ylabel("Σ|h_m| (norm.)")
    ax2.set_xlim(0, 15)
    ax2.set_ylim(0, None)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Why the CTLE loop nulls the signed correlation rather than minimizing Σ|h_m| (§7-6)",
        fontsize=12, y=1.03,
    )
    fig.tight_layout()
    fig.savefig(OUT / "ctle_cost_functions.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_regimes()
    fig_costs()
    print("wrote", OUT / "ctle_postcursor_regimes.png")
    print("wrote", OUT / "ctle_cost_functions.png")
