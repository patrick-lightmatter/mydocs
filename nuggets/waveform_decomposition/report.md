# Waveform Decomposition: Signal + ISI + Distortion + Noise

**Project:** optical-serdes
**Source:** [`src/optical_serdes/analysis/waveform_decomposition.py`](../../../optical-serdes/src/optical_serdes/analysis/waveform_decomposition.py)
**Example:** [`examples/waveform_decomposition_demo.py`](../../../optical-serdes/examples/waveform_decomposition_demo.py)
**Skill (linear baseline):** [`channel-characterise`](../../../optical-serdes/.claude/skills/channel-characterise.md)

---

## TL;DR

> **Update (Jun 22 2026):** the LTI input model was unified.  Both modes
> now feed the Wiener stage a **ZOH staircase** $x_\text{ZOH}(t)$ built
> from the symbol stream (or the measured upstream waveform in per-block
> mode); there is no longer a Dirac-train code path.  The recovered
> kernel $\hat h$ is therefore the **channel impulse response**, *not*
> the single-bit response.  Numbers and conclusions tied to the
> Wiener baseline (§7.11, §7.11.1, §8) have been re-measured under
> the new model; the **exact-baseline** results in §7.1–§7.10 are
> unaffected (they never relied on the Wiener path).

**What this is.**  A method that takes one captured waveform + the
transmitted symbols and splits the result into four physically distinct
components:
$r = \underbrace{a[m]h_0}_\text{desired} + \underbrace{\sum_{k\neq m}a[k]h_{m-k}}_\text{ISI} + \underbrace{d(t)}_\text{distortion} + \underbrace{n(t)}_\text{noise}$
The linear half is Wiener-Hopf channel estimation against a ZOH input
(§3–§4); the new piece is **pattern-conditional averaging** of the
residual that separates the deterministic distortion from the random
noise (§5).

**The one number that governs everything: $L_\text{collapse} = \min(M, N)$.**
The leftover-noise floor of the estimator collapses to machine epsilon
exactly when the context window $L$ reaches the smaller of the channel
memory $M$ (in UI) and the source entropy $N$ (PRBS order, or $\infty$
for IID).  This is derived, swept across both axes, and validated to
sub-percent agreement in §7.8.  This law is a property of the
**residual**, so it holds for any consistent linear baseline — exact
or Wiener.

