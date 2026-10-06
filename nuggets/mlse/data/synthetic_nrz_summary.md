# MLSE on coloured FFE-output noise: Euclidean vs whitened (NRZ)

- FFE: 8 pre + 1 + 23 post taps, MMSE (Wiener) designed per SNR point
- Symbols per point: 2,000,000 (sim floor 5e-07); same noise realisation for all receivers
- SNR = σ_a²‖h‖²/σ_n² at the FFE input (matched-filter-bound SNR)
- Whitening filter design: min_error
- Required-SNR columns are read at SER = 0.0001; ρ₁ and whitening gain at the mid-sweep SNR

## f₃dB = 0.15 f_baud — h = [0.0095, 0.2231, 0.4077, 0.2733, 0.0876, 0.0052, -0.0063]

MFB needs 11.32 dB at SER 0.0001; ρ₁ / whitening gain quoted at 18 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | nan | +nan | nan | +nan | nan |
| DFE (3 tap) | — | 18.53 | +7.21 | nan | +nan | nan |
| full ML | 6 | 14.78 | +3.46 | nan | +nan | nan |
| GPR L=1 | 1 | 18.96 | +7.64 | 17.88 | -0.365 | 0.00 |
| GPR L=1 +W(1) | 2 | 16.00 | +4.69 | 15.49 | -0.131 | 0.90 |
| GPR L=1 +W(2) | 3 | 15.13 | +3.82 | 14.62 | +0.029 | 1.59 |
| GPR L=1 +W(4) | 5 | 15.20 | +3.88 | 14.75 | +0.009 | 1.69 |
| GPR L=2 | 2 | 15.38 | +4.06 | 14.78 | -0.046 | 0.00 |
| GPR L=3 | 3 | 15.01 | +3.70 | 14.49 | +0.077 | 0.00 |
| GPR L=5 | 5 | 14.99 | +3.68 | 14.48 | +0.086 | 0.00 |
| fixed 1+0.5D | 1 | 20.92 | +9.60 | 19.48 | -0.428 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 16.14 | +4.83 | 15.70 | -0.189 | 1.24 |
| fixed 1+0.5D +W(2) | 3 | 15.24 | +3.92 | 14.73 | +0.002 | 1.94 |
| fixed 1+0.5D +W(4) | 5 | 15.26 | +3.95 | 14.83 | +0.002 | 1.95 |
| LE + MLSE(res L=2) | 2 | nan | +nan | nan | -0.534 | 0.00 |
| LE +W(1) | 1 | 19.19 | +7.88 | 18.17 | -0.386 | 3.81 |
| LE +W(2) | 2 | 15.56 | +4.25 | 15.02 | -0.113 | 5.24 |
| LE +W(4) | 4 | 15.25 | +3.93 | 14.83 | +0.003 | 5.50 |

## f₃dB = 0.2 f_baud — h = [0.1786, 0.5276, 0.2704, 0.0314, -0.0079]

MFB needs 11.32 dB at SER 0.0001; ρ₁ / whitening gain quoted at 18 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | 18.71 | +7.40 | nan | +nan | nan |
| DFE (3 tap) | — | 15.19 | +3.87 | nan | +nan | nan |
| full ML | 4 | 13.10 | +1.78 | nan | +nan | nan |
| GPR L=1 | 1 | 13.93 | +2.62 | 12.96 | -0.197 | 0.00 |
| GPR L=1 +W(1) | 2 | 13.33 | +2.01 | 12.78 | -0.032 | 0.19 |
| GPR L=1 +W(2) | 3 | 13.31 | +2.00 | 12.69 | +0.013 | 0.30 |
| GPR L=1 +W(4) | 5 | 13.19 | +1.87 | 12.62 | +0.001 | 0.37 |
| GPR L=2 | 2 | 13.16 | +1.84 | 12.56 | +0.022 | 0.00 |
| GPR L=3 | 3 | 13.17 | +1.85 | 12.56 | +0.029 | 0.00 |
| GPR L=5 | 5 | 13.15 | +1.83 | 12.56 | +0.029 | 0.00 |
| fixed 1+0.5D | 1 | 14.25 | +2.93 | 13.40 | -0.384 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 13.34 | +2.02 | 12.71 | -0.042 | 0.73 |
| fixed 1+0.5D +W(2) | 3 | 13.27 | +1.95 | 12.63 | +0.000 | 0.77 |
| fixed 1+0.5D +W(4) | 5 | 13.21 | +1.89 | 12.61 | -0.003 | 0.78 |
| LE + MLSE(res L=2) | 2 | 18.14 | +6.82 | 17.82 | -0.690 | 0.00 |
| LE +W(1) | 1 | 13.95 | +2.64 | 13.08 | -0.216 | 3.30 |
| LE +W(2) | 2 | 13.19 | +1.88 | 12.60 | -0.009 | 3.69 |
| LE +W(4) | 4 | 13.22 | +1.90 | 12.61 | -0.003 | 3.69 |

## f₃dB = 0.25 f_baud — h = [0.1396, 0.6322, 0.2281]

MFB needs 11.32 dB at SER 0.0001; ρ₁ / whitening gain quoted at 18 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | 14.37 | +3.05 | nan | +nan | nan |
| DFE (3 tap) | — | 13.15 | +1.84 | nan | +nan | nan |
| full ML | 2 | 11.78 | +0.46 | nan | +nan | nan |
| GPR L=1 | 1 | 11.85 | +0.53 | 11.49 | -0.038 | 0.00 |
| GPR L=1 +W(1) | 2 | 11.85 | +0.53 | 11.50 | -0.001 | 0.01 |
| GPR L=1 +W(2) | 3 | 11.87 | +0.55 | 11.47 | +0.004 | 0.03 |
| GPR L=1 +W(4) | 5 | 11.89 | +0.58 | 11.45 | +0.002 | 0.04 |
| GPR L=2 | 2 | 11.84 | +0.52 | 11.44 | +0.015 | 0.00 |
| GPR L=3 | 3 | 11.84 | +0.52 | 11.44 | +0.015 | 0.00 |
| GPR L=5 | 5 | 11.84 | +0.52 | 11.44 | +0.015 | 0.00 |
| fixed 1+0.5D | 1 | 11.89 | +0.58 | 11.51 | -0.099 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 11.86 | +0.54 | 11.49 | -0.002 | 0.04 |
| fixed 1+0.5D +W(2) | 3 | 11.87 | +0.56 | 11.46 | +0.003 | 0.05 |
| fixed 1+0.5D +W(4) | 5 | 11.87 | +0.56 | 11.45 | +0.002 | 0.05 |
| LE + MLSE(res L=2) | 2 | 14.14 | +2.83 | 14.09 | -0.547 | 0.00 |
| LE +W(1) | 1 | 11.90 | +0.59 | 11.53 | -0.049 | 1.63 |
| LE +W(2) | 2 | 11.86 | +0.55 | 11.45 | +0.002 | 1.67 |
| LE +W(4) | 4 | 11.86 | +0.55 | 11.45 | +0.002 | 1.67 |
