#!/usr/bin/env python3
"""DES-OCI-106G-EYM-001 Rev 0.2 — Figure 2-1. Eye monitor block diagram.

Drawn to the Section 2.2 placeholder: one channel; the monitor is the ninth slice
beside the greyed mission path. Blocks are numbered with Table 2-2 and labelled
with its Class / RTL names and the Table 6-2 register names. The dashed boundary
is the Table 9-1 observe-only termination: the scan loop closes only through
registers. Solid arrows are sampled data, dashed arrows are register / control,
dotted arrows are clocks.
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

W, H = 240.0, 104.0
# Same points per data-unit as the previous canvas, so the type does not change size.
fig = plt.figure(figsize=(16.6 * W / 252.0, 16.6 * H / 252.0))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis('off')

NAVY, BLUE, GRAY, DARK = '#1F3864', '#2E5395', '#7F7F7F', '#333333'
TEAL, AMBER = '#1F6B5A', '#8A6A2F'
MONO = 'DejaVu Sans Mono'
STYLE = {
    'sig':  ('black', '-', 1.25),
    'ctl':  (BLUE, (0, (4, 2.2)), 1.05),
    'clk':  (GRAY, (0, (1.2, 1.6)), 1.35),
    'gate': (AMBER, (0, (3.2, 1.8)), 1.0),
}
GREY_E, GREY_T, GREY_F = '#8A8A8A', '#4E4E4E', '#F4F4F4'

def zone(x0, x1, y0, y1, label, fill, edge='#BFBFBF', lw=0.8, ls=(0, (3, 2)),
         tc='#404040', fs=7.3, dy=2.05):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fill, edgecolor=edge,
                           lw=lw, ls=ls, zorder=0))
    if label:
        ax.text((x0 + x1) / 2, y1 - dy, label, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tc, zorder=6)

def badge(x, y, num, r=1.15, fs=6.0):
    ax.add_patch(Circle((x, y), r, facecolor=NAVY, edgecolor='white', lw=0.6, zorder=7))
    ax.text(x, y, num, ha='center', va='center', fontsize=fs, color='white',
            fontweight='bold', zorder=8)

def block(x0, y0, w, h, title, sub=None, num=None, fs=7.3, sfs=5.05, tfrac=0.68, sfrac=0.30,
          fill='white', edge=NAVY, lw=1.15, zorder=3, tcolor=NAVY, ls='-', tdx=0.0):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.55',
                                facecolor=fill, edgecolor=edge, lw=lw, ls=ls, zorder=zorder))
    cx = x0 + w / 2 + tdx
    if sub:
        ax.text(cx, y0 + h * tfrac, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.02)
        ax.text(x0 + w / 2, y0 + h * sfrac, sub, ha='center', va='center', fontsize=sfs,
                color=DARK, zorder=zorder + 3, linespacing=1.08)
    else:
        ax.text(cx, y0 + h / 2, title, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tcolor, zorder=zorder + 3, linespacing=1.02)
    if num:
        badge(x0 + 1.55, y0 + h - 1.5, num)

def head(p_from, p_to, color, L=1.4, half_w=0.55, z=5):
    d = np.array(p_to, float) - np.array(p_from, float)
    nrm = np.linalg.norm(d)
    if nrm < 1e-6:
        return tuple(p_to)
    d /= nrm
    n = np.array([-d[1], d[0]])
    tip = np.array(p_to, float)
    base = tip - d * L
    ax.add_patch(Polygon([tip, base + n * half_w, base - n * half_w], closed=True,
                         facecolor=color, edgecolor=color, lw=0.3, zorder=z))
    return tuple(base)

def route(pts, style='sig', arrow=True, z=4):
    color, ls, lw = STYLE[style]
    pts = [tuple(map(float, p)) for p in pts]
    if arrow:
        base = head(pts[-2], pts[-1], color, z=z + 1)
        pts = pts[:-1] + [base]
    ax.add_line(Line2D([p[0] for p in pts], [p[1] for p in pts], color=color, ls=ls, lw=lw,
                       zorder=z, solid_capstyle='butt'))

def hline(x0, x1, y, style='ctl', hops=(), arrow=False, z=4, r=1.55):
    """Horizontal run. hops are x positions of vertical wires it crosses without joining."""
    color, ls, lw = STYLE[style]
    direction = 1.0 if x1 >= x0 else -1.0
    hs = [h for h in hops if (h - x0) * direction > r and (x1 - h) * direction > r]
    hs.sort(reverse=(direction < 0))
    cursor = float(x0)
    for hx in hs:
        stop = hx - direction * r
        ax.add_line(Line2D([cursor, stop], [y, y], color=color, ls=ls, lw=lw,
                           zorder=z, solid_capstyle='butt'))
        th = np.linspace(np.pi, 0, 20) if direction > 0 else np.linspace(0, np.pi, 20)
        ax.plot(hx + r * np.cos(th), y + r * np.sin(th), color=color, lw=lw,
                solid_capstyle='round', zorder=z + 1)
        cursor = hx + direction * r
    end = float(x1)
    if arrow:
        end = head((cursor, y), (x1, y), color, z=z + 1)[0]
    if abs(end - cursor) > 0.05:
        ax.add_line(Line2D([cursor, end], [y, y], color=color, ls=ls, lw=lw,
                           zorder=z, solid_capstyle='butt'))

def dot(x, y, color='black', r=0.42):
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor=color, zorder=6))

def label(x, y, s, fs=5.05, ha='center', va='center', color=DARK, rot=0, bold=False,
          bbox=False, style='normal', mono=False):
    kw = {}
    if bbox:
        kw['bbox'] = dict(boxstyle='square,pad=0.07', facecolor='white', edgecolor='none', alpha=0.94)
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, rotation=rot,
            fontweight='bold' if bold else 'normal', fontstyle=style, zorder=10,
            fontfamily=MONO if mono else plt.rcParams['font.family'],
            linespacing=1.06, **kw)

# Box sizes follow the rendered text (same point sizes) plus a small pad.
AX, AW = 8.0, 26.0                 # ninth-slice column, right edge 34, center 21
H_BUF, H_SH, H_SL, H_DM, H_CL = 5.8, 6.0, 5.2, 5.6, 8.4
GAP = 3.6
Y_BUF = 47.4                       # top 53.2; leaves the observe-zone title clear
Y_SH = Y_BUF - GAP - H_SH          # 42.6, top 48.6
Y_SL = Y_SH - GAP - H_SL           # 33.8, top 39.0
Y_DM = Y_SL - GAP - H_DM           # 24.6, top 30.2
Y_CL = 6.4                         # top 14.8

PX, PW, PH = 40.0, 42.0, 7.2       # pi_mon
PY = (Y_SH + H_SH / 2) - PH / 2    # centered on mon_sh
TX, TW, TH = 40.0, 26.0, 5.6       # threshold DAC
TY = (Y_SL + H_SL / 2) - TH / 2
OX, OW, OH = 68.5, 22.0, 5.6       # offset DAC, same row
OY = TY
EX, EW, EH = 40.0, 50.0, 9.4       # EyeMonNrz; top stays under the offset wire
EY = 15.6
FX, FW, FH = 198.0, 36.0, 11.0     # firmware, outside the observe boundary
FY = 40.0

DX = 96.0                          # d-word drop
CKX, POSX = 118.0, 140.0           # clock and slave drops

# ------------------------------------------------------------------ zones
zone(1.6, 190.0, 71.5, 101.5,
     'Mission context (greyed)  —  one channel    ·    RXF-001 §8,  CLK-001 §8',
     '#F3F3F3', tc='#5A5A5A', fs=7.1, dy=1.7)
zone(1.6, 190.0, 4.6, 62.2, '', '#F4FAF7', edge=TEAL, lw=1.35, ls=(0, (5, 2.4)))
label(96.0, 60.4, 'observe-only — terminates in registers', fs=7.2, bold=True, color=TEAL)
label(96.0, 58.0,
      'no hardware path from EyeMonNrz to a DAC, a PI code, the CDR, or an adaptation loop    (Table 9-1 item 3)',
      fs=4.85, color=TEAL, style='italic')
zone(194.5, 238.2, FY - 1.6, FY + FH + 3.2, 'Firmware', '#FFF8F0', tc='#8A5A20', fs=6.9, dy=1.5)

# ------------------------------------------------------------------ mission path
block(3.2, 82.6, 16.5, 5.2, 'CTLE output', 'y(t) node', fs=7.0, sfs=5.3, tfrac=0.66, sfrac=0.26,
      fill=GREY_F, edge=GREY_E, tcolor=GREY_T, lw=0.9)
JX, JY = 23.0, 85.2
dot(JX, JY)
route([(19.7, JY), (JX, JY)], 'sig', arrow=False)
route([(JX, JY), (30.0, JY)], 'sig')
block(30.0, 82.8, 22.0, 4.8, 'CTLE-even buffer', fs=6.5, fill=GREY_F, edge=GREY_E, tcolor=GREY_T, lw=0.85)
route([(JX, JY), (JX, 77.6), (30.0, 77.6)], 'sig')
dot(JX, 77.6)
block(30.0, 75.2, 22.0, 4.8, 'CTLE-odd buffer', fs=6.5, fill=GREY_F, edge=GREY_E, tcolor=GREY_T, lw=0.85)

SX, SY, SW, SHH = 58.0, 73.2, 28.0, 8.4
for k in (2, 1):
    ax.add_patch(FancyBboxPatch((SX + 0.7 * k, SY + 0.65 * k), SW, SHH,
                                boxstyle='round,pad=0,rounding_size=0.45',
                                facecolor='#EEEEEE', edgecolor='#9A9A9A', lw=0.55, zorder=2))
block(SX, SY, SW, SHH, 'S/H + comparator', 'eight slices  φ0 … φ7\nCK8_PI[7:0]  →  d(n)',
      fs=6.7, sfs=5.0, tfrac=0.68, sfrac=0.32, fill=GREY_F, edge=GREY_E, tcolor=GREY_T, lw=0.9)
route([(52.0, JY), (55.0, JY), (55.0, SY + SHH - 1.6), (SX, SY + SHH - 1.6)], 'sig')
route([(52.0, 77.6), (55.0, 77.6), (55.0, SY + 2.4), (SX, SY + 2.4)], 'sig')
label(53.2, 81.0, 'even', fs=4.5, color=GRAY, ha='left')
label(53.4, 74.0, 'odd', fs=4.5, color=GRAY, ha='left', va='top')

block(112.0, 82.4, 18.0, 5.4, 'CDR', 'pi_code', fs=7.0, sfs=5.2, tfrac=0.66, sfrac=0.26,
      fill=GREY_F, edge=GREY_E, tcolor=GREY_T, lw=0.85)
block(134.0, 81.5, 24.0, 7.2, 'Data phase\ninterpolator', 'pos_data', fs=6.4, sfs=5.0,
      tfrac=0.68, sfrac=0.20, fill=GREY_F, edge=GREY_E, tcolor=GREY_T, lw=0.85)
route([(130.0, 85.1), (134.0, 85.1)], 'ctl')
label(132.0, 86.6, 'pi_code', fs=4.6, color=BLUE, mono=True, bbox=True)

# CK8_PI into the mission slices, run below the CDR; the CK8 set drops from the branch
CK_Y = SY + SHH * 0.62
route([(134.0, 82.0), (134.0, CK_Y)], 'clk', arrow=False)
route([(134.0, CK_Y), (SX + SW, CK_Y)], 'clk')
label(108.0, CK_Y + 1.45, 'CK8_PI[7:0]', fs=4.6, color=GRAY, va='bottom', bbox=True)
dot(CKX, CK_Y, GRAY)

# ------------------------------------------------------------------ ninth slice, top to bottom
block(AX, Y_BUF, AW, H_BUF, 'mon_buf', 'replica buffer\nstatic dummies · constant load',
      num='#1', fs=7.2, sfs=4.75, tfrac=0.70, sfrac=0.30)
route([(JX, 77.6), (JX, Y_BUF + H_BUF)], 'sig')
label(27.0, 56.4, 'only mission node touched · always-on (item 1)', fs=4.55,
      color=TEAL, style='italic', ha='left', bbox=True)
label(4.6, 42.0, 'ninth slice', fs=4.6, color=TEAL, style='italic', rot=90)

block(AX, Y_SH, AW, H_SH, 'mon_sh', 'track 4 UI · hold 4 UI\nsample on falling CK_MON',
      num='#2', fs=7.2, sfs=4.7, tfrac=0.70, sfrac=0.28)
route([(AX + AW / 2, Y_BUF), (AX + AW / 2, Y_SH + H_SH)], 'sig')
label(AX + AW / 2 + 1.6, (Y_BUF + Y_SH + H_SH) / 2, 'y', fs=4.8, ha='left', bbox=True)

block(AX, Y_SL, AW, H_SL, 'mon_slicer', 'm(n) = sign(y_mon − V_mon)',
      num='#3', fs=7.0, sfs=4.65, tfrac=0.68, sfrac=0.26)
route([(AX + AW / 2, Y_SH), (AX + AW / 2, Y_SL + H_SL)], 'sig')
label(AX + AW / 2 + 1.6, (Y_SH + Y_SL + H_SL) / 2, 'y_mon', fs=4.6, ha='left', mono=True, bbox=True)

block(AX, Y_DM, AW, H_DM, 'DMUX 1:16', 'CK_WMON ∥ CK_WRX[k_mon]\n2-stage retiming → CK_WRX',
      fs=6.5, sfs=4.45, tfrac=0.70, sfrac=0.28)
route([(AX + AW / 2, Y_SL), (AX + AW / 2, Y_DM + H_DM)], 'sig')
label(AX + 6.5, (Y_SL + Y_DM + H_DM) / 2 + 0.7, 'm(n)', fs=4.6, ha='center', va='bottom',
      mono=True, bbox=True)

# ------------------------------------------------------------------ pi_mon and the two DACs
block(PX, PY, PW, PH, 'pi_mon',
      'single-output rotator · CLK-001 §9.4\n'
      'pos_mon = pos_data + 32·k_mon + mon_phase_offset\n'
      'separate filtered supply (item 2)',
      num='#6', fs=7.1, sfs=4.7, tfrac=0.78, sfrac=0.34)
CKY = Y_SH + H_SH * 0.62
route([(PX, CKY), (AX + AW, CKY)], 'clk')
dot(PX - 3.2, CKY, GRAY)
route([(PX - 3.2, CKY), (PX - 3.2, Y_SL + H_SL * 0.72), (AX + AW, Y_SL + H_SL * 0.72)], 'clk')
label(PX - 3.4, CKY + 1.3, 'CK_MON', fs=4.6, color=GRAY, ha='right', va='bottom', bbox=True)
label(35.1, 36.6, 'comp. clock', fs=4.2, color=GRAY, ha='center', va='center', rot=90, bbox=True)

block(TX, TY, TW, TH, 'mon_thresh_dac',
      'V_mon = s·code·V_LSB,mon\nstatic Vp grid only (item 4)',
      num='#4', fs=6.3, sfs=4.4, tfrac=0.70, sfrac=0.28)
VY = Y_SL + H_SL * 0.32
hline(TX, AX + AW, VY, 'sig', arrow=True)
label((TX + AX + AW) / 2, VY + 1.15, 'V_mon', fs=4.5, color=DARK, va='bottom', mono=True, bbox=True)

block(OX, OY, OW, OH, 'mon_offset_dac', 'mon_offset_trim\nvertical-zero cal. §8',
      num='#5', fs=6.2, sfs=4.35, tfrac=0.68, sfrac=0.26)
# offset voltage under the DAC row, into the slicer bottom, clear of the m(n) drop
OY_W = Y_SL - 1.7
route([(OX + 6.0, OY), (OX + 6.0, OY_W)], 'sig', arrow=False)
hline(OX + 6.0, AX + AW * 0.72, OY_W, 'sig', hops=(AX + AW / 2, DX), arrow=False, r=1.05)
route([(AX + AW * 0.72, OY_W), (AX + AW * 0.72, Y_SL)], 'sig')
label(58.0, OY_W - 1.15, 'offset', fs=4.4, color=DARK, va='top', bbox=True)

# calibrated CK8 set and the slave position
route([(CKX, CK_Y), (CKX, PY + PH * 0.62)], 'clk', arrow=False)
hline(CKX, PX + PW, PY + PH * 0.62, 'clk', hops=(DX,), arrow=True, r=1.15)
label(CKX + 1.6, 56.0, 'CK8 set', fs=4.55, color=GRAY, ha='left', rot=90, bbox=True)
route([(146.0, 81.5), (POSX, 81.5), (POSX, PY + PH * 0.28)], 'ctl', arrow=False)
hline(POSX, PX + PW, PY + PH * 0.28, 'ctl', hops=(DX,), arrow=True, r=1.15)
label(POSX + 1.6, 50.0, 'pos_data (slave)', fs=4.5, color=BLUE, ha='left', rot=90, bbox=True)

# ------------------------------------------------------------------ EyeMonNrz and the dwell-validity clears
block(AX, Y_CL, AW, H_CL, 'clears mon_dwell_valid',
      'CDR-006 signal-valid gate\n'
      'CDR-005 re-acq / lock loss\n'
      'CDR-007 gear-shift\n'
      'ADP-002 freeze / non-mission\n'
      'DRX-003 AGC gain step\n'
      'k_mon / slave-mode write',
      fs=4.7, sfs=3.85, tfrac=0.88, sfrac=0.40, fill='#FFFBF3', edge=AMBER, lw=0.85,
      tcolor='#6E5420')
block(EX, EY, EW, EH, 'EyeMonNrz    CK_WRX domain',
      'hit = d ⊕ m   ·   mon_gate_sel\n'
      'mon_settle  ·  mon_dwell\n'
      'mon_hit_count, mon_valid_count (40 bit)\n'
      'mon_start / mon_busy / mon_done  ·  mon_status\n'
      'mon_dwell_valid  ·  mon_event_flags',
      num='#7', fs=7.2, sfs=4.85, tfrac=0.84, sfrac=0.38)
route([(AX + AW, Y_CL + H_CL * 0.45), (EX - 2.4, Y_CL + H_CL * 0.45),
       (EX - 2.4, EY + 2.2), (EX, EY + 2.2)], 'gate')
label(EX - 1.2, (Y_CL + H_CL * 0.45 + EY + 2.2) / 2, 'flag', fs=4.2, color=AMBER, ha='right', bbox=True)
MWY = Y_DM + H_DM * 0.55
route([(AX + AW, MWY), (EX, MWY)], 'sig')
label((AX + AW + EX) / 2, MWY + 1.15, 'm word', fs=4.4, va='bottom', mono=True, bbox=True)
# d word of slice k_mon, off the right side of the mission slices
route([(SX + SW, SY + 1.8), (DX, SY + 1.8)], 'sig', arrow=False)
route([(DX, SY + 1.8), (DX, EY + EH * 0.55)], 'sig', arrow=False)
hline(DX, EX + EW, EY + EH * 0.55, 'sig', arrow=True)
label(DX + 2.2, 46.0, 'd word of slice k_mon\nsame UI index', fs=4.45, ha='left', color=DARK, bbox=True)

# ------------------------------------------------------------------ firmware — the loop closes only through registers
block(FX, FY, FW, FH, 'Scan orchestration',
      'raster · bathtub · contour\n'
      'extrapolation (§7)\n'
      'calibration (§8)\n'
      'FDR log (MGT-003)\n'
      'loop closes only\nthrough registers',
      num='#8', fs=6.8, sfs=4.9, tfrac=0.82, sfrac=0.38,
      fill='#FFFDF8', edge='#C47B2B', lw=1.0, tcolor='#8A4E12')

# Register writes gather on short risers into the compact firmware block.
PI_REG_Y = PY + PH * 0.78
TH_REG_Y = TY + TH + 1.6
OFF_Y = OY + OH / 2
EYE_HI = EY + EH * 0.72
EYE_LO = EY + EH * 0.28
R_TH, R_OFF, R_HI, R_LO = 192.5, 188.8, 185.2, 220.0
hline(FX, PX + PW, PI_REG_Y, 'ctl', hops=(DX, CKX, POSX, R_TH, R_OFF), arrow=True, r=1.1)
label(155.0, PI_REG_Y + 1.3, 'k_mon, mon_phase_offset −16…+15, mon_slave_en',
      fs=4.3, color=BLUE, ha='center', va='bottom', mono=True, bbox=True)
hline(R_TH, TX + TW / 2, TH_REG_Y, 'ctl', hops=(DX, CKX, POSX, R_OFF, R_HI), arrow=False, r=1.1)
route([(TX + TW / 2, TH_REG_Y), (TX + TW / 2, TY + TH)], 'ctl')
route([(R_TH, TH_REG_Y), (R_TH, FY + 7.2), (FX, FY + 7.2)], 'ctl')
label(148.0, TH_REG_Y + 1.25, 'mon_thresh_sign, mon_thresh_code', fs=4.3, color=BLUE,
      ha='center', va='bottom', mono=True, bbox=True)
hline(R_OFF, OX + OW, OFF_Y, 'ctl', hops=(DX, CKX, POSX, R_HI), arrow=False, r=1.1)
route([(R_OFF, OFF_Y), (R_OFF, FY + 4.6), (FX, FY + 4.6)], 'ctl')
label(150.0, OFF_Y + 1.2, 'mon_offset_trim', fs=4.4, color=BLUE, va='bottom', mono=True, bbox=True)
hline(R_HI, EX + EW, EYE_HI, 'ctl', hops=(DX,), arrow=False, r=1.1)
route([(R_HI, EYE_HI), (R_HI, FY + 1.4), (FX, FY + 1.4)], 'ctl')
label(145.0, EYE_HI + 1.2, 'mon_start, mon_gate_sel, mon_settle, mon_dwell',
      fs=4.15, color=BLUE, va='bottom', mono=True, bbox=True)
hline(EX + EW, R_LO, EYE_LO, 'ctl', hops=(DX,), arrow=False, r=1.1)
route([(R_LO, EYE_LO), (R_LO, FY)], 'ctl')
label(145.0, EYE_LO - 1.15, 'counts, mon_done, mon_dwell_valid, mon_status',
      fs=4.15, color=BLUE, va='top', mono=True, bbox=True)

# ------------------------------------------------------------------ legend
lx, ly = 3.0, 1.7
items = [('sig', 'sampled data'), ('ctl', 'register / control'),
         ('clk', 'clock'), ('gate', 'clears mon_dwell_valid')]
x = lx
for st, txt in items:
    c, ls, lw = STYLE[st]
    ax.add_line(Line2D([x, x + 5.0], [ly, ly], color=c, ls=ls, lw=lw, zorder=6))
    head((x, ly), (x + 5.6, ly), c, L=1.15, half_w=0.46)
    label(x + 6.3, ly, txt, fs=5.0, ha='left')
    x += 6.3 + 0.50 * len(txt) + 2.8
label(x + 0.4, ly, 'an arch crosses without joining', fs=5.0, ha='left', color=GRAY, style='italic')
label(238.2, 1.55, 'DES-OCI-106G-EYM-001 Rev 0.2  ·  Figure 2-1  ·  one channel',
      fs=5.0, ha='right', color=GRAY, style='italic')

fig.savefig(OUT, dpi=DPI, facecolor='white')
print('wrote', OUT)
