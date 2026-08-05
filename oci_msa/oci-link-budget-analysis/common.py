"""
Shared machinery for the OCI link-budget analyses (GEN1 53.125 GBd / GEN2 106.25 GBd NRZ).

Contents:
  - TIA table loading (Ocelot ADFET TT corner: differential TF CSVs + output-noise CSV),
    input-referral conventions, Personick-style noise-bandwidth integrals.
  - Sim: rate-dependent frequency grid plus pulse-response construction, peak-distortion ISI,
    FIR/CTLE joint optimization (peak-swing constraint, de-emphasis + noise-enhancement costs),
    dual-Dirac jitter penalty, Tx pole models.
  - Q-solve for required OMA with RIN/shot (signal-dependent noise), MPI (Bhatt/King
    discounted upper bound), unit helpers.

Conventions (established in the GEN1 bottom-up budget and kept everywhere for comparability):
  - Input-referred TIA noise i_n = (output noise rms from the noise CSV) / (peak single-ended
    p-leg transimpedance). This is the conservative reading of the model, which injects the
    noise target on the p-leg only while the signal sees the full differential gain.
  - Analytic sensitivity floor: OMA = 2 * Q * i_n / R  (Personick, lecture 4).
  - ISI as peak distortion: PP = -10*log10((cursor - sum|pre| - sum|post|) / cursor), optical dB.
  - CTLE noise-enhancement cost: 10*log10( rms gain of the CTLE over the TIA-shaped white
    input noise ), charged to the scenario. Tx FIR de-emphasis cost: -10*log10(sum(w)) under
    the sum|w| = 1 peak-swing constraint (slice-DAC, linear EO).
"""
import os
from itertools import product

import numpy as np
import pandas as pd
from scipy import signal as sig

# ----------------------------------------------------------------------------- constants
Q = 7.035                    # Personick Q for BER 1e-12
RESP = 0.876                 # PD responsivity A/W (from the TIA model's pd column)
QE = 1.602e-19
IL_LINK = 2.5                # dB, 500 m link insertion loss (OCI v1.0)

TIA_DIR = ('/home/patrick/sludds/LM-link-vpiphotonics/Mesa/Components/TIA/'
           'Ocelot_TIA_ADFET.vtmg_pack/Inputs/TT_TIA_DATA_ED_ADFET_20250520/')
PKG_DIR = '/home/patrick/sludds/Caribou_EOE/Package/'


def dbm(w):
    return 10 * np.log10(w / 1e-3)


def floor_dbm(inr, resp=RESP, q=Q):
    """Analytic amp-noise sensitivity floor, dBm OMA."""
    return dbm(2 * q * inr / resp)


# ----------------------------------------------------------------------------- TIA tables
def load_tia_settings(base=TIA_DIR):
    """Load all TIA settings: differential TF, single-ended peak gain, 3 dB BW, noise
    integrals (with the model's 60 GHz filtfilt noise-path LPF), input-referred noise."""
    noise_df = pd.read_csv(base + 'TT_Tia_Noise.csv', header=None, names=['k', 'v'])
    noise = dict(zip(noise_df['k'].astype(str).str.zfill(8), noise_df['v']))
    settings = []
    for key, vn in noise.items():
        tf = base + f'TT_Tia_TF_{key}.csv'
        if not os.path.exists(tf):
            continue
        d = pd.read_csv(tf)
        ff = d['ipreal X'].values
        Hp = d['ipreal Y'].values + 1j * d['ipimag Y'].values
        Hc = Hp - (d['inreal Y'].values + 1j * d['inimag Y'].values)   # differential
        Rpd = np.abs(d['pdreal Y'].values + 1j * d['pdimag Y'].values)[0]
        Hm = np.abs(Hc)
        H0 = Hm.max()
        ipk = Hm.argmax()
        ab = np.where(Hm[ipk:] < H0 / np.sqrt(2))[0]
        bw = ff[ipk + ab[0]] if len(ab) else ff[-1]
        # GEN1 (bottom-up 53G budget) worked entirely on the single-ended p-leg response:
        Hpm = np.abs(Hp)
        H0se = Hpm.max()                              # single-ended p-leg peak (GEN1 convention)
        ipk_se = Hpm.argmax()
        ab_se = np.where(Hpm[ipk_se:] < H0se / np.sqrt(2))[0]
        bw_se = ff[ipk_se + ab_se[0]] if len(ab_se) else ff[-1]
        BWn_se = np.trapz((Hpm / H0se) ** 2, ff)      # GEN1 Personick integral (no noise LPF)
        L2 = 1.0 / (1.0 + (ff / 60e9) ** 2) ** 2      # model's 60 GHz filtfilt noise LPF, |L|^2
        Hn2 = (Hm / H0) ** 2 * L2
        B1 = np.trapz(Hn2, ff)                        # white-noise integral (noise BW)
        B2 = np.trapz(ff ** 2 * Hn2, ff)              # f^2-noise integral
        settings.append(dict(
            key=key, vn=vn, H0=H0, H0se=H0se, bw=bw, bw_se=bw_se, BWn_se=BWn_se, B1=B1, B2=B2,
            inr=vn / H0se, f=ff, H=Hc, Rpd=Rpd,
            peak_db=20 * np.log10(H0 / np.abs(Hc[np.searchsorted(ff, 2e9)]))))
    return settings


