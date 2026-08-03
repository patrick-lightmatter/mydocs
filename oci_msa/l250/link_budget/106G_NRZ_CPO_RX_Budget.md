# 106G NRZ CPO Optical Receiver Budget

**System:** OCI Gen2 GF — CDNS Custom SerDes (L250)  
**Modulation:** NRZ OOK  
**Data rate:** 106 Gbps per lane  
**Wavelength:** 1310 nm, 4-lambda WDM  
**Last updated:** 2026-08-01  
**Source data:** `ocigen2gf_OMA_rollup_2026-07-13`, CliffSubset slides (2026-07-22/30)

---

## 1. System Architecture

```
Laser (+23.75 dBm)
  |
  |-- Delivery chain (PMF, FAU, fiber attach, aging)
  |-- On-chip routing (edge coupler, SiN mux, splitters)
  |-- Tx VOA (clamp <= +10 dBm)
  |-- MRM modulator bank (4x at 106G NRZ, OMA ~+3.67 dBm at Tx3e)
  |-- Post-MRM routing + interleaver + PSR
  |-- Tx fiber attach + FAU + connector (TP2)vscode-webview://1d2fvsm6kqomguvm4oh0itqm0bff8gibb2vequgtavbc7jgjbhpo/home/patrick/mydocs/106G_NRZ_CPO_RX_Budget.md
  |
[External 2.5 dB fiber plant]
  |
  |-- Rx fiber attach + FAU + connector (TP3)
  |-- Rx PSR + interleaver + VOA + CRR
  |-- Rx routing to PD (Rx6a)      <- OMA target: >= sensitivity
  |
  PD (~6 fF, R ~0.75 A/W)
  |
  TIA (Caribou 224g / L250, R_f = 600 ohm)
  |
  CTLE (1z, 2p -- zero @ 14.5 GHz, biquad pole @ 56.4 GHz, Q = 1.168)
  |
  Buffer (source-follower)
  |
  Interleaved S/H --> ADC --> FFE (2+1+2) / DFE --> Decision
```

---

## 2. OCI Gen2 GF Optical Power Budget

Three use cases from `ocigen2gf_OMA_rollup_2026-07-13`:

| Use case | Mode | OMA at Rx PD (-3sigma) | Median | (+3sigma) |
|---|---|---|---|---|
| Case 10 (on-chip mux SKU) | Mission | -11.36 dBm | **-8.62 dBm** | -6.97 dBm |
| Case 11 (on-chip mux SKU) | Max power | -0.96 dBm | **+1.79 dBm** | +3.46 dBm |
| Case 23 (muxed input SKU) | Loopback | +0.09 dBm | **+0.50 dBm** | +0.90 dBm |

**Mission mode (Case 10) is the binding case.** All link margin analysis below uses Case 10.

### 2.1 Key Segment Losses -- Case 10, Mission Mode

| Segment | Description | -3sigma (dB) | Median (dB) | +3sigma (dB) |
|---|---|---|---|---|
| Laser output | Pav | -- | +23.75 dBm | -- |
| Laser to TP2 | Full TX network | 23.46 | **25.06** | 27.42 |
| mod to TP2 | Post-MRM to faceplate | 2.86 | **3.95** | 6.09 |
| TP3 to PD | Rx chip optical path | 4.72 | **5.79** | 7.91 |
| Full link loss | Laser to PD | 30.33 | **32.39** | 35.33 |
| OMA at Rx PD | Net signal at photodetector | -11.36 | **-8.62** | -6.97 |

**MRM modulator parameters (3 V drive, 106G NRZ):**
- OMA relative to Pav (Tx3a): 3.70 dB (nominal)
- Average power loss of modulated MRM (Tx3b): 4.70 dB below input Pav
- MRM bus NLA loss (Tx3d, 4x MRMs tuned): 1.806 dB median
- MRM bus passive loss (Tx3e): 0.310 dB

