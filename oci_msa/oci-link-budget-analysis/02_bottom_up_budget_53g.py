"""
02 - GEN1 bottom-up OMA-domain link budget at 53.125 GBd NRZ, BER 1e-12 (Q = 7.035).

Produces (OCI-link-budget-bottom-up canvas): penalty stack total, required OMA at Rx,
closure margins vs spec Tx cases, assumption sensitivity table.
NOTE: the canvas numbers (stack 2.87 dB, +0.66 dB spec-min margin) were computed with the
spec's -19 dB end reflectances AND the signal-TF Personick noise bandwidth (28.2 GHz).
The budget now books -24 dB ends (shared GEN1/GEN2 product line) and BWn = 1.5x f3dB
(44 GHz) for the shot/RIN/dark terms. Set MPI_REFL_DB=-19 and BWn = sel['BWn_se'] to
reproduce the canvas.

Methodology: Sackinger/Palermo lecture 4 (Personick sensitivity, power penalties), lecture 7
(ER/CD), lecture 10 (dual-Dirac jitter), Bhatt/King 802.3bs MPI upper bound.

NOTE ON MACHINERY: this script intentionally keeps the ORIGINAL GEN1 pulse-response
implementation (N=4096 start-of-array pulse, simple LF flatten with zero excess phase,
+/-16 UI ISI span, argmax sampling) so it reproduces the canvas numbers exactly. The improved
machinery (centered pulse, causal LF flatten, phase-optimized sampling) lives in common.Sim
and is used from script 03 onward.
"""
import numpy as np
import pandas as pd
from scipy import signal as sig
from math import erfc

from common import Q, QE, TIA_DIR, dbm, load_tia_settings, floor_dbm

# ---------------- ASSUMPTIONS (judgment calls, not computed) ----------------
ASSUMPTIONS = dict(
    ER_DB=3.5,            # spec minimum extinction ratio
    RIN_DB=-138.0,        # Tx RIN_OMA spec at 21.4 dB ORL
    RJ_UI=0.010,          # rms random jitter, DSP-SerDes class assumption
    DJ_UI=0.10,           # deterministic jitter p-p
    XTALK_ISO_DB=20.0,    # MRR demux adjacent-channel isolation assumption
    XTALK_DOMA_DB=3.0,    # aggressor OMA advantage (spec dOMA)
    THRESH_OFFSET=0.025,  # decision threshold offset, fraction of swing
    DARK_UA=1.0,          # worst-case dark current
    MPI_D=0.5,            # Bhatt/King discount factor
    MPI_REFL_DB=-24.0,    # end reflectances: GEN1/GEN2 share the product line, so the
                          # GEN2-derived <= -24 dB requirement applies to both generations
                          # (OCI spec only requires -19 dB, which would book 0.51 dB MPI)
    MPI_CONN_DB=-35.0, MPI_NCONN=4,
    IL=2.5,               # link insertion loss dB
)

BAUD = 53.125e9
UI = 1.0 / BAUD

