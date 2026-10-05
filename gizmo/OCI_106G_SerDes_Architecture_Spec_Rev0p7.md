400G OCI Line-Side SerDes Chiplet - Architecture and Requirements Specification

**400G OCI Line-Side SerDes Chiplet**

Architecture and Requirements Specification

*4 x 106.25 GBd NRZ DWDM native | 200G OCI v1.0 compatible (4 x 53.125 GBd) | Micro-Ring Modulator CPO | IEEE P802.3dj 106.25 GBd class*

| **Field** | **Value** |
| --- | --- |
| Document ID | ARCH-OCI-106G-001 |
| Revision | 0.7 (Draft for review) |
| Date | September 21, 2026 |
| Status | DRAFT - 171 requirements. 400G OCI mode values are the chiplet design baseline established by this document (Section 1.5) pending publication of the OCI Gen2 specification, which is currently being authored; 200G OCI compatibility mode is normative per the OCI Gen1 Optical PHY Specification v1.0. Internal allocations to be populated. Hub document of the OCI 106G design-document set (Section 1.7): the companion design documents indexed there decompose the derived families of Section 6; where a companion document and this document differ, this document governs. |
| Governing specifications | OCI Gen1 Optical PHY Specification v1.0 (normative for 200G OCI mode; architectural lineage for 400G OCI mode); OCI Gen2 Optical PHY Specification (in authoring — 400G OCI mode values are this document’s baseline pending its publication); IEEE Draft P802.3dj/D1.3 — 106.25 GBd clause chain: Cl.176 (200G/lane PMA), Annex 176C/176D (200GAUI-1 C2C/C2M), Cl.180 (DR PMD family), Annex 174A, Annex 178B; OIF CEI-05.3 (CEI-112G-XSR Cl.24 and CEI-56G-XSR-NRZ, used for baud-rate alignment of electrical specs); OIF CMIS 5.3 (management interface); OIF ELSFP-01.0 (external laser source) |
| Scope | Dual-rate line-side NRZ SerDes chiplet (CPO): SerDes TX, driver, micro-ring modulator; photodetector, TIA, CTLE, slicer, CDR; OCI 2:4 (400G mode) / 1:4 (200G mode) PMA; deskew engine; management; robustness, reliability, EMC, manufacturing-test, and firmware requirements; index of companion design documents |

| **Revision** | **Date** | **Change summary** |
| --- | --- | --- |
| 0.1 | September 14, 2026 | Initial requirements baseline for the 400G OCI operating mode: 159 requirements in 23 families (TXO, RXO, LNK, LOG, BUP, WDM, DFT, MGT, DJI, REG, DTX, DRX, SYS, ELE, CDR, ADP, LOM, SQL, ROB, REL, EMC, MFG, FW). |
| 0.2 | September 14, 2026 | Added the 200G OCI compatibility mode as a product requirement: new CMP family (CMP-001..012, Section 4.4) with Table 4-1 side-by-side mode parameters, and dual-mode provisions in PMA (LOG-001), deskew (BUP-002), clocking (SYS-001), CDR (CDR-001), receive bandwidth (DRX-004), FIR timing (ELE-007), thresholds (LOM-002, SQL-001/003), management (MGT-004), and verification (VER-002/004/005). Table 2-1 restated per operating mode. Total: 171 requirements. |
| 0.3 | September 14, 2026 | FEC architecture clarified: the only host FEC options are RS(544,514) and RS(528,514); no concatenated or inner FEC layer exists between the chiplet and the host decoder. LOG-002 updated to cover both RS variants under the same Annex 174A codeword error ratio allocation (< 1.45E-11, equivalent pre-FEC BER 2.92E-4) and to state that the chiplet has no visibility into the FEC variant. DJI-001 updated with the same context for the 17-bin counter interface. Product description (Section 1.2), architectural decision note (Section 3.3), and B4 (Section 1.5) updated accordingly. Requirement count unchanged: 171. |
| 0.4 | September 14, 2026 | Driver topology corrected to nonlinear switching throughout. Section 3.1 TX signal chain updated; rationale note added (optical linearity obligation falls on the ring transfer function and FIR pre-emphasis; TXO-008 overshoot limit governs acceptable nonlinearity at TP2). DTX-006 rewritten to reflect switching-driver framing: V_high/V_low and slew rate replace “swing and linearity”; driver-ring-photon-lifetime edge interaction made an explicit characterisation obligation. Table 2-1 CEI-56G-XSR-NRZ row updated to note that only edge-rate and jitter limits transfer; linear output-level and linearity limits do not apply. Requirement count unchanged: 171. |
| 0.5 | September 14, 2026 | Added Section 1.6 (Requirement families and ID structure): Table 1-1 lists all 24 FAMILY-NNN prefixes used in the document with their plain-English scope, section reference, requirement count, and normative/derived/productization status. Requirement count unchanged: 171. |
| 0.6 | September 14, 2026 | OCI and OIF attributions corrected throughout. The OCI Gen1 and OCI Gen2 specifications are OCI industry documents, not OIF publications; OIF’s role in this document is confined to CMIS 5.3 (management interface), ELSFP-01.0 (external laser source), and CEI-05.3 (baud-rate-matched electrical reference for jitter/JTOL alignment). All instances of “OIF 200G OCI”, “OIF 400G OCI”, and “OIF OCI specification” replaced with “OCI Gen1” or “OCI Gen2” as appropriate. Section 1.1 Purpose now explicitly states OIF’s two roles. Requirement count unchanged: 171. |
| 0.7 | September 21, 2026 | Established as hub of the design-document set. New Section 1.7 indexes the eight issued companion design documents (JIT, TXD, SQL, CLK, RXF, CDR, ADP, EYM) and five planned ones (REB, CHE, TDC, PHO, logic/system); Table 1-1 and Section 10 gain a “Decomposed in” column; each Section 6 subsection names its decomposing document. Predecessor-document citations removed (Section 2, ELE-005 source, Section 9) and replaced by DES-OCI-106G-JIT-001. Half-rate TX clocking and 8-way interleaved baud/8 RX sampling recorded as chip-level decisions (Sections 3.1-3.3), closing the SYS-001 “full-rate or half-rate” ambiguity. Risk register updated with companion-document status (R2, R4, R8, R9) and new R10 (RX eye budget unowned). Section 9: SQL-001 re-base item, RX eye budget promoted to a decision item, child-issued derived constraints (JIT-D1..D4) and sibling reconciliations registered. No requirement values changed; total remains 171. |

# 1. Introduction

## 1.1 Purpose

This document defines the architecture and captures the complete requirements baseline (171 requirements, REQ IDs below) for a dual-rate line-side SerDes chiplet for Optical Compute Interconnect (OCI). Its native **400G OCI mode** operates four DWDM channels at 106.25 GBd NRZ (425 Gb/s per fiber port) and interoperates with the IEEE P802.3dj Ethernet stack at its native 200 Gb/s-per-lane signaling rate. Its **200G OCI compatibility mode** operates the same four channels at 53.125 GBd NRZ in full compliance with the OCI Gen1 Optical PHY Specification v1.0, so that the chiplet links to deployed OCI Gen1 partner devices. The OCI Gen2 specification — the normative document for the 400G OCI mode — is currently being authored; because it is not yet published, the 400G-mode optical and logical values in Sections 4-5 constitute the chiplet’s design baseline, derived from the OCI Gen1 architecture as stated in Section 1.5, and shall be re-baselined when the Gen2 specification is issued. OIF standards are used in this document in two specific roles: CMIS 5.3 for the management interface, and CEI-05.3 (CEI-112G-XSR, CEI-56G-XSR-NRZ) to provide baud-rate-matched electrical references for adjusting jitter and JTOL specifications between OCI Gen1 and Gen2 baud rates. OIF does not govern the OCI optical PHY. The document serves as the contract between system architecture, circuit design, photonics design, firmware, and verification, and as the traceability anchor for the compliance evidence package. Implementation detail for the derived families of Section 6 is captured in the companion design documents indexed in Section 1.7; this document remains the requirements authority and governs on any conflict.

## 1.2 Product description

The product is a co-packaged optics (CPO) chiplet implementing a bare-bones analog optical PHY. The transmit signal chain is: host die-to-die (D2D) interface, SerDes TX serializer, modulator driver, micro-ring modulator (MRM), Band-Mux, single-mode fiber. The receive chain is: fiber, Band-Mux, ring demultiplexer, photodetector (PD), transimpedance amplifier (TIA), continuous-time linear equalizer (CTLE), slicer, clock and data recovery (CDR), deskew engine, D2D interface. In 400G OCI mode four DWDM channels at 106.25 Gb/s NRZ aggregate 425 Gb/s per fiber port, carrying two 212.5 Gb/s host PMA streams (the two lanes of a 400GBASE-R 16:2 SM-PMA). In 200G OCI mode the same four channels run at 53.125 Gb/s and carry one 212.5 Gb/s host stream through the OCI Gen1 1:4 PMA. Light is supplied by an external laser source (ELS) per OIF ELSFP over polarization-maintaining fiber. There is no line-side FEC, DFE, or DSP: the analog chain alone must meet the raw pre-FEC BER budget of the host FEC — either RS(544,514) or RS(528,514) — in both modes. The 400G-mode design point sizes the hardware (ring Q, photodetector and TIA bandwidth, TP1 jitter budget); the 200G mode is served by programmable bandwidth, timing, and threshold settings on the same hardware.

## 1.3 Scope and exclusions

In scope: line-side optical TX/RX compliance at TP2/TP3 in both operating modes, the TP1 electrical decomposition binding the transmitter design, the 2:4 / 1:4 PMA and deskew engine, CDR and adaptation behavior, ELS interface and control, management (CMIS 5.3, VDM, alarms), test/diagnostic hardware, 802.3dj upstream integration constraints, safety/regulatory framework, robustness/reliability/EMC/manufacturing/firmware requirements, and the derived internal specifications required to meet the above. Out of scope: the host ASIC PCS/FEC implementation, the ELS internal design, board/system mechanical design, and the D2D protocol definition (its error-rate and clocking obligations are captured as requirements on this chiplet).

## 1.4 Requirement conventions

Requirements use ‘shall’ for normative obligations and ‘should’ for recommendations. Each requirement carries: a unique ID; a source; and a verification method: T = Test, A = Analysis, I = Inspection, D = Demonstration. Source notation: **“********400G baseline********”** = a 400G-mode value established by this document per Section 1.5 (pending publication of the OCI Gen2 specification), cited together with the OCI Gen1 v1.0 table that provides its architectural lineage; **“********OCI v1.0 T.x-y********”** = OCI Gen1 Optical PHY Specification v1.0 table/section, normative in 200G OCI mode and, for baud-independent content (wavelength grid, dB ratios, protocol, timers), applicable in both modes; **“********802.3dj X********”** = an IEEE P802.3dj 106.25 GBd clause applied at matching baud in 400G mode; **“********CEI-112G-XSR********”** = OIF CEI-05.3 Clause 24, used as a baud-rate-matched electrical reference for 200G OCI mode jitter and JTOL alignment; **“********Derived: ********<********parent********>************”** = internal decomposition traced to its parent(s). Unless a mode is stated, a requirement applies to 400G OCI mode; requirements that apply in both modes say so, and 200G-mode values are collected in Section 4.4. UI = 9.412 ps in 400G mode (1/106.25 GHz; 802.3dj Table 116-9 uses 9.41176 ps) and 18.824 ps in 200G mode.

## 1.5 Operating modes and basis of the 400G OCI mode values

The chiplet supports two line-side operating modes per fiber port, selected by the host through management (CMP-001). The 200G OCI mode is fully specified by the OCI Gen1 specification v1.0. The 400G OCI mode is governed by the OCI Gen2 specification, which is currently being authored; its values are established by this document from the OCI Gen1 architecture as follows, so that any item overturned when the Gen2 specification is published can be traced to the requirements it affects (Section 9):

- **B1 - Baud and UI.** 106.25 GBd NRZ; UI = 9.412 ps. Limits stated in UI (jitter, FIR delays, CID lengths, eye positions) are stated in UI and apply in both modes; their absolute values differ by the UI ratio. Timing budgets stated in ms (Table 1-3 timers, lock/loselock, persistence windows) are protocol-level and identical in both modes.

- **B2 - Physical budgets fixed by fiber and package.** Insertion loss, chromatic dispersion range, MPI allocation, reflectance, and skew in picoseconds are properties of the channel and package and are identical in both modes. Skew expressed in UI is therefore twice the 200G-mode figure in 400G mode (0-15 UI deskew; < 4 UI routing).

- **B3 - Receiver noise bandwidth and the 3 dB power offset.** Doubling the baud doubles the receiver noise bandwidth; for a TIA-limited NRZ receiver this costs approximately 3 dB of OMA sensitivity (first-order; between 1.5 dB for white-noise-limited and 4.5 dB for capacitance-limited front ends). To preserve the LNK-001 channel budget (2.5 dB IL + 0.2 dB MPI) and every relative margin of the OCI v1.0 link design (LOS vs. mission power, squelch vs. mission OMA, loss-of-modulation discrimination band, SQL-003 rail-polarity margin), all 400G-mode TP2/TP3 signal power levels — OMA, average power, sensitivity, SRS, LOS thresholds, squelched OMA, LOM threshold — sit 3 dB above their 200G-mode counterparts. Device limits that do not scale with baud (PD damage threshold) follow the baud-matched 802.3dj Cl.180 receiver class. This is the most consequential 400G-mode design decision and the first item to confirm against the OCI Gen2 specification (Section 9).

- **B4 - Measurement methodology.** The TDEC reference receiver follows the 0.5 x baud rule: 53.125 GHz fourth-order Bessel-Thomson, no equalizer, in 400G mode (26.5625 GHz in 200G mode); the 802.3dj Cl.180 TDECQ reference equalizer is not adopted for NRZ TDEC. Histogram positions (0.4/0.6 UI), the 2.4E-4 pre-FEC BER threshold (the 802.3dj Annex 174A / OCI v1.0 compliance point, applicable to both RS(544,514) and RS(528,514) hosts via the same codeword-error-ratio allocation), and the pattern-to-parameter mapping (PRBS13 / SSPR / PRBS31) are common to both modes. The host FEC variant is determined by the host PCS, not the chiplet; the chiplet’s analog design point must satisfy the 2.4E-4 threshold regardless of which RS variant is deployed.

- **B5 - Ratios and wavelengths.** Dimensionless dB limits (TDEC 3.4 dB, dTDEC 0.4 dB, ER 3.5-4.5 dB, OMA imbalance 3 dB, SMSR 30 dB, SEC 3.4 dB, overshoot 22%), the DWDM grid and its +/-0.2 nm tolerance, and the RIN density (-138 dB/Hz) are identical in both modes. Where the baud-matched 802.3dj Cl.180 value differs, it is adopted for transition time (8 ps at 106.25 GBd) and noted for RIN (-139 dB/Hz).

- **B6 - Standards cross-references selected for baud match.** Every external citation is checked against Table 2-1. In 400G mode, 802.3dj references route through the 106.25 GBd clause chain; the 113.4375 GBd concatenated-FEC clauses (Cl.177/178/179 PMDs, Cl.182) are not used as normative sources. OIF CEI 56 GBd-class clauses (CEI-112G-XSR, CEI-56G-XSR-NRZ) are baud-matched to 200G mode only and are used there as the electrical cross-check.

- **B7 - Lane geometry.** A 425 Gb/s fiber port carries two 212.5 Gb/s host streams through a 2:4 PMA, with the four-channel deskew group defined per fiber port. The OCI v1.0 four-channel deskew engine, training/release patterns, and relink protocol are used unchanged in both modes; in 200G mode the PMA is the OCI v1.0 1:4.

## 1.6 Requirement families and ID structure

Every requirement in this document has an ID of the form **FAMILY-NNN** (e.g., TXO-005, ELE-002). The family prefix identifies the functional area and the section where the requirement lives. Table 1-1 lists all 24 families in the order they appear.

**Normative families** (Sections 4-5) state what the chiplet must do at its external interfaces or toward external standards. They trace directly to OCI Gen1 v1.0, IEEE P802.3dj, or regulatory documents; OIF CEI is used as a baud-rate reference for electrical specs, not as a governing standard. **Derived families** (Section 6) are internal allocations — decompositions of normative parents into circuit-level obligations that a normative standard does not specify but that must be met for the normative requirement to pass. **Productization families** (Section 7) cover device-level obligations (robustness, reliability, EMC, manufacturing, firmware) that the optical requirements presuppose but do not state.

When a derived family is referenced in prose — for example, “ELE-006 TP1 transition-time limit” in Section 3.1 — it means the requirement identified by that ID in Section 6.4. Cross-references within the document always use the FAMILY-NNN form.

**Table 1-1. Requirement families**

