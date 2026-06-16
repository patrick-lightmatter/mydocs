# OCI MSA DSP Receiver Simulation — 106.25 Gbps NRZ

**Script:** `scripts/dsp_rx/oci_msa_dsp_txrx.py`  
**Signal:** NRZ · 106.25 Gbaud · PRBS-31  
**Platform:** OCI MSA (Colossus MRM + SMF optical link)  
**Simulation type:** Full closed-loop TX → channel → DSP RX, noise-swept

---

## 1. Overview

This document describes the end-to-end NRZ receiver simulation for the OCI MSA
platform.  The simulation generates a PRBS-31 bit sequence at the transmitter,
propagates it through a measured S4P electrical channel and a physics-based
silicon-photonic SMF link model (SmfLink), and then recovers the signal with a
digital DSP receiver consisting of a CTLE, baud-rate Mueller-Müller CDR, and an
LMS-adapted FFE.

The simulation is entirely synthetic — no waveform captures are replayed.  This
differs from the earlier Caribou OCI-Gen2 waveform study (in which Virtuoso
captures were used as the RX input) and allows independent control of the noise
floor through `RxAnalogNoise`.

---

## 2. Signal Chain

### 2.1 Transmitter

```
PRBS-31 (500,000 bits)
      │
      ▼
TX FFE (baud-rate FIR, DC-normalised)   ← default: bypass [1.0]
      │
      ▼
×OSR upsample  (OSR = 32)
      │
      ▼
÷ DRIVE_SCALE (1.6 V)  → drive[n]
```

| Parameter | Value |
|---|---|
| Pattern | PRBS-31 (first 500,000 bits of maximal-length sequence) |
| TX FFE | 1-tap bypass by default; configurable |
| Oversampling ratio (OSR) | 32 |
| Drive scale | 1.6 V (normalises the MRM drive voltage) |

The TX FFE is applied as a causal baud-rate FIR filter and normalised to unit DC
gain before upsampling.  A `[1.0]` tap vector is a transparent bypass.

### 2.2 Electrical Channel — S4P

```
drive[n]
      │
      ▼
S4P discrete IR  (IFFT synthesis, measured phase, 128 UI span)
      │
      ▼
drive_through_s4p[n]
```

The S4P file (`l20_il15_rl17_90ohms_100ports_v2.s4p`) is loaded with the
`13_24` port convention (differential, 4-port → 2-port Sdd21 extraction) and
converted to a discrete-time impulse response via inverse FFT at the simulation
sample rate.  The resulting FIR filter is applied to the upsampled drive
waveform by convolution.

| Parameter | Value |
|---|---|
| S4P file | `l20_il15_rl17_90ohms_100ports_v2.s4p` |
| Port convention | `13_24` (differential) |
| IR synthesis | IFFT, measured phase, 128 UI span |
| Peak index (sample delay) | ≈ 915 samples (≈ 28.6 UI at OSR = 32) |

The 28.6 UI bulk delay reflects the electrical substrate / package trace length
and determines where the channel cursor appears in the FFE tap window.

### 2.3 Optical Link — SmfLink

```
drive_through_s4p[n]
      │
      ▼
TX driver (Caribou NVDA corner 1 impulse response)
      │
      ▼
RC pre-filter (τ = 3.5 ps)
      │
      ▼
MRM TCMT modulator  (ring resonator, TCMT Euler ODE)
      │   optical field s_through[n]
      ▼
SMF fiber (group delay dispersion at 1311 nm)
      │   tp3[n]  optical power (W)
      ▼
PD + TIA (Caribou NVDA impulse response)
      │
      ▼
RX nonlinearity (corner 1)
      │
      ▼
tp4[n]   (photocurrent-derived voltage, ~0.078 V half-swing)
```

The `SmfLink` model replicates the MATLAB `smfLink.m` reference exactly
(CornerSelector = 1, no noise sources active).  The chain is deterministic:
RIN, shot noise, and MPI are modelled as flags in `SmfLinkConfig` but are not
wired into the simulation at this stage.

**Noise sources not active in this simulation:**

| Source | Flag | Status |
|---|---|---|
| Relative intensity noise (RIN) | `include_rin` | Declared, not wired |
| Multi-path interference (MPI) | `include_mpi` | Declared, not wired |
| Shot noise | — | Not implemented |
| TIA thermal noise | `RxAnalogNoise` | Injected via ADC noise sweep (§3) |

SmfLink configuration (defaults):

