DES-OCI-106G-JIT-001 Rev 0.3 | Companion to ARCH-OCI-106G-001 Rev 0.7 | JIT Design Specification

**400G OCI Line-Side SerDes Chiplet**

TX Electrical Jitter Budget at TP1 — Specification and Derivation

*Companion to ARCH-OCI-106G-001 Rev 0.7 | Derivation of ELE-002..005, SYS-002, EMC-003 | Both operating modes (106.25 / 53.125 GBd)*

| **Document ID** | DES-OCI-106G-JIT-001 |
| --- | --- |
| **Revision** | 0.3 (Draft for review) |
| **Date** | September 21, 2026 |
| **Status** | DRAFT. Design companion to the Architecture and Requirements Specification ARCH-OCI-106G-001 Rev 0.7. Where this document and Rev 0.7 differ, Rev 0.7 governs. Design confidence: Medium. The σ_RJ clock-chain allocation is the binding kill-or-confirm item of the transmitter (risk R8). |
| **Parent requirements** | ELE-002 (JRMS), ELE-003 (EOJ), ELE-004 (J4u), ELE-005 (internal dual-Dirac budget), ELE-006 (edge rate and rise/fall mismatch — inputs to DCD and ISI), ELE-008 (inter-tap matching — input to the FIR slice-DCD adder); SYS-002 (clock-chain phase-noise allocation σ_RJ ≤ 104 fs); DTX-001 (TX jitter budget); EMC-003 (crosstalk within BUJ), EMC-004 (spurs); LOG-002 (2.4E-4 compliance point and the 1e-12 internal design point); CMP-007 (200G-mode UI-relative limits and absolutes). |
| **Sibling documents** | DES-OCI-106G-TXD-001 — TX Pre-Driver and Driver (consumes the per-block allocations of this document in its Table 3-2); DES-OCI-106G-CDR-001 — receive CDR (phase-interpolator class referenced in the clock-chain build-up). |
| **Governing specifications** | IEEE Draft P802.3dj — 200G/lane electrical clock-jitter metrics at 106.25 ± 50 ppm GBd, cited per Rev 0.7 as 179.9.4.6 via Annex 176C/176D (D1.3 names JRMS03 / EOJ03 / J4u03; D3.1 renames to JHRMS / EOJ03 / JH4u, collapses J4u to one value, and renumbers to 179.9.4.7 / Table 179-7 — values unchanged). OIF CEI-112G-XSR — 200G-mode cross-check (CMP-007). OCI Gen1 v1.0 Table 2-2 — TDEC at TP2 (the only optical TX quality metric). |
| **Scope** | Definition of TP1; the three adopted 802.3dj clock-jitter limits; the internal dual-Dirac budget at the raw-BER 1e-12 FEC-free operating point; first-principles derivation of each term (clock-chain build-up, duty-cycle / rise-fall model, first-order settling model, crosstalk slew model); assembly, sensitivity, and eye-mask input; crosswalk between the two limit sets; verification methodology at an unprobeable test point; both operating modes. |
| **Out of scope** | Circuit design of the PLL, distribution, phase interpolator, serializer, pre-driver, and driver (allocations only); optical TDEC decomposition at TP2 (DTX-001..007); receive-side jitter tolerance (DRX-006, CDR-001). |

| **Revision** | **Date** | **Change summary** |
| --- | --- | --- |
| 0.2 | September 18, 2026 | Initial issue. Derivation of ELE-002..005, SYS-002, and EMC-003 per ARCH-OCI-106G-001 Rev 0.6; 802.3dj citation aligned to the Rev 0.6 form (D1.3 179.9.4.6 via Annex 176C) with the D3.1 renaming noted; σ_RJ absolute stated consistently as 104 fs (0.011 UI × 9.412 ps, not rounded to 100 fs); transition-time corners labelled to ELE-006 (3.3 ps typical, 4.0 ps hard maximum; 3.6 ps kept as an intermediate corner); 200G OCI mode absolutes added to the budget and the hardware-fixed terms re-expressed in 200G UI (CMP-007); the FIR slice-DCD adder (0.05 UI) related to ELE-008 and flagged; figures and prose derivations replaced by tables. |
| 0.2 | September 18, 2026 | Gap closure after review. (1) ISI: second-order settling analysis added (Table 5-4b); the 0.012 UI allocation is shown to require TP1 electrical overshoot ≤ 2 % (ζ ≥ 0.8) at the hard-max edge — new derived constraint JIT-D1, handed to DES-OCI-106G-TXD-001 Table 5-2. (2) FIR slice-DCD adder decomposed by simulation (Table 5-3b): tap-slice skew at the ELE-008 limit contributes 0.0003 UI; the 0.05 UI is reproduced by a logic-1 / logic-0 bank asymmetry of ≈ 0.13 per side tap (ELE-010) — adder re-labelled “bank-asymmetry apparent DCD”, bounded as JIT-D2, attribution (TP1 timing vs. TP2 optical credit) referred to the link budget. (3) DCD margin table added (Table 5-3c) with a DCC design target of ± 0.2 % (≈ 10 % margin). (4) Clock-chain build-up restated in three variants (Table 5-1b): the phase-interpolator term is receive-side unless the TX uses a PI for tap-delay generation; without it the first-cut gap is 1.5 dB, not 2.7 dB. (5) Statistical (convolved) DJ combination evaluated (Table 5-8): σ_RJ relaxes only to 108–114 fs, so the 104 fs requirement is robust. (6) TJ at the 2.4E-4 compliance point tabulated. (7) TP1 eye-mask definition added (Section 6.2). Open items 2, 3, 4 closed or converted to constraints; item 1 narrowed. |
| 0.3 | September 21, 2026 | Re-pinned to ARCH-OCI-106G-001 Rev 0.7 (hub revision; its Section 1.7 indexes this document). Predecessor-document references removed throughout per the OCI 106G document-structure convention: the Status field now states scope and confidence only; provenance statements are replaced by citations of the owning document in the set or by open items; cross-references into DES-OCI-106G-CDR-001 converted from legacy §6-x numbering to its Section numbers. No technical values changed. |

# 1. Introduction

## 1.1 Purpose

The optical specification binds transmitter quality only through TDEC at TP2 and provides no electrical decomposition. This document supplies the two limit sets that bind the transmitter electrically at TP1 — the 802.3dj clock-jitter limits adopted at native baud (ELE-002..004) and the internal dual-Dirac budget at the raw-BER 1e-12 point that no standard specifies (ELE-005) — and records the derivation of every number in the second set so that the per-block allocations returned by the circuit owners (DES-OCI-106G-TXD-001 Table 3-2) can be checked against a stated model rather than a bare limit.

## 1.2 Conventions

