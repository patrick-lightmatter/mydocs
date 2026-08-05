# 106G NRZ CPO TX Budget — OCI Gen2

**System:** Lightmatter OCI Gen2, GlobalFoundries process  
**Modulation:** NRZ, 106.25 GBaud per lane, 4λ DWDM  
**Date:** 2026-08-02  
**Sources:** 200G-OCI Optical Phy Spec v1.0 (Gen1 baseline), IEEE 802.3ck-2022,  
IEEE P802.3dj D1.3, ECEN721 Lecture 7 (TX Analysis), ECEN720 Lecture 10 (Jitter)

---

## 1. Overview and Scope

This document builds the transmitter-side link budget for OCI Gen2 at 106.25 GBaud NRZ.  
The OCI Gen1 spec (53.125 GBaud) is the normative baseline; all per-UI timing parameters
scale by ÷2, all frequency/bandwidth parameters scale by ×2, and all optical power
parameters are unchanged. The TX chain runs from the External Laser Source (ELS) through
the OCI chiplet's MRM driver → Micro-Ring Resonator (MRM) modulator to the fiber attach
point (TP2).

### BER Conventions in This Document

Two distinct BER thresholds are used — they apply to different layers:

| Layer | BER target | Q | Applies to |
|---|---|---|---|
| TX electrical driver jitter | **1×10⁻¹²** | **7.035** | Driver DJ/RJ/PSIJ spec, eye mask |
| OCI optical TDEC measurement | **2.4×10⁻⁴** | 3.54 | Optical TX compliance (OCI Gen2 spec) |

The 1e-12 BER is the uncoded raw link BER target (conservative; no FEC assumed in the
driver spec). The 2.4e-4 threshold is the KP4 pre-FEC BER used in the OCI optical TDEC
compliance measurement only.

### Scope
- TX driver electrical specification (swing, EQ, rise/fall, jitter, eye mask)
- OCI Gen2 TX optical specifications (scaled from Gen1 Table 2-2)
- MRM modulator physics: transform-limited spectrum, chirp, bandwidth
- Chromatic dispersion penalty at 1310 nm operating band
- Extinction ratio and OMA power analysis
- RIN noise penalty
- TDEC budget (modulator + driver + dispersion + ER)
- TX jitter budget (Dual Dirac, BER = 1×10⁻¹²)
- TX optical power chain: ELS → MRM → TP2
- ELS interface requirements

---

## 2. TX System Architecture

```
ELS (CW, 4λ per group)
  │
  ├─ PMF pigtail (~0.5 m, IL ≈ 0.5 dB)
  │
  └─► OCI Chiplet (per-lane)
        │
        ├─ CDNS L250 SerDes TX
        │    └─ 4-tap TX FFE (c-2, c-1, c0, c+1)
        │         │
        │         ▼
        ├─ MRM Driver (integrated, NOT 50Ω)
        │    ├─ Differential output swing: 0.5–1.5 Vpp diff
        │    ├─ Asymmetric rise/fall control (MRM nonlinearity cancellation)
        │    └─► MRM electrode (RC load, no transmission line)
        │
        ├─ MRM Modulator (ring resonator, ~3 dB IL on-state)
        │    ├─ CW laser → intensity modulation (α ≈ 0, chirp-free)
        │    ├─ Heater DAC for thermal wavelength lock
        │    └─ Optical output: NRZ at TP2
        │
        ├─ Fiber attach / coupler (~0.5 dB IL)
        │
        └─► TP2 (optical TX compliance reference plane)
              │
              └─► 500 m SMF-28 → TP3 → RX chiplet
```

**Measurement planes:**
- **TP1**: ELS output (laser facet, before PMF)
- **TP2**: OCI chiplet fiber output (OCI optical TX compliance)
- **TP3**: Receiver fiber input (after 500 m fiber)

---

## 3. TX Driver Electrical Specification

The OCI Gen2 MRM driver is co-designed and co-integrated with the MRM on the GF photonics
platform. This integration changes the driver spec relative to a standard SerDes TX driver.
The following taxonomy follows industry convention for NRZ drivers (reference: A. Izadi,
Lightmatter internal communication).

### 3.1 Differential Output Swing

The driver must swing the MRM PN junction voltage from the "off-resonance" (high
transmission = "1") state to "on-resonance" (low transmission = "0") state.

| Parameter | Value | Notes |
|---|---|---|
| Vswing, differential, min | 0.5 Vpp | Minimum for ER ≥ 3.5 dB |
| Vswing, differential, typ | 1.0 Vpp | Design target for ER ≈ 4.5 dB |
| Vswing, differential, max | 1.5 Vpp | Limited by GF device reliability |
| Common-mode output | Device-dependent | Set by MRM DC bias for resonance alignment |

Higher swing increases ER but increases driver power consumption quadratically.
The operating point balances ER vs power and ring heating (resonance shift from self-heating).

### 3.2 Output Impedance and Return Loss

**NOT REQUIRED for integrated MRM driver.**

The MRM electrode is a lumped RC load driven by a co-located driver — there is no
transmission line between them. The standard 50Ω output impedance and return-loss specs
(ERL, common-mode return loss) that appear in external-drive TX specs do not apply here.

The relevant electrical load seen by the driver is:
```
C_MRM ≈ 10–30 fF     (depletion PN junction)
R_series ≈ 10–30 Ω   (contact + via resistance)
τ_RC = R × C ≈ 0.3–0.9 ps  →  BW_RC ≈ 180–530 GHz  (not the bandwidth limiter)
```

The MRM optical photon lifetime (BW_ring ≈ 60 GHz target) is the dominant bandwidth
constraint — not the driver RC product.

