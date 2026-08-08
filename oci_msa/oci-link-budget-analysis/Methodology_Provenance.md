# Calculation Methodology Provenance

Companion to `OCI_Link_Budget_Report.md`. Every calculation methodology used in the
budget is classified into one of three tiers:

- **Tier 1 — from a reference.** The formula/method is taken directly from a standard,
  textbook, or published presentation. Trust level: the method itself needs no review;
  only the input parameters do.
- **Tier 2 — hybrid.** Standard building blocks, but the specific assembly, accounting
  convention, or implementation recipe was constructed for this project. Review the
  assembly, not the blocks.
- **Tier 3 — derived here.** Project-specific derivations, empirical fits, or modeling
  decisions original to this analysis. These deserve the most scrutiny.

References are cited by the short names of Appendix B of the main report
(`lecture 4` = `food/lecture4_ee721_rx_analysis.pdf`, etc.). "Where" columns point to
the implementing script and the report section.

---

## Tier 1 — taken from a reference

| Method | Formula / model | Reference | Where |
|---|---|---|---|
| BER ↔ Q mapping | $\mathrm{BER} = \tfrac12\,\mathrm{erfc}(Q/\sqrt2)$; $Q = 7.035$ at $10^{-12}$ | Personick; lecture 4 | report §2.2 |
| Amplifier-noise sensitivity floor | $\mathrm{OMA_{sens}} = 2\,Q\,i_n/R$ | Personick; lecture 4 | `common.floor_dbm`, §2.3 |
| Noise-equivalent-bandwidth integral | $\int \lvert H(f)/H_0\rvert^2\,df$ ("Personick integral") — retained for the §4.3 noise-power scaling law and CTLE noise enhancement, **no longer** the budget's $B_n$ (see Tier 2 item 2.7) | lecture 4 | `common.load_tia_settings` |
| Single-pole noise-bandwidth factor | $B_n = (\pi/2) f_{3\mathrm{dB}} \approx 1.57 \times$; the budget rounds to $1.5\times$ | classical NEB result (Säckinger-style texts) | §2.3, Tier 2 item 2.7 |
| Q-solve with signal-dependent noise | Level-dependent shot ($2qRP_LB_n$) and RIN ($\mathrm{RIN}\,B_n\,I_L^2$) on both rails; bisect OMA for $Q$ target | Säckinger-style Rx analysis; lectures 4, 7 | `common.rin_shot_penalty`, §2.6 |
| ER penalty structure | ER enters through rail powers $P_1 = \mathrm{OMA}\frac{E}{E-1}$, $P_0 = P_1 - \mathrm{OMA}$ in the Q-solve (OMA domain — no $\frac{E+1}{E-1}$ average-power factor) | lecture 7 | same Q-solve, §2.1/§2.6 |
| RIN $Q^2$ scaling and RIN BER floor | Penalty grows $\propto Q^2$; floor check $Q_{\max} = [\sqrt{\mathrm{RIN}B_n}(P_1{+}P_0)/\mathrm{OMA}]^{-1}$ | lecture 7 | script `02`, §2.6 |
| MPI penalty | Discounted upper bound $P = -10\log_{10}(1-x)$, $x = 4DS\frac{E}{E-1}$, $S$ = reflection-pair sum; $D = 0.5$ discount | Bhatt / King 802.3bs presentations (`food/bhatt_3bs_01a_0116`, `king_01a_0116_smf`) | `common.mpi_penalty`, §2.6 |
| Dual-Dirac total jitter | $TJ = DJ + 2\,Q\,\sigma_{RJ}$ | lecture 10 (EE720); MJSQ / Fibre Channel methodology, used in 802.3 and OIF-CEI budgets | `common.jitter_pp` (first half), §2.6 |
| Peak-distortion ISI criterion | Worst-case eye $= h_0 - \sum_{i\ne0}\lvert h_i\rvert$; penalty $-10\log_{10}(\mathrm{eye}/h_0)$ | Classical worst-case bound (peak-distortion criterion, Lucky et al.); standard in link budgets | `common.pp_of`, §2.4 |
| Chromatic dispersion channel model | Quadratic spectral phase $\exp(j\pi D_{\mathrm{disp}} L\lambda^2 f^2/c)$ | Standard fiber-optics; lecture 7 | script `02` `pulse_metrics`, §2.4 |
| Decision-threshold-offset penalty | $10\log_{10}(1+2\delta)$ for offset $\delta$ of half-swing | Säckinger-style penalty form; lecture 4 | scripts `02`–`04`, §2.6 |
| Dark-current penalty | $10\log_{10}\sqrt{1 + 2qI_{DK}B_n/i_n^2}$ (noise-addition form) | lecture 4 | script `02`, §2.6 |
| Eye-closure crosstalk penalty form | $-10\log_{10}(1-2\varepsilon)$ for relative aggressor amplitude $\varepsilon$ | Standard eye-closure penalty form | scripts `02`–`04`, §2.6 |
| Baseline-wander / LF-cutoff sizing | AC-coupling droop over an $N$-bit CID run sets $f_{LF}$ for a given eye-closure allowance | Standard AC-coupling analysis; lecture 4 CID discussion | script `05`, report §5 |
| Budget-structure template | Penalty-allocation framework, discrete-reflectance table structure, TDEC/SRS definitions | OCI MSA v1.0; IEEE P802.3dj D1.3 Cl. 180/181 | report §1, §3, Appendix A |
| Bessel-Thomson reference Rx | BT4 at 0.5 × baud as the TDEC reference filter | OCI MSA / IEEE TDEC method | `common.bessel4`, scripts `02`/`04` |

