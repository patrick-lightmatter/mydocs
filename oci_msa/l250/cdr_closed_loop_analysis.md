# Closed-Loop Bang-Bang CDR Analysis — DigitalMmCdr

**Small-signal linearization of the L250 digital Mueller–Müller CDR**

**Status:** draft
**Date:** 2026-07-22
**Companion to:** `architecture_spec.md` Section 5 (§5-1 … §5-12)

---

## 1. Introduction and scope

This document performs a closed-loop, small-signal analysis of the L250
receiver's timing loop — the `DigitalMmCdr` block specified in
`architecture_spec.md` §5 — following the linearized bang-bang phase-locked
loop (PLL) methodology of Sonntag and Stonick, *"A Digital Clock and Data
Recovery Architecture for Multi-Gigabit/s Binary Links,"* IEEE JSSC vol. 41,
no. 8, pp. 1867–1875, Aug. 2006 (henceforth **[Sonntag2006]**). That paper
gives the canonical recipe for reducing a nonlinear bang-bang CDR to a
tractable second-order continuous-time PLL:

1. Linearize the binary (bang-bang) phase detector (BBPD) into an effective
   gain `K_bb` set by the slope of its S-curve at the origin, which for
   Gaussian crossing jitter is proportional to `1/σ`.
2. Map the digital proportional and frequency-register paths onto an
   equivalent charge-pump loop filter (proportional gain + integral gain)
   through a backward-difference substitution `s → (1 − z⁻¹)/T`.
3. Build the closed-loop jitter transfer `H(s)`, read off natural frequency
   `ω_n`, damping `ζ`, and −3 dB bandwidth, and from those the jitter
   tolerance / transfer / generation behaviour.
4. Treat decimation, self-noise (hunting), limit cycles, slew-limiting, and
   latency-driven stability as corrections to the linear picture.

**Where our detector departs from the paper.** [Sonntag2006] analyses a
per-UI early–late BBPD whose parallel outputs are decimated by *majority
voting* into a multi-bit word. Our detector differs in three ways that must
be carried through the derivation explicitly:

- **Transition gating (Mueller–Müller, not edge-sampled).** Our PD
  (`EarlyLateVoteGenNrz`, §5-3) is a baud-rate MM detector that votes only on
  a data transition `d(k−1) ≠ d(k+1)`, with sign
  `sign[(d(k+1) − d(k−1))·e(k)]`. `e(k)` is the 1-bit sliced signed error from
  the dual error-slicer stage (§2-2). This is still a bang-bang detector (the
  information per vote is a single sign bit), so the [Sonntag2006]
  S-curve linearization applies per vote — but the *effective* PD gain is
  scaled by the transition density `ρ` (≈ 0.5 for random NRZ) because
  non-transition UI contribute an exact zero (§5-12).
- **Boxcar accumulation, not hierarchical voting.** Our decimator
  (`CdrVoter`, §5-4) forms a plain signed sum `diff = Σ vote` over
  `cdr_width` UI. This is the *boxcar FIR* case of [Sonntag2006] §III-B, which
  has full DC gain equal to the number of addends — **not** the reduced-gain
  "decimation by voting" case (their Fig. 9, where hierarchical majority
  voting cost ≈ 46 % of the boxcar gain). We therefore use the boxcar DC gain
  and drop the paper's `g_vote` reduction factor, noting the difference where
  it matters.
- **Digital-to-phase converter is a wrapping phase interpolator.** Our
  "DPC" (§5-5) is the `FsmPhase` accumulator driving an N-code phase
  interpolator (PI). Its average gain is exactly `pi_span_ui / n_pi_codes`
  UI per code and is PVT-insensitive by the wrap argument of [Sonntag2006]
  §III (a full control-range wrap returns exactly one span).

The remainder of the document maps [Sonntag2006]'s method onto the
`DigitalMmCdr` fixed-point parameters and produces numeric values at the L250
defaults.

### 1.1 Parameter set used

All numeric results use the **source-of-truth spec values of `architecture_spec.md`
§5-2**, which are the intended L250 configuration:

| Symbol | Spec name | Value | Meaning |
|---|---|---|---|
| `f_b` | `DATA_RATE` | 106.25 GBd | Baud rate |
| `UI` | — | 9.4118 ps | `1/f_b` |
| `W` | `cdr_width` | 32 UI | Voter window (decimation factor) |
| `p_step` | `p_step` | 2 | Proportional numerator |
| `p_div` | `p_div` | 512 | Proportional divider / phase sub-code granularity |
| `f_step` | `f_step` | 2 | Frequency-register numerator |
| `f_div` | `f_div` | 256 | Frequency-register divider |
| `f_bound` | `f_bound` | 2¹⁵ = 32 768 | Frequency-register clamp (±) |
| `N_PI` | `n_pi_codes` | 32 (5-bit) | PI codes across the span |
| `span` | `pi_span_ui` | 1.0 UI | PI span (full-rate PI) |
| `ρ` | — | 0.5 | Transition density (random NRZ) |

