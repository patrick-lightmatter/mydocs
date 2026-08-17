# OCI Tx / Rx PMA Requirements — MSA Capture and Standards Cross-Reference

**Project:** OCI-Gen2 — 106.25G NRZ co-packaged optical transceiver  
**Governing MSA (Gen1):** [200G OCI Optical PHY Specification v1.0](./200G-OCI-Optical-Phy-Specification-v1.0.pdf) (March 11, 2026)  
**Local standards used for cross-check:** [`../standards/`](../standards/) — IEEE P802.3dj/D1.3, OIF CEI-05.2  
**Related:** [CDR_Standards_Traceability.md](./CDR_Standards_Traceability.md) (CDR bandwidth / ppm derivations); [gen1_evk_compliance_matrix.md](./gen1_evk_compliance_matrix.md) (GEN1 EVK test-plan mapping of every row below to a measurement method and prediction)

---

## 1. Scope and how to read this document

The Gen1 MSA defines a **53.125 GBd NRZ** optical line interface (4λ × 53.125 Gbps → 212.5 Gbps per fiber). Gen2 doubles the baud to **106.25 GBd NRZ**; values marked *Gen2 scale* are derived, not MSA-normative.

This document records:

1. **Normative MSA numbers** that bind the Tx/Rx PMA (optical eye, power, stress, deskew, timing).
2. **What the MSA does *not* specify** (notably an explicit JTOL mask and signaling-rate ppm).
3. **Referenced / supporting standard content** from the MSA’s own reference list and from the local `standards/` folder, for the gaps and for Gen2 electrical PMA budgeting.

| Layer | MSA Gen1 | Gen2 design intent |
|-------|----------|--------------------|
| Optical baud / lane | 53.125 GBd NRZ | 106.25 GBd NRZ |
| Aggregate / fiber | 212.5 Gbps (4λ) | 425 Gbps (4λ) if same architecture |
| UI | ≈ 18.82 ps | ≈ 9.41 ps |

---

## 2. Normative sources

### 2.1 MSA References (p. 8)

The MSA explicitly cites:

| Reference | Role for PMA |
|-----------|----------------|
| **IEEE Draft P802.3dj** (MSA text: “2p3”; local copy: **D1.3**, Dec 2024) | TDEC measurement method lineage; signaling-rate / FEC / optical stress methodology at 106.25 GBd (PAM4 in dj) |
| **OIF CMIS 5.3** | Management, LOS/LOL flags, VDM (PreFEC BER, PRBS BER, MPI) |
| **OIF ELSFP-01.0** | External laser source interface |

### 2.2 Local standards folder (not cited by name in MSA, but used for JTOL / electrical PMA)

| Document | File | PMA use |
|----------|------|---------|
| IEEE P802.3dj/D1.3 | `standards/Copy of P802d3dj draft D1p3...pdf` (+ `_dj_d13.txt`) | Optical Cl. 180 TDECQ/SECQ = 3.4 dB; electrical JTOL Table 179–12; **±50 ppm** signaling rate on 106.25 GBd PMDs |
| OIF CEI-05.2 | `standards/Copy of OIF-CEI-05.2...pdf` (+ `_cei52.txt`) | Cl. 19 **CEI-56G-XSR-NRZ** (Gen1-baud NRZ XSR); Cl. 24 **CEI-112G-XSR-PAM4** (JTOL mask, TX J8u/JRMS/EOJ); §3.2.11 **±100 ppm** baud tolerance |

---

## 3. MSA — PMA architecture requirements (§1)

These are structural / protocol requirements on the OCI PMA/PMD, not optical eye numbers.

