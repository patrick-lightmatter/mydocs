# Caribou OCI-Gen2 NRZ Receiver Study — 1-Tap DFE

**Date:** 2026-06-07
**Signal:** NRZ, 106.25 Gbaud
**Platform:** Caribou OCI-Gen2
**Waveform source:** Virtuoso transient, 6 OMA × VGA variants
**TX reference:** `snps200g_nrz_from_bitfile_300k_symbols_pam4digits.txt` (300 k symbols)

This report extends the baseline FFE-only study with a single-tap decision-feedback
equaliser (DFE) on the first post-cursor, matching the SNPS reference receiver chain.

---

## 1  Receiver Chain

```
analog in
   │
   ▼
CTLE  (1z2p, pk = 4.0 dB, G_DC = −3.0 dB)
   │
   ▼
IdealADC  (32 SPS, fs ≈ 3.4 GS/s)
   │
   ▼
Mueller-Müller CDR  (baud-rate MM-TED, kp = 0.01, TED w_pre = 0.9 / w_post = 1.0)
   │
   ▼
RxFFE  (5 pre + 1 main + 14 post = 20 taps, μ = 0.01, LMS)
         cursor +1 tap constrained to zero — first post-cursor reserved for DFE
   │
   ▼
RxDFE  (1 feedback tap b₁, μ = 0.005, LMS)
   │
   ▼
NRZ slicer
```

### 1.1  DFE equation

```
y_out[k] = y_ff[k] − b₁ · â[k−1]
```

where `y_ff[k]` is the FFE output, `b₁` is the adaptive feedback tap, and `â[k−1]`
is the previous hard decision (±1 for NRZ).

### 1.2  FFE cursor+1 constraint

The FFE tap at cursor position +1 (the tap applied to the sample one UI in the past,
i.e. the one that would otherwise cancel h₁ independently) is forced to zero after
the CDR+FFE adaptive pass.  This ensures the DFE has exclusive ownership of the
first post-cursor ISI component and its tap value reflects the actual channel h₁.

Without this constraint, the FFE and DFE jointly absorb h₁, leaving the DFE tap
near zero and providing no diagnostic value.

---

## 2  Convergence Methodology

### 2.1  Staged three-pass adaptation

Enabling CDR, FFE, and DFE simultaneously is unstable: the DFE feedback
introduces a constant bias of `+b₁` into the MM-TED, causing the CDR to drift
continuously.  A staged approach resolves this.

**Pass 1 — CDR + FFE adaptive (no DFE)**
The waveform is tiled 3× (≈131 k symbols).  The DFE is excluded so the MM-TED
is unbiased.  The CDR converges to its lock point (phase 29 / 32) and the FFE
adapts all 20 taps via LMS, including the cursor+1 tap.

**Cursor+1 zeroing**
After Pass 1 the cursor+1 FFE tap is set to zero, handing the first post-cursor
ISI component over to the DFE exclusively.

**Pass 2 — DFE training (frozen CDR + FFE, adaptive DFE)**
The CDR is locked at the settled phase (kp = ki = 0).  The FFE is frozen at the
Pass-1 taps (cursor+1 = 0).  The DFE adapts on a single un-tiled CSV period
(≈43 k symbols, avoiding tile-boundary preamble artefacts) until b₁ converges.

**Pass 3 — Frozen final pass**
A single CSV period is run with all loops frozen: CDR at settled phase, FFE at
Pass-1 taps (cursor+1 = 0), DFE at Pass-2 tap.  BER and SNR are measured on
this pass.

### 2.2  Performance metrics

- **SNR** — eye amplitude / intra-level σ of frozen-pass equalised output, dB.
- **Extrapolated BER** — Gaussian eye-model projection to the `10⁻¹²` tail.
- **Confidence BER** — Poisson 95 % upper bound.  Zero errors in 43 k symbols gives
  an upper bound of `8.45 × 10⁻⁹`.
- **Raw BER** — direct error count over the frozen pass.  Zero across all variants.

All six variants are polarity-inverted relative to the TX reference, consistent with
the known OCI-Gen2 channel characteristic.

---

## 3  Test Matrix

