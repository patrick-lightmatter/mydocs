# MRM Laser-Power Step-Response (Loop-Bandwidth) Study — PGT + L2V, 10 mW masked IADC

Companion to the sinusoidal laser-bandwidth reports
([`MRM_PGT_LASER_BANDWIDTH_REPORT.md`](MRM_PGT_LASER_BANDWIDTH_REPORT.md),
[`MRM_L2V_LASER_BANDWIDTH_REPORT.md`](MRM_L2V_LASER_BANDWIDTH_REPORT.md)) and to
the thermal-aggressor consolidation
([`../MRM_THERMAL_SIMS_PGT_L2V.md`](../MRM_THERMAL_SIMS_PGT_L2V.md)).

Instead of a sinusoidal sweep, this study drives a **laser-power step up** (+1 %
and +10 % from a 10 mW baseline) and measures the loop's transient. The loop
bandwidth is read off the **10–90 % rise time** of the heater actuator
response, `f_3dB ≈ 0.35 / t_rise` (first-order equivalent, `τ = t_rise / 2.2`).
It reuses the *same setting combinations* the 10 mW masked-IADC triangle studies
characterized (PGT §6 / L2V §7 of the thermal doc), so the bandwidth numbers are
directly comparable to the thermal-rejection results at the same operating
point.

* **Plant:** `coupe_mrm_block` via `scripts/run_tsmc.sh` (caribou-mrm `.venv`).
* **Heater DAC:** sweet-spot HDAC, 13-bit, **LSB = 0.201 mV** (1.8 V FS).
* **Optical power:** **10 mW** center, hot-side lock, **step up only** (+1 %, +10 %).
* **Baseline lock point:** reused from the triangle studies (PGT hot-peak
  ≈ 0.715 V; L2V re-derived per mask from the on-grid open-loop sweep).
* **ADC:** 16-bit / 560 µA drop FS with the low *N* bits masked (ENOB cut), the
  same masked-IADC model as the 10 mW triangle studies. L2V `peak_ratio` uses a
  separate broadband full-scale (`bb_fullscale_A = 2·P_center = 20 mA`) so the
  10 mW operating point lands mid-ADC with ±10 % headroom.
* **Aggressor mechanism:** a step on the laser drive current
  (`P = P_center` for `t < t_step`, `P_center·(1+depth)` after), injected at the
  ADC sample rate inside each control window — i.e. the same per-sample laser
  injection path the sinusoidal harness uses, with a step waveform.

## Sources (regenerated at, in `goldens/mrm/`)

| Artifact | Path |
|---|---|
| Aggregated summary (one row per controller/config/depth) | `output/mrm_laser_step_study/laser_step_study_summary.csv` |
| Bandwidth + actuator-excursion comparison figure | `output/mrm_laser_step_study/laser_step_bandwidth.png` |
| Per-run traces / metrics | `output/mrm_laser_step_study/{pgt,l2v}/<config>_<depth>/` |
| PGT step worker | `src/testbench/skadi_mrm_pgt_laser_disturbance.py --profile step` |
| L2V step worker | `src/testbench/mrm_l2v_laser_disturbance.py --profile step` |
| Study orchestrator | `src/testbench/run_laser_step_study.py` |

---

## TL;DR

* **PGT rejects the laser step entirely — there is no rise time to measure.**
  Across every config (kstep 6/7, mask 6/7, dither 48 mV) and both step sizes,
  the hill-climb holds its heater limit-cycle around the **same** mean lock point
  (≤ 2.4 mV residual, i.e. within the dither cycle). The drop photocurrent and
  Goertzel energy simply scale with the +10 % input power (open-loop optical
  scaling, energy ∝ power²), but the Goertzel **argmax does not move with power**,
  so the loop does not re-point. This is the structural power-invariance the
  sinusoidal study predicted, now shown directly in the time domain.
  → For PGT the right metric vs a laser step is **rejection**, not bandwidth.

* **L2V re-points only for the +10 % step; its closed-loop bandwidth is
  ≈ 0.8–1.0 kHz**, set by the 50 µs control tick × 8-code (1 LSB) bang-bang slew
  — essentially **independent of target mode and mask**:

  | Target mode | mask 7 (9-bit) | mask 8 (8-bit) | mask 9 (7-bit) |
  |---|---|---|---|
  | `iadc_value` | 875 Hz (0.40 ms) | 1000 Hz (0.35 ms) | 1000 Hz (0.35 ms) |
  | `peak_ratio` | 778 Hz (0.45 ms) | 778 Hz (0.45 ms) | 778 Hz (0.45 ms) |

  Differences are 1–2 control-tick quantization steps; treat them all as
  **≈ 0.8–1.0 kHz effective loop bandwidth**.

* **The +1 % step is sub-quantum at masks 7/8/9 and is rejected by both
  controllers** (heater moves ≤ 1 LSB = 0.2 mV). At a 10 mW baseline a +1 %
  laser change lands inside the masked-IADC quantum / dead zone, so L2V never
  leaves lock — the same ENOB floor that sets the thermal-rejection residual.

## Method notes / caveats

* **Bandwidth is read from the actuator (heater V), not the drop current.** For
  a rejecting loop the drop-current "edge" is just the optical input step, not a
  loop response, so it is reported for context only. `loop_bw_hz` is emitted only
  when the heater actually chases (`heater_responded = True`); otherwise
  `bw_source = "rejected"`.