| Item | Requirement | MSA locus |
|------|-------------|-----------|
| Host PMA interface | OCI PMA attaches to 200GBASE-R 8:1, 400GBASE-R 16:2, 800GBASE-R 32:4, or 1.6TBASE-R 16:8 SM-PMA | §1 |
| Lane geometry | 200G 1:4 / 400G 2:8 / 800G 4:16 / 1.6T 8:32 OCI PMA | §1 |
| Electrical aggregate | Host side: **212.5 Gbps** streams; PMD side: **n × 53.125 Gbps** NRZ | §1 |
| Modulation | **53.125 Gbaud NRZ** on **4 wavelengths** per 212.5 Gbps stream | §1, Table 2-1 |
| Deskew | Hardware deskew of 4λ before data is passed up; state machine active indefinitely | §1.1 |
| Deskew range | Compensate **0–7 UI** relative delay across the four 53.125 Gbps channels | §1.1 |
| Skew budget (informative notes) | TX routing &lt; 2 UI; fiber CD &lt; 3 UI; RX routing &lt; 2 UI | §1.1 notes 6–8 |
| Pattern detect | Functional at **BER ≤ 1E-4**; robust to MPI / back-reflection | §1.1 |
| Pattern swap | Training → release → mission: **phase-continuous, glitch-free** so far-end **CDR does not lose lock** | §1.1 |
| TX squelch (relink) | Modulation off, **AOP stays on** (MRR heater lock); duration **60–75 ms** | §1.1, Table 1-3 |
| Invalid RX → relink | LOS, **CDR LOL**, or PCS repeated uncorrectable errors | §1.1 |
| Bit/λ mapping | LSB ↔ shortest wavelength on TX and RX | §1.2 |

### 3.1 Deskew timing (Table 1-3 + notes)

| Timer | Min | Max | Unit |
|-------|-----|-----|------|
| `relink_squelch_tx_duration` | 60 | 75 | ms |
| `timeout_data_detect` | 200 | 250 | ms |
| `timeout_data_sync` | 100 | 150 | ms |
| `timeout_data_validate` | 200 | 450 | ms |
| `duration_to_transmit_training_pattern` | 285 | — | ms |
| `duration_to_transmit_release_pattern` | 200 | — | ms |
| `t_loselock` (lack of modulation) | — | 50 | ms |
| `t_lock` (modulation restored) | — | 50 | ms |
| `t_detect` / `t_skew` | — | 100 | ms each |

Training / release patterns: 160-bit, mostly repeating `0xCC` (1100); channel ID in bits 23:16 (Tables 1-1, 1-2).

---

## 4. MSA — Optical transmitter requirements (§2.2, Table 2-2)

Normative for Gen1 optical TX. Gen2 must re-budget at 2× baud (especially transition time in UI and reference-receiver BW).

### 4.1 Wavelengths (Type A / Type B groups)

| Channel | Group A (nm) min / typ / max | Group B (nm) min / typ / max |
|---------|------------------------------|------------------------------|
| λ0 | 1307.8 / 1308 / 1308.2 | 1327.49 / 1327.69 / 1327.89 |
| λ1 | 1310.08 / 1310.28 / 1310.48 | 1329.85 / 1330.05 / 1330.25 |
| λ2 | 1312.38 / 1312.58 / 1312.78 | 1332.21 / 1332.41 / 1332.61 |
| λ3 | 1314.68 / 1314.88 / 1315.08 | 1334.58 / 1334.78 / 1334.98 |

### 4.2 Power, eye, and noise

| Parameter | Symbol | Limit | Unit | Condition / note |
|-----------|--------|-------|------|------------------|
| SMSR | SMSR | ≥ 30 | dB | |
| Total average launch power / group | Pavg_total | ≤ 6 | dBm | PRBS13 |
| Average launch power / channel | Pavg | −8.5 (info min) … 0 (max) | dBm | PRBS13; min informative |
| OMA / channel | OMA | ≥ max(−5.5, −6.9+TDEC); ≤ −1 | dBm | PRBS13 |
| OMA imbalance any two channels | dOMA | ≤ 3 | dB | PRBS13 |
| **TDEC** | TDEC | **≤ 3.4** | **dB** | **SSPR**; see §4.3 |
| Extinction ratio | ER | ≥ 3.5 (typ 4.5) | dB | PRBS13 |
| \|TDEC_SSPR − TDEC_PRBS13\| | dTDEC | ≤ 0.4 | dB | |
| Squelched TX OMA / channel | Tsq_channel | ≤ −15 | dBm | AOP held constant |
| **Transition time (20–80%)** | — | **≤ 17** | **ps** | SSPR; ≈ **0.90 UI** @ 53.125 GBd → Gen2 scale ≈ **8.5 ps** if same UI fraction |
| Over / undershoot | — | ≤ 22 | % | SSPR |
| RIN₂₁.₄OMA | RIN_OMA | ≤ −138 | dB/Hz | PRBS13; 21.4 dB RL |
| Optical return loss tolerance | ORL | ≤ 21.4 | dB | |
| TX data-path reflectance | Tx_data_Ref | ≤ −19 | dB | into TX, TX band |
| OE laser input reflectance (ELS) | OE_Lin_Ref | ≤ −26 | dB | ELS implementations |