# ---------------- design point from the survey ----------------
settings = load_tia_settings()
# GEN1 convention: selection and noise bandwidth on the single-ended p-leg response
ok = sorted([s for s in settings if s['bw_se'] >= 0.55 * BAUD], key=lambda s: s['inr'])
sel, med, worst = ok[0], ok[len(ok) // 2], ok[-1]
R = sel['Rpd']
in_amp = sel['inr']
# Noise integration bandwidth for the signal-dependent terms (shot/RIN/dark):
# 1.5x the circuit's 3 dB bandwidth (single-pole NEB factor pi/2, rounded), NOT the
# signal-TF Personick integral (28.2 GHz here) - real receiver noise extends beyond
# f3dB (cf. the f^2 scaling finding in script 04), so the shape integral understates it.
BWn = 1.5 * sel['bw_se']
d0 = pd.read_csv(TIA_DIR + f"TT_Tia_TF_{sel['key']}.csv")

OMA_sens_amp = 2 * Q * in_amp / R
print(f"design point {sel['key']}: i_n={in_amp*1e6:.2f} uA, R={R:.3f} A/W, BWn={BWn/1e9:.1f} GHz")
print(f"analytic floor = {dbm(OMA_sens_amp):.2f} dBm OMA   (canvas: -12.93)")

ER_DB = ASSUMPTIONS['ER_DB']
r = 10 ** (ER_DB / 10)


def solve_oma(er_lin, rin_lin=0.0, include_shot=True):
    oma = OMA_sens_amp
    for _ in range(200):
        P1 = oma * er_lin / (er_lin - 1)
        P0 = oma / (er_lin - 1)
        s1 = np.sqrt(in_amp ** 2 + (2 * QE * R * P1 * BWn if include_shot else 0)
                     + (R * P1) ** 2 * rin_lin * BWn)
        s0 = np.sqrt(in_amp ** 2 + (2 * QE * R * P0 * BWn if include_shot else 0)
                     + (R * P0) ** 2 * rin_lin * BWn)
        oma_new = Q * (s0 + s1) / R
        if abs(oma_new / oma - 1) < 1e-12:
            break
        oma = oma_new
    return oma


pen = {}
OMA_shot = solve_oma(r)
pen['ER / signal-dependent shot noise'] = dbm(OMA_shot) - dbm(OMA_sens_amp)

rin = 10 ** (ASSUMPTIONS['RIN_DB'] / 10)
OMA_rin = solve_oma(r, rin_lin=rin)
pen['RIN (-138 dB/Hz, Q^2-scaled)'] = dbm(OMA_rin) - dbm(OMA_shot)
Qmax_rin = 1.0 / (np.sqrt(rin * BWn) * (r / (r - 1) + 1 / (r - 1)))
print(f"RIN-limited Qmax = {Qmax_rin:.2f} (BER floor {0.5*erfc(Qmax_rin/np.sqrt(2)):.1e}) - no floor issue" if Qmax_rin > Q else "RIN FLOOR VIOLATION")

Rt = Rr = 10 ** (ASSUMPTIONS['MPI_REFL_DB'] / 10)
Rc = 10 ** (ASSUMPTIONS['MPI_CONN_DB'] / 10)
nc = ASSUMPTIONS['MPI_NCONN']
S = np.sqrt(Rt * Rr) + nc * np.sqrt(Rt * Rc) + nc * np.sqrt(Rr * Rc) + nc * (nc - 1) / 2 * Rc
x_mpi = ASSUMPTIONS['MPI_D'] * 4 * S * r / (r - 1)
pen[f"MPI (Bhatt UB, D=0.5, {ASSUMPTIONS['MPI_REFL_DB']:.0f} dB ends)"] = 10 * np.log10(1 / (1 - x_mpi))

# ---------------- ISI / CD / jitter via legacy pulse machinery ----------------
fgrid = d0['ipreal X'].values
Hd = (d0['ipreal Y'].values + 1j * d0['ipimag Y'].values) \
     - (d0['inreal Y'].values + 1j * d0['inimag Y'].values)
i2g = np.searchsorted(fgrid, 2e9)
Hd = Hd.copy()
Hd[:i2g] = Hd[i2g]                       # legacy DC-restoration flatten
Hd_norm = Hd / np.abs(Hd).max()

os_r, N = 32, 4096
fs = BAUD * os_r
freqs = np.fft.rfftfreq(N, 1 / fs)
Hi = np.interp(freqs, fgrid, Hd_norm.real) + 1j * np.interp(freqs, fgrid, Hd_norm.imag)
b, a = sig.bessel(4, 2 * np.pi * 26.5625e9, btype='low', analog=True, norm='mag')
_, Htx = sig.freqs(b, a, worN=2 * np.pi * freqs)


def pulse_metrics(disp_ps_nm=0.0):
    lam, c = 1315e-9, 3e8
    Hcd = np.exp(1j * np.pi * (disp_ps_nm * 1e-12 / 1e-9) * lam ** 2 / c * freqs ** 2)
    H = Hi * Hcd * Htx
    x = np.zeros(N)
    x[:os_r] = 1.0
    y = np.fft.irfft(np.fft.rfft(x) * H, n=N)
    kmax = np.argmax(y)
    cur = y[kmax]
    span = 16
    pre = sum(abs(y[kmax + i * os_r]) for i in range(-span, 0) if kmax + i * os_r >= 0)
    post = sum(abs(y[kmax + i * os_r]) for i in range(1, span + 1) if kmax + i * os_r < N)
    return cur, pre, post, y, kmax


cur, pre, post, y, kmax = pulse_metrics(0.0)
pp_isi_raw = -10 * np.log10(max(1e-9, cur - pre - post) / cur)
pp_isi_dfe = -10 * np.log10(max(1e-9, cur - pre) / cur)
print(f"ISI: cursor={cur:.3f} pre={pre:.4f} post={post:.4f}; raw={pp_isi_raw:.2f} dB, post-DFE={pp_isi_dfe:.2f} dB")
pen['ISI residual (BT4 Tx + TIA, DFE removes post-cursors)'] = pp_isi_dfe

cur2, pre2, post2, _, _ = pulse_metrics(1.7)
pp_cd = (-10 * np.log10((cur2 - pre2 - post2) / cur2)) - pp_isi_raw
cur3, pre3, post3, _, _ = pulse_metrics(-0.9)
pp_cd_neg = (-10 * np.log10((cur3 - pre3 - post3) / cur3)) - pp_isi_raw
pen['Chromatic dispersion (worst of +/-)'] = max(pp_cd, pp_cd_neg, 0.0)

RJ, DJ = ASSUMPTIONS['RJ_UI'], ASSUMPTIONS['DJ_UI']
TJ = DJ + 2 * Q * RJ
off = int(round(TJ / 2 * os_r))


def eye_open(koff):
    kk = kmax + koff
    span = 16
    pre_ = sum(abs(y[kk + i * os_r]) for i in range(-span, 0) if kk + i * os_r >= 0)
    return y[kk] - pre_


pp_jit = -10 * np.log10(min(eye_open(-off), eye_open(off)) / eye_open(0))
pen[f'Jitter (RJ={RJ} UI rms, DJ={DJ} UI -> TJ={TJ:.2f} UI)'] = pp_jit

eps_x = 2 * 10 ** (-ASSUMPTIONS['XTALK_ISO_DB'] / 10) * 10 ** (ASSUMPTIONS['XTALK_DOMA_DB'] / 10)
pen['Inter-channel crosstalk (20 dB iso, +3 dB dOMA)'] = -10 * np.log10(1 - 2 * eps_x)
pen['Decision threshold offset (2.5%)'] = 10 * np.log10(1 + 2 * ASSUMPTIONS['THRESH_OFFSET'])
pen['Dark current (1 uA)'] = 10 * np.log10(np.sqrt(1 + 2 * QE * ASSUMPTIONS['DARK_UA'] * 1e-6 * BWn / in_amp ** 2))

print("\n--- GEN1 PENALTY STACK (dB) ---")
tot = sum(pen.values())
for k, v in pen.items():
    print(f"{v:6.3f}  {k}")
print(f"{tot:6.3f}  TOTAL   (canvas, at -19 dB ends: 2.87)")

req_at_rx = dbm(OMA_sens_amp) + tot
print(f"\nrequired OMA at Rx = {req_at_rx:.2f} dBm")
IL = ASSUMPTIONS['IL']
for name, txoma, tdec in [("Spec-min Tx (TDEC=1.4 dB)", -5.5, 1.4),
                          ("Spec-min Tx (TDEC=3.4 dB)", -3.5, 3.4),
                          ("Realistic LM Tx", -3.2, 2.0)]:
    margin = (txoma - IL - tdec) - req_at_rx
    print(f"{name}: margin {margin:+.2f} dB")
print("(canvas, at -19 dB ends: spec-min TDEC=1.4 case -> +0.66 dB)")

# ---------------- assumption sensitivity ----------------
print("\n--- assumption sensitivity (vs spec-min TDEC=1.4 base) ---")
base_margin = (-5.5 - IL - 1.4) - req_at_rx
for nm, s in [('median TIA setting', med), ('worst TIA setting', worst)]:
    d_ = floor_dbm(s['inr'], resp=s['Rpd']) - dbm(OMA_sens_amp)
    print(f"{nm}: i_n={s['inr']*1e6:.2f} uA -> margin {base_margin - d_:+.2f} dB")
for Rx_ in (0.8, 1.0):
    d_ = dbm(2 * Q * in_amp / Rx_) - dbm(OMA_sens_amp)
    print(f"R={Rx_} A/W: margin {base_margin - d_:+.2f} dB")
