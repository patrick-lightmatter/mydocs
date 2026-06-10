# Caribou MRM Stabilization — Bandwidth & Aggressor Studies

Self-contained documentation for the latest MRM controller aggressor studies on
the **coupe** ring + **sweet-spot HDAC** (LSB = 0.201 mV at 1.8 V FS) +
16-bit/500 µA ADC. Two aggressors (ambient **thermal drift** and **laser power**)
× two controllers (**PGT** extremum-seeking, **L2V** lock-to-value). Each report
embeds its figures from [`figures/`](figures); aggregate data is in
[`data/`](data). Full per-run traces and the generating testbenches live in the
repo under `goldens/mrm/` (see each report's *Reproduce* section).

## Reports

| Aggressor | Controller | Report | Headline |
|---|---|---|---|
| Thermal drift | **PGT** | [`MRM_PGT_THERMAL_DRIFT_REPORT.md`](MRM_PGT_THERMAL_DRIFT_REPORT.md) | Max trackable drift ~100/250/750/1000 K/s at kstep 3/4/5/6; ~0.4× of the pure-slew limit; needs `ovr_counter=0` to acquire. **Power-independent 0.5–8 mW.** |
| Thermal drift (triangle) | **PGT** | [`MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md`](MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md) | 10 mW triangle (up + down) study. Holds 25→80→25 °C @ 100 K/s (apex loss 12.6 %, round-trip −19.5 %) at kstep=7, mask=6, dither=48 mV. Three named failure modes: **sense-blind apex, actuator saturation, hill-climb step too small.** |
| Thermal drift | **L2V** | [`MRM_L2V_THERMAL_DRIFT_REPORT.md`](MRM_L2V_THERMAL_DRIFT_REPORT.md) | Max trackable ~750/1250/2000/2500 K/s at 1/2/4/7 LSB; up to 0.94× pure-slew; **2.7–7.5× faster than PGT**. Small steps power-independent; **step 56 collapses above ~4 mW**. |
| Laser power | **PGT** | [`MRM_PGT_LASER_BANDWIDTH_REPORT.md`](MRM_PGT_LASER_BANDWIDTH_REPORT.md) | Power-invariant by design; residual ≤ 9 mV pk-pk at ±10 %. **`kstep=3` is the HDAC floor and the best rejection setting** — the old "kstep→1" win is gone. |
| Laser power | **L2V** | [`MRM_L2V_LASER_BANDWIDTH_REPORT.md`](MRM_L2V_LASER_BANDWIDTH_REPORT.md) | **Target mode decides everything: `PEAK_RATIO` rejects ~7× better than `IADC_VALUE`** (57 vs 394 codes at ±10 %) because its target scales with live power. `adc_dead_zone` irrelevant to rejection. |

All four studies share the plant tuning coefficient **|dV/dT_amb| ≈ 5 mV/K**
(power-independent) and the same 13-bit snapped DAC model. The
[controller selection guide](../../photon/goldens/mrm/docs/MRM_CONTROLLER_SELECTION_GUIDE.md)
in the repo carries a banner noting which of its older recommendations these
studies supersede.

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
  data/
    pgt_thermal_drift_analysis.json, pgt_sweep_metrics_ovr{0,3}.csv
    l2v_thermal_drift_analysis.json, l2v_sweep_metrics.csv, l2v_open_loop_*.{json,csv}
    pgt_laser_phase{A,B,C}_summary.csv   PGT laser aggregate metrics
    l2v_laser_phase{A,B,C}_summary.csv   L2V laser aggregate metrics
    power_campaign/power_campaign_summary.json
    pgt_triangle/                        per-run metrics JSONs for the triangle study
```
