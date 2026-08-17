# L250 Griffin EVK — OCI-MSA GEN1 Compliance Test Matrix

**Status:** draft — maps every normative GEN1 (53.125 GBd NRZ) spec line to an EVK
test/measurement method and to what is already predicted from simulation.
**Date:** 2026-08-12
**Purpose of the EVK:** the L250 Griffin EVK is a **53.125 GBd NRZ, OCI-MSA v1.0
GEN1-rate** vehicle whose job is to **prove GEN1 compliance** before the L250
*product* — the 106.25 GBd NRZ CPO design in `architecture_spec.md` — is
committed. This document is the GEN1-side companion to that product spec: it does
not re-derive requirements, it maps existing GEN1 numbers onto a test plan.

**Sources:**

- Normative limits: [`OCI_PMA_TxRx_Requirements.md`](./OCI_PMA_TxRx_Requirements.md)
  §4 (Tx, Table 2-2), §5 (Rx, Tables 2-3/2-4), §6.1 (link, Table 2-5), §3 (MSA §1
  structural/protocol requirements) — itself sourced from
  `200G-OCI-Optical-Phy-Specification-v1.0.pdf`.
- GEN1 bottom-up link budget and receiver-side spec-compliance check:
  [`OCI_Link_Budget_Report.md`](../oci-link-budget-analysis/OCI_Link_Budget_Report.md)
  §3 (design-point TIA, penalty stack, closure margins, receiver-side compliance
  table added 2026-08-12).
- EVK-specific laser-power / OMA operating points: `L250 Griffin EVK` deck,
  July 21 2026 (`link_budget/old/L250_Griffin_EVK_072125.pdf`), slides 7–9.
  Flagged in that deck as **±2 dB uncertainty at this stage** and built on an
  assumed Rx SerDes with 2 pre + 2 post FFE taps + 1 DFE tap — a **different Rx
  architecture** than the CTLE-only, no-DFE analog SerDes in `architecture_spec.md`
  §1-2, so its numbers are EVK-specific and not directly transferable to the GEN2
  product receiver.

## How to read this matrix

