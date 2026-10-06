# MLSE on coloured FFE-output noise: Euclidean vs whitened (NRZ)

- FFE: 8 pre + 1 + 23 post taps, MMSE (Wiener) designed per SNR point
- Symbols per point: 2,000,000 (sim floor 5e-07); same noise realisation for all receivers
- SNR = σ_a²‖h‖²/σ_n² at the FFE input (matched-filter-bound SNR)
- Required-SNR columns are read at SER = 0.0001; ρ₁ and whitening gain at the mid-sweep SNR

## f₃dB = 0.15 f_baud — h = [0.0095, 0.2231, 0.4077, 0.2733, 0.0876, 0.0052, -0.0063]

MFB needs 11.32 dB at SER 0.0001; ρ₁ / whitening gain quoted at 18 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | nan | +nan | nan | +nan | nan |
| DFE (3 tap) | — | 18.53 | +7.21 | nan | +nan | nan |
| full ML | 6 | 14.78 | +3.46 | nan | +nan | nan |
| GPR L=1 | 1 | 18.96 | +7.64 | 17.88 | -0.365 | 0.00 |
| GPR L=1 +W(1) | 2 | 16.16 | +4.84 | 15.71 | -0.166 | 0.62 |
| GPR L=1 +W(2) | 3 | 15.16 | +3.85 | 14.66 | -0.016 | 1.20 |
| GPR L=1 +W(4) | 5 | 15.41 | +4.09 | 14.85 | -0.039 | 1.31 |
| GPR L=2 | 2 | 15.38 | +4.06 | 14.78 | -0.046 | 0.00 |
| GPR L=3 | 3 | 15.01 | +3.70 | 14.49 | +0.077 | 0.00 |
| GPR L=5 | 5 | 14.99 | +3.68 | 14.48 | +0.086 | 0.00 |
| fixed 1+0.5D | 1 | 20.92 | +9.60 | 19.48 | -0.428 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 16.71 | +5.40 | 16.15 | -0.259 | 0.88 |
| fixed 1+0.5D +W(2) | 3 | 15.40 | +4.08 | 15.02 | -0.139 | 1.38 |
| fixed 1+0.5D +W(4) | 5 | 15.47 | +4.16 | 15.14 | -0.135 | 1.40 |
| LE + MLSE(res L=2) | 2 | nan | +nan | nan | -0.534 | 0.00 |
| LE +W(1) | 1 | 19.88 | +8.56 | 18.81 | -0.420 | 1.44 |
| LE +W(2) | 2 | nan | +nan | 19.14 | -0.426 | 1.45 |
| LE +W(4) | 4 | 19.89 | +8.57 | 19.04 | -0.407 | 1.47 |

## f₃dB = 0.2 f_baud — h = [0.1786, 0.5276, 0.2704, 0.0314, -0.0079]

MFB needs 11.32 dB at SER 0.0001; ρ₁ / whitening gain quoted at 18 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | 18.71 | +7.40 | nan | +nan | nan |
| DFE (3 tap) | — | 15.19 | +3.87 | nan | +nan | nan |
| full ML | 4 | 13.10 | +1.78 | nan | +nan | nan |
| GPR L=1 | 1 | 13.93 | +2.62 | 12.96 | -0.197 | 0.00 |
| GPR L=1 +W(1) | 2 | 13.35 | +2.04 | 12.79 | -0.038 | 0.17 |
| GPR L=1 +W(2) | 3 | 13.28 | +1.97 | 12.67 | +0.010 | 0.28 |
| GPR L=1 +W(4) | 5 | 13.20 | +1.89 | 12.62 | -0.001 | 0.35 |
| GPR L=2 | 2 | 13.16 | +1.84 | 12.56 | +0.022 | 0.00 |
| GPR L=3 | 3 | 13.17 | +1.85 | 12.56 | +0.029 | 0.00 |
| GPR L=5 | 5 | 13.15 | +1.83 | 12.56 | +0.029 | 0.00 |
| fixed 1+0.5D | 1 | 14.25 | +2.93 | 13.40 | -0.384 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 13.36 | +2.05 | 12.74 | -0.059 | 0.69 |
| fixed 1+0.5D +W(2) | 3 | 13.30 | +1.98 | 12.66 | -0.018 | 0.73 |
| fixed 1+0.5D +W(4) | 5 | 13.22 | +1.90 | 12.63 | -0.020 | 0.74 |
| LE + MLSE(res L=2) | 2 | 18.14 | +6.82 | 17.82 | -0.690 | 0.00 |
| LE +W(1) | 1 | 14.03 | +2.71 | 13.22 | -0.239 | 2.70 |
| LE +W(2) | 2 | 13.83 | +2.51 | 13.09 | -0.150 | 2.79 |
| LE +W(4) | 4 | 13.78 | +2.46 | 13.01 | -0.150 | 2.80 |

## f₃dB = 0.25 f_baud — h = [0.1396, 0.6322, 0.2281]

MFB needs 11.32 dB at SER 0.0001; ρ₁ / whitening gain quoted at 18 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | 14.37 | +3.05 | nan | +nan | nan |
| DFE (3 tap) | — | 13.15 | +1.84 | nan | +nan | nan |
| full ML | 2 | 11.78 | +0.46 | nan | +nan | nan |
| GPR L=1 | 1 | 11.85 | +0.53 | 11.49 | -0.038 | 0.00 |
| GPR L=1 +W(1) | 2 | 11.85 | +0.53 | 11.50 | -0.001 | 0.01 |
| GPR L=1 +W(2) | 3 | 11.85 | +0.54 | 11.46 | +0.004 | 0.03 |
| GPR L=1 +W(4) | 5 | 11.89 | +0.57 | 11.45 | +0.002 | 0.04 |
| GPR L=2 | 2 | 11.84 | +0.52 | 11.44 | +0.015 | 0.00 |
| GPR L=3 | 3 | 11.84 | +0.52 | 11.44 | +0.015 | 0.00 |
| GPR L=5 | 5 | 11.84 | +0.52 | 11.44 | +0.015 | 0.00 |
| fixed 1+0.5D | 1 | 11.89 | +0.58 | 11.51 | -0.099 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 11.86 | +0.54 | 11.49 | -0.003 | 0.04 |
| fixed 1+0.5D +W(2) | 3 | 11.87 | +0.55 | 11.46 | +0.002 | 0.05 |
| fixed 1+0.5D +W(4) | 5 | 11.89 | +0.57 | 11.45 | +0.001 | 0.05 |
| LE + MLSE(res L=2) | 2 | 14.14 | +2.83 | 14.09 | -0.547 | 0.00 |
| LE +W(1) | 1 | 11.93 | +0.62 | 11.55 | -0.055 | 1.54 |
| LE +W(2) | 2 | 11.88 | +0.57 | 11.51 | -0.016 | 1.57 |
| LE +W(4) | 4 | 11.88 | +0.57 | 11.51 | -0.016 | 1.57 |
