"""
03 - CPO EQ study at 53.125 GBd (originally the "GEN2 CPO" analysis; after the rate
correction this is the GEN1-rate CPO baseline on the GEN2 canvas).

Produces (OCI-GEN2-CPO-spec canvas, GEN1 column): pulse cursors h-1=0.128 / h+1=0.229 at the
typical 12 ps Tx corner, EQ scenario comparison (CTLE-only net 1.86 dB), analog-CDR jitter
0.73 dB, MPI 0.205 dB at -24 dB ends, stack total 4.23 dB, required OMA -8.70 dBm,
margin +2.70 dB at Tx OMA -3.5 dBm, TIA qualification (9 settings with >=2 dB margin).
NOTE: canvas values (stack 3.90, -9.03, +3.03, 21 settings) predate the BWn = 1.5x f3dB
convention (ER/shot+RIN carried from script 02 at the old shape-integral BWn).

Inputs: TIA tables (common.TIA_DIR), package s4p counterfactual (common.PKG_DIR).
"""
import numpy as np

from common import (Q, IL_LINK, PKG_DIR, Sim, dbm, floor_dbm, load_tia_settings,
                    mpi_penalty, sdd21_from_s4p)

# ---------------- ASSUMPTIONS (judgment calls, not computed) ----------------
ASSUMPTIONS = dict(
    TX_TR_PS=(10.0, 12.0, 17.0),   # 20-80% transition-time corners: fast/typ/max
    RJ_UI=0.012, DJ_UI=0.12,       # analog-CDR jitter (DJ includes 0.04 UI slice DCD)
    ER_DB=4.5,                     # GEN2 ER target (cuts MPI)
    REFL_DB=-24.0,                 # GEN2 end-reflectance target
    MICROBUMP=[(30e-15, 30e-12), (50e-15, 50e-12)],   # C, L bounds
    # stack lines carried from script 02 (rate- and architecture-independent here;
    # BWn = 1.5x f3dB convention, see script 02):
    ER_SHOT=0.177, RIN=0.681, CD=0.01, XTALK=0.36, THRESH=0.21,
    FLOOR_DBM=-12.93,              # design point floor from 01/02
    TX_OMA=-3.5,
)

BAUD = 53.125e9
sim = Sim(BAUD)
NYQ = BAUD / 2

settings = load_tia_settings()
sel = next(s for s in settings if s['key'] == '12211111')
Htia = sim.tia_interp(sel)

# Tx corners as 2 identical poles fitted to 20-80% transition time
Htx = {}
for nm, tr in zip(('fast', 'typ', 'max'), ASSUMPTIONS['TX_TR_PS']):
    H, fp = sim.tx_two_pole_from_tr(tr * 1e-12)
    Htx[nm] = H
    print(f"Tx {nm} {tr:.0f} ps: poles {fp/1e9:.1f} GHz each, cascade f3dB "
          f"{fp*np.sqrt(np.sqrt(2)-1)/1e9:.1f} GHz")

# microbump + package counterfactual
# (RC pole at placeholder 50-ohm effective node impedance; unterminated direct drive)
for C, L in ASSUMPTIONS['MICROBUMP']:
    fres = 1 / (2 * np.pi * np.sqrt(L * C))
    fpole = 1 / (2 * np.pi * 50 * C)
    print(f"microbump C={C*1e15:.0f} fF L={L*1e12:.0f} pH: LC res {fres/1e9:.0f} GHz, RC pole {fpole/1e9:.0f} GHz")
try:
    for p in ('TL_TX_64G', 'TL_RX_64G'):
        fpk, sdd = sdd21_from_s4p(PKG_DIR + p + '.s4p')
        il = -20 * np.log10(np.interp(NYQ, fpk, np.abs(sdd)))
        print(f"package {p}: IL at {NYQ/1e9:.1f} GHz Nyquist = {il:.2f} dB (CPO avoids this)")
except Exception as e:
    print("s4p parse failed:", e)

# ---------------- unequalized pulse decomposition per Tx corner ----------------
for nm in ('fast', 'typ', 'max'):
    pp, pre, post, c, t, ci, kk, y = sim.eval_chain(Htx[nm] * Htia, span=8)
    tt = t / t[ci]
    print(f"\nTx {nm} + TIA: taps h-2..h+3 = {np.round(tt[ci-2:ci+4], 3)}")
    print(f"  pre={pre/c:.3f} post={post/c:.3f}; unequalized PP={pp:.2f} dB")
print("(canvas: typ h-1=0.128, h+1=0.229, unEQ 2.05 dB)")

# ---------------- EQ scenarios (typ corner; costs charged) ----------------
ch_typ = Htx['typ'] * Htia
print("\n--- EQ scenarios, typ Tx ---")
pp0 = sim.eval_chain(ch_typ, span=8)[0]
print(f"A. no EQ: {pp0:.2f} dB")

tot_b, (w_b, pp_b, de_b) = sim.opt_fir(0, 1, ch_typ, span=8)
print(f"B. FIR main+1post: taps={np.round(w_b,3)} -> {tot_b:.2f} dB (isi {pp_b:.2f} + deemph {de_b:.2f})")
tot_c, (w_c, pp_c, de_c) = sim.opt_fir(1, 1, ch_typ, span=8)
print(f"C. FIR3 1pre+1post: taps={np.round(w_c,3)} -> {tot_c:.2f} dB")