| **Item** | **Convention** |
| --- | --- |
| Operating modes | 400G OCI mode: 106.25 GBd, UI = 9.412 ps. 200G OCI mode: 53.125 GBd, UI = 18.824 ps. All limits are stated in UI and apply in both modes (CMP-007); absolutes are given per mode. Terms that are hardware-fixed in seconds (clock RJ, edge-derived DCD and ISI, slew-limited BUJ) occupy a smaller UI fraction in 200G mode (Table 4-2). |
| Requirement references | FAMILY-NNN refers to the requirement of that ID in Rev 0.7; §x.y without prefix refers to Rev 0.7. |
| Operating points | Compliance point: pre-FEC BER 2.4E-4 (Q = 3.49) — the 802.3dj / OCI anchor (LOG-002). Internal design point: raw BER < 1e-12, FEC-free (Q = 7.034) — the point at which the dual-Dirac budget is stated (Rev 0.7 §3.3). |
| Assembly convention | Bounded terms add linearly (worst-case alignment); Gaussian terms add in RSS. Pessimistic against convolution of the true bounded PDFs — the correct direction for a sign-off budget. |
| Transition density | ρ = 1 (every UI has an edge at risk); ρ = 0.5 would lower Q(1e-12) to 6.94, a 1.3 % relaxation not worth the bookkeeping. |
| Alignment | TIE is measured against the ideal serializer clock; recovered-clock alignment is prohibited (same folding convention as the TP1 eye mask). |
| Placeholders | TBD = value tracked in the requirements database; owner deliverables are listed in Section 9. |

## 1.3 Parent requirement map

**Table 1-1. Rev 0.7 requirements defined or derived by this document**

| **Req ID** | **Rev 0.7 obligation (abridged)** | **This document** | **Section** |
| --- | --- | --- | --- |
| **ELE-002** | JRMS ≤ 0.023 UI rms (216 fs), 802.3dj method. | Adopted limit and applicability notes; internal analog σ_RJ sits 52 % inside it. | 2.3, 6 |
| **ELE-003** | EOJ ≤ 0.025 UI pp (235 fs). | Adopted; the derived DCD lands exactly on it. | 2.3, 5.2 |
| **ELE-004** | J4u ≤ 0.118 UI pp (1.11 ps). | Adopted; it is the ceiling that sizes σ_RJ through the tougher-spec rule. | 2.3, 5.1, 6 |
| **ELE-005** | Dual-Dirac budget at 1e-12: σ_RJ, DCD, ISI, BUJ, DDJ, DJ-dd, TJ; additive bounded, RSS Gaussian at Q = 7.034. | Defined normatively in Table 4-1; every term derived in Section 5. | 4, 5 |
| **ELE-006** | TP1 edge ≤ 0.35 UI typical, 4.0 ps hard max; rise/fall mismatch ≤ 0.35 ps. | Inputs to the DCD (mismatch) and ISI (edge corners) derivations. | 5.2, 5.3 |
| **ELE-008** | Inter-tap matching ≤ 2.6 % UI. | Contributor to the FIR slice-DCD adder (Open item 3). | 5.2, 5.5 |
| **SYS-002** | Clock-chain phase-noise budget to σ_RJ ≤ 104 fs rms; refclk specification derived accordingly. | Clock-chain build-up and required re-partition (142 → ≤ 104 fs). | 5.1 |
| **DTX-001** | TX jitter well under 0.3 UI pk-pk before optical penalties. | TJ(1e-12) ≤ 0.278 UI is the quantitative form. | 5.5 |
| **EMC-003** | Aggregate crosstalk within BUJ ≤ 0.036 UI (339 fs). | Coupling bound ≤ 2.5 % at the worst-case slew corner. | 5.4 |
| **EMC-004** | Spur limits from the ELE-004 ceiling. | Supply-coupled periodic jitter is carried inside BUJ, not budgeted separately. | 5.4 |
| **LOG-002** | 2.4E-4 compliance point; RS-only host FEC. | Q table; the 1e-12 point is the internal design margin above it. | 3.3 |
| **CMP-007** | TP1 jitter met in UI in both modes; 200G absolutes 433 fs / 471 fs / 2.22 ps. | 200G columns; hardware-fixed terms re-expressed in 200G UI. | 2.3, 4.2 |

# 2. Reference Points and Adopted Standard Limits

## 2.1 Test points

**Table 2-1. CPO transmit test points**

| **Point** | **Location** | **Domain** | **What binds there** | **Access** | **Req** |
| --- | --- | --- | --- | --- | --- |
| **TP1** | Electrical input of the MRM, after the TX microbump pad (EIC → PIC boundary) | Electrical | All TX electrical limits: this document, DES-OCI-106G-TXD-001 | None — buried in-package; verified by simulation, on-die instrumentation, test vehicle | ELE-001 |
| **TP2** | Optical output at the fiber reference plane | Optical | OCI Table 2-2 TX optical: TDEC, OMA, ER, transition time (TXO family) | Bench-accessible compliance point | Rev 0.7 §4.1 |
| **TP3** | Optical input at the fiber reference plane (receiver counterpart) | Optical | Sensitivity, SRS, JTOL (RXO, DRX-006) | Bench-accessible | Rev 0.7 §4.2 |

## 2.2 Test-point location diagram

**Figure 2-1. TP1 test-point location diagram**

*\[FIGURE PLACEHOLDER — insert test-point location diagram here. Suggested content: a simplified single-channel version of DES-OCI-106G-TXD-001 Figure 2-1, drawn to show where the TP1 budget binds, with the Location, Domain and Access columns of Table 2-1 as annotations on each test point. Chain, left to right: TX PLL and serializer (host-derived line clock from the reference, LC-PLL and distribution chain of DES-OCI-106G-CLK-001) → pre-driver (0 / 1 / 2 UI branch phases) → TX driver (3-tap analog FIR, hard clip, series peaking) → TP1 → TX microbump and pad (EIC → PIC boundary) → micro-ring modulator → bus waveguide → Band-Mux → fiber → TP2; optionally the far-end fiber input as TP3. Mark TP1 as a buried, in-package electrical reference plane at the differential input of the MRM after the microbump pad, extracted load ≈ 150 fF (DES-OCI-106G-TXD-001 Table 2-3), with the note “no physical access — verified by simulation, on-die instrumentation (edge monitor, eye / jitter monitor, static-level readback) and the driver test vehicle with probe-able replica pad” (Section 7); mark TP2 as the bench-accessible optical compliance point at the fiber reference plane (OCI Table 2-2 TX optical limits; TXO family, outside this budget), bound to TP1 through the MRM electro-optic model (ELE-001). Annotate the jitter contributors of Table 4-1 at the stage where each arises and show them all summing at TP1: clock chain (reference + LC-PLL + distribution + serializer) → random jitter σ_RJ ≤ 104 fs rms (Section 5.1) and the DCC-residual part of DCD; serializer / pre-driver / driver edge asymmetry → duty-cycle distortion DCD ≤ 235 fs pp (Section 5.2) plus the FIR slice-DCD adder (0.05 UI, Section 5.5); driver edge rate and settling into the TP1 load → ISI jitter ≤ 113 fs pp (Section 5.3); crosstalk from the other three WDM lanes and supply-coupled spurs entering the driver and pad → bounded uncorrelated jitter BUJ ≤ 339 fs pp (Section 5.4); the dual-Dirac assembly DJ_δδ and TJ at 1e-12 stated at TP1 (Section 5.5) and the 802.3dj clock-jitter limits adopted there (Section 2.3, Table 2-2). Everything to the right of TP1 is optical (TDEC, ER, transition time) and belongs to the TXO family, not to this budget. Electrical path solid, optical path drawn as a waveguide / fiber line, jitter-contributor call-outs as dashed arrows onto TP1.\]*

