# L250 OCI-MSA Gen2 — TX Sign-Off Parameter & Closure Checklist

**Status:** draft — parameter inventory plus open closure actions
**Date:** 2026-07-28
**Companion to:** `architecture_spec.md` §3 (TX jitter), §4 (electrical driver), §8 (optical transmitter / MRM); `OCI_PMA_TxRx_Requirements.md` (MSA/standards source); `CDR_Standards_Traceability.md`

---

## Purpose and how to read this table

This is a **sign-off closure checklist**, not a normative spec. Every `Value` cell remains intentionally `TBD` until its owning design team closes it and the result is folded into `architecture_spec.md`. The document inventories TX-side parameters spanning the **electrical driver** (`architecture_spec.md` §3–§4), the **optical transmitter / MRM** (§8), the laser interface, and TX-side protocol behavior.

Each row carries:

- **Placeholder / symbol** — the variable name, if one already exists in `architecture_spec.md` or the `optical-serdes` toolbox; `—` if this is a new item with no established symbol yet.
- **Value** — always `TBD` in this document, by design.
- **TBD basis** — reuses the exact tagging convention already used throughout `architecture_spec.md` (`TBD_from_partner`, `TBD_from_sim_sweep`, `TBD_from_link_budget`, `TBD_analog_design`), so this checklist can be merged into that document later without a translation step.
- **Gen1 / standards reference (context only)** — the nearest existing number from the MSA or cross-referenced standard, shown **only as scaling context**, not as the Gen2 value. Where the doc states an explicit Gen2 scale relationship, that's noted too.

Sections I–VI inventory electrical-driver parameters. Sections VII–IX inventory the optical TX, laser interface, and protocol requirements pulled from `OCI_PMA_TxRx_Requirements.md`. Section X lists verification work. Section XI is the actionable **OCI-MSA Gen2 TX-driver closure tracker** for the critical information still missing from the architecture specification.

---

## I. Architecture & Equalization

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| TX equalization topology (FIR taps + de-emphasis / peaking) | `FirDacDriver`, `FirDacTapConfig` | TBD | `TBD_analog_design` | — |
| Number of taps & delay structure (pre/main/post vs. main/post-1/post-2) | `N_tap` | TBD | `TBD_analog_design` | — |
| Output stage linearity class (active switching vs. linear buffer) | — | TBD | `TBD_analog_design` | — |
| Return loss / back-termination | — | TBD | `TBD_analog_design` | dj-adjacent: TX data-path reflectance ≤ −19 dB (MSA §4.2) — optical-domain reflectance, not an electrical SDD22 analog |

