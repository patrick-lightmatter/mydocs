# Danyang Driver + BiasT + MRM Characterisation Summary

**Dataset:** `0720` Virtuoso AC + transient captures  
**Raw data:** `optical-serdes/temp/food/danyang/`  
**Analysis scripts:** `optical-serdes/temp/food/danyang/*.py`  
**Baud-rate reference:** 106.25 GBd NRZ (`UI = 9.41 ps`, resampled to `UI/32 = 0.294 ps`)

---

## Signal chain

Both AC and transient testbenches probe the same insertion points:

```
VIN → DRV → (drv out) → BiasT → (drv_eic / eic out) → MRM → Opto
```

| Node key (diff) | Description | Role |
|---|---|---|
| `input` / `drv_in` | Differential input | Stimulus reference |
| `drv` | Driver output | Pre-BiasT electrical output |
| `drv_eic` | BiasT output | Post-BiasT; drives the MRM |
| `vmrm` / `mrm` | MRM input | Modulator electrical port |
| `opto` | Optical power | Modulator output (AC diff only) |

Single-ended captures record P and N legs separately at each node (`DRV_single_*` files).

---

## Source files

| File | Format | Content |
|---|---|---|
| `DRV_diff_ac_response_0720_w_notes.xlsx` | Excel | Differential AC sweep: mag + phase, 121 log-spaced points (100 kHz – 100 GHz) |
| `DRV_single_ac_response_0720_w_notes.xlsx` | Excel | Single-ended (P/N) AC sweep, same frequency grid |
| `DRV_diff_tran_response_0720.csv` | CSV | Differential transient: step/pulse response |
| `DRV_single_tran_response_0720.csv` | CSV | Single-ended (P/N) transient |

**Transient stimulus:** differential pulse — low for 0–100 ns, high for 100 ns–5.1 µs, then back low. The rising edge at ~100 ns is finely resolved (~1 ps near the edge); the long hold exposes BiasT/MRM droop and settling.

**Transient grid:** 1445 non-uniform samples over 10.09 µs (mean Δt ≈ 7 ns; sub-ps spacing at the edge). All baud-rate analysis resamples onto a uniform `UI/32` grid via linear interpolation.

---

## Analysis scripts

All scripts live in `optical-serdes/temp/food/danyang/` and share loaders/constants in `load_data.py`.

| Script | Purpose | Output figure(s) |
|---|---|---|
| `ac_bode.py` | Bode plots (mag + phase) for diff and single-ended AC | `ac_bode_diff.png`, `ac_bode_single.png` |
| `transient_response.py` | Full pulse + rising-edge zoom for diff and SE | `transient_diff.png`, `transient_single.png` |
| `crosscheck_diff_single.py` | Validate `Vdiff` vs `Vp − Vn` in AC and transient | `crosscheck_diff_single.png` |
| `extract_sbr_from_step.py` | Step → IR → frequency response (DRV and BiasT nodes) | `step_raw_vs_interpolated.png`, `step_derived_ir.png`, `step_derived_freqresponse.png` |
| `eye_diagrams.py` | PRBS-15 NRZ eyes through derived IRs | `eye_diagrams.png` |
| `channel_plus_driver.py` | Cascade BiasT output with Masood channel IR | `channel_plus_driver_freqresponse.png`, `channel_plus_driver_impulse_responses.png`, `channel_plus_driver_eye.png` |

Regenerate all plots:

```bash
cd optical-serdes/temp/food/danyang
python3 ac_bode.py
python3 transient_response.py
python3 crosscheck_diff_single.py
python3 extract_sbr_from_step.py
python3 eye_diagrams.py
python3 channel_plus_driver.py
```

---

## Data validation (diff vs single-ended)

Direct differential probes match `Vp − Vn` from the single-ended dataset to numerical precision:

| Node | AC max \|error\| | Transient max \|error\| |
|---|---:|---:|
| DRV input | 0.0000 dB | 1×10⁻¹³ V |
| DRV output | 0.0000 dB | 1×10⁻¹¹ V |
| BiasT output | 0.0000 dB | 1×10⁻¹¹ V |
| MRM input | 0.0000 dB | 1×10⁻¹¹ V |

The two testbenches are self-consistent; either representation can be used for analysis.

![Diff vs single-ended cross-check](crosscheck_diff_single.png)

---

## AC (small-signal) results

Frequency sweep: 100 kHz – 100 GHz, 121 points. Magnitude normalised to the value at 100 kHz.

**Nyquist loss at 53.125 GHz** (half of 106.25 GBd):

| Node | Nyquist magnitude (rel. 100 kHz) |
|---|---:|
| DRV input | −3.71 dB |
| DRV output | −0.64 dB |
| BiasT output | +8.74 dB |
| MRM input | +10.18 dB |

The BiasT and MRM nodes show *gain* relative to the 100 kHz reference because the BiasT is AC-coupled: the low-frequency reference sits on the blocked-DC side of the high-pass characteristic. These AC numbers describe the small-signal phasor chain, not the large-signal step bandwidth in isolation.

Optical output (`opto`) is available in the differential AC file as a power magnitude (not dB-normalised voltage).

![Differential AC Bode](ac_bode_diff.png)

![Single-ended AC Bode (P solid, N dashed)](ac_bode_single.png)

---

## Transient (large-signal step) results

**Step swings** (rising edge, diff):

| Node | Swing (V) | 10–90% risetime (ps) |
|---|---:|---:|
| DRV output (`drv`) | 1.145 | 11.2 |
| BiasT output (`drv_eic`) | 1.106 | 9.7 |

DRV output spans roughly ±1.15 V differential. BiasT output is single-ended referenced (0.45 – 2.85 V range over the full pulse). MRM input (`vmrm`) tracks BiasT output closely. Optical power (`opto`) swings ~3 – 8 mW.

The long hold (multi-µs) reveals slow droop on the BiasT/MRM side — expected from AC coupling — but this is far slower than baud-rate ISI and must be handled carefully when building convolution kernels (see below).

![Differential transient response](transient_diff.png)

![Single-ended transient response](transient_single.png)

---

## Step-derived impulse response and frequency response

Method (per `optical-serdes/.claude/skills/characterise-step-sbr.md`):

1. Window the rising edge: 50 ps before → 2.5 ns after t = 100 ns.
2. Linear interpolation onto uniform `UI/32` grid.
3. Differentiate step response → continuous IR (V/s).
4. Discrete tap: `h[n] = ir × DT`.
5. FFT of tapered IR → magnitude and group delay.

**Caveat:** the applied step has a finite (~10–20 ps) input risetime, so the derived IR is `(source risetime) ⊗ (system)`, not a deconvolved Dirac-source response. Suitable for first-look bandwidth/ISI modelling; Wiener deconvolution would be needed for a true Dirac IR.

**Nyquist loss from step-derived IR** (truncated to 30 UI + tail taper):

| Node | DC gain Σh | Nyquist loss |
|---|---:|---:|
| DRV output | 1.144 | −9.87 dB |
| BiasT output | 1.131 | −6.92 dB |

Step-derived Nyquist loss is more pessimistic than the AC small-signal numbers for DRV output (−9.9 dB vs −0.6 dB), reflecting the combined effect of finite input edge rate, large-signal behaviour, and the differentiation/FFT pipeline. Use AC for small-signal chain budgeting; use step-derived IR for time-domain eye/ISI simulation.

Group-delay plots mask bins below 5 GHz and where \|H\| is >40 dB below peak, to suppress numerical artefacts from truncation and AC-coupling tails.

![Step response: raw vs UI/32-interpolated](step_raw_vs_interpolated.png)

![Derived impulse responses](step_derived_ir.png)

