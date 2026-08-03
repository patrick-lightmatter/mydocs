# 106G NRZ CPO End-to-End Link Budget — OCI Gen2

**System:** Lightmatter OCI Gen2, GlobalFoundries process  
**Modulation:** NRZ OOK, 106.25 GBaud per lane, 4λ DWDM  
**Fiber reach:** 500 m SMF-28  
**Date:** 2026-08-03  
**RX architecture:** TX 3-tap FIR + TIA with embedded CTLE (55 GHz) — no RX FFE, no RX DFE  
**Sources:** 200G-OCI Optical Phy Spec v1.0, `ocigen2gf_OMA_rollup_2026-07-13`,  
IEEE 802.3ck-2022, ECEN721 Lecture 7, ECEN720 Lecture 10

---

## Executive Summary

The proposed architecture uses TX-only equalization enabled by a short-memory channel (combined τ ≈ 0.29 UI). A 3-tap TX FIR pre-compensates the combined MRM and TIA response, eliminating the need for RX FFE and DFE. A TIA with embedded passive CTLE extends receiver bandwidth to approximately 55 GHz while avoiding the noise penalty of a separate active CTLE gain stage. This simplifies the receiver, improves estimated sensitivity by approximately 1 dB, and increases predicted RS(255,239) net link margin by approximately 1.7 dB relative to the prior architecture.

**Architecture validity depends on:** MRM BW ≥ 60 GHz at all PVT corners; TIA embedded CTLE BW ≥ 53 GHz at SS corner; C_in ≤ 55 fF (45 μm bump required); TIA input-referred noise ≤ 3.5 μA_rms. None of these has been confirmed by post-layout simulation. See §1.3 for full confidence assessment and §11 for risk register.

---

## Key Numbers At a Glance

| Parameter | Value | Unit | Status |
|---|---|---|---|
| Baud rate | 106.25 | GBaud | Specification |
| Unit interval (UI) | 9.41 | ps | Derived |
| MRM bandwidth | ≥ 60 | GHz | Measured (hard requirement) |
| TIA + embedded CTLE BW | ~55 | GHz | **Estimated** |
| TX driver rise time | ≤ 6 | ps | Specification |
| TX FIR (c₋₁ / c₀ / c₊₁) | −0.10 / 0.65 / −0.25 | — | Derived |
| Combined channel τ | ~2.77 | ps = 0.29 UI | Derived |
| ISI captured by 3-tap FIR | > 99.9 | % | Derived |
| OMA at PD (median / −3σ) | −8.62 / −11.36 | dBm | Measured |
| TIA input-referred noise | ~3.0 | μA_rms | **Estimated** |
| OMA sensitivity (RS FEC, BER=1e-3) | −16.1 | dBm | Derived |
| Net RS link margin, median / −3σ | +5.4–5.7 / +2.6–2.9 | dB | Derived |
| Recommended FEC | RS(255,239) | — | Recommended |

---

## Architecture Validity Envelope

This architecture is valid if and only if all four conditions are simultaneously satisfied:

1. **MRM BW ≥ 55 GHz** at worst-case PVT — below this, ISI at +2 UI exceeds 0.5%, creating a BER floor with no RX FFE to compensate (§6.1).
2. **TIA embedded CTLE BW ≥ 53.125 GHz (Nyquist)** at SS corner — below Nyquist creates aliased ISI that the TX FIR cannot pre-compensate (§8.4, §11 R1).
3. **C_in ≤ 55 fF** — 45 μm micro-bump pitch required; 110 μm makes the 55 GHz embedded CTLE BW target physically unachievable (§8.3).
4. **TIA noise ≤ 3.5 μA_rms** at worst-case corner — above this threshold the −3σ RS link margin turns negative after penalties (§9.2).

---

## Out of Scope

The following topics are excluded from this document and are tracked separately:

- ADC quantization noise and ENOB requirements
- CDR loop filter design and acquisition
- Thermal heater controller architecture and settling time
- DSP/firmware architecture and FIR adaptation algorithms
- Manufacturing calibration procedures
- Inter-channel crosstalk (WDM ring coupling)
- Multi-lane aggregation and skew management

---

## 1. System Overview

### 1.1 BER Conventions

| BER | Q | 2Q | Layer | Context |
|---|---|---|---|---|
| **1×10⁻¹²** | 7.035 | 14.07 | Raw link / TX driver jitter | Uncoded sensitivity; driver electrical spec |
| **1×10⁻³** | 3.090 | 6.18 | RS(255,239) pre-FEC | RX sensitivity; recommended FEC |
| **2.4×10⁻⁴** | 3.54 | 7.07 | KP4 pre-FEC / OCI TDEC | Optical compliance measurement only |

### 1.2 Key Baud-Rate Parameters

| Parameter | Value | Notes |
|---|---|---|
| Baud rate | 106.25 GBaud | ×2 Gen1 |
| UI | 9.41 ps | ÷2 Gen1 (18.82 ps) |
| Nyquist frequency | 53.125 GHz | BR/2 — minimum RX BW |
| TDEC ref RX BW | 53.125 GHz | 0.5 × BR, scaled from Gen1 |
| Optical rise time target | 8.5 ps | ÷2 Gen1 (17 ps) |
| Driver rise time target | 6 ps | Electrical at MRM electrode |

### 1.3 Parameter Status and Confidence

