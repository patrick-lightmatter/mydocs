# Spec ↔ Model Cross-Check

**Spec:** `mydocs/oci_msa/l250/architecture_spec.md`
**Model:** `optical-serdes/scripts/oci_msa_gen2/mrm_nrz_transceiver_106g25.py` (plus the library defaults it inherits: `DigitalMmCdr`, `CtleAdaptNrz`, `AgcVpNrz`, `OffsetAdaptNrz`, `VpAdaptNrz`, `FirDacDriver`)
**Round 1 date:** 2026-07-23
**Round 2 date:** 2026-07-23 (post §4/§6-4/§6-6 spec revision, post PI-resolution code fix)

## Summary

The analog chain and the loop *algorithms* (truth tables, dead-bands, accumulator semantics, de-glitch strobes, DC-ownership handover) in the spec match the reference script. The differences fall into four buckets:

1. **Intentional, validated spec-vs-model divergences** (PI resolution, `f_bound`) — the spec value is deliberate; the model still runs its own defaults. These need explicit "model default vs spec value" annotations so nobody reads the §5-2 table as a description of the simulation.
2. **Values the spec leaves TBD that the model runs concretely** (AGC code width, `V_LSB` values) — worth recording as behavioral-model working points.
3. **Genuine mismatches / spec gaps** (CTLE code railing vs the stage-4 exit criterion, slow-loop rates, bring-up sequencing, §1-1 block diagram).
4. **[Round 2] A newly-committed spec value that directly conflicts with the model** — §4-1/§6-6 now commit the CTLE hardware peaking range to **0–2 dB** (was TBD in round 1), but the model's fixed baseline (6 dB) and RX-loop adaptation range (2.5–10 dB) both lie entirely or mostly outside that window. This is the most significant finding of round 2 — see §4 below.

## Round 1 → Round 2 status changes

- ✅ **Resolved**: the script's hard-coded 128-code PI literals (§1.1 action 3) were fixed this session — `_run_rx_loops` now parametrises `n_pi_codes`/`pi_span_ui`/`p_div`/`f_bound` and derives `init_pi % n_pi_codes`, the plot labels, and the UI-offset print from the resolved CDR config instead of literals. Verified with a full rerun: `OVERALL: PASS`, `BER = 0.000e+00`, `init_pi = 8 codes (of 128) (0.062 UI offset)` printed correctly.
- ✅ **Resolved (spec-side)**: §6-4's AGC `G_step` row is no longer TBD — it now reads "0.5 dB / LSB (§4-1)", which **matches the script's `agc_step_db = 0.5`** exactly. Remove this from the round-1 "spec-TBD, model concrete" bucket.
- 🔶 **Changed, new mismatch**: §6-6's CTLE `P_min`/`P_step` row is no longer TBD either — it now reads "0 dB, 1 dB/LSB (§4-1)". This used to be bucket-2 (spec TBD, model runs 2.5 dB / 0.5 dB-step concretely); now that the spec has committed to *different* concrete numbers, it's a bucket-3/4 real conflict, not just a documentation gap. See §4.

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
- [x] ~~Reference script: `_run_rx_loops` hard-codes the 128-code space...~~ **Fixed 2026-07-23**: `n_pi_codes`, `pi_span_ui`, `p_div`, `f_bound` are now optional kwargs on `_run_rx_loops`, resolved once via a constructed `DigitalMmCdr` and threaded through `init_pi % cdr.n_pi_codes`, the returned `loops` dict, the `main()` summary print, and the `_plot_rx_loops_pi_code` labels/scaling. Full rerun confirms no behavior change at the (still-default) 128-code configuration: `OVERALL: PASS`, `BER = 0.000e+00`.

### 1.2 `f_bound` — spec 2¹⁵; model default 2²⁰