### 4.3 TDEC measurement method (MSA Note 2 — PMA-critical)

- Reference receiver: **26.5625 GHz BT4** (= **0.5 × baud**), **no equalizer**
- Vertical histograms at **0.4 UI** and **0.6 UI**
- Pre-FEC BER threshold for TDEC: **2.4E-4**
- Method details deferred to **IEEE 802.3** (MSA → dj / optical TDEC family)

**Gen2 scale:** reference RX BW → **53.125 GHz BT4** if the 0.5×baud rule is kept.

---

## 5. MSA — Optical receiver requirements (§2.3, Tables 2-3 / 2-4)

| Parameter | Symbol | Limit | Unit | Notes |
|-----------|--------|-------|------|-------|
| Wavelengths | — | same grids as TX (A receive B, B receive A) | nm | |
| Damage threshold / channel | — | 4.5 | dBm | |
| Average receive power / channel | Pavg | −11 (info min) … 0 (max) | dBm | min informative |
| Rx OMA imbalance | dOMA | ≤ 3 | dB | |
| Receiver reflectance | Rx_Ref | ≤ −19 | dB | |
| OMA / channel (max) | OMA | ≤ −1 | dBm | |
| Receiver sensitivity (OMA) | RxSens | ≤ max(−8.2, −9.6 + TDEC) | dBm | PRBS31 |
| **Stressed receiver sensitivity** | **SRS** | **≤ −6.2** | **dBm** | PRBS31; BER = **2.4E-4** at TP3 |
| BER floor | BER_FL | ≤ **1E-6** | — | Ref TX with TDEC ≥ 2 dB; OMA from (−8.2+TDEC) to −1 dBm |
| LOS assert (AOP) | LOS_A | −19 … −14 (typ −16.5) | dBm | |
| LOS hysteresis | LOS_H | 1 … 3 (typ 2) | dB | |
| LOS de-assert | LOS_D | −18 … −11 (typ −14.5) | dBm | informative |
| **Loss-of-lock detection delay** | **t_LOL** | **≤ 50** | **ms** | modulation on/off → LOL flag |

### 5.1 Stressed receiver test (Table 2-4)

| Parameter | Value | Unit |
|-----------|-------|------|
| **Stressed eye closure (SEC), channel under test** | **3.4** | **dB** |
| OMA of each aggressor channel | −3.2 | dBm |

**Important gap:** the MSA specifies **SEC = 3.4 dB** and SRS OMA, but **does not publish a sinusoidal JTOL frequency/amplitude table**. JTOL for CDR BW must come from IEEE / OIF cross-references (see §7–§8).

---

## 6. MSA — Link, ELS, diagnostics (PMA-adjacent)

### 6.1 Fiber link model (Table 2-5)

| Parameter | Limit | Unit |
|-----------|-------|------|
| Reach context | 500 m SMF-28 | — |
| Total IL | ≤ 2.5 | dB |
| Chromatic dispersion | −0.9 … 1.7 | ps/nm |
| MPI penalty tolerance | 0.2 | dB |

### 6.2 External laser (Table 2-6) — noise into TX PMA

| Parameter | Limit | Unit |
|-----------|-------|------|
| Laser RIN | ≤ −144 | dB/Hz |
| Linewidth | ≤ 1 | MHz |
| SMSR | ≥ 30 | dB |
| Polarization extinction | ≥ 16 | dB |
| ELS output reflectance / ORL tolerance | ≤ −26 / −26 | dB |

### 6.3 Diagnostics that exercise the PMA

CMIS 5.3 + OCI VDM (Tables 3-2, §5): PreFEC BER (host/line), per-channel PRBS checker BER, MPI metrics, LOS/LOL-related flags. Alarm thresholds TBD in MSA.

---

## 7. Gaps in the MSA (must be filled from references)

| Needed for Tx/Rx PMA | In MSA? | Fill from |
|----------------------|---------|-----------|
| Explicit RX **JTOL** (SJ vs frequency) | **No** | P802.3dj Table 179–12 (electrical); CEI-112G-XSR Table 24-12 / Fig 24-5; optical SRS SJ in dj Cl. 180.9.13 |
| Signaling-rate / **ppm** | **No** | dj optical/electrical: **106.25 ± 50 ppm**; CEI §3.2.11: **±100 ppm** async |
| TX electrical jitter (Jrms, J4u/J8u, EOJ) | **No** (optical TDEC only) | CEI-56G-XSR-NRZ Table 19-8; CEI-112G-XSR Table 24-5; dj Cl. 178/179 |
| CDR loop BW | **No** | Derived — see [CDR_Standards_Traceability.md](./CDR_Standards_Traceability.md) |
| SSC | **No** (Ethernet optical lineage) | N/A |
| Pre-FEC BER for Gen2 FEC | Gen1: **2.4E-4** | dj concatenated FEC may allow ~1E-3…5E-3 — **project decision** |

