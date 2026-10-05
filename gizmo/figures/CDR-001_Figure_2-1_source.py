#!/usr/bin/env python3
"""DES-OCI-106G-CDR-001 Rev 0.2 — Figure 2-1. CDR top-level block diagram.

Drawn to the Section 2.2 placeholder: deserialized d/e bus through
early_late_vote_gen → cdr_voter → pathGain + f_path (proportional and frequency
branches) → fsm_phase → piTable. lock_det draws p_inc and state_f. The
signal_valid hold gates en_p / en_f. Every arrow is a Table 2-3 signal name.
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

W, H = 228.0, 124.0
fig = plt.figure(figsize=(16.6, 16.6 * H / W))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

NAVY, BLUE, GRAY, DARK = '#1F3864', '#2E5395', '#7F7F7F', '#333333'
MONO = 'DejaVu Sans Mono'
STYLE = {
    'sig': ('black', '-', 1.3),
    'ctl': (BLUE, (0, (4, 2.2)), 1.1),
}

def zone(x0, x1, y0, y1, label, fill):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fill, edgecolor='#BFBFBF',
                           lw=0.8, ls=(0, (3, 2)), zorder=0))
    ax.text((x0 + x1) / 2, y1 - 2.3, label, ha='center', va='center', fontsize=8.0,
            fontweight='bold', color='#404040', zorder=6)

def block(x0, y0, w, h, title, sub=None, fs=8.0, sfs=5.8, tfrac=0.72, sfrac=0.30,
          fill='white', edge=NAVY, lw=1.2, zorder=3, tcolor=NAVY, ls='-'):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.7',
                                facecolor=fill, edgecolor=edge, lw=lw, ls=ls, zorder=zorder))
    cx = x0 + w / 2
    if sub:
        ax.text(cx, y0 + h * tfrac, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.05)
        ax.text(cx, y0 + h * sfrac, sub, ha='center', va='center', fontsize=sfs, color=DARK,
                zorder=zorder + 3, linespacing=1.12)
    else:
        ax.text(cx, y0 + h / 2, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.05)

def head(p_from, p_to, color, L=1.55, half_w=0.65, z=5):
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

def hop(x, y, r=1.15):
    """Semicircle bridge so a vertical wire crosses a horizontal one without joining."""
    th = np.linspace(-np.pi / 2, np.pi / 2, 24)
    ax.plot(x + r * np.cos(th), y + r * np.sin(th), color='black', lw=1.3,
            solid_capstyle='round', zorder=5)

def label(x, y, s, fs=5.7, ha='center', va='center', color=DARK, rot=0, bold=False,
          bbox=False, style='normal', mono=False):
    kw = {}
    if bbox:
        kw['bbox'] = dict(boxstyle='square,pad=0.12', facecolor='white', edgecolor='none', alpha=0.94)
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, rotation=rot,
            fontweight='bold' if bold else 'normal', fontstyle=style, zorder=9,
            fontfamily=MONO if mono else plt.rcParams['font.family'],
            linespacing=1.12, **kw)

# ------------------------------------------------------------------ zones (Table 2-3 rate column)
Y0, Y1 = 6.2, 118.5
Y = 62.0
zone(1.6, 56.5, Y0, Y1, 'Symbol rate — deserialized 128-bit bus', '#EDF3FA')
zone(58.5, 226.4, Y0, Y1, 'Per dump — one update per cdr_width = 128 UI  (≈ 830 / 415 MHz)', '#F7F3EC')
label(57.5, 22, 'vote bus → dump', fs=5.4, rot=90, color=GRAY, style='italic')

# ------------------------------------------------------------------ d/e bus → early_late_vote_gen → cdr_voter
block(4, Y - 10, 16, 20, 'd / e bus', 'deserialized\n128-bit',
      fs=7.6, sfs=5.6, tfrac=0.70, sfrac=0.30, edge=GRAY, lw=0.9, ls=(0, (3, 2)), tcolor=DARK)
block(26, Y - 12, 26, 24, 'early_late\nvote_gen', 'MM detector · per UI\n(Table 4-1)',
      fs=7.6, sfs=5.6, tfrac=0.70, sfrac=0.28)
route([(20, Y), (26, Y)], 'sig')
label(23, 77.8, 'd(k−1), d(k+1), e(k)', fs=5.3, va='bottom', mono=True)

block(64, Y - 10, 22, 20, 'cdr_voter', 'majority of 128 votes\nacc resets on dump',
      fs=7.8, sfs=5.5, tfrac=0.68, sfrac=0.28)
route([(52, Y), (64, Y)], 'sig')
label(58, Y + 2.3, 'vote × 128', fs=5.4, va='bottom', mono=True, bbox=True)
route([(75, Y + 10), (75, Y + 16)], 'sig')
label(75, Y + 17.6, 'dump', fs=5.5, va='bottom', mono=True)

# ------------------------------------------------------------------ pathGain + f_path: proportional and frequency branches
EX, EY, EW, EH = 96, 38, 64, 52          # right 160, top 90
ax.add_patch(FancyBboxPatch((EX, EY), EW, EH, boxstyle='round,pad=0,rounding_size=0.8',
                            facecolor='#FFFcf8', edgecolor=NAVY, lw=1.15, zorder=2))
label(EX + EW / 2, EY + EH - 3.4, 'pathGain + f_path', fs=8.0, bold=True, color=NAVY)

# diff splits into both branches
route([(86, Y), (92, Y)], 'sig', arrow=False)
dot(92, Y)
route([(92, Y), (92, 76), (104, 76)], 'sig')
route([(92, Y), (92, 52), (108, 52)], 'sig')
label(93.4, 69, 'diff', fs=5.4, ha='left', mono=True, bbox=True)

block(104, 69, 24, 14, 'pathGain', 'proportional\np_inc = en_p ? diff·p_step : 0',
      fs=7.2, sfs=5.1, tfrac=0.74, sfrac=0.32)
block(108, 45, 24, 14, 'f_path', 'saturating state_f\nf_out = floor(state_f / f_div)',
      fs=7.2, sfs=5.1, tfrac=0.74, sfrac=0.32)

SX, SY = 150.5, Y
ax.add_patch(Circle((SX, SY), 1.9, facecolor='white', edgecolor='black', lw=1.15, zorder=5))
label(SX, SY + 0.15, 'Σ', fs=8.5, bold=True)
# Both branches meet the summer on its vertical axis; delta leaves on the fsm centerline.
route([(128, 76), (SX, 76), (SX, SY + 1.9)], 'sig')
dot(140, 76)
label(133, 77.7, 'p_inc', fs=5.3, va='bottom', mono=True, bbox=True)
route([(132, 52), (SX, 52), (SX, SY - 1.9)], 'sig')
label(135.2, 49.5, 'f_out', fs=5.3, va='top', mono=True, bbox=True)

# ------------------------------------------------------------------ fsm_phase → piTable
block(166, Y - 10, 24, 20, 'fsm_phase', 'state_p wraps\npi_code = floor(state_p / p_div)',
      fs=7.6, sfs=5.3, tfrac=0.72, sfrac=0.28)
route([(SX + 1.9, Y), (166, Y)], 'sig')
label(162, Y + 2.2, 'delta', fs=5.5, va='bottom', mono=True, bbox=True)
route([(178, Y + 17), (178, Y + 10)], 'ctl')
label(178, Y + 18.4, 'flip_dir', fs=5.4, va='bottom', mono=True, color=BLUE)

block(196, Y - 10, 20, 20, 'piTable', '5-bit code → delay\nMFG-003 calibration',
      fs=7.6, sfs=5.4, tfrac=0.70, sfrac=0.28)
route([(190, Y), (196, Y)], 'sig')
label(193, Y + 2.2, 'pi_code', fs=5.4, va='bottom', mono=True, bbox=True)
route([(216, Y), (224.5, Y)], 'sig')
label(220.2, Y + 2.3, 'PI control word', fs=5.3, va='bottom')
label(220.2, Y - 2.4, 'sampler delay', fs=5.2, va='top', color=GRAY)

# ------------------------------------------------------------------ lock_det from p_inc and state_f
block(108, 14, 40, 16, 'lock_det', 'two observables · persistence\nSection 9 · CDR-005',
      fs=7.6, sfs=5.4, tfrac=0.70, sfrac=0.28)
# p_inc tap drops from the upper wire and bridges over f_out
route([(140, 76), (140, 52 + 1.15)], 'sig', arrow=False)
hop(140, 52)
route([(140, 52 - 1.15), (140, 30)], 'sig')
label(141.5, 66, 'p_inc', fs=5.2, ha='left', mono=True, bbox=True)
route([(120, 45), (120, 30)], 'sig')
label(121.5, 38.5, 'state_f', fs=5.2, ha='left', mono=True, bbox=True)
route([(148, 22), (168, 22)], 'sig')
label(158, 23.6, 'cdr_lock', fs=5.5, va='bottom', mono=True, bbox=True)
label(158, 19.6, 'link SM · adaptation (ADP-001)', fs=5.2, va='top', color=GRAY)

# ------------------------------------------------------------------ signal_valid hold gates en_p / en_f (Section 10)
block(104, 100, 46, 13, 'signal_valid hold', 'forces en_p = en_f = 0\nstate held · CDR-006 · Section 10',
      fs=7.4, sfs=5.4, tfrac=0.72, sfrac=0.30, edge=BLUE, lw=0.95, ls=(0, (3, 2)), tcolor=BLUE)
route([(88, 106.5), (104, 106.5)], 'ctl')
label(90, 109.2, 'signal_valid', fs=5.4, ha='left', va='bottom', mono=True, color=BLUE)
label(90, 112.2, 'LOM-004 / RXO-006', fs=5.1, ha='left', va='bottom', color=GRAY)

route([(116, 100), (116, 83)], 'ctl')
label(117.4, 91.5, 'en_p', fs=5.4, ha='left', mono=True, color=BLUE, bbox=True)
route([(138, 100), (138, 88), (132, 88), (132, 59)], 'ctl')
label(139.4, 94, 'en_f', fs=5.4, ha='left', mono=True, color=BLUE, bbox=True)

# signal_valid also a lock_det input (Table 2-3); crosses diff with no dot
route([(104, 106.5), (90, 106.5), (90, 22), (108, 22)], 'ctl')
dot(90, 106.5, BLUE)
label(88.4, 88, 'signal_valid', fs=5.2, ha='right', rot=90, mono=True, color=BLUE)

# ------------------------------------------------------------------ legend
lx, ly = 4, 2.6
items = [('sig', 'loop signal  (Table 2-3)'),
         ('ctl', 'hold / enable  (signal_valid, en_p, en_f, flip_dir)')]
x = lx
for st, txt in items:
    c, ls, lw = STYLE[st]
    ax.add_line(Line2D([x, x + 5], [ly, ly], color=c, ls=ls, lw=lw, zorder=6))
    head((x, ly), (x + 5.6, ly), c, L=1.3, half_w=0.55)
    label(x + 6.3, ly, txt, fs=6.0, ha='left')
    x += 6.3 + 0.55 * len(txt) + 4
dot(x, ly)
label(x + 1.3, ly, 'junction — crossings without a dot are not connected', fs=6.0, ha='left')
label(226.2, 2.0, 'DES-OCI-106G-CDR-001 Rev 0.2 · Figure 2-1 · CDR top level (one channel)',
      fs=6.0, ha='right', color=GRAY, style='italic')

fig.savefig(OUT, dpi=DPI, facecolor='white')
print('wrote', OUT)
