# TX Electrical Jitter Budget at TP1 — First-Principles Derivation

**Companion document to `architecture_spec.md`** (L250 PMA, 106.25 Gbps NRZ optical link)

**Status:** draft — kept separate for now; to be folded into the architecture spec after review
**Date:** 2026-08-21

**Why this document exists.** The architecture spec (§2) adopts the IEEE P802.3dj D3.1 jitter triplet (`JHRMS`, `EOJ03`, `JH4u`, Table 179-7) as TP1 design targets, but dj deliberately defines **no dual-Dirac RJ/DJ split, no `DDJ = DCD + ISI` sub-allocation, no BUJ, and no total-jitter-at-BER metric** — its methodology isolates clock jitter and pushes pattern-dependent closure into a voltage-domain ratio, and every dj limit is anchored to RS-FEC operation at pre-FEC BER 2.4E-4. This link commits to **raw BER < 1e-12, FEC-free** (spec §1-3), a concept outside dj's framework. The decomposed jitter budget the design engineers need at that operating point therefore cannot be sourced from any standard and is derived here from first principles. All quantities are defined at **TP1**, the electrical input to the MRM modulator (spec §A-1, Figure 2-1), with **UI = 9.412 ps** at 106.25 GBd.

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
| Phase interpolator (DNL + intrinsic) | 70 | 5-bit PI class, §5-8 of the spec (`TBD_analog_design`) |
| Serializer / final 2:1 mux | 40 | (`TBD_analog_design`) |
| **RSS total** | **≈ 142 fs rms** | $\sqrt{100^2+60^2+70^2+40^2}$ |

$$
\boxed{\,\sigma_{RJ} \le 0.011\ \mathrm{UI\ rms}\ (104\ \mathrm{fs})\,}
$$

**Allocation set by the dj `JH4u` ceiling, not by the chain build-up.** The spec's $\sigma_{RJ}$ allocation is bound by the tougher-spec rule (spec §2-3): at BUJ = 0.036 UI, meeting `JH4u` ≤ 0.118 UI pp requires $\sigma_{RJ} \le 0.011$ UI. The first-cut chain build-up above lands at ≈142 fs, 1.37× over this allocation: the chain must improve by ≈2.7 dB in integrated phase-noise power (e.g. a ≈72/45/50/30 fs re-partition, RSS ≈ 103 fs), and that re-partition is `TBD_analog_design`. This is the budget's binding design risk and carries the kill-or-confirm flag. Cross-check: dj `JHRMS` ≤ 0.023 UI rms is the standards analog (clock-only, slope-extrapolated) — the target is 52% inside it.

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

Evaluating with the spec's own hardware limits: the §3-2 rise/fall-mismatch limit $\Delta t_{rf} \le 0.35$ ps contributes $0.175\ \mathrm{ps} = 0.0186$ UI, and a duty-cycle-correction (DCC) loop holding $D = 50\% \pm 0.3\%$ contributes $0.006$ UI:

$$
DCD = 0.0186 + 0.006 = 0.0246\ \mathrm{UI} \;\Rightarrow\; \boxed{\,DCD \le 0.025\ \mathrm{UI\ pp}\ (0.235\ \mathrm{ps})\,}
$$

This lands exactly on dj `EOJ03` ≤ 0.025 UI — the derived internal allocation and the standards ceiling coincide, which is a useful sanity anchor, not a coincidence to rely on — and is consistent with the committed §3-2 `DCD ≤ 0.025 UI` value. DCC residual and $\Delta t_{rf}$ partitioning are `TBD_analog_design`.

FIR-included configuration (current baseline per the spec §3): the link budget books an additional ≈ 0.05 UI of **FIR slice-DCD** (tap-slice skew in the 3-tap analog TX FIR, `OCI_Link_Budget_Summary.md` §5). This is carried as a separate adder in Section 6, zero in the no-FIR (removal-study) configuration.

---

## 4. ISI jitter — settling model

Model the driver + 150 fF load (spec §3-3) as a first-order system with time constant τ; the 20–80% transition time is $t_{2080} = \tau \ln 4 = 1.386\,\tau$. For a rising edge whose starting voltage depends on history, the signal is $v(t) = 1 - (1 - V_0)e^{-t/\tau}$ (normalized ±1 swing). A fully settled start gives $V_0 = -1$ and crossing at $t^* = \tau\ln 2$; a start only one UI after the previous transition gives $V_0 = -1 + 2e^{-T/\tau}$ and an early crossing. The displacement for run length $k$ is $\tau\, e^{-kT/\tau}$ to first order, and the worst-case peak-to-peak ISI jitter over all run lengths (e.g. exercised by PRBS31) is the geometric sum