## II. Voltage, Impedance & Bandwidth (electrical driver)

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| Differential output swing | `swing_pk2pk` (`V_pp`) | TBD | `TBD_from_partner` | CEI-56G-XSR-NRZ TX Vdiff: 250–400 mVppd (§9.2) — different technology class (electrical XSR, not integrated MRM driver) |
| Output impedance (un-peaked) | — | **N/A** | N/A — architecture | Direct microbump to a capacitive-only MRM load, no transmission line and no back-termination resistor (matches `OCI_Gen2_PMA_Architecture.md`'s "Output diff DC impedance" row, dashed for both 64G-NRZ and 106G-NRZ-CPO columns — only the 224G-PAM4 *terminated-line* reference carries a value). There is no controlled/matched output resistance to spec in this topology. |
| Diff capacitive output load | — | TBD | `TBD_from_partner` | MSA-analogous doc gives **60 fF** for this exact CPO topology (all three reference columns, including 106G-NRZ). Not N/A — this is the load the driver's output stage must be designed against; CPO makes it *more* load-bearing, not moot, since there is no termination resistor to dominate the loaded response. |
| Peaking network topology / BW-extension target | — | TBD | `TBD_analog_design` | — |
| Mid-band gain | — | TBD | `TBD_from_partner` | — |
| Gain control range / step | — | TBD | `TBD_from_partner` | — |
| EQ gain peaking (de-emphasis) range / step | — | TBD | `TBD_from_sim_sweep` | — |
| High-pass 3 dB BW (AC-coupling corner) | — | TBD | `TBD_from_partner` | — |
| Rise/fall time (20–80 %, 10–90 %), electrical | — | TBD | `TBD_from_sim_sweep` | CEI-56G-XSR-NRZ: ≥ 4 ps (min edge, §9.2) — a *floor*, not a ceiling, and Gen1-baud |

## III. Equalization Tap Matching / Precision

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| TX EQ coefficient range & resolution | `N_tapq` (`quantization_bits`) | TBD | `TBD_from_sim_sweep` | — |
| De-emphasis cap (fraction of main-cursor weight) | `w_pre, w_main, w_post` | TBD | `TBD_from_sim_sweep` | — |
| Inter-tap phase delay matching | — | TBD | `TBD_analog_design` | — |
| Summing-node capacitive matching | — | TBD | `TBD_analog_design` | — |
| Tap-weight current-ratio matching (PVT) | — | TBD | `TBD_analog_design` | — |

## IV. Electrical Timing, Jitter & Eye Mask

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| Random jitter, RMS | `J_RMS` | TBD | `TBD_from_link_budget` | CEI-112G-XSR TX JRMS ≤ 0.0224 UIrms (§9.3) |
| Eye-opening jitter (EOJ) | `EOJ` | TBD | `TBD_from_link_budget` | CEI-112G-XSR TX EOJ ≤ 0.025 UIpp (§9.3); CEI-56G-XSR-NRZ TX EOJ ≤ 0.035 UIpp (§9.2) |
| High-probability jitter (J4u/J8u) | `J4u`/`J8u` | TBD | `TBD_from_link_budget` | CEI-112G-XSR TX J8u ≤ 0.1546 UI (§9.3) |
| Total jitter @ BER | `TJ` | TBD | `TBD_from_link_budget` | CEI-56G-XSR-NRZ TX TJ ≤ 0.28 UI (§9.2) |
| SNDR | `SNDR` | TBD | `TBD_from_link_budget` | CEI-112G-XSR TX SNDR ≥ 32.5 dB (§9.3) |
| Pulse-width distortion / DCD | — | TBD | `TBD_from_sim_sweep` | — |
| Electrical eye mask (horizontal / vertical opening) | $X_1$, $X_2$, $Y_1$, $Y_2$ | Provisional: 0.14 UI / 0.40 UI / 400 mV / 1500 mV | `TBD_from_link_budget` | Normative definition in `architecture_spec.md` §4-5. $Y_1$ is a model-derived static lower bound; PVT and dynamic NRZ TDEC remain open (`mrm_y1_derivation.json`). CEI-56G-XSR-NRZ reference: X1=0.14 UI, X2=0.4 UI, Y1=125 mV, Y2=200 mV (§9.2) |
| Transition-time budget, electrical (re-scaled from Gen1) | — | TBD | `TBD_from_link_budget` | — |
| Signaling-rate / ppm tolerance (TX clock) | — | TBD | `TBD_from_partner` | dj: **±50 ppm** (Cl. 178/179/180, §8.3); CEI §3.2.11: **±100 ppm** async — project must pick one (§7 gap in MSA) |

## V. Group Delay Variation

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| GDV, band 1 (DC–f₁) | `GDV_1` | TBD | `TBD_from_sim_sweep` | — |
| GDV, band 2 (f₁–f₂) | `GDV_2` | TBD | `TBD_from_sim_sweep` | — |
| GDV, band 3 (f₂–BW edge) | `GDV_3` | TBD | `TBD_from_sim_sweep` | — |
| Band-edge frequencies (f₁, f₂, f₃) | — | TBD | `TBD_from_sim_sweep` | — |

## VI. Power & Efficiency

Analog TX-driver energy is a **separate** line from the SerDes power budget. The 0.4 pJ/bit driver target covers analog pre-driver, FIR-DAC slices, merged-cascode output, and bias. Serializer, TX digital, and clocking are SerDes, not this table. See `architecture_spec.md` §1-3.

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| Energy efficiency, analog TX driver | — | 0.4 pJ/bit (first-cut) | Analog driver (separate from SerDes) | architecture_spec.md §1-3, §4-1; not a partner deliverable |
| Energy efficiency, analog TX driver by block | — | TBD within 0.4 pJ/bit | `TBD_analog_design` | Split analog pre-driver / FIR DAC / cascode / bias; serializer is SerDes, not this split |
| FOM, pJ/(bit·V), normalized to load | — | TBD | `TBD_analog_design` | — |

## VII. Optical Transmitter (Modulator) Requirements — *new, from `OCI_PMA_TxRx_Requirements.md` §4*

These bind the **optical** output of the TX (MRM + driver + laser), as distinct from the electrical driver items in Sections I–VI. The current architecture-level targets are in `architecture_spec.md` §8; this table tracks the remaining sign-off closure.

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| Side-mode suppression ratio (SMSR) | `SMSR` | TBD | `TBD_from_partner` | MSA: ≥ 30 dB (§4.2) |
| Total average launch power / group | `Pavg_total` | TBD | `TBD_from_partner` | MSA: ≤ 6 dBm, PRBS13 (§4.2) |
| Average launch power / channel | `Pavg` | TBD | `TBD_from_partner` | MSA: −8.5 (info min) … 0 (max) dBm (§4.2) |
| OMA / channel | `OMA` | TBD | `TBD_from_link_budget` | MSA: ≥ max(−5.5, −6.9+TDEC); ≤ −1 dBm (§4.2) |
| OMA imbalance across channels | `dOMA` | TBD | `TBD_from_partner` | MSA: ≤ 3 dB (§4.2) |
| TDEC | `TDEC` | TBD | `TBD_from_link_budget` | MSA: ≤ 3.4 dB, SSPR, BER = 2.4E-4 (§4.2–4.3) |
| \|TDEC_SSPR − TDEC_PRBS13\| | `dTDEC` | TBD | `TBD_from_link_budget` | MSA: ≤ 0.4 dB (§4.2) |
| Extinction ratio | `ER` | TBD | `TBD_from_partner` | MSA: ≥ 3.5 dB (typ 4.5), PRBS13 (§4.2) |
| Squelched TX OMA / channel | `Tsq_channel` | TBD | `TBD_from_partner` | MSA: ≤ −15 dBm, AOP held constant (§4.2) |
| Transition time (20–80%), optical | — | TBD | `TBD_from_link_budget` | MSA Gen1: ≤ 17 ps (≈0.90 UI @ 53.125 GBd) → Gen2 scale ≈ 8.5 ps if same UI fraction (§4.2, §11); dj Cl. 180 (PAM4, informative only): 8 ps max (§8.1) |
| Over / undershoot | — | TBD | `TBD_from_sim_sweep` | MSA: ≤ 22 %, SSPR (§4.2); dj Cl. 180: 22% (§8.1) |
| RIN, OMA-referenced | `RIN_OMA` | TBD | `TBD_from_partner` | MSA: ≤ −138 dB/Hz, PRBS13, 21.4 dB RL (§4.2); dj Cl. 180: −139 dB/Hz (§8.1) |
| Optical return loss tolerance | `ORL` | TBD | `TBD_analog_design` | MSA: ≤ 21.4 dB (§4.2) |
| TX data-path reflectance | `Tx_data_Ref` | TBD | `TBD_analog_design` | MSA: ≤ −19 dB, into TX, TX band (§4.2) |
| Center-wavelength accuracy (λ0–λ3, Group A/B) | — | TBD | `TBD_from_partner` | MSA Table 2-1 min/typ/max grids (§4.1) — same grids as Gen1, no Gen2-specific change expected |
| TX squelch / relink duration | `relink_squelch_tx_duration` | TBD | `TBD_from_partner` | MSA: 60–75 ms, AOP stays on / MRR heater lock (§3, §3.1) |
| TX routing skew contribution (into 4λ deskew budget) | — | TBD | `TBD_analog_design` | MSA informative note: TX routing < 2 UI (§3.1 notes) |
| Pre-FEC BER operating point (drives TDEC/SRS test condition) | — | TBD | `TBD_from_link_budget` | MSA: 2.4E-4 (§4.3); dj concatenated FEC may allow ~1E-3…5E-3 — **open project decision** (§7) |

## VIII. External Laser Source (ELS) Interface — *new, from `OCI_PMA_TxRx_Requirements.md` §6.2*

Applies if the TX uses an external (non-integrated) laser source per OIF ELS-01.0.

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| Laser RIN | — | TBD | `TBD_from_partner` | MSA: ≤ −144 dB/Hz (§6.2) |
| Laser linewidth | — | TBD | `TBD_from_partner` | MSA: ≤ 1 MHz (§6.2) |
| Laser SMSR | — | TBD | `TBD_from_partner` | MSA: ≥ 30 dB (§6.2) |
| Polarization extinction | — | TBD | `TBD_from_partner` | MSA: ≥ 16 dB (§6.2) |
| ELS output reflectance / ORL tolerance | — | TBD | `TBD_analog_design` | MSA: ≤ −26 dB / −26 dB (§6.2) |
| OE laser input reflectance | `OE_Lin_Ref` | TBD | `TBD_analog_design` | MSA: ≤ −26 dB, ELS implementations (§4.2) |

## IX. TX-Side Protocol / Link Behavior — *new, from `OCI_PMA_TxRx_Requirements.md` §3*

Structural/timing requirements on the TX that aren't captured by an electrical or optical eye-diagram number.

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| Pattern-swap continuity (training → release → mission) | — | TBD | `TBD_analog_design` | MSA: phase-continuous, glitch-free so far-end CDR does not lose lock (§3, §1.1) |
| Training / release pattern definition | — | TBD | `TBD_from_partner` | MSA: 160-bit, mostly repeating `0xCC`; channel ID in bits 23:16 (§3.1) |
| `duration_to_transmit_training_pattern` | — | TBD | `TBD_from_partner` | MSA: ≥ 285 ms (§3.1 Table 1-3) |
| `duration_to_transmit_release_pattern` | — | TBD | `TBD_from_partner` | MSA: ≥ 200 ms (§3.1 Table 1-3) |
| Bit/λ mapping convention | — | TBD | `TBD_analog_design` | MSA: LSB ↔ shortest wavelength on TX and RX (§3, §1.2) |

## X. Sign-off / Verification Methodology

| Spec Item | Placeholder / symbol | Value | TBD basis | Gen1 / standards reference (context only) |
|---|---|---|---|---|
| Transient timing sign-off (tap matching, DCD) | — | TBD | `TBD_analog_design` | — |
| Loaded output-network sign-off (all EQ codes) | — | TBD | `TBD_analog_design` | Verify the §4-4 pad-level 20–80% rise/fall-time window and eye mask with the extracted 60 fF MRM load; no independent −3 dB-bandwidth or prescribed peaking-topology requirement |
| Electrical jitter & eye-mask sign-off (Dual-Dirac import) | — | TBD | `TBD_from_link_budget` | — |
| Optical TDEC/SRS sign-off (reference receiver, histogram method) | — | TBD | `TBD_from_link_budget` | MSA: ref RX 26.5625 GHz BT4 (Gen1) → 53.125 GHz BT4 (Gen2, if 0.5×baud rule kept), no equalizer, histograms at 0.4/0.6 UI (§4.3) |
| PVT corner set | — | TBD | `TBD_analog_design` | — |

---

## XI. OCI-MSA Gen2 Critical TX-Driver Closure Actions

This tracker captures the critical information still required before the TX driver can progress from architecture targets to schematic freeze and sign-off. It deliberately excludes the **serializer input and pre-driver interface**, which is already assigned to CDNS in `architecture_spec.md` §4-2.

Status convention: unchecked = open; checked = closed and folded into `architecture_spec.md` with a linked sign-off artifact.

### XI-A. Process, supply, bias, and electrical reliability

- [ ] **Freeze the implementation process and device options.** Record the PDK/model revision, process node, thin-/thick-oxide devices, resistor/capacitor options, and approved high-voltage stack. Owner: analog design / CDNS. Basis: `TBD_from_partner`.
- [ ] **Define all driver supply rails and tolerances.** Include nominal/min/max values, sequencing, ripple/noise assumptions, and domains used by the FIR DAC, merged-cascode stage, bias generation, and digital controls. Owner: analog design / power integrity. Basis: `TBD_analog_design`.
- [ ] **Close the DC output-voltage envelope.** Specify output common mode, differential and single-ended extrema for the 2–3 Vppd swing, static levels, and behavior at every legal tap code. Owner: analog design. Basis: `TBD_analog_design`.
- [ ] **Map the driver waveform onto the MRM terminals.** State anode/cathode polarity, $V_{bias}$ reference, maximum reverse bias, minimum depletion voltage, and prohibited forward-bias region across PVT. Owner: analog design + PIC partner. Basis: `TBD_from_partner`.
- [ ] **Verify device and MRM electrical stress.** Check $V_{GS}$, $V_{GD}$, $V_{DS}$, junction field, hot-carrier stress, time-dependent dielectric breakdown, and power-up/down transients for all data and squelch states. Owner: analog reliability. Basis: `TBD_analog_design`.
- [ ] **Define safe startup, shutdown, reset, and squelch waveforms.** Prevent MRM forward bias, over-voltage, uncontrolled output states, and coefficient-bank glitches while supplies or clocks are absent. Owner: analog design + link controller. Basis: `TBD_analog_design`.
- [ ] **Set ESD, latch-up, and microbump protection requirements.** Confirm the protection parasitics remain inside the 60 fF total-load budget. Owner: I/O reliability + package. Basis: `TBD_analog_design`.

### XI-B. Asymmetric FFE and coefficient-DAC semantics

- [ ] **Define the logic-1 / logic-0 coefficient-bank selection truth table.** State whether bank selection is based on symbol level, transition direction, or explicit symbol history for pre/main/post branches. Owner: architecture + CDNS. Basis: `TBD_analog_design`.
- [ ] **Freeze the 8-bit coefficient coding.** Define sign-magnitude encoding, positive/negative ranges, zero code(s), main-tap range, LSB weight, illegal codes, and saturation behavior. Owner: mixed-signal architecture. Basis: `TBD_analog_design`.
- [ ] **Define the aggregate-current and swing constraint.** Specify how coefficient normalization, enabled-slice count, and the 2–3 Vppd limit interact independently for each edge bank. Owner: analog design. Basis: `TBD_analog_design`.
- [ ] **Resolve the tap-current matching unit.** Clarify whether “±1.5% LSB” means percent of one LSB, percent of full-scale current, percent of programmed tap current, or an INL/DNL bound; replace it with an implementable monotonicity/matching requirement. Owner: analog design. Basis: `TBD_analog_design`.
- [ ] **Define atomic coefficient updates.** Specify shadow registers, update strobe, clock domain crossing, glitch-free bank transfer, and behavior if an update coincides with a data transition. Owner: mixed-signal / RTL. Basis: `TBD_analog_design`.
- [ ] **Define reset, default, readback, and trim behavior.** Include power-on codes, main-only fallback, coefficient readback, production trim storage, and whether calibration may alter each edge bank independently. Owner: mixed-signal / test. Basis: `TBD_analog_design`.
- [ ] **Validate the asymmetric FFE against the nonlinear MRM model.** Sweep both coefficient banks against optical rise/fall asymmetry, TDEC, OMA, ER, and worst-case DDJ; publish the selected range and resolution. Owner: system simulation + PIC. Basis: `TBD_from_sim_sweep`.

### XI-C. Output load and loaded transition-time closure

- [ ] **Deliver a nonlinear electrical MRM load model.** Provide $C_{PN}(V,T,P)$, junction/series resistance, substrate loss, pad capacitance, routing parasitics, and terminal polarity over the full voltage envelope. Owner: PIC partner. Basis: `TBD_from_partner`.
- [ ] **Deliver the extracted EIC-to-PIC interconnect model.** Include microbump, local routing, differential imbalance, coupling to neighboring lanes, and process/package variation. Owner: package / extraction. Basis: `TBD_from_partner`.
- [ ] **Freeze the total load range, not only its nominal value.** Replace the nominal 60 fF with min/typ/max differential and common-mode loading limits across MRM, pad, routing, ESD, and extraction corners. Owner: PIC + package + analog. Basis: `TBD_from_partner`.
- [ ] **Select the output-network implementation.** The analog designer owns the circuit topology; no series/shunt-peaking or independent −3 dB-bandwidth requirement is imposed. Document the chosen implementation and demonstrate compliance through the loaded rise/fall-time and eye-mask tests. Owner: analog design. Basis: `TBD_analog_design`.
- [ ] **Verify the 3.2–4.5 ps loaded 20–80% rise/fall window.** Cover both edge polarities, both FFE banks, all legal coefficient codes, extracted parasitics, PVT, supply noise, and simultaneous-lane switching. Owner: analog sign-off. Basis: `TBD_from_sim_sweep`.
- [ ] **Close output-stage damping and stability as internal design checks.** Demonstrate that ringing or settling does not violate the pad-level eye mask, DDJ/ISI budget, or MRM voltage limits; do not introduce a separate topology-specific requirement. Owner: analog design. Basis: `TBD_analog_design`.

### XI-D. Electrical measurement and decomposition methodology

- [ ] **Define the electrical sign-off test point and de-embedding.** State exactly where the differential waveform is measured, which package/interconnect elements are included, and any de-embedding applied. Owner: SI / validation. Basis: `TBD_analog_design`.
- [ ] **Define rise/fall-time measurement.** Specify differential versus single-ended measurement, 20%/80% voltage references, pattern, coefficient setting, common-mode treatment, filtering, and averaging. Owner: analog validation. Basis: `TBD_from_sim_sweep`.
- [x] **Fully define the four-coordinate eye mask (definition done; values provisional).** Coordinate system, polygon construction, alignment, and pass/fail rule are now committed in `architecture_spec.md` §4-5, with a machine-readable artifact (`tx_eye_mask.json`) and checker/renderer (`optical-serdes/scripts/oci_msa_gen2/tx_eye_mask.py`). Remaining open items tracked below. Owner: link budget / validation. Basis: `TBD_from_link_budget`.
- [ ] **Finalize the provisional eye-mask coordinate values.** $Y_1$ is now 400 mV, a rounded nominal static floor from the modeled $Q=5000$ corner; partner PVT and dynamic NRZ TDEC must close it. $X_2$ (0.40 UI) must be validated against the 3.2–4.5 ps transition-time envelope; $X_1$ (0.14 UI) must reconcile with the internal 1e-12 jitter budget; $Y_2$ (1500 mV = $V_{PP,max}/2$) must be confirmed against MRM reverse-bias reliability limits. Owner: link budget / PIC / SI. Basis: `TBD_from_link_budget`.
- [ ] **Finalize eye-mask pass/fail statistics and BER convention.** Confirm the provisional ≥10⁶ UI per-corner observation length and decide between strict zero-hit and a hit-ratio (BER-equivalent) allowance. Note (spec §4-5 decomposition): the §3 allocations close $X_1$ with +0.015 UI margin only at the pre-FEC standards anchor of 2.4e-4; at the committed internal raw-BER target of 1e-12, the RJ term grows to 0.155 UI and total closure violates $X_1$ by 0.063 UI, so the mask convention and/or allocations require revision. Owner: link budget / validation. Basis: `TBD_from_link_budget`.
- [x] **Derive the nominal static $Y_1$ floor from the electro-optic transfer.** `mrm_y1_derivation.py` maps the §8 $Q=5000$–8000 range and 25 pm/V tuning into ER/OMA voltage thresholds. Worst static corner is 399.2 mV at $Q=5000$, rounded to provisional $Y_1=400$ mV. Artifact: `mrm_y1_derivation.json`. Owner: system modelling. Basis: `TBD_from_sim_sweep`.
- [ ] **Close $Y_1$ across partner PVT and dynamic NRZ TDEC.** Replace the rate-scaled TCMT surrogate with partner $P(V)$ curves across process, voltage, temperature, wavelength and heater-lock error; reconcile the model bias convention with §8-3; run SSPR through the normative 53.125 GHz BT4 receiver; then verify vertical eye distributions including residual ISI, ripple, level mismatch, noise, distortion, and swing derating. Owner: link budget / PIC / SI. Basis: `TBD_from_partner`.
- [ ] **Define the jitter reference clock and extraction algorithm.** State whether timing error is measured against an ideal source clock, recovered clock, or fitted UI; define crossing threshold, histogram construction, sample count, and BER extrapolation. Owner: link budget / validation. Basis: `TBD_from_link_budget`.
- [ ] **Define the $DJ_{\delta\delta}\rightarrow DDJ+BUJ$ extraction.** Provide reproducible procedures for isolating `DCD`, `ISI`, `DDJ`, and simultaneous-lane `BUJ` without double counting J4u/J8u or total jitter. Owner: SI / link budget. Basis: `TBD_from_link_budget`.
- [ ] **Define the SNDR calculation.** Specify input pattern, observation bandwidth, clock alignment, fitted pulse response/equalizer treatment, harmonic/noise inclusion, and reporting point. Owner: validation. Basis: `TBD_from_link_budget`.
- [ ] **Correlate electrical and optical metrics.** Demonstrate how pad-level swing, transition time, DDJ/ISI, and eye-mask margin map into MRM OMA, ER, optical transition time, and TDEC across the nonlinear load corners. Owner: system simulation + PIC. Basis: `TBD_from_sim_sweep`.

### XI-E. Power, thermal, area, and physical reliability

- [ ] **Allocate the analog TX-driver energy target by block.** Split the 0.4 pJ/bit analog-driver line among analog pre-driver, tap-delay generation, FIR DAC slices, merged-cascode output stage, and biasing. Do **not** fold serializer, TX digital, or clocking into this split — those belong to the SerDes budget (§1-3). Owner: architecture + analog. Basis: analog driver allocation (not `TBD_from_partner`, not SerDes).
- [ ] **Specify static and dynamic power conditions.** Report nominal and worst-case current/power for PRBS activity, alternating `1010`, static data, disabled taps, training, and squelch across PVT. Owner: analog design. Basis: `TBD_analog_design`.
- [ ] **Set area and placement limits.** Include the driver core, local decoupling, bias circuits, calibration logic, routing keep-outs, and lane-to-lane pitch. Owner: physical design. Basis: `TBD_analog_design`.
- [ ] **Close thermal interaction with the PIC.** Define junction-temperature limits, lane-to-lane thermal coupling, MRM-heater proximity, temperature gradients across coefficient slices, and required thermal sensors/guard bands. Owner: thermal + analog + PIC. Basis: `TBD_analog_design`.
- [ ] **Complete EM/IR and current-density sign-off.** Cover supply mesh, output devices, DAC slices, microbump current, local return paths, and simultaneous-lane switching. Owner: physical design / reliability. Basis: `TBD_analog_design`.
- [ ] **Define lifetime and aging closure.** Include duty-cycle assumptions, bias-temperature instability, hot-carrier aging, dielectric wear-out, and post-aging swing/timing margin. Owner: reliability. Basis: `TBD_analog_design`.

### XI-F. PVT, mismatch, calibration, and sign-off artifacts

- [ ] **Publish the required PVT matrix.** List process corners, model revisions, supply corners, temperature range, extracted-RC corners, MRM-load corners, and simultaneous-lane aggressor conditions. Owner: analog sign-off. Basis: `TBD_analog_design`.
- [ ] **Set Monte Carlo yield requirements.** Define local/global variation, sample count or confidence method, yield target, and which swing/timing/matching/eye metrics are statistical. Owner: analog sign-off. Basis: `TBD_analog_design`.
- [ ] **Define available trims and calibration authority.** State trim ranges, code resolution, production versus runtime calibration, nonvolatile storage, and which requirements must pass before and after trim. Owner: mixed-signal / test. Basis: `TBD_analog_design`.
- [ ] **Define pre-layout and post-layout acceptance gates.** Identify which requirements close at schematic, extracted block, EIC+PIC co-simulation, package extraction, and final optical-link simulation. Owner: program / sign-off. Basis: `TBD_analog_design`.
- [ ] **Archive reproducible sign-off artifacts.** For every closed item, retain the testbench, model revisions, corner manifest, scripts, waveforms, summary report, and requirement-to-result traceability. Owner: each requirement owner. Basis: sign-off process.

---

## Notes

- Sections I–VI intentionally exclude the specific numeric values from the "frozen sign-off" table reviewed earlier in this thread (e.g. 10 fF load, 65 GHz BW, 85 fs RJ) — those had unresolved reconciliation issues against this project's established baseline (60 fF load, 0.022 UI RJ) and are not carried forward here as even provisional values.
- Sections VII–IX preserve the optical-eye, laser-interface, and TX protocol inventory sourced from `OCI_PMA_TxRx_Requirements.md`; the architecture-level optical transmitter requirements are now present in `architecture_spec.md` §8.
- Where `OCI_PMA_TxRx_Requirements.md` already flags something as an open MSA gap (ppm, JTOL, pre-FEC BER decision — its own §7), that's carried through here rather than re-adjudicated.
- This checklist does not include RX-side items (TIA, CDR, adaptation loops); those have dedicated requirements in `architecture_spec.md` §5–§7.