**Dominant variable loss elements driving the +-3sigma spread:**
- Laser fiber attach (lognormal, 1.08 dB mean, sigma=0.411): ~1.3 dB spread
- Rx fiber attach TM (same lognormal): ~1.3 dB spread
- TX interleaver (skew-normal, 0.46 dB median): ~0.5 dB spread
- Rx interleaver: ~0.5 dB spread

### 2.2 Receive-Side Optical Losses (TP3 to PD), Median Breakdown

| Element | Loss (dB) |
|---|---|
| External fiber plant (TP3b) | 2.500 |
| Rx faceplate connector | 0.200 |
| Rx FAU connector | 0.200 |
| Rx fiber attach TM (lognormal) | 1.009 |
| Fiber attach aging | 0.500 |
| Rx edge coupler on-chip | 0.100 |
| Rx PSR (TM) + SiN-Si escalator | 0.460 |
| Si-SiN escalator | 0.050 |
| PSR tap (1%) | 0.010 |
| Rx interleaver | 0.464 |
| Interleaver control loss | 0.120 |
| Interleaver tap (1%) | 0.020 |
| SiN-Si escalator | 0.050 |
| Rx VOA passive + NLA | 0.210 |
| Rx routing to CRR | 0.350 |
| CRR input tap (1%) | 0.010 |
| CRR control loss | 0.200 |
| CRR bank passive | 0.310 |
| CRR to PD passive | 0.500 |
| **Total TP3 to PD** | **~5.79 dB** |

Note: In max-power mode (Case 11) the Rx VOA is fully transparent, producing 10+ dB
higher OMA at the PD. Verify TIA VGA/AGC headroom at this extreme.

---

## 3. CPO Interconnect & TIA Input Capacitance

CPO co-packages PIC and EIC via micro-bumps. C_in at the TIA input is the first-order
CPO-specific design variable driving CTLE boost requirements.

| Component | Capacitance | Notes |
|---|---|---|
| PD (GF target -- TBD) | ~6 fF | Must update to actual GF PD model |
| PIC interconnect (EMX/Coupe) | 3.4 fF | Needs re-extraction with GF PD |
| Micro-bump (45 um pitch) | 10 fF | 5 pH series inductance |
| Micro-bump (110 um pitch) | 40 fF | 10 pH series inductance |
| EIC interconnect (EMX/N3) | 2.7 fF | Needs re-extraction |
| ESD cap (CDM 25 V) | ~24 fF | Attach to T-coil/inverter port (not PD side) |
| **Total C_in (45 um bump)** | **~46 fF** | Best case |
| **Total C_in (110 um bump)** | **~76 fF** | Worst case |

The 30 fF difference between bump pitches is the largest controllable C_in knob.

---

## 4. TIA & CTLE Front-End Specification

### 4.1 TIA Parameters (Caribou 224g model, target for L250)

| Parameter | Value | Notes |
|---|---|---|
| Topology | Inverter + T-coil + feedback R | CMOS inverter TIA |
| Feedback resistance R_f | 600 ohm | |
| Inverter multiplier (m-factor) | 100 | |
| Supply V_DDA | 0.75 V nom / 0.85 V opt | 0.85 V reduces CTLE boost ~1-2 dB |
| Inverter stacking | 2-stack | 1-stack saves 1-2 dB CTLE boost; 2-stack for ESD |
| ESD placement | T-coil port to inverter | Better BW than direct PD attach (Caribou DR validated) |
| ESD cap (CDM 25V) | ~24 fF | |
| Midband gain (before CTLE, 1 GHz) | ~54.8 dB (V/A) | TT corner |

**Behavioural model calibration status:**
- Midband gain: ~0.7 dB delta vs. extracted netlist -- acceptable for initial estimates
- Eye amplitude: model is ~3 dB larger than extracted (optimistic -- do not use for margin)
- Input current: model shows excess overshoot (T-coil input impedance too optimistic)
- Action items: update to GF PD model; re-extract PIC/EIC parasitics; fix T-coil load