> **Note on the model defaults.** The behavioral module
> `src/optical_serdes/rx/mm_cdr_digital.py` ships historical *class defaults*
> of `p_div = 128`, `n_pi_codes = 128`, `f_bound = 2²⁰`. These are **not** the
> L250 spec values — §5-2 and §5-6 supersede them (`p_div = 512`,
> `n_pi_codes = 32`, `f_bound = 2¹⁵`). This analysis uses the spec values
> throughout; a run that keeps the class defaults will scale as noted in the
> sensitivity comments. The load-bearing product
> `f_div·p_div·cdr_width·n_pi_codes = 2²⁷` (§5-6) is preserved by the spec
> split, so ppm results are identical either way.

---

## 2. Bang-bang phase detector linearization

### 2.1 The ideal-slicer S-curve ([Sonntag2006] eqs. 1–4)

Consider a 1-bit slicer whose input has mean `μ` and additive zero-mean
Gaussian noise of standard deviation `σ_v`. Its ±1 output has ensemble
average

$$
\bar{o}(\mu) \;=\; \Pr[x>0] - \Pr[x<0] \;=\; 1 - 2\,Q\!\left(\frac{\mu}{\sigma_v}\right)
\;=\; \operatorname{erf}\!\left(\frac{\mu}{\sqrt{2}\,\sigma_v}\right),
$$

where `Q(·)` is the Gaussian tail integral. For small `μ` this linearizes to
the slope at the origin ([Sonntag2006] eq. 1):

$$
\bar{o}(\mu)\;\approx\;\sqrt{\tfrac{2}{\pi}}\;\frac{\mu}{\sigma_v}, \qquad
\left.\frac{d\bar{o}}{d\mu}\right|_{0} = \sqrt{\tfrac{2}{\pi}}\,\frac{1}{\sigma_v}.
$$

Used as a phase detector, a static phase error `φ_e` (in UI) at a rising
transition produces a mean sliced voltage `μ = (dv/dt)\,φ_e·UI`
proportional to the signal slope at the crossing. At the zero crossing,
additive voltage noise and timing jitter are interchangeable through the same
slope, `σ_v = (dv/dt)·σ_t`, so when we substitute `μ` and `σ_v` the slope
`(dv/dt)` **cancels** ([Sonntag2006] eq. 4). The per-transition detector slope
at the origin, expressed directly in phase (UI), is therefore

$$
\boxed{\,K_{bb} \;=\; \sqrt{\tfrac{2}{\pi}}\;\frac{1}{\sigma_\varphi}\,}
\qquad [\text{PD output per UI of phase error}],
$$

with `σ_φ` the RMS crossing jitter expressed in UI. This is the key
bang-bang result: **the small-signal PD gain is inversely proportional to the
input jitter** — a large-jitter input produces a shallow S-curve (low gain),
a clean input produces a steep one (high gain). All jitter present at the
crossing (RJ + slope-referred DJ + BBPD self-noise) enters `σ_φ`; per
[Sonntag2006] §II-C the standard deviation of non-Gaussian DJ may be used in
the same formula as a working approximation.

### 2.2 Transition gating and windowed (boxcar) averaging

Two L250-specific factors convert the per-transition slope into the gain seen
by the loop filter, i.e. the mean of `diff` versus `φ_e`.

**Transition density.** Only UI carrying a data transition vote (§5-3);
for random NRZ the transition density is `ρ = ½`. A UI with no transition
contributes an exact zero, so the *mean number of voting UI* per window is
`ρ·W`.

**Boxcar window sum.** `CdrVoter` sums the ternary votes over `W = cdr_width`
UI (§5-4). Because this is a linear boxcar sum (not hierarchical voting), its
DC gain is simply the count of contributing votes. Combining,

$$
\mathbb{E}[\,\text{diff}\,] \;=\; \underbrace{\rho\,W}_{\text{voting UI/window}}\;
K_{bb}\;\varphi_e \;\equiv\; K_{\text{det}}\,\varphi_e,
\qquad
\boxed{\,K_{\text{det}} \;=\; \rho\,W\,\sqrt{\tfrac{2}{\pi}}\;\frac{1}{\sigma_\varphi}\,}
\quad[\text{counts of diff per UI}].
$$

At the L250 defaults with the RJ baseline `σ_φ = 0.022 UI` (the CEI-XSR
`J_RMS ≤ 0.022 UI` term imported in §3-4):

$$
K_{bb} = \frac{0.7979}{0.022} = 36.3\ \text{UI}^{-1}, \qquad
K_{\text{det}} = 0.5\cdot32\cdot36.3 = \mathbf{580}\ \text{counts/UI}.
$$

**Linear range.** `diff` is bounded by the number of transitions in the
window, `|diff| ≤ ρW ≈ 16` on average (`≤ W = 32` only for an all-transition
pattern such as `1010`). The small-signal model holds while `K_det·|φ_e| ≲
ρW`, i.e. `|φ_e| ≲ 1/(K_bb) = σ_φ/√(2/π) ≈ 0.028 UI` at the baseline. Beyond
that the S-curve saturates and the loop is slew-limited (§6).

