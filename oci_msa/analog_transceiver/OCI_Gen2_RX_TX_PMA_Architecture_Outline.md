# OCI-Gen2 PMA Architecture Document — Outline

> **Full draft:** [OCI_Gen2_PMA_Architecture.md](./OCI_Gen2_PMA_Architecture.md)

**Project:** OCI-Gen2 — 106.25G NRZ Co-Packaged Optics  
**Scope:** TX Driver / FFE, RX TIA / CTLE / AGC, sampling, digital adaptation (LMS channel estimator, Mueller–Müller CDR)  
**Reference diagram:** [OCI-Gen2.png](./OCI-Gen2.png)  
**Style:** loop-centric algorithm chapters — truth tables, filtering, range/resolution, nesting of loops  

**Legend (from block diagram):**  
- Optical (yellow) — LightMatter responsibility (laser, modulator, band mux, optical channel, MR, PD)  
- Analog (blue) — Driver, TIA, CTLE, S/H, PLL / phase rotator  
- Digital (purple) — Error truth table, LMS channel estimator, MM-CDR, adaptation  

---

## Document Front Matter

- Title, authors, revision history  
- Related docs: OCI-Gen2 Chip Plan, OCI-CDNS Sketchbook  
- Diagram history notes (e.g. 1/14/2022 initial draft; 2/1/2022 remove CDR wraparound loop; CTLE on PD side only)  
- Acronyms and notation (`d(n)`, `e(n)`, `h_k`, PI code, UI, ppm, etc.)  
- What is in-scope vs. out-of-scope (optical path vs. electrical PMA)

---

## Chapter 1: Introduction

### 1-1 Purpose of this document
- Describe algorithm and control designs of OCI-Gen2 PMA loops and blocks  
- Matlab / behavioral → RTL → synthesis flow  
- No readable schematic for digital loops; truth tables and filter equations are the source of truth  

### 1-2 System context: 106.25G NRZ CPO
- End-to-end path: NRZ data → Driver (pre/main/post) → microbump → optical (LightMatter) → microbump → TIA → CTLE → S/H → Digital  
- Target rate: **106.25 Gbps NRZ**  
- Co-packaged optics interface assumptions (microbumps, PD current into TIA)

### 1-3 Block inventory (full vs. semi-loops)
List each loop/block and whether it **detects only**, **adapts continuously**, or **adapt-and-freeze**:

| # | Block / Loop | Domain | Notes |
|---|--------------|--------|-------|
| 1 | TX Driver FFE (pre / main / post) | Analog + control | Analog FFE; discrete data in → continuous drive out |
| 2 | TIA (+ optional integrated CTLE/AGC) | Analog | Prefer CTLE+AGC in TIA if area allows |
| 3 | CTLE | Analog | Buffer / EQ between TIA and samplers |
| 4 | AGC | Analog / digital control | Drive TIA gain to preset target |
| 5 | Offset cancellation | Analog / digital | Vertical eye placement (if present) |
| 6 | Sampling (S/H) + data / error slicers | Analog | Produce `d(n)`, `e(n)` |
| 7 | PLL + phase rotator / PI | Analog | Sampling clock generation |
| 8 | Error truth table | Digital | Maps samples → `e(n)` for adaptation |
| 9 | Channel estimator (LMS) | Digital | Estimate `h_k`; tap update `h(n+1)=h(n)+μ·e(n)·d(n−k)` |
| 10 | Mueller–Müller CDR | Digital | Timing from `h_{-1}`, `h_1` → PI code |
| 11 | CTLE adaptation | Digital | Minimize Σ\|h\| (or agreed ISI metric) |
| 12 | Lock detect / freeze control | Digital | CDR / adaptation lock status |

### 1-4 How loops interact (nesting / roles)
- **MM-CDR** — horizontal (timing) lock via PI / phase rotator  
- **Offset** (if any) — vertical location  
- **AGC** — eye amplitude / TIA gain  
- **CTLE adaptation + LMS `h_k`** — eye shape / residual ISI  
- **Driver FFE** — TX-side pre-emphasis into modulator (static or adapted via back-channel / offline)

