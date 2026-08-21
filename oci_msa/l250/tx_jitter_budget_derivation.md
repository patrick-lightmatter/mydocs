# TX Electrical Jitter Budget at TP1 — First-Principles Derivation

**Companion document to `architecture_spec.md`** (L250 PMA, 106.25 Gbps NRZ optical link)

**Status:** draft — kept separate for now; to be folded into the architecture spec after review
**Date:** 2026-08-21

**Why this document exists.** The architecture spec (§3-1) adopts the IEEE P802.3dj D3.1 jitter triplet (`JHRMS`, `EOJ03`, `JH4u`, Table 179-7) as TP1 design targets, but dj deliberately defines **no dual-Dirac RJ/DJ split, no `DDJ = DCD + ISI` sub-allocation, no BUJ, and no total-jitter-at-BER metric** — its methodology isolates clock jitter and pushes pattern-dependent closure into a voltage-domain ratio, and every dj limit is anchored to RS-FEC operation at pre-FEC BER 2.4E-4. This link commits to **raw BER < 1e-12, FEC-free** (spec §1-3), a concept outside dj's framework. The decomposed jitter budget the design engineers need at that operating point therefore cannot be sourced from any standard and is derived here from first principles. All quantities are defined at **TP1**, the electrical input to the MRM modulator (spec §2-1, Figure 3-1), with **UI = 9.412 ps** at 106.25 GBd.

---

## 1. First principles: jitter taxonomy and the dual-Dirac model

### 1-1 Taxonomy

Total timing error at the TP1 mid-level crossing decomposes by physical origin:

| Term | Nature | Physical origin |
|---|---|---|
| `RJ` (σ_RJ) | Unbounded, Gaussian | Thermal/flicker phase noise of the PLL, clock distribution, phase interpolator, serializer |
| `DCD` | Bounded, data-correlated | Half-rate-clock duty-cycle error; rise/fall delay mismatch |
| `ISI` | Bounded, data-correlated | Finite bandwidth: incomplete settling of prior symbols shifts the crossing |
| `BUJ` | Bounded, data-uncorrelated | Crosstalk from adjacent WDM lanes; supply-coupled periodic jitter |

$$
DDJ = DCD + ISI, \qquad DJ_{\delta\delta} = DDJ + BUJ
$$

Bounded terms add linearly (worst-case alignment of bounded distributions); Gaussian terms add in RSS. This is the worst-case-additive convention: it is pessimistic against convolution of the true bounded PDFs, which is the correct direction for a sign-off budget.

### 1-2 The dual-Dirac model, derived

The measured jitter PDF is the convolution of the bounded DJ PDF with the Gaussian RJ PDF. The dual-Dirac approximation replaces the bounded PDF with two Dirac impulses separated by $DJ_{\delta\delta}$, so each eye edge contributes a Gaussian of width σ_RJ centered $DJ_{\delta\delta}/2$ inside the ideal edge. The probability that an edge intrudes a distance $t$ past its Dirac center is the Gaussian tail $\tfrac{1}{2}\mathrm{erfc}\!\left(\tfrac{t}{\sigma\sqrt{2}}\right)$. Setting this equal to the target BER defines the Q-factor,

$$
\mathrm{BER} = \tfrac{1}{2}\,\mathrm{erfc}\!\left(\tfrac{Q}{\sqrt{2}}\right),
$$

and the total jitter opening consumed at that BER is the two edges' Dirac separation plus a $Q\sigma$ tail on each side:

$$
\boxed{\,TJ(\mathrm{BER}) = DJ_{\delta\delta} + 2\,Q(\mathrm{BER})\,\sigma_{RJ}\,}
$$

| BER | $Q$ |
|---|---|
| 1E-4 | 3.719 |
| 2.4E-4 (dj pre-FEC anchor) | 3.49 |
| 1E-8 | 5.612 |
| **1E-12 (internal spec)** | **7.034** |

Convention note: this uses transition density ρ = 1 (every UI has an edge at risk), the conservative choice and the same one used in `OCI_Link_Budget_Summary.md`. A ρ = 0.5 convention (random data) would lower $Q(10^{-12})$ to 6.94 — a 1.3% relaxation not worth the bookkeeping.

---

## 2. Random jitter σ_RJ — clock-chain build-up

RJ at TP1 is the integrated phase noise of the clock generation and distribution chain, converted to time by $\sigma_t = \phi_{rms}/(2\pi f_{clk})$. Independent Gaussian sources RSS:

| Contributor | Allocation (fs rms) | Basis |
|---|---|---|
| TX PLL (integrated 4 MHz – f_baud/2; the CRU/CDR high-pass removes tracked LF jitter) | 100 | State-of-the-art 53.125 GHz LC-PLL class (`TBD_analog_design`) |
| Clock distribution buffers | 60 | Supply-noise-limited (`TBD_analog_design`) |
| Phase interpolator (DNL + intrinsic) | 70 | 5-bit PI class, §6-8 of the spec (`TBD_analog_design`) |
| Serializer / final 2:1 mux | 40 | (`TBD_analog_design`) |
| **RSS total** | **≈ 142 fs rms** | $\sqrt{100^2+60^2+70^2+40^2}$ |

$$
\boxed{\,\sigma_{RJ} \le 0.015\ \mathrm{UI\ rms}\ (141\ \mathrm{fs})\,}, \qquad \text{fallback } 0.018\ \mathrm{UI}\ (169\ \mathrm{fs})
$$

The 0.018 UI fallback is retained because the 141 fs chain build-up is aggressive (flagged **low confidence** / kill-or-confirm in the link budget); Section 6 shows what the fallback costs. Cross-check: dj `JHRMS` ≤ 0.023 UI rms is the standards analog (clock-only, slope-extrapolated) — our target is 35% inside it.

---

## 3. Duty-cycle distortion DCD

The serializer's final 2:1 mux is clocked at half rate (53.125 GHz), so a clock duty cycle $D \ne 50\%$ makes even/odd bit widths alternate: widths are $2D \cdot UI$ and $2(1-D) \cdot UI$, giving an even–odd crossing displacement of

$$
DCD_{duty} = |2D - 1| \cdot UI .
$$

Independently, a differential rise/fall time mismatch $\Delta t_{rf} = |t_r - t_f|$ shifts the mid-level crossing by half the mismatch on alternating edge polarities:

$$
DCD_{rf} \approx \Delta t_{rf}/2 .
$$

Evaluating with the spec's own hardware limits: the §4-4 rise/fall-mismatch limit $\Delta t_{rf} \le 0.35$ ps contributes $0.175\ \mathrm{ps} = 0.0186$ UI, and a duty-cycle-correction (DCC) loop holding $D = 50\% \pm 0.3\%$ contributes $0.006$ UI:

$$
DCD = 0.0186 + 0.006 = 0.0246\ \mathrm{UI} \;\Rightarrow\; \boxed{\,DCD \le 0.025\ \mathrm{UI\ pp}\ (0.235\ \mathrm{ps})\,}
$$

Two observations. **(i)** This lands exactly on dj `EOJ03` ≤ 0.025 UI — the derived internal allocation and the standards ceiling coincide, which is a useful sanity anchor, not a coincidence to rely on. **(ii)** The interim §4-4 value `DCD ≤ 0.015 UI` is **internally inconsistent** with the §4-4 $\Delta t_{rf} \le 0.35$ ps limit (whose crossing shift alone is 0.0186 UI); this derivation resolves the inconsistency in favor of 0.025 UI. DCC residual and $\Delta t_{rf}$ partitioning are `TBD_analog_design`.

FIR-retained option only: the link budget books an additional ≈ 0.05 UI of **FIR slice-DCD** (coefficient-slice skew in the 3-tap FIR-DAC, `OCI_Link_Budget_Summary.md` §5). This is carried as a separate adder in Section 6, zero in the recommended no-FIR baseline.

---

## 4. ISI jitter — settling model

Model the driver + 60 fF load as a first-order system with time constant τ; the 20–80% transition time is $t_{2080} = \tau \ln 4 = 1.386\,\tau$. For a rising edge whose starting voltage depends on history, the signal is $v(t) = 1 - (1 - V_0)e^{-t/\tau}$ (normalized ±1 swing). A fully settled start gives $V_0 = -1$ and crossing at $t^* = \tau\ln 2$; a start only one UI after the previous transition gives $V_0 = -1 + 2e^{-T/\tau}$ and an early crossing. The displacement for run length $k$ is $\tau\, e^{-kT/\tau}$ to first order, and the worst-case peak-to-peak ISI jitter over all run lengths (e.g. exercised by PRBS31) is the geometric sum

$$
ISI_{pp} \approx \tau \cdot \frac{e^{-T/\tau}}{1 - e^{-T/\tau}}, \qquad T = UI = 9.412\ \mathrm{ps}.
$$

Evaluated at the three §4-4 transition-time corners:

