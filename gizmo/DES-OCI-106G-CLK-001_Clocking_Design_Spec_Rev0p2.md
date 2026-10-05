DES-OCI-106G-CLK-001 Rev 0.2 | Companion to ARCH-OCI-106G-001 Rev 0.7 | CLK Design Specification

**400G OCI Line-Side SerDes Chiplet**

**Clock Generation, Distribution, and Phase Interpolation — Design Specification**

*Companion to ARCH-OCI-106G-001 Rev 0.7 | Design decomposition of SYS-001/002, ELE-005 clock-chain allocation, CDR-001/002/006/007, EMC-004, CMP-005 | Both operating modes (106.25 / 53.125 GBd)*

| Document ID | DES-OCI-106G-CLK-001 |
| --- | --- |
| Revision | 0.2 (Draft for review) |
| Date | September 21, 2026 |
| Status | DRAFT. Design companion to the Architecture and Requirements Specification ARCH-OCI-106G-001 Rev 0.7. Where this document and Rev 0.7 differ, Rev 0.7 governs. Design confidence: Low–Medium. The architecture is fixed — half-rate 53.125 GHz LC-PLL, 8-way interleaved baud/8 sampling clock, CDR-commanded phase interpolator — but most electrical values are CDNS deliverables not yet populated (Section 14). The clock-chain σ_RJ allocation is the binding risk of the program (R8). |
| Parent requirements | SYS-001 (host-derived line clock, dual-rate synthesis chain and frequency plan), SYS-002 (reference and PLL phase-noise budget to σ_RJ ≤ 104 fs rms, refclk specification), SYS-003 (recovered-clock to host-clock crossing, interface only), SYS-007 (bring-up sequence, lock time); ELE-002..005 (TP1 clock-jitter share: JHRMS, EOJ03, JH4u, dual-Dirac σ_RJ / DCD); ELE-007/008 (FIR branch-phase generation, interface to DES-OCI-106G-TXD-001); DTX-001 (TX jitter budget), DTX-010 (PSIJ / PSRR); CDR-001 (loop bandwidth window, PI actuator), CDR-002 (±200 ppm rotation), CDR-004 (no mission-mode slips), CDR-006 (PI code hold), CDR-007 (gear-shift step size); DRX-006 (JTOL mask, both modes); EMC-003 (crosstalk), EMC-004 (no SSC, spur limits at PLL and serializer output); CMP-005 (dual-rate PLL, serializer, CDR), CMP-009 (per-mode parameter sets); DJI-005 (clock switchover rule); TXO-001 (±50 ppm), TXO-012 (channel-to-channel skew); SQL-001 (static-rail park); MFG-003 (PI-linearity calibration in NVM); ROB-004/007; SYS-008 (pJ/bit). Derived constraints consumed from DES-OCI-106G-JIT-001 Rev 0.2 Table 8-2: JIT-D3 (duty-cycle-correction design target ± 0.2 %, limit ± 0.3 %) and JIT-D4 (whether a phase interpolator is in the TX clock path — answered here). |
| Sibling documents | DES-OCI-106G-JIT-001 Rev 0.2 — TX electrical jitter budget at TP1 (owns the σ_RJ, DCD, ISI, and BUJ allocations; its Table 5-1 / 5-1b clock-chain build-up, Table 5-3 / 5-3c DCD model, and Table 5-5 BUJ slew model are the inputs to Section 3, and this document is the closure vehicle for its Open item 1 and its JIT-D3 / JIT-D4 constraints); DES-OCI-106G-TXD-001 — TX pre-driver and driver (consumes the serializer output and the 0 / 1 / 2 UI branch phases; owns the TP1 budget roll-up, Table 3-2 there); DES-OCI-106G-RXF-001 — RX analog front end (its Section 8 slicer front end is clocked by the 8-phase sampling clock defined here); DES-OCI-106G-CDR-001 — baud-rate Mueller–Müller CDR whose phase FSM commands the phase interpolator of Section 9; DES-OCI-106G-ADP-001 — adaptation loops (dither budget); DES-OCI-106G-SQL-001 — squelch (serializer park state); DES-OCI-106G-EYM-001 — RX eye monitor (its horizontal axis is the slaved monitor phase interpolator pi_mon of Section 9.4; it consumes CK_MON, the monitor word alignment, and the coupling limits of Table 9-5). |
| Governing specifications | IEEE Draft P802.3dj/D1.3 179.9.4.6 via Annex 176C/176D — TP1 clock-jitter metrics (JRMS03 / EOJ03 / J4u03; later drafts JHRMS / JH4u) measured with a 4 MHz CRU at 20 dB/decade, and the 106.25 GBd receiver JTOL mask (Table 176D-10); OIF CEI-05.3 Clause 24 (CEI-112G-XSR) — baud-matched 200G-mode jitter and JTOL cross-check (f_CRU ≈ 4.0 MHz at 53.125 GBd); OCI Gen1 Optical PHY Specification v1.0 — Table 1-3 timers (t_lock / t_loselock ≤ 50 ms). Design inputs: DES-OCI-106G-JIT-001 Rev 0.2 (TP1 jitter budget, cited throughout); DES-OCI-106G-CDR-001 (PI parameter set); CDNS “Proposed Interleaved RX Architecture” / “8-Phase S/H Timing” material (2026). |
| Scope | Clock generation and distribution for one channel in both directions: the reference-clock interface from the host clock domain; the 53.125 GHz LC-PLL; the mode divider and half-rate clock distribution with duty-cycle correction; the serializer clock interface (half-rate 2:1 final mux, FIR branch-phase retiming, TX word clock); the RX 8-phase (baud/8) interleaved sampling-clock generator and its phase calibration; the CDR-commanded phase interpolator; the eye-monitor sampling clock (a second, slaved phase interpolator and its clock branch); the recovered word clock and the hand-off to the CDR, deskew, and elastic-FIFO domains; clock purity, supply, and robustness interfaces; dual-rate provisions; verification hooks. Per channel; four instances per fiber port (shared elements identified in Table 2-1). |
| Out of scope | CDR loop algorithm, gains, lock detector, and fixed-point sizing (DES-OCI-106G-CDR-001 — this document only fixes the actuator the loop drives); serializer data path, FIR tap slices, and TP1 electrical limits (DES-OCI-106G-TXD-001); TIA / CTLE / sample-hold / comparator circuits (DES-OCI-106G-RXF-001, Section 8 there); elastic-FIFO depth and deskew engine (SYS-003, BUP family — logic documents); the eye monitor’s vertical axis, monitor slice, comparison logic, registers, and scan procedure (DES-OCI-106G-EYM-001 — this document supplies only its sampling clock); D2D link definition (SYS-004); the host-side reference-clock source (only its required specification is derived here, SYS-002). |

| **Revision** | **Date** | **Change summary** |
| --- | --- | --- |
| 0.1 | September 18, 2026 | Initial issue. Design decomposition of SYS-001/002, the ELE-005 clock-chain allocation, CDR-001/002/006/007, EMC-004, and CMP-005 per ARCH-OCI-106G-001 Rev 0.6, incorporating the clock-chain build-up (100 / 60 / 70 / 40 fs) and half-rate duty-cycle DCD model now owned by DES-OCI-106G-JIT-001, the phase-interpolator parameters of DES-OCI-106G-CDR-001 (5-bit PI, 1.0 UI span, 128-UI update window), and the CDNS interleaved-RX / 8-phase S/H timing material; clocking structured into Sections 4–9 (reference clock; PLL architecture and phase-noise specification; distribution bandwidth, skew, and duty-cycle correction; serializer timing and output-jitter model; PVT sensitivity and tuning ranges); the phase interpolator given a dedicated section (Section 9) with resolution, interpolation interval, rotation continuity, update timing, linearity, hold, and calibration obligations traced to DES-OCI-106G-CDR-001; the RX sampling clock restated as an 8-way interleaved baud/8 eight-phase clock (13.28 GHz in 400G mode, 6.64 GHz in 200G mode) so that no slicer is clocked at the line rate, with the even/odd CTLE split, 4-UI track / 4-UI hold windows, 2-of-4 tracking rule, and 2-UI charge-share settling carried from the timing diagram; 200G OCI mode column added to every frequency, jitter, and timing table (CMP-005); the first-cut clock-chain build-up (RSS 142 fs) restated against the 104 fs ELE-005 allocation with the phase-interpolator bookkeeping (TX chain vs. RX sampling chain) made explicit and the RX sampling-clock jitter routed to the RX eye budget; half-rate duty-cycle DCD carried at 0.006 UI (D = 50 % ± 0.3 pt); spur limit derived from the ELE-004 / BUJ ceiling for EMC-004; the single-“TX/RX PLL” and per-channel-“RX PLL” descriptions reconciled as a shared per-channel PLL baseline with the alternatives listed; ownership placeholders retained as explicit deliverables (Section 14). |
| 0.1 | September 18, 2026 | Reconciliation with DES-OCI-106G-JIT-001 Rev 0.2 (TP1 jitter budget). (1) Section 3.1 re-based on JIT-001 Tables 5-1 / 5-1b: the clock-chain build-up is cited rather than re-derived, and this document answers JIT-D4 — no phase interpolator in the TX clock path (the FIR branch phases are serializer-domain copies, Table 7-1) — so the “No PI in TX path” variant of Table 5-1b applies: first-cut RSS 123 fs, 1.19× (1.5 dB) over the 104 fs allocation; the 72 / 45 / 30 fs working re-partition (90 fs) is offered as the closure of JIT-001 Open item 1. (2) JIT-D3 adopted: DCC design target ± 0.2 pt (0.004 UI) with ± 0.3 pt (0.006 UI) as the limit, carried into Tables 3-3, 6-1, 7-1, 10-1, and 13-1; the DCD partition is fixed per JIT-001 Table 5-3c and Open item 8 narrowed to the DCC loop and monitor. (3) The FIR slice-DCD adder re-labelled bank-asymmetry apparent DCD (JIT-001 Table 5-3b, JIT-D2). (4) Periodic jitter from clock spurs stated as a sub-allocation of the JIT-001 Table 5-5 BUJ ceiling (equivalent aggressor 14 mV of the 51 mV sum at 0.30 V/ps), not a separate term. (5) 200G-mode margins and the ∂TJ/∂σ_RJ = 14.07 sensitivity referenced to JIT-001 Tables 4-2 and 5-7; robustness of the 104 fs requirement to the DJ combination convention (JIT-001 Table 5-8) noted. |
| 0.1 | September 18, 2026 | Eye-monitor sampling clock added for DES-OCI-106G-EYM-001 (RX eye monitor). Block 9 in Table 2-1; CK_MON and CK_WMON in the frequency plan (Table 2-2); partition and architecture-decision rows (Tables 2-3, 2-4); monitor slice and the monitor as skew-calibration observable in Tables 8-1 / 8-2; instrument-error row in Table 8-3; monitor DMUX and word alignment in Table 8-4; new Section 9.4 defining the slaved single-output monitor phase interpolator pi_mon — position law pos_mon = (pos_data + 32 · k_mon + mon_phase_offset) mod 256, 1/32 UI step, ±0.5 UI fine range, slice select, slaved / absolute modes, matched update timing, skew and jitter bounds, hold and idle behaviour (Table 9-4) — and its obligations toward the data path (Table 9-5: ≤ 10 fs pp coupling, static load, word alignment, metastability retiming); power (Table 12-1), verification (Table 13-1), and open-item (17) entries; DFT-003 / MFG-003 rows added to the parent map. |
| 0.2 | September 21, 2026 | Re-pinned to ARCH-OCI-106G-001 Rev 0.7 (hub revision; its Section 1.7 indexes this document). Predecessor-document references removed throughout per the OCI 106G document-structure convention: the Status field now states scope and confidence only; provenance statements are replaced by citations of the owning document in the set or by open items; cross-references into DES-OCI-106G-CDR-001 converted from legacy §6-x numbering to its Section numbers. No technical values changed. |

# 1. Introduction

## 1.1 Purpose

This document is the design decomposition of the clocking obligations of ARCH-OCI-106G-001 Rev 0.7: the frequency plan and dual-rate synthesis chain that SYS-001 asks to be documented, the reference and PLL phase-noise budget that SYS-002 derives from ELE-005 (σ_RJ ≤ 104 fs rms at TP1, allocated to the clock chain by DES-OCI-106G-JIT-001 Rev 0.2 Table 5-1), the clock-purity limits of EMC-004, and the phase-interpolator behaviors that CDR-001/002/006/007 and DES-OCI-106G-CDR-001 assume of their actuator. It partitions the clock chain into blocks with separate specifications — reference-clock interface, LC-PLL, distribution and duty-cycle correction, serializer clock interface, 8-phase interleaved sampling-clock generator, and phase interpolator — fixes which specification lives with which block, allocates the clock-chain jitter terms of the TP1 budget and of the RX eye budget, and states the per-mode values so that circuit design, the CDR RTL, the slicer front end, firmware, and verification share one definition.

This document is organised around four clocking subsystems (reference, PLL, distribution, serializer / sampling clocks) plus the phase interpolator. It fixes the parameters that are already fixed by the parent requirements or by the sibling design documents, and structures the remaining values as explicit owner deliverables rather than leaving them as prose TBDs.

## 1.2 Conventions

| **Item** | **Convention** |
| --- | --- |
| Operating modes | 400G OCI mode: 106.25 GBd NRZ, UI = 9.412 ps, half-rate clock 53.125 GHz. 200G OCI mode: 53.125 GBd NRZ, UI = 18.824 ps, half-rate clock 26.5625 GHz. Limits stated in UI apply in both modes; absolute values are given per mode. Jitter and skew are hardware properties fixed in femtoseconds, and are therefore a smaller UI fraction in 200G mode; the VCO frequency is the same in both modes (Section 5). |
| Requirement references | FAMILY-NNN refers to the requirement of that ID in Rev 0.7; §x.y without prefix refers to Rev 0.7. “DES-OCI-106G-CDR-001 Section x.y” refers to that document’s own section numbering. |
| Clock reference planes | f_ref — reference clock at the PLL input. CK_VCO — PLL output. CK_HR — half-rate line clock after the mode divider, at the serializer final mux (period = 2 UI in both modes). CK8[7:0] — 8-phase sampling clock at baud/8, phase spacing 1 UI. CK8_PI[7:0] — the same set after phase interpolation, at the sample/hold switches. CK_WTX / CK_WRX — TX and recovered RX word clocks. Serializer output — the plane at which EMC-004 spur compliance and the ELE clock-jitter metrics are simulated (TP1 itself is buried, ELE-001). |
| Owners | CDNS — clocking (PLL, distribution, serializer clock interface, 8-phase generator, PI, monitors) and the CDNS EIC slice front end; LM — PIC, TIA / LM-EIC CTLE, driver, and the TP1 roll-up. An entry marked “CDNS” in a Target column is a value that owner shall supply; it is tracked in Section 14. |
| Jitter conventions | σ_t = φ_rms / (2π f_clk) with f_clk the clock at which the phase noise is stated (1 fs ↔ 0.0191° at 53.125 GHz; 0.0096° at 26.5625 GHz). Random terms integrate single-sideband phase noise from 4 MHz (first-order CRU / CDR high-pass at 20 dB/decade, the 802.3dj 179.9.4.6 convention) to f_baud/2 and add in RSS; bounded terms add worst-case (ELE-005). Peak-to-peak terms at BER 1e-12 use Q = 7.034; at the 2.4E-4 compliance point Q = 3.49. |
| Phase noise | L(f) in dBc/Hz, single-sideband, referred to the carrier named in the table. A ÷2 lowers L(f) by 6 dB for the same time jitter; a ×N multiplication raises in-band L(f) by 20·log10(N). |
| Phase and skew | Static phase error is stated peak-to-peak against the ideal 1-UI grid after calibration; 1 PI code = 1/32 UI = 0.031 UI. |
| Placeholders | TBD = value tracked in the requirements database; not yet fixed by analysis or by the owner. “Working target” = a value proposed here for closure and not yet committed by the owner. Section 14 lists the open items and owner deliverables. |