### 1-5 Optical vs. electrical responsibility
- LightMatter: laser, mod, band mux, optical channel, MR, PD  
- Electrical PMA: Driver, TIA, CTLE, clocks, digital adaptation  
- Interface contracts at microbumps (voltage/current, swing, impedance, latency)

---

## Chapter 2: Top-Level Signal Flow and Eye / Pulse Response

### 2-1 End-to-end signal flow
- Walk the diagram left → right with domain crossings at microbumps  
- Discrete NRZ → continuous driver waveform → optical → PD current → TIA voltage → CTLE → samples  

### 2-2 Unit interval and rate assumptions
- 106.25G NRZ: UI ≈ 9.41 ps  
- Internal clocking / deserialization width (TBD: 2T, 4T, etc.)  
- Relationship of digital update rate to baud  

### 2-3 Eye diagram interpretation (diagram inset)
- Horizontal / vertical cursors at 106G NRZ eye  
- Sampling instant vs. peak / crossing locations  

### 2-4 Pulse response and cursor definitions (diagram inset)
- `h_{-1}` (pre-cursor), `h_0` (main), `h_1` (post-cursor)  
- How MM-CDR uses `h_{-1}` vs `h_1` imbalance for early/late  
- Link to LMS channel estimator outputs  

### 2-5 Capture-FF topology
- Baud-rate data + error sampling model for LMS / MM-CDR  

---

## Chapter 3: TX Driver and Analog FFE *(new for CPO)*

### 3-1 Role of the Driver in CPO
- Drive modulator through microbump with controlled continuous waveform  
- Analog FFE from CR/CP: discrete data → continuous equalized drive  

### 3-2 Three-tap structure: pre / main / post
- Functional definition of each tap  
- UI delay blocks feeding the summer / driver  
- Layout note: minimize variation across pre/main/post  

### 3-3 Transfer function and equalization intent
- Discrete-time FFE model: `y[n] = c_pre·d[n+1] + c_main·d[n] + c_post·d[n−1]` (confirm sign/index convention)  
- Target: open optical / electrical eye into PD+TIA under known channel  

### 3-4 Range, resolution, and control interface
- DAC / code ranges for pre, main, post  
- Static programming vs. adapted coefficients  
- Constraints (swing, linearity, common-mode into microbump)

### 3-5 Adaptation options (if any)
- Offline / lab sweep  
- Back-channel / protocol-assisted  
- Freeze after bring-up  

### 3-6 Driver–optical interface requirements
- Microbump electrical spec  
- Interaction with modulator bandwidth and optical channel  

### 3-7 Conclusions

---

## Chapter 4: TIA Front-End *(new for CPO)*

### 4-1 Role of the TIA
- Convert PD photocurrent to voltage for CTLE / samplers  
- Noise, bandwidth, and gain tradeoffs at 106G  

### 4-2 Preferred integration: CTLE and AGC inside TIA
- Diagram note: integrate CTLE+AGC into TIA if space allows  
- Pros/cons of integrated vs. discrete CTLE after TIA  

### 4-3 TIA transfer function and peaking
- Transimpedance `Z_T(s)`, peaking options  
- Interaction with PD capacitance and microbump parasitics  

### 4-4 Input interface from PD / microbump
- Current range, DC, overload / saturation  
- Coupling and biasing  

### 4-5 Programmability and monitoring
- Gain codes, peaking codes, status bits  
- Observability for bring-up  

### 4-6 Conclusions

---

## Chapter 5: CTLE

### 5-1 Why CTLE after (or inside) TIA
- Linear EQ for optical + package + TIA ISI  
- Acts as buffer between PD/TIA and sampling path  

### 5-2 CTLE transfer function
- Zero/pole placement; peaking vs. DC gain  
- Relation to estimated channel `h_k`  