$$
ISI_{pp} \approx \tau \cdot \frac{e^{-T/\tau}}{1 - e^{-T/\tau}}, \qquad T = UI = 9.412\ \mathrm{ps}.
$$

Evaluated at the three §3-2 transition-time corners:

| 20–80% edge (§3-2) | τ (ps) | $ISI_{pp}$ (ps) | $ISI_{pp}$ (UI) |
|---|---|---|---|
| 3.3 ps (0.35 UI, fast) | 2.38 | 0.047 | 0.005 |
| 3.6 ps (0.38 UI, typical) | 2.60 | 0.071 | 0.008 |
| 4.0 ps (0.42 UI, hard max) | 2.89 | 0.115 | **0.012** |

The allocation must hold at the slowest edge the design is allowed to ship:

$$
\boxed{\,ISI \le 0.012\ \mathrm{UI\ pp}\ (0.113\ \mathrm{ps})\,} \quad \text{(set by the 4.0 ps hard-max corner)}
$$

At the typical 3.6 ps edge the first-order model predicts 0.008 UI. Remaining headroom is for second-order response, microbump reflections, and $C_{PN}(V)$ (spec §7-3). Validation against extracted two-pole fits is `TBD_from_sim_sweep`.

---

## 5. Bounded uncorrelated jitter BUJ — crosstalk slew model

A data-uncorrelated voltage perturbation $V_x$ at the crossing converts to timing error through the edge slew rate: $\Delta t = 2V_x/SR$ peak-to-peak (the aggressor can push either direction). The mid-swing slew rate of an edge with 20–80% time $t_{2080}$ over swing $V_{pp}$ is approximately $SR \approx 0.6\,V_{pp}/t_{2080}$. Worst case (minimum swing 2.0 Vppd, hard-max 4.0 ps edge): $SR = 0.300$ V/ps.

Allocating

$$
\boxed{\,BUJ \le 0.036\ \mathrm{UI\ pp}\ (0.339\ \mathrm{ps})\,}
$$

bounds the tolerable aggressor sum at the crossing to $V_x \le SR \cdot \Delta t/2 = 51$ mV — i.e. **≤ 2.5% total coupling** from all simultaneously switching WDM lanes plus supply-coupled spurs, at the worst-case corner (63 mV / 2.5% at the typical 3.6 ps / 2.5 V point). Extracted-crosstalk verification against this coupling bound is `TBD_from_sim_sweep`; periodic (supply-spur) jitter is included inside this allocation rather than budgeted separately.

---

## 6. Assembly: DJ, TJ at BER 1e-12, and sensitivity

$$
DJ_{\delta\delta} = DCD + ISI + BUJ = 0.025 + 0.012 + 0.036 = 0.073\ \mathrm{UI\ pp}
$$

| Configuration | $DJ_{\delta\delta}$ (UI pp) | $\sigma_{RJ}$ (UI rms) | $TJ(10^{-12}) = DJ + 14.07\,\sigma$ | TJ (ps) |
|---|---|---|---|---|
| **FIR-included (+0.05 UI slice-DCD) — current baseline** | **0.123** | **0.011** | **0.278 UI** | **2.61** |
| No-FIR (removal-study configuration) | 0.073 | 0.011 | 0.228 UI | 2.14 |

Horizontal eye remaining at TP1 at BER 1e-12: $1 - 0.278 = 0.722$ UI = 6.80 ps (FIR baseline); $0.772$ UI = 7.27 ps (no-FIR).

**Sensitivity.** $\partial TJ/\partial\sigma_{RJ} = 2Q = 14.1$: every 10 fs of RMS clock jitter costs 141 fs of eye at 1e-12, while bounded terms trade 1:1. RJ is by far the strongest lever in this budget — clock-chain phase noise, not edge rate, is where design effort buys the most margin. This is why σ_RJ carries its own kill-or-confirm flag.

**Eye-mask input.** The §3-4 mask half-closure coordinate follows directly: $X_1 = TJ/2 = 0.139$ UI (FIR baseline); $0.114$ UI (no-FIR).

---

## 7. Cross-checks against the adopted dj metrics