## 2.3 802.3dj clock-jitter limits adopted at TP1

**Table 2-2. Adopted limits (802.3dj 179.9.4.6 via Annex 176C/176D at 106.25 ± 50 ppm GBd)**

| **Metric (D1.3 / D3.1 name)** | **Subclause (D3.1)** | **Limit at TP1** | **400G OCI mode** | **200G OCI mode** | **Bounds** | **Req** |
| --- | --- | --- | --- | --- | --- | --- |
| **Signaling rate** | 179.9.4.1 | 106.25 GBd ± 50 ppm (53.125 in 200G mode) | — | — | Baud-rate accuracy (in-package PMA tolerance) | TXO-001 |
| **JRMS03 / JHRMS** | 179.9.4.7.1 | ≤ 0.023 UI rms | ≤ 216 fs rms | ≤ 433 fs rms | RMS clock jitter, slope-extrapolated, additive noise removed | ELE-002 |
| **EOJ03** | 179.9.4.7.3 | ≤ 0.025 UI pp | ≤ 235 fs pp | ≤ 471 fs pp | Even–odd jitter — the DCD analog | ELE-003 |
| **J4u03 / JH4u** | 179.9.4.7.2 | ≤ 0.118 UI pp (D1.3 Class A; D3.1 single value) | ≤ 1.11 ps pp | ≤ 2.22 ps pp | Bounded high-probability clock jitter, all-but-1E-4 interval | ELE-004 |

**Table 2-3. Applicability notes**

| **Note** | **Statement** | **Consequence** |
| --- | --- | --- |
| **(a) PAM4 numbers on an NRZ link** | No NRZ electrical standard exists at 106.25 GBd. EOJ03 is even–odd jitter on PAM4 levels 0↔3 — full-swing edges, the only kind NRZ has. JHRMS / JH4u fit timing spread vs. edge slope and extrapolate to infinite slope, isolating clock phase noise, which is modulation-agnostic at the same baud. | Limits transfer to NRZ directly; no UI-relative-analog caveat (Rev 0.7 B6). |
| **(b) dj books no ISI / DDJ** | Transition locations, thresholds, and the JH extrapolation exclude pattern-dependent closure. | ISI and DDJ are allocated only by the internal budget (Section 4) and enforced by the ELE-006 edge window and the TP1 eye mask. |
| **(c) TP1 is unprobeable** | The only accessible compliance points are optical TP2 / TP3. | Table 2-2 binds design verification (Section 7), not a bench test. Measurement recipe when simulated: BT4 at 60 GHz, AC-coupled 50 Ω, CRU 4 MHz / 20 dB per decade, PRBS13Q (PRBS9Q allowed). |
| **(d) Draft tracking** | Rev 0.7 cites D1.3; D3.1 names and numbering are noted in Table 2-2. Values are unchanged between drafts; D3.1 collapses the per-host-class J4u values to one. | Re-check at each adopted draft and at ratification (Rev 0.7 §9 “802.3dj clause chain”). |
| **(e) 200G-mode cross-check** | The same UI-relative limits apply at 53.125 GBd; the baud-matched OIF reference there is CEI-112G-XSR (JRMS ≤ 0.0224 UI, EOJ ≤ 0.025 UI). | CMP-007. |

# 3. Dual-Dirac Framework

## 3.1 Taxonomy

**Table 3-1. Timing-error terms at the TP1 mid-level crossing, by physical origin**

| **Term** | **Symbol** | **Nature** | **Physical origin** | **Derived in** |
| --- | --- | --- | --- | --- |
| **Random jitter** | σ_RJ | Unbounded, Gaussian | Thermal / flicker phase noise of PLL, clock distribution, phase interpolator, serializer | 5.1 |
| **Duty-cycle distortion** | DCD | Bounded, data-correlated | Half-rate-clock duty-cycle error; rise/fall delay mismatch | 5.2 |
| **ISI jitter** | ISI | Bounded, data-correlated | Finite bandwidth: incomplete settling of prior symbols shifts the crossing | 5.3 |
| **Bounded uncorrelated jitter** | BUJ | Bounded, data-uncorrelated | Crosstalk from adjacent WDM lanes; supply-coupled periodic jitter | 5.4 |
| **Data-dependent jitter** | DDJ = DCD + ISI | Bounded | Sum of the data-correlated terms | 5.5 |
| **Deterministic total** | DJ_δδ = DDJ + BUJ (+ FIR slice-DCD adder) | Bounded | Linear sum of all bounded terms | 5.5 |
| **Total jitter at BER** | TJ(BER) = DJ_δδ + 2·Q(BER)·σ_RJ | Composite | Dual-Dirac opening at the target BER | 5.5 |

## 3.2 Model

**Table 3-2. Dual-Dirac model and assembly rules**

| **Element** | **Statement** |
| --- | --- |
| **Measured PDF** | Convolution of the bounded DJ PDF with the Gaussian RJ PDF. |
| **Dual-Dirac approximation** | Bounded PDF replaced by two impulses separated by DJ_δδ; each eye edge contributes a Gaussian of width σ_RJ centred DJ_δδ / 2 inside the ideal edge. |
| **Tail probability** | P(edge intrudes a distance t past its Dirac centre) = ½ · erfc(t / (σ√2)). |
| **Q-factor** | BER = ½ · erfc(Q / √2) defines Q(BER). |
| **Total jitter opening** | TJ(BER) = DJ_δδ + 2 · Q(BER) · σ_RJ — Dirac separation plus a Q·σ tail on each side. |
| **Bounded terms** | Add linearly (worst-case alignment of bounded distributions). |
| **Gaussian terms** | Add in RSS (independent sources). |
| **Direction of error** | Pessimistic against convolution of the true bounded PDFs — correct for sign-off. |

## 3.3 Q table

**Table 3-3. Q-factor at the relevant BER points (ρ = 1)**

| **BER** | **Q** | **Role** |
| --- | --- | --- |
| **1E-4** | 3.719 | JH4u interval (all-but-1E-4); used in the tougher-spec rule (Section 5.1) |
| **2.4E-4** | 3.49 | 802.3dj / OCI pre-FEC compliance anchor (LOG-002) |
| **1E-8** | 5.612 | Intermediate (extrapolation check) |
| **1E-12** | 7.034 | Internal FEC-free design point at which Table 4-1 is stated; 2Q = 14.07 |

# 4. Internal Dual-Dirac Budget at TP1 (ELE-005)