| **Prefix** | **Family name** | **Section** | **Decomposed in** | **Count** | **Status** | **Plain-English scope** |
| --- | --- | --- | --- | --- | --- | --- |
| TXO | Transmitter optical | 4.1 | DES-OCI-106G-TXD-001 (electrical binding via ELE); DES-OCI-106G-JIT-001 | 12 | Normative | Optical output at TP2: OMA, TDEC, ER, transition time, RIN, squelch power, wavelength, skew |
| RXO | Receiver optical | 4.2 | DES-OCI-106G-RXF-001 (003/004/006) | 7 | Normative | Optical input at TP3: sensitivity, SRS, BER floor, damage threshold, LOS, loss-of-lock |
| LNK | Link and ELS | 4.3 | — | 2 | Normative | End-to-end link budget closure; external laser source interface |
| CMP | Compatibility mode | 4.4 | All companion documents (per-mode provisions) | 12 | Normative | 200G OCI backward-compatibility: dual-rate PMA, 53.125 GBd compliance, mode management |
| LOG | Logical / PMA | 5.1 | — (logic document planned) | 4 | Normative | PMA lane mapping (2:4 / 1:4), FEC budget, deskew protocol, bring-up timing |
| BUP | Bring-up / deskew | 5.2 | — (logic document planned) | 5 | Normative | Deskew engine internals: pattern generation, skew compensation, relink state machine |
| WDM | WDM and ELS control | 5.3 | — (photonics document planned) | 5 | Normative | Bidirectional DWDM fiber port, Band-Mux isolation, ELS power-control protocol |
| DFT | Diagnostics and test | 5.4 | DES-OCI-106G-EYM-001 (003/004) | 4 | Normative | PRBS generators/checkers, loopback modes, MPI metric, pre-FEC BER monitors |
| MGT | Management | 5.5 | — | 6 | Normative | CMIS 5.3 interface, VDM observables, alarms, digital-diagnostics accuracy |
| DJI | 802.3dj integration | 5.6 | — | 5 | Normative | Host PMA interface, FEC bin counters, PMD control/status, delay allocation, start-up |
| REG | Regulatory / safety | 5.7 | — | 10 | Normative | Laser safety (IEC 60825), EMC emissions, product lifetime, PICS, Clause 45 mapping |
| DTX | Derived TX | 6.1 | DES-OCI-106G-TXD-001 (006, 010); DES-OCI-106G-SQL-001 (012); DES-OCI-106G-JIT-001 (001); photonics document planned (002..005, 007..009) | 12 | Derived | Transmitter budget decomposition: jitter, ring Q, FSR, heater, driver swing, chirp, crosstalk, squelch circuit |
| DRX | Derived RX | 6.2 | DES-OCI-106G-RXF-001 (001..005); DES-OCI-106G-CDR-001 (006); DES-OCI-106G-EYM-001 (004 confirmation); photonics document planned (007/008) | 10 | Derived | Receiver budget decomposition: PD, TIA noise, AGC range, CTLE closure, CDR JTOL, LOS calibration |
| SYS | Derived system | 6.3 | DES-OCI-106G-CLK-001 (001, 002; 003 interface) | 8 | Derived | Clocking and D2D: frequency synthesis, PLL phase noise, elastic FIFOs, power sequencing, thermal, bring-up sequence |
| ELE | Derived electrical (TP1) | 6.4 | DES-OCI-106G-JIT-001 (002..005 derivation); DES-OCI-106G-TXD-001 (001..010 implementation); DES-OCI-106G-CLK-001 (003, 007/008) | 10 | Derived | Transmitter electrical decomposition at TP1 (buried MRM input): clock jitter, EOJ, J4u, dual-Dirac budget, FIR timing, tap banks |
| CDR | Derived CDR | 6.5 | DES-OCI-106G-CDR-001; DES-OCI-106G-CLK-001 Section 9 (phase interpolator) | 7 | Derived | Clock-and-data-recovery behavior: loop bandwidth, frequency acquisition, CID coast, cycle slips, lock detector, signal-hold |
| ADP | Derived adaptation | 6.6 | DES-OCI-106G-ADP-001 | 5 | Derived | RX adaptation and bring-up: loop nesting order, freeze conditions, dither bound, de-glitch, AC-coupling corner |
| LOM | Derived loss-of-modulation | 6.7 | DES-OCI-106G-SQL-001 Section 6 | 4 | Derived | Loss-of-modulation detector: threshold placement, persistence window, AGC interaction, signal_valid hand-off |
| SQL | Derived squelch | 6.8 | DES-OCI-106G-SQL-001 | 5 | Derived | Squelch circuit: OMA limit during squelch, drop-port servo, rail-polarity margin, entry/exit timing, soak verification |
| ROB | Robustness | 7.1 | — (interfaces in TXD, RXF, CLK) | 7 | Productization | ESD (HBM/CDM), latch-up, power sequencing, supply tolerance, driver fault, over-temperature, wearout |
| REL | Reliability | 7.2 | — | 6 | Productization | Component qualification (HTOL, TC, THB), CPO interconnect reliability, MSL, FIT, SEU, environmental corners |
| EMC | EMC and crosstalk | 7.3 | — (003/004 inputs in DES-OCI-106G-JIT-001 Section 5.4, DES-OCI-106G-CLK-001 Section 3.4) | 4 | Productization | Radiated emissions (CISPR 32), conducted immunity, on-die crosstalk budget, clock spur limits |
| MFG | Manufacturing | 7.4 | — (003 calibration interfaces in ADP, EYM, SQL) | 6 | Productization | Wafer-level structural test, KGD flow, calibration NVM, post-assembly screening, device traceability |
| FW | Firmware | 7.5 | — | 5 | Productization | Firmware authentication, fail-safe update, hardware watchdog, register robustness, maintenance-state gating |

## 1.7 Companion design documents

This document is the hub of the OCI 106G SerDes design-document set. It owns the block diagram, inter-block interfaces, operating modes, shared budgets, and every requirement. The companion design documents below decompose the derived families of Section 6 into implementation: they state *how* a block meets its requirements, map each behaviour back to a FAMILY-NNN ID, and own their block’s internal parameters, verification hooks, and open items. Each companion document names this document as its parent and, where it interacts with another block, names that block’s document as a sibling. Where a companion document and this document differ, this document governs; a companion document that needs a requirement changed raises it here, not locally.

Content that applies to more than one block — a supply rail, a test-point definition, an interface width, a chip-level partition decision — lives in this document only. Companion documents cite it; they do not restate it. No document in the set refers to any predecessor architecture document, by name or indirectly; this set is the architecture.

**Table 1-2. Companion design documents (issued)**

| **Document ID** | **Title** | **Rev / date** | **Decomposes** | **Siblings** | **Confidence (self-reported)** |
| --- | --- | --- | --- | --- | --- |
| DES-OCI-106G-JIT-001 | TX Electrical Jitter Budget at TP1 — Specification and Derivation | 0.3 / 21 Sep 2026 | ELE-002..006, ELE-008; SYS-002; DTX-001; EMC-003/004; CMP-007 | TXD, CDR, CLK | Medium. Owns the sigma_RJ / DCD / ISI / BUJ allocations (TX-side budget document, peer of the RX eye budget) |
| DES-OCI-106G-TXD-001 | TX Pre-Driver and Driver | 0.2 / 21 Sep 2026 | ELE-001..010; DTX-001/002/006/010; TXO-008; CMP-007; SYS-002; ROB-001/005; EMC-003/004 | JIT, SQL, CLK, CDR, ADP | Medium; electrical values are owner deliverables |
| DES-OCI-106G-SQL-001 | TX Squelch and Loss-of-Modulation | 0.2 / 21 Sep 2026 | SQL-001..005; LOM-001..004; DTX-012; TXO-010; BUP-003/004 | TXD, CDR, ADP | Low; partner dependencies unresolved. Requirement-numbering and dual-mode re-base pending (Section 9) |
| DES-OCI-106G-CLK-001 | Clock Generation, Distribution, and Phase Interpolation | 0.2 / 21 Sep 2026 | SYS-001/002 (003 interface); ELE-002..005, 007/008; CDR-001/002/006/007 (actuator); EMC-004; CMP-005; DTX-001 | JIT, TXD, CDR, RXF, EYM | Low-Medium. Implements the half-rate / interleaved-sampling decision of Section 3.3 |
| DES-OCI-106G-RXF-001 | RX Analog Front End — TIA, CTLE, AGC, and Slicer Interface | 0.2 / 21 Sep 2026 | DRX-001..005; RXO-003/004/006; CMP-006/009 | ADP, CDR, SQL, CLK, EYM | Medium for TIA/CTLE/AGC; slicer front end is a placeholder set |
| DES-OCI-106G-CDR-001 | Clock and Data Recovery | 0.2 / 21 Sep 2026 | CDR-001..007; DRX-006; CMP-005; RXO-007; ADP-001/002 (gating); LOM-004; BUP-003 | ADP, SQL, CLK | Medium |
| DES-OCI-106G-ADP-001 | Receive Digital Adaptation Loops | 0.2 / 21 Sep 2026 | ADP-001..005; DRX-003/004/005 (adaptation-facing); CMP-006/009; CDR-005/006; LOM-002/004; DFT-003; MGT-004; MFG-003 | CDR, SQL, RXF | Medium overall; Offset/BLW and CTLE loops Low |
| DES-OCI-106G-EYM-001 | RX Eye Monitor (EyeMonNrz) | 0.2 / 21 Sep 2026 | DFT-003/004; REG-009; DRX-004/005 (confirmation); ADP-003; MFG-003; CMP-005/007/009 | CLK, RXF, CDR, ADP | Medium for measurement architecture; Low-Medium for the monitor slice |

**Table 1-3. Companion design documents (planned)**

| **Document ID** | **Title** | **Trigger** | **Decomposes** |
| --- | --- | --- | --- |
| DES-OCI-106G-REB-001 | RX Eye Budget at the Slicer Input | Risk R10; blocks numeric closure in ADP, CDR, CLK, EYM | CDR-001 jitter peaking; ADP-003 aggregate dither; DRX-004 statistical eye; RX clocking terms (CLK-001 Table 8-3); vertical terms (RXF-001 Table 8-3) |
| DES-OCI-106G-CHE-001 | Channel Estimator | EYM-001 open item 11 | ADP-001 Section 5 (observe-only estimator); DFT-003 |
| DES-OCI-106G-TDC-001 | TX Disparity Checker | EYM-001 open item 11; SQL-001 open item 9 | Section 9 “TX disparity checker algorithm” |
| DES-OCI-106G-PHO-001 | Photonics — MRM, Ring Demux, Heater Servo | Risks R1, R3, R4 | DTX-002..005, 007..009; DRX-007/008; WDM-005 |
| — | Logic / system documents (PMA, deskew, D2D, management, bring-up) | Not yet scoped | LOG, BUP, DJI, SYS-003..008, MGT, FW |

Reading order for a new reader: this document Sections 1-3, then JIT-001 (TX budget), TXD-001 and CLK-001, RXF-001, CDR-001, ADP-001, EYM-001, SQL-001.

# 2. References

- OCI Gen1 Optical PHY Specification, version 1.0 (‘OCI v1.0’). Normative for 200G OCI mode; architectural lineage for 400G OCI mode. Cited as OCI v1.0 T.x-y (table), Sec./F. (section/figure). This is an OCI industry specification; it is not published by OIF.

- OCI Gen2 Optical PHY Specification (in authoring, unpublished at the date of this document). The normative governing document for 400G OCI mode. Values in this document marked “400G baseline” are established from OCI Gen1 pending its publication and shall be re-baselined against it when issued.

- IEEE Draft P802.3dj/D1.3, December 2024 (‘802.3dj’). Draft, subject to change; later drafts rename JRMS03 / J4u03 to JHRMS / JH4u. Only the 106.25 GBd clause chain (Cl.176, Annex 176C/176D, Cl.180, Annex 174A, Annex 178B, Table 116-9 106.25 GBd column) is normative for 400G mode (Table 2-1).

- OIF CEI-05.3 (July 2025) — Common Electrical I/O; Clause 24 CEI-112G-XSR (JTOL mask, TX jitter, CID stress pattern) and Clause 19 CEI-56G-XSR-NRZ, both 36-58 GBd class: baud-matched to 200G OCI mode and used there as the electrical cross-check; test-method content (JTOL pattern construction) used in both modes. The CEI-224G-XSR die-to-OE project is unpublished (Section 9).

- OIF CMIS revision 5.3 — Common Management Interface Specification.

- OIF-ELSFP-01.0 — External Laser Source implementation agreement.

- IEC 60825-1/-2 (laser safety); IEEE 802.3 Annex J.2 (general safety).

- ANSI/ESDA/JEDEC JS-001 (HBM) and JS-002 (CDM); JEDEC JESD78 (latch-up); JEDEC JESD47 and JESD22 series (component qualification); IPC/JEDEC J-STD-020 (moisture sensitivity).

- Telcordia GR-468-CORE (optoelectronic device reliability; adapted for CPO interconnect qualification).

- CISPR 32 / FCC Part 15 (emissions); IEC 61000-4-3 / -4-6 (immunity).

- DES-OCI-106G-xxx-001 companion design documents — indexed in Section 1.7 (Tables 1-2 and 1-3) and cited in this document by Document ID and section.

**Table 2-1. Baud-rate alignment of external cross-references by operating mode**

| **Reference** | **Signaling** | **Baud** | **400G OCI mode (106.25 GBd)** | **200G OCI mode (53.125 GBd)** |
| --- | --- | --- | --- | --- |
| 802.3dj Cl.176 (200G/lane SM-PMA), Annex 174A (FEC error budget) | PAM4 host lanes, 212.5 Gb/s | 106.25 GBd | Native host interface; 2:4 PMA — host lane and optical channel share a baud | Native host interface; 1:4 PMA per OCI v1.0 |
| 802.3dj Annex 176C / 176D (200GAUI-1 C2C / C2M): TX output jitter per 179.9.4.6 (JRMS03 / EOJ03 / J4u03, 4 MHz CRU); RX JTOL Table 176D-10 (= Table 179-12) | PAM4 | 106.25 +/- 50 ppm GBd | Native electrical jitter and JTOL references; Cl.179 definitions imported at 106.25 GBd by 176C.4.3.6 / 176C.4.4.5 | Not baud-matched; the same UI-relative limits are met in UI (CMP-005/007) and cross-checked against CEI-112G-XSR |
| 802.3dj Cl.180 (200GBASE-DR1 / 400GBASE-DR2 / 800GBASE-DR4 / 1.6TBASE-DR8) | PAM4 optical | 106.25 +/- 50 ppm GBd | Native optical lineage: 8 ps transition, 22%, 3.5 dB ER, 3.4 dB TDECQ/SECQ, RIN21.4OMA -139 dB/Hz, RX damage 5 dBm, Pavg RX -6.3 to +4 dBm | Not applicable; OCI v1.0 Tables 2-2 / 2-3 govern |
| 802.3dj Cl.177 (inner FEC), Cl.178 (KR1), Cl.179 (CR1/CR2/…), Cl.182 (DR-2 family) | PAM4, concatenated FEC | 113.4375 GBd | Not baud-matched (6.7% high, inner-FEC class); cited only through the Annex 176C/176D definitions | Not applicable |
| 802.3dj Table 116-8 / 116-9 (skew, skew variation) | — | ns; UI columns per baud | 106.25 GBd column (1 UI = 9.41176 ps): SP2 skew variation 0.4 ns = 43 UI; SP3 0.6 ns = 64 UI | 53.125 GBd column (1 UI = 18.82353 ps): SP2 = 21 UI; SP3 = 32 UI |
| 802.3dj Annex 178B (start-up without ILT; RTS via squelch/unsquelch) | Protocol | — | Native (baud-independent) | Native (baud-independent) |
| OIF CEI-05.3 Cl.24 CEI-112G-XSR (JTOL mask, CID pattern, f_CRU = f_b/13280; TX JRMS <= 0.0224 UI, EOJ <= 0.025 UI, J8u <= 0.1546 UI) | PAM4 | 36-58 GBd | Not baud-matched (f_b/13280 would imply 8 MHz); JTOL test-pattern construction (72-UI CID runs between PRBS31 segments) used as method only | Baud-matched: JTOL corner ~4.0 MHz at 53.125 GBd; TX-jitter and JTOL cross-check for CMP-005 / CMP-007 |
| OIF CEI-05.3 Cl.19 CEI-56G-XSR-NRZ | NRZ | 39.8-58 GBd | 4.0 ps hard-max switching edge kept as the ELE-006 TP1 transition-time limit (0.42 UI); driver topology is nonlinear switching (not linear) so the CEI-56G-XSR-NRZ TX linearity and output-level limits do not apply — only the edge-rate and jitter limits transfer | Baud-matched NRZ TP1 edge-rate cross-check for 200G mode |
| OIF CEI-224G-XSR (project, unpublished) | PAM4 | ~112.5 GBd class | Watch item: becomes the baud-matched OIF die-to-OE reference when published (Section 9) | — |
| OCI Gen1 v1.0 Sec.1.1, Table 1-3 (deskew protocol, timers) | Protocol | ms | Used unchanged (B1, B7) | Native |

# 3. System Architecture Overview

## 3.1 Signal chain and compliance points