## 1.3 Parent requirement map

**Table 1-1. Rev 0.7 requirements satisfied or interfaced by this document**

| **Req ID** | **Rev 0.7 obligation (abridged)** | **Design response** | **Section** |
| --- | --- | --- | --- |
| SYS-001 | Line clock derived from the host PCS domain over D2D (±50 ppm); dual-rate synthesis chain (full- or half-rate) and frequency plan documented. | Half-rate architecture fixed; frequency plan Table 2-2; reference-clock interface Table 4-1; mode divider Table 5-1. | 2.3, 4, 5 |
| SYS-002 | Reference and TX PLL phase-noise budgets allocated from DTX-001 / ELE-005 (σ_RJ ≤ 104 fs rms) over the CDR-tracked band; refclk specification derived. | Clock-chain allocation Table 3-1 (re-partition of JIT-001 Table 5-1, closing JIT-001 Open item 1); integration convention Table 3-2; PLL masks Table 5-2; refclk phase-noise derivation Table 4-1. | 3, 4, 5 |
| SYS-003 | Elastic FIFOs at the recovered-clock / host-clock crossing sized for ±100 ppm. | Interface only: recovered word clock definition and ppm relations Table 8-4; sizing is a logic deliverable. | 8.5 |
| SYS-007 | End-to-end bring-up sequence with bounded time-to-traffic, both modes. | PLL lock time, coarse calibration, phase and PI calibration steps as entries of the sequence (Tables 5-3, 8-2, 9-3, 10-2). | 5, 8, 9, 10 |
| ELE-002 / 003 / 004 | TP1 JRMS ≤ 0.023 UI rms; EOJ ≤ 0.025 UI pp; J4u ≤ 0.118 UI pp. | Clock-only cross-checks in Table 3-2; DCD share of EOJ in Table 3-3; spur (PJ) share of J4u in Table 3-4. | 3 |
| ELE-005 | Dual-Dirac budget at 1e-12: σ_RJ ≤ 104 fs; DCD ≤ 235 fs; BUJ ≤ 339 fs. | σ_RJ allocated across PLL, distribution, serializer in Table 3-1 (PI bookkeeping per JIT-001 Table 5-1b); DCD duty-cycle share 0.006 UI limit / 0.004 UI target (JIT-D3); PJ inside BUJ (JIT-001 Table 5-5). | 3 |
| ELE-007 / 008, CMP-007 | 3-tap FIR with 0 / 1 / 2 UI branch delays tracking the baud; inter-tap matching ≤ 2.6 % UI (0.24 ps). | Branch phases generated as half-rate-clock retimed copies (baud tracking inherent); skew returned to TXD Table 6-3. | 7 |
| DTX-001 | TX jitter budget decomposed across SerDes TX RJ, PLL phase noise, driver DJ. | PLL and distribution RJ are the clock-chain rows of that budget (Table 3-1). | 3 |
| DTX-010 | PSIJ within TDEC allocation; PSRR per rail over the signal bandwidth. | Supply interface and PSRR obligations for the PLL, distribution, and PI rails (Tables 5-4, 11-1). | 5.4, 11 |
| CDR-001 | Closed-loop bandwidth 4–6 MHz in both modes; heavily damped mission gains; low jitter peaking. | PI update rate, code-step capability, and code-to-phase latency fixed so the loop of CDR-001 doc can meet the window (Table 9-1); per-mode gain note (Table 10-1). | 9, 10 |
| CDR-002 | Acquire and track ±200 ppm; frequency register saturates with ≥ 20 % margin. | PI rotation continuous over ≥ ±244 ppm without bit slip (Tables 9-1, 9-2). | 9 |
| CDR-004 | No mission-mode cycle slips; bursts > 7 symbols < 1E-20. | Glitch-free code changes and seamless wrap (no duplicated or missed sampling edge) are PI obligations (Table 9-1). | 9 |
| CDR-006 | On invalid signal hold PI code, phase accumulator, frequency register; warm re-acquisition. | PI phase hold with bounded drift over the hold interval (Table 9-1). | 9 |
| CDR-007 | Acquisition / mission gain sets; gear-shift transition without loss of lock. | PI maximum code step per update covers the acquisition gear (Table 9-1). | 9 |
| DRX-006, CMP-005 | JTOL mask 5 UI at 40 kHz … 0.05 UI at ≥ 4 MHz at both bauds; PLL, serializer, CDR operate at both bauds. | Dual-rate frequency plan (Table 2-2); untracked-SJ term carried in the RX timing budget (Table 8-3); mode-change sequence (Table 10-2). | 2.3, 8.4, 10 |
| EMC-003 | Aggregate crosstalk within BUJ ≤ 339 fs and the RX eye budget. | 53 GHz and 13 GHz clock nets as aggressors: isolation obligations (Table 11-1); PJ allocation shared with crosstalk (Table 3-4). | 3.4, 11 |
| EMC-004 | No spread-spectrum; spur limits from the ELE-004 ceiling at each baud; verified at PLL and serializer output across PVT in both modes. | Spur limit ≤ −42 dBc (power sum, offsets > 4 MHz) for PJ ≤ 0.010 UI pp (Table 3-4); integer-N PLL (Table 5-1); verification Table 13-1. | 3.4, 5, 13 |
| CMP-009 | Per-mode parameter sets reloaded before port enable. | Per-mode PI LUT, phase-calibration set, DCC target, divider setting (Table 10-1). | 10 |
| DJI-005 | TX clock transitions from local to recovered clock only while RTS is false. | No clock switchover exists: the TX line clock is always host-derived; satisfied by construction (Table 7-1). | 7 |
| TXO-001, TXO-012 | ±50 ppm signaling rate; channel-to-channel TX skew < 4 UI (37.6 ps) per end. | Frequency inherits the host-derived f_ref; clock-chain share of inter-channel skew ≤ 1 UI working target (Table 6-1). | 4, 6 |
| SQL-001 | Static-rail serializer park; full-swing toggling prohibited. | Clocks keep running during park; the serializer output holds a legal static state (Table 7-1). | 7 |
| MFG-003 | PI linearity and per-mode parameter sets stored in NVM with integrity protection. | PI and 8-phase calibration storage (Tables 8-2, 9-3). | 8, 9 |
| DFT-003, MFG-003 (eye monitor) | Slicer-margin-derived MPI metric; monitor calibrations stored in NVM with integrity protection. | Eye-monitor sampling clock CK_MON from the slaved rotator pi_mon (Section 9.4); phase_zero_mon calibration per slice and per mode stored with the clocking parameter set. | 9.4 |
| SYS-008 | pJ/bit power target per mode. | Clocking power tally (Table 12-1). | 12 |
| JIT-D3 / JIT-D4 (DES-OCI-106G-JIT-001 Rev 0.2 Table 8-2) | Derived constraints handed to the clock chain: DCC design target ± 0.2 % with ± 0.3 % as the limit; tap-delay generation shall state whether a phase interpolator is in the TX clock path (if so, its DNL is booked in DJ_δδ, not in σ_RJ). | JIT-D3 adopted (Tables 3-3, 6-1, 7-1, 13-1). JIT-D4 answered: no PI in the TX path — branch phases are serializer-domain copies (Table 7-1) — so JIT-001 Table 5-1b variant “No PI in TX path” governs Table 3-1. | 3, 6, 7 |

# 2. Architecture and Partition

## 2.1 Clock signal chain

One clock chain per channel serves both directions: the LC-PLL produces the half-rate clock, which the serializer uses directly and which the RX divides into eight sampling phases that the CDR rotates through the phase interpolator. Nomenclature is fixed in Table 2-1 and used throughout the sibling documents; Figure 2-1 (Section 2.2) draws the chain.

**Table 2-1. Blocks of the clock chain (per channel unless stated)**

