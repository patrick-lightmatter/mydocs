"""
04 - GEN2 requirements derivation at 106.25 GBd NRZ, CTLE-only receiver.

Produces (OCI-GEN2-CPO-spec canvas, GEN2 column):
  - 152-setting rescan at 106.25 GBd (motivates a new TIA design class: 0 settings qualify)
  - measured-noise scaling regression: f2-only fit R^2 = 0.871 vs white-only 0.590
  - scaled-design floors at 58 GHz: white-scaled 5.4 uA -> -10.60 dBm, f2-scaled 17 uA -> -5.63 dBm
  - required TIA noise inversion (i_n <= ~4.0 uA for +2 dB margin, pre-microbump accounting)
  - target-class TIA (58 GHz Butterworth-2, 4.5 uA): floor -11.41 dBm
  - final stack incl. 25 fF microbump in the ISI chain: fast/typ/max Tx = 3.74 / 4.07 / 4.62 dB
    -> margins +1.67 / +1.34 / +0.79 dB at Tx OMA -3.5 dBm
  - supporting lines: RIN+shot Q-solve 1.16 dB at BWn = 1.5 x f3dB = 87 GHz, CD 0.04 dB
    booked, TDEC proxy 0.77/1.11/1.77 dB, microbump droop table, jitter 0.95 dB at
    RJ 0.015 / DJ 0.14 UI
  - jitter CDR-fallback check (0.018 UI / 169 fs RJ vs. the 0.015 UI / 141 fs baseline):
    +0.19 dB incremental, re-evaluated at os_r=256 to resolve a sample-grid quantization
    artifact at the default os_r=32 (see Methodology_Provenance.md 2.1)
  NOTE: canvas values (stack 3.74 typ, +1.67, 4.37 uA, RIN+shot 0.82) predate the
  BWn = 1.5x f3dB convention (they used the Butterworth-2 shape integral, 64 GHz).

Inputs: TIA tables (common.TIA_DIR), package s4p (common.PKG_DIR).
"""
import numpy as np
from scipy.optimize import nnls

from common import (Q, RESP, IL_LINK, PKG_DIR, Sim, dbm, floor_dbm, load_tia_settings,
                    mpi_penalty, rin_shot_penalty, sdd21_from_s4p)

# ---------------- ASSUMPTIONS (judgment calls, not computed) ----------------
ASSUMPTIONS = dict(
    TX_TR_UI=(0.35, 0.45, 0.60),  # 20-80% transition corners as fractions of the 9.412 ps UI
    RJ_UI=0.015,                  # 141 fs rms - chosen as aggressive-but-plausible for an
                                  # analog CDR at 106 GBd (0.012 UI = 113 fs judged beyond SOA)
    DJ_UI=0.14,                   # incl. 0.05 UI slice-DCD allocation
    ER_DB=4.5, REFL_DB=-24.0,
    MICROBUMP_C=25e-15,           # tightened GEN2 budget (from the droop scan below)
    CD_BOOKED=0.04,               # ~4x the GEN1 0.01 dB (pulse-sim gives 0.013; booked conservative)
    XTALK=0.36, THRESH=0.21,      # carried from GEN1 (rate-independent in OMA domain)
    TIA_TARGET_F3DB=58e9,         # required-class reference response (Butterworth-2)
    TIA_TARGET_IN=4.5e-6,         # target-class noise (internal, unreferenced estimate for
                                  # 100GBd-class TIAs: ~2.5-5 uA / 55-65 GHz -- not a cited source)
    TX_OMA=-3.5,
)

BAUD = 106.25e9
sim = Sim(BAUD)
NYQ = BAUD / 2
print(f"UI = {sim.UI*1e12:.3f} ps, Nyquist = {NYQ/1e9:.3f} GHz")

settings = load_tia_settings()
settings.sort(key=lambda s: -s['bw'])
print(f"settings: {len(settings)}; max BW = {settings[0]['bw']/1e9:.1f} GHz "
      f"({settings[0]['bw']/BAUD:.2f}x baud)")

