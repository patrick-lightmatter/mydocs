DES-OCI-106G-ADP-001 Rev 0.2 | Companion to ARCH-OCI-106G-001 Rev 0.7 | ADP Design Specification

**400G OCI Line-Side SerDes Chiplet**

Receive Digital Adaptation Loops — Design Specification

*Companion to ARCH-OCI-106G-001 Rev 0.7 | Design decomposition of ADP-001..005, DRX-003/004/005 | Both operating modes (106.25 / 53.125 GBd)*

| **Document ID** | DES-OCI-106G-ADP-001 |
| --- | --- |
| **Revision** | 0.2 (Draft for review) |
| **Date** | September 21, 2026 |
| **Status** | DRAFT. Design companion to the Architecture and Requirements Specification ARCH-OCI-106G-001 Rev 0.7. Where this document and Rev 0.7 differ, Rev 0.7 governs. Design confidence: Medium overall; Offset/BLW loop and CTLE loop Low (Section 12). |
| **Parent requirements** | ADP-001..005 (Rev 0.7 §6.6); DRX-003 (AGC range, gain-step vs. CDR lock), DRX-004 (CTLE range, receive bandwidth), DRX-005 (slicer offset trim, threshold servo, AC-coupling corner); CMP-006 (200G-mode bandwidth), CMP-009 (per-mode gain ranges and thresholds); CDR-005 (lock gate), CDR-006 (signal-valid freeze); LOM-002, LOM-004 (detector independence from the adaptive thresholds); DFT-003 (MPI metric), MGT-004 (VDM observables), MFG-003 (calibration NVM). |
| **Sibling documents** | DES-OCI-106G-CDR-001 — Clock and Data Recovery Design Specification (the CDR loop that gates these loops and whose lock point they disturb); DES-OCI-106G-SQL-001 — TX Squelch and Loss-of-Modulation (the signal_valid source). |
| **Scope** | Four first-order digital control loops on a common fixed-point template — error-slicer thresholds (Vp_top / Vp_bot), front-end gain (AGC), vertical offset / baseline wander (Offset), CTLE peaking — plus an observe-only channel estimator. Algorithms, truth tables, parameters, nesting order, freeze conditions, dither budget, and verification hooks. Per channel; four instances per fiber port. |
| **Out of scope** | CDR loop (DES-OCI-106G-CDR-001); analog implementation of the threshold, offset, gain, and peaking controls; TIA DC-offset-cancellation circuit and AC-coupling corner sizing (DRX-005, ADP-005 — interface constraints only); LOS / loss-of-modulation detectors; link-controller bring-up sequencing (SYS-007). |

| **Revision** | **Date** | **Change summary** |
| --- | --- | --- |
| 0.1 | September 18, 2026 | Initial issue. Design decomposition of ADP-001..005 and the adaptation-facing parts of DRX-003/004/005 per ARCH-OCI-106G-001 Rev 0.6; the CDR row of the loop inventory now points to DES-OCI-106G-CDR-001; a 200G OCI mode column added to every timing table (CMP-005/006/009); Python listings and figures replaced by update-equation and property tables; the CTLE init-code discussion reduced to the specification value (code 7 = 6.0 dB); the AGC code width lower bound (≥ 6 bits for 62–80 dBΩ at 0.5 dB/LSB) made explicit; the Offset-loop “~NN UI/LSB” placeholder tied to the Vp T_LSB; LOM-002 / LOM-004 interface constraints on the Vp and AGC loops added. |
| 0.2 | September 21, 2026 | Re-pinned to ARCH-OCI-106G-001 Rev 0.7 (hub revision; its Section 1.7 indexes this document). Predecessor-document references removed throughout per the OCI 106G document-structure convention: the Status field now states scope and confidence only; provenance statements are replaced by citations of the owning document in the set or by open items; cross-references into DES-OCI-106G-CDR-001 converted from legacy §6-x numbering to its Section numbers. No technical values changed. |

# 1. Introduction

## 1.1 Purpose

This document is the design decomposition of the receive adaptation requirements of ARCH-OCI-106G-001 Rev 0.7 (ADP-001..005 and the adaptation-facing parts of DRX-003/004/005). It fixes the loop template, per-loop arithmetic, parameters, nesting order, and freeze conditions so that RTL, behavioral model, firmware, and verification share one definition, and maps each behavior back to its requirement.

## 1.2 Conventions

| **Item** | **Convention** |
| --- | --- |
| Operating modes | 400G OCI mode: 106.25 GBd NRZ, UI = 9.412 ps. 200G OCI mode: 53.125 GBd NRZ, UI = 18.824 ps. Loop arithmetic is in UI and codes and is mode-independent; window durations and convergence times in ns/µs are given per mode. Gain and peaking ranges are stored per mode (CMP-009). |
| Requirement references | FAMILY-NNN refers to the requirement of that ID in Rev 0.7. “CDR-001” style references to the CDR design are to DES-OCI-106G-CDR-001; §x.y without prefix refers to Rev 0.7. |
| “DAC” | Any digital code that sets an analog operating point — a programmable knob, not necessarily a voltage or current converter. Vp and offset codes drive comparator references; the AGC code sets transimpedance gain; the CTLE code sets the equalizer transfer function. Each loop accumulates an integer code and writes it to an interface. |
| Observables | All continuous loops use the dual-error-slicer outputs already present for the CDR: data decision d ∈ {±1} and signed error e ∈ {±1}, or the Vp DAC codes (digitized readbacks of the rail amplitudes). No additional comparators or analog observables. |
| Symbols | Configuration and register names in monospace (vp_shift, corr_deadband) are shared by the behavioral model and the RTL. Placeholder symbols (N_code, T_LSB) follow the template of Table 2-3. |
| Placeholders | TBD = value tracked in the requirements database; not yet fixed by analysis. Section 12 lists the open items. |

## 1.3 Parent requirement map

**Table 1-1. Rev 0.7 requirements satisfied or interfaced by this document**