| Parameter | Value | Source | Status | Confidence |
|---|---|---|---|---|
| OMA at PD — median / −3σ | −8.62 / −11.36 dBm | OMA rollup | **Measured** | High |
| MRM bandwidth | ≥ 60 GHz | MRM S21 | **Measured** | High |
| TX optical rise time | ≤ 8.5 ps | TDEC compliance | **Measured** | High |
| TDEC (design / spec) | 2.0 / 3.4 dB | OCI Gen2 spec | **Measured** | High |
| C_in — 45 μm bump | ~46 fF | EMX extraction | **Modelled** | Medium |
| PD responsivity | 0.75 A/W | GF PD (assumed) | **Assumed** | Medium |
| TX FIR coefficients | −0.10/0.65/−0.25 | MMSE estimate | **Derived** | Medium |
| TIA + embedded CTLE BW | ~55 GHz | T-coil model | **Estimated** | **Low** |
| TIA input-referred noise | ~3.0 μA_rms | Scaling estimate | **Estimated** | **Low** |
| SS corner TIA BW | 36–44 GHz | Scaling estimate | **Estimated** | **Low** |

*Confidence levels: High = from measurement or verified simulation; Medium = modelled or derived from first principles; Low = engineering estimate, requires post-layout simulation before sign-off.*

---

## 2. Full Signal Chain

```
 ELS (CW, +23.75 dBm total, 4λ)
  │  PMF pigtail + connectors         ─ ~0.8 dB
  ▼  [TP1]
 OCI TX Chiplet
  │  CDNS L250 SerDes TX
  │  3-tap TX FIR (c₋₁=−0.10, c₀=0.65, c₊₁=−0.25) — optimised for MRM + TIA channel
  │  Integrated MRM Driver (~1.0 Vpp diff, asymmetric tr/tf correction)
  │  MRM modulator bank (4×, α≈0, ER~4.5 dB, BW≥60 GHz, τ_ph=2.65 ps)
  │  On-chip post-MRM routing + interleaver + PSR   ─ ~3.95 dB (median)
  ▼  [TP2 — OCI optical compliance point]
  │  OMA: −0.28 dBm median (actual); ≥ −5.0 dBm (spec floor, TDEC=2.0 dB)
  │
  │  500 m SMF-28                     ─ ≤ 2.5 dB (spec max)
  │  CD: ~1.0 ps pulse broadening @ 1311 nm — negligible (< 0.1 dB)
  ▼  [TP3]
 OCI RX Chiplet
  │  FAU + PSR + interleaver + VOA + CRR  ─ ~3.29 dB (median)
  │  Fiber attach (lognormal) + aging      ─ ~1.5 dB (median)
  │  External fiber plant (TP3b)           ─ 2.5 dB
  ▼  Photodetector  (R ≈ 0.75 A/W, C_PD ≈ 6 fF)  [assumed — §1.3]
  │  OMA at PD: −8.62 dBm median, −11.36 dBm at −3σ
  │
  │  TIA with embedded CTLE (single stage)
  │    Rf = 600 Ω CMOS inverter + T-coil + shunt peaking → ~55 GHz BW [estimated]
  │    Input-referred noise: ~3.0 μA_rms TT, 105°C [estimated — §1.3]
  │    No separate CTLE stage. No RX FFE. No RX DFE.
  │
  │  S/H + ADC → Decision
  ▼  RS(255,239) FEC → Data out (net 99.2 Gb/s)
```

**Why no RX FFE:** The combined channel ISI (MRM 60 GHz + TIA 55 GHz, τ_combined ≈ 2.77 ps = 0.29 UI) decays exponentially. ISI at +1 UI = 3.3%; at +2 UI = 0.11%. The 3-tap TX FIR spans ±1 UI and captures > 99.9% of ISI energy. See §6.1 for the derivation of this condition.

---

## 3. Architecture Decisions

### 3.1 Decision Table

| Decision | Selected | Alternatives evaluated | Basis for selection |
|---|---|---|---|
| RX equalization | **TX 3-tap FIR only** | TX FIR + RX 2+1+2 FFE | Channel τ = 0.29 UI; ISI at +2 UI < 0.12%; FFE adds noise via separate CTLE |
| RX CTLE | **Embedded in TIA (passive T-coil)** | Separate active 1z2p CTLE | Active CTLE self-noise ~2.0 μA_rms + amplifies TIA noise 2.7×; passive T-coil avoids both |
| Bump pitch | **45 μm (required)** | 110 μm | 110 μm → C_in = 76 fF → embedded CTLE BW ~36 GHz (below Nyquist) |
| TX FIR taps | **3 (±1 UI span)** | 4 or 5 taps | ISI at ±2 UI = 0.11% → 4th tap gives < 0.1 dB improvement; not worth normalization cost |
| FEC | **RS(255,239)** | KP4, uncoded | Uncoded fails at −3σ; KP4 gives only +1.9–2.2 dB margin at −3σ vs +2.6–2.9 for RS |
| MRM BW target | **≥ 60 GHz (hard)** | Relax to 40 GHz | No FFE fallback: at 40 GHz, ISI at +2 UI = 2.7% → BER floor (§6.1) |

### 3.2 Design Margins Summary

| Margin | Value | Binding constraint |
|---|---|---|
| TX OMA vs compliance floor | +4.7 dB | OCI spec OMA_min = −5.0 dBm |
| TDEC vs spec max | 1.4 dB | 2.0 dB design vs 3.4 dB spec |
| ISI energy captured by FIR | > 99.9% | +2 UI ISI = 0.11% |
| TIA BW vs Nyquist (TT) | +1.9 GHz | 55 vs 53.125 GHz (tight) |
| Net RS link margin, −3σ | +2.6–2.9 dB | OMA at PD −11.36 dBm, sens −16.1 dBm |
| TDEC implication of c₊₁=−0.25 | 0.4 dB headroom consumed | 2.2 dB vs 3.4 dB spec |

---

## 4. Gen1 → Gen2 Scaling

