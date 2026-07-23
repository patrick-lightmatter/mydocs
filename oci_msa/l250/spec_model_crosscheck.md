# Spec ↔ Model Cross-Check

**Spec:** `mydocs/oci_msa/l250/architecture_spec.md`
**Model:** `optical-serdes/scripts/oci_msa_gen2/mrm_nrz_transceiver_106g25.py` (plus the library defaults it inherits: `DigitalMmCdr`, `CtleAdaptNrz`, `AgcVpNrz`, `OffsetAdaptNrz`, `VpAdaptNrz`, `FirDacDriver`)
**Date:** 2026-07-23

## Summary

The analog chain and the loop *algorithms* (truth tables, dead-bands, accumulator semantics, de-glitch strobes, DC-ownership handover) in the spec match the reference script. The differences fall into three buckets:

1. **Intentional, validated spec-vs-model divergences** (PI resolution, `f_bound`) — the spec value is deliberate; the model still runs its own defaults. These need explicit "model default vs spec value" annotations so nobody reads the §5-2 table as a description of the simulation.
2. **Values the spec leaves TBD that the model runs concretely** (CTLE peaking range, AGC code width/step, `V_LSB` values) — worth recording as behavioral-model working points.
3. **Genuine mismatches / spec gaps** (CTLE code railing vs the stage-4 exit criterion, slow-loop rates, bring-up sequencing, §1-1 block diagram).

---

## 1. Intentional divergences (validated, need annotation only)

### 1.1 PI resolution — spec 5-bit / 32 codes over 1 UI; model default 7-bit / 128 codes

The spec's `n_pi_codes = 32`, `p_div = 512` (§5-2) is a **deliberate spec decision, not an error**. It was validated in a dedicated study, `scripts/oci_msa_gen2/pi_resolution_study_5bit.py` (outputs in `scripts/oci_msa_gen2/runs/pi_resolution_study/`), which:

- rebuilt the identical end-to-end chain at SPS = 128 so both PI grids are placement-exact;
- used **hardware-faithful PI-quantised sampling** (the reference script's `phase_ui()` pointer carries fractional `p_div` sub-code precision, which would have hidden the quantisation entirely);
- compared 7-bit (128 codes) vs 5-bit (32 codes, including the `p_div = 512` spec variant) at 0 ppm and ±200 ppm frequency offset;
- found the CDR still converges and tracks with the 5-bit PI.

The spec was updated to 5-bit only after this verification. Note the UI-domain loop dynamics are identical in both configurations: the product `f_div·p_div·cdr_width·n_pi_codes` = 2²⁷ is preserved, the per-window proportional step is `diff·1.22×10⁻⁴` UI, and `reg_max = n_pi_codes·p_div = 16 384` either way. Only the PI quantum differs (1/32 UI ≈ 294 fs vs 1/128 UI ≈ 73.5 fs).

**Remaining actions:**

- [ ] §5-2: annotate the `n_pi_codes` / `p_div` rows with the model default (128 / 128) and cite the PI-resolution study as the basis for the 5-bit spec value (§5-8 already argues achievability; it should reference the study explicitly).
- [ ] §5-2 derived-width table: the phase-accumulator row says `reg_max` is "set by `p_div·n_pi_codes` = 512·32 = 16 384" — true for the spec config; add that the model's 128·128 gives the same value.
- [ ] Reference script: `_run_rx_loops` hard-codes the 128-code space (`init_pi % 128`, `phase_ui * 128.0` in the plot helper, "pi_code (0..127)" axis). These break silently if the script is ever run at the spec's 32-code configuration — parametrise on `cdr.n_pi_codes`.

### 1.2 `f_bound` — spec 2¹⁵; model default 2²⁰

§5-6 already notes the model's historical default of 2²⁰ is "a model default, not the spec value", but the §5-2 table lists 2¹⁵ as "Default" without flagging that the reference script does **not** override it — every closed-loop result in the script's outputs runs at `f_bound = 2²⁰` (±7 813 ppm capability vs the spec's ±244 ppm sizing).

- [ ] §5-2: annotate the `f_bound` row the same way as `n_pi_codes` (spec value 2¹⁵, model default 2²⁰).

---

## 2. Spec-TBD values that are concrete in the model

The spec intentionally leaves these TBD pending hardware design (§0 conventions); recording the model's working values would make the spec self-contained for anyone reproducing the simulation.

| Quantity | Spec | Model (script) |
|---|---|---|
| CTLE peaking range (§6-6 `N_code,ctle`, `P_min`, `P_step`) | TBD | 4-bit code, 2.5 dB min, 0.5 dB/LSB ⇒ **2.5–10.0 dB**; `init_code = 7` = 6.0 dB baseline |
| AGC code / step (§6-4 `N_code,agc`, `G_step`) | TBD | 6-bit × 0.5 dB/LSB (±16 dB about mid-scale) |
| `V_LSB,vp` (§6-3) | TBD | 4 mV (8-bit DAC, 0–1020 mV span) |
| `V_LSB,off` (§6-5) | TBD | 1 mV (8-bit, satisfies `V_LSB,off < V_LSB,vp`) |
| AGC target `vp_ideal` (§6-4 `V_target`) | TBD from link budget | auto-derived from a unity-gain probe: median \|sample − mean\| |

Also: the `CtleAdaptNrz` *module* default is different from both (5-bit from 0 dB ⇒ 0–15.5 dB) — three inconsistent "defaults" exist for the peaking range.

- [ ] Add a "behavioral-model value" column or footnote for these rows in §6-3/§6-4/§6-5/§6-6.
- [ ] Reconcile eventually: 6-bit × 0.5 dB AGC = 31.5 dB span vs the §4-1 TIA hardware target of 62–80 dBΩ (18 dB span).

---

## 3. Genuine mismatches / spec gaps

### 3.1 CTLE loop rails at full scale on this channel — stage-4 exit criterion unreachable

The script documents (docstring "Expected behavior on this channel") that `h(−1)` and `h(+1)` stay positive at every peaking the 1z2p topology can reach (**topology cap ≈ 10.3 dB**), so the lag-1 sign-sign correlation never crosses zero: the peaking code climbs monotonically and **saturates at 10 dB** with persistently positive correlation. The joint TxFIR × peaking sweep optimum is likewise pinned at the cap.

Spec impact:

- [ ] §6-10 stage 4 exit criterion ("`|corr_meas| ≤ corr_deadband` for consecutive windows") never fires on an under-equalizable channel. Add a saturation/timeout exit (script practice: code railed + persistent one-sided correlation ⇒ freeze via `lock_ctle`).
- [ ] §4-2 / §6-6: note the ~10.3 dB peaking cap of the 1z2p topology (f_z/f_N = 0.25, f_p2/f_N = 2.0), and that the 6 dB baseline is *not* the optimum for the modeled channel (sweep optimum ≈ 10 dB).

### 3.2 Slow-loop decimation / shift values

| Loop | Spec default | Script actual | Spec T_LSB | Script T_LSB |
|---|---|---|---|---|
| AGC | `decimation = 4096`, `shift = 1` | `decimation = 1024`, `shift = 0` | ≥ 8192 UI | 1024 UI |
| Offset | `decimation = 2048`, `shift = 1` | `decimation = 256`, `shift = 0` | ≥ 4096 UI | 256 UI |
| CTLE | `decimation = 2048`, `shift = 1`, dead-band 0.02 (≈ 0.9 σ) | `decimation = 512`, `shift = 0`, dead-band 0.10 (≈ 2.3 σ at 512 UI) | ≥ 4096 UI | 512 UI |

The script's faster values are a deliberate simulation-length accommodation (its docstring: the module-default offset rate "would need ~82k UI, far more than the ~33k UI available here"). But:

- §6-9's separation claims ("offset ~128× slower than Vp", "AGC ≥ 8192 UI/LSB") do not describe the model as run; the script's ladder is offset (256) → CTLE (512) → AGC (1024) UI per vote, with the nesting argued via sub-LSB Vp settling (~30× margin) rather than a decade of decimation.
- §6-6's dead-band sizing narrative (σ ≈ 0.022, dead-band at 0.9 σ) doesn't match the script's operating point (σ ≈ 0.044, 2.3 σ).

- [ ] Note in §6-9 that the reference simulation runs an acquisition-gear-shifted ladder (which §6-9's own gear-shift guidance sanctions) and give both value sets.

### 3.3 Bring-up sequencing

Spec §6-10 stages the loops on lock/settle criteria with AGC last (frozen until stage 5). The script instead runs **CDR + Vp + AGC live from UI 0**, engages offset at fixed UI 2000 (simultaneous SE→diff mean freeze — this part matches stage 3's DCOC handover), and CTLE at fixed UI 8000. There is no lock-detector gating anywhere (`CdrLockDetector` is never instantiated), and no signal-valid gate / CID-coast exercise (§5-11, §5-12 are unvalidated by this script).

- [ ] Either add a §6-10 note that the behavioral model approximates the staging with fixed engage timers and runs AGC continuously, or align the script with the staged sequence. Flag §5-11/§5-12 and the lock detector as not yet exercised end-to-end.

### 3.4 §1-1 block diagram omits the CTLE and three of the four adaptation loops

The RX subgraph shows PD → TIA → slicers; the script's chain is TIA → **1z2p CTLE (adaptive, waveform bank)** → **AGC gain** → **− offset_v** → slicers, and the digital-loops box shows only the CDR (no Vp/AGC/offset/CTLE loops). The diagram also labels "pi_code 0…31", which is the spec value — fine, but see §1.1 annotation. The §6-10 text diagram already has the CTLE; the top-level mermaid should match it.

- [ ] Update the §1-1 mermaid.

### 3.5 Minor / informational

- `init_pi`: spec default 0; script uses 8 — deliberate, to make the CDR pull-in visible. Likewise the injected AGC (−6 codes) and offset (+20 codes) initial errors vs the spec's mid-scale presets are demonstration artifacts, not presets.
- Laser / drive interface: +10 dBm CW at 1311 nm (`MRM_P_IN_W = 10 mW`), `DRIVE_SCALE ≈ 0.186`, mid-slope `v_dc` from `static_power()` — §3-2 covers this only qualitatively; no spec row for laser power.
- Pattern: script uses PRBS-15 (§1-3's modulation row just says "PRBS, Others").
- `init_mean`: spec says "set to TIA operating point if known"; script seeds it from the unity-gain probe mean scaled by the initial AGC gain — consistent, worth a line in §6-3.