### 3.3 TX Equalization

From Arash Izadi: *"Transmitter equalization coefficient range and resolution (ex. Pre,
Post, 3 bit, 0.3x max)"*

The driver implements a 3-tap FIR equalizer to pre-compensate ISI introduced by the
combined driver + MRM bandwidth channel:

```
y(k) = c_{-1}·x(k+1) + c_0·x(k) + c_{+1}·x(k-1)

where x(k) ∈ {−1, +1} (NRZ data symbols)
```

| Tap | Name | Range | Resolution | Typical value | Purpose |
|---|---|---|---|---|---|
| c₋₁ | Pre-cursor | 0 to −0.3 | 3-bit (8 steps) | −0.10 | Pre-cursor ISI from driver latency/phase |
| c₀ | Main cursor | remainder | — | ~0.70 | Signal amplitude (normalized) |
| c₊₁ | Post-cursor | 0 to −0.3 | 3-bit (8 steps) | −0.22 | Post-cursor ISI from MRM Lorentzian rolloff |

Normalization constraint: |c₋₁| + c₀ + |c₊₁| = 1 (total power preserved)

With c₋₁ = −0.10 and c₊₁ = −0.22: c₀ = 1 − 0.10 − 0.22 = 0.68

The post-cursor is dominant because the MRM's Lorentzian transfer function creates
significant post-cursor ISI at 106G (BW_MRM/BR = 60/106 ≈ 0.57 — well below Nyquist).

**Step size:** With 3-bit resolution over a 0.3 range: step = 0.3/7 ≈ 0.043 per tap
(0 to 0.3 in 8 levels). This gives sufficient resolution to minimize residual ISI.

### 3.4 Rise/Fall Time Constraints

Rise and fall time (20%–80%) at the MRM electrode sets the final electrical slew rate
before optical conversion. The MRM's photon lifetime then further limits the optical
edge rate.

| Parameter | Spec | Notes |
|---|---|---|
| Rise time, max (20-80%) | ≤ 6 ps | At MRM electrode, after TX EQ |
| Fall time, max (20-80%) | ≤ 6 ps | Symmetric target before asymmetric correction |
| Rise time, driver BW implied | BW ≥ 58 GHz | 0.35 / 6 ps |
| Optical rise time at TP2 | ≤ 8.5 ps | After MRM conversion (OCI optical spec) |

The electrical 6 ps target at the driver output gives margin for the MRM optical
bandwidth to further limit the optical edge to ≤ 8.5 ps at TP2.

### 3.5 Asymmetrical Peaking and Rise/Fall Time Control

**Lightmatter-specific feature** (per A. Izadi): *"To cancel MRM nonlinearity."*

The MRM resonance has a Lorentzian lineshape, making the transmission a nonlinear function
of the drive voltage. The CW laser is parked slightly off-resonance (typically blue-detuned).
This creates asymmetric optical edge speeds:

```
Optical transfer:  T(V) = T_max / (1 + (V − V_res)² / (ΔV_FWHM/2)²)

Near resonance (V ≈ V_res): steep slope → fast optical transition (one polarity)
Far from resonance:           shallow slope → slow optical transition (other polarity)
```

Result at TP2 (without correction):
- One edge (into resonance): fast optical rise → short transition
- Other edge (out of resonance): slow optical rise → long transition
- Consequence: **asymmetric eye, increased DCD, TDEC contribution**

Correction (driver-applied asymmetric peaking):
- Pre-emphasis amplitude asymmetry: apply more voltage overshoot on the slow edge
- Edge rate asymmetry: tune rising vs falling slew rate independently
- Target: tr_optical ≈ tf_optical at TP2, minimizing DCD

This requires characterization of the specific MRM bias point and resonance shape,
and calibration per-channel (each MRM ring may have a slightly different Lorentzian).

### 3.6 Jitter Limits

Per A. Izadi: *"Random and deterministic jitter limits (DJ, RJ, PSIJ)"*

At BER = **1×10⁻¹²** (Q = 7.035, 2Q = 14.07):

```
TJ(1e-12) = DJ_pp + 14.07 × σ_RJ
```

| Jitter type | Symbol | Allocation | UI (9.41 ps) | Source |
|---|---|---|---|---|
| Duty cycle distortion | DCD | ≤ 0.40 ps_pp | ≤ 4.3% | Clock divider tr/tf mismatch |
| ISI — electrical | ISI_elec | ≤ 0.60 ps_pp | ≤ 6.4% | Residual after TX EQ |
| ISI — optical (MRM) | ISI_opt | ≤ 0.40 ps_pp | ≤ 4.3% | MRM BW + CD combined |
| Bounded uncorrelated | BUJ | ≤ 0.30 ps_pp | ≤ 3.2% | Crosstalk from adjacent rings |
| Periodic sinusoidal | PSIJ | ≤ 0.30 ps_pp | ≤ 3.2% | VCO/supply noise, PLL ref feedthrough |
| **Total DJ_pp** | | **≤ 2.00 ps_pp** | **≤ 21.3% UI** | RSS of bounded terms |
| Random jitter | σ_RJ | **≤ 0.15 ps_rms** | ≤ 1.6% UI | SerDes TX PLL VCO |
| **Total TJ at BER=1e-12** | | **≤ 4.11 ps_pp** | **≤ 43.7% UI** | = 2.00 + 14.07×0.15 |
| **Eye opening** | | **≥ 5.30 ps** | **≥ 56.3% UI** | = 9.41 − 4.11 |

### 3.7 Eye Mask