TX path: D2D RX (two 212.5 Gb/s host streams per port in 400G mode; one in 200G mode) -> 2:4 or 1:4 PMA and lane remap (host-stream-to-channel mapping, wavelength indexing) -> 4x SerDes TX (106.25 or 53.125 Gb/s, clock derived from host domain) -> 4x nonlinear switching drivers -> 4x MRM on a shared bus waveguide (DWDM Group A or B) -> Band-Mux -> fiber. Nonlinear switching drivers are used for power efficiency; the optical linearity obligation falls on the ring-modulator transfer function and the FIR pre-emphasis (ELE-007/010, DTX-006), and the 22% overshoot limit (TXO-008) defines the acceptable nonlinearity at TP2. Compliance point TP2 is the optical output at the defined fiber reference plane. TP1 — the electrical input to the MRM — is buried in-package and unprobeable; it binds the Section 6.4 transmitter electrical decomposition and is verified by simulation and on-die instrumentation.

RX path: fiber -> Band-Mux -> 4x ring demux filters -> 4x PD -> 4x TIA + AGC -> 4x CTLE (mode-dependent bandwidth) -> 4x slicer + CDR (8-way interleaved sample/hold and comparator slices at baud/8; no receiver circuit is clocked at the line rate — DES-OCI-106G-CLK-001 Section 2.5, DES-OCI-106G-RXF-001 Section 8) -> deskew engine (integer-UI realignment across the four channels of the port: 0-15 UI in 400G mode, 0-7 UI in 200G mode) -> 4:2 gearbox to two 212.5 Gb/s host streams (4:1 to one stream in 200G mode) -> D2D TX. Compliance point TP3 is the optical input at the fiber reference plane.

## 3.2 Functional blocks

- Dual-rate PMA: 2:4 bit mux/demux between two 212.5 Gb/s host streams and four 106.25 Gb/s NRZ channels, each host stream on a pair of adjacent wavelengths with LSB on the shorter wavelength (LOG-001); OCI v1.0 1:4 mode with one host stream and LSB on the shortest wavelength (CMP-003).

- Deskew engine: per-channel 160-bit pattern generators/correlators (OCI v1.0 Tables 1-1/1-2), training/release/mission state machine per OCI v1.0 Section 1.1 over the four channels of a fiber port, permanently armed relink logic, operating at either baud (BUP-001..005, LOG-003/004, CMP-004).

- Thermal control: per-ring heater DACs and lock servos (TX rings and RX demux filters), dither-based lock with amplitude budgeted inside TDEC; wide-range acquisition mode for ELS start-up (DTX-004/005, DRX-008, WDM-005); squelch-bias interaction with the heater servo per DES-OCI-106G-SQL-001 Section 4. Ring Q is sized for 106.25 GBd (DTX-002) and must also deliver the 200G-mode ER/TDEC (CMP-008).

- ELS interface: ELSFP control channel for per-wavelength power request and attenuation, with mode-dependent power setpoints; PM fiber input coupling (WDM-003/004, LNK-002).

- Clocking: host-derived line clock (+/-50 ppm), dual-rate TX PLL and serializer, per-channel dual-rate RX CDR, elastic FIFOs at the domain crossing (SYS-001..003, TXO-001, CMP-005); half-rate clocking architecture — 53.125 GHz LC-PLL, final 2:1 mux, fixed VCO with divide-by-2 in 200G mode — is the recorded decision (Section 3.3; DES-OCI-106G-CLK-001 Sections 2.3 and 2.5); PLL-instance count and reference frequency remain open (CLK-001 open items 2 and 4).

- Management subsystem: embedded core presenting CMIS 5.3 with both operating modes advertised as distinct applications; VDM observables, alarms/warnings at channel / host-stream / die granularity; flight data recorder (MGT-001..006, CMP-010); firmware robustness per Section 7.5.

- DFT: per-channel PRBS13/SSPR/PRBS31 generators and checkers at either line rate, electrical and optical loopbacks, MPI metric, pre-FEC BER monitors per host stream (DFT-001..004); per-channel in-situ RX eye monitor at the slicer input as the margin / BER observable (DES-OCI-106G-EYM-001); production-test and KGD hooks per Section 7.4.

- Safety/supervision: fault detection with ELS shutdown authority, safe power sequencing, dual TX-off semantics — transmit disable vs. heater-safe squelch (REG-002/008, DJI-003, SYS-005); electrical-robustness envelope per Section 7.1.

## 3.3 Key architectural decisions and their driving requirements

- Dual-rate on a single architecture: backward compatibility with deployed 200G OCI v1.0 partners is a product requirement (CMP family), so the analog front end, clocking, PMA, and deskew engine are dual-rate. The 400G-mode design point sizes the hardware — ring Q, PD/TIA bandwidth, TP1 jitter budget — and the 200G mode is served by programmable receive bandwidth (CMP-006), baud-tracking FIR timing (CMP-007), and per-mode thresholds and calibration (CMP-009) rather than duplicated hardware.

- CTLE-only receive equalization (no DFE/FFE/DSP): viable only if the statistical-eye analysis of DRX-004 closes the 3.4 dB SEC stressed condition at -3.2 dBm OMA with aggressors, with a receive-chain bandwidth of 64-80 GHz. PD capacitance and TIA noise at that bandwidth make this the gating receiver analysis.

- Ring Q selection: photon-lifetime bandwidth for 106.25 GBd requires Q of roughly 2500-4000 (DTX-002), which widens the linewidth and reduces detuning-per-volt modulation efficiency. ER (TXO-006), OMA (TXO-005), transition time (TXO-008), inter-ring crosstalk (DTX-003), and the 200G-mode ER/TDEC (CMP-008) are all resolved through this single trade; it is the gating photonics decision (risk R1).

- 3 dB optical power offset between modes (B3): preserves every OCI v1.0 relative margin in 400G mode but raises per-channel launch power to +3 dBm maximum and group power to 9 dBm, so ELS power demand, ring self-heating, laser-safety margin, and PD-damage margin are re-verified at 400G-mode levels. Holding 200G-mode power levels in 400G mode is not adopted because the LNK-001 channel (2.5 dB IL, dominated by connectors) cannot be shortened to compensate.

- 2:4 PMA with a port-level deskew group (B7): the four channels of a fiber port are deskewed together, so the two host streams sharing the port are realigned to a common reference. Relink (squelch) is per fiber port and affects both host streams simultaneously, which is inherent since they share the fiber. In 200G mode the port carries one host stream (CMP-003).

- Native-baud 802.3dj referencing (B6): the 802.3dj 200G/lane electrical and optical clauses at 106.25 GBd bind at matching baud in 400G mode, so the ELE, CDR, and DRX-006 families carry no UI-relative-analog caveat; the 113.4375 GBd concatenated-FEC clauses are excluded. In 200G mode the baud-matched electrical cross-check is OIF CEI-112G-XSR.

- No line-side FEC: LOG-002 places the entire 2.4E-4 pre-FEC budget on the raw analog link in both modes. The host FEC is an RS-only architecture — either RS(544,514) or RS(528,514) — with no inner or concatenated FEC layer between the chiplet and the host decoder. DJI-002 makes burst statistics (FEC bin histograms), not mean BER, the acceptance criterion. The internal design point is raw BER < 1e-12 and drives the ELE-005 dual-Dirac budget and the CDR-004 mission cycle-slip prohibition.

- Half-rate TX clocking and interleaved RX sampling: no circuit in either direction is clocked at 106.25 GHz. TX: a half-rate 53.125 GHz LC-PLL drives a final 2:1 mux, so clock duty-cycle error appears as even/odd (DCD) jitter and a duty-cycle-correction loop with a 0.006 UI allocation is required (ELE-003; DES-OCI-106G-JIT-001 Table 5-3c). RX: 8-way interleaved sample/hold and comparator slices at baud/8 with a phase interpolator that rotates all eight phases together, so per-phase skew calibration and seamless interpolator wrap (CDR-004) become architecture obligations. This is a chip-level partition decision with consequences in the ELE, CDR, and DRX families; rationale and alternatives are recorded in DES-OCI-106G-CLK-001 Table 2-4.

## 3.4 Risk register (top items)

- R0 - Specification risk: the OCI Gen2 specification is still being authored; the 3 dB power offset (B3), PMA lane geometry (B7), and transition-time/RIN choices (B5) are the values most likely to be overturned. Mitigate by keeping Section 9 current and parameterizing firmware limits (LOM-002 threshold, LOS, squelch OMA, timers) rather than hard-coding them; the per-mode parameter structure of CMP-009 provides the mechanism.

- R1 - Ring bandwidth vs. modulation efficiency at 106.25 GBd (TXO-005/006/008, DTX-002/003/006, CMP-008): lower Q reduces detuning-per-swing efficiency; the 3.5-4.5 dB ER window at bounded drive swing may not close in either mode. Mitigate with early MRM co-simulation across Q = 2500-4000, efficiency (pm/V) and swing (Vppd), and an ER/OMA/transition-time feasibility gate before photonics tape-out.

- R2 - CTLE-only SRS closure (RXO-002/DRX-001/002/004): PD capacitance and TIA input-referred noise over 64-80 GHz; mitigate with statistical-eye signoff before RTL freeze; fallback is an added RX peaking stage or reduced SRS margin claim. Status (DES-OCI-106G-RXF-001): the partner TIA specification is 50-60 GHz against the 64-80 GHz DRX-004 window, and its overload, DC-cancellation, and input-noise limits also fall short of the derived targets (RXF-001 Section 12 items 1, 4, 5); closure or link-budget re-derivation is the gating RX item.

- R3 - Pattern-dependent ring wander vs. dTDEC 0.4 dB (TXO-004/DTX-005) at 400G-mode absorbed optical power: the self-heating disturbance amplitude is 3 dB higher than in 200G mode while the dTDEC allocation is unchanged; mitigate with the behavioral thermal model and driver-side compensation study.

- R4 - Squelch/heater interaction (TXO-010/DTX-012/DRX-008): mitigate with squelch-mode testchip and partner-squelch soak in both modes (DES-OCI-106G-SQL-001, issued; requirement-numbering and dual-mode re-base pending, Section 9).

- R5 - Burst errors from lock transients vs. FEC codeword histograms (DJI-002/VER-007): mitigate with bin-counter instrumentation on first silicon and the CDR-004/ADP-004 burst-avoidance requirements.

- R6 - ELS power headroom and coupling-loss growth (LNK-001/002, WDM-004, DTX-009): 400G-mode launch power plus coupling loss must fit the ELSFP per-wavelength power envelope; mitigate with the lot-tracked loss table and an early ELSFP power-budget check.

- R7 - CPO microbump / fiber-attach reliability under thermal cycling and heater power: mitigate with the GR-468-derived qualification of REL-002 and ROB-005 fault detection.

- R8 - TP1 electrical closure at 9.412 ps UI (ELE-002..008): 104 fs rms clock-jitter budget, 4.0 ps hard-max edge, 0.24 ps inter-tap matching; mitigate with clock-chain phase-noise budgeting first (largest margin lever) and driver test-vehicle measurement. Status (DES-OCI-106G-JIT-001, DES-OCI-106G-CLK-001): first-cut clock-chain RSS 123 fs, 1.5 dB over the 104 fs allocation with no phase interpolator in the TX path (JIT-D4); a 72 / 45 / 30 fs re-partition (90 fs) is proposed as closure and awaits CDNS confirmation (CLK-001 open item 1).

- R9 - Dual-rate analog front end (CMP-005/006/007, MFG-003/004): switchable receive bandwidth (64-80 vs. 32-40 GHz), baud-tracking FIR branch delays, and a doubled per-mode calibration set that lengthens production test; mitigate with mode-switchable blocks on the testchip, a shared calibration structure with per-mode deltas, and a 200G-mode sensitivity check on first silicon. Dual-rate clocking method and 200G-mode word width: DES-OCI-106G-CLK-001 Section 10; 200G-mode analog parameter set: DES-OCI-106G-RXF-001 open item 8.

- R10 - RX eye budget unowned: four companion documents (ADP, CDR, CLK, EYM) defer numeric closure to a receiver eye budget that exists neither as a document nor as a Section 6 allocation. Until it is issued, the CDR-001 jitter-peaking limit, the ADP-003 aggregate-dither allocation, and the RX sampling-clock skew / RJ / interpolator terms cannot be signed off. Mitigate by issuing DES-OCI-106G-REB-001 (Section 1.7, Table 1-3) as the receive-side peer of DES-OCI-106G-JIT-001.

# 4. Optical and Link Requirements (Normative)

## 4.1 Transmitter optical requirements (TP2), 400G OCI mode

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| TXO-001 | Each optical channel shall operate at 106.25 GBd NRZ in 400G OCI mode (53.125 GBd in 200G OCI mode, CMP-001). The transmit signaling rate shall be held within +/-50 ppm in both modes (in-package PMA/PCS tightened tolerance; equal to the 802.3dj 106.25 GBd PMD tolerance). | 400G baseline; OCI v1.0 T.2-1; 802.3dj Cl.176, T.180-7 | T |
| TXO-002 | Each transmit wavelength shall be held within +/-0.2 nm of its DWDM grid value in Group A or Group B (Group A: 1308.00 / 1310.28 / 1312.58 / 1314.88 nm; Group B: 1327.69 / 1330.05 / 1332.41 / 1334.78 nm). The micro-ring resonance servo shall maintain grid registration across the full operating temperature range and traffic conditions. The grid is identical in both operating modes. | OCI v1.0 T.2-2 (both modes) | T |
| TXO-003 | Transmitter and dispersion eye closure (TDEC) shall be <= 3.4 dB per channel, measured with the SSPR pattern using a 53.125 GHz (0.5 x baud) fourth-order Bessel-Thomson reference receiver, no equalizer, vertical histograms at 0.4/0.6 UI, and a pre-FEC BER threshold of 2.4E-4 (200G mode: 26.5625 GHz reference receiver, CMP-002). | 400G baseline; OCI v1.0 T.2-2 n.2; 802.3dj Cl.180 method lineage | T |
| TXO-004 | Pattern dependence of eye closure shall satisfy │TDEC(SSPR) - TDEC(PRBS13)│ <= 0.4 dB per channel in both modes, bounding data-dependent baseline wander from ring self-heating and carrier effects. | OCI v1.0 T.2-2 n.3 (both modes) | T |
| TXO-005 | Launched OMA per channel shall be >= max(-2.5, -3.9 + TDEC) dBm and <= +2 dBm. Difference in OMA between any two DWDM channels shall be <= 3 dB (both modes). | 400G baseline; OCI v1.0 T.2-2 | T |
| TXO-006 | Extinction ratio per channel shall be within 3.5 dB (min) to 4.5 dB (max), measured with PRBS13, in both modes. Both limits are normative; ring drive shall be bounded to respect the ER ceiling. | OCI v1.0 T.2-2 (both modes); 802.3dj T.180-7 ER min | T |
| TXO-007 | Average launch power per channel shall be within -5.5 to +3 dBm; total average launch power per CWDM group shall be <= 9 dBm. | 400G baseline; OCI v1.0 T.2-2 | T |
| TXO-008 | Transmitter 20-80% transition time shall be <= 8 ps (SSPR); transmitter overshoot/undershoot shall be <= 22% (both modes). The 8 ps limit is the 802.3dj Cl.180 value at 106.25 GBd; same-UI-fraction scaling of the OCI v1.0 200G-mode limit would give 8.5 ps. | 400G baseline; 802.3dj T.180-7; OCI v1.0 T.2-2 | T |
| TXO-009 | RIN21.4OMA shall be <= -138 dB/Hz per channel with 21.4 dB optical return loss applied (PRBS13), in both modes. Note: 802.3dj Cl.180 specifies -139 dB/Hz at the same baud and ORL condition; the OCI v1.0 density is retained (B5) and the 400G-mode receiver noise budget shall carry the additional integrated RIN of its wider bandwidth. | OCI v1.0 T.2-2 (both modes) | T |
| TXO-010 | When squelched, launched OMA per channel shall be <= -12 dBm (200G mode: <= -15 dBm) while average optical power remains constant, so heater lock is maintained in TX and far-end RX micro-rings. Squelch shall suppress modulation only, never average power. | 400G baseline; OCI v1.0 T.2-2 n.4 | T |
| TXO-011 | Transmitter data-path reflectance shall be <= -19 dB (looking into TX from data-path egress, TX band); optical-engine laser-input reflectance shall be <= -26 dB at the ELS connection (both modes). | OCI v1.0 T.2-2 (both modes) | T |
| TXO-012 | Channel-to-channel skew at the TX optical output arising from electrical and optical routing shall be < 4 UI (37.6 ps) in 400G mode and < 2 UI in 200G mode — the same absolute budget. | 400G baseline; OCI v1.0 Sec.1.1 n.6 (B2) | A/T |

