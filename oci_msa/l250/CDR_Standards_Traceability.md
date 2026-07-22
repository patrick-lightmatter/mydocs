# OCI-Gen2 CDR Governing Parameters — MSA Derivation and Standards Traceability

**Project:** OCI-Gen2 — 106.25G NRZ Co-Packaged Optics
**Companion docs:** [OCI_Gen2_PMA_Architecture.md](./OCI_Gen2_PMA_Architecture.md) (Ch. 11 MM-CDR, Ch. 14 targets), [mm_cdr_calc](./mm_cdr_calc/README.md)
**Governing MSA:** [200G OCI Optical PHY Specification v1.0](./200G-OCI-Optical-Phy-Specification-v1.0.pdf) (Gen1, 53.125 GBd NRZ, March 2026)

**Standards in hand** (reviewed; extracted values are integrated below):

| Document | File | Status |
|---|---|---|
| IEEE P802.3dj Draft D1.3 (Dec 2024) | `../standards/Copy of P802d3dj draft D1p3...pdf` | Draft — values subject to change until ratification |
| OIF-CEI-05.2 (incl. CEI-112G-XSR-PAM4 Cl. 24, XSR+ Cl. 28) | `../standards/Copy of OIF-CEI-05.2...pdf` | Ratified IA |

**Purpose:** the MSA defines Gen1 at 53.125 GBd. Gen2 doubles the baud to 106.25 GBd NRZ, so CDR governing parameters (bandwidth, ppm range, lock behavior) must be *derived* — partly from the MSA, partly from the standards it references. This document records each derivation and its traceability so the guesses can be replaced as standards freeze.

---

## 1. What the Gen1 MSA actually specifies

The MSA contains **no explicit CDR parameter table** (no JTOL mask, no ppm number, no loop bandwidth). It constrains the CDR indirectly:

| # | MSA item (Gen1, 53.125 GBd) | Value | CDR relevance |
|---|------------------------------|-------|---------------|
| 1 | Signaling rate | 53.125 GBd NRZ per wavelength | Gen2 = 2× = **106.25 GBd** |
| 2 | Pre-FEC BER threshold | 2.4E-4 (TDEC and SRS tests) | Eye margin the CDR budget is judged at |
| 3 | BER floor | 1E-6 | Error-floor sanity limit |
| 4 | TDEC / SEC max | 3.4 dB | Eye opening EO for JTOL → bandwidth math |
| 5 | Reference receiver BW | 26.5625 GHz BT4 = 0.5 × baud | RX analog chain target → **53.1 GHz at Gen2** |
| 6 | TX transition time | ≤ 17 ps 20–80% (≈ 0.9 UI) | Pulse shape → \(h_1\) magnitude at the MM PD |
| 7 | Loss-of-lock detection | t_LOL ≤ 50 ms | Lock-detect reporting budget |
| 8 | Deskew timers | t_lock ≤ 50 ms; timeouts 100–450 ms | CDR lock-time budget (very generous) |
| 9 | TX squelch on relink | 60–75 ms, modulation off, AOP stays on | CDR must **freeze on LOS**, not drift |
| 10 | Deskew patterns | 160-bit, mostly `0xCC` (1100 repeat); swaps are phase-continuous | Pattern the CDR/LMS must lock and *stay locked* through |
| 11 | Pattern detect robustness | Functional at BER ≤ 1E-4 | Lock/detect logic margin |
| 12 | SSC | **Not mentioned** (Ethernet optical lineage) | No SSC tracking requirement |
| 13 | ppm | **Not in MSA** — resolved from P802.3dj D1.3: **±50 ppm** (see §2.3) | Frequency-path range |
| 14 | Fiber link | 500 m SMF, IL ≤ 2.5 dB, CD −0.9…1.7 ps/nm | Channel model context; skew ≤ 7 UI handled by deskew, not CDR |

---

## 2. Derived Gen2 CDR governing parameters

### 2.1 Bandwidth lower bound — from the actual JTOL masks (updated with standards values)

