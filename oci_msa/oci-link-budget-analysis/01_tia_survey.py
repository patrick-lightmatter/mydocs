"""
01 - TIA survey: scan all 152 Ocelot ADFET TT-corner settings.

Produces (used on the OCI-link-budget-bottom-up canvas):
  - settings count, usable count at 53.125 GBd (BW3dB >= 0.55 x baud)
  - GEN1 design point 12211111: i_n = 3.17 uA rms, BW 29.3 GHz, R = 0.876 A/W
  - analytic sensitivity floor -12.93 dBm OMA at Q = 7.035

Inputs: TT_Tia_Noise.csv + TT_Tia_TF_<key>.csv under common.TIA_DIR.
"""
import numpy as np

from common import Q, TIA_DIR, floor_dbm, load_tia_settings

BAUD_GEN1 = 53.125e9

settings = load_tia_settings()
print(f"settings analyzed: {len(settings)}  (from {TIA_DIR})")

# usable at GEN1: BW3dB >= 0.55 x baud (lecture 4: optimum Rx BW ~0.6-0.7 x bit rate for NRSZ).
# GEN1 convention: bandwidth/selection on the single-ended p-leg response (bw_se).
BW_MIN = 0.55 * BAUD_GEN1
ok = sorted([s for s in settings if s['bw_se'] >= BW_MIN], key=lambda s: s['inr'])
print(f"settings with BW3dB >= {BW_MIN/1e9:.1f} GHz: {len(ok)}")

for name, s in [('BEST-usable', ok[0]), ('MEDIAN-usable', ok[len(ok)//2]), ('WORST-usable', ok[-1])]:
    print(f"{name}: key={s['key']} ZTse={s['H0se']:.0f} V/A ({20*np.log10(s['H0se']):.1f} dBohm SE, "
          f"{20*np.log10(s['H0']):.1f} dBohm diff) BW3dB={s['bw_se']/1e9:.1f} GHz "
          f"BWn={s['BWn_se']/1e9:.1f} GHz vn={s['vn']*1e3:.2f} mV in={s['inr']*1e6:.2f} uA rms "
          f"Rpd={s['Rpd']:.3f} A/W")

sel = ok[0]
print(f"\nGEN1 design point: key={sel['key']}, i_n = {sel['inr']*1e6:.2f} uA rms, "
      f"R = {sel['Rpd']:.3f} A/W, BW3dB = {sel['bw_se']/1e9:.1f} GHz = {sel['bw_se']/BAUD_GEN1:.2f} x baud")
print(f"Analytic floor 2*Q*i_n/R at Q={Q}: {floor_dbm(sel['inr'], resp=sel['Rpd']):.2f} dBm OMA")
print(f"(expected on canvas: i_n 3.17 uA, 29.3 GHz, floor -12.93 dBm)")