# ---------------- noise scaling regression (white vs f^2) ----------------
A_ = np.array([[s['B1'], s['B2']] for s in settings])
b_ = np.array([s['inr'] ** 2 for s in settings])
sc = A_.max(axis=0)
x, _ = nnls(A_ / sc, b_)
I0g, I2g = x / sc
pred = A_ @ np.array([I0g, I2g])
r2 = 1 - np.sum((b_ - pred) ** 2) / np.sum((b_ - b_.mean()) ** 2)
c_w = (A_[:, 0] @ b_) / (A_[:, 0] @ A_[:, 0])
r2_w = 1 - np.sum((b_ - c_w * A_[:, 0]) ** 2) / np.sum((b_ - b_.mean()) ** 2)
c_f = (A_[:, 1] @ b_) / (A_[:, 1] @ A_[:, 1])
r2_f = 1 - np.sum((b_ - c_f * A_[:, 1]) ** 2) / np.sum((b_ - b_.mean()) ** 2)
print(f"noise regression: 2-param nnls R^2={r2:.3f} (white component -> 0); "
      f"single-param white-only R^2={r2_w:.3f}, f2-only R^2={r2_f:.3f} "
      f"-> family noise scales ~BW^1.5 (canvas: 0.590 vs 0.871)")

# ---------------- Tx corners ----------------
Htx = {}
for nm, fr in zip(('fast', 'typ', 'max'), ASSUMPTIONS['TX_TR_UI']):
    H, fp = sim.tx_two_pole_from_tr(fr * sim.UI)
    Htx[nm] = H
    print(f"Tx {nm} {fr:.2f} UI = {fr*sim.UI*1e12:.2f} ps: poles {fp/1e9:.1f} GHz each, "
          f"cascade f3dB {fp*np.sqrt(np.sqrt(2)-1)/1e9:.1f} GHz")

# ---------------- 152-setting rescan (motivation for the new TIA class) ----------------
s29 = next(s for s in settings if s['key'] == '12211111')
Ht29 = sim.tia_interp(s29)
b29 = sim.ctle_sweep(Htx['typ'] * Ht29, Ht29, np.arange(6e9, 30e9, 2e9), np.arange(40e9, 90e9, 5e9))
print(f"\nGEN1 design point at 106G, best CTLE-only ISI+EQ: {b29[0]:.2f} dB (canvas: 7.25)")
sbest = settings[0]
Htb = sim.tia_interp(sbest)
bb = sim.ctle_sweep(Htx['typ'] * Htb, Htb, np.arange(8e9, 36e9, 2e9), np.arange(45e9, 95e9, 5e9))
print(f"widest measured ({sbest['key']}, {sbest['bw']/1e9:.1f} GHz): CTLE-only {bb[0]:.2f} dB (canvas: 6.06)")