The eye mask combines all the above into a single go/no-go compliance test. Eye mask
compliance is measured at the TX output (electrical at the MRM electrode, optical at TP2).

**Electrical eye mask (100GAUI-1, IEEE 802.3ck Annex 120F):**  
Normalized to UI = 9.41 ps. The mask defines a forbidden zone centered in the eye.
Typical inner mask corners:

```
(x₁, ±y₁) = (0.25 UI, ±0.6 × amplitude_pp)
(x₂, ±y₂) = (0.40 UI, ±0.3 × amplitude_pp)
```

No waveform sample shall fall within the mask inner region at the specified BER = 1e-12.

**Optical eye mask (OCI Gen2 at TP2):**  
Defined by the OCI Gen2 specification (TBD at time of writing; expected to follow OCI
Gen1 eye mask scaled to 106.25 GBaud). Key constraints embedded in optical spec:
TDEC ≤ 3.4 dB, transition time ≤ 8.5 ps, overshoot ≤ 22%, ER ≥ 3.5 dB.

---

## 4. Gen1 → Gen2 Scaling Rules

| Parameter | Gen1 | Gen2 | Scale |
|---|---|---|---|
| Baud rate | 53.125 GBaud | **106.25 GBaud** | ×2 |
| UI | 18.82 ps | **9.41 ps** | ÷2 |
| TDEC ref RX BW | 26.5625 GHz | **53.125 GHz** | ×2 |
| Rise time spec (20-80%), optical | 17 ps | **~8.5 ps** | ÷2 |
| Rise time spec (20-80%), driver | ~10 ps | **~6 ps** | ÷2 |
| Spectral BW (transform-limited) | ~0.30 nm | **~0.61 nm** | ×2 |
| Optical power specs (OMA, Pavg) | — | **unchanged** | ×1 |
| TDEC limit | 3.4 dB | **3.4 dB** | ×1 |
| ER | 3.5 dB min | **3.5 dB min** | ×1 |
| RIN_OMA | −138 dB/Hz | **−138 dB/Hz** | ×1 |
| CD (fiber channel) | −0.9 to +1.7 ps/nm | **same** | ×1 |
| Driver jitter BER | 1×10⁻¹² | **1×10⁻¹²** | ×1 |
| Q factor (driver jitter BER=1e-12) | 7.035 | **7.035** | ×1 |
| TDEC BER (optical compliance) | 2.4×10⁻⁴ | **2.4×10⁻⁴** | ×1 |

**Note on TDEC tightness:** The Gen2 reference receiver has twice the bandwidth, so it
passes more of the MRM and driver roll-off into the eye measurement. A MRM with Gen1
bandwidth (~30 GHz) would generate significantly more ISI and fail TDEC at Gen2.
The MRM and driver must both target ≥ 60 GHz 3dB bandwidth.

---

## 5. OCI Gen2 TX Optical Specifications

Derived from OCI 200G v1.0 Table 2-2 with Gen2 scaling.  
Wavelengths: Group A: 1307.8–1315.1 nm; Group B: 1327.5–1335.0 nm (4 channels per group).

### 5.1 TX Compliance Spec Table (at TP2)

| Parameter | Gen1 (53G) | **Gen2 (106G)** | Unit | Notes |
|---|---|---|---|---|
| Baud rate | 53.125 | **106.25** | GBaud | |
| SMSR | ≥ 30 | **≥ 30** | dB | Laser side-mode suppression |
| Pavg per channel, min | −8.5 | **−8.5** | dBm | |
| Pavg per channel, max | 0 | **0** | dBm | |
| Pavg total per group (4λ), max | +6 | **+6** | dBm | Sum of 4 channels |
| OMA per channel, min | max(−5.5, −6.9+TDEC) | **same formula** | dBm | TDEC in dB |
| OMA per channel, max | −1 | **−1** | dBm | |
| TDEC, max | 3.4 | **3.4** | dB | Ref RX: BT-4, BW = BR/2 = 53.125 GHz |
| dTDEC \|SSPR−PRBS13\|, max | 0.4 | **0.4** | dB | Pattern sensitivity |
| ER (extinction ratio), min | 3.5 | **3.5** | dB | P1/P0 |
| ER typical | 4.5 | **4.5** | dB | Design target |
| Transition time (20-80%), max | 17 | **~8.5** | ps | Optical, at TP2 |
| Overshoot / undershoot, max | 22 | **22** | % | Relative to OMA |
| RIN\_OMA, max | −138 | **−138** | dB/Hz | At ORL = 21.4 dB |
| Squelched OMA, max | −15 | **−15** | dBm | Per channel, during squelch |
| ORL tolerance | 21.4 | **21.4** | dB | |
| TX data path reflectance | −19 | **−19** | dB | Back-reflection into fiber |
| OE laser input reflectance | −26 | **−26** | dB | |

### 5.2 OMA Compliance Floor vs TDEC

```
OMA_min = max(−5.5 dBm, −6.9 dBm + TDEC_dB)
```

| TDEC (dB) | OMA_min (dBm) | Governing term |
|---|---|---|
| 0.0 | −5.5 | Fixed floor |
| 1.4 | −5.5 | Crossover point |
| 1.9 (design target) | −5.0 | TDEC-dependent |
| 3.4 (spec max) | −3.5 | TDEC-dependent |

---

## 6. MRM Modulator Physics

### 6.1 Transform-Limited Spectrum (α = 0)

The MRM modulates intensity by shifting the ring resonance on/off the CW carrier wavelength.
Unlike a DML, the laser frequency is fixed — only the amplitude changes. This gives:
- **Chirp parameter α = 0** (no frequency modulation)
- **Transform-limited optical spectrum** (narrowest possible for a given data rate)
- Sinc²-shaped power spectrum with 3 dB bandwidth ≈ baud rate B