**Pre-collapse, the floor is not free either — the IR predicts it.**  For
$L < L_\text{collapse}$ the leftover RMS is
$\;\text{RMS}(g'(y_\text{lin})\cdot u_W)\;$ where $u_W$ is the
out-of-window IR tail and $g'$ is the nonlinearity slope.  Synthetic data
with a known IR, a weak tanh, and 2.5 M symbols matches this prediction
across $M\in\{7,13,51\}$ UI to within a few % (§7.9).  No mystery floor.

**Two baselines, two regimes:**

| baseline | what $\hat h$ is | use | floor |
|---|---|---|---|
| **exact** (oracle IR) | planted channel IR (or SBR) | synthetic validation only | machine $\epsilon$; matches IR prediction down to $10^{-18}$ (§7.9, §7.10) |
| **Wiener** (real captures) | Tikhonov-regularised channel IR recovered from $(x_\text{ZOH}, y)$ | production | clipped from below by $\varepsilon_W$ (§7.11), split between $\hat d$ and $\hat n$ |

The Wiener clip $\varepsilon_W = \hat y_\text{exact} - \hat y_\text{W}$
under a ZOH drive has **two distinct components**: (i) a small
symbol-correlated piece that pattern averaging attributes to
$\hat d_W$ (the band-limited cursor-tap effect remains, but is now
the *channel-IR* cursor, not the SBR cursor), and (ii) a broadband
piece coming from the ZOH input's sinc nulls — these are the
frequencies the Wiener filter regularises into noise.  Pattern
averaging cannot capture (ii), so it lands in $\hat n_W$.

**Concrete Wiener floors under the ZOH model (in-window $M=7$, PRBS13):**

* Default `reg=1e-4`: $\varepsilon_W\approx1.6\times10^{-2}$ RMS,
  $d_\text{err,W}\approx1.5\times10^{-2}$, with $\hat n_W$ inflated by
  the broadband Wiener noise.
* Fine `reg=1e-6`: $\varepsilon_W\approx3.0\times10^{-3}$,
  $d_\text{err,W}\approx9\times10^{-4}$ — best achievable on this
  setup; reducing `reg` further enters the noise-amplification
  regime.
* Effective SDR ceiling against a signal RMS $\approx 0.95$ is
  $\sim 36$ dB at default reg, $\sim 60$ dB at `reg=1e-6`.

**Operating guidance for real captures (§7.11):**

1. Use Wiener IR window $n_\text{pre}=n_\text{post}\gtrsim M$.  For
   pkctrl3-class channels ($M\lesssim 20$–$30$ UI) the default 51-UI
   window is fine.
2. Pick context $L \geq \min(M, N)$ for collapse, or use the §7.9
   IR-predicted floor to know how much distortion is unresolved at
   smaller $L$.
3. For coarse measurements (real SDR $\ll 35$ dB) keep the default
   `reg=1e-4`.  For fine measurements (35–60 dB target), drop to
   `reg=1e-6` — this is the new sweet spot under the ZOH model.
4. **Trust $\hat n_W$ only when injected $\sigma$ comfortably
   exceeds $\varepsilon_W$.**  In the §7.10 null-case sweep,
   $\sigma_{\hat n_W}/\sigma\to 1$ as $\sigma$ rises above the
   Wiener noise floor; below it $\hat n_W$ is dominated by the
   broadband Wiener noise and over-reports.
5. Distortion bins need $\gtrsim 4$ hits each; for context $L$ this
   demands a record of at least $\sim4\cdot 2^L$ UI (data-starvation
   wall in §7.9.1).

**What's been validated end-to-end (§7):**

* Pattern coverage at the symbol-spaced cursor (§7.2).
* Distortion-recovery and noise-variance recovery vs injected $\sigma$ —
  exact baseline gives $\sigma_\hat n/\sigma\to 1$ and
  $d_\text{err}\propto\sigma/\sqrt K$ across 4 decades (§7.3, §7.10).
* Null case: known channel, no nonlinearity, noise only — exact baseline
  recovers $\hat d_\text{RMS}\sim 10^{-7}$ and
  $\sigma_\hat n/\sigma=1.000$ (§7.10).
* Static-nonlinearity sweep, PRBS-order sweep, channel-memory sweep —
  all line up on the $\min(M,N)$ collapse law (§7.6–§7.8).
* Wiener (ZOH-input) baseline calibrated against the exact baseline
  (§7.11), and the §7.9 IR prediction re-tested through the Wiener
  pipeline (§7.11.1).  The Wiener floor under ZOH is higher than the
  old Dirac-train numbers when distortion is weak and noise is
  near-zero (because regularised sinc-nulls now leak into $\hat n_W$);
  it is comparable to the old numbers when σ dominates ε_W.

**Confidence.**  The exact-baseline pipeline is fully understood —
every observed floor is predicted by an analytic model, and the
synthetic chain reaches machine epsilon when the assumptions are
met.  The Wiener (ZOH) baseline is the only non-trivial bias in
production; its magnitude is bounded by §7.11 and its operating
sweet spot is `reg=1e-6` with $n_\text{pre}=n_\text{post}\gtrsim M$.

---

## 1  Motivation

A captured serial-link waveform is the sum of several physically distinct
contributions. The textbook decomposition is

$$
r(t) = a[m]  h_0 + \sum_{k\neq m} a[k]  h_{m-k} + d(t) + n(t)
$$

evaluated at every UI's cursor sampling instant. The four terms are, in order: the **desired** cursor-only signal $a[m]  h_0$; the linear **ISI** $\sum_{k\neq m} a[k]  h_{m-k}$ from neighbouring symbols; the deterministic **distortion** $d(t)$ from any non-LTI behaviour of the channel; and the random **noise** $n(t)$ that is uncorrelated with the symbol stream.

This nugget describes the procedure used by
`optical_serdes.analysis.waveform_decomposition` to recover each of the
four components from a single captured waveform together with the known
transmitted symbol sequence. The construction generalises in two ways:

* **From-symbols mode** (`decompose_waveform`) treats the entire link
  from symbols to the probe point as one black box.
* **Per-block mode** (`decompose_block_waveform`) characterises one
  block (upstream-probe → downstream-probe) in isolation, attributing
  every joule of impairment in the result to that block alone.

The linear baseline is Wiener-Hopf channel estimation from the
[`channel-characterise`](../../../optical-serdes/.claude/skills/channel-characterise.md)
skill; the new piece is the pattern-conditioned residual averaging
that separates deterministic distortion from random noise. How wide a
symbol context that averaging needs is governed by the collapse law
$L_\text{collapse} = \min(M, N)$ derived and validated in §7.8.

Notation: lowercase Latin letters denote time-domain real signals;
boldface uppercase denotes their length-$N$ rfft transforms;
$a[k] \in \mathcal{A}$ is the transmitted symbol at UI $k$, with
alphabet $\mathcal{A} = \{-1, +1\}$ for NRZ or
$\mathcal{A} = \{-3, -1, +1, +3\}$ for PAM4; $T$ is the symbol period and
$L = T \cdot f_s$ is the integer "samples per UI" (SPS).

---

## 2  System Model

The link is modelled as

$$
y(t) = \int_{-\infty}^{\infty} h(\tau)  x(t-\tau)  d\tau + d(t) + n(t)
$$

where $x(t)$ is the LTI input driving the block under study and
$h(t)$ is the block's continuous-time impulse response.
We discretise at sample period $T_s = T/L$, write $y[t] = y(t T_s)$, and
work on a finite record of length $N$.

**Unified ZOH-input model.**  Both from-symbols and per-block modes feed
the Wiener stage the same kind of input: a continuous-time-like waveform
sampled at $L$ samples per UI.  In per-block mode that waveform is the
*measured* upstream probe.  In from-symbols mode there is no measured
upstream waveform, so the module synthesises one as the ideal NRZ /
PAM4 zero-order-hold (ZOH) staircase

$$
x_\text{ZOH}[t] \;=\; a\!\left[\lfloor t/L\rfloor\right], \quad t\in[0,N)
$$

(equivalent to `np.repeat(symbols, L)`).  This is what the transmitter
would produce if it had an ideal rectangular pulse shape and infinite
slew rate.  The choice is deliberate: it makes the recovered kernel
$\hat h$ a discrete approximation of the **channel impulse response**
$h_\text{ch}$, rather than the *single-bit response*
$\text{SBR} = h_\text{ch}\star\mathrm{rect}_T$ that the previous
Dirac-train code path returned.

| Mode            | $x[t]$                                              | $\hat h[\tau]$ recovered             |
|-----------------|-----------------------------------------------------|--------------------------------------|
| from-symbols    | synthesised ZOH staircase $x_\text{ZOH}$            | full link channel IR (symbols → probe) |
| per-block       | measured upstream probe waveform                    | block-only IR (upstream → block out)   |

**Consequence: the cursor tap is now sub-unit.**  The cursor sample
$h_0 = \hat h[L n_\text{pre}]$ is the value of the channel IR at the
cursor offset — *not* the full per-symbol gain.  For a smooth
band-limited channel the ZOH staircase already carries the per-UI
rectangle, so $h_0$ underestimates the "gain per symbol" that one
would read off the SBR.  This is by design; the multi-tap structure
of $\hat h$ is what makes the desired/ISI split clean (§4) and is
also what gets convolved with the ZOH staircase to produce
$y_\text{desired}$.  See §9.1 for the implications on the
desired/ISI cosmetic.

The ZOH input has spectral nulls at every integer multiple of the
baud rate.  At those frequencies the Tikhonov regularisation of
the Wiener filter dominates, leaving a small **broadband noise**
in $\hat h$; this is the source of the new Wiener-baseline noise
floor characterised in §7.11.

---

## 3  Linear Stage: Wiener-Hopf Channel Estimation

Steps 1–3 reuse the routine documented by
[`channel-characterise`](../../../optical-serdes/.claude/skills/channel-characterise.md);
they are summarised here only to establish notation.

### 3.1  Alignment

Cross-correlation gives the integer-sample lag

$$
\hat\tau = \arg\max_\tau \big| (y \star x)[\tau] \big|, \qquad (y \star x)[\tau] = \sum_t y[t+\tau] x[t]
$$

After alignment we work on a trimmed pair $(\tilde x[t], \tilde y[t])$
of length $N$ chosen as the largest multiple of $L$ that fits, with
$\tilde y[t] = y[t + y_\text{off}]$ and $y_\text{off} = \max(\hat\tau, 0)$.

### 3.2  Wiener-Hopf Deconvolution

With $\mathbf{X}[f] = \mathcal{F}\{\tilde x\}$ and
$\mathbf{Y}[f] = \mathcal{F}\{\tilde y\}$, the Tikhonov-regularised
deconvolution is

$$
\mathbf{H}[f] = \frac{\overline{\mathbf{X}[f]} \mathbf{Y}[f]}{|\mathbf{X}[f]|^2 + \lambda}, \qquad \lambda = \rho \overline{|\mathbf{X}|^2}
$$

with $\rho \in [10^{-5}, 10^{-3}]$ a fractional regularisation. The
length-$N$ time-domain estimate is
$h_\text{full}[\tau] = \mathcal{F}^{-1}\{\mathbf{H}\}$.

### 3.3  Windowing and Normalisation

The cursor sample is identified as
$c = \arg\max_{\tau < N/4} |h_\text{full}[\tau]|$. The windowed,
cursor-normalised IR is

$$
h_\text{win}[\tau] = \frac{h_\text{full}\big[(\tau - L n_\text{pre} + c) \bmod N\big]}{h_\text{full}[c]}, \qquad \tau \in [0, L(n_\text{pre}+n_\text{post}))
$$

so that $h_\text{win}[L n_\text{pre}] = 1$ and $\|h_\text{win}\|$ is
bounded. The "actual" IR is then $h_\text{win} \cdot \text{norm}$ with
$\text{norm} = h_\text{full}[c]$.

### 3.4  Reconstruction $\hat y$

For both modes the linear prediction is

$$
\hat{y}[t] = \mathcal{F}^{-1} \left\{ X[f] \cdot \mathcal{F}\{h_{\text{rec}}\}[f] \right\}[t]
$$

where $h_\text{rec}$ is $h_\text{win}\cdot\text{norm}$ embedded in a
length-$N$ kernel and rolled back so its cursor sits at sample
index $c$. This is the canonical $\hat y$ used by `compute_sndr`.

The **LTI residual** is

$$
e[t] = \tilde y[t] - \hat y[t]
$$

and the **classical SNDR** of the linear fit is

$$
\text{SNDR}_\text{dB} = 10 \log_{10} \frac{\langle \tilde y^2\rangle}{\langle e^2 \rangle}
$$

evaluated over a guard-trimmed window to suppress circular-edge
artefacts of $\mathcal{F}^{-1}$.

---

## 4  Linear Split: Desired + ISI

With both modes now using a continuous-time-like $x$ (measured for
per-block, ZOH-synthesised for from-symbols), the desired / ISI split
is **a single equation**:

**Boxed relation (Eq. 7):**

$$
y_\text{desired}(t) \;=\; h_0 \cdot x(t - c), \qquad y_\text{ISI}(t) \;=\; \hat y(t) - y_\text{desired}(t)
$$

where $h_0 = h_\text{win}[L n_\text{pre}] \cdot \text{norm}$ is the
cursor tap of the recovered channel IR and $c$ is the symbol→$\tilde y$
lag of §3.1.

* **From-symbols mode** — $x = x_\text{ZOH}$ (the synthetic staircase
  of §2).  $y_\text{desired}$ is *the rectangular PAM4 staircase
  scaled by the channel-IR cursor tap*; i.e. what the link would
  produce if the channel were a pure scalar gain equal to $h_0$.
  Because the staircase already carries the rectangular pulse shape,
  $h_0$ is the **channel cursor**, not the SBR cursor; for a
  smooth band-limited channel $h_0$ is therefore smaller than the
  per-symbol gain that one reads off the SBR.
* **Per-block mode** — $x$ is the measured upstream waveform.
  $y_\text{desired}$ is *what the block would produce if it were a
  perfect scalar gain $h_0$ plus its own delay $c$*.  For a
  memoryless block $y_\text{ISI} \equiv 0$ in the ideal limit (see
  §9.1 for the band-limited subtlety).

For an ideal cursor-only link ($h_\text{ch} = h_0 \cdot \delta$),
$y_\text{desired} \equiv \hat y$ and $y_\text{ISI} \equiv 0$, so this
view is invariant under "ideal channel ⇒ no ISI". Reflections,
overshoot, pulse-shape rise/fall time, and any deviation of the
channel from a single tap appear in $y_\text{ISI}$.

### 4.2  Closure

By construction, the split satisfies

$$
\hat y(t) \equiv y_\text{desired}(t) + y_\text{ISI}(t) \quad \text{(exact, up to FP rounding)}
$$

so the full four-way decomposition

$$
\tilde y(t) = y_\text{desired}(t) + y_\text{ISI}(t) + y_\text{distortion}(t) + y_\text{noise}(t)
$$

closes to machine epsilon (see §5 for the residual split). The
implementation reports `closure_rms`; it has been observed at
$10^{-17}$ – $10^{-20}$ for typical inputs.

---

## 5  Distortion / Noise Split: Pattern-Conditioned Averaging

The LTI residual $e[t]$ contains two distinct phenomena:

* **Deterministic distortion**, which is a function of the local
  symbol pattern. Examples: TX driver compression, TIA saturation,
  MZM cosine bend, supply-bounce-induced level shifts.
* **Random noise** that is uncorrelated with the symbol stream.
  Examples: thermal Johnson noise, shot noise, oscillator phase noise.

The key observation is that ensemble averaging over UIs sharing the
same local symbol context kills the random component (zero-mean by
assumption) while preserving the deterministic component.

### 5.1  UI Windows and Symbol Indexing

Let $\phi = c \bmod L$ be the within-UI cursor phase. We bin
$\tilde y$ into cursor-centred UI windows of width $L$,

$$
\mathcal{W}_{m_\text{UI}} = \big[ m_\text{UI} L + \phi - \lfloor L/2 \rfloor, m_\text{UI} L + \phi + L - \lfloor L/2 \rfloor \big)
$$

each of which contains exactly one cursor sample. Under the unified
ZOH-input model, $c$ (the lag from §3.1) is the cursor lag from the
Wiener input $x$ to $\tilde y$ — for from-symbols it is the lag from
$x_\text{ZOH}$ to $\tilde y$; for per-block it is the lag from the
measured upstream waveform to $\tilde y$.  In *both* cases that is
**not** the same as the symbol→$\tilde y$ lag, because $x$ already
carries a one-UI pulse shape and its own delay relative to the
symbol grid.

So in both modes we recover the symbol→$\tilde y$ lag $c_\text{sym}$
separately by cross-correlating a Dirac-spaced version of the symbol
train against $\tilde y$:

$$
c_\text{sym} = \arg\max_\tau \big|(\tilde y \star \mathrm{Dirac}(a))[\tau]\big|
$$

after which $m_\text{sym} = m_\text{UI} - \lfloor c_\text{sym} / L\rfloor$
and the UI grid uses $\phi = c_\text{sym} \bmod L$.  The Dirac
correlation is used **only** to locate the SBR peak for the symbol
indexing; it does not enter the Wiener fit.

### 5.2  Pattern Definition

The local symbol context at UI $m_\text{sym}$ of length $P = p_- + 1 + p_+$ is

$$
\pi_{m_\text{sym}} = \big(a[m_\text{sym} - p_-], \ldots, a[m_\text{sym}], \ldots, a[m_\text{sym} + p_+]\big) \in \mathcal{A}^P
$$

There are $|\mathcal{A}|^P$ distinct patterns; for PAM4 with $P=5$ this
is $4^5 = 1024$.

### 5.3  Conditional Mean and Distortion Estimate

For each pattern $\pi \in \mathcal{A}^P$ let
$\mathcal{M}_\pi = \{ m_\text{UI} : \pi_{m_\text{sym}} = \pi \}$, the set
of UIs sharing that context. The empirical conditional mean of the
residual restricted to UI $m_\text{UI}$ is

$$
\bar e_\pi[j] = \frac{1}{|\mathcal{M}_\pi|} \sum_{m \in \mathcal{M}_\pi} e\big[mL + \phi - \lfloor L/2\rfloor + j\big], \qquad j \in [0, L)
$$

The distortion estimate at sample $t = m_\text{UI}  L + \phi - \lfloor L/2\rfloor + j$ is

$$
\hat d(t) = \bar e_{\pi_{m_\text{sym}}}[j] \quad \text{for} \quad |\mathcal{M}_{\pi_{m_\text{sym}}}| \ge N_\text{min}
$$

$$
\hat d(t) = 0 \quad \text{for} \quad |\mathcal{M}_{\pi_{m_\text{sym}}}| < N_\text{min}
$$

and the random-noise estimate is the complementary residual

$$
\hat n(t) = e(t) - \hat d(t)
$$

The minimum-hits threshold $N_\text{min}$ (default $4$) prevents
patterns with too few observations from contaminating the distortion
estimate; their residual flows entirely into $\hat n$.

### 5.4  Statistical Properties

Under the model $e[t] = d_\pi[j] + n[t]$ with $n[t]$ zero-mean and
uncorrelated with $\pi$,

$$
\mathbb{E}\big[\bar e_\pi[j]\big] = d_\pi[j], \qquad \mathrm{Var}\big[\bar e_\pi[j]\big] = \frac{\sigma_n^2}{|\mathcal{M}_\pi|}
$$

So $\bar e_\pi$ is an *unbiased* estimator of the deterministic
distortion at the cost of a per-bin variance $\sigma_n^2 /
|\mathcal{M}_\pi|$. For $|\mathcal{M}_\pi| \gtrsim 100$ (typical at
$N_\text{sym} \cdot |\mathcal{A}|^{-P} \gtrsim 100$) this is two orders of
magnitude below $\sigma_n^2$ and $\hat d$ closely tracks the true $d$.

A useful design rule:

**Boxed rule of thumb (Eq. 18):**

$$
N_\text{sym} \gtrsim 100 \cdot |\mathcal{A}|^P
$$

for an unbiased and well-conditioned $\hat d$. PAM4 with $P=5$ asks for
$\sim 10^5$ symbols; the pkctrl3 dataset's $N_\text{sym} = 1.6 \cdot 10^5$
gives $\sim 156$ hits per pattern.

---

## 6  Scalar Metrics

All metrics are computed over a guard-trimmed evaluation region
$\mathcal{R} = [G L,  N - G L)$ with $G$ the guard in UIs. Define

$$
P_q = \frac{1}{|\mathcal{R}|} \sum_{t\in\mathcal{R}} q[t]^2, \qquad q \in \{\tilde y, y_\text{desired}, y_\text{ISI}, \hat d, \hat n, e\}
$$

Then the three SNDR-like quantities are

$$
\text{SNDR}_\text{dB} = 10 \log_{10} \frac{P_{\tilde y}}{P_e}
$$

$$
\text{SDR}_\text{dB} = 10 \log_{10} \frac{P_{\tilde y}}{P_{\hat d}}
$$

$$
\text{SNR}_\text{dB} = 10 \log_{10} \frac{P_{\tilde y}}{P_{\hat n}}
$$

Interpretation:

* **SNDR** — total LTI-fit quality. The standard channel-characterisation metric.
* **SDR**  — *deterministic floor.* The ceiling that any LTI equaliser
  reaches if all random noise is removed. The portion not reachable by
  any linear EQ; reachable in principle by Volterra / LUT / NN
  cancellation.
* **SNR**  — *random-noise floor.* The ceiling that any nonlinear
  canceller reaches if all deterministic content is removed.

These three satisfy

$$
\frac{1}{10^{\text{SNDR}/10}} = \frac{1}{10^{\text{SDR}/10}} + \frac{1}{10^{\text{SNR}/10}} + \frac{2 \langle \hat d, \hat n\rangle / |\mathcal{R}|}{P_{\tilde y}}
$$

so the gap $\min(\text{SDR}, \text{SNR}) - \text{SNDR}$ measures how
close the link is to being limited by a single mechanism.

The implementation also exports `closure_rms`,

$$
\text{closure\_rms} = \sqrt{\frac{1}{|\mathcal{R}|} \sum_{t\in\mathcal{R}} \Big(\tilde y[t] - y_\text{desired}[t] - y_\text{ISI}[t] - \hat d[t] - \hat n[t]\Big)^2}
$$

which by Eq. (9), (15), (16) is identically zero up to floating-point
rounding.

---

## 7  Synthetic Verification and New Sweep Results

The synthetic validation was expanded to stress identifiability and
conditioning, not just "single-point" correctness. The central result of
this section is the **collapse law** $L_\text{collapse} = \min(M, N)$
(§7.8): the context window needed to fully separate deterministic
distortion from noise is the smaller of the channel memory $M$ and the
source-state order $N$, bounded by data starvation. §7.1–§7.7 build up
the evidence; §7.8 states and verifies the law, and §7.9 shows the
pre-collapse floor *value* is itself predicted by the IR taps. Readers
after the punchline can jump to §7.8. §7.10 closes the loop with the dual
null case — known channel, no nonlinearity, noise only — confirming
distortion $\approx 0$ and exact noise-variance recovery up to the
$\sigma^2/K$ averaging penalty.  §7.11 calibrates the **Wiener (ZOH)
baseline** against the exact baseline: under the unified ZOH input
model, the Wiener fit error $\varepsilon_W$ splits into a small
symbol-correlated component (lands in $\hat d_W$) and a broadband
ZOH-sinc-null component (lands in $\hat n_W$); the resulting SDR
ceiling is $\sim 36$ dB at default `reg=1e-4` and $\sim 60$ dB at
`reg=1e-6`.

§7.1–§7.10 use the **exact** (oracle) linear baseline, so they are
**independent of the Dirac/ZOH choice** for the Wiener input.  Only
§7.11 and §7.11.1 exercise the Wiener path and were re-measured
under the ZOH model.

### 7.1  Current Synthetic Setup

For the controlled experiments in this report, the generator now uses:

1. **PRBS13 NRZ** source, length $N_\text{bits}=500\cdot512=256{,}000$.
2. 5th-order digital Bessel pulse at $L=8$ SPS (same construction as §3).
3. Optional weak nonlinearity:
   $y_\text{nonlinear}=\tanh(\alpha y_\text{linear})/\tanh(\alpha)$
   (typical sweep value $\alpha=0.15$).
4. Configurable AWGN $\sigma_n$.
5. Two linear-baseline modes in plotting:
   - **wiener**: $\hat y$ from Wiener deconvolution against $x_\text{ZOH}$
   - **exact**: planted pulse convolved with the symbol stream
     (oracle baseline; bypasses Wiener entirely)

The main diagnostic remains:
[`figures/synthetic_decomposition.png`](figures/synthetic_decomposition.png).

![Synthetic decomposition recovery](figures/synthetic_decomposition.png)

### 7.2  Pattern Coverage Sanity Check

To verify that finite-context averaging is statistically meaningful, we
added explicit 5-bit context histograms for the PRBS streams:

* [`figures/prbs13_5ui_sequence_histogram.png`](figures/prbs13_5ui_sequence_histogram.png)
* (historical comparison) [`figures/prbs9_5ui_sequence_histogram.png`](figures/prbs9_5ui_sequence_histogram.png)

![PRBS13 5-bit histogram](figures/prbs13_5ui_sequence_histogram.png)

These figures show that pattern occupancy is close to uniform but not
exactly identical for a finite capture, which matters for per-pattern
variance.

### 7.3  Noise Sweep at Fixed Context

The 1-D sweep
[`figures/distortion_sigma_vs_noise_sigma.png`](figures/distortion_sigma_vs_noise_sigma.png)
shows distortion-estimate sigma vs injected noise sigma (exact linear
baseline, nonlinearity off):

![Distortion sigma vs noise sigma](figures/distortion_sigma_vs_noise_sigma.png)

Result: $\sigma_{\hat d}$ scales approximately linearly with $\sigma_n$,
as expected from Eq. (17) ($\mathrm{Var}(\bar e_\pi)\propto \sigma_n^2 /
|\mathcal M_\pi|$).

### 7.4  2-D Sweep: Noise Sigma vs Context Length

The new heatmap
[`figures/distortion_error_heatmap_noise_vs_context.png`](figures/distortion_error_heatmap_noise_vs_context.png)
maps distortion RMS error over:

* x-axis: $\sigma_n \in [10^{-8},10^{-2}]$ (log-spaced)
* y-axis: context length $P=2p+1$ with $p\in\{2,\ldots,14\}$

![Distortion error heatmap](figures/distortion_error_heatmap_noise_vs_context.png)

This makes two trends explicit:

1. At fixed context, higher noise raises distortion-estimate error.
2. At fixed noise, increasing context lowers deterministic leakage until
   a floor set by finite data / edge handling / floating-point limits.

### 7.5  Context-Length Sweep at Zero Noise (Interior Region)

The figure
[`figures/distortion_error_vs_bit_sequence_no_noise.png`](figures/distortion_error_vs_bit_sequence_no_noise.png)
plots (i) distortion RMS error and (ii) estimated noise sigma vs
bit-sequence window length, **computed on the interior analyzed region
only**.

![Distortion/noise vs bit-sequence length](figures/distortion_error_vs_bit_sequence_no_noise.png)

Key finding: with PRBS13 + exact baseline + zero injected noise, both
curves collapse to machine epsilon as context approaches the PRBS order
(about 13 bits and above in this setup). This reproduces the expected
state-identifiability behavior: once the context effectively resolves
the driving sequence state, deterministic residuals are fully captured
by $\hat d$ and $\hat n\to0$.

### 7.6  Static Nonlinearity Strength vs Context

To check whether the collapse context depends on the *severity* of the
distortion, we sweep the static (memoryless) tanh compression strength
$\alpha \in \{0.05, 0.1, 0.2, 0.3, 0.4\}$ and re-run the context sweep
(5–15 UI) at exact baseline, zero noise.

* [`figures/nonlinearity_gain_context_sweep.png`](figures/nonlinearity_gain_context_sweep.png) — PRBS13.
* [`figures/nonlinearity_gain_context_sweep_prbs31.png`](figures/nonlinearity_gain_context_sweep_prbs31.png) — PRBS31, same 5–15 UI window.
* [`figures/nonlinearity_gain_context_sweep_prbs31_ctx25-35.png`](figures/nonlinearity_gain_context_sweep_prbs31_ctx25-35.png) — PRBS31 extended to 25–35 UI, chasing the PRBS31 collapse.

![Static nonlinearity gain × context sweep](figures/nonlinearity_gain_context_sweep.png)

Two findings, both as predicted:

1. **Magnitude scales, location does not.** Stronger $\alpha$ raises the
   distortion magnitude and the *pre-collapse* leftover-noise floor in
   lockstep, but the context at which the floor collapses is unchanged.
   The collapse is a property of *source-state identifiability*, not of
   how hard the nonlinearity bends.
2. **PRBS13 collapses at 13; PRBS31 does not collapse in-window.** With
   PRBS31 the floor keeps descending but never crashes to epsilon — even
   out to 35 UI — because the 31-bit state is never resolved within a
   feasible window (and the available record starves long before then,
   see §7.8).

### 7.7  Source-Order Dependence and the Identifiability Mechanism

Holding the channel and a weak nonlinearity fixed, sweeping the PRBS
order across $\{7, 9, 11, 13, 15\}$ shows the collapse context tracking
the order exactly:

[`figures/prbs_order_context_collapse_sweep.png`](figures/prbs_order_context_collapse_sweep.png)

![PRBS-order dependence of the collapse](figures/prbs_order_context_collapse_sweep.png)

Each PRBS-$N$ noise floor crashes to the floating-point floor precisely
when the context window reaches $N$ UI, and the distortion-captured
fraction hits 100 % there. The mechanism is illustrated in

[`figures/context_identifiability_intuition.png`](figures/context_identifiability_intuition.png)

![Why the collapse happens at the PRBS order](figures/context_identifiability_intuition.png)

Conditioning on $N-1$ symbols leaves one past symbol free; because the
channel is causal, that free symbol still drives the cursor distortion,
so a single context bin secretly holds **two** distinct distortion
waveforms and their conditional mean leaves a residual (the "noise"
floor). Extending the context to the full $N$ symbols pins the LFSR
state, splitting the bin into two pure groups that each collapse onto a
single waveform — residual $\to 0$.

### 7.8  The Collapse Law: Context $= \min(M, N)$

The §7.5–§7.7 results are unified by recognising **two independent
routes** to fully resolving the linear ISI by conditional averaging:

* **Cover the memory.** If the context window spans every significant
  channel tap, the distortion is determined by the in-window symbols
  regardless of the source. This needs context $\ge M$, the **channel
  memory** (effective tap span in UI).
* **Identify the source state.** For an order-$N$ PRBS, any $N$
  consecutive symbols uniquely fix the LFSR state and therefore the
  *entire* surrounding sequence — all taps, however far. This needs
  context $\ge N$, the **source-state order**, independent of $M$.

Whichever fires first wins, giving the

**Boxed collapse law:**

$$
\boxed{\;L_\text{collapse} \;=\; \min(M,\, N)\;}
$$

subject to enough data for the patterns to recur (§5.4). This is
verified by fixing the source and varying the channel memory $M$ (via
the skin + dielectric loss budget), then repeating across three sources
of increasing entropy:

| Channel memory $M$ (UI) | 3 | 7 | 9 | 13 | 51 |
|---|---|---|---|---|---|
| **PRBS9** ($N=9$) collapse | 3 | 7 | 9 | **9** | **9** |
| **IID** ($N\to\infty$) collapse | 3 | 7 | 11 | **13** | **never** |
| **PRBS31** ($N=31$) collapse | 3 | 7 | 11 | **13** | **never** |

* [`figures/channel_memory_vs_context_prbs9.png`](figures/channel_memory_vs_context_prbs9.png) — fixed PRBS9, varied $M$: points land on $\min(M, 9)$ (flat cap at $N=9$ once $M\ge 9$).
* [`figures/channel_memory_vs_context_iid.png`](figures/channel_memory_vs_context_iid.png) — IID source: $N\to\infty$, so the law degenerates to $L_\text{collapse}=M$ (the bare diagonal); the long-memory channel never collapses.
* [`figures/channel_memory_vs_context_prbs31.png`](figures/channel_memory_vs_context_prbs31.png) — PRBS31: $N=31$ exceeds both the sweep and the data-starvation wall, so it is locally indistinguishable from IID and reproduces it exactly.

![Channel memory M vs source order N — PRBS9](figures/channel_memory_vs_context_prbs9.png)

![Channel memory M vs source order N — IID](figures/channel_memory_vs_context_iid.png)

The PRBS9 panel shows the cap: channels with $M = 13$ or $51$ both
collapse at $N=9$, because identifying the 9-bit state resolves taps the
window cannot reach. Removing the state shortcut (IID, or PRBS31 over a
record far shorter than its $2^{31}-1$ period) pushes the collapse back
to $M$: $M=13$ now needs context 13, and $M=51$ never collapses.

**Data-starvation ceiling.** With a high-entropy source, conditioning on
$L$ symbols creates $2^L$ distinct patterns, each recurring
$\approx N_\text{sym}/2^L$ times. Once $2^L \gtrsim N_\text{sym}/N_\text{min}$
the bins stop recurring often enough to estimate, so the leftover noise
*rises* again past that wall (here $L\approx\log_2(256{,}000/4)\approx 16$
UI). A PRBS-$N$ source never hits this wall as long as $N$ is small,
because its distinct patterns saturate at $2^N$ rather than $2^L$ — which
is exactly why PRBS9 collapses cleanly but IID/PRBS31 degrade beyond
~16 UI.

### 7.9  The Pre-Collapse Floor is Predicted by the IR

The §7.8 *location* of the collapse is set by $\min(M,N)$; its *value*
before collapse is set quantitatively by the IR. The leftover noise at a
finite context is the first-order distortion response to the **uncovered
ISI**. At context $L = 2W+1$ the symbols outside the window contribute a
linear component

$$
u_W(t) = \sum_{|k|>W} a[m-k]\, p_k
$$

— exactly $\mathrm{conv}(a, p)$ with the pulse's central $\pm W$ UI
zeroed — and a first-order expansion of the static nonlinearity
$g(y)=\tanh(\alpha y)/\tanh(\alpha)-y$ about the covered value gives

**Boxed pre-collapse floor:**

$$
\boxed{\;\hat n_\text{RMS}(L) \;\approx\; \mathrm{RMS}\big( g'(y_\text{lin})\, u_W \big),
\qquad g'(y) = \tfrac{\alpha}{\tanh\alpha}\,\mathrm{sech}^2(\alpha y) - 1\;}
$$

This prediction uses **only the planted IR taps and the known
nonlinearity — no fit**.

[`figures/predicted_floor_vs_ir.png`](figures/predicted_floor_vs_ir.png)

![Pre-collapse floor predicted from the IR taps](figures/predicted_floor_vs_ir.png)

For three IID-driven channels ($M = 7, 13, 51$ UI) the predicted curve
(dashed) lands on the measured leftover (markers) across the entire
descent and into the collapse — e.g. for $M=13$, measured
$[2.7, 1.6, 0.99, 0.58, 0.16]\times10^{-5}$ vs predicted
$[2.8, 1.5, 0.99, 0.54, 0.17]\times10^{-5}$. Two consequences:

1. **The floor decay rate is the IR tail.** As $W$ grows, $u_W$ loses the
   taps now inside the window, so the floor falls like the square root of
   the *uncovered tap energy* $\sum_{|k|>W}p_k^2$. The right panel shows
   the symbol-spaced $|p_k|$ profiles: the long-memory channel ($M=51$)
   has the slowest-decaying tail and therefore the slowest-falling floor.
2. **Divergence pinpoints data starvation.** Measured and predicted agree
   until $L \gtrsim 16$, where the *measured* floor turns back up (the
   §7.8 starvation wall) while the IR prediction keeps falling. The gap is
   the signature that the rise is a finite-data artefact, not channel
   physics.

So the deterministic-distortion floor is fully accounted for: its
*location* by $\min(M,N)$ and its *value* by the IR taps, leaving only
genuine random noise and finite-data starvation unmodelled.

#### 7.9.1  Confirming the rise is data starvation, not channel physics

The leftover *climbs* past $\sim$16 UI in the figure above. To prove this
is the data-starvation ceiling and not a channel effect, re-run the
identical $M=51$ channel with **10× more symbols** ($N_\text{sym}$:
$256\text{k}\to2.56\text{M}$). The IR — and therefore the IR-predicted
floor — is unchanged, so any movement must be a finite-data artefact.

[`figures/predicted_floor_vs_ir_2p5M.png`](figures/predicted_floor_vs_ir_2p5M.png)

![Data-starvation wall moves with record length](figures/predicted_floor_vs_ir_2p5M.png)

| Context $L$ | leftover @256k | %UIs kept @256k | leftover @2.56M | %UIs kept @2.56M | IR-predicted |
|---|---|---|---|---|---|
| 13 | $3.2\times10^{-5}$ | 100 % | $3.2\times10^{-5}$ | 100 % | $3.2\times10^{-5}$ |
| 15 | $4.3\times10^{-5}$ | 98 % | $2.8\times10^{-5}$ | 100 % | $2.9\times10^{-5}$ |
| **17** | $\mathbf{2.3\times10^{-4}}$ | **31 %** | $\mathbf{2.5\times10^{-5}}$ | **100 %** | $2.5\times10^{-5}$ |
| 19 | $2.7\times10^{-4}$ | 1 % | $1.0\times10^{-4}$ | 87 % | $2.3\times10^{-5}$ |
| 21 | $2.7\times10^{-4}$ | 0 % | $2.5\times10^{-4}$ | 13 % | $2.1\times10^{-5}$ |

Three things confirm the mechanism:

1. **The $L=17$ climb vanishes with more data** — leftover drops $2.3\times10^{-4}\to2.5\times10^{-5}$ (9×) purely by adding symbols, and `%UIs kept` flips $31\%\to100\%$. The channel was identical, so that floor was a starvation artefact.
2. **The measured floor lands on the $N_\text{sym}$-independent IR prediction** once the data permits ($2.5\times10^{-5}$ at $L=17$, matching the prediction exactly) — the IR said where the floor *should* be; 256k was too starved to reach it, 2.56M does.
3. **The wall moves by exactly $\log_2(10)\approx 3.3$ UI** (from $\sim$16 to $\sim$19.3 UI), relocating the climb to $L=19$–$21$ where hits-per-pattern fall back through $N_\text{min}=4$. A channel-physics floor cannot move when only data is added; a starvation floor must — and does, by the predicted amount.

### 7.10  Null Case: Known Channel, No Nonlinearity, Noise Only

The dual of §7.6–§7.9 (distortion, no noise) is the pure-noise case: known
channel, $\alpha = 0$, AWGN only. The LTI residual is then *pure noise*, so
the split should return distortion $\approx 0$ and recover the injected
noise variance.

[`figures/null_case_noise_recovery.png`](figures/null_case_noise_recovery.png)

![Null-case validation: noise recovered, distortion ≈ 0](figures/null_case_noise_recovery.png)

**Panel 1 (vs injected $\sigma$, short $P=5$ context).** The estimated
noise RMS lands on the unity diagonal across three decades of $\sigma$
(recovered/injected variance $= 0.9994$), while the estimated distortion
RMS sits a factor $\sqrt{K}\approx 89$ below it and scales linearly with
$\sigma$ — i.e. it is a finite-sample artefact, not real distortion.

**Why distortion is not *exactly* zero.** With $e = n$ the per-pattern
mean of $K$ noise samples is itself random with variance $\sigma^2/K$.
Power conservation $P_e = P_{\hat d} + P_{\hat n}$ then splits as

$$
P_{\hat d} = \frac{\sigma^2}{K}, \qquad
P_{\hat n} = \sigma^2\Big(1 - \frac{1}{K}\Big), \qquad
K = \frac{N_\text{analysed}}{N_\text{patterns}}
$$

so the distortion soaks up exactly the fraction $1/K$ of the noise and the
noise estimate is biased *low* by the same $1/K$. This is Eq. (17)/§5.4
made concrete: $\hat d$ is unbiased ($\mathbb E[\bar e_\pi]=0$ here) with
per-bin variance $\sigma^2/|\mathcal M_\pi|$.

**Panel 2 (vs context, fixed $\sigma$).** Sweeping $P$ with an IID source,
the residual mis-split fraction — equivalently the distortion power
*and* the noise-variance deficit, which are equal by power conservation —
tracks the prediction $1/K = 2^P/N_\text{analysed}$ across three decades:
$3\times10^{-5}$ at $P=3$ rising to $3.2\times10^{-2}$ at $P=13$. The
engineering rule follows directly: **when only the noise floor is of
interest, use the shortest context that still covers the channel memory**
($P \gtrsim M$, §7.8) — every extra UI of context beyond that trades real
noise for spurious distortion at rate $1/K$.

### 7.11  Wiener vs Exact Linear Baseline (ZOH input model)

Every validation in §7.1–§7.10 used the **exact** (oracle) planted IR
as the linear baseline.  Real captures use the **Wiener** estimate via
[`estimate_channel`](../../../optical-serdes/src/optical_serdes/utils/channel_estimation.py),
which under the unified ZOH input model (§2) returns the channel IR
$\hat h_\text{ch}$.  Its fit error
$\varepsilon_W = \hat y_\text{exact}-\hat y_\text{Wiener}$ is a mix of
*deterministic, symbol-correlated* content (pattern averaging will push
this into $\hat d_W$) and *broadband, symbol-uncorrelated* content from
the ZOH input's sinc nulls (pattern averaging leaves this in $\hat n_W$).
This section calibrates the leakage of each with a synthetic where
ground truth is known: $y = y_\text{lin}+d_\text{true}+n_\text{true}$
is decomposed twice on the same alignment grid (PRBS13, weak tanh
$\alpha=0.1$ giving $d_\text{true,RMS}\approx 4.7\times10^{-4}$, 51-UI
Wiener IR window).

[`figures/wiener_vs_exact_baseline.png`](figures/wiener_vs_exact_baseline.png)

![Wiener vs exact baseline](figures/wiener_vs_exact_baseline.png)

**Panel A — vs injected $\sigma$, in-window channel ($M=7$ UI), default
reg $=10^{-4}$.**  The exact-baseline distortion error scales linearly
with $\sigma$ (the $\sigma/\sqrt{K}$ averaging artefact, §7.10) and stays
well below $d_\text{true,RMS}$.  The Wiener distortion error sits at a
floor of $\sim 1.5\times10^{-2}$ — about **30× the true distortion RMS**
— and is ~independent of $\sigma$.  The noise-variance ratio
$\text{var}(\hat n_W)/\sigma^2$ tells the new story: at low $\sigma$ the
Wiener-noise component of $\varepsilon_W$ dwarfs the AWGN, inflating
$\hat n_W$ by factors of hundreds; once $\sigma\gtrsim\varepsilon_W$
($\sigma\gtrsim 3\times10^{-2}$ here) the ratio is back to ~unity.

| $\sigma$ | $\varepsilon_W$ RMS | $d_\text{err}$ (exact) | $d_\text{err}$ (Wiener) | $\text{var}(\hat n_W)/\sigma^2$ |
|---|---|---|---|---|
| $10^{-4}$ | $1.58\times10^{-2}$ | $2.0\times10^{-5}$ | $1.53\times10^{-2}$ | **1639** |
| $10^{-3}$ | $1.58\times10^{-2}$ | $3.0\times10^{-5}$ | $1.52\times10^{-2}$ | **17.4** |
| $10^{-2}$ | $1.57\times10^{-2}$ | $2.2\times10^{-4}$ | $1.51\times10^{-2}$ | **1.17** |
| $10^{-1}$ | $1.86\times10^{-2}$ | $2.2\times10^{-3}$ | $1.48\times10^{-2}$ | **1.01** |

This is the principal qualitative change from the old Dirac-train
factorization: under Dirac drive, $\varepsilon_W$ was almost entirely
symbol-correlated (cursor-tap bias) and pattern averaging absorbed
~100 % of it into $\hat d_W$, leaving $\hat n_W$ clean.  Under the ZOH
drive, $\varepsilon_W$ now has a broadband component from the sinc
nulls — *this is why $\hat n_W$ no longer tracks $\sigma$ at low SNR*.

**Panel B — fixed $\sigma=10^{-2}$, sweep channel memory $M$.**  With
the 51-UI Wiener window, $M\in\{7,13,25,51\}$ UI all fit (the longest
just barely):

| $M$ | $\varepsilon_W$ RMS | $d_\text{err}$ (Wiener) | $\text{var}(\hat n_W)/\sigma^2$ | $d_\text{true,RMS}$ |
|---|---|---|---|---|
| 7  | $1.62\times10^{-2}$ | $1.57\times10^{-2}$ | 1.18 | $4.6\times10^{-4}$ |
| 13 | $1.33\times10^{-2}$ | $1.27\times10^{-2}$ | 1.14 | $5.4\times10^{-4}$ |
| 25 | $1.06\times10^{-2}$ | $1.01\times10^{-2}$ | 1.09 | $6.5\times10^{-4}$ |
| 51 | $9.11\times10^{-3}$ | $6.17\times10^{-3}$ | 1.44 | $1.1\times10^{-3}$ |

Unlike the old Dirac-train numbers (where $\varepsilon_W$ was flat in
$M$), the ZOH ε_W *decreases* with $M$.  Intuition: a longer
channel has more energy at low frequencies and less at the ZOH's
spectral nulls, so the regularised-noise component of $\varepsilon_W$
shrinks.  At $M=51$ (right at the window edge) IR truncation starts
to leak unstructured energy into $\hat n_W$
($\text{var}(\hat n_W)/\sigma^2:1.18\to1.44$) — the symbol-correlated
component drops but the broadband component creeps back up.

**Panel C — sweep Wiener Tikhonov regularisation `reg` (in-window, fixed
$\sigma=10^{-2}$).**  The `reg`-sweep pins the mechanism:

| `reg` | $h_0$ (W) | $\varepsilon_W$ RMS | $d_\text{err}$ (Wiener) | $\text{var}(\hat n_W)/\sigma^2$ |
|---|---|---|---|---|
| $10^{-3}$ | 0.503 | $6.04\times10^{-2}$ | $6.02\times10^{-2}$ | 1.30 |
| $10^{-4}$ **(default)** | 0.631 | $1.57\times10^{-2}$ | $1.51\times10^{-2}$ | 1.17 |
| $10^{-5}$ | 0.687 | $4.32\times10^{-3}$ | $2.81\times10^{-3}$ | 1.11 |
| $10^{-6}$ **(recommended)** | 0.707 | $2.98\times10^{-3}$ | $8.68\times10^{-4}$ | 1.08 |
| $10^{-7}$ | 0.713 | $2.59\times10^{-3}$ | $9.82\times10^{-4}$ | 1.06 |
| $10^{-8}$ | 0.714 | $3.31\times10^{-3}$ | $1.07\times10^{-3}$ | 1.10 |

The `reg`-sweep shrinks $\varepsilon_W$ to a floor of
$\sim 2.6\times10^{-3}$ around `reg`$=10^{-7}$; below that
noise-amplification re-inflates it.  The optimum
*distortion-recovery* point is `reg`$=10^{-6}$, giving
$d_\text{err,W}\approx 9\times10^{-4}$ — a **17×** improvement on
the default reg.  The noise-variance ratio also pulls in toward
unity (1.17 → 1.08).

In ratio terms against signal RMS $\approx 0.95$, the achievable
SDR ceilings are roughly:

| `reg` | $d_\text{err,W}$ | SDR ceiling |
|---|---|---|
| $10^{-3}$ | $6.0\times10^{-2}$ | 24 dB |
| $10^{-4}$ | $1.5\times10^{-2}$ | 36 dB |
| $10^{-5}$ | $2.8\times10^{-3}$ | 51 dB |
| $10^{-6}$ | $8.7\times10^{-4}$ | 60 dB |
| $10^{-7}$ | $9.8\times10^{-4}$ | 60 dB |

So the **Wiener-baseline SDR ceiling** is $\sim 36$ dB at default reg
and $\sim 60$ dB at `reg=1e-6`.  These numbers replace the old "40 dB
@ reg=1e-4, 60 dB @ reg=1e-6, $\sim -20\log_{10}(\text{reg})$ dB" rule
of thumb from the Dirac-train factorization — the ceiling at default
reg has dropped by $\sim 4$ dB because more of $\varepsilon_W$ now
leaks into $\hat n_W$ rather than fully landing in $\hat d_W$.

> Aside on $h_0$: the reported Wiener cursor tap settles around 0.71
> as reg shrinks.  This is **not** a residual bias — it is the cursor
> sample of the channel IR $h_\text{ch}$, which for this PAM4 / NRZ
> setup with a 5th-order Bessel pulse and a smooth electrical channel
> is intrinsically below unity (the planted pulse has peak 1 spanning
> several samples; deconvolving by the rectangular ZOH spreads that
> peak over $L$ samples, leaving the cursor at ~$1/L$ times an
> integrated weight).  The OLD Dirac-train factorization recovered
> $h_0\approx 1$ because it returned the SBR cursor, not the IR
> cursor.

**Operating guidance (closes the §1 motivation):**

* For coarse measurements where the *real* SDR is far below 35 dB, the
  default `reg=1e-4` is fine — the Wiener floor is well under the signal.
* For fine measurements (SDR target 35–60 dB), **lower `reg` to
  $10^{-6}$** *when the channel comfortably fits the Wiener window*
  (§7.11.1); $d_\text{err,W}$ drops by 17× and
  $\text{var}(\hat n_W)/\sigma^2$ pulls into unity.
* For **noise-variance recovery**, require $\sigma\gtrsim\varepsilon_W$
  — i.e. for `reg=1e-6` the trusted floor is $\sigma\gtrsim 3\times10^{-3}$
  (RMS).  Below that, the broadband Wiener noise dominates $\hat n_W$.
* The §7.8 collapse law and §7.9 IR-prediction were validated against the
  exact baseline and are unchanged.  Under the Wiener baseline, the
  pre-collapse floors in those experiments are **clipped from below**
  at $\varepsilon_W$; collapse locations are unaffected.
* The **exact-baseline** path remains the right tool for any quantitative
  ground-truth synthetic validation.

### 7.11.1  §7.9 IR-prediction under the Wiener (ZOH) baseline

§7.9 validated the IR-predicted leftover-noise floor against the exact
baseline; §7.11 calibrated the Wiener clip at default reg.  Tying the two
together: can the Wiener pipeline recover the §7.9 descent if we use the
recommended low reg?  Re-running the §7.9 measurement (IID source, weak
tanh $\alpha=0.05$, no noise, 51-UI Wiener IR window) at both
`reg`$=10^{-4}$ and `reg`$=10^{-6}$ for two channels — $M=7$ UI (well
in-window) and $M=51$ UI (right at the window edge) — gives:

[`figures/predicted_floor_wiener_recovers_ir.png`](figures/predicted_floor_wiener_recovers_ir.png)

![Wiener IR recovery (ZOH model)](figures/predicted_floor_wiener_recovers_ir.png)

| channel | `reg` | $\varepsilon_W$ RMS | floor at $L=3$ | floor at $L=15$ |
|---|---|---|---|---|
| $M=7$ (in-window) | $10^{-4}$ | $4.2\times10^{-3}$ | $4.0\times10^{-3}$ | $3.6\times10^{-3}$ |
| $M=7$ (in-window) | $10^{-6}$ | $1.4\times10^{-3}$ | $1.4\times10^{-3}$ | $1.3\times10^{-3}$ |
| $M=51$ (window-edge) | $10^{-4}$ | $6.6\times10^{-3}$ | $6.6\times10^{-3}$ | $6.2\times10^{-3}$ |
| $M=51$ (window-edge) | $10^{-6}$ | $6.4\times10^{-3}$ | $6.4\times10^{-3}$ | $6.0\times10^{-3}$ |

This is the corner of the experiment design where the ZOH model
loses the most ground to the old Dirac-train code: with σ=0 and a
weak nonlinearity, the only thing in the Wiener residual is the
ZOH sinc-null noise itself.  Pattern averaging cannot capture that
broadband component, so essentially the entire $\varepsilon_W$ now
appears as leftover (the Wiener curves in the figure are *flat in
$L$* at the $\varepsilon_W$ level — no descent at all).  For
comparison, the old Dirac-train numbers had a much smaller
$\varepsilon_W$ in this regime ($\sim 8\times10^{-4}$ at reg=1e-4,
$\sim 10^{-4}$ at reg=1e-6) **and** pattern averaging absorbed
~90 % of it into $\hat d_W$, so the old leftover was $\sim 10^{-4}$
range — 10–30× lower than the new numbers.

That sounds like a regression, and in this synthetic corner it is.
But it is a *physical* one — the old number was wrong in two ways
at once:

1. It returned the SBR cursor, not the channel IR cursor, so $h_0$
   reflected the full per-symbol gain (this is what the user
   asked us to fix).
2. Its $\varepsilon_W$ was symbol-correlated (cursor-tap bias under
   Dirac drive) so it cleanly landed in $\hat d_W$ — but that
   meant any *real* distortion below $\varepsilon_W$ was
   indistinguishable from the Wiener bias.

The new model has a higher leftover *floor* but a lower bias on
$\hat d_W$ — the Wiener bias is now mostly broadband noise, not a
synthetic distortion comb, and lowering reg removes it.  Two regimes:

* **In-window $M$ (left panel).**  Lowering reg from $10^{-4}$ to $10^{-6}$
  drops the Wiener floor ~3× (from $\sim 4\times10^{-3}$ to $\sim
  1.4\times10^{-3}$), consistent with the noise-amplification model of
  §7.11 Part C.  At reg=1e-6 the floor is still 100× above the IR
  prediction (which descends to $\sim 10^{-5}$ by $L=7$); there is no
  reg low enough to push the ZOH sinc-null noise below that.  The exact
  baseline remains the only path that follows the prediction to machine
  epsilon.
* **Near-window $M$ (right panel).**  When $M$ approaches the Wiener
  window length, **IR truncation** dominates $\varepsilon_W$ — both reg
  values give an identical floor of $6.4\times10^{-3}$, flat in $L$.
  Tightening reg cannot recover the missing IR tail.

So the Wiener floor is set by the larger of two independent terms:

| failure mode | symptom | fix |
|---|---|---|
| ZOH sinc-null noise | $\varepsilon_W$ shrinks with `reg`, bottoms out at `reg=1e-7`; broadband, leaks into $\hat n_W$ | lower `reg` (§7.11 Panel C) — bottoms out at $\sim 2.6\times10^{-3}$ in this setup |
| IR truncation | $\varepsilon_W$ independent of `reg`, scales with channel energy beyond window | **widen the Wiener window** ($n_\text{pre}, n_\text{post}$ each $\gtrsim M$) |

For pkctrl3-class channels (skin-and-dielectric $\sim 5$–$10$ dB,
$M\lesssim 20$–$30$ UI), the default 51-UI window covers $M$ comfortably
and lowering reg is the productive lever.  If a longer channel pushes $M$
toward the window edge, widen the window first — *then* tighten reg.

**Practical implication.**  When the goal is precision **distortion
recovery** of structure above $\sim 10^{-3}$ RMS (i.e. real captures
with anything resembling realistic σ), the new ZOH model with
`reg=1e-6` is sufficient and physically correct.  When the goal is
to chase the IR-predicted descent of leftover noise below
$\sim 10^{-3}$, only the **exact baseline** (oracle IR) gets you
there under either factorization — and the new factorization is
honest about it.

---

## 8  Worked Example: pkctrl3 PAM4 at 106.25 GBaud

The pkctrl3 dataset is a 160 000 UI PAM4 capture with seven probe
points along the link (TX → DRV_OUT → MZM_IN → Pout → Pin_PD → TIA_OUT
→ RX_CH_OUT → RX_IN). Running
`examples/waveform_decomposition_demo.py` reproduces both flavours of
the decomposition.

> **Pre-ZOH-change snapshot.**  The numbers in §8.1 below were computed
> under the *old* Dirac-train factorization.  Under the new ZOH input
> model (§2):
>
> * **Per-block** results (§8.2, §8.3) are **unchanged**.  The
>   per-block code path has always used the measured upstream waveform
>   as $x$, so the ZOH change is a no-op there.
> * **From-symbols** results (§8.1) will **shift modestly**.  The
>   Wiener residual differs because the ZOH input has sinc nulls (§2)
>   that the Dirac drive did not.  SNDR (which sees only the residual
>   magnitude) is expected to be similar; SDR and SNR will re-split
>   because the symbol-correlated vs broadband content of
>   $\varepsilon_W$ rebalances.  The desired/ISI cosmetic will also
>   look different — $h_0$ is now the channel-IR cursor, so it is
>   sub-unit and $y_\text{ISI}$ carries more weight (this is the
>   §9.1 cosmetic, not a real defect).  Re-running on the pkctrl3
>   dataset is needed to refresh the precise numbers; it has not
>   been done in this round because the dataset is not in the
>   current workspace.

### 8.1  From-Symbols, TIA_OUT  *(pre-ZOH snapshot)*

![From-symbols decomposition at TIA_OUT](figures/pkctrl3_from_symbols_tia_out.png)

Result *(old Dirac path)*: SNDR = 19.76 dB, SDR = 29.58 dB,
SNR = 20.24 dB, closure = $4.4\cdot10^{-18}$. This reproduces the
from-symbols TIA_OUT SNDR of 19.70 dB published in the
`channel-characterise` skill's worked example.

What's new is the SDR/SNR split: SDR − SNR = 9.3 dB, so TIA_OUT's link
floor is dominated by random noise (~$8\times$ more than deterministic
distortion). A perfect nonlinear canceller would reach SNR = 20.2 dB,
only 0.5 dB above the current SNDR — a small target.

The §7.11 calibration tells us how to read this in light of the
ZOH change: TIA_OUT's measured SDR (29.6 dB) is well *below* the
ZOH Wiener-baseline ceiling at default reg (~36 dB) and far below
the `reg=1e-6` ceiling (~60 dB), so the SDR reading is
measurement-limited, not Wiener-bias-limited.  The headline
distortion-vs-noise verdict is therefore expected to survive the
re-run; expect a small numerical shift in SDR/SNR (a few tenths
of a dB), not a sign flip.

### 8.2  Per-Block, MZM and PD+TIA

![Per-block decomposition at Pin_PD → TIA_OUT](figures/pkctrl3_per_block_pin_to_tia.png)

Per-block view of the TIA alone. The middle panel's $y_\text{desired}$
is small relative to $y_\text{ISI}$ — see §9.1 — but this is the
expected band-limited cursor-tap behavior, not a real signal-loss
defect. The bottom panel reveals the genuine distortion vs noise
character of the block.

![Per-block decomposition at MZM_IN → Pout](figures/pkctrl3_per_block_mzm_to_pout.png)

The MZM block: SDR = 36.8 dB, SNR = 40.7 dB. Here SDR < SNR, so
*deterministic distortion dominates noise* — the cosine bend's
fingerprint. This is the only block in the chain where nonlinear
cancellation (LUT or analytic inversion of the cosine) would buy more
than ~0.5 dB.

### 8.3  Cross-Block Summary

![Per-block bar chart](figures/pkctrl3_block_comparison.png)

Comparison across the three analysed blocks:

| Block                | SNDR (dB) | SDR (dB) | SNR (dB) | dominated by    |
|----------------------|-----------|----------|----------|-----------------|
| MZM (IN→Pout)        | 35.4      | 36.8     | 40.7     | **distortion**  |
| PD + TIA (Pin→TIA_OUT) | 22.8    | 32.6     | 23.3     | random noise    |
| RX channel (TIA→RX_CH_OUT) | 26.6 | 48.0   | 26.6     | random noise    |

The bar chart makes the engineering tradeoff explicit: the MZM is the
only block where deterministic-distortion budget is the binding
constraint; the rest of the chain is random-noise-limited and would
benefit from a quieter front end before a nonlinear canceller is added.

---

## 9  Limitations and Caveats

1. **Band-limited cursor-tap and the Wiener-baseline SDR floor (ZOH
   model).** Eq. (7)'s $h_0$ is the *cursor sample* of the recovered
   channel impulse response under a ZOH input — *not* the cursor
   sample of the single-bit response and *not* the block's true scalar
   per-symbol gain.  For a smooth band-limited channel and the
   default `reg=1e-4`,
   [`estimate_channel`](../../../optical-serdes/src/optical_serdes/utils/channel_estimation.py)
   gives an $h_0$ that sits well below unity (e.g. 0.63 for the
   reference Bessel-channel test in §7.11) because the ZOH input
   already carries the rectangular pulse shape; the per-symbol gain
   would be the *integral* of $\hat h$ across the UI, not the
   single-sample $h_0$.

   The Wiener fit error
   $\varepsilon_W = \hat y_\text{exact}-\hat y_\text{W}$ under ZOH
   drive has **two distinct components**:

   * *Symbol-correlated cursor-tap effect.*  The Wiener cursor tap of
     $\hat h_\text{ch}$ is biased by a regularisation-dependent amount.
     This component is correlated with the local symbol and is
     attributed by pattern averaging to $\hat d_W$.  Magnitude at
     default reg: a small fraction of $\varepsilon_W$.
   * *Broadband Wiener noise from ZOH sinc nulls.*  The ZOH input has
     spectral nulls at integer baud-rate harmonics.  Tikhonov
     regularisation dominates there, returning a small broadband noise
     in $\hat h_\text{ch}$ and therefore in $\hat y_W$.  This component
     is symbol-uncorrelated and lands in $\hat n_W$.  Magnitude at
     default reg: the bulk of $\varepsilon_W$.

   Two distinct consequences:

   * *Cosmetic effect on the desired/ISI split.*  $h_0 \ll 1$ and a
     non-zero $y_\text{ISI}$ appears even for a memoryless block.
     This is an artefact of the cursor-tap split applied to a
     channel IR; the total LTI fit $\hat y$ and the SNDR / closure
     are unaffected.
   * *Quantitative effect on $\hat d$ and $\hat n$.*  Pattern
     averaging absorbs the symbol-correlated piece into $\hat d_W$
     and leaves the broadband piece in $\hat n_W$.  The §7.11 data
     give an **SDR ceiling of $\sim 36$ dB at `reg=1e-4`** and
     $\sim 60$ dB at `reg=1e-6`, and a **noise-variance bias** that
     inflates $\text{var}(\hat n_W)/\sigma^2$ for $\sigma$ comparable
     to or smaller than $\varepsilon_W$.  Lower `reg` to $10^{-6}$
     for SDR target $\gtrsim 50$ dB; below `reg`$\sim 10^{-7}$ a
     noise-amplification floor takes over.

   An alternative split is the projection coefficient
   $g_\text{eff} = \langle \hat y, x\rangle / \langle x, x\rangle$,
   which recovers the true per-symbol scalar gain for memoryless
   blocks but conflates correlated ISI taps with gain.  The module
   chooses cursor-tap by default because the multi-tap ISI structure
   is preserved cleanly (important for real TIA-style blocks with
   actual postcursor memory).

2. **Pattern context vs. nonlinear memory and sequence state.** Eq. (15)
   bins on a finite symbol window. If context is too short, deterministic
   structure leaks into $\hat n$. The context needed to capture all of it
   follows the collapse law $L_\text{collapse} = \min(M, N)$ (§7.8): the
   smaller of the **channel memory** $M$ and the **source-state order**
   $N$. PRBS-driven synthetic tests can collapse early via state
   identifiability (the $N$ route), masking the true channel memory;
   IID or long-PRBS drives remove that shortcut and expose $M$ directly,
   but are then bounded by the data-starvation ceiling
   $2^P \lesssim N_\text{sym}/N_\text{min}$. For real captures (effectively
   high-entropy sources) choose $P$ to cover the dominant memory $M$, and
   verify with context sweeps (§7.4–§7.8).

3. **Pattern sparsity.** Eq. (18) is a soft floor. For PAM4 with
   $P=7$ ($4^7 = 16{,}384$ patterns), the pkctrl3 capture only delivers
   ~10 hits per pattern, marginal for stable averaging. Either reduce
   $P$ or increase capture length; the module reports
   `pattern_uis_kept` so the user can see how many UIs survived
   $N_\text{min}$.

4. **Negative alignment lag is not supported.** If the captured $y$
   arrives *before* $x$ in time (rare, requires deliberate misalignment),
   the routines raise `NotImplementedError`. Pre-pad with leading zeros
   or pre-trim to enforce positive lag.

5. **Linear baseline assumes time-invariance.** Slow drift in the
   channel (thermal, supply, etc.) appears as a long-memory pattern
   correlated with no symbol pattern and lands in $\hat n$. For DCD or
   slow gain wander, a more elaborate Volterra estimate of $\hat d$
   would be needed.

6. **Interior vs full-wave metrics.** `_pattern_average_distortion`
   populates $\hat d$ only on valid cursor-centered UI windows. Samples
   outside that analyzed span are left at zero in $\hat d$, so full-wave
   `std(ŷ_noise)` can be dominated by edge regions. For context-sweep
   diagnostics, report interior-only metrics (as in §7.5) unless edge
   behaviour is explicitly the quantity of interest.

---

## 10  Module Reference

* [`decompose_waveform(y, symbols, …)`](../../../optical-serdes/src/optical_serdes/analysis/waveform_decomposition.py)
  — from-symbols mode (§4.1).
* [`decompose_block_waveform(x, y, symbols, …)`](../../../optical-serdes/src/optical_serdes/analysis/waveform_decomposition.py)
  — per-block mode (§4.2).
* `WaveformDecomposition` — result dataclass containing every component
  waveform, the underlying `ChannelEstimate`, and a
  `DecompositionMetrics` block with all scalar metrics from §6.
* `plot_decomposition(decomp, …)` — three-panel Plotly figure
  (LTI fit, desired/ISI, distortion/noise) used in the pkctrl3 figures
  above.

The pattern-conditioned distortion / noise machinery is fully reused
between modes; only the linear split (§4) and the
symbol→$\tilde y$ cursor (§5.1) differ.

The example workflow lives at
[`examples/waveform_decomposition_demo.py`](../../../optical-serdes/examples/waveform_decomposition_demo.py)
and the test suite at
[`tests/test_analysis/test_waveform_decomposition.py`](../../../optical-serdes/tests/test_analysis/test_waveform_decomposition.py)
covers closure, LTI-fit quality, distortion recovery, validation, and
the surface invariants of `WaveformDecomposition`.

---

## 11  References

1. **`channel-characterise` skill** —
   [`.claude/skills/channel-characterise.md`](../../../optical-serdes/.claude/skills/channel-characterise.md).
   Documents the Wiener-Hopf channel-estimation primitives this module
   builds on (steps 1–3 of §3).
2. Jeruchim, Balaban, Shanmugan, *Simulation of Communication Systems*,
   2nd ed., Kluwer 2000. §5.4 derives the characteristic-function PDF
   convolution that motivates the per-pattern averaging form in §5.
3. Proakis, *Digital Communications*, 4th ed., McGraw-Hill 2001,
   Ch. 10 — exact BER for ISI channels via pattern enumeration; the
   same pattern grouping is the basis of Eq. (14).
4. Forney, "Maximum-Likelihood Sequence Estimation of Digital Sequences
   in the Presence of Intersymbol Interference," *IEEE Trans. Inf.
   Theory*, vol. 18, no. 3, pp. 363–378, 1972 — foundational
   enumeration of ISI pattern combinations.