---

## 8. IEEE P802.3dj/D1.3 — content that fills MSA gaps

*Local extract: `standards/_dj_d13.txt`. MSA cites a later “2p3” draft; numbers below are from D1.3 and must be re-checked when the cited draft is obtained.*

### 8.1 Optical PMD at 106.25 GBd (Cl. 180 DR family) — same numbers as MSA eye budget, PAM4 format

Closest optical parallel at **Gen2 baud** (modulation is **PAM4**, not NRZ):

| Parameter | dj Cl. 180 (DR) | MSA Gen1 NRZ |
|-----------|-----------------|--------------|
| Signaling rate | **106.25 ± 50 ppm** GBd | 53.125 Gbaud (ppm not stated) |
| TDECQ / TECQ max | **3.4 dB** | TDEC **3.4 dB** |
| SECQ (SRS) | **3.4 dB** | SEC **3.4 dB** |
| Over/undershoot | 22% | 22% |
| ER min | 3.5 dB | 3.5 dB |
| Transition time max | **8 ps** (PAM4 @ 106.25) | 17 ps (NRZ @ 53.125) |
| RIN | −139 dB/Hz | −138 dB/Hz |
| Reach | 2 m … 500 m | 500 m SMF |

Use dj for: **ppm**, TDECQ *method* at 106 GBd, and SRS calibration practice. Do **not** copy PAM4 equalizer assumptions into an NRZ Gen2 TDEC without an explicit Gen2 MSA decision.

### 8.2 Electrical RX jitter tolerance (Table 179–12) — primary JTOL candidate for CDR

Used by Cl. 178/179 receiver JTOL at 106.25 GBd electrical:

| Case | A | B | C | D | E | F | G |
|------|---|---|---|---|---|---|---|
| Frequency (MHz) | 0.04 | 0.1333 | 0.4 | 1.333 | 4 | 12 | 40 |
| Amplitude (UI pk-pk) | 5 | 1.5 | 0.5 | 0.15 | 0.05 | 0.05 | 0.05 |

Corner ≈ **4 MHz @ 0.05 UI** (flat high-frequency shelf). This is the cleanest published mask in the local standards set for Gen2 CDR bandwidth floor work.

### 8.3 Signaling-rate tolerance summary (dj)

| Context | Tolerance |
|---------|-----------|
| 106.25 GBd PMD TX/RX (Cl. 178/179/180…) | **± 50 ppm** |
| Some AUI/XS cases when paired with certain PMDs | ±50 ppm instead of ±100 ppm |

For a plesiochronous optical link with independent ends: design for **±50 ppm each end → ±100 ppm relative** unless OCI Gen2 states otherwise. (CEI allows ±100 ppm each end — more severe; see §9.)

---

## 9. OIF CEI-05.2 — electrical PMA / XSR cross-check

*MSA does not cite CEI, but CPO die-to-OE links are XSR-class; local CEI-05.2 is the available JTOL/jitter decomposition source.*

### 9.1 Common baud tolerance (CEI §3.2.11)

All CEI interfaces: operate asynchronously with **±100 ppm** from nominal baud.

### 9.2 CEI-56G-XSR-NRZ (Clause 19) — Gen1-baud NRZ XSR

| Parameter | Value |
|-----------|-------|
| Baud | 39.8 … 58.0 Gsym/s (±100 ppm clocks) |
| TX Vdiff | 250 … 400 mVppd |
| TX rise/fall 20–80% | ≥ 4 ps (min edge; table lists 4 ps) |
| TX UUGJ | ≤ 0.15 UIpp |
| TX UBHPJ | ≤ 0.15 UIpp |
| TX EOJ | ≤ 0.035 UIpp |
| TX TJ | ≤ 0.28 UI |
| Eye mask | X1=0.14 UI, X2=0.4 UI, Y1=125 mV, Y2=200 mV |
| RX | Tolerate TX jitter Table 19-8 + compliant channel @ clause BER |

