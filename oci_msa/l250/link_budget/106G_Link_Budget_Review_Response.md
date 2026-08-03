# Response to Architecture Review Feedback
**Document reviewed:** 106G_NRZ_CPO_Link_Budget.md (OCI Gen2, no-RX-EQ architecture)  
**Date:** 2026-08-03

---

## Overall

The assessment is accurate and fair. The "85–90% complete architecture document" framing is the right way to think about it — the technical content is solid but the editorial structure does not yet match the document's ambition. The criticisms are largely orthogonal to the content, which means the fixes are achievable without revisiting the analysis.

Accepted items are committed below with specific actions. Two items warrant brief discussion before committing.

---

## Accepted — will fix

### 1. Add executive summary (before Section 1)

A single-page summary stating the architecture choice, what enables it, what it delivers, and what must hold for it to be valid. The reviewer's draft is nearly perfect:

> *The architecture uses TX-only equalization enabled by a short-memory channel (τ ≈ 0.29 UI). A 3-tap TX FIR compensates the combined MRM and TIA response, eliminating RX FFE and DFE. A TIA with embedded passive CTLE extends bandwidth to ~55 GHz while avoiding the noise penalty of a separate active CTLE stage. This simplifies the receiver, improves estimated sensitivity by ~1 dB, and increases predicted RS(255,239) link margin by ~1.7 dB relative to the prior architecture. Architecture validity depends on MRM BW ≥ 60 GHz, TIA BW ≥ 53 GHz across PVT, C_in ≤ 46 fF, and TIA noise ≤ 3.0 μA_rms.*

This goes in immediately after the title block.

### 2. Add Assumed vs Verified table (early, in Section 1)

This is the most actionable feedback and directly addresses the document's biggest credibility risk. The 3.0 μA_rms noise figure appearing in a dozen tables reads like measured data. It is not. A table like the following should appear in Section 1 and be referenced whenever the value is used:

| Parameter | Value | Status | Source |
|---|---|---|---|
| MRM BW | ≥ 60 GHz | **Measured** | MRM S21 characterisation |
| OMA at PD (median/−3σ) | −8.62 / −11.36 dBm | **Measured** | `ocigen2gf_OMA_rollup_2026-07-13` |
| PD responsivity | 0.75 A/W | **Assumed** | GF PD spec pending |
| TIA + embedded CTLE BW | ~55 GHz | **Estimated** | Requires post-layout simulation |
| TIA input-referred noise | ~3.0 μA_rms | **Estimated** | Requires post-layout simulation |
| C_in (45 μm bump) | ~46 fF | **Modelled** | EMX extraction; GF PD geometry assumed |
| TX FIR coefficients | c₀=0.65, c₊₁=−0.25 | **Derived** | MMSE estimate; requires channel measurement |

### 3. Add architecture decision table

| Decision | Alternative(s) considered | Reason selected |
|---|---|---|
| 3-tap TX FIR (no RX FFE) | 2+1+2 RX FFE + 3-tap TX FIR | Channel ISI confined to ±1 UI (τ=0.29 UI); FFE unnecessary, adds noise via separate CTLE |
| Embedded CTLE (passive, TIA) | Separate active 1z2p CTLE stage | Passive T-coil eliminates active stage self-noise (~2 μA_rms); estimated −0.75 dB noise improvement |
| 45 μm bump pitch | 110 μm | 110 μm → C_in = 76 fF → embedded CTLE BW drops to ~36 GHz (below Nyquist) |
| RS(255,239) FEC | KP4, uncoded | −3σ uncoded fails; KP4 viable but only +1.9–2.2 dB margin; RS gives +2.6 dB headroom |
| MRM BW ≥ 60 GHz (hard requirement) | Relax to 40 GHz | No RX FFE fallback: ISI at +2 UI from 40 GHz MRM = 2.7% → BER floor |

### 4. Move key assumptions and kill conditions earlier

Currently buried in Section 10. A one-paragraph "Architecture Validity Envelope" after the executive summary, stating:

> *This architecture fails if any of the following conditions are violated: (1) MRM BW < 55 GHz at worst-case PVT, (2) TIA embedded CTLE BW < 53 GHz at SS corner, (3) C_in > 55 fF (110 μm bump or C_PD larger than assumed), (4) TIA noise > 4.0 μA_rms at worst-case corner.*

This tells a reviewer exactly what to challenge before they read a single equation.

### 5. Reduce derivation density in the main body

Commit to moving the following into appendices:
- Full ISI exponential decay table and derivation (§5.1 Steps 2–4)
- TX FIR Nyquist frequency response derivation (§5.2 W_FIR calculation)
- DCOC threshold shift derivation (§5.5)
- RIN noise calculation (§5.7)
- Full CPO optical loss element-by-element table (§7.1 — keep summary row only in main body)

Main body retains only the results and conclusions. Estimated reduction: ~30–35% of body length.

### 6. Reduce repetition

"55 GHz", "no RX FFE", and "MRM BW ≥ 60 GHz (hard requirement)" each appear 7–10 times. Fix: define each once (in the executive summary and the relevant section), then cross-reference. Mechanical edit but material improvement.

---

## Partial acceptance — needs discussion

### Circuit-level topology detail

The reviewer is correct that architecture readers do not need the inverter chain + T-coil + shunt peaking schematic sketch. However, the embedded CTLE topology is described there for one specific reason: **the noise estimate of 3.0 μA_rms depends entirely on whether the BW extension is passive (T-coil) or active (gain stage).** That distinction is architectural, not implementational.

Proposed resolution: keep one sentence stating the topology class ("passive inductive extension, no active gain stage") and its implication ("no transistor self-noise added"), move all circuit detail to a new Appendix D ("TIA Circuit Topology Notes").

### Figures

Completely valid — the absence of block diagrams is the document's most obvious gap. Markdown limits this to ASCII art, but that is better than nothing. Committed additions:

1. System block diagram (annotated signal chain with power levels at each node)
2. Noise budget waterfall (contributions to total i_n_rms)
3. ISI decay plot: ISI amplitude vs. symbol index for MRM, TIA, combined, after TX FIR
4. Jitter budget pie (DJ breakdown by source)

These would be placeholder ASCII figures in the markdown version, with a note indicating where rendered figures should be inserted in the formal document.

---

## Revision plan

| Action | Scope | Priority |
|---|---|---|
| Add executive summary | New ½-page section | High — do first |
| Add Assumed vs Verified table | New table in §1 | High — changes how document reads |
| Add architecture decision table | New section after §2 | High |
| Add architecture validity envelope | New callout box after exec summary | High |
| Move derivations to appendices | Edit §5.1, §5.2, §5.5, §5.7, §7.1 | Medium |
| Reduce repetition | Mechanical edit, document-wide | Medium |
| Add ASCII block diagrams | 4 new figures | Medium |
| Move circuit detail to Appendix D | Edit §7.4 | Low |
