"""
06 - Device trade-off matrix at 106.25 GBd (OCI-GEN2-device-tradeoffs canvas).

Produces:
  - 24-cell scenario matrix: TIA {A@3uA/50G, A@4uA/50G, B@4uA/60G, B@5uA/60G} x
    Tx {FIR3 typ 0.45 UI, FIR3 slow 0.60 UI, no-FIR 60 GHz driver with MRM 40/50/60/80 GHz}
    (canvas cells e.g. B@4 no-FIR/MRM60 = +1.99 dB; worst combo B@5/MRM40 = +0.50 dB)
  - FIR value isolation on a matched 60+60 GHz channel (FIR converges to zero taps;
    net difference is the slice-DCD jitter charge: no-FIR better by ~0.27 dB)
  - TIA A-vs-B crossover: A wins below i_n ~ 3.6 uA

Inputs: none beyond common constants (TIA options are user-provided device data;
Butterworth-2 models assumed to MEET the section-7 phase/peaking spec).
"""
import numpy as np

from common import IL_LINK, Sim, floor_dbm, rin_shot_penalty

# ---------------- ASSUMPTIONS (judgment calls + user-provided device data) ----------------
ASSUMPTIONS = dict(
    # user-provided device brackets:
    TIA_OPTIONS={'A@3uA/50G': (50e9, 3e-6), 'A@4uA/50G': (50e9, 4e-6),
                 'B@4uA/60G': (60e9, 4e-6), 'B@5uA/60G': (60e9, 5e-6)},
    # TIA phase quality: modeled Butterworth-2 = MEETS spec sec-7 peaking/GD lines (assumed)
    TX_FIR_TR_UI=(0.45, 0.60),   # FIR3 cases: composite 2-pole corners
    DRV_F3DB=60e9,               # no-FIR case: single driver pole (user-provided)
    MRM_F3DB=(80e9, 60e9, 50e9, 40e9),  # MRM EO pole sensitivity (assumption - no 106G MRM data)
    RJ_UI=0.015,
    DJ_FIR=0.14,                 # incl. 0.05 UI slice-DCD allocation
    DJ_NOFIR=0.11,               # slice DCD credited back, 0.02 UI ordinary driver DCD kept
    MICROBUMP_C=25e-15,
    OTHERS=0.205 + 0.04 + 0.36 + 0.21,   # MPI + CD + xtalk + threshold (from script 04)
    TX_OMA=-3.5, ER_DB=4.5,
)

BAUD = 106.25e9
sim = Sim(BAUD)
Hmb = sim.one_pole(1 / (2 * np.pi * 50 * ASSUMPTIONS['MICROBUMP_C']))
FZ = np.arange(10e9, 40e9, 3e9)
FP = np.arange(45e9, 100e9, 6e9)

tias = {}
for k, (f0, inr) in ASSUMPTIONS['TIA_OPTIONS'].items():
    Hb = sim.butter2(f0)
    tias[k] = dict(H=Hb, inr=inr, BWn=np.trapz(np.abs(Hb) ** 2 / np.abs(Hb[1]) ** 2, sim.freqs),
                   floor=floor_dbm(inr))
    print(f"TIA {k}: BWn={tias[k]['BWn']/1e9:.1f} GHz, floor={tias[k]['floor']:.2f} dBm")

txs = {}
for fr in ASSUMPTIONS['TX_FIR_TR_UI']:
    H, _ = sim.tx_two_pole_from_tr(fr * sim.UI)
    txs[f'FIR3, {fr:.2f} UI driver'] = dict(H=H, fir=True, DJ=ASSUMPTIONS['DJ_FIR'])
for fm in ASSUMPTIONS['MRM_F3DB']:
    txs[f'no-FIR, drv 60G + MRM {fm/1e9:.0f}G'] = dict(
        H=sim.two_pole(ASSUMPTIONS['DRV_F3DB'], fm), fir=False, DJ=ASSUMPTIONS['DJ_NOFIR'])
for k, v in txs.items():
    print(f"Tx {k}: 20-80% = {sim.tr2080_of(v['H'])*1e12:.2f} ps ({sim.tr2080_of(v['H'])/sim.UI:.2f} UI)")