---

## Tier 2 — hybrid (standard blocks, project-specific assembly)

### 2.1 Jitter penalty recipe (`common.jitter_pp`; GEN1 variant in script `02`)

**Blocks:** dual-Dirac TJ (Tier 1) + peak-distortion eye (Tier 1).
**Assembly (ours):** convert TJ into a worst-case sampling-phase offset of $\pm TJ/2$
from eye center, re-evaluate the peak-distortion vertical opening of the simulated
pulse response at that offset, and book
$-10\log_{10}[\min(\mathrm{eye}(-TJ/2),\mathrm{eye}(+TJ/2))/\mathrm{eye}(0)]$.
A closed eye at the offset returns "no finite penalty" and fails the scenario.

Textbook treatments typically approximate the jitter penalty from the waveform slope
at the sampling instant; the eye-re-evaluation used here captures curvature and
asymmetry of the actual equalized pulse but is not lifted from any standard.

*Known optimism (GEN1 only):* script `02`'s variant excludes post-cursors from the
offset eye, i.e. it assumes the DSP-SerDes DFE still cancels post-cursors perfectly at
the displaced sampling phase, whereas real DFE taps are trained at eye center. GEN2
(`common.jitter_pp` on the CTLE-equalized chain, no DFE) has no such assumption — all
cursors are counted.

*Sample-grid quantization:* at the default `Sim(BAUD)` oversampling (`os_r=32`), the
offset index used to sample the eye is `round(TJ/2 × os_r)`; two RJ/DJ scenarios whose
TJ differ by less than roughly one sample step (≈ 1.6% UI at os\_r=32) can round to the
same offset and report identical PP, masking small deltas. The GEN2 141 fs vs. 169 fs
CDR-fallback comparison (report §8) is affected by this and is re-evaluated at
`os_r=256` in script `04` to resolve the real +0.19 dB delta between the two RJ specs.

### 2.2 CD penalty as a delta of peak distortion (script `02`, `04`)

The quadratic-phase channel is Tier 1; booking the penalty as the *difference* between
the peak-distortion metric with and without dispersion (rather than a closed-form CD
penalty) is our accounting choice. It prevents double-counting the dispersion-free ISI
already booked in the ISI+EQ line.

### 2.3 CTLE optimization metric (`common.ctle_sweep`)

The 1-zero / 2-coincident-pole CTLE form and the concept of linear-equalizer noise
enhancement are standard. Our assembly: charge each candidate its rms noise gain over
the TIA-shaped (white-input) noise,
$\eta = \sqrt{\int\lvert H_{TIA}H_c\rvert^2 df / \int\lvert H_{TIA}\rvert^2 df}$, and
minimize $P_{\mathrm{ISI}} + 10\log_{10}\eta$ over a (zero, pole) grid. The
$10\log_{10}\eta$ charge is exact for the amplifier-noise-limited Q-solve (noise rms
scales the floor linearly); it slightly misprices the signal-dependent terms, which is
accepted as second-order.

### 2.4 Tx FIR optimization and de-emphasis charge (`common.opt_fir`)

The $-10\log_{10}(\sum_i w_i)$ de-emphasis cost under the peak-swing constraint
$\sum_i\lvert w_i\rvert = 1$ is standard SerDes Tx-FIR bookkeeping. Our assembly: joint
grid search (step 0.02–0.04) minimizing ISI penalty + de-emphasis cost, optionally
nested with the CTLE sweep for joint FIR+CTLE cells.