![Frequency response from derived IR](step_derived_freqresponse.png)

---

## Eye diagrams (PRBS-15, 106.25 GBd NRZ)

Drive: one full PRBS-15 period (32 767 bits), zero-order hold (`np.repeat(symbols, SPS)`), convolved with the truncated step-derived IR.

| Node | Eye height (V) | Eye width (UI) |
|---|---:|---:|
| DRV output | 0.429 | 0.375 |
| BiasT output | 0.596 | 0.344 |

**IR truncation (30 UI):** the full 2.5 ns extraction window leaves `drv_eic` sitting on a tiny but persistent one-signed plateau from microsecond-scale BiasT droop. Unlike DRV's alternating-sign tail, this plateau integrates coherently over long PRBS runs and produces spurious baseline wander that artificially closes the eye. Truncating the kernel to 30 UI past the main lobe removes this artefact while retaining baud-rate ISI.

![PRBS-15 eye diagrams at DRV and BiasT outputs](eye_diagrams.png)

---

## Effective channel: Danyang driver + Masood interconnect

The BiasT output (`drv_eic`) was cascaded with the Masood channel impulse response (`optical-serdes/temp/data/step_response/from_masood/impulse_response.csv`), resampled to the same `UI/32` grid:

```
h_effective = conv(h_driver, h_channel)
```

**Nyquist loss at 53.125 GHz:**

| Block | Loss |
|---|---:|
| Danyang driver + BiasT | −6.92 dB |
| Masood channel | −4.77 dB |
| **Cascade (effective channel)** | **−11.69 dB** |

The dB-sum matches the direct FFT of `h_combined` exactly.

**Effective-channel eye** (PRBS-15 through cascade):

| Metric | Value |
|---|---:|
| Eye height | 0.133 V |
| Eye width | 0.312 UI |

The combined ~12 dB Nyquist loss produces a tight but still open eye.

![Frequency response: driver vs channel vs cascade](channel_plus_driver_freqresponse.png)

![Impulse responses: driver, channel, combined](channel_plus_driver_impulse_responses.png)

![NRZ eye at effective-channel output](channel_plus_driver_eye.png)

To cascade the channel before the BiasT instead (bare DRV output), change `DRIVER_NODE = "drv"` at the top of `channel_plus_driver.py`.

---

## Key takeaways

1. **Dataset quality:** differential and single-ended captures are internally consistent across AC and transient domains.
2. **Driver bandwidth:** DRV output has ~11 ps 10–90% edge rate on a ~1.15 V step; step-derived Nyquist loss is ~−10 dB, tighter than ideal for clean 106G NRZ without equalisation.
3. **BiasT impact:** AC coupling adds high-pass shaping and long-timescale droop. For baud-rate simulation, truncate the IR to an ISI-relevant window (~30 UI) rather than using the full 2.5 ns extraction span.
4. **End-to-end electrical channel:** Danyang BiasT output + Masood channel ≈ **−11.7 dB at Nyquist**, eye height ~0.13 V at unit NRZ swing — marginal but open; FFE/CDR would likely be required in a real receiver.
5. **MRM/optical path:** AC and transient data include MRM and optical nodes; this summary focused on the electrical TX chain through BiasT. Optical modulation characterisation is available in the AC Bode plots but not yet folded into the IR/eye pipeline.

---

## Assumptions and limitations

- Baud rate fixed at **106.25 GBd** for all UI-normalised analysis (matches the OCI-Gen2 / Masood channel work).
- Step-derived IR includes the finite input edge; not deconvolved.
- BiasT droop handled by IR truncation for eyes/convolution, not by explicit high-pass modelling.
- Masood channel cascade attaches at **BiasT output** (`drv_eic`), modelling the interconnect between the TX assembly and the MRM.
- AC Nyquist numbers for BiasT/MRM nodes use a 100 kHz reference and are not directly comparable to the step-derived loss figures.
