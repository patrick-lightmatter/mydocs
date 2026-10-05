DES-OCI-106G-SQL-001 Rev 0.2 | Companion to ARCH-OCI-106G-001 Rev 0.7 | SQL Design Specification

**400G OCI Line-Side SerDes Chiplet**

TX Squelch and Loss-of-Modulation — Design Specification

*Companion to ARCH-OCI-106G-001 Rev 0.7 | Design decomposition of the SQL and LOM families, BUP-003/004, TXO-010 | Both squelch triggers (relink handshake / invalid electrical input)*

| **Document ID** | DES-OCI-106G-SQL-001 |
| --- | --- |
| **Revision** | 0.2 (Draft for review) |
| **Date** | September 21, 2026 |
| **Status** | DRAFT. Design companion to ARCH-OCI-106G-001 Rev 0.7. Where this document and Rev 0.7 differ, Rev 0.7 governs. Design confidence: Low. Significant partner dependencies are unresolved (Section 10). Requirement numbering in Sections 1.3–10 (SQL-001..012) predates ARCH-OCI-106G-001 Rev 0.6 and does not match its SQL-001..005 / LOM-001..004; values are 200G-mode only. Both are corrected in the next revision (ARCH-OCI-106G-001 Rev 0.7 Section 9, “SQL-001 re-base”); until then the ARCH-OCI-106G-001 text governs wherever the two differ. |
| **Parent requirements** | SQL-001..005 and LOM-001..004 (Rev 0.7 §6.7–§6.8; the SQL-001..012 numbering used in the body of this revision predates Rev 0.6 and is re-based in the next revision — see Status); TXO-010 (constant-AOP squelch, OCI Gen1 v1.0 Table 2-2 note 4, Tsq_channel ≤ −15 dBm per channel); OCI Gen1 v1.0 Table 1-3 (relink_squelch_tx_duration 60–75 ms); BUP-003/004 (relink on loss of lock / loss of modulation); LOM-003 (persistence window ≥ 1 µs); LOM-004 (signal_valid hand-off to CDR and adaptation). |
| **Sibling documents** | DES-OCI-106G-TXD-001 — TX Pre-Driver and Driver; DES-OCI-106G-CDR-001 — CDR Design Specification; DES-OCI-106G-ADP-001 — Adaptation Loops. |
| **Governing specifications** | OCI Gen1 Optical PHY Specification v1.0 Table 1-3 and Table 2-2 n.4; DJI-003 (PMD transmit-disable); RXO-006 (far-end LOS threshold −14 dBm AOP); BUP-003/004 (relink trigger on loss of modulation). |
| **Scope** | TX squelch behavior spanning pre-driver source mux, driver swing-mute and DC-bias path, per-channel MRM squelch bias (V_sq), and heater-servo interface; TxSquelchSeq sequencer state machine; V_sq calibration procedure; loss-of-modulation detector design for the far-end RX. Per channel; four instances per fiber port; lane-atomic operation across the WDM group. |
| **Out of scope** | Heater-servo architecture and lock-detector design (TBD_from_partner); TX PLL and serializer circuit design (SYS-001/002); ELS / PMD transmit-disable path (future management-plane section); link-controller relink timing and deskew state machine (BUP/LOG family); TX disparity checker algorithm (Rev 0.7 §9). |

| **Revision** | **Date** | **Change summary** |
| --- | --- | --- |
| 0.1 | September 18, 2026 | Initial issue. Design decomposition of the TX squelch and loss-of-modulation requirements per ARCH-OCI-106G-001 Rev 0.6. Mermaid block diagram and stateDiagram replaced by block-partition and state-transition tables. Python sequencer pseudocode replaced by ordered-step tables. SQL-002 updated to reflect drop-port-as-servo-observable with launched per-channel power as normative quantity (technical correction: through-path bus tap is broadband and cannot attribute per-channel power in the four-DWDM shared-bus architecture; two-point drop-port calibration now required). Loss-of-modulation detector defined in Section 6. |
| 0.2 | September 21, 2026 | Re-pinned to ARCH-OCI-106G-001 Rev 0.7 (hub revision; its Section 1.7 indexes this document). Predecessor-document references removed throughout per the OCI 106G document-structure convention: the Status field now states scope and confidence only; provenance statements are replaced by citations of the owning document in the set or by open items; cross-references into DES-OCI-106G-CDR-001 converted from legacy §6-x numbering to its Section numbers. No technical values changed. |

# 1. Introduction

## 1.1 Purpose

This document is the design decomposition of the TX squelch requirements of ARCH-OCI-106G-001 Rev 0.7 (SQL-001..012) together with the loss-of-modulation detection requirements (LOM-003/004, BUP-003/004). It fixes the sequencer architecture, state machine, per-channel V_sq calibration, timing budgets, and block interfaces so that firmware, RTL, analog design, and verification share one definition, and maps each behavior back to its requirement.

Squelch is the modulation-suppressed, power-preserving TX state mandated by TXO-010: launched OMA ≤ −15 dBm per channel while average launched power remains constant within ±0.5 dB of the pre-squelch mission value. It is a protocol signal, not an idle convenience. Two PMA uses share the same optical signature: the OCI relink handshake (squelch_cmd asserted by the link controller for relink_squelch_tx_duration, followed by glitch-free transition to the 160-bit deskew training pattern) and invalid-electrical-input hold (TX stream not mission data; the same mute preserves average optical power so the thermal-tuning loop does not unlock at either end of the link).

Squelch is architecturally distinct from PMD transmit disable (DJI-003). Transmit disable removes optical power via the ELS/laser path and does not preserve average power. Squelch shall never be implemented by ELS power reduction, heater park, or laser blanking (SQL-011). This sequencer shall not be reused for the transmit-disable path; the distinction is recorded here so a later management-plane section cannot cross-reference this document as authorization.

## 1.2 Conventions

| **Item** | **Convention** |
| --- | --- |
| Requirement references | FAMILY-NNN (e.g. SQL-003) refers to the requirement of that ID in Rev 0.7. Section references of the form §x.y without a family prefix are to Rev 0.7; “Section x.y” without prefix refers to this document. |
| Symbols | Configuration and signal names appear in monospace (squelch_cmd, src_sel, swing_mute, v_sq). Names are shared by the behavioral model and the RTL. |
| “DAC” | Any digital code that sets an analog operating point — a programmable knob, not necessarily a voltage or current converter. swing_mute, v_sq, and the heater code are three different DACs on three different nodes. Squelch may write the first two; it shall not write the heater code (§7.9 rule 1, SQL-008). |
| Owners | CDNS — serializer, pre-driver source mux, and glitch-free src_sel deliverable. LM — TX driver swing-mute and DC-bias-path independence, voltage-mode mute realization. Partner — heater-servo architecture, lock detector, monitor-photodiode path and calibration. Owner-tagged entries are tracked as open items in Section 10. |
| AOP | Average Optical Power at the TX fiber reference plane (TP2), per channel, single polarization, unless stated otherwise. |
| Lane group | All WDM lanes of a PMA group. squelch_cmd is asserted and deasserted lane-atomically across the group (SQL-012). Per-lane squelch is a test-mode hook only. |
| Placeholders | TBD = value tracked in the requirements database; not yet fixed by analysis or partner delivery. Section 10 lists the open items and owner deliverables. |