802.3dj contains no dual-Dirac decomposition, no DDJ sub-allocation, no BUJ, and no total-jitter-at-BER metric; every dj limit is anchored to RS-FEC operation at 2.4E-4. The budget the design needs at its 1e-12 FEC-free point therefore cannot be sourced from any standard and is defined normatively here.

**Table 4-1. Normative budget (UI-relative; absolutes per mode)**

| **Quantity** | **Symbol** | **Requirement (UI)** | **400G OCI mode** | **200G OCI mode** | **Set by** | **Section** |
| --- | --- | --- | --- | --- | --- | --- |
| **RMS random jitter** | σ_RJ | ≤ 0.011 UI rms | ≤ 104 fs | ≤ 207 fs | JH4u ceiling via the tougher-spec rule | 5.1 |
| **Duty-cycle distortion** | DCD | ≤ 0.025 UI pp | ≤ 235 fs | ≤ 471 fs | Rise/fall mismatch + DCC residual | 5.2 |
| **ISI jitter** | ISI | ≤ 0.012 UI pp | ≤ 113 fs | ≤ 226 fs | Settling model at the 4.0 ps hard-max edge | 5.3 |
| **Bounded uncorrelated jitter** | BUJ | ≤ 0.036 UI pp | ≤ 339 fs | ≤ 678 fs | Crosstalk slew model, ≤ 2.5 % coupling | 5.4 |
| **Data-dependent jitter** | DDJ = DCD + ISI | ≤ 0.037 UI pp | ≤ 348 fs | ≤ 696 fs | Linear sum | 5.5 |
| **Deterministic total, FIR-included (baseline)** | DJ_δδ | ≤ 0.123 UI pp | ≤ 1.16 ps | ≤ 2.32 ps | DDJ + BUJ + 0.05 UI FIR slice-DCD adder | 5.5 |
| **Deterministic total, no-FIR (removal study)** | DJ_δδ | ≤ 0.073 UI pp | ≤ 0.69 ps | ≤ 1.37 ps | DDJ + BUJ | 5.5 |
| **Total jitter at 1e-12, FIR-included** | TJ | ≤ 0.278 UI pp | ≤ 2.61 ps | ≤ 5.23 ps | DJ_δδ + 14.07 · σ_RJ | 5.5 |
| **Total jitter at 1e-12, no-FIR** | TJ | ≤ 0.228 UI pp | ≤ 2.14 ps | ≤ 4.29 ps | DJ_δδ + 14.07 · σ_RJ | 5.5 |
| **Eye-mask half-closure, FIR-included / no-FIR** | X₁ = TJ / 2 | 0.139 / 0.114 UI | 1.31 / 1.07 ps | 2.62 / 2.15 ps | Input to the TP1 eye mask | 5.5 |

*0.011 UI × 9.412 ps = 103.5 fs, carried as 104 fs to match ELE-005 and SYS-002 (a rounded 100 fs is not used). The 200G-mode column is the UI-relative budget scaled to 18.824 ps (Rev 0.7 §6 convention); Table 4-2 shows that the hardware-fixed terms actually consume far less of it.*

## 4.2 Hardware-fixed terms in 200G OCI mode

**Table 4-2. Terms fixed in seconds by the hardware, re-expressed in the 18.824 ps UI (CMP-007 check)**

| **Term** | **Hardware value (both modes)** | **400G UI fraction** | **200G UI fraction** | **Budget (UI)** | **Margin in 200G mode** |
| --- | --- | --- | --- | --- | --- |
| **σ_RJ (clock chain)** | ≤ 104 fs rms | 0.011 | 0.0055 | 0.011 | 2× (clock RJ in seconds is baud-independent to first order) |
| **DCD — rise/fall term** | 0.175 ps (½ × 0.35 ps mismatch) | 0.0186 | 0.0093 | — | — |
| **DCD — DCC residual** | ±0.3 % duty ⇒ 0.006 UI (UI-relative, stays) | 0.006 | 0.006 | — | — |
| **DCD total** | — | 0.0246 | 0.0153 | 0.025 | 1.6× |
| **ISI (4.0 ps edge, τ = 2.89 ps)** | 0.115 ps at T = 9.412 ps; 0.004 ps at T = 18.824 ps | 0.012 | 0.0002 | 0.012 | ≈ 50× (settling essentially complete in a 2× longer UI) |
| **BUJ (slew model, 51 mV at 0.30 V/ps)** | 0.339 ps | 0.036 | 0.018 | 0.036 | 2× |
| **TJ(1e-12), FIR-included** | ≈ 2.61 ps worst case (all terms at 400G hardware values) | 0.278 | ≈ 0.139 | 0.278 | ≈ 2×; horizontal eye ≈ 0.86 UI |

# 5. Derivation of Each Term

## 5.1 Random jitter σ_RJ — clock-chain build-up (SYS-002)

RJ at TP1 is the integrated phase noise of the clock generation and distribution chain, σ_t = φ_rms / (2π f_clk), with independent Gaussian sources added in RSS. The integration band is 4 MHz to f_baud / 2: the far-end CRU / CDR high-pass removes tracked low-frequency jitter.

**Table 5-1. Clock-chain contributors (fs rms)**

| **Contributor** | **First-cut allocation** | **Required re-partition (example)** | **Basis** | **Owner** |
| --- | --- | --- | --- | --- |
| **TX PLL (4 MHz – f_baud/2)** | 100 | 72 | State-of-the-art 53.125 GHz LC-PLL class | Analog (TBD) |
| **Clock distribution buffers** | 60 | 45 | Supply-noise-limited | Analog (TBD) |
| **Phase interpolator (DNL + intrinsic)** | 70 | 50 | 5-bit PI class (DES-OCI-106G-CDR-001 Table 3-1) | Analog (TBD) |
| **Serializer / final 2:1 mux** | 40 | 30 | — | Analog (TBD) |
| **RSS total** | ≈ 142 | ≈ 103 | √(Σ x²) | — |
| **Allocation (Table 4-1)** | ≤ 104 (0.011 UI) | ≤ 104 | Set by the JH4u ceiling, not by the build-up (Table 5-2) | SYS-002 |
| **Gap** | 1.37× over (≈ 2.7 dB integrated phase-noise power) | Closes | Binding design risk — kill-or-confirm (Rev 0.7 R8) | Open item 1 |

**Table 5-1b. Build-up variants — the phase-interpolator question**

| **Variant** | **Terms (fs rms)** | **RSS (fs)** | **Gap to 104 fs** | **When it applies** |
| --- | --- | --- | --- | --- |
| **With PI in TX path** | PLL 100, distribution 60, PI 70, serializer 40 | 142 | 1.37× (2.7 dB) | TX contains a 5-bit phase interpolator in the serializer clock path (e.g. for FIR tap-delay generation — DES-OCI-106G-TXD-001 Table 6-3, TBD) |
| **No PI in TX path** | PLL 100, distribution 60, serializer 40 | 123 | 1.19× (1.5 dB) | Tap phases generated in the serializer domain without a PI; the 70 fs PI term belongs to the receive-side CDR chain (DES-OCI-106G-CLK-001 Section 9) |
| **PI present, DNL reclassified** | PLL 100, distribution 60, PI intrinsic ≈ 40, serializer 40; PI DNL → bounded (added to DJ_δδ) | 130 | 1.25× (1.9 dB) | PI present; its DNL is deterministic and belongs in the bounded budget, not in RSS |
| **Decision** | DES-OCI-106G-TXD-001 Table 6-3 (tap-delay generation, CDNS) fixes which variant is real; until then the with-PI 142 fs is the conservative planning figure | — | — | Open item 1 |

