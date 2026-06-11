# MRM L2V Triangle-Aggressor Report -- coupe + sweet-spot HDAC, 10 mW

Companion to [`MRM_L2V_THERMAL_DRIFT_REPORT.md`](MRM_L2V_THERMAL_DRIFT_REPORT.md)
(monotonic drift, 1 mW, step x rate sweep) and to
[`MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md`](MRM_PGT_TRIANGLE_AGGRESSOR_REPORT.md)
(PGT triangle at the same operating point). This report measures how well the
**L2V (lock-to-value)** controller holds drop-port retention through a symmetric
ambient triangle at **10 mW** as the masked-IADC ENOB is varied.

Where the PGT triangle study was a **multi-knob hunt for failure modes** at a
105 C apex (sense-blind apex, actuator saturation, hill-climb step too small),
the L2V triangle at the same 80 C apex is in the **deeply easy regime** for
the controller. Tracking is driven by direct ADC error rather than slope sense,
so there is no apex-blindness equivalent; the slew rate (100 K/s) is more than
20x below the L2V monotonic ceiling at the smallest step (the 1 mW monotonic
report measured ~750 K/s at 1 LSB). The only stress visible at this operating
point is **mask quantization**, which sets a retention floor that scales
roughly x2 per mask step.

## Sources

| Artifact | This folder | Regenerated at (repo) |
|---|---|---|
| Mask 7 / 8 / 9 5-panel overviews | [`figures/l2v_triangle/mask{7,8,9}_25to80_100Kps_5panel.png`](figures/l2v_triangle/) | `goldens/mrm/output/l2v_thermal_aggressor_10mW/triangle_25to80_100Kps_mask{7,8,9}/l2v_thermal_drift.png` |
| Mask 7 / 8 / 9 closed-vs-frozen overlays | [`figures/l2v_triangle/mask{7,8,9}_25to80_100Kps_compare.png`](figures/l2v_triangle/) | `goldens/mrm/output/l2v_thermal_aggressor_10mW/triangle_25to80_100Kps_mask{7,8,9}/l2v_thermal_drift_compare.png` |
| Three-mask overlay | [`figures/l2v_triangle/mask_compare_25to80_100Kps.png`](figures/l2v_triangle/mask_compare_25to80_100Kps.png) | `goldens/mrm/output/l2v_thermal_aggressor_10mW/mask_compare_25to80_100Kps.png` |
| Smoke (peak 30 C) 5-panel | [`figures/l2v_triangle/smoke_25to30_100Kps_mask9_5panel.png`](figures/l2v_triangle/smoke_25to30_100Kps_mask9_5panel.png) | `goldens/mrm/output/l2v_thermal_aggressor_10mW_smoke/triangle_25to30_100Kps_mask9/l2v_thermal_drift.png` |
| Per-mask metrics JSONs | [`data/l2v_triangle/mask{7,8,9}_25to80_100Kps_metrics.json`](data/l2v_triangle/) | matching `l2v_thermal_drift_metrics.json` per run dir |
| Run summary | n/a | `goldens/mrm/output/l2v_thermal_aggressor_10mW/SUMMARY.md` |
| Plan + bench-mechanics audit | n/a | `goldens/mrm/docs/L2V_THERMAL_AGGRESSOR_PLAN.md` |

The full per-tick traces (each 22201 ticks, ~1.5 MB) live with the run dirs in
the repo; only the metrics JSONs are mirrored here.

---

## Executive summary

1. **L2V at 10 mW holds 25 -> 80 -> 25 C @ 100 K/s + 10 ms settle** for masks
   {7, 8, 9} (effective ENOB 9, 8, 7 bits on the 16-bit datapath). All three
   runs track; none saturate the heater; drop retention stays within 3 % of
   the pre-drift baseline.
2. **Mask quantization sets the retention floor**, not slew or sensing. Drop
   loss RMS scales roughly x2.6 per mask step (0.29 % -> 0.78 % -> 1.91 %),
   tracking the doubling of the mask quantum (128 -> 256 -> 512 codes) plus
   a small contribution from the up-to-one-quantum target-snap shift.