| **Req ID** | **Rev 0.7 obligation (abridged)** | **Design response** | **Section** |
| --- | --- | --- | --- |
| **ADP-001** | Vp, offset/BLW, AGC, CTLE frozen at presets until CDR lock, then released in a defined nesting order; convergence inside the ≥ 285 ms training window. | Release order Vp → Offset → CTLE → AGC on cdr_lock (Table 3-1); worst-case full-range convergence ≈ 10 µs / 20 µs per mode (Table 3-3), ≫ 10⁴× inside the window. | 3 |
| **ADP-002** | All loops freeze and telemetry is gated invalid during non-mission periodic patterns, TX squelch, and invalid signal; re-enable only on mission-rate data. | Per-loop adapt gate driven by signal_valid, cdr_lock, and a link-controller mission_pattern flag (Table 3-2). | 3.2 |
| **ADP-003** | Converged dither ≈ 1 LSB per loop via sub-LSB gain and dead-bands; aggregate dither budgeted within RX eye margin at 2.4E-4 and 1e-12. | Sub-LSB shift per loop; hysteresis (AGC), code dead-band (Offset), correlation dead-band (CTLE); per-loop dither table; aggregate allocation TBD (Rev 0.7 §9). | 9 |
| **ADP-004** | CTLE code changes de-glitched (response swap between UI); threshold and timing loops re-settle before new windows are used. | De-glitch strobe on code change; settle hold-off before the next CTLE window; Vp/CDR re-settle constraint. | 8.4 |
| **ADP-005** | AC-coupling / DCOC corner holds BLW ≤ 0.05 dB over 72-UI CID; co-designed with deskew-pattern spectrum and threshold servo. | Interface constraint: TIA DCOC quasi-static on the digital Offset-loop timescale; corner sizing is a DRX-005 circuit obligation. | 7.4 |
| **DRX-003** | AGC range from sensitivity floor to +2 dBm OMA without overload; 200G gain ranges per CMP-009; gain-step switching shall not disturb CDR lock. | Linear-in-dB 0.5 dB/LSB code; ≥ 6-bit code for 62–80 dBΩ; AGC is the slowest loop; hysteresis stops post-lock dither. | 6 |
| **DRX-004** | CTLE peaking range and shape open the 3.4 dB SEC eye; RX bandwidth 64–80 GHz (400G), 32–40 GHz (200G). | 4-bit peaking code, 2.5–10.0 dB at 0.5 dB/LSB (400G-mode values); 200G-mode range per CMP-006 stored per mode. | 8 |
| **DRX-005** | Slicer offset trimmable; threshold-adaptation servo tracks BLW; AC-coupling corner co-designed. | Vp loops are the threshold servo; Offset loop is the trim, driven from Vp code imbalance. | 4, 7 |
| **CMP-006 / CMP-009** | Per-mode receive bandwidth; AGC/gain ranges, thresholds stored and reloaded per mode. | Per-mode parameter sets for AGC (range, V_target) and CTLE (P_min, P_step); loop logic unchanged. | 6.3, 8.3 |
| **CDR-005 / CDR-006** | Lock detector gates adaptation; signal-valid freezes adaptation and holds CDR state. | cdr_lock and signal_valid are inputs to the adaptation gate (Table 3-2). | 3.2 |
| **LOM-002 / LOM-004** | Adaptive Vp thresholds shall not serve as the loss-of-modulation detection reference; detector either tracks the AGC code or freezes the AGC before evaluating. | Vp codes are exported as readbacks only; the AGC exposes a freeze input and its code for the LOM detector. | 4.4, 6.4 |
| **DFT-003 / MGT-004** | MPI metric from slicer margin or low-frequency amplitude statistics; VDM observables. | Vp codes, channel-estimator ĥ_i, and window statistics exported as telemetry; MPI-metric derivation is a candidate use (Open item). | 5.4, 10 |

# 2. Common Architecture

## 2.1 Loop inventory

**Table 2-1. Adaptation loops and the CDR they nest inside**

| **Loop** | **Controls** | **Observable** | **Order** | **Block** | **Confidence** |
| --- | --- | --- | --- | --- | --- |
| **CDR (phase + frequency)** | PI code | d(k±1), signed e(k) | 2nd | DigitalMmCdr — DES-OCI-106G-CDR-001 | — |
| **Vp_top / Vp_bot** | Dual error-slicer threshold DACs | Per-UI e₊ / e₋ gated by d | 1st | VpAdaptNrz | Medium |
| **Channel estimator ĥ_i** | Nothing — observe-only readback registers | Per-UI d(k−i)·e(k) from the mission slicers | — (open-loop correlator) | ChanEstNrz | Medium |
| **Offset / BLW** | Common offset DAC | Vp_top vs. Vp_bot code imbalance | 1st | OffsetAdaptNrz | Low |
| **CTLE** | Peaking / boost DAC | Sign-sign correlation of e with past d | 1st | CtleAdaptNrz | Low |
| **AGC** | Front-end gain code | Merged │Vp│ vs. target | 1st | AgcVpNrz | Medium |
| **Lock / freeze** | Gates every loop above | cdr_lock, signal_valid, mission_pattern | Semi (FSM) | adapt = 0 per loop | — |

## 2.2 Block diagram

**Figure 2-1. Adaptation loop nesting and gating diagram**

*\[FIGURE PLACEHOLDER — insert block diagram here. Suggested content: the CDR at the centre with the outer loops arranged around it by nesting rank, using the block names of Table 2-1 and the rank order of Table 3-1. Centre: DigitalMmCdr (rank 0, DES-OCI-106G-CDR-001) with output pi_code → phase interpolator (DES-OCI-106G-CLK-001 Section 9) and status output cdr_lock. Rings outward: rank 1 VpAdaptNrz (Vp_top / Vp_bot; T_LSB ≈ 32 UI), rank 2 OffsetAdaptNrz (≥ 4096 UI), rank 3 CtleAdaptNrz (≥ 4096 UI), rank 4 AgcVpNrz (outermost; ≥ 8192 UI); ChanEstNrz (channel estimator ĥ_i) drawn beside the ladder as observe-only (snapshot per 65 536 UI; readback registers; no actuator). Data inputs from the RX slicers (DES-OCI-106G-RXF-001 Section 8), entering from the left: decision d(k) and signed error e(k) (e₊ / e₋ per rail, gated by d) → the CDR (d(k±1), e(k)) and → the observe stages of VpAdaptNrz (per-UI e on the active rail), ChanEstNrz (d(k−i)·e(k)) and CtleAdaptNrz ((d, e) pairs with decision history). AgcVpNrz and OffsetAdaptNrz observe the Vp codes, not the slicers: draw their observe inputs as arrows from the VpAdaptNrz code outputs (window mean of (Vp_top + Vp_bot)/2 vs. V_target; code_top − code_bot), per the Observe column of Table 2-5. Control outputs to the RX front-end analog plant (DES-OCI-106G-RXF-001 Table 2-2), exiting right: Vp_top / Vp_bot DAC codes (8 bits each) → error-slicer threshold DACs; offset code (8 bits) → offset DAC ahead of the slicers; CTLE peaking code (4 bits) → CTLE, through the ADP-004 de-glitch strobe; gain code → AGC gain stage. Gating block (“Lock / freeze”, last row of Table 2-1; conditions of Table 3-2): inputs signal_valid (LOS / loss of modulation; CDR-006, LOM-004), cdr_lock from the CDR, the mission_pattern indication (non-mission periodic pattern, TX squelch, deskew training / release pattern), LOM-candidate detection, the CTLE de-glitch strobe, and the per-loop firmware enables and lock bits; outputs one adapt enable per loop. Show signal_valid = 0 freezing every loop (Hold) and holding the CDR; cdr_lock = 1 releasing VpAdaptNrz at stage 1 and, by firmware sequence, OffsetAdaptNrz, CtleAdaptNrz and AgcVpNrz at stages 2–4 (Table 3-1); the mission_pattern condition holding all outer loops (Vp runs on the deskew pattern only); the LOM candidate freezing AgcVpNrz; the CTLE strobe holding off CTLE and AGC for N windows; telemetry valid after stage 4. Data arrows solid, control-code arrows dashed, gating arrows dotted; one instance per channel.\]*

## 2.3 Shared processing template

**Table 2-2. Pipeline stages common to Vp, AGC, Offset, and CTLE**