| **#** | **Block** | **Function** | **Owner** | **Output interface** | **Governing requirements** |
| --- | --- | --- | --- | --- | --- |
| 1 | Reference-clock interface | Receives the forwarded / derived host-domain clock f_ref over the D2D interface; activity monitor; may be shared by the four channels of a port. | CDNS / D2D | f_ref to the PLL | SYS-001, SYS-002, EMC-004, REG-007 |
| 2 | LC-PLL | Integer-N frequency synthesis to CK_VCO = 53.125 GHz in both modes; lock detector; coarse tuning calibration. | CDNS | CK_VCO differential | SYS-001/002, EMC-004, DTX-010, CMP-005 (Section 5) |
| 3 | Mode divider and half-rate distribution | ÷1 (400G) / ÷2 (200G) to CK_HR; low-jitter buffering to the serializer and to the 8-phase generator; duty-cycle correction (DCC) at the serializer. | CDNS | CK_HR to blocks 4 and 5 | ELE-003/005, CMP-005 (Section 6) |
| 4 | Serializer clock interface | Half-rate 2:1 final mux clock; retimed 0 / 1 / 2 UI branch-phase copies for the driver FIR; ÷64 TX word clock; legal static park state. | CDNS | Full-rate NRZ and branch phases into the pre-driver (TXD Table 2-1 #2); CK_WTX to TX digital | ELE-002..005, ELE-007/008, CMP-007, SQL-001, DJI-005 (Section 7) |
| 5 | 8-phase sampling-clock generator | CK_HR ÷ 4 with I/Q cascade → eight phases at baud/8 spaced 1 UI, 50 % duty; per-phase static-skew calibration. | CDNS | CK8[7:0] | CDR-001, DRX-006, RXF §8 (Section 8) |
| 6 | Phase interpolator (rotator) | Rotates the whole CK8 set by the CDR code in 1/32 UI steps, continuously and glitch-free; holds on signal-invalid. | CDNS | CK8_PI[7:0] to the S/H switches and comparators | CDR-001/002/004/006/007, MFG-003 (Section 9) |
| 7 | Slice clocking, DMUX, recovered word clock | Slice clock buffers; 1:16 deserialization per slice; CK_WRX = CK8_PI[0] ÷ 16 as the recovered domain; 128-UI window boundary to the CDR. | CDNS | d / e words at CK_WRX to the CDR and deskew phase FIFOs | DES-OCI-106G-CDR-001 Section 5, SYS-003, BUP-002 (Section 8.5) |
| 8 | Monitors | PLL lock detect, refclk loss, DCC readback, phase-calibration and PI-calibration readback, on-die jitter / phase monitor. The RX eye monitor is a separate instrument (DES-OCI-106G-EYM-001) whose sampling clock is block 9. | CDNS / DFT | Management registers, flight data recorder | SYS-007, REG-007, MGT-003, DFT (Section 13) |
| 9 | Eye-monitor sampling clock (monitor PI) | Second, single-output phase rotator pi_mon slaved to the data-path position: CK_MON = data sample phase + slice select k_mon (integer UI) + fine offset ±16 codes (±0.5 UI). Clocks the monitor slice (S/H + comparator) and its 1:16 DMUX, word-aligned to the selected mission slice; keeps running at a parked position when the monitor is idle. | CDNS | CK_MON to the monitor slice (EYM Table 2-2); m-word at CK_WRX to EyeMonNrz | DFT-003, MFG-003, CDR-002/006, DES-OCI-106G-EYM-001 (Section 9.4) |

## 2.2 Block diagram

**Figure 2-1. Clock distribution block diagram**

*\[FIGURE PLACEHOLDER — insert block diagram here. Suggested content: the full clock tree of one channel, blocks numbered with the Table 2-1 rows, every clock arrow labelled with its symbol and both-mode frequency from Table 2-2 (frequency plan). Left to right: host / D2D domain → reference-clock interface (#1; f_ref, forwarded / derived host-domain clock, ±50 ppm; activity monitor; may be shared by the four channels of a port) → LC-PLL (#2; integer-N; CK_VCO = 53.125 GHz differential in both modes; lock detector; coarse-tuning calibration) → mode divider and half-rate distribution (#3; ÷1 in 400G mode / ÷2 in 200G mode → CK_HR = 53.125 / 26.5625 GHz, period 2 UI; low-jitter buffers). From #3 two branches. TX branch: duty-cycle correction (DCC) at the serializer → serializer clock interface (#4; CK_HR clocks the half-rate 2:1 final mux — the full-rate NRZ exists only at the mux output, there is no 106.25 GHz clock anywhere in the design; retimed 0 / 1 / 2 UI branch-phase copies into the pre-driver FIR, DES-OCI-106G-TXD-001 Table 2-1 #2; ÷64 → CK_WTX = 830.078 / 415.04 MHz to TX digital; legal static park state). RX branch: 8-phase sampling-clock generator (#5; CK_HR ÷ 4 as cascaded I/Q ÷2, both polarities → CK8\[7:0\] = 13.28125 / 6.640625 GHz, phases 1 UI apart, 50 % duty; per-phase static-skew calibration DACs) → phase interpolator / rotator (#6; rotates the whole CK8 set by the CDR code in 1/32 UI steps = 294 fs / 588 fs, glitch-free; holds on signal-invalid → CK8_PI\[7:0\]) → slice clocking, DMUX and recovered word clock (#7; buffers to the eight S/H switches, the 24 comparators and the DMUX first stages; 1:16 deserialization; CK_WRX = CK8_PI\[0\] ÷ 16 = 830.078 MHz × (1 + Δf) → d / e words to the CDR loop filter and the deskew phase FIFOs) and, in parallel, the monitor PI pi_mon (#9; fed from the calibrated CK8 set and slaved to the data-path position + 32 · k_mon + mon_phase_offset → CK_MON to the eye-monitor slice and its 1:16 DMUX → CK_WMON; DES-OCI-106G-EYM-001 Table 2-2). Monitors (#8; PLL lock, refclk loss, DCC readback, phase- and PI-calibration readback, jitter / phase monitor) → management registers and flight data recorder. Control inputs, entering from above: mode select (400G / 200G OCI; CMP-005, Section 10) → the ÷1 / ÷2 mode divider of #3 and the PI step (294 → 588 fs) — the VCO frequency and the ÷4 of #5 do not change; pi_code from the CDR phase FSM at CK_WRX (DES-OCI-106G-CDR-001) → #6; signal_valid hold → #6; k_mon and mon_phase_offset → #9; phase-calibration codes (MFG-003 NVM) → #5; the DCC loop around the serializer mux. Domain boundaries to mark: host / D2D domain (f_ref) → PLL and CK_HR domain (one LC-PLL per channel as the baseline, shared between the channel’s TX serializer and its RX 8-phase generator; PLL-instance alternatives per Table 2-4) → per-channel TX distribution (CDNS) and per-channel RX distribution (CDNS) → recovered domain CK_WRX (the only clock at the far-end rate) → host domain via the elastic FIFO (SYS-003; out of scope). Clock arrows solid, control arrows dashed.\]*

## 2.3 Frequency plan (SYS-001)

Table 2-2 is the frequency plan SYS-001 asks to be documented. The architecture is half-rate: no 106.25 GHz clock exists anywhere in the design. The VCO frequency is identical in both modes; the mode divider is the only element that changes.

**Table 2-2. Clock frequency plan per operating mode**

| **Clock** | **Symbol** | **400G OCI mode** | **200G OCI mode** | **Derivation** | **Consumers** |
| --- | --- | --- | --- | --- | --- |
| Reference clock | f_ref | TBD — candidates 830.078 MHz (f_baud/128), 1660.16 MHz (f_baud/64), 3320.31 MHz (f_baud/32) | Same absolute f_ref (host domain unchanged) | Forwarded / derived from the host PCS domain over D2D (Table 4-1) | PLL |
| VCO / PLL output | CK_VCO | 53.125 GHz | 53.125 GHz (unchanged) | f_ref × N, N integer (N = 64 at 830.078 MHz) | Mode divider |
| Half-rate line clock | CK_HR | 53.125 GHz; period 18.824 ps = 2 UI | 26.5625 GHz; period 37.647 ps = 2 UI | CK_VCO ÷ 1 or ÷ 2 | Serializer 2:1 mux, branch retiming, DCC, 8-phase generator, TX word-clock divider |
| 8-phase sampling clock | CK8[7:0] | 13.28125 GHz; period 75.29 ps = 8 UI; phases 45° = 9.412 ps apart; 50 % duty | 6.640625 GHz; period 150.59 ps = 8 UI; phases 18.824 ps apart | CK_HR ÷ 4 (cascaded I/Q ÷2, both polarities) | PI |
| Interpolated sampling phases | CK8_PI[7:0] | As CK8, rotated by the CDR code in 294 fs steps | As CK8, 588 fs steps | Section 9 | S/H switches, 24 comparators, DMUX first stage |
| Eye-monitor sampling clock | CK_MON | 13.28125 GHz, single phase; position (pos_data + 32 · k_mon + mon_phase_offset) mod 256 in 294 fs steps | 6.640625 GHz, 588 fs steps | Second rotator pi_mon from CK8[7:0], slaved to the data position (Section 9.4) | Monitor S/H switch, monitor comparator, monitor DMUX (DES-OCI-106G-EYM-001) |
| Recovered RX word clock | CK_WRX | 830.078 MHz × (1 + far-end offset), W_rx = 128 | 415.04 MHz (W_rx = 128, baseline) or 830 MHz (W_rx = 64, Open item 7) | CK8_PI[0] ÷ 16 (÷ 8 for W_rx = 64) | DMUX output, CDR loop filter (one dump per cycle), deskew phase-FIFO write side |
| Monitor word clock | CK_WMON | 830.078 MHz × (1 + far-end offset) = CK_MON ÷ 16; word boundary aligned to the CK_WRX word of slice k_mon | 415.04 MHz (or 830 MHz) | CK_MON ÷ 16 (÷ 8 for W_rx = 64); re-aligned on every change of k_mon | Monitor DMUX output into EyeMonNrz, which runs at CK_WRX (Table 8-4) |
| TX word clock | CK_WTX | 830.078 MHz (W_tx = 128) | 415.04 MHz | CK_HR ÷ 64 | TX digital, PMA, serializer input stage |
| CDR update rate | f_upd | 830.078 MHz (one dump per 128 UI) | 415.04 MHz (or 830 MHz with W_rx = 64) | = CK_WRX | Loop filter, phase FSM, PI code |
| Host / D2D clock | — | Host domain, ±50 ppm | Host domain | Out of scope (SYS-003/004) | Elastic-FIFO read side |

## 2.4 Partition of specifications

**Table 2-3. Where each specification lives**

| **Specification** | **Lives with** | **Rationale** |
| --- | --- | --- |
| PLL phase-noise mask, tuning range, lock time, reference spurs | LC-PLL (Section 5) | The PLL is the dominant σ_RJ contributor and the only spur source besides the reference. |
| Clock-chain σ_RJ (TP1 share) | Allocated across PLL, distribution, serializer (Table 3-1); roll-up in TXD Table 3-2 | TP1 totals are ELE-002..005; each block receives an allocation from the link budget. |
| Duty-cycle distortion of the half-rate clock | Distribution / DCC (Section 6), measured at the serializer final mux | DCD_duty = │2D − 1│ · UI is a clocking term; driver rise/fall mismatch is the TXD term of the same 0.025 UI ceiling. |
| FIR branch delays 0 / 1 / 2 UI | Serializer clock interface (generation, Section 7); TXD (matching at TP1) | Phases are created in the half-rate clock domain; the ELE-008 0.24 ps limit is measured at TP1. |
| 8-phase static skew and duty cycle | 8-phase generator and calibration (Section 8) | Per-slice sampling-instant error; a horizontal term of the RX eye budget (RXF Table 8-3). |
| PI resolution, interpolation interval, rotation continuity, linearity, update timing, hold | PI (Section 9), hardware; DES-OCI-106G-CDR-001 for code space and gains | The PI is the loop actuator; its code space and update cadence are fixed jointly with the CDR RTL. |
| CDR closed-loop bandwidth, damping, lock detector, frequency register | DES-OCI-106G-CDR-001 | This document supplies the actuator properties (step, latency, range) the loop needs. |
| Spurs, SSC prohibition | PLL and reference (Section 5), verified at the serializer output | EMC-004 names both planes. |
| Recovered-clock to host-clock crossing, deskew phase FIFOs | Logic documents (SYS-003, BUP-002); clock definitions here (Table 8-4) | Depth and skew-variation budgets are logic obligations; the ppm relations come from the clock plan. |
| Eye-monitor horizontal axis: monitor sampling phase (position law, step, offset range, slaving), skew to the data phase, instrument jitter, coupling into the data path, word alignment | Monitor PI (Section 9.4, Tables 9-4 / 9-5); DES-OCI-106G-EYM-001 for the vertical axis, monitor slice, comparison logic, registers, scan procedure, and calibration | pi_mon is a clocking block slaved to the data PI; the eye monitor consumes its phase as the horizontal axis of the 2D scan. |
| Power and area | Each block separately (Section 12) | PLL power does not scale with baud; buffer power partly does. |

## 2.5 Architecture decisions

**Table 2-4. Clocking architecture decisions and their consequences**

| **Attribute** | **Decision** | **Rationale / consequence** | **Req / status** |
| --- | --- | --- | --- |
| TX clocking rate | Half-rate: 53.125 GHz LC-PLL, final 2:1 mux clocked by CK_HR | No full-rate clock at 106.25 GHz; both clock edges define alternate bits, so duty-cycle error becomes even/odd (DCD) jitter — a DCC loop and a 0.006 UI allocation are required (Table 3-3). | SYS-001 (documented here) |
| Dual-rate method | VCO fixed at 53.125 GHz in both modes; ÷2 after the PLL in 200G mode | One tank, one tuning range, one phase-noise mask; time jitter unchanged, UI-relative jitter halves in 200G mode. Alternative — retuning the VCO to 26.5625 GHz — doubles the tuning range or needs a second tank and is rejected pending Open item 3. | CMP-005 |
| RX sampling architecture | 8-way interleaved sample/hold + comparator slices at baud/8 (13.28 / 6.64 GHz) | From the CDNS interleaved-RX proposal: S/H interleaving reduces CTLE loading, mitigates sampling-aperture ISI, and lets each comparator run at a noise-optimised speed; no circuit in the receiver is clocked at the line rate. Consequence: an 8-phase clock with per-phase skew calibration and a PI that rotates all eight phases together. | DRX-004, RXF §8 |
| Even / odd split | φ0/2/4/6 drive four slices from the CTLE-even buffer; φ1/3/5/7 four slices from the CTLE-odd buffer; two of four tracking at any time | Extends the front-end bandwidth and reduces charge-sharing ISI; each buffer sees two sampling capacitors at a time. | RXF Table 8-1 |
| Phase-detector clocking | Baud-rate Mueller–Müller: data-phase clocks only, no edge clock | Only the error comparator is needed; halves the clock count and power relative to an edge-sampled CDR. | DES-OCI-106G-CDR-001 Section 4 |
| Phase interpolator topology | Baseline: phase rotator interpolating between adjacent CK8 phases (1 UI interval) with seamless rotation over the 8-UI period; alternative: 1-UI DLL delay element (Option B, Table 9-2) | Seamless wrap is required so that the ±200 ppm tracking never shifts the slice-to-bit assignment (no bit slip, CDR-004). The 1.0 UI PI span of DES-OCI-106G-CDR-001 Section 3.1 is preserved as the interpolation interval. Selection is Open item 5 (Table 9-2). | CDR-002/004 |
| PLL instances | Baseline: one LC-PLL per channel, shared between the channel’s serializer and its 8-phase generator | A single shared “TX/RX PLL” per channel is the baseline; the RX architecture power estimate budgets an RX PLL per channel (60 mW). Alternatives: separate TX and RX PLLs per channel; one TX PLL per port with a 53 GHz distribution tree across four channels. Open item 4. | SYS-001, SYS-008 |
| Reference-clock frequency | TBD; integer-N with N ≤ 64 preferred | In-band PLL noise = reference noise + 20·log10(N): N = 64 (830 MHz) costs 36 dB, N = 340 (156.25 MHz) 51 dB. Open item 2. | SYS-002 |
| TX clock source | Host-derived always; no local / recovered switchover | DJI-005 satisfied by construction; the recovered clock exists only in the RX domain. | DJI-005, SYS-001 |
| Digital update domain | Word width 128 → ≈ 830 MHz word clocks (400G mode) | Keeps the CDR loop filter, phase FSM, and TX digital below 1 GHz (DES-OCI-106G-CDR-001 Section 5). | — |
| Eye-monitor clocking | Dedicated single-output rotator pi_mon fed from the calibrated CK8 set and slaved to the data-path position plus slice select and fine offset; one monitor slice (S/H + comparator) at baud/8 | The monitor point must hold a fixed horizontal displacement from the eye centre while the CDR rotates at up to ±244 ppm, so its phase is derived from the data position rather than free-running. A single monitor slice keeps the CTLE load static (replica buffer, EYM Table 5-1) and observes one UI in eight; slice select pairs it with any mission slice, which also makes it the observable for the Table 8-2 skew calibration. Alternatives (monitor comparator per slice; monitor S/H on a mission buffer) are EYM Table 2-4. | DES-OCI-106G-EYM-001; DFT-003 |

# 3. Clock-Chain Jitter Budget (SYS-002, ELE-005, DTX-001)

The TP1 dual-Dirac budget is owned by DES-OCI-106G-JIT-001 Rev 0.2. This section decomposes its clock-chain terms into block allocations: σ_RJ (JIT-001 Tables 5-1 / 5-1b / 5-2), the duty-cycle share of DCD (Tables 5-3 / 5-3c), and periodic jitter carried inside BUJ (Table 5-5). The random-jitter allocation σ_RJ ≤ 0.011 UI rms (104 fs at 9.412 ps) is set by the JH4u ceiling through the tougher-spec rule, not by the chain build-up, and is the binding kill-or-confirm item of the program (risk R8); JIT-001 Table 5-8 shows it is robust to the bounded-term combination convention (104–114 fs whichever is adopted), so the clock chain must improve rather than the budget relax. Its sensitivity is ∂TJ/∂σ_RJ = 2Q = 14.07 at 1e-12 (JIT-001 Table 5-7): every 10 fs rms of clock jitter costs 141 fs of eye, whereas bounded terms trade 1:1, so clock-chain phase noise is where design effort buys the most margin.

## 3.1 Random-jitter allocation

JIT-001 Table 5-1 carries the first-cut four-term build-up — PLL 100, distribution 60, phase interpolator 70, serializer 40 fs → 142 fs RSS, 1.37× (2.7 dB) over the allocation — and its Table 5-1b evaluates three variants according to whether a phase interpolator is in the TX clock path, deferring the decision to TXD Table 6-3 as constraint JIT-D4. This document supplies that decision: the FIR branch phases are serializer-domain copies of the NRZ stream (Table 7-1) and the only phase interpolator in the design is the RX CDR actuator of Section 9, whose jitter appears at the receiver sampling instant and in the RX eye budget (Table 8-3), not at TP1. The “No PI in TX path” variant of JIT-001 Table 5-1b therefore governs: first-cut RSS 123 fs, 1.19× (1.5 dB) over 104 fs. The gap is narrower than the 2.7 dB of the with-PI variant but does not close by bookkeeping alone, so a re-partition is still required; the working targets below (72 / 45 / 30 fs → 90 fs, one closing example, 13 % inside) are CDNS deliverables and are offered as the closure of JIT-001 Open item 1. Should CDNS instead implement the branch phases with a PI-class delay element, the “PI present, DNL reclassified” variant applies (130 fs, PI DNL booked in DJ_δδ) and Table 3-1 shall be re-issued.

**Table 3-1. Clock-chain σ_RJ allocation (fs rms, integrated 4 MHz – f_baud/2; hardware values hold in both modes)**

| **Contributor** | **First cut (JIT-001 Table 5-1)** | **Working target** | **Basis / constraint** | **Section / Req** |
| --- | --- | --- | --- | --- |
| LC-PLL | 100 | 72 | State-of-the-art 53.125 GHz LC-PLL class; masks A / B of Table 5-2 integrate to ≈ 100 / ≈ 68 fs | 5; SYS-002 |
| Clock distribution buffers (incl. mode divider, DCC path) | 60 | 45 | Supply-noise limited; PSRR per Table 11-1 | 6; DTX-010 |
| Serializer / final 2:1 mux | 40 | 30 | Mux and last retiming stage | 7; ELE-005 |
| RSS — TP1 chain (PLL + distribution + serializer) | 123 | 90 | JIT-001 Table 5-1b variant “No PI in TX path” (JIT-D4 answered, Table 7-1). Against ≤ 104 fs (ELE-005): first cut 1.19× (1.5 dB) over; working target 13 % inside. Roll-up returned to TXD Table 3-2 “PLL / serializer” column and to JIT-001 Table 5-1 | 3; ELE-005, DTX-001 |
| Phase interpolator (DNL + intrinsic) | 70 | 50 | RX sampling path only (Section 9) — carried in the first-cut TP1 build-up of JIT-001 Table 5-1; here routed to the RX eye budget, Table 8-3 | 9; CDR-001 |
| RSS — incl. PI (JIT-001 “with PI” variant) | 142 | 103 | JIT-001 Table 5-1: 1.37× (2.7 dB) over 104 fs; the 72 / 45 / 50 / 30 fs re-partition example there closes at 103 fs. Shown for traceability only — not the TP1 chain of this design. Intermediate variant “PI present, DNL reclassified”: 130 fs (1.9 dB) | JIT-001 Table 5-1b |
| RSS — RX sampling-clock chain (PLL + distribution + ÷4 + PI) | — | ≈ 99 + divider term (TBD) | Term of the RX eye budget (Table 8-3); 2Qσ = 0.15 UI pp at 1e-12 for 100 fs | 8.4; RX eye budget |
| Allocation per mode | — | — | 104 fs = 0.011 UI (400G); 207 fs = 0.011 UI (200G). The hardware value is fixed in fs, so 200G mode has ≈ 2× UI margin (0.0055 UI at 104 fs, JIT-001 Table 4-2) | CMP-007 |

*First-cut and working-target values marked here are not owner commitments; the re-partition that closes at ≤ 104 fs is Open item 1 (JIT-001 Open item 1). Cross-check: JHRMS ≤ 0.023 UI rms (216 fs) is the clock-only standards analog — the allocation is 52 % inside it (JIT-001 Table 6-1). The tougher-spec rule that sizes the allocation, σ_RJ ≤ (0.118 − 0.036) / (2 × 3.719) = 0.011 UI, is JIT-001 Table 5-2 and is not re-derived here.*

## 3.2 Integration band and conversion

**Table 3-2. Phase-noise integration and jitter conventions**

| **Item** | **400G OCI mode** | **200G OCI mode** | **Notes / Req** |
| --- | --- | --- | --- |
| Integration band | 4 MHz – 53.125 GHz | 4 MHz – 26.5625 GHz | Lower bound: CRU / CDR high-pass removes tracked low-frequency jitter (179.9.4.6, CDR-001 window 4–6 MHz); upper bound f_baud/2 |
| High-pass weighting | │H(f)│² = f² / (f² + f_c²), f_c = 4 MHz | Same shape (CEI-112G-XSR corner ≈ 4.0 MHz at 53.125 GBd) | First-order, 20 dB/decade (ELE-002); noise below 4 MHz is attenuated, not excluded |
| Conversion | σ_t = φ_rms / (2π · 53.125 GHz); 1 fs ↔ 0.0191° ↔ 3.34 × 10⁻⁴ rad | σ_t = φ_rms / (2π · 26.5625 GHz); 1 fs ↔ 0.0096° | Phase noise of the ÷2 output is 6 dB lower for the same time jitter |
| 104 fs in phase units | 1.99° rms; 0.0347 rad; −29.2 dBc integrated | 0.99° rms at 26.5625 GHz | ELE-005 |
| Summation | Gaussian RSS; bounded worst-case-additive | Same | ELE-005 sign-off convention |
| Eye sensitivity | ∂TJ/∂σ_RJ = 2Q(1e-12) = 14.07 | Same in UI | 10 fs rms → 141 fs of eye at 1e-12 (JIT-001 Table 5-7) |
| Clock-only cross-checks | JHRMS ≤ 216 fs rms; JH4u = BUJ + 2Q(1e-4)·σ_RJ = 0.036 + 0.082 = 0.118 UI | JRMS ≤ 433 fs; J4u ≤ 2.22 ps (CMP-007); CEI-112G-XSR JRMS ≤ 0.0224 UI | σ_RJ is sized so that JH4u lands on its ceiling (tougher-spec rule); ELE-002/004 |

## 3.3 Duty-cycle distortion of the half-rate clock (ELE-003)

Because the final 2:1 mux is clocked at half rate, a clock duty cycle D ≠ 50 % makes even and odd bit widths alternate between 2D · UI and 2(1 − D) · UI, displacing the even–odd crossing by DCD_duty = |2D − 1| · UI. Independently, the driver’s rise/fall mismatch Δt_rf shifts the crossing by Δt_rf / 2 (TXD, ELE-006). The two terms add linearly to the EOJ03 ceiling. JIT-001 Table 5-3c evaluates the margin: at the limit values (0.35 ps mismatch, ± 0.3 pt duty) the sum is 0.0246 UI — effectively zero margin — and its disposition holds the ELE-006 mismatch limit at 0.35 ps and tightens the DCC design target to ± 0.2 pt (JIT-D3), giving 0.0226 UI and ≈ 10 % margin. The clocking owner therefore carries a design target and a limit.

**Table 3-3. DCD decomposition at TP1**

| **Term** | **Model** | **Allocation (UI pp)** | **400G abs.** | **200G abs.** | **Owner / Req** |
| --- | --- | --- | --- | --- | --- |
| Half-rate clock duty cycle at the final mux | DCD_duty = │2D − 1│ · UI | Limit: D = 50 % ± 0.3 pt → 0.006. Design target: ± 0.2 pt → 0.004 (JIT-D3) | 56 fs limit / 38 fs target | 113 fs limit / 75 fs target | Clocking — DCC loop (Section 6); ELE-003; JIT-001 Table 5-3c |
| Driver rise/fall mismatch | Δt_rf / 2 | 0.35 ps / 2 = 0.175 ps → 0.0186 (400G) / 0.0093 (200G) | 175 fs | 175 fs | TXD Table 5-2; ELE-006 |
| Total DCD | Linear sum | ≤ 0.025 (= EOJ03 ceiling); 0.0246 at the limits (1.6 % margin), 0.0226 at the DCC target (9.6 % margin) | 235 fs | 471 fs (hardware sum ≈ 288 fs → 0.0153 UI; 1.6× margin, JIT-001 Table 4-2) | ELE-003 / 005; TXD Table 3-2; JIT-001 Table 5-3c |
| FIR bank-asymmetry apparent DCD (FIR enabled) | Logic-1 / logic-0 side-tap asymmetry Δw ≈ 0.13 per side tap (JIT-001 Table 5-3b; tap-slice skew at the ELE-008 limit contributes only 0.0003 UI) | + 0.05 (bounded by JIT-D2: │Δw_pre│ + │Δw_post│ ≤ 0.26) | + 471 fs | + 941 fs | TXD Table 6-1; not a clocking term; separate DJ_δδ adder, zero in the no-FIR configuration |

*The DCC / Δt_rf partition is fixed by JIT-001 Table 5-3c (Open item 2 there, closed): mismatch limit 0.35 ps unchanged, DCC design target ± 0.2 pt with ± 0.3 pt as the limit. Open item 8 here is therefore limited to the DCC loop bandwidth, convergence at both clock rates, and a duty monitor able to demonstrate the ± 0.2 pt target. The DCC target is UI-relative and therefore identical in both modes; the loop must operate on the 26.5625 GHz clock as well.*

## 3.4 Periodic jitter and spur limits (EMC-004, ELE-004)

Supply-coupled and reference spurs on the half-rate clock appear as sinusoidal (periodic) jitter that is bounded and data-uncorrelated. ELE-005 and JIT-001 Table 5-5 book it inside BUJ ≤ 0.036 UI pp (339 fs) together with crosstalk — JIT-001 converts that ceiling into a tolerable aggressor sum of 51 mV at the worst-case slew corner (2.0 Vppd, 4.0 ps edge, 0.30 V/ps) and carries supply-spur PJ inside it rather than as a separate term — and EMC-004 asks for spur limits derived from the ELE-004 ceiling at each baud. The clock chain is one of the aggressors of that sum; this section converts a spur level into periodic jitter at the clock and proposes how the BUJ ceiling is split between clock spurs and the crosstalk of EMC-003 (JIT-001 Open item 5). A spur at S dBc relative to the carrier is a phase modulation of peak deviation β = 2 · 10^(S/20) rad, whose peak-to-peak time jitter is J_pp = β / (π · f_clk). With f_clk · UI = 0.5 in both modes (CK_HR period = 2 UI), J_pp / UI = 2β / π, independent of mode.

**Table 3-4. Spur-to-jitter conversion at CK_HR and working limits**

| **PJ allocation (UI pp)** | **Peak phase deviation β** | **Spur limit at CK_HR (power sum of all spurs at offsets ****>**** 4 MHz)** | **Notes (equivalent aggressor at 0.30 V/ps per JIT-001 Table 5-5: V_x = SR · J_pp / 2)** |
| --- | --- | --- | --- |
| 0.005 | 7.9 mrad | −48 dBc | Comfortable; leaves 0.031 UI of BUJ to crosstalk (equivalent aggressor 7 mV of the 51 mV sum) |
| 0.010 (working allocation) | 15.7 mrad | −42 dBc | Baseline split of BUJ: 0.010 UI spurs / 0.026 UI crosstalk (Open item 9); 94 fs (400G) / 188 fs (200G); equivalent aggressor 14 mV, leaving 37 mV of the 51 mV sum to WDM-lane crosstalk |
| 0.015 | 23.6 mrad | −39 dBc | Squeezes the EMC-003 crosstalk allocation |
| 0.036 (entire BUJ) | 56.5 mrad | −31 dBc | Not permitted: consumes the whole 51 mV aggressor sum; no allocation left for crosstalk |

*Spurs below the 4 MHz corner are tracked by the far-end CDR and CRU and are weighted by the Table 3-2 high-pass; spurs above it count fully. The reference spur (at f_ref and harmonics) is always above the corner. Spread-spectrum modulation of the line clock is prohibited (EMC-004). Compliance is verified at the PLL output and at the serializer output across PVT in both modes (Table 13-1).*

# 4. Reference Clock (SYS-001, SYS-002)

The line clock is derived from the host PCS clock domain over the D2D interface so that the ±50 ppm in-package tolerance (TXO-001) is inherited rather than synthesized. The reference-clock specification toward the host falls out of the PLL phase-noise mask and the multiplication ratio; it is the SYS-002 deliverable that the overview marks as the first thing to close.

**Table 4-1. Reference-clock interface parameters**

| **Parameter** | **Target / Default** | **Basis / constraint** | **Req** |
| --- | --- | --- | --- |
| Source | Forwarded or derived clock from the host PCS domain over D2D | Guarantees ±50 ppm without a local crystal; the D2D selection (UCIe / BoW / custom) fixes the physical form (Open item 2) | SYS-001, SYS-004 |
| Frequency f_ref | TBD — candidates 830.078 MHz (N = 64), 1660.16 MHz (N = 32), 3320.31 MHz (N = 16); 156.25 MHz (N = 340) not preferred | N = 53.125 GHz / f_ref shall be an integer (no fractional-N spurs, EMC-004); in-band PLL noise rises by 20·log10(N) = 36.1 / 30.1 / 24.1 / 50.6 dB respectively | SYS-001/002, EMC-004 |
| Same f_ref in both modes | Required | The VCO frequency is unchanged in 200G mode (Table 2-4); only the mode divider changes | CMP-005 |
| Frequency tolerance | ±50 ppm (host-derived) | TXO-001; the CDR tracks ±200 ppm relative (CDR-002) | TXO-001 |
| Phase noise (in-band, offsets up to the PLL bandwidth) | ≤ L_PLL,in-band − 20·log10(N) − 3 dB; e.g. ≤ −144 dBc/Hz at 4 MHz offset for N = 64 against mask B (−105 dBc/Hz at 53.125 GHz) | Reference noise multiplied by N dominates in-band noise together with the PFD / charge-pump; the 3 dB margin covers the PLL’s own in-band contribution (Open item 2) | SYS-002 |
| Phase noise (far-out) | Not critical beyond the PLL bandwidth | Suppressed by the loop; the VCO sets the far-out mask | SYS-002 |
| Spurs | TBD dBc, such that the CK_HR power-summed spur level meets Table 3-4 (−42 dBc working) after 20·log10(N) and loop filtering | Reference spurs at k · f_ref are above the 4 MHz corner and count fully | EMC-004 |
| Spread-spectrum | None | Prohibited on the line clock | EMC-004 |
| Duty cycle / signalling | TBD (differential; swing and common mode per the D2D selection) | Only the edge used by the PFD matters; both edges if a 2× PFD is used | — |
| Loss / activity detection | Reference-loss monitor → latched fault; TX held safe (squelched / disabled), heaters safe | A lost reference must never leave a ring transmitting unlocked data or an unflagged link-down | REG-007, SYS-005, ROB-003 |
| Sharing | One reference per port (four channels) or per die, TBD | Shared reference keeps inter-channel frequency identical; per-channel PLLs still see identical f_ref | SYS-001 |
| Documentation | This table plus Table 2-2 constitute the SYS-001 frequency-plan record | — | SYS-001 |

# 5. LC-PLL (SYS-001, SYS-002, EMC-004, CMP-005)

## 5.1 Topology

**Table 5-1. PLL architecture decisions**

| **Attribute** | **Decision / value** | **Rationale / consequence** | **Req** |
| --- | --- | --- | --- |
| Type | Integer-N LC-PLL, VCO at 53.125 GHz | LC tank for the ≈ 100 fs → 72 fs integrated jitter class at 53 GHz; integer-N avoids fractional spurs (EMC-004) | SYS-001/002, EMC-004 |
| Reference and ratio | f_ref per Table 4-1; N = 53.125 GHz / f_ref integer (64 at 830.078 MHz) | In-band noise floor = reference + 20·log10(N) + PFD / CP; low N preferred | SYS-002 |
| Loop bandwidth | TBD (working 3–8 MHz) | Trade: a wider loop suppresses VCO noise in the 4–30 MHz band that counts most (Table 5-2 band breakdown) but passes more multiplied reference noise; the optimum sits near the VCO / reference cross-over and is a CDNS deliverable | SYS-002 |
| Mode divider | ÷1 (400G) / ÷2 (200G) after the PLL, before distribution | VCO, loop, and masks unchanged between modes; the ÷2 adds a small divider jitter term (Table 6-1) | CMP-005 |
| Instances and sharing | One PLL per channel, shared TX / RX (baseline) | Per Table 2-4; separate TX / RX PLLs or one TX PLL per port are the alternatives (Open item 4); a shared PLL couples serializer switching noise into the RX sampling clock — PSRR / isolation obligation (Table 11-1) | SYS-001, SYS-008 |
| Outputs | CK_VCO differential to the mode divider; lock-detect flag; coarse-tune code readback | Lock flag enters the SYS-007 bring-up sequence and the REG-007 fault taxonomy | SYS-007, REG-007 |
| Lock time | TBD µs from reference valid (incl. coarse calibration) | Budgeted inside SYS-007 time-to-traffic; not on the t_lock ≤ 50 ms critical path unless the PLL must re-lock on mode change (Table 10-2) | SYS-007 |
| Power | 60 mW per channel (RX architecture estimate) — covers TX and RX if shared | Does not scale with baud (Table 12-1) | SYS-008 |

## 5.2 Phase-noise specification

Two masks are stated: mask A integrates to the first-cut 100 fs PLL allocation of JIT-001 Table 5-1, mask B to the 72 fs working target of Table 3-1. Both are illustrative decompositions of the integrated targets, not owner commitments: the committed deliverable is the integrated value with the Table 3-2 weighting, and CDNS may redistribute the mask. The wideband floor matters at this carrier — a −150 dBc/Hz floor alone integrates to ≈ 31 fs over 1–53 GHz — and the 4–30 MHz decade contributes the largest share because the 4 MHz high-pass has just opened there.

**Table 5-2. PLL single-sideband phase noise at CK_VCO = 53.125 GHz (dBc/Hz; illustrative masks)**

| **Offset** | **Mask A (first cut, ≈ 100 fs)** | **Mask B (working target, ≈ 72 fs)** | **Notes** |
| --- | --- | --- | --- |
| 1 MHz | −98 | −100 | Largely removed by the 4 MHz high-pass (weight 0.06) |
| 4 MHz | −102 | −105 | CRU / CDR corner; in-band region — reference + 20·log10(N) + PFD / CP |
| 10 MHz | −106 | −110 | Loop-bandwidth region |
| 30 MHz | −115 | −119 | Transition to VCO-dominated; 4–30 MHz band contributes ≈ 55 % of the total power |
| 100 MHz | −125 | −129 | VCO 20 dB/decade |
| 300 MHz | −134 | −138 | — |
| 1 GHz | −142 | −146 | — |
| 3 GHz | −148 | −151 | Approaching the floor |
| Floor to 53.125 GHz | −149 | −152 | Buffer / divider noise floor; ≈ 25–30 fs by itself |
| Integrated, 4 MHz – 53.125 GHz, CRU-weighted (400G mode) | ≈ 100 fs rms; φ_rms ≈ 1.9°; −29.4 dBc | ≈ 68 fs rms; φ_rms ≈ 1.3°; −33 dBc | σ_t = φ_rms / (2π · 53.125 GHz) |
| Integrated, 4 MHz – 26.5625 GHz at the ÷2 output (200G mode) | ≈ 98 fs = 0.0052 UI | ≈ 65 fs = 0.0035 UI | Mask values at 26.5625 GHz read 6 dB lower for the same time jitter; UI-relative margin ≈ 2× |

*Mask values are given to ±1 dB; the integrated result is what is verified (Table 13-1, SYS-002 A). The masks assume the Table 3-2 first-order 4 MHz high-pass; a brick-wall lower bound would read ≈ 5 % lower.*

## 5.3 Tuning range, calibration, and PVT

**Table 5-3. VCO tuning and PVT provisions**

| **Parameter** | **Target / Default** | **Basis / constraint** | **Req** |
| --- | --- | --- | --- |
| Center frequency | 53.125 GHz | Both modes | SYS-001 |
| Tuning range | TBD — working ≥ ±6 % (≈ 50–56.5 GHz) as coarse capacitor bank plus fine varactor | Shall cover the tank’s PVT and aging shift with lock margin at every corner; the ±50 ppm reference range is negligible against it | SYS-001 |
| Coarse-tune calibration | Foreground at bring-up, code stored; re-run on reference-loss recovery | Entry of the SYS-007 sequence; no re-tune on mode change (VCO unchanged) | SYS-007, CMP-005 |
| Fine gain K_VCO | TBD MHz/V | Low enough that control-line and supply noise stay inside mask B; high enough to hold lock across the temperature range without a coarse step | SYS-002, DTX-010 |
| Temperature range | Declared cold-plate range (SYS-006), TX-region and RX-region sensors available | Lock shall hold without a coarse re-calibration across the range, or the re-calibration shall be hitless (Open item 12) | SYS-006, MGT-006 |
| Supply sensitivity | TBD fs per mV (pushing) | Enters the PSRR derivation of Table 11-1 | DTX-010 |
| Lock detector | Programmable frequency-error window and persistence; assert / de-assert exposed | Feeds SYS-007 and REG-007 (PLL unlock is a latched fault) | REG-007 |
| Aging | Within the tuning margin over ≥ 100 000 h | Continuously oscillating tank and buffers signed off for wearout | ROB-007 |

## 5.4 Spurs and supply

**Table 5-4. PLL clock-purity and supply interface**

| **Item** | **Limit** | **Basis** |
| --- | --- | --- |
| Reference spurs (k · f_ref offsets) and their harmonics | Power-summed spur level at CK_HR ≤ −42 dBc (working) for PJ ≤ 0.010 UI pp | Table 3-4; verified at the PLL output and the serializer output in both modes |
| Fractional spurs | None — integer-N | EMC-004 |
| Spread-spectrum modulation | Prohibited | EMC-004 |
| Supply-induced phase noise | Within mask B at every offset; PSRR per rail TBD from the ROB-004 PDN transient mask | DTX-010; dedicated regulated rail for the VCO and charge pump |
| Coupling from the serializer (shared PLL) | Serializer data-dependent supply current shall not produce spurs above the Table 3-4 limit at CK_HR | Data-pattern-dependent tones at f_baud / pattern-length; EMC-003 |
| Verification planes | PLL output (test port), serializer output (extracted simulation and on-die monitor), across PVT, both modes | EMC-004 |

# 6. Clock Distribution and Duty-Cycle Correction (ELE-003, ELE-005)

The distribution tree carries CK_HR from the mode divider to the serializer final mux and to the 8-phase generator of the same channel. Its jitter allocation is supply-noise limited, and it hosts the duty-cycle-correction loop that owns the 0.006 UI DCD term of Table 3-3. The distribution bandwidth and skew budget are fixed here.

**Table 6-1. Clock-distribution parameters**

| **Parameter** | **Target / Default** | **Basis / constraint** | **Req** |
| --- | --- | --- | --- |
| Topology | PLL → mode divider → CK_HR buffer chain → (a) serializer 2:1 mux and branch retiming; (b) ÷4 8-phase generator; per channel | Two loads only; no inter-channel 53 GHz routing in the per-channel PLL baseline | SYS-001 |
| Random-jitter allocation | 60 fs rms first cut → 45 fs working (incl. mode divider and DCC path) | Table 3-1; supply-noise limited | ELE-005 |
| Mode-divider jitter (200G mode) | TBD fs, inside the 45 fs allocation | The ÷2 adds its own noise; UI-relative margin is 2× in 200G mode | CMP-005 |
| Buffer bandwidth / edge rate | TBD; edge rate at the final mux fast enough that supply noise converts to ≤ the allocation (Δt = ΔV / slew) | Slower edges convert supply noise into more jitter and into duty-cycle error | ELE-005, DTX-010 |
| Duty-cycle correction (DCC) | On CK_HR at the serializer final mux; residual D = 50 % ± 0.2 pt design target (0.004 UI pp), ± 0.3 pt limit (0.006 UI pp) — JIT-D3; loop bandwidth ≪ 4 MHz (quasi-static); duty monitor with resolution ≤ 0.05 pt and correction code readable | Table 3-3; JIT-001 Table 5-3c; same UI-relative target in both modes (26.5625 GHz clock in 200G mode) | ELE-003; JIT-D3 |
| Duty cycle into the 8-phase generator | 50 % ± TBD | A ÷4 divider re-establishes 50 % duty on its outputs; input duty error maps into even/odd phase spacing error, corrected by the phase calibration of Table 8-2 | Section 8 |
| Skew, TX branch vs. RX branch | Unconstrained | Independent domains; the RX phase is set by the PI | — |
| Inter-channel TX skew (clock-chain share) | ≤ 1 UI working target (9.4 ps) between the four channels of a port | Inside the TXO-012 < 4 UI (37.6 ps) routing-skew budget per end; with per-channel PLLs it is the static phase-offset spread of PLLs locked to one reference plus tree mismatch | TXO-012 |
| Supply | Dedicated, regulated clock rail; PSRR TBD from the ROB-004 mask so that PSIJ ≤ the 45 fs allocation and periodic terms ≤ Table 3-4 | Heater-rail ripple excluded from the clock rails | DTX-010 |
| Isolation | 53 GHz nets shielded from the TIA input, the slice inputs, and the TP1 nets; return paths defined | Clock is an aggressor in the EMC-003 budget | EMC-003 |
| Power | RX branch inside the 15 mW “CLK buffer” estimate; TX branch TBD | Table 12-1 | SYS-008 |

# 7. Serializer Clock Interface and TX Timing (ELE-002..005, ELE-007/008, CMP-007)

The serializer is a CDNS deliverable defined in DES-OCI-106G-TXD-001 Table 2-1 (block 1) and Table 4-1; this section fixes its clocking and the output-jitter model. All timing is generated in the half-rate clock domain, so the FIR branch delays track the baud automatically (CMP-007).

**Table 7-1. Serializer clocking and TX timing parameters**

| **Parameter** | **400G OCI mode** | **200G OCI mode** | **Constraint / basis** | **Req** |
| --- | --- | --- | --- | --- |
| Final mux | 2:1 at half rate, clocked by CK_HR = 53.125 GHz; rising edge → even bit, falling edge → odd bit | 2:1 at CK_HR = 26.5625 GHz | Both edges define bit boundaries → duty cycle becomes DCD (Table 3-3) | ELE-003 |
| Serializer tree | 128 → … → 4 → 2 → 1; the last two stages at CK_HR/2 (26.56 GHz, quarter rate) and CK_HR | Same structure at half the clock rates | Only the final stage sees the full DCD sensitivity; earlier stages are retimed | SYS-001 |
| Half-rate duty at the final mux | 50 % ± 0.2 pt target / ± 0.3 pt limit after DCC → 0.004 / 0.006 UI = 38 / 56 fs pp | 50 % ± 0.2 / ± 0.3 pt → 75 / 113 fs pp (0.004 / 0.006 UI) | Leaves 0.0186 UI to the driver rise/fall term inside the 0.025 UI EOJ03 ceiling; the ± 0.2 pt target buys ≈ 10 % DCD margin (JIT-001 Table 5-3c, JIT-D3) | ELE-003 / 005; JIT-D3 |
| Serializer random jitter | 40 fs rms first cut → 30 fs working | Same hardware value | Table 3-1; final mux plus last retiming stage | ELE-005 |
| FIR branch phases 0 / 1 / 2 UI | Retimed copies of the NRZ stream: 1 UI = half a CK_HR period (opposite clock edge), 2 UI = one CK_HR period; 0 / 9.41 / 18.82 ps | 0 / 18.82 / 37.65 ps — inherent baud tracking | Method entry of TXD Table 6-3 (“serializer-domain phase copies”) — and the answer to JIT-D4: no phase interpolator or delay element is in the TX clock path, so JIT-001 Table 5-1b variant “No PI in TX path” governs Table 3-1. Inter-phase skew at the tap-slice inputs TBD (LM target / CDNS achieved) feeding the ELE-008 0.24 ps TP1 matching | ELE-007 / 008, CMP-007; JIT-D4 |
| Output-jitter model at the serializer output | TIE = PLL phase noise (4 MHz high-pass) ⊕ distribution ⊕ mux (RSS, Table 3-1) + DCD_duty (Table 3-3) + PJ from spurs (Table 3-4); no data-dependent term before the pre-driver | Same model, UI = 18.824 ps | The plane at which EMC-004 spur compliance and the clock-only ELE-002/004 metrics are simulated; TP1 adds the pre-driver and driver terms (TXD Table 3-2) | ELE-002..005, EMC-004 |
| TX word clock CK_WTX | 830.078 MHz (W_tx = 128), CK_HR ÷ 64 | 415.04 MHz | TX digital, PMA, PRBS generators run below 1 GHz | — |
| Legal static park states | Serializer output held at a defined static rail; CK_HR and CK_WTX keep running | Same | Squelch suppresses modulation only; clocks running keeps the PLL, DCC, and 8-phase calibration warm for a glitch-free exit (SQL-005) | SQL-001, DES-OCI-106G-SQL-001 |
| Clock switchover | None — the TX line clock is always the host-derived clock | Same | DJI-005 (transition only while RTS is false) is satisfied by construction; if a recovered-clock TX option is ever added it shall obey DJI-005 | DJI-005 |
| Inter-channel TX clock skew | ≤ 1 UI working target | ≤ 0.5 UI (same 9.4 ps) | Table 6-1; inside TXO-012 | TXO-012 |
| Frequency accuracy | 106.25 GBd ± 50 ppm (inherited from f_ref) | 53.125 GBd ± 50 ppm | No local frequency source | TXO-001, CMP-005 |
| Observability | On-die TIE / eye monitor at the serializer output (edge-crossing statistics vs. CK_HR), DCC readback, PRBS generators (DFT-001) | Same | ELE-001: TP1 is unprobeable; the serializer output is the accessible internal plane | ELE-001, DFT-001 |

# 8. RX 8-Phase Interleaved Sampling Clock (CDR-001, DRX-006, RXF Section 8)

The receive slicer front end (DES-OCI-106G-RXF-001 Section 8) is 8-way interleaved: eight sample-and-hold plus comparator slices per channel, each clocked at baud/8, so that no receive circuit is clocked at the line rate. Each slice tracks the CTLE output for four UI, samples on the falling edge of its phase, and holds for four UI while its comparators resolve. The even slices are driven by the CTLE-even buffer and the odd slices by the CTLE-odd buffer. At any instant only two of the four slices on each buffer are tracking, which limits the load the buffer sees. Figure 8-1 (Section 8.2) draws the sampling-clock path from the 8-phase generator to the recovered word-clock domain.

## 8.1 Interleaving architecture and slice timing

**Table 8-1. 8-way interleaved sampling — timing fixed by the 8-Phase S/H timing diagram**

| **Attribute** | **400G OCI mode** | **200G OCI mode** | **Basis / notes** |
| --- | --- | --- | --- |
| Interleave factor | 8 — each slice samples every 8th UI | 8 | No comparator or S/H is clocked at the line rate; comparator clock = baud/8 |
| Slice clock (per phase) | clk8 = 13.28125 GHz; period 75.29 ps = 8 UI | 6.640625 GHz; period 150.59 ps | CK8_PI[k], k = 0..7 |
| Phase spacing | 1 UI = 9.412 ps = 45° of clk8 | 1 UI = 18.824 ps | Ideal grid against which static skew is measured (Table 8-2) |
| Duty cycle | 50 % — high = tracking, low = holding | 50 % | Two of four phases of each parity are high at any instant |
| Track window | 4 UI = 37.6 ps (φk high) | 4 UI = 75.3 ps | S/H follows the CTLE buffer output |
| Sampling instant | Falling edge of φk (end of track) | Same | Sampling-edge jitter and skew are the terms of Table 8-3 |
| Hold / decision window | 4 UI = 37.6 ps (φk low) | 4 UI = 75.3 ps | Comparator regenerates and resets at clk8 — noise-optimised speed; hold-mode bandwidth and kickback per RXF Table 8-1 |
| Even / odd split | φ0, φ2, φ4, φ6 → CTLE-even buffer → 4 slices; φ1, φ3, φ5, φ7 → CTLE-odd buffer → 4 slices | Same | Each buffer drives two tracking sampling capacitors at a time (2-of-4 rule) |
| Charge-share settling | ≥ 2 UI = 18.8 ps between a slice starting to track and the co-tracking slice’s sampling edge | ≥ 2 UI = 37.6 ps | Timing-diagram annotation (φ2 / φ4); the disturbance when a new sampling capacitor connects must settle inside the RXF Table 8-3 error allocation before the other slice samples (Open item 10) |
| Sampling sequence | φ4, φ5, φ6, φ7, φ0, φ1, φ2, φ3 on consecutive UIs (repeating every 8 UI) | Same | UI index n of the 8-UI frame is sampled by φ((n + 4) mod 8); even UIs by even phases |
| Comparators per slice | Data slicer + top and bottom error slicers (3), all at the data phase | Same | RXF Table 8-2; a baud-rate Mueller–Müller CDR needs no edge comparator |
| Comparators per channel | 24 mission at 13.28 GHz, plus one monitor comparator on CK_MON | 24 + 1 at 6.64 GHz | 10 mW estimate for the 24 (Table 12-1); the monitor slice is EYM Table 11-1 |
| Monitor slice (eye monitor) | One additional S/H + comparator — a replica of a mission slice — clocked by CK_MON at baud/8; samples the UIs of mission slice k_mon displaced by mon_phase_offset (±0.5 UI) | Same, at 6.64 GHz | DES-OCI-106G-EYM-001 Section 5; hangs on its own scaled replica buffer, so the mission even / odd buffers and the 2-of-4 rule are untouched (Section 9.4) |
| Aperture | Sampling-edge transition time at the S/H switch TBD ps, matched across phases | Same hardware | Interleaving with S/H mitigates sampling-aperture ISI; edge-rate mismatch between phases is skew (Table 8-2) |

## 8.2 Block diagram

**Figure 8-1. RX 8-way interleaved sampling clock architecture**

*\[FIGURE PLACEHOLDER — insert block diagram here. Suggested content: the receive sampling-clock path of one channel from the 8-phase generator to the recovered word-clock domain, annotated with the timing of Table 8-1. Top: 8-phase generator (method of Table 8-2: CK_HR ÷ 4 as cascaded I/Q ÷2 stages, both polarities) → CK8\[7:0\] → per-phase delay DACs (static-skew calibration trims; codes per mode from MFG-003 NVM; residual ≤ 0.02 UI pp target) → phase interpolator / rotator (Section 9) with pi_code from the CDR loop filter / phase FSM (DES-OCI-106G-CDR-001) and the signal_valid hold → CK8_PI\[7:0\] = φ0 … φ7. Beside the clock bus draw the eight waveforms: slice clock 13.28125 GHz (period 8 UI = 75.29 ps) in 400G mode / 6.640625 GHz (150.59 ps) in 200G mode; adjacent phases 1 UI = 9.412 ps (400G) / 18.824 ps (200G) apart = 45° of the slice clock; 50 % duty — high = track 4 UI, falling edge = sampling instant, low = hold 4 UI; sampling sequence φ4, φ5, φ6, φ7, φ0, φ1, φ2, φ3 on consecutive UIs. Middle: the sampler array — eight sample / hold + comparator slices (each S/H switch clocked by its φk; three comparators per slice — data, top error, bottom error — all at the data phase; 24 mission comparators per channel); the φ0 / φ2 / φ4 / φ6 slices fed by the CTLE-even buffer and the φ1 / φ3 / φ5 / φ7 slices by the CTLE-odd buffer (2-of-4 tracking rule); load per phase = one S/H switch, three comparator clock inputs, one DMUX first stage. Show the ninth (monitor) slice beside them on its own replica buffer, clocked by CK_MON from pi_mon (Section 9.4; DES-OCI-106G-EYM-001 Section 5), with slice select k_mon. Bottom: DMUX stage — each slice’s d, e_top, e_bot at 13.28 Gb/s → 1:16 deserialization (1:8 if W_rx = 64, Open item 7) → 128-bit d and 128-bit signed e words per CK_WRX cycle; the monitor DMUX 1:16 → CK_WMON word aligned to the CK_WRX word of slice k_mon → EyeMonNrz. Recovered clock domain: CK_WRX = CK8_PI\[0\] ÷ 16 = 830.078 MHz × (1 + Δf) (415.04 MHz in 200G mode), drawn as a dashed domain boundary enclosing the DMUX outputs, the CDR loop filter and phase FSM (one voter dump per 128 UI; DES-OCI-106G-CDR-001 Section 5) and the deskew phase-FIFO write side (BUP-002), with the elastic-FIFO crossing to the host domain (SYS-003; logic deliverable) shown leaving the boundary. Calibration observable: eye monitor with slice select (DES-OCI-106G-EYM-001 Section 8) → firmware → per-phase trim codes, drawn as a dashed feedback arrow into the delay DACs. Clock arrows solid, data arrows double, control and calibration arrows dashed.\]*

## 8.3 Multi-phase generation and calibration

**Table 8-2. 8-phase generator parameters**

| **Item** | **Target / Default** | **Constraint / basis** | **Req / owner** |
| --- | --- | --- | --- |
| Method (baseline) | CK_HR ÷ 4 as two cascaded ÷2 stages: stage 1 gives 26.56 GHz I/Q (90° = 1 UI); stage 2 divides I and Q and takes both polarities → eight 13.28 GHz phases at 45° = 1 UI | Phases inherit the PLL phase noise; the divider adds a term TBD inside the RX chain allocation (Table 3-1). In 200G mode the same divider runs from the 26.5625 GHz CK_HR | CDNS |
| Alternative | Dedicated multi-phase oscillator or DLL at baud/8 | Trades divider phase error for a second locked loop; not the baseline | Open item 6 |
| Duty cycle per phase | 50 % ± TBD | Track window ≥ 4 UI minus the aperture; settle ≥ 2 UI preserved in the worst case | Table 8-1 |
| Static phase error, uncalibrated | TBD (divider and buffer mismatch, input duty error) | Bounded so that calibration range covers it | CDNS |
| Static phase error, residual after calibration | ≤ 0.02 UI pp (188 fs / 376 fs) any phase to the ideal 1-UI grid — working target | Horizontal eye term of the worst slice (Table 8-3); the MM lock point is set by the ensemble, so per-slice skew is not tracked by the CDR | Open item 6; RXF Table 8-3 |
| Calibration | Per-phase delay DACs; foreground at bring-up (SYS-007) using the on-die phase / eye monitor, plus background tracking; codes per mode stored in NVM | MFG-003 integrity protection; re-calibration shall be hitless in mission mode or confined to the maintenance state (FW-005) | MFG-003, SYS-007, FW-005 |
| Phase-error observable | Eye monitor with slice select (DES-OCI-106G-EYM-001 Section 8): the displacement of the per-slice horizontal bathtub centre from offset 0, measured against the common monitor phase, is the skew of that slice’s sampling instant (per-slice skew scan ≈ 20 ms); error-slicer eye-centre statistics as the fallback | The monitor is the proposed calibration observable of this table and also serves the DFT-003 MPI metric and VDM | DFT-003; EYM Table 8-1 |
| Sampling-edge transition time | TBD ps at the S/H switch, matched across phases | Aperture and edge-rate matching | RXF Table 8-1 |
| Load per phase | One S/H switch, three comparator clock inputs, DMUX first stage; plus the pi_mon input load, constant (Table 9-5) | Inside the 15 mW “CLK buffer” estimate; the monitor slice itself loads CK_MON, not CK8_PI | SYS-008 |
| Random jitter | Shared with the whole chain: PLL + distribution + divider (Table 3-1 RX row) | Divider term TBD | CDNS |

## 8.4 RX sampling-clock timing budget

The receiver eye budget of Rev 0.7 §9 is a placeholder and RXF Table 8-3 carries only the CDR dither (1 PI code) as a horizontal term. The terms below are the clocking contributions that budget must also carry; they are stated here so that the RX eye analysis (DRX-004 statistical eye) and the RXF bookkeeping can pick them up (Open item 6).

**Table 8-3. Clocking terms of the RX horizontal eye budget**

| **Term** | **Value** | **Nature** | **Consumer / notes** |
| --- | --- | --- | --- |
| RX clock-chain random jitter (PLL + distribution + ÷4 + PI), above the CDR bandwidth | ≈ 100 fs rms working (RSS 72 / 45 / 50 + divider TBD) | Gaussian | 2Qσ = 0.15 UI pp at 1e-12 (Q = 7.034); 0.074 UI pp at the 2.4E-4 compliance point (Q = 3.49); halves in UI in 200G mode |
| CDR steady-state dither | ±1 PI code = 0.031 UI pp | Bounded | Already in RXF Table 8-3; ADP-003 aggregate-dither allocation |
| Static inter-phase skew (worst slice) | ≤ 0.02 UI pp working target | Bounded, per slice | Table 8-2; appears as a per-slice offset of the sampling instant |
| PI integral non-linearity | ≤ 1 LSB = 0.031 UI working target | Bounded | Static part is absorbed by the MM lock; the part that varies with code during frequency tracking is periodic jitter at the rotation rate (Table 9-1) |
| Untracked sinusoidal jitter under the JTOL mask | 0.10–0.15 UI pp budget (0.05 UI shelf above 4 MHz) | Bounded | CDR-001; the loop bandwidth window is the CDR document’s obligation |
| Duty-cycle error per phase | Shortens the track or settle window; does not move the sampling instant | — | Table 8-2 |
| Eye-monitor instrument error (affects the measured eye, not the mission eye) | Monitor-unique jitter ≤ 50 fs rms; residual monitor-to-data skew ≤ 0.25 code (working, Table 9-4) | Gaussian / bounded | Broadens a measured 100 fs bathtub by ≤ 12 fs rms (≤ 0.02 UI pp at 1e-12) and shifts it by ≤ 74 fs; EYM Table 7-2 corrects the extrapolated eye for both. Common-chain jitter is shared with the data clock and does not appear as an instrument term |
| Aggregate | To be summed by the RX eye analysis with the TX TJ and the vertical terms of RXF Table 8-3 | — | Rev 0.7 §9 “RX eye budget” placeholder |

## 8.5 DMUX and the recovered clock domain

**Table 8-4. Deserialization and recovered word clock**

| **Item** | **400G OCI mode** | **200G OCI mode** | **Notes / Req** |
| --- | --- | --- | --- |
| Slice output rate | 13.28 Gb/s per slice for each of d, e_top, e_bot | 6.64 Gb/s | Retimed on the slice’s own phase |
| Deserialization per slice | 1:16 | 1:16 (W_rx = 128, baseline) or 1:8 (W_rx = 64) | Open item 7 |
| Word | 128-bit d plus 128-bit signed e (or e_top / e_bot) per CK_WRX cycle | Same | Feeds the ternary vote generator and the deskew engine |
| Recovered word clock CK_WRX | CK8_PI[0] ÷ 16 = 830.078 MHz × (1 + Δf); tracks the far-end rate because the PI rotates continuously | 415.04 MHz (or 830 MHz) | The only clock in the receiver that runs at the far-end rate; SYS-003 |
| CDR window boundary | One CK_WRX cycle = 128 UI = one voter dump (cdr_width = 128) | Same in UI | DES-OCI-106G-CDR-001 Section 5; the loop filter and phase FSM run at CK_WRX |
| Crossing to the host domain | Elastic FIFO per host stream, ±100 ppm relative, depth against DJI-004 skew-variation limits | Bit depth scales with baud | SYS-003 — logic deliverable; not sized here |
| Deskew interface | Phase-FIFO write clock = CK_WRX of the channel; integer-UI realignment 0–15 UI in the deskew engine | 0–7 UI | BUP-002 |
| Relationship between channels | Four independent CK_WRX domains per port (one per channel), each at its own far-end phase | Same | B7 port-level deskew group |
| Monitor DMUX and word (eye monitor) | 1:16 from CK_MON; 16 m bits per CK_WMON word, aligned to the CK_WRX word of slice k_mon so that m and d of the same UI index pair off | 1:16 (or 1:8) | Alignment fixed once per k_mon and held across the full ±16-code offset range (│offset│ ≤ 0.5 UI keeps the pairing unambiguous); two-stage retiming resolves the deliberately metastable monitor comparator (Table 9-5; EYM Table 6-1) |

# 9. Phase Interpolator (CDR-001/002/004/006/007, DES-OCI-106G-CDR-001)

The phase interpolator is the actuator of the baud-rate Mueller–Müller CDR: the phase FSM of DES-OCI-106G-CDR-001 wraps its accumulated delta into a 5-bit code with 1/32 UI resolution, and the PI moves the sampling instant of all eight interleaved slices together. The CDR document fixes the code space and the loop gains; this section fixes what the hardware must do with the code — resolution, interpolation interval, continuity of rotation, update timing, linearity, jitter, and hold — including delay-cell characterisation (Section 9.3).

## 9.1 Definition

**Table 9-1. Phase-interpolator parameters**

| **Parameter** | **Value** | **400G OCI mode** | **200G OCI mode** | **Notes** | **Req** |
| --- | --- | --- | --- | --- | --- |
| Code from the CDR | 5 bits per UI (n_pi_codes = 32), from a wrapping phase accumulator with 512 sub-codes per code | — | — | DES-OCI-106G-CDR-001 Section 3.1 / 5.1; the PI sees integer codes only | CDR-001 |
| Resolution (1 LSB) | 1/32 UI | 294 fs | 588 fs | Steady-state dither ±1 code = 0.031 UI pp (RXF Table 8-3) | CDR-001, ADP-003 |
| Interpolation interval (PI span, DES-OCI-106G-CDR-001 Section 3.1) | 1.0 UI — between adjacent CK8 phases φk and φk+1 | 9.412 ps | 18.824 ps | 45° of clk8; the 32 codes of one UI select the mixing weight within one phase pair | — |
| Rotation range | Unlimited — modular over the 8-UI clk8 period (8 pairs × 32 codes = 256 positions) | 75.3 ps | 150.6 ps | Seamless wrap; a code carry moves to the next phase pair without a phase discontinuity (Table 9-2) | CDR-002, CDR-004 |
| Phases moved | All eight CK8 phases together by one common code | — | — | Per-phase skew is a separate, calibrated quantity (Table 8-2) | — |
| Code update rate | Once per voter dump (cdr_width = 128 UI), synchronous to CK_WRX | 830.078 MHz | 415.04 MHz (W_rx = 128) | DES-OCI-106G-CDR-001 Section 5 | CDR-001 |
| Code step per update, mission mode | Proportional ≤ 128 · 2 / 512 = 0.5 code plus frequency ≤ 0.82 code at 200 ppm → design for ≥ 2 codes glitch-free | ≤ 0.0625 UI | ≤ 0.0625 UI | Default gains p_step / p_div = 2 / 512, f_step / f_div = 2 / 64 | CDR-001, CDR-002 |
| Code step per update, acquisition | TBD ≥ mission step; the gear-shift (smaller p_div) may step several codes per update | TBD | TBD | Programmable acquisition gains (CDR-007); PI shall follow without a missed or duplicated sampling edge | CDR-007 |
| Continuous rotation rate | ≥ ±244 ppm (frequency clamp f_bound = 2¹⁵) | 1 UI per 4098 UI; one code per 128 UI | Same in UI | CDR-002 target ±200 ppm with ≥ 20 % clamp margin; at 100 ppm one code per 313 UI, one UI per 94 ns | CDR-002 |
| Code-to-phase latency | ≤ 1 update period, deterministic (working) | ≤ 1.2 ns | ≤ 2.4 ns | Part of the loop delay that the heavily damped mission gains must tolerate (DES-OCI-106G-CDR-001 Section 7.1) | CDR-001 |
| Glitch-free code change | A code change shall never create, duplicate, or suppress a sampling edge on any phase; changes applied between the sampling edges of the affected phases | — | — | A glitch is a burst error source (CDR-004 < 1E-20 for bursts > 7 symbols) | CDR-004 |
| Monotonicity | Required over all 256 positions including phase-pair boundaries | — | — | No phase reversal at any code step; otherwise the MM loop can lock to a false point | CDR-001 |
| DNL | ≤ ±0.5 LSB working target | ≤ 147 fs | ≤ 294 fs | Feeds the “DNL + intrinsic” jitter row of Table 3-1 | CDNS |
| INL | ≤ ±1 LSB after calibration, working target | ≤ 294 fs | ≤ 588 fs | Static part absorbed by the MM lock; code-dependent part is periodic jitter at the rotation rate (10.6 MHz at 100 ppm, 21 MHz at 200 ppm) | MFG-003 |
| Random jitter (intrinsic + DNL) | 70 fs rms first cut → 50 fs working | — | — | Table 3-1 (RX sampling chain, Table 8-3) | CDR-001 |
| Hold on signal-invalid | Code and phase held; phase drift ≤ TBD (working ≤ 1 LSB) over the hold interval ≥ 50 ms | ≤ 294 fs | ≤ 588 fs | Warm re-acquisition requires the sampling phase to stay inside the eye; temperature drift of the mixer / bias during a squelch event | CDR-006, RXO-007 |
| Per-mode LUT (piTable) | Code → mixer-weight table stored per mode; calibration in NVM | — | — | CMP-009; MFG-003 | CMP-009 |
| Initial code | init_pi = 0 (any position valid) | — | — | DES-OCI-106G-CDR-001 Section 3.1 | — |
| Test access | Code override and readback; phase-step measurement via the on-die phase monitor | — | — | Enables DNL / INL characterisation and MFG-003 calibration | DFT |

## 9.2 Rotation topology in the interleaved sampler

In an 8-way interleaved receiver the PI must rotate the whole phase set continuously while the CDR tracks the far-end frequency: at ±100 ppm the sampling phase advances one full UI every 94 ns. The alternative realisation is a 1-UI, 5-bit delay-locked-loop element (Option B). Applied as a common delay to all eight phases, a 1-UI element must jump back by one UI each time the CDR code wraps, which shifts the slice-to-bit assignment by one position and forces a bit-slip correction in the DMUX on every wrap. A rotator that interpolates between adjacent phases and carries into the next phase pair has no such discontinuity. The CDR fixed-point sizing is unaffected by either choice because it depends only on n_pi_codes / pi_span_ui = 32 per UI (DES-OCI-106G-CDR-001 Section 3.2).

**Table 9-2. PI implementation options**

| **Attribute** | **Option A — 8-phase rotator (baseline)** | **Option B — 1-UI DLL delay element** |
| --- | --- | --- |
| Mechanism | Phase mixing between adjacent CK8 phases φk and φk+1 (1 UI apart); 3-bit pair select + 5-bit mixing weight = 256 positions over the 8-UI clk8 period | A common 0–1 UI delay, locked to one UI by a DLL, applied to all eight phases; 32 taps of 294 fs |
| Wrap behaviour | Seamless: code 31 of pair k continues as code 0 of pair k+1; no phase discontinuity, no bit slip | Hard 1-UI jump at code 31 → 0; the DMUX must add or drop one bit position per wrap (every 94 ns at 100 ppm) and the CDR must flag the wrap |
| CDR interface | The wrapping accumulator’s UI carry increments / decrements the pair select; n_pi_codes may be kept at 32 with a 3-bit carry counter, or restated as 256 with pi_span_ui = 8 — sizing invariant (Open item 5) | 5-bit code directly; wrap flag to the DMUX |
| Linearity | Mixer linearity needs clock edge times ≥ the phase spacing; at 13.28 GHz with 9.4 ps spacing this is natural | 294 fs taps across a 9.4 ps line are mismatch-limited; INL calibration mandatory |
| Jitter | Mixer and pair-select buffers; 50 fs working target | Delay-line noise; same allocation |
| Dual-rate | Same structure at 6.64 GHz; LUT per mode | DLL re-locks to 18.8 ps; LUT per mode |
| Status | Baseline of this document | Alternative; retained until Open item 5 closes |

## 9.3 Characterisation and calibration

**Table 9-3. PI characterisation and calibration obligations**

| **Item** | **Obligation** | **Basis / Req** |
| --- | --- | --- |
| Transfer characteristic | Phase vs. code measured over all 256 positions at PVT corners and in both modes; DNL, INL, monotonicity reported | Table 9-1; verification Table 13-1 |
| Gain K_PI | fs per code vs. supply and temperature; the CDR loop gain scales with K_PI, so its variation shall stay inside the CDR-001 bandwidth window (4–6 MHz) | CDR-001; working ±15 % over PVT (TBD) |
| Calibration | Foreground at bring-up: sweep the code against the on-die phase monitor (or use the CDR’s own lock point against a known pattern) and load the piTable; store per mode in NVM with integrity check | MFG-003, SYS-007, CMP-009 |
| Background tracking | Temperature drift of the mixing weights tracked without disturbing lock — corrections ≤ 1 LSB per commit, edge-aligned, in the maintenance state or shown hitless | FW-005, ADP-004 (analog to the CTLE de-glitch rule) |
| Hold-drift characterisation | Phase drift of a held code over ≥ 50 ms across the temperature range | CDR-006, RXO-007 |
| Wrap / carry test | Continuous rotation at ±244 ppm-equivalent code ramps in both directions with PRBS31; no bit errors, no FEC-visible bursts | CDR-002, CDR-004, DJI-002 |
| Observability | Current code, calibration table, K_PI estimate, and wrap counter readable; events logged | MGT-003 |

## 9.4 Monitor phase interpolator pi_mon — eye-monitor sampling clock (DES-OCI-106G-EYM-001)

The RX eye monitor measures the eye at any (Δt, V) point during live traffic with one additional sample/hold + comparator slice (EYM Section 5). Its horizontal axis is a second phase interpolator, pi_mon, that is not free-running: the data-path position rotates continuously at the far-end ppm offset and dithers with tracked jitter, so an absolute monitor phase would smear across the eye at the tracking ramp rate. pi_mon therefore receives the data PI’s position every update and adds a programmed displacement, and the monitor point stays at a fixed horizontal offset from the eye centre as the CDR tracks. In the interleaved receiver the displacement has two parts — an integer number of UI that selects which mission slice’s UIs the monitor observes (k_mon) and a fine offset of ±16 codes (±0.5 UI) that sweeps across that UI — and pi_mon is the Table 9-2 Option A rotator with a single output. Nothing in the mission path depends on it: a monitor glitch corrupts only monitor samples.

**Table 9-4. Monitor phase interpolator (pi_mon) parameters**

| **Parameter** | **Value** | **400G OCI mode** | **200G OCI mode** | **Notes** | **Req** |
| --- | --- | --- | --- | --- | --- |
| Topology | Single-output rotator of the Option A class: 3-bit pair select + 5-bit mixing weight over the calibrated CK8[7:0] set; own LUT (piTable_mon) | — | — | Reuses the data-rotator cell; separate supply filter and routing (Table 9-5); its input load on CK8 is part of the calibrated set | CDNS |
| Position law | pos_mon = (pos_data + 32 · k_mon + mon_phase_offset) mod 256, where pos_data = 32 · pair + pi_code is the data PI’s full 8-bit position | — | — | k_mon ∈ 0 … 7 (slice select, integer UI); mon_phase_offset ∈ −16 … +15 codes (±0.5 UI); adder in the CK_WRX domain (EYM Table 4-1 / 6-2 registers) | EYM |
| Slaving | mon_slave_en = 1 (mission): pos_mon tracks pos_data. = 0 (test): pos_data forced to zero, pos_mon absolute | — | — | Absolute mode only with a frozen CDR (code override) in synchronous electrical loopback, where the far-end offset is zero; used to characterise the data PI transfer (Table 9-3, EYM Table 8-2) | DFT-002 |
| Resolution | 1/32 UI, identical to the data PI | 294 fs | 588 fs | Horizontal scan step of the eye monitor | EYM |
| Fine offset range | ±0.5 UI about the sampling instant of slice k_mon | ±4.71 ps | ±9.41 ps | The eye is periodic in 1 UI, so ±0.5 UI covers it; k_mon extends the reach to any mission slice (256 positions in all) | EYM |
| Update timing | Same CK_WRX cycle as the data PI code; code-to-phase latency matched to the data PI (working ≤ 0.1 update period) | ≤ 1.2 ns | ≤ 2.4 ns | A latency mismatch Δ during a ppm ramp displaces the monitor by 244 ppm × Δ — ≈ 0.3 fs for Δ = 1.2 ns, negligible; matching matters only for transient (gear-shift) steps, whose dwells the monitor discards anyway | EYM |
| Rotation | Continuous with the data PI, ≥ ±244 ppm; seamless pair carry | Same | Same | A monitor glitch corrupts only monitor samples, so the CDR-004 glitch-free rule is a measurement-quality obligation here, not a burst-error one | CDR-002 |
| Reprogramming k_mon or the offset | Phase reaches the new position within ≤ 1 update period; analog settling TBD (CDNS) — covered by the EyeMonNrz settle timer before the dwell opens | TBD | TBD | Settling value delivered to EYM Table 6-2 (mon_settle) | CDNS |
| Static skew to the data phase, uncalibrated | CK_MON vs. CK8_PI[k_mon] at equal commanded position: ≤ ±2 codes (≤ 0.0625 UI) working bound | ≤ 588 fs | ≤ 1.18 ps | Branch and mixer mismatch; must lie inside the ±16-code offset range with margin — calibrated out as phase_zero_mon[k_mon] (EYM Section 8) | CDNS |
| Static skew, residual after calibration | ≤ 0.25 code working | ≤ 74 fs | ≤ 147 fs | Sub-code residual; sets the horizontal accuracy of the measured eye centre (cancels in the eye width) | EYM |
| Pair-to-pair skew of pi_mon | ≤ 0.5 code before calibration, TBD | ≤ 147 fs | ≤ 294 fs | Averages out of the measurement in mission: because pos_mon is slaved, the monitor’s interpolation pair cycles through all eight pairs as the CDR rotates (one full 8-UI rotation per 79 µs dwell at ≥ 1 ppm). Appears only in synchronous loopback, where it is characterised (EYM Open item 7) | MFG-003 |
| Monitor-unique random jitter | pi_mon intrinsic + monitor branch buffers ≤ 50 fs rms working (same class as the data PI, Table 3-1) | — | — | Common-chain jitter (PLL, distribution, ÷4) is shared with the data clock and does not broaden the measured bathtub; the monitor-unique part does (Table 8-3 row) — an instrument error that EYM Table 7-2 corrects for | EYM |
| Hold on signal-invalid | Follows the data PI (same held position input); k_mon and offset registers retained | Same | Same | Monitor counters are held, not cleared (EYM Table 9-2) | CDR-006 |
| Idle state | pi_mon and CK_MON keep running at the parked position (k_mon = 0, offset 0) when the monitor is disabled; no power-down in mission mode | — | — | Constant activity: supply signature and coupling into the data path do not change with monitor state (EYM Table 9-1 item 2) | EYM |
| Dual-rate | Same structure at 6.64 GHz; piTable_mon and phase_zero_mon per mode | — | — | CMP-009 parameter set | CMP-009 |
| Power | TBD — working estimate 3 mW (rotator + branch + monitor DMUX first stage) | ≈ 0.03 pJ/bit | TBD | Table 12-1; the monitor slice itself is EYM Table 11-1 | SYS-008 |
| Test access | pos_mon readback and override; phase-step measurement against the data phase through the monitor itself | — | — | Also the DNL / INL characterisation path of the data PI (Table 9-3) | DFT |

**Table 9-5. Monitor-clock obligations toward the data path (clocking half of the EYM non-intrusiveness constraints)**

| **Item** | **Obligation** | **Basis / verification** | **Req** |
| --- | --- | --- | --- |
| Coupling into the data sampling phase | Induced phase modulation on CK8_PI[7:0] ≤ 10 fs pp (≈ 0.001 UI) at any pos_mon, in both modes — working target | pi_mon sweeps every phase relationship to the data clock during a scan, so supply / substrate coupling from the monitor branch is exercised at every relative phase and must stay far below the Table 8-3 allocations. Verification: sweep pos_mon over 256 positions while the on-die TIE monitor observes the data phase (Table 13-1) | EMC-003, DTX-010; EYM Table 9-1 |
| Isolation measures | Separate regulated / filtered supply for pi_mon and the monitor clock branch; return-path separation; routing keep-out from the CK8_PI tree and the mission slice clock buffers | CDNS layout deliverable | ROB-004 |
| Static load on the CK8 set | pi_mon’s input load on CK8[7:0] present and constant regardless of monitor state; monitor enable / disable shall not change the phase or duty of any CK8_PI phase | The pi_mon input load is part of the set that Table 8-2 calibrates | Table 8-2 |
| Word alignment | Monitor DMUX word boundary aligned to the CK_WRX word of slice k_mon; re-aligned on every change of k_mon; unaffected by the fine offset across the full ±16-code range | Pairing of m(n) with d(n) is unambiguous for │offset│ ≤ 0.5 UI (Table 8-4; EYM Table 4-2) | EYM Table 6-1 |
| Metastability retiming | Two-stage retiming of the monitor comparator output into the CK_WMON domain, resolving to a legal ±1 without disturbing adjacent bus lanes | The monitor is deliberately parked at decision boundaries, so metastable outputs are the normal case | EYM Table 6-1 |
| Verification | pos_mon accuracy vs. the data phase over 256 positions; offset range; skew calibration convergence; monitor-unique jitter; coupling sweep; alignment across k_mon changes | Table 13-1 rows “Monitor PI”; EYM Table 12-1 | EYM |

# 10. Dual-Rate Operation and Mode Change (CMP-005, CMP-009)

Backward compatibility with OCI Gen1 partners is a product requirement: the PLL, serializer, and CDR shall operate at both bauds with ±50 ppm tolerance (CMP-005). The clock chain meets this with one hardware set and a mode divider; every mode-dependent clocking parameter is part of the CMP-009 parameter set reloaded before the port is enabled.

**Table 10-1. Mode-dependent clocking parameters**

| **Parameter** | **400G OCI mode** | **200G OCI mode** | **Owner / notes** |
| --- | --- | --- | --- |
| VCO frequency | 53.125 GHz | 53.125 GHz | Unchanged — no re-tune, no re-lock (Table 2-4) |
| Mode divider | ÷1 | ÷2 | Clocking; the only hardware switch |
| CK_HR | 53.125 GHz | 26.5625 GHz | Period = 2 UI in both |
| CK8 / clk8 | 13.28125 GHz, 9.412 ps spacing | 6.640625 GHz, 18.824 ps spacing | Same ÷4 |
| PI LSB | 294 fs | 588 fs | 1/32 UI in both; piTable per mode |
| 8-phase calibration set | Per mode | Per mode | Delay-DAC codes differ with the clock period |
| DCC target | 50 % ± 0.2 pt (limit ± 0.3 pt) | 50 % ± 0.2 pt (limit ± 0.3 pt) | JIT-D3; UI-relative; loop operates at both clock rates |
| Word clocks CK_WTX / CK_WRX | 830.078 MHz (W = 128) | 415.04 MHz (W = 128) — or 830 MHz with W = 64 | Open item 7; digital timing closure at 830 MHz covers both if W = 64 is chosen |
| CDR update period | 128 UI = 1.205 ns | 128 UI = 2.41 ns (W = 128) | CDR-001 doc |
| CDR gain set | Mission / acquisition sets | Separate sets — per-UI gains give half the bandwidth in Hz at twice the UI, so 200G-mode gains must be re-derived to hold the 4–6 MHz window | CDR-001, CDR-007, CMP-009 — CDR document deliverable, noted here as a clocking consequence |
| Jitter allocations in UI | σ_RJ ≤ 0.011 UI = 104 fs | ≤ 0.011 UI = 207 fs (hardware ≈ 90–103 fs) | CMP-007; ≈ 2× margin in 200G mode |
| Spur limit | −42 dBc at CK_HR (working) | −42 dBc at CK_HR (working) | Table 3-4; verified in both modes (EMC-004) |
| JTOL corner cross-check | 4 MHz (802.3dj Table 176D-10) | ≈ 4.0 MHz (CEI-112G-XSR f_b/13280) | DRX-006, CMP-005 |

**Table 10-2. Mode-change sequence (clocking entries; the port is disabled throughout)**

| **Step** | **Action** | **Domain / Req** |
| --- | --- | --- |
| 1 | Host provisions the mode per port through the management interface; the port is disabled or squelched (no mission data) | Management; CMP-001, CMP-011 (no autonomous change) |
| 2 | Firmware loads the CMP-009 parameter set for the target mode: mode divider, DCC target, 8-phase calibration codes, piTable and piTable_mon, phase_zero_mon[0 … 7], CDR gain sets, word-width configuration | Management; CMP-009, MFG-003 |
| 3 | Mode divider switches; CK_HR, CK8, and word clocks settle (no PLL re-lock required since the VCO is unchanged; PLL lock flag shall stay asserted) | Clocking; CMP-005 |
| 4 | DCC re-converges on the new CK_HR; 8-phase calibration verified against the stored set (foreground check if the bring-up sequence allows) | Clocking; SYS-007 |
| 5 | CDR reset to acquisition presets (init_pi, frequency register cleared); adaptation loops frozen at presets | CDR-001 doc; ADP-001 |
| 6 | Port enabled; SYS-007 bring-up proceeds (ELS, ring acquisition, deskew training at the new baud) | SYS-007, LOG-004 |

*The mode is fixed for the duration of a link session (CMP-011); the sequence above is never executed autonomously. Because the VCO does not move, the mode change does not consume PLL lock time, which keeps the SYS-007 time-to-traffic budget identical in both modes.*

# 11. Supply, Robustness, and EMC Interfaces

**Table 11-1. Interfaces the clock chain must satisfy toward the productization families**

| **Interface** | **Obligation** | **Req** |
| --- | --- | --- |
| Supply-induced jitter / PSRR | PSRR per clock rail (VCO / charge pump, distribution, PI, slice clock buffers) derived over the noise bandwidth from the ROB-004 PDN transient mask so that broadband PSIJ fits inside the Table 3-1 allocations (45 fs distribution, 72 fs PLL, 50 fs PI) and periodic PSIJ inside the Table 3-4 spur allocation; heater-rail ripple excluded from every clock rail; regulated rails for the VCO and PI | DTX-010, ROB-004 |
| Rail tolerance and transients | All clocking specifications met with every rail at ±5 % (or the tighter declared tolerance); PDN transients within the declared mask shall not unlock the PLL, corrupt calibration codes, or move the PI code | ROB-004 |
| Brownout | Reference loss or PLL unlock detected on every rail excursion forces the REG-008 safe state (TX squelched / disabled, heaters safe) before logic becomes indeterminate; recovery re-enters the bring-up sequence | ROB-003, REG-008, SYS-005 |
| Clock purity | No spread-spectrum on the line clock; spur limits per Table 3-4 verified at the PLL output and serializer output across PVT in both modes | EMC-004 |
| Crosstalk — clock as aggressor | CK_HR (53 / 26.6 GHz), CK8 (13.3 / 6.6 GHz), and their harmonics coupling into the TIA input, the slice inputs, and the TP1 nets shall be budgeted inside the aggregate crosstalk allocation (BUJ ≤ 339 fs at TP1 and the RX eye budget); shielded routing and defined return paths | EMC-003 |
| Crosstalk — clock as victim | Data-dependent switching of the serializer and drivers (all four lanes active, worst-case tap codes) shall not couple into the PLL, distribution, or PI beyond the Table 3-4 periodic-jitter allocation | EMC-003, EMC-004 |
| Radiated emissions | The 53.125 GHz clock and its harmonics are part of the chiplet emissions budget; on-package containment (layout, shielding, return path) is a chiplet responsibility | EMC-001 |
| Immunity | Under IEC 61000-4-3 / -4-6 class stress: no PLL unlock without recovery, no unrecoverable state; degradations flagged through the fault structure and recovered by the permanently armed relink logic | EMC-002, BUP-003 |
| ESD | Reference-clock input pads (if on external microbumps) withstand ≥ 250 V CDM | ROB-001 |
| Wearout | Continuously oscillating VCO, 53 GHz buffers, and 13 GHz slice clocks signed off for ≥ 100 000 power-on hours at the declared mission profile (400G mode worst case) | ROB-007 |
| Soft errors | Calibration registers (piTable, phase DACs, DCC, coarse-tune code) and the mode-divider setting protected (parity / ECC) so that an SEU cannot silently move the sampling phase, change the mode, or unlock the PLL unflagged | REL-005 |
| Squelch and dark-fiber behaviour | Clocks keep running during TX park and during RX signal-invalid; the PI holds (CDR-006); no clock gating that would require re-calibration on exit | SQL-001, CDR-006, DRX-008 |

# 12. Power and Area Summary

The only quantified estimate is the CDNS interleaved-RX architecture study (100 mW per channel = 0.94 pJ/bit at 106.25 Gb/s), of which the RX PLL and clock buffers are the clocking share. TX-side clocking power is an owner deliverable; if the per-channel PLL is shared between TX and RX (baseline), the 60 mW covers both directions.

**Table 12-1. Clocking power and area (per channel)**

| **Block** | **400G OCI mode** | **200G OCI mode** | **Status / notes** |
| --- | --- | --- | --- |
| LC-PLL (“RX PLL” in the architecture estimate) | 60 mW = 0.56 pJ/bit | ≈ 60 mW = 1.13 pJ/bit (does not scale) | CDNS estimate; shared TX / RX in the baseline (Open item 4) |
| Clock buffers — distribution, ÷4 8-phase generator, PI, slice clock buffers (“CLK buffer”) | 15 mW = 0.14 pJ/bit | TBD (partly scales with clock rate) | CDNS estimate |
| Monitor PI pi_mon, monitor clock branch, monitor DMUX first stage (eye monitor) | TBD — working estimate 3 mW = 0.03 pJ/bit | TBD | Section 9.4; not in the architecture estimate. The monitor slice itself (replica buffer, S/H, comparator, DACs ≈ 2.5 mW) is EYM Table 11-1 |
| Subtotal — RX clocking | 75 mW = 0.71 pJ/bit (78 mW with the monitor clocking) | ≈ 1.4 pJ/bit if unchanged | Feeds the SYS-008 pJ/bit target per mode |
| DMUX (for reference) | 5 mW | TBD | RX logic; quoted from the same estimate |
| Comparators, 24 (for reference) | 10 mW | TBD | RXF Section 8; quoted from the same estimate |
| CTLE-even / odd buffers in the CDNS EIC (for reference) | 10 mW | TBD | RXF Section 8; quoted from the same estimate |
| RX EIC total (architecture estimate) | 100 mW = 0.94 pJ/bit | — | Excludes the LM TIA / CTLE macro (RXF Table 10-1: 0.4 pJ/bit = 42.5 mW) |
| TX PLL (if separate from the RX PLL) | TBD (0 if shared) | TBD | Open item 4 |
| TX clock distribution, DCC, serializer clocking | TBD | TBD | CDNS deliverable; serializer data path power is tallied in TXD |
| Reference-clock receiver (per port, shared) | TBD | TBD | Amortised over four channels |
| Area | TBD — LC tank dominates; one tank per channel in the baseline | — | A shared per-port PLL trades tank area for a 53 GHz tree |

*The PLL and buffer power does not halve in 200G mode, so the clocking pJ/bit roughly doubles there; SYS-008 sets separate targets per mode.*

# 13. Verification

TP1 is unprobeable and the 53 GHz internal clock nodes are not bench-accessible either: S = extracted-view simulation, O = on-die instrumentation (phase / jitter monitor at the serializer output, per-slice eye statistics, DCC and calibration readback, PLL test port), V = test vehicle (PLL macro and slice-clock macro with probe access), T = system test, A = analysis.

**Table 13-1. Verification matrix**

| **Req** | **Item** | **Method** | **Condition** | **Pass criterion** |
| --- | --- | --- | --- | --- |
| SYS-001 | Frequency plan and dual-rate chain | I | Tables 2-2, 4-1, 10-1 reviewed against the D2D selection | Documented; integer N; same f_ref in both modes |
| SYS-002 / ELE-005 | PLL integrated phase noise | V / S / A | PLL macro on the test vehicle, 4 MHz first-order high-pass to f_baud/2, PVT, both dividers (method of JIT-001 Table 7-2, SYS-002 row) | ≤ 72 fs rms working (≤ 100 fs first cut) at 53.125 GHz; ≤ 65 fs at the ÷2 output; chain RSS ≤ 104 fs |
| ELE-005 / DTX-001 | Clock-chain σ_RJ roll-up at the serializer output | S / A | PLL + distribution + mux RSS from extracted simulation; returned to TXD Table 3-2 | ≤ 104 fs rms (400G); ≤ 207 fs (200G) |
| ELE-002 / 004 | Clock-only JHRMS / JH4u at the serializer output | S / O | PRBS13 / PRBS31, 4 MHz CRU, PVT | JRMS ≤ 216 / 433 fs; J4u ≤ 1.11 / 2.22 ps (clock share) |
| ELE-003 | Half-rate duty cycle and DCD | S / O / V | DCC engaged, PVT, both clock rates; even/odd crossing separation at the serializer output | D = 50 % ± 0.2 pt target, ± 0.3 pt limit (JIT-D3); DCD_duty ≤ 0.004 UI target / 0.006 UI limit (38 / 56 fs in 400G, 75 / 113 fs in 200G) |
| EMC-004 | Spurs and SSC | V / S / O | PLL output and serializer output; all lanes active, worst-case tap codes; PVT; both modes | Power-summed spurs above 4 MHz ≤ −42 dBc at CK_HR; no spread-spectrum |
| DTX-010 | PSIJ / PSRR | S / V | Rail noise masks per the PDN specification injected on each clock rail | Broadband PSIJ inside the Table 3-1 allocations; periodic inside Table 3-4 |
| EYM / DFT-003 | Monitor PI position and offset (Table 9-4) | S / V / O | pos_mon swept over 256 positions at a fixed data position; k_mon 0 … 7; offset −16 … +15; both modes; skew calibration run to convergence | Static skew to CK8_PI[k_mon] ≤ ±2 codes uncalibrated, ≤ 0.25 code after phase_zero_mon; monotonic steps; word alignment held across the sweep and re-established after every k_mon change |
| EYM | Monitor-clock coupling (Table 9-5) | S / V / O | pos_mon sweep while the on-die TIE monitor observes the data phase; monitor enable toggled; both modes | ≤ 10 fs pp induced on CK8_PI; no change of CK8_PI phase or duty with monitor state |
| EYM | Monitor-unique jitter (Table 9-4) | S / V | pi_mon + monitor branch, PVT, both dividers | ≤ 50 fs rms working |
| SYS-007 | PLL lock time, coarse calibration, phase and PI calibration time | V / T | Reference valid → lock; cold and warm starts; both modes | Inside the SYS-007 time-to-traffic budget; lock flag correct |
| CDR-001 / DRX-006 | JTOL with the PI as actuator | T / S | Full 802.3dj / CEI-112G-XSR mask at both bauds, PRBS31 with 72-UI CID runs, both modes | BER ≤ 2.4E-4 at every mask point; untracked SJ ≤ 0.10–0.15 UI pp |
| CDR-002 / CDR-004 | Continuous rotation and wrap | T / S | ±200 ppm (and ±244 ppm code-ramp) both directions, PRBS31, FEC 17-bin counters | No bit errors, no bin-histogram excursion, no bit slip at any wrap |
| Section 9 | PI transfer characteristic | V / O | All 256 positions, PVT, both modes; phase-step measurement | Monotonic; DNL ≤ ±0.5 LSB; INL ≤ ±1 LSB after calibration; K_PI variation inside the CDR-001 window |
| Section 9 | PI jitter and code-change glitches | S / V | Code steps of 1–2 codes (mission) and acquisition steps at 830 MHz update rate | ≤ 50 fs rms intrinsic + DNL; no created, duplicated, or suppressed sampling edge |
| CDR-006 / RXO-007 | PI hold and warm re-acquisition | T | signal_valid de-asserted ≥ 50 ms, temperature ramp; then re-asserted | Phase drift ≤ 1 LSB; lock re-asserted without cycle slip |
| Section 8 | 8-phase static skew and duty cycle | V / O | All eight phases against the 1-UI grid after calibration; PVT; both modes | Residual skew ≤ 0.02 UI pp (188 / 376 fs); duty within Table 8-2 |
| Section 8 / RXF §8 | Track, hold, and charge-share settling | S | Extracted slice front end with the 8-phase timing; 2-of-4 tracking; worst-case data | Settling within 2 UI to the RXF Table 8-3 error allocation; no aperture-induced ISI beyond budget |
| Section 8.4 | RX horizontal eye terms | A | Clock-chain RJ, skew, PI INL, dither, untracked SJ summed into the RX eye analysis | Margin at 2.4E-4 and 1e-12 per the Rev 0.7 §9 RX eye budget |
| ELE-007 / 008, CMP-007 | Branch-phase generation | S | Both bauds; PVT | Delays 0 / 9.41 / 18.82 ps and 0 / 18.82 / 37.65 ps within the TXD Table 6-3 accuracy; skew inside the ELE-008 0.24 ps TP1 matching |
| SQL-001 | Clocks during park | S / T | Serializer parked; squelch entry / exit | PLL, DCC, and calibrations hold; glitch-free exit (SQL-005) |
| CMP-005 / CMP-009 | Mode change | T | Table 10-2 sequence in both directions | PLL stays locked; parameter set reloaded before enable; CDR acquires at the new baud |
| EMC-003 | Clock crosstalk | S / V | All lanes active; TIA input and TP1 victims; PRBS31 uncorrelated | Contribution inside the BUJ 339 fs and RX eye allocations |
| ROB-007 | Wearout of continuously toggling clock paths | A | Mission profile, 400G mode | ≥ 100 000 h |

# 14. Open Items and Owner Deliverables

**Table 14-1. Open items**

| **#** | **Item** | **Owner** | **Dependency / closure** |
| --- | --- | --- | --- |
| 1 | Clock-chain σ_RJ re-partition to ≤ 104 fs rms — closure vehicle for JIT-001 Rev 0.2 Open item 1. JIT-D4 is answered here (no PI in the TX clock path, Table 7-1), so the JIT-001 Table 5-1b variant “No PI in TX path” applies: first cut 123 fs, 1.19× (1.5 dB) over; the 72 / 45 / 30 fs working targets (90 fs) are one closing re-partition. CDNS to confirm the branch-phase method in TXD Table 6-3 (a PI-class delay element would move the chain to the 130 fs variant and book PI DNL in DJ_δδ) and commit the per-block values; the refclk phase-noise specification follows (Open item 2). Binding risk R8; return the roll-up to TXD Table 3-2 and JIT-001 Table 5-1 | CDNS / link budget | PLL macro simulation and test vehicle; SYS-002; JIT-001 Open item 1 |
| 2 | Reference-clock frequency and multiplication ratio (candidates N = 64 / 32 / 16), physical form per the D2D selection, and the resulting refclk phase-noise and spur specification toward the host (SYS-002 deliverable) | CDNS / system architecture | D2D interface selection (SYS-004); Table 5-2 mask |
| 3 | Dual-rate method: fixed 53.125 GHz VCO with ÷2 (baseline) vs. re-tuned VCO; confirm the divider jitter term and that no re-lock is needed on mode change | CDNS | CMP-005; Table 10-2 |
| 4 | PLL instances: one shared TX / RX PLL per channel (baseline) vs. separate TX / RX PLLs vs. one TX PLL per port; power (60 mW per channel), serializer-to-RX coupling, inter-channel skew | CDNS / system architecture | SYS-008 pJ/bit target; EMC-003 isolation analysis |
| 5 | PI topology: 8-phase rotator (baseline, seamless wrap) vs. 1-UI DLL delay element (Option B) with DMUX bit-slip correction; reconcile n_pi_codes / pi_span_ui and the pair-select carry with DES-OCI-106G-CDR-001 Sections 3.1 / 5.1 | CDNS / CDR | CDR-001 doc update; Table 9-2 |
| 6 | RX eye budget clocking terms: 8-phase residual skew target (≤ 0.02 UI working), RX sampling-chain RJ (≈ 100 fs), PI INL, and the ÷4 divider term to be added to RXF Table 8-3 and to the DRX-004 statistical-eye analysis; calibration method — the eye monitor with slice select is the proposed observable (Section 9.4; EYM Table 8-1) | CDNS / RX analog / adaptation | Rev 0.7 §9 RX eye budget; RXF Open item 9; EYM |
| 7 | 200G-mode word width: W = 128 (415 MHz word clocks, baseline) vs. W = 64 (830 MHz); cdr_width / f_div pairing and the 200G CDR gain sets that hold the 4–6 MHz window | CDR / logic | CDR-001 doc; CMP-009 |
| 8 | DCD (narrowed): the partition is fixed by JIT-001 Table 5-3c / JIT-D3 — driver rise/fall 0.35 ps (0.0186 UI) held, DCC design target ± 0.2 pt (0.004 UI) with ± 0.3 pt (0.006 UI) as the limit. Remaining: DCC loop bandwidth, convergence at both clock rates, and a duty monitor with resolution ≤ 0.05 pt able to demonstrate the target | CDNS | Table 6-1; ELE-003; JIT-D3 |
| 9 | BUJ split between periodic (spur) jitter and crosstalk: −42 dBc for 0.010 UI pp (equivalent aggressor 14 mV of the 51 mV sum of JIT-001 Table 5-5) is the working allocation; confirm against the EMC-003 extracted-crosstalk result with all four lanes active (JIT-001 Open item 5) | CDNS / EMC | ELE-005, EMC-003/004; JIT-001 Table 5-5 |
| 10 | Slice front-end timing closure with the 8-phase clock: charge-share settling within 2 UI, track-window margin with duty-cycle error, sampling-edge transition time, S/H hold-mode bandwidth and kickback | CDNS (slice) / RX analog | RXF Tables 8-1 / 8-2 (Open item 9 there) |
| 11 | PSRR per clock rail from the ROB-004 PDN transient mask; regulated rails for VCO and PI | CDNS / PDN | DTX-010; PDN specification |
| 12 | PLL tuning range, K_VCO, coarse-calibration strategy across the cold-plate range (hitless re-calibration or none), lock time | CDNS | SYS-006 thermal envelope; SYS-007 |
| 13 | PI parameters marked TBD or working in Table 9-1: DNL / INL, K_PI variation, hold drift, acquisition step size, code-to-phase latency; calibration procedure and NVM layout | CDNS / CDR / firmware | MFG-003; CDR-007 |
| 14 | On-die instrumentation set: serializer-output TIE / jitter monitor, DCC readback, the RX eye monitor with slice select as the RX eye / phase observable (EYM), PI phase-step measurement (absolute-mode monitor, Table 9-4), PLL test port — sufficient for ELE-001 / EMC-004 verification without physical access | CDNS / DFT | DFT plan; ELE-001; EYM |
| 15 | Power: TX clocking power, reference receiver, 200G-mode clocking pJ/bit; area of one LC tank per channel | CDNS | SYS-008 roll-up |
| 16 | Behavioral / extracted 200G-mode regression of all Table 13-1 items at 53.125 GBd | Verification | CMP-005 |
| 17 | Monitor phase interpolator (Section 9.4): uncalibrated skew bound (±2 codes), pair-to-pair skew, monitor-unique jitter (50 fs), coupling limit (10 fs pp), settling time after reprogramming (mon_settle), the k_mon word-alignment mechanism, and the absolute-mode override to be confirmed by CDNS; values delivered to DES-OCI-106G-EYM-001 Tables 4-1 / 6-2 / 12-1 (EYM Open item 3) | CDNS / EYM | DES-OCI-106G-EYM-001; extracted clock-distribution design |

*End of DES-OCI-106G-CLK-001 Rev 0.2.*

DES-OCI-106G-CLK-001 Rev 0.2 | DRAFT | Page  of