cnt = 0
n_eye_closed = 0
n_sim = 0
fz_r = np.arange(8e9, 36e9, 4e9)
fp_r = np.arange(45e9, 95e9, 10e9)
for s in settings:
    if s['bw'] < 0.25 * BAUD:
        continue
    n_sim += 1
    Ht = sim.tia_interp(s)
    bs = sim.ctle_sweep(Htx['typ'] * Ht, Ht, fz_r, fp_r)
    pj_i, _ = sim.jitter_pp(Htx['typ'] * Ht * sim.ctle(bs[1][0], bs[1][1], bs[1][1]),
                            ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_UI'])
    if pj_i is None:
        n_eye_closed += 1
        continue
    rs_i = rin_shot_penalty(s['inr'], 1.5 * s['bw'])   # BWn = 1.5x f3dB convention
    tot = rs_i + 0.205 + bs[0] + 0.04 + pj_i + 0.36 + 0.21
    if (-1.5 - IL_LINK) - (floor_dbm(s['inr']) + tot) >= 0:
        cnt += 1
print(f"152-setting rescan: {n_sim} simulated (bw >= 0.25x baud), {n_eye_closed} jitter-eye "
      f"closed, {cnt} qualify even at Tx OMA -1.5 dBm  (canvas: 0 of 152)")

# ---------------- scaled-design floors + required-class TIA ----------------
Hh = sim.butter2(ASSUMPTIONS['TIA_TARGET_F3DB'])
Hh2n = np.abs(Hh) ** 2 / np.abs(Hh[1]) ** 2
B1h = np.trapz(Hh2n, sim.freqs)
B2h = np.trapz(sim.freqs ** 2 * Hh2n, sim.freqs)
inr_white = s29['inr'] * np.sqrt(B1h / s29['B1'])
inr_f2 = s29['inr'] * np.sqrt(B2h / s29['B2'])
print(f"\nscaling the GEN1 design point to 58 GHz (BWn {B1h/1e9:.1f} GHz, x{B1h/s29['B1']:.2f}):")
print(f"  white-scaled (sqrt BW): {inr_white*1e6:.2f} uA -> floor {floor_dbm(inr_white):.2f} dBm (canvas: -10.60)")
print(f"  f2-scaled (BW^1.5):     {inr_f2*1e6:.1f} uA -> floor {floor_dbm(inr_f2):.2f} dBm (canvas: -5.63)")

IN_T = ASSUMPTIONS['TIA_TARGET_IN']
# Noise integration bandwidth for shot/RIN: 1.5x f3dB (NOT the Butterworth-2 shape
# integral B1h = 64 GHz, which understates a real part's noise tail - cf. the f^2
# scaling finding above and the >= 1.5x f3dB measurement requirement in the spec).
BN_T = 1.5 * ASSUMPTIONS['TIA_TARGET_F3DB']
print(f"target-class TIA: {IN_T*1e6:.1f} uA, BWn = 1.5 x 58 = {BN_T/1e9:.0f} GHz "
      f"-> floor {floor_dbm(IN_T):.2f} dBm (canvas: -11.41)")

# FIR3+CTLE vs CTLE-only on the target-class TIA (typ Tx, no bump - as originally run):
bh = sim.ctle_sweep(Htx['typ'] * Hh, Hh, np.arange(10e9, 40e9, 3e9), np.arange(50e9, 100e9, 6e9))
bhm = (1e9, None)
for fz in np.arange(12e9, 40e9, 4e9):
    for fp in np.arange(50e9, 100e9, 8e9):
        Hc = sim.ctle(fz, fp, fp)
        ne = sim.ctle_noise_enh(Hh, Hc)
        tw, pl = sim.opt_fir(1, 1, Htx['typ'] * Hh * Hc, step=0.04)
        if tw + 10 * np.log10(ne) < bhm[0]:
            bhm = (tw + 10 * np.log10(ne), (fz, fp, ne) + pl)
print(f"\ntarget-class TIA, typ Tx: CTLE-only {bh[0]:.2f} dB vs FIR3+CTLE {bhm[0]:.2f} dB "
      f"taps={np.round(bhm[1][3], 3)} (canvas: 0.93 vs 0.94 - FIR buys nothing here)")
# 4th FIR tap check on the best measured setting (worst tails):
Hcb = sim.ctle(bb[1][0], bb[1][1], bb[1][1])
t3, _ = sim.opt_fir(1, 1, Htx['typ'] * Htb * Hcb, step=0.04)
t4, _ = sim.opt_fir(1, 2, Htx['typ'] * Htb * Hcb, step=0.04)
print(f"4th-tap check (best measured + its CTLE): 3-tap {t3:.2f} vs 4-tap {t4:.2f} dB (canvas: 5.60 vs 5.60)")

# ---------------- ISI+EQ with the 25 fF microbump in chain ----------------
# Unterminated direct EIC-on-PIC drive: no physical 50 ohm. 50 is a placeholder
# effective node impedance (conservative if driver Rout / TIA Rin are lower).
Hmb = sim.one_pole(1 / (2 * np.pi * 50 * ASSUMPTIONS['MICROBUMP_C']))
print("\nmicrobump droop scan (placeholder 50-ohm effective node impedance):")
for C in (20e-15, 25e-15, 30e-15, 50e-15):
    fpole = 1 / (2 * np.pi * 50 * C)
    droop = -20 * np.log10(np.abs(1 / (1 + 1j * NYQ / fpole)))
    print(f"  C={C*1e15:.0f} fF: pole {fpole/1e9:.0f} GHz, droop at Nyquist {droop:.2f} dB")

isi = {}
ctle_pick = {}
for nm in ('fast', 'typ', 'max'):
    bx = sim.ctle_sweep(Htx[nm] * Hh * Hmb, Hh, np.arange(10e9, 40e9, 3e9), np.arange(50e9, 100e9, 6e9))
    isi[nm] = bx[0]
    ctle_pick[nm] = bx[1]
    print(f"ISI+EQ (25 fF bump, target TIA), Tx {nm}: {bx[0]:.2f} dB "
          f"(CTLE z={bx[1][0]/1e9:.0f}G p={bx[1][1]/1e9:.0f}G, ne={bx[1][3]:.2f})")
print("(canvas: 0.82 / 1.15 / 1.70)")

# ---------------- jitter, RIN, TDEC, MPI ----------------
Hop = Htx['typ'] * Hh * Hmb * sim.ctle(ctle_pick['typ'][0], ctle_pick['typ'][1], ctle_pick['typ'][1])
pj, TJ = sim.jitter_pp(Hop, ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_UI'])
print(f"\njitter: RJ {ASSUMPTIONS['RJ_UI']} UI = {ASSUMPTIONS['RJ_UI']*sim.UI*1e15:.0f} fs, "
      f"TJ = {TJ:.3f} UI = {TJ*sim.UI*1e12:.2f} ps -> PP {pj:.2f} dB (canvas: 0.95)")

# fallback CDR spec check (if the 0.015 UI / 141 fs analog-CDR RJ target is not met by
# the vendor and a looser 0.018 UI / 169 fs spec has to be accepted instead). Same Hop
# chain, DJ unchanged; the delta below is the actual booked cost of the fallback, not
# an estimate (os_r=32 default in Sim() rounds both cases to the same TJ/2 sample bin,
# so this is re-evaluated at os_r=256 for resolution -- see note in Methodology_Provenance).
sim_fine = Sim(BAUD, os_r=256, n=8192 * 8)
Hop_fine = (sim_fine.tx_two_pole_from_tr(0.45 * sim_fine.UI)[0] * sim_fine.butter2(58e9)
            * sim_fine.one_pole(1 / (2 * np.pi * 50 * ASSUMPTIONS['MICROBUMP_C']))
            * sim_fine.ctle(ctle_pick['typ'][0], ctle_pick['typ'][1], ctle_pick['typ'][1]))
pj_fb, TJ_fb = sim_fine.jitter_pp(Hop_fine, 0.018, ASSUMPTIONS['DJ_UI'])
pj_base_fine, _ = sim_fine.jitter_pp(Hop_fine, ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_UI'])
print(f"jitter fallback: RJ 0.018 UI = {0.018*sim.UI*1e15:.0f} fs, TJ = {TJ_fb:.3f} UI -> "
      f"PP {pj_fb:.2f} dB vs {pj_base_fine:.2f} dB at baseline (delta {pj_fb-pj_base_fine:+.2f} dB, "
      f"re-evaluated at os_r=256 to resolve the sample-grid quantization at os_r=32)")

rs = rin_shot_penalty(IN_T, BN_T)
print(f"RIN+shot Q-solve at BWn {BN_T/1e9:.0f} GHz: {rs:.3f} dB (canvas, at shape-integral 64 GHz: 0.82)")

Hbt4 = sim.bessel4(0.5 * BAUD)
for nm in ('fast', 'typ', 'max'):
    print(f"TDEC proxy Tx {nm} through BT4 {0.5*BAUD/1e9:.1f} GHz: "
          f"{sim.eval_chain(Htx[nm]*Hbt4)[0]:.2f} dB")
print("(canvas: 0.77 / 1.11 / 1.77 -> spec TDEC <= 1.8)")

MPI = mpi_penalty(ASSUMPTIONS['REFL_DB'], ASSUMPTIONS['REFL_DB'], -35, 4, ASSUMPTIONS['ER_DB'], 0.5)
print(f"MPI: {MPI:.3f} dB")

# CD check by pulse sim (0.04 dB is booked conservatively)
lam, c0 = 1310e-9, 3e8
DL = 1.7e-3
beta2L = -DL * lam ** 2 / (2 * np.pi * c0)
Hcd = np.exp(0.5j * beta2L * (2 * np.pi * sim.freqs) ** 2)
print(f"CD pulse-sim at +1.7 ps/nm: {sim.eval_chain(Hop*Hcd)[0] - sim.eval_chain(Hop)[0]:.3f} dB "
      f"(booked: {ASSUMPTIONS['CD_BOOKED']})")

# ---------------- stack & closure ----------------
print("\n--- GEN2 closure (target-class TIA, Tx OMA -3.5 dBm) ---")
for nm in ('fast', 'typ', 'max'):
    stack = rs + MPI + isi[nm] + ASSUMPTIONS['CD_BOOKED'] + pj + ASSUMPTIONS['XTALK'] + ASSUMPTIONS['THRESH']
    req = floor_dbm(IN_T) + stack
    m = ASSUMPTIONS['TX_OMA'] - IL_LINK - req
    print(f"Tx {nm}: stack {stack:.2f} dB, required OMA {req:.2f} dBm, margin {m:+.2f} dB")
print("(canvas: 3.41/+2.00, 3.74/+1.67, 4.29/+1.12)")

# ---------------- required-noise inversion ----------------
def required_in(tx_oma, margin, isi_line, jit_line):
    inr_ = 4e-6
    for _ in range(6):
        tot = (rin_shot_penalty(inr_, BN_T) + MPI + isi_line + ASSUMPTIONS['CD_BOOKED']
               + jit_line + ASSUMPTIONS['XTALK'] + ASSUMPTIONS['THRESH'])
        fl_req = tx_oma - IL_LINK - margin - tot
        inr_ = 10 ** (fl_req / 10) * 1e-3 * RESP / (2 * Q)
    return inr_

# as derived for the canvas section 2 (pre-bump ISI line 0.93, jitter on unbumped chain):
pj_nb, _ = sim.jitter_pp(Htx['typ'] * Hh * sim.ctle(bh[1][0], bh[1][1], bh[1][1]),
                         ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_UI'])
r_nb = required_in(-3.5, 2.0, bh[0], pj_nb)
r_wb = required_in(-3.5, 2.0, isi['typ'], pj)
print(f"\nrequired i_n for +2 dB margin at Tx OMA -3.5 dBm:")
print(f"  pre-microbump accounting (as on canvas sec 2): {r_nb*1e6:.2f} uA "
      f"({r_nb/np.sqrt(BN_T)*1e12:.1f} pA/rtHz avg over {BN_T/1e9:.0f} GHz)  (canvas: 4.37)")
print(f"  with 25 fF bump charged to ISI: {r_wb*1e6:.2f} uA  "
      f"(equivalently, 4.5 uA target gives +1.34 dB not +2.0)")

# package counterfactual at the new Nyquist
try:
    for p in ('TL_TX_64G', 'TL_RX_64G'):
        fpk, sdd = sdd21_from_s4p(PKG_DIR + p + '.s4p')
        print(f"package {p}: IL at 53.1 GHz = "
              f"{-20*np.log10(np.interp(NYQ, fpk, np.abs(sdd))):.2f} dB (CPO avoids)")
except Exception as e:
    print("s4p parse failed:", e)
