# L2V Thermal Aggressor Study Status

**Date**: 2026-06-10  
**Operator**: Cursor Agent (handoff from PGT campaign)

## Objective
Mirror the PGT thermal-aggressor study for the **L2V** (Lock-to-Value) controller at **10 mW**. Characterize ADC ENOB floor under triangular ambient thermal aggression (25 → 80 → 25 °C @ 100 K/s).

## Status: RUNS IN PROGRESS

### Completed Prerequisites
- ✅ **P1**: Generated 10 mW L2V open-loop sweep summary
  - Peak ADC: 23040 @ 0.695 V
  - Target IADC: 17280 (96/128 of peak)
  - Hot-start V: 0.730 V
  - Mask bits: 9 (7-bit ENOB for sweep generation)

### Completed Bench Modifications
- ✅ **B1**: Plumbed `--adc-mask-bits` through L2V closed-loop bench
  - Added CLI args `--adc-mask-bits` and `--adc-fs-A`
  - Threaded mask_bits through all `current_to_adc_code` calls
  - Forwarded to frozen-reference subprocess
- ✅ **B2**: Plumbed `--adc-mask-bits` through L2V open-loop bench  
  - Added CLI arg `--adc-mask-bits` (default=7)
  - Persisted to summary JSON
- ✅ **B3**: Added triangle thermal profile to L2V drift bench
  - Imported `skadi.network as sknetwork`
  - Copied `_build_triangle_profile` from PGT bench
  - Modified drift runners to accept `ambient_func` and step per-tick
  - Added phase tracking to records
- ✅ **B4**: Added per-phase metrics to L2V drift bench
  - Per-phase `drift_in_dz_frac` and `drift_err_rms_codes`
  - Apex metrics (last 5% ramp_up + first 5% ramp_down)
  - Roundtrip residual (mean error in settle phase)
  - Triangle metadata in metrics JSON
  - Phase boundary visualization in plots

### Running Simulations

| Run | ADC Mask | ENOB | Triangle Profile | PID | Status |
|-----|----------|------|------------------|-----|--------|
| **L7** | 7 | 9-bit | 25→80→25 °C @ 100 K/s | 3295310 | RUNNING |
| **L8** | 8 | 8-bit | 25→80→25 °C @ 100 K/s | 3295312 | RUNNING |
| **L9** | 9 | 7-bit | 25→80→25 °C @ 100 K/s | 3295314 | RUNNING |

**Common config**:
- `--step-size-acq 8`, `--step-size-track 8` (no coarse phase, `--fine-switch-frac 0.0`)
- `--adc-dead-zone 2` (±2 codes)
- `--time-step 31.25e-9` (matches PGT)
- `--ctrl-dec 1600` (50 µs decision cadence, max usable)
- `--n-acq-ticks 600` (~30 ms acquisition)
- `--n-drift-ticks 22500` (~1.125 s sim time = full triangle + settle)
- `--include-frozen-reference` (for comparison overlay)

**Estimated completion**: ~3 hours per run (based on PGT empirical wall-time).

### Output Locations
- Open-loop sweep: `goldens/mrm/output/mrm_l2v_open_loop_10mW/`
- Triangle runs: `goldens/mrm/output/l2v_thermal_aggressor_10mW/triangle_25to80_100Kps_mask{7,8,9}/`
- Per-run artifacts:
  - `l2v_thermal_drift.png` (5-panel overview)
  - `l2v_thermal_drift_compare.png` (closed-loop vs frozen-DAC overlay)
  - `l2v_thermal_drift_trace.csv` (per-tick telemetry)
  - `l2v_thermal_drift_metrics.json` (summary + per-phase metrics)
  - `frozen/l2v_thermal_drift_frozen_trace.csv` (frozen-DAC reference)

### Next Steps
1. Monitor runs for completion (~3h)
2. Verify all runs produced:
   - Phase-labeled plots with vlines/shading
   - Per-phase metrics in JSON
   - Frozen-reference comparison overlay
3. Generate `SUMMARY.md` with:
   - 3-row metrics table (mask, drift_in_dz_frac by phase, apex/roundtrip residual)
   - Verdict per run (tracked / marginal / lost lock)
   - Threshold determination: mask=9 feasible or not?
4. Copy final report + figures to `mydocs/caribou/stab/`

## Reference
- **Plan**: `goldens/mrm/docs/L2V_THERMAL_AGGRESSOR_PLAN.md`
- **PGT Report**: `mydocs/caribou/stab/MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md`
- **Methodology Skill**: `agents/skills/pgt-thermal-aggressor-sweep/SKILL.md`