**Table 5-2. Tougher-spec rule sizing σ_RJ**

| **Step** | **Statement** | **Value** |
| --- | --- | --- |
| 1 | The JH family excludes data-correlated jitter; its internal analog is the clock-visible jitter at 1E-4: BUJ + 2 · Q(1E-4) · σ_RJ | — |
| 2 | Fix BUJ at its allocation | 0.036 UI |
| 3 | Require the analog to land on the JH4u ceiling | ≤ 0.118 UI |
| 4 | Solve: σ_RJ ≤ (0.118 − 0.036) / (2 × 3.719) | ≤ 0.011 UI = 104 fs |
| 5 | Cross-check against JHRMS ≤ 0.023 UI rms (clock-only, slope-extrapolated) | Target is 52 % inside the ceiling — consistent |

## 5.2 Duty-cycle distortion DCD

**Table 5-3. DCD model and evaluation at the ELE-006 hardware limits**

| **Mechanism** | **Model** | **Input** | **Contribution** | **Req** |
| --- | --- | --- | --- | --- |
| **Half-rate clock duty cycle** | Final 2:1 mux clocked at f_baud / 2 (53.125 GHz; 26.5625 GHz in 200G mode): even/odd widths 2D·UI and 2(1−D)·UI ⇒ DCD_duty = │2D − 1│ · UI | DCC loop holds D = 50 % ± 0.3 % | 0.006 UI | SYS-001 |
| **Rise/fall mismatch** | Differential Δt_rf = │t_r − t_f│ shifts the mid-level crossing by half the mismatch on alternating polarities ⇒ DCD_rf ≈ Δt_rf / 2 | Δt_rf ≤ 0.35 ps | 0.175 ps = 0.0186 UI | ELE-006 |
| **Sum** | DCD = 0.0186 + 0.006 | — | 0.0246 UI ⇒ allocation 0.025 UI pp (235 fs) | ELE-005 |
| **Standards anchor** | Lands exactly on EOJ03 ≤ 0.025 UI — a sanity anchor, not a coincidence to rely on | — | Coincident | ELE-003 |
| **FIR slice-DCD adder (FIR-included baseline only)** | Tap-slice skew in the 3-tap analog FIR, booked by the link budget as a separate adder in DJ_δδ; zero in the no-FIR configuration | ELE-008 matching ≤ 0.026 UI is one contributor | ≈ 0.05 UI | ELE-008; Open item 3 |
| **Partitioning** | DCC residual vs. Δt_rf split | TBD | — | Open item 2 |

**Table 5-3b. FIR slice-DCD adder — decomposition by simulation (3-tap FIR, second-order slices ζ = 0.7, 4.0 ps edge)**

| **Mechanism** | **Stimulus** | **Effect on composite TP1 crossing** | **Conclusion** |
| --- | --- | --- | --- |
| **Tap-slice phase skew** | Pre or post slice skewed by the ELE-008 limit, ± 0.026 UI, all sign combinations | ≤ 0.0003 UI | Negligible: side slices have settled by the main crossing, so skew changes pre-emphasis shape, not timing. Skew is not the origin of the adder. |
| **Per-slice DCD** | All three slices carry 0.025 UI DCD | 0.025 UI | Passes through 1:1 via the main slice — already counted in the DCD row; no additional adder. |
| **Bank asymmetry (ELE-010)** | Logic-1 bank side taps −0.25 / logic-0 bank side taps −0.15 (Δw = 0.10 per side tap) | 0.038 UI apparent DCD | Rising and falling composite edges have different shapes ⇒ different crossing times. Sensitivity ≈ 0.19 UI per unit Δw per side tap (both sides changed equally). |
| **Bank asymmetry** | Δw = 0.15 per side tap | 0.057 UI | Brackets the 0.05 UI adder: 0.05 UI ⇔ Δw ≈ 0.13 per side tap. |
| **Bank asymmetry** | Δw = 0.25 (one bank with side taps off) | 0.093 UI | Full-range asymmetry would nearly double the adder. |
| **Derived constraint JIT-D2** | Programmed logic-1 / logic-0 side-tap difference | │Δw_pre│ + │Δw_post│ ≤ 0.26 (≈ 0.13 per side) keeps the apparent DCD ≤ 0.05 UI | Constraint on the ELE-010 bank contents (DES-OCI-106G-TXD-001 Table 6-1). Whether this intentional pre-distortion counts as TP1 timing error or is credited back at TP2 through the MRM asymmetry it corrects is a link-budget attribution decision (Open item 3, narrowed). |

**Table 5-3c. DCD margin against the 0.025 UI allocation**

| **Rise/fall mismatch** | **DCC residual** | **DCD (UI)** | **Margin** | **Status** |
| --- | --- | --- | --- | --- |
| **0.35 ps (ELE-006 limit)** | ± 0.3 % (limit) | 0.0246 | 1.6 % | Both terms at limit — effectively zero margin |
| **0.35 ps** | ± 0.2 % | 0.0226 | 9.6 % | Recommended design target: hold the ELE-006 mismatch limit, tighten the DCC target |
| **0.30 ps** | ± 0.3 % | 0.0219 | 12.3 % | Alternative: tighten mismatch, hold DCC |
| **0.30 ps** | ± 0.2 % | 0.0199 | 20.3 % | Both tightened |
| **0.25 ps** | ± 0.2 % | 0.0173 | 30.9 % | Stretch |
| **Disposition** | ELE-006 mismatch limit 0.35 ps unchanged; DCC design target ± 0.2 % with ± 0.3 % as the limit (allocation still met, 1.6 %, at the limit) | — | — | Open item 2 closed |

## 5.3 ISI jitter — first-order settling model

Driver plus the ≈ 150 fF MRM-and-pad load is modelled as a first-order system with time constant τ; t_20–80 = τ · ln 4 = 1.386 τ. For a rising edge starting from a history-dependent voltage V₀, v(t) = 1 − (1 − V₀)·e^(−t/τ) on a normalised ±1 swing: a settled start crosses at τ·ln 2, a start one UI after the previous transition crosses early. The displacement for run length k is τ·e^(−kT/τ) to first order, and the worst-case pk-pk ISI over all run lengths (exercised by PRBS31) is the geometric sum ISI_pp ≈ τ · e^(−T/τ) / (1 − e^(−T/τ)), T = UI.

**Table 5-4. ISI at the ELE-006 transition-time corners (T = 9.412 ps)**

