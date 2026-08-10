"""
07 - Figures for the results-only summary (OCI_Link_Budget_Summary.md).

Produces:
  - fig_waterfall.png : GEN2 typical-corner budget waterfall (floor + stack vs delivered)
  - fig_tornado.png   : GEN2 margin sensitivity tornado (single-lever swings, report section 8)

All numbers are taken from the report / scripts 04-05 (BWn = 1.5x f3dB convention).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- waterfall (GEN2 typical Tx corner) ----------------
FLOOR = -11.41
LINES = [
    ("Shot/RIN", 1.16),
    ("MPI", 0.21),
    ("ISI+EQ", 1.15),
    ("CD", 0.04),
    ("Jitter", 0.95),
    ("Crosstalk", 0.36),
    ("Threshold", 0.21),
]
REQUIRED = -7.34   # floor + unrounded stack (4.07)
DELIVERED = -6.0   # Tx OMA -3.5 dBm - 2.5 dB link IL
MARGIN = DELIVERED - REQUIRED

fig, ax = plt.subplots(figsize=(9, 5))
labels = ["Floor"] + [n for n, _ in LINES] + ["Required", "Delivered"]
bottoms, heights, colors = [], [], []

bottoms.append(FLOOR); heights.append(0.001); colors.append("#1f77b4")
run = FLOOR
for _, v in LINES:
    bottoms.append(run); heights.append(v); colors.append("#ff7f0e")
    run += v
bottoms.append(REQUIRED); heights.append(0.001); colors.append("#d62728")
bottoms.append(DELIVERED); heights.append(0.001); colors.append("#2ca02c")

x = range(len(labels))
for xi, b, h, c in zip(x, bottoms, heights, colors):
    if h <= 0.001:
        ax.hlines(b, xi - 0.4, xi + 0.4, color=c, linewidth=3)
    else:
        ax.bar(xi, h, bottom=b, color=c, width=0.8, edgecolor="white")

ax.hlines(DELIVERED, -0.5, len(labels) - 0.5, color="#2ca02c", linestyle="--", linewidth=1)
ax.annotate(f"margin +{MARGIN:.2f} dB",
            xy=(len(labels) - 1.55, (REQUIRED + DELIVERED) / 2),
            fontsize=11, color="#2ca02c", fontweight="bold", ha="right", va="center")
ax.annotate("", xy=(len(labels) - 1.5, DELIVERED), xytext=(len(labels) - 1.5, REQUIRED),
            arrowprops=dict(arrowstyle="<->", color="#2ca02c"))

vals = [f"{FLOOR:.2f}"] + [f"+{v:.2f}" for _, v in LINES] + [f"{REQUIRED:.2f}", f"{DELIVERED:.2f}"]
for xi, (b, h, t) in enumerate(zip(bottoms, heights, vals)):
    ax.text(xi, b + max(h, 0.001) + 0.12, t, ha="center", fontsize=9)

ax.set_xticks(list(x))
ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
ax.set_ylabel("OMA (dBm)")
ax.set_title("GEN2 budget waterfall - typical Tx corner (106.25 GBd NRZ CPO)")
ax.set_ylim(-12.3, -4.8)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("fig_waterfall.png", dpi=160)
print("wrote fig_waterfall.png")

# ---------------- tornado (GEN2 margin sensitivity, report section 8) ----------------
SENS = [  # (label, delta dB on the +1.34 dB typical margin)
    ("Tx OMA  \u22123.5 \u2192 \u22121.5 dBm", +2.0),
    ("TIA noise +0.5 \u00b5A (4.5\u21925.0)", -1.0),
    ("TIA noise \u22120.5 \u00b5A (4.5\u21924.0)", +0.9),
    ("MRM EO BW 80 \u2192 40 GHz", -0.8),
    ("Tx transition 0.45 \u2192 0.60 UI", -0.55),
    ("Microbump 25 \u2192 50 fF", -0.5),
    ("Crosstalk iso 20 \u2192 17 dB", -0.4),
    ("Bn \u2192 shape integral", +0.34),
    ("End refl. \u221224 \u2192 \u221219 dB", -0.31),
    ("CDR RJ 141 \u2192 169 fs", -0.19),
]
SENS.sort(key=lambda t: abs(t[1]))

fig2, ax2 = plt.subplots(figsize=(8, 5.5))
y = range(len(SENS))
for yi, (lab, d) in enumerate(SENS):
    ax2.barh(yi, d, color="#2ca02c" if d > 0 else "#d62728", height=0.6)
    ax2.text(d + (0.04 if d > 0 else -0.04), yi, f"{d:+.2f}",
             va="center", ha="left" if d > 0 else "right", fontsize=9)
ax2.axvline(0, color="black", linewidth=1)
ax2.set_yticks(list(y))
ax2.set_yticklabels([lab for lab, _ in SENS], fontsize=9)
ax2.set_xlabel("Margin change (dB) vs +1.34 dB typical baseline")
ax2.set_title("GEN2 margin sensitivity (single-lever swings)")
ax2.set_xlim(-1.5, 2.5)
ax2.grid(axis="x", alpha=0.3)
fig2.tight_layout()
fig2.savefig("fig_tornado.png", dpi=160)
print("wrote fig_tornado.png")