## 1.3 Parent requirement map

**Table 1-1. Rev 0.7 requirements satisfied or interfaced by this document**

| **Req ID** | **Rev 0.7 obligation (abridged)** | **Design response** | **Section** |
| --- | --- | --- | --- |
| **SQL-001** | Squelched OMA ≤ −15 dBm (Tsq_channel); pre-driver + driver ≥ 20 dB electrical suppression → ≥ 14 dB optical vs. §8.2 max OMA −1 dBm. | Entry sequence ramps swing_mute to MUTE in ≤ 1 ms; combined mute target is the ≥ 20 dB suppression design goal (Table 3-2); residual feedthrough floor must stay below −15 dBm. | 3, 5 |
| **SQL-002** | AOP constant within ±0.5 dB of pre-squelch mission Pavg; far-end demux-filter lock held; squelch shall not trigger far-end LOS (RXO-006 −14 dBm AOP). Drop port is the servo observable; launched per-channel power is the normative quantity, bridged by a two-point calibration. | V_sq calibrated against drop port to land static transmission at mission-average launched power; separate parked-drive calibration point required. Bus-tap monitor demoted to cross-check role. | 4, 5 |
| **SQL-003** | Glitch-free three-way src_sel (mission / deskew / hold); serializer and TX PLL run continuously; source transitions phase-continuous. | Source mux is a glitch-free synchronous three-way switch on the serializer clock (Table 2-2); TX PLL and serializer never stop. | 2.3, 3 |
| **SQL-004** | Pre-driver mute holds CM and duty-cycle balance; any CM step at driver input settles within the SQL-002 AOP window. | Pre-driver CM and DCD balance held through mute entry/exit; explicit constraint added to the CDNS §3.1 interface obligation. | 2.3 |
| **SQL-005** | Driver swing muted while independently preserving MRM DC bias; DC operating point shall not move when RF swing is removed. Mute entry/exit ≤ 1 ms. Voltage-mode realization TBD_analog_design; supply-collapse mute prohibited. | Driver swing path and DC bias path are independent nodes (Table 2-3); supply-collapse and shared swing/bias control are prohibited; FIR tap weights not changed by swing_mute so exit is hitless. | 2.4, 3 |
| **SQL-006** | Per-channel calibrated V_sq such that static transmission equals modulated-state average. Factory + in-service re-trim against the TX drop-port monitor photodiode. | V_sq is a factory-set, periodically re-trimmed per-lane calibration quantity; two-point drop-port calibration required. | 4 |
| **SQL-007** | Junction remains in depletion at V_sq. Residual resonance shift inside heater linear capture range. | V_sq operating-regime containment is a design constraint on the calibration procedure and V_sq sweep range. | 4.2 |
| **SQL-008** | Heater servo remains closed-loop through entry/dwell/exit on monitor-PD average power; dither continues, amplitude bounded vs. SQL-001. | Heater servo stays closed throughout; squelch freezes integrator ramp limits (transient guard only) but does not freeze integrator state or open the loop. | 3.3, 3.5 |
| **SQL-009** | Servo absorbs RF-removal/restoration thermal step with zero unlock; residual detuning inside mission budget in ≤ 10 ms (target), inside the 60 ms minimum dwell. | Thermal-step settle target t_heater_squelch_settle ≤ 10 ms; 60 ms minimum dwell provides 50 ms guard margin. | 5 |
| **SQL-010** | Sequencing satisfies OCI Gen1 v1.0 Table 1-3: squelch for relink_squelch_tx_duration (60–75 ms) then glitch-free 160-bit training; far end detects mute within t_loselock ≤ 50 ms. | State machine drives the 60–75 ms dwell and phase-continuous exit to deskew training; PMA does not insert any gap between squelch exit and the start of the training pattern. | 3, 5 |
| **SQL-011** | Architecturally distinct from PMD transmit disable: disable removes AOP via ELS; squelch preserves AOP. Never implement squelch by ELS attenuation, heater park, or laser blanking. | Stated as a design prohibition in Section 1.1; ELS disable path is explicitly out of scope. | 1.1 |
| **SQL-012** | All WDM lanes of a PMA group enter/exit together (lane-atomic). Per-lane squelch is test-only. | squelch_cmd is lane-atomic across the group; per-lane override is a test-mode register hook. | 7 |
| **LOM-003** | Loss-of-modulation detection persistence ≥ 1 µs (far end). | Persistence window lower bound ≥ 1 µs per LOM-003; upper bound well below t_loselock ≤ 50 ms; design in Section 6.3. | 6.3 |
| **LOM-004** | signal_valid de-asserted on loss of modulation; CDR and adaptation loops hold state. | loss_of_modulation flag asserts signal_invalid, gating the CDR (DES-OCI-106G-CDR-001 §10) and all adaptation loops (DES-OCI-106G-ADP-001 §3.2). | 6 |
| **BUP-003** | Relink triggered on CDR loss of lock or loss of modulation. | loss_of_modulation flag feeds the relink-trigger branch at the deskew state machine. | 6.4 |
| **BUP-004** | Loss-of-modulation detector distinct from LOS detector; separate flags drive separate relink branches. | LOS (AOP below threshold; RXO-006 monitor path) and loss-of-modulation (AOP above threshold AND modulation metric below threshold) are independent conditions reported on separate flags. | 6.2 |

# 2. Architecture and Partition

## 2.1 Signal chain

TX squelch spans five blocks in the transmit path plus the heater servo and the disparity checker. Table 2-1 fixes block nomenclature and squelch-mode roles; all blocks are per-channel with four instances per fiber port. Figure 2-1 (Section 2.2) draws the signal chain and the control overlay.

**Table 2-1. Squelch-relevant blocks (per channel)**