§5-6 already notes the model's historical default of 2²⁰ is "a model default, not the spec value", but the §5-2 table lists 2¹⁵ as "Default" without flagging that the reference script does **not** override it — every closed-loop result in the script's outputs runs at `f_bound = 2²⁰` (±7 813 ppm capability vs the spec's ±244 ppm sizing).

- [ ] §5-2: annotate the `f_bound` row the same way as `n_pi_codes` (spec value 2¹⁵, model default 2²⁰).

---

## 2. Spec-TBD values that are concrete in the model

The spec intentionally leaves these TBD pending hardware design (§0 conventions); recording the model's working values would make the spec self-contained for anyone reproducing the simulation. (CTLE peaking range and AGC `G_step` have moved out of this bucket as of round 2 — see §1 status changes and §4.)

| Quantity | Spec | Model (script) |
|---|---|---|
| AGC code width (§6-4 `N_code,agc`) | TBD | 6-bit (64 codes) |
| `V_LSB,vp` (§6-3) | TBD | 4 mV (8-bit DAC, 0–1020 mV span) |
| `V_LSB,off` (§6-5) | TBD | 1 mV (8-bit, satisfies `V_LSB,off < V_LSB,vp`) |
| AGC target `vp_ideal` (§6-4 `V_target`) | TBD from link budget | auto-derived from a unity-gain probe: median \|sample − mean\| |

- [ ] Add a "behavioral-model value" column or footnote for these rows in §6-3/§6-4/§6-5.

---

## 3. [Round 2 — RESOLVED 2026-07-23] CTLE peaking range: spec now commits 0–2 dB; model runs 6 dB fixed / 2.5–10 dB adaptive — headline finding

**Resolution:** rather than re-target the model to a 0–2 dB hardware range, the spec was updated to adopt the model's actual values as the (explicitly-labeled) simulation-derived working point: §4-1 and §6-6 now read `P_min = 2.5 dB`, `P_step = 0.5 dB`, `N_code,ctle = 4-bit` (16 codes) ⇒ **2.5–10.0 dB**, matching `CtleAdaptNrz`'s defaults exactly, with the 6.0 dB non-adaptive baseline called out as sitting inside that range (code 7). Both §4-1 and §6-6 now flag this explicitly as *"simulation-derived, not yet a hardware-signed-off target"* and cross-reference `simulation_revisit_items.md` for the still-open question of whether the outer-pole placement needed to reach the ≈10.3 dB topology ceiling is physically realizable — the action items below are superseded by that tracking item rather than closed outright.

§4-1 previously left the CTLE peaking range TBD (round 1 bucket 2). It has since been rewritten into a merged TIA+CTLE+AGC macro spec (§4) and now **commits concrete numbers**:

```235:236:mydocs/oci_msa/l250/architecture_spec.md
| CTLE peaking range | `P_min`–`P_max` | TBD | **0–2 dB** | First-cut hardware target (PMA doc §4-6, `TBD_from_sim_sweep`); spanned by the CTLE adaptation loop (§6-6, `P_min`/`P_step`) |
| CTLE peaking step | `P_step` | TBD | **1 dB** | Same quantity as `P_step` in the §6-6 CTLE parameter table; `N_code,ctle` (code width) remains TBD |
```

§6-6 echoes this ("only 3 codes span the 0–2 dB range at this step"), implying an intended `N_code,ctle` of ~2 bits (codes 0–2 or 0–3).

**The model does not reflect this anywhere:**

- The **fixed, non-adaptive CTLE baseline** used for nearly the entire script (tp35_ctle waveform, all eye diagrams, the CTLE Bode plot, the end-to-end frequency-response characterisation, and the TX-FIR-only optimisation stage) is `CTLE_PEAKING_DB = 6.0` dB — 3× the spec's committed `P_max`.
- The **RX-loop CTLE adaptation** (`_run_rx_loops` defaults: `ctle_code_bits = 4`, `ctle_peak_min_db = 2.5`, `ctle_peak_step_db = 0.5`) spans **2.5–10.0 dB** over 16 codes — entirely above the spec's 0–2 dB window, both in minimum, step size (0.5 dB vs 1 dB), and code count (16 vs the spec's implied ~3–4).

**Why this matters quantitatively — the model's own sweep data shows the gap is large, not cosmetic.** The joint TxFIR×peaking sweep (`ctle_peaking_sweep.png` / run log) reports, per peaking value, the best achievable tp35_ctle worst-case eye opening after re-optimising the TX FIR taps at each peaking:

| CTLE peaking | Best eye opening (optimal TX FIR) |
|---|---|
| 0 dB (no CTLE) | +77.6 mV |
| 1 dB | +80.6 mV |
| **2 dB (spec `P_max`)** | **+90.1 mV** |
| 6 dB (model's fixed baseline) | +147.4 mV |
| 10 dB (model's adaptation-loop ceiling ≈ 1z2p topology cap ~10.3 dB) | +234.2 mV |

If the real hardware CTLE tops out at 2 dB as now specified, the TX-FIR-only compensation this model already computed caps the achievable eye opening at **~90 mV — about 38% of the 234 mV the model's chain otherwise finds achievable up at the topology cap**, and 61% of what the fixed 6 dB baseline (used throughout the rest of the script) delivers. Since §1-2 point 2 commits this architecture to **linear equalization, CTLE only — no DFE, no FFE taps**, there is no other RX-side lever to close that gap; the only other knob is the TX FIR (already re-optimised in this table) and the fixed analog chain (driver/MRM/fiber/PD/TIA bandwidths).

**Action items (original, kept for history):**

- [x] ~~Either revisit the 0–2 dB hardware target... or re-run/re-validate at a hardware-realistic 0–2 dB CTLE...~~ **Resolved by adopting the model's range into the spec** (2.5–10.0 dB) rather than constraining the model to 0–2 dB. The realizability question moves to `simulation_revisit_items.md` §1 (outer-pole placement).
- [x] ~~Reconcile the three now-conflicting CTLE numbers...~~ **Resolved**: spec `P_min/P_step/N_code,ctle` now equal the model's `peak_min_db=2.5`/`peak_step_db=0.5`/`code_bits=4` exactly. `CTLE_PEAKING_DB = 6.0` is documented in §4-2 as the fixed non-adaptive baseline, explicitly noted as *not* the sweep optimum.
- [ ] Still open — round-1 finding §5.1 (CTLE code railing / stage-4 exit criterion): even at 2.5–10.0 dB the code rails at 10.0 dB on this channel (persistent positive correlation, topology cap ≈10.3 dB), so the §6-10 stage-4 exit criterion still needs a saturation/timeout path. Unaffected by this resolution.

## 4. AGC gain-code range is not centered on the spec's transimpedance target

§4-1 also now commits a transimpedance gain range/step (`Z_T,min`–`Z_T,max` = 62–80 dBΩ, `G_step` = 0.5 dB), and §6-4 correctly cross-references `G_step = 0.5 dB` — this **does** match the model's `agc_step_db = 0.5`. However, the model's fixed baseline transimpedance is `TIA_ZT_OHM = 1000 Ω` = **60 dBΩ**, and the AGC gain code is centered (mid-scale) on that baseline:

```text
code_bits = 6 → code_mid = 1 << 5 = 32, codes 0..63
gain range: (0 − 32)·0.5 = −16.0 dB  →  (63 − 32)·0.5 = +15.5 dB
absolute range: 60 − 16.0 = 44.0 dBΩ  →  60 + 15.5 = 75.5 dBΩ
```

So the model's achievable AGC range (**44.0–75.5 dBΩ**) sits mostly *below* the spec's committed 62–80 dBΩ target — it undershoots the top by 4.5 dB and extends 18 dB below the bottom of the target window it will never need. The fixed baseline `Z_T` needs to move up by roughly the target window's mid-point minus 60 dBΩ (≈ +11 dB, e.g. `TIA_ZT_OHM ≈ 3550 Ω` ⇒ 71 dBΩ) for the AGC code range to actually straddle 62–80 dBΩ, or the AGC code's `init_code`/mid-scale mapping needs to be decoupled from `code_mid` so it can be biased toward the top of the range.

- [ ] Re-center the model's `TIA_ZT_OHM` baseline (or the AGC's effective 0 dB reference) so the ±`code_mid`-scaled range actually covers 62–80 dBΩ.

---

## 5. Genuine mismatches / spec gaps

### 5.1 CTLE loop rails at full scale on this channel — stage-4 exit criterion unreachable

The script documents (docstring "Expected behavior on this channel") that `h(−1)` and `h(+1)` stay positive at every peaking the 1z2p topology can reach (**topology cap ≈ 10.3 dB**), so the lag-1 sign-sign correlation never crosses zero: the peaking code climbs monotonically and **saturates at 10 dB** with persistently positive correlation. The joint TxFIR × peaking sweep optimum is likewise pinned at the cap.

Spec impact:

- [ ] §6-10 stage 4 exit criterion ("`|corr_meas| ≤ corr_deadband` for consecutive windows") never fires on an under-equalizable channel. Add a saturation/timeout exit (script practice: code railed + persistent one-sided correlation ⇒ freeze via `lock_ctle`).
- [ ] §4-2 / §6-6: note the ~10.3 dB peaking cap of the 1z2p topology (f_z/f_N = 0.25, f_p2/f_N = 2.0), and that the 6 dB baseline is *not* the optimum for the modeled channel (sweep optimum ≈ 10 dB).

### 5.2 Slow-loop decimation / shift values

| Loop | Spec default | Script actual | Spec T_LSB | Script T_LSB |
|---|---|---|---|---|
| AGC | `decimation = 4096`, `shift = 1` | `decimation = 1024`, `shift = 0` | ≥ 8192 UI | 1024 UI |
| Offset | `decimation = 2048`, `shift = 1` | `decimation = 256`, `shift = 0` | ≥ 4096 UI | 256 UI |
| CTLE | `decimation = 2048`, `shift = 1`, dead-band 0.02 (≈ 0.9 σ) | `decimation = 512`, `shift = 0`, dead-band 0.10 (≈ 2.3 σ at 512 UI) | ≥ 4096 UI | 512 UI |

The script's faster values are a deliberate simulation-length accommodation (its docstring: the module-default offset rate "would need ~82k UI, far more than the ~33k UI available here"). But:

- §6-9's separation claims ("offset ~128× slower than Vp", "AGC ≥ 8192 UI/LSB") do not describe the model as run; the script's ladder is offset (256) → CTLE (512) → AGC (1024) UI per vote, with the nesting argued via sub-LSB Vp settling (~30× margin) rather than a decade of decimation.
- §6-6's dead-band sizing narrative (σ ≈ 0.022, dead-band at 0.9 σ) doesn't match the script's operating point (σ ≈ 0.044, 2.3 σ).

- [ ] Note in §6-9 that the reference simulation runs an acquisition-gear-shifted ladder (which §6-9's own gear-shift guidance sanctions) and give both value sets.

### 5.3 Bring-up sequencing

Spec §6-10 stages the loops on lock/settle criteria with AGC last (frozen until stage 5). The script instead runs **CDR + Vp + AGC live from UI 0**, engages offset at fixed UI 2000 (simultaneous SE→diff mean freeze — this part matches stage 3's DCOC handover), and CTLE at fixed UI 8000. There is no lock-detector gating anywhere (`CdrLockDetector` is never instantiated), and no signal-valid gate / CID-coast exercise (§5-11, §5-12 are unvalidated by this script).

- [ ] Either add a §6-10 note that the behavioral model approximates the staging with fixed engage timers and runs AGC continuously, or align the script with the staged sequence. Flag §5-11/§5-12 and the lock detector as not yet exercised end-to-end.

### 5.4 §1-1 block diagram omits the CTLE and three of the four adaptation loops

The RX subgraph shows PD → TIA → slicers; the script's chain is TIA → **1z2p CTLE (adaptive, waveform bank)** → **AGC gain** → **− offset_v** → slicers, and the digital-loops box shows only the CDR (no Vp/AGC/offset/CTLE loops). The diagram also labels "pi_code 0…31", which is the spec value — fine, but see §1.1 annotation. The §6-10 text diagram already has the CTLE; the top-level mermaid should match it.

- [ ] Update the §1-1 mermaid.

### 5.5 Minor / informational

- `init_pi`: spec default 0; script uses 8 — deliberate, to make the CDR pull-in visible. Likewise the injected AGC (−6 codes) and offset (+20 codes) initial errors vs the spec's mid-scale presets are demonstration artifacts, not presets.
- Laser / drive interface: +10 dBm CW at 1311 nm (`MRM_P_IN_W = 10 mW`), `DRIVE_SCALE ≈ 0.186`, mid-slope `v_dc` from `static_power()` — §3-2 covers this only qualitatively; no spec row for laser power.
- Pattern: script uses PRBS-15 (§1-3's modulation row just says "PRBS, Others").
- `init_mean`: spec says "set to TIA operating point if known"; script seeds it from the unity-gain probe mean scaled by the initial AGC gain — consistent, worth a line in §6-3.