| **20–80 % edge** | **Corner** | **τ (ps)** | **ISI_pp (ps)** | **ISI_pp (UI)** | **Note** |
| --- | --- | --- | --- | --- | --- |
| **3.3 ps (0.35 UI)** | ELE-006 typical | 2.38 | 0.047 | 0.005 | — |
| **3.6 ps (0.38 UI)** | Intermediate corner | 2.60 | 0.071 | 0.008 | Headroom to the allocation covers second-order response, microbump reflections, C_PN(V) |
| **4.0 ps (0.42 UI)** | ELE-006 hard maximum | 2.89 | 0.115 | 0.012 | Allocation must hold at the slowest edge the design may ship ⇒ ISI ≤ 0.012 UI pp (113 fs) |
| **Validation** | Extracted two-pole fits vs. the first-order model | — | — | — | TBD from simulation sweep (Open item 4) |

**Table 5-4b. Second-order settling — ISI vs. damping at fixed 20–80 % edge (worst case over all 10-bit histories)**

| **Damping ζ** | **Electrical overshoot** | **ISI_pp at 3.3 ps edge (UI)** | **ISI_pp at 4.0 ps edge (UI)** | **Against 0.012 UI allocation** |
| --- | --- | --- | --- | --- |
| **First-order (reference)** | 0 % | 0.005 | 0.012 | At limit (first-order model) |
| **1.0 (critical)** | 0 % | 0.002 | 0.006 | 2× margin — second-order settles faster than first-order at equal 20–80 % |
| **0.8** | 1.5 % | 0.006 | 0.010 | Inside allocation |
| **0.7** | 4.6 % | 0.016 | 0.029 | 2.4× over |
| **0.6** | 9.5 % | 0.036 | 0.065 | 5.4× over |
| **0.5** | 16.3 % | 0.079 | 0.127 | 10× over |
| **Derived constraint JIT-D1** | TP1 electrical overshoot ≤ 2 % (ζ ≥ 0.8) at the 4.0 ps hard-max edge under the extracted load | — | — | The series inductive peaking (L_out) and any resistive-feedback enhancement in the driver shall be damped to this limit; handed to DES-OCI-106G-TXD-001 Table 5-2. The 22 % TXO-008 optical overshoot limit at TP2 is a separate, much looser quantity. |

*The first-order model is therefore not an optimistic bound: the risk is peaking, not bandwidth. With JIT-D1 in place the ISI allocation has ≥ 20 % margin at the hard-max edge; extracted two-pole validation (Open item 4) becomes a confirmation of ζ rather than of the model class.*

## 5.4 Bounded uncorrelated jitter BUJ — crosstalk slew model (EMC-003)

**Table 5-5. Slew-rate conversion of aggressor voltage to timing**

| **Step** | **Statement** | **Worst-case corner (2.0 Vppd, 4.0 ps)** | **Typical corner (2.5 Vppd, 3.6 ps)** |
| --- | --- | --- | --- |
| **Model** | A data-uncorrelated perturbation V_x at the crossing converts through the edge slew rate: Δt_pp = 2 · V_x / SR (aggressor pushes either way) | — | — |
| **Slew rate** | SR ≈ 0.6 · V_pp / t_20–80 | 0.300 V/ps | 0.417 V/ps |
| **Allocation** | BUJ ≤ 0.036 UI pp = 0.339 ps | 0.339 ps | 0.339 ps |
| **Tolerable aggressor sum** | V_x ≤ SR · Δt / 2 | 51 mV | 71 mV |
| **Coupling bound** | V_x / V_pp | ≤ 2.5 % of all simultaneously switching WDM lanes plus supply-coupled spurs | ≤ 2.5 % ⇒ 63 mV (bound not binding at this corner) |
| **Periodic jitter** | Supply-spur PJ is carried inside BUJ, not budgeted separately | EMC-004 spur limits derive from the same ceiling | — |
| **Verification** | Extracted crosstalk with all lanes active vs. the coupling bound | TBD from simulation sweep (Open item 5) | — |

## 5.5 Assembly, sensitivity, and eye-mask input

**Table 5-6. Assembly at BER 1e-12 (Q = 7.034, 2Q = 14.07)**

| **Configuration** | **DCD** | **ISI** | **BUJ** | **FIR adder** | **DJ_δδ (UI pp)** | **σ_RJ (UI rms)** | **TJ(1e-12) (UI pp)** | **TJ (ps, 400G)** | **Horizontal eye at TP1** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **FIR-included — current baseline** | 0.025 | 0.012 | 0.036 | 0.050 | 0.123 | 0.011 | 0.278 | 2.61 | 0.722 UI = 6.80 ps |
| **No-FIR — removal-study configuration** | 0.025 | 0.012 | 0.036 | 0 | 0.073 | 0.011 | 0.228 | 2.14 | 0.772 UI = 7.27 ps |

**Table 5-7. Sensitivity and derived inputs**

| **Item** | **Value** | **Consequence** |
| --- | --- | --- |
| **∂TJ / ∂σ_RJ at 1e-12** | 2Q = 14.07 | Every 10 fs rms of clock jitter costs 141 fs of eye; bounded terms trade 1:1. Clock-chain phase noise, not edge rate, is where design effort buys the most margin — hence the σ_RJ kill-or-confirm flag (R8). |
| **∂TJ / ∂(bounded term)** | 1 | DCD, ISI, BUJ, and the FIR adder each trade one-for-one with eye. |
| **Eye-mask half-closure X₁ = TJ / 2** | 0.139 UI (FIR-included); 0.114 UI (no-FIR) | Horizontal coordinate of the TP1 eye mask; 1.31 / 1.07 ps in 400G mode. |
| **DTX-001 working target** | TX jitter well under 0.3 UI pk-pk before optical penalties | Satisfied by TJ ≤ 0.278 UI at 1e-12 (and by a wide margin at the 2.4E-4 compliance point, where 2Q = 6.98 ⇒ TJ ≈ 0.20 UI). |

## 5.6 Robustness of the σ_RJ requirement — statistical DJ combination

The linear (worst-case-additive) bounded-term convention and ρ = 1 were reviewed as possible over-conservatism that might be forcing the 104 fs clock requirement. The bounded terms were instead convolved as independent distributions (DCD dual-Dirac; ISI as its actual pattern PDF from the settling model; BUJ dual-Dirac or uniform), combined with the Gaussian RJ, and the 1e-12 opening solved directly (no-FIR configuration, TJ = 0.228 UI).

**Table 5-8. Statistical vs. linear DJ combination at BER 1e-12**