| Parameter | Gen1 (53G) | Gen2 (106G) | Scale | Coupling |
|---|---|---|---|---|
| Baud rate | 53.125 GBaud | **106.25 GBaud** | ×2 | Both |
| UI | 18.82 ps | **9.41 ps** | ÷2 | Both |
| TDEC ref RX BW | 26.5625 GHz | **53.125 GHz** | ×2 | TX compliance |
| Optical rise time (TP2) | 17 ps | **8.5 ps** | ÷2 | → RX TIA BW requirement |
| Driver rise time | ~10 ps | **~6 ps** | ÷2 | TX driver |
| RX effective BW target | ~27 GHz | **~55 GHz** | ×2 | RX design |
| MRM bandwidth target | ~30 GHz | **≥ 60 GHz** | ×2 | Joint TX+RX |
| Optical power specs | — | **unchanged** | ×1 | Both |
| TDEC limit | 3.4 dB | **3.4 dB** | ×1 | TX compliance |
| RIN_OMA spec | −138 dB/Hz | **−138 dB/Hz** | ×1 | Both |

---

## 5. Transmitter

### 5.1 ELS Requirements

| Parameter | Spec | Notes |
|---|---|---|
| Total output power | +23.75 dBm typical | 4λ, split to MRM bank |
| Laser RIN | ≤ −144 dB/Hz | Tighter than TX compliance; §6.7 shows RIN penalty is negligible |
| Linewidth | ≤ 1 MHz | Negligible vs 0.61 nm modulation BW |
| SMSR | ≥ 30 dB | |
| Polarization extinction ratio | ≥ 16 dB | TE-mode MRM; PMF required |

### 5.2 MRM Driver and 3-Tap TX FIR

The MRM driver is co-integrated with the ring modulator. It drives a lumped RC load (C_MRM ≈ 10–30 fF, R_contact ≈ 10–30 Ω); no 50 Ω termination applies.

| Parameter | Spec | Notes |
|---|---|---|
| Differential swing (typ / max) | 1.0 / 1.5 Vpp | Design target for ER ≈ 4.5 dB |
| Output impedance | N/A | Integrated — lumped RC load only |
| TX FIR taps | 3 (c₋₁, c₀, c₊₁) | Optimised for MRM + TIA channel (not just MRM) |
| c₋₁ / c₀ / c₊₁ (design) | −0.10 / 0.65 / −0.25 | See §6.2; 3-bit per tap, step 0.043 |
| Normalization | \|c₋₁\| + c₀ + \|c₊₁\| = 1 | |
| Rise/fall time (20-80%) | **≤ 6 ps** | At MRM electrode; after TX FIR |
| Asymmetric tr/tf control | Independent slew per edge | Cancels MRM Lorentzian DCD; must track heater register (§5.3) |
| DJ_pp (BER = 1e-12) | ≤ 2.00 ps_pp | 21.3% UI |
| σ_RJ (BER = 1e-12) | ≤ 0.15 ps_rms | 1.6% UI |
| TJ at BER = 1e-12 | ≤ 4.11 ps | = 2.00 + 14.07 × 0.15 |

### 5.3 MRM Modulator

| Parameter | Value | Notes |
|---|---|---|
| Modulation type | Intensity (ring resonance shift) | α ≈ 0, chirp-free, transform-limited |
| Optical BW target | ≥ 60 GHz | Photon lifetime τ_ph = 1/(2π·60GHz) = 2.65 ps |
| Insertion loss (on-state) | 2–3 dB | Through-port waveguide + coupler |
| Extinction ratio | ≥ 3.5 dB, typ 4.5 dB | Via Vswing and bias point |
| Thermal sensitivity | ~80 pm/°C | Closed-loop heater mandatory |

**Optical edge asymmetry (DCD) mechanism:** The MRM transfer function T(V) is Lorentzian. Driving *onto* resonance uses the steep slope of T(V) — fast falling edge. Driving *off* resonance is bottlenecked by the photon cavity lifetime (τ_ph = 2.65 ps) — slower rising edge. This asymmetric tr/tf creates DCD in the optical eye. The driver applies independent per-edge slew rate control to equalize optical edges at TP2. **This correction cannot be static:** as the heater adjusts the ring bias point, the Lorentzian shape shifts and the slew correction must update in concert.

**Spectral linewidth** (α=0, λ=1311 nm): Δλ = λ²B/c = 0.609 nm. CD penalty over 500 m SMF: ΔT = 1.04 ps = 0.11 UI → **< 0.1 dB** (see Appendix D.1).

### 5.4 TX Optical Chain (ELS → TP2)

From `ocigen2gf_OMA_rollup_2026-07-13`, Case 10:

| Segment | −3σ | Median | +3σ |
|---|---|---|---|
| ELS to TP2 (full TX network) | 23.46 dB | **25.06 dB** | 27.42 dB |
| MRM output OMA (Tx3e) | — | **+3.67 dBm** | — |
| Post-MRM routing to TP2 | 2.86 dB | **3.95 dB** | 6.09 dB |
| **OMA at TP2** | **+0.81 dBm** | **−0.28 dBm** | **−2.42 dBm** |

OCI compliance floor at TDEC = 2.0 dB: OMA_min = max(−5.5, −6.9+2.0) = **−5.0 dBm**. Actual median −0.28 dBm → **+4.7 dB margin** to floor.

### 5.5 TDEC Budget

Measurement: BT-4 ref RX at 53.125 GHz, no EQ, SSPR, BER = 2.4×10⁻⁴.