### 4.2 CTLE Filter (Python-Optimized 1z2p)

Optimization target: BW_3dB >= 50 GHz AND phase delay variation <= 3 ps (0-56 GHz).

| Parameter | Before CTLE | After CTLE | Unit |
|---|---|---|---|
| Bandwidth (3 dB) | 10.5 | **61.3** | GHz |
| CTLE peaking | -- | 13.4 | dB |
| Group delay pp (0-56 GHz) | 14.6 | 6.7 | ps |
| Phase delay pp (0-56 GHz) | 11.0 | 3.0 | ps |
| Input-referred noise | 1.4 | **3.8** | uA_rms |

Optimized coefficients (TT, 105 C, bump_cap_factor=1, i.e. 45 um pitch):

| Filter parameter | Value |
|---|---|
| Zero frequency | 14.50 GHz |
| Biquad pole frequency | 56.36 GHz |
| Biquad Q | 1.168 |

The CTLE integrates noise over wider bandwidth: input-referred RMS noise increases
1.4 -> 3.8 uA_rms. SS corner characterization is pending and will likely be worse.

Bandwidth vs. 106G NRZ Personick criterion:
- Without equalization: BW_opt = 0.65 x 106 = 69 GHz
- With CTLE/DFE: BW >= 50 GHz sufficient
- Achieved (TT, 105 C): 61.3 GHz -- within spec

---

## 5. Noise & Sensitivity Analysis

### 5.1 Noise Bandwidths (Bessel Filter Approx, BW_3dB = 61.3 GHz)

| Noise bandwidth | Formula | Value |
|---|---|---|
| BW_n (white/thermal, 1st-order) | 1.15 x BW_3dB | **70.5 GHz** |
| BW_n2 (f^2 gate noise, 2nd-order) | 1.78 x BW_3dB | **109.1 GHz** |

### 5.2 Sensitivity Formulas

For NRZ OOK, thermal-noise dominated (sigma_0 = sigma_1 = i_n_rms):

```
OMA sensitivity:      OMA_sens    = 2Q x i_n_rms / R
Avg power sensitivity: P_avg_sens = Q x i_n_rms / R

With photodiode shot noise:
  P_avg_sens_PIN = (Q x i_n_rms / R) + (Q^2 x q x BW_n / R)
```

where Q = Personick Q-factor, R = PD responsivity [A/W], q = 1.6e-19 C.

### 5.3 Baseline Assumptions

| Parameter | Value | Status |
|---|---|---|
| i_n_rms | 3.8 uA_rms | TT 105 C after CTLE. SS corner: TBD. |
| PD responsivity R | 0.75 A/W | Assumed -- **confirm GF PD spec** |
| Wavelength | 1310 nm | OCI Gen2 GF |
| BW_3dB (post-CTLE) | 61.3 GHz | TT, 105 C |
| BW_n | 70.5 GHz | Bessel approximation |

### 5.4 Sensitivity vs. BER / FEC Target

| BER target | Personick Q | OMA_sens (dBm) | P_avg_sens (dBm) | Application |
|---|---|---|---|---|
| 10^-12 | 7.035 | **-11.5** | -14.5 | Uncoded raw link |
| 10^-5  | 4.265 | -14.3 | -17.3 | High-perf FEC pre-FEC |
| 10^-3  | 3.090 | **-15.0** | -18.0 | RS(255,239) pre-FEC |

Shot noise penalty at median received OMA (-8.62 dBm, R = 0.75 A/W, Q = 7.035):
  Q^2 x q x BW_n / R = 49.5 x 1.6e-19 x 70.5e9 / 0.75 = 0.75 uW ~ 0.02 dB
Shot noise is negligible (<0.1 dB) -- this is a thermal-noise dominated design.

---

## 6. Link Margin Summary

**Reference: Case 10, mission mode, on-chip mux SKU.**