### 2.5 OMA-domain stack and TDEC accounting (report §2.1)

Building the budget in the OMA domain with a penalty stack is standard IEEE/MSA
practice. Two accounting choices are ours: (i) transmitter eye closure is booked
*inside* the ISI+EQ line (the pulse simulation contains the Tx filter) rather than as
a separate TDEC subtraction, avoiding double counting — except the GEN1 spec-minimum
closure where the spec's own TDEC-coupled OMA law is exercised; (ii) TDEC is applied
unscaled from its BER $2.4\times10^{-4}$ definition to the $10^{-12}$ target (its
deterministic content does not scale with Q — a flagged caveat, report §3.2).

### 2.6a Noise-integration-bandwidth convention (report §2.3, register row 23)

**Blocks:** the single-pole noise-equivalent-bandwidth factor $\pi/2 \times f_{3\mathrm{dB}}$
(Tier 1, rounded to 1.5×).
**Assembly (project decision, user-directed):** apply $B_n = 1.5 \times f_{3\mathrm{dB}}$
to all signal-dependent noise terms (shot, RIN, dark) and density↔rms conversions, for
both generations, *in place of* exact shape integrals of the signal transfer function.
Rationale: real receiver noise extends beyond the circuit's 3 dB point (the measured
family's $f^2$-dominated noise, §4.3), so shape integrals of clean model responses
(0.96× measured GEN1, 1.10× ideal Butterworth-2) understate a physical part's noise
bandwidth. The 1.5× rule is deliberately conservative; it costs ~0.33 dB on each
generation's stack versus the shape-integral accounting.

### 2.6 Pulse-response engine (`common.Sim`, report §2.4)

Single 1-UI rectangular pulse through the cascaded frequency response on a
32×-oversampled grid, with the sampling phase optimized for maximum eye
(`taps_of`). Each block (FFT-based propagation, UI-spaced tap extraction) is textbook
signal processing; sharing one engine across ISI, CD, and jitter so the three lines
are mutually consistent is our design decision.

---

## Tier 3 — derived in this project

### 3.1 TIA input-referral convention (single-ended p-leg)

$i_n = v_{n,\mathrm{out}} / Z_{T,\mathrm{peak\;SE\;p\text{-}leg}}$. This is our
conservative reading of the vendor model, which injects its noise target on the p-leg
only while the signal sees the differential gain. Kept for both generations for
comparability. `common.py` computes both conventions. (Report §2.3.)

### 3.2 Noise-versus-bandwidth scaling law (script `04`)

Empirical regression across the 152 measured settings decomposing input noise into
white + $f^2$-shaped terms (integrals $B_1 = \int\lvert H_n\rvert^2 df$,
$B_2 = \int f^2\lvert H_n\rvert^2 df$ in `load_tia_settings`). The finding that the
family is $f^2$-dominated ($R^2$ 0.87 vs 0.59 for white-only), and the consequent claim
that 53G-class parts cannot be re-tuned to GEN2 bandwidths within the noise ceiling, is
an original empirical result of this analysis.

### 3.3 Microbump model (report §2.4)

The EIC is bumped directly onto the PIC (unterminated direct drive), so the bump is
extra load capacitance. It is booked as a single lumped pole at an assumed effective
node impedance (placeholder 50 Ω; 25 fF → 127 GHz), conservative when the actual
driver-output / TIA-input impedance is lower. The circuit theory is elementary; the
modeling decision (lumped, not a transmission line; the impedance placeholder; 25 fF
budget) is ours and is flagged as a top risk in report §8.

### 3.4 Slice-DAC FIR linearity argument (report §2.5)

Derivation that three parallel two-level (limiting) driver slices with 1-UI delays
summing at the output node implement an *exact* linear FIR on NRZ data — slice
nonlinearity cannot corrupt tap accuracy because each slice is two-level. This
justifies using linear FIR math for the nonlinear driver. Ours.

### 3.5 Group-delay-ripple spec line (script `05`, report §5)

The ≤ 3 ps (~0.3 UI) GD-ripple requirement was derived from a measured setting that
passed all magnitude-domain screens but showed 12.5 ps of GD ripple (2–40 GHz),
producing an $h_{-1} \approx 0.48$ pre-cursor that a CTLE cannot remove. The diagnosis
method (re-simulate the measured complex TF, attribute the eye closure to phase) and
the resulting spec line are original to this analysis.