| Contributor | dB |
|---|---|
| MRM optical BW (60 GHz Lorentzian) through ref RX | 0.6 |
| TX FIR residual after equalization | 0.5 |
| Finite ER = 4.5 dB (P0 leakage) | 0.3 |
| MRM nonlinearity residual after asymmetric correction | 0.2 |
| DCD residual | 0.15 |
| Chromatic dispersion (1.04 ps broadening) | 0.10 |
| Overshoot/ringing residual | 0.15 |
| **Design sub-total** | **2.0** |
| c₊₁ = −0.25 adjustment (vs −0.22 for BT4 reference) | ~+0.2 |
| **Effective TDEC with this FIR** | **~2.2 dB** |
| **Margin to spec** | **1.2 dB** |
| **Spec limit** | **3.4 dB** |

### 5.6 TX Jitter Budget (BER = 1×10⁻¹²)

| Component | Budget | % UI |
|---|---|---|
| DCD | 0.40 ps_pp | 4.3% |
| ISI — electrical (after FIR) | 0.60 ps_pp | 6.4% |
| ISI — optical (MRM Lorentzian) | 0.40 ps_pp | 4.3% |
| BUJ (adjacent WDM ring crosstalk) | 0.30 ps_pp | 3.2% |
| PSIJ (VCO/supply, PLL ref) | 0.30 ps_pp | 3.2% |
| **DJ_pp total** | **2.00 ps_pp** | **21.3%** |
| σ_RJ (SerDes TX PLL VCO) | 0.15 ps_rms | 1.6% |
| **TJ at BER = 1e-12** | **4.11 ps_pp** | **43.7%** |
| **TX eye opening** | **5.30 ps** | **56.3%** |

---

## 6. TX–RX Coupling Analysis

### 6.1 TX Rise Time → RX Minimum Bandwidth; FIR Sufficiency Condition

The 6 ps electrical driver rise time and 60 GHz MRM bandwidth combine quadratically to produce 8.5 ps optical edges at TP2 (derivation in Appendix D.2):

```
t_r_optical = √(6.0² + 5.83²) = 8.37 ps ≈ 8.5 ps   ✓
```

**Enabling condition for 3-tap TX FIR without RX FFE:**

ISI at +k UI decays as exp(−k·UI/τ). For the 3-tap FIR (±1 UI span) to capture > 99.9% of ISI energy, the uncancelled ISI at +2 UI must be below the FIR quantization noise floor (~0.12%):

```
exp(−2·UI/τ) < 0.0012   →   τ < UI / 3.4 = 2.77 ps   →   BW > 57 GHz
```

Equivalently: **BW_channel >> BR/(2π) ≈ 16.9 GHz** (necessary condition); the sufficient condition is BW_channel > 57 GHz.

| Stage | BW | τ | τ/UI | ISI at +1UI | ISI at +2UI |
|---|---|---|---|---|---|
| MRM | 60 GHz | 2.65 ps | 0.28 | 3.3% | 0.11% |
| TIA (embedded CTLE) | 55 GHz | 2.89 ps | 0.31 | 3.8% | 0.14% |
| **Combined** | **~40 GHz eff.** | **~2.77 ps** | **0.29** | **~6.4%** (pre-FIR) | **0.11%** |

The 3-tap TX FIR cancels the 6.4% first post-cursor. Residual 0.11% at +2 UI is below quantization noise — **no RX FFE required**. If MRM BW falls below 55 GHz (τ > 2.89 ps), ISI at +2 UI exceeds 0.5% and a 4th FIR tap or RX FFE becomes necessary (see §11, Risk R3).

RX embedded CTLE must achieve ≥ Nyquist (53.125 GHz) to avoid aliased ISI. At TT target of 55 GHz, margin is only +1.9 GHz — confirm SS corner (§11, Risk R1).

### 6.2 TX FIR Coefficient Shift for Full Channel

Targeting MRM + TIA together (vs MRM alone with RX FFE backup) increases the required c₊₁ from −0.22 to −0.25 to cancel the larger combined post-cursor ISI. Under normalization, c₀ drops from 0.68 to 0.65, reducing effective OMA by 0.37 dB at the decision point. The FIR maintains unity gain at Nyquist in both cases. See Appendix D.3 for the Nyquist frequency response derivation.

| Coefficient | With RX 2+1+2 FFE | **No RX EQ** |
|---|---|---|
| c₋₁ | −0.10 | −0.10 |
| c₀ | 0.68 | **0.65** |
| c₊₁ | −0.22 | **−0.25** |

### 6.3 TX TDEC → RX ISI Penalty

With 3-tap TX FIR as the sole equalizer:

| Residual after TX FIR | Penalty |
|---|---|
| ISI at +1 UI — cancelled by c₊₁ | ~0 dB |
| ISI at +2 UI (0.11%) — uncancelled | ~0.05 dB |
| FIR coefficient quantization (±0.043 LSB) | ~0.2 dB |
| Pattern-dependent ISI from MRM nonlinearity | ~0.2 dB |
| CD broadening (1.04 ps through TIA) | ~0.1 dB |
| **Total residual ISI penalty** | **~0.5–0.8 dB** |

This is better than the 1.0–1.5 dB achieved by the prior TX FIR + RX FFE combination, because the channel's short ISI memory suits TX pre-compensation more naturally than post-equalization of a CTLE-processed signal.

### 6.4 TX OMA → RX Sensitivity

OMA cascade (see §7 for full optical chain loss):

```
OMA at TP2 (median/−3σ): −0.28 / −2.42 dBm
Total loss TP2 → PD (median): ~8.34 dB
OMA at PD (median/−3σ): −8.62 / −11.36 dBm   ✓ matches rollup
```

At 3.0 μA_rms noise: OMA_sens(1e-12) = −12.5 dBm; OMA_sens(1e-3) = **−16.1 dBm** (§8.5).

### 6.5 TX ER → RX Decision Threshold