**Assumptions stated explicitly.**
- Gaussian (or DJ-as-Gaussian) crossing statistics, small phase error.
- Zero phase-slicer offset. [Sonntag2006] §II-C and Fig. 5 show that error-slicer
  offset flattens the S-curve and can create a dead zone, cutting `K_bb`. Our
  Vp loops (§6-3) servo the error slicers onto the rail medians, so the
  nominal analysis takes offset ≈ 0; a residual offset is a `K_bb`-reduction
  caveat (§10).
- `ρ = 0.5`. Mueller–Müller lock (`h₋₁ = h₊₁`, §5-3) is assumed so that the
  ternary sign is an unbiased early/late indicator; CID runs (§5-12) drop `ρ`
  transiently to 0 and are handled by the frequency register coasting.

---

## 3. Loop filter → continuous-time model

### 3.1 Fixed-point → phase (UI) unit conversions

The phase accumulator `state_p` runs in **sub-code** units, where one PI code
= `p_div` sub-codes and one PI code = `span/N_PI` UI. Hence

$$
1\ \text{sub-code} = \frac{\text{span}}{N_{PI}\,p_{div}}\ \text{UI}
= \frac{1}{32\cdot512}\ \text{UI} = \frac{1}{16384}\ \text{UI} \approx 0.574\ \text{fs},
\qquad
1\ \text{PI code} = \frac{1}{32}\ \text{UI} \approx 294\ \text{fs}.
$$

Per window dump (§5-7), the loop filter emits, in sub-codes,

$$
\text{p\_inc} = \text{diff}\cdot p_{step}, \quad
\text{state\_f} \mathrel{+}= \text{diff}\cdot f_{step}, \quad
\text{f\_out} = \left\lfloor \frac{\text{state\_f}}{f_{div}}\right\rfloor, \quad
\delta = \text{p\_inc} + \text{f\_out},
$$

and the phase accumulator integrates `δ`. Converting to UI, define the two
per-count gains:

$$
a \;\triangleq\; \frac{p_{step}}{N_{PI}\,p_{div}}
= \frac{2}{16384} = 1.221\times10^{-4}\ \frac{\text{UI}}{\text{count}}
\quad(\text{proportional, per window}),
$$

$$
b \;\triangleq\; \frac{f_{step}}{f_{div}\,N_{PI}\,p_{div}}
= \frac{2}{256\cdot16384} = 4.768\times10^{-7}\ \frac{\text{UI}}{\text{count}\cdot\text{window}}
\quad(\text{integral}).
$$

`a` is the sampling-phase step (UI) per unit of `diff` from the proportional
path in one window; `b` is the *increment to the phase ramp rate* (UI per
window) per unit of `diff` fed to the frequency register.

### 3.2 Update period and discrete update

The voter decimates by `W`, so the loop filter and phase FSM update once per

$$
T \;=\; W\cdot UI \;=\; 32\cdot9.4118\ \text{ps} = 301.2\ \text{ps},
\qquad f_{\text{upd}} = 1/T = 3.320\ \text{GHz}.
$$

Let `n` index windows. The sampling phase `φ_out` (UI) is a pure accumulator
of `δ` (the `FsmPhase` integrator = the analog VCO/DPC):

$$
\varphi_{out}[n] - \varphi_{out}[n-1] \;=\; \delta[n]
= K_{\text{det}}\Bigl(a\,\varphi_e[n] + b\!\!\sum_{m\le n}\!\varphi_e[m]\Bigr),
\qquad \varphi_e = \varphi_{in} - \varphi_{out}.
$$

### 3.3 Backward-difference / continuous mapping ([Sonntag2006] eqs. 5–8)

Following [Sonntag2006]'s substitution `1 − z⁻¹ → sT`, the open-loop transfer
from `φ_e` to `φ_out` is type-II (two poles at the origin — one from the
frequency register, one from the phase accumulator):

$$
L(z) = \frac{K_{\text{det}}\bigl(a + b/(1-z^{-1})\bigr)}{1-z^{-1}}
\;\xrightarrow{\,1-z^{-1}\to sT\,}\;
L(s) = \frac{K_{\text{det}}\,a}{sT} + \frac{K_{\text{det}}\,b}{(sT)^2}
= \frac{K_P}{s} + \frac{K_I}{s^2}.
$$

The equivalent **continuous-time proportional and integral loop gains** are

$$
\boxed{\,K_P = \frac{K_{\text{det}}\,a}{T}\ \ [\text{s}^{-1}], \qquad
K_I = \frac{K_{\text{det}}\,b}{T^2}\ \ [\text{s}^{-2}]\,}.
$$

It is convenient to also keep the **dimensionless per-window loop
coefficients**, which are `T`-independent and expose `ζ` directly:

$$
K_{P,\text{win}} = K_{\text{det}}\,a \;(=K_P T), \qquad
K_{I,\text{win}} = K_{\text{det}}\,b \;(=K_I T^2).
$$