Contrast with directly-modulated transmitters (Lecture 7):

| Transmitter type | α | Spectral width | Dispersion reach |
|---|---|---|---|
| DML | 4–6 | Δλ × √(α²+1) ≈ 4–6× wider | Limited; 4× shorter than EML |
| EML (MZM/EAM) | ≈ 0 | Δλ_TL = λ²B/c | Maximum reach |
| **MRM (OCI Gen2)** | **≈ 0** | **Δλ_TL** | **Maximum reach** |

### 6.2 MRM Bandwidth Requirement

The MRM optical 3dB bandwidth (set by the ring photon lifetime) must be large enough to
support 106.25 GBaud NRZ with acceptable TDEC. Ring photon lifetime:

```
τ_ph = 1 / (2π × BW_MRM)   →   BW_MRM = 60 GHz: τ_ph = 2.65 ps
```

The Lorentzian roll-off creates post-cursor ISI. The faster the ring (shorter τ_ph,
wider BW), the lower the ISI but the higher the required coupling (→ higher IL trade-off).
See §10.4 for the BW vs TDEC trade-off table.

### 6.3 MRM Insertion Loss

- On-state (through-port when off-resonance): **~2–3 dB** (waveguide + coupler)
- Off-state extinction (when on-resonance): sets the ER floor
- Thermal sensitivity: ~80 pm/°C → heater closed-loop required
- WDM: 4 MRM rings per group, individual thermal tuning per ring

---

## 7. Spectral Linewidth and Chromatic Dispersion

### 7.1 Transform-Limited Spectral Linewidth

```
Δλ = (λ² / c) × B                                       [from Lecture 7]

At λ = 1311 nm (Group A center), B = 106.25 GHz:
Δλ = (1311×10⁻⁹)² × 106.25×10⁹ / (3×10⁸) = 0.609 nm
```

| Quantity | Gen1 | Gen2 |
|---|---|---|
| Baud rate | 53.125 GHz | 106.25 GHz |
| Δλ (transform-limited) | 0.305 nm | **0.609 nm** |
| ELS laser linewidth | ≤ 0.0007 nm (1 MHz) | **same** |
| Dominant contributor | Signal modulation | **Signal modulation** |

The ELS linewidth (0.0007 nm) is negligible vs the modulation spectral width (0.609 nm).
The system is firmly in the transform-limited (not source-limited) regime.

### 7.2 Chromatic Dispersion Penalty

OCI Gen2 operates at 1308–1335 nm, near SMF-28 zero dispersion (λ₀ ≈ 1310 nm):

| Channel group | Center λ | Typical D | 500 m CD |
|---|---|---|---|
| A | 1311 nm | ~0.1 ps/(nm·km) | ~0.05 ps/nm |
| B | 1331 nm | ~0.7 ps/(nm·km) | ~0.35 ps/nm |

OCI spec maximum total channel dispersion: |CD| ≤ 1.7 ps/nm

Maximum pulse broadening (worst case, Group B at spec limit):
```
ΔT = |CD_max| × Δλ = 1.7 ps/nm × 0.609 nm = 1.04 ps = 0.11 UI
```

**1 dB dispersion penalty condition (Lecture 7):** ΔT ≤ UI/2 = 4.7 ps

At ΔT = 1.04 ps → **well below 1 dB threshold. CD penalty < 0.1 dB.**

This is why OCI Gen2 targets 1310 nm: near-zero dispersion eliminates CD as a
significant TX budget line item. A 1550 nm design at the same baud rate would incur:
```
D_SMF(1550nm) ≈ 17 ps/(nm·km)
ΔT = 17×0.5 × 0.609 nm ≈ 5.2 ps = 0.55 UI → ~0.8 dB TDEC
```

---

## 8. Extinction Ratio and OMA Analysis

### 8.1 Definitions

```
ER = P1 / P0      (linear ratio)
OMA = P1 − P0
P_avg = (P1 + P0) / 2
OMA = 2(ER−1)/(ER+1) × P_avg
```

### 8.2 Average-Power Receiver Penalty

For a TIA-noise-limited receiver (constant noise), sensitivity referenced to Pavg:

```
PP_avg = (ER + 1) / (ER − 1)    [linear, Lecture 7]
```

| ER (dB) | ER (linear) | PP_avg (dB) | OMA/P_avg |
|---|---|---|---|
| 3.5 (min spec) | 2.24 | 4.18 dB | 0.765 (−1.16 dB) |
| 4.5 (typical) | 2.82 | 3.22 dB | 0.952 (−0.21 dB) |
| 6.0 | 3.98 | 2.09 dB | 0.992 (−0.04 dB) |
| ∞ (ideal NRZ) | ∞ | 0 dB | 2 (+3.01 dB) |

### 8.3 OMA-Based Specification Advantage

The OCI spec is **OMA-based**. At constant OMA, ER incurs no receiver noise penalty
(the TIA noise floor is fixed; OMA sets the SNR directly). ER still matters for:
1. P0 leakage → reduced eye amplitude → TDEC contribution (§10.2)
2. Pavg budget → MRM self-heating, group power limit
3. Higher ER → lower required Pavg for same OMA → saves ~1 dB ELS power (§12.2)

### 8.4 P0 Leakage → Eye Amplitude Reduction (TDEC Contribution)

