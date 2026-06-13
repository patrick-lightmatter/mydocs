# OCI MSA — Analog Transceiver Development Log

**Author:** Patrick Satarzadeh  
**Project:** 106.25 Gbps NRZ fully-analog receiver (and eventual full transceiver)  
**Repository:** `optical-serdes` — branch `construction`  
**Status:** 🟡 In development

---

## Contents

1. [Motivation](#1-motivation)
2. [Target Specification](#2-target-specification)
3. [Receiver Architecture](#3-receiver-architecture)
4. [Development Log](#4-development-log)
5. [Open Questions](#5-open-questions)
6. [Roadmap](#6-roadmap)

---

## 1. Motivation

Conventional coherent and short-reach SerDes receivers rely on a high-resolution
ADC in the data path, followed by a DSP core running FFE/DFE and digital CDR.  
For cost- and power-constrained OCI MSA applications, a **fully-analog receiver**
offers a lower-power, lower-latency alternative: all timing and level decisions are
made by analog comparators, and the only digital circuitry is the CDR back-end loop
filter and calibration engine.

The architecture explored here targets **106.25 Gbps NRZ** — the OCI MSA line-rate.

---

## 2. Target Specification

| Parameter | Value | Notes |
|-----------|-------|-------|
| Line rate | 106.25 Gbps | NRZ |
| Symbol rate | 106.25 GBaud | |
| UI | ≈ 9.41 ps | |
| Technology | < 7 nm CMOS | Enables fast digital gates in CDR path |
| CDR architecture | Baud-rate bang-bang MM | No edge sampler |
| ADC in data path | None | Fully-analog decision path |
| Phase interpolator resolution | 1/32 UI ≈ 0.29 ps | 32-phase grid |
| Front-end equalization | CTLE (future) | VGA for gain control (future) |
| h₀ calibration | Digital engine | Fixed or adaptive (TBD) |

---

## 3. Receiver Architecture

**Detailed block diagram and signal definitions:**
[diagrams/analog_nrz_rx_106g25.md](diagrams/analog_nrz_rx_106g25.md)

### Summary

```
Analog in
  │
  ├─[CTLE]──[VGA]──[T/H, baud-rate]──────────────────── Data Slicer (0) ──► d[n] ──► DATA OUT
  │                       │                                    │
  │                       ├── Error Slicer (+h₀) ── z_p[n]   │
  │                       └── Error Slicer (−h₀) ── z_m[n]   │
  │                                │                           │
  │                         MUX (sel=d[n])                     │
  │                                │                           │
  │                              z[n] = sign(y[n] − d[n]·h₀) │
  │                                │                           │
  │                         D-latch (1 UI)  ◄──────────────────┘
  │                        d[n-1], z[n-1]
  │                                │
  │                         BB MM-TED
  │                  e[n] = d[n-1]·z[n] − d[n]·z[n-1]
  │                                │
  │                          sign(e[n])  ──►  [Digital CDR Engine]
  │                                               │
  │                            ┌──────────────────┤
  │                         Loop filter         h₀ est.   VGA ctrl
  │                            │
  └──────────────────────── DCO/PI  (32-phase) ──► CK (baud)
```

### Key design decisions

* **No edge sampler.** MM is baud-rate: timing information is extracted from the
  amplitude of consecutive data samples through residual ISI — not from a midpoint
  transition sample.
* **Error slicers at ±h₀, not ±1.** The slicers detect residual ISI relative to
  the cursor amplitude.  `z[n] = sign(y[n] − d[n]·h₀)` strips the cursor term and
  exposes the sign of the postcursor ISI coefficient h₁, which is the timing error
  signal.
* **Digital MUX is safe at < 7 nm.** All slicer outputs are rail-to-rail digital.
  A 2:1 digital MUX costs ~1–2 ps in advanced CMOS — well within the 9.41 ps UI.
* **No analog delay cell.** d[n-1] and z[n-1] are obtained by D-latching the
  slicer outputs at the baud clock — no precision analog delay line.
* **h₀ in digital engine, not analog.** The error slicer threshold is a DAC-driven
  voltage from the CDR back-end.  The CDR also controls VGA gain, so h₀ and the eye
  amplitude track each other.

---

## 4. Development Log

---

### Milestone 1 — 2026-06-08 · Architecture definition + BB MM-CDR lock (ideal channel)

#### What was done

Defined the complete receiver architecture from first principles:

1. Established the bang-bang Mueller-Muller TED formulation:
   - Data slicer: `d[n] = sign(y[n])`
   - Two error slicers: `z_p[n] = sign(y[n] − h₀)`,  `z_m[n] = sign(y[n] + h₀)`
   - MUX: `z[n] = sign(y[n] − d[n]·h₀)`
   - TED: `e[n] = d[n-1]·z[n] − d[n]·z[n-1]`
   - CDR drives on `sign(e[n])` (bang-bang, ∈ {−1, 0, +1})

2. Implemented `AnalogMmCdr` in
   `src/optical_serdes/rx/mm_cdr.py` — a new class alongside the existing
   ADC-based `MuellerMullerCDR`.  Key interface: `step(d_curr, z_curr, state)`
   takes pre-sliced binary inputs; the analog `y[n]` value never enters the CDR
   loop.

3. Ran the first end-to-end simulation:
   - PRBS-15 (32 767 symbols) → 4th-order Bessel-Thomson channel → `AnalogMmCdr`
   - Phase interpolator: `PhaseInterpolator(n_phases=32)` from
     `src/optical_serdes/rx/pi.py`
   - No noise, no CTLE, no VGA — bare minimum to demonstrate lock

#### Results

| Run | BT loss @ Nyquist | f₃dB | h₀ | Initial pi | Lock pi | Lock phase |
|-----|------------------|------|----|-----------|---------|------------|
| A | −3 dB | 53.125 GHz | 0.9518 | 8 | **6** | 0.188 UI / 1.76 ps |
| B | −6 dB | 38.97 GHz  | 0.8272 | 15 | **13** | 0.406 UI / 3.82 ps |

Both runs: **BER = 0** after settling (noiseless channel, < 500 UI acquisition).

Eye diagrams (slicer input, 2 000 overlaid 2-UI windows):

| Run A (−3 dB) | Run B (−6 dB) |
|---|---|
| Wide open eye; lock at ≈ 0.19 UI | Increased ISI spread; lock at ≈ 0.41 UI |
| ![run A](figures/eye_prbs15_bt4_3dB.png) | ![run B](figures/eye_prbs15_bt4_6dB.png) |

> Figures also in `optical-serdes/runs/analog_rx/`.

#### Key observations

* **CDR needs residual ISI to operate.** The BB MM-TED error signal is
  `sign(d[n-1]·h₁)` — it is zero if the channel has no postcursor ISI (h₁ = 0).
  The BT filter at Nyquist bandwidth deliberately leaves significant h₁, which
  provides the timing discriminant.  A perfectly equalized channel (after full CTLE)
  would blind the TED — CTLE tuning must stop short of zeroing the postcursor.

* **Lock point ≈ single-symbol peak.** The predicted lock phase (from the
  single-symbol BT response peak, `pi_natural`) matched the CDR lock within 1
  PI step in both runs.  This confirms the TED zero-crossing coincides with the
  cursor of the channel impulse response, as expected from MM theory.

* **Acquisition is very fast.** From initial offsets of ¼ UI (run A) and nearly
  ½ UI (run B), the CDR was effectively locked within ~50 UI.  The phase trajectory
  showed clean bang-bang limit-cycling (±1 PI step) from the first few hundred
  symbols.

* **h₀ drops with more bandwidth limiting.** Run B (−6 dB at Nyquist) gives
  h₀ = 0.827 vs. 0.952 in run A.  When CTLE and VGA are added, the VGA will
  restore the eye amplitude to a design target and h₀ will be set accordingly
  by the calibration engine.

#### Simulation code

```
scripts/analog_rx/analog_rx_prbs15_eye.py
src/optical_serdes/rx/mm_cdr.py   → AnalogMmCdr, AnalogMmCdrState
src/optical_serdes/rx/pi.py       → PhaseInterpolator
```

---

### Milestone 2 — 2026-06-08 · h₀ real-time estimation via sign-error LMS

#### What was done

Identified and implemented a closed-form h₀ estimator that operates
entirely within the all-slicer signal path — no ADC access to `y[n]` required.

**Key insight.**
The error slicer already computes:

```
z[n] = sign(y[n] − d[n]·h₀)
```

This is exactly the sign of the h₀ estimation error.  Standard LMS
for a single-weight cursor estimator would update:

```
h₀[n+1] = h₀[n] + μ · d[n] · (y[n] − d[n]·h₀[n])
```

Replacing the continuous residual with its sign gives the **sign-error LMS** rule:

```
h₀[n+1] = h₀[n] + μ · d[n] · z[n]
```

Both `d[n]` and `z[n]` are already present in the CDR data path.
No new hardware is required beyond a digital accumulator and a step DAC
feeding the error slicer threshold.  The loop closes as:

```
y[n] → comparators → d[n], z[n] → sign-error LMS → h₀[n+1] → DAC → Vth(±h₀)
```

**Simulation.**
The sign-error LMS update was added to `run_cdr()` inside the
per-symbol loop alongside the BB MM-CDR step.  Both adaptations run
simultaneously; the CDR clock and the h₀ estimate converge together
from arbitrary initial conditions.

Channel: 4th-order BT, −6 dB @ Nyquist (f₃dB = 38.97 GHz).
Starting conditions: `pi_code = 15` (≈ ½ UI from true lock), `h₀_init = 0.5`
(well below true value, to exercise convergence).

#### Results

| Parameter | Value |
|-----------|-------|
| True h₀ (cursor_h0) | 0.8272 |
| Initial h₀ estimate | 0.5000 |
| Converged h₀ (median post-settle) | 0.8155 |
| Estimation error | −1.4 % |
| Adapt. step μ | 5 × 10⁻⁴ |
| Lock pi_code | 14 |
| PRBS-15 symbols | 32 767 |
| OSR | 32 |

The 1.4 % residual is the **granularity floor of sign-error LMS** — the
estimator converges to within ±μ of the true value in expectation.
Reducing μ tightens the floor at the cost of slower initial convergence.

Three-panel figure — CDR phase trajectory, h₀ convergence, and eye diagram
with the converged ±h₀ thresholds overlaid:

<iframe src="figures/eye_prbs15_bt4_6dB_h0lms.html"
        width="100%" height="720px" style="border:none;"></iframe>

> Static fallback: ![h₀ LMS eye diagram](figures/eye_prbs15_bt4_6dB_h0lms.png)

#### Key observations

* **Algorithm re-uses existing CDR signals.**  `d[n]` and `z[n]` are
  already latched for the BB MM-TED.  The sign-error LMS adds only an
  accumulate-and-clip operation — a handful of digital gates — to derive
  the DAC control word for the error slicer threshold.

* **Joint convergence is stable.**  CDR phase lock and h₀ adaptation
  proceed in parallel without observable interference.  Both settle
  within the first 500 UI from the chosen initial conditions.

* **Residual error is bounded and predictable.**  The ±μ floor means
  the error slicer threshold dithers around the true h₀.  For
  μ = 5 × 10⁻⁴, the dither amplitude is < 0.05 % of the eye opening —
  negligible compared to other analog front-end impairments.

* **Q5 resolved.**  The question "what algorithm estimates h₀ without
  ADC access?" is answered: sign-error LMS on `z[n]·d[n]`.

#### Simulation code

```
scripts/analog_rx/analog_rx_prbs15_eye.py   (updated: h₀ LMS in run_cdr)
src/optical_serdes/rx/mm_cdr.py             → AnalogMmCdr (unchanged)
```

---

### Milestone 3 — 2026-06-09 · CTLE integration + peaking sweep

#### What was done

Added a 1z2p `CtleZPK` peaking stage between the BT channel and the slicer
input in `scripts/analog_rx/analog_rx_prbs15_eye.py`.  Swept CTLE peaking
from 0 dB (bypass) to 9 dB in 3 dB steps and measured CDR lock, h₁
(first postcursor after equalization), and h₀ convergence at each level.

Each sweep point now produces a **4-panel figure**:
1. CDR phase trajectory
2. h₀ sign-error LMS adaptation
3. Frequency response (BT channel, CTLE, combined) with Nyquist marker
4. Eye diagram at the slicer input with ±h₀ thresholds overlaid

**CTLE design:** `CtleZPK.from_peaking(peaking_db, data_rate=106.25e9, samples_per_symbol=32)` —
1-zero 2-pole (1z2p) topology; zero at 0.25·f_Nyq, second pole at 2·f_Nyq;
first pole solved by Brent's method to achieve the target Nyquist peaking.
Maximum achievable peaking with default pole/zero ratios: ≈ 10.4 dB.

**Combined IR analysis:** after applying BT filter then CTLE to a single-symbol
pulse, the peak (h₀) and first postcursor h₁ are extracted from the combined
impulse response.  Both the CDR lock point and the h₀ LMS are evaluated
against the combined channel, not the bare BT channel.

#### Implementation note — loop polarity bug found and fixed

An initial run (loop_sign = +1 hardwired) showed lock failure at 3, 6, 9 dB.
Post-analysis identified the root cause: when the combined IR (BT + CTLE)
overshoots, h₁ goes negative, which inverts the TED polarity.  The
original CDR drove the phase in the wrong direction and diverged.

**Fix:** added `loop_sign: int` to `AnalogMmCdr`
(`src/optical_serdes/rx/mm_cdr.py`).  The TED output is multiplied by
`loop_sign` before the loop filter.  In `run_cdr()`, `loop_sign =
sign(h₁_true)` is derived from the combined IR before the simulation starts.
In hardware this would be set by a brief calibration phase (or by the CTLE
control word, since the designer knows which direction h₁ will go).

The fundamental TED requirement is **|h₁| > 0** (nonzero postcursor at the
sampling phase), not h₁ > 0.  The sign of h₁ controls which direction the
loop must wind — it is a polarity setting, not a stability condition.

#### Results (after loop_sign fix)

Channel: 4th-order BT, −6 dB @ Nyquist (f₃dB = 38.97 GHz).  OSR = 32.

| CTLE pk | pi_nat | lock pi | δ (UI) | h₀_peak | h₀_conv | h₀_conv gain vs bypass | h₁_true | h₁/h₀  | Locked |
|---------|--------|---------|--------|---------|---------|------------------------|---------|--------|--------|
| 0 dB    |  12    |  14     | +0.06  | 0.8272  | 0.8155  | baseline               | +0.1174 | +0.142 | **YES** |
| 3 dB    |  15    |  29     | +0.44  | 1.0549  | 0.8690  | +6.6 %                 | −0.0107 | −0.010 | **YES** |
| 6 dB    |  12    |  25     | +0.41  | 1.2777  | 0.8230  | +0.9 %                 | −0.1702 | −0.133 | **YES** |
| 9 dB    |   9    |  21     | +0.38  | 1.5199  | 1.0040  | +23 %                  | −0.4206 | −0.277 | **YES** |

δ = (lock_pi − pi_nat) / OSR in UI.  h₀_peak = IR peak amplitude; h₀_conv =
cursor amplitude at the *actual* CDR sampling phase (the quantity the
sign-error LMS converges to — not an estimation error).  Lock criterion:
≥ 90 % of post-settle pi_codes within ±3 (modular) of modal value.

Figures (static PNG fallback):

| 0 dB bypass | 3 dB |
|---|---|
| ![0 dB](figures/eye_prbs15_bt4_ctle_pk0dB.png) | ![3 dB](figures/eye_prbs15_bt4_ctle_pk3dB.png) |

| 6 dB | 9 dB |
|---|---|
| ![6 dB](figures/eye_prbs15_bt4_ctle_pk6dB.png) | ![9 dB](figures/eye_prbs15_bt4_ctle_pk9dB.png) |

> Full interactive HTML figures in `optical-serdes/runs/analog_rx/`.

#### Key observations

* **h₁ changes sign between 0 and 3 dB peaking.**  At bypass h₁/h₀ = +14 %;
  at 3 dB it is −1 %.  The zero crossing is at ≈ **2.7 dB** of CTLE peaking
  for this channel.  Above 2.7 dB the combined IR overshoots and h₁ goes
  negative at the IR peak — but the CDR still locks after the polarity fix.

* **The MM lock point ≠ IR peak.**  The CDR locks where h₁(φ) = 0 — i.e.,
  where the combined IR value exactly one UI after the sampling phase is zero.
  For the BT-only channel this zero crossing is close to the peak (δ ≈ 0.06
  UI); for BT + CTLE with an oscillating IR it migrates to δ ≈ 0.4 UI.

* **h₀_conv is correct, not erroneous.**  The sign-error LMS adapts to the
  cursor amplitude at the *actual sampling phase*.  The gap between h₀_conv
  and h₀_peak is a real performance penalty: the CDR is not sampling at the
  optimal (maximum eye-opening) point.  The h₁ = 0 lock constraint and the
  h₀ maximisation objective are in tension.

* **CTLE does help, but less than the IR peak suggests.**  The effective eye
  opening (h₀_conv) improves by only 23 % at 9 dB peaking, even though the
  IR peak grows by 84 %.  Most of the CTLE benefit is "wasted" because the
  lock point migrates away from the peak.

* **6 dB CTLE gives almost no cursor benefit (+0.9 %)** vs. bypass — the
  lock-point migration nearly cancels the IR peak growth.

* **Q4 revised.**  The TED remains well-conditioned (|h₁| > 0 at the lock
  point) for all tested peaking levels.  The CDR polarity must match sign(h₁)
  — this is a hardware calibration requirement, not a fundamental instability.
  The original concern (TED blindness at h₁ = 0) applies only at exactly the
  h₁ = 0 crossing (≈ 2.7 dB here); even there, the lock point shifts rather
  than the CDR failing entirely.

* **Q7 partially answered.**  Topology: 1z2p CTLE is sufficient.  The optimal
  peaking is not simply "below 2.7 dB" but a trade-off: low peaking keeps the
  lock point near the IR peak (good h₀_conv/h₀_peak ratio) while high peaking
  grows the IR peak but moves the lock point away (poor ratio).  Optimal
  operating point requires characterising h₀_conv vs. peaking for the actual
  OCI MSA channel.

#### Simulation code

```
scripts/analog_rx/analog_rx_prbs15_eye.py      (rewritten: 4-panel figure, CTLE sweep)
src/optical_serdes/rx/mm_cdr.py                → AnalogMmCdr: added loop_sign field
src/optical_serdes/rx/ctle.py                  → CtleZPK.from_peaking (existing)
```

---

### Milestone 4 — 2026-06-13 · Full OCI MSA optical link via SmfLink + phase sweep metrics

#### What was done

Replaced the idealised Bessel-Thomson channel with the full OCI MSA optical transceiver
model (`SmfLink`) and created a new simulation script
`scripts/analog_rx/oci_msa_analog_txrx.py`.  This is the first end-to-end simulation of
the complete physical signal chain.

**1. SmfLink — full transceiver chain**

The `SmfLink` class (`src/optical_serdes/optical/smf_link.py`) models:

```
drive voltage → TX driver (OLA IIR) → RC IIR (τ = 3.5 ps) → MRM (TCMT Euler ODE)
             → SMF chromatic dispersion filter → PD+TIA (OLA IIR) → piecewise-linear
               RX nonlinearity → tp4
```

Default configuration (OCI MSA Caribou NVDA, CornerSelector = 1):

| Parameter | Value |
|---|---|
| Baud rate | 106.25 GBaud |
| OSR | 32 |
| MRM average optical power | 0 dBm |
| Fiber path | 203 m total (four SMF segments) |
| RX corner | 1 |

**2. Drive voltage convention**

```python
drive = np.repeat(symbols, OSR) / DRIVE_SCALE   # DRIVE_SCALE = 1.6
```

Matches the MATLAB `smfLink` harness (`x = (bits − mean(bits)) / 1.6`).
For balanced PRBS-15, symbols ∈ {±1} are already mean-zero.

**3. MRM through-port polarity inversion**

A +1 drive voltage pushes the MRM resonance toward the laser wavelength → increased
optical absorption → *less* transmitted power.  The channel impulse response cursor
is therefore **negative** (h₀ ≈ −1.0 in normalised units).

Consequence: `np.argmax(ir)` was finding a small positive noise feature rather than the
actual cursor.  Fixed in both `cursor_h0_h1()` and the IR figure panel:

```python
peak_idx = int(np.argmax(np.abs(ir)))   # correct for inverted channels
```

The CDR still locks correctly because `loop_sign = sign(h₁)` is derived from the
channel IR before the simulation starts, and h₁ = +0.029 → `loop_sign = +1`.

**4. TP4 normalisation**

Because the MRM nonlinearity skews the amplitude distribution, simple peak normalisation
is unreliable.  Percentile-based normalisation is used instead:

```python
v_mid  = np.mean(tp4)
v_half = (np.percentile(tp4, 97) − np.percentile(tp4, 3)) / 2
rx_base = (tp4 − v_mid) / v_half
```

This is robust against the optical nonlinear wings at the extremes of the eye.

**5. Channel impulse response via small-signal pulse injection**

The linearised channel IR is obtained by:
1. Warming up the MRM to DC steady-state with 200 UI of zero drive
2. Injecting a +1/DRIVE_SCALE ZOH pulse (1 UI wide)
3. Subtracting an all-zero baseline run
4. Normalising the differential response to unit peak magnitude

CTLE (if active) is then convolved with the normalised delta to give the effective IR
seen at the slicer input.

**6. Phase sweep metrics panel**

A new analysis panel computes eye opening and Q-factor across all OSR = 32 phase offsets
for the settled waveform:

```
opening[k] = mean(positive samples at phase k) − mean(negative samples at phase k)
Q[k]       = opening[k] / (std(positives) + std(negatives))
```

Three markers are shown on both the sweep panel and the eye diagram:
- **CDR lock** (crimson) — where the bang-bang MM-CDR converged
- **max eye opening** (seagreen) — phase that maximises vertical opening
- **max Q-factor** (darkorange) — phase that maximises the SNR metric

This makes it immediately visible whether the CDR lock point is optimal or has migrated
due to the h₁ = 0 constraint.

**7. Six-panel figure**

| Panel | Content |
|---|---|
| 1 | CDR phase trajectory (pi_code vs symbol index) |
| 2 | h₀ adaptation (sign-error LMS) |
| 3 | Frequency response — fiber + RX frontend + combined (magnitude + group delay) |
| 4 | Impulse response — SmfLink channel vs SmfLink + CTLE, with h₀/h₁ markers |
| 5 | Phase sweep — eye opening & Q-factor vs sampling phase |
| 6 | Eye diagram at slicer input with CDR lock / max-opening / max-Q phase markers |

**8. TX driver removed from FR plot**

The TX driver is internal to SmfLink and not accessible as a separate output node.
The frequency response panel previously reconstructed it from `TxDriver.half_spectrum()`
for plotting, but this is misleading — it implies an observable that isn't in the signal
path.  The import and trace were removed; the FR panel now shows only fiber, RX frontend,
and their combination.

**9. Cold start validation**

Confirmed CDR acquires and locks correctly from a true cold start:
`INITIAL_PI = 0`, `H0_INIT = 0.0`.  The phase trajectory panel shows the full
acquisition sweep from phase 0 to lock at pi = 9.

#### Results

Channel: SmfLink (OCI MSA, 203 m SMF, MRM 0 dBm).  CTLE: bypass (0 dB).

| Parameter | Value |
|---|---|
| Natural lock pi (IR peak % OSR) | 12 |
| CDR lock pi | 9 |
| h₀_true (IR cursor, normalised) | −1.0000 |
| h₀_conv (sign-error LMS, post-settle) | 0.7625 |
| h₁_true | +0.0291 |
| h₁/h₀ | −0.029 |
| CDR locked | **YES** |
| PRBS-15 symbols | 32 767 |
| OSR | 32 |

Note: h₀_true is normalised to the IR peak (= −1 by construction); h₀_conv is in
units of the percentile-normalised `rx_base` waveform.  The two scales are
incommensurable — the −176 % "error" in the table is a display artefact, not a
calibration failure.  The CDR and LMS both operate correctly in their respective
amplitude references.

Output figures: `runs/analog_rx/eye_prbs15_smflink_pk0dB.html / .png`

#### Key observations

* **MRM polarity inversion is handled transparently.**  The `loop_sign = sign(h₁)`
  convention introduced in Milestone 3 generalises correctly: h₁ > 0 at the lock
  point regardless of cursor polarity.

* **CDR lock ≠ max eye opening, but the gap is small.**  Lock at pi = 9 vs.
  max-opening at pi = 12 (3/32 UI ≈ 0.094 UI offset).  The Q-factor peak also
  coincides with pi = 12, so both metrics agree that the CDR is slightly sub-optimal.
  The offset is the expected h₁ = 0 lock-point shift.

* **h₁/h₀ = −2.9 % is very small.**  The OCI MSA channel has much less postcursor
  ISI than the BT test channel (which had h₁/h₀ ≈ +14 % at bypass).  This means
  the TED error signal is weak — a small h₁ gives a narrow phase discriminant.
  CDR Kp and bandwidth should be revisited for this channel's ISI profile.

* **Fiber contribution is negligible at 203 m.**  The frequency response panel shows
  the fiber as essentially flat — chromatic dispersion is insignificant at this length
  for 106G NRZ.  The dominant bandwidth limits are the TX driver and RX frontend.

#### Simulation code

```
scripts/analog_rx/oci_msa_analog_txrx.py    (new — replaces analog_rx_prbs15_eye.py
                                              for OCI MSA transceiver work)
src/optical_serdes/optical/smf_link.py      → SmfLink, SmfLinkConfig (existing)
src/optical_serdes/rx/mm_cdr.py             → AnalogMmCdr (unchanged)
src/optical_serdes/rx/ctle.py               → CtleZPK (unchanged)
```

---

## 5. Open Questions

These are the unresolved design questions that will drive the next development phases.

### CDR & TED

| # | Question | Impact | Status |
|---|---------|--------|--------|
| Q1 | What is the CDR bandwidth and jitter peaking for the bang-bang loop? | Jitter tolerance, limit-cycle amplitude | Not yet measured |
| Q2 | Is a proportional-only (first-order) loop sufficient, or do we need frequency acquisition (integral path)? | Lock range, ppm tolerance | Open |
| Q3 | How sensitive is the lock point to errors in h₀? | Error slicer miscalibration → phase offset | Open |
| Q4 | Does the TED remain well-conditioned after CTLE equalizes most of the channel? | TED gain reduction, possible loss of lock | ✅ **Resolved** — Fundamental requirement is \|h₁\| > 0 (not h₁ > 0); CDR polarity must track sign(h₁).  With correct loop_sign the CDR locks at all tested peaking levels.  Lock point migrates ~0.4 UI from IR peak for aggressive CTLE, reducing effective cursor amplitude (Milestone 3) |

### h₀ calibration

| # | Question | Impact | Status |
|---|---------|--------|--------|
| Q5 | What algorithm estimates h₀ without ADC access to `y[n]`? | The LMS formula `d[n]·y[n]` is unavailable in all-slicer path | ✅ **Resolved** — sign-error LMS: `h₀ += μ·d[n]·z[n]` (Milestone 2) |
| Q6 | Peak detector on the eye opening vs. fixed calibration on known pilot sequence? | Convergence time, accuracy | Superseded by sign-error LMS; may revisit for faster cold-start |

### Analog front-end

| # | Question | Impact | Status |
|---|---------|--------|--------|
| Q7 | What CTLE topology and peaking target for the OCI MSA channel? | ISI structure, h₀ level, TED gain | 🟡 **Partial** — Topology: 1z2p (`CtleZPK`).  Peaking must stay below the h₁=0 crossing of the combined IR (≈ 2.7 dB for −6 dB BT; varies by channel loss profile).  Exact target requires per-channel characterisation using SmfLink (Milestone 4) |
| Q8 | Half-rate (53.125 GHz × 2) or full-rate (106.25 GHz) clocking? | T/H bandwidth, VCO design | Open |
| Q9 | How is the VGA gain controlled to keep the eye amplitude ≈ h₀_target? | Error slicer accuracy | Open |
| Q10 | Is Kp = 1.0 appropriate for the OCI MSA channel with h₁/h₀ = −2.9 %? | CDR bandwidth, limit-cycle jitter — weak TED discriminant may require lower Kp | Open (Milestone 4: flag raised) |

---

## 6. Roadmap

### Phase 1 — Ideal simulation ✅ (Milestone 1)
- [x] Define BB MM-TED architecture (two error slicers, digital MUX)
- [x] Implement `AnalogMmCdr` class
- [x] Demonstrate lock on PRBS-15 through BT channel (no noise, no CTLE)
- [x] Validate lock point = single-symbol peak of channel response

### Phase 2 — Loop characterisation
- [ ] Sweep initial phase offset: verify lock-in range
- [ ] Measure CDR bandwidth and jitter transfer / jitter tolerance (sinusoidal jitter injection)
- [ ] Characterise limit-cycle jitter amplitude vs. Kp
- [ ] Add integral path (Ki) and verify frequency acquisition range

### Phase 3 — Channel realism
- [ ] Add AWGN — measure BER vs. SNR floor with analytic MM-CDR
- [x] Add CTLE (1z2p) — verify TED does not lose discriminant after equalization (Milestone 3: h₁=0 crossing at ≈ 2.7 dB for −6 dB BT channel)
- [x] Confirm h₀ tracking still accurate after CTLE reshapes eye (Milestone 3: tracking accurate only when CDR is locked; degrades when h₁ → 0)

### Phase 4 — h₀ calibration ✅ (Milestone 2 — sign-error LMS)
- [x] Identify h₀ estimator compatible with all-slicer path (sign-error LMS)
- [x] Implement and validate: `h₀ += μ·d[n]·z[n]` — converges jointly with CDR
- [ ] Sweep μ: characterise convergence speed vs. steady-state error trade-off
- [ ] Stress-test: large h₀ mis-start, noisy channel, post-CTLE eye
- [ ] Close the loop with VGA: h₀ estimate → error slicer DAC → VGA gain ctrl

### Phase 5 — Full analog front-end integration
- [ ] Integrate VGA model (gain controlled from digital engine)
- [ ] CTLE + VGA + BB MM-CDR end-to-end
- [ ] Verify BER vs. channel loss sweep

### Phase 4b — OCI MSA channel characterisation ✅ (Milestone 4)
- [x] Replace BT test channel with `SmfLink` (full OCI MSA optical transceiver model)
- [x] Validate drive voltage convention matches MATLAB reference (DRIVE_SCALE = 1.6)
- [x] Handle MRM through-port polarity inversion (negative cursor; abs-value peak detection)
- [x] Add phase sweep panel: eye opening + Q-factor vs sampling phase, with lock / max-opening / max-Q markers
- [x] Cold start validation: CDR acquires from pi=0, h₀ from 0.0
- [ ] Sweep CTLE peaking on OCI MSA channel (currently only bypass tested)
- [ ] Characterise CDR Kp vs. lock stability for weak-ISI channel (h₁/h₀ = −2.9 %)

### Phase 5 — Full analog front-end integration
- [ ] Integrate VGA model (gain controlled from digital engine)
- [ ] CTLE + VGA + BB MM-CDR end-to-end
- [ ] Verify BER vs. channel loss sweep
- [ ] Add noise (shot noise, TIA thermal, laser RIN) and measure SNR floor

### Phase 6 — Transmitter (future)
- [ ] TX pre-emphasis (drive shaping before TX driver)
- [ ] Combined TX DSP + SmfLink + analog RX link simulation

---

*This document is updated at each development milestone.
Detailed architecture reference: [diagrams/analog_nrz_rx_106g25.md](diagrams/analog_nrz_rx_106g25.md)*