### 5-3 CTLE adaptation (under consideration)
- Metric: minimize sum of absolute values of estimated channel coefficients (per diagram)  
- Alternative metrics (MMSE subset, precursor/postcursor balance)  
- Update rate vs. LMS / CDR  

### 5-4 Range, resolution, filtering
- Code range, step size, IIR/accumulator settings  
- Continuous adapt vs. adapt-and-freeze  

### 5-5 Nesting with AGC and CDR
- Who moves first during acquisition  
- Freeze order  

### 5-6 Conclusions

---

## Chapter 6: AGC Loop

### 6-1 Why AGC is needed
- Hold sampler / eye amplitude at target despite PD current and channel variation  

### 6-2 What the AGC code controls
- TIA gain (preferred) and/or post-TIA VGA  
- Target: preset desired amplitude (diagram note)  

### 6-3 Detection metric
- Peak / |error| / estimated `|h_0|` based AGC error  
- Hysteresis mode (optional)  

### 6-4 Filtering: slowest loop among adaptations
- Bandwidth relative to LMS, CTLE, CDR  
- Stability when nested with CTLE  

### 6-5 Range, resolution, freeze behavior  

### 6-6 Conclusions

---

## Chapter 7: Offset Cancellation (and optional BLW)

### 7-1 Need for offset cancel at 106G CPO RX
- Comparator / TIA / CTLE offsets vs. eye height  

### 7-2 Decision truth tables (should-move-up / down)
- Data vs. error slicer based detection  

### 7-3 Filtering, DAC range, resolution  

### 7-4 Common vs. per-slicer offset  

### 7-5 Baseline wander (if applicable to optical / AC path)  

### 7-6 Conclusions

---

## Chapter 8: Sampling Path — Data, Error, and Truth Tables

### 8-1 Sample-and-hold topology
- Dual S/H path shown on diagram  
- Relationship to PLL / phase rotator clocks  

### 8-2 Data decisions `d(n)`
- Threshold, timing, deserialization  

### 8-3 Error signal `e(n)` and Error Truth Table
- How error samples are formed for LMS  
- Valid conditions / pattern gating  

### 8-4 Eye-scan / diagnostic sampling (if supported)
- Roaming vertical/horizontal offsets  

### 8-5 Conclusions

---

## Chapter 9: Clocking — PLL, Phase Rotator / PI

### 9-1 Clock architecture overview
- PLL → phase selection / mixer / rotator → sampler clocks  

### 9-2 Phase interpolator / rotator model
- Code width, taps per UI, cyclic wrap behavior  
- Effective resolution at 106.25G  

### 9-3 Reset and rate-mode behavior
- Deterministic phase relationships at reset release  

### 9-4 Latency budget into MM-CDR
- Analog + digital pipeline latency budget  

### 9-5 Conclusions

---

## Chapter 10: Channel Estimator — LMS Filter

### 10-1 Purpose
- Estimate discrete channel taps `h_k` for CDR, CTLE adaptation, diagnostics  

### 10-2 LMS structure (per diagram)
- Delay line `z^{-1}`, multipliers, tap vector  
- Update: `h(n+1) = h(n) + μ · e(n) · d(n−k)`  
- Sign-sign / signed / floating variants (tradeoffs)  

### 10-3 Tap set
- Minimum: `h_{-1}`, `h_0`, `h_1` for MM-CDR  
- Extended taps if used for CTLE metric Σ\|h\|  

### 10-4 Step size `μ`, filtering, and convergence
- Acquisition vs. tracking `μ`  
- Freeze after lock  

### 10-5 Coupling to Error Truth Table and data path  

### 10-6 Conclusions

---

## Chapter 11: Mueller–Müller CDR

### 11-1 Why MM-CDR for this architecture
- Baud-rate timing recovery using estimated cursors (fits LMS + single sampling phase)  

### 11-2 Phase detector using `h_{-1}` and `h_1`
- Early/late from precursor vs. postcursor imbalance (pulse-response inset)  
- Truth / arithmetic form of PD output  