### 3.6 DC-restoration flattening of measured TFs (`common.tia_interp`)

Measured TIA magnitude below 2 GHz is held at its 2 GHz value with the extracted
bulk-delay phase preserved (keeps the response causal). This encodes the assumption
that a baseline-wander loop handles the AC-coupling droop; §5 converts it into an
explicit LF-cutoff requirement. The specific procedure is ours.

### 3.7 Noise-shape finding and spec mechanism (script `05`)

Result that $f^2$-shaped input noise of equal rms sees ≤ 0 dB extra post-CTLE penalty
versus white (the mild CTLE's poles sit where the $f^2$ noise lives), so the spec
enforces noise shape via a full-band rms limit plus a spot-density ceiling instead of a
post-CTLE allowance. Original analysis.

### 3.8 `verify_tia()` six-step compliance recipe (script `05`)

The pass/fail recipe (bandwidth gate, rms noise, spot density, peaking, GD ripple,
jitter-eye survival) on the standard TF+noise data format is our construction, built so
vendor deliverables can be screened mechanically.

### 3.9 Assumed penalty-line parameters

Not methodologies, but assumption sets original to this budget (labeled in report §7
and the `ASSUMPTIONS` dicts): crosstalk 20 dB isolation / +3 dB ΔOMA / 2 neighbors,
threshold offset 2.5%, jitter RJ/DJ splits per generation (including the 0.04 UI
slice-DCD term folded into GEN1-CPO/GEN2 DJ), CID = 72 bits, PD cap 30–40 fF.

**Rx OMA max / overload governing case (script `05`, report §5).** `RX_OMA_MAX_DBM =
−1.0` is a bare judgment call with no documented derivation from a Tx-OMA/link-IL
corner (unlike, e.g., the DC-handling line which is computed *from* it). An adversarial
review (Gemini) proposed an alternative +1.79 dBm / 1.13 mA$_{\mathrm{pp}}$ max-power
case (20.8 dB dynamic range) sourced from an external "parallel budget" that could not
be traced anywhere in this repo. Reviewed and retained −1 dBm on 2026-08-07 as the
governing case for the shared TIA macro, since no variant combining a higher max Tx
launch OMA with a lower minimum link IL than this report's documented −3.5 to −1.5 dBm
/ ~2.5–3 dB corners is on record. If such a variant is later confirmed to share this
TIA macro, its $\mathrm{OMA_{Tx,max}} - \mathrm{IL_{min}}$ should replace −1 dBm as the
ceiling, and the 696 µApp / 750 µA DCOC / 14 dB dynamic-range lines re-derived against
it — the same "shared macro must meet the union of variants" logic already applied to
the end-reflectance requirement (Tier 3, §3.9).

**TIA input-noise literature bracket (script `04`, report §4.4/§5, register row 22).**
The "2.5–5 µA at 55–65 GHz" range quoted for 100 GBd-class TIAs is an internal
engineering estimate assembled from the team's general awareness of the state of the
art at the time this budget was written; it is **not traceable to a specific cited
publication or datasheet**. Treat it as a plausibility check on the derived 4.0–4.5 µA
target-class number, not as independent corroborating evidence. If a defensible
citation is needed (e.g. for an external-facing spec), it should be sourced and
replaced before that use.

---

## Review priority

Tier 3 items 3.1–3.3 carry the most numerical leverage on the GEN2 conclusion (they set
the noise ceiling, the "can't re-tune 53G parts" claim, and the bump ISI charge).
Tier 2 item 2.1's GEN1 DFE-at-offset optimism is bounded (GEN1 closes with +0.60 dB
worst case) but worth knowing. All Tier 1 items are parameter-audit only.

---

## Appendix C — Executive-summary calculation walk-throughs

Worked arithmetic behind each headline number in the report's §1 GEN1/GEN2 summary
tables. Each entry names the methodology tier item it instantiates, the implementing
script, and the report section with the full context.

### C.1 GEN1 analytic receiver floor

Amplifier-noise sensitivity floor (Tier 1, $\mathrm{OMA_{sens}} = 2Qi_n/R$), calibrated
on the lowest-noise bandwidth-adequate measured TIA setting (`12211111`:
$i_n = 3.17\ \mu$A rms, $f_{3\mathrm{dB}} \approx 29.3$ GHz, ≥ 0.55× baud):

$$\mathrm{OMA_{floor}} = \frac{2 \times 7.035 \times 3.17\ \mu\mathrm{A}}{0.876\ \mathrm{A/W}}
= 50.9\ \mu\mathrm{W} = \mathbf{-12.93\ dBm}.$$

