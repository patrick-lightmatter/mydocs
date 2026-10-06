# MLSE on coloured FFE-output noise: Euclidean vs whitened (PAM4)

- FFE: 8 pre + 1 + 23 post taps, MMSE (Wiener) designed per SNR point
- Symbols per point: 1,000,000 (sim floor 1e-06); same noise realisation for all receivers
- SNR = σ_a²‖h‖²/σ_n² at the FFE input (matched-filter-bound SNR)
- Whitening filter design: min_error
- Required-SNR columns are read at SER = 0.0001; ρ₁ and whitening gain at the mid-sweep SNR

## f₃dB = 0.15 f_baud — h = [0.0095, 0.2231, 0.4077, 0.2733, 0.0876, 0.0052, -0.0063]

MFB needs 18.54 dB at SER 0.0001; ρ₁ / whitening gain quoted at 24 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | nan | +nan | nan | +nan | nan |
| DFE (3 tap) | — | 27.41 | +8.87 | nan | +nan | nan |
| GPR L=1 | 1 | 28.33 | +9.79 | 26.79 | -0.519 | 0.00 |
| GPR L=1 +W(1) | 2 | 24.68 | +6.14 | 24.15 | -0.197 | 1.58 |
| GPR L=1 +W(2) | 3 | 24.10 | +5.56 | 23.36 | +0.008 | 2.29 |
| GPR L=1 +W(3) | 4 | 24.08 | +5.54 | 23.34 | +0.004 | 2.31 |
| GPR L=2 | 2 | 24.54 | +6.00 | 23.91 | -0.143 | 0.00 |
| GPR L=3 | 3 | 24.08 | +5.54 | 23.28 | +0.015 | 0.00 |
| GPR L=4 | 4 | 24.06 | +5.52 | 23.24 | +0.033 | 0.00 |
| fixed 1+0.5D | 1 | nan | +nan | nan | -0.633 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 24.79 | +6.25 | 24.14 | -0.284 | 3.13 |
| fixed 1+0.5D +W(2) | 3 | 24.04 | +5.50 | 23.35 | -0.034 | 3.88 |
| fixed 1+0.5D +W(3) | 4 | 24.06 | +5.52 | 23.27 | -0.001 | 3.91 |
| LE + MLSE(res L=2) | 2 | nan | +nan | nan | -0.714 | 0.00 |
| LE +W(1) | 1 | 28.35 | +9.81 | 26.85 | -0.527 | 6.16 |
| LE +W(2) | 2 | 24.55 | +6.01 | 23.90 | -0.169 | 8.20 |
| LE +W(3) | 3 | 24.08 | +5.54 | 23.31 | -0.016 | 8.55 |

## f₃dB = 0.2 f_baud — h = [0.1786, 0.5276, 0.2704, 0.0314, -0.0079]

MFB needs 18.54 dB at SER 0.0001; ρ₁ / whitening gain quoted at 24 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | 26.31 | +7.77 | nan | +nan | nan |
| DFE (3 tap) | — | 23.00 | +4.46 | nan | +nan | nan |
| full ML | 4 | 20.71 | +2.17 | nan | +nan | nan |
| GPR L=1 | 1 | 21.55 | +3.01 | 20.59 | -0.234 | 0.00 |
| GPR L=1 +W(1) | 2 | 20.93 | +2.39 | 20.12 | -0.035 | 0.25 |
| GPR L=1 +W(2) | 3 | 20.91 | +2.37 | 20.05 | +0.016 | 0.36 |
| GPR L=1 +W(3) | 4 | 20.80 | +2.26 | 20.01 | +0.007 | 0.40 |
| GPR L=2 | 2 | 20.79 | +2.25 | 19.98 | +0.001 | 0.00 |
| GPR L=3 | 3 | 20.75 | +2.21 | 19.98 | +0.009 | 0.00 |
| GPR L=4 | 4 | 20.74 | +2.20 | 19.98 | +0.009 | 0.00 |
| fixed 1+0.5D | 1 | 22.48 | +3.94 | 21.58 | -0.463 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 20.80 | +2.26 | 20.04 | -0.042 | 1.07 |
| fixed 1+0.5D +W(2) | 3 | 20.76 | +2.22 | 19.99 | +0.003 | 1.11 |
| fixed 1+0.5D +W(3) | 4 | 20.75 | +2.21 | 19.98 | +0.000 | 1.11 |
| LE + MLSE(res L=2) | 2 | 26.22 | +7.68 | 26.26 | -0.755 | 0.00 |
| LE +W(1) | 1 | 21.55 | +3.01 | 20.60 | -0.239 | 3.84 |
| LE +W(2) | 2 | 20.76 | +2.22 | 19.98 | -0.007 | 4.28 |
| LE +W(3) | 3 | 20.75 | +2.21 | 19.98 | +0.000 | 4.29 |

## f₃dB = 0.25 f_baud — h = [0.1396, 0.6322, 0.2281]

MFB needs 18.54 dB at SER 0.0001; ρ₁ / whitening gain quoted at 24 dB.

| receiver | trellis memory | req. SNR MC [dB] | vs MFB [dB] | req. SNR bound [dB] | ρ₁(error) | whitening gain p→∞ proxy [dB] |
|---|---|---|---|---|---|---|
| LE | — | 21.77 | +3.23 | nan | +nan | nan |
| DFE (3 tap) | — | 20.59 | +2.05 | nan | +nan | nan |
| full ML | 2 | 18.96 | +0.42 | nan | +nan | nan |
| GPR L=1 | 1 | 19.14 | +0.60 | 18.60 | -0.053 | 0.00 |
| GPR L=1 +W(1) | 2 | 19.07 | +0.53 | 18.56 | -0.005 | 0.01 |
| GPR L=1 +W(2) | 3 | 19.14 | +0.60 | 18.55 | +0.001 | 0.03 |
| GPR L=1 +W(3) | 4 | 19.09 | +0.55 | 18.54 | -0.001 | 0.04 |
| GPR L=2 | 2 | 18.99 | +0.45 | 18.54 | +0.002 | 0.00 |
| GPR L=3 | 3 | 18.99 | +0.45 | 18.54 | +0.002 | 0.00 |
| GPR L=4 | 4 | 18.99 | +0.45 | 18.54 | +0.002 | 0.00 |
| fixed 1+0.5D | 1 | 19.18 | +0.64 | 18.64 | -0.127 | 0.00 |
| fixed 1+0.5D +W(1) | 2 | 19.00 | +0.46 | 18.55 | -0.006 | 0.07 |
| fixed 1+0.5D +W(2) | 3 | 19.02 | +0.48 | 18.54 | -0.001 | 0.07 |
| fixed 1+0.5D +W(3) | 4 | 19.06 | +0.52 | 18.54 | -0.002 | 0.07 |
| LE + MLSE(res L=2) | 2 | 21.69 | +3.15 | 21.78 | -0.573 | 0.00 |
| LE +W(1) | 1 | 19.12 | +0.58 | 18.60 | -0.056 | 1.75 |
| LE +W(2) | 2 | 18.97 | +0.43 | 18.54 | -0.002 | 1.79 |
| LE +W(3) | 3 | 19.05 | +0.51 | 18.54 | -0.002 | 1.79 |
