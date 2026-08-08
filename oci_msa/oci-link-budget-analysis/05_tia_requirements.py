"""
05 - GEN2 TIA requirements derivations (spec canvas section 7) + verification recipe.

Produces:
  - bandwidth window: total sensitivity flat at ~-8.3/-8.4 dBm across f3dB 45-64 GHz
    (canvas -8.66 plateau predates the BWn = 1.5x f3dB convention)
  - noise-shape finding: f2-shaped input noise sees <= 0 dB extra post-CTLE penalty vs
    equal-rms white (the mild CTLE's poles sit where f2 noise lives) -> spec enforces shape
    via full-band rms + spot-density ceiling instead of a post-CTLE allowance
  - peaking sweep (2nd-order, f3dB held at 58 GHz): peaking <= ~1 dB keeps ISI+EQ within
    +0.11 dB of the 1.15 dB budget line
  - group-delay diagnosis: widest measured setting has 12.5 ps GD ripple (2-40 GHz) with
    flat magnitude -> h-1 ~ 0.48 pre-cursor; motivates the <= 3 ps GD-ripple spec line
  - ZT floor (57 dBohm), overload currents (162-696 uApp, 731 uA DC), LF cutoff (1.34 MHz
    for 0.05 dB BLW at 72-bit CID)
  - verify_tia(): the 6-step pass/fail recipe on the standard TF+noise data format

Inputs: TIA tables (common.TIA_DIR).
"""
import numpy as np

from common import (Q, RESP, IL_LINK, Sim, floor_dbm, load_tia_settings, mpi_penalty,
                    rin_shot_penalty)

# ---------------- ASSUMPTIONS (judgment calls, not computed) ----------------
ASSUMPTIONS = dict(
    PD_CAP_FF=(30, 40),        # 100G-class waveguide PD capacitance - NO PD data in repos
    SLICER_MV=(10, 15),        # min slicer eye, lecture-4 real-slicer discussion
    DOWNSTREAM_NOISE_MV=1.0,   # CTLE+slicer input-referred noise for the 3x dominance rule
    CID_BITS=72,               # consecutive-identical-digit run for baseline wander
    BLW_PENALTY_DB=0.05,
    RJ_UI=0.015, DJ_UI=0.14,
    TIA_TARGET_F3DB=58e9, TIA_TARGET_IN=4.5e-6,
    MICROBUMP_C=25e-15,
    RX_OMA_MAX_DBM=-1.0,           # judgment call, not derived from a Tx-OMA/link-IL
                                   # corner; reviewed vs. an alternative +1.79 dBm /
                                   # 1.13 mApp case and retained -- see
                                   # Methodology_Provenance.md ("Rx OMA max / overload
                                   # governing case")
    ER_DB=4.5,
    REQ_OMA_FLOOR_DBM=-7.34,   # GEN2 required OMA at Rx (script 04, typ Tx, BWn=1.5x f3dB)
)

BAUD = 106.25e9
sim = Sim(BAUD)
settings = load_tia_settings()
settings.sort(key=lambda s: -s['bw'])
s12 = next(s for s in settings if s['key'] == '12211111')

Hh = sim.butter2(ASSUMPTIONS['TIA_TARGET_F3DB'])
# 50 = placeholder effective node impedance (unterminated direct drive, no physical 50 ohm)
Hmb = sim.one_pole(1 / (2 * np.pi * 50 * ASSUMPTIONS['MICROBUMP_C']))
Htx_typ, _ = sim.tx_two_pole_from_tr(0.45 * sim.UI)
Htx_max, _ = sim.tx_two_pole_from_tr(0.60 * sim.UI)

b2t = sim.ctle_sweep(Htx_typ * Hh * Hmb, Hh, np.arange(10e9, 40e9, 3e9), np.arange(50e9, 100e9, 6e9))
fz0, fp0 = b2t[1][0], b2t[1][1]
Hc0 = sim.ctle(fz0, fp0, fp0)
print(f"reference chain CTLE: z={fz0/1e9:.0f}G p={fp0/1e9:.0f}G, ISI+EQ = {b2t[0]:.2f} dB (canvas: 1.15)")

# ---------------- noise spectral shape vs CTLE ----------------
print("\n--- noise shape: extra post-CTLE penalty vs equal-rms white ---")
Ht2 = np.abs(Hh) ** 2
Hc2 = np.abs(Hh * Hc0) ** 2
ne_white = np.sqrt(np.trapz(Hc2, sim.freqs) / np.trapz(Ht2, sim.freqs))
for fc in (15e9, 25e9, 40e9, 1e15):
    D2 = 1 + (sim.freqs / fc) ** 2
    ne = np.sqrt(np.trapz(D2 * Hc2, sim.freqs) / np.trapz(D2 * Ht2, sim.freqs))
    print(f"  f2 corner {fc/1e9:7.0f} GHz: extra {10*np.log10(ne/ne_white):+.3f} dB")