`K_{P,win}` is the fraction of a UI of phase error corrected per window by the
proportional path; `K_{I,win}` is the per-window frequency increment per UI of
error.

At the defaults with `σ_φ = 0.022 UI` (`K_det = 580`):

| Quantity | Expression | Value |
|---|---|---|
| `a` | `p_step/(N_PI·p_div)` | 1.221×10⁻⁴ UI/count |
| `b` | `f_step/(f_div·N_PI·p_div)` | 4.768×10⁻⁷ UI/count/window |
| `K_{P,win}` | `K_det·a` | 0.0708 (per window) |
| `K_{I,win}` | `K_det·b` | 2.77×10⁻⁴ (per window) |
| `K_P` | `K_det·a/T` | 2.35×10⁸ s⁻¹ |
| `K_I` | `K_det·b/T²` | 3.05×10¹⁵ s⁻² |

---

## 4. Closed-loop transfer function

With `L(s) = K_P/s + K_I/s²`, the jitter (phase) transfer function is the
classic type-II form ([Sonntag2006] eq. 10):

$$
H(s) = \frac{\varphi_{out}}{\varphi_{in}} = \frac{L(s)}{1+L(s)}
= \frac{K_P\,s + K_I}{s^2 + K_P\,s + K_I}
= \frac{2\zeta\omega_n\,s + \omega_n^2}{s^2 + 2\zeta\omega_n\,s + \omega_n^2},
$$

and the phase-error (high-pass) transfer, used for jitter tolerance, is

$$
E(s) = 1 - H(s) = \frac{1}{1+L(s)} = \frac{s^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}.
$$

Matching coefficients gives the natural frequency and damping:

$$
\boxed{\,\omega_n = \sqrt{K_I} = \frac{\sqrt{K_{I,\text{win}}}}{T},\qquad
\zeta = \frac{K_P}{2\omega_n} = \frac{K_{P,\text{win}}}{2\sqrt{K_{I,\text{win}}}}
= \frac{a}{2}\sqrt{\frac{K_{\text{det}}}{b}}\,}.
$$

`H(s)` carries a real zero at `ω_z = ω_n/(2ζ) = K_I/K_P`, characteristic of a
type-II loop; it lifts the −3 dB bandwidth well above `ω_n` when the loop is
overdamped. The −3 dB jitter-transfer bandwidth is

$$
\omega_{3dB} = \omega_n\sqrt{\,1 + 2\zeta^2 + \sqrt{(1+2\zeta^2)^2 + 1}\,}.
$$

### 4.1 Numeric values at the defaults

Evaluating at the L250 spec parameters (numbers verified with a numpy check,
`temp/cdr_bb_analysis_check.py`):

| `σ_φ` [UI] | `K_bb` [UI⁻¹] | `K_det` | `K_P` [s⁻¹] | `K_I` [s⁻²] | `f_n = ω_n/2π` | `ζ` | `f_{3dB}` |
|---|---|---|---|---|---|---|---|
| 0.010 | 79.8 | 1277 | 5.17×10⁸ | 6.71×10¹⁵ | 13.0 MHz | 3.16 | 84.4 MHz |
| 0.020 | 39.9 | 638 | 2.59×10⁸ | 3.36×10¹⁵ | 9.22 MHz | 2.23 | 43.2 MHz |
| **0.022** | **36.3** | **580** | **2.35×10⁸** | **3.05×10¹⁵** | **8.79 MHz** | **2.13** | **39.5 MHz** |
| 0.030 | 26.6 | 426 | 1.73×10⁸ | 2.24×10¹⁵ | 7.53 MHz | 1.82 | 29.5 MHz |
| 0.050 | 16.0 | 255 | 1.03×10⁸ | 1.34×10¹⁵ | 5.83 MHz | 1.41 | 18.5 MHz |
| 0.100 | 7.98 | 128 | 5.17×10⁷ | 6.71×10¹⁴ | 4.12 MHz | 1.00 | 10.2 MHz |

Because `K_det ∝ 1/σ_φ`, and `ω_n ∝ √K_det`, `ζ ∝ √K_det`, both scale as
`1/√σ_φ`. **The loop bandwidth is jitter-dependent** — the defining feature of
a bang-bang loop.

### 4.2 Comparison with the §5-9 4–6 MHz target

- At the **RJ-only baseline** (`σ_φ = 0.022 UI`), the natural/tracking corner
  `f_n ≈ 8.8 MHz` sits **above** the 4–6 MHz design target, and the
  jitter-transfer `f_{3dB} ≈ 39 MHz` **exceeds even the ~30 MHz latency
  ceiling** (§5-9). The loop as specified is *wider* than the target when the
  input is clean.
- This directly corroborates the §5-9 caveat that the integer parameters
  (`p_step/p_div = 2/512`, `f_step/f_div = 2/256`) "were chosen to satisfy
  dither and pull-in criteria (§5-8) … not to hit the 4–6 MHz closed-loop
  bandwidth per se" and "must be verified against, and if necessary re-tuned
  to, this bandwidth target." **This analysis is that verification, and the
  answer is: re-tune is needed to bring the clean-input bandwidth down.**