| **Stage** | **Function** | **Programmability** | **Notes** |
| --- | --- | --- | --- |
| **Observe** | Signal readback: per-UI slicer samples, Vp codes, or (d, e) pairs. | Fixed per loop | No new analog hardware; observables already exist for the CDR. |
| **Average** | Accumulate the observable over a decimation window of D UI. | D firmware-programmable (rate knob) | Averaging is what gives the outer loops their noise rejection. |
| **Vote** | Truth table on the window measurement → vote ∈ {+1, 0, −1}. | Dead-band / hysteresis parameter per loop | Dead-band and hysteresis live here: vote 0 inside the band. |
| **Scale** | Vote enters the accumulator with gain 1/2^shift LSB per vote. | shift per loop | Sub-LSB gain is the primary dither attenuator (ADP-003). |
| **Accumulate** | Saturating integer accumulator; no wrap. | Width N_code + N_shift | Saturation, never wrap — the CDR phase accumulator is the only wrapping register in the receiver. |
| **DAC code** | code = acc >> shift; written to the analog control interface. | Mapping per loop (linear, linear-in-dB) | Optional de-glitch strobe on code change (mandatory for CTLE, ADP-004). |

## 2.4 Pipeline diagram

**Figure 2-2. Shared adaptation loop processing pipeline**

*\[FIGURE PLACEHOLDER — insert block diagram here. Suggested content: the six stages of Table 2-2 as a left-to-right pipeline, one block per stage, with the programmable parameter of each stage entering from above (firmware registers, Section 10) and the adapt enable from the gating block of Figure 2-1 entering from below. Stages and signals: Observe (input: per-UI slicer samples d, e, Vp codes, or (d, e) pairs; selection fixed per loop) → Average (accumulate over a decimation window of D UI; parameter D, firmware-programmable; output = window measurement) → Vote (truth table with dead-band / hysteresis; parameters DB / hyst; output vote ∈ {+1, 0, −1}, 0 inside the band) → Scale (gain 1/2^shift LSB per vote; parameter shift = N_shift) → Accumulate (saturating integer accumulator of width N_accum = N_code + N_shift; acc = clip(acc + vote, 0, ((1 << code_bits) − 1) << shift), Table 2-4 step A1; no wrap) → DAC code (code = acc >> shift, step A2; analog setting = f(code), linear or linear-in-dB, step A3; optional de-glitch strobe on code change, mandatory for CTLE per ADP-004) → analog control interface (DES-OCI-106G-RXF-001 Table 2-2). Show adapt = 0 holding the Vote and Accumulate stages (code retained); show acc and code as telemetry readbacks (Section 10); annotate T_LSB = D · 2^N_shift as the resulting minimum UI per code LSB (Table 2-3). Label the figure as the generic template instantiated per loop by Table 2-5 (Observe / Average / Vote / DAC / code-to-setting columns) with the placeholders of Table 2-3 and the per-loop arithmetic of Tables 4-1 (Vp), 6-1 (AGC), 7-1 (Offset) and 8-1 (CTLE); note that the channel estimator (Section 5) and the eye monitor (DES-OCI-106G-EYM-001) use stages 1–2 only and terminate in a readback register.\]*

## 2.5 Fixed-point template

**Table 2-3. Placeholders instantiated by every loop (values in Sections 4–8)**

| **Placeholder** | **Meaning** | **Formula / source** |
| --- | --- | --- |
| **N_code** | DAC / code register width | Per loop (dac_bits / code_bits) |
| **N_shift** | Sub-LSB gain shift | Per loop (*_shift) |
| **N_accum** | Accumulator width | N_code + N_shift; holds 0 … (2^N_code − 1)·2^N_shift |
| **D** | Decimation (UI per vote) | Per loop (decimation); firmware-programmable |
| **T_LSB** | Minimum UI per code LSB | D · 2^N_shift (one vote per window) |
| **DB / hyst** | Dead-band half-width or hysteresis half-window | Per loop; units of the loop’s own observable |

**Table 2-4. Shared accumulator kernel (VpDac, GainDac, OffsetDac, CtleDac)**

| **Step** | **Equation** | **Bound behavior** |
| --- | --- | --- |
| A1 | acc = clip(acc + vote, 0, ((1 << code_bits) − 1) << shift) | Saturate at both ends; no wrap |
| A2 | code = acc >> shift | Integer DAC code out; changes only when acc crosses a 2^shift boundary |
| A3 | Analog setting = f(code) per loop (Table 2-5) | Linear (Vp, Offset) or linear-in-dB (AGC, CTLE) |

**Table 2-5. Per-loop instantiation of the template**

| **Loop** | **Observe** | **Average** | **Vote** | **DAC** | **Code → setting** |
| --- | --- | --- | --- | --- | --- |
| **Vp_top / Vp_bot** | Per-UI error-slicer output on the active rail | vp_decimation-UI window per rail (default 1 = per-UI) | Sign of the window sum; no dead-band | VpDac × 2 | Threshold = code · V_LSB,vp (linear) |
| **Channel estimator** | Per-UI d(k−i)·e(k), one lag per instance | decimation-UI correlation window | None — mean is read out | None (readback register) | ĥ_i = signed fraction ∈ [−1, +1] |
| **AGC** | Vp threshold readbacks | decimation-UI window mean of (Vp_top + Vp_bot)/2 | Hysteresis comparison vs. V_target | GainDac | Gain = 10^((code − code_mid)·G_step/20) (linear-in-dB) |
| **Offset / BLW** | Integer Vp code readbacks | decimation-UI window mean of (code_top − code_bot) | Dead-band comparison in Vp codes | OffsetDac, signed about mid-scale | offset_v = (code − code_mid) · V_LSB,off (linear); subtracted ahead of the slicers |
| **CTLE** | Per-UI (d, e) pairs with decision history | decimation-UI correlation window over lags | Correlation dead-band | CtleDac | peaking_dB = P_min + code · P_step (linear-in-dB) |

# 3. Nesting, Gating, and Convergence (ADP-001, ADP-002)

## 3.1 Nesting order

**Table 3-1. Loop bandwidth ordering and release sequence on CDR lock**

| **Rank** | **Loop** | **T_LSB (defaults)** | **Released** | **Reason for position** |
| --- | --- | --- | --- | --- |
| 0 (innermost) | CDR | ≈ 256 windows of 128 UI per PI code at lock (DES-OCI-106G-CDR-001) | Always running; asserts cdr_lock | Every other loop reads d, e at a sampling phase that must already be settled. |
| 1 | Vp_top / Vp_bot | ≈ 32 UI per LSB (D = 1) | Stage 1, on cdr_lock | Fastest continuous loop; its codes are the observable for AGC and Offset. |
| 2 | Offset / BLW | ≥ 4096 UI per LSB | Stage 2 | Must be slower than the Vp codes it reads (rails re-settle in ≈ T_LSB,vp per step) and faster than the loops that rescale or reshape the eye. |
| 3 | CTLE | ≥ 4096 UI per LSB | Stage 3 | Peaking steps move the CDR lock point (h(−1) = h(+1)) and the Vp medians; Vp and CDR must re-settle before each new window (ADP-004). |
| 4 (outermost) | AGC | ≥ 8192 UI per LSB | Stage 4 | Slowest: every gain step rescales the entire eye, so Vp DACs and MM votes must re-settle before the next AGC window is trustworthy (DRX-003). |
| — | Channel estimator | Snapshot per 65 536 UI | Runs whenever adapt is true; no release slot | Actuates nothing; occupies no disturbance-ladder slot. |