### 6.1 Gross Link Margin (Before Penalties)

| | -3sigma OMA | Median OMA | +3sigma OMA |
|---|---|---|---|
| OMA at PD (dBm) | -11.36 | -8.62 | -6.97 |
| Uncoded sensitivity (dBm OMA) | | -11.5 | |
| **Gross margin -- uncoded** | **+0.14 dB** | **+2.88 dB** | +4.53 dB |
| RS(255,239) sensitivity (dBm OMA) | | -15.0 | |
| **Gross margin -- RS FEC** | **+3.64 dB** | **+6.38 dB** | +8.03 dB |

The uncoded -3sigma gross margin is only +0.14 dB.
**RS(255,239) FEC is mandatory** for robust operation across the full optical distribution.

### 6.2 Power Penalty Budget

| Penalty | Estimate (dB) | Notes |
|---|---|---|
| Decision threshold offset (DCOC) | ~0.5 | PP = 1 + 2*delta; depends on DCOC loop settling |
| Residual ISI / eye closure | ~1.0-1.5 | After CTLE + 2+1+2 FFE; worst at +3sigma loss corner |
| Reflection / back-scatter | ~0.3 | Reduced in CPO vs. pluggable (short optical path) |
| Wavelength PDL (4-lambda) | ~0.5 | Interleaver + PSR insertion loss variation across lambda |
| Dark current (I_DK) | TBD | Awaiting GF PD spec; expected <0.1 dB |
| TIA noise at SS corner | TBD | 3.8 uA_rms is TT 105 C only -- SS sweep required |
| **Total estimated penalty** | **~2.3-2.8 dB** | Excluding uncharacterized SS noise |

### 6.3 Net Link Margin After Penalties

| Mode | Median OMA | -3sigma OMA |
|---|---|---|
| Uncoded (10^-12) | +0.1 to +0.6 dB | **Negative -- link fails** |
| RS(255,239) FEC (10^-3) | **+3.6 to +4.1 dB** | **+0.8 to +1.3 dB** |

---

## 7. FEC Options

RS(255,239): 7.1% overhead, corrected BER = 10^-12, net electrical coding gain ~5.6 dB.

| Metric | Uncoded | RS(255,239) | KP4 (BER_pre = 2.4e-4) |
|---|---|---|---|
| Required raw BER | 10^-12 | 10^-3 | 2.4e-4 |
| Personick Q | 7.035 | 3.090 | ~3.54 |
| OMA sensitivity | -11.5 dBm | -15.0 dBm | ~-14.2 dBm |
| Gain vs. uncoded | -- | **+3.5 dB** | +2.7 dB |
| Overhead | 0% | 7.1% | 6.25% |
| Net median margin (2.5 dB penalty applied) | +0.4 dB | +3.9 dB | +3.2 dB |

RS(255,239) is the primary recommendation. KP4 is viable if lower overhead is needed.

---

## 8. Maximum Tolerable TIA Noise

i_n_max = i_sig_pp / (2Q) = R x OMA / (2Q). Baseline: R = 0.75 A/W, BW_3dB = 61.3 GHz.

| OMA at PD | i_sig_pp | Max i_n -- uncoded (Q=7.035) | Max i_n -- RS FEC (Q=3.090) |
|---|---|---|---|
| -11.5 dBm | 53 uApp | 3.8 uA_rms | 8.6 uA_rms |
| -8.6 dBm (median) | 103 uApp | 7.3 uA_rms | 16.7 uA_rms |
| -7.0 dBm (+3sigma) | 149 uApp | 10.6 uA_rms | 24.1 uA_rms |
| +1.8 dBm (max pwr) | 1130 uApp | 80 uA_rms | -- |

At TT 105 C, TIA+CTLE delivers 3.8 uA_rms. This exactly meets uncoded at median OMA
with no headroom. With RS FEC at median OMA the noise budget opens to 7.3 uA_rms.

