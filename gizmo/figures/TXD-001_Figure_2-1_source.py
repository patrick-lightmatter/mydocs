#!/usr/bin/env python3
"""DES-OCI-106G-TXD-001 Rev 0.2 — Figure 2-1. Transmit electrical path block diagram.

Drawn to the Section 2.2 placeholder: one channel, electrical input left, TP2 right;
blocks numbered per Table 2-1; each hop labelled with that row's output interface.
Coefficient path is the Section 7 glitchless update (Tables 7-1 / 7-2, banks in
Table 6-2). Squelch nodes are DES-OCI-106G-SQL-001 §2.4 and Table 7-1 (SQL-005).
Ownership zones follow the Owner column of Table 2-1.
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

W, H = 236.0, 150.0
fig = plt.figure(figsize=(17.2, 17.2 * H / W))
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
    ax.text((x0 + x1) / 2, y1 - 2.2, label, ha='center', va='center', fontsize=8.0,
            fontweight='bold', color='#404040', zorder=6)

def badge(x, y, num, r=1.15, fs=6.2):
    ax.add_patch(Circle((x, y), r, facecolor=NAVY, edgecolor='white', lw=0.6, zorder=7))
    ax.text(x, y, num, ha='center', va='center', fontsize=fs, color='white',
            fontweight='bold', zorder=8)

def block(x0, y0, w, h, title, sub=None, num=None, fs=8.0, sfs=6.0, tfrac=0.70, sfrac=0.30,
          fill='white', edge=NAVY, lw=1.2, zorder=3, badge_pos='tl', tcolor=NAVY, ls='-', tdx=0.0):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.7',
                                facecolor=fill, edgecolor=edge, lw=lw, ls=ls, zorder=zorder))
    cx = x0 + w / 2
    if sub:
        ax.text(cx + tdx, y0 + h * tfrac, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.05)
        ax.text(cx, y0 + h * sfrac, sub, ha='center', va='center', fontsize=sfs, color=DARK,
                zorder=zorder + 3, linespacing=1.12)
    else:
        ax.text(cx, y0 + h / 2, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.05)
    if num:
        if badge_pos == 'tl':
            badge(x0 + 1.55, y0 + h - 1.55, num)
        else:
            badge(x0 + w - 1.45, y0 + h - 1.45, num, r=0.95, fs=5.4)

def head(p_from, p_to, color, L=1.6, half_w=0.7, z=5):
    d = np.array(p_to, float) - np.array(p_from, float)
    nrm = np.linalg.norm(d)
    if nrm < 1e-6:
        return tuple(p_to)
    d /= nrm
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

def dot(x, y, color='black', r=0.48):
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor=color, zorder=6))

def label(x, y, s, fs=6.0, ha='center', va='center', color=DARK, rot=0, bold=False, bbox=False,
          style='normal'):
    kw = {}
    if bbox:
        kw['bbox'] = dict(boxstyle='square,pad=0.12', facecolor='white', edgecolor='none', alpha=0.94)
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, rotation=rot,
            fontweight='bold' if bold else 'normal', fontstyle=style, zorder=9,
            linespacing=1.12, **kw)

# ------------------------------------------------------------------ ownership zones (Table 2-1 Owner column)
POST, MAIN, PRE = 42.0, 56.0, 70.0
Y0, Y1 = 6.0, 145.0
zone(1.6, 76.5, Y0, Y1, 'CDNS — TX PLL, serializer, pre-driver, branch phases  (#1, #2)', '#EDF3FA')
zone(78.5, 168.0, Y0, Y1, 'LM — driver output stage, microbump and pad; tap matching at TP1  (#3, #4)', '#F7F3EC')
zone(170.0, 234.4, Y0, Y1, 'Photonics — MRM, bus waveguide, Band-Mux  (#5)', '#F4F4F4')
label(77.5, 24, 'CDNS → LM', fs=5.6, rot=90, color=GRAY, style='italic')
label(169.0, 24, 'to photonics', fs=5.6, rot=90, color=GRAY, style='italic')

# ------------------------------------------------------------------ #1 serializer, source mux, #2 pre-driver
block(3.5, 128.0, 28, 12.2, 'Line-clock chain', 'host-derived ±50 ppm\nDES-OCI-106G-CLK-001 §7',
      fs=7.2, sfs=5.8, tfrac=0.72, sfrac=0.32, edge=GRAY, lw=0.9, ls=(0, (3, 2)), tcolor=DARK)
block(3.5, 46, 28, 20, 'TX PLL and\nserializer', 'legal static park states\n(Table 4-1)',
      num='#1', fs=7.8, sfs=5.8, tfrac=0.66, sfrac=0.26)
route([(17.5, 128.0), (17.5, 66)], 'clk')
label(19.6, 100, 'line clock', fs=5.6, rot=90, color=GRAY)

block(35.5, 49, 15, 14, 'Source mux', 'MISSION\nDESKEW\nHOLD',
      fs=7.0, sfs=5.6, tfrac=0.78, sfrac=0.36)
route([(31.5, MAIN), (35.5, MAIN)], 'sig')
label(33.4, 69.2, 'full-rate NRZ\ninto the pre-driver', fs=5.5)
route([(50.5, MAIN), (54.5, MAIN)], 'sig')

block(54.5, 36, 20, 42, 'Input\npre-driver', 'level shift and fan-out\n0 / 1 / 2 UI phases\n(Table 6-3)',
      num='#2', fs=7.8, sfs=5.8, tfrac=0.78, sfrac=0.34)

for y, name in ((PRE, '0 UI  pre'), (MAIN, '1 UI  main'), (POST, '2 UI  post')):
    route([(74.5, y), (90, y)], 'sig')
    label(78.6, y + 1.45, name, fs=5.3, va='bottom', bbox=True)
label(64.5, 31.6, 'three tap-slice inputs\n(pre, main, post)', fs=5.5, va='top')

# ------------------------------------------------------------------ #3 TX driver: tap slices, sum, hard clip, L_out
DX0, DY0, DW, DH = 86, 26, 48, 60          # top = 86, right = 134
ax.add_patch(FancyBboxPatch((DX0, DY0), DW, DH, boxstyle='round,pad=0,rounding_size=0.8',
                            facecolor='#FFFcf8', edgecolor=NAVY, lw=1.15, zorder=2))
label(118, DY0 + DH - 3.2, 'TX driver output stage', fs=7.8, bold=True, color=NAVY)
badge(DX0 + 2.3, DY0 + DH - 3.1, '#3')
label(118, DY0 + DH - 6.3, 'signed analog tap slices  ·  LM', fs=5.6, color=DARK)

def tap(y, title, sub):
    block(90, y - 4.3, 17, 8.6, title, sub, fs=7.0, sfs=5.4, tfrac=0.70, sfrac=0.28)

tap(PRE, 'Pre tap', '0 to −0.25 · ≥ 2 bit')
tap(MAIN, 'Main tap', 'signed weight')
tap(POST, 'Post tap', '0 to −0.25 · ≥ 2 bit')

SX = 115.0
ax.add_patch(Circle((SX, MAIN), 1.85, facecolor='white', edgecolor='black', lw=1.15, zorder=5))
label(SX, MAIN + 0.15, 'Σ', fs=8.5, bold=True, color='black')
label(113.4, 49.4, 'hard clip', fs=5.4, ha='right')
route([(107, PRE), (SX, PRE), (SX, MAIN + 1.85)], 'sig')
route([(107, MAIN), (SX - 1.85, MAIN)], 'sig')
route([(107, POST), (SX, POST), (SX, MAIN - 1.85)], 'sig')

block(119.2, MAIN - 4.6, 8.0, 9.2, 'L_out', 'series\npeaking', fs=7.0, sfs=5.2, tfrac=0.74, sfrac=0.30)
route([(SX + 1.85, MAIN), (119.2, MAIN)], 'sig')
route([(127.2, MAIN), (148, MAIN)], 'sig')
label(132.6, MAIN + 2.3, 'V_high / V_low', fs=5.5, va='bottom', bbox=True)
label(132.6, MAIN - 2.15, 'differential drive', fs=5.3, va='top', bbox=True)

block(90, 27.4, 24, 7.4, 'swing-mute DAC', 'swing path · weights held',
      fs=6.4, sfs=5.2, tfrac=0.70, sfrac=0.28)

# ------------------------------------------------------------------ #4 microbump and the independent bias network
block(148, 44, 15.5, 24, 'TX microbump\nand pad', 'ESD · package',
      num='#4', fs=7.2, sfs=5.8, tfrac=0.68, sfrac=0.24)
block(148, 26.2, 15.5, 14.0, 'MRM bias\nnetwork', 'V_bias · DC path',
      fs=7.0, sfs=5.6, tfrac=0.70, sfrac=0.26)

# DC bias joins the swing only at the TP1 node
route([(163.5, 33.2), (168.4, 33.2), (168.4, MAIN)], 'sig', arrow=False)
dot(168.4, MAIN)
label(170.2, 44.5, 'DC bias', fs=5.4, rot=90, color=DARK)
route([(163.5, MAIN), (176, MAIN)], 'sig')
ax.add_line(Line2D([165.6, 165.6], [MAIN - 3.2, MAIN + 3.2], color=DARK, lw=1.5, zorder=6))
label(165.6, 71.2, 'TP1', fs=7.4, bold=True, va='bottom')

label(118, 18.4, 'TP1  buried in-package, no physical access, extracted load ≈ 150 fF  (Tables 2-3, 8-1)',
      fs=5.5)
label(118, 14.6, 'swing_mute and V_bias / v_sq are separate nodes — no shared control, no supply collapse (SQL-005)',
      fs=5.5, color=BLUE)

# ------------------------------------------------------------------ #5 MRM → waveguide → Band-Mux → TP2
block(176, 45, 15, 22, 'Micro-ring\nmodulator', 'electro-optic\nring Q',
      num='#5', fs=7.2, sfs=5.6, tfrac=0.68, sfrac=0.26)
route([(191, MAIN), (202, MAIN)], 'opt')
label(196.5, MAIN + 2.05, 'bus waveguide', fs=5.4, va='bottom', color=ORANGE, bbox=True)
block(202, 47, 13, 18, 'Band-Mux', 'WDM band\nmultiplexer', fs=7.2, sfs=5.6, tfrac=0.68, sfrac=0.28)
route([(215, MAIN), (226, MAIN)], 'opt')
label(219.2, MAIN + 1.6, 'fiber', fs=5.4, va='bottom', color=ORANGE)
ax.add_line(Line2D([227.6, 227.6], [MAIN - 3.4, MAIN + 3.4], color=DARK, lw=1.5, zorder=6))
label(227.6, MAIN + 4.6, 'TP2', fs=7.4, bold=True, va='bottom')
label(227.6, MAIN - 4.8, 'optical compliance\nat the fiber\nreference plane', fs=5.3, va='top')

# ------------------------------------------------------------------ coefficient path (Section 7): management above the boundary
block(86, 129.2, 40, 11.4, 'Firmware shadow registers',
      'logic-1 and logic-0 banks\npre / main / post · per mode\nand temperature zone (Table 6-2)',
      fs=7.0, sfs=5.4, tfrac=0.78, sfrac=0.34, edge=BLUE, lw=0.95, ls=(0, (3, 2)), tcolor=BLUE)
block(114, 109.6, 34, 10.0, 'Commit strobe sync',
      'armed for the next UI boundary\n(Tables 7-1 / 7-2)',
      fs=7.0, sfs=5.4, tfrac=0.72, sfrac=0.30, edge=BLUE, lw=0.95, ls=(0, (3, 2)), tcolor=BLUE)

ax.add_line(Line2D([84, 154], [126.2, 126.2], color=BLUE, lw=0.9, ls=(0, (1.2, 1.5)), zorder=2))
label(87, 127.2, 'management domain', fs=5.3, ha='left', va='bottom', color=BLUE, style='italic')
label(87, 125.2, 'line-clock domain', fs=5.3, ha='left', va='top', color=BLUE, style='italic')

route([(106, 129.2), (106, 114.6), (114, 114.6)], 'ctl')
label(104.6, 121.5, 'commit\nstrobe', fs=5.3, ha='right', color=BLUE)
route([(148, 114.6), (158, 114.6), (158, 134.9), (126, 134.9)], 'ctl')
label(159.4, 132.4, 'commit count /\ncurrent codes', fs=5.3, ha='left', color=BLUE)

# one UI edge into the top of every slice; horizontals stay in the gaps between slices
BUS = 83.6
route([(114, 109.6), (BUS, 109.6), (BUS, 49.0)], 'ctl', arrow=False)
for gap_y, top_y in ((77.6, PRE + 4.3), (63.0, MAIN + 4.3), (49.0, POST + 4.3)):
    dot(BUS, gap_y, BLUE)
    route([(BUS, gap_y), (98.5, gap_y), (98.5, top_y)], 'ctl')
label(81.6, 92, 'same UI edge\nall three slices', fs=5.3, rot=90, color=BLUE)

# ------------------------------------------------------------------ squelch: three wires, no shared segment (SQL-005)
block(36, 128.4, 38, 12.0, 'TxSquelchSeq',
      'DES-OCI-106G-SQL-001 §2.4\nsrc_sel · swing_mute · v_sq',
      fs=7.2, sfs=5.5, tfrac=0.70, sfrac=0.30, edge=BLUE, lw=0.95, ls=(0, (3, 2)), tcolor=BLUE)

route([(43, 128.4), (43, 63)], 'ctl')
label(44.6, 82, 'src_sel', fs=5.5, ha='left', color=BLUE, bbox=True)

# swing_mute drops in the driver-to-pad gap; v_sq drops beside it into the bias block only
route([(55, 128.4), (55, 103.2), (139.2, 103.2), (139.2, 31.1), (114, 31.1)], 'ctl')
label(108, 104.2, 'swing_mute', fs=5.5, va='bottom', color=BLUE, bbox=True)
route([(68, 128.4), (68, 96.2), (143.6, 96.2), (143.6, 33.2), (148, 33.2)], 'ctl')
label(108, 97.2, 'v_sq    V_bias held', fs=5.5, va='bottom', color=BLUE, bbox=True)

# ------------------------------------------------------------------ legend
lx, ly = 3.5, 2.8
items = [('opt', 'optical'), ('sig', 'electrical signal'),
         ('ctl', 'digital control  (coefficients §7, squelch SQL-001)'),
         ('clk', 'line clock')]
x = lx
for st, txt in items:
    c, ls, lw = STYLE[st]
    ax.add_line(Line2D([x, x + 5], [ly, ly], color=c, ls=ls, lw=lw, zorder=6))
    head((x, ly), (x + 5.6, ly), c, L=1.3, half_w=0.55)
    label(x + 6.2, ly, txt, fs=6.0, ha='left')
    x += 6.2 + 0.56 * len(txt) + 3.0
dot(x + 0.3, ly)
label(x + 1.4, ly, 'junction — crossings without a dot are not connected', fs=6.0, ha='left')
label(234.2, 2.2, 'DES-OCI-106G-TXD-001 Rev 0.2 · Figure 2-1 · Transmit electrical path (one channel)',
      fs=6.0, ha='right', color=GRAY, style='italic')

fig.savefig(OUT, dpi=DPI, facecolor='white')
print('wrote', OUT)