- The target is approached only when the crossing jitter is large
  (`σ_φ ≈ 0.10 UI` gives `f_n ≈ 4.1 MHz`), i.e. the loop self-narrows under
  stress but is over-wide at nominal RJ.
- **Which "bandwidth" the target refers to matters.** If §5-9's 4–6 MHz means
  the tracking corner (`≈ f_n`), the loop is ~1.5–2× high at baseline. If it
  means the jitter-transfer `f_{3dB}`, the loop is ~7× high. Because the loop
  is overdamped the two differ by ~4.5×; the doc should pin down the
  definition when the budget closes (see §10). A concrete re-tune that lands
  `f_n` at 5 MHz at `σ_φ = 0.022 UI` is to reduce the integral gain by
  `(5/8.79)² ≈ 0.32`, e.g. `f_div = 768` (`f_step = 2`), and to hold `ζ` by
  reducing the proportional gain proportionally (`p_div ≈ 900`); these must
  then be re-checked against the dither floor (§7) and pull-in (§6).

The heavy damping (`ζ = 2.1` at baseline, always `> 1` for `σ_φ ≤ 0.10 UI`)
means the response is **overdamped with no jitter peaking**, exactly the
"heavily damped, ζ significantly greater than 1, jitter peaking minimal"
posture that §5-10 requires for the cycle-slip-free mission mode.

---

## 5. Jitter tolerance, transfer, and generation

### 5.1 Jitter transfer (peaking)

For `ζ ≥ 1` the type-II `H(s)` has **no gain peaking** — the low-frequency
zero `ω_z = ω_n/(2ζ)` and the overdamped poles give a monotone roll-off after
a gentle shelf. Peaking would require `ζ < 1/√2`, which at these gains needs
`σ_φ > 0.20 UI` (well outside the operating range). Thus **jitter generation
transferred from input to output is not amplified**, consistent with the
§5-10 mission-mode requirement. [Sonntag2006] Fig. 12 shows the opposite
trade in their part (1.1 / 2 / 3.6 dB peaking as bandwidth is pushed up); our
default sits deliberately on the no-peaking side.

### 5.2 Jitter tolerance (JTOL)

Jitter tolerance is the input sinusoidal-jitter amplitude that holds the
sampling phase error to a fixed margin `φ_{e,max}` (the horizontal eye
budget). Using the high-pass error transfer `E(s)`,

$$
A_{\text{JTOL}}(\omega) = \frac{\varphi_{e,\max}}{|E(j\omega)|}
= \varphi_{e,\max}\,\frac{|\,-\omega^2 + 2\zeta\omega_n j\omega + \omega_n^2\,|}{\omega^2}.
$$

Asymptotes:

- **Low frequency** (`ω ≪ ω_n`): `|E| ≈ ω²/ω_n²`, so
  `A_{JTOL} ≈ φ_{e,max}·(ω_n/ω)²` → **40 dB/decade** slope. The two integrators
  (frequency register + phase accumulator) give the type-II
  `1/f²` tolerance that lets the loop swallow large low-frequency wander (and
  the static ppm offset, §6).
- **Corner** near `ω_n` (`f_n ≈ 8.8 MHz` at baseline).
- **High frequency** (`ω ≫ ω_n`): `A_{JTOL} → φ_{e,max}`, the flat floor set
  by the eye margin, independent of the loop.

**Relation to the §5-9 masks.** The OIF CEI-112G-XSR (Table 24-12) and IEEE
P802.3dj (Tables 179-12 / 182-20) masks have their 1/f-to-flat corner at
~4 MHz (dj) / ~8 MHz (`f_CRU = f_b/13280 ≈ 8 MHz`, CEI). For the loop to
absorb the low-frequency SJ ramp, its tolerance corner (`≈ f_n`) must sit
**at or above** the mask corner. At the RJ baseline `f_n ≈ 8.8 MHz` clears
both mask corners comfortably (this is the flip side of the "too wide"
finding of §4.2: the loop over-tracks, spending margin on tracking jitter it
could have charged to the eye). Below the corner the loop tracks the SJ at no
eye cost; above it, the residual (including the mask's 0.05 UI pk-pk
high-frequency floor, §5-9) lands on the sampling instant and is charged to
the horizontal eye budget. As [Sonntag2006] §III-C warns, the *linear* JTOL
curve is optimistic at low frequency, where large-signal **slew-limiting**
(§6), not the small-signal corner, sets the true tolerance.

### 5.3 Jitter generation / self-noise

[Sonntag2006] §II-E: the BBPD emits a full-scale ±1 for *every* transition, so
its output carries a broadband self-noise whose input-referred RMS is, after
scaling by `1/K_bb`, **proportional to the input jitter itself**
(`σ_{self} ∝ σ_φ`). The loop bandwidth must be kept low enough that little of
this self-noise power sits in the passband. In our loop the generated jitter
at lock is dominated instead by the **phase quantization** (1 PI code), which
is analyzed as the limit cycle in §7; the continuous self-noise term is
sub-dominant because the PI step (294 fs = 0.031 UI) is larger than the
input-referred self-noise contribution filtered by the loop.

