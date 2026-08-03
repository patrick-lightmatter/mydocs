# 106G NRZ CPO Link Budget — Technical Q&A
**Reference:** 106G_NRZ_CPO_Link_Budget.md (OCI Gen2, no-RX-EQ architecture)

---

## 1. Why can the RX FFE and DFE be completely omitted?

The key is that both channel poles — the MRM Lorentzian and the TIA embedded CTLE — have very short time constants relative to the unit interval:

| Stage | BW | τ = 1/(2π·BW) | τ / UI |
|---|---|---|---|
| MRM | 60 GHz | 2.65 ps | 0.28 |
| TIA + embedded CTLE | 55 GHz | 2.89 ps | 0.31 |
| Combined | ~40 GHz effective | ~2.77 ps | **0.29** |

Because τ_combined = 2.77 ps is only 0.29 UI, ISI decays exponentially and is almost entirely gone by +1 UI:

```
ISI at +1 UI:  exp(−9.41 / 2.77) = exp(−3.40) = 3.3%   ← TX FIR c₊₁ cancels this
ISI at +2 UI:  exp(−18.82 / 2.77) = exp(−6.79) = 0.11%  ← below quantization noise
ISI at +3 UI:  0.004%                                     ← negligible
```

Total ISI energy outside ±1 UI = 0.12%, so the 3-tap TX FIR (spanning ±1 UI = ±9.41 ps) captures **> 99.9% of ISI energy**. After optimal c₊₁ cancellation, residual post-cursor ISI is < 0.3% — less than the quantization error of any practical equalizer tap. There is simply nothing left for an RX FFE or DFE to improve upon.

The enabling bandwidth condition is **τ << UI**, or equivalently **BW_channel >> BR / (2π)** = 106.25 / 6.28 ≈ 16.9 GHz. Both the MRM (60 GHz) and TIA (55 GHz) easily satisfy this, making this architecture viable.

---

## 2. How do TX FIR tap coefficients shift when targeting the full MRM + TIA channel?

When the TX FIR was backed up by an RX 2+1+2 FFE, it only needed to pre-compensate the MRM Lorentzian post-cursor. With no RX FFE, it must cancel the combined first post-cursor from both stages:

| Source | ISI at +1 UI (before FIR) |
|---|---|
| MRM alone (60 GHz) | exp(−9.41/2.65) = 2.9% |
| TIA alone (55 GHz) | exp(−9.41/2.89) = 3.8% |
| Combined (approximate) | ~6.4% |

This drives c₊₁ from −0.22 to **−0.25** to null the larger combined ISI. By the normalization constraint |c₋₁| + c₀ + |c₊₁| = 1, c₀ drops from 0.68 to **0.65**:

| Coefficient | With RX FFE | **No RX EQ** | Change |
|---|---|---|---|
| c₋₁ | −0.10 | −0.10 | unchanged |
| c₀ | 0.68 | **0.65** | −0.03 |
| c₊₁ | −0.22 | **−0.25** | −0.03 |

**Effect on Nyquist gain:** The FIR response at the Nyquist frequency (f·T_UI = 0.5) is:

```
W_FIR(f_Nyq) = −c₋₁ + c₀ − c₊₁ = 0.10 + 0.65 + 0.25 = 1.00
```

The Nyquist gain remains unity in both designs — the FIR correctly inverts the channel rolloff at Nyquist. However, the **main cursor c₀ = 0.65 vs 0.68** means the effective signal amplitude at the decision point is reduced by 20·log(0.65/0.68) = **0.37 dB** — a small but real OMA penalty, already absorbed into the TDEC budget (design sub-total increases from 2.0 to ~2.2 dB).

---

## 3. What physical mechanism causes MRM optical edge asymmetry and how is it corrected?

The MRM operates via ring resonance shift: the laser is held near the ring's resonant wavelength, and the applied voltage shifts the resonance through the plasma dispersion effect, toggling between high-transmission (off-resonance, logic "1") and low-transmission (on-resonance, logic "0") states.