The generic 1/1667-UI placeholder mask is now **retired**. Three real masks apply, all with the same shape (flat 5 UI floor at very low f, 20 dB/dec 1/f region, 0.05 UI high-frequency floor) but different corners:

**(a) P802.3dj electrical, Table 179–12** (200GBASE-KR1/CR1; identical Table 176D–10 for C2M). Fixed frequencies, valid at 106.25 GBd:

| Case | A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|---|
| Jitter frequency (MHz) | 0.04 | 0.1333 | 0.4 | 1.333 | 4 | 12 | 40 |
| SJ amplitude (UI pk-pk) | 5 | 1.5 | 0.5 | 0.15 | 0.05 | 0.05 | 0.05 |

1/f region product: \(f \cdot A_{SJ} = 2.0\times10^{5}\) Hz·UI; corner at **4 MHz**.

**(b) P802.3dj optical SRS, Table 182–20** (DR types at 106.25 GBd): not specified below 42.7 kHz; \(A_{SJ} = 2.13\times10^{5}\,\text{Hz}/f\) UI from 42.7 kHz to 4.27 MHz; 0.05 UI from **4.27 MHz** to 10× loop BW. The dj TDECQ reference CRU is likewise **4.27 MHz, 20 dB/dec**.

**(c) OIF CEI-112G-XSR, Table 24-12 / Figure 24-5** (ratified; baud-scaled): corner \(f_{CRU} = f_b/13280\), tested at \(f_{CRU}/100\) (5 UI), \(f_{CRU}/3\) (0.15 UI), \(f_{CRU}\), \(3f_{CRU}\), \(10f_{CRU}\) (0.05 UI). **At 106.25 GBd: \(f_{CRU}\) = 8.0 MHz**, tests at 80 kHz → 80 MHz. 1/f product: \(4.0\times10^{5}\) Hz·UI — 2× the dj masks. This is the **binding case** for the XSR-class D2OE link.

**Bandwidth floor.** For a first-order tracking response with corner \(f_c\), untracked SJ in the 1/f region is constant: \((f \cdot A_{SJ})/f_c\). Requiring it to fit the untracked-jitter budget \(J_{bud}\):

\[
f_c \ \geq\ \frac{f \cdot A_{SJ}}{J_{bud}} \quad\Rightarrow\quad
f_c \geq \frac{4.0\times10^{5}}{J_{bud}}\ \text{(CEI mask)},\qquad
f_c \geq \frac{2.0\times10^{5}}{J_{bud}}\ \text{(dj mask)}
\]

| Untracked SJ budget | Floor (dj mask) | Floor (CEI-XSR mask) |
|---|---|---|
| 0.20 UI pk-pk | 1.0 MHz | 2.0 MHz |
| 0.15 UI pk-pk | 1.3 MHz | 2.7 MHz |
| 0.10 UI pk-pk | 2.0 MHz | 4.0 MHz |

Plus the 0.05 UI floor above the corner is essentially untracked and must be absorbed by the eye budget unconditionally.

**Assessment of the `mm_cdr_calc` default (3.2 MHz):** untracked SJ = 0.0625 UI (dj) / 0.125 UI (CEI) in the 1/f region — passes with a ≥ 0.13 UI budget, but sits *below* the reference-CRU corners the standards are written around (4, 4.27, 8 MHz). **Recommendation: move the design target to ~4–6 MHz.** The latency ceiling (§2.2) leaves ample room. Note also that JTOL is tested out to \(10f_{CRU}\) = 80 MHz at 0.05 UI — jitter peaking must stay minimal there, which the heavily-damped default (ζ ≈ 1.8) provides.

### 2.2 Bandwidth upper bound — from loop latency (not the standards)

With 437 UI total loop latency (`mm_cdr_calc` default), the phase-margin ceiling is ≈ 30 MHz. Valid design window is now ≈ **2.7–30 MHz**, target **4–6 MHz** (§2.1).