* **L2V `peak_ratio` still moves ~2.2 mV on the +10 % step** even though it
  ratio-tracks the live broadband power. Reason: a +10 % power step at 10 mW also
  causes a real **self-heating resonance shift**; `peak_ratio` rejects the
  power-scaling of the *reading* but not the physical operating-point shift, so a
  small real chase remains. Its rise time (≈ 0.45 ms) is therefore similar to
  `iadc_value`'s — the two modes differ in steady-state rejection quality (see
  the sinusoidal report), not in step-response speed.
* **Rise time is quantized by the control update period** (PGT window ≈ 134 µs;
  L2V tick = 50 µs). The reported bandwidths are coarse (`rough loop BW`, as
  requested), bounded above by the update rate.
* **Scope:** up-steps only; baseline lock points reused from the triangle
  studies (not re-derived per run). Down-steps and a finer depth sweep are
  straightforward follow-ups (`--p-depth`, both polarities).

## Figures

### Bandwidth / excursion summary (all cases)

Top: closed-loop bandwidth from the 10–90 % rise time (bars only where the loop
chases; "rejected" = heater held lock). Bottom: heater actuator excursion
(small = rejected).

![Loop bandwidth and actuator excursion across all configs and step sizes](figures/laser_step/laser_step_bandwidth.png)

### PGT — laser-step traces (loop holds lock; no re-point)

Panels per figure: laser power · heater V (actuator) · drop photocurrent ·
Goertzel energy. The heater limit-cycles around the **same** mean after the
step; drop/energy scale with input power only.

| Config | +1 % step | +10 % step |
|---|---|---|
| kstep 7, mask 6 (10-bit), dither 48 mV — *triangle winner* | ![PGT k7 mask6 +1%](figures/laser_step/pgt_k7_mask6_d48_1pct.png) | ![PGT k7 mask6 +10%](figures/laser_step/pgt_k7_mask6_d48_10pct.png) |
| kstep 6, mask 6 (10-bit), dither 48 mV | ![PGT k6 mask6 +1%](figures/laser_step/pgt_k6_mask6_d48_1pct.png) | ![PGT k6 mask6 +10%](figures/laser_step/pgt_k6_mask6_d48_10pct.png) |
| kstep 7, mask 7 (9-bit), dither 48 mV | ![PGT k7 mask7 +1%](figures/laser_step/pgt_k7_mask7_d48_1pct.png) | ![PGT k7 mask7 +10%](figures/laser_step/pgt_k7_mask7_d48_10pct.png) |

### L2V — laser-step traces

Panels per figure: laser power · ADC vs target · ADC error · heater V
(actuator). The +10 % `iadc_value` cases show the clean monotonic heater slew
the rise time is measured on; +1 % cases are sub-quantum (no chase).

#### `iadc_value` (hold absolute ADC code)

| Mask | +1 % step | +10 % step |
|---|---|---|
| mask 7 (9-bit ENOB) | ![L2V iadc mask7 +1%](figures/laser_step/l2v_mask7_iadc_value_1pct.png) | ![L2V iadc mask7 +10%](figures/laser_step/l2v_mask7_iadc_value_10pct.png) |
| mask 8 (8-bit ENOB) | ![L2V iadc mask8 +1%](figures/laser_step/l2v_mask8_iadc_value_1pct.png) | ![L2V iadc mask8 +10%](figures/laser_step/l2v_mask8_iadc_value_10pct.png) |
| mask 9 (7-bit ENOB) | ![L2V iadc mask9 +1%](figures/laser_step/l2v_mask9_iadc_value_1pct.png) | ![L2V iadc mask9 +10%](figures/laser_step/l2v_mask9_iadc_value_10pct.png) |

#### `peak_ratio` (hold ADC at a ratio of live broadband power)

| Mask | +1 % step | +10 % step |
|---|---|---|
| mask 7 (9-bit ENOB) | ![L2V peak_ratio mask7 +1%](figures/laser_step/l2v_mask7_peak_ratio_1pct.png) | ![L2V peak_ratio mask7 +10%](figures/laser_step/l2v_mask7_peak_ratio_10pct.png) |
| mask 8 (8-bit ENOB) | ![L2V peak_ratio mask8 +1%](figures/laser_step/l2v_mask8_peak_ratio_1pct.png) | ![L2V peak_ratio mask8 +10%](figures/laser_step/l2v_mask8_peak_ratio_10pct.png) |
| mask 9 (7-bit ENOB) | ![L2V peak_ratio mask9 +1%](figures/laser_step/l2v_mask9_peak_ratio_1pct.png) | ![L2V peak_ratio mask9 +10%](figures/laser_step/l2v_mask9_peak_ratio_10pct.png) |

## Reproduce

```bash
cd goldens/mrm
# full matrix (6 PGT + 12 L2V runs, ~3-4 min with 6 workers):
scripts/run_tsmc.sh -m src.testbench.run_laser_step_study \
    --out-dir output/mrm_laser_step_study --max-workers 6

# single config, e.g. L2V iadc_value +10% at mask 7:
scripts/run_tsmc.sh -m src.testbench.mrm_l2v_laser_disturbance --profile step \
    --p-center-W 0.01 --p-depth 0.10 --target-mode iadc_value \
    --adc-mask-bits 7 --bb-fullscale-A 0.02 --out-dir /tmp/l2v_step

# single config, PGT triangle-winner +10%:
scripts/run_tsmc.sh -m src.testbench.skadi_mrm_pgt_laser_disturbance --profile step \
    --p-center-W 0.01 --p-depth 0.10 --kstep 7 --adc-mask-bits 6 \
    --dither-amp-v 0.048 --mh-voltage-init 0.715 --ovr-counter 0 \
    --out-dir /tmp/pgt_step
```