The MRM transfer function is Lorentzian:

```
T(V) = T_max / [1 + (V − V_res)² / (ΔV_FWHM/2)²]
```

This function is nonlinear in V. Crucially, the **gradient dT/dV** is different on the two sides of resonance. As a result, driving the ring *onto* resonance (into the absorptive state) sweeps through the steep rising slope of T(V) — producing a fast optical falling edge — while driving the ring *off* resonance requires waiting for photons trapped in the cavity to leak out, limited by the photon lifetime τ_ph = 1/(2π·BW_MRM) = 2.65 ps. This produces a slower optical rising edge.

The result is **asymmetric optical rise and fall times** (tr_optical ≠ tf_optical), which appears as duty-cycle distortion (DCD) in the optical eye at TP2.

**Correction:** The integrated MRM driver applies **independent, asymmetric slew rate control** on the electrical drive signal — pre-distorting the rise and fall edges separately to equalize the resulting optical edges. This is a Lightmatter-specific capability requiring per-channel calibration, because the correction coefficients depend on the MRM operating point (heater-set bias), drive amplitude, and temperature. The residual DCD after correction is budgeted at 0.15 dB in the TDEC table.

---

## 4. Why is 45 μm bump pitch strictly required, and what happens at 110 μm?

The micro-bump is the dominant variable capacitance in the TIA input node. Its capacitance scales strongly with pitch:

| Component | 45 μm bump | 110 μm bump |
|---|---|---|
| Micro-bump | ~10 fF | ~40 fF |
| All other parasitics | ~36 fF | ~36 fF |
| **Total C_in** | **~46 fF** | **~76 fF** |

The unpeaked TIA pole frequency scales as f_3dB = 1/(2π · Rf · C_in):

```
45 μm:  f_base = 1/(2π × 600 Ω × 46 fF) = 5.77 GHz
110 μm: f_base = 1/(2π × 600 Ω × 76 fF) = 3.50 GHz
```

Reaching the 55 GHz embedded CTLE target requires approximately 9.5× bandwidth extension from the T-coil + shunt peaking network. Applied to each base:

```
45 μm:  5.77 GHz × 9.5 ≈ 55 GHz  ✓  target met
110 μm: 3.50 GHz × 9.5 ≈ 33 GHz  ✗  below Nyquist (53.125 GHz)
```