### 2.3 ppm — resolved: ±50 ppm per end, frequency path mandatory

**P802.3dj D1.3 specifies 106.25 ± 50 ppm GBd** for every 200G/lane interface: Cl. 178 (KR1, TP0v), Cl. 179 (CR1, TP5v), Annex 176C (C2C), Annex 176D (C2M), and all DR optical clauses. CEI-05.2 §3.2.11 requires each interface to operate **asynchronously with ±100 ppm** baud tolerance, and its RX tolerance tests offset the test transmitter by ±100 ppm relative to the receiver.

- The link is **plesiochronous**. Worst-case relative offset: **±100 ppm** (±50 per end under dj; the CEI ±100 ppm test bounds the same requirement). This *tightens* the earlier ±200 ppm assumption.
- Design capture target: **±200 ppm** (2× margin over requirement).
- The CDR **frequency path is required** (overrides the earlier "ppm ≈ 0 if mesochronous" assumption in the architecture doc, Ch. 14 / Open Item 5).

Acquisition: phase-path saturated correction at default gains is 30.5 ppm against 100 ppm applied → ratio 0.305, which now **meets** the sat-correction ≳ ¼·applied criterion at the *required* offset, but not at the ±200 ppm *design* target (0.15). **Gear-shift remains the recommendation**: acquire with `divP` = 2 (≈ 61 ppm sat correction, ratio 0.61 at requirement / 0.31 at design target), shift to tracking gains after lock. The 50 ms budget makes this trivial.

### 2.4 SSC — none (confirmed)

Neither P802.3dj D1.3 nor CEI-05.2 imposes spread-spectrum clocking on these interfaces. The SSC ramp-rate constraint in `mm_cdr_calc` is **not applicable**; the frequency path only tracks static ±100 ppm. (PCIe is the standard that would have imposed SSC — checked, N/A.)

### 2.5 Lock time, lock detect, and the cycle-slip ban

- MSA budgets (50 ms detect, 100–450 ms state timeouts) exceed even cycle-slip acquisition (~tens of µs) by ~1000×. Not a binding constraint.
- **Cycle slips are effectively banned in mission mode:** CEI-05.2 §24.2.2 limits error bursts longer than 7 symbols to probability < 1E-20 (bursts > 3 symbols < 1E-12). A CDR cycle slip produces a burst orders of magnitude longer, so slips are permitted only during acquisition, never during tracking. This is the quantitative basis for the heavily-damped (ζ ≈ 1.8) loop and the gear-shift policy in §2.3.
- Binding *behavioral* requirements:
  1. **Freeze PI code and frequency register on LOS** during the 60–75 ms squelch window (no drift).
  2. **Maintain lock through phase-continuous pattern swaps** (training → release → mission).
  3. Lock detect must assert/deassert within t_LOL ≤ 50 ms (trivial vs. Ch. 11-6 window sizes).

### 2.6 Pattern robustness — periodic training pattern and long CID runs

Two distinct pattern stresses, from two sources:

**(a) MSA deskew pattern (periodic).** Dominated by repeating `1100` (period 4 UI, transitions every 2 UI). A **periodic pattern has non-white autocorrelation → can bias the LMS \(h_k\) estimates** feeding the MM phase detector. A crossing-based bang-bang CDR would not care; a MM-CDR might.
*Required verification (model):* \(h_{-1} - \alpha h_1\) has a stable, unbiased zero on the `0xCC` pattern at BER up to 1E-4. *Recommended policy:* freeze CTLE/AGC adaptation during deskew states; CDR + minimal LMS only.

**(b) CEI CID jitter-tolerance pattern (transition starvation).** CEI-05.2 §2.1.1.1 defines the JTOL test pattern as PRBS31 segments interleaved with **72 consecutive identical digits** (both polarities, inverting). The CDR and LMS must **coast through 72 UI with zero transitions** while the full SJ mask is applied, without losing lock or degrading BER. Design implications: MM-CDR update gating on data activity, frequency register holds the ramp during starvation, and the 72-UI coast must be included in the JTOL verification testbench.

