# Caribou MRM Stabilization — Bandwidth & Aggressor Studies

Self-contained documentation for the latest MRM controller aggressor studies on
the **coupe** ring + **sweet-spot HDAC** (LSB = 0.201 mV at 1.8 V FS). Two
aggressors (ambient **thermal drift** and **laser power**) × two controllers
(**PGT** extremum-seeking, **L2V** lock-to-value). Each report embeds its figures
from [`figures/`](figures); aggregate data is in [`data/`](data). Full per-run
traces and the generating testbenches live in the repo under `goldens/mrm/` (see
each report's *Reproduce* section).

**These studies span a deliberate range of simulation fidelity.** The DAC is
hardware-representative throughout, but the ADC model differs by study — the
1 mW studies use an *idealized* converter and the 10 mW triangle studies use the
*production masked IADC*. This is intentional and load-bearing, not an
inconsistency; read [Simulation fidelity](#simulation-fidelity-data-converters)
before comparing absolute numbers across studies.

## Reports

| Aggressor | Controller | Report | Headline |
|---|---|---|---|
| Thermal drift | **PGT** | [`MRM_PGT_THERMAL_DRIFT_REPORT.md`](MRM_PGT_THERMAL_DRIFT_REPORT.md) | Max trackable drift ~100/250/750/1000 K/s at kstep 3/4/5/6; ~0.4× of the pure-slew limit; needs `ovr_counter=0` to acquire. **Power-independent 0.5–8 mW.** |
| Thermal drift (triangle) | **PGT** | [`MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md`](MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md) | 10 mW triangle (up + down) study. Holds 25→80→25 °C @ 100 K/s (apex loss 12.6 %, round-trip −19.5 %) at kstep=7, mask=6, dither=48 mV. Three named failure modes: **sense-blind apex, actuator saturation, hill-climb step too small.** |
| Thermal drift | **L2V** | [`MRM_L2V_THERMAL_DRIFT_REPORT.md`](MRM_L2V_THERMAL_DRIFT_REPORT.md) | Max trackable ~750/1250/2000/2500 K/s at 1/2/4/7 LSB; up to 0.94× pure-slew; **2.7–7.5× faster than PGT**. Small steps power-independent; **step 56 collapses above ~4 mW**. |
| Thermal drift (triangle) | **L2V** | [`MRM_L2V_TRIANGLE_AGGRESSOR_REPORT.md`](MRM_L2V_TRIANGLE_AGGRESSOR_REPORT.md) | 10 mW triangle, mask {7,8,9} sweep at 1 LSB step. Tracks 25→80→25 °C @ 100 K/s on all three with apex loss **0.33 / 0.81 / 1.88 %** — **5–40× tighter than PGT** at the same operating point. Mask quantization sets the retention floor (~×2 per mask step); no controller failure mode triggered. |
| Laser power | **PGT** | [`MRM_PGT_LASER_BANDWIDTH_REPORT.md`](MRM_PGT_LASER_BANDWIDTH_REPORT.md) | Power-invariant by design; residual ≤ 9 mV pk-pk at ±10 %. **`kstep=3` is the HDAC floor and the best rejection setting** — the old "kstep→1" win is gone. |
| Laser power | **L2V** | [`MRM_L2V_LASER_BANDWIDTH_REPORT.md`](MRM_L2V_LASER_BANDWIDTH_REPORT.md) | **Target mode decides everything: `PEAK_RATIO` rejects ~7× better than `IADC_VALUE`** (57 vs 394 codes at ±10 %) because its target scales with live power. `adc_dead_zone` irrelevant to rejection. |

All six studies share the plant tuning coefficient **|dV/dT_amb| ≈ 5 mV/K**
(power-independent) and the same 13-bit snapped DAC model. The
[controller selection guide](../../photon/goldens/mrm/docs/MRM_CONTROLLER_SELECTION_GUIDE.md)
in the repo carries a banner noting which of its older recommendations these
studies supersede.

## Simulation fidelity (data converters)

The studies were run at **two different points on the model-fidelity axis**, and
the differences are intentional. The actuator (sweet-spot HDAC) is the
hardware-representative 13-bit snapped grid in **all six**; the **ADC / IADC**
sense path is where fidelity varies:

| Study | Optical power | ADC model | ADC full-scale | Effective ENOB |
|---|---|---|---|---|
| PGT thermal drift | 1 mW | **ideal** 16-bit | 500 µA | 16-bit (no masking) |
| L2V thermal drift | 1 mW | **ideal** 16-bit | 500 µA | 16-bit (no masking) |
| PGT laser bandwidth | 1 mW | **ideal** 16-bit | 500 µA | 16-bit (no masking) |
| L2V laser bandwidth | 1 mW | **ideal** 16-bit (`bb_fullscale_A = 2 mA`) | 500 µA | 16-bit (no masking) |
| PGT triangle | 10 mW | **production masked IADC** | 560 µA | **10-bit** (mask 6; mask 7 = 9-bit also run) |
| L2V triangle | 10 mW | **production masked IADC** | 560 µA | **9 / 8 / 7-bit** (mask 7 / 8 / 9 swept) |

Three things follow, and they matter when reading numbers *across* the table:

* **The two axes are coupled, not free.** The masked IADC is *why* the triangle
  studies run at 10 mW rather than 1 mW: with the low bits zeroed, the dither /
  signal swing at 1 mW falls below the masked LSB, so the PGT preflight checker
  flags 1 mW **BLIND**. The ideal-ADC studies have no such floor and so can sit
  at 1 mW. You cannot simply re-run a masked-IADC study at 1 mW, or an
  ideal-ADC study with the production resolution, without changing the regime.
* **ADC quantization is a first-order effect only in the masked studies.** In
  the triangle reports it *is* the headline physics — mask quantization sets the
  L2V retention floor (≈ ×2 per mask step), and the masked-LSB dither floor is
  the PGT **sense-blind apex** (F-A). In the 1 mW ideal-ADC studies that floor
  is absent by construction, so their ripple / residual numbers are *optimistic*
  about quantization relative to silicon.
* **Absolute tightness is not directly comparable across the two groups.** e.g.
  the L2V triangle apex (0.33–1.88 %) *includes* mask quantization at 10 mW,
  whereas the L2V thermal-drift ripple (ideal ADC, 1 mW) does not — the
  controller-vs-controller *ratios within each group* (and within each report)
  are the trustworthy comparisons; cross-group absolutes carry the converter
  caveat above.

The two 10 mW triangle reports are the closest to hardware (production masked
IADC); the four 1 mW reports trade converter realism for a clean, power-matched
controller comparison.

## Key cross-cutting findings

* **Both controllers have a structural laser-power invariance:** PGT because the
  Goertzel argmax is power-independent; L2V *only in `PEAK_RATIO`*, because the
  target is referenced to live broadband power. `IADC_VALUE` has no power
  reference and shows the full laser swing as ADC error.
* **Thermal tracking is slew-limited and (mostly) power-independent.** The slew
  ceiling is a DAC/timing property. The exceptions are L2V's coarse steps, whose
  acquisition margin shrinks at high power (step 56 unusable > 4 mW).
* **The sweet-spot HDAC floor pins the smallest step to 1 LSB,** removing the old
  reports' "make the step smaller" rejection lever for both controllers.

## Folder layout

```
stab/
  README.md                              this index
  MRM_PGT_THERMAL_DRIFT_REPORT.md        + §6 bandwidth-vs-power (0.5–8 mW)
  MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md   10 mW triangle (up+down), 3 failure modes
  MRM_L2V_THERMAL_DRIFT_REPORT.md        + §6 bandwidth-vs-power (0.5–8 mW)
  MRM_PGT_LASER_BANDWIDTH_REPORT.md      laser aggressor, 1 mW
  MRM_L2V_LASER_BANDWIDTH_REPORT.md      laser aggressor, 1 mW, both target modes
  figures/
    pgt_thermal_drift_analysis.png       PGT thermal 4-panel summary
    pgt_tracking_vs_drift_ovr{0,3}.png   PGT thermal sweeps (override OFF/ON)
    l2v_thermal_drift_analysis.png       L2V thermal 4-panel summary
    l2v_tracking_vs_drift.png            L2V thermal sweep
    l2v_open_loop_sweep.png              L2V 1 mW op-point sweep
    power_campaign/                      bandwidth-vs-power (0.5–8 mW)
      pgt_bandwidth_vs_power.png
      l2v_bandwidth_vs_power.png
      bandwidth_vs_power_compare.png
    laser_pgt/                           PGT laser study figures + curated waveforms
    laser_l2v/                           L2V laser study figures + curated waveforms
    waveforms/                           64 per-power thermal traces (32 PGT + 32 L2V)
    pgt_triangle/                        10 mW triangle study: 5-panels + 2 overlays
    l2v_triangle/                        10 mW triangle mask sweep: 5-panels + compare overlays
  data/
    pgt_thermal_drift_analysis.json, pgt_sweep_metrics_ovr{0,3}.csv
    l2v_thermal_drift_analysis.json, l2v_sweep_metrics.csv, l2v_open_loop_*.{json,csv}
    pgt_laser_phase{A,B,C}_summary.csv   PGT laser aggregate metrics
    l2v_laser_phase{A,B,C}_summary.csv   L2V laser aggregate metrics
    power_campaign/power_campaign_summary.json
    pgt_triangle/                        per-run metrics JSONs for the triangle study
    l2v_triangle/                        per-mask metrics JSONs (mask 7/8/9, 25→80→25 °C @ 100 K/s, 10 mW)
```
