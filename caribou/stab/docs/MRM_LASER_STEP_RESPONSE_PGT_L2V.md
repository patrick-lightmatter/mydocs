# MRM Laser-Power Step-Response Study — PGT + L2V, 10 mW masked IADC

Companion to the sinusoidal laser-bandwidth reports
([`MRM_PGT_LASER_BANDWIDTH_REPORT.md`](MRM_PGT_LASER_BANDWIDTH_REPORT.md),
[`MRM_L2V_LASER_BANDWIDTH_REPORT.md`](MRM_L2V_LASER_BANDWIDTH_REPORT.md)) and to
the thermal-aggressor consolidation
([`../MRM_THERMAL_SIMS_PGT_L2V.md`](../MRM_THERMAL_SIMS_PGT_L2V.md)).

Instead of a sinusoidal sweep, this study drives a **laser-power step up** (+1 %
and +10 % from a 10 mW baseline) and asks one question of each controller:
**does the heater re-point in response, and if so, was that move necessary?**
For the loops that *do* re-point, the speed of that move is read off the
**10–90 % rise time** of the heater actuator, `f_3dB ≈ 0.35 / t_rise`
(first-order equivalent, `τ = t_rise / 2.2`). It reuses the *same setting
combinations* the 10 mW masked-IADC triangle studies characterized (PGT §6 /
L2V §7 of the thermal doc), so it is directly comparable to the
thermal-rejection results at the same operating point.

* **Plant:** `coupe_mrm_block` via `scripts/run_tsmc.sh` (caribou-mrm `.venv`).
* **Heater DAC:** sweet-spot HDAC, 16-bit controller code on a 13-bit physical
  grid. **1 physical LSB = 8 controller codes = (1.8 − 0.15)/8192 V ≈ 0.20 mV**
  (1.8 V FS, 0.15 V boost). All re-point sizes below are quoted in these LSBs.
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

## Sources (in `goldens/mrm/`)

| Artifact | Path |
|---|---|
| Aggregated summary (one row per controller/config/depth) | `output/mrm_laser_step_study/laser_step_study_summary.csv` |
| Re-point + bandwidth comparison figure | `output/mrm_laser_step_study/laser_step_bandwidth.png` |
| Per-run traces / metrics | `output/mrm_laser_step_study/{pgt,l2v}/<config>_<depth>/` |
| PGT step worker | `src/testbench/skadi_mrm_pgt_laser_disturbance.py --profile step` |
| L2V step worker | `src/testbench/mrm_l2v_laser_disturbance.py --profile step` |
| Study orchestrator (`--replot` re-aggregates without re-simulating) | `src/testbench/run_laser_step_study.py` |

---

## TL;DR — three different responses to the same laser step

A +10 % laser step at 10 mW produces a **real ~10-LSB self-heating resonance
shift** (the extra absorbed power warms the ring). What each controller *does*
about it is the whole story:

| Controller / mode | net heater re-point (+10 % step) | did it re-point? | correct? |
|---|---|---|---|
| **PGT** (Goertzel hill-climb) | **≤ 1.5 steps**, inside its own limit cycle | **No** — holds lock | ✅ correct |
| **L2V `peak_ratio`** (ratio target) | **~11 LSB**, *opposite* direction to `iadc` | Yes — tracks the peak | ✅ correct (necessary move) |
| **L2V `iadc_value`** (absolute-current target) | **~9 LSB**, detunes off-peak | Yes — defends a fixed current | ❌ unnecessary chase |

1. **PGT holds — and rightly so.** Across every config (kstep 6/7, mask 6/7,
   dither 48 mV) and both step sizes, the hill-climb's *net* lock point does not
   move: the settled-mean shift is ≤ 1.5 hill-climb steps and stays **inside the
   dither limit cycle** (net re-point ≤ ½ of the limit-cycle pk-pk in every
   case). Two reasons: (a) the Goertzel argmax is power-invariant, so it rejects
   the optical +10 % scaling outright, and (b) the residual ~10-LSB real thermal
   shift is **smaller than one kstep-7 hill-climb step (16 LSB)**, so it is
   absorbed by the limit cycle rather than producing a net code change. There is
   no rise time to measure → PGT's metric vs a laser step is **rejection**.

2. **L2V `iadc_value` chases unnecessarily.** This mode pins the *absolute* drop
   photocurrent. When the laser steps +10 %, the drop current rises, and the
   loop deliberately **detunes the ring (~9 LSB / 9 track-steps, in the heat
   direction) to push the photocurrent back down** — re-pointing *off* the
   optimal resonance to satisfy an objective that has nothing to do with where
   the resonance actually is. This is the "unnecessary chase."

3. **L2V `peak_ratio` also re-points (~11 LSB), but its move is correct.** Its
   target scales with live broadband power, so it ignores the optical +10 %
   scaling. The residual move tracks the **real self-heating resonance shift** to
   stay on the optimal peak — note it re-points in the **opposite direction**
   to `iadc_value` (toward, not away from, the shifted peak). Its excursion is
   actually *comparable to or slightly larger* than `iadc_value`'s in raw LSBs;
   the distinction is **why** it moves (tracking the true peak vs defending a
   stale current), not the magnitude.

**The +1 % step is sub-quantum and is held by everything** (net re-point ≤ 1 LSB
at masks 7/8/9, `responded = False` for both controllers). At a 10 mW baseline a
+1 % laser change lands inside the masked-IADC quantum / dead zone, the same
ENOB floor that sets the thermal-rejection residual.

### Bandwidth of the moves that do happen