def isi_eq(Htx, Htia, fir):
    ch = Htx * Hmb * Htia
    b = sim.ctle_sweep(ch, Htia, FZ, FP)
    best, Hop = b[0], ch * sim.ctle(b[1][0], b[1][1], b[1][1])
    tag = "CTLE-only"
    if fir:
        bm = (1e9, None)
        for fz in np.arange(12e9, 40e9, 6e9):
            for fp in np.arange(48e9, 100e9, 10e9):
                Hc = sim.ctle(fz, fp, fp)
                ne = sim.ctle_noise_enh(Htia, Hc)
                tw, pl = sim.opt_fir(1, 1, ch * Hc, step=0.04)
                if tw + 10 * np.log10(ne) < bm[0]:
                    bm = (tw + 10 * np.log10(ne), (fz, fp, ne) + pl)
        if bm[0] < best:
            best = bm[0]
            w = bm[1][3]
            tag = f"FIR3 taps={np.round(w, 3)}"
            Hop = sim.fir_apply(ch, w) * sim.ctle(bm[1][0], bm[1][1], bm[1][1])
    return best, tag, Hop


print("\n=== scenario matrix (margins at Tx OMA -3.5 dBm, 1e-12) ===")
for tk, tv in txs.items():
    for kk_, kv in tias.items():
        isi, tag, Hop = isi_eq(tv['H'], kv['H'], tv['fir'])
        pj, _ = sim.jitter_pp(Hop, ASSUMPTIONS['RJ_UI'], tv['DJ'])
        rs = rin_shot_penalty(kv['inr'], kv['BWn'])
        tot = rs + isi + pj + ASSUMPTIONS['OTHERS']
        m = (ASSUMPTIONS['TX_OMA'] - IL_LINK) - (kv['floor'] + tot)
        print(f"{tk:28s} x {kk_}: isi={isi:.2f} jit={pj:.2f} stack={tot:.2f} margin={m:+.2f} | {tag}")

# ---------------- FIR value isolation (matched 60+60 channel, B@4) ----------------
print("\n--- FIR value isolation (matched 60+60 GHz channel, TIA B@4) ---")
kv = tias['B@4uA/60G']
ch = sim.two_pole(60e9, 60e9)
i0, t0, H0op = isi_eq(ch, kv['H'], False)
i1, t1, H1op = isi_eq(ch, kv['H'], True)
pj0, _ = sim.jitter_pp(H0op, ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_NOFIR'])
pj1, _ = sim.jitter_pp(H1op, ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_FIR'])
print(f"no-FIR: ISI+EQ={i0:.2f} + jitter(DJ {ASSUMPTIONS['DJ_NOFIR']})={pj0:.2f} -> {i0+pj0:.2f} dB")
print(f"FIR3:   ISI+EQ={i1:.2f} + jitter(DJ {ASSUMPTIONS['DJ_FIR']})={pj1:.2f} -> {i1+pj1:.2f} dB | {t1}")
print(f"-> no-FIR strictly better by {i1+pj1-i0-pj0:.2f} dB (canvas: 0.27; ISI identical, DCD charge only)")
kk2, t2, ci2 = sim.taps_of(sim.pulse(ch * Hmb * kv['H']))
tt2 = t2 / t2[ci2]
print(f"channel taps h-1/h+1: {tt2[ci2-1]:.3f} / {tt2[ci2+1]:.3f} (mild post-cursor, CTLE territory)")

# ---------------- A-vs-B crossover ----------------
# margin_A(i_n) = margin_A(3uA) - [floor(i_n)-floor(3uA)] - d(rin); solve = margin_B(4uA)
mB = None
mA3 = None
tvt = txs['FIR3, 0.45 UI driver']
for kk_, kv_ in (('A@3uA/50G', tias['A@3uA/50G']), ('B@4uA/60G', tias['B@4uA/60G'])):
    isi, tag, Hop = isi_eq(tvt['H'], kv_['H'], True)
    pj, _ = sim.jitter_pp(Hop, ASSUMPTIONS['RJ_UI'], tvt['DJ'])
    tot = rin_shot_penalty(kv_['inr'], kv_['BWn']) + isi + pj + ASSUMPTIONS['OTHERS']
    m = (ASSUMPTIONS['TX_OMA'] - IL_LINK) - (kv_['floor'] + tot)
    if kk_.startswith('A'):
        mA3 = m
    else:
        mB = m
x = 3e-6 * 10 ** ((mA3 - mB) / 10)   # floor is 10*log10(i_n)-linear; rin drift is second order
print(f"\nA-vs-B crossover: A margin matches B@4uA at i_n ~ {x*1e6:.2f} uA (canvas: ~3.6)")