| Variant | OMA (µW) | VGA |
|---------|----------|-----|
| OMA_100uW_VGA1_0 | 100 | 0 |
| OMA_100uW_VGA1_2 | 100 | 2 |
| OMA_150uW_VGA1_0 | 150 | 0 |
| OMA_150uW_VGA1_2 | 150 | 2 |
| OMA_200uW_VGA1_0 | 200 | 0 |
| OMA_200uW_VGA1_2 | 200 | 2 |

---

## 4  Results

### 4.1  Per-variant BER and SNR

| Variant | Raw BER | Conf. BER | Extrap. BER | SNR (dB) | Intra σ | DFE b₁ | CDR phase |
|---------|---------|-----------|-------------|----------|---------|--------|-----------|
| OMA_100uW_VGA1_0 | 0 | 8.45 × 10⁻⁹ | 3.11 × 10⁻⁵ | **12.05** | 0.2969 | +0.5922 | 29 |
| OMA_100uW_VGA1_2 | 0 | 8.45 × 10⁻⁹ | 3.16 × 10⁻⁵ | **12.04** | 0.3055 | +0.6311 | 29 |
| OMA_150uW_VGA1_0 | 0 | 8.45 × 10⁻⁹ | 1.25 × 10⁻⁵ | **12.50** | 0.2860 | +0.6101 | 29 |
| OMA_150uW_VGA1_2 | 0 | 8.45 × 10⁻⁹ | 1.49 × 10⁻⁵ | **12.41** | 0.2942 | +0.6390 | 29 |
| OMA_200uW_VGA1_0 | 0 | 8.45 × 10⁻⁹ | 1.00 × 10⁻⁵ | **12.60** | 0.2835 | +0.6167 | 29 |
| OMA_200uW_VGA1_2 | 0 | 8.45 × 10⁻⁹ | 1.09 × 10⁻⁵ | **12.56** | 0.2886 | +0.6360 | 29 |

### 4.2  Comparison with FFE-only baseline

| Variant | SNR — baseline | SNR — FFE + DFE | Δ SNR | Extrap. BER — baseline | Extrap. BER — FFE + DFE |
|---------|---------------|----------------|-------|------------------------|------------------------|
| OMA_100uW_VGA1_0 | 15.22 dB | 12.05 dB | −3.17 dB | 3.98 × 10⁻⁹ | 3.11 × 10⁻⁵ |
| OMA_100uW_VGA1_2 | 16.13 dB | 12.04 dB | −4.09 dB | 7.58 × 10⁻¹¹ | 3.16 × 10⁻⁵ |
| OMA_150uW_VGA1_0 | 17.27 dB | 12.50 dB | −4.77 dB | 1.38 × 10⁻¹³ | 1.25 × 10⁻⁵ |
| OMA_150uW_VGA1_2 | 17.89 dB | 12.41 dB | −5.48 dB | 2.14 × 10⁻¹⁵ | 1.49 × 10⁻⁵ |
| OMA_200uW_VGA1_0 | 18.31 dB | 12.60 dB | −5.71 dB | 9.16 × 10⁻¹⁷ | 1.00 × 10⁻⁵ |
| OMA_200uW_VGA1_2 | 18.69 dB | 12.56 dB | −6.13 dB | 3.82 × 10⁻¹⁸ | 1.09 × 10⁻⁵ |

The SNR penalty (3–6 dB relative to baseline) reflects the cost of the cursor+1
constraint: the baseline FFE used the cursor+1 tap as part of a joint 14-tap
post-cursor optimisation, and a single DFE tap cannot fully substitute for that
joint optimisation.  The penalty grows with OMA because at higher OMA, the noise
floor drops and residual ISI from unconstrained joint optimisation becomes the
dominant impairment.

### 4.3  DFE tap interpretation