| Status | Meaning |
|---|---|
| **PREDICTED-PASS** | Simulation/analysis already predicts a pass, with a quoted margin. Silicon measurement still required for sign-off — this is not a substitute for it. |
| **MUST-MEASURE** | No model prediction exists (parametric depends on driver/MRM/TIA silicon, not on the link-budget's OMA-domain model); EVK measurement is the only source of a number. |
| **GAP** | The OCI MSA itself does not specify this; a project decision or an external standard's number must be adopted before the EVK test plan can call it pass/fail (carried from `OCI_PMA_TxRx_Requirements.md` §7). |
| **N/A (EVK)** | Structural/protocol requirement that is a firmware/state-machine behavior, not an analog/optical measurement — verify by test bench, not by the link budget. |

---

## 0. A significant Rx-model divide — read the Rx table (§2) with this caveat

The two GEN1 Rx-sensitivity sources cited in this matrix are **not two independent
confirmations of the same claim** — they model different hardware and answer
different questions. This was found by cross-checking the two sources against each
other after an initial draft of this matrix conflated them.

**The gap, quantified.** Report §3.2's bottom-up model requires **−10.00 dBm** OMA
at TP3 for BER 10⁻¹². The Griffin EVK deck's own model (slide 9, "LM Tx to LM Rx
@ 1E-12") requires **−6.6 dBm** — **3.4 dB worse** for the identical BER target.

**Root cause — two different TIA/driver programs, not just different assumptions:**

- The report's floor and stack (`02_bottom_up_budget_53g.py`) are built from **152
  measured settings of the Mesa program's `Ocelot_TIA_ADFET`** part, and the
  headline number cherry-picks the single *lowest-noise* setting
  (`i_n = 3.17 µA`) as its design point — consistent with the report's stated
  purpose (§1): "derive component requirements... not to grade existing parts,"
  i.e. a best-achievable **ceiling case**, by design.
- The EVK deck's Rx-sensitivity curves (slides 8–9) are "Alex's simulation for OCI
  links for Nevada, based on **Caribou DR OMNI** Semi-Behavioral driver model...
  and Caribou DR OMNI TIA" — a different program (`Caribou`, not `Mesa`) modeling
  whatever driver/TIA is actually intended for the Griffin silicon, evaluated with
  explicit worst-case crosstalk baked in. This is a **representative-case
  provisioning** exercise, not a ceiling-case derivation.
- The report **explicitly disclaims unifying with this body of work**: "Nothing
  under `sandbox/alex` feeds the scripts; the independently produced COUPE BIDI
  waterfall (−11.8 dBm OMA at BER 10⁻¹²) is cited once in §3 as a sanity
  cross-check only" (Report Appendix B). That −11.8 dBm cross-check is itself a
  *different* Alex model (`sandbox/alex/COUPE_BIDI_PIC_LINK`, a bidirectional 4+4
  COUPE link) than the Caribou-DR-OMNI-based curves behind the EVK deck's laser
  table — so even the report's own sanity check doesn't touch the number the EVK
  is actually sized against.
- **The gap is almost fully explained by the report's own §3.4 sensitivity row**:
  swapping the design point from the best of the 152 Ocelot settings to the
  *worst usable* one (`i_n = 6.75 µA`, still passing the report's bandwidth gate)
  costs +3.28 dB on the floor — pushing required OMA to ≈ **−6.72 dBm**, within
  0.1 dB of the EVK deck's −6.6 dBm Caribou-DR-OMNI number. This strongly suggests
  Caribou DR OMNI is comparably noisy to the *worst*, not the *best*, member of
  the Ocelot survey — or is simply a different, noisier design.

**Implication for §2 below:** the report's margins (+5.7 / +4.3 / +4.2 dB) are a
best-case ceiling from a TIA characterization dataset that may not even be the part
going into Griffin silicon. The EVK deck's own numbers (last column of the §2
table) are the more relevant EVK-specific evidence and are called out separately
per row — they show smaller, though still generally positive, margins against the
MSA compliance thresholds (as opposed to the internal 10⁻¹² target, which the
deck's own model does not close with margin at the spec-minimum Tx corner). Treat
the Ocelot-based "+dB" figures as **an upper bound on what a good TIA design point
could achieve**, not as evidence about the specific TIA in this EVK.

---

## 1. Transmitter — Table 2-2 (MSA §2.2)

| Parameter | Limit | EVK test method | Prediction | Status |
|---|---:|---|---|---|
| OMA / channel | ≥ max(−5.5, −6.9+TDEC); ≤ −1 dBm | Optical power meter at TP2, per-λ, PRBS13 | Report §3.2: spec-min Tx closes at TP3 with +0.60 dB margin (both TDEC 1.4 and 3.4 dB corners); realistic Tx (−3.2 dBm, TDEC≈2) at +2.30 dB. EVK deck slide 9: LM Tx sized to −3.2/−4.1 dBm TP2 depending on config | **PREDICTED-PASS** (subject to EVK's own driver/MRM electro-optic transfer, not yet measured) |
| Total average launch power / group | ≤ 6 dBm | Power meter, all 4λ combined | Sized by EVK laser-power table (17/16/≥20.25 dBm *fiber* power upstream of 1:4 split, per config) — group power at the OE input is a laser-budget quantity, not yet cross-checked against the 6 dBm/group ceiling | **MUST-MEASURE** |
| Average launch power / channel | −8.5 (info min) … 0 (max) dBm | Power meter, PRBS13 | Not modeled (informative min only binds if below) | **MUST-MEASURE** |
| dOMA (channel imbalance) | ≤ 3 dB | Optical power meter, all 4λ | Used as an *input* to the Rx budget (crosstalk aggressor advantage, report §3.1) — not itself predicted; is a per-channel driver/MRM matching outcome | **MUST-MEASURE** |
| TDEC | ≤ 3.4 dB, SSPR, BER 2.4E-4, BT4 26.5625 GHz ref RX | SSPR pattern through BT4-filtered scope/BERT per MSA Note 2 method | Report treats TDEC as an **external input** (1.4 / 2.0 / 3.4 dB scenarios), not a driver-model output — the report's ISI+EQ line uses only reference-receiver filtering to avoid double-counting (§2.1). EVK deck assumes TDEC 2.5 dB for both LM and 3rd-party Tx without independent justification | **MUST-MEASURE** |
| \|TDEC_SSPR − TDEC_PRBS13\| | ≤ 0.4 dB | Same rig, both patterns | Not modeled | **MUST-MEASURE** |
| Extinction ratio | ≥ 3.5 (typ 4.5) dB | Optical eye / power ratio | Report books 3.5 dB (spec minimum) throughout §3.1; every GEN1 penalty line assumes this floor. A higher measured ER would only relax the shot/RIN/MPI lines | **MUST-MEASURE** (report assumes worst case; measured ER ≥ 3.5 dB is the pass condition, higher is bonus margin) |
| Squelched TX OMA / channel | ≤ −15 dBm, AOP constant | Power meter during squelch state | Not modeled — firmware/driver behavior | **MUST-MEASURE** |
| Transition time (20–80%) | ≤ 17 ps, SSPR | Scope eye measurement | Report's ISI/jitter lines use a BT4 reference-Tx pulse response (§3.1), not a transition-time spec directly; not a stand-in for the silicon measurement | **MUST-MEASURE** |
| Over/undershoot | ≤ 22 %, SSPR | Scope eye measurement | Not modeled | **MUST-MEASURE** |
| RIN, OMA-referenced | ≤ −138 dB/Hz, 21.4 dB RL | RIN test set at TP2 | Report books −138 dB/Hz throughout; §3.4 sensitivity shows if the *laser* is ELS-only (−144 dB/Hz) the RIN line falls from 0.68→0.16 dB, worth +1.13 dB margin — i.e. the number the report needs is a **ceiling**, and the true value is likely better if ELS RIN dominates | **MUST-MEASURE** (report's 0.68 dB stack line assumes the −138 dB/Hz worst case) |
| Optical return loss tolerance | ≤ 21.4 dB | Return-loss test | Not modeled | **MUST-MEASURE** |
| TX data-path reflectance | ≤ −19 dB (spec) / **≤ −24 dB (project requirement, report §3.3)** | Reflectance measurement into TX from data-path egress | Report §3.3/§3.4: the MPI line is booked at 0.24 dB assuming ≤−24 dB ends (shared GEN1/GEN2 product-line requirement, tighter than the MSA's −19 dB); at the spec's own −19 dB the internal 10⁻¹² closure still holds at **+0.33 dB** margin, so a part meeting only the MSA floor does not break compliance, only erodes margin | **MUST-MEASURE** against the project's own ≤−24 dB target; **PREDICTED-PASS** against the MSA's −19 dB floor either way |
| OE laser input reflectance (ELS) | ≤ −26 dB | Reflectance measurement, ELS connection | Not modeled; applies only if EVK uses an external laser (deck confirms PMF/ELS architecture) | **MUST-MEASURE** |

## 2. Receiver — Tables 2-3 / 2-4 (MSA §2.3)

| Parameter | Limit | EVK test method | Prediction | Status |
|---|---:|---|---|---|
| Rx OMA imbalance (dOMA) | ≤ 3 dB | Power meter across channels | Used as Rx-budget crosstalk input, not itself predicted | **MUST-MEASURE** |
| Receiver reflectance | ≤ −19 dB (spec) / ≤ −24 dB (project) | Reflectance measurement into Rx | Same finding as the Tx-side reflectance row: report §3.3 requires ≤−24 dB for the ~0.2 dB MPI line, but 10⁻¹² closure survives the spec's −19 dB at +0.33 dB margin | **MUST-MEASURE** against project target; **PREDICTED-PASS** against MSA floor |
| Receiver sensitivity (RxSens), unstressed | ≤ max(−8.2, −9.6+TDEC) dBm, PRBS31 | BERT sweep to BER 2.4E-4 at TP3 | **Report ceiling (Ocelot, best-of-152, §3.2):** −13.9 dBm, **+5.7 dB**. **EVK model (Caribou DR OMNI):** the deck does not evaluate this exact condition (BER 2.4E-4, unstressed, no aggressors) — its two data points (−6.9 dBm delivered → forecast 5e-10; −6.6 dBm required for 1e-12) don't include a 2.4E-4 crossing to read off directly. Do not infer a margin number here without that curve — see §0 | **PREDICTED-PASS** on the report's ceiling-case TIA only; the margin against the EVK's likely actual (Caribou DR OMNI) receiver is **unknown**, not merely smaller — needs the BER-vs-OMA curve evaluated at 2.4E-4 |
| Stressed receiver sensitivity (SRS) | ≤ −6.2 dBm, PRBS31, SEC 3.4 dB + aggressors at −3.2 dBm | BERT sweep under Table 2-4 stress conditions at TP3 | **Report ceiling (Ocelot, best-of-152, §3.2):** −10.5 dBm, **+4.3 dB**. **EVK model (Caribou DR OMNI, deck slide 9):** "worst-case-compliant-3rd-party-Tx → LM Rx" forecasts BER ≤ 5e-10 at −6.9 dBm delivered — this is a *different* stress condition (spec-min Tx corner, not the Table 2-4 SEC 3.4 dB + aggressor test) and a materially noisier receiver model than the report's ceiling case (§0); it is **not** a corroboration of the +4.3 dB figure | **PREDICTED-PASS** on the report's ceiling-case TIA only; the EVK's own model has not been evaluated against the exact SRS condition — **MUST-MEASURE / MUST-MODEL** for the actual Griffin TIA |
| BER floor | ≤ 1E-6 over OMA (−8.2+TDEC) … −1 dBm, ref Tx TDEC ≥ 2 dB | BERT floor sweep across that OMA range | **Report ceiling (Ocelot, best-of-152, §3.2):** required OMA −10.4 dBm at the range minimum, **+4.2 dB**; RIN-limited BER ceiling ~10⁻⁴⁸. Not evaluated against the Caribou DR OMNI model | **PREDICTED-PASS** on the report's ceiling-case TIA only — **not yet evaluated** against the EVK's actual (likely noisier, §0) receiver model |
| LOS assert / hysteresis / de-assert | −19…−14 dBm / 1…3 dB / −18…−11 dBm | AOP sweep, threshold measurement | Not modeled — firmware/comparator calibration | **MUST-MEASURE** |
| Loss-of-lock detection delay (t_LOL) | ≤ 50 ms | Modulation on/off → LOL flag timing | Not modeled — CDR/firmware state-machine timing, not an OMA-domain quantity | **MUST-MEASURE** |

## 3. Fiber link model — Table 2-5 (MSA §2.4)

| Parameter | Limit | EVK test method | Prediction | Status |
|---|---:|---|---|---|
| Total fiber link IL | ≤ 2.5 dB, 500 m SMF-28 | Insertion-loss measurement of the actual EVK test fiber/connector set | This is a **budget input**, not an output — the report allocates exactly 2.5 dB throughout. EVK bring-up should confirm the test setup's real IL is ≤ 2.5 dB (or the report's closure margins above shrink dB-for-dB) | **MUST-MEASURE** (setup characterization, not a silicon spec) |
| Chromatic dispersion | −0.9…+1.7 ps/nm | Not separately measurable on a short EVK fiber run; carried as a corner in simulation | Report §3.1: CD line is 0.01 dB (computed 0.005) at the worst corner — negligible at GEN1 rate/reach | **PREDICTED-PASS** (negligible impact; not a meaningful EVK bench test at 500 m) |
| MPI penalty tolerance | 0.2 dB | Not directly measurable as an isolated dB; backed into via reflectance measurements above | Report §3.3/§3.4: booked at 0.24 dB (≤−24 dB ends) with the ≤−19 dB fallback still closing at +0.33 dB | **MUST-MEASURE** (via reflectance, not directly) |

## 4. Structural / protocol requirements (MSA §1)

These bind PMA state-machine behavior, not an optical/electrical eye parameter — the
link-budget model has nothing to say about them; they are firmware/digital-design
verification items.

| Requirement | Limit | Verification | Status |
|---|---|---|---|
| Deskew range | Compensate 0–7 UI across the 4λ | Bench test with induced skew | **N/A (EVK)** — logic verification |
| Pattern-swap continuity | Phase-continuous, glitch-free training→release→mission | Protocol analyzer / far-end CDR lock monitor | **N/A (EVK)** — logic verification |
| TX squelch (relink) | AOP constant, modulation off, 60–75 ms | Timing measurement during relink | **N/A (EVK)** — timing verification |
| Pattern detect robustness | Functional at BER ≤ 1E-4 | Injected-error bench test | **N/A (EVK)** — logic verification |
| Deskew/detect/sync/validate timers | Table 1-3 (§3.1 of `OCI_PMA_TxRx_Requirements.md`) | State-machine timing capture | **N/A (EVK)** — timing verification |

## 5. Standards gaps — not resolvable from the MSA alone

Carried from `OCI_PMA_TxRx_Requirements.md` §7. These need a **project decision**
before the EVK test plan can assign a pass/fail limit; the link budget report does
not (and cannot) predict compliance against a number the MSA never states.

| Item | MSA status | Candidate source | Status |
|---|---|---|---|
| RX jitter tolerance (JTOL, SJ vs. frequency) | Not specified | dj Table 179-12 (electrical) or CEI-112G-XSR Table 24-12 (§8.2/§9.3 of `OCI_PMA_TxRx_Requirements.md`) | **GAP** — pick a mask before EVK JTOL bench test is defined |
| Signaling-rate / ppm tolerance | Not specified for GEN1 NRZ | dj: ±50 ppm per end; CEI: ±100 ppm async (§8.3/§9.1) | **GAP** — needed to size the EVK CDR frequency-offset bench test |
| TX electrical jitter (Jrms, J4u/J8u, EOJ) | Not specified (only optical TDEC) | CEI-56G-XSR-NRZ Table 19-8 (Gen1-baud NRZ analog) | **GAP** — no normative electrical-domain limit to test the EVK driver against |
| Pre-FEC BER operating point | 2.4E-4 (used for TDEC/SRS test conditions) | N/A — already fixed for GEN1 | Resolved for GEN1 (this is a GEN2-only open question per §7) |

## 6. Summary rollup

**Receiver side is weaker evidence than a first read suggests — see §0.** The
link-budget report predicts compliance against every Table 2-3/2-4 sensitivity
limit with **4.2–5.7 dB of margin**, but that number comes from cherry-picking the
best of 152 measured settings of a **different TIA program (Mesa/Ocelot ADFET)**
than the one the EVK deck's own Rx model uses (**Caribou DR OMNI**), and the report
explicitly disclaims combining its scripts with that body of work. The report's own
sensitivity table (§3.4) shows that swapping to the *worst usable* Ocelot setting
already erases most of this margin and lands within 0.1 dB of the EVK deck's
independently-required OMA for 1e-12 (−6.6 dBm vs. the report's −10.0 dBm) — a
3.4 dB gap that is not noise, it is a different, and apparently noisier, receiver.
**Net effect: treat the report's 4.2–5.7 dB margins as an upper bound on what a
good TIA design point could achieve, not as evidence about the actual Griffin TIA.**
The EVK deck's own model gives a qualitatively similar conclusion (the link closes,
with real but smaller margin against the MSA's 2.4E-4-BER compliance thresholds)
but does not evaluate the exact SRS/RxSens test conditions, so no comparably
precise EVK-specific margin number exists yet — closing that gap (running the
Caribou DR OMNI Rx model against the literal Table 2-3/2-4 conditions) is probably
the single highest-value next analysis for GEN1 compliance confidence.

**Transmitter side:** every Table 2-2 parametric is a **MUST-MEASURE** — the link
budget takes Tx parametrics (ER, TDEC, RIN, transition time) as *inputs*, not
outputs, so there is no simulation substitute for measuring the EVK's actual driver
+ MRM + laser electro-optic transfer. The OMA/power-budget math is the one place
both sources give a number, but per §0 they are ceiling-case vs. representative-case
models of different hardware, so "both close with positive margin" should not be
read as two confirmations of one result — each is one data point on a different
question (report: could a good design close it; deck: does the intended EVK design
close it).

**Before compliance testing can be called complete**, three items need resolution
outside the MSA itself (§5 above: JTOL mask, ppm tolerance, TX electrical jitter
limit) — none of these are GEN1-specific gaps invented by this project; they are
gaps in the MSA itself that the GEN2 requirements doc already flagged.

**Reflectance is the one place project practice is stricter than the letter of the
MSA:** ≤−24 dB is adopted so the ~0.2 dB MPI allocation holds by construction
(shared GEN1/GEN2 product line), but the report confirms the MSA's own −19 dB floor
would still close GEN1 at +0.33 dB — so an EVK part meeting only −19 dB is still
MSA-compliant, just with less margin than the project intends to carry forward into
GEN2.

---

## Traceability / open items

- [ ] **Highest priority (§0):** confirm which TIA program (Mesa/Ocelot ADFET vs.
  Caribou DR OMNI, or a third part) is actually intended/measured for the Griffin
  EVK silicon, and re-run the report's §3.1–3.2 penalty stack against that part's
  characterization data instead of the cherry-picked Ocelot best-of-152 point. This
  is the single biggest open question behind every Rx-side PREDICTED-PASS in §2.
- [ ] **(§0)** Ask for (or derive from) the Caribou-DR-OMNI BER-vs-OMA curve
  evaluated at BER = 2.4E-4 under the literal Table 2-3 (RxSens) and Table 2-4
  (SRS: SEC 3.4 dB + aggressors at −3.2 dBm) conditions — the deck's existing data
  points (5e-10 at −6.9 dBm; −6.6 dBm for 1e-12) don't cover the actual MSA
  compliance BER, so no EVK-specific margin number exists yet for §2's three
  sensitivity rows.
- [ ] Populate `MUST-MEASURE` rows once EVK bring-up data exists; convert them to
  `PASS`/`FAIL` with a linked test report, following the closure-tracking
  convention used in `tx_signoff_checklist.md`.
- [ ] Reconcile the EVK deck's Rx architecture (2 pre + 2 post FFE + 1 DFE) against
  the GEN1 report's DFE-only assumption (§3.1: "DFE removes post-cursors") — both
  are DFE-bearing, unlike the GEN2 product's CTLE-only receiver, but the tap counts
  differ and haven't been cross-checked against each other.
- [ ] The EVK deck's ±2 dB stated uncertainty is larger than several of the margins
  in this matrix (e.g. reflectance closure at +0.33 dB, §3.4 of the report) — flag
  which PREDICTED-PASS rows would flip under a −2 dB deck-uncertainty draw and
  prioritize those for early EVK measurement.
- [ ] Once JTOL/ppm/TX-jitter are decided (§5), fold the resulting limits back into
  `OCI_PMA_TxRx_Requirements.md` §7 and re-open this matrix's GAP rows.
