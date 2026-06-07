# Caribou MRM Stabilization — Thermal-Drift Bandwidth Study

Self-contained documentation for the latest MRM controller temperature
(thermal-drift) aggressor study on the **coupe** ring + **sweet-spot HDAC** +
16-bit/500 µA ADC, at the **1 mW** operating point. Each report embeds its
figures from [`figures/`](figures); the underlying aggregate data is in
[`data/`](data). The full per-run traces and the generating testbenches live in
the repo under `goldens/mrm/` (see each report's *Reproduce* section).

## Reports

| Controller | Report | Headline |
|---|---|---|
| **PGT** (peak-gain tracker, extremum-seeking) | [`MRM_PGT_THERMAL_DRIFT_REPORT.md`](MRM_PGT_THERMAL_DRIFT_REPORT.md) | Max trackable drift ~100 / 250 / 750 / 1000 K/s at kstep 3/4/5/6; ~0.4× of the pure-slew limit; needs `ovr_counter=0` to acquire at high kstep. |
| **L2V** (lock-to-value, dead-zone target tracking) | [`MRM_L2V_THERMAL_DRIFT_REPORT.md`](MRM_L2V_THERMAL_DRIFT_REPORT.md) | Max trackable drift ~750 / 1250 / 2000 / 2500 K/s at 1/2/4/7 LSB; up to 0.94× of the pure-slew limit; **2.7–7.5× faster than PGT** at matched step granularity. |

Both studies share the plant tuning coefficient **|dV/dT_amb| ≈ 5 mV/K** and
the same 13-bit snapped DAC model (LSB = 0.201 mV at 1.8 V FS).

## Folder layout

```
stab/
  README.md                          this index
  MRM_PGT_THERMAL_DRIFT_REPORT.md
  MRM_L2V_THERMAL_DRIFT_REPORT.md
  figures/                           PNGs embedded by the reports
    pgt_thermal_drift_analysis.png   PGT 4-panel summary (Figure 1)
    pgt_tracking_vs_drift_ovr0.png   PGT sweep, override OFF (Figure 3)
    pgt_tracking_vs_drift_ovr3.png   PGT sweep, override ON  (Figure 2)
    pgt_tracking_grid_ovr0.png       PGT kstep x drift heatmap
    l2v_thermal_drift_analysis.png   L2V 4-panel summary (Figure 1)
    l2v_tracking_vs_drift.png        L2V sweep (Figure 3)
    l2v_tracking_grid.png            L2V step x drift heatmap
    l2v_open_loop_sweep.png          L2V 1 mW op-point sweep (Figure 2)
  data/                              aggregate metrics + analysis summaries
    pgt_thermal_drift_analysis.json
    pgt_sweep_metrics_ovr0.csv
    pgt_sweep_metrics_ovr3.csv
    l2v_thermal_drift_analysis.json
    l2v_sweep_metrics.csv
    l2v_open_loop_summary.json
    l2v_open_loop_sweep.csv
```