For the loops that *do* chase (only the L2V +10 % cases), the rise time gives an
effective closed-loop bandwidth of **≈ 0.8–1.0 kHz**, set by the 50 µs control
tick × 1-LSB bang-bang slew — essentially **independent of target mode and
mask**:

| Target mode | mask 7 (9-bit) | mask 8 (8-bit) | mask 9 (7-bit) |
|---|---|---|---|
| `iadc_value` | 875 Hz (0.40 ms) | 1000 Hz (0.35 ms) | 1000 Hz (0.35 ms) |
| `peak_ratio` | 778 Hz (0.45 ms) | 778 Hz (0.45 ms) | 778 Hz (0.45 ms) |

Differences are 1–2 control-tick quantization steps; treat them all as
**≈ 0.8–1.0 kHz**. This is a **large-signal, slew-limited** number (how fast the
bang-bang DAC can walk), not a small-signal loop bandwidth.

## How a "move" is determined (DAC codes, not photocurrent)

The actuator is the heater DAC, so a "move" is measured directly in **heater
voltage / DAC codes**, never in photocurrent (the drop current rises with the
optical step whether or not the loop responds, so it cannot tell a chase from a
rejection).

* **Net re-point** = mean of the last 20 % of *post*-step heater samples minus
  the mean of the last 20 % of *pre*-step samples (`v_post_ss_mV − v_pre_ss_mV`).
  This steady-state delta is converted to **DAC LSBs** (1 LSB ≈ 0.20 mV = 8
  controller codes) and to **controller steps** (PGT: 2^kstep codes/step; L2V:
  `step_size_track` = 8 codes = 1 LSB/step) in the CSV
  (`net_repoint_dac_lsb`, `net_repoint_steps`).
* **Held vs chased needs the limit-cycle context.** Raw LSB counts alone are
  misleading: PGT's kstep-7 limit cycle swings ±16 LSB/step, so a half-step
  sampling offset (~8 LSB) looks numerically similar to L2V's real ~9-LSB chase.
  The discriminator is the **net re-point relative to the loop's own
  limit-cycle pk-pk** (`limit_cycle_pkpk_lsb`): if the permanent shift clears the
  limit cycle it is a real chase (`heater_responded = True`); if it stays inside,
  the loop held. The figure overlays the pk-pk as black caps so this is visible
  per case.
* **`net_repoint_steps` is the clean separator:** PGT ≤ 1.5, L2V held +1 % cases
  ≤ 1, L2V chased +10 % cases 9–11.5.

## Method notes / caveats

* **Bandwidth is emitted only when the heater actually chases.** For a holding
  loop `loop_bw_hz` is blank and `bw_source = "rejected"`; the drop-current
  "edge" there is just the optical input step, reported for context only.
* **Rise time is quantized by the control update period** (PGT window ≈ 134 µs;
  L2V tick = 50 µs), so the bandwidths are coarse and bounded above by the
  update rate.
* **`peak_ratio` excursion correction.** An earlier draft framed `peak_ratio`'s
  +10 % move as "minor." It is not minor in magnitude (~11 LSB, comparable to
  `iadc_value`); it is *correct in intent* — it tracks the physical resonance
  shift instead of an artifact. The two modes differ in steady-state rejection
  quality (see the sinusoidal report) and in *direction* of the step move, not
  in step-response speed.
* **Scope:** up-steps only; baseline lock points reused from the triangle
  studies (not re-derived per run). Down-steps and a finer depth sweep are
  straightforward follow-ups (`--p-depth`, both polarities).

## Figures

### Re-point vs limit cycle, and bandwidth (all cases)

Top: closed-loop bandwidth from the 10–90 % rise time — bars only where the loop
chases; "rejected (no chase)" elsewhere. Bottom: **net heater re-point in DAC
LSBs** (blue bars) with the **limit-cycle pk-pk** overlaid as black caps. A move
is a real chase only when the blue bar clears its black cap (the L2V +10 %
cases, marked "chase"); PGT and the +1 % cases stay below their caps (held).

![Loop bandwidth and net DAC re-point across all configs and step sizes](figures/laser_step/laser_step_bandwidth.png)

### PGT — laser-step traces (loop holds lock; no net re-point)

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
(actuator). The +10 % cases show the monotonic heater slew the rise time is
measured on; +1 % cases are sub-quantum (no chase). Note `iadc_value` and
`peak_ratio` re-point in opposite directions on the +10 % step.

#### `iadc_value` (hold absolute ADC code — chases unnecessarily)

| Mask | +1 % step | +10 % step |
|---|---|---|
| mask 7 (9-bit ENOB) | ![L2V iadc mask7 +1%](figures/laser_step/l2v_mask7_iadc_value_1pct.png) | ![L2V iadc mask7 +10%](figures/laser_step/l2v_mask7_iadc_value_10pct.png) |
| mask 8 (8-bit ENOB) | ![L2V iadc mask8 +1%](figures/laser_step/l2v_mask8_iadc_value_1pct.png) | ![L2V iadc mask8 +10%](figures/laser_step/l2v_mask8_iadc_value_10pct.png) |
| mask 9 (7-bit ENOB) | ![L2V iadc mask9 +1%](figures/laser_step/l2v_mask9_iadc_value_1pct.png) | ![L2V iadc mask9 +10%](figures/laser_step/l2v_mask9_iadc_value_10pct.png) |

#### `peak_ratio` (hold ADC at a ratio of live broadband power — tracks the real shift)

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

# re-aggregate + re-plot from existing runs (no re-simulation):
scripts/run_tsmc.sh -m src.testbench.run_laser_step_study \
    --out-dir output/mrm_laser_step_study --replot

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