*Stage order of the two outer loops (CTLE before AGC) follows the bandwidth ordering above and is to be confirmed by co-simulation (Section 12). The order is a firmware sequence, not hardware — each loop exposes an independent** ****adapt**** **enable.*

## 3.2 Freeze and enable conditions

**Table 3-2. Adaptation gate by condition (adapt**** = 1 means the loop votes and steps)**

| **Condition** | **Vp** | **Offset** | **CTLE** | **AGC** | **Chan. est.** | **Telemetry** | **Req** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| signal_valid = 0 (LOS or loss of modulation) | Hold | Hold | Hold | Hold | Hold | Invalid | ADP-002, CDR-006, LOM-004 |
| cdr_lock = 0 (acquisition or lock lost) | Preset / hold | Hold | Hold | Hold | Hold | Invalid | ADP-001, CDR-005 |
| cdr_lock = 1, non-mission periodic pattern (e.g. 0xCC) or TX squelch | Hold | Hold | Hold | Hold | Hold | Invalid | ADP-002 |
| cdr_lock = 1, deskew training / release pattern | Run | Hold | Hold | Hold | Hold | Invalid | ADP-002 (pattern autocorrelation biases the outer-loop observables); Open item 3 |
| cdr_lock = 1, mission-rate data, bring-up | Run | Released stage 2 | Released stage 3 | Released stage 4 | Run | Valid after stage 4 | ADP-001 |
| cdr_lock = 1, mission tracking | Run | Run | Run | Run | Run | Valid | — |
| LOM detector candidate detection | Run | Run | Run | freeze (or detector tracks the AGC code) | Run | Valid | LOM-004 |
| CTLE code change (de-glitch strobe) | Run | Run | Hold-off N windows | Hold-off | Run | Valid | ADP-004 |
| Firmware lock (lock_*) | Per bit | Per bit | Per bit | Per bit | Per bit | — | FW-005 (maintenance state) |

*“**Hold**”** retains the current code; presets are applied only from reset or on firmware command (warm re-entry after lock loss, consistent with CDR-006).*

## 3.3 Convergence budget

**Table 3-3. Worst-case full-range convergence at default parameters vs. the LOG-004 training window**

| **Loop** | **Codes traversed (worst case)** | **T_LSB** | **UI** | **400G OCI mode** | **200G OCI mode** |
| --- | --- | --- | --- | --- | --- |
| **Vp_top / Vp_bot** | 256 (8-bit, full range) | 32 UI | 8 192 | 77 ns | 154 ns |
| **Offset / BLW** | 256 (8-bit, full range) | 4 096 UI | 1.05 M | 9.9 µs | 19.7 µs |
| **CTLE** | 16 (4-bit, full range) | 4 096 UI | 65.5 k | 0.62 µs | 1.23 µs |
| **AGC** | 64 (6-bit assumed, TBD) | 8 192 UI | 524 k | 4.9 µs | 9.9 µs |
| **Channel estimator** | 1 snapshot | 65 536 UI | 65.5 k | 0.62 µs | 1.23 µs |
| **Sequential total (stages 1–4)** | — | — | ≈ 1.65 M | ≈ 15.5 µs | ≈ 31 µs |
| **Available (LOG-004 training pattern)** | — | — | — | ≥ 285 ms | ≥ 285 ms |
| **Margin** | — | — | — | > 10⁴× | > 10⁴× |

*Totals exclude the settle hold-offs of ADP-004 and any firmware-inserted dwell between stages; even at 100× the table values the sequence remains well inside the window.*

# 4. Error-Slicer Thresholds — Vp_top / Vp_bot (DRX-005)

Each rail threshold DAC adjusts for ≈ 50/50 error-slicer duty on its active polarity and converges to the conditional median of the rail amplitude at the sampling phase. Because that median tracks the main cursor (y = d·h₀ + ISI), Vp_top ≈ Vp_bot ≈ h₀: the loop digitizes h₀ and its codes are the amplitude readback used by the AGC and Offset loops.

## 4.1 Update

**Table 4-1. Per-UI and per-window arithmetic (VpAdaptNrz)**

| **Step** | **Equation** | **Rate** | **Notes** |
| --- | --- | --- | --- |
| S1 | d = +1 if y ≥ 0 else −1 | Per UI | Data slicer; threshold DAC at nominal mid-scale = 0 V |
| S2 | e_top = +1 if y > +Vp_top else −1; e_bot = +1 if y > −Vp_bot else −1 | Per UI | Top / bottom error slicers |
| S3 | e = e_top if d = +1 else e_bot | Per UI | Signed MM error = sign(y − d·Vp_rail); shared with the CDR and CTLE |
| S4 | if d = +1: vote_sum_top += e_top; else: vote_sum_bot += −e_bot | Per UI | Valid-gated accumulation; bottom rail sign mirrored |
| S5 | On ui_count = vp_decimation: each rail with a non-zero sum steps its DAC by sign(sum); sums and count cleared | Per window | Window collapses to a ±1 vote ⇒ fixed 1/2^vp_shift LSB step: bang-bang median lock |

## 4.2 Truth tables

**Table 4-2. Vp_top vote (valid only when d**** = +1)**

| **d(k)** | **e₊(k)**** (sample vs. +Vp_top)** | **Vote** | **Action** |
| --- | --- | --- | --- |
| +1 | +1 (above) | +1 | Too many samples above → raise threshold |
| +1 | −1 (below) | −1 | Too few above → lower threshold |
| −1 | ± | — | Hold (rail not active this UI) |

**Table 4-3. Vp_bot vote (valid only when d**** = −1; vote = −****e₋****)**

| **d(k)** | **e₋(k)**** (sample vs. −Vp_bot)** | **Vote** | **Action** |
| --- | --- | --- | --- |
| −1 | −1 (below −Vp_bot) | +1 | Raise threshold magnitude |
| −1 | +1 (above −Vp_bot) | −1 | Lower threshold magnitude |
| +1 | ± | — | Hold |

## 4.3 Parameters

**Table 4-4. Vp loop parameters (per rail)**