Script `02`; report §2.3, §3.1.

### C.2 GEN1 penalty stack (2.93 dB)

Sum of nine lines, each computed per the §2.6 formulas (Tier 1 forms, Tier 2 assembly);
inputs: ER 3.5 dB, $B_n = 1.5 \times 29.3 = 43.9$ GHz, $R = 0.876$ A/W, $Q = 7.035$.

| Line | dB | Arithmetic |
|---|---:|---|
| ER / shot | 0.18 | Q-solve (bisection on OMA) with level-dependent shot $2qRP_LB_n$ on both rails |
| RIN | 0.68 | Q-solve with $\sigma_{RIN,L} = RP_L\sqrt{10^{-13.8}\times 43.9\mathrm{e}9}$; the $Q^2$ scaling makes it 4.5× its 0.15 dB value at spec BER |
| MPI | 0.24 | see C.5 (−24 dB ends, ER 3.5, $D=0.5$) |
| ISI residual after EQ | 0.64 | unequalized taps: cursor 0.809, pre 0.111, post 0.205; DFE removes post → $-10\log_{10}[(0.809-0.111)/0.809]$ |
| CD | 0.01 | pulse-sim delta at +1.7 ps/nm gives 0.005; booked 0.01 |
| Jitter | 0.61 | $TJ = 0.10 + 2 \times 7.035 \times 0.010 = 0.241$ UI (4.5 ps); eye re-evaluated at $\pm TJ/2$ (Tier 2 item 2.1) |
| Crosstalk | 0.36 | $\varepsilon = 2 \times 10^{-20/10} \times 10^{+3/10} = 0.0399$; $-10\log_{10}(1-2\varepsilon)$ |
| Threshold offset | 0.21 | $10\log_{10}(1 + 2 \times 0.025)$ |
| Dark current | 0.00 | $10\log_{10}\sqrt{1 + 2q \times 1\mu\mathrm{A} \times 43.9\mathrm{e}9 / (3.17\mu\mathrm{A})^2} = 0.003$ |

Unrounded sum = **2.93 dB**. Script `02`; report §3.1.

### C.3 GEN1 required OMA at the receiver

Floor plus stack: $-12.93 + 2.93 = \mathbf{-10.00}$ dBm. Report §3.2.

### C.4 GEN1 closure margins

Margin = (Tx OMA − link IL − TDEC) − required OMA, with link IL 2.5 dB (500 m):

- **Spec-minimum Tx (+0.60 dB):** the spec's OMA-min law
  $\max(-5.5, -6.9 + \mathrm{TDEC})$ pins OMA − TDEC at −6.9 dBm for TDEC ≥ 1.4 dB, so
  both spec corners (TDEC 1.4 and 3.4 dB) land at $-6.9 - 2.5 = -9.40$ dBm at the Rx;
  margin $= -9.40 - (-10.00) = \mathbf{+0.60\ dB}$.
- **Realistic Tx (+2.30 dB):** $-3.2 - 2.5 - 2.0 = -7.70$ dBm at the Rx; margin
  $= -7.70 - (-10.00) = \mathbf{+2.30\ dB}$.

TDEC applied unscaled from its $2.4\times10^{-4}$ definition (Tier 2 item 2.5 caveat).
Script `02`; report §3.2.

### C.5 MPI reflectance finding

Bhatt/King discounted upper bound (Tier 1): $P = -10\log_{10}(1-x)$,
$x = 4DS\frac{E}{E-1}$, with 2 ends ($R_t = R_r$), $n = 4$ connectors at
$R_c = 10^{-3.5}$, and
$S = \sqrt{R_tR_r} + n\sqrt{R_tR_c} + n\sqrt{R_rR_c} + \frac{n(n-1)}{2}R_c$.

- **Ends at −19 dB (spec):** $S = 0.0126 + 2 \times 0.0080 + 0.0019 = 0.0304$; at
  ER 3.5 dB ($E/(E{-}1) = 1.807$), $D = 0.5$: $x = 0.110$ →
  $P = \mathbf{0.51\ dB}$ (2.5× the 0.2 dB allocation; $D = 1$ worst case: 1.08 dB).
- **Ends at −24 dB (adopted):** $S = 0.0040 + 2 \times 0.0045 + 0.0019 = 0.0149$;
  GEN1 (ER 3.5): $x = 0.0537$ → $P = \mathbf{0.24\ dB}$. GEN2 (ER 4.5,
  $E/(E{-}1) = 1.550$): $x = 0.0460$ → $P = \mathbf{0.205\ dB}$.

