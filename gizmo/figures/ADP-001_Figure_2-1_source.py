#!/usr/bin/env python3
"""DES-OCI-106G-ADP-001 Rev 0.2 — Figure 2-1. Adaptation loop nesting and gating.

Drawn to Section 2.2: DigitalMmCdr at rank 0; rings 1–4 per Table 3-1;
ChanEstNrz observe-only beside the ladder; slicer inputs from the left;
RXF-001 Table 2-2 codes on the right; Lock/freeze gating (Table 3-2) above.
pi_code is omitted; the CDR figure already shows the phase interpolator.
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

W, H = 188.0, 100.0
fig = plt.figure(figsize=(15.2, 15.2 * H / W))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

NAVY, BLUE, GRAY, DARK, TEAL = '#1F3864', '#2E5395', '#7F7F7F', '#333333', '#2E6B5A'
MONO = 'DejaVu Sans Mono'
STYLE = {
    'sig':  ('black', '-', 1.25),
    'ctl':  (BLUE, (0, (4, 2.2)), 1.05),
    'gate': (GRAY, (0, (1.2, 1.6)), 1.05),
}

def zone(x0, x1, y0, y1, label, fill):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fill, edgecolor='#BFBFBF',
                           lw=0.8, ls=(0, (3, 2)), zorder=0))
    ax.text((x0 + x1) / 2, y1 - 1.9, label, ha='center', va='center', fontsize=7.2,
            fontweight='bold', color='#404040', zorder=6)

def ring(x0, y0, w, h, rank, name, t_ls, fill='#FFFFFF', edge=NAVY, lw=1.0):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.7',
                                facecolor=fill, edgecolor=edge, lw=lw, zorder=1))
    ax.text(x0 + w / 2, y0 + h - 1.7, f'rank {rank} · {name}', ha='center', va='center',
            fontsize=6.3, fontweight='bold', color=edge, zorder=4)
    ax.text(x0 + w / 2, y0 + h - 3.6, t_ls, ha='center', va='center', fontsize=5.2,
            color=DARK, zorder=4, style='italic')

def block(x0, y0, w, h, title, sub=None, fs=7.2, sfs=5.2, tfrac=0.70, sfrac=0.28,
          fill='white', edge=NAVY, lw=1.1, zorder=5, tcolor=NAVY, ls='-'):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.55',
                                facecolor=fill, edgecolor=edge, lw=lw, ls=ls, zorder=zorder))
    cx = x0 + w / 2
    if sub:
        ax.text(cx, y0 + h * tfrac, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 2, linespacing=1.02)
        ax.text(cx, y0 + h * sfrac, sub, ha='center', va='center', fontsize=sfs, color=DARK,
                zorder=zorder + 2, linespacing=1.08)
    else:
        ax.text(cx, y0 + h / 2, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 2, linespacing=1.02)

def head(p_from, p_to, color, L=1.35, half_w=0.55, z=6):
    d = np.array(p_to, float) - np.array(p_from, float)
    nrm = np.linalg.norm(d)
    if nrm < 1e-6:
        return tuple(p_to)
    d /= nrm
    n = np.array([-d[1], d[0]])
    tip = np.array(p_to, float)
    base = tip - d * L
    ax.add_patch(Polygon([tip, base + n * half_w, base - n * half_w], closed=True,
                         facecolor=color, edgecolor=color, lw=0.4, zorder=z))
    return tuple(base)

def route(pts, style='sig', arrow=True, z=3):
    color, ls, lw = STYLE[style]
    pts = [tuple(map(float, p)) for p in pts]
    if arrow:
        base = head(pts[-2], pts[-1], color, z=z + 1)
        pts = pts[:-1] + [base]
    ax.add_line(Line2D([p[0] for p in pts], [p[1] for p in pts], color=color, ls=ls, lw=lw,
                       zorder=z, solid_capstyle='butt'))

def dot(x, y, color='black', r=0.4):
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor=color, zorder=7))

def label(x, y, s, fs=5.2, ha='center', va='center', color=DARK, rot=0, bold=False,
          bbox=False, style='normal', mono=False):
    kw = {}
    if bbox:
        kw['bbox'] = dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.94)
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, rotation=rot,
            fontweight='bold' if bold else 'normal', fontstyle=style, zorder=10,
            fontfamily=MONO if mono else plt.rcParams['font.family'],
            linespacing=1.08, **kw)

# ------------------------------------------------------------------ zones
Y0, Y1 = 5.0, 96.5
zone(1.2, 42.5, Y0, Y1, 'Observe — RX slicers  (RXF-001 §8)', '#EDF3FA')
zone(44.5, 138.5, Y0, Y1, 'Nesting rank 0 (inner) … 4 (outer)   Tables 2-1, 3-1', '#F7F3EC')
zone(140.5, 186.8, Y0, Y1, 'Actuate — RX front end  (RXF-001 Table 2-2)', '#F1F1F8')

# ------------------------------------------------------------------ nested rings
# Top inset holds the two-line caption; the outer ring keeps a bottom strip for the Vp-code note.
ring(48, 11, 88, 62, 4, 'AgcVpNrz', '≥ 8192 UI · stage 4', fill='#FFF9F2', lw=1.1)
ring(52, 19, 80, 49, 3, 'CtleAdaptNrz', '≥ 4096 UI · stage 3', fill='#FFFCF8')
ring(56, 24, 72, 39, 2, 'OffsetAdaptNrz', '≥ 4096 UI · stage 2')
ring(60, 29, 64, 29, 1, 'VpAdaptNrz', '≈ 32 UI · stage 1', lw=1.15)
# rank 4 right=136 top=73; rank 3 left=52 top=68; rank 2 left=56 top=63; rank 1 left=60 top=58

block(68, 32, 40, 15, 'DigitalMmCdr', 'rank 0 · CDR-001\nMM · 2nd order',
      fs=7.0, sfs=5.0, tfrac=0.68, sfrac=0.28, zorder=6)
# CDR right=108 top=47

block(48, 12.2, 88, 6.2, 'Vp codes → Offset (code_top − code_bot) and AGC (mean |Vp| vs V_target)',
      fs=5.0, fill='#FFF9F2', edge='none', lw=0, tcolor=BLUE, zorder=4)

# ------------------------------------------------------------------ Lock / freeze above the outer ring
block(48, 84, 88, 10.5, 'Lock / freeze', 'signal_valid = 0 holds all · cdr_lock releases stages 1–4 · Table 3-2',
      fs=7.0, sfs=4.9, tfrac=0.68, sfrac=0.28, edge=GRAY, lw=0.95, ls=(0, (3, 2)), tcolor=DARK)

# cdr_lock rises into Lock. pi_code is drawn on the CDR figure, not here.
route([(108, 40), (122, 40), (122, 84)], 'ctl')
label(123.3, 64, 'cdr_lock', fs=5.0, ha='left', mono=True, color=BLUE, bbox=True)

for x in (56, 64, 116, 128):
    route([(x, 84), (x, 73)], 'gate')
label(92, 78.6, 'adapt', fs=5.0, color=GRAY, style='italic')

# ------------------------------------------------------------------ slicers
block(3.2, 26, 22, 24, 'RX slicers', 'd(k), e(k)\ne₊ / e₋',
      fs=7.0, sfs=5.1, tfrac=0.72, sfrac=0.28, edge=GRAY, lw=0.9, ls=(0, (3, 2)), tcolor=DARK)
# Horizontal entries: CDR left=68, rank 1 left=60, rank 3 left=52. All inside the target span.
route([(25.2, 42), (68, 42)], 'sig')
label(46, 43.2, 'd(k±1), e(k)', fs=4.9, va='bottom', mono=True, bbox=True)
route([(25.2, 35), (60, 35)], 'sig')
label(42, 36.2, 'e on active rail', fs=4.8, va='bottom', mono=True, bbox=True)
route([(25.2, 29), (52, 29)], 'sig')
label(38, 30.2, '(d, e) + history', fs=4.7, va='bottom', mono=True, bbox=True)

block(3.2, 6.2, 36, 14, 'ChanEstNrz', 'observe-only ĥ_i\nsnapshot / 65 536 UI · no actuator',
      fs=6.6, sfs=4.9, tfrac=0.70, sfrac=0.28, edge=TEAL, tcolor=TEAL, lw=0.95, ls=(0, (3, 2)))
route([(14.2, 26), (14.2, 20.2)], 'sig')
label(22, 23.2, 'd(k−i)·e(k)', fs=4.8, ha='left', va='center', mono=True, bbox=True)

# ------------------------------------------------------------------ analog plant, one chip per code
chips = [
    (62, 'Vp_top / Vp_bot', '8 b → threshold DACs'),
    (50, 'offset code', '8 b → offset DAC'),
    (38, 'CTLE peaking', '4 b → ADP-004 strobe'),
    (26, 'gain code', '→ AGC gain stage'),
]
for y, title, sub in chips:
    block(148, y - 4.6, 36, 9.2, title, sub, fs=6.2, sfs=4.9, tfrac=0.68, sfrac=0.28)
    route([(136, y), (148, y)], 'ctl')

# ------------------------------------------------------------------ legend
lx, ly = 3.0, 2.2
items = [('sig', 'data observe (d, e)'), ('ctl', 'control code'),
         ('gate', 'adapt enable')]
x = lx
for st, txt in items:
    c, ls, lw = STYLE[st]
    ax.add_line(Line2D([x, x + 4.5], [ly, ly], color=c, ls=ls, lw=lw, zorder=6))
    head((x, ly), (x + 5.0, ly), c, L=1.15, half_w=0.48)
    label(x + 5.6, ly, txt, fs=5.4, ha='left')
    x += 5.6 + 0.50 * len(txt) + 2.6
dot(x, ly)
label(x + 1.1, ly, 'no dot — not connected', fs=5.4, ha='left')
label(186.2, 1.8, 'DES-OCI-106G-ADP-001 Rev 0.2 · Figure 2-1 · one channel',
      fs=5.4, ha='right', color=GRAY, style='italic')

fig.savefig(OUT, dpi=DPI, facecolor='white')
print('wrote', OUT)