def sdd21_from_s4p(path):
    """Differential S21 of a 4-port touchstone file (package-trace counterfactual)."""
    vals = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('#'):
                continue
            vals.extend(float(x) for x in line.split())
    pts = np.array(vals).reshape(-1, 33)
    f = pts[:, 0]
    S = pts[:, 1:].reshape(-1, 4, 4, 2)
    S = S[..., 0] + 1j * S[..., 1]
    return f, 0.5 * (S[:, 1, 0] + S[:, 3, 2] - S[:, 1, 2] - S[:, 3, 0])


# ----------------------------------------------------------------------------- Sim grid
# analytic 2-pole step response s(t) = 1 - (1 + t/tau) e^{-t/tau}: 20/80% crossing times
_TT = np.linspace(0, 60, 400000)
_S2 = 1 - (1 + _TT) * np.exp(-_TT)
_T20 = np.interp(0.2, _S2, _TT)
_T80 = np.interp(0.8, _S2, _TT)


class Sim:
    """Rate-dependent frequency grid + pulse-response machinery."""

    def __init__(self, baud, os_r=32, n=8192):
        self.baud = baud
        self.UI = 1.0 / baud
        self.os_r = os_r
        self.N = n
        self.fs = baud * os_r
        self.freqs = np.fft.rfftfreq(n, 1 / self.fs)

    # ---- Tx models ----
    def tx_two_pole_from_tr(self, tr2080):
        """Two identical cascaded real poles fitted to a 20-80% transition time.
        Returns (H, pole_freq_each)."""
        tau = tr2080 / (_T80 - _T20)
        fp = 1 / (2 * np.pi * tau)
        return 1.0 / (1 + 1j * self.freqs / fp) ** 2, fp

    def two_pole(self, f1, f2):
        return 1.0 / ((1 + 1j * self.freqs / f1) * (1 + 1j * self.freqs / f2))

    def one_pole(self, f0):
        return 1.0 / (1 + 1j * self.freqs / f0)

    def butter2(self, f0):
        b, a = sig.butter(2, 2 * np.pi * f0, btype='low', analog=True)
        _, H = sig.freqs(b, a, worN=2 * np.pi * self.freqs)
        return H

    def bessel4(self, f0):
        b, a = sig.bessel(4, 2 * np.pi * f0, btype='low', analog=True, norm='mag')
        _, H = sig.freqs(b, a, worN=2 * np.pi * self.freqs)
        return H

    def tr2080_of(self, H):
        """Numerical 20-80% step transition time of a transfer function."""
        h = np.fft.irfft(H, n=self.N)
        st = np.cumsum(h)
        st /= st[-1] if abs(st[-1]) > 1e-9 else 1.0
        i80 = np.argmax(st >= 0.8)
        i20 = np.argmax(st >= 0.2)
        return (i80 - i20) / self.fs

    # ---- measured TIA TF onto the grid ----
    def tia_interp(self, s, flatten=True):
        """Interpolate a measured differential TF onto the grid, normalized to peak 1.
        flatten=True applies DC restoration: magnitude below 2 GHz held at the 2 GHz value
        with the bulk-delay phase preserved (keeps the response causal)."""
        Hd = s['H'].copy()
        fgrid = s['f']
        if flatten:
            i2g = np.searchsorted(fgrid, 2e9)
            i10 = np.searchsorted(fgrid, 10e9)
            ph = np.unwrap(np.angle(Hd[i2g:i10]))
            tau_blk = -np.polyfit(fgrid[i2g:i10], ph, 1)[0] / (2 * np.pi)
            Hd[:i2g] = np.abs(Hd[i2g]) * np.exp(-1j * 2 * np.pi * fgrid[:i2g] * tau_blk)
        Hn = Hd / np.abs(Hd).max()
        out = (np.interp(self.freqs, fgrid, Hn.real)
               + 1j * np.interp(self.freqs, fgrid, Hn.imag))
        out[self.freqs > fgrid[-1]] = 0.0
        return out

    # ---- pulse response & ISI ----
    def pulse(self, H):
        x = np.zeros(self.N)
        x[self.N // 2:self.N // 2 + self.os_r] = 1.0      # centered 1-UI pulse
        return np.fft.irfft(np.fft.rfft(x) * H, n=self.N)

    def taps_of(self, y, span=10):
        """UI-spaced taps around the cursor, sampling phase optimized for max eye."""
        k = np.argmax(y)
        best = None
        for ph in range(-self.os_r // 2, self.os_r // 2):
            kk = k + ph
            t = np.array([y[kk + i * self.os_r] for i in range(-span, span + 1)
                          if 0 <= kk + i * self.os_r < self.N])
            ci = np.argmax(np.abs(t))
            m = t[ci] - np.abs(np.delete(t, ci)).sum()
            if best is None or m > best[0]:
                best = (m, kk, t, ci)
        _, kk, t, ci = best
        return kk, t, ci

    @staticmethod
    def pp_of(t, ci, dfe_taps=0):
        """Peak-distortion penalty (optical dB); dfe_taps post-cursors removed if given."""
        c = t[ci]
        pre = np.abs(t[:ci]).sum()
        post = np.abs(t[ci + 1 + dfe_taps:]).sum()
        eye = c - pre - post
        return -10 * np.log10(max(eye, 1e-12) / c), pre, post, c

    def eval_chain(self, H, span=10, dfe_taps=0):
        y = self.pulse(H)
        kk, t, ci = self.taps_of(y, span=span)
        return self.pp_of(t, ci, dfe_taps=dfe_taps) + (t, ci, kk, y)

    # ---- EQ ----
    def fir_apply(self, H, w):
        z = np.exp(-1j * 2 * np.pi * self.freqs * self.UI)
        F = sum(wi * z ** i for i, wi in enumerate(w))
        return H * F

    def ctle(self, fz, fp1, fp2):
        s = 1j * 2 * np.pi * self.freqs
        H = (1 + s / (2 * np.pi * fz)) / ((1 + s / (2 * np.pi * fp1)) * (1 + s / (2 * np.pi * fp2)))
        return H / np.abs(H[1])       # unit DC gain; peaking shows as HF boost

    def ctle_noise_enh(self, Htia, Hc):
        """rms noise gain of the CTLE over the TIA-shaped (white-input) noise."""
        return np.sqrt(np.trapz(np.abs(Htia * Hc) ** 2, self.freqs)
                       / np.trapz(np.abs(Htia) ** 2, self.freqs))

    def ctle_sweep(self, Hchannel, Htia_ref, fz_rng, fp_rng, span=10):
        """Min over (zero, double pole) of ISI PP + 10*log10(noise enhancement)."""
        best = (1e9, None)
        den = np.trapz(np.abs(Htia_ref) ** 2, self.freqs)
        for fz in fz_rng:
            for fp in fp_rng:
                Hc = self.ctle(fz, fp, fp)
                pp = self.eval_chain(Hchannel * Hc, span=span)[0]
                ne = np.sqrt(np.trapz(np.abs(Htia_ref * Hc) ** 2, self.freqs) / den)
                tot = pp + 10 * np.log10(ne)
                if tot < best[0]:
                    best = (tot, (fz, fp, pp, ne))
        return best

    def opt_fir(self, npre, npost, Hbase, step=0.02, wmin=-0.40, dfe_taps=0, span=10):
        """Grid search over tap weights under sum|w| = 1 peak-swing constraint.
        Returns (ISI PP + de-emphasis cost, (weights, PP, de-emphasis))."""
        best = (1e9, None)
        rng = np.arange(wmin, 0.001, step)
        for combo in product(*([rng] * (npre + npost))):
            w = list(combo[:npre]) + [1.0] + list(combo[npre:])
            wsum_abs = sum(abs(x) for x in w)
            w = [x / wsum_abs for x in w]
            if sum(w) <= 0:
                continue
            pp = self.eval_chain(self.fir_apply(Hbase, w), span=span, dfe_taps=dfe_taps)[0]
            deemph = -10 * np.log10(sum(w))
            if pp + deemph < best[0]:
                best = (pp + deemph, (w, pp, deemph))
        return best

    # ---- jitter ----
    def jitter_pp(self, H, rj_ui, dj_ui, span=10, q=Q):
        """Dual-Dirac: TJ = DJ + 2*Q*sigma_RJ; penalty on the equalized eye at +/-TJ/2.
        Returns (penalty dB or None if the eye is closed at the offset, TJ in UI)."""
        TJ = dj_ui + 2 * q * rj_ui
        pp, pre, post, c, t, ci, kk, y = self.eval_chain(H, span=span)

        def eye_at(off):
            kk2 = kk + off
            t2 = np.array([y[kk2 + i * self.os_r] for i in range(-span, span + 1)
                           if 0 <= kk2 + i * self.os_r < self.N])
            ci2 = np.argmax(np.abs(t2))
            return t2[ci2] - np.abs(np.delete(t2, ci2)).sum()

        off = int(round(TJ / 2 * self.os_r))
        e0 = eye_at(0)
        emin = min(eye_at(-off), eye_at(off))
        if emin <= 0 or e0 <= 0:
            return None, TJ
        return -10 * np.log10(emin / e0), TJ


# ----------------------------------------------------------------------------- penalties
def rin_shot_penalty(inr_amp, bwn, er_db=4.5, rin_db=-138.0, with_shot=True,
                     resp=RESP, q=Q):
    """Q-solve: extra OMA (dB) needed vs the amp-noise-only floor when RIN and shot noise
    (signal-dependent, on both rails) are added."""
    rin = 10 ** (rin_db / 10)
    E = 10 ** (er_db / 10)

    def Qof(oma):
        I1 = oma * E / (E - 1) * resp
        I0 = I1 - oma * resp
        s1 = np.sqrt(inr_amp ** 2 + rin * bwn * I1 ** 2 + (2 * QE * I1 * bwn if with_shot else 0))
        s0 = np.sqrt(inr_amp ** 2 + rin * bwn * I0 ** 2 + (2 * QE * I0 * bwn if with_shot else 0))
        return oma * resp / (s1 + s0)

    lo, hi = 1e-6, 5e-3
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        if Qof(mid) < q:
            lo = mid
        else:
            hi = mid
    return 10 * np.log10(np.sqrt(lo * hi) / (2 * q * inr_amp / resp))


def mpi_penalty(rt_db, rr_db, rc_db, n_conn, er_db, D):
    """Bhatt/King discounted MPI upper bound (802.3bs), optical dB."""
    Rt, Rr, Rc = 10 ** (rt_db / 10), 10 ** (rr_db / 10), 10 ** (rc_db / 10)
    E = 10 ** (er_db / 10)
    S = (np.sqrt(Rt * Rr) + n_conn * np.sqrt(Rt * Rc) + n_conn * np.sqrt(Rr * Rc)
         + n_conn * (n_conn - 1) / 2 * Rc)
    x = D * 4 * S * E / (E - 1)
    return 10 * np.log10(1 / (1 - x))