## 4.2 Receiver optical requirements (TP3), 400G OCI mode

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| RXO-001 | Receiver sensitivity (OMA) per channel shall be <= max(-5.2, -6.6 + TDEC) dBm at BER 2.4E-4, PRBS31. | 400G baseline; OCI v1.0 T.2-3 | T |
| RXO-002 | Stressed receiver sensitivity (OMA) shall be <= -3.2 dBm with a 3.4 dB stressed-eye-closure (SEC) conformance signal on the channel under test and all aggressor channels active at -0.2 dBm OMA, at BER 2.4E-4 (PRBS31). The CTLE-only analog receive chain shall close this condition without decision feedback equalization. | 400G baseline; OCI v1.0 T.2-3, T.2-4 | T |
| RXO-003 | BER floor: with a reference transmitter of TDEC >= 2 dB, receiver BER shall remain <= 1E-6 over the input OMA range (-5.2 + TDEC) dBm to +2 dBm, with no TIA/AGC overload behavior across the range. | 400G baseline; OCI v1.0 T.2-3 n.3 | T |
| RXO-004 | The receiver shall survive continuous input at the 5 dBm damage threshold (802.3dj Cl.180 106.25 GBd receiver class; 2 dB above the TXO-007 maximum, see Section 9; this also covers the OCI v1.0 200G-mode threshold of 4.5 dBm), operate over Pavg -8 to +3 dBm per channel, and tolerate 3 dB OMA difference between any two channels (both modes). | 400G baseline; 802.3dj T.180-8; OCI v1.0 T.2-3 | T |
| RXO-005 | Receiver reflectance shall be <= -19 dB looking into the RX port (both modes). | OCI v1.0 T.2-3 (both modes) | T |
| RXO-006 | Loss-of-signal (LOS) shall assert at -16 / -13.5 / -11 dBm AOP (min/typ/max) per channel with 1-3 dB hysteresis (200G mode: -19 / -16.5 / -14 dBm, CMP-009); LOS de-assert derives from assert + hysteresis. An average-power monitor independent of the data path shall implement this function. | 400G baseline; OCI v1.0 T.2-3 | T |
| RXO-007 | Loss-of-lock detection delay shall be <= 50 ms from modulation on/off change to the change in the loss-of-lock flag in both modes; the CDR shall provide a robust lock detector feeding the link state machine. | OCI v1.0 T.2-3 n.5 (both modes) | T |

## 4.3 Channel and external laser source

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| LNK-001 | The link shall close over the reference channel in both modes: 500 m SMF-28, 2.5 dB total insertion loss, chromatic dispersion -0.9 to +1.7 ps/nm, with a 0.2 dB MPI penalty allocation. 400G-mode budget at maximum TDEC: TX OMA(min) -0.5 dBm - 2.5 dB - 0.2 dB = -3.2 dBm = stressed RX sensitivity; at TDEC <= 1.4 dB: -2.5 - 2.7 = -5.2 dBm = sensitivity. (200G mode closes identically at -6.2 / -8.2 dBm per OCI v1.0.) | 400G baseline; OCI v1.0 T.2-5 | A/T |
| LNK-002 | The chiplet shall source light from an OIF ELSFP-compliant external laser source via polarization-maintaining fiber; the coupling-loss and polarization budget shall be closed against the ELS output-power and PER envelope at the 400G-mode launch power of TXO-007 (risk R6) and at the 200G-mode power of CMP-002. | OCI v1.0 Sec.2.5 | A/I |

## 4.4 200G OCI compatibility mode (backward compatibility)

The chiplet shall interoperate with 200G OCI Gen1 partner devices built to OCI Gen1 Optical PHY Specification v1.0. In this mode the four channels of a fiber port run at 53.125 GBd NRZ and every OCI v1.0 normative requirement applies at TP2/TP3 and in the logical layer. Table 4-1 places the two modes side by side; the CMP requirements below bind the dual-rate provisions that the rest of this document presupposes.

**Table 4-1. Operating-mode parameters (400G OCI mode per Sections 4.1-4.2; 200G OCI mode per OCI v1.0 Tables 2-2 to 2-4)**

| **Parameter** | **400G OCI mode** | **200G OCI mode (OCI v1.0)** |
| --- | --- | --- |
| Signaling rate / UI | 106.25 GBd NRZ / 9.412 ps | 53.125 GBd NRZ / 18.824 ps |
| Port capacity / host streams / PMA | 425 Gb/s / two 212.5 Gb/s / 2:4 | 212.5 Gb/s / one 212.5 Gb/s / 1:4 |
| TDEC reference receiver | 53.125 GHz BT4, no equalizer | 26.5625 GHz BT4, no equalizer |
| TDEC / dTDEC / ER / overshoot / OMA imbalance | <= 3.4 dB / <= 0.4 dB / 3.5-4.5 dB / <= 22% / <= 3 dB | identical |
| TX OMA per channel | >= max(-2.5, -3.9 + TDEC), <= +2 dBm | >= max(-5.5, -6.9 + TDEC), <= -1 dBm |
| TX Pavg per channel / per CWDM group | -5.5 to +3 dBm / <= 9 dBm | -8.5 to 0 dBm / <= 6 dBm |
| Transition time 20-80% (SSPR) | <= 8 ps | <= 17 ps |
| RIN21.4OMA / reflectances / SMSR / grid | <= -138 dB/Hz / -19, -26 dB / >= 30 dB / Group A-B | identical |
| Squelched OMA (Pavg held constant) | <= -12 dBm | <= -15 dBm |
| RX sensitivity (OMA) | <= max(-5.2, -6.6 + TDEC) dBm | <= max(-8.2, -9.6 + TDEC) dBm |
| SRS / aggressor OMA (SEC 3.4 dB) | <= -3.2 dBm / -0.2 dBm | <= -6.2 dBm / -3.2 dBm |
| BER floor <= 1E-6 over OMA range | (-5.2 + TDEC) to +2 dBm | (-8.2 + TDEC) to -1 dBm |
| RX Pavg / damage threshold | -8 to +3 dBm / 5 dBm | -11 to 0 dBm / 4.5 dBm (hardware meets 5 dBm) |
| LOS assert min/typ/max (AOP) / hysteresis | -16 / -13.5 / -11 dBm / 1-3 dB | -19 / -16.5 / -14 dBm / 1-3 dB |
| Loss-of-modulation threshold (nominal) | -9 to -8 dBm OMA-equivalent | -12 to -11 dBm OMA-equivalent |
| Deskew range / routing skew per end | 0-15 UI / < 4 UI (37.6 ps) | 0-7 UI / < 2 UI (37.6 ps) |
| Receive-chain bandwidth (0.6-0.75 x baud) | 64-80 GHz | 32-40 GHz |
| Electrical jitter / JTOL cross-reference | 802.3dj Annex 176C/176D (native baud) | OIF CEI-112G-XSR Cl.24 (baud-matched); limits in UI per Section 6.4 |
| Channel (IL, CD, MPI), timers (Table 1-3), patterns (Tables 1-1/1-2), t_LOL | identical | identical |

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| CMP-001 | The chiplet shall support two line-side operating modes per fiber port, selectable through the management interface (MGT-001, CMP-010) and fixed for the duration of a link session: 400G OCI mode — four channels at 106.25 GBd NRZ (425 Gb/s per port, two 212.5 Gb/s host streams), governed by Sections 4.1-4.3; and 200G OCI mode — four channels at 53.125 GBd NRZ (212.5 Gb/s per port, one host stream), compliant with OCI Gen1 Optical PHY Specification v1.0 for interoperation with OCI Gen1 Type A and Type B partner devices. Mode shall be selectable independently per port. | OCI v1.0 (200G mode); 400G baseline | T/D |
| CMP-002 | In 200G OCI mode the transmitter and receiver shall comply with OCI v1.0 Tables 2-2, 2-3, and 2-4 at TP2/TP3 (values in Table 4-1): TDEC <= 3.4 dB with a 26.5625 GHz BT4 reference receiver; OMA >= max(-5.5, -6.9 + TDEC) and <= -1 dBm; Pavg -8.5 to 0 dBm per channel and <= 6 dBm per group; transition time <= 17 ps; squelched OMA <= -15 dBm; sensitivity <= max(-8.2, -9.6 + TDEC) dBm; SRS <= -6.2 dBm with 3.4 dB SEC and aggressors at -3.2 dBm; BER floor over (-8.2 + TDEC) to -1 dBm; LOS assert -19 / -16.5 / -14 dBm AOP; Pavg RX -11 to 0 dBm. Baud-independent parameters (grid, ER, dTDEC, RIN, reflectance, SMSR, OMA imbalance, hysteresis, t_LOL) are identical in both modes. | OCI v1.0 T.2-2 / 2-3 / 2-4 | T |
| CMP-003 | In 200G OCI mode the PMA shall operate as the OCI v1.0 1:4 PMA: one 212.5 Gb/s host stream (200GBASE-R 8:1 SM-PMA lane) demultiplexed to four 53.125 Gb/s NRZ channels with the LSB on the shortest wavelength, and multiplexed in reverse (OCI v1.0 Sec.1.2). The port’s second host-stream interface shall be idle in this mode; a host may alternatively drive a 400GBASE-R 16:2 SM-PMA across two fiber ports in the OCI v1.0 2:8 geometry. | OCI v1.0 Sec.1, 1.2 | T |
| CMP-004 | The deskew engine shall operate in both modes with the OCI v1.0 160-bit training and release patterns (Tables 1-1/1-2), the Table 1-3 timer set, correlation/voting detection at BER up to 1E-4, and a compensation range of 0-7 UI at 53.125 GBd in 200G mode (0-15 UI at 106.25 GBd in 400G mode, BUP-002) — the same ~130 ps absolute skew envelope. | OCI v1.0 Sec.1.1, T.1-3 | T |
| CMP-005 | The TX PLL, serializer, driver FIR timing, and RX CDR shall operate at both 106.25 and 53.125 GBd with +/-50 ppm tolerance. In 200G mode the CDR shall meet a jitter-tolerance mask of the same shape as DRX-006 (5 UI at 40 kHz rolling to 0.05 UI at >= 4 MHz) at 53.125 GBd, consistent with the baud-matched OIF CEI-112G-XSR mask (CEI-05.3 Cl.24, f_CRU = f_b/13280 ~ 4.0 MHz at 53.125 GBd), with the CDR-001 bandwidth window and the CDR-002..007 behaviors applying in both modes. | CEI-112G-XSR (200G mode); Derived: SYS-001, CDR-001..007 | A/T |
| CMP-006 | The receive chain shall provide a 200G-mode bandwidth configuration (overall TIA/CTLE bandwidth ~0.6-0.75 x 53.125 GBd = 32-40 GHz) so that receiver noise is integrated over the 200G-mode bandwidth and the OCI v1.0 sensitivity (-8.2 dBm), stressed sensitivity (-6.2 dBm), and BER-floor requirements are met. Operating the 400G-mode front end at full bandwidth in 200G mode is acceptable only if those limits are demonstrated with margin. | Derived: DRX-002/004; OCI v1.0 T.2-3 | A/T |
| CMP-007 | FIR branch delays shall track the operating baud (0/1/2 UI in both modes: 0 / 9.41 / 18.82 ps in 400G mode, 0 / 18.82 / 37.65 ps in 200G mode), FIR coefficient banks shall be stored per mode, and the TP1 jitter limits of Section 6.4 shall be met in UI in both modes (200G-mode absolutes: JRMS 433 fs, EOJ 471 fs, J4u 2.22 ps), consistent with the baud-matched OIF CEI-112G-XSR transmitter limits (JRMS <= 0.0224 UI, EOJ <= 0.025 UI) in 200G mode. | Derived: ELE-002..007; CEI-112G-XSR (200G mode) | A/T |
| CMP-008 | The MRM, driver swing, and heater servo shall deliver the OCI v1.0 ER window (3.5-4.5 dB), OMA, TDEC, and dTDEC at 53.125 GBd with the hardware ring Q selected for 400G mode (DTX-002), and the ELS per-wavelength power requests (WDM-004) shall place launched Pavg within -8.5 to 0 dBm (<= 6 dBm per group) in 200G mode. | Derived: DTX-002/006; OCI v1.0 T.2-2 | A/T |
| CMP-009 | Squelched-OMA limits, LOS thresholds, the loss-of-modulation detection threshold (LOM-002: nominal -12 to -11 dBm OMA-equivalent in 200G mode; -9 to -8 dBm in 400G mode), squelch drop-port setpoints (SQL-002), rail-polarity margins (SQL-003), AGC/gain ranges, and receive-bandwidth settings shall be stored and applied per mode; a mode change shall reload the complete parameter set before the port is enabled. | Derived: RXO-006; TXO-010; LOM-002; SQL-002/003 | T |
| CMP-010 | The management interface shall advertise the two operating modes as distinct CMIS applications (the 200G application per OCI v1.0 Sec.3; the 400G application per this document until an OCI Gen2 application code is assigned), shall report the active mode per port, and shall expose in 200G mode the OCI v1.0 VDM observable and alarm set at OCI v1.0 granularity (per DWDM channel, per 212.5 Gb/s lane, per die). | OCI v1.0 Sec.3; CMIS 5.3 | I/T |
| CMP-011 | Operating mode shall be host-provisioned per port. Because OCI v1.0 defines no rate negotiation, the chiplet shall not autonomously change mode during a link session. It should detect a partner’s line rate during Deskew_Data_Detect by correlating the training pattern at both baud rates and, when the provisioned mode does not match, raise a rate-mismatch alarm (without switching mode). | OCI v1.0 Sec.1.1; Derived: BUP-001 | D |
| CMP-012 | Compliance in 200G OCI mode shall be demonstrated against OCI v1.0 Tables 2-2 to 2-5 with the OCI v1.0 TDEC recipe (26.5625 GHz BT4, 0.4/0.6 UI histograms, 2.4E-4) and SRS bench (3.4 dB SEC, aggressors at -3.2 dBm OMA), and interoperability shall be demonstrated against 200G OCI Type A and Type B partner devices — including relink/squelch handshakes and every path back to Deskew_Data_Relink — against the Table 1-3 timers. | OCI v1.0 T.2-2..2-5, Sec.2; Derived: VER-002/004/005/008 | T/D |

# 5. Logical Layer, Bring-up, and Management Requirements

## 5.1 PMA mapping, FEC budget, and link start-up

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| LOG-001 | In 400G OCI mode the PMA shall map two 212.5 Gb/s host streams — the two PMA lanes of a 400GBASE-R 16:2 SM-PMA (802.3dj Cl.176), each equivalent to a 200GBASE-R 8:1 SM-PMA output — to the four 106.25 Gb/s NRZ channels of one fiber port (2:4), and multiplex in reverse. Each host stream shall be 1:2 bit-demultiplexed onto a pair of adjacent wavelengths: host stream 0 onto channels 0 and 1 (the two shortest wavelengths), host stream 1 onto channels 2 and 3; within each pair the LSB shall map to the shorter wavelength, and recovered data shall return to the corresponding bit position (extension of the OCI v1.0 LSB-to-shortest-wavelength rule). The 200G-mode 1:4 mapping is defined by CMP-003. | 400G baseline; OCI v1.0 Sec.1, 1.2 (B7) | T |
| LOG-002 | The optical segment shall operate within a pre-FEC BER budget of 2.4E-4 in both modes. The host FEC is an RS-only architecture with no inner or concatenated FEC layer; the two permitted variants are RS(544,514) (200GBASE-R / 400GBASE-R / 800GBASE-R PCS) and RS(528,514). Both share the same 802.3dj Annex 174A PHY-to-PHY error ratio allocation: FEC codeword error ratio < 1.45E-11, equivalent to a total pre-FEC BER of 2.92E-4 for uncorrelated errors. The chiplet shall meet the 2.4E-4 compliance point regardless of which RS variant is deployed by the host PCS; the chiplet has no visibility into the FEC variant in normal operation. In 400G mode each host stream traverses two optical channels and the budget applies to the per-host-stream aggregate seen by the decoder. | 802.3dj Ann.174A | T/A |
| LOG-003 | The chiplet shall implement the OCI per-port deskew engine in both modes: transmit/detect the 160-bit training and release patterns of OCI v1.0 Tables 1-1/1-2 on each of the four channels, measure and remove inter-channel skew, and transition to mission data phase-continuously and glitch-free so the partner CDR never loses lock. | OCI v1.0 Sec.1.1 (both modes) | T/D |
| LOG-004 | Link bring-up timing shall comply with OCI v1.0 Table 1-3 in both modes: relink_squelch_tx_duration 60-75 ms; timeout_data_detect 200-250 ms; timeout_data_sync 100-150 ms; timeout_data_validate 200-450 ms; training-pattern duration >= 285 ms; release-pattern duration >= 200 ms; t_lock/t_loselock <= 50 ms; t_detect <= 100 ms; t_skew <= 100 ms. Timer values shall be firmware-configurable per mode pending publication of the OCI Gen2 specification. | OCI v1.0 T.1-3 (both modes) | T |