| **Placeholder** | **Model / RTL name** | **Default** | **Range** | **Meaning** |
| --- | --- | --- | --- | --- |
| **N_code** | dac_bits | 8 | — | Threshold DAC width per rail (codes 0…255) |
| **V_LSB,vp** | v_lsb | TBD | — | Threshold = code · V_LSB,vp; range 0 … 255 · V_LSB,vp. Pending slicer-input full-scale (DRX-002/003 analyses) |
| **N_shift** | vp_shift | 4 | — | Loop gain = 1/16 LSB per valid vote |
| **N_accum** | VpDac.acc | 12 bits | — | dac_bits + vp_shift; saturate, no wrap |
| **D** | vp_decimation | 1 UI | 1 … 2¹² UI | Window per vote; > 1 gives majority voting per rail per window |
| **T_LSB** | — | ≈ 32 UI per LSB | — | 2 · 2^vp_shift UI at D = 1 (each rail sees valid votes at ≈ half the symbol rate); vp_decimation · 2^vp_shift UI for D ≫ 1 |
| **Dead-band** | — | None | — | Pure bang-bang median loop; dithers ±1 LSB by design, attenuated by the 1/16 sub-LSB gain. Downstream loops carry their own dead-bands (Sections 6, 7). |
| **Preset** | init_code | TBD (from MFG-003 calibration) | 0 … 255 | Applied from reset; held (not re-applied) on lock loss |

## 4.4 Interfaces and constraints

**Table 4-5. Vp loop interfaces**

| **Interface** | **Direction** | **Consumer / constraint** | **Req** |
| --- | --- | --- | --- |
| **code_top, code_bot**** readbacks** | Out | AGC (merged amplitude), Offset (imbalance), telemetry (VDM), candidate MPI metric | DRX-003, MGT-004, DFT-003 |
| **e**** (signed error)** | Out | CDR phase detector; CTLE correlator; channel estimator | CDR-001, ADP-004 |
| **Loss-of-modulation reference** | Prohibited | The adaptive Vp thresholds shall not serve as the LOM detection reference; LOM uses an absolute, gain-referred threshold | LOM-002 |
| **Baseline-wander tracking** | — | Vp loops are the threshold-adaptation servo of DRX-005; slow wander appears as rail-code imbalance and is removed by the Offset loop | DRX-005, ADP-005 |
| **adapt**** / preset** | In | Table 3-2 | ADP-001/002 |

# 5. Channel Estimator (observe-only)

The channel estimator is the Vp sign-sign update re-aimed: the same valid-gated windowed accumulation on the same (d, e) stream, gated by a lagged decision d(k−i) instead of the current one, terminating in a readback register instead of a threshold DAC. It is pure digital logic plus a decision-history shift register — no comparator, no DAC, no analog hardware.

**Table 5-1. Delta from the Vp loop**

| **Attribute** | **Vp loop (Section 4)** | **Channel estimator** |
| --- | --- | --- |
| **Gating decision** | d(k) — the current decision selects the active rail | d(k−i) — the i-UI-old decision; one instance per lag i |
| **Accumulator terminates in** | Threshold DAC — the estimate must physically move an error slicer | Readback register — nothing moves |
| **Equilibrium** | Nulls its observable: ⟨d(k)·e(k)⟩ → 0 locks the rails to the conditional medians (= h₀) | Nulls nothing: ⟨d(k−i)·e(k)⟩ settles at a value ∝ h_i and is read out as-is |
| **Role** | Controller — the h₀ digitizer feeding AGC and Offset | Instrument — observe-only telemetry; closes no loop |
| **Relationship to CTLE** | — | Identical observable, opposite use: the CTLE loop nulls the lag-summed correlation through the peaking code; the estimator reports it per lag. ĥ₊₁ is the residual the CTLE drives into corr_deadband. |

**Table 5-2. Per-lag, per-UI product (accumulated, not stepped into a DAC)**

| **d(k−i)** | **e(k)** | **Product** | **Meaning** |
| --- | --- | --- | --- |
| +1 | +1 | +1 | Residual high given a lagged mark → h_i pulls up |
| +1 | −1 | −1 | Residual low given a lagged mark → h_i pulls down |
| −1 | −1 | +1 | Mirrored space rail |
| −1 | +1 | −1 | Mirrored space rail |

**Table 5-3. Channel-estimator parameters**

| **Placeholder** | **Model / RTL name** | **Default** | **Range** | **Meaning** |
| --- | --- | --- | --- | --- |
| **M_est** | lags | (−1, +1, +2, +3) | — | Lag set, all in parallel; the deepest lag sets the d-history depth |
| **D_est** | decimation | 65 536 UI | 2¹² … 2²⁴ UI | Window per readback snapshot; statistical floor of the mean = 1/√D_est ≈ 0.004 at default |
| **N_acc,est** | acc width | 17 bits signed | — | Bounded by the window (│acc│ ≤ D_est): saturation impossible by construction |
| **—** | h_hat[i] | Signed fraction ∈ [−1, +1] | — | Normalized cursor readback in units of the error-slicer decision (σ_e); not a voltage |
| **—** | e pipeline | 1 UI (lag −1 only) | — | Pre-cursor alignment of e(k) against d(k+1) |
| **Dead-band** | — | None | — | No code to dither and no vote quantization; readback noise is statistical (σ = 1/√D_est per snapshot) — average snapshots for a quieter estimate |
| **Nesting** | — | None | — | Actuates nothing; no disturbance-ladder slot or bandwidth constraint in mission mode |

**Table 5-4. Uses of the readbacks**

| **Use** | **How** | **Req** |
| --- | --- | --- |
| **CTLE bring-up cross-check** | Firmware sweeps the peaking code and confirms the ĥ_m zero-crossings cluster at one code (validates the single-metric premise of Section 8.2) | DRX-004; Open item 4 |
| **Telemetry** | ĥ_i snapshots exported as vendor VDM observables | MGT-004 |
| **MPI metric (candidate)** | Low-frequency statistics of ĥ_0 / Vp codes as an interferometric-noise indicator | DFT-003, DRX-010; Open item 5 |
| **Debug** | Per-lag pulse-response readback at any operating point without an eye monitor | — |

# 6. AGC (DRX-003)

The AGC drives the programmable front-end gain so that the merged rail amplitude — measured from the settled Vp codes at no extra hardware cost — hits a target. The code maps to gain linear-in-dB, so each LSB is a constant fractional amplitude step and loop dynamics do not depend on where the code sits.

## 6.1 Update

**Table 6-1. Per-window arithmetic (AgcVpNrz)**

| **Step** | **Equation** | **Rate** |
| --- | --- | --- |
| G1 | vp_sum += 0.5 · (vp_top + vp_bot); ui_count += 1 | Per UI |
| G2 | On ui_count = decimation: vp_mean = vp_sum / decimation; err = vp_mean − vp_ideal | Per window |
| G3 | vote = 0 if │err│ ≤ hysteresis_v; else +1 if err < 0 else −1 | Per window |
| G4 | dac.step(vote) — saturating gain-code accumulator (Table 2-4) | Per window |
| G5 | g_lin = 10^((code − code_mid) · step_db / 20) | On code change |

## 6.2 Truth table

**Table 6-2. AGC vote on the window mean**

| **Condition on window mean** | **Vote** | **Action** |
| --- | --- | --- |
| Vp_mean < Vp_ideal − hyst | +1 | Eye too small → raise gain code |
| Vp_mean > Vp_ideal + hyst | −1 | Eye too big → lower gain code |
| │Vp_mean − Vp_ideal│ ≤ hyst | 0 | Inside window → hold |

## 6.3 Parameters

**Table 6-3. AGC parameters (stored per operating mode, CMP-009)**