| Parameter | Value |
|---|---|
| MRM avg optical power | 0 dBm |
| Fiber lengths | [1, 1, 200, 1] m (≈ 203 m total) |
| Connector loss | 3 × 0.5 dB |
| Fiber attenuation | 0.4 dB/km |
| Fiber zero-dispersion λ | 1310 nm |
| Center wavelength | 1311 nm |

### 2.4 Polarity Detection

The MRM through-port characteristic produces an inverted signal polarity
(increasing drive voltage → decreasing optical power at through-port → negative
h₀ in the normalised channel IR).  The polarity is detected automatically by
computing the channel impulse response and examining the sign of the peak:

```python
h0, h1, pi_nat = cursor_h0_h1(ir)   # normalised IR peak and first post-cursor
polarity = +1 if h0 >= 0 else -1
tp4_rx = polarity * tp4
```

All runs in this document use the inverted channel (h₀ ≈ −1.0 before CTLE;
h₀ ≈ −1.24 at 6 dB CTLE peaking due to CTLE DC gain).

---

## 3. Receiver Architecture

```
tp4_rx[n]  (OSR = 32 samples/UI)
      │
      ▼
CtleZPK   (zero-pole-gain CTLE, optional peaking)
      │  32 SPS
      ▼
RxAnalogNoise   (AWGN on oversampled waveform, σ = noise_rms)
      │
      ▼
IdealADC   (sample at CDR-selected phase)
      │  1 sample/UI (baud rate)
      ▼
MuellerMullerCDR   (MM-TED + phase interpolator, 32 phases/UI)
      │  baud-rate samples at settled phase
      ▼
RxFFE   (LMS, 2 pre + 1 cursor + 8 post = 11 taps)
      │
      [RxDFE]   (optional, disabled by default)
      │
      ▼
NRZ slicer (threshold = 0)
      │
      ▼
Recovered bits + BER
```

### 3.1 CTLE — `CtleZPK`

The `CtleZPK.from_peaking_with_bw_limit()` factory produces a zero-pole-gain
CTLE matched to a specified Nyquist peaking and 3 dB bandwidth.  Two operating
points are swept:

| Configuration | Peaking | 3 dB BW |
|---|---|---|
| CTLE bypass | 0 dB (pass-through) | — |
| CTLE 6 dB | 6.0 dB at Nyquist | 80 GHz |

At 0 dB peaking, no CTLE object is created and the raw `tp4_rx` signal feeds
the ADC directly.  At 6 dB peaking, the CTLE boosts the high-frequency content
before the CDR sampler, shifting the CDR lock point from 0.156 UI (phase 5/32)
to 0.500 UI (phase 16/32, exact eye centre) by changing the channel phase
response seen by the MM-TED.

The CtleZPK model differs from the earlier Caribou study's 1z2p (`Ctle1z2p`)
in that it is parameterised directly by pole-zero locations with a bandwidth
limit constraint rather than by peaking-db and DC-gain independently.

### 3.2 Noise Injection — `RxAnalogNoise`

AWGN is injected on the **oversampled waveform after the CTLE and before the
CDR sampling phase selection**.  This represents TIA thermal noise referred to
the ADC input: the CDR sees the same noisy waveform as the ADC, so timing
uncertainty from thermal noise is included in the CDR PI jitter.

```python
analog_noise = RxAnalogNoise(ctle_output_rms_v=noise_rms)
```

Each oversampled sample receives an independent Gaussian draw with standard
deviation `noise_rms`.  The baud-rate ADC sample inherits the same σ (one
oversampled sample is selected per UI).

The noise sweep covers:

| σ (mV RMS) | Pre-FFE SNR (approx.) | Expected post-EQ BER range |
|---|---|---|
| 5 mV | ~24 dB | ≪ 1 × 10⁻¹² (ISI-limited) |
| 15 mV | ~14 dB | ~ 10⁻⁶ – 10⁻⁴ |
| 25 mV | ~10 dB | ~ 10⁻³ – 10⁻² |

Pre-FFE SNR is estimated from the tp4 half-swing (~0.078 V):
`SNR ≈ 20 log₁₀(0.078 / σ)`.  Post-FFE SNR is higher due to the FFE's
matched-filter-like integration of the ISI spread.

### 3.3 Ideal ADC

An `IdealADC` samples the (noisy) oversampled waveform at the single phase
index selected by the CDR phase interpolator.  No quantisation noise or
saturation is modelled.  The ADC output is a baud-rate scalar stream.