| **#** | **Block** | **Mission role** | **Squelch-mode role** | **Owner** | **Req** |
| --- | --- | --- | --- | --- | --- |
| **1** | TX PLL and serializer | Full-rate NRZ serialization; clock never stops | Continues running; only data content changes; src_sel steers the source, not the clock | CDNS | SYS-001, SQL-003 |
| **2** | Pre-driver source mux (TxSourceMux) | Passes mission data to the driver | Glitch-free three-way switch — MISSION / DESKEW / HOLD; synchronous to the serializer clock | CDNS | SQL-003, SQL-004 |
| **3** | TX driver — swing path | RF swing drives the MRM through the modulation window | swing_mute → MUTE; FIR tap weights held at mission values; entry/exit ≤ 1 ms | LM | SQL-001, SQL-005 |
| **4** | TX driver — DC bias path | V_bias (mission DC reverse-bias −1.5 to −2.0 V) | Independent of swing path; v_sq applied at ENTER step E5 and released at EXIT step X3 | LM | SQL-005, SQL-006 |
| **5** | MRM and drop-port monitor PD | Carrier-depletion modulation; drop-port photocurrent is the per-channel servo observable | Static drive at v_sq; drop-port current calibrated to equal mission-average launched power (two-point calibration); heater servo runs closed-loop | Partner / Photonics | SQL-002, SQL-006..009 |
| **6** | Heater servo (thermal-tuning loop) | Closed-loop lock on drop-port average power | Continues closed through entry/dwell/exit; integrator ramp limits frozen at entry/exit (transient guard only); dither at squelch profile | Partner | SQL-008, SQL-009 |
| **7** | TX disparity checker (TxDisparityNrz) | Observe-only mission-data density monitor | meas_valid forced low; disp_flag held; accumulators cleared on exit; not used as a squelch error signal or substitute servo observable | LM (digital) | Rev 0.7 §9.4 |
| **8** | Link controller | Commands squelch timing and exit destination | Asserts/deasserts squelch_cmd; chooses EXIT_TO_TRAINING or EXIT_TO_MISSION; owns relink_squelch_tx_duration within 60–75 ms | System | BUP-003, SQL-010, SQL-012 |

## 2.2 Block diagram

**Figure 2-1. TX squelch signal chain and control overlay**