### 2.7 Jitter budget inputs from the standards (TX side)

TX output jitter limits define the random/deterministic jitter the RX budget must absorb alongside untracked SJ (§2.1). All are measured through a reference CRU (dj: 4 MHz, 20 dB/dec; CEI: \(f_b/13280\), 20 dB/dec — i.e., jitter below the corner is *excluded*, consistent with the CDR tracking it):

| Parameter | P802.3dj Cl. 179 (CR1 TX, TP0v) | P802.3dj 176D (C2M module out) | CEI-112G-XSR TX | Units |
|---|---|---|---|---|
| J_RMS (uncorrelated, rms) | 0.023 | 0.023 | 0.0224 | UI |
| EOJ (even-odd) | 0.025 | 0.025 | 0.025 | UI pk-pk |
| J4u / J8u (tail jitter) | 0.118–0.12 (J4u03) | 0.135 (J4u03) | 0.1546 (J8u) | UI |
| SNDR / SNR_ISI (min) | SNR_ISI 28 | 26 | SNDR 32.5 | dB |

Working allocation for the Gen2 D2OE RX eye-width budget at the pre-FEC operating point: RJ ≈ 0.023 UI rms, DJ (EOJ + residual ISI) per COM, untracked SJ 0.10–0.15 UI pk-pk → this is the \(J_{bud}\) entering the §2.1 bandwidth floor.

Related front-end item: dj limits the **AC-coupling high-pass corner to ≤ 100 kHz** (Cl. 178.10.6; 50 kHz for C2C). Baseline wander below that corner belongs to the offset/BLW loop, not the CDR.

### 2.8 Front-end context (for completeness)

- Reference receiver 0.5 × baud → ~53 GHz TIA+CTLE chain target at Gen2 (MSA); dj TDECQ uses BT4 56.7 GHz at the same baud — consistent.
- TDEC/SEC 3.4 dB, RIN −138 dB/Hz, MPI penalty 0.2 dB → amplitude noise floor for the error slicer / LMS.
- Reference clock quality example (CEI Table 1-10): ±100 ppm, phase noise −125 dBc/Hz at 1 MHz — starting point for the clocking chapter's refclk spec.

### 2.9 Summary table — Gen2 CDR targets

| Parameter | Derived value | Confidence | Trace |
|-----------|---------------|------------|-------|
| Baud | 106.25 GBd NRZ | Firm (2× MSA; = dj 200G/lane) | MSA; dj Cl. 178/179 |
| CDR BW | target **4–6 MHz** (floor 2.7–4 MHz, ceiling 30 MHz) | From real masks (dj draft + CEI ratified) | §2.1–2.2 |
| Untracked SJ to budget | 0.05 UI floor + ≤ ~0.1 UI (1/f region at 4 MHz BW, CEI mask) | Firm method | §2.1, §2.7 |
| ppm capture | **±100 required (±50/end), ±200 design** | dj D1.3 + CEI (ratified) | §2.3 |
| Frequency path | **Required** | Firm | §2.3 |
| SSC | None | Firm (both docs checked) | §2.4 |
| Cycle slips | Banned in tracking (burst spec) | Firm | §2.5 |
| Lock time | ≪ 50 ms (µs-scale actual) | Firm | §2.5 |
| LOS behavior | Freeze PI + freq reg | Firm | §2.5 |
| Pattern lock | `0xCC` periodic **and** 72-UI CID coast | Needs model check | §2.6 |
| TX jitter into RX budget | J_RMS 0.023 UI, J4u/J8u 0.12–0.155 UI | dj draft / CEI ratified | §2.7 |
| Pre-FEC BER | 2.4E-4 (Gen1 optical) — **may relax if Gen2 adopts dj concatenated FEC**; XSR-class electrical expects 1E-6…1E-9 raw | Open decision | §3.1, §3.4 |

---

## 3. Standards verification stack