## 5.2 Deskew and bring-up engine

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| BUP-001 | Each channel shall implement 160-bit pattern generators and correlators for both the deskew training (Table 1-1) and release (Table 1-2) patterns, which differ only in bits 23:16 and carry wavelength-indexed channel IDs 0-3 per fiber port, operating at either line rate. Detection shall function at BER up to 1E-4 and remain robust under MPI and back-reflection (correlation/voting detection, not exact match). | OCI v1.0 Sec.1.1 (both modes) | T |
| BUP-002 | The deskew function shall compensate 0 to 15 UI (141 ps) of relative delay between the earliest and latest arriving channel in 400G mode (e.g., phase FIFOs plus programmable integer-UI digital delay per channel), covering fiber CD skew (< 6 UI) plus routing skew (< 4 UI per end), and 0 to 7 UI at 53.125 GBd in 200G mode (CMP-004) — the same absolute skew envelope. | 400G baseline; OCI v1.0 Sec.1.1 (B2) | T |
| BUP-003 | The deskew state machine shall remain armed indefinitely and re-enter Deskew_Data_Relink when RX data becomes invalid, defined as RX LOS, RX CDR loss of lock, or repeated uncorrectable FEC codewords reported by the host PCS on any host stream of the port. A D2D sideband shall carry the host-PCS uncorrectable-FEC indication to the chiplet. | OCI v1.0 Sec.1.1 (both modes) | T/D |
| BUP-004 | The receiver shall implement a loss-of-modulation detector, distinct from average-power LOS, that identifies modulation squelch (average power present, OMA absent) within the 50 ms t_loselock budget in both modes, to recognize the relink handshake. | OCI v1.0 Sec.1.1, T.2-3 (both modes) | T |
| BUP-005 | A configurable logical remap layer shall map physical TX/RX slices to wavelength-indexed channels (channel 0 = shortest wavelength) and shall map host streams to channels per LOG-001 (400G mode) or CMP-003 (200G mode), since deskew patterns and bit ordering are wavelength-indexed while physical channel numbering is implementation-specific. | OCI v1.0 Sec.1.1 (both modes) | I/T |

## 5.3 Bidirectional WDM and ELS interface

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| WDM-001 | Each fiber port shall carry 425 Gb/s (200G mode: 212.5 Gb/s) bidirectionally on a single fiber: TX on one CWDM group and RX on the other (Type A/B). The on-chip Band-Mux shall provide TX-to-RX isolation sufficient that local TX power (up to 9 dBm total in 400G mode) contributes negligible penalty at RX sensitivity levels. Asymmetric A/B implementations are permitted. | 400G baseline; OCI v1.0 Sec.2, F.2-1 | A/T |
| WDM-002 | Side-mode suppression ratio at the TX output shall be >= 30 dB in both modes; the ring modulator shall not degrade ELS SMSR (e.g., via side-mode enhancement near adjacent resonances, which lie closer in linewidth terms with the lower-Q rings required for 106.25 GBd). | OCI v1.0 T.2-2 (both modes) | T |
| WDM-003 | The design shall interoperate with the ELSFP envelope: laser linewidth <= 1 MHz, laser RIN <= -144 dB/Hz, polarization extinction ratio >= 16 dB on the PM input, ELS output reflectance and optical return loss tolerance of -26 dB. The TXO-009 budget shall account for ELS RIN integrated over the 400G-mode receiver bandwidth. | OCI v1.0 T.2-6 (both modes) | A/T |
| WDM-004 | Firmware shall implement the ELS power-control protocol: request per-wavelength power up to P_ELS_WL and request source-side attenuation up to dPELS, and shall use this mechanism to trim per-channel TX OMA, absorb coupling-loss variation, and set the mode-dependent launch power (TXO-007 in 400G mode; CMP-008 in 200G mode). Adequacy of P_ELS_WL for the 400G-mode launch-power plan shall be confirmed against the ELSFP envelope (Section 9). | OCI v1.0 T.2-6 n.1 | D |
| WDM-005 | Bring-up shall tolerate ELS start-up mode, in which wavelength and other parameters may be out of specification (continuity verification only). Ring-lock acquisition shall use a wide-range sweep/acquire strategy that does not assume on-grid ELS light at first illumination. | OCI v1.0 T.2-6 n.2 | D |

## 5.4 Built-in test and diagnostics

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| DFT-001 | Each channel shall include line-rate pattern generation and checking for PRBS13, SSPR, and PRBS31 (the patterns mandated by the compliance test conditions) at both 106.25 and 53.125 Gb/s. Per-channel PRBS checker BER shall be exposed as VDM observables (types 121-124). | OCI v1.0 T.2-2/2-3, T.3-2 | T |
| DFT-002 | The chiplet shall provide electrical loopback (around the SerDes) and optical/line loopback modes for debug and self-test in both modes, per the OCI recommendation and CPO test-access necessity. | OCI v1.0 Sec.3 | D |
| DFT-003 | Each channel shall implement an MPI-detection metric (VDM types 125-128), e.g., derived from slicer margin or low-frequency amplitude statistics, sensitive enough to flag links approaching the 0.2 dB MPI allocation. | OCI v1.0 T.3-2, T.2-5 | T/A |
| DFT-004 | Pre-FEC BER monitors shall be provided per 212.5 Gb/s host stream (two per port in 400G mode; one in 200G mode) for both host side and line side (VDM types 15/16), plus host-side LTP (type 8), with defined derivation (host PCS FEC counters and/or PRBS checkers). | OCI v1.0 T.3-2 | T |

## 5.5 Management plane (CMIS / VDM / alarms)

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| MGT-001 | The optical engine shall present a CMIS 5.3-based management interface to the host, implemented with an embedded processing core, advertising both operating modes (CMP-010). | OCI v1.0 Sec.3 | D/I |
| MGT-002 | Flag-summary registers shall be extended to banks 4-7 (upper nibble of the lower-page registers) for host layers managing eight optical engines (interposer OCI). | OCI v1.0 Sec.3.1, T.3-1 | T |
| MGT-003 | A flight data recorder should be provided for post-mortem debug, using the CDB protocol; implementation is vendor-specific. | OCI v1.0 Sec.3.2 | D |
| MGT-004 | Alarms and warnings shall be reported at three granularities: per DWDM channel (four per port: TX bias current from ELS, TX optical power, RX optical power, PRBS checker BER, MPI metric); per 212.5 Gb/s host stream (two per port in 400G mode, one in 200G mode: host/line pre-FEC BER, host LTP); per die (Vcc aux, TX temperature, RX temperature, chiplet temperature). Thresholds are mode-dependent and TBD (Section 9). | OCI v1.0 Sec.5 | T/I |
| MGT-005 | Digital diagnostics accuracy: chiplet temperature +/-3 degC at the cold-plate interface above the hottest region; ELS case temperature +/-3 degC; Vcc +/-2%; TX output and RX input power +/-2 dB referenced to the blade/chassis fiber connector; TX bias +/-10% relayed from the ELS. | OCI v1.0 T.4-1 | T |
| MGT-006 | On-die telemetry shall include separate TX-region and RX-region temperature sensors, an aggregate chiplet sensor, and aux-rail voltage monitors, placed to satisfy MGT-005 and to serve the heater-lock control loops. | OCI v1.0 T.4-1, Sec.5 | I/T |

## 5.6 IEEE 802.3dj upstream integration

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| DJI-001 | The chiplet shall interface cleanly to the 400GBASE-R 16:2 SM-PMA in 400G mode (two 212.5 Gb/s streams at the 200G/lane PMA service interface, 802.3dj Cl.176) and to a 200GBASE-R 8:1 SM-PMA lane in 200G mode, and shall support the PMA-level PRBS31Q test pattern with 17-bin block error counters (bins for 1-15 symbol errors plus 16+) per host stream, enabling the Annex 174A error-histogram method across the link. The 17-bin counter structure is common to both RS(544,514) and RS(528,514) host FEC variants and does not require the chiplet to distinguish between them. | 802.3dj Cl.176, Ann.174A | T |
| DJI-002 | Error burstiness shall be qualified against FEC codeword/block error ratio via error histograms, not mean BER alone. Transient events (e.g., ring heater-lock dither and recovery) shall be characterized against the bin counters. | 802.3dj Ann.174A | T/A |
| DJI-003 | PMD-style control/status shall be implemented: global and per-lane transmit disable, per-lane signal detect, TX fault and RX fault, exposed via the management mapping. Transmit disable shall be distinct from the heater-safe modulation squelch (TXO-010): two defined TX-off behaviors. | 802.3dj Cl.45 mapping | T/I |
| DJI-004 | The chiplet shall respect the 802.3dj PMD delay allocation for the applicable PMD class (400GBASE-R two-lane 106.25 GBd in 400G mode; 200GBASE-R single-lane in 200G mode, including 2 m fiber) and the SP2/SP3 skew and skew-variation limits — 802.3dj Table 116-9: skew variation SP2 0.4 ns (43 UI at 106.25 GBd; 21 UI at 53.125 GBd), SP3 0.6 ns (64 UI; 32 UI) — so host PCS deskew closes. Elastic buffer depth (bit count scaling with baud for the same time budget) shall be budgeted against these limits. | 802.3dj Cl.169, T.116-8/116-9 | A/T |
| DJI-005 | Start-up shall follow 802.3dj Annex 178B semantics for interfaces without full ILT: ready-to-send communicated by squelch/unsquelch; SIGNAL_OK derived from local and remote RTS; TX clock transitions from local to recovered clock only while RTS is false (retimer clock-switchover rule). Baud-independent protocol semantics, both modes. | 802.3dj Ann.178B | T/D |

## 5.7 Safety, regulatory, and compliance framework

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| REG-001 | The integrated system shall conform to the general safety requirements of IEEE 802.3 Annex J.2 (IEC 62368-class product safety). | 802.3dj PMD Cl. x.10.1 | I |
| REG-002 | The optical subsystem shall conform to Hazard Level 1 laser requirements per IEC 60825-1/-2 under any condition of operation, including single-fault conditions, whether coupled into fiber or out of an open bore, at the 400G-mode group launch power of up to 9 dBm (TXO-007) plus ELS fault headroom. Fault detection shall be capable of commanding ELS shutdown/attenuation; host usage restrictions shall be formally documented. | 802.3dj PMD Cl. x.10.2 | T/I |
| REG-003 | The integrated system shall comply with applicable local and national electromagnetic-emission codes; on-package EMI containment for the 106.25 GBd driver adjacent to the host ASIC is a chiplet-level design responsibility. | 802.3dj PMD Cl. x.10.5 | T |
| REG-004 | Normative optical specifications shall be met over the life of the product across the manufacturer-declared environmental and power range, in both modes, including end-of-life laser power droop and coupling degradation (heater range and lock-margin implications). | 802.3dj PMD Cl. x.10.4 | A/T |
| REG-005 | Product literature shall declare the operating environmental envelope, the supported operating modes, and distances over which specifications are met; labeling shall include applicable safety warnings, port-type designation, and Hazard Level 1 laser labeling. | 802.3dj PMD Cl. x.10.7 | I |
| REG-006 | PMD control/status variables shall be mapped per Clause 45 MDIO or a documented equivalent (CMIS implementation): reset, global/per-lane transmit disable, global/per-lane signal detect. | 802.3dj Cl.45 | I/T |
| REG-007 | A fault taxonomy shall define distinct, latched, reportable transmit fault, receive fault, and global PMD fault variables with documented trigger conditions (heater unlock, ELS power loss, CDR unlock, rate mismatch per CMP-011, etc.). | 802.3dj PMD mgmt | I/T |
| REG-008 | PMD_reset shall bring the chiplet to a defined safe state (TX squelched/disabled, deskew state machine in relink, heaters in safe mode) without violating laser safety during the transient. | 802.3dj Cl.45; REG-002 | T |
| REG-009 | Chiplet telemetry (line pre-FEC BER, VDM observables) shall be statistically consistent with host-PCS FEC-degrade detection and bin counters, so FEC-degrade signaling and field triage are coherent across the stack. | 802.3dj FEC degrade; OCI v1.0 T.3-2 | T/A |
| REG-010 | PICS proformas shall be completed for every 802.3dj clause claimed (Cl.176 SM-PMA, Annex 174A methods, Annex 178B behavior), together with an OCI compliance matrix (OCI v1.0 for 200G mode; the 400G baseline of this document until the OCI Gen2 specification is published). | 802.3dj PICS | I |

# 6. Derived Requirements (Internal Decomposition)

The requirements in this section are not stated in the governing specifications; they are the internal allocations required for Sections 4-5 to pass, each traced to its parent(s). Numeric placeholders are populated by the analyses they mandate and are tracked in the requirements database. Each subsection below names the companion design document that decomposes it (Section 1.7). Companion documents state how; this section states what, and governs on conflict. Absolute values alongside UI values are given at UI = 9.412 ps (400G mode); the 200G-mode absolutes are twice as large.

## 6.1 Transmitter budget decomposition

Decomposed in: DES-OCI-106G-TXD-001 (DTX-006, DTX-010); DES-OCI-106G-SQL-001 (DTX-012); DES-OCI-106G-JIT-001 (DTX-001). Photonics items DTX-002..005 and DTX-007..009 await DES-OCI-106G-PHO-001.

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| DTX-001 | A TX jitter budget shall decompose the TDEC 3.4 dB allocation across SerDes TX RJ, PLL phase noise, driver DJ, and ring-induced DDJ, with SSPR worst-case margin. Working target: total TX jitter well under 0.3 UI pk-pk (1 UI = 9.412 ps, i.e., under ~2.8 ps) before optical penalties. | Derived: TXO-003 | A |
| DTX-002 | End-to-end TX bandwidth shall be partitioned (SerDes output, driver, ring photon-lifetime) to meet the 8 ps 20-80% optical transition time; ring Q shall be selected on the modulation-efficiency vs. intrinsic-bandwidth trade against TXO-005/TXO-008. Working Q range ~2500-4000 (photon-lifetime bandwidth ~60-90 GHz; FWHM ~330-520 pm at 1310 nm). The selected Q shall also deliver the 200G-mode ER/TDEC (CMP-008). This is the gating photonics trade (risk R1). | Derived: TXO-008; CMP-008 | A/T |
| DTX-003 | Ring FSR and grid engineering: four cascaded rings per bus with resonances on the ~2.3 nm DWDM spacing; FSR chosen so no adjacent resonance lands on a neighbor channel; inter-ring crosstalk penalty allocated (< 0.5 dB) within the TDEC budget. At the ~330-520 pm linewidth of the DTX-002 ring the Lorentzian tail at the 2.3 nm neighbor offset is only about -21 dB, so the allocation shall be verified at the selected Q. | Derived: TXO-002/003 | A/T |
| DTX-004 | Heater tuning shall cover a full FSR (fab variation plus temperature range) with DAC resolution fine enough that residual detuning keeps OMA/ER/TDEC in specification (GHz-class detuning tolerance, scaling with linewidth); worst-case heater power shall be budgeted at temperature corners including the 400G-mode absorbed optical power. | Derived: TXO-002/005/006 | A/T |
| DTX-005 | The heater lock loop plus circuit compensation shall suppress pattern-dependent resonance drift to meet dTDEC <= 0.4 dB at the 400G-mode absorbed power (3 dB above 200G mode, risk R3); lock-dither amplitude shall be small enough not to consume the TDEC budget. A behavioral thermal-servo model shall be maintained. | Derived: TXO-004 | A/T |
| DTX-006 | Driver high and low output voltage levels (V_high, V_low) and the switching slew rate, mapped through the measured ring electro-optic transfer function, shall land ER within the 3.5-4.5 dB window in both operating modes at the DTX-002 Q (CMP-008). Because nonlinear switching drivers are used, ER and TDEC are set by the combination of drive-level selection and FIR pre-emphasis (ELE-007/010); pre-emphasis coefficients shall be characterised and stored per mode and temperature zone. Optical overshoot shall be kept <= 22% (TXO-008); the interaction of driver switching edges with ring photon lifetime and any ringing on the TP1 waveform shall be characterised, not assumed benign. | Derived: TXO-006/008; CMP-008 | T |
| DTX-007 | Ring transient chirp interacting with the CD range (-0.9 to +1.7 ps/nm) shall be verified against TDEC at both dispersion extremes. The dispersion penalty scales approximately with baud squared, so chirp shall be bounded explicitly at 106.25 GBd rather than assumed negligible. | Derived: TXO-003; LNK-001 | T/A |
| DTX-008 | Reflection immunity: RIN21.4OMA shall be met with 21.4 dB ORL applied in an isolator-free path; ELS stability shall be verified against worst-case chiplet back-reflection (-26 dB budget) at the 400G-mode launch power. | Derived: TXO-009/011 | T |
| DTX-009 | A coupling-loss allocation table (ELS-to-PMF-to-chip, on-chip routing, ring IL, mux, chip-to-fiber; TX and RX) shall be maintained and tracked against measured assembly-lot data; it is the closing document for LNK-001 and for the ELS power-headroom check of WDM-004 (risk R6). | Derived: LNK-001/002 | A/I |
| DTX-010 | Power-supply-induced jitter (TX PLL/driver) and heater-rail ripple (wavelength FM converting to amplitude noise post-ring) shall fit within the TDEC and RIN allocations; PSRR specifications shall be derived per rail over the 400G-mode signal bandwidth. | Derived: TXO-003/009 | A/T |
| DTX-011 | On-die TX-to-TX electrical and optical (bus waveguide) crosstalk across the four channels shall be budgeted against the 3 dB channel-imbalance case, consistent with the all-aggressors-active SRS condition (aggressors at -0.2 dBm OMA in 400G mode; -3.2 dBm in 200G mode). | Derived: RXO-002; TXO-005 | A/T |
| DTX-012 | The squelch circuit shall implement a bias-hold mode parking the ring so OMA <= -12 dBm (200G mode: <= -15 dBm) with constant average power (heater lock preserved at both ends), with entry/exit timing compatible with the 60-75 ms relink window and glitch-free re-entry into pattern transmission. Implementation per DES-OCI-106G-SQL-001; limits applied per mode (CMP-009). | Derived: TXO-010; LOG-004 | T |