*\[FIGURE PLACEHOLDER — insert block diagram here. Suggested content: one channel (four instances per fiber port), the eight blocks of Table 2-1 in signal-flow order along the bottom and TxSquelchSeq as the control overlay above them; signal names from Table 7-1. Signal path, left to right: TX PLL and serializer (#1, CDNS; clock never stops; full-rate NRZ) → pre-driver source mux TxSourceMux (#2, CDNS): three inputs MISSION data, DESKEW (160-bit OCI deskew training pattern) and HOLD (legal static serializer code); select input src_sel ∈ {MISSION, DESKEW, HOLD}, glitch-free and synchronous to the serializer clock → pre-driver (CM and DCD balance held through mute) → TX driver drawn as two independent nodes: the swing path (#3, LM; analog-FIR tap slices / swing-mute DAC; control input swing_mute ∈ {MISSION, MUTE}; FIR tap weights held at mission values) and the DC-bias path (#4, LM; V_bias, mission reverse-bias −1.5 to −2.0 V, with the independent v_sq trim DAC; control input v_sq) — no shared node between them and no supply-collapse path (SQL-005) → MRM with its drop-port monitor PD (#5, partner / photonics) → bus waveguide → Band-Mux → fiber (TP2). Heater servo (#6, partner): drop-port photocurrent (average launched power, the servo observable) → servo → heater DAC → MRM heater, drawn as a closed loop that stays closed through entry, dwell and exit; inputs heater_ramp_limit_freeze (ramp-limit freeze only; integrator state not touched) and the dither at the squelch profile; output heater.unlock. TX disparity checker TxDisparityNrz (#7, LM digital): observe-only tap on the mission data stream, gated by meas_valid, output disp_flag (held during squelch); draw no path from it to the heater servo (it is not a servo observable). Control overlay: TxSquelchSeq (Section 3) with inputs squelch_cmd and squelch_exit_dest from the link controller (#8, system; squelch_cmd lane-atomic across the WDM group, SQL-012; lane_squelch_override test input) and heater.unlock from #6; outputs src_sel → #2, swing_mute → #3, v_sq → #4 (per-lane calibrated code loaded from MFG-003 NVM, Section 4), heater_ramp_limit_freeze → #6, meas_valid → #7. Ownership boundaries from the Owner column of Table 2-1: CDNS (#1, #2); LM (#3, #4, #7); partner / photonics (#5, #6); system (#8). Data path solid, TxSquelchSeq control arrows dashed, servo loop dotted.\]*

## 2.3 Pre-driver source mux interface (CDNS deliverable)

**Table 2-2. TxSourceMux requirements**

| **Parameter** | **Requirement** | **Rationale** | **Req** |
| --- | --- | --- | --- |
| **Source count** | Three-way: MISSION, DESKEW (160-bit OCI deskew training pattern), HOLD (legal static serializer code) | Relink sequence requires a phase-continuous transition from HOLD to DESKEW on exit without the far-end CDR treating exit as a cold re-acquisition | SQL-003, SQL-010 |
| **Switching discipline** | Glitch-free; transitions synchronous to the serializer clock | Prevents spurious MRM modulation from a metastable transition | SQL-003 |
| **HOLD codes** | Legal non-toggling serializer output states as defined in §3.1; preference: all-1s (see Section 4.3) | Non-toggling required so no residual swing violates Tsq_channel; a toggling hold code would produce │dens│ = 1 at the disparity checker and must not reach the heater servo | SQL-001, SQL-003 |
| **CM and DCD balance** | Pre-driver output common mode and duty-cycle balance held through mute entry/exit within the SQL-002 ±0.5 dB AOP window | A CM or DCD step propagating to the MRM perturbs AOP beyond the ±0.5 dB budget | SQL-004 |
| **TX PLL and serializer** | Continue running through all squelch states | Phase continuity on HOLD → DESKEW is what prevents the far-end CDR from cold re-acquiring | SQL-003, CDR-006 |
| **Legal static states definition** | TBD_from_partner — specific codes enumerated in §3.1 interface deliverable | Open item 2; tracked in Section 10 | SQL-001 |

## 2.4 Driver swing-mute and bias-path independence (LM deliverable)

**Table 2-3. TX driver squelch-interface requirements**

| **Parameter** | **Requirement** | **Prohibition / note** | **Req** |
| --- | --- | --- | --- |
| **Path independence** | Swing path (analog-FIR tap-slices / swing_mute DAC) and DC bias (V_bias / v_sq) shall be on separate, independent control nodes | Supply-collapse mute and shared swing/bias control are prohibited: any topology in which muting the swing also moves the DC operating point changes static transmission and violates constant AOP | SQL-005 |
| **Swing mute** | swing_mute → MUTE collapses the RF swing to a static DC hold; FIR tap weights remain at their mission values so exit is hitless | swing_mute shall not alter FIR tap weights; shall not write the heater code | SQL-001, SQL-005, ELE-009 |
| **Mute depth** | Pre-driver + driver composite ≥ 20 dB electrical suppression; optical consequence ≥ 14 dB OMA suppression vs. §8.2 max OMA −1 dBm → Tsq_channel | Residual OMA floor (clock / data-path / FIR-slice feedthrough) must remain below −15 dBm optical | SQL-001 |
| **Mute settling** | Entry and exit each within t_squelch_settle ≤ 1 ms | Negligible against the 60 ms minimum dwell; driver transient must not push AOP outside ±0.5 dB | SQL-005 |
| **V_sq interface** | Driver DC bias path exposes an independent trim DAC for v_sq, distinct from V_bias and distinct from swing_mute | v_sq is a per-lane calibrated code owned by TxSquelchSeq; it cannot share a node with swing_mute | SQL-006 |
| **Voltage-mode realization** | Swing mute is a swing-path disable or FIR-slice collapse to a DC hold, not a supply-rail collapse | TBD_analog_design; open item 1; tracked in Section 10 | SQL-005 |

# 3. Sequencer (TxSquelchSeq)

## 3.1 Architecture

TxSquelchSeq is a digital sequencer commanded by the link controller. It owns src_sel, swing_mute, and v_sq. It does not own the heater code, the TX PLL, or the serializer clock. It is not a second adaptation loop or a second heater controller — it is a sequenced plant change that the heater servo must survive. The disparity checker remains observe-only and is gated for the duration (Rev 0.7 §9.4). Figure 3-1 (Section 3.2) draws the state machine that Table 3-1 (Section 3.3) tabulates.

## 3.2 State diagram

**Figure 3-1. TxSquelchSeq state diagram**

*\[FIGURE PLACEHOLDER — insert state-transition diagram (a state diagram, not a block diagram) here. Suggested content: the seven states of Table 3-1 as nodes with the state names verbatim — MISSION, ENTER, DWELL, EXIT_TO_TRAINING, EXIT_TO_MISSION, TRAINING, FAULT — with MISSION marked as the power-on default (reset arrow). Transition arcs, each labelled with its trigger: MISSION → ENTER on squelch_cmd assert (link controller); ENTER → DWELL on entry complete (steps E1–E5 of Table 3-2 done; AOP within ±0.5 dB of pre-squelch Pavg; within t_squelch_settle ≤ 1 ms); DWELL → EXIT_TO_TRAINING on squelch_cmd deassert with squelch_exit_dest = DESKEW (after relink_squelch_tx_duration 60–75 ms); DWELL → EXIT_TO_MISSION on squelch_cmd deassert with squelch_exit_dest = MISSION (invalid-input path); DWELL → FAULT on heater.unlock asserted during dwell; EXIT_TO_TRAINING → TRAINING on exit complete (steps X1–X6 of Table 3-4 with src_sel → DESKEW at X1; within 1 ms; no gap before the 160-bit training pattern); TRAINING → MISSION on training_complete from the link controller (training interval ≥ 285 ms owned by the link controller / PCS); EXIT_TO_MISSION → MISSION on exit complete (X1–X6 with src_sel → MISSION at X1); FAULT → no automatic exit — external fault clear only, drawn as a dashed arc leaving the diagram. Draw the normal relink path MISSION → ENTER → DWELL → EXIT_TO_TRAINING → TRAINING → MISSION as the solid main cycle, the invalid-input path DWELL → EXIT_TO_MISSION → MISSION as a dashed shortcut, and DWELL → FAULT as a bold terminal arc. Annotate each state with its behaviour from Table 3-1: MISSION — meas_valid = 1, swing_mute = MISSION, V_bias held; ENTER — E1 heater_ramp_limit_freeze = 1, E2 meas_valid = 0, E3 src_sel = HOLD, E4 swing_mute → MUTE, E5 v_sq applied; DWELL — heater servo closed (thermal step settles within ≤ 10 ms), dither at the squelch profile, residual OMA ≤ −15 dBm, AOP within ±0.5 dB, all WDM lanes muted, far end detects loss of modulation within t_loselock ≤ 50 ms; EXIT_TO_TRAINING / EXIT_TO_MISSION — X1 src_sel, X2 swing_mute → MISSION, X3 v_sq released, X4 acc = 0 / persist = 0, X5 meas_valid = 1, X6 heater_ramp_limit_freeze = 0; TRAINING — src_sel = DESKEW; FAULT — TX fault asserted, no heater re-acquisition. Signal names per Table 7-1.\]*

## 3.3 State machine

**Table 3-1. TxSquelchSeq state machine**

| **State** | **Entry condition** | **Behavior while in state** | **Exit condition** | **Next state** |
| --- | --- | --- | --- | --- |
| **MISSION** | Power-on default; training complete | Mission modulation running; meas_valid = 1; swing_mute = MISSION; V_bias held | squelch_cmd asserted by link controller | ENTER |
| **ENTER** | squelch_cmd assert | Execute Table 3-2 steps E1–E5 in order. Target: AOP within ±0.5 dB of pre-squelch Pavg; all steps complete within t_squelch_settle ≤ 1 ms. | Entry complete | DWELL |
| **DWELL** | Entry complete | Heater servo absorbs RF-removal thermal step (target ≤ 10 ms). Dither continues at squelch profile. Residual OMA verified ≤ −15 dBm. All WDM lanes held muted. Far end detects loss of modulation within t_loselock ≤ 50 ms. | squelch_cmd deasserted by link controller (after relink_squelch_tx_duration 60–75 ms) | EXIT_TO_TRAINING or EXIT_TO_MISSION per squelch_exit_dest |
| **DWELL** | — | As above | heater.unlock asserted during dwell | FAULT |
| **EXIT_TO_TRAINING** | squelch_cmd deassert; squelch_exit_dest = DESKEW | Execute Table 3-4 steps X1–X6 with src_sel → DESKEW at X1. Exit complete within t_squelch_settle ≤ 1 ms. 160-bit OCI Gen1 v1.0 training pattern begins immediately; no gap. | Exit complete | TRAINING |
| **EXIT_TO_MISSION** | squelch_cmd deassert; squelch_exit_dest = MISSION | Execute Table 3-4 steps X1–X6 with src_sel → MISSION at X1. No deskew training required (invalid-input recovery path). | Exit complete | MISSION |
| **TRAINING** | src_sel = DESKEW; training running | Link controller / PCS own the training interval (≥ 285 ms, OCI Gen1 v1.0). PMA must not insert any gap between squelch exit and the training pattern. | training_complete signaled by link controller | MISSION |
| **FAULT** | heater.unlock during DWELL | TX fault asserted. Squelch not exited with an unlocked ring. PMA does not attempt to re-acquire the heater (would put a second controller on the thermal node). | External fault clear | — |

## 3.4 ENTER sequence

**Table 3-2. TxSquelchSeq ENTER steps (all within t_squelch_settle ≤ 1 ms)**

| **Step** | **Action** | **Signal** | **Constraint** | **Req** |
| --- | --- | --- | --- | --- |
| **E1** | Freeze heater integrator ramp limits | heater_ramp_limit_freeze = 1 | Loop stays closed; integrator state is not touched; ramp-limit freeze prevents the 1 ms electrical transient from integrating as a large error | SQL-008 |
| **E2** | Gate disparity checker | meas_valid = 0; hold disp_flag | Prevents │dens│ = 1 on the hold code from propagating to the thermal-tuning loop | Rev 0.7 §9.4 |
| **E3** | Switch data-path source | src_sel = HOLD | Glitch-free; synchronous to the serializer clock; TX PLL and serializer keep running | SQL-003 |
| **E4** | Ramp swing mute | swing_mute → MUTE | Independent of V_bias and v_sq; pre-driver CM and DCD balance held within the SQL-002 AOP window | SQL-001, SQL-004, SQL-005 |
| **E5** | Apply per-channel squelch bias | v_sq = calibrated value (per lane, from MFG-003 NVM) | Drop-port current calibrated to equal mission-average launched power (parked-drive calibration point); junction remains in depletion; V_bias node not moved | SQL-002, SQL-006, SQL-007 |
| **—** | Completion criterion | — | AOP within ±0.5 dB of pre-squelch Pavg; all steps complete within t_squelch_settle ≤ 1 ms | SQL-002, SQL-005 |

## 3.5 DWELL obligations

**Table 3-3. TxSquelchSeq DWELL obligations**

| **Observable** | **Required behavior** | **Req** |
| --- | --- | --- |
| **Heater servo** | Closed-loop throughout; servo absorbs the RF-removal thermal step (resonance shift from changed intracavity energy and carrier self-heating) with zero unlock events; residual detuning back inside mission budget within t_heater_squelch_settle ≤ 10 ms | SQL-008, SQL-009 |
| **Heater dither** | Dither continues at the squelch profile (mission profile or reduced-amplitude squelch profile if mission dither would violate Tsq_channel); dither-induced residual OMA must not consume the Tsq_channel margin | SQL-001, SQL-008 |
| **Residual OMA** | Launched OMA ≤ −15 dBm per channel across the dwell, including driver feedthrough and heater dither | SQL-001 |
| **AOP** | Within ±0.5 dB of pre-squelch Pavg throughout dwell | SQL-002 |
| **Lane atomicity** | All WDM lanes of the PMA group remain muted together | SQL-012 |
| **Heater unlock** | If heater.unlock is asserted during dwell, escalate to FAULT state; the PMA does not take over the heater DAC | SQL-008, SQL-009 |
| **Far-end behavior (informative)** | Far-end CDR holds pi_code / state_p / state_f per CDR-006 signal_valid gate. Far-end demux-filter heaters stay locked because AOP is constant. Far-end adaptation loops freeze per ADP-002. | LOM-004, BUP-003 |

## 3.6 EXIT sequence

**Table 3-4. TxSquelchSeq EXIT steps (all within t_squelch_settle ≤ 1 ms)**

| **Step** | **Action** | **Signal** | **Constraint** | **Req** |
| --- | --- | --- | --- | --- |
| **X1** | Switch source to training pattern (or mission) | src_sel = DESKEW_TRAINING (relink path) or MISSION (invalid-input path) | Phase-continuous; 160-bit OCI Gen1 v1.0 deskew pattern begins immediately; no gap between squelch exit and the ≥ 285 ms training window | SQL-003, SQL-010 |
| **X2** | Restore swing | swing_mute → MISSION | Independent of V_bias and v_sq | SQL-005 |
| **X3** | Release squelch bias | v_sq released; V_bias resumes | Ring detuning returns to mission operating point over heater servo time constants; exit thermal walk-back must be characterized against dTDEC and the training-detect budget | SQL-006 |
| **X4** | Clear disparity state | acc = 0; persist = 0 | First post-squelch snapshot is not a partial window | Rev 0.7 §9.4 |
| **X5** | Re-enable disparity checker | meas_valid = 1 | Only after the training or mission stream is live | Rev 0.7 §9.4 |
| **X6** | Release heater ramp limits | heater_ramp_limit_freeze = 0 | Loop returns to normal integrator ramp limits | SQL-008 |
| **—** | Completion criterion | — | AOP within ±0.5 dB; within t_squelch_settle ≤ 1 ms; immediately compliant with the ≥ 285 ms training-pattern transmission requirement | SQL-002, SQL-010 |

# 4. MRM Squelch Bias (V_sq)

## 4.1 Calibration

V_sq is a per-channel calibrated quantity — not the electrical mid-swing, not derivable analytically from V_bias — because the ring transfer function is strongly nonlinear in both voltage and wavelength. The correct operating point is the DC reverse-bias level at which the ring’s static (parked-drive) drop-port transmission equals the time-averaged drop-port transmission under mission modulation.

The through-path (bus-waveguide) tap is broadband and reports the aggregate of all four DWDM channels plus unmodulated ELS carrier light; it cannot serve as the per-channel servo observable. The drop port is the only per-λ power observable. The calibration bridges drop-port current to launched per-channel power and requires two distinct calibration points because the intracavity optical state differs between the mission 50/50 modulated condition and the parked-drive (HOLD code) condition.

**Table 4-1. V_sq calibration procedure**

| **Step** | **Action** | **Observable** | **Storage** | **Req** |
| --- | --- | --- | --- | --- |
| **Factory point 1 (mission-data)** | Apply mission modulation on the target channel; record the drop-port photocurrent corresponding to mission average launched power; this is the AOP servo setpoint | Drop-port monitor PD current | MFG-003 NVM per lane, with temperature annotation | SQL-002, SQL-006 |
| **Factory point 2 (parked-drive)** | Apply the HOLD code (all-1s preferred, Section 4.3); sweep v_sq until the drop-port photocurrent equals the point-1 baseline; record this v_sq code | Drop-port monitor PD current | MFG-003 NVM per lane, distinct entry from point 1, with temperature annotation | SQL-002, SQL-006 |
| **Temperature sweep** | Repeat both points at hot, nominal, and cold plate corners; firmware interpolates between corners for in-service operation | On-die temperature sensor | Per-lane, per-corner NVM entries | SQL-006 |
| **In-service re-trim** | Repeat point-2 calibration at the cadence required to track v_sq drift (aging, ring re-alignment); overwrite the in-service NVM entry with timestamp | Drop-port monitor PD current | In-service NVM field; timestamp | SQL-006 |

The broadband aggregate bus-tap monitor is retained as a cross-check observable — verifying total group power stays within the Pavg_total budget (§8.2) and does not step at squelch entry/exit — but is explicitly barred from serving as the per-channel servo observable or the v_sq calibration reference.

## 4.2 Operating regime and junction constraint

**Table 4-2. V_sq operating-regime constraints**

| **Attribute** | **Requirement** | **Rationale** | **Req** |
| --- | --- | --- | --- |
| **Junction regime** | V_sq shall keep the MRM junction in depletion at all process, voltage, and temperature corners | Carrier-plasma index and absorption changes between the squelched and modulated states must remain small so the resulting resonance step stays inside the heater servo’s linear capture range | SQL-007 |
| **V_sq vs. V_bias** | V_sq is a distinct operating point from the mission DC reverse-bias V_bias (−1.5 V to −2.0 V, §8.3) | The nonlinear ring transfer function maps a different voltage to the mission-average static transmission; V_sq is not predictable from V_bias | SQL-006 |
| **Required shift magnitude** | Full drive swing ≈ 50–75 pm at 25 pm/V against a 160–260 pm FWHM (Q = 5000–8000); V_sq retune is a fraction of a linewidth, well inside the heater full-FSR range | Confirms thermal feasibility; the heater servo can absorb the entry/exit step | SQL-009 |
| **Thermal step character** | Removing RF modulation changes average intracavity energy and carrier self-heating, producing a resonance step at squelch entry and exit. This step (not a drift) is absorbed by the heater servo, not by opening the loop. | SQL-008, SQL-009 |  |

## 4.3 Rail selection for the HOLD code

The choice of HOLD rail determines the direction of the transient AOP excursion before the heater servo corrects it.

**Table 4-3. HOLD code rail-selection rationale**

| **Rail** | **AOP excursion before servo correction (4.5 dB ER ceiling)** | **Far-end LOS risk** | **Selection** |
| --- | --- | --- | --- |
| **All-1s (logic high)** | +1.7 dB relative to mission Pavg | Excursion upward; far-end AOP moves away from the −14 dBm LOS assert threshold (RXO-006) | Preferred |
| **All-0s (logic low)** | −2.8 dB relative to mission Pavg | If mission Pavg ≈ −8.5 dBm floor with 2.5 dB channel IL, far-end AOP ≈ −13.8 dBm — grazes the −14 dBm worst-case LOS assert; a spurious LOS converts the clean loss-of-modulation handshake into a dark-fiber indication at the far end | PROHIBITED |

The TxDisparityNrz checker will assert disp_flag on an all-1s stream, but meas_valid is forced low during squelch (ENTER step E2) and the flag does not reach the thermal-tuning loop.

# 5. Timing

**Table 5-1. Squelch timing budget**

| **Interval** | **Symbol** | **Target** | **Satisfaction criterion** | **Req** |
| --- | --- | --- | --- | --- |
| **Entry sequence** | t_squelch_settle | ≤ 1 ms | Steps E1–E5 complete (Table 3-2); AOP within ±0.5 dB; CM/DCD balance held | SQL-002, SQL-005 |
| **Heater thermal-step settle** | t_heater_squelch_settle | ≤ 10 ms (target) | Servo absorbs RF-removal thermal step; residual detuning inside mission detuning budget; zero unlock events. Settled entirely within the 60 ms minimum dwell, not in addition to it. | SQL-009 |
| **Relink dwell** | relink_squelch_tx_duration | 60 ms to 75 ms | OCI Gen1 v1.0 Table 1-3 dwell at squelched OMA. Entry sequence (≤ 1 ms) and thermal-step settle (≤ 10 ms) are inside this window. The 60 ms minimum provides a 50 ms guard after thermal settle. The dwell cannot be shortened — it is an OCI Gen1 v1.0 protocol number. | SQL-010 |
| **Far-end loss-of-modulation detect** | t_loselock | ≤ 50 ms (far end) | Bounds allowable residual OMA ripple during dwell; gives the far-end CDR its signal_valid gate. Not a local timer; the local thermal settle (≤ 10 ms) leaves a 40 ms guard inside t_loselock. | SQL-010 |
| **Exit sequence** | t_squelch_settle | ≤ 1 ms | Steps X1–X6 complete (Table 3-4); phase-continuous switch to 160-bit deskew training; AOP within ±0.5 dB | SQL-002, SQL-003 |
| **Deskew training after exit** | — | ≥ 285 ms (OCI Gen1 v1.0) | Link-controller / PCS obligation; PMA must not insert any gap between squelch exit and the start of the training pattern | SQL-010, BUP-003 |

Note on the 60 ms minimum: the minimum is set by the requirement that the far end can detect mute within t_loselock ≤ 50 ms and still have a 10 ms thermal-settle guard before dwell ends. Enter and exit settling (each ≤ 1 ms) are budgeted inside the dwell, not on top of it. The 75 ms maximum is the protocol deadline after which training must begin.

# 6. Loss-of-Modulation Detector (Far-End RX)

## 6.1 Purpose

When our TX squelch is active, the far-end RX sees an invalid-signal condition: AOP is above the LOS threshold but modulation is absent. The loss-of-modulation detector provides the signal_valid assertion that gates the far-end CDR (DES-OCI-106G-CDR-001 §10 hold) and all adaptation loops (DES-OCI-106G-ADP-001 §3.2 freeze), and feeds the BUP-003 relink trigger. It must be distinct from the LOS detector (BUP-004) because the two conditions have different optical signatures and drive different relink-branch responses.

## 6.2 Discrimination principle

The OCI spec provides a ≈ 6–7 dB gap between the worst-case mission OMA at the far-end TP3 (≈ −8.2 dBm sensitivity floor, −6.2 dBm stressed) and the loudest legal squelch leakage (≤ −15 dBm optical minus channel loss). The detector places its threshold in this gap; the qualifying AOP monitor distinguishes squelch from dark fiber.

**Table 6-1. Signal-state discrimination**

| **Condition** | **AOP at far-end TP3** | **Modulation metric** | **Flag** |
| --- | --- | --- | --- |
| **Mission traffic** | Above LOS de-assert threshold (RXO-006) | Above detector threshold | — |
| **Squelch / loss of modulation** | Above LOS de-assert threshold | Below detector threshold (OMA ≤ −15 dBm minus channel loss) | loss_of_modulation |
| **Dark fiber / LOS** | Below LOS assert threshold | — | LOS (RXO-006 path) |

## 6.3 Detector architecture

**Table 6-2. Loss-of-modulation detector design**

| **Element** | **Design** | **Rationale** | **Req** |
| --- | --- | --- | --- |
| **Amplitude metric** | Shadow comparator (or time-shared error slicer) with threshold DAC parked at a fixed absolute level (≈ −11 to −12 dBm OMA referred through the known TIA/AGC gain); counts threshold exceedances per window | Mission data crosses the absolute threshold constantly; squelch leakage plus noise does not. The threshold must be absolute (AGC-code-compensated), not adaptive — an adaptive threshold tracks the noise floor and reports “signal” on a squelch input. | LOM-004, BUP-004 |
| **AOP qualifier** | RXO-006 average-power monitor, independent of the data path | loss_of_modulation = (AOP above LOS de-assert level) AND (modulation metric below threshold); the AOP term distinguishes squelch from dark fiber | BUP-004 |
| **Persistence window** | Lower bound ≥ 1 µs (LOM-003); upper bound ≪ t_loselock ≤ 50 ms | A 72-UI CID run is ≈ 1.35 ns — five orders of magnitude shorter than a 75 ms relink dwell; any window from 1 µs to a few ms separates them. CID is not a hazard for the amplitude detector: during a CID the signal is at a full-amplitude rail, not at squelch amplitude. | LOM-003, BUP-004 |

## 6.4 AGC interaction

**Table 6-3. AGC freeze interaction**

| **Scenario** | **Risk** | **Mitigation** | **Req** |
| --- | --- | --- | --- |
| **Modulation disappears; AGC unfrozen** | AGC rails toward maximum gain, amplifying noise and squelch leakage toward the detector threshold; the control loop can suppress the loss-of-modulation assertion | Scale the detector threshold with the AGC code (absolute referral through AGC gain), or freeze the AGC on candidate-detection before the persistence window expires | ADP-002 |
| **Transient events (AGC gain-step, pattern transition)** | Momentarily bring the amplitude metric below threshold | Persistence window (Table 6-2) absorbs transients; AGC interaction is the primary design hazard, not CID | LOM-003 |

## 6.5 Detection and recovery flow

**Table 6-4. Loss-of-modulation detection and recovery sequence (informative)**

| **Step** | **Action** | **Who** |
| --- | --- | --- |
| **1** | Analog amplitude metric falls below the absolute threshold AND AOP remains above the LOS de-assert level | Detector hardware |
| **2** | Persistence window runs (≥ 1 µs, ≪ 50 ms) | Detector hardware |
| **3** | loss_of_modulation flag asserted; signal_valid de-asserted | Detector → CDR / ADP interface |
| **4** | CDR holds pi_code, state_p, state_f (CDR-006); all adaptation loops freeze (ADP-002) | DES-OCI-106G-CDR-001, DES-OCI-106G-ADP-001 |
| **5** | Deskew FSM enters Deskew_Data_Relink (BUP-003) | Link controller |
| **6** | Partner TX unsquelches; amplitude reappears above the threshold | Partner TxSquelchSeq EXIT |
| **7** | loss_of_modulation flag clears within the detection latency budget | Detector hardware |
| **8** | CDR warm-resumes from held phase and frequency; adaptation loops re-enabled in nesting order per ADP-001 | DES-OCI-106G-CDR-001, DES-OCI-106G-ADP-001 |

The held CDR phase and frequency (step 4) are the payoff of the constant-AOP squelch constraint: because AOP is preserved at the far end, the demux-filter heaters stay locked and the CDR’s sampling point remains valid, enabling a warm resume rather than a cold re-acquisition.

# 7. Interfaces

**Table 7-1. TxSquelchSeq external interface signals**

| **Interface** | **Signal** | **Direction** | **Protocol / constraint** | **Req** |
| --- | --- | --- | --- | --- |
| **Link controller** | squelch_cmd | Input | Level signal; lane-atomic across the WDM group; assert = start ENTER, deassert = start EXIT | SQL-010, SQL-012 |
| **Link controller** | squelch_exit_dest | Input | Selects EXIT_TO_TRAINING (relink path) or EXIT_TO_MISSION (invalid-input path) | SQL-010 |
| **Pre-driver / serializer (CDNS)** | src_sel | Output | Glitch-free three-way: {MISSION, DESKEW, HOLD}; synchronous to serializer clock; TX PLL and serializer remain locked through all transitions | SQL-003 |
| **Driver swing path (LM)** | swing_mute | Output | {MISSION, MUTE}; independent of V_bias and v_sq; FIR tap weights not affected | SQL-001, SQL-005 |
| **Driver DC-bias path (LM)** | v_sq | Output | Per-lane calibrated code; applied at E5, released at X3; distinct control node from swing_mute | SQL-006 |
| **Heater servo (Partner)** | heater_ramp_limit_freeze | Output | Asserted at E1, released at X6; transient guard only; loop stays closed; integrator state not frozen | SQL-008 |
| **Heater servo (Partner)** | heater.unlock | Input | If asserted during DWELL, TxSquelchSeq transitions to FAULT | SQL-008, SQL-009 |
| **TX disparity checker** | meas_valid | Output | Forced low at E2; re-asserted at X5 after accumulator clear | Rev 0.7 §9.4 |
| **TX disparity checker** | disp_flag | Output (hold) | Held during squelch; acc and persist counters cleared on exit before meas_valid = 1 | Rev 0.7 §9.4 |
| **Test mode** | lane_squelch_override | Input | Per-lane squelch enable; test modes only; not asserted in mission; does not override the group-atomic squelch_cmd | SQL-012 |

# 8. Parameter Table

**Table 8-1. Sequencer and calibration parameters**

| **Symbol** | **Model / RTL name** | **Default / target** | **Meaning** | **Req** |
| --- | --- | --- | --- | --- |
| **Tsq_channel** | tsq_channel | ≤ −15 dBm OMA per channel | Squelched launched OMA ceiling; TXO-010 / §8.4 | SQL-001 |
| **relink_squelch_tx_duration** | relink_squelch_tx_duration | 60 ms to 75 ms | OCI Gen1 v1.0 Table 1-3 dwell at squelched OMA; not the enter/exit slew time | SQL-010 |
| **ΔP_avg,sq** | aop_squelch_tol | ±0.5 dB vs. pre-squelch Pavg | AOP constancy across entry/dwell/exit; compatible with §8.2 Pavg range −8.5 dBm to 0 dBm; also protects far-end against LOS assert at −14 dBm (RXO-006) | SQL-002 |
| **A_mute,e** | swing_mute_db | ≥ 20 dB electrical (design target) | Pre-driver + driver composite swing suppression; optical consequence ≥ 14 dB OMA suppression | SQL-001 |
| **t_squelch_settle** | t_squelch_settle | ≤ 1 ms | Mute/bias sequencing and CM/DCD balance settle; applies to both ENTER and EXIT | SQL-005 |
| **t_heater_squelch_settle** | t_heater_squelch_settle | ≤ 10 ms (target) | Heater-servo absorption of RF-removal / restoration thermal step; to be confirmed against partner τ_th (open item 6) | SQL-009 |
| **t_loselock** | — | ≤ 50 ms (far end) | Far-end loss-of-modulation detect; bounds residual OMA ripple in dwell; not a local timer | SQL-010 |
| **V_sq** | v_sq (per lane) | Calibrated; ≠ mid-swing; ≠ V_bias | Static MRM bias whose drop-port current equals the mission-average launched-power calibration point (parked-drive point); factory + in-service trim via drop-port monitor PD | SQL-006 |
| **src_sel** | src_sel | {MISSION, DESKEW, HOLD} | Glitch-free three-way source mux; HOLD code per §3.1 TBD_from_partner | SQL-003 |
| **swing_mute** | swing_mute | {MISSION, MUTE} | Driver RF-swing mute DAC; independent of DC bias path; TBD_analog_design for voltage-mode realization | SQL-001, SQL-005 |
| **squelch_cmd** | squelch_cmd | Level from link controller | Lane-atomic assert/deassert; per-lane override is test-only | SQL-012 |
| **squelch_dither_profile** | squelch_dither_profile | Mission dither, or reduced | Heater dither during dwell; must not cause dither-induced OMA to violate Tsq_channel; if mission dither is too large, a reduced profile with lock-slope penalty analysis is required (TBD_from_sim_sweep, open item 5) | SQL-008 |
| **heater_ramp_limit_freeze** | heater_ramp_limit_freeze | Asserted during ENTER/EXIT | Transient guard on servo integrator ramp limits; loop remains closed; integrator state not frozen | SQL-008 |

# 9. Verification

Method codes: S = extracted-view simulation across PVT, T = system-level test or test vehicle, A = analytical model.

**Table 9-1. Verification matrix**

| **Req** | **Item** | **Method** | **Condition** | **Pass criterion** |
| --- | --- | --- | --- | --- |
| **SQL-001** | Squelched OMA and swing suppression | S / T | Serializer HOLD code applied; swing_mute → MUTE; PVT corners; all lane codes | OMA ≤ −15 dBm at TP2 per channel; electrical suppression ≥ 20 dB; driver feedthrough floor below −15 dBm |
| **SQL-002** | AOP constancy; no far-end LOS | T (system) / S | Full squelch entry/dwell/exit cycle; hot and cold plate corners; both calibration points (mission-data, parked-drive) exercised | ΔAOP ≤ ±0.5 dB vs. pre-squelch Pavg throughout; far-end AOP never below LOS assert threshold (RXO-006) |
| **SQL-003** | Phase-continuous source transitions | T (system) | src_sel: MISSION → HOLD → DESKEW_TRAINING; serializer clock running | No glitch at the MRM output; far-end CDR lock held through entry and exit; warm resume confirmed from held pi_code |
| **SQL-004** | CM / DCD balance hold | S / T | Pre-driver mute entry/exit at all process corners | CM step and DCD change at driver input within the SQL-002 AOP window |
| **SQL-005** | Swing-mute independence from DC bias | S | swing_mute asserted; V_bias / v_sq swept independently | DC operating point does not change when swing_mute transitions; no supply-collapse path confirmed absent |
| **SQL-006** | V_sq calibration accuracy and drift | T (factory) | Per-lane v_sq calibration at hot / nominal / cold; aging soak; both calibration points; in-service re-trim exercised | Drop-port current at v_sq equals mission-baseline within ±0.5 dB AOP window at all temperature corners; in-service point tracks drift within budget |
| **SQL-007** | Junction depletion at V_sq | S | V_sq range swept over all PVT corners | Junction remains in depletion at all corners; no forward-bias condition |
| **SQL-008** | Heater servo closed-loop through squelch; dither bounded | T (system) | Full squelch cycle; servo running; dither at squelch profile; heater_ramp_limit_freeze waveform captured | No loop-open events; heater_ramp_limit_freeze does not freeze the integrator state; dither-induced OMA within Tsq_channel |
| **SQL-009** | Thermal-step absorption; zero unlock | T (system, ≥ 10k cycles) | Hot and cold plate corners; entry/exit at maximum ramp rate; heater lock monitored | Zero unlock events over the soak; residual detuning inside mission budget within ≤ 10 ms; settling profiles logged |
| **SQL-010** | Sequencing vs. OCI Gen1 v1.0 Table 1-3 | T (system) | Full relink handshake: ENTER → DWELL (60–75 ms) → EXIT_TO_TRAINING → TRAINING (≥ 285 ms) | Protocol timing satisfied; far-end detects mute within 50 ms; training pattern starts within t_squelch_settle of squelch_cmd deassert; no gap |
| **SQL-011** | Squelch vs. transmit-disable discrimination | T | Both conditions triggered separately on the same channel | AOP removed under transmit disable; AOP preserved under squelch; no cross-trigger in either direction |
| **SQL-012** | Lane atomicity | T | Group squelch entry/exit; lane-to-lane skew measured | All WDM lanes enter/exit within the lane-skew budget; no partial-group state observed by far-end deskew engine |
| **LOM-003/004 / BUP-003/004** | Loss-of-modulation detection and recovery | T (system) | Far-end CDR and demux-filter lock monitored through squelch cycles; persistence timer characterized | loss_of_modulation flag asserts within t_loselock ≤ 50 ms; no spurious LOS; no far-end heater unlock; CDR warm-resumes from held state |

# 10. Open Items

**Table 10-1. Open items and owner deliverables**

| **#** | **Item** | **Owner** | **Dependency / closure** |
| --- | --- | --- | --- |
| **1** | Voltage-mode realization of swing_mute that does not move V_bias; no supply collapse; no shared swing/bias control node | LM (TBD_analog_design) | DES-OCI-106G-TXD-001 §2.4; circuit design |
| **2** | CDNS legal static HOLD code enumeration, glitch-free src_sel timing specification, CM/DCD balance hold through mute entry/exit | CDNS (TBD_from_partner) | Rev 0.7 §3.1 interface deliverable; DES-OCI-106G-TXD-001 Table 4-1 |
| **3** | TX drop-port monitor photodiode path, v_sq trim engine, temperature annotation, in-service re-trim cadence; two-point calibration procedure (mission-data and parked-drive) implemented in production flow | Partner / Analog (TBD_from_partner, TBD_analog_design) | Section 4; MFG-003 NVM layout |
| **4** | Heater-servo architecture, lock detector, linear capture range, dither profiles (mission and squelch), integrator ramp-limit interface; EIC digital interface to TxSquelchSeq | Partner (TBD_from_partner); Analog (TBD_analog_design) | SQL-008/009; dither profile per item 5 |
| **5** | Mission vs. squelch dither profile: confirm mission dither does not consume Tsq_channel; if it does, define the reduced-dither squelch profile with the lock-slope penalty analyzed | Simulation (TBD_from_sim_sweep) | SQL-008; heater-servo bandwidth from partner (item 4) |
| **6** | Confirm t_heater_squelch_settle ≤ 10 ms against partner τ_th and heater-loop bandwidth; dwell remains 60–75 ms regardless of the result | Simulation (TBD_from_sim_sweep) | SQL-009; partner loop parameters (item 4) |
| **7** | Lane-group membership (WDM lane count per PMA group) and lane-to-lane entry/exit skew budget for SQL-012 | Partner (TBD_from_partner) | Rev 0.7 §3.1 serializer lane count; §8.2 Pavg_total |
| **8** | ELS / PMD-disable specification and a production test confirming that disable and squelch cannot be cross-triggered (SQL-011) | System / Management plane | Future management-plane section; this document’s scope boundary |
| **9** | Behavioral model TxSquelchSeq: AOP step, residual OMA including dither, heater-lock soak, interaction with TxDisparityNrz gating (Rev 0.7 §9) | Verification | SQL-002, SQL-008, SQL-009; partner loop parameters |
| **10** | Deskew-pattern generator placement (PMA vs. PCS) and the ≥ 285 ms training hold enforcement; which side of the CDNS interface the 160-bit OCI Gen1 v1.0 deskew pattern resides | Partner (TBD_from_partner) | SQL-010; BUP-003 |
| **11** | Electrical mute depth and v_sq accuracy verified at 106.25 GBd; protocol times (60–75 ms, 50 ms, 285 ms) are baud-independent | Simulation (TBD_from_sim_sweep) | SQL-001, SQL-006 |
| **12** | Loss-of-modulation detector: absolute threshold placement in the ≈ 6–7 dB discrimination gap; AGC freeze/scale rule; persistence window bounds formalized as derived requirements (candidate BUP or LOM family additions for Rev 0.2) | Architecture | Section 6; LOM-003/004; BUP-004 |
| **13** | Drop-port coupling ratio and monitor-diode responsivity tolerances vs. MGT-005 ±2 dB TX-power reporting accuracy; verify both calibration points stay within the VDM types 113–116 accuracy budget | Analog / Photonics | Section 4.1; MFG-003 NVM; item 3 |

*End of DES-OCI-106G-SQL-001 Rev 0.2.*

DES-OCI-106G-SQL-001 Rev 0.2 | DRAFT | Page  of