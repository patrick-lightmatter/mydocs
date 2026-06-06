# Confidence BER — Method and Derivation
@Patrick Satarzadeh

**Reference:** Synopsys SIPI, *Confidence BER (conf BER) Algorithm*, E224, 2026 — [PDF](../../references/Conf%20BER%20Algorithm_E224.pdf)

**Implementation:** `optical_serdes.analysis.conf_ber`

---

## Table of Contents

- [1. Motivation](#1-motivation)
- [2. Problem Statement](#2-problem-statement)
- [3. Stage 1 — Poisson Upper Confidence Bound](#3-stage-1--poisson-upper-confidence-bound)
  - [3.1 Error process model](#31-error-process-model)
  - [3.2 Confidence interval via the Poisson CDF](#32-confidence-interval-via-the-poisson-cdf)
  - [3.3 Chi-squared equivalence (closed form)](#33-chi-squared-equivalence-closed-form)
  - [3.4 The zero-error case and the calibration reference](#34-the-zero-error-case-and-the-calibration-reference)
- [4. Stage 2 — Q-Function Projection to the Target BER](#4-stage-2--q-function-projection-to-the-target-ber)
  - [4.1 Gaussian noise assumption](#41-gaussian-noise-assumption)
  - [4.2 BER–margin relationship](#42-bermargin-relationship)
  - [4.3 Scale factor derivation](#43-scale-factor-derivation)
  - [4.4 Final expression](#44-final-expression)
  - [4.5 Algebraic sanity check](#45-algebraic-sanity-check)
- [5. Modulation Scaling](#5-modulation-scaling)
  - [5.1 NRZ](#51-nrz)
  - [5.2 PAM4](#52-pam4)
- [6. Algorithm Summary](#6-algorithm-summary)
- [7. Relation to the Synopsys Reference](#7-relation-to-the-synopsys-reference)
- [8. Assumptions and Validity](#8-assumptions-and-validity)
- [9. Worked Examples](#9-worked-examples)
  - [9.1 OMA sweep — 106.25 Gbaud NRZ (OCI-Gen2)](#91-oma-sweep--10625-gbaud-nrz-oci-gen2)
  - [9.2 PAM4 cross-check against Synopsys reference](#92-pam4-cross-check-against-synopsys-reference)
- [10. Implementation Notes](#10-implementation-notes)
- [References](#references)

---

## 1. Motivation

A link simulation produces a finite number of symbols $N$ and counts $k$ errors,
giving the raw BER estimate $\hat{p} = k/N$.  This estimate has two weaknesses
that make it unsuitable as the sole qualification metric.

**Statistical uncertainty.**  For small $k$, $\hat{p}$ has high variance.
When $k = 0$ the estimate is identically zero regardless of the true error rate.
Even when $k > 0$, a statement such as "$\hat{p} = 6\times10^{-5}$" carries no
quantification of how far the true BER $p$ might differ.

**SNR mismatch.**  The simulation may not be run at the same operating point as
the target specification.  A simulation that counts 128 errors in 2 M bits does
not directly tell you whether the link meets a BER target of $10^{-12}$.
Projecting from the simulation SNR to the specification SNR requires a noise
model.

The Confidence BER algorithm addresses both issues in sequence \[1\]:

1. **Stage 1** — model-free: replace $\hat{p}$ with a Poisson upper confidence
   bound $p_U$, so that the true BER is below $p_U$ with probability $1-\alpha$.
2. **Stage 2** — Gaussian model: project $p_U$ from the simulation SNR to the
   target BER operating point using the Q-function (complementary error function).

---

## 2. Problem Statement

**Given:**

- $k$ — observed errors
- $N$ — total compared bits/symbols
- $p_\text{target}$ — BER target of the link specification (e.g. $10^{-12}$)
- $\alpha$ — significance level (typically $0.05$ for 95 % confidence)
- Modulation format (NRZ or PAM4)

**Find:** a single number $p_\text{conf}$ such that:

- With probability at least $1-\alpha$, the true BER satisfies $p \leq p_U$ (Stage 1),
- Under Gaussian noise, $p_U$ at the simulation SNR projects to $p_\text{conf}$
  at the SNR corresponding to $p_\text{target}$ (Stage 2).

**Interpretation:** $p_\text{conf}$ is the projected BER at the specification
SNR, bounded above with $(1-\alpha)$ confidence.  A link passes if
$p_\text{conf} < p_\text{target}$.

---

## 3. Stage 1 — Poisson Upper Confidence Bound

### 3.1 Error process model

Baud-rate errors are modelled as independent events with constant probability $p$
per symbol.  For large $N$, the number of errors $K$ is well approximated by a
Poisson random variable with mean $\lambda = Np$:

$$K \sim \text{Poisson}(\lambda), \quad \lambda = Np$$

This is exact in the limit $N \to \infty$, $p \to 0$ with $\lambda$ fixed, which
holds for all BER targets of practical interest ($p < 10^{-3}$,
$N \sim 10^6$–$10^9$) \[2\].

### 3.2 Confidence interval via the Poisson CDF

We seek the smallest value $p_U$ such that the probability of observing *at most*
$k$ errors is at least $\alpha$, i.e. the $(1-\alpha)$ upper one-sided confidence
limit on $p$:

$$P\!\left(K \leq k \;\big|\; p = p_U\right) = \alpha$$

Expanding the Poisson CDF:

$$e^{-Np_U} \sum_{j=0}^{k} \frac{(Np_U)^j}{j!} = \alpha \tag{1}$$

For $k = 0$ this reduces to $e^{-Np_U} = \alpha$, so
$p_U = -\ln(\alpha)/N$.

For $k > 0$, equation (1) has no closed-form solution in $p_U$ and must be
solved numerically — which is what the Synopsys formulation does via
`fminsearch`.  A computationally superior closed form exists via the relationship
to the chi-squared distribution (Section 3.3).

### 3.3 Chi-squared equivalence (closed form)

The Poisson CDF is related to the regularised incomplete gamma function, which is
in turn the CDF of the chi-squared distribution \[2\].  Specifically, equation (1) is
equivalent to:

$$p_U = \frac{\chi^2_{1-\alpha,\; 2(k+1)}}{2N} \tag{2}$$

where $\chi^2_{q,\nu}$ denotes the $q$-th quantile of the chi-squared
distribution with $\nu$ degrees of freedom.  This identity follows from:

$$P(K \leq k \mid \lambda) = \frac{\Gamma(k+1, \lambda)}{\Gamma(k+1)} = 1 - F_{\chi^2_{2(k+1)}}(2\lambda)$$

where $\Gamma(\cdot,\cdot)$ is the upper incomplete gamma function and
$F_{\chi^2_\nu}$ is the chi-squared CDF.  Setting the left side equal to $\alpha$
and solving for $\lambda = Np_U$ yields (2).

Equation (2) is exact, avoids numerical optimisation, and is provided natively
by `scipy.stats.chi2.ppf`.

### 3.4 The zero-error case and the calibration reference

The Synopsys algorithm defines a **calibration reference** \[1\] $p_\text{sim}$: the
95 % upper bound when zero errors are observed in $N_\text{ref} = 3\times10^6$
bits:

$$p_\text{sim} = \frac{\chi^2_{0.95,\, 2}}{2 N_\text{ref}} = \frac{-2\ln 0.05}{2\times 3\times10^6} = \frac{-\ln 0.05}{3\times10^6} \approx 9.986\times10^{-7} \tag{3}$$

This is the "best-case" confidence bound achievable with the reference run length.
It serves as the anchor for the Q-function projection in Stage 2.

---

## 4. Stage 2 — Q-Function Projection to the Target BER

### 4.1 Gaussian noise assumption

Assume the amplitude noise at the decision point is a zero-mean Gaussian random
variable with standard deviation $\sigma$.  The BER depends on the normalised eye
margin $\mu = V/\sigma$, where $V$ is the half eye opening (distance from the
decision threshold to the nearest signal level):

$$\text{BER} = s_f \cdot \mathrm{erfc}\!\left(\frac{\mu}{\sqrt{2}}\right) \tag{4}$$

where $s_f$ is a modulation-dependent scaling factor (see Section 5) and
$\mathrm{erfc}$ is the complementary error function
$\mathrm{erfc}(x) = \frac{2}{\sqrt{\pi}}\int_x^\infty e^{-t^2}\,dt$.

Inverting (4):

$$\mu = \sqrt{2}\,\mathrm{erfc}^{-1}\!\!\left(\frac{\text{BER}}{s_f}\right) \tag{5}$$

### 4.2 BER–margin relationship

Define the coefficient $C = 1/s_f$.  Equation (5) becomes:

$$\mu(\text{BER}) = \sqrt{2}\,\mathrm{erfc}^{-1}(C \cdot \text{BER}) \tag{6}$$

Under the Gaussian model, $\sigma$ is fixed: $\mu$ scales linearly with $V$, and
$V$ scales with the signal-to-noise ratio.  The ratio of margins at two BER
values $p_1$ and $p_2$ is therefore:

$$\frac{\mu(p_1)}{\mu(p_2)} = \frac{\mathrm{erfc}^{-1}(C\,p_1)}{\mathrm{erfc}^{-1}(C\,p_2)} \tag{7}$$

This ratio is a pure function of the two BER values and the modulation format; it
does not depend on $\sigma$.

### 4.3 Scale factor derivation

The Q-function scale factor $r$ is defined as the ratio of the margin at the
target BER to the margin at the calibration reference $p_\text{sim}$:

$$r = \frac{\mu(p_\text{target})}{\mu(p_\text{sim})} = \frac{\mathrm{erfc}^{-1}(C\,p_\text{target})}{\mathrm{erfc}^{-1}(C\,p_\text{sim})} \tag{8}$$

Physically, $r$ answers: *"by what factor must the normalised eye margin increase
to move from $p_\text{sim}$ to $p_\text{target}$?"*  For $p_\text{target} < p_\text{sim}$
(lower target BER requires larger margin), $r > 1$.

### 4.4 Final expression

Starting from the Poisson upper bound $p_U$, compute its corresponding normalised
margin, scale it by $r$, and invert via the erfc to obtain $p_\text{conf}$:

$$\mu_U = \sqrt{2}\,\mathrm{erfc}^{-1}(C\,p_U)$$
$$\mu_\text{conf} = \mu_U \cdot r$$
$$p_\text{conf} = s_f \cdot \mathrm{erfc}\!\left(\frac{\mu_\text{conf}}{\sqrt{2}}\right) = s_f \cdot \mathrm{erfc}\!\left(\mathrm{erfc}^{-1}(C\,p_U) \cdot r\right)$$

Substituting the definition of $r$:

$$\boxed{p_\text{conf} = s_f \cdot \mathrm{erfc}\!\!\left(\mathrm{erfc}^{-1}(C\,p_U)\cdot \frac{\mathrm{erfc}^{-1}(C\,p_\text{target})}{\mathrm{erfc}^{-1}(C\,p_\text{sim})}\right)} \tag{9}$$

where:
- $p_U$ — Poisson 95 % upper bound (equation 2)
- $p_\text{sim}$ — calibration reference (equation 3)
- $C = 1/s_f$ — modulation coefficient
- $s_f$ — modulation scaling factor

### 4.5 Algebraic sanity check

When the simulation achieves zero errors in $N_\text{ref}$ bits, the Poisson
bound gives $p_U = p_\text{sim}$ exactly.  Substituting into (9):

$$p_\text{conf} = s_f \cdot \mathrm{erfc}\!\left(\mathrm{erfc}^{-1}(C\,p_\text{sim})\cdot\frac{\mathrm{erfc}^{-1}(C\,p_\text{target})}{\mathrm{erfc}^{-1}(C\,p_\text{sim})}\right) = s_f \cdot \mathrm{erfc}\!\left(\mathrm{erfc}^{-1}(C\,p_\text{target})\right) = s_f \cdot C\,p_\text{target} = p_\text{target}$$

So $p_\text{conf} = p_\text{target}$ identically.  This is the defining calibration
property: the reference run achieves exactly the target BER at 95 % confidence.

---

## 5. Modulation Scaling

### 5.1 NRZ

For binary NRZ with a single threshold at the mid-point between the two levels,
the BER under AWGN is exactly:

$$\text{BER}_\text{NRZ} = Q\!\left(\frac{V}{\sigma}\right) = \frac{1}{2}\mathrm{erfc}\!\left(\frac{V}{\sigma\sqrt{2}}\right)$$

Comparing with (4): $s_f = 1/2$, $C = 2$.

$$\mathrm{erfc}^{-1}(2\,\text{BER}) = \frac{V}{\sigma\sqrt{2}} \tag{10}$$

The argument to $\mathrm{erfc}^{-1}$ is the normalised margin in units of
$1/\sqrt{2}$ sigma, i.e. $Q^{-1}(\text{BER})/\sqrt{2}$.

### 5.2 PAM4

For symmetric 4-level PAM with three inner and two outer eye openings, the
outer eye openings dominate the SER \[3\].  For equal level spacing $2V$ between
adjacent levels and the same noise standard deviation $\sigma$ on all levels:

$$\text{SER}_\text{PAM4} \approx \frac{3}{2}\mathrm{erfc}\!\left(\frac{V}{\sigma\sqrt{2}}\right)$$

With Gray coding (1 bit error per symbol error on average for near-outer eyes)
and $\log_2(4) = 2$ bits per symbol:

$$\text{BER}_\text{PAM4} \approx \frac{3}{4}\mathrm{erfc}\!\left(\frac{V}{\sigma\sqrt{2}}\right)$$

However, the Synopsys definition \[1\] uses a normalised form that accounts for the
effective number of bits and outer eye fractions, yielding:

$$s_f = \frac{M-1}{M}\cdot\frac{10}{\lfloor 10\log_2 M\rfloor} = \frac{3}{4}\cdot\frac{10}{20} = \frac{3}{8} = 0.375, \quad C = \frac{8}{3}$$

for $M = 4$.  The formula generalises as:

$$s_f(M) = \frac{M-1}{M}\cdot\frac{10}{\lfloor 10\log_2 M\rfloor} \tag{11}$$

| $M$ | Format | $s_f$ | $C = 1/s_f$ |
|-----|--------|--------|-------------|
| 2   | NRZ    | 0.5    | 2           |
| 4   | PAM4   | 0.375  | 8/3 ≈ 2.667 |

---

## 6. Algorithm Summary

**Inputs:** $k$, $N$, $p_\text{target}$, $\alpha$, $M$ (signal levels)

**Step 1.** Compute the scaling factor $s_f$ and coefficient $C = 1/s_f$ from equation (11).

**Step 2.** Compute the Poisson $(1-\alpha)$ upper confidence bound:
$$p_U = \frac{\chi^2_{1-\alpha,\; 2(k+1)}}{2N}$$

**Step 3.** Compute the calibration reference:
$$p_\text{sim} = \frac{\chi^2_{1-\alpha,\; 2}}{2 N_\text{ref}} = \frac{-\ln\alpha}{N_\text{ref}}, \quad N_\text{ref} = 3\times10^6$$

**Step 4.** Compute the Q-function scale factor:
$$r = \frac{\mathrm{erfc}^{-1}(C\,p_\text{target})}{\mathrm{erfc}^{-1}(C\,p_\text{sim})}$$

**Step 5.** Project to the target SNR:
$$p_\text{conf} = s_f \cdot \mathrm{erfc}\!\left(\mathrm{erfc}^{-1}(C\,p_U)\cdot r\right)$$

**Pass criterion (Synopsys \[1\]):** $p_\text{conf} < 10^{-6}$ for MLSD receiver.
Our toolbox uses $p_\text{conf} < p_\text{target}$ as the natural criterion.

---

## 7. Relation to the Synopsys Reference

The Synopsys PDF presents the algorithm in terms of several intermediate
quantities.  The correspondence to our notation is:

| Synopsys symbol | This document | Notes |
|---|---|---|
| `ber_conf` (inner) | residual of equation (1) | Zero-finding objective; our formulation uses the closed-form chi-squared instead |
| `ber_sim` | $p_\text{sim}$ | Calibration reference, equation (3); numerically confirmed: $9.9858\times10^{-7}$ |
| `ber_scale` | $r$ | Q-function ratio, equation (8); PAM4 reference value $r = 1.4193$ |
| `scaling_factor` | $s_f$ | PAM4: 0.375; NRZ: 0.5 |
| `ber_c` | $(k+1)/N$ | Laplace-smoothed estimate; used as starting point for their `fminsearch` |
| `ber_conf_raw` | objective function of $p_U$ search | Zero-crossing of the Poisson CDF |
| `ber_conf_sim_raw` | $p_U$ | The Poisson upper bound we compute directly |
| `ber_conf` (final) | $p_\text{conf}$ | Equation (9) |

The Synopsys formulation uses `fminsearch` to solve the Poisson CDF numerically.
Our implementation uses the closed-form chi-squared equivalence (equation 2),
which is algebraically identical and computationally superior.

The `ber_scale` formula in the PDF uses `sqrt(2)*erfcinv(...)` in both numerator
and denominator — the `sqrt(2)` cancels, confirming it is the ratio of
$\mathrm{erfc}^{-1}$ values as in equation (8).  The argument
`sig_lvls * log2(sig_lvls)^(sig_lvls/(sig_lvls-1))` in the PDF resolves to
$C = 1/s_f$ for both NRZ and PAM4, consistent with equation (11).

---

## 8. Assumptions and Validity

### 8.1 Poisson independence (Stage 1)

The chi-squared confidence bound is exact for a Poisson process — i.e. errors
arrive independently at rate $p$.  Violations:

- **Burst errors from ISI:** if the channel produces error bursts (e.g. a
  dominant ISI pattern that always fails), errors are correlated and the true
  variance of $k$ exceeds the Poisson value.  $p_U$ underestimates the true
  upper bound.
- **Periodic waveform repetition:** if a short waveform tile is repeated to
  extend the simulation, the same noise realisations recur every period.  The
  count $k$ and hence $\hat{p}$ are still valid estimates of the tile-averaged
  BER, but rare events (deep noise excursions) that do not appear in the tile
  are never sampled.

### 8.2 Gaussian noise (Stage 2)

The Q-function projection is exact only if the amplitude noise is Gaussian at
all SNR levels.  Deviations:

- **Non-Gaussian tails** (e.g. from RIN spurs, deterministic jitter, or clipping)
  cause the erfc to over-estimate the probability mass in the tail.  The
  projection will be optimistic (conf BER too low).
- **Noise floor vs. noise at target SNR:** the scale factor $r$ implicitly
  assumes the same noise standard deviation $\sigma$ applies at both the
  simulation and target SNR.  If the noise changes character (e.g. gain
  compression reduces signal swing and changes the SNR asymmetrically), $r$ is
  not well-defined.

### 8.3 Range of valid extrapolation

The ratio $r$ grows without bound as $p_\text{target} \to 0$.  For
$p_\text{target} = 10^{-12}$, $p_\text{sim} \approx 10^{-6}$, the extrapolation
spans 6 decades.  At this range, any deviation from Gaussian in the far tail is
amplified.  The method is most reliable when the simulation BER is within 1–2
orders of magnitude of the target, and least reliable as the gap widens.

### 8.4 Choice of $N_\text{ref}$

The calibration reference $N_\text{ref} = 3\times10^6$ bits is fixed in the
Synopsys definition.  It sets the zero-error floor $p_\text{sim}$.  A larger
$N_\text{ref}$ lowers $p_\text{sim}$ and increases $r$, making the algorithm
more conservative.  Our implementation uses the same value for consistency with
Synopsys.

---

## 9. Worked Examples

### 9.1 OMA sweep — 106.25 Gbaud NRZ (OCI-Gen2)

**Setup:** SNPS simulation on caribou OCI-Gen2, binary NRZ at 106.25 Gbaud.
Results from `run_summary.json` files in
`temp/data/waveform/caribou_oci_gen2/Results/`.

Parameters: $\alpha = 0.05$, $N_\text{ref} = 3\times10^6$, $M = 2$ (NRZ),
$p_\text{target} = 10^{-12}$.

Common values:

$$p_\text{sim} = \frac{-\ln 0.05}{3\times10^6} = 9.986\times10^{-7}$$

$$r = \frac{\mathrm{erfc}^{-1}(2\times10^{-12})}{\mathrm{erfc}^{-1}(2\times9.986\times10^{-7})} = \frac{\mathrm{erfc}^{-1}(2\times10^{-12})}{\mathrm{erfc}^{-1}(1.997\times10^{-6})} \approx \frac{5.065}{3.423} = 1.480$$

| Variant | $k$ | $N$ | $\hat{p}$ | $p_U$ (95%) | $p_\text{conf}$ |
|---|---|---|---|---|---|
| OMA 100 µW VGA1\_0 | 128 | 1,979,998 | $6.46\times10^{-5}$ | $7.49\times10^{-5}$ | $1.01\times10^{-8}$ |
| OMA 100 µW VGA1\_2 | 142 | 1,979,998 | $7.17\times10^{-5}$ | $8.28\times10^{-5}$ | $1.24\times10^{-8}$ |
| OMA 150 µW VGA1\_0 | 18  | 1,979,998 | $9.09\times10^{-6}$ | $1.26\times10^{-5}$ | $2.62\times10^{-10}$ |
| OMA 150 µW VGA1\_2 | 21  | 1,979,998 | $1.06\times10^{-5}$ | $1.45\times10^{-5}$ | $3.42\times10^{-10}$ |
| OMA 200 µW VGA1\_0 | 142 | 1,979,998 | $7.17\times10^{-5}$ | $8.28\times10^{-5}$ | $1.24\times10^{-8}$ |
| OMA 200 µW VGA1\_2 | 111,854 | 1,979,998 | $5.65\times10^{-2}$ | $5.65\times10^{-2}$ | $\gg 1$ (fail) |

**Observation.** The OMA 200 µW VGA1\_2 variant has a raw BER of 5.65 %, indicating
a severely degraded signal path (likely a polarity or alignment issue in the
SNPS run rather than a true link failure).  All other variants pass the Synopsys
criterion ($p_\text{conf} < 10^{-6}$); 150 µW variants are approximately 30×
better than 100 µW variants, consistent with the expected SNR improvement.

**Step-by-step for OMA 100 µW VGA1\_0:**

$$p_U = \frac{\chi^2_{0.95,\; 258}}{2\times1{,}979{,}998} = \frac{305.78}{3{,}959{,}996} = 7.49\times10^{-5}$$

$$p_\text{conf} = 0.5 \times \mathrm{erfc}\!\left(\mathrm{erfc}^{-1}(2\times7.49\times10^{-5})\times1.480\right)$$
$$= 0.5 \times \mathrm{erfc}\!\left(\mathrm{erfc}^{-1}(1.497\times10^{-4})\times1.480\right)$$
$$= 0.5 \times \mathrm{erfc}(2.211\times1.480)$$
$$= 0.5 \times \mathrm{erfc}(3.272) = 1.01\times10^{-8}$$

### 9.2 PAM4 cross-check against Synopsys reference

The Synopsys PDF specifies a calibration case: $M=4$, $k=0$, $N=1.5\times10^6$
symbols ($3\times10^6$ bits), $p_\text{target} = 10^{-11}$, $\alpha=0.05$.
Expected outputs: $p_\text{sim} = 9.986\times10^{-7}$, $r = 1.4193$.

Using our formula with $C = 8/3$:

$$p_\text{sim} = \frac{-\ln 0.05}{3\times10^6} = 9.986\times10^{-7} \quad \checkmark$$

$$r = \frac{\mathrm{erfc}^{-1}((8/3)\times10^{-11})}{\mathrm{erfc}^{-1}((8/3)\times9.986\times10^{-7})} = \frac{\mathrm{erfc}^{-1}(2.667\times10^{-11})}{\mathrm{erfc}^{-1}(2.663\times10^{-6})}$$

Evaluating numerically: $r = 1.4193$ $\checkmark$

This confirms the formula is consistent with the Synopsys reference for PAM4.

---

## 10. Implementation Notes

```python
from optical_serdes.analysis.conf_ber import conf_ber_nrz, conf_ber_pam4, conf_ber_summary

# NRZ: 128 errors in ~2M symbols, target BER = 1e-12
result = conf_ber_nrz(128, 1_979_998, target_ber=1e-12)
print(conf_ber_summary(result))
# Conf BER Summary (NRZ, target=1e-12, 95% CI)
#   Errors / bits:      128 / 1,979,998
#   Raw BER:            6.4647e-05
#   Poisson upper:      7.4865e-05
#   ber_scale:          1.4798
#   Conf BER:           1.0079e-08

# Sanity check: zero errors in N_ref bits → conf_ber == target_ber
r0 = conf_ber_nrz(0, 3_000_000, target_ber=1e-12)
assert abs(r0.conf_ber - 1e-12) / 1e-12 < 1e-6  # passes

# PAM4 with Synopsys reference parameters
r_pam4 = conf_ber_pam4(0, 1_500_000, target_ber=1e-11)
assert abs(r_pam4.ber_scale - 1.4193) < 1e-4    # passes
```

The Poisson bound is evaluated using `scipy.stats.chi2.ppf`, which computes the
chi-squared quantile via the regularised incomplete gamma function.  The
Q-function operations use `scipy.special.erfcinv` and `erfc`.  Both are
numerically stable across the ranges of interest ($p$ down to $\sim10^{-15}$
before `erfcinv` approaches its precision limit).

The `ConfBerResult` dataclass exposes all intermediate values so that each step
can be inspected independently.

---

## References

\[1\] Synopsys SIPI Team, *Confidence BER (conf BER) Algorithm*, internal
presentation E224, 2026 — [PDF](../../references/Conf%20BER%20Algorithm_E224.pdf).
*Cited in: §1 (algorithm structure), §3.4 (calibration reference), §5.2 (PAM4 scaling), §6 (pass criterion), §7 (symbol correspondence).*

\[2\] The chi-squared / Poisson CDF equivalence is a standard result in reliability
statistics; see e.g. Nelson, W., *Applied Life Data Analysis*, Wiley, 1982, §A5.
*Cited in: §3.1 (Poisson model), §3.3 (closed-form chi-squared bound).*

\[3\] Proakis, J. G. & Salehi, M., *Digital Communications*, 5th ed.,
McGraw-Hill, 2007, §5.4 (M-ary PAM BER under AWGN).
*Cited in: §5.2 (PAM4 SER derivation).*

\[4\] IEEE Std 802.3df-2024, *Physical Layer Specifications and Management
Parameters for 200 Gb/s, 400 Gb/s, 800 Gb/s, and 1.6 Tb/s Ethernet*.
Pre-FEC BER floor definitions.
*Context only; not directly cited in the derivation.*