At 36 GHz (the document's estimate for 110 μm), the embedded CTLE BW is below Nyquist. Without an RX FFE to compensate, this guarantees uncorrectable ISI and a BER floor. The only alternatives — reducing Rf or increasing peaking beyond the passive T-coil regime — both dramatically worsen noise. **45 μm is therefore a hard architectural constraint, not a preference.**

---

## 5. How does the embedded CTLE reduce noise versus a separate active CTLE stage?

A separate active CTLE stage degrades noise in two ways:

1. **It amplifies existing TIA noise.** With 13.4 dB of peaking at ~50 GHz, the CTLE boosts the TIA's high-frequency noise components by up to 13.4 dB (≈5× in amplitude) before integration. The noise bandwidth grows from ~12 GHz (TIA alone) to 70.5 GHz.

2. **It adds its own circuit noise.** The CTLE transistors and resistors contribute an input-referred self-noise estimated at ~2.0 μA_rms equivalent.

Combined effect: 1.4 μA_rms (TIA alone) → 3.8 μA_rms after separate CTLE — a 2.71× (8.6 dB power) increase.

The embedded T-coil approach eliminates both noise mechanisms:

- The T-coil is a passive (lossless) element. Its spiral resistance ≈ 2–5 Ω contributes only:
  `σ_Rtcoil = √(4kT × 3 Ω × 63 GHz) ≈ 55 nA_rms` — 55× below the baseline TIA noise.
- There is no separate gain stage amplifying the noise spectrum.

The resulting noise is dominated purely by the TIA's own thermal sources, scaled by the increased noise bandwidth:

```
σ_n_embedded ≈ 1.4 × √(BW_n_embedded / BW_n_base) ≈ 1.4 × √(61/11.7) ≈ 3.0 μA_rms
```

This yields **OMA sensitivity of −16.1 dBm (RS FEC)** versus −15.0 dBm for the separate CTLE design — a **~1.1 dB improvement** — without any additional circuit complexity.

---

## 6. Which use case is the binding mission case, and what are the OMA levels at the PD?

**Case 10 (On-chip mux, Mission mode)** is the binding case from the `ocigen2gf_OMA_rollup_2026-07-13` dataset. It represents the nominal operating point with all realistic loss contributions included (fiber attach variability, on-chip routing, aging).

| Statistic | OMA at Photodetector |
|---|---|
| +3σ | −6.97 dBm |
| **Median** | **−8.62 dBm** |
| **−3σ** | **−11.36 dBm** |

The median OMA at the PD is −8.62 dBm, derived from the full loss chain:

```
OMA at TP2 (median): −0.28 dBm
Fiber (500 m SMF-28): −2.5 dB
RX chip optical path (TP3 to PD): −5.79 dB
OMA at PD:  −0.28 − 2.5 − 5.79 ≈ −8.57 dBm  ≈ −8.62 dBm ✓
```

Cases 11 and 23 produce much higher OMA at the PD (+1.79 dBm and +0.50 dBm median respectively), but these create a linearity/dynamic range requirement on the TIA rather than a sensitivity requirement. Case 10 defines the receiver sensitivity floor.

---

## 7. How does ER = 4.5 dB shift the optimal decision threshold, and why must DCOC be dynamic?

For a constant-noise TIA (σ₀ = σ₁ = i_n_rms), the optimal decision threshold is at the midpoint of the two signal levels — which equals the average photocurrent:

```
I_thresh_opt = R × P_avg = R × OMA × (ER + 1) / (2(ER − 1))
```

At ER = 4.5 dB (linear ratio 2.82):

```
(ER + 1) / (2(ER − 1)) = 3.82 / 3.64 = 1.049
```

The optimal threshold sits **4.9% of OMA above the midpoint** (OMA/2), shifted toward the "1" level because the "0" level is not at zero — it has residual photocurrent P0 = OMA/(ER−1). A DCOC loop that targets OMA/2 rather than Pavg introduces a ~4.9% error, resulting in approximately 0.5 dB power penalty.

**Why continuous DCOC is required:** The MRM operating point is actively controlled by a thermal heater loop, and the ER varies between 3.5 and 4.5 dB over the operating range (temperature, Vswing, aging). The optimal threshold P_avg shifts accordingly:

```
ΔI_thresh ≈ 0.062 × 0.75 A/W × OMA_pp ≈ 4.8 μA  (at median mission OMA)
```

This is a ~4.7% shift in OMA — comparable to the original DCOC error itself. A factory-calibrated static threshold cannot track these real-time operating point changes. The DCOC loop must remain active and have a settling time fast enough (< 1 μs) to follow MRM heater updates.

---

## 8. What are the TX jitter limits at BER = 1×10⁻¹², and what eye opening remains at the RX decision point?

**TX driver jitter budget (at TP2):**

| Component | Value | % UI |
|---|---|---|
| DJ_pp (DCD + ISI + BUJ + PSIJ) | ≤ 2.00 ps_pp | 21.3% |
| σ_RJ (SerDes TX PLL VCO) | ≤ 0.15 ps_rms | 1.6% |
| **TJ at BER = 1×10⁻¹²** | **≤ 4.11 ps_pp** | **43.7% UI** |
| **TX eye opening at TP2** | **5.30 ps** | **56.3% UI** |

Using the Dual Dirac model: TJ = DJ_pp + 2Q·σ_RJ = 2.00 + 14.07 × 0.15 = 4.11 ps.

**At the RX decision point**, CDR tracking adds ~0.10 ps_pp DJ and ~0.10 ps_rms RJ:

```
DJ_total = 2.00 + 0.10 = 2.10 ps_pp
σ_RJ_total = √(0.15² + 0.10²) = 0.187 ps_rms

TJ_decision = 2.10 + 14.07 × 0.187 = 4.73 ps_pp
Eye opening = 9.41 − 4.73 = 4.68 ps = 49.7% UI
```

**49.7% of UI** remains open at the decision point — healthy margin for CDR steady-state phase error and sampler metastability. The eye does not close below 40% UI even with CDR additions.

---

## 9. What FEC scheme is recommended, and what net margins does it achieve?

**RS(255,239)** is the recommended FEC:
- 7.1% overhead → net data rate 99.2 Gb/s per lane
- Pre-FEC target: BER ≤ 1×10⁻³; post-FEC: < 10⁻¹²

**Net link margins after ~1.8–2.1 dB of penalties** (DCOC 0.5 dB, residual ISI 0.5–0.8 dB, PDL 0.5 dB, back-scatter 0.3 dB):

| Condition | Gross margin | Penalties | **Net margin** |
|---|---|---|---|
| Median (−8.62 dBm at PD) | +7.5 dB | 1.8–2.1 dB | **+5.4 to +5.7 dB** |
| −3σ (−11.36 dBm at PD) | +4.7 dB | 1.8–2.1 dB | **+2.6 to +2.9 dB** |

This is a **+1.6 to +1.8 dB improvement** over the prior architecture (TX 3-tap + RX FFE + separate CTLE), which achieved only +0.8 to +1.3 dB at −3σ. The improvement comes from (a) lower RX noise eliminating the separate CTLE active stage and (b) reduced residual ISI penalty from the better-matched TX FIR equalization.

KP4 RS(544,514) is now also viable at +1.9–2.2 dB net margin at −3σ, which would recover the 0.8 Gb/s net rate loss relative to 100 Gb/s. RS(255,239) remains preferred for robustness headroom, particularly given open SS corner uncertainties.

---

## 10. What is the highest-risk SS corner item, and what mitigations are proposed?

**Highest-risk item: TIA + embedded CTLE bandwidth falling below the Nyquist frequency (53.125 GHz) at the Slow-Slow process corner.**

At the SS corner, transistor gm is reduced, effective Rf feedback gain drops, and the T-coil resonance may shift. The expected BW degradation is 20–35%, bringing the embedded CTLE from the 55 GHz TT target down to an estimated **36–44 GHz at SS**:

```
SS BW estimate: 55 GHz × (1 − 0.30) = 38.5 GHz  (mid-range estimate)
Nyquist:        53.125 GHz
Shortfall:      ~14.6 GHz below Nyquist
```

This is critical because, **unlike the prior design where the RX FFE could absorb degraded channel bandwidth**, this no-RX-EQ architecture has no such fallback. A BW below Nyquist creates aliased ISI components that the TX FIR cannot pre-compensate, producing a BER floor regardless of power level.

**Proposed mitigations:**

1. **Voltage-programmable Rf:** At SS corner, reduce Rf from 600 Ω to ~450 Ω (per-chip register). BW scales as 1/Rf → 33% increase → recovers ~13 GHz (38.5 → 51 GHz). Noise increases by √(600/450) = 1.15× → ~0.5 dB penalty, acceptable within the +2.6 dB RS margin.

2. **Programmable T-coil capacitor bank:** Coarse-tune the peaking resonance to compensate for PVT shifts in gm, keeping the T-coil resonance aligned with the target frequency.

3. **Accept controlled ISI penalty:** If SS BW lands at 44 GHz (optimistic end of estimate), the combined channel BW and TX FIR residual produce ~1.5 dB additional ISI penalty. The −3σ RS FEC margin of +2.6 dB can absorb this and remain positive.

These mitigations can be combined. The most important immediate action is **SS corner simulation of the full TIA + T-coil + shunt peaking netlist** to quantify actual BW degradation before architecture sign-off.
