"""
07 - Figures for the results-only summary (OCI_Link_Budget_Summary.md).

Produces:
  - fig_waterfall.png : GEN2 typical-corner budget waterfall (floor + stack -> required
                        OMA, vs delivered OMA; margin = shaded gap)
  - fig_tornado.png   : GEN2 margin sensitivity (bars run from the +1.34 dB baseline to
                        the resulting margin when one lever moves; same axis convention
                        as the waterfall's margin)

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

fig, ax = plt.subplots(figsize=(10, 5.5))
labels = ["Receiver\nfloor"] + [n for n, _ in LINES] + ["Required\nOMA", "Delivered\nOMA"]
n = len(labels)

# margin band, drawn first so bars sit on top
ax.axhspan(REQUIRED, DELIVERED, color="#2ca02c", alpha=0.12)

# floor level bar
ax.bar(0, 0.12, bottom=FLOOR - 0.12, color="#1f77b4", width=0.8)
ax.text(0, FLOOR - 0.35, f"{FLOOR:.2f}", ha="center", fontsize=9, fontweight="bold")

run = FLOOR
levels = [FLOOR]
for i, (nm, v) in enumerate(LINES, start=1):
    ax.bar(i, v, bottom=run, color="#ff7f0e", width=0.8, edgecolor="white")
    ax.text(i, run + v + 0.10, f"+{v:.2f}", ha="center", fontsize=9)
    run += v
    levels.append(run)

# step connectors between cumulative levels
for i in range(len(levels) - 1):
    ax.plot([i + 0.4, i + 1 - 0.4], [levels[i + 1] - LINES[i][1], levels[i + 1] - LINES[i][1]],
            color="gray", linewidth=0.8, linestyle=":")

# required and delivered level bars
ax.bar(n - 2, 0.12, bottom=REQUIRED - 0.12, color="#d62728", width=0.8)
ax.text(n - 2, REQUIRED - 0.35, f"{REQUIRED:.2f}", ha="center", fontsize=9,
        fontweight="bold", color="#d62728")
ax.bar(n - 1, 0.12, bottom=DELIVERED - 0.12, color="#2ca02c", width=0.8)
ax.text(n - 1, DELIVERED + 0.15, f"{DELIVERED:.2f}", ha="center", fontsize=9,
        fontweight="bold", color="#2ca02c")

# guide lines across the chart at required and delivered
ax.axhline(REQUIRED, color="#d62728", linewidth=0.8, linestyle="--", alpha=0.6)
ax.axhline(DELIVERED, color="#2ca02c", linewidth=0.8, linestyle="--", alpha=0.6)

# margin arrow between the two levels
ax.annotate("", xy=(n - 1.5, DELIVERED), xytext=(n - 1.5, REQUIRED),
            arrowprops=dict(arrowstyle="<->", color="#2ca02c", linewidth=1.5))
ax.text(n - 1.62, (REQUIRED + DELIVERED) / 2, f"margin\n+{MARGIN:.2f} dB",
        fontsize=11, color="#2ca02c", fontweight="bold", ha="right", va="center")

ax.text(0.02, 0.97,
        "Read left to right: penalties stack on the receiver noise floor to give the\n"
        "required OMA (\u22127.34). Delivered OMA (\u22126.00 = Tx \u22123.5 dBm \u2212 2.5 dB link IL)\n"
        "sits above it; the gap is the +1.34 dB margin.",
        transform=ax.transAxes, fontsize=9, va="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="lightgray"))

ax.set_xticks(range(n))
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("OMA (dBm)")
ax.set_title("GEN2 budget waterfall — typical Tx corner (106.25 GBd NRZ CPO)")
ax.set_ylim(-12.4, -4.4)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig("fig_waterfall.png", dpi=160)
print("wrote fig_waterfall.png")

# ---------------- sensitivity (resulting margin per single lever) ----------------
BASE = 1.34  # typical-corner margin, same number as the waterfall gap
SENS = [  # (label, delta dB on the typical margin)
    ("Tx OMA  \u22123.5 \u2192 \u22121.5 dBm", +2.0),
    ("TIA noise 4.5 \u2192 5.0 \u00b5A", -1.0),
    ("TIA noise 4.5 \u2192 4.0 \u00b5A", +0.9),
    ("MRM EO BW 80 \u2192 40 GHz", -0.8),
    ("Tx transition 0.45 \u2192 0.60 UI", -0.55),
    ("Microbump 25 \u2192 50 fF", -0.5),
    ("Crosstalk iso 20 \u2192 17 dB", -0.4),
    ("Bn \u2192 shape integral", +0.34),
    ("End refl. \u221224 \u2192 \u221219 dB", -0.31),
    ("CDR RJ 141 \u2192 169 fs", -0.19),
]
SENS.sort(key=lambda t: abs(t[1]))  # largest |delta| ends up at the top of the barh

fig2, ax2 = plt.subplots(figsize=(9, 5.5))
for yi, (lab, d) in enumerate(SENS):
    res = BASE + d
    ax2.barh(yi, d, left=BASE, color="#2ca02c" if d > 0 else "#d62728", height=0.6)
    ax2.text(res + (0.05 if d > 0 else -0.05), yi, f"{res:+.2f}",
             va="center", ha="left" if d > 0 else "right", fontsize=9, fontweight="bold")

ax2.set_ylim(-1.4, len(SENS) + 1.8)
ax2.axvline(BASE, color="black", linewidth=1.2)
ax2.text(BASE + 0.05, len(SENS) + 0.1, f"baseline +{BASE:.2f} dB\n(the waterfall margin)",
         fontsize=9, ha="left", va="bottom")
ax2.axvline(0, color="#d62728", linewidth=1.2, linestyle="--")
ax2.text(0.05, -0.85, "0 dB = link no longer closes", fontsize=9, color="#d62728",
         ha="left", va="center")

ax2.set_yticks(range(len(SENS)))
ax2.set_yticklabels([lab for lab, _ in SENS], fontsize=9)
ax2.set_xlabel("Resulting typical-corner margin (dB) if that one lever moves")
ax2.set_title("GEN2 margin sensitivity — one lever at a time, all else at baseline", pad=28)
ax2.set_xlim(-0.6, 3.9)
ax2.grid(axis="x", alpha=0.25)
fig2.tight_layout()
fig2.savefig("fig_tornado.png", dpi=160)
print("wrote fig_tornado.png")