## 6.2 Receiver budget decomposition

Decomposed in: DES-OCI-106G-RXF-001 (DRX-001..005); DES-OCI-106G-CDR-001 (DRX-006); DES-OCI-106G-EYM-001 (on-silicon confirmation of DRX-004). DRX-007/008 (ring demux and its servo) await DES-OCI-106G-PHO-001.

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| DRX-001 | Photodetector responsivity, dark current, capacitance, and bandwidth targets shall be derived to make RXO-001 achievable at 106.25 GBd (PD bandwidth consistent with the 64-80 GHz receive-chain target of DRX-004); PD capacitance shall be treated as the primary sensitivity-limiting term for the CTLE-only receiver (risk R2). | Derived: RXO-001 | A |
| DRX-002 | TIA input-referred current-noise density shall be back-computed from -5.2 dBm OMA sensitivity at BER 2.4E-4 (Q ~ 3.5 NRZ) through responsivity and coupling loss, integrated over the 400G-mode receive bandwidth, with margin held for the SEC-stressed case. The realized sensitivity difference between the two operating modes shall be reported against the 3 dB allowance of Section 1.5 (B3). | Derived: RXO-001/002 | A/T |
| DRX-003 | RX gain range and AGC shall support clean operation from the sensitivity floor to +2 dBm OMA (+3 dBm average) without overload, with 200G-mode gain ranges per CMP-009; AGC gain-step switching shall not disturb CDR lock. | Derived: RXO-003/004 | T |
| DRX-004 | CTLE peaking range and shape shall be derived to open a 3.4 dB SEC stressed eye with overall RX bandwidth ~0.6-0.75 x baud (64-80 GHz in 400G mode; a 32-40 GHz 200G-mode configuration per CMP-006); a statistical-eye analysis shall demonstrate CTLE-only closure of the SRS condition at -3.2 dBm OMA with aggressors active (gating analysis for the no-DFE architecture). | Derived: RXO-002; CMP-006 | A/T |
| DRX-005 | Slicer input-referred offset shall be trimmable, and a threshold-adaptation servo shall track baseline wander; the AC-coupling corner and wander tolerance shall be co-designed against the deskew-pattern and NRZ low-frequency content at both line rates. | Derived: RXO-001/002; BUP-001 | T |
| DRX-006 | The CDR shall be designed to the 802.3dj 106.25 GBd receiver jitter-tolerance mask (Table 176D-10, identical to Table 179-12, applied at native baud): 5 UI at 40 kHz, 1.5 UI at 133 kHz, 0.5 UI at 400 kHz, 0.15 UI at 1.33 MHz, 0.05 UI at 4, 12, and 40 MHz; the same mask shape applies at 53.125 GBd in 200G mode (CMP-005); and the CDR shall maintain lock through phase-continuous training/release/mission pattern transitions. | 802.3dj T.176D-10 / 176C.4.4.5; Derived: LOG-003 | T |
| DRX-007 | RX demux adjacent-channel rejection shall be sufficient that a neighbor channel 3 dB hotter contributes negligible crosstalk penalty at the photodetector, at the filter linewidth required for 106.25 GBd. | Derived: RXO-004 | A/T |
| DRX-008 | RX filter/ring lock shall acquire and hold using only incoming average power (no pilot tone), shall hold through partner squelch events, and shall reacquire after dark fiber, in both modes. | Derived: TXO-010; WDM-005 | T/D |
| DRX-009 | LOS calibration accuracy shall be allocated such that the 5 dB assert window (-16 to -11 dBm AOP in 400G mode; -19 to -14 dBm in 200G mode) and the +/-2 dB power-reporting accuracy are met by the same monitor path. | Derived: RXO-006; MGT-005 | A/T |
| DRX-010 | RX baseline-wander and interferometric-noise sensitivity shall be characterized against the 0.2 dB MPI allocation, and the MPI metric (DFT-003) shall be validated as a leading indicator. | Derived: LNK-001; DFT-003 | T/A |

## 6.3 Clocking, D2D, and system integration

Decomposed in: DES-OCI-106G-CLK-001 (SYS-001, SYS-002; SYS-003 interface only). The half-rate clocking decision that SYS-001 asks to be documented is recorded in Section 3.3. SYS-004..008 are system and logic obligations without a companion document at this revision.

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| SYS-001 | The line clock shall be derived from the host PCS clock domain over the D2D interface (forwarded/derived clock) to guarantee the +/-50 ppm in-package tolerance; the dual-rate synthesis chain (106.25 and 53.125 GBd; full-rate or half-rate clocking architecture) and frequency plan shall be documented. | Derived: TXO-001; CMP-005; decision recorded Section 3.3, DES-OCI-106G-CLK-001 Section 2.3 | A/I |
| SYS-002 | Reference and TX PLL phase-noise budgets shall be allocated from DTX-001 and ELE-005 (sigma_RJ <= 104 fs rms), integrating phase noise over the far-end CDR-tracked band to a UI-rms target; the refclk specification shall be derived accordingly. | Derived: DTX-001; ELE-005 | A |
| SYS-003 | Per-host-stream elastic FIFOs at the recovered-clock to host-clock crossing shall be sized for +/-100 ppm worst-case offset (bit depth scaling with baud for the same time budget) while respecting the PMD delay allocation and skew-variation limits (DJI-004). | Derived: DJI-004 | A/T |
| SYS-004 | The D2D electrical link (UCIe/BoW/custom, 425 Gb/s per port plus sideband) shall be effectively error-free (raw BER <= 1E-15 class) so it consumes none of the 2.4E-4 optical budget; any D2D retry/CRC mechanism shall not inject burst errors visible to host FEC bins. | Derived: LOG-002; DJI-002 | A/T |
| SYS-005 | Power sequencing shall define rail bring-up order with TX held safe (disabled/squelched) until heaters lock and the ELS handshake completes; brownout response shall never violate laser safety or leave rings unlocked while transmitting. | Derived: REG-002/008 | T/D |
| SYS-006 | Thermal design shall guarantee specification compliance across the declared cold-plate temperature range with hottest-region sensing (MGT-006); a heater-power vs. plate-temperature analysis shall demonstrate lock margin at both extremes including the 400G-mode absorbed optical power. | Derived: REG-004; MGT-005 | A/T |
| SYS-007 | An end-to-end bring-up sequence (mode provisioning, ELS start-up/continuity, ring acquisition, power request/trim, deskew training) shall be defined with a bounded total time-to-traffic consistent with the Table 1-3 timers, and documented for both modes. | Derived: WDM-005; LOG-004; CMP-001 | D |
| SYS-008 | The multi-port scaling architecture (3.2T die = 8 x 425 Gb/s ports, or 1.6T die = 4 ports; half the aggregate in 200G mode) shall define per-die alarm granularity, shared vs. per-port ELS wavelength strategy, bank management (MGT-002), and a pJ/bit power target per mode. | Derived: MGT-002/004 | A/I |

## 6.4 Transmitter electrical decomposition at TP1

Decomposed in: DES-OCI-106G-JIT-001 (derivation of ELE-002..005 and the dual-Dirac budget); DES-OCI-106G-TXD-001 (implementation of ELE-001..010 at TP1); DES-OCI-106G-CLK-001 (ELE-003 half-rate DCD, ELE-007/008 branch-phase generation).

The optical specifications bind TX quality only through the TDEC family at TP2 and provide no electrical decomposition that can bind the transmitter. At 106.25 GBd the IEEE P802.3dj 200G/lane electrical clauses run at exactly the line-side baud: the limits below apply at native baud via Annex 176C/176D (200GAUI-1 C2C/C2M), which import the Clause 179 jitter definitions (179.9.4.6: JRMS03 / EOJ03 / J4u03; later drafts JHRMS / EOJ03 / JH4u) at a 106.25 +/- 50 ppm GBd signaling rate. The 802.3dj values are PAM4 clock-jitter metrics on full-swing (0-3) transitions and transfer to NRZ directly. In 200G mode the same UI-relative limits apply at 53.125 GBd, where the baud-matched cross-check is OIF CEI-112G-XSR (CMP-007). The internal dual-Dirac budget that no standard specifies is stated in UI and in absolute terms at 9.412 ps.

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| ELE-001 | All transmitter electrical requirements shall be defined at TP1, the electrical input to the MRM modulator. TP1 is buried in-package without physical access and shall be verified by simulation, on-die instrumentation, and test-vehicle measurement rather than bench test; the correlation of TP1 electrical limits to the TP2 optical requirements shall be documented through the MRM electro-optic model. | Derived: TXO-003..008 | A/I |
| ELE-002 | TP1 RMS clock jitter (JRMS03 / JHRMS; slope-extrapolated with additive noise removed) shall be <= 0.023 UI rms (216 fs at UI = 9.412 ps), measured per the 802.3dj methodology: CRU corner 4 MHz at 20 dB/decade, full-swing transitions only. | 802.3dj 179.9.4.6 via Ann.176C.4.3.6 | A/T |
| ELE-003 | TP1 even-odd jitter (EOJ03, the duty-cycle-distortion analog on full-swing NRZ edges) shall be <= 0.025 UI pp (235 fs at UI = 9.412 ps). | 802.3dj 179.9.4.6 via Ann.176C | A/T |
| ELE-004 | TP1 bounded high-probability clock jitter (J4u03 / JH4u, the all-but-1E-4 interval of the jitter distribution) shall be <= 0.118 UI pp (1.11 ps at UI = 9.412 ps; D1.3 Class A value, Class B 0.12 UI). | 802.3dj 179.9.4.6 via Ann.176C | A/T |
| ELE-005 | An internal dual-Dirac jitter budget shall be maintained at the committed raw-BER 1e-12 (FEC-free) operating point, which no standard specifies: sigma_RJ <= 0.011 UI rms (104 fs); DCD <= 0.025 UI pp (235 fs); ISI <= 0.012 UI pp (113 fs); BUJ <= 0.036 UI pp (339 fs); DDJ = DCD + ISI <= 0.037 UI pp (348 fs); DJ-dd <= 0.123 UI pp (1.16 ps, FIR enabled) / 0.073 UI pp (0.69 ps, no-FIR); TJ(1e-12) <= 0.278 UI pp (2.61 ps) / 0.228 UI pp (2.14 ps). Bounded terms add linearly (worst-case-additive sign-off convention); Gaussian terms add in RSS at Q = 7.034. | Derived: LOG-002; TXO-003; DES-OCI-106G-JIT-001 Sections 4-5 | A |
| ELE-006 | The TP1 electrical 20-80% transition time shall be allocated <= 0.35 UI typical (3.3 ps) with a 4.0 ps hard maximum under the extracted MRM-plus-pad load, and electrical rise/fall mismatch shall be <= 3.7% of UI (0.35 ps), so that residual asymmetry remains within the correction capacity of the asymmetric FIR banks (ELE-010) and the TP2 8 ps optical transition-time limit (TXO-008) closes with margin. | Derived: TXO-008 | A/T |
| ELE-007 | The transmitter shall implement a 3-tap analog FIR (pre, main, post) with branch delays fixed at 0/1/2 UI of the operating baud (0 / 9.41 / 18.82 ps in 400G mode; 0 / 18.82 / 37.65 ps in 200G mode, CMP-007), pre- and post-tap weight ranges of 0 to -0.25, and at least 2-bit tap resolution; coefficient-quantization noise shall be shown negligible within the TDEC budget. | Derived: TXO-003/008; CMP-007 | A/I |
| ELE-008 | Inter-tap phase-delay matching between FIR slices shall be <= 2.6% of UI (0.24 ps in 400G mode) across process, voltage, and temperature corners and across all legal tap codes. | Derived: TXO-003 | T |
| ELE-009 | FIR coefficient updates shall be glitchless (hitless) in mission mode: tap codes shall be updatable during live traffic without raw-BER degradation, error bursts visible to host FEC bins, or partner CDR re-acquisition, enabling live trimming for temperature and aging drift. | Derived: TXO-003/004; DJI-002 | T/D |
| ELE-010 | The transmitter shall provide independent logic-1 and logic-0 FIR coefficient banks to correct the asymmetric rise/fall dynamics of the carrier-depletion MRM (voltage-dependent junction capacitance and detuning-dependent transitions); hardware support is normative, programmed values are populated by simulation sweep per mode. | Derived: TXO-008; DTX-006 | I/T |

## 6.5 Clock and data recovery

Decomposed in: DES-OCI-106G-CDR-001 (loop, lock detector, gear-shift, CID coast, signal-valid hold); DES-OCI-106G-CLK-001 Section 9 (the phase interpolator the loop drives).

These requirements make the CDR behaviors that link robustness depends on normative, complementing DRX-006. The JTOL mask and CRU corner come from the 802.3dj 106.25 GBd receiver specification at native baud in 400G mode; in 200G mode the baud-matched cross-check is OIF CEI-112G-XSR (Table 2-1, CMP-005).

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| CDR-001 | The RX CDR closed-loop bandwidth shall lie in a 4-6 MHz design window in both modes, above the 4 MHz corner of the native 802.3dj 106.25 GBd JTOL mask (Table 176D-10: 0.05 UI shelf from 4 MHz; 4 MHz measurement CRU per 179.9.4.6) and above the CEI-112G-XSR corner (~4.0 MHz at 53.125 GBd) in 200G mode, so untracked sinusoidal jitter stays under a 0.10-0.15 UI pk-pk budget; mission-mode loop shaping shall be heavily damped (zeta >> 1) with jitter peaking low enough not to erode the eye budget. The window shall be re-checked against the CEI-224G-XSR mask when published (Section 9). | 802.3dj T.176D-10, 179.9.4.6; CEI-112G-XSR (200G mode); Derived: DRX-006 | A/T |
| CDR-002 | The CDR shall acquire and track a +/-200 ppm frequency offset (2x margin over the +/-100 ppm relative offset of two +/-50 ppm ends, TXO-001), and the frequency register shall be sized with at least 20% clamp margin beyond the design target, saturating (never wrapping) at its bound. | Derived: TXO-001; 802.3dj Cl.176 | A/T |
| CDR-003 | The CDR shall coast through at least 72 UI (678 ps in 400G mode; 1.36 ns in 200G mode) of consecutive identical digits without loss of lock while the full JTOL mask of DRX-006 is applied (test pattern construction per the OIF CEI JTOL method: 72-UI runs of both polarities between PRBS31 segments); during the run the learned frequency estimate shall continue to advance the sampling phase. | Derived: DRX-006; OIF CEI-05.3 Sec.3.2 (method) | T |
| CDR-004 | Cycle slips are permitted only during acquisition, before mission data. In mission-mode tracking, cycle slips shall be vanishingly rare such that error bursts longer than 7 symbols occur with probability < 1E-20, keeping burst statistics compatible with the host FEC bin-histogram acceptance criterion. | Derived: DJI-002 | A/T |
| CDR-005 | The CDR shall implement a lock detector with programmable phase- and frequency-settling thresholds and consecutive-window persistence for both assert and de-assert, exposed to the link state machine, and fast enough to support the t_lock / t_loselock <= 50 ms budgets of RXO-007 and Table 1-3. | Derived: RXO-007; LOG-004 | T |
| CDR-006 | On an invalid-signal condition (LOS or loss of modulation), the CDR shall hold its phase-interpolator code, phase accumulator, and frequency register, and freeze all adaptation loops; on signal return it shall resume from the held state (warm re-acquisition) rather than re-acquiring from presets. The signal-valid gate shall not fire during a CID run. | Derived: TXO-010; BUP-004 | T/D |
| CDR-007 | The CDR shall provide programmable acquisition and mission gain sets (acquisition gear-shift), and the transition from acquisition to mission gains shall not itself cause loss of lock or a phase transient exceeding the tracking budget. | Derived: LOG-004 | T |

## 6.6 Adaptation and bring-up behavior

Decomposed in: DES-OCI-106G-ADP-001; interfaces to DES-OCI-106G-RXF-001 (codes) and DES-OCI-106G-CDR-001 (lock gate).

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| ADP-001 | RX adaptation shall follow a nested bring-up: threshold (Vp), offset/BLW, gain (AGC), and equalization (CTLE) loops shall be held frozen at presets until the CDR asserts lock, then released in a defined nesting order, with total convergence fitting inside the training-pattern duration budget of LOG-004 (>= 285 ms training window). | Derived: LOG-004; RXO-002 | T/D |
| ADP-002 | All adaptation loops shall freeze (adapt = false) and telemetry accumulation shall be gated invalid during non-mission periodic patterns, TX squelch, and invalid-signal conditions, because non-white pattern autocorrelation biases the loop observables; loops re-enable only once mission-rate data is present. | Derived: LOG-003; TXO-010 | T |
| ADP-003 | Converged loop dither shall be bounded to approximately 1 LSB per loop via sub-LSB accumulator gain and dead-bands, and the aggregate dither of all loops (threshold, offset, gain, peaking, plus CDR phase dither) shall be budgeted within the RX eye margin at the 2.4E-4 compliance point and the 1e-12 internal point. | Derived: RXO-001/002 | A/T |
| ADP-004 | Equalizer (CTLE) code changes shall be de-glitched (response swap aligned between UI), and the threshold and timing loops shall be allowed to re-settle before new adaptation windows are used, so that adaptation stepping never disturbs CDR lock or produces FEC-visible error bursts. | Derived: DRX-004/006; DJI-002 | T |
| ADP-005 | The receive-path AC-coupling / DC-offset-cancellation corner shall be sized to hold baseline wander to <= 0.05 dB over a 72-bit consecutive-identical-digit run (678 ps in 400G mode; 1.36 ns in 200G mode), co-designed with the deskew-pattern spectrum and the threshold-adaptation servo of DRX-005. | Derived: DRX-005 | A/T |