```
Normalized eye amplitude = 1 − 2/(ER+1) = (ER−1)/(ER+1)

At ER = 3.5 dB (2.24): normalized = 1.24/3.24 = 0.383 → eye loss ≈ 0.4 dB TDEC
At ER = 4.5 dB (2.82): normalized = 1.82/3.82 = 0.476 → eye loss ≈ 0.3 dB TDEC
```

---

## 9. RIN Budget

### 9.1 RIN-to-SNR Calculation

```
SNR_RIN = 1 / (RIN_OMA × BW_noise)
BW_noise ≈ 0.75 × BR = 0.75 × 106.25 GHz = 79.7 GHz   (BT-4 effective noise BW)

RIN_OMA = −138 dB/Hz = 1.585×10⁻¹⁴ /Hz  (TX compliance spec max)

SNR_RIN = 1 / (1.585×10⁻¹⁴ × 79.7×10⁹) = 1 / 1.263×10⁻³ = 792 → 28.99 dB
```

### 9.2 RIN Penalty at BER = 1×10⁻¹²

```
Q = 7.035,  Q² = 49.5  →  required SNR = 49.5  →  16.94 dB

RIN margin = 28.99 − 16.94 = 12.05 dB

RIN power penalty = 10 log₁₀(1 + Q²/SNR_RIN) = 10 log₁₀(1 + 49.5/792) = 10 log₁₀(1.0625)
                  ≈ 0.26 dB   (small, included in TDEC margin)
```

At the optical TDEC measurement BER = 2.4×10⁻⁴ (Q = 3.54, Q² = 12.5):
```
RIN margin = 28.99 − 10.98 = 18.0 dB → RIN penalty = 0.07 dB (negligible)
```

---

## 10. TDEC Budget

### 10.1 TDEC Definition and Measurement

TDEC measures optical eye closure relative to an ideal reference at the OCI TX compliance
BER threshold (note: this is NOT the driver jitter BER):

```
TDEC = −10 log₁₀(OMA_meas / OMA_ref)
```

**Gen2 measurement conditions:**
- Reference receiver: 4th-order Bessel-Thomson, BW = **53.125 GHz** (= BR/2)
- Equalizer: **none** at the RX
- Test pattern: **SSPR** (Single Spectrum Pseudo-Random)
- Eye histogram center: 0.4 UI × 9.41 ps = **3.76 ps** from each edge
- BER threshold: **2.4×10⁻⁴** (KP4 pre-FEC optical compliance)
- dTDEC: |TDEC_SSPR − TDEC_PRBS13| ≤ 0.4 dB

### 10.2 TDEC Contributors — Budget Allocation

| Contributor | Mechanism | Penalty (dB) | Notes |
|---|---|---|---|
| MRM optical BW | Lorentzian rolloff at 60 GHz → post-cursor ISI | 0.6 | BW_MRM = 60 GHz target |
| TX driver + EQ residual | CDNS L250 SerDes TX FFE; residual ISI through 53 GHz ref RX | 0.5 | Post 3-tap EQ |
| Finite extinction ratio | P0 leakage at ER = 4.5 dB | 0.3 | See §8.4 |
| MRM nonlinearity | Lorentzian → asymmetric eye; partially corrected by asymmetric driver | 0.2 | Residual after driver correction |
| DCD / rise-fall asymmetry | tr ≠ tf optical, after asymmetric peaking correction | 0.15 | Residual DCD |
| Chromatic dispersion | 1.04 ps broadening × 53 GHz ref RX ISI | 0.1 | Near-zero at 1310 nm |
| Overshoot / ringing | MRM coupled-ring response; driver pre-emphasis | 0.15 | Residual |
| **Design sub-total** | | **2.0** | |
| **Margin to spec** | | **1.4** | 41% headroom |
| **Spec limit (max)** | | **3.4** | OCI Gen2 optical requirement |

### 10.3 MRM Bandwidth vs TDEC

| BW_MRM | BW_MRM / BR | TDEC_MRM contribution | Driver EQ needed |
|---|---|---|---|
| 40 GHz | 0.38 | ~1.2 dB | Aggressive 3-tap |
| 60 GHz | 0.56 | ~0.6 dB | 2-tap sufficient |
| 80 GHz | 0.75 | ~0.3 dB | 1-tap sufficient |
| 106 GHz | 1.0 | ~0.1 dB | No EQ needed |

**Target: BW_MRM ≥ 60 GHz → TDEC_MRM ≤ 0.6 dB.**

---

## 11. TX Jitter Budget — Dual Dirac Model

**BER = 1×10⁻¹² (Q = 7.035, 2Q = 14.07)** — applies to TX driver electrical compliance.

### 11.1 Jitter Taxonomy (Lecture 10, Palermo ECEN720)

```
TJ(t) = RJ(t) ∗ DJ(t)    (PDF convolution)
DJ(t) = SJ/PSIJ(t) ∗ DCD(t) ∗ ISI(t) ∗ BUJ(t)
```

| Type | Symbol | Source | Statistics |
|---|---|---|---|
| Random Jitter | RJ | TX PLL VCO thermal noise | Gaussian (unbounded); σ_RJ |
| Periodic / Sinusoidal | PSIJ | Power supply noise, PLL ref feedthrough | Periodic; arcsine PDF; bounded |
| Duty Cycle Distortion | DCD | Clock divider tr/tf mismatch, asymmetric buffers | Dual delta; bounded |
| ISI Jitter | ISI | BW-limited channel (electrical + optical) | Bounded; reduced by TX EQ |
| Bounded Uncorrelated | BUJ | Crosstalk from adjacent WDM rings | Bounded; uncorrelated to victim |

### 11.2 Dual Dirac Model