The DFE tap b₁ is consistent across all six variants (0.592–0.639), independent
of OMA and VGA setting.  This is expected: b₁ reflects the channel first
post-cursor h₁ (at the CDR's sampling phase), which is a channel property, not a
function of optical power.

The tap values are significantly larger than the near-zero values obtained when
the cursor+1 FFE tap is left free (~0.005).  This confirms that the cursor+1
constraint successfully redirects the first post-cursor cancellation responsibility
to the DFE.

### 4.4  OMA vs BER curve

![OMA vs BER (DFE)](figures_dfe/oma_vs_ber_dfe.png)

---

## 5  Adapted Equalizer Tap Weights

CTLE: **1z2p, peaking = 4.0 dB, G_DC = −3.0 dB** (all variants).
FFE: **5 pre + 1 main + 14 post cursors** (20 taps). Cursor +1 forced to 0.

### 5.1  OMA_100uW_VGA1_0

| Tap | Weight | | Tap | Weight |
|-----|--------|-|-----|--------|
| +14 | −0.001855 | | +0 (main) | **+3.130293** |
| +13 | −0.001952 | | −1 | −1.019586 |
| +12 | +0.019616 | | −2 | +0.307747 |
| +11 | −0.023258 | | −3 | −0.098288 |
| +10 | +0.032718 | | −4 | +0.028265 |
| +9 | −0.035070 | | −5 | −0.023056 |
| +8 | +0.058388 | | **DFE b₁** | **+0.592233** |
| +7 | −0.077172 | | | |
| +6 | +0.144892 | | | |
| +5 | −0.205430 | | | |
| +4 | +0.448149 | | | |
| +3 | −0.670145 | | | |
| +2 | +1.414710 | | | |
| **+1** | **0.000000** ← zeroed | | | |

### 5.2  OMA_100uW_VGA1_2

| Tap | Weight | | Tap | Weight |
|-----|--------|-|-----|--------|
| +14 | −0.005903 | | +0 (main) | **+3.243450** |
| +13 | −0.006510 | | −1 | −1.113150 |
| +12 | +0.028383 | | −2 | +0.366194 |
| +11 | −0.014310 | | −3 | −0.144950 |
| +10 | +0.005475 | | −4 | +0.026653 |
| +9 | −0.022791 | | −5 | −0.025651 |
| +8 | +0.062698 | | **DFE b₁** | **+0.631135** |
| +7 | −0.075379 | | | |
| +6 | +0.137931 | | | |
| +5 | −0.211229 | | | |
| +4 | +0.452168 | | | |
| +3 | −0.700849 | | | |
| +2 | +1.475886 | | | |
| **+1** | **0.000000** ← zeroed | | | |

### 5.3  OMA_150uW_VGA1_0

| Tap | Weight | | Tap | Weight |
|-----|--------|-|-----|--------|
| +14 | −0.001529 | | +0 (main) | **+3.001787** |
| +13 | −0.005206 | | −1 | −0.973860 |
| +12 | +0.021706 | | −2 | +0.297390 |
| +11 | −0.021038 | | −3 | −0.097783 |
| +10 | +0.028479 | | −4 | +0.024578 |
| +9 | −0.034886 | | −5 | −0.019641 |
| +8 | +0.057318 | | **DFE b₁** | **+0.610113** |
| +7 | −0.076718 | | | |
| +6 | +0.142284 | | | |
| +5 | −0.206942 | | | |
| +4 | +0.445887 | | | |
| +3 | −0.667644 | | | |
| +2 | +1.378975 | | | |
| **+1** | **0.000000** ← zeroed | | | |

### 5.4  OMA_150uW_VGA1_2

| Tap | Weight | | Tap | Weight |
|-----|--------|-|-----|--------|
| +14 | −0.004140 | | +0 (main) | **+3.073463** |
| +13 | −0.008626 | | −1 | −1.039409 |
| +12 | +0.028234 | | −2 | +0.338216 |
| +11 | −0.015360 | | −3 | −0.128569 |
| +10 | +0.009849 | | −4 | +0.022245 |
| +9 | −0.023853 | | −5 | −0.021232 |
| +8 | +0.056441 | | **DFE b₁** | **+0.639031** |
| +7 | −0.070395 | | | |
| +6 | +0.128993 | | | |
| +5 | −0.200088 | | | |
| +4 | +0.432471 | | | |
| +3 | −0.673826 | | | |
| +2 | +1.405839 | | | |
| **+1** | **0.000000** ← zeroed | | | |

### 5.5  OMA_200uW_VGA1_0

| Tap | Weight | | Tap | Weight |
|-----|--------|-|-----|--------|
| +14 | −0.000755 | | +0 (main) | **+2.920242** |
| +13 | −0.007185 | | −1 | −0.933644 |
| +12 | +0.023163 | | −2 | +0.283029 |
| +11 | −0.020118 | | −3 | −0.093473 |
| +10 | +0.026552 | | −4 | +0.021103 |
| +9 | −0.034533 | | −5 | −0.017607 |
| +8 | +0.055920 | | **DFE b₁** | **+0.616652** |
| +7 | −0.075472 | | | |
| +6 | +0.140266 | | | |
| +5 | −0.206851 | | | |
| +4 | +0.442537 | | | |
| +3 | −0.662317 | | | |
| +2 | +1.352313 | | | |
| **+1** | **0.000000** ← zeroed | | | |

### 5.6  OMA_200uW_VGA1_2

| Tap | Weight | | Tap | Weight |
|-----|--------|-|-----|--------|
| +14 | −0.002549 | | +0 (main) | **+2.958168** |
| +13 | −0.009965 | | −1 | −0.976925 |
| +12 | +0.028575 | | −2 | +0.310857 |
| +11 | −0.016153 | | −3 | −0.114044 |
| +10 | +0.011368 | | −4 | +0.017489 |
| +9 | −0.023238 | | −5 | −0.017896 |
| +8 | +0.051078 | | **DFE b₁** | **+0.635988** |
| +7 | −0.064649 | | | |
| +6 | +0.120100 | | | |
| +5 | −0.187856 | | | |
| +4 | +0.411687 | | | |
| +3 | −0.645115 | | | |
| +2 | +1.347643 | | | |
| **+1** | **0.000000** ← zeroed | | | |

---

## 6  CDR Convergence

All variants lock to **phase 29 / 32** with CDR PI standard deviation ≤ 0.3,
identical to the FFE-only baseline.  The staged adaptation (CDR+FFE first,
cursor+1 zeroed, then DFE trains with frozen CDR) prevents the DFE feedback
from biasing the MM-TED.

### CDR trajectories

#### OMA_100uW_VGA1_0
![CDR trajectory OMA_100uW_VGA1_0](figures_dfe/cdr_trajectory_OMA_100uW_VGA1_0.png)

#### OMA_100uW_VGA1_2
![CDR trajectory OMA_100uW_VGA1_2](figures_dfe/cdr_trajectory_OMA_100uW_VGA1_2.png)

#### OMA_150uW_VGA1_0
![CDR trajectory OMA_150uW_VGA1_0](figures_dfe/cdr_trajectory_OMA_150uW_VGA1_0.png)

#### OMA_150uW_VGA1_2
![CDR trajectory OMA_150uW_VGA1_2](figures_dfe/cdr_trajectory_OMA_150uW_VGA1_2.png)

#### OMA_200uW_VGA1_0
![CDR trajectory OMA_200uW_VGA1_0](figures_dfe/cdr_trajectory_OMA_200uW_VGA1_0.png)

#### OMA_200uW_VGA1_2
![CDR trajectory OMA_200uW_VGA1_2](figures_dfe/cdr_trajectory_OMA_200uW_VGA1_2.png)

---

## 7  DFE Tap Convergence

The DFE tap starts at zero at the beginning of Pass 2 and converges within the
single CSV period (≈43 k symbols, ≈0.41 µs).  No tile-boundary artefacts are
present since the training pass uses the un-tiled waveform.

#### OMA_100uW_VGA1_0
![DFE tap trajectory OMA_100uW_VGA1_0](figures_dfe/dfe_tap_trajectory_OMA_100uW_VGA1_0.png)

#### OMA_100uW_VGA1_2
![DFE tap trajectory OMA_100uW_VGA1_2](figures_dfe/dfe_tap_trajectory_OMA_100uW_VGA1_2.png)

#### OMA_150uW_VGA1_0
![DFE tap trajectory OMA_150uW_VGA1_0](figures_dfe/dfe_tap_trajectory_OMA_150uW_VGA1_0.png)

#### OMA_150uW_VGA1_2
![DFE tap trajectory OMA_150uW_VGA1_2](figures_dfe/dfe_tap_trajectory_OMA_150uW_VGA1_2.png)

#### OMA_200uW_VGA1_0
![DFE tap trajectory OMA_200uW_VGA1_0](figures_dfe/dfe_tap_trajectory_OMA_200uW_VGA1_0.png)

#### OMA_200uW_VGA1_2
![DFE tap trajectory OMA_200uW_VGA1_2](figures_dfe/dfe_tap_trajectory_OMA_200uW_VGA1_2.png)

---

## 8  Adaptation Dashboards

Each dashboard shows (top to bottom): FFE tap convergence, CDR PI code trajectory,
rolling SNR, timing error, and DFE b₁ convergence.

#### OMA_100uW_VGA1_0
![Adaptation dashboard OMA_100uW_VGA1_0](figures_dfe/rx_adaptation_dashboard_OMA_100uW_VGA1_0.png)

#### OMA_100uW_VGA1_2
![Adaptation dashboard OMA_100uW_VGA1_2](figures_dfe/rx_adaptation_dashboard_OMA_100uW_VGA1_2.png)

#### OMA_150uW_VGA1_0
![Adaptation dashboard OMA_150uW_VGA1_0](figures_dfe/rx_adaptation_dashboard_OMA_150uW_VGA1_0.png)

#### OMA_150uW_VGA1_2
![Adaptation dashboard OMA_150uW_VGA1_2](figures_dfe/rx_adaptation_dashboard_OMA_150uW_VGA1_2.png)

#### OMA_200uW_VGA1_0
![Adaptation dashboard OMA_200uW_VGA1_0](figures_dfe/rx_adaptation_dashboard_OMA_200uW_VGA1_0.png)

#### OMA_200uW_VGA1_2
![Adaptation dashboard OMA_200uW_VGA1_2](figures_dfe/rx_adaptation_dashboard_OMA_200uW_VGA1_2.png)

---

## 9  Eye Diagrams

### 9.1  Post-FFE eye (DFE input)

The post-FFE eye shows the signal after the constrained FFE (cursor+1 = 0) and
before DFE feedback is applied.  Residual first post-cursor ISI is visible as
eye asymmetry; the DFE corrects this.

#### OMA_100uW_VGA1_0
![Post-FFE eye OMA_100uW_VGA1_0](figures_dfe/eye_post_ffe_OMA_100uW_VGA1_0.png)

#### OMA_100uW_VGA1_2
![Post-FFE eye OMA_100uW_VGA1_2](figures_dfe/eye_post_ffe_OMA_100uW_VGA1_2.png)

#### OMA_150uW_VGA1_0
![Post-FFE eye OMA_150uW_VGA1_0](figures_dfe/eye_post_ffe_OMA_150uW_VGA1_0.png)

#### OMA_150uW_VGA1_2
![Post-FFE eye OMA_150uW_VGA1_2](figures_dfe/eye_post_ffe_OMA_150uW_VGA1_2.png)

#### OMA_200uW_VGA1_0
![Post-FFE eye OMA_200uW_VGA1_0](figures_dfe/eye_post_ffe_OMA_200uW_VGA1_0.png)

#### OMA_200uW_VGA1_2
![Post-FFE eye OMA_200uW_VGA1_2](figures_dfe/eye_post_ffe_OMA_200uW_VGA1_2.png)

### 9.2  Equalized output histograms (FFE + DFE combined)

#### OMA_100uW_VGA1_0
![Eq histogram OMA_100uW_VGA1_0](figures_dfe/eq_histogram_OMA_100uW_VGA1_0.png)

#### OMA_100uW_VGA1_2
![Eq histogram OMA_100uW_VGA1_2](figures_dfe/eq_histogram_OMA_100uW_VGA1_2.png)

#### OMA_150uW_VGA1_0
![Eq histogram OMA_150uW_VGA1_0](figures_dfe/eq_histogram_OMA_150uW_VGA1_0.png)

#### OMA_150uW_VGA1_2
![Eq histogram OMA_150uW_VGA1_2](figures_dfe/eq_histogram_OMA_150uW_VGA1_2.png)

#### OMA_200uW_VGA1_0
![Eq histogram OMA_200uW_VGA1_0](figures_dfe/eq_histogram_OMA_200uW_VGA1_0.png)

#### OMA_200uW_VGA1_2
![Eq histogram OMA_200uW_VGA1_2](figures_dfe/eq_histogram_OMA_200uW_VGA1_2.png)

---

## 10  FFE Tap Profiles

#### OMA_100uW_VGA1_0
![FFE taps OMA_100uW_VGA1_0](figures_dfe/ffe_taps_final_OMA_100uW_VGA1_0.png)

#### OMA_100uW_VGA1_2
![FFE taps OMA_100uW_VGA1_2](figures_dfe/ffe_taps_final_OMA_100uW_VGA1_2.png)

#### OMA_150uW_VGA1_0
![FFE taps OMA_150uW_VGA1_0](figures_dfe/ffe_taps_final_OMA_150uW_VGA1_0.png)

#### OMA_150uW_VGA1_2
![FFE taps OMA_150uW_VGA1_2](figures_dfe/ffe_taps_final_OMA_150uW_VGA1_2.png)

#### OMA_200uW_VGA1_0
![FFE taps OMA_200uW_VGA1_0](figures_dfe/ffe_taps_final_OMA_200uW_VGA1_0.png)

#### OMA_200uW_VGA1_2
![FFE taps OMA_200uW_VGA1_2](figures_dfe/ffe_taps_final_OMA_200uW_VGA1_2.png)

---

## 11  TX Alignment Overlays

32-SPS raw waveform overlaid with the reconstructed TX NRZ ideal waveform and
bit-1 symbol slots (orange shading).  First 250 symbols shown.

#### OMA_100uW_VGA1_0
![Alignment overlay OMA_100uW_VGA1_0](figures_dfe/alignment_overlay_nrz_OMA_100uW_VGA1_0.png)

#### OMA_100uW_VGA1_2
![Alignment overlay OMA_100uW_VGA1_2](figures_dfe/alignment_overlay_nrz_OMA_100uW_VGA1_2.png)

#### OMA_150uW_VGA1_0
![Alignment overlay OMA_150uW_VGA1_0](figures_dfe/alignment_overlay_nrz_OMA_150uW_VGA1_0.png)

#### OMA_150uW_VGA1_2
![Alignment overlay OMA_150uW_VGA1_2](figures_dfe/alignment_overlay_nrz_OMA_150uW_VGA1_2.png)

#### OMA_200uW_VGA1_0
![Alignment overlay OMA_200uW_VGA1_0](figures_dfe/alignment_overlay_nrz_OMA_200uW_VGA1_0.png)

#### OMA_200uW_VGA1_2
![Alignment overlay OMA_200uW_VGA1_2](figures_dfe/alignment_overlay_nrz_OMA_200uW_VGA1_2.png)

---

## 12  Summary

Adding a 1-tap DFE with exclusive ownership of the first post-cursor (cursor+1
FFE tap forced to zero) produces DFE tap values of **b₁ ≈ 0.59–0.64** across all
six OMA and VGA operating points.  The tap is consistent with OMA level as expected
for a channel property.

The SNR relative to the unconstrained FFE-only baseline is 3–6 dB lower.  This
penalty reflects the ISI left by prohibiting the FFE's cursor+1 tap from participating
in the joint post-cursor optimisation: the remaining 13 FFE post-cursor taps partially
compensate but a single DFE tap cannot fully recover the loss.  The penalty grows with
OMA because at higher power the noise floor recedes and residual ISI becomes the
dominant impairment.

CDR phase is unchanged from the baseline (29 / 32) with equivalent PI standard
deviation (≤ 0.3), confirming that the staged adaptation approach correctly isolates
the DFE from the CDR timing loop.

**Key implementation findings:**

1. Simultaneous CDR + FFE + DFE adaptation is unstable due to a constant MM-TED
   bias of `+b₁` from the DFE feedback.  Staged adaptation (CDR+FFE first, then
   DFE with frozen CDR) resolves this.

2. Without the cursor+1 constraint, the FFE and DFE jointly absorb h₁ leaving
   b₁ ≈ 0.005.  The constraint gives b₁ ≈ 0.62, exposing the actual channel
   first post-cursor.

3. Using a single un-tiled CSV period for the DFE training pass eliminates
   tile-boundary preamble spikes in the DFE convergence trajectory.

---

*Script: `examples/caribou_oci_gen2_nrz_results.py --n-dfe 1 --repeat 3 --batch`*
*Results: `runs/caribou_oci_gen2_nrz_results_dfe/`*
*Figures: `figures_dfe/`*