---

## 6. Frequency acquisition and slew limits

### 6.1 Maximum trackable offset (type-II lock range)

A steady frequency offset is absorbed by a constant `state_f` producing a
constant phase ramp (§5-6). The clamp `f_bound` sets the maximum:

$$
\text{ppm}_{\max} = \frac{f_{bound}\cdot10^6}{f_{div}\,p_{div}\,W\,N_{PI}}
= \frac{2^{15}\cdot10^6}{2^{27}} = 244\ \text{ppm},
$$

with the governing product `f_div·p_div·W·N_PI = 2²⁷` (§5-6). The settled
register value for the ±200 ppm design target is
`state_f = 200×10⁻⁶·2²⁷ = 26 844`, giving ~22 % clamp margin — reproducing
§5-6 exactly. Frequency resolution is `10⁶/2²⁷ = 0.00745 ppm` per LSB.

### 6.2 Slew rate and pull-in time

During acquisition the S-curve is saturated, so each transition votes with
the same sign and `diff` saturates at its transition-limited maximum
`|diff| ≈ ρW = 16` (not `W = 32` — a consequence of transition gating, §2.2).
The frequency register then slews at

$$
\Delta\text{state\_f} = |\text{diff}|\cdot f_{step} \approx 16\cdot2 = 32\ \text{counts/window}.
$$

The minimum windows to build the 200 ppm register value is

$$
N_{\text{win}} \approx \frac{26\,844}{32} \approx 839\ \text{windows}
= 839\cdot32 \approx \mathbf{26.8k\ UI}.
$$

The behavioral result (§5-8) is ~56k UI (~0.5 µs). The ~2× gap is expected:
`diff` only stays saturated far from lock; as `state_f` approaches its target
the vote majority collapses toward zero, so the last portion of the ramp is
slow, and the proportional path adds its own settling. The closed-form
minimum (26.8k UI) and the simulated full-settle (56k UI) are therefore
**consistent to order of magnitude and correctly bracket the transient**.
The §5-6 note that `state_f` overshoots to ≈ −28k before settling at −26.6k
(~5 %) is the expected type-II second-order overshoot given `ζ = 2.1`
(overdamped in the small-signal limit, but the large-signal slew-then-capture
trajectory still overshoots because the proportional term does not brake
until the S-curve re-linearizes).

The maximum proportional phase slew (large error) is
`ρW·a/T = 16·1.221×10⁻⁴/301.2 ps ≈ 6.5×10⁶ UI/s`, i.e. the loop can hunt the
sampling point across the eye far faster than any plausible mechanical/thermal
phase drift; acquisition is frequency-register-limited, not proportional-limited.

---

## 7. Limit cycle, hunting, and dither at lock

### 7.1 Quantization-pinned dither

At lock the residual vote majority is small (`|diff|` of order 1). The
proportional path moves the phase accumulator by `diff·p_step = 2·diff`
sub-codes per window, but the emitted `pi_code = ⌊state_p/p_div⌋` only changes
when `state_p` crosses a `p_div = 512`-sub-code boundary. With `|diff| ≈ 1`
this takes `512/2 = 256` windows, so **the PI output cannot chatter faster
than ~256 windows per code**, and the steady-state dither is pinned to a
single PI code:

$$
\text{dither}_{pp} = 1\ \text{PI code} = \frac{1}{N_{PI}}\ \text{UI}
= \frac{1}{32}\ \text{UI} = 0.031\ \text{UI (pk-pk)} \approx 294\ \text{fs},
$$

with RMS ≈ 0.0040 UI for a triangular/uniform dither — exactly the §5-8
figure. This is the L250 realization of [Sonntag2006]'s "dither bits": the
lower `log₂(p_div) = 9` bits of the phase integrator are truncated away, so
the quantization noise is buried and the limit cycle is confined to ±½ code
about the lock point.

### 7.2 Role of `p_div` and the classic bang-bang limit cycle

[Sonntag2006] §II-E notes that as input jitter falls, `K_bb` rises until the
loop goes small-signal unstable and enters a limit cycle, which prevents the
phase jitter from reaching zero. In our loop this manifests as the
1-PI-code hunt: `p_div` sets the phase-step floor and hence the limit-cycle
amplitude. §5-8 records that a **smaller `p_div`** (higher proportional gain)
lets the loop overshoot and hunt across **2 PI codes** (≈ 0.063 UI pk-pk)
instead of settling within one — the direct large-`K_bb` instability the
paper describes. Keeping `p_div = 512` places the per-window proportional step
(`≤ ρW·a = 16·1.221×10⁻⁴ ≈ 2.0×10⁻³ UI`, and `≤ 1×10⁻³ UI` per §6-8) below
the code granularity, so the loop damps into one code. The trade is slower
acquisition (§6.2), which is why §5-8/§6-9 recommend making `p_div`
programmable for an acquisition gear-shift.