The ≤ −24 dB end requirement is enforced for both generations (shared product line).
`common.mpi_penalty`; report §2.6, §3.3.

### C.6 GEN2 rate scaling

Direct arithmetic: UI $= 1/106.25\ \mathrm{GBd} = 9.412$ ps (half of GEN1's 18.82 ps);
Nyquist $= 106.25/2 = 53.125$ GHz (double GEN1's 26.56 GHz). Report §4.

### C.7 GEN2 derived TIA class

Four independent derivations, all in script `05` (report §5):

- **$f_{3\mathrm{dB}}$ 50–64 GHz:** total sensitivity (white-scaled floor + ISI+EQ +
  RIN at $B_n = 1.5f_{3\mathrm{dB}}$) swept vs $f_{3\mathrm{dB}}$ is flat at
  −8.3/−8.4 dBm across 45–64 GHz; a window spec, not a point spec.
- **$i_n \le 4.0\ \mu$A:** fixed-point inversion of the full §4.4 stack for +2 dB
  margin at Tx OMA −3.5 dBm (script `04` `required_in`): 4.03 µA pre-bump accounting,
  3.83 µA with the bump charged → spec written as ≤ 4.0 µA.
- **≤ 14 pA/√Hz average density:** $4.0\ \mu\mathrm{A}/\sqrt{87\ \mathrm{GHz}} =
  13.6$ pA/√Hz → mask 14 band-average, 16 spot (shape check in Tier 3 item 3.7).
- **Peaking ≤ 1 dB, GD ripple ≤ 3 ps:** variable-$Q$ sweep (1.25 dB peaking costs
  +0.11 dB ISI) and the 12.5 ps ripple → $h_{-1} \approx 0.48$ diagnosis (Tier 3
  item 3.5).

### C.8 GEN2 target-class TIA floor

Same Tier 1 floor formula as C.1, at the target class ($i_n = 4.5\ \mu$A rms,
Butterworth-2 at 58 GHz):

$$\mathrm{OMA_{floor}} = \frac{2 \times 7.035 \times 4.5\ \mu\mathrm{A}}{0.876\ \mathrm{A/W}}
= 72.3\ \mu\mathrm{W} = \mathbf{-11.41\ dBm}.$$

Script `04`; report §4.4.

### C.9 GEN2 penalty stack (4.07 dB, typical Tx)

Inputs: ER 4.5 dB, $B_n = 1.5 \times 58 = 87$ GHz, typical Tx 0.45 UI, 25 fF microbump
in chain, optimal CTLE $z = 37$ / $p = 62$ GHz:

| Line | dB | Arithmetic |
|---|---:|---|
| ER/shot + RIN (one Q-solve) | 1.16 | `rin_shot_penalty(4.5 µA, 87 GHz)` |
| MPI | 0.21 | C.5, GEN2 case (0.205) |
| ISI + EQ net | 1.15 | CTLE sweep on Tx×TIA×bump chain, net of ×0.99 noise enhancement |
| CD | 0.04 | pulse-sim gives 0.015 at +1.7 ps/nm; booked 0.04 (~baud² of GEN1's 0.01) |
| Jitter | 0.95 | $TJ = 0.14 + 2 \times 7.035 \times 0.015 = 0.351$ UI (3.30 ps); eye at $\pm TJ/2$ |
| Crosstalk | 0.36 | carried from GEN1 (rate-independent in OMA domain) |
| Threshold offset | 0.21 | $10\log_{10}(1.05)$ |

Unrounded sum = **4.07 dB** (fast Tx 0.35 UI: 3.74; max Tx 0.60 UI: 4.62 — only the
ISI+EQ and jitter lines move). Script `04`; report §4.4.

### C.10 GEN2 closure margins

Required OMA = floor + stack; margin = (Tx OMA − link IL) − required OMA, at Tx OMA
−3.5 dBm and link IL 2.5 dB (Rx OMA −6.0 dBm):

| Tx corner | Stack | Required OMA | Margin |
|---|---:|---:|---:|
| Fast (0.35 UI) | 3.74 | $-11.41 + 3.74 = -7.67$ | $-6.0 + 7.67 = \mathbf{+1.67}$ |
| Typical (0.45 UI) | 4.07 | $-7.34$ | $\mathbf{+1.34}$ |
| Max (0.60 UI) | 4.62 | $-6.79$ | $\mathbf{+0.79}$ |

Script `04`; report §4.4.