### 3.1 IEEE P802.3dj — primary (the MSA's own reference) — **D1.3 reviewed**

Draft D1.3 (Dec 2024) is in hand; ratification expected H2 2026. Its 200G/lane PMDs run at **exactly 106.25 GBd** (PAM4, but the clocking content transfers). Extracted:

- **Signaling-rate tolerance ± 50 ppm** everywhere at 200G/lane → §2.3
- **JTOL Table 179–12 / 176D–10** (electrical) and **Table 182–20** (optical SRS) → §2.1
- **Reference CRU 4 MHz (electrical) / 4.27 MHz (optical TDECQ), 20 dB/dec** → measurement convention aligned to CDR tracking
- **FEC architecture confirmed**: concatenated inner **Hamming(68,60)** (Cl. 177) + outer RS-544, with block-error-ratio test limit 1.45E-11 — pre-FEC thresholds far looser than Gen1's 2.4E-4. **If OCI Gen2 adopts dj-style FEC, EO margin and the CDR bandwidth floor change materially. Explicit project decision required.**
- Values remain draft until D3.x/SA ballot closes — recheck deltas at ratification.

### 3.2 Ratified 53.125 GBd optical clauses — IEEE 802.3cd / cu / db (Cl. 121/124/140)

The clauses the Gen1 MSA's TDEC/SRS methodology descends from — final. Now mainly a fallback: the dj D1.3 masks (§2.1) supersede the "scale ×2 from Gen1" interim approach.

### 3.3 OIF CEI-224G family (LR/MR rev 12 liaised Apr 2026; XSR/VSR in progress)

**CEI-224G-XSR (die-to-die / die-to-OE) remains the closest future analog to the CPO microbump link.** Still member-gated / in progress; until then, CEI-112G-XSR (§3.4) baud-scaled is the working XSR-class reference.

### 3.4 OIF CEI-112G-XSR-PAM4 (ratified, Cl. 24 of CEI-05.2) — **reviewed**

Extracted and integrated:

- **JTOL Table 24-12 / Figure 24-5** with \(f_{CRU} = f_b/13280\) → 8 MHz at Gen2 baud → §2.1 (binding mask)
- **±100 ppm asynchronous** baud tolerance (§3.2.11; RX tests at ±100 ppm offset) → §2.3
- **TX jitter**: J8u ≤ 0.1546 UI, J_RMS ≤ 0.0224 UI, EOJ ≤ 0.025 UI, SNDR ≥ 32.5 dB → §2.7
- **Raw BER classes 1E-6 / 1E-8 / 1E-9** by channel category (FEC assumed to reach 1E-15), **burst limits** (> 7 symbols < 1E-20) → §2.5 cycle-slip ban
- **CID JTOL pattern**: PRBS31 + 72-bit CID both polarities → §2.6(b)
- Clause 28 (XSR+) reuses Table 24-12 with COM 3 dB — same mask, so conclusions carry over.

### 3.5 Supporting

| Standard | Use |
|----------|-----|
| OIF ELSFP + CPO framework IAs | Laser interface (already in MSA); die-to-OE clock architecture guidance |
| Telcordia GR-253 / ITU-T G.8251 | Heritage of the 20 dB/dec mask shape (historical context only — real masks now in hand) |
| IBTA InfiniBand XDR (200G/lane) | Independent same-baud-class jitter/ppm budgets; relevant if non-Ethernet traffic ever carried |
| PCIe 6/7 | **Contrast only** — the SSC/refclk regime OCI does *not* have; keep as "checked, N/A" |
| IEEE 802.3 Cl. 91 (RS-544 KP4) | Basis of Gen1 2.4E-4 threshold; baseline for the Gen2 FEC decision |

---

## 4. Parameter → source traceability