| **Placeholder** | **Model / RTL name** | **Default** | **Range** | **Meaning** |
| --- | --- | --- | --- | --- |
| **V_target** | vp_ideal | TBD per mode | — | Target merged rail amplitude (Vp_top + Vp_bot)/2; from link budget and slicer-input full-scale (DRX-002/003) |
| **V_hyst** | hysteresis_v | Auto: vp_ideal · (10^(step_db/40) − 1) | — | Hysteresis half-window = half of one gain step’s effect on the rail; a fraction of the target, not an absolute voltage |
| **N_code,agc** | code_bits | TBD; ≥ 6 | — | Gain-code width. 62–80 dBΩ at 0.5 dB/LSB = 36 codes ⇒ ≥ 6 bits; sized by the front-end design (DRX-002) |
| **G_step** | step_db | 0.5 dB / LSB | — | Linear-in-dB; ±2^(N_code−1) · G_step about mid-scale; code_mid = 2^(N_code−1) = 0 dB |
| **N_shift** | agc_shift | 1 | — | Loop gain = 1/2 LSB per vote |
| **N_accum** | GainDac.acc | N_code,agc + 1 bits | — | Saturate, no wrap |
| **D** | decimation | 4 096 UI | 2⁸ … 2¹⁶ UI | Window length per vote; firmware rate knob |
| **T_LSB** | — | ≥ 8 192 UI per LSB | — | decimation · 2^agc_shift |
| **Preset** | init_code | Mid-scale (0 dB) or MFG-003 calibration value | — | Per mode |
| **Gain range** | — | 62–80 dBΩ (400G mode); 200G-mode range TBD | — | Per-mode range and bandwidth setting reloaded on mode change (CMP-006/009) |

## 6.4 Properties and interfaces

**Table 6-4. AGC behavior and constraints**

| **Item** | **Behavior** | **Req** |
| --- | --- | --- |
| **Dead-band / hysteresis** | Voltage hysteresis half-window on the window mean. With the auto default, once inside the band neither neighbouring code’s error can exceed it, so a converged loop cannot dither between two adjacent codes while still tracking slow voltage/temperature drift. | ADP-003 |
| **Nesting** | Slowest continuous loop (Table 3-1): every gain step rescales the whole eye; Vp DACs and MM votes re-settle before the next window is used. | ADP-001 |
| **Gain step vs. CDR lock** | One 0.5 dB step changes rail amplitude by ≈ 6 %; the MM lock point h(−1) = h(+1) is amplitude-independent, so a single step shall not disturb CDR lock. Verified per Table 10-1. | DRX-003 |
| **LOM detector interaction** | The AGC exposes a freeze input and its code; the LOM detector either freezes the AGC before evaluating its persistence window or refers its absolute threshold through the code. | LOM-004 |
| **Overload range** | Range shall cover the sensitivity floor to +2 dBm OMA (+3 dBm average) without TIA/AGC overload; 200G-mode range per CMP-009. | DRX-003, RXO-003 |

# 7. Offset / Baseline Wander (DRX-005, ADP-005) — Low Confidence

Vertical centering error is read from the Vp codes: with residual offset r (positive = waveform too high), rail half-amplitude a, and Vp LSB L, code_top ≈ (a + r)/L and code_bot ≈ (a − r)/L, so the imbalance code_top − code_bot ≈ 2r/L. The loop nulls that imbalance through a signed offset DAC ahead of the slicers.

## 7.1 Update

**Table 7-1. Per-window arithmetic (OffsetAdaptNrz)**

| **Step** | **Equation** | **Rate** |
| --- | --- | --- |
| O1 | imb_sum += code_top − code_bot; ui_count += 1 | Per UI |
| O2 | On ui_count = decimation: imb_mean = imb_sum / decimation | Per window |
| O3 | vote = 0 if │imb_mean│ ≤ deadband_codes; else +1 if imb_mean > 0 else −1 | Per window |
| O4 | dac.step(vote); offset_v = (code − code_mid) · v_lsb | Per window |
| O5 | y_corrected = y − offset_v (analog offset DAC ahead of the slicers; caller subtracts) | Continuous |

## 7.2 Truth table

**Table 7-2. Offset vote on the window-mean imbalance**

| **Condition on window-mean imbalance** | **Vote** | **Action** |
| --- | --- | --- |
| imb_mean > +deadband_codes | +1 | Waveform high (code_top > code_bot) → offset_v up; subtraction moves the waveform down |
| imb_mean < −deadband_codes | −1 | Waveform low → offset_v down |
| │imb_mean│ ≤ deadband_codes | 0 | Centered → hold |

## 7.3 Parameters

**Table 7-3. Offset loop parameters**

| **Placeholder** | **Model / RTL name** | **Default** | **Range** | **Meaning** |
| --- | --- | --- | --- | --- |
| **N_code** | dac_bits | 8 | — | Offset-code width; mid-scale code_mid = 128 = 0 V |
| **V_LSB,off** | v_lsb | TBD | — | offset_v = (code − 128) · V_LSB,off ⇒ trim range ±128 · V_LSB,off. Constraint: V_LSB,off < V_LSB,vp (fine trim resolving fractions of a Vp code) |
| **N_shift** | offset_shift | 1 | — | Loop gain = 1/2 LSB per vote |
| **N_accum** | OffsetDac.acc | 9 bits | — | dac_bits + offset_shift; saturate, no wrap |
| **D** | decimation | 2 048 UI | 2⁸ … 2¹⁶ UI | Window length per vote; firmware rate knob |
| **DB** | deadband_codes | 1.0 Vp code | — | Dead-band half-width on the mean imbalance |
| **T_LSB** | — | ≥ 4 096 UI per LSB | — | decimation · 2^offset_shift |
| **Preset** | init_code | Mid-scale (0 V) or MFG-003 calibration value | 0 … 255 | Slicer input-referred offset trim of DRX-005 |

## 7.4 Properties and interfaces

**Table 7-4. Offset loop behavior and constraints**

| **Item** | **Behavior** | **Req** |
| --- | --- | --- |
| **Dead-band** | The Vp loops are bang-bang and dither ±1 LSB around lock; the window mean plus a one-code dead-band keeps the Offset loop from chasing that dither, so lock is quiet. | ADP-003 |
| **Nesting** | Slower than the Vp loops it reads (rails shift by V_LSB,vp per Vp step and re-settle in ≈ T_LSB,vp ≈ 32 UI per LSB); faster than CTLE and AGC. | ADP-001 |
| **TIA DC-offset cancellation** | Correction is applied ahead of the slicers but after the TIA DCOC. The TIA DCOC shall be quasi-static on this loop’s timescale (≥ 4 096 UI per step) so two integrators do not compete for the DC node; equivalently, the analog DCOC bandwidth may be much higher than this loop’s, but not comparable to it. | DRX-005, ADP-005 |
| **Baseline wander over CID** | The ≤ 0.05 dB BLW over 72 UI (678 ps / 1.36 ns) is an AC-coupling / DCOC corner obligation on the analog path; this loop removes only the slow residual visible in the Vp code imbalance. | ADP-005 |
| **Confidence** | Low: the imbalance-to-offset gain (2/L) depends on V_LSB,vp and on the assumption that both rails see the same ISI distribution; confirm by co-simulation with the Vp loop and the deskew-pattern spectrum. | Open item 6 |