best_ctle = (1e9, None)
for fz in np.arange(6e9, 22e9, 1e9):
    for fp in np.arange(28e9, 45e9, 2e9):
        Hc = sim.ctle(fz, fp, fp)
        pp = sim.eval_chain(ch_typ * Hc, span=8)[0]
        ne = sim.ctle_noise_enh(Htia, Hc)
        if pp + 10 * np.log10(ne) < best_ctle[0]:
            best_ctle = (pp + 10 * np.log10(ne), (fz, fp, pp, ne))
fz0, fp0, ppc, ne0 = best_ctle[1]
print(f"D. CTLE only (z={fz0/1e9:.0f}G p={fp0/1e9:.0f}G): {best_ctle[0]:.2f} dB "
      f"(isi {ppc:.2f} + noise {10*np.log10(ne0):.2f})   (canvas: 1.86)")

best_mix = (1e9, None)
for fz in np.arange(8e9, 22e9, 2e9):
    for fp in np.arange(30e9, 45e9, 3e9):
        Hc = sim.ctle(fz, fp, fp)
        ne = sim.ctle_noise_enh(Htia, Hc)
        tw, pl = sim.opt_fir(1, 1, ch_typ * Hc, span=8)
        if tw + 10 * np.log10(ne) < best_mix[0]:
            best_mix = (tw + 10 * np.log10(ne), (fz, fp, ne) + pl)
print(f"E. FIR3+CTLE: {best_mix[0]:.2f} dB (taps={np.round(best_mix[1][3],3)})")

# worst-corner set
ch_max = Htx['max'] * Htia
ppw = sim.eval_chain(ch_max, span=8)[0]
best_ctle_w = (1e9, None)
for fz in np.arange(6e9, 22e9, 2e9):
    for fp in np.arange(28e9, 46e9, 3e9):
        Hc = sim.ctle(fz, fp, fp)
        pp = sim.eval_chain(ch_max * Hc, span=8)[0]
        ne = sim.ctle_noise_enh(Htia, Hc)
        if pp + 10 * np.log10(ne) < best_ctle_w[0]:
            best_ctle_w = (pp + 10 * np.log10(ne), (fz, fp, pp, ne))
tot_fw, _ = sim.opt_fir(1, 1, ch_max, span=8)
print(f"worst Tx 17 ps: no EQ {ppw:.2f} / FIR3 {tot_fw:.2f} / CTLE-only {best_ctle_w[0]:.2f} dB "
      f"(canvas: 4.00 / 3.51 / 3.01)")

# ---------------- jitter on the chosen (CTLE-only) chain ----------------
Hchosen = ch_typ * sim.ctle(fz0, fp0, fp0)
pj, TJ = sim.jitter_pp(Hchosen, ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_UI'], span=8)
print(f"\njitter: TJ={TJ:.3f} UI ({TJ*sim.UI*1e12:.1f} ps) -> PP={pj:.2f} dB   (canvas: 0.73)")

# ---------------- MPI + stack + closure ----------------
mpi = mpi_penalty(ASSUMPTIONS['REFL_DB'], ASSUMPTIONS['REFL_DB'], -35, 4, ASSUMPTIONS['ER_DB'], 0.5)
print(f"MPI (-24 dB ends, ER 4.5, D=0.5): {mpi:.3f} dB   (canvas: 0.205)")

A = ASSUMPTIONS
stack = {'ER/shot': A['ER_SHOT'], 'RIN': A['RIN'], 'MPI': mpi,
         'ISI+EQ net (typ, CTLE-only)': best_ctle[0], 'CD': A['CD'],
         'Jitter': pj, 'Xtalk': A['XTALK'], 'Threshold': A['THRESH']}
tot = sum(stack.values())
print("\n--- 53 GBd CPO stack ---")
for k, v in stack.items():
    print(f"{v:6.3f}  {k}")
print(f"{tot:6.3f}  TOTAL   (canvas: 3.90)")

req = A['FLOOR_DBM'] + tot
m = A['TX_OMA'] - IL_LINK - req
print(f"required OMA at Rx = {req:.2f} dBm (canvas -9.03); margin at Tx OMA {A['TX_OMA']} dBm = "
      f"{m:+.2f} dB (canvas +3.03)")

# ---------------- TIA qualification at this stack ----------------
cnt_bw = cnt_ok = 0
imax = 0.0
for s in settings:
    if s['bw'] < 0.55 * BAUD:
        continue
    cnt_bw += 1
    mm = (A['TX_OMA'] - IL_LINK) - (floor_dbm(s['inr']) + tot)
    if mm >= 2.0:
        cnt_ok += 1
        imax = max(imax, s['inr'])
print(f"\nTIA qualification: {cnt_bw} settings with BW>=0.55x baud; {cnt_ok} close with >=2 dB "
      f"margin (canvas: 21); max i_n among qualifiers = {imax*1e6:.2f} uA")