| **Combination** | **TJ at σ_RJ = 0.011 UI** | **σ_RJ allowed for TJ = 0.228 UI** | **Relaxation** |
| --- | --- | --- | --- |
| **Linear worst-case (baseline convention)** | 0.228 UI | 0.011 UI = 104 fs | — |
| **DCD dual-Dirac ⊗ ISI pattern PDF ⊗ BUJ dual-Dirac** | 0.221 UI | 0.0115 UI = 109 fs | + 5 % |
| **DCD dual-Dirac ⊗ ISI pattern PDF ⊗ BUJ uniform** | 0.213 UI | 0.0122 UI = 114 fs | + 10 % |
| **All three dual-Dirac** | 0.221 UI | 0.0115 UI = 108 fs | + 4 % |
| **ρ = 0.5 instead of 1** | Q(1e-12) 7.034 → 6.937 | ≈ + 1.4 % | Not worth the bookkeeping; ρ = 1 retained |
| **Conclusion** | The bounded terms are small relative to 2Qσ, so their combination rule barely matters | σ_RJ ≤ 104–114 fs whichever convention is adopted | The requirement is robust; the clock chain must improve (or the PI term must be shown absent, Table 5-1b). Linear convention retained for sign-off. |

**Table 5-9. Margin at the 2.4E-4 compliance point (Q = 3.49, 2Q = 6.98)**

| **Configuration** | **DJ_δδ (UI)** | **TJ(2.4E-4) (UI)** | **Horizontal eye** | **vs. TJ(1e-12)** |
| --- | --- | --- | --- | --- |
| **FIR-included** | 0.123 | 0.200 | 0.800 UI = 7.53 ps | 0.078 UI of the eye is the internal 1e-12 margin above the compliance point |
| **No-FIR** | 0.073 | 0.150 | 0.850 UI = 8.00 ps | 0.078 UI |

# 6. Crosswalk Between the Two Limit Sets

The two tables do not map term-for-term: the dj JH family isolates clock jitter (slope-extrapolated, pattern-dependent closure excluded), while the internal budget decomposes all timing error at TP1 by physical origin.

**Table 6-1. 802.3dj limits vs. internal budget**

| **dj metric** | **dj limit** | **Internal analog** | **Internal value** | **Status** | **Req** |
| --- | --- | --- | --- | --- | --- |
| **JHRMS** | ≤ 0.023 UI rms | σ_RJ | ≤ 0.011 UI rms | Consistent — 52 % inside the dj ceiling | ELE-002 / ELE-005 |
| **EOJ03** | ≤ 0.025 UI pp | DCD | ≤ 0.025 UI pp | Coincident — the DCD derivation lands exactly on the dj ceiling | ELE-003 / ELE-005 |
| **JH4u** | ≤ 0.118 UI pp | Clock-visible jitter at 1E-4: BUJ + 2·Q(1E-4)·σ_RJ = 0.036 + 0.082 | 0.118 UI pp | Coincident — σ_RJ sized to land on the dj ceiling (tougher-spec rule) | ELE-004 / ELE-005 |
| **—** | — | ISI, DDJ | ≤ 0.012 / 0.037 UI pp | No dj counterpart (note b) | ELE-005 |
| **—** | — | TJ(1e-12), X₁ | ≤ 0.278 / 0.139 UI (FIR-included); 0.228 / 0.114 (no-FIR) | No dj counterpart — dj has no total-jitter-at-BER metric | ELE-005 |

## 6.2 TP1 eye-mask definition

The TP1 eye mask referenced by DES-OCI-106G-TXD-001 is defined here from the budget. Horizontal coordinates follow from TJ; the vertical coordinate is proposed from the minimum drive swing and the BUJ coupling bound and is to be confirmed with the MRM model (Open item 7).

**Table 6-2. TP1 differential eye mask (hexagon; coordinates relative to the ideal crossing, UI = 9.412 ps in 400G mode)**

| **Coordinate** | **Definition** | **FIR-included** | **No-FIR** | **Basis** |
| --- | --- | --- | --- | --- |
| **X₁ (mask tip, zero crossing)** | TJ(1e-12) / 2 | 0.139 UI (1.31 ps) | 0.114 UI (1.07 ps) | Table 4-1 |
| **X₂ (mask shoulder)** | X₁ + t_20–80,max / UI × 0.3 | 0.27 UI | 0.24 UI | Shoulder set so the 4.0 ps hard-max edge at ≥ 30 % amplitude clears the mask; confirm against extracted edges |
| **Y₁ (mask half-height at the shoulder)** | (V_swing,min / 2) × (1 − 2 × 0.025 coupling − overshoot 0.02) = 0.5 × 2.0 V × 0.93 | ± 0.93 V (proposed) | ± 0.93 V (proposed) | DES-OCI-106G-TXD-001 Table 5-3 minimum swing; Table 5-5 coupling bound; JIT-D1 overshoot |
| **Y₂ (outer limit)** | V_high,max + 2 % overshoot | Per drive option | Per drive option | JIT-D1; ESD clamp margin (TXD Table 5-3) |
| **Alignment** | Ideal serializer clock; recovered-clock alignment prohibited; folding over 1 UI | — | — | Section 1.2 |
| **Patterns / conditions** | PRBS13, PRBS31; all PVT corners; all legal tap codes and both banks; all lanes active | — | — | Table 2-3 (c), Table 7-1 |
| **Hit criterion** | Zero mask hits over the simulated record; tails extrapolated per Table 7-1 step 4 | — | — | ELE-001 |

# 7. Verification Methodology at TP1 (ELE-001)

**Table 7-1. Simulation-based extraction sequence**

| **Step** | **Procedure** | **Output** | **Compared against** |
| --- | --- | --- | --- |
| **1 — TIE extraction** | Transient simulation of the extracted driver + 150 fF MRM-and-pad load; PRBS13 and PRBS31; all PVT corners and legal tap codes; record time-interval error of each differential mid-level crossing against the ideal serializer clock (recovered-clock alignment prohibited) | TIE record per corner | — |
| **2 — DDJ separation** | Average the waveform per pattern context (e.g. 5-bit history); crossing spread of the averaged waveforms = DDJ; even/odd separation within it = DCD; remainder = ISI | DCD, ISI, DDJ | Tables 5-3, 5-4 |
| **3 — BUJ / PJ separation** | Aggressor lanes toggling, victim pattern fixed; added non-Gaussian TIE = BUJ; spectral lines identify supply-coupled PJ | BUJ, PJ | Table 5-5 coupling bound |
| **4 — RJ and TJ extrapolation** | Dual-Dirac fit of the TIE histogram tails ⇒ σ_RJ and DJ_δδ; extrapolate to 1e-12 via the Table 3-3 Q values (direct simulation of 1e12 bits is infeasible; Q-scale extrapolation is the committed convention) | σ_RJ, DJ_δδ, TJ(1e-12) | Table 4-1 |
| **5 — Standards metrics** | Apply the 179.9.4 recipe (BT4 60 GHz, 4 MHz CRU, PRBS13Q) to the same TIE record | JHRMS, EOJ03, JH4u | Table 2-2 |
| **6 — Correlation** | Repeat steps 1–5 on the driver test vehicle and against on-die instrumentation readbacks | Model-to-silicon correlation | ELE-001 |

**Table 7-2. Verification matrix**