# 8. CTLE Peaking (DRX-004, ADP-004) — Low Confidence

Error-based sign-sign adaptation: with the Vp DACs tracking the rail medians, residual post-cursor ISI h_m appears as correlation between the signed error and the m-UI-old decision. corr > 0 ⇔ h_m > 0 ⇔ under-boosted → raise peaking; corr < 0 ⇔ over-boosted → lower. Lag 1 senses the first post-cursor; longer lags (3–6) sense the long tail; lags sums a configurable set into one metric so a single code covers both.

## 8.1 Update

**Table 8-1. Per-window arithmetic (CtleAdaptNrz)**

| **Step** | **Equation** | **Rate** |
| --- | --- | --- |
| C1 | corr_sum += Σ_m∈lags d_hist[m−1] · e; ui_count += 1; d_hist.push(d) | Per UI (once the decision history is full) |
| C2 | On ui_count = decimation: corr = corr_sum / (decimation · len(lags)) ∈ [−1, +1] | Per window |
| C3 | vote = 0 if │corr│ ≤ corr_deadband; else +1 if corr > 0 else −1 | Per window |
| C4 | dac.step(vote) — saturating peaking-code accumulator | Per window |
| C5 | peaking_dB = peak_min_db + code · peak_step_db; de-glitch strobe on code change (Section 8.4) | On code change |

## 8.2 Cost function

**Table 8-2. Why the loop nulls the signed correlation rather than minimizing Σ|h_m|**

| **Criterion** | **Signed correlation Σ⟨d(k−m)·e(k)⟩ (used)** | **Magnitude cost Σ│h_m│ (offline cross-check only)** |
| --- | --- | --- |
| **Direction** | Monotone through zero in the peaking code: one window carries both the error and its sign — exactly what a vote → accumulate loop needs | V-shaped in the code: a single reading cannot tell under- from over-boost; descending it requires deliberately dithering a knob whose every step moves the CDR lock point |
| **Equilibrium** | Zero crossing (inside corr_deadband) | Minimum — at essentially the same code when all post-cursors respond to peaking monotonically in the same direction (one-knob projection of Lucky’s zero-forcing criterion). Premise: residual tail dominated by one time constant, the channel class a one-zero CTLE targets. Checkable in-system via the Section 5 ĥ_m sweep. |
| **Statistics** | Per-UI product d(k−m)·e(k) is unbiased; noise averages out over the window | Rectified Σ│ĥ_m│ is biased upward near the noise floor (E│ĥ│ > │h│ for │h│ ≲ 1/√D) — worst exactly at convergence |
| **Availability** | Hardware loop | Firmware sweep of the peaking code against ĥ_i readbacks or eye-monitor opening at bring-up |

**Table 8-3. CTLE vote on the window-mean correlation**

| **Condition on window-mean correlation** | **Vote** | **Action** |
| --- | --- | --- |
| corr > +corr_deadband | +1 | Under-boost (residual h_m > 0) → raise peaking code |
| corr < −corr_deadband | −1 | Over-boost (post-cursors ring negative) → lower peaking code |
| │corr│ ≤ corr_deadband | 0 | Converged → hold |

## 8.3 Parameters

**Table 8-4. CTLE loop parameters (peaking range stored per operating mode, CMP-006/009)**

| **Placeholder** | **Model / RTL name** | **Default** | **Range** | **Meaning** |
| --- | --- | --- | --- | --- |
| **N_code,ctle** | code_bits | 4 (16 codes) | — | Peaking-code width, codes 0 … 15 |
| **N_shift** | ctle_shift | 1 | — | Loop gain = 1/2 LSB per vote |
| **N_accum** | CtleDac.acc | 5 bits | — | code_bits + ctle_shift; saturate, no wrap |
| **D** | decimation | 2 048 UI | 2⁸ … 2¹⁶ UI | Correlation window per vote; firmware rate knob. Noise floor 1/√(D · len(lags)) and hence the dead-band sizing move with D |
| **M** | lags | (1,) | — | Decision lags summed into the metric; add 3–6 for long-tail sensing |
| **DB** | corr_deadband | 0.02 | — | No-vote dead-band on the mean correlation (≈ 0.9 σ at defaults; see Table 8-5) |
| **P_min, P_step** | peak_min_db, peak_step_db | 2.5 dB, 0.5 dB / LSB (400G mode) | — | peaking_dB = P_min + code · P_step = 2.5 … 10.0 dB. 200G-mode range TBD with the 32–40 GHz bandwidth configuration (CMP-006) |
| **Preset** | init_code | 7 (6.0 dB) | 0 … 15 | Matches the fixed non-adaptive CTLE baseline of the behavioral model; MFG-003 may override per device and mode |
| **T_LSB** | — | ≥ 4 096 UI per LSB | — | decimation · 2^ctle_shift |

## 8.4 Properties, de-glitch, and interfaces

**Table 8-5. CTLE loop behavior and constraints**

| **Item** | **Behavior** | **Req** |
| --- | --- | --- |
| **Dead-band** | At convergence the window correlation is noise with σ = 1/√(decimation · len(lags)) ≈ 0.022 at defaults; corr_deadband = 0.02 (≈ 0.9 σ) suppresses most noise votes and the 1/2 sub-LSB gain attenuates the rest, limiting dither to ≈ 1 LSB (0.5 dB). For a quiet converged code raise the dead-band to ≥ 2–3 σ or increase D. A true 1-LSB boost error gives │corr│ ≈ 0.1–0.5, well above either setting. | ADP-003 |
| **Nesting** | Slower than the CDR: peaking steps reshape the pulse the MM detector locks to (h(−1) = h(+1)), and the shared error slicers must stay quasi-static relative to CDR updates. | ADP-001 |
| **De-glitch strobe** | Every code change is applied through a strobe that swaps the CTLE response between UI; after the swap the loop observes a hold-off of settle_windows (TBD) before its next correlation window so Vp and CDR have re-settled. | ADP-004 |
| **No FEC-visible bursts** | A single 0.5 dB step at the settled code shall not produce an error burst visible in the host FEC bin counters (17-bin histogram). | ADP-004, DJI-002 |
| **Bandwidth / range per mode** | 400G-mode peaking range serves the 64–80 GHz receive bandwidth; the 200G-mode configuration (32–40 GHz) carries its own P_min/P_step and preset. | DRX-004, CMP-006 |
| **Freeze** | adapt = 0 via lock_ctle (Table 3-2). | ADP-002 |
| **Confidence** | Low: single-metric equilibrium premise (Table 8-2) and dead-band sizing depend on the realized channel tail; confirm by ĥ_m sweep on the statistical-eye channel set of DRX-004. | Open item 4 |

# 9. Dither and Eye-Margin Budget (ADP-003)

**Table 9-1. Converged dither per loop and its eye-margin term**