### 7.3 Frequency-path dither

The frequency register contributes `⌊state_f/f_div⌋`; a 1-LSB wobble of the
divided value is `1/(N_PI·p_div) = 0.57 fs` — three orders below the PI-code
dither, so the frequency path adds negligible steady-state jitter. The P/F
quantum separation (`f_step/f_div` two decades below `p_step/p_div`, §6-9) is
what keeps the frequency path from contributing hunting.

---

## 8. Stability and update-rate constraints

### 8.1 Discrete-time validity

The continuous approximation `1 − z⁻¹ → sT` is accurate while
`ω_{3dB}·T ≪ 1`. At the baseline `ω_{3dB}·T = 0.0747 rad` (`≈ 4.3°`), so the
sampled-data corrections are small and the continuous `H(s)` is trustworthy.
Equivalently the loop bandwidth (`f_{3dB} ≈ 39 MHz`) is ~85× below the update
rate (`f_upd = 3.32 GHz`), far from the `f_upd/π` sampled-loop stability
limit.

### 8.2 Latency and the ~30 MHz ceiling

[Sonntag2006] eq. 6 carries an explicit `z^{−Δ}` latency term (deserialization
+ loop-filter pipe + DPC settling); when the round-trip latency `t_d`
approaches `π/ω_{crossover}` the phase margin collapses. Modeling the latency
as a delay `t_d = D·T` (D windows of pipeline), the extra phase lag at the
loop crossover `ω_c ≈ K_P` (for the overdamped loop) is `Δφ = ω_c·t_d`. The
§5-9 upper bound (~30 MHz) is the crossover at which this lag erodes the phase
margin for a realistic `D` of a few windows:

$$
f_c^{\max} \sim \frac{\phi_{\text{margin,budget}}}{2\pi\,D\,T}.
$$

With `D ≈ 3` windows (`t_d ≈ 0.9 ns`) and a 60° margin budget,
`f_c^{max} ≈ 0.17/(3·0.30 ns) ≈ 185 MHz` for a first-order crossover; the more
conservative ~30 MHz ceiling of §5-9 reflects the *type-II* margin (the
integral pole already spends phase) plus PI settling and is the number to
carry until the physical pipeline depth `D` is fixed. **The key stability
finding: at the baseline the loop's own `f_{3dB} ≈ 39 MHz` is uncomfortably
close to this latency ceiling** — another reason (besides §4.2) to reduce the
gains so the clean-input bandwidth sits inside the 4–6 MHz target with margin
against the ceiling.

### 8.3 Frequency-register clamp

`state_f` is clamped, not wrapped (§5-6). Clamping is the correct stable
degradation: an offset beyond ±244 ppm leaves the loop slewing at its maximum
ramp and simply failing to complete pull-in (detectable as persistent
one-sided `diff`), rather than a catastrophic sign flip. The phase accumulator
is the only wrapping register and wraps modulo `2·reg_max = 2·N_PI·p_div`,
giving unbounded phase rotation for plesiochronous tracking.

---

## 9. Summary table (defaults, `σ_φ = 0.022 UI`)

| Quantity | Symbol | Expression | Value |
|---|---|---|---|
| Baud rate | `f_b` | spec | 106.25 GBd |
| Unit interval | `UI` | `1/f_b` | 9.4118 ps |
| Update period | `T` | `W·UI` | 301.2 ps |
| Update rate | `f_upd` | `1/T` | 3.320 GHz |
| Transition density | `ρ` | random NRZ | 0.5 |
| Crossing jitter (baseline) | `σ_φ` | CEI-XSR `J_RMS` (§3-4) | 0.022 UI |
| Per-transition BBPD gain | `K_bb` | `√(2/π)/σ_φ` | 36.3 UI⁻¹ |
| Detector gain (windowed) | `K_det` | `ρW·K_bb` | 580 counts/UI |
| Proportional per-count | `a` | `p_step/(N_PI·p_div)` | 1.221×10⁻⁴ UI/count |
| Integral per-count | `b` | `f_step/(f_div·N_PI·p_div)` | 4.768×10⁻⁷ UI/count/win |
| Proportional loop gain | `K_P` | `K_det·a/T` | 2.35×10⁸ s⁻¹ |
| Integral loop gain | `K_I` | `K_det·b/T²` | 3.05×10¹⁵ s⁻² |
| Natural frequency | `f_n` | `√K_I/2π` | **8.79 MHz** |
| Damping factor | `ζ` | `K_P/(2ω_n)` | **2.13** |
| `ζ·ω_n` (loop pole real part) | — | `K_P/2` | 1.18×10⁸ s⁻¹ (18.7 MHz) |
| Jitter-transfer −3 dB | `f_{3dB}` | type-II formula | **39.5 MHz** |
| Jitter peaking | — | `ζ > 1/√2` | none (overdamped) |
| Max trackable offset | `ppm_max` | `f_bound·10⁶/2²⁷` | ±244 ppm |
| `state_f` at 200 ppm | — | `200e-6·2²⁷` | 26 844 |
| Freq. resolution | — | `10⁶/2²⁷` | 0.00745 ppm/LSB |
| Acquisition (200 ppm, min) | — | `26844/(ρW·f_step)·W` | ≈ 26.8k UI |
| Acquisition (200 ppm, sim) | — | §5-8 | ≈ 56k UI |
| Steady-state dither | — | 1 PI code | 0.031 UI pp (0.0040 UI RMS) |