```
DJ(t) = ½ δ(t − DJ_pp/2) + ½ δ(t + DJ_pp/2)

TJ(BER) = DJ_pp + 2 × Q(BER) × σ_RJ

At BER = 1×10⁻¹²: Q = 7.035
TJ(1e-12) = DJ_pp + 14.07 × σ_RJ
```

### 11.3 Gen2 TX Driver Jitter Budget

UI_Gen2 = 9.41 ps, BER target = 1×10⁻¹²

| Component | Budget | % UI | Governed by |
|---|---|---|---|
| DCD | 0.40 ps_pp | 4.3% | SerDes TX clock divider duty cycle |
| ISI — electrical (after EQ) | 0.60 ps_pp | 6.4% | Residual ISI through 3-tap TX FFE |
| ISI — optical (MRM 60 GHz) | 0.40 ps_pp | 4.3% | Ring photon lifetime + CD = 1 ps |
| BUJ (adjacent ring crosstalk) | 0.30 ps_pp | 3.2% | 4λ WDM rings on same die, thermal/optical |
| PSIJ (VCO supply, PLL ref) | 0.30 ps_pp | 3.2% | LDO-regulated supply; spread-spectrum |
| **DJ_pp total** | **2.00 ps_pp** | **21.3% UI** | Sum of bounded components |
| **σ_RJ** | **0.15 ps_rms** | 1.6% UI | SerDes TX PLL VCO, ~100 fs/√Hz integrated |
| **TJ at BER = 1e-12** | **4.11 ps_pp** | **43.7% UI** | = 2.00 + 14.07×0.15 |
| **Eye opening (timing)** | **5.30 ps** | **56.3% UI** | = 9.41 − 4.11 |

### 11.4 Jitter–TDEC Relationship

TDEC captures **vertical** eye closure (ISI-amplitude); jitter captures **horizontal** eye
closure (timing). The TDEC measurement excludes the outer 0.4 UI per edge (histogram
centering), providing tolerance for horizontal jitter up to:

```
DJ_pp allowance within TDEC window = 2 × 0.4 UI − 2Q_opt × σ_RJ
  (where Q_opt = 3.54 at optical BER = 2.4e-4)
= 2 × 3.76 ps − 7.07 × 0.15 ps = 7.52 − 1.06 = 6.46 ps_pp

Design DJ_pp = 2.00 ps_pp → TDEC window margin = 6.46 − 2.00 = 4.46 ps_pp ✓
```

---

## 12. TX Optical Power Chain Budget

### 12.1 Per-Channel Loss (ELS → TP2)

| Element | Nominal IL | Range | Notes |
|---|---|---|---|
| PMF pigtail + connectors | 0.8 dB | 0.5–1.0 | APC connector, 0.5 m PMF |
| OCI chiplet fiber coupler (in) | 0.7 dB | 0.5–0.8 | Lensed fiber or grating coupler |
| MRM on-state insertion loss | 2.5 dB | 2.0–3.5 | Waveguide + coupler through-port |
| On-chip waveguide routing | 0.7 dB | 0.5–1.0 | Bends, crossings, tapers |
| Fiber attach (out) | 0.3 dB | 0.3–0.5 | SMF coupling |
| **Total TX path loss** | **5.0 dB** | 3.8–6.8 | |

### 12.2 ELS Power Requirement per Channel

Design target: TDEC = 2.0 dB → OMA_TP2 = −5.0 dBm (from §5.2)

```
At ER = 4.5 dB (2.82): OMA = 0.952 × P_avg  → P_avg = OMA/0.952

P_avg at TP2 = −5.0 dBm + 0.21 dB = −4.79 dBm

Required ELS CW power per channel = −4.79 + 5.0 = +0.21 dBm (1.05 mW)
```

Higher ER improves ELS efficiency: at ER = 6.0 dB (3.98 linear):
```
OMA = 0.992 × P_avg → P_avg ≈ OMA → Saved ~1 dB vs ER = 3.5 dB
```

### 12.3 Multi-Channel Power Summary

| Condition | OMA/ch (TP2) | Pavg/ch (TP2) | ELS/ch | 4-ch ELS total |
|---|---|---|---|---|
| TDEC = 2.0 dB (design) | −5.0 dBm | −4.8 dBm | +0.2 dBm (1.05 mW) | 4.2 mW |
| TDEC = 3.4 dB (spec max) | −3.5 dBm | −3.3 dBm | +1.7 dBm (1.48 mW) | 5.9 mW |
| OMA max (−1 dBm) | −1.0 dBm | −0.8 dBm | +4.2 dBm (2.63 mW) | 10.5 mW |

Group power limit: 4 × max_OMA = 4 × 1.0 mW = 4.0 mW → **+6.0 dBm ≤ 6 dBm spec ✓**
At design target: 4 × 0.32 mW = 1.28 mW → **−1.0 dBm, well within limit.**

### 12.4 Fiber Link Budget (TP2 → TP3)

| Parameter | Value | Source |
|---|---|---|
| Fiber length | 500 m | OCI Gen2 reach spec |
| SMF-28 attenuation at 1310 nm | 0.35 dB/km | Typical |
| Fiber loss (500 m) | 0.18 dB | |
| Connector at TP3 | 0.5 dB | 1 connector |
| Other (splices, bends) | < 0.3 dB | |
| **Total fiber IL (TP2 → TP3)** | **≤ 2.5 dB** | OCI Gen2 spec max |

At design-target OMA_TP2 = −5.0 dBm:
```
OMA_TP3 = −5.0 − 2.5 = −7.5 dBm
```
This feeds into [106G_NRZ_CPO_RX_Budget.md](106G_NRZ_CPO_RX_Budget.md) as the
OMA input to the TIA sensitivity analysis.

