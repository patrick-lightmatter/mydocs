# 106.25G NRZ Fully-Analog Receiver — Block Diagram

**Author:** Patrick Satarzadeh

---

## Architecture Overview

Baud-rate sampled, bang-bang Mueller-Muller CDR.  No edge samplers.
All signal decisions are made by analog comparators (slicers); the CDR loop filter,
h₀ estimator, and VGA controller live in a digital back-end engine.

```
                                                  ┌─────────────────────────────────────────────────────┐
                                                  │              DIGITAL CDR ENGINE                      │
                                                  │                                                       │
                                                  │  ┌─────────────┐   ┌───────────────┐                │
                                                  │  │  Loop Filter │──►│  DCO / PI     │──► CK (baud)  │
                                                  │  │  (IIR / PI) │   └───────────────┘               │
                                                  │  └──────▲──────┘                                    │
                                                  │         │ sign(e[n])                                 │
                                                  │  ┌──────┴──────┐                                    │
                                                  │  │ h₀ estimator│──► ±Vth (error slicer thresholds)  │
                                                  │  └─────────────┘                                    │
                                                  │  ┌─────────────┐                                    │
                                                  │  │  VGA ctrl   │──► Gain word                       │
                                                  │  └─────────────┘                                    │
                                                  └─────────────────────────────────────────────────────┘
                                                            ▲
                                                            │ sign( e[n] )
                                                            │
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                ANALOG FRONT-END + BB MM-TED                                           │
 │                                                                                                        │
 │  NRZ in                                                                                                │
 │   │                                                                                                    │
 │   ▼                                                                                                    │
 │  ┌──────┐    ┌─────┐    ┌────────────────┐                                                            │
 │  │ CTLE │───►│ VGA │───►│  T/H  (baud)   │◄── CK (baud, from DCO/PI)                                │
 │  └──────┘    └─────┘    └───────┬────────┘                                                            │
 │                                 │                                                                      │
 │              ┌──────────────────┼──────────────────────┐                                              │
 │              │                  │                       │                                              │
 │              ▼                  ▼                       ▼                                              │
 │      ┌──────────────┐  ┌─────────────────┐   ┌──────────────────┐                                    │
 │      │ DATA SLICER  │  │  ERROR SLICER + │   │  ERROR SLICER −  │                                    │
 │      │   Vth = 0    │  │   Vth = +h₀     │   │   Vth = −h₀      │                                    │
 │      └──────┬───────┘  └────────┬────────┘   └────────┬─────────┘                                    │
 │             │                   │                      │                                               │
 │           d[n]               z_p[n]                 z_m[n]                                            │
 │      = sign(y[n])    = sign(y[n] − h₀)      = sign(y[n] + h₀)                                        │
 │             │                   │                      │                                               │
 │             │             ┌─────┴──────────────────────┘                                              │
 │             │             │          MUX (select by d[n])                                             │
 │             │             │  z[n] = d[n]=+1 ? z_p[n] : z_m[n]                                        │
 │             │             │       = sign( y[n] − d[n]·h₀ )                                            │
 │             │             └──────────────┬──────────────                                              │
 │             │                            │                                                             │
 │             │                          z[n]                                                            │
 │             │                            │                                                             │
 │             ├────────────────────────────┤                                                             │
 │             ▼                            ▼                          DATA OUT                           │
 │      ┌─────────────┐           ┌─────────────┐                        ▲                               │
 │      │   D-LATCH   │           │   D-LATCH   │         d[n] ──────────┴──────────────────────────►   │
 │      │    1 UI     │           │    1 UI     │                                                         │
 │      └──────┬──────┘           └──────┬──────┘                                                        │
 │             │                         │                                                                │
 │           d[n-1]                    z[n-1]                                                             │
 │             │                         │                                                                │
 │             └──────────┬──────────────┘                                                               │
 │                        ▼                                                                               │
 │             ┌──────────────────────────────────┐                                                      │
 │             │           BB MM-TED              │                                                       │
 │             │                                  │                                                       │
 │             │  e[n] = d[n-1]·z[n] − d[n]·z[n-1]│                                                     │
 │             │                                  │                                                       │
 │             │  out = sign(e[n])  ∈ {−1, 0, +1} │                                                      │
 │             └──────────────────────────────────┘                                                      │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Signal Definitions

| Symbol | Expression | Source |
|--------|-----------|--------|
| `y[n]` | Analog T/H output at sample n | T/H sampler |
| `d[n]` | `sign(y[n])` | Data slicer, Vth = 0 |
| `z_p[n]` | `sign(y[n] − h₀)` | Positive error slicer, Vth = +h₀ |
| `z_m[n]` | `sign(y[n] + h₀)` | Negative error slicer, Vth = −h₀ |
| `z[n]` | `sign(y[n] − d[n]·h₀)` | MUX output: `z_p` if `d[n]=+1`, `z_m` if `d[n]=−1` |
| `d[n-1]` | `d[n]` delayed 1 UI | D-latch on d[n] |
| `z[n-1]` | `z[n]` delayed 1 UI | D-latch on z[n] |
| `e[n]` | `d[n-1]·z[n] − d[n]·z[n-1]` | BB MM-TED output |

All signals entering the TED are ternary `{−1, 0, +1}`.  The TED combinational
logic can be implemented with a small number of gates or a pair of Gilbert-cell
multipliers followed by a subtractor comparator.

---

## Block-by-Block Description

### CTLE
Continuous-time linear equalizer.  Peaking frequency ≈ f_baud/2 = 53.125 GHz.
Compensates high-frequency channel roll-off.

### VGA
Variable gain amplifier.  Gain set by the digital CDR engine so the T/H sees an
eye amplitude of approximately h₀.  This ties the analog gain to the same h₀
reference used by the error slicer.

### T/H — Track-and-Hold
Samples the equalized waveform once per UI (≈ 9.41 ps period).
Clock is supplied by the DCO/PI under CDR control.
**No second T/H is needed** — y[n-1] is implicitly captured by latching the slicer
outputs (d[n-1], z[n-1]) rather than the raw analog value.

### Data Slicer (Vth = 0)
Standard NRZ decision comparator.  Produces `d[n] ∈ {+1, −1}`.

### Error Slicers (Vth = ±h₀)
Two comparators with thresholds at `+h₀` and `−h₀`, both driven by the same T/H output.

```
z_p[n] = sign(y[n] − h₀)   ← fires near boundary for +1 symbols
z_m[n] = sign(y[n] + h₀)   ← fires near boundary for −1 symbols
```

A MUX (one gate, controlled by `d[n]`) selects the appropriate slicer:

```
z[n] = sign(y[n] − d[n]·h₀)
```

At perfect timing:
- `d[n] = +1`: `y[n] = +h₀ → z[n] = sign(0)` — boundary (TED zero-crossing)
- `d[n] = −1`: `y[n] = −h₀ → z[n] = sign(0)` — boundary (TED zero-crossing)

The two-slicer / MUX arrangement makes the TED S-curve symmetric for both
polarities of data transition.

The MUX is a **digital** 2:1 gate — all three slicer outputs (`d[n]`, `z_p[n]`,
`z_m[n]`) are rail-to-rail digital signals.  In a sub-7 nm CMOS node the MUX
contributes ~1–2 ps of delay, well within the 9.41 ps UI budget.  This is not an
analog MUX (no continuous-amplitude path, no kickback or bandwidth concern).

### D-Latches (1 UI delay)
One flip-flop on d[n] and one on z[n], both clocked at the baud rate.
Produce d[n-1] and z[n-1] respectively.  No analog delay cell required.

### BB MM-TED

```
e[n] = d[n-1]·z[n] − d[n]·z[n-1]
```

With `z[n] = sign(y[n] − d[n]·h₀)`, truth-table for key cases (ignoring z = 0 boundary):

| d[n-1] | d[n] | z[n] | z[n-1] | e[n] | Interpretation |
|--------|------|------|--------|------|----------------|
| +1 | +1 | ±1 | ±1 | 0 | No transition — always cancels (d[n-1]=d[n]) |
| −1 | −1 | ±1 | ±1 | 0 | No transition — always cancels |
| −1 | +1 | −1 | −1 | **+2** | Rising transition, **early** (y[n] < +h₀) |
| −1 | +1 | +1 | −1 | 0 | Rising transition, **locked** (y[n] ≈ +h₀) |
| −1 | +1 | +1 | +1 | **−2** | Rising transition, **late** (y[n-1] > −h₀) |
| +1 | −1 | +1 | +1 | **−2** | Falling transition, **early** (y[n] > −h₀) |
| +1 | −1 | −1 | +1 | 0 | Falling transition, **locked** (y[n] ≈ −h₀) |
| +1 | −1 | −1 | −1 | **+2** | Falling transition, **late** (y[n-1] < +h₀) |

CDR retards clock when `sign(e[n]) = +1` (early), advances when `sign(e[n]) = −1` (late).

### Digital CDR Engine

Receives the 1-bit bang-bang signal `sign(e[n])` and runs entirely in the digital
domain:

| Sub-block | Function |
|-----------|---------|
| Loop filter (IIR/PI) | Integrates sign(e) to produce a phase control word |
| DCO / PI | Generates the baud-rate sampling clock from the phase word |
| h₀ estimator | Tracks the cursor amplitude; updates the error slicer threshold |
| VGA controller | Adjusts analog gain to maintain consistent eye amplitude |

---

## Key Design Properties

* **No edge sampler** — MM is inherently baud-rate; timing information is extracted
  from the amplitude of consecutive data samples, not from the transition midpoint.
* **No analog delay cell** — delaying the slicer outputs (digital) rather than the
  raw analog signal eliminates a precision 9.41 ps delay in the analog domain.
* **h₀ coupling** — the same h₀ estimate drives both the VGA (sets eye amplitude)
  and the error slicer threshold, so they track each other automatically.

---

---

## Simulation 1 — Minimal Lock Demonstration

### Goal
Verify that the BB MM-TED can acquire and maintain phase lock on a band-limited NRZ
signal without CTLE, VGA, or h₀ adaptation.  h₀ is computed analytically from the
channel ahead of time and held fixed throughout.

### Transmitter

| Parameter | Value |
|-----------|-------|
| Data pattern | PRBS-15 (polynomial x¹⁵ + x¹⁴ + 1, length 32 767 symbols) |
| Symbol alphabet | NRZ ∈ {+1, −1} |
| Baud rate | 106.25 Gbps |
| UI | 1 / 106.25 GHz ≈ 9.412 ps |
| Oversampling ratio (OSR) | 32 samples / UI |
| Simulation sample rate | 106.25 GHz × 32 = 3.4 THz (Tₛ ≈ 0.294 ps) |
| Pulse shaping | Zero-order hold — each symbol repeated 32× (rectangular NRZ pulse) |

Total simulation length: 32 767 × 32 = 1 048 544 samples.

### Channel

| Parameter | Value |
|-----------|-------|
| Model | Bessel-Thomson (BT) low-pass filter |
| Order | 4th order |
| −3 dB frequency | f_Nyquist = f_baud / 2 = 53.125 GHz |
| Implementation | `scipy.signal` (analog BT prototype → `lp2lp` → `bilinear` at Tₛ) |
| Noise | None (first simulation is noiseless) |

The 4th-order BT filter at Nyquist bandwidth gives a smooth, maximally-flat group
delay response that approximates the combined TX driver + package + PCB channel.

### Known h₀ Calculation

Before running the CDR, h₀ is computed once from the channel impulse response:

1. Create a single isolated +1 symbol: 32 ones followed by sufficient zeros.
2. Pass through the BT filter.
3. h₀ = peak value of the filtered output.

This is the cursor amplitude the error slicers will threshold against.  Because there
is no VGA, the signal amplitude is whatever the BT filter preserves of the unit
rectangular pulse (expected h₀ ≈ 0.6–0.8 for 4th-order BT at Nyquist BW — exact
value computed at run-time).

### Receiver (simulation model)

No CTLE, no VGA, no noise.  Only:
- Data slicer at 0
- Two error slicers at ±h₀ (fixed)
- Digital MUX → z[n]
- D-latches for d[n-1], z[n-1]
- BB MM-TED
- Proportional-only CDR loop filter

#### Phase interpolator
The sampling clock is modelled as a **discrete phase interpolator** using the
existing `PhaseInterpolator` class (`src/optical_serdes/rx/pi.py`) with
`n_phases = OSR = 32`.

```python
pi = PhaseInterpolator(n_phases=32)
idx = pi.data_index(ui, pi_code)   # → ui*32 + (pi_code % 32)
y_n = waveform[idx]
```

Because OSR = n_phases = 32, the oversampled simulation grid is the PI resolution
grid — there is no interpolation between samples.  Each integer step in `pi_code`
corresponds to exactly 1/32 UI ≈ 0.29 ps, matching the stated hardware resolution.

The `pi_code` is an integer in [0, 31]; `PhaseInterpolator.wrap()` handles modulo
arithmetic cleanly.

#### CDR update rule (per baud cycle)
```
idx      = pi.data_index(ui, pi_code)
y[n]     = waveform[idx]
d[n]     = sign(y[n])
z[n]     = sign(y[n] − d[n]·h₀)        # MUX between ±h₀ error slicers
e[n]     = d[n-1]·z[n] − d[n]·z[n-1]  # BB MM-TED
pi_code  = (pi_code + sign(e[n])) % 32 # ±1 step per bang-bang correction
d[n-1]  ← d[n]
z[n-1]  ← z[n]
ui      += 1
```

| CDR parameter | Value | Notes |
|--------------|-------|-------|
| PI resolution | 1/32 UI ≈ 0.29 ps | Integer step in `pi_code` |
| Proportional gain `Kp` | 1 step | One PI code increment per bang-bang output |
| Integral gain `Ki` | 0 | Proportional-only; loop will limit-cycle ±1 step |
| Initial `pi_code` | 8 (= OSR/4) | Deliberate ¼ UI offset to exercise acquisition |

The proportional-only loop will exhibit limit-cycle jitter (the phase dithers ±1
PI step around the locking point) — this is expected and correct for a first-order
BB CDR.

### Outputs / pass criteria

| Output | How to measure | Pass |
|--------|---------------|------|
| Phase trajectory | Plot `φ mod OSR` vs. symbol index | Converges to a stable narrow band within ~200 UI |
| TED output | Plot `sign(e[n])` running average vs. symbol index | Mean → 0 after lock |
| Post-lock BER | Compare d[n] to transmitted symbols (after 500 UI settling) | BER = 0 (noiseless channel) |
| Eye diagram | Overlay waveform segments at recovered phase | Open eye centred on ±h₀ |

---

## Open Design Questions

1. **h₀ estimator algorithm** — peak detector, least-mean-squares adaptation, or
   fixed calibration?  LMS on the error signal is natural but requires the
   analytic product `d[n]·y[n]` (continuous amplitude), which isn't available
   in this all-slicer path.
2. **TED gain vs. jitter trade-off** — bang-bang (sign-only) CDR is simpler but
   introduces limit-cycle jitter.  A partial-linear approach (replacing `sign(e)`
   with a multi-level quantised error) could reduce jitter at the cost of an extra
   slicer or two.
3. **Half-rate clocking** — at 106.25 Gbps, a 53.125 GHz half-rate clock with two
   interleaved T/H phases is often preferred.  The block diagram above shows a
   simplified full-rate view.