## 6.7 Loss-of-modulation detection

These requirements decompose BUP-004 into a verifiable detector specification. Decomposed in: DES-OCI-106G-SQL-001 Section 6 (requirement-numbering re-base pending, Section 9); the detection threshold is mode-dependent (CMP-009).

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| LOM-001 | The receiver shall implement a loss-of-modulation detector, distinct from average-power LOS, formed as the logical AND of: (a) average optical power above the LOS de-assert level, from the RXO-006 average-power monitor that is independent of the data path; and (b) a modulation-amplitude metric below a defined absolute threshold. Loss-of-modulation and LOS shall be reported as distinct conditions and shall drive distinct branches of the BUP-003 relink logic, since the first indicates a squelching (relinking) partner and the second a dark fiber. | Derived: BUP-004; RXO-006 | T |
| LOM-002 | The modulation-amplitude detection threshold shall be an absolute, gain-referred level placed inside the discrimination band between the maximum legal squelched OMA at TP3 (<= -12 dBm at TP2 minus channel loss) and the minimum legal mission OMA (stressed sensitivity -3.2 dBm; sensitivity floor -5.2 dBm), nominally -9 to -8 dBm OMA-equivalent in 400G mode (200G mode: -15 dBm squelch vs. -6.2 / -8.2 dBm mission, nominally -12 to -11 dBm), referred to the slicer input through the calibrated TIA/AGC gain (consistent with the MGT-005 accuracy chain). Detection shall use amplitude/threshold-crossing statistics, not transition density. The adaptive Vp/error-slicer thresholds shall not serve as the detection reference. | Derived: TXO-010; RXO-001/002; CMP-009 | A/T |
| LOM-003 | Loss-of-modulation assertion shall require the amplitude metric to remain below threshold for a programmable persistence window bounded such that legal no-modulation intervals (72-UI CID runs, phase-continuous pattern swaps) and AGC transients never false-assert (window >= 1 us), while end-to-end detection latency remains within the 50 ms t_loselock budget (window <= 10 ms recommended). De-assertion shall be symmetric with hysteresis so a marginal signal does not chatter the relink state machine. | Derived: BUP-004; RXO-007; LOG-004 | T |
| LOM-004 | The detector shall be robust to the AGC: either the detection threshold shall track the AGC gain code (absolute referral), or candidate detection shall freeze the AGC before the persistence window is evaluated. On assertion, the detector shall de-assert signal_valid — holding CDR phase/frequency state and freezing all adaptation loops per CDR-006 and ADP-002 — and shall notify the deskew state machine to enter Deskew_Data_Relink. | Derived: DRX-003; CDR-006; BUP-003 | T/D |

## 6.8 Squelch implementation decomposition

These requirements decompose DTX-012 into a verifiable squelch specification with defined observables and entry/exit constraints. Implementation detail, design trades, and sequencing — the static-rail serializer park with thermal re-park of the ring, the drop-port power servo, and the pre-position/walk-back exit sequence — are in DES-OCI-106G-SQL-001 (requirement-numbering and dual-mode re-base pending, Section 9). Power limits are applied per mode (CMP-009); the drive-induced detuning shift is a small fraction of the ring linewidth in either mode.

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| SQL-001 | The DTX-012 bias-hold squelch shall suppress modulation only: launched OMA shall be <= -12 dBm during squelch in 400G mode (<= -15 dBm in 200G mode), average optical power shall remain constant at the mission setpoint, and full-swing toggling at any rate is prohibited. Only heater lock dither, already budgeted within TDEC (DTX-005), may remain as a residual modulation component. | Derived: DTX-012; TXO-010 | I/T |
| SQL-002 | The squelch power servo shall use the per-channel drop-port monitor as its observable. The servo setpoint shall be a drop-port target calibrated to the normative launched per-channel average power, with a distinct calibration point for the parked drive state, stored per channel and per mode in calibration NVM (MFG-003). The aggregate bus tap may be used as a cross-check on group total launch power (<= 9 dBm in 400G mode; <= 6 dBm in 200G mode) but shall not serve as the per-channel servo observable. | Derived: TXO-010/007; MGT-005; MFG-003 | A/T |
| SQL-003 | The parked rail polarity shall be selected per channel such that the pre-servo launch-power transient at squelch entry never drives far-end average receive power below the worst-case LOS assert threshold (-11 dBm AOP in 400G mode; -14 dBm in 200G mode) under worst-case mission Pavg (-5.5 dBm; -8.5 dBm) and channel insertion loss (2.5 dB). A spurious far-end LOS during squelch entry shall be treated as a failure of the relink handshake. | Derived: TXO-010; RXO-006; CMP-009 | A/T |
| SQL-004 | Squelch entry: launched OMA shall fall to the mode’s squelched-OMA limit immediately upon parking (within driver settling time), and launched average power shall settle to within a defined tolerance of the mission setpoint (placeholder, tracked in Section 9) well inside the 60-75 ms relink_squelch_tx_duration window. The required heater detuning shift shall be verified to be within servo authority at all temperature corners. | Derived: DTX-012; LOG-004 | A/T |
| SQL-005 | Squelch exit: the unsquelch sequence shall be explicitly defined such that re-entry into pattern transmission is glitch-free, the residual OMA/ER/TDEC transient never causes the partner CDR to lose lock or training-pattern detection to fail (pattern detect margin: functional at BER <= 1E-4 with correlation/voting, training window >= 285 ms), and dTDEC recovery is complete before mission data. Exit behavior shall be verified by partner-squelch soak testing in both modes (risk R4). | Derived: DTX-012; BUP-001; LOG-003/004 | T/D |

# 7. Robustness, Reliability, EMC, Manufacturing, and Firmware Requirements

These families cover the device-robustness and productization obligations that the optical and logical requirements of Sections 4-6 presuppose but do not state. They are baud-independent except where noted and are normative for product release; they feed the VER-010 evidence package.

## 7.1 ESD and electrical robustness

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| ROB-001 | ESD withstand: management and low-speed host pins shall withstand >= 2 kV HBM per ANSI/ESDA/JEDEC JS-001; high-speed line-side and D2D microbump interfaces shall withstand >= 250 V CDM per JS-002, with the device ESD classification and any handling restrictions documented in the datasheet. | JS-001 / JS-002 | T/I |
| ROB-002 | The chiplet shall be latch-up immune per JESD78 Class II (+/-100 mA, 1.5x Vmax overvoltage) at maximum rated junction temperature. | JESD78 | T |
| ROB-003 | Any power-rail sequencing order and ramp rate within datasheet limits shall be non-damaging and shall not violate laser safety; undervoltage/brownout detection on every rail shall force the safe state of REG-008 (TX squelched/disabled, heaters safe) before logic becomes indeterminate, and recovery from brownout shall re-enter the bring-up sequence cleanly. | Derived: REG-002/008; SYS-005 | T/D |
| ROB-004 | The chiplet shall meet all specifications with every supply rail at +/-5% of nominal (or the tighter declared tolerance), shall survive transient excursions within the declared PDN mask without damage or configuration loss, and shall provide on-die supply monitors with warning/critical thresholds mapped to the MGT-004 alarm structure. | Derived: MGT-004/006 | A/T |
| ROB-005 | The TX driver output shall survive an indefinite short circuit or open circuit at the MRM interface (including an unbonded or failed microbump) without damage, and shall detect and report a latched TX fault for a stuck or non-responding modulator interface. | Derived: REG-007 | T |
| ROB-006 | The die shall monitor junction temperature against warning and critical thresholds; a critical over-temperature event shall force heater-safe squelch and request ELS attenuation/shutdown without violating IEC 60825 Hazard Level 1 during the transient, and shall be reported as a latched fault. | Derived: REG-002/007; MGT-004 | T/D |
| ROB-007 | Silicon wearout (electromigration, HCI, BTI, TDDB, and stress migration) shall be signed off for >= 100,000 power-on hours at the declared mission profile (temperature and activity, 400G mode as the worst case), including the heater DAC drivers and the continuously-toggling 106.25 GBd line-rate paths; derating rules and the mission profile shall be documented. | Derived: REG-004 | A |

## 7.2 Reliability and environmental qualification

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| REL-001 | The chiplet shall complete a component qualification per JEDEC JESD47 (or a documented CPO-adapted equivalent): HTOL >= 1000 h at maximum rated junction temperature, temperature cycling per JESD22-A104 across the declared storage range, THB/uHAST moisture stress, and high-temperature storage, with zero fails on the defined sample plan or documented disposition. | JESD47 / JESD22 | T/I |
| REL-002 | CPO-specific interconnect reliability shall be qualified: the EIC-to-PIC microbump array and the fiber-attach/coupling interface shall survive temperature cycling, mechanical shock, and vibration per a documented GR-468-derived plan, with post-stress coupling-loss drift remaining inside the DTX-009 lot-tracked allocation and post-stress TP2/TP3 compliance demonstrated in both modes. | Telcordia GR-468 (adapted); Derived: LNK-001 | T |
| REL-003 | The moisture sensitivity level of the assembled part shall be classified per J-STD-020 and declared, with bake and floor-life handling requirements documented for module assembly. | J-STD-020 | I/T |
| REL-004 | A long-term failure-rate target (FIT, placeholder pending reliability budget roll-up) shall be allocated and demonstrated by HTOL extrapolation at 60% confidence; early-life failures shall be screened by burn-in or a statistically justified equivalent screen. | Derived: REG-004 | A/T |
| REL-005 | Soft-error robustness: configuration registers (including the active operating mode and its parameter set), safety-relevant state machines (deskew/relink, squelch, heater control), and embedded-core memories shall be protected (parity, ECC, or redundancy) such that a single-event upset cannot cause a laser-safety violation, silent corruption of normative operating points, an unflagged mode change, or an unflagged link-down; detected upsets shall be counted and reported. | Derived: REG-002/007; CMP-009 | A/T |
| REL-006 | The declared environmental envelope (cold-plate temperature range, humidity, altitude) shall be verified by test at its extremes with all normative optical specifications met in both modes, including heater lock margin at the hot extreme with hot data patterns at the 400G-mode absorbed optical power (per SYS-006), and results shall feed the REG-005 product-literature declaration. | Derived: REG-004/005; SYS-006 | T |

## 7.3 Electromagnetic compatibility and crosstalk

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| EMC-001 | A chiplet-level radiated-emissions budget shall be defined and met so that the host platform can comply with CISPR 32 / FCC Part 15 Class A: on-package containment (layout, shielding, return-path design) for the 106.25 GBd drivers and clock spurs adjacent to the host ASIC is a chiplet design responsibility, decomposed from REG-003. | Derived: REG-003; CISPR 32 | A/T |
| EMC-002 | Under platform-level radiated and conducted immunity stress (IEC 61000-4-3 / -4-6 class), the chiplet shall exhibit no damage, no laser-safety violation, and no unrecoverable state: any link degradation shall be flagged through the standard fault/alarm structure and shall recover autonomously via the permanently-armed relink logic. | IEC 61000-4; Derived: BUP-003 | T/D |
| EMC-003 | Aggregate on-die and in-package crosstalk (TX-to-TX, TX-to-RX, D2D-to-analog, heater/supply coupling) shall be budgeted within the ELE-005 bounded-uncorrelated-jitter allocation (BUJ <= 0.036 UI = 339 fs) and the RX eye budget, and verified with all lanes active on uncorrelated data and worst-case tap codes (consistent with the all-aggressors-active SRS condition of RXO-002). | Derived: RXO-002; ELE-005 | A/T |
| EMC-004 | The line clock shall carry no spread-spectrum modulation, and reference/PLL spur limits shall be derived from the ELE-004 bounded-jitter ceiling at each operating baud; spur compliance shall be verified at the PLL output and at the serializer output across PVT in both modes. | Derived: TXO-001; ELE-004 | A/T |

## 7.4 Manufacturing test and screening

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| MFG-001 | Wafer-level production test shall cover DC/leakage parametrics, structural test with >= 98% stuck-at coverage plus transition-fault coverage on the digital core, memory BIST on all embedded memories, and analog trim of references, offsets, and DAC ranges. | Derived: VER-006 | T/I |
| MFG-002 | A known-good-die (KGD) flow shall be defined to protect CPO assembly yield: pre-assembly line-rate self-test at 106.25 Gb/s (and a 53.125 Gb/s mode check) using the on-chip PRBS generators/checkers and electrical loopback (DFT-001/002) at wafer or singulated-die level, with documented KGD pass criteria and outgoing quality target. | Derived: DFT-001/002 | T/I |
| MFG-003 | Per-device calibration (heater DAC ranges and lock presets, threshold/offset trims, PI linearity, monitor calibrations per MGT-005, squelch drop-port setpoints per SQL-002, and the per-mode parameter sets of CMP-009) shall be stored in on-die or module NVM with integrity protection (CRC or ECC); a failed boot-time integrity check shall force documented fail-safe defaults and a latched fault, never an unsafe or silently mis-calibrated state. | Derived: MGT-005; REG-007; CMP-009 | T/I |
| MFG-004 | Post-assembly production screening shall include TP2/TP3 parametric test (OMA, ER, average power, sensitivity; TDEC on a documented sample plan) at the calibrated fiber reference plane of VER-001 in 400G mode, plus a documented 200G-mode subset sufficient to guarantee CMP-002, with guard-banded production limits traceable to the Section 4 values. | Derived: VER-001/002; CMP-002 | T/I |
| MFG-005 | Each device shall carry an electronically readable unique ID (exposed via the CMIS management interface) linking to lot/wafer/die-coordinate traceability and to the DTX-009 coupling-loss lot-tracking records, supporting field triage and recall containment. | Derived: DTX-009; MGT-001 | I |
| MFG-006 | Statistical outlier screening (part-average testing or statistical bin limits) shall be applied to key parametrics (sensitivity, TDEC-correlated metrics, heater power, supply currents) to remove maverick material that passes absolute limits but deviates from the population. | Derived: REG-004 | I/T |

## 7.5 Firmware and management robustness

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| FW-001 | Firmware images for the embedded management core shall be cryptographically signed, and the boot process shall reject unauthenticated or corrupted images; the active firmware version and image hash shall be readable via the CMIS interface. | Derived: MGT-001 | T/I |
| FW-002 | Firmware update over the CDB protocol shall be fail-safe: loss of power or aborted transfer at any point during an update shall leave the device bootable (dual-bank or protected golden image), with automatic fallback and a reported update-failure status. | Derived: MGT-003; OCI v1.0 Sec.3.2 | T/D |
| FW-003 | A hardware watchdog shall supervise the embedded core; watchdog expiry shall force the REG-008 safe state (TX squelched/disabled, heaters safe, deskew in relink) without violating laser safety, set a latched fault, and log the event to the flight data recorder. | Derived: REG-007/008; MGT-003 | T |
| FW-004 | The management register map shall be robust to illegal access: out-of-range or malformed writes shall be rejected or clamped without hanging the management interface or corrupting adjacent state, and safety-critical controls (ELS power requests, transmit disable, heater overrides, operating-mode selection) shall require defined multi-step write sequences to prevent single-write accidents. | Derived: REG-002/006; CMP-001 | T/I |
| FW-005 | In mission mode, safety- and compliance-critical configuration (normative operating points, squelch/heater parameters, deskew timers, operating mode, and the mode-dependent thresholds of CMP-009) shall be modifiable only through a defined maintenance state, and all such changes shall be recorded with timestamps in the flight data recorder to keep the compliance evidence chain intact. | Derived: REG-010; MGT-003; CMP-009 | I/D |

# 8. Verification, Conformance, and Manufacturing