Best **NRZ** electrical analog at Gen1-class baud for driver / microbump budgeting.

### 9.3 CEI-112G-XSR-PAM4 (Clause 24) — JTOL mask + TX jitter at ~56 GBd PAM4

| Parameter | Value |
|-----------|-------|
| Baud | 36 … 58 Gsym/s |
| TX J8u | ≤ 0.1546 UI |
| TX JRMS | ≤ 0.0224 UIrms |
| TX EOJ | ≤ 0.025 UIpp |
| TX SNDR | ≥ 32.5 dB |
| CRU corner | **f_CRU = f_b / 13280** |
| JTOL test points | f_CRU/100, /3, 1×, 3×, 10× with SJ = **5, 0.15, 0.05, 0.05, 0.05 UI** |
| JTOL mask | f &lt; f_b/1.328e6: NS; slope region to f_b/13280 @ 5 UI; then **0.05 UI** to 10 f_CRU |

At f_b = 53.125 GBd: f_CRU ≈ **4.0 MHz**. At f_b = 106.25 GBd (if same ratio applied): f_CRU ≈ **8.0 MHz**.

---

## 10. Consolidated PMA design checklist

### 10.1 Normative from OCI MSA (Gen1) — must satisfy / scale

- [ ] TDEC ≤ 3.4 dB @ BER 2.4E-4, BT4 ref RX = 0.5×baud, hist @ 0.4/0.6 UI  
- [ ] TX transition ≤ 17 ps (20–80%) @ Gen1; re-spec in ps for Gen2  
- [ ] TX over/undershoot ≤ 22%; ER ≥ 3.5 dB; RIN_OMA ≤ −138 dB/Hz  
- [ ] OMA / Pavg / dOMA / squelch OMA per Tables 2-2 / 2-3  
- [ ] SRS ≤ −6.2 dBm OMA with **SEC = 3.4 dB**, aggressors −3.2 dBm  
- [ ] BER floor ≤ 1E-6 over stated OMA range  
- [ ] t_LOL ≤ 50 ms; LOS thresholds; freeze behavior during 60–75 ms squelch  
- [ ] Deskew 0–7 UI; pattern detect @ BER 1E-4; phase-continuous pattern swaps  
- [ ] Link: 500 m, IL ≤ 2.5 dB, CD −0.9…1.7 ps/nm, MPI 0.2 dB  

### 10.2 From standards (fill MSA gaps) — confirm for Gen2

- [ ] Adopt JTOL: prefer **dj Table 179–12**; cross-check CEI-112G-XSR Fig 24-5  
- [ ] Adopt ppm: **±50 ppm** (dj PMD) or **±100 ppm** (CEI) — pick and size frequency path  
- [ ] TX electrical jitter budget: CEI-56G-XSR-NRZ (NRZ) and/or CEI-112G-XSR / dj Cl. 178  
- [ ] Decide Gen2 pre-FEC BER (keep 2.4E-4 vs dj-style concatenated FEC)  
- [ ] Re-pull numbers when MSA-cited **P802.3dj 2p3** (or later) is available vs local D1.3  

### 10.3 Explicitly *not* required by MSA / Ethernet optical lineage

- SSC tracking  
- Published optical SJ table inside the OCI PHY PDF itself  

---

## 11. Gen2 quick map (53.125 → 106.25 GBd NRZ)

| MSA Gen1 quantity | Gen2 working assumption |
|-------------------|-------------------------|
| 53.125 GBd | **106.25 GBd** |
| Ref RX 26.5625 GHz | **53.125 GHz** BT4 |
| TDEC/SEC 3.4 dB | Keep until Gen2 MSA; method may become TDECQ-like |
| Transition ≤ 17 ps (0.9 UI) | ≤ **~8.5 ps** if same UI fraction |
| SRS SEC 3.4 dB @ 2.4E-4 | Same stress *ratio* until FEC decision changes EO |
| No JTOL table | Use dj Table 179–12 (scale interpretation in CDR doc) |
| No ppm | **±50 ppm** (dj) or **±100 ppm** (CEI) |

Detailed CDR bandwidth / ppm derivation: [CDR_Standards_Traceability.md](./CDR_Standards_Traceability.md).

---

## Revision history

| Date | Rev | Notes |
|------|-----|-------|
| 2026-07-19 | 0.1 | Initial capture from OCI Optical PHY v1.0 + local P802.3dj/D1.3 and CEI-05.2 |
