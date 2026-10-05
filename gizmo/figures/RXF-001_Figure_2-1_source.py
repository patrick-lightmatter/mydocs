#!/usr/bin/env python3
"""DES-OCI-106G-RXF-001 Rev 0.2 — Figure 2-1. RX front-end signal chain block diagram.

Drawn to the Section 2.2 placeholder: one channel, optical input left, digital handoff
right; blocks numbered per Table 2-1; control codes per Table 2-2; AGC loop (Section 6),
DCOC loop and average-power monitor (Section 6.3 / 9.1); 8-way interleaved slicer front
end (Section 8, CLK-001 Section 8); ownership zones per the Location column of Table 2-1.
"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon
from matplotlib.lines import Line2D
import numpy as np

plt.rcParams['font.family'] = ['Carlito', 'DejaVu Sans']
plt.rcParams['mathtext.default'] = 'regular'

OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/work/fig.png'
DPI = int(sys.argv[2]) if len(sys.argv) > 2 else 300

W, H = 180.0, 100.0
fig = plt.figure(figsize=(15, 15 * H / W))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

NAVY, BLUE, ORANGE, GRAY, DARK = '#1F3864', '#2E5395', '#C55A11', '#7F7F7F', '#333333'
STYLE = {  # colour, linestyle, linewidth
    'opt':  (ORANGE, '-', 2.0),
    'sig':  ('black', '-', 1.3),
    'ctl':  (BLUE, (0, (4, 2.2)), 1.1),
    'clk':  (GRAY, (0, (1.2, 1.6)), 1.4),
}

# ------------------------------------------------------------------ primitives
def zone(x0, x1, y0, y1, label, fill):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fill, edgecolor='#BFBFBF',
                           lw=0.8, ls=(0, (3, 2)), zorder=0))
    ax.text((x0 + x1) / 2, y1 - 2.3, label, ha='center', va='center', fontsize=9,
            fontweight='bold', color='#404040', zorder=6)

def badge(x, y, num, r=1.15, fs=6.2):
    ax.add_patch(Circle((x, y), r, facecolor=NAVY, edgecolor='white', lw=0.6, zorder=7))
    ax.text(x, y, num, ha='center', va='center', fontsize=fs, color='white',
            fontweight='bold', zorder=8)

def block(x0, y0, w, h, title, sub=None, num=None, fs=8.5, sfs=6.6, tfrac=0.70, sfrac=0.30,
          fill='white', edge=NAVY, lw=1.2, zorder=3, badge_pos='tl', tcolor=NAVY, ls='-', tdx=0.0):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.7',
                                facecolor=fill, edgecolor=edge, lw=lw, ls=ls, zorder=zorder))
    cx = x0 + w / 2
    if sub:
        ax.text(cx + tdx, y0 + h * tfrac, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.1)
        ax.text(cx, y0 + h * sfrac, sub, ha='center', va='center', fontsize=sfs, color=DARK,
                zorder=zorder + 3, linespacing=1.15)
    else:
        ax.text(cx, y0 + h / 2, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.1)
    if num:
        if badge_pos == 'tl':
            badge(x0 + 1.5, y0 + h - 1.5, num)
        else:  # 'tr'
            badge(x0 + w - 1.4, y0 + h - 1.4, num, r=0.95, fs=5.4)

def head(p_from, p_to, color, L=1.6, half_w=0.7, z=5):
    d = np.array(p_to, float) - np.array(p_from, float)
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    tip = np.array(p_to, float); base = tip - d * L
    ax.add_patch(Polygon([tip, base + n * half_w, base - n * half_w], closed=True,
                         facecolor=color, edgecolor=color, lw=0.4, zorder=z))
    return tuple(base)

def route(pts, style='sig', arrow=True, z=4):
    color, ls, lw = STYLE[style]
    pts = [tuple(map(float, p)) for p in pts]
    if arrow:
        base = head(pts[-2], pts[-1], color, z=z + 1)
        pts = pts[:-1] + [base]
    ax.add_line(Line2D([p[0] for p in pts], [p[1] for p in pts], color=color, ls=ls, lw=lw,
                       zorder=z, solid_capstyle='butt'))

def dot(x, y, color='black', r=0.55):
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor=color, zorder=6))

def label(x, y, s, fs=6.3, ha='center', va='center', color=DARK, rot=0, bold=False, bbox=False,
          style='normal'):
    kw = {}
    if bbox:
        kw['bbox'] = dict(boxstyle='square,pad=0.15', facecolor='white', edgecolor='none', alpha=0.92)
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, rotation=rot,
            fontweight='bold' if bold else 'normal', fontstyle=style, zorder=9,
            linespacing=1.12, **kw)

# ------------------------------------------------------------------ ownership zones
Y0, Y1 = 6.5, 95.5
zone(1.5, 50.5, Y0, Y1, 'Photonics partner — PIC  (Table 2-1 location: PIC)', '#F4F4F4')
zone(52.5, 116.5, Y0, Y1, 'SerDes analog block — TIA macro  (Sections 4–7)', '#EDF3FA')
zone(118.5, 158.8, Y0, Y1, 'SerDes RX front end — buffer, slicers, DMUX  (Section 8)', '#F1F1F8')
zone(160.3, 179.5, Y0, Y1, 'RX digital (sibling documents)', '#F6F6F6')

# boundary annotations in the zone gaps
label(51.5, 20, 'PD → TIA boundary  (photonics → SerDes analog)', fs=5.6, rot=90, color=GRAY, style='italic')
label(117.5, 20, 'buffer → slicer boundary  (TIA macro → SerDes RX)', fs=5.6, rot=90, color=GRAY, style='italic')
label(159.55, 17, 'analog → digital handoff', fs=5.6, rot=90, color=GRAY, style='italic')

# ------------------------------------------------------------------ main chain (y 62–74)
YB, HB, YC = 62, 12, 68

# fiber + TP3
route([(1.5, YC), (9, YC)], 'opt', arrow=True)
ax.add_line(Line2D([5, 5], [64.6, 71.4], color=DARK, lw=1.4, zorder=6))
label(5, 72.7, 'TP3', fs=7.5, bold=True, va='bottom')
label(5.2, 60.3, 'optical input at the\nfiber reference plane\n(Table 3-1)', fs=5.8, va='top')
label(7.3, 66.6, 'fiber', fs=5.8, va='top')

block(9, YB, 11, HB, 'Band-Mux', 'WDM band\n(de)multiplexer')
route([(20, YC), (24, YC)], 'opt')
block(24, YB, 12, HB, 'Ring demux\nfilter', 'per-channel λ select', tfrac=0.68, sfrac=0.22)
route([(36, YC), (40, YC)], 'opt')
block(40, YB, 9, HB, 'Photodiode', 'O/E conversion\n(DRX-001)', num='#1')

# PD -> TIA (electrical), with DCOC cancellation junction
route([(49, YC), (55, YC)], 'sig')
label(51.2, 69.4, 'I_PD', fs=6.8, va='bottom')

block(55, YB, 12, HB, 'TIA core', 'transimpedance;\n1st pole with C_PD', num='#2')
route([(67, YC), (71, YC)], 'sig')
block(71, YB, 12, HB, 'AGC gain stage', '65–80 dBΩ · 0.5 dB/LSB\n(Table 6-1)', num='#4')
route([(83, YC), (87, YC)], 'sig')
block(87, YB, 12, HB, 'CTLE', 'one-zero peaking\n2.5–10 dB (Table 5-2)', num='#5')

# output buffer pair (#6)
ax.add_patch(FancyBboxPatch((102.5, 58), 13, 21, boxstyle='round,pad=0,rounding_size=0.7',
                            facecolor='#FBFBFD', edgecolor=NAVY, lw=0.8, ls=(0, (3, 2)), zorder=2))
label(109, 77.3, 'Output buffer', fs=7.2, bold=True, color=NAVY)
badge(104, 77.3, '#6', r=1.05, fs=5.8)
block(103.5, 69.5, 11, 6, 'CTLE-even buffer', fs=7.3)
block(103.5, 60.5, 11, 6, 'CTLE-odd buffer', fs=7.3)
label(109, 59.1, 'slicer input 100–600 mVpp (Table 4-1)', fs=5.5, va='center')
route([(99, YC), (101, YC), (101, 72.5), (103.5, 72.5)], 'sig')
route([(101, YC), (101, 63.5), (103.5, 63.5)], 'sig')
dot(101, YC)

# DCOC (#3) loop around the TIA
block(55, 43.5, 12, 9, 'DC-offset\ncancellation (DCOC)', 'analog loop · f_HP ≤ 100 kHz\n≥ 750 µA (Table 6-3)',
      num='#3', fs=7.8, sfs=6.1, tfrac=0.70, sfrac=0.27)
dot(68.5, YC)
route([(68.5, YC), (68.5, 48), (67, 48)], 'sig')
label(69.2, 56, 'sense', fs=5.6, ha='left')
route([(55, 48), (53.2, 48), (53.2, YC - 0.55)], 'sig', arrow=False)
dot(53.2, YC)
label(52.6, 57.5, 'I_cancel\n(avg. photo-\ncurrent)', fs=5.5, ha='right')

# Average-power monitor (#10)
block(55, 29.5, 12, 9, 'Average-power\nmonitor', 'DC photocurrent readback\n(RXO-006, LOM-001)',
      num='#10', fs=7.8, sfs=6.1, tfrac=0.66, sfrac=0.25, tdx=1.0)
route([(61, 43.5), (61, 38.5)], 'sig')
label(61.7, 41, 'cancellation-current\nreadback', fs=5.5, ha='left')
route([(61, 29.5), (61, 23.5)], 'sig')
label(61, 22.6, 'to management: LOS assert / Pavg readback\n(Section 9.1; RXO-006, DRX-009)', fs=5.8, va='top')

# ------------------------------------------------------------------ top-side firmware / LOM inputs
block(84, 84.2, 20, 5.6, 'Firmware: bandwidth mode 400G / 200G\n(1 b; CMP-006/009; Table 2-2)',
      fs=6.3, fill='#FFFFFF', edge=BLUE, lw=0.9, ls=(0, (3, 2)), tcolor=BLUE)
route([(94, 84.2), (94, 74)], 'ctl')
route([(84, 87), (61, 87), (61, 74)], 'ctl')
label(61.8, 80.5, 'TIA / CTLE pole set\n(Table 5-1)', fs=5.6, ha='left')
label(77, 80.6, 'AGC freeze ← LOM detector\n(LOM-004; DES-OCI-106G-SQL-001 §6)', fs=5.6, va='bottom')
route([(77, 80.2), (77, 74)], 'ctl')

# ------------------------------------------------------------------ slicer array (Section 8)
AX0, AY0, AW, AH = 121, 40, 26, 46
for k in (2, 1):  # stack shadows (×8 slices)
    ax.add_patch(FancyBboxPatch((AX0 + 0.9 * k, AY0 + 0.9 * k), AW, AH,
                                boxstyle='round,pad=0,rounding_size=0.7',
                                facecolor='white', edgecolor=NAVY, lw=0.7, zorder=2))
ax.add_patch(FancyBboxPatch((AX0, AY0), AW, AH, boxstyle='round,pad=0,rounding_size=0.7',
                            facecolor='white', edgecolor=NAVY, lw=1.2, zorder=3))
label(AX0 + AW / 2, 83.4, 'Slicer array — 8 interleaved slices φ0 … φ7\n(one slice shown; CLK-001 Table 8-1)',
      fs=7.0, bold=True, color=NAVY)

# even / odd inputs from the buffers
route([(114.5, 72.5), (121, 72.5)], 'sig')
route([(114.5, 63.5), (121, 63.5)], 'sig')
label(117.7, 73.6, 'even slices\nφ0 / 2 / 4 / 6', fs=5.5, va='bottom')
label(117.7, 62.4, 'odd slices\nφ1 / 3 / 5 / 7', fs=5.5, va='top')
route([(121, 72.5), (122.2, 72.5), (122.2, 63.5), (121, 63.5)], 'sig', arrow=False)
route([(122.2, YC), (123, YC)], 'sig')

# S/H (#7)
block(123, 62.5, 6, 9, 'S/H', 'track 4 UI\nhold 4 UI', num='#7', fs=7.8, sfs=5.8, tfrac=0.70, sfrac=0.30, tdx=0.9)
# summing node (offset subtraction ahead of the slicers)
route([(129, YC), (129.9, YC)], 'sig', arrow=False)
ax.add_patch(Circle((131, YC), 1.1, facecolor='white', edgecolor='black', lw=1.1, zorder=5))
label(131, YC + 0.05, '−', fs=8, bold=True, color='black')
route([(132.1, YC), (134.2, YC)], 'sig', arrow=False)
ax.add_line(Line2D([134.2, 134.2], [59.5, 74.5], color='black', lw=1.3, zorder=4))
dot(134.2, YC)
for y in (74.5, YC, 59.5):
    route([(134.2, y), (135.2, y)], 'sig')

# comparators (#8, #9)
block(135.2, 72.0, 10, 5, 'Error slicer', 'top: +Vp_top → e₊', num='#9', fs=6.6, sfs=6.0,
      tfrac=0.68, sfrac=0.28, badge_pos='tr')
block(135.2, 64.5, 10, 5, 'Data slicer', 'threshold ≈ 0 → d', num='#8', fs=6.6, sfs=6.0,
      tfrac=0.68, sfrac=0.28, badge_pos='tr')
block(135.2, 57.0, 10, 5, 'Error slicer', 'bot: −Vp_bot → e₋', num='#9', fs=6.6, sfs=6.0,
      tfrac=0.68, sfrac=0.28, badge_pos='tr')

# DACs and their reference / offset lines (control style)
block(123, 43, 22.2, 5.5, 'Threshold & offset DACs (Table 8-2)', 'Vp_top, Vp_bot: 8 b each · offset: 8 b',
      fs=6.5, sfs=5.9, tfrac=0.70, sfrac=0.27)
route([(131, 48.5), (131, YC - 1.1)], 'ctl')
label(130.3, 57, 'offset_v', fs=5.5, rot=90, color=BLUE)
route([(139, 48.5), (139, 57)], 'ctl')
label(138.3, 52.6, 'Vp_bot', fs=5.5, rot=90, color=BLUE)
route([(133.2, 48.5), (133.2, 79.5), (140, 79.5), (140, 77)], 'ctl')
label(136.7, 80.0, 'Vp_top', fs=5.5, va='bottom', color=BLUE)

# slice outputs -> DMUX
for y, s in ((74.5, 'e₊'), (YC, 'd'), (59.5, 'e₋')):
    route([(145.2, y), (150, y)], 'sig')
    label(146.1, y + 0.45, s, fs=6.3, va='bottom', bbox=True)

# clock into the array from the PI
route([(161.8, 50), (147, 50)], 'clk')
label(147.4, 49.1, 'CK8_PI[7:0]\none phase φk per slice\nbaud/8 (CLK-001 §8)', fs=5.5, ha='left', va='top', bbox=True)

# DMUX
block(150, 56, 6.5, 24, '1:16 DMUX per slice  (d, e₊, e₋)', fs=7.2)
ax.texts[-1].set_rotation(90)
route([(156.5, YC), (161.8, YC)], 'sig')
dot(158.7, YC)
route([(158.7, YC), (158.7, 31), (161.8, 31)], 'sig')
label(159.6, 47.5, 'd, e words @ CK_WRX', fs=5.8, rot=90, color=DARK)

# ------------------------------------------------------------------ RX digital (zone D)
block(161.8, 62, 16, 12, 'DigitalMmCdr — CDR', 'DES-OCI-106G-CDR-001\nslicer-output handoff (d, e)', num=None,
      fs=8.2, sfs=6.3)
block(161.8, 46, 16, 8, 'Phase interpolator', '+ 8-phase clock generator\nDES-OCI-106G-CLK-001 §8–9',
      fs=7.6, sfs=6.1, tfrac=0.72, sfrac=0.28)
route([(169.8, 62), (169.8, 54)], 'ctl')
label(170.6, 58, 'pi_code', fs=6.0, ha='left', color=BLUE)
block(161.8, 24, 16, 14, 'Adaptation loops',
      'DES-OCI-106G-ADP-001\nVpAdaptNrz · OffsetAdaptNrz\nCtleAdaptNrz · AgcVpNrz\nAGC loop observes Vp codes (§6)',
      fs=8.2, sfs=6.0, tfrac=0.80, sfrac=0.36)

# control bus back into the analog plant (Table 2-2 codes)
route([(169.8, 24), (169.8, 11), (77, 11), (77, YB)], 'ctl')
route([(93, 11), (93, YB)], 'ctl');  dot(93, 11, BLUE)
route([(132, 11), (132, 43)], 'ctl'); dot(132, 11, BLUE)
label(77.8, 36, 'gain code (≥ 5 b)\nAgcVpNrz  (Table 2-2)', fs=6.0, ha='left', color=BLUE)
label(93.8, 36, 'peaking code (4 b)\nCtleAdaptNrz\nvia ADP-004 de-glitch strobe', fs=6.0, ha='left', color=BLUE)
label(132.8, 27, 'Vp_top / Vp_bot codes (8 b × 2)  VpAdaptNrz\noffset code (8 b)  OffsetAdaptNrz\n(Table 2-2)',
      fs=6.0, ha='left', color=BLUE)

# ------------------------------------------------------------------ legend & footer
lx, ly = 4, 3.2
items = [('opt', 'optical'), ('sig', 'electrical signal'), ('ctl', 'digital control code (Table 2-2)'),
         ('clk', 'sampling clock')]
x = lx
for st, txt in items:
    c, ls, lw = STYLE[st]
    ax.add_line(Line2D([x, x + 5], [ly, ly], color=c, ls=ls, lw=lw, zorder=6))
    head((x, ly), (x + 5.6, ly), c, L=1.3, half_w=0.55)
    label(x + 6.4, ly, txt, fs=6.3, ha='left')
    x += 6.4 + 0.62 * len(txt) + 4
dot(x + 0.6, ly); label(x + 1.8, ly, 'junction — crossings without a dot are not connected', fs=6.3, ha='left')
label(178.5, 2.6, 'DES-OCI-106G-RXF-001 Rev 0.2 · Figure 2-1 · RX front-end signal chain (one channel)',
      fs=6.3, ha='right', color=GRAY, style='italic')

fig.savefig(OUT, dpi=DPI, facecolor='white')
print('wrote', OUT)