### 3.4 Mueller-Müller CDR — `MuellerMullerCDR`

The baud-rate MM-TED computes a timing error from consecutive baud samples and
their hard decisions:

```
e[n] = w_post · d[n−1] · x[n]  −  w_pre · d[n] · x[n−1]
```

where `x[n]` is the current ADC sample, `d[n]` is the slicer decision, and
`w_pre`, `w_post` are asymmetric TED weights (both 1.0 in this simulation —
the KNR sweep is used to verify CDR phase alignment analytically).

The loop filter is proportional-integral:

| Parameter | Value |
|---|---|
| Proportional gain kp | 0.05 |
| Integral gain ki | 0.001 |
| Phases per UI | 32 |
| Initial phase | 0 |
| TED signal | `"raw"` (pre-FFE ADC samples) |

`ted_signal="raw"` is essential: using the equalized signal would introduce a
DC bias of `+b₁` from any DFE feedback tap into the MM-TED, destabilising the
loop.

**Lock point.** The CDR lock phase is determined by the joint channel + CTLE
impulse response.  For this channel:
- 0 dB CTLE: locks at phase 5/32 (0.156 UI)
- 6 dB CTLE: locks at phase 16/32 (0.500 UI, eye centre)

The KNR analysis (§6) confirms that the analytical lock point predicted from
the pulse response exactly matches the CDR's settled phase in both cases.

### 3.5 Feed-Forward Equaliser — `RxFFE`

The FFE is a baud-rate transversal FIR filter adapted by LMS:

```
y[n] = Σ_k  w[k] · x[n − k]      k ∈ {−n_post, …, 0 (cursor), …, +n_pre}
```

| Parameter | Value |
|---|---|
| Pre-cursor taps n_pre | 2 |
| Cursor | 1 |
| Post-cursor taps n_post | 8 |
| Total taps | 11 |
| LMS step size μ | 5 × 10⁻⁴ |
| Adaptation starts at | symbol 3,000 |
| Modulation | NRZ |

The 8-tap post-cursor allocation is modest relative to the Caribou study (14
taps) because the S4P channel has a steeper but shorter ISI tail at 106.25
Gbaud.  The large bulk delay (≈ 29 UI from the S4P + SmfLink chain) appears as
a large dominant tap at index 8 in the 11-tap window — the FFE effectively
acts as a fractional delay plus equaliser.

After the 10,000-symbol convergence window the FFE taps are stable.  At 500k
symbols, the LMS is fully converged and the post-EQ SNR reaches 18–19 dB in
the noise-free case.

### 3.6 Decision-Feedback Equaliser — `RxDFE` (optional)

A single-tap or multi-tap DFE is available but disabled by default
(`ENABLE_DFE = False`).  When enabled, the DFE operates simultaneously with
the CDR and FFE via the LMS update rule:

```
y_out[k] = y_ff[k] − Σ_i b_i · â[k−i]
```

where `â[k−i]` are previous hard decisions and `b_i` are adaptive feedback
taps.

**Stability caveat.** When `ted_signal="raw"`, the pre-FFE ADC samples feed
the MM-TED.  In this mode the DFE feedback does not enter the TED path, so
CDR and DFE can adapt simultaneously.  If `ted_signal="equalized"` is used,
simultaneous CDR + DFE adaptation is unstable because each DFE feedback tap
introduces a constant bias of `+b_i` into the TED output; staged adaptation
(CDR + FFE first, then DFE with frozen CDR) is required in that case.

A speculative (loop-unrolled) DFE variant `SpeculativeDfe` is also available
for situations where the critical path through the DFE feedback is timing-
constrained.

---

## 4. Adaptation Methodology

The simulation runs a single continuous adaptive pass over all 500,000 symbols.
CDR and FFE adapt simultaneously from the start; the FFE is gated off for the
first 3,000 symbols to allow the CDR to acquire lock before the equaliser
introduces a time-varying frequency response.

Quality metrics are computed on the settled portion of the output:

```
SETTLE = BER_CONVERGENCE_SKIP = 10,000 symbols
settled_samples = equalized_samples[SETTLE:]
```

This is a simpler methodology than the two-pass (adaptive + frozen) approach
used in the Caribou study.  The tradeoff is that adaptation transients are
included in the first 10k symbols, which are then discarded.  At μ = 5 × 10⁻⁴
the FFE converges within approximately 5k–8k symbols, so the 10k skip is
sufficient.

---

## 5. SNR and BER Estimation