---

## 9. Equalization Budget

Source: L250 Griffin EVK specification.

| Block | Configuration | Role |
|---|---|---|
| CTLE | 1z2p Python-optimized | Extend BW to 61.3 GHz; compensate C_in roll-off |
| RX FFE | 2 pre + 1 main + 2 post taps | Residual linear ISI after CTLE |
| RX DFE | TBD | Post-cursor ISI without noise enhancement |

At 106G NRZ (UI = 9.43 ps) with 61.3 GHz front-end, residual channel memory is
non-trivial. FFE tap adequacy should be verified against measured TIA impulse responses
at worst-case C_in (110 um bump pitch).

---

## 10. Design Trade-Off Summary

| Decision | Trade-off | Recommendation |
|---|---|---|
| **Bump pitch** | 45 um (10 fF) vs. 110 um (40 fF) | **45 um strongly preferred** -- 30 fF C_in saving |
| **ESD placement** | PD-side vs. T-coil/inverter port | **T-coil port** -- better BW (Caribou DR validated) |
| **V_DDA** | 0.75 V vs. 0.85 V | 0.85 V reduces CTLE boost 1-2 dB; minor noise cost |
| **Inverter stacking** | 1-stack vs. 2-stack | 1-stack saves 1-2 dB boost; 2-stack if ESD spec is firm |
| **FEC** | None / RS(255,239) / KP4 | **RS(255,239) mandatory**; KP4 if overhead is constrained |
| **PD responsivity** | 0.75 A/W assumed | **Confirm GF PD spec** -- 0.1 A/W shifts sensitivity ~0.5 dB |
| **TIA noise PVT** | TT 105 C only characterized | **Run SS + high-temp corner** sweep immediately |

---

## 11. Top-Line Summary

| Parameter | Value | Unit |
|---|---|---|
| Data rate | 106 | Gbps/lane |
| Wavelength | 1310, 4-lambda | nm |
| Laser output (typ) | +23.75 | dBm |
| OMA at MRM output (Tx3e, median) | +3.67 | dBm |
| Full link loss (median / +3sigma) | 32.4 / 35.3 | dB |
| **OMA at PD -- mission median** | **-8.62** | **dBm** |
| **OMA at PD -- mission -3sigma** | **-11.36** | **dBm** |
| TIA feedback resistance | 600 | ohm |
| TIA input cap (45 um bump, estimated) | ~46 | fF |
| CTLE post-filter BW (TT 105 C) | 61.3 | GHz |
| CTLE peaking | 13.4 | dB |
| Input-referred noise (TT 105 C) | **3.8** | **uA_rms** |
| PD responsivity (assumed) | 0.75 | A/W |
| OMA sensitivity -- uncoded (10^-12) | -11.5 | dBm |
| OMA sensitivity -- RS FEC (10^-3) | -15.0 | dBm |
| Gross link margin -- median, RS FEC | +6.4 | dB |
| Gross link margin -- -3sigma, RS FEC | +3.6 | dB |
| Estimated power penalties | ~2.3-2.8 | dB |
| **Net margin -- median, RS FEC** | **+3.6 to +4.1** | **dB** |
| **Net margin -- -3sigma, RS FEC** | **+0.8 to +1.3** | **dB** |

---

## 12. Next Steps (Priority Order)

1. **Confirm GF PD responsivity and dark current** -- largest unresolved assumption
2. **Run TIA+CTLE noise across PVT corners** -- SS corner is the critical unknown
3. **Re-extract PIC/EIC interconnect parasitics** with GF PD geometry
4. **Fix T-coil input impedance in behavioural model** (currently 3 dB optimistic on eye)
5. **Quantify ISI penalty** with full FFE simulation at worst-case 3sigma optical channel
6. **Lock bump pitch** (45 um vs. 110 um) -- first-order sensitivity decision
7. **Lock FEC choice** (RS(255,239) vs. KP4) to set final margin targets