print("  -> f2 shape is NOT punished by the mild CTLE; binding constraints are full-band rms + spot ceiling")

# ---------------- peaking / group-delay tolerance (variable-Q 2nd order at 58 GHz) ----------------
print("\n--- peaking sweep (f3dB held at 58 GHz) ---")
def h2q(Qf, f3db):
    xs = np.linspace(0.01, 5, 200000)
    m2 = 1.0 / ((1 - xs ** 2) ** 2 + xs ** 2 / Qf ** 2)
    x3 = xs[np.where(m2 >= 0.5)[0][-1]]
    w0 = 2 * np.pi * f3db / x3
    s = 1j * 2 * np.pi * sim.freqs
    return 1.0 / (1 + s / (Qf * w0) + (s / w0) ** 2)

for Qf in (0.71, 0.85, 1.0, 1.2, 1.5, 2.0):
    H2 = h2q(Qf, 58e9)
    pk = 20 * np.log10(np.abs(H2).max() / np.abs(H2[1]))
    i40 = np.searchsorted(sim.freqs, 40e9)
    ph = np.unwrap(np.angle(H2[1:i40]))
    gd = -np.gradient(ph, sim.freqs[1:i40]) / (2 * np.pi)
    kk, t, ci = sim.taps_of(sim.pulse(Htx_typ * Hmb * H2))
    tt = t / t[ci]
    b_ = sim.ctle_sweep(Htx_typ * Hmb * H2, H2, np.arange(10e9, 40e9, 4e9), np.arange(50e9, 100e9, 8e9))
    print(f"  Q={Qf:.2f}: peaking {pk:5.2f} dB, GD ripple {(gd.max()-gd.min())*1e12:5.2f} ps, "
          f"h-1={tt[ci-1]:+.3f}, CTLE-net {b_[0]:.2f} dB")
print("  -> spec: peaking <= 1.0 dB, GD ripple <= 3 ps (2-40 GHz)")

# ---------------- GD-ripple diagnosis of the widest measured setting ----------------
sbest = settings[0]
ff = sbest['f']
i2 = np.searchsorted(ff, 2e9)
i40 = np.searchsorted(ff, 40e9)
ph = np.unwrap(np.angle(sbest['H'][i2:i40]))
gd = -np.gradient(ph, ff[i2:i40]) / (2 * np.pi)
kk, t, ci = sim.taps_of(sim.pulse(Htx_typ * sim.tia_interp(sbest, flatten=False)))
tt = t / t[ci]
print(f"\nmeasured {sbest['key']}: magnitude peaking {sbest['peak_db']:.1f} dB but GD ripple "
      f"{(gd.max()-gd.min())*1e12:.2f} ps (2-40 GHz) -> raw h-1 = {tt[ci-1]:.3f} "
      f"(canvas: 12.5 ps, 0.48). GEN1 design point:", end=" ")
ph2 = np.unwrap(np.angle(s12['H'][i2:i40]))
gd2 = -np.gradient(ph2, ff[i2:i40]) / (2 * np.pi)
print(f"{(gd2.max()-gd2.min())*1e12:.2f} ps ripple (fine at 53 GBd, not at 106)")

# ---------------- bandwidth window ----------------
print("\n--- BW window: floor(white-scaled) + ISI+EQ + RIN vs f3dB ---")
for f0 in (45e9, 50e9, 53e9, 58e9, 64e9, 70e9):
    Hb = sim.butter2(f0)
    B1h = np.trapz(np.abs(Hb) ** 2 / np.abs(Hb[1]) ** 2, sim.freqs)
    inr_w = s12['inr'] * np.sqrt(B1h / s12['B1'])
    b_ = sim.ctle_sweep(Htx_typ * Hb * Hmb, Hb, np.arange(10e9, 40e9, 4e9), np.arange(45e9, 100e9, 8e9))
    tot = floor_dbm(inr_w) + b_[0] + rin_shot_penalty(inr_w, 1.5 * f0)   # BWn = 1.5x f3dB
    print(f"  f3dB {f0/1e9:.0f} GHz: {tot:.2f} dBm")
print("  -> flat 50-64 GHz (canvas: -8.66 plateau); window spec, not a point spec")

# ---------------- ZT / overload / LF cutoff ----------------
print("\n--- gain, overload, LF cutoff ---")
E = 10 ** (ASSUMPTIONS['ER_DB'] / 10)
for nm, oma_dbm in (("required-OMA floor", ASSUMPTIONS['REQ_OMA_FLOOR_DBM']),
                    ("Rx OMA max", ASSUMPTIONS['RX_OMA_MAX_DBM'])):
    oma = 10 ** (oma_dbm / 10) * 1e-3
    pavg = oma * (E + 1) / (2 * (E - 1))
    print(f"  {nm} {oma_dbm:.2f} dBm: Ipp={oma*RESP*1e6:.0f} uApp, Idc={pavg*RESP*1e6:.0f} uA")
