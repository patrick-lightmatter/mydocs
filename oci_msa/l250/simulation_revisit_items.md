# L250 — Items to Revisit in Simulation

Working punch-list of places where the behavioral simulation model (or the architecture spec derived from it) makes an assumption that is probably **not physically realizable** or otherwise needs re-checking before it is trusted for architecture sign-off. This is a tracking document, not a spec — nothing here is authoritative until it is resolved and folded back into `architecture_spec.md` (or explicitly dropped).

Status values: **Open** (not yet investigated) · **In progress** · **Resolved** (folded back into the spec, with a note here for history).

---

## 1. CTLE outer pole placed at 106.25 GHz (= Nyquist × 2) is probably not realizable

**Status:** Open — flagged 2026-07-21.

**Where it shows up:** the behavioral model's fixed CTLE baseline (spec §4-2) is built with a 1-zero/2-pole peaking factory that places:

- zero at `f_z_ratio × f_Nyq` = 0.25 × 53.125 GHz = 13.28 GHz
- outer pole at `f_p2_ratio × f_Nyq` = 2.0 × 53.125 GHz = **106.25 GHz**
- inner pole solved analytically to hit a +6 dB peaking target at Nyquist

**Concern:** a real pole at 106.25 GHz implies an analog corner running at the full baud rate on top of whatever bandwidth the TIA, driver, and MRM/PD already consume. That is a very aggressive corner for a peaking stage specifically (as opposed to the "main" bandwidth-limiting elements), and may not be achievable in the target process at reasonable power/area — this needs a reality check against actual device/process bandwidth limits before the `f_p2_ratio = 2.0` default is treated as a real architecture number rather than a curve-fitting knob.

**Why it matters:** the whole point of this pole (and `f_z_ratio`) is to hit a peaking *shape* target (+6 dB at Nyquist in the current baseline; TBD range in the adaptive loop per spec §6-6). If the outer pole has to move to a realizable frequency, the achievable peaking-vs-frequency shape changes, which can shift: the CTLE peaking value actually needed to close the link, the adaptive loop's required code range/resolution (also currently TBD in the spec, see §6-6), and the eye-opening margins the rest of the chain (Vp/AGC/CDR) were implicitly sized against.

**What to check in simulation:**
1. Get a real bound on achievable pole frequency from the analog/process side (or at least a defensible upper limit) instead of `f_p2_ratio = 2.0` as a free parameter.
2. Re-run the peaking design with the outer pole clamped to that bound and see how much peaking is still achievable at Nyquist — the zero/inner-pole solve may need to change, or peaking-at-Nyquist may have to drop below +6 dB, or the zero ratio may need to move closer in.
3. There is already a bandwidth-limited variant of the CTLE factory in the model (`from_peaking_with_bw_limit`) that appends extra real poles to enforce an overall −3 dB bandwidth target — this is close to what's needed and could be adapted or used as a starting point, but it wasn't built specifically for "the peaking pole itself is capped," so check that it produces sensible zero/pole placement under that reframing rather than just re-purpose it blindly.
4. Re-check downstream: does the link still close (eye opening, counted BER) with the realizable CTLE shape? Does the CTLE adaptation loop's needed peaking range change?
5. Once bounded, decide whether `CTLE_F_P2_RATIO` (or its replacement) is worth exposing as a named, cited parameter in the spec, or whether it should be dropped in favor of a "peaking shape TBD, bounded by process" note similar to how the CTLE code range/resolution is currently handled (spec §6-6).

**Owner / next step:** get an analog/process bandwidth bound, then re-sweep the CTLE factory as above. No changes made to `architecture_spec.md` pending this.

---

## 2. CTLE de-glitch "discard the next windows" mitigation not empirically verified

**Status:** Open — flagged 2026-07-24.

**Where it shows up:** spec §6-8 (interaction matrix, CTLE row) documents a de-glitch strobe on CTLE code change ("swap the response between UI, discard the next windows"), with a follow-up note analyzing when the discard is actually load-bearing vs. belt-and-suspenders. `CtleAdaptNrz.step` (`src/optical_serdes/rx/ctle_adapt_nrz.py:280-324`) has no discard/blanking logic, and the `_run_rx_loops` loop in `mrm_nrz_transceiver_106g25.py` (~line 1826-1832) starts accumulating the next correlation window immediately after swapping `wave` to the new peaking bank entry — the mitigation described in the spec is not implemented in the reference script.

**Concern:** the spec's own analysis argues the discard matters more at the reference script's actual, faster CTLE rate (`ctle_decimation=512, ctle_shift=0` ⇒ 512 UI/LSB, ~16× the CDR's 32-UI dump) than at the mission defaults (`ctle_decimation=2048, ctle_shift=1` ⇒ 4096 UI/LSB, ~128×), because the CDR's proportional path (≤0.125 PI code/window) can take several hundred to ~1000+ UI to walk to the new lock point after a peaking-driven group-delay jump — potentially not diluted away within a single 512-UI correlation window. This has not been checked against actual simulation data.

**Why it matters:** if the un-diluted transient does bias `corr_meas` right after a code change, the script's CTLE convergence trace could show extra hunting or a biased settle point that isn't representative of the mission-rate behavior the spec models — and conversely, if it turns out to be negligible even at the script's rate, that's useful evidence the discard can be dropped from the architecture entirely (simplifying the RTL).

**What to check in simulation:**
1. Inspect `ctle_corr_log` (or `corr_meas` trajectory) from `mrm_nrz_transceiver_106g25.py` runs for a visible dip/spike or outlier in the window immediately following each CTLE code change, relative to the steady-state noise floor (`σ ≈ 1/√(decimation·len(lags))`).
2. If a contamination effect is visible, quantify how often it flips a vote's sign (vs. just adding noise within the dead-band) and whether it changes the number of windows to converge.
3. Re-run with an explicit discard (blank N windows post-swap) and compare convergence trajectories to isolate the effect.
4. If the effect is negligible even at `ctle_decimation=512`, note this as evidence the explicit discard can be dropped from the architecture (RTL simplification); if not, fold the confirmed need back into spec §6-8.

**Owner / next step:** run the `corr_meas`-vs-code-change inspection above against an existing or fresh `mrm_nrz_transceiver_106g25.py` sweep log. No changes made to `architecture_spec.md` pending this beyond the qualitative note already added to §6-8.

---

<!-- Add new items below with the same template: Status, Where it shows up, Concern, Why it matters, What to check in simulation, Owner / next step. -->
@mydocs/oci_msa/l250/architecture_spec.md:200-201 i think we need a separate section dedicated to jitter