| 20–80% edge (§4-4) | τ (ps) | $ISI_{pp}$ (ps) | $ISI_{pp}$ (UI) |
|---|---|---|---|
| 3.3 ps (0.35 UI, fast) | 2.38 | 0.047 | 0.005 |
| 4.2 ps (0.45 UI, typical) | 3.03 | 0.142 | 0.015 |
| 5.6 ps (0.60 UI, hard max) | 4.04 | 0.435 | **0.046** |

The allocation must hold at the slowest edge the design is allowed to ship:

$$
\boxed{\,ISI \le 0.045\ \mathrm{UI\ pp}\ (0.424\ \mathrm{ps})\,} \quad \text{(set by the 5.6 ps hard-max corner)}
$$

At the typical 4.2 ps edge the first-order model predicts only 0.015 UI — the ≈ 3× headroom absorbs what the single-pole model does not capture: second-order response and group-delay ripple, reflections at the unterminated capacitive microbump, and the MRM's voltage-dependent junction capacitance ($C_{PN}(V)$, spec §8-3). Validation against extracted two-pole fits is `TBD_from_sim_sweep`.

---

## 5. Bounded uncorrelated jitter BUJ — crosstalk slew model

A data-uncorrelated voltage perturbation $V_x$ at the crossing converts to timing error through the edge slew rate: $\Delta t = 2V_x/SR$ peak-to-peak (the aggressor can push either direction). The mid-swing slew rate of an edge with 20–80% time $t_{2080}$ over swing $V_{pp}$ is approximately $SR \approx 0.6\,V_{pp}/t_{2080}$. Worst case (minimum swing 2.0 Vppd, hard-max 5.6 ps edge): $SR = 0.214$ V/ps.

Allocating

$$
\boxed{\,BUJ \le 0.036\ \mathrm{UI\ pp}\ (0.339\ \mathrm{ps})\,}
$$

bounds the tolerable aggressor sum at the crossing to $V_x \le SR \cdot \Delta t/2 = 36$ mV — i.e. **≤ 1.8% total coupling** from all simultaneously switching WDM lanes plus supply-coupled spurs, at the worst-case corner (60 mV / 2.4% at the typical 4.2 ps / 2.5 V point). Extracted-crosstalk verification against this coupling bound is `TBD_from_sim_sweep`; periodic (supply-spur) jitter is included inside this allocation rather than budgeted separately.

---

## 6. Assembly: DJ, TJ at BER 1e-12, and sensitivity

$$
DJ_{\delta\delta} = DCD + ISI + BUJ = 0.025 + 0.045 + 0.036 = 0.106\ \mathrm{UI\ pp}
$$

| Configuration | $DJ_{\delta\delta}$ (UI pp) | $\sigma_{RJ}$ (UI rms) | $TJ(10^{-12}) = DJ + 14.07\,\sigma$ | TJ (ps) |
|---|---|---|---|---|
| **No-FIR baseline (recommended)** | **0.106** | **0.015** | **0.317 UI** | **2.98** |
| No-FIR, RJ fallback | 0.106 | 0.018 | 0.359 UI | 3.38 |
| FIR-retained (+0.05 UI slice-DCD) | 0.156 | 0.015 | 0.367 UI | 3.45 |
| FIR-retained, RJ fallback | 0.156 | 0.018 | 0.409 UI | 3.85 |

Horizontal eye remaining at TP1 at BER 1e-12 (baseline): $1 - 0.317 = 0.683$ UI = 6.43 ps.

**Sensitivity.** $\partial TJ/\partial\sigma_{RJ} = 2Q = 14.1$: every 10 fs of RMS clock jitter costs 141 fs of eye at 1e-12, while bounded terms trade 1:1. RJ is by far the strongest lever in this budget — clock-chain phase noise, not edge rate, is where design effort buys the most margin. This is why σ_RJ carries its own kill-or-confirm flag.

**Eye-mask input.** The §4-5 mask half-closure coordinate follows directly: $X_1 = TJ/2 = 0.158$ UI (baseline). This supersedes both the provisional $X_1 = 0.14$ UI (CEI-era) and the 0.176 UI implied by the link budget's FIR-retained TJ = 0.351 UI, once adopted; the mask geometry re-run (`tx_eye_mask.py`) should use the configuration actually being signed off.

---

## 7. Cross-checks against the adopted dj metrics