| dj metric (spec §2) | dj limit | This budget's analog | Status |
|---|---|---|---|
| `JHRMS` | ≤ 0.023 UI rms | $\sigma_{RJ} \le 0.011$ UI rms | Consistent — 52% inside the ceiling |
| `EOJ03` | ≤ 0.025 UI pp | $DCD \le 0.025$ UI pp | Coincident by derivation (§3) |
| `JH4u` | ≤ 0.118 UI pp | clock-visible jitter at 1E-4: $BUJ + 2\,Q(10^{-4})\,\sigma_{RJ} = 0.036 + 0.082 = 0.118$ UI | Coincident — $\sigma_{RJ}$ sized to the ceiling (tougher-spec rule) |

$\sigma_{RJ}$ is bound by the tougher-spec rule (spec §2-3): the JH family excludes data-correlated jitter, so its internal analog is BUJ plus the RJ tail at 1E-4; at the fixed BUJ = 0.036 UI, landing exactly on `JH4u` = 0.118 UI requires $\sigma_{RJ} \le$ 0.011 UI (104 fs), the budget's binding allocation. The consequence lives in §2: the first-cut clock-chain build-up (142 fs) does not fit this allocation and must be re-partitioned — the remaining kill-or-confirm (`TBD_from_sim_sweep`).

---

## 8. Verification methodology at TP1

TP1 is unprobeable (spec §2 note (c)); all verification is extracted-netlist simulation, on-die instrumentation, and test-vehicle correlation.

1. **TIE extraction.** Transient simulation with the extracted driver + 150 fF MRM-plus-pad load, PRBS13 and PRBS31, all corners; record time-interval error of each differential mid-level crossing at TP1 against the ideal serializer clock (same folding convention as the §3-4 mask — recovered-clock alignment prohibited).
2. **DDJ separation.** Average the waveform per pattern context (e.g. 5-bit history); crossing spread of the averaged waveforms = DDJ; even/odd separation within it = DCD, remainder = ISI. Compare against Sections 3–4.
3. **BUJ/PJ separation.** With aggressor lanes toggling and victim pattern fixed, the added non-Gaussian TIE is BUJ; spectral lines identify supply-coupled PJ. Compare against the Section 5 coupling bound.
4. **RJ and TJ extrapolation.** Fit the Gaussian tails of the TIE histogram (dual-Dirac fit) to extract σ_RJ and $DJ_{\delta\delta}$; extrapolate to $10^{-12}$ via the Section 1 Q-table — direct simulation of 1e12 bits is not feasible, Q-scale extrapolation is the committed convention (consistent with spec §1-3).

---

## 9. Summary — derived TX jitter requirements at TP1

| Quantity | Symbol | Requirement | Abs. @ 9.412 ps UI | Derivation |
|---|---|---|---|---|
| RMS random jitter | $\sigma_{RJ}$ | ≤ 0.011 UI rms | ≤ 104 fs | §2 — set by the dj `JH4u` ceiling (tougher-spec rule); the 142 fs first-cut chain build-up must be re-partitioned to close at 104 fs |
| Duty-cycle distortion | `DCD` | ≤ 0.025 UI pp | ≤ 0.235 ps | §3 duty + rise/fall model |
| ISI jitter | `ISI` | ≤ 0.012 UI pp | ≤ 0.113 ps | §4 settling model at the 4.0 ps hard-max edge |
| Bounded uncorrelated | `BUJ` | ≤ 0.036 UI pp | ≤ 0.339 ps | §5 crosstalk slew model (≤ 2.5% coupling at 2.0 Vppd / 4.0 ps) |
| Deterministic total | $DJ_{\delta\delta}$ | ≤ 0.123 UI pp FIR-included (baseline); ≤ 0.073 no-FIR | ≤ 1.16 / 0.69 ps | §6 linear sum |
| Total jitter at BER 1E-12 | `TJ` | ≤ 0.278 UI pp FIR-included (baseline); ≤ 0.228 no-FIR | ≤ 2.61 / 2.14 ps | §6, $TJ = DJ + 2Q\sigma$, $Q = 7.034$ |
| Eye-mask half-closure | $X_1$ | 0.139 UI FIR-included (baseline); 0.114 no-FIR | 1.31 / 1.07 ps | §6, $TJ/2$ |

The `JH4u` tension (§7) is resolved by the tougher-spec rule; the resulting 104 fs clock-chain requirement is the budget's binding kill-or-confirm.