3. **L2V is 5-40x tighter than PGT at the same operating point.** The PGT
   triangle at 25 -> 80 -> 25 C @ 100 K/s, 10 mW, with its winning config
   reports apex drop-loss RMS **12.6 %**; the L2V mask 7 / 8 / 9 apex values
   are **0.33 % / 0.81 % / 1.88 %**. PGT's failure-finding triangle was at
   105 C apex; L2V at 80 C is in the deeply easy regime by comparison.
4. **No controller failure mode triggered.** The PGT triangle isolated three
   (sense-blind apex, actuator saturation, hill-climb step too small). For
   L2V at 10 mW / 80 C apex / 100 K/s, none of those preconditions are
   present: L2V senses ADC error directly (no Goertzel slope to flatten), the
   heater never goes below 360 mV (well above 0 V floor), and the bang-bang
   step is 1 LSB by design.
5. **Three bench-mechanics defects had to be fixed before the campaign was
   trustworthy.** They are documented as named bench modes (M-A target snap,
   M-B drop_A storage, M-C per-step ambient drive) in section 4 because each
   is a foot-gun for any future masked-ADC L2V campaign.
6. **Operating envelope (validated):** 25 -> 80 C symmetric triangle, 100 K/s,
   10 mW, ENOB >= 7 bits at the IADC. Open levers: higher apex (105 C is
   uncharted on L2V), faster ramp (this campaign was 25x below the slew
   ceiling at 1 LSB step), per-power init derivation, lower laser power.

---

## 1. Setup

The plant, DAC, and ADC are identical to the PGT triangle study and the L2V
monotonic study: `coupe_mrm_block` (TSMC Caribou ring) on the sweet-spot HDAC
(13-bit physical grid, 1.8 V FS, 1.62 V clamp, LSB = 0.201 mV) with the
production 16-bit / 560 uA masked IADC. What changes vs the L2V monotonic
study at 1 mW:

- **10 mW, not 1 mW.** Pairs the L2V campaign with the PGT triangle for a
  direct controller-vs-controller comparison at the same operating point.
- **Triangle, not monotonic.** The bench gained `--drift-profile triangle`
  with `--triangle-peak-C`, `--triangle-rate-K-per-s`, `--triangle-settle-ms`,
  driving ambient via `sknetwork.set_ambient_temperature()` once per controller
  tick (per-tick, **not** per Skadi step -- see section 4 / M-C).
- **Mask sweep, not step sweep.** The campaign sweeps `--adc-mask-bits` over
  {7, 8, 9}, fixing the controller step at 1 LSB (`--step-size-acq 8`,
  `--step-size-track 8`, `--fine-switch-frac 0.0`) so the only varying
  resolution knob is the IADC ENOB at the slope sense.

Fixed knobs (matched to the PGT-triangle ctrl-dec to keep simulation cost
comparable):

| knob | value | rationale |
|---|---|---|
| `--ctrl-dec` | 1600 (50 us cadence) | matches PGT triangle; >= 1 thermal tau |
| `--time-step` | 31.25 ns | matches PGT triangle |
| `--step-size-acq` / `--step-size-track` | 8 / 8 | 1 LSB on the 13-bit snapped HDAC; sub-LSB is inert |
| `--fine-switch-frac` | 0.0 | single fine-step regime; no coarse acquisition phase |
| `--adc-dead-zone` | 2 (half = 2 codes) | unchanged from L2V default |
| `--n-acq-ticks` | 600 | 30 ms acquisition; lock confirmed by tick 120 in all three runs |
| `--triangle-peak-C` | 80 | matches PGT-triangle envelope |
| `--triangle-rate-K-per-s` | 100 | 25x below the L2V monotonic ceiling at 1 LSB |
| `--triangle-settle-ms` | 10 | matches PGT triangle |

Each run uses its **own** per-mask open-loop sweep summary
(`mrm_l2v_open_loop_10mW_mask{7,8,9}/`); a single shared sweep at one mask was
the original plan and would have broken for the other two via off-grid target.
See section 4 / M-A.

The headline tracking metric is **drop loss** (percentage below the
post-acquisition, pre-drift drop current `drop_ref_A`), mirroring the PGT
triangle report. The L2V `in_dead_zone` flag is reported only as a diagnostic;
under masks 7/8/9 the +-2-code dead zone is sub-quantum (mask quantum is
128/256/512 codes), so the loop steps in/out of the zone every tick and the
metric reads ~84 % even when drop is held within < 1 % of the baseline.

---

@@SEC2@@