| dj metric (spec §3-1) | dj limit | This budget's analog | Status |
|---|---|---|---|
| `JHRMS` | ≤ 0.023 UI rms | $\sigma_{RJ} \le 0.015$ UI rms | Consistent — 35% inside the ceiling |
| `EOJ03` | ≤ 0.025 UI pp | $DCD \le 0.025$ UI pp | Coincident by derivation (§3) |
| `JH4u` | ≤ 0.118 UI pp | clock-visible jitter at 1E-4: $BUJ + 2\,Q(10^{-4})\,\sigma_{RJ} = 0.036 + 0.112 = 0.148$ UI | **Tension** — see below |

The `JH4u` comparison is the one open item: the JH family excludes data-correlated jitter, so its internal analog is BUJ plus the RJ tail at 1E-4, which exceeds the dj ceiling by 0.03 UI. Meeting dj's JH4u-class clock cleanliness would require $\sigma_{RJ} \le 0.011$ UI (104 fs) at BUJ = 0.036 UI, or a tighter BUJ. Since TP1 is a design-verification point, not a dj compliance point (spec §3-1 note (c)), this is **informative**, but it flags that this budget describes a transmitter that would not pass dj's clock-jitter screen — worth a conscious decision (kill-or-confirm, `TBD_from_sim_sweep`).

---

## 8. Verification methodology at TP1

TP1 is unprobeable (spec §3-1 note (c)); all verification is extracted-netlist simulation, on-die instrumentation, and test-vehicle correlation.

1. **TIE extraction.** Transient simulation with the extracted driver + 60 fF MRM-plus-pad load, PRBS13 and PRBS31, all corners; record time-interval error of each differential mid-level crossing at TP1 against the ideal serializer clock (same folding convention as the §4-5 mask — recovered-clock alignment prohibited).
2. **DDJ separation.** Average the waveform per pattern context (e.g. 5-bit history); crossing spread of the averaged waveforms = DDJ; even/odd separation within it = DCD, remainder = ISI. Compare against Sections 3–4.
3. **BUJ/PJ separation.** With aggressor lanes toggling and victim pattern fixed, the added non-Gaussian TIE is BUJ; spectral lines identify supply-coupled PJ. Compare against the Section 5 coupling bound.
4. **RJ and TJ extrapolation.** Fit the Gaussian tails of the TIE histogram (dual-Dirac fit) to extract σ_RJ and $DJ_{\delta\delta}$; extrapolate to $10^{-12}$ via the Section 1 Q-table — direct simulation of 1e12 bits is not feasible, Q-scale extrapolation is the committed convention (consistent with spec §1-3).

---

## 9. Summary — derived TX jitter requirements at TP1

| Quantity | Symbol | Requirement | Abs. @ 9.412 ps UI | Derivation |
|---|---|---|---|---|
| RMS random jitter | $\sigma_{RJ}$ | ≤ 0.015 UI rms (fallback 0.018) | ≤ 141 fs (169) | §2 clock-chain RSS |
| Duty-cycle distortion | `DCD` | ≤ 0.025 UI pp | ≤ 0.235 ps | §3 duty + rise/fall model |
| ISI jitter | `ISI` | ≤ 0.045 UI pp | ≤ 0.424 ps | §4 settling model at the 5.6 ps hard-max edge |
| Bounded uncorrelated | `BUJ` | ≤ 0.036 UI pp | ≤ 0.339 ps | §5 crosstalk slew model (≤ 1.8% coupling) |
| Deterministic total | $DJ_{\delta\delta}$ | ≤ 0.106 UI pp (no-FIR); ≤ 0.156 FIR-retained | ≤ 1.00 / 1.47 ps | §6 linear sum |
| Total jitter at BER 1E-12 | `TJ` | ≤ 0.317 UI pp (baseline) | ≤ 2.98 ps | §6, $TJ = DJ + 2Q\sigma$, $Q = 7.034$ |
| Eye-mask half-closure | $X_1$ | 0.158 UI (baseline) | 1.49 ps | §6, $TJ/2$ |

**Supersessions on integration** (deltas vs. the interim `architecture_spec.md` §4-4 values): `DCD` 0.015 → **0.025 UI** (resolves the $\Delta t_{rf}$ inconsistency, §3); `DDJ` 0.060 → **0.070 UI** (= DCD + ISI); $DJ_{\delta\delta}$ 0.11 → **0.106 UI** (no-FIR — effectively confirmed); `TJ` 0.351 → **0.317 UI** baseline (the 0.351 was FIR-retained with DCD = 0.015; the FIR-retained value here is 0.367); $X_1$ 0.14 → **0.158 UI**. σ_RJ (0.015/0.018) and BUJ (0.036) are confirmed unchanged. The open `JH4u` tension (§7) should be dispositioned before these values are promoted into §4-4.