**Bandwidth vs target:** at baseline the tracking corner `f_n ≈ 8.8 MHz`
exceeds the §5-9 design target of 4–6 MHz, and `f_{3dB} ≈ 39 MHz` exceeds the
~30 MHz latency ceiling. The gains satisfy the dither (§7) and pull-in (§6)
criteria they were chosen for, but **must be reduced** (integral gain ×~0.32,
holding `ζ`) to bring the clean-input bandwidth into the target window — the
re-tune §5-9 flagged as pending.

---

## 10. Assumptions, caveats, and open items

Flagged `TBD` in the spirit of `architecture_spec.md` (symbolic where a
number is not yet derivable):

1. **Crossing-jitter operating point `σ_φ` — TBD.** Every dynamic result
   scales with `σ_φ` (as `1/√σ_φ`). The baseline uses the CEI-XSR RJ term
   (0.022 UI, §3-4); the true `σ_φ` includes slope-referred DJ, residual ISI
   after CTLE, and BBPD self-noise, and is likely larger (0.03–0.05 UI),
   which *lowers* `f_n`/`ζ` toward the target. **Action:** extract `σ_φ` at the
   data-slicer crossing from the behavioral RX and re-evaluate the §4.1 table
   at that point.
2. **Definition of the §5-9 "closed-loop bandwidth" — TBD.** Whether 4–6 MHz
   means `f_n` (tracking corner) or `f_{3dB}` (jitter transfer) changes the
   verdict by ~4.5× (the overdamped `ζ·` spread). Pin this down before the
   re-tune.
3. **Gain re-tune — open.** The proposed `f_div ≈ 768`, `p_div ≈ 900` (to land
   `f_n ≈ 5 MHz` at `σ_φ = 0.022 UI` while holding `ζ ≈ 2`) must be checked
   against (a) the 1-PI-code dither floor (§7), (b) 200 ppm pull-in time
   (§6), and (c) the frequency-register clamp (§8.3). Confirm in
   closed-loop sim.
4. **Loop latency `D` — TBD.** The ~30 MHz ceiling (§8.2) depends on the
   physical pipeline depth (deserialization + filter + PI settling), not yet
   fixed. Needs the RTL/silicon pipeline count to convert to a hard phase-margin
   number.
5. **Error-slicer offset — caveat.** The analysis assumes zero phase-slicer
   offset (`K_bb` at full S-curve slope). Residual offset flattens the S-curve
   and can create a dead zone ([Sonntag2006] Fig. 5), reducing `K_bb` and hence
   the loop bandwidth, and adding low-frequency phase wander. The Vp loops
   (§6-3) null this in steady state; quantify the residual once `V_LSB,vp`
   (§2) is set.
6. **Boxcar vs voting gain — resolved but flagged.** We used the boxcar DC
   gain (`ρW`) because `CdrVoter` sums linearly; if the silicon adopts
   hierarchical majority voting for timing closure (as [Sonntag2006] Fig. 8),
   apply their `g_vote` reduction (~0.5 for vote-by-4) to `K_det`, which lowers
   `f_n`/`ζ` accordingly.
7. **Transition density `ρ` — pattern dependence.** `ρ = 0.5` assumes random
   NRZ. Periodic bring-up patterns (`0xCC`, §5-12) and CID runs (72 UI, §5-12)
   change `ρ` and momentarily zero the PD gain; the frequency register coasts
   through these, but JTOL under the CID + SJ combination needs the §5-12
   behavioral confirmation.
8. **Large-signal JTOL floor — TBD.** The §5.2 curve is the small-signal
   tolerance; the true low-frequency JTOL is set by slew-limiting (§6) and
   must be read from a large-signal sinusoidal-jitter sweep, not this linear
   model ([Sonntag2006] §III-C caveat).

---

### References

- J. L. Sonntag and J. Stonick, "A Digital Clock and Data Recovery
  Architecture for Multi-Gigabit/s Binary Links," *IEEE J. Solid-State
  Circuits*, vol. 41, no. 8, pp. 1867–1875, Aug. 2006.
- `architecture_spec.md`, L250 PMA Architecture Specification, Section 5
  (CDR) and §3-4 (TX jitter budget), §5-9 (bandwidth target), §5-10
  (cycle-slip / damping).
- `src/optical_serdes/rx/mm_cdr_digital.py` — `DigitalMmCdr` implementation
  (`EarlyLateVoteGenNrz`, `CdrVoter`, `LoopFilter`, `FsmPhase`).