---

## 13. ELS Requirements

From OCI 200G v1.0 Table 2-6, applicable to Gen2:

| Parameter | Spec | Notes |
|---|---|---|
| Laser RIN | ≤ −144 dB/Hz | At max ORL; 6 dB tighter than TX spec |
| Laser linewidth | ≤ 1 MHz (≈ 0.7 pm) | Negligible vs 609 pm modulation width |
| SMSR | ≥ 30 dB | |
| Polarization extinction ratio | ≥ 16 dB | TE-only MRM modulation |
| ELS output reflectance | ≤ −26 dB | Back-reflection into laser |
| ORL tolerance | ≤ −26 dB | ELS must tolerate reflections from fiber plant |
| Output power | IS | Implementation-specific; see §12.3 |

**Polarization:** MRM is TE-only. PMF from ELS to OCI chiplet is mandatory. Polarization
rotation > (30° from TE) costs > 0.5 dB in effective OMA — a hidden loss item.

**CW stability:** ±0.5 dB ELS power drift → ±0.5 dB OMA drift, consuming TDEC margin.
Closed-loop monitoring (per-channel optical power tap + feedback to ELS gain or VOA)
is strongly recommended.

---

## 14. Standards Compliance Context

### 14.1 Electrical Interface: IEEE 802.3ck-2022

IEEE 802.3ck governs the 100GAUI-1 chip-to-chip and chip-to-module electrical interface
between the CDNS L250 SerDes and the MRM driver (or package boundary):

| 802.3ck Parameter | Spec | Clause |
|---|---|---|
| Signaling rate | 106.25 GBd ± 100 ppm | 162.9 |
| TX output ERL | ≥ 10 dB | 162.9.4.8 |
| TX output SNDR | ≥ 26 dB | 162.9.4.6 |
| TX DJ_pp | ≤ 0.20 UI = 1.88 ps | 162.9.4.7 |
| TX RJ_rms | ≤ 0.010 UI = 0.094 ps | 162.9.4.7 |
| TX equalization | Pre, Post, 3-bit, ±0.3× max | 120F.3.1.5 |

Note: The integrated MRM driver is exempt from the ERL/impedance specs (no package launch).
The 802.3ck electrical TX jitter specs apply at the SerDes output pad (before the MRM driver
redrives). The MRM driver adds its own jitter contribution tracked in §11.3.

### 14.2 Optical: OCI Gen2 Spec (derived from 200G-OCI v1.0)

Primary compliance is the OCI Gen2 optical spec at TP2 (§5). The IEEE 802.3ck covers only
the electrical interface; there is no 802.3ck optical PMD for this wavelength/topology.
The relevant draft for future 200G optical short-reach (P802.3dj) covers electrical and
optical interfaces at 200G–1.6T but does not directly specify the WDM-MRM CPO topology
used in OCI Gen2.

### 14.3 FEC Context

| FEC | Pre-FEC BER | Q | Post-FEC BER | Use |
|---|---|---|---|---|
| None (raw link) | — | 7.035 | **1×10⁻¹²** | Driver jitter spec |
| KP4 RS(544,514) | 2.4×10⁻⁴ | 3.54 | < 10⁻¹³ | OCI TDEC optical spec |
| RS(255,239) | 10⁻³ | 3.09 | < 10⁻¹² | Alternative (not OCI primary) |

---

## 15. TX Budget Summary

| Metric | Spec / Target | Design Value | Margin | Risk |
|---|---|---|---|---|
| TDEC | ≤ 3.4 dB | 2.0 dB | 1.4 dB | Medium — MRM BW critical |
| dTDEC | ≤ 0.4 dB | 0.2 dB | 0.2 dB | Low |
| OMA_min (at TDEC=2.0) | ≥ −5.0 dBm | −5.0 dBm | 0 dB | High — tight with ELS IL |
| OMA_max | ≤ −1.0 dBm | −5.0 dBm | 4.0 dB | Low |
| ER | ≥ 3.5 dB | 4.5 dB | 1.0 dB | Low |
| Optical tr/tf | ≤ 8.5 ps | ~7 ps | 1.5 ps | Medium — MRM photon lifetime |
| Driver tr/tf | ≤ 6 ps | target | TBD | Medium |
| Driver DJ_pp | ≤ 2.00 ps (budget) | 2.00 ps | 0 ps | Medium — full allocation used |
| Driver σ_RJ | ≤ 0.15 ps | 0.15 ps | 0 ps | Medium — full allocation used |
| TJ at 1e-12 | ≤ 4.11 ps (43.7% UI) | 4.11 ps | 56.3% UI open | Medium |
| TX EQ: post-cursor | ≤ 0.3× | ~0.22 | 0.08 | Low |
| TX EQ: pre-cursor | ≤ 0.3× | ~0.10 | 0.20 | Low |
| Overshoot | ≤ 22% | 10% | 12% | Low |
| RIN penalty (1e-12) | — | 0.26 dB | ~12 dB margin | Low |
| CD penalty | — | 0.1 dB | ~0.8 dB vs limit | Low |
| Group power (4ch) | ≤ +6 dBm | +1.0 dBm | 5 dB | Low |

---

## 16. Design Trade-offs and Risks

### 16.1 MRM Bandwidth vs Insertion Loss
Higher ring BW → smaller ring or higher coupling → more IL. At 60 GHz target BW,
the ring must be critically coupled with low round-trip loss. Options:
- **Segmented electrodes**: reduce series resistance → higher RC BW
- **Travelling-wave design**: removes lumped-element RC limit
- **Larger ring radius**: lower optical loss but narrower FSR (WDM crosstalk risk)