For constant noise (σ₀ = σ₁), optimal threshold = Pavg = R·OMA·(ER+1)/(2(ER−1)). At ER = 4.5 dB, this is **4.9% above OMA/2**. TX ER varies 3.5–4.5 dB with heater state, shifting the optimal threshold by ~4.8 μA (4.7% of OMA). The DCOC loop must remain active to track this drift. See Appendix D.4 for the threshold shift derivation.

### 6.6 TX Jitter → RX CDR

TX TJ = 4.11 ps at TP2. After CDR tracking additions (DJ +0.10 ps, σ_RJ adds to 0.187 ps):

```
TJ_decision = 2.10 + 14.07 × 0.187 = 4.73 ps → eye opening = 4.68 ps = 49.7% UI   ✓
```

### 6.7 TX RIN → RX Noise Floor

σ_RIN ≈ 3.4 nA_rms at median OMA (derivation in Appendix D.5) — 880× below TIA noise (3.0 μA_rms). **RIN is negligible** regardless of ELS spec compliance.

---

## 7. Optical Power Budget

### 7.1 End-to-End Loss Summary (Case 10, Mission Mode)

| Segment | −3σ | Median | +3σ |
|---|---|---|---|
| ELS to TP2 | 23.46 dB | 25.06 dB | 27.42 dB |
| TP2 to TP3 (fiber) | — | ≤ 2.5 dB | — |
| TP3 to PD (RX chip) | 4.72 dB | 5.79 dB | 7.91 dB |
| **Total: ELS → PD** | **30.33 dB** | **32.39 dB** | **35.33 dB** |
| **OMA at PD** | **−11.36 dBm** | **−8.62 dBm** | **−6.97 dBm** |

Full per-element RX optical loss table is in Appendix D.6. Case 10 (mission mode) is binding. Cases 11 and 23 define AGC dynamic range (§7.2), not sensitivity.

### 7.2 RX Dynamic Range Requirement

Case 11 (max power) OMA = +1.79 dBm at PD → I_OMA = 1.13 mApp. Mission case: 103 μApp. **Dynamic range: 20.8 dB.** The TIA must not clip at 1.13 mApp — verify linearity at Case 11 (no VGA/AGC ahead of embedded CTLE TIA).

---

## 8. Receiver

### 8.1 RX Optical Chain (TP3 → PD)

Total TP3 to PD loss: **5.79 dB** (median), 4.72 dB (−3σ), 7.91 dB (+3σ). Full element-by-element breakdown in Appendix D.6.

### 8.2 Photodetector

| Parameter | Value | Status |
|---|---|---|
| Responsivity R | 0.75 A/W | **Assumed** — confirm GF PD spec |
| Junction capacitance C_PD | ~6 fF | **Modelled** — update to GF geometry |
| Dark current | TBD | Expected < 0.1 dB penalty |