eye_ua = 2 * Q * ASSUMPTIONS['TIA_TARGET_IN']
print(f"  eye current at sensitivity: {eye_ua*1e6:.1f} uApp")
for mv in ASSUMPTIONS['SLICER_MV']:
    print(f"  slicer {mv} mVppd -> ZT >= {20*np.log10(mv*1e-3/eye_ua):.1f} dBohm")
zt_dom = 3 * ASSUMPTIONS['DOWNSTREAM_NOISE_MV'] * 1e-3 / ASSUMPTIONS['TIA_TARGET_IN']
print(f"  3x downstream-noise dominance ({ASSUMPTIONS['DOWNSTREAM_NOISE_MV']} mV rms) -> "
      f"ZT >= {20*np.log10(zt_dom):.1f} dBohm  (binding line -> spec 57 dBohm)")
h0s = sorted(20 * np.log10(s['H0']) for s in settings)
print(f"  measured family diff ZT range: {h0s[0]:.1f} .. {h0s[-1]:.1f} dBohm")
e_ = 1 - 10 ** (-ASSUMPTIONS['BLW_PENALTY_DB'] / 10)
fL = (e_ / 2) / (2 * np.pi * ASSUMPTIONS['CID_BITS'] * sim.UI)
print(f"  LF cutoff for {ASSUMPTIONS['BLW_PENALTY_DB']} dB BLW at {ASSUMPTIONS['CID_BITS']}-bit CID: "
      f"<= {fL/1e6:.2f} MHz (canvas: 1.34 -> spec <= 1 MHz)")


# ---------------- the 6-step verification recipe as a reusable function ----------------
def verify_tia(setting, sim106=sim, tx_tr_ui=0.45, verbose=True):
    """Run the spec-canvas section-7 pass/fail recipe on a measured setting
    (dict from common.load_tia_settings; i.e. differential TF + output-noise rms).
    A measured noise SPECTRUM (for the density mask) is not in this data format, so
    step 1 checks total rms only. Returns dict of step results."""
    res = {}
    # 1. input-referred noise (ceiling from script 04 inversion at BWn = 1.5x f3dB)
    res['in_uA'] = setting['inr'] * 1e6
    res['pass_noise'] = setting['inr'] <= 4.0e-6
    # 2. response quality
    ff = setting['f']
    i2 = np.searchsorted(ff, 2e9)
    i40 = np.searchsorted(ff, 40e9)
    ph_ = np.unwrap(np.angle(setting['H'][i2:i40]))
    gd_ = -np.gradient(ph_, ff[i2:i40]) / (2 * np.pi)
    res['f3dB_GHz'] = setting['bw'] / 1e9
    res['peaking_dB'] = setting['peak_db']
    res['gd_ripple_ps'] = (gd_.max() - gd_.min()) * 1e12
    res['pass_response'] = (50e9 <= setting['bw'] <= 64e9 and setting['peak_db'] <= 1.0
                            and res['gd_ripple_ps'] <= 3.0)
    # 3. analytic floor
    res['floor_dBm'] = floor_dbm(setting['inr'])
    res['pass_floor'] = res['floor_dBm'] <= -11.9
    # 4. ISI+EQ
    Htx_, _ = sim106.tx_two_pole_from_tr(tx_tr_ui * sim106.UI)
    Ht = sim106.tia_interp(setting)
    bx = sim106.ctle_sweep(Htx_ * Hmb * Ht, Ht, np.arange(10e9, 40e9, 3e9), np.arange(45e9, 95e9, 6e9))
    res['isi_eq_dB'] = bx[0]
    res['pass_isi'] = bx[0] <= 1.15
    # 5. jitter
    pj_, TJ_ = sim106.jitter_pp(Htx_ * Hmb * Ht * sim106.ctle(bx[1][0], bx[1][1], bx[1][1]),
                                ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_UI'])
    res['jitter_dB'] = pj_
    res['pass_jitter'] = pj_ is not None and pj_ <= 1.0
    # 6. end-to-end margin
    if pj_ is not None:
        stack = (rin_shot_penalty(setting['inr'], 1.5 * setting['bw'])   # BWn = 1.5x f3dB
                 + mpi_penalty(-24, -24, -35, 4, 4.5, 0.5)
                 + bx[0] + 0.04 + pj_ + 0.36 + 0.21)
        res['margin_dB'] = (-3.5 - IL_LINK) - (res['floor_dBm'] + stack)
        res['pass_margin'] = res['margin_dB'] >= 1.5
    else:
        res['margin_dB'] = None
        res['pass_margin'] = False
    res['PASS'] = all(res[k] for k in res if k.startswith('pass_'))
    if verbose:
        print(f"  verify_tia({setting['key']}): " + ", ".join(
            f"{k}={v if not isinstance(v, float) else round(v, 2)}" for k, v in res.items()))
    return res


print("\n--- verification recipe demo (GEN1 design point through the GEN2 recipe) ---")
verify_tia(s12)