### 5.1 Post-EQ amplitude statistics

The settled equalized samples are split at the NRZ decision threshold (0 in
the FFE's normalised output space):

```
S₁ = { y[n] > 0 },    S₀ = { y[n] ≤ 0 }
μ₁, σ₁ = mean, std of S₁
μ₀, σ₀ = mean, std of S₀
```

The **asymmetric Gaussian BER** formula is used as the primary blind estimator:

```
BER_gaussian = ½ · erfc( (μ₁ − μ₀) / (√2 · (σ₀ + σ₁)) )
```

This generalises the symmetric Q-function `Q((μ₁ − μ₀) / (2σ))` to the case
where the two NRZ levels have different noise variances, which occurs whenever
the pre-FFE ISI residual or TIA thermal noise is not symmetric about the eye
centre.  The optimal asymmetric decision threshold is:

```
V_th = (μ₀ σ₁ + μ₁ σ₀) / (σ₀ + σ₁)
```

The **post-EQ SNR** is defined as:

```
SNR_dB = 20 · log₁₀( (μ₁ − μ₀) / (σ₀ + σ₁) )
```

This is the Q-factor of the NRZ eye expressed in dB, directly related to the
expected BER under the asymmetric Gaussian model.

**Caveat.** The Gaussian assumption underestimates BER when the noise has heavy
tails (pattern-dependent ISI residual, periodic jitter tones, non-linear
crosstalk).  The blind BER estimate should be read as an optimistic lower bound;
the confidence BER bound (§5.3) provides a statistically rigorous upper bound
from the actual error count.

### 5.2 Counted BER

The raw BER is measured by comparing the settled slicer decisions against the
known PRBS-31 reference bit sequence:

```python
result.ber = n_errors / n_compared
```

The comparison uses a cross-correlation alignment over the settling window to
account for the CDR-induced sample offset and the S4P bulk delay.  Polarity
inversion is handled by the pre-simulation negation of `tp4_rx`.

### 5.3 Confidence BER

The confidence BER converts a finite-run error count `k` in `N` compared bits
into a statistically bounded projected BER at a target operating point
(default: 10⁻¹²).

**Stage 1 — Poisson 95% upper bound:**

```
p_U = −ln(0.05) / N          (for k = 0 errors)
p_U = χ²_{0.95, 2(k+1)} / (2N)   (general case)
```

**Stage 2 — Q-function projection to target BER:**

Under Gaussian noise, the BER scales with the normalised eye margin through the
complementary error function.  The projection ratio is:

```
r = erfc⁻¹(2 · p_target) / erfc⁻¹(2 · p_sim)
p_conf = ½ · erfc( erfc⁻¹(2 · p_U) · r )
```

where `p_sim = −ln(0.05) / 3 × 10⁶` is the calibration reference (zero errors
in 3M bits).

At N = 490,000 symbols (500k minus 10k settle) with zero errors:

```
p_U   = −ln(0.05) / 490,000 ≈ 6.11 × 10⁻⁶
p_conf ≈ 4.84 × 10⁻¹¹   (target = 10⁻¹²)
```

**Caveats:**
- The Poisson bound is exact for independent errors and conservative for mildly
  correlated errors.
- The erfc projection from ~10⁻⁶ to 10⁻¹² spans six decades.  Non-Gaussian
  tails (ISI residual, jitter tones) are not captured.
- When noise injection (`RxAnalogNoise`) is active, the confidence BER reflects
  the combined effect of channel ISI and thermal noise.

### 5.4 Timing-jitter bathtub

A waveform-domain bathtub BER is computed from the oversampled post-CTLE
waveform using TIE jitter decomposition (OIF-JITTER methodology):

1. Detect zero crossings in the DC-centred waveform (median removed).
2. Compute TIE = actual crossing time − ideal alternating-pattern crossing time.
3. Decompose TIE into RJ (spectral), DJ (ISI + DCD + periodic), and dual-Dirac
   component.
4. Integrate the jitter PDF via CDF-fold to obtain the bathtub BER vs. sampling
   phase.

**Limitation.** The `pattern_len=2` (alternating-NRZ) assumption used for the
ideal crossing reference is incorrect for PRBS-31 through a 29 UI channel.
Consecutive identical bits (runs of 0s or 1s) create missing crossings that
pollute the TIE histogram.  The bathtub Rj and DJ numbers from this step are
therefore diagnostic only; the post-EQ Gaussian BER (§5.1) and counted BER
(§5.2) are the primary metrics.

---

## 6. KNR Analysis — Analytical CDR Lock Point

The KNR (K-factor Noise Ratio) analysis provides an analytical prediction of
the stable CDR lock phase without running the CDR loop.  It estimates the
pulse response `h[φ, k]` of the channel at each of the 32 sampling phases φ
via cross-correlation of the oversampled waveform against the known reference
symbols, then evaluates the MM-TED timing function:

```
TF[φ] = Σ_k  (w_post · h[φ, k−1] − w_pre · h[φ, k+1]) · h[φ, k]
```

The stable lock points are the zero crossings of TF[φ] with negative slope.
The KNR at each phase quantifies the signal-to-noise ratio of the TED output:

```
KNR[φ] = TF[φ]² / σ²_TED[φ]
```

High KNR at a stable crossing → strong, well-defined lock.  Low KNR → noisy
TED, susceptible to cycle slips.

**Results (noise-free, PRBS-31, 500k symbols):**

| CTLE | Analytical lock | CDR settled | KNR at lock |
|---|---|---|---|
| 0 dB (bypass) | phase 5 (0.156 UI) | phase 5 | 0.958 |
| 6 dB peaking | phase 16 (0.500 UI) | phase 16 | 1.074 |

The perfect agreement between analytical prediction and actual CDR lock
confirms that the MM-TED is operating at the theoretically optimal phase for
both CTLE configurations.

---

## 7. Post-Simulation Analysis Pipeline

After each `run_one()` call the 9-step `analyse_rx_result()` pipeline is
applied (from `src/optical_serdes/rx/rx_analysis.py`):

| Step | Metric | Source |
|---|---|---|
| 1 | Blind BER (asymmetric Gaussian) + post-EQ SNR | `equalized_samples` |
| 2 | CDR lock code, PI jitter std, frequency offset | `pi_code_trajectory` |
| 3 | Counted BER + Poisson upper bound + confidence BER | `result.ber`, `result.n_errors` |
| 4 | Timing-jitter bathtub from oversampled waveform | `post_ctle`, `t_axis` |
| 5 | Final FFE / DFE tap weights | `ffe_taps_final`, `dfe_taps_final` |
| 6 | Channel estimator IR (when enabled) | `channel_est_taps_final` |
| 7 | KNR analysis — analytical vs actual CDR lock | `waveform`, `reference_bits` |
| 8 | Plotly dashboard (HTML + PNG) | all of the above |
| 9 | Text summary | `print_rx_summary()` |

The analysis dashboard (`plot_rx_analysis()`) is a 4-row × 2-col Plotly figure:

| Row | Left panel | Right panel |
|---|---|---|
| 0 | Post-EQ amplitude histogram (log-y, Gaussian fits) | Channel estimator IR |
| 1 | FFE tap convergence (full width) | — |
| 2 | CDR PI code trajectory | MM-TED timing error (500-pt avg) |
| 3 | Bathtub BER vs sampling phase | KNR vs sampling phase |

---

## 8. Noise Sweep — Effect of Input-Referred TIA Noise

The outer loop sweeps `noise_rms` ∈ {5, 15, 25} mV and the inner loop sweeps
`peaking_db` ∈ {0, 6} dB, producing 6 simulation runs.  The key expected trend
is summarised below (noise-free reference shown for context):

| σ (mV) | CTLE pk (dB) | Expected SNR (dB) | Expected BER_gaussian |
|---|---|---|---|
| 0 (ISI only) | 0 | 18.2 | 1.9 × 10⁻¹⁶ |
| 0 (ISI only) | 6 | 18.6 | 5.9 × 10⁻¹⁸ |
| 5 mV | 0 | ~18 | ISI-limited |
| 5 mV | 6 | ~18 | ISI-limited |
| 15 mV | 0 | ~14 | ~10⁻⁶ |
| 15 mV | 6 | ~14 | ~10⁻⁶ |
| 25 mV | 0 | ~10 | ~10⁻³ |
| 25 mV | 6 | ~10 | ~10⁻³ |

At σ = 5 mV the noise floor is below the ISI residual floor so the BER is
unchanged from the noise-free case.  The crossover occurs somewhere between 5
and 15 mV for this channel and equaliser configuration.

The CDR PI jitter standard deviation is expected to increase with σ because
the MM-TED sees a noisier waveform (noise is injected before CDR sampling).
At σ = 25 mV the PI std may exceed the 0.5-code warning threshold.

---

## 9. Configuration Reference

### Script parameters (`scripts/dsp_rx/oci_msa_dsp_txrx.py`)

```python
BAUD_RATE          = 106.25e9      # symbols per second
OSR                = 32            # samples per symbol
DRIVE_SCALE        = 1.6           # TX drive voltage normalisation

PRBS_ORDER         = 31
N_SYMBOLS          = 500_000

TX_FFE_TAPS        = [1.0]         # bypass; set e.g. [0.8, 0.2] for de-emphasis

BW_3DB_HZ          = 80e9
PEAKING_DB_LIST    = [0.0, 6.0]    # dB at Nyquist

CDR_KP             = 0.05
CDR_KI             = 0.001

FFE_N_PRE          = 2
FFE_N_POST         = 8
FFE_MU             = 5e-4
FFE_ENABLE_AFTER   = 3_000

ENABLE_DFE         = False         # set True to enable RxDFE
DFE_N_FB           = 2
DFE_MU             = 2e-4
DFE_ENABLE_AFTER   = 8_000

ENABLE_SPEC_DFE    = False         # set True to use SpeculativeDfe instead
SPEC_DFE_UNROLLED  = 1

NOISE_RMS_V_LIST   = [0.005, 0.015, 0.025]   # V RMS at CTLE output

SETTLE_UI          = 10_000        # BER_CONVERGENCE_SKIP
```

### Channel

```
S4P: /lm/analog/colossus/channels/l20_il15_rl17_90ohms_100ports_v2.s4p
Convention: 13_24 (differential)
SmfLink defaults: fiber 203 m total, MRM 0 dBm, CornerSelector = 1
```

### Outputs

```
runs/dsp_rx/
  eye_prbs31_dsp_pk{N}dB_n{M}mV.html / .png     plot_rx_dashboard
  analysis_prbs31_dsp_pk{N}dB_n{M}mV.html / .png  plot_rx_analysis
```

---

## 10. Comparison with Caribou OCI-Gen2 Waveform Study

The earlier reports (`report.md`, `report_dfe.md`) characterised a real receiver
using Virtuoso waveform captures from 6 OMA × VGA variants of the Caribou
OCI-Gen2 silicon-photonic transceiver.  Key differences:

| Aspect | OCI-Gen2 Waveform Study | DSP RX Simulation (this document) |
|---|---|---|
| RX input | Hardware Virtuoso capture | Synthetic PRBS-31 via SmfLink |
| TX | Known reference bitfile (300k symbols) | PRBS-31 generated in-sim |
| Channel | Embedded in waveform | S4P + SmfLink (explicit) |
| CTLE | 1z2p (Ctle1z2p), pk = 4 dB, G_DC = −3 dB | CtleZPK, pk ∈ {0, 6} dB |
| FFE | 5 + 1 + 14 = 20 taps, μ = 0.01 | 2 + 1 + 8 = 11 taps, μ = 5 × 10⁻⁴ |
| CDR kp | 0.01 | 0.05 |
| TED weights | w_pre = 0.9, w_post = 1.0 | w_pre = w_post = 1.0 |
| Noise | None (hardware noise floor in waveform) | Explicit AWGN sweep via RxAnalogNoise |
| Adaptation | Two-pass (adaptive + frozen) | Single-pass, settled region |
| Symbol count | ~131k adaptive + ~43k frozen | 500k single pass |
| CDR lock (OCI-Gen2) | Phase 29/32 (0.906 UI) | Phase 5/32 (pk=0) or 16/32 (pk=6) |

The SNR values from the two studies are not directly comparable.  In the
waveform study, the noise floor is set by real hardware thermal noise (TIA,
ADC, etc.) and the post-FFE SNR of 15–19 dB reflects the true link budget at
the operating OMA.  In the DSP RX simulation, the noise-free post-FFE SNR of
~18 dB is entirely ISI residual; adding σ = 15 mV of thermal noise brings the
SNR into the range observed in the hardware study.

The DFE study (`report_dfe.md`) established that the Caribou OCI-Gen2 channel
has a strong first post-cursor (DFE b₁ ≈ 0.60–0.64) and requires a full 14-tap
post-cursor FFE to manage the multi-UI ISI tail.  The Colossus S4P channel used
in this simulation has a shorter effective ISI span (well captured by 8 post-
cursor taps) due to its different dispersion profile.

---

*Script: `scripts/dsp_rx/oci_msa_dsp_txrx.py`*  
*Results: `runs/dsp_rx/`*  
*Framework: `src/optical_serdes/`*