A 0.1 A/W error in R shifts OMA sensitivity by ~0.5 dB. This is a priority measurement item (§12 #5).

### 8.3 CPO Interconnect and TIA Input Capacitance

| Component | 45 μm pitch | 110 μm pitch |
|---|---|---|
| PD + PIC interconnect + EIC | ~36 fF | ~36 fF |
| Micro-bump | ~10 fF | ~40 fF |
| ESD cap (T-coil port) | ~24 fF | ~24 fF |
| **Total C_in** | **~46 fF** | **~76 fF** |

At 110 μm: TIA base BW = 3.50 GHz → embedded CTLE reaches only ~36 GHz (below Nyquist). **45 μm is required.** Every additional 10 fF over the 46 fF budget reduces embedded CTLE BW by ~18%.

### 8.4 TIA with Embedded CTLE

**Architecture rationale:** The prior design used a separate active 1z2p CTLE stage (13.4 dB peaking) to extend TIA BW from 10.5 to 61.3 GHz. That stage amplified TIA noise from 1.4 to 3.8 μA_rms and added its own transistor self-noise (~2.0 μA_rms equivalent). This design embeds the CTLE function within the TIA using passive inductive peaking (T-coil + shunt peaking), which adds no transistor noise and avoids high-frequency noise amplification.

| Parameter | Target | Notes |
|---|---|---|
| Bandwidth (−3 dB) | **~55 GHz** | T-coil + shunt peaking; requires simulation [Low confidence] |
| Integrated peaking | **≤ 6 dB** | Passive only — no separate gain stage |
| Feedback resistance Rf | 600 Ω | Programmable to 450 Ω at SS corner (§11, R1) |
| Supply V_DDA | 0.85 V | |
| Base TIA BW (no peaking, 46 fF) | ~5.8 GHz | f = 1/(2π × 600 × 46e-15) |
| Extension factor required | ~9.5× | Via T-coil + shunt peaking cascade |
| Bump pitch | **45 μm required** | 110 μm → BW ~36 GHz (below Nyquist) |

Passive T-coil spiral resistance (~2–5 Ω) contributes σ_n ≈ 55 nA_rms — negligible versus TIA thermal noise. **Post-layout EM simulation is required** before this BW and noise estimate can be elevated from Low to Medium confidence.

### 8.5 Noise and Sensitivity

Estimated input-referred noise: **~3.0 μA_rms (TT, 105°C)** [Low confidence — see §1.3].

```
OMA_sensitivity = 2Q × i_n / R
```

| BER | Q | OMA_sens (2.5 μA) | OMA_sens (3.0 μA) | OMA_sens (3.5 μA) | FEC |
|---|---|---|---|---|---|
| 1×10⁻¹² | 7.035 | −13.3 dBm | **−12.5 dBm** | −11.6 dBm | Uncoded |
| 1×10⁻³ | 3.090 | −16.9 dBm | **−16.1 dBm** | −15.1 dBm | RS(255,239) |

Centre column (3.0 μA_rms) is the design estimate. Range spans expected post-layout outcome.

### 8.6 RX Equalization — None

No RX FFE. No RX DFE. All ISI equalization is pre-distortion by the 3-tap TX FIR. This is valid because channel ISI is confined to ±1 UI (§6.1). Benefits: no FFE pipeline latency (~5 UI eliminated); no FFE datapath power at 106 Gb/s. Risk: no fallback if MRM BW degrades below 55 GHz (§11, R3).

---

## 9. End-to-End Link Margin

### 9.1 Power Penalty Budget

| Penalty source | Estimate | Notes |
|---|---|---|
| DCOC threshold error | ~0.5 dB | ER variation → Pavg shift ~4.7%; see §6.5 |
| Residual ISI after TX FIR | ~0.5–0.8 dB | No RX FFE; ISI confined to ±1 UI (§6.3) |
| Wavelength PDL (4λ WDM) | ~0.5 dB | Interleaver + PSR variation across λ |
| Back-scatter / reflections | ~0.3 dB | CPO reduces this vs pluggable |
| Dark current (PD) | TBD | Expected < 0.1 dB — awaiting GF spec |
| RIN | < 0.01 dB | Negligible (§6.7) |
| SS corner TIA noise increase | TBD | Primary open risk (§11, R1) |
| **Total estimated** | **~1.8–2.1 dB** | Excludes SS corner and PD unknowns |

### 9.2 Net Link Margin

Using i_n = 3.0 μA_rms (design estimate):

| FEC | OMA_sens | Gross, median | Gross, −3σ | Penalties | **Net, median** | **Net, −3σ** |
|---|---|---|---|---|---|---|
| Uncoded (1e-12) | −12.5 dBm | +3.9 dB | +1.1 dB | 1.8–2.1 dB | +1.8–2.1 dB | **FAIL** |
| **RS(255,239) (1e-3)** | **−16.1 dBm** | **+7.5 dB** | **+4.7 dB** | 1.8–2.1 dB | **+5.4–5.7 dB** | **+2.6–2.9 dB** |
| KP4 (2.4e-4) | −15.4 dBm | +6.8 dB | +4.0 dB | 1.8–2.1 dB | +4.7–5.0 dB | +1.9–2.2 dB |

**Improvement vs prior architecture** (TX FIR + RX 2+1+2 FFE + separate active CTLE, i_n = 3.8 μA_rms):

| Metric | Prior | **This design** | Δ |
|---|---|---|---|
| OMA_sens, RS FEC | −15.0 dBm | **−16.1 dBm** | +1.1 dB |
| Net margin −3σ, RS | +0.8–1.3 dB | **+2.6–2.9 dB** | **+1.6–1.8 dB** |
| ISI residual penalty | 1.0–1.5 dB | **0.5–0.8 dB** | +0.4 dB |

---

## 10. FEC Recommendation

**RS(255,239) is mandatory.** Uncoded fails at −3σ. With the improved link margin of this architecture, KP4 is now also viable, recovering 0.8 Gb/s net rate toward 100 GbE line rate.

| FEC | Overhead | Pre-FEC BER | Net −3σ margin | Net rate | Verdict |
|---|---|---|---|---|---|
| None | 0% | 1×10⁻¹² | Negative | 106.25 Gb/s | **FAIL** |
| KP4 RS(544,514) | 6.25% | 2.4×10⁻⁴ | +1.9–2.2 dB | 100.0 Gb/s | Viable |
| **RS(255,239)** | **7.1%** | **10⁻³** | **+2.6–2.9 dB** | **99.2 Gb/s** | **Recommended** |

The +2.6–2.9 dB margin at −3σ provides headroom to absorb up to ~2 dB of uncharacterised SS corner TIA noise penalty while remaining positive.

---

## 11. Risk Register

Probability: Low < 20%, Medium 20–60%, High > 60%.  
Impact: Critical = architecture invalidated; High = > 1 dB margin loss; Medium = 0.5–1 dB.

| ID | Risk | P | Impact | Primary mitigation | Contingency |
|---|---|---|---|---|---|
| **R1** | TIA embedded CTLE BW < Nyquist (53.125 GHz) at SS corner | M | **Critical** | Programmable Rf: 600→450 Ω (+33% BW, +0.5 dB noise penalty) | Add T-coil resonance tuning cap bank |
| **R2** | TIA input-referred noise > 3.5 μA_rms | M | High | Optimise T-coil peaking level; reduce parasitic losses | Revert to active CTLE + accept noise penalty |
| **R3** | MRM BW < 55 GHz at worst-case PVT | L | **Critical** | Add 4th TX FIR tap c₊₂ (±2 UI span) | Reinstate RX 2+1+2 FFE as fallback |
| **R4** | PD responsivity < 0.70 A/W | L | High | Increase TX OMA; re-optimise TIA Rf | Higher-power ELS or lower-loss RX optical path |
| **R5** | TX FIR coefficients mistracking MRM operating point | M | Medium | Active adaptation; startup training sequence | Wider 3-bit coefficient range; 4-bit option |
| **R6** | C_in > 55 fF (bump or PD parasitics over budget) | L | High | Maintain 45 μm bump; re-extract C_PD at GF geometry | Reduce Rf (noise trade); redesign bump landing pad |

**R1 is the highest-priority risk.** SS corner BW could fall to 36–44 GHz (below Nyquist), creating an uncorrectable ISI floor with no RX FFE fallback. The Rf=450 Ω mitigation costs ~0.5 dB noise (narrowing −3σ RS margin to ~+2.1 dB) but keeps the architecture viable.

---

## 12. Next Steps

| # | Action | Owner | Priority |
|---|---|---|---|
| 1 | Post-layout simulation: TIA + T-coil at TT/SS/FF, 105°C — confirm BW and i_n | RX circuit | **P0** |
| 2 | SS corner BW check: verify ≥ 53.125 GHz or confirm Rf programmability sufficient | RX circuit | **P0** |
| 3 | GF PD spec: confirm R ≥ 0.75 A/W and C_PD at operating wavelength (1308–1335 nm) | PD team | **P1** |
| 4 | MRM S21 at PVT corners: verify BW ≥ 60 GHz at SS, 85°C | MRM team | **P1** |
| 5 | TX FIR MMSE optimisation: run channel sim with extracted MRM S21 + TIA response; confirm 3-tap sufficient | TX/RX DSP | **P1** |
| 6 | Re-extract C_in with final GF PD geometry; confirm ≤ 46 fF at 45 μm bump | Packaging | **P1** |
| 7 | MRM asymmetric peaking calibration: build tr/tf coefficient table vs temperature and heater state | TX team | **P2** |
| 8 | TDEC measurement at TP2 with c₊₁ = −0.25; confirm ≤ 3.4 dB spec | Test | **P2** |
| 9 | TIA linearity at Case 11 OMA: verify no clipping at I_OMA = 1.13 mApp | RX circuit | **P2** |
| 10 | End-to-end BER sweep: confirm RS(255,239) margin ≥ 2.5 dB at simulated −3σ OMA | System | **P3** |

---

## 13. System Summary Table

| Parameter | Value | Unit | Status |
|---|---|---|---|
| Baud rate | 106.25 | GBaud | Specification |
| UI | 9.41 | ps | |
| TX FIR | c₋₁=−0.10, c₀=0.65, c₊₁=−0.25 | — | Derived |
| Channel τ_combined | ~2.77 | ps = 0.29 UI | Derived |
| ISI captured by 3-tap FIR | > 99.9 | % | Derived |
| ELS total power | +23.75 | dBm | Measured |
| OMA at TP2 (median / spec floor) | −0.28 / −5.0 | dBm | Measured / OCI spec |
| OMA at PD (median / −3σ) | −8.62 / −11.36 | dBm | Measured |
| Full link loss (median) | 32.39 | dB | Measured |
| TIA + embedded CTLE BW (TT) | ~55 | GHz | **Estimated** |
| TIA input-referred noise (TT) | ~3.0 | μA_rms | **Estimated** |
| PD responsivity | 0.75 | A/W | **Assumed** |
| OMA_sens — uncoded / RS(255,239) | −12.5 / −16.1 | dBm | Derived |
| Gross margin — median / −3σ, RS | +7.5 / +4.7 | dB | Derived |
| Penalties (estimated) | 1.8–2.1 | dB | Estimated |
| **Net margin — median / −3σ, RS** | **+5.4–5.7 / +2.6–2.9** | **dB** | Derived |
| MRM BW (hard requirement) | ≥ 60 | GHz | Measured |
| TX optical rise time | ≤ 8.5 | ps | Specification |
| TX driver rise time | ≤ 6 | ps | Specification |
| TX DJ_pp / σ_RJ / TJ (1e-12) | 2.00 / 0.15 / 4.11 | ps | Specification |
| FEC | RS(255,239) | — | Recommended |
| Net data rate | 99.2 | Gb/s | Derived |

---

## Architecture Verdict

Based on this analysis, the proposed architecture is technically feasible and offers an estimated **+1.6–1.8 dB improvement in net RS(255,239) link margin at −3σ** relative to the prior design (TX FIR + RX FFE + separate active CTLE), while simplifying the receiver by eliminating three analog stages. The improvement is enabled by the short-memory optical-electrical channel (τ ≈ 0.29 UI) and the lower noise of passive TIA bandwidth extension.

**The architecture is contingent on three unconfirmed items:** (1) TIA embedded CTLE achieving ≥ 53 GHz at SS corner; (2) input-referred noise ≤ 3.5 μA_rms; (3) MRM BW remaining ≥ 55 GHz at worst-case PVT. Until post-layout simulation and MRM characterisation close these items, all link margin numbers carry Low confidence and should not be used for product commitments.

---

## Appendix A: Key Formulas

```
Optical rise time (two poles):  t_r = √(t_r1² + t_r2²)
Channel time constant:          τ = 1/(2π·BW_3dB)
ISI at +k UI (Lorentzian):     ISI(k) = exp(−k·UI/τ)
Sufficient no-FFE condition:    BW_channel > UI/(2·ln(1/ε)) ≈ 57 GHz  (for ε < 0.12%)
Necessary condition:            BW_channel >> BR/(2π) ≈ 16.9 GHz
TX FIR at Nyquist:             W(f_Nyq) = −c₋₁ + c₀ − c₊₁
OMA sensitivity:                OMA_sens = 2Q·i_n/R
Optimal threshold (const. σ):  I_th = R·OMA·(ER+1)/(2(ER−1))
TX jitter (Dual Dirac):        TJ(BER) = DJ_pp + 2Q(BER)·σ_RJ
OCI TDEC floor:                OMA_min = max(−5.5, −6.9 + TDEC_dB)  [dBm]
CD pulse broadening:           ΔT = D·L·Δλ  [ps/(nm·km) · km · nm]
```

## Appendix B: OCI Gen2 Wavelength Plan

| Group | Ch | λ (nm) | D [ps/(nm·km)] |
|---|---|---|---|
| A | A0–A3 | 1307.8–1315.1 | 0.05–0.15 |
| B | B0–B3 | 1327.5–1334.9 | 0.60–0.80 |

All channels: CD penalty < 0.1 dB over 500 m SMF-28.

## Appendix C: Architecture Comparison

| Parameter | Prior (TX FIR + RX FFE + sep. CTLE) | **This design (TX FIR, no RX EQ)** |
|---|---|---|
| Separate CTLE stage | 1z2p, 13.4 dB peaking, active | **None — embedded in TIA** |
| CTLE BW | 61.3 GHz | **~55 GHz** |
| RX FFE | 2+1+2 (5 taps) | **None** |
| RX DFE | TBD | **None** |
| TIA noise (TT) | 3.8 μA_rms | **~3.0 μA_rms (est.)** |
| OMA_sens, RS FEC | −15.0 dBm | **−16.1 dBm** |
| ISI penalty | 1.0–1.5 dB | **0.5–0.8 dB** |
| Net margin −3σ, RS | +0.8–1.3 dB | **+2.6–2.9 dB** |
| MRM BW requirement | ≥ 60 GHz (preferred) | **≥ 60 GHz (hard — no FFE fallback)** |
| Bump pitch | 45 μm preferred | **45 μm required** |
| Highest open risk | SS corner noise | **SS corner BW < Nyquist** |

## Appendix D: Supporting Derivations

### D.1 Chromatic Dispersion Pulse Broadening
```
Δλ (transform-limited, α=0, λ=1311 nm):
  Δλ = λ²·B/c = (1311e-9)² × 106.25e9 / 3e8 = 0.609 nm

ΔT = D · L · Δλ = 1.7 ps/(nm·km) × 0.5 km × 0.609 nm = 0.52 ps
  (Using max D in Group A band; worst channel: 1.7 ps/(nm·km) × 0.609 nm × 0.5 km ≈ 0.52 ps
   as fraction of UI: 0.52/9.41 = 5.5% → < 0.1 dB penalty)
```

### D.2 Combined Optical Rise Time
```
t_r_MRM  = 0.35/BW_MRM = 0.35/(60 GHz) = 5.83 ps
t_r_elec = 6.0 ps  (driver spec)
t_r_optical = √(6.0² + 5.83²) = √(36.0 + 34.0) = √70 = 8.37 ps ≈ 8.5 ps  ✓
```

### D.3 TX FIR Frequency Response at Nyquist
```
At f_Nyq: f·T_UI = 0.5  →  e^{±j2π·f_Nyq·T_UI} = e^{±jπ} = −1

W_FIR(f_Nyq) = c₋₁·(−1) + c₀ + c₊₁·(−1)
              = −c₋₁ + c₀ − c₊₁

With c₋₁=−0.10, c₀=0.65, c₊₁=−0.25:
W_FIR(f_Nyq) = 0.10 + 0.65 + 0.25 = 1.00 (0 dB — unity gain at Nyquist)

ΔOMAeff = 20·log10(c₀_new/c₀_old) = 20·log10(0.65/0.68) = −0.37 dB
```

### D.4 DCOC Optimal Threshold and ER-Driven Drift
```
I_thresh_opt = R·OMA·(ER+1)/(2(ER−1))

At ER=4.5 dB (2.82): (ER+1)/(2(ER−1)) = 3.82/3.64 = 1.049
→ threshold is 4.9% above OMA/2

ER variation 3.5→4.5 dB:
  factor at ER=3.5 dB (2.24): (3.24)/(2.48) = 1.306  →  scaled to OMA/2: 1.131 of half-OMA
  factor at ER=4.5 dB (2.82): 1.049
  Δ(I_thresh) = OMA × (1.131 − 1.049)/2 = OMA × 0.041
  At median OMA: 103 μApp × 0.041 ≈ 4.2 μA  (~4.1% of OMA)
  Budget uses 4.7% including TIA offset drift → 4.8 μA
```

### D.5 RIN Noise Calculation
```
P_avg at median OMA = −8.62 dBm, ER=4.5 dB:
  OMA = 10^(−8.62/10) × 10⁻³ = 137.2 μW
  P_avg = OMA×(ER+1)/(2(ER−1)) = 137.2 × 1.049 = 143.9 μW
  I_avg = R × P_avg = 0.75 × 143.9 μW = 107.9 μA

BW_n ≈ 1.11 × 55 GHz = 61.1 GHz  (Butterworth noise BW estimate)
RIN_OMA = 10^(−138/10) = 1.585×10⁻¹⁴ /Hz

σ_RIN = √(RIN_OMA × I_avg² × BW_n)
      = √(1.585e-14 × (107.9e-6)² × 61.1e9)
      = √(1.585e-14 × 1.164e-8 × 6.11e10)
      = √(1.13e-11) = 3.36 nA_rms

Ratio to TIA noise: 3.36 nA / 3000 nA = 0.0011  →  < 0.001 dB penalty
```

### D.6 RX Optical Loss — Full Per-Element Breakdown (TP3 → PD)

| Element | Loss (dB) |
|---|---|
| External fiber plant (TP3b) | 2.500 |
| Rx faceplate + FAU connectors | 0.400 |
| Rx fiber attach TM (lognormal, 1.009 dB median) | 1.009 |
| Fiber attach aging | 0.500 |
| Rx edge coupler on-chip | 0.100 |
| Rx PSR (TM) + SiN-Si escalators | 0.510 |
| PSR tap (1%) + interleaver tap (1%) | 0.030 |
| Rx interleaver | 0.464 |
| Interleaver control loss | 0.120 |
| Rx VOA passive + NLA | 0.210 |
| Rx routing to CRR | 0.350 |
| CRR input tap + control + passive | 0.520 |
| CRR to PD passive | 0.500 |
| Rx SiN-Si escalator | 0.050 |
| **Total TP3 to PD** | **~5.76 dB ≈ 5.79 dB** |