### 11-3 Loop filter: phase path
- Accumulator, gain knobs (inc / div analogs)  
- PI code update  

### 11-4 Frequency path (if required)
- ppm / SSC tracking needs for CPO use cases  
- Damping criteria (2nd-order loop formulas)  

### 11-5 Bandwidth, time-constant, and SJ tolerance
- Linearized PD gain assumptions  
- Upper bound from standards / link budget; lower bound from loop latency  
- Example setting table at 106.25G  

### 11-6 Lock detect
- Saturation / slew windows on PI code  

### 11-7 Nesting with LMS (who updates when)  

### 11-8 Conclusions

---

## Chapter 12: Acquisition Sequence and Loop Nesting

### 12-1 Power-up / reset sequence
- Order: clocks → TIA/AGC coarse → CTLE coarse → LMS → MM-CDR → fine adapt  

### 12-2 Mutual exclusion and freeze policies
- Which loops run during training vs. mission mode  

### 12-3 Recommended default gains / time constants  

### 12-4 Failure modes and recovery
- Unlock, AGC rail, CTLE max peaking, LMS divergence  

### 12-5 Conclusions

---

## Chapter 13: Optical Channel Interface Notes (LightMatter)

### 13-1 Blocks owned outside electrical PMA
- Laser, modulator, band mux, optical channel, MR, PD  

### 13-2 Electrical contracts at microbumps
- TX driver → mod; PD → TIA  

### 13-3 Optical impairments that adaptation must absorb
- Loss, dispersion-like ISI, MR / mux effects (as seen electrically)  

### 13-4 What not to put in PMA adaptation  

---

## Chapter 14: Performance Targets and Validation

### 14-1 Eye opening / BER targets at 106.25G NRZ  

### 14-2 Jitter tolerance and CDR bandwidth checks  

### 14-3 Adaptation convergence time and ppm / SSC (if applicable)  

### 14-4 Lab / silicon bring-up checklist  
- Driver tap sweeps, TIA gain, CTLE peaking, LMS tap readout, PI code behavior  

### 14-5 Correlation to Matlab models and diagram insets  

---

## Chapter 15: Open Items and Design Decisions

### 15-1 CTLE+AGC integrated in TIA vs. discrete CTLE  
### 15-2 CTLE adaptation metric finalization (Σ\|h\| vs. alternatives)  
### 15-3 Driver FFE: static vs. adapted  
### 15-4 Need for offset / BLW / eye-scan  
### 15-5 Frequency-path CDR necessity for CPO clocking model  
### 15-6 Deserialization width and digital update rate  

---

## Appendices

### Appendix A: OCI-Gen2 block diagram
- Embed / link [OCI-Gen2.png](./OCI-Gen2.png)  
- Color legend and history notes  

### Appendix B: Notation and signal dictionary
- `d(n)`, `e(n)`, `h_k`, PI code, AGC code, CTLE code, driver tap codes  

### Appendix C: LMS and MM-CDR derivation notes
- Sign-sign MMSE / LMS details  
- MM phase detector from `h_{-1}`, `h_1`  

### Appendix D: Bandwidth / damping calculation worksheets
- Worked examples at 106.25 Gbps  

### Appendix E: Truth tables (full set)
- Error truth table  
- Offset up/down  
- AGC up/down  
- CTLE adapt decisions  
- MM-CDR early/late  

### Appendix F: Register / programming map (placeholder)
- Control knobs for Driver, TIA, CTLE, AGC, LMS `μ`, CDR gains, freezes  

### Appendix G: Revision history of this architecture document  

---

## Suggested writing order

1. Ch. 1–2 (context + eye/pulse definitions)  
2. Ch. 3 Driver, Ch. 4 TIA *(new mandatory chapters)*  
3. Ch. 5–7 CTLE / AGC / Offset  
4. Ch. 8–9 Sampling + clocks  
5. Ch. 10–11 LMS + MM-CDR *(core digital)*  
6. Ch. 12 acquisition  
7. Appendices with equations and truth tables  