| **Req ID** | **Requirement** | **Source** | **Ver.** |
| --- | --- | --- | --- |
| VER-001 | A TP2/TP3 test-access strategy shall be defined for the CPO part (calibrated fiber pigtail / connector reference plane); power-monitor calibration shall de-embed all loss between chip and the blade/chassis fiber connector reference point. | Derived: MGT-005 | I/T |
| VER-002 | Golden TDEC measurement recipes shall be established for both modes (400G: 53.125 GHz BT4 reference receiver; 200G: 26.5625 GHz BT4 per OCI v1.0; no equalizer, 0.4/0.6 UI histograms, 2.4E-4 threshold) and correlated between internal benches and compliance-lab instruments before margin claims; the 400G recipe shall be checked against 802.3dj Cl.180 TDECQ instrumentation at the same baud for reference-receiver calibration practice. | OCI v1.0 T.2-2 n.2; 802.3dj Cl.180 (method) | T/I |
| VER-003 | A pattern-mapped test plan shall cover PRBS13 (wavelength/ER/OMA/RIN), SSPR (TDEC/transition/overshoot), and PRBS31 (sensitivity/BER floor/SRS) at both line rates; on-die generators shall be validated bit-for-bit against external BERT patterns. | OCI v1.0 T.2-2/2-3 | T |
| VER-004 | An SRS conformance bench shall be built and calibrated for both modes: 3.4 dB SEC stressor on the channel under test with three aggressors active at -0.2 dBm OMA (400G mode) or -3.2 dBm OMA (200G mode, OCI v1.0 Table 2-4). | 400G baseline; OCI v1.0 T.2-4 | T/I |
| VER-005 | An interoperability program shall test A-type against B-type partners, including asymmetric implementations permitted by OCI v1.0. In 200G mode this shall include multi-vendor 200G OCI partner devices (CMP-012). In 400G mode the program shall begin with calibrated reference transmitters/receivers and two-chiplet self-interoperation and shall be extended to third-party 400G OCI partners when available. | OCI v1.0 Sec.2; CMP-012 | D |
| VER-006 | A corner qualification matrix shall demonstrate all optical specifications across voltage, temperature, and aging corners in both modes, including heater lock at hot-plate plus hot-data worst case at the 400G-mode absorbed optical power (lifetime normative language). | REG-004 | T |
| VER-007 | System-level qualification shall collect 17-bin FEC error histograms (Annex 174A) through thermal transients, squelch/relink events, mode-provisioning cycles, and MPI injection; pass/fail shall be judged on codeword error ratio, not mean BER. | 802.3dj Ann.174A | T |
| VER-008 | Bring-up robustness testing shall exercise and time every path back to Deskew_Data_Relink in both modes: fiber hot-plug, mid-traffic disconnect, partner reset, injected 1E-4 BER during pattern detect, MPI/back-reflection during deskew, and rate-mismatch provisioning (CMP-011), all against the Table 1-3 timeouts. | OCI v1.0 Sec.1.1, T.1-3 | T/D |
| VER-009 | Management-plane conformance shall include CMIS 5.3 compliance testing (with bank 4-7 extensions and both advertised applications), VDM observable accuracy validation against instruments, and FDR retrieval verification via CDB. | OCI v1.0 Sec.3; CMP-010 | T/D |
| VER-010 | A release documentation package shall be produced: completed 802.3dj PICS, OCI compliance matrix (OCI v1.0 for 200G mode; the 400G baseline of this document until the OCI Gen2 specification is published), laser-safety certification file with host usage restrictions, declared environmental envelope and operating modes, coupling-loss budget with measured distributions, and interoperability reports. Absent a certification body, this evidence package constitutes MSA compliance. | REG-005/010 | I |

# 9. Open Items and Specification Watch List

**400G OCI mode baseline:**

- **OCI Gen2 specification in authoring.** Every “400G baseline” value shall be re-baselined when the OCI Gen2 specification is published. Firmware-visible thresholds derived from baseline values (LOS, squelched OMA, LOM threshold, timers) shall be parameters, not constants (CMP-009, FW-005).

- **3 dB power offset (B3) — first item to confirm.** The 400G-mode power plan rests on a first-order 3 dB sensitivity allowance for the doubled noise bandwidth. DRX-002 shall report the realized penalty; if the future specification instead holds 200G-mode power levels, LNK-001 margin falls by the realized penalty and TXO-005/007/010, RXO-001/002/003/004/006, LOM-002, and SQL-003 revert to the Table 4-1 200G-mode column.

- **RX damage threshold.** 5 dBm (802.3dj Cl.180 receiver class) gives 2 dB above the 400G-mode Pavg maximum; a 4.5 dB margin (the OCI v1.0 200G-mode relationship) would require 7.5 dBm, above the demonstrated 106.25 GBd PD class. Confirm PD capability and the eventual specification choice.

- **Transition time and RIN.** TXO-008 adopts the 802.3dj Cl.180 8 ps (vs. 8.5 ps by UI scaling of the 200G-mode limit); TXO-009 retains -138 dB/Hz where Cl.180 specifies -139 dB/Hz at the same baud and ORL. Both to be confirmed.

- **PMA lane geometry (B7).** The 2:4 mapping (host stream to adjacent wavelength pair, LSB to shorter wavelength) and the port-level four-channel deskew group are this document’s choices; an interleaved mapping (stream 0 on channels 0/2, stream 1 on 1/3) or a per-host-stream two-channel deskew group are the alternatives. Confirm before RTL freeze of the remap layer (BUP-005).

- **Ring Q feasibility gate (risk R1).** DTX-002/006 and CMP-008 close only if the MRM can deliver 3.5-4.5 dB ER at bounded swing with Q ~2500-4000 at both baud rates; the photonics co-simulation is the gating item for the optical plan.

- **DWDM grid at the 106.25 GBd linewidth.** DTX-003 crosstalk allocation (< 0.5 dB) to be verified; if it fails, a wider grid spacing for 400G mode is the specification-level remedy (affects TXO-002, Band-Mux passbands, ELS wavelength plan, and 200G-mode grid commonality).

- **ELS power headroom (risk R6).** Confirm ELSFP P_ELS_WL covers the 400G-mode launch power plus coupling loss and end-of-life droop; otherwise the power plan or the coupling-loss allocation (DTX-009) must give.

- **Laser safety at 9 dBm/group.** REG-002 Hazard Level 1 analysis at 400G-mode power including single-fault ELS conditions.

- **802.3dj clause chain.** D1.3 is cited; Table 178-6 in D1.3 shows 106.25 GBd for Clause 178 while the inner-FEC PMD classes are expected at 113.4375 GBd in later drafts — citations therefore route through Annex 176C/176D, whose signaling rate is 106.25 +/- 50 ppm GBd in all drafts. Re-check Annex 176C/176D, Cl.180, Table 116-9, and Annex 174A values at each adopted draft and at ratification.

- **OIF CEI-224G-XSR.** Unpublished (CEI-05.3, July 2025, still tops out at 112G-class clauses). When published: cross-check the CDR-001 bandwidth window against its JTOL corner (if f_b/13280 is retained, ~8 MHz at 106.25 GBd) and adopt its die-to-OE TX/RX electrical limits as the baud-matched OIF electrical cross-reference for the Section 6.4 ELE family.

- **Deskew range.** 0-15 UI (B2) assumes the eventual specification preserves the OCI v1.0 absolute skew envelope; if it keeps 0-7 UI at 106.25 GBd, routing and CD skew budgets in ps halve and TXO-012 tightens to < 2 UI (18.8 ps).

- **Chirp x dispersion (DTX-007).** With the dispersion penalty scaling as baud squared, ring chirp is a first-order TDEC term at 106.25 GBd; a chirp limit may need to become an explicit derived requirement.

- **TP1 clock-chain budget (risk R8).** ELE-005 sigma_RJ <= 104 fs rms is the binding kill-or-confirm item of the TP1 budget (DES-OCI-106G-JIT-001 Section 5.1; DES-OCI-106G-CLK-001 Section 3.1); the reference-clock and PLL phase-noise allocation (SYS-002) shall be closed first. Status: first-cut RSS 123 fs (1.5 dB over) with no interpolator in the TX path; 90 fs re-partition proposed (CLK-001 open item 1).

**200G OCI compatibility mode:**

- **Mode provisioning vs. rate detection (CMP-011).** Decide whether the optional dual-rate training-pattern correlation is implemented in first silicon; define the rate-mismatch alarm semantics and host recovery procedure.

- **200G-mode receive bandwidth (CMP-006).** Select the bandwidth-switching mechanism (TIA feedback / CTLE pole programming vs. post-CTLE filtering) and confirm the 200G-mode sensitivity margin by analysis before RTL freeze; a 400G front end run at full bandwidth is unlikely to meet -8.2 dBm without it.

- **Per-mode calibration cost (MFG-003/004).** Size the production-test time for the doubled parameter set; define the minimum 200G-mode production subset that guarantees CMP-002.

- **400G application code (CMP-010).** No CMIS application code exists for an OCI Gen2 medium; a vendor-specific code shall be used and documented until an OCI Gen2 assignment exists. Note: CMIS is an OIF specification and the code assignment process runs through OIF CMIS; the point is that the OCI Gen2 medium type has not yet been registered.

- **SQL-001 re-base.** DES-OCI-106G-SQL-001 was issued against a superseded requirement numbering (SQL-001..012) and 200G-mode values only. Its next revision shall re-base onto SQL-001..005 / LOM-001..004 of this document, and add the 400G-mode column throughout (per-mode drop-port setpoints, rail-polarity analysis at both LOS windows, exit sequencing at both baud rates).

**General:**

- VDM alarm/warning thresholds TBD (MGT-004); agree observables with lead customers.

- Derived numeric allocations (DTX/DRX/SYS) to be populated from analyses DTX-001, DRX-002, DRX-004, SYS-002, and the DTX-009 coupling-loss table.

- D2D interface selection (UCIe/BoW/custom) pending; SYS-004 error-rate and SYS-001 clock-forwarding obligations apply to any choice; D2D bandwidth per port is 425 Gb/s.

- REL-004 FIT allocation, ROB-004 PDN transient mask, EMC-001 chiplet-level emissions limits, MFG-004 production guard-bands await their parent analyses.

- **RX eye budget (risk R10).** No document or Section 6 allocation owns the receiver eye budget. Blocked on it: the CDR-001 jitter-peaking limit (CDR-001 open item 2), the ADP-003 aggregate-dither allocation (ADP-001 open item 2), the RX sampling-chain skew / RJ / interpolator INL / divider terms (CLK-001 open item 6), the RXF-001 Table 8-3 vertical terms, and the EYM-001 extrapolation reference. Decision: issue DES-OCI-106G-REB-001 as the receive-side peer of DES-OCI-106G-JIT-001 (recommended, Table 1-3), or add a Section 6.9 allocation table.

- **Child-issued derived constraints.** JIT-D1 (TP1 overshoot <= 2 %, zeta >= 0.8), JIT-D2 (FIR bank-asymmetry DCD bound), JIT-D3 (DCC +/-0.2 pt target / +/-0.3 pt limit), and JIT-D4 (no phase interpolator in the TX clock path) are binding on DES-OCI-106G-TXD-001 and DES-OCI-106G-CLK-001 but sit outside the FAMILY-NNN scheme of Section 1.6; SQL-001 open item 12 proposes LOM/BUP additions. Decide at the next revision: promote to ELE-011.. / LOM-005.. with the derivation cited, or formally recognise design-document-local IDs in Section 1.6.

- **Planned companion documents.** DES-OCI-106G-REB-001 (RX eye budget), DES-OCI-106G-CHE-001 (channel estimator), DES-OCI-106G-TDC-001 (TX disparity checker), DES-OCI-106G-PHO-001 (photonics), and the logic/system documents of Table 1-3 to be scoped and issued.

- **Sibling reconciliations.** DES-OCI-106G-RXF-001 and DES-OCI-106G-ADP-001: AGC range lower bound (62 vs. 65 dBohm) and gain reference plane (RXF-001 open items 2-3). DES-OCI-106G-CLK-001 and DES-OCI-106G-CDR-001: phase-interpolator topology and code space (CLK-001 open item 5). Recorded here; closed by the owners.

- LOM-002 threshold placement (nominal -9 to -8 dBm OMA-equivalent in 400G mode; -12 to -11 dBm in 200G mode) and LOM-003 persistence window default to be finalized from the channel-loss distribution and AGC settling characterization; the detector observable should be exposed as a debug readback alongside the VDM MPI metric.

- SQL-004 average-power settling tolerance and SQL-003 per-channel rail-polarity table to be populated; two-point drop-port calibration (SQL-002) to be added to the production calibration flow (MFG-003); drop-tap coupling ratio and monitor-diode responsivity tolerances to be budgeted against the MGT-005 +/-2 dB TX-power reporting accuracy.

# 10. Traceability Summary

| **Family (count)** | **Coverage** | **Design decomposition** |
| --- | --- | --- |
| TXO-001..012 (12) | TX optical, TP2, 400G mode - 400G baseline with OCI v1.0 Table 2-2 / Section 1.1 lineage; 802.3dj Cl.180 for transition time, ER min, ppm | DES-OCI-106G-TXD-001 (electrical binding via ELE); DES-OCI-106G-JIT-001 |
| RXO-001..007 (7) | RX optical, TP3, 400G mode - 400G baseline with OCI v1.0 Tables 2-3 / 2-4 lineage; 802.3dj Cl.180 for damage threshold | DES-OCI-106G-RXF-001 (003/004/006) |
| LNK-001..002 (2) | Channel model and ELS - OCI v1.0 Tables 2-5 / 2-6 (both modes) | — |
| CMP-001..012 (12) | 200G OCI compatibility mode and dual-rate provisions - OCI v1.0 Tables 2-2..2-5, Sections 1-3; OIF CEI-112G-XSR (53 GBd class); derived dual-rate parents | All companion documents (per-mode provisions) |
| LOG-001..004 (4) | PMA mapping (2:4 / 1:4), FEC budget, start-up timing - OCI v1.0 Sec.1, 802.3dj Cl.176 / Annex 174A | — (logic document planned) |
| BUP-001..005 (5) | Deskew/bring-up engine internals - OCI v1.0 Sec.1.1 (0-15 / 0-7 UI ranges) | — (logic document planned) |
| WDM-001..005 (5) | Bidirectional WDM and ELS interface - OCI v1.0 Sec.2, Table 2-6 | — (photonics document planned) |
| DFT-001..004 (4) | Built-in test and diagnostics - OCI v1.0 Sec.3, Table 3-2 | DES-OCI-106G-EYM-001 (003/004) |
| MGT-001..006 (6) | Management plane - OCI v1.0 Sec.3-5, Table 4-1; CMIS 5.3 | — |
| DJI-001..005 (5) | 802.3dj upstream integration - Cl.176, Annexes 174A/178B, Table 116-9 | — |
| REG-001..010 (10) | Safety, regulatory, compliance framework - 802.3dj PMD x.10, Cl.45 | — |
| DTX-001..012 (12) | Derived TX decomposition - traced to TXO/LNK/CMP parents | DES-OCI-106G-TXD-001 (006, 010); DES-OCI-106G-SQL-001 (012); DES-OCI-106G-JIT-001 (001); photonics document planned (002..005, 007..009) |
| DRX-001..010 (10) | Derived RX decomposition - traced to RXO/LNK/CMP parents; DRX-006 JTOL from 802.3dj Table 176D-10 | DES-OCI-106G-RXF-001 (001..005); DES-OCI-106G-CDR-001 (006); DES-OCI-106G-EYM-001 (004 confirmation); photonics document planned (007/008) |
| SYS-001..008 (8) | Derived clocking/D2D/system - traced to LOG/DJI/REG/CMP parents | DES-OCI-106G-CLK-001 (001, 002; 003 interface) |
| ELE-001..010 (10) | TP1 transmitter electrical decomposition - 802.3dj 179.9.4.6 via Annex 176C at 106.25 GBd; derived TXO/LOG parents; CEI-112G-XSR cross-check in 200G mode | DES-OCI-106G-JIT-001 (002..005 derivation); DES-OCI-106G-TXD-001 (001..010 implementation); DES-OCI-106G-CLK-001 (003, 007/008) |
| CDR-001..007 (7) | Clock and data recovery behavior - 802.3dj Table 176D-10 / 179.9.4.6; CEI-112G-XSR (200G mode); derived TXO/RXO/BUP/LOG parents | DES-OCI-106G-CDR-001; DES-OCI-106G-CLK-001 Section 9 (phase interpolator) |
| ADP-001..005 (5) | Adaptation and bring-up behavior - derived LOG/RXO/DRX parents | DES-OCI-106G-ADP-001 |
| ROB-001..007 (7) | ESD, latch-up, sequencing, supply, fault, thermal, wearout robustness - JS-001/002, JESD78, derived REG parents | — (interfaces in TXD, RXF, CLK) |
| REL-001..006 (6) | Reliability and environmental qualification - JESD47/22, J-STD-020, GR-468 adapted, derived REG parents | — |
| EMC-001..004 (4) | Emissions, immunity, crosstalk, clock purity - CISPR 32, IEC 61000-4, derived REG-003/RXO-002 parents | — (003/004 inputs in DES-OCI-106G-JIT-001 Section 5.4, DES-OCI-106G-CLK-001 Section 3.4) |
| MFG-001..006 (6) | Manufacturing test, KGD, calibration NVM, screening, traceability - derived VER/DFT/MGT/CMP parents | — (003 calibration interfaces in ADP, EYM, SQL) |
| FW-001..005 (5) | Firmware and management robustness - derived MGT/REG/CMP parents | — |
| LOM-001..004 (4) | Loss-of-modulation detection - derived BUP-004/RXO-006/TXO-010/CDR-006 parents (mode-dependent thresholds) | DES-OCI-106G-SQL-001 Section 6 |
| SQL-001..005 (5) | Squelch implementation decomposition - derived DTX-012/TXO-010/RXO-006 parents (mode-dependent limits) | DES-OCI-106G-SQL-001 |
| Total: 171 requirements | *Full matrix (parent, allocation value, status, operating mode) maintained in the requirements database* | Section 1.7 |

ARCH-OCI-106G-001 Rev 0.7 | DRAFT | Page  of