### 16.2 TX EQ Coefficient Trade-off

Higher post-cursor coefficient reduces ISI but reduces main-cursor amplitude, lowering
OMA for the same drive swing. At c₊₁ = −0.22:
```
OMA_after_EQ = OMA_no_EQ × (c₀ − |c₊₁|) / 1 = not a simple subtraction
(EQ redistributes energy; full Nyquist bandwidth analysis needed)
```
Measured TDEC vs EQ coefficient should be swept experimentally during bring-up.

### 16.3 Asymmetric Peaking Calibration

The MRM nonlinearity varies with:
- Bias point (heater-set wavelength offset from resonance)
- Temperature (resonance drift changes the nonlinearity slope)
- Drive amplitude (Vswing sets which portion of the Lorentzian is traversed)

A per-chip, per-temperature calibration table for the asymmetric pre-emphasis coefficients
is likely needed. This adds firmware complexity but is necessary to minimize DCD at 106G.

### 16.4 Thermal Drift and Wavelength Lock

MRM resonance: ~80 pm/°C. WDM channel spacing: ~2.3 nm.
Max tolerable drift before channel collision: 2300/80 = **28.8°C**.
On-chip thermal variation ±10°C + tile coupling ±5°C → heater loop settling < 50 ms.
Heater power per ring: 1–5 mW. For 8 rings per chiplet (4 per group × 2 groups):
**Heater power budget: 8–40 mW per chiplet.**

### 16.5 PSIJ from On-Chip Power Supply

At 106.25 GBaud, reference clock is 106.25/N GHz (with integer N SerDes divider).
Power supply noise at multiples of this frequency appears as PSIJ. The SerDes PLL
VCO supply must be LDO-regulated to keep PSIJ_pp ≤ 0.30 ps. Switching noise from
heater DAC updates should be isolated from the SerDes supply domain.

---

## 17. Next Steps

1. **MRM S21 measurement**: Measure modulation bandwidth from DC to 80 GHz.
   Target: 3dB BW ≥ 60 GHz. Record Lorentzian shape for asymmetric peaking design.

2. **Driver EQ optimization**: Sweep [c₋₁, c₊₁] coefficients at 3-bit resolution.
   Minimize TDEC at TP2. Measure dTDEC(SSPR vs PRBS13) ≤ 0.4 dB.

3. **Asymmetric peaking calibration**: Characterize MRM nonlinearity at design bias;
   iterate driver rise/fall asymmetry coefficients to minimize DCD in optical eye.

4. **TDEC test at TP2**: Drive at 106.25 GBaud SSPR; measure through 53.125 GHz BT-4
   reference receiver; verify TDEC ≤ 3.4 dB and dTDEC ≤ 0.4 dB.

5. **Electrical jitter measurement**: Extract DJ_pp, σ_RJ, PSIJ_pp from bathtub curve
   at the SerDes TX output. Verify TJ ≤ 4.11 ps at BER = 1×10⁻¹².

6. **ER and OMA sweep**: Vary MRM bias (heater DAC) and drive swing (Vswing).
   Map ER vs OMA vs TDEC. Find optimal operating point.

7. **ELS power sweep**: Characterize OMA at TP2 vs ELS CW power. Confirm ≥ −5.0 dBm
   OMA with 5 dB nominal TX path IL. Measure total group power.

8. **Thermal lock loop**: Validate heater feedback settling time < 50 ms over
   −10°C to +85°C range. Characterize PSIJ from heater DAC switching.

9. **End-to-end BER**: OCI TX + 500 m SMF-28 + OCI RX. Measure BER vs OMA.
   Compare against RX budget sensitivity prediction.

---

## Appendix A: Key Formulas

```
# Transform-limited spectral linewidth
Δλ = λ² × B / c

# ER average-power penalty
PP_avg = (ER + 1) / (ER − 1)    [linear]

# OMA–Pavg relationship
OMA / P_avg = 2(ER − 1) / (ER + 1)

# RIN SNR
SNR_RIN = 1 / (RIN_linear × BW_noise)

# Dual Dirac total jitter
TJ(BER) = DJ_pp + 2 × Q(BER) × σ_RJ

# Key Q values
Q(1×10⁻¹²)   = 7.035  →  2Q = 14.07   [driver jitter spec]
Q(2.4×10⁻⁴)  = 3.54   →  2Q =  7.07   [OCI TDEC optical compliance]

# TX FIR equalizer normalization
|c₋₁| + c₀ + |c₊₁| = 1
c₀ = 1 − |c₋₁| − |c₊₁|

# TDEC OMA floor
OMA_min = max(−5.5 dBm, −6.9 dBm + TDEC_dB)

# Chromatic dispersion pulse broadening
ΔT = |CD_total| × Δλ    [ps_total × nm = ps]
```

## Appendix B: OCI Wavelength Plan (Gen2, same as Gen1)

| Group | Channel | λ (nm) | D at λ | Notes |
|---|---|---|---|---|
| A | A0 | 1307.8 | ~0.1 ps/(nm·km) | |
| A | A1 | 1310.1 | ~0.05 | Near λ₀ |
| A | A2 | 1312.4 | ~0.1 | |
| A | A3 | 1315.1 | ~0.15 | |
| B | B0 | 1327.5 | ~0.6 | |
| B | B1 | 1329.8 | ~0.7 | |
| B | B2 | 1332.2 | ~0.7 | |
| B | B3 | 1334.9 | ~0.8 | |

All channels within SMF-28 low-dispersion window. No WDM grid changes Gen1 → Gen2.