| CDR parameter | Primary source | Cross-check |
|---|---|---|
| BW lower bound (JTOL) | dj D1.3 Table 179–12 / 182–20 | CEI-05.2 Table 24-12 (ratified, binding for XSR class) |
| BW upper bound | Own latency budget (no standard) | High-freq JTOL cases (0.05 UI at up to \(10f_{CRU}\)) bound peaking |
| ppm range | dj D1.3: ±50 ppm (Cl. 178/179, 176C/D, optical) | CEI-05.2 §3.2.11: ±100 ppm async |
| SSC | Absent in dj D1.3 (confirmed) | Absent in CEI-05.2 (confirmed); PCIe contrast (N/A) |
| Cycle-slip ban | CEI-05.2 §24.2.2 burst limits | dj block error ratio 1.45E-11 |
| Pre-FEC BER / EO | Gen1 MSA (2.4E-4) vs Gen2 FEC decision | dj Cl. 177 concatenated FEC; CEI XSR raw 1E-6…1E-9 |
| TX jitter inputs | dj Cl. 179 / 176D tables | CEI-05.2 Table 24 TX jitter |
| Lock time / t_LOL | Gen1 MSA deskew timers | CMIS 5.3 timing |
| LOS / squelch behavior | Gen1 MSA deskew state machine | — |
| Pattern robustness | Gen1 MSA `0xCC` (periodic) | CEI-05.2 §2.1.1.1 CID-72 (starvation) |
| Stress eye / TDEC method | dj Cl. 182 (TDECQ @ 106.25 GBd, CRU 4.27 MHz) | 802.3cu at Gen1 baud |
| RX reference BW | Gen1 MSA (0.5 × baud) ×2 | dj BT4 56.7 GHz TDECQ receiver |
| AC-coupling corner | dj 178.10.6: ≤ 100 kHz | dj 176C: ≤ 50 kHz |

---

## 5. Open confirmations (action items)

1. ~~P802.3dj signaling-rate tolerance~~ — **RESOLVED (D1.3): ±50 ppm per end → ±100 ppm relative.** Residual: reconfirm at ratification.
2. **Gen2 FEC choice** — Gen1 KP4-style 2.4E-4 vs dj concatenated (Hamming(68,60)+RS-544) → sets EO and the CDR bandwidth floor (§3.1). *Still open — project decision.*
3. ~~P802.3dj SJ tables~~ — **RESOLVED (D1.3): Tables 179–12 / 176D–10 / 182–20 captured in §2.1.** Residual: propagate into arch doc Appendix D and `mm_cdr_calc` (replace generic mask); recheck at ratification.
4. **CEI-224G-XSR draft** — still pending via OIF membership. Interim: CEI-112G-XSR (ratified, reviewed) baud-scaled per §2.1(c).
5. **LMS bias on `0xCC` pattern** — verify in the Python/Matlab model; set deskew-state freeze policy (§2.6a). **NEW: add 72-UI CID coast to the same verification (§2.6b).**
6. **Update architecture doc** — Ch. 11/14/15 + Appendix D: frequency path mandatory, ±100 ppm required / ±200 design, LOS freeze, cycle-slip ban, CDR BW target 4–6 MHz, real JTOL masks; drop SSC from `mm_cdr_calc` constraints.
7. **NEW: `mm_cdr_calc` re-tune** — raise default bandwidth toward 4–6 MHz (checking phase margin against the 437 UI latency) and add the CEI/dj masks as built-in JTOL checks.

---

## Revision history

| Date | Rev | Notes |
|------|-----|-------|
| 2026-07-19 | 0.1 | Initial capture of MSA-derived CDR parameters and standards verification stack |
| 2026-07-19 | 0.2 | Integrated reviewed standards: P802.3dj D1.3 (±50 ppm, JTOL Tables 179–12/176D–10/182–20, CRU corners, Hamming(68,60)+RS-544 FEC, AC-coupling corner) and OIF-CEI-05.2 / CEI-112G-XSR (JTOL Table 24-12 → 8 MHz corner at Gen2, ±100 ppm async, TX jitter, burst-error cycle-slip ban, CID-72 pattern). Retired generic 1/1667 mask; BW target moved to 4–6 MHz; ppm requirement tightened to ±100 relative |