| **Req** | **Item** | **Method** | **Pass criterion (400G mode; 200G in UI)** |
| --- | --- | --- | --- |
| **ELE-002/003/004** | Adopted 802.3dj limits | Step 5 | JHRMS ≤ 0.023 UI rms; EOJ03 ≤ 0.025 UI pp; JH4u ≤ 0.118 UI pp |
| **ELE-005** | Dual-Dirac budget | Steps 2–4 | Each term within Table 4-1; TJ(1e-12) ≤ 0.278 UI (FIR) / 0.228 UI (no-FIR) |
| **SYS-002** | Clock-chain σ_RJ | Phase-noise integration 4 MHz – f_baud/2 of the re-partitioned chain | ≤ 104 fs rms |
| **ELE-006 → 5.2 / 5.3** | Edge and mismatch inputs | Step 1 at the 4.0 ps corner | DCD ≤ 0.025 UI; ISI ≤ 0.012 UI at the hard-max edge |
| **EMC-003** | Crosstalk coupling | Step 3, all lanes active, worst-case tap codes | V_x ≤ 51 mV (≤ 2.5 %) at 2.0 Vppd / 4.0 ps |
| **CMP-007** | Dual-rate | Steps 1–5 at 53.125 GBd | UI-relative limits met; Table 4-2 margins realised; CEI-112G-XSR cross-check |

# 8. Summary of Derived TX Jitter Requirements at TP1

**Table 8-1. Requirement summary (identical to ELE-005; derivation pointers)**

| **Quantity** | **Symbol** | **Requirement** | **400G abs.** | **200G abs.** | **Derivation** |
| --- | --- | --- | --- | --- | --- |
| **RMS random jitter** | σ_RJ | ≤ 0.011 UI rms | ≤ 104 fs | ≤ 207 fs | 5.1 — JH4u ceiling (tougher-spec rule); 142 fs first-cut chain must re-partition to ≤ 104 fs |
| **Duty-cycle distortion** | DCD | ≤ 0.025 UI pp | ≤ 235 fs | ≤ 471 fs | 5.2 — duty + rise/fall model |
| **ISI jitter** | ISI | ≤ 0.012 UI pp | ≤ 113 fs | ≤ 226 fs | 5.3 — settling model at the 4.0 ps hard-max edge |
| **Bounded uncorrelated** | BUJ | ≤ 0.036 UI pp | ≤ 339 fs | ≤ 678 fs | 5.4 — slew model, ≤ 2.5 % coupling at 2.0 Vppd / 4.0 ps |
| **Data-dependent** | DDJ | ≤ 0.037 UI pp | ≤ 348 fs | ≤ 696 fs | 5.5 — linear sum |
| **Deterministic total** | DJ_δδ | ≤ 0.123 UI pp FIR-included; ≤ 0.073 no-FIR | ≤ 1.16 / 0.69 ps | ≤ 2.32 / 1.37 ps | 5.5 — linear sum incl. 0.05 UI FIR adder |
| **Total jitter at 1e-12** | TJ | ≤ 0.278 UI pp FIR-included; ≤ 0.228 no-FIR | ≤ 2.61 / 2.14 ps | ≤ 5.23 / 4.29 ps | 5.5 — TJ = DJ_δδ + 2Qσ, Q = 7.034 |
| **Eye-mask half-closure** | X₁ | 0.139 UI FIR-included; 0.114 no-FIR | 1.31 / 1.07 ps | 2.62 / 2.15 ps | 5.5 — TJ / 2 |

**Table 8-2. New derived constraints from the Rev 0.2 gap closure**

| **ID** | **Constraint** | **Value** | **Handed to** | **Origin** |
| --- | --- | --- | --- | --- |
| **JIT-D1** | TP1 electrical overshoot at the hard-max edge under the extracted load | ≤ 2 % (ζ ≥ 0.8) | DES-OCI-106G-TXD-001 Table 5-2 (driver electrical limits) | Table 5-4b — ISI allocation holds only with damped peaking |
| **JIT-D2** | Programmed logic-1 / logic-0 side-tap asymmetry (ELE-010 banks) | │Δw_pre│ + │Δw_post│ ≤ 0.26 | DES-OCI-106G-TXD-001 Table 6-1 (FIR definition) | Table 5-3b — bounds the apparent DCD adder at 0.05 UI |
| **JIT-D3** | Duty-cycle-correction design target (limit ± 0.3 %) | ± 0.2 % | Serializer / clock (CDNS), DES-OCI-106G-TXD-001 Table 4-1 | Table 5-3c — creates ≈ 10 % DCD margin |
| **JIT-D4** | Tap-delay generation shall state whether a phase interpolator is in the TX clock path; if so, its DNL is booked in DJ_δδ, not in σ_RJ | Decision | DES-OCI-106G-TXD-001 Table 6-3 | Table 5-1b |

# 9. Open Items

**Table 9-1. Open items and owner deliverables**

| **#** | **Item** | **Owner** | **Dependency / closure** |
| --- | --- | --- | --- |
| 1 | Clock-chain re-partition (narrowed): the 104 fs allocation is robust to the combination convention (Table 5-8); the gap is 2.7 dB with a PI in the TX path or 1.5 dB without it (Table 5-1b). Resolve JIT-D4 first, then re-partition the PLL / distribution / serializer chain and derive the refclk phase-noise specification — kill-or-confirm (R8) | Analog / SYS-002 / CDNS | Phase-noise budget; first item to close in the TP1 budget (Rev 0.7 §9) |
| 2 | Closed — Table 5-3c: mismatch limit held at 0.35 ps, DCC design target ± 0.2 % (JIT-D3) | — | — |
| 3 | Narrowed — Table 5-3b: the adder is bank-asymmetry apparent DCD, bounded by JIT-D2. Remaining decision: whether it is booked as TP1 timing error (this document, conservative) or credited back at TP2 as the intended correction of the MRM rise/fall asymmetry | Link budget / photonics | MRM electro-optic model; DTX-006 |
| 4 | Converted — Table 5-4b: extracted two-pole fits now confirm ζ ≥ 0.8 (JIT-D1) rather than the model class; C_PN(V) and microbump reflections to be included in the extraction | LM | Simulation sweep |
| 5 | Crosstalk verification against the 2.5 % coupling bound with all four lanes active; identification of supply-coupled spurs | LM / EMC | Simulation sweep; EMC-003/004 |
| 6 | Draft tracking: confirm Table 2-2 values against the adopted 802.3dj draft at each revision and at ratification (D1.3 vs. D3.1 naming and J4u class collapse) | Standards | Rev 0.7 §9 |
| 7 | TP1 eye mask (Table 6-2) issued as a proposal: confirm Y₁ against the MRM electro-optic model and X₂ against extracted edges | Architecture / photonics | ELE-006, DTX-006 |
| 8 | 200G-mode confirmation of the hardware-fixed terms (Table 4-2) and the CEI-112G-XSR cross-check | Verification | CMP-007 |

*End of DES-OCI-106G-JIT-001 Rev 0.3.*

DES-OCI-106G-JIT-001 Rev 0.3 | DRAFT | Page  of