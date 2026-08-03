# OCI Gen2 106G NRZ — SerDes TX Discussion Outline
**For:** Cadence (CDNS) L250 SerDes Team  
**From:** Lightmatter  
**Purpose:** Alignment on TX FIR requirements and interface spec ahead of slide development  
**Status:** Preliminary — for discussion

---

## 1. Context

Lightmatter is designing an OCI Gen2 coherent photonic interconnect running **106.25 GBaud NRZ** per lane over 500 m SMF. The TX SerDes (CDNS L250) drives an integrated micro-ring modulator (MRM). This is an optical modulation application — the channel and equalization requirements differ significantly from a standard electrical SerDes application.

Key differences from a standard backplane/copper SerDes deployment:
- Driver sees a **lumped RC load** (MRM electrode: C ≈ 10–30 fF, R ≈ 10–30 Ω) — no transmission line, no 50 Ω termination
- Channel ISI is dominated by the **MRM Lorentzian optical response** (BW target ≥ 60 GHz), not a PCB trace
- **No RX-side FFE or DFE** — the TX FIR must pre-compensate the full channel (MRM + RX TIA) with 3 taps only
- **Asymmetric rise/fall correction** is required to cancel MRM optical nonlinearity

---

## 2. TX FIR Requirements

### 2.1 Tap Configuration

- **3 taps:** pre-cursor (c₋₁), main cursor (c₀), post-cursor (c₊₁)
- Normalization: |c₋₁| + c₀ + |c₊₁| = 1
- **Working design point:** c₋₁ = −0.10, c₀ = 0.65, c₊₁ = −0.25

The post-cursor tap is dominant and compensates the MRM Lorentzian post-ISI **and** the RX TIA response. Because there is no RX FFE, the TX FIR carries all equalization responsibility.

**Discussion topic for CDNS:** Can L250 support coefficient optimization targeting a photonic (MRM + optical TIA) channel model rather than a standard electrical channel? What is the expected convergence path?

### 2.2 Coefficient Range and Resolution

| Tap | Range | Step size | Notes |
|---|---|---|---|
| c₋₁ (pre) | 0 to −0.30× | 3-bit (0.043/step) | Group delay from TIA |
| c₀ (main) | derived from normalization | — | |
| c₊₁ (post) | 0 to −0.30× | 3-bit (0.043/step) | MRM + TIA ISI; needs −0.25 |

**Discussion topic:** Is −0.25 reachable with 3-bit resolution (step 0.043)? Nearest 3-bit value: −0.258 (6 steps). Confirm quantization error is acceptable.

### 2.3 Asymmetric Rise/Fall Correction

MRM transfer function T(V) is nonlinear (Lorentzian) — the optical edge into resonance
is faster than the edge out of resonance. This creates duty-cycle distortion (DCD) in the
optical eye. The driver must apply **independent, asymmetric slew rate control** on rise vs fall.

**Discussion topic for CDNS:** Does L250 support independent tr/tf adjustment (not just
symmetric peaking)? What is the control granularity? Can this be software-programmable
per-channel at runtime (temperature-tracking requirement)?

---

## 3. Electrical Interface Spec (Driver Output)

| Parameter | Target | Notes |
|---|---|---|
| Differential output swing | 0.5–1.5 Vpp diff | 1.0 Vpp typical for ER ≈ 4.5 dB |
| Output impedance / return loss | **N/A** | No transmission line — lumped RC load only |
| Rise/fall time (20-80%) | **≤ 6 ps** | At MRM electrode; after TX FIR |
| Baud rate | 106.25 GBaud | OCI Gen2 |

---

## 4. Jitter Budget (BER = 1×10⁻¹²)

Target total jitter at TP2 (optical fiber attach):

| Component | Budget |
|---|---|
| DJ_pp total | ≤ 2.00 ps_pp (21% UI) |
| σ_RJ | ≤ 0.15 ps_rms |
| TJ at BER = 1e-12 | ≤ 4.11 ps_pp (44% UI) |

**Discussion topic for CDNS:** What is L250's TX output jitter at 106.25 GBaud with 3-tap FIR active? Is the σ_RJ ≤ 0.15 ps spec achievable from the PLL at this baud rate?

---

## 5. Open Questions for CDNS

1. **FIR coefficient adaptation:** Does L250 support an adaptive/LMS mode for TX FIR, or coefficient loading only? For this application, startup adaptation to an MRM+TIA channel model is needed.

2. **Asymmetric peaking control:** Independent programmable tr/tf slew — available? Granularity?

3. **Rise time spec margin:** What is L250's nominal electrical rise time at 106 GBaud with 3-tap FIR? Do we have margin to the 6 ps target?

4. **Jitter characterisation:** Can CDNS provide σ_RJ and DJ_pp data at 106.25 GBaud for L250?

5. **Supply sensitivity (PSIJ):** What is expected PSIJ contribution from SerDes supply coupling at expected supply noise frequencies? Target ≤ 0.30 ps_pp PSIJ.

6. **SS corner performance:** L250 TX output BW at SS process corner — does rise time stay ≤ 6 ps?

---

## 6. Suggested CDNS Slide Topics

- L250 TX FIR: tap count options, coefficient range/resolution at 106 GBaud
- Asymmetric tr/tf capability and software programmability
- TX output jitter characterisation (DJ, σ_RJ) at 106 GBaud
- TX output swing range and programmability
- Channel adaptation flow for non-standard (optical) channel
- PSIJ / supply coupling characterisation
- SS corner electrical performance data

---

## 7. Next Steps

| Action | Owner | Timing |
|---|---|---|
| CDNS to confirm L250 3-tap coefficient range at 106G | CDNS | Before next sync |
| CDNS to share TX jitter (DJ, RJ) characterisation data at 106 GBaud | CDNS | Before next sync |
| CDNS to confirm asymmetric tr/tf adjustment capability | CDNS | Before next sync |
| Lightmatter to share MRM + TIA channel model for FIR optimisation | Lightmatter | After MRM S21 measurement |
| Joint FIR coefficient optimisation session | Both | TBD |