| **Loop** | **Dither mechanism at lock** | **Attenuation** | **Bound (defaults)** | **Eye-margin term** | **Status** |
| --- | --- | --- | --- | --- | --- |
| **CDR** | 1-PI-code limit cycle | Floor division by p_div = 512 | 0.031 UI pp (≈ 0.004 UI rms) | Horizontal | DES-OCI-106G-CDR-001 |
| **Vp_top / Vp_bot** | Bang-bang median dither ±1 LSB | 1/16 sub-LSB gain | ±1 · V_LSB,vp (threshold only — does not move the signal) | Threshold placement error | V_LSB,vp TBD |
| **Offset / BLW** | None after lock (dead-band 1.0 Vp code) | 1/2 sub-LSB gain | ≤ 1 · V_LSB,off across slow drift | Vertical centering | V_LSB,off TBD |
| **CTLE** | ≈ 1 LSB at 0.9 σ dead-band; 0 at ≥ 2–3 σ | 1/2 sub-LSB gain | 0.5 dB peaking step ⇒ pulse reshaping; moves CDR lock point | Horizontal + vertical | Dead-band setting to be chosen |
| **AGC** | None after lock (hysteresis = ½ step) | 1/2 sub-LSB gain | 0 codes; 0.5 dB (≈ 6 % amplitude) across slow drift | Vertical (scales whole eye) | N_code TBD |
| **Aggregate** | Sum of the above at the 2.4E-4 compliance point and the 1e-12 internal point | — | TBD | RX eye budget allocation | Rev 0.7 §9 placeholder; Open item 2 |

# 10. Telemetry and Firmware Controls

**Table 10-1. Registers exposed per channel**

| **Register** | **Direction** | **Content** | **Use** | **Req** |
| --- | --- | --- | --- | --- |
| **code_top, code_bot** | Read | Vp threshold codes (8-bit each) | Amplitude readback; VDM; MPI-metric candidate | MGT-004, DFT-003 |
| **agc_code, offset_code, ctle_code** | Read | Current DAC codes | Convergence monitoring; flight data recorder | MGT-003/004 |
| **h_hat[i]** | Read | Channel-estimator snapshots per lag | CTLE cross-check; debug; VDM | MGT-004 |
| ***_decimation** | Read/write | Window lengths per loop (Sections 4–8 ranges) | Firmware rate knobs; changed only in maintenance state | FW-005 |
| ***_deadband****, ****hysteresis_v****, ****vp_ideal** | Read/write | Vote thresholds | Per-mode parameter set | CMP-009, FW-005 |
| **init_*****,****** ****preset_load** | Read/write | Presets from calibration NVM | Reset and mode change | MFG-003, CMP-009 |
| **adapt_*****,****** ****lock_*** | Read/write | Per-loop enable / freeze | Table 3-2 gating; maintenance overrides | ADP-001/002 |
| **agc_freeze** | Write (from LOM detector) | Freeze AGC during candidate LOM evaluation | Detector robustness to AGC | LOM-004 |
| **telemetry_valid** | Read | Cleared under every Hold row of Table 3-2 | Gates VDM accumulation | ADP-002 |

# 11. Verification

**Table 11-1. Verification matrix**

| **Req** | **Item** | **Method** | **Condition** | **Pass criterion** |
| --- | --- | --- | --- | --- |
| **ADP-001** | Nested bring-up | T / D | Cold start on mission data, both modes; codes logged per window | Loops release only after cdr_lock, in Table 3-1 order; all codes settled well inside 285 ms |
| **ADP-002** | Freeze conditions | T | signal_valid low; 0xCC pattern; training/release patterns; partner squelch | No code changes while frozen; telemetry_valid cleared; re-enable only on mission data |
| **ADP-003** | Converged dither | A / T | Settled loops, ≥ 10⁶ windows per corner | Per-loop dither within Table 9-1 bounds; aggregate within the allocated eye margin (once populated) |
| **ADP-004** | CTLE de-glitch | T | Forced ±1 code steps at the settled point; FEC 17-bin counters active | No CDR lock loss; no FEC-visible burst; Vp re-settles within the hold-off |
| **ADP-005** | BLW over CID | A / T | 72-UI CID runs in PRBS31, both modes | BLW ≤ 0.05 dB; Offset loop does not react to the run (analog-path obligation, this loop passive) |
| **DRX-003** | AGC range and step | T | Input OMA swept from sensitivity floor to +2 dBm | No overload; each 0.5 dB step leaves CDR locked; 200G-mode range meets CMP-009 |
| **DRX-004** | CTLE convergence and equilibrium | A / T | Statistical-eye channel set; peaking-code sweep with ĥ_m readback | Loop equilibrium within ±1 code of the Σ│ĥ_m│ minimum; SEC 3.4 dB eye opens at the converged code |
| **DRX-005** | Threshold servo and offset trim | T | Injected input offset and slow baseline wander | Vp codes track the rail medians; Offset loop nulls the imbalance to within the dead-band |
| **LOM-002 / LOM-004** | Detector independence | I / T | Partner squelch with AGC active | LOM reference is absolute/gain-referred; agc_freeze honored; no false LOM during adaptation |
| **CMP-005/006/009** | Dual-rate operation | T | All of the above at 53.125 GBd with the 200G parameter set | Same criteria; per-mode presets reloaded on mode change |

# 12. Open Items

**Table 12-1. Open items and dependencies**

| **#** | **Item** | **Owner** | **Dependency / closure** |
| --- | --- | --- | --- |
| 1 | Confirm release order of the outer loops (CTLE before AGC, Table 3-1) and the stage dwell times by co-simulation with the CDR model | Adaptation architecture | Behavioral model; SYS-007 bring-up sequence |
| 2 | Aggregate dither eye-margin allocation for ADP-003 (Table 9-1 “Aggregate” row) | RX eye budget | Rev 0.7 §9 placeholder |
| 3 | Whether the Vp loops may run on the deskew training/release patterns (Table 3-2) or must also hold; depends on the OCI v1.0 160-bit pattern spectrum | Adaptation / deskew | BUP-001 pattern analysis; ADP-005 co-design |
| 4 | CTLE single-metric premise: ĥ_m zero-crossing clustering on the DRX-004 channel set; lags and corr_deadband final values; settle_windows hold-off | Adaptation architecture | Statistical-eye channel models |
| 5 | MPI-metric derivation (DFT-003) from Vp / ĥ_0 low-frequency statistics vs. a dedicated observable | DFT / adaptation | DRX-010 characterization |
| 6 | Offset loop gain and V_LSB,off / V_LSB,vp ratio once slicer-input full-scale is fixed; TIA DCOC bandwidth agreement | Analog / adaptation | DRX-002/003/005 analyses |
| 7 | AGC code width (≥ 6 bits) and 200G-mode gain range, V_target, and CTLE P_min/P_step for the 32–40 GHz configuration | Analog / CMP | CMP-006/009; front-end design |
| 8 | Vp init_code, AGC and Offset presets in calibration NVM; per-mode storage and integrity check | MFG / firmware | MFG-003 |
| 9 | Behavioral-model 200G-mode regression (all Section 11 items at 53.125 GBd) | Verification | CMP-005 |

*End of DES-OCI-106G-ADP-001 Rev 0.2.*

DES-OCI-106G-ADP-001 Rev 0.2 | DRAFT | Page  of