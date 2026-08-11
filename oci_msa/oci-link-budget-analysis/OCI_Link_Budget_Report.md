# OCI Optical Link Budget — GEN1 (53.125 GBd) and GEN2 (106.25 GBd CPO) Unified Engineering Report

**Scope.** Bottom-up, OMA-domain link budgets per DWDM channel for the 200G OCI line
interface at an internal pre-FEC BER target of $10^{-12}$ ($Q = 7.035$), covering the
GEN1 MSA-rate link (53.125 GBd NRZ) and the GEN2 co-packaged-optics (CPO) link
(106.25 GBd NRZ, analog SerDes, CTLE-only receiver). The document unifies four analysis
canvases and details the methodology and calculations behind every result. All numbers
trace to the runnable scripts in this folder (`01`–`06`, see Appendix A) or to a labeled
assumption in §7.

---

## 0. Glossary

### Acronyms / abbreviations

| Term | Meaning |
|---|---|
| OCI | Optical Compute Interconnect |
| MSA | Multi-Source Agreement |
| GBd | Gigabaud |
| NRZ | Non-Return-to-Zero |
| CPO | Co-Packaged Optics |
| BER | Bit Error Rate |
| FEC / KP4 | Forward Error Correction / the RS(544,514) code used at 100–200G |
| OMA | Optical Modulation Amplitude |
| TIA | Transimpedance Amplifier |
| SRS | Stressed Receiver Sensitivity |
| TDEC(Q) | Transmitter and Dispersion Eye Closure (Quaternary, for PAM4) |
| SEC(Q) | Stressed Eye Closure (Quaternary) |
| ER | Extinction Ratio |
| MPI | Multipath Interference |
| RIN | Relative Intensity Noise |
| ORL | Optical Return Loss |
| ISI | Intersymbol Interference |
| EQ | Equalization |
| FIR | Finite Impulse Response (filter) |
| CTLE | Continuous-Time Linear Equalizer |
| DFE | Decision Feedback Equalizer |
| CD | Chromatic Dispersion |
| DJ / RJ / TJ | Deterministic / Random / Total Jitter |
| DCD | Duty-Cycle Distortion |
| UI | Unit Interval |
| PD | Photodiode |
| MRM | Micro-Ring Modulator; sole acronym for ring resonators in this report |
| EIC / PIC | Electronic / Photonic Integrated Circuit |
| ELS | External Laser Source |
| SerDes | Serializer/Deserializer |
| CID | Consecutive Identical Digits |
| AGC | Automatic Gain Control |
| LF | Low Frequency |
| SE | Single-Ended |
| BT4 | Bessel-Thomson 4th-order (reference filter) |
| TP2 / TP3 | Test Point 2 / 3 (Tx output / Rx input) |
| IL | Insertion Loss |
| SMF | Single-Mode Fiber |
| DWDM | Dense Wavelength-Division Multiplexing |
| TT | Typical-Typical (process corner) |
| SOA | State of the Art |

### Math symbols

| Symbol | Meaning | First used |
|---|---|---|
| $Q$ | Personick Q-factor | §2.2 |
| $i_n$ | Input-referred rms noise current (TIA) | §2.3 |
| $R$ | Photodiode responsivity (A/W) | §2.3 |
| $Z_T$ | Transimpedance gain | §2.3, §5 |
| $B_n$ | Noise integration bandwidth, $1.5 \times f_{3\mathrm{dB}}$ convention | §2.3 |
| $H(f)$ | Transfer function (generic) | §2.3–2.5 |
| $\mathrm{OMA_{floor}}$ / $\mathrm{OMA_{sens}}$ | Analytic noise-limited sensitivity | §2.1, §2.3 |
| $P_i$ | Penalty stack line $i$ (dB) | §2.1, §2.6 |
| $h_{-1}, h_{+1}, h_{+2}$ | Pulse-response cursors (pre-, post-1, post-2) | §2.4 |
| $\tau$ | Pole time constant | §2.4 |
| $t_{20\text{–}80}$ | 20–80% transition time | §2.4 |
| $\omega_z, \omega_p$ | CTLE zero / pole (angular freq.) | §2.5 |
| $\eta$ | CTLE rms noise-enhancement factor | §2.5 |
| $D_{\mathrm{MPI}}$ | MPI discount factor | §2.6 |
| $D_{\mathrm{disp}}$ | Fiber dispersion coefficient (ps/nm), CD penalty formula | §2.6 |
| $S$ | MPI reflection-pair sum | §2.6, §3.3 |
| $R_t, R_r, R_c$ | Transmitter / receiver / connector reflectance | §2.6, §3.3 |
| $E$ | Extinction ratio (linear, in MPI formula) | §2.6 |
| $\sigma_{RJ}$ | RJ standard deviation | §2.6 |
| $I_{DK}$ | Dark current | §2.6 |
| $q$ | Electron charge | §2.6 |
| $\varepsilon$ | Crosstalk factor | §2.6 |
| $\delta$ | Threshold-offset fraction of swing | §2.6 |
| $\lambda$ | Wavelength | §2.4 (CD) |
| $N$ | CID run length (bits) | §5 |
| $f_{LF}$ | Low-frequency cutoff | §5 |
| $f_{3\mathrm{dB}}$ | 3 dB bandwidth | throughout |

*Note:* $D$ is used for two distinct quantities in the source derivations (MPI discount
factor and fiber dispersion coefficient). They are disambiguated above as $D_{\mathrm{MPI}}$
and $D_{\mathrm{disp}}$ for this glossary, though the body text below still uses the bare
$D$ in each local context — read it per §2.6's two formulas.

---

## 1. Executive summary

The link budget's purpose is to **derive component requirements** — above all, the GEN2
receiver TIA class — not to grade existing parts. Measured TIA characterization data
(152 gain/peaking settings of the Ocelot ADFET family, TT corner) is used throughout as
**model-calibration input**: it anchors the input-referral convention, exposes the
family's noise-versus-bandwidth scaling law, and supplied the group-delay lesson that
became a headline spec line.

**Targets.**

| Item | Value |
|---|---|
| Internal pre-FEC BER target | $10^{-12}$ (Personick $Q = 7.035$) |
| OCI MSA compliance threshold | $2.4\times10^{-4}$ ($Q = 3.49$) |
| KP4 FEC role at the internal target | Pure margin — designing to $10^{-12}$ pre-FEC means the FEC carries no traffic-dependent burden |

**GEN1 (53.125 GBd NRZ, per OCI MSA v1.0).**

| Item | Value | Calculation |
|---|---|---|
| Analytic receiver floor | **−12.93 dBm OMA** (calibrated on the lowest-noise bandwidth-adequate TIA setting: $i_n = 3.17\ \mu$A rms, 29.3 GHz) | [C.1](Methodology_Provenance.md#c1-gen1-analytic-receiver-floor) |
| Penalty stack | **2.93 dB** | [C.2](Methodology_Provenance.md#c2-gen1-penalty-stack-293-db) |
| Required OMA at the receiver | **−10.00 dBm** | [C.3](Methodology_Provenance.md#c3-gen1-required-oma-at-the-receiver) |
| Closure vs. spec-minimum transmitter | **+0.60 dB** | [C.4](Methodology_Provenance.md#c4-gen1-closure-margins) |
| Closure vs. realistic transmitter (−3.2 dBm OMA, TDEC ≈ 2 dB) | **+2.30 dB** | [C.4](Methodology_Provenance.md#c4-gen1-closure-margins) |
| Spec finding | At the spec's −19 dB end reflectances the derived MPI penalty would be 0.51 dB — 2.5× the MSA's 0.2 dB allocation. Meeting ~0.2 dB requires **≤ −24 dB** ends. Because GEN1 and GEN2 share the product line, the ≤ −24 dB requirement is enforced for both generations, ensuring the ~0.2 dB MPI line by construction (GEN1 books 0.24 dB, §3.3) | [C.5](Methodology_Provenance.md#c5-mpi-reflectance-finding) |

**GEN2 (106.25 GBd NRZ, CPO).**

| Item | Value | Calculation |
|---|---|---|
| Rate scaling | UI halves to 9.412 ps, and Nyquist doubles to 53.125 GHz | [C.6](Methodology_Provenance.md#c6-gen2-rate-scaling) |
| Derived TIA class (§5) | $f_{3\mathrm{dB}}$ 50–64 GHz, $i_n \le 4.0\ \mu$A rms (≤ 14 pA/√Hz average density over $B_n = 1.5 \times f_{3\mathrm{dB}}$), peaking ≤ 1 dB, group-delay ripple ≤ 3 ps | [C.7](Methodology_Provenance.md#c7-gen2-derived-tia-class) |
| Target-class TIA floor | 58 GHz, 4.5 µA → floor **−11.41 dBm** | [C.8](Methodology_Provenance.md#c8-gen2-target-class-tia-floor) |
| Penalty stack (typical Tx corner) | **4.07 dB** | [C.9](Methodology_Provenance.md#c9-gen2-penalty-stack-407-db-typical-tx) |
| Closure margin, typical Tx corner | **+1.34 dB** at Tx OMA −3.5 dBm | [C.10](Methodology_Provenance.md#c10-gen2-closure-margins) |
| Closure margin, fast / slow Tx corners | +1.67 dB / +0.79 dB | [C.10](Methodology_Provenance.md#c10-gen2-closure-margins) |

**GEN2 budget waterfall (typical corner).** Delivered power: Tx OMA −3.5 dBm − 2.5 dB
link IL = **−6.0 dBm at the Rx**. Required power, built up from the receiver floor:
−11.41 dBm (floor) + 1.16 (shot/RIN) + 0.21 (MPI) + 1.15 (ISI+EQ) + 0.04 (CD) + 0.95
(jitter) + 0.36 (crosstalk) + 0.21 (threshold) = **−7.34 dBm required** (lines shown
rounded; the unrounded stack is 4.07 dB —
[C.9](Methodology_Provenance.md#c9-gen2-penalty-stack-407-db-typical-tx)). Margin
= −6.0 − (−7.34) = **+1.34 dB**. (Note the direction: penalties stack *on the floor*
to form the required OMA; they are not subtracted from the delivered −6.0 dBm.)

**Bottom line: feasible, but specification-sensitive.** The GEN2 link closes at every
modeled corner, but +1.34 dB typical / +0.79 dB slow-Tx is workable rather than
comfortable — the worst-everything device cell reaches +0.16 dB (§6.1), and several
independent Low-confidence assumptions (table below) can each move the margin by
0.2–1 dB. The doubled rate does not break the optical budget; it moves the problem
into the receiver implementation (the §5 TIA class) and into validating the
assumptions below.

**Device trade study.** Against user-provided device brackets, the **preferred
baseline architecture is a no-FIR 60 GHz driver with the 60 GHz / 4–5 µA TIA
(option B)**: **+1.63 dB** typical margin, degrading to +0.16 dB only in the
worst-everything corner (5 µA noise and a 40 GHz MRM) — degraded but never broken,
though that corner now leans on the Tx OMA relief valve. A 3-tap slice-DAC Tx FIR buys
no ISI improvement on this short, clean channel (the joint optimizer drives the taps
to zero) and costs 0.27 dB of slice-DCD jitter. **A single post-cursor tap is retained
as a design option pending measured MRM EO response** — MRM detuning peaking is the
one impairment a Tx FIR fixes that the CTLE cannot (§6.3, §8).

**Key derived requirements.**

- GEN2 TIA table (§5, headline above)
- Noise integration bandwidth convention: $B_n = 1.5 \times f_{3\mathrm{dB}}$, both generations (§2.3)
- End reflectance ≤ −24 dB at both Tx and Rx (both generations — shared product line)
- Tx 20–80 % transition time ≤ 5.6 ps (0.60 UI) hard / 4.2 ps (0.45 UI) target
- Microbump ≤ 25 fF
- Jitter budget: RJ ≤ 141 fs rms, DJ ≤ 1.32 ps (TJ@1e-12 = 3.30 ps)
- TDEC ≤ 1.8 dB

**Status and confidence of the load-bearing inputs.** The requirements above are only
as strong as what they stand on. Reading guide: *Measured* = taken from
characterization data in the repos; *Derived* = computed by the scripts from the §2
framework; *Assumed* = judgment call, no supporting measurement; *Required* = design
decision this report enforces; *Model result* = output of the budget, inherits the
confidence of its inputs. Full provenance per §7 and `Methodology_Provenance.md`.

| Item | Status | Confidence |
|---|---|---|
| GEN1 design-point TIA ($i_n$ 3.17 µA, 29.3 GHz), $R$ = 0.876 A/W | Measured (152-setting tables) | High |
| Family noise-vs-bandwidth scaling law ($f^2$-dominated) | Measured + regression fit | High |
| GD-ripple failure mode (12.5 ps → $h_{-1}$ ≈ 0.48) | Measured | High |
| TIA noise ceiling ≤ 4.0 µA | Derived (stack inversion, §4.4) | Medium — hinges on the $B_n$ convention and the stack's assumed lines |
| TIA bandwidth window 50–64 GHz | Derived (sensitivity sweep, §5) | Medium |
| GD ripple ≤ 3 ps / peaking ≤ 1 dB | Derived (measured lesson translated to 106 GBd by model sweep) | Medium |
| Microbump ≤ 25 fF | Derived (droop scan) — but at an **assumed** $R_{\mathrm{eff}}$ = 50 Ω node impedance | Medium |
| $B_n = 1.5 \times f_{3\mathrm{dB}}$ | Convention (design-bounding, §2.3) | Medium — pending measured integrated noise spectra to ≥ 90 GHz |
| End reflectance ≤ −24 dB | Required (enforced, §3.3) | Medium — manufacturing feasibility judged achievable |
| PD capacitance 30–40 fF | Assumed (**unmeasured**) | **Low** |
| MRM EO bandwidth 40–80 GHz bracket | Assumed (no 106 GBd data) | **Low** |
| MRM peaking-free response | Assumed (**unverified** — the one impairment that could reverse the no-FIR choice) | **Low** |
| RJ 141 fs rms (analog CDR) | Assumed target (SOA edge; fallback +0.19 dB, §8) | **Low** |
| +1.34 dB typical closure margin | Model result | Medium — inherits every line above |

---

## 2. Methodology

### 2.1 OMA-domain budget framework

The budget is built per DWDM channel in the optical-modulation-amplitude (OMA) domain,
between TP2 (transmitter output) and TP3 (receiver input):

$$\mathrm{OMA_{TX}} - \mathrm{IL_{link}} \ge \mathrm{OMA_{floor}} + \sum_i P_i
\quad\Longrightarrow\quad
\mathrm{margin} = (\mathrm{OMA_{TX}} - \mathrm{IL}) - (\mathrm{OMA_{floor}} + \textstyle\sum_i P_i)$$

where $\mathrm{OMA_{floor}}$ is the analytic amplifier-noise-limited sensitivity (§2.3)
and $P_i$ are the power penalties (§2.6). OMA rather than average power is used because
NRZ decisions ride on the eye amplitude. Average-power bookkeeping would drag the
extinction-ratio penalty $\frac{ER+1}{ER-1}$ into every line, whereas in the OMA domain
ER only enters through signal-dependent noise (shot, RIN, MPI) on the individual rails.

**TDEC accounting choice.** Transmitter eye closure is booked **inside the ISI+EQ line**
of the penalty stack (the pulse-response simulation contains the Tx filter), *not* as a
separate TDEC subtraction — this avoids double counting. The one exception is the GEN1
closure against the *spec-minimum* transmitter (§3.2), where the spec's own
TDEC-coupled OMA floor is exercised and TDEC is subtracted explicitly while the ISI
line uses only the reference-receiver filtering.

### 2.2 BER targets and Personick Q

$\mathrm{BER} = \tfrac12\,\mathrm{erfc}(Q/\sqrt2)$:

| BER | $Q$ | Role |
|---|---|---|
| $2.4\times10^{-4}$ | 3.49 | OCI MSA compliance threshold (TDEC, SRS, RxSens) |
| $10^{-6}$ | 4.75 | MSA BER-floor requirement |
| $10^{-12}$ | **7.035** | **Internal design target used throughout** |
| $10^{-15}$ | 7.94 | Deep-margin studies |

In an amplifier-noise-limited receiver the move from $Q=3.49$ to $Q=7.035$ costs
$10\log_{10}(7.035/3.49) \approx 3.0$ dB of OMA. At $10^{-12}$ pre-FEC, the KP4 FEC
carries no traffic-dependent burden — it is pure margin. Penalties that scale with
$Q^2$ (RIN, §2.6) grow disproportionately at this target: this is why the internal
budget cannot simply re-use spec-threshold penalty values.

### 2.3 Analytic sensitivity floor from measured TIA data

The floor is calibrated from characterization tables, not assumed:

1. **Input-referral.** For each TIA setting, input-referred noise
   $i_n = v_{n,\mathrm{out}} / Z_{T,\mathrm{peak}}$, with $v_{n,\mathrm{out}}$ from
   `TT_Tia_Noise.csv` and $Z_{T,\mathrm{peak}}$ the **peak single-ended p-leg**
   transimpedance from the TF table. The single-ended convention is the conservative
   reading of the model (which injects its noise target on the p-leg while the signal
   sees the differential gain). It is kept for both generations for comparability.
2. **Noise integration bandwidth.** For the signal-dependent noise terms (shot, RIN,
   dark current): $B_n = 1.5 \times f_{3\mathrm{dB}}$, both generations — the
   single-pole noise-equivalent-bandwidth factor ($\pi/2$, rounded down), applied as a
   deliberately conservative convention. The signal-TF Personick integral
   ($\int|H/H_0|^2 df$ — 28.2 GHz for this design point, or 1.10× $f_{3\mathrm{dB}}$
   for an ideal Butterworth-2) is **not** used: it understates a real receiver's noise
   bandwidth, because physical noise densities extend well beyond the circuit's 3 dB
   point (the measured family's noise is $f^2$-shaped, §4.3) — noise must be
   integrated beyond the bandwidth of the circuit. GEN1 design point:
   $B_n = 1.5 \times 29.3 = 43.9$ GHz.
3. **Floor.** $\mathrm{OMA_{sens}} = 2\,Q\,i_n / R$.

**Worked GEN1 example** (setting `12211111`, the lowest-noise setting with
$f_{3\mathrm{dB}} \ge 0.55\times$ baud — 55 of 152 settings meet that gate):
$v_n = 5.28$ mV, $Z_T = 1664$ V/A (64.4 dBΩ SE, 70.7 dBΩ differential) →
$i_n = 3.17\ \mu$A rms, $B_n = 43.9$ GHz ($1.5 \times 29.3$), $R = 0.876$ A/W (the `pd`
column of the same tables). Then

$$\mathrm{OMA_{sens}} = \frac{2 \times 7.035 \times 3.17\ \mu\mathrm{A}}{0.876\ \mathrm{A/W}} = 50.9\ \mu\mathrm{W} = \mathbf{-12.93\ dBm}.$$

(Script `01`. At the spec's $Q = 3.49$ the same receiver floors at −15.97 dBm,
comfortably inside the −6.2 dBm SRS limit.)

**Three noise-bandwidth accountings, compared.** To keep the modeling choice explicit
(it is the single most consequential convention in the budget — register row 23):

| Accounting | GEN1 (29.3 GHz design pt) | GEN2 (58 GHz class) | Standing |
|---|---|---|---|
| Signal-TF shape integral ($\int\lvert H/H_0\rvert^2 df$) | 28.2 GHz (0.96×) | 64 GHz (1.10×) | Rejected for $B_n$ — a clean-model integral that understates a physical part's noise bandwidth |
| Measured noise reality | $f^2$-dominated: density keeps **rising** past $f_{3\mathrm{dB}}$ (§4.3) | **unmeasured** above ~60 GHz | The reason the shape integral is rejected; the eventual ground truth |
| $\mathbf{1.5 \times f_{3\mathrm{dB}}}$ (adopted) | 43.9 GHz | 87 GHz | **Design-bounding convention, pending measured integrated noise spectra to ≥ 90 GHz.** Not a physical fact; costs ~0.33 dB per stack vs the shape integral (§3.4, row 23) |

When candidate-TIA noise spectra measured to ≥ $1.5 \times f_{3\mathrm{dB}}$ exist,
the measured integral replaces the convention and the ~0.33 dB of deliberate
conservatism is either recovered or confirmed as real.

### 2.4 Pulse-response framework (ISI, CD, jitter share one engine)

A single 1-UI rectangular pulse is propagated through the cascaded frequency response
on a 32×-oversampled grid ($N = 8192$):

- **Tx:** two identical cascaded real poles fitted to the specified 20–80 % transition
  time via the analytic 2-pole step response $s(t) = 1-(1+t/\tau)e^{-t/\tau}$
  ($t_{20\text{–}80} \approx 3.36\,\tau$). GEN1's spec-referenced Tx uses the 26.5625 GHz
  4th-order Bessel-Thomson TDEC reference filter instead.
- **TIA:** measured differential TF interpolated onto the grid, magnitude flattened
  below 2 GHz with bulk-delay phase preserved — this encodes the **DC-restoration
  assumption** (a baseline-wander loop handles the AC-coupling droop — §5 turns this
  into an explicit LF-cutoff requirement). Hypothetical TIAs use 2nd-order Butterworth
  responses.
- **Microbump (GEN2):** the EIC is bumped directly onto the PIC — the driver drives
  the modulator (and the PD feeds the TIA) straight through the bump, unterminated.
  The bump capacitance is booked as a single pole $f_p = 1/(2\pi R_{\mathrm{eff}} C)$
  at an assumed effective node impedance $R_{\mathrm{eff}}$ (placeholder 50 Ω pending
  the actual driver $R_{\mathrm{out}}$ / TIA $R_{\mathrm{in}}$): 25 fF → 127 GHz.
  Conservative when the real node impedance is lower, as direct drive intends.
- **ISI metric:** peak distortion on UI-spaced taps around the cursor with the sampling
  phase optimized for maximum eye:
  $P_{\mathrm{ISI}} = -10\log_{10}\!\big[(h_0 - \sum|h_{i\ne0}|)/h_0\big]$ (optical dB).
- **CD:** quadratic spectral phase $\exp(j\pi D L \lambda^2 f^2/c)$ at the spec corners
  ±1.7/−0.9 ps/nm. The penalty is the *delta* of the peak-distortion metric.

### 2.5 Equalization modeling

- **Tx FIR (slice DAC).** Three parallel limiting driver slices (pre/main/post) with
  1-UI delays summing at the output node. Because each slice is two-level and the data
  is NRZ, the summed waveform is exactly a linear FIR on the data — slice nonlinearity
  does not corrupt tap accuracy. The peak-swing constraint $\sum_i |w_i| = 1$ means
  de-emphasis costs OMA: the optimizer charges
  $-10\log_{10}(\sum_i w_i)$ against every candidate tap set (grid search, step 0.02–0.04).
- **Rx CTLE.** One zero, two coincident poles, unit DC gain:
  $H(s) = (1+s/\omega_z)/(1+s/\omega_p)^2$. Each candidate is charged its **noise
  enhancement**, the rms gain over the TIA-shaped noise:
  $\eta = \sqrt{\int|H_{TIA}H_c|^2 df / \int|H_{TIA}|^2 df}$, and the sweep minimizes
  $P_{\mathrm{ISI}} + 10\log_{10}\eta$. Joint FIR+CTLE cells nest the two searches.
- **DFE:** excluded by architecture (GEN2 is CTLE-only). GEN1's budget assumes the
  standard DSP-SerDes DFE removes post-cursors (§3.1).

### 2.6 Penalty formulas and inputs

| Penalty | Model | Inputs |
|---|---|---|
| ER / shot | Q-solve with level-dependent shot on both rails: $\sigma_L^2 = i_n^2 + 2qR P_L B_n$ | ER 3.5 dB (GEN1 spec min) / 4.5 dB (GEN2 target) |
| RIN | Q-solve with $\sigma_{RIN,L} = R P_L\sqrt{\mathrm{RIN}\cdot B_n}$, penalty scales as $Q^2$ | RIN$_{\mathrm{OMA}}$ −138 dB/Hz @ 21.4 dB ORL. **RIN-floor check:** $Q_{\max} = [\,\sqrt{\mathrm{RIN}\,B_n}\,(P_1+P_0)/\mathrm{OMA}\,]^{-1} = 14.5$ → BER floor $\sim 10^{-47}$, no floor issue |
| MPI | Bhatt/King discounted upper bound: $P = -10\log_{10}(1-x)$, $x = 4DS\frac{E}{E-1}$, $S = \sqrt{R_tR_r} + n\sqrt{R_tR_c} + n\sqrt{R_rR_c} + \frac{n(n-1)}{2}R_c$ | $D=0.5$. Ends −24 dB for both generations (shared product line, §3.3; spec allows −19 dB → 0.51 dB), 4 connectors −35 dB. GEN1 (ER 3.5): 0.24 dB. GEN2 (ER 4.5): 0.205 dB |
| ISI + EQ | §2.4/§2.5 net of noise enhancement and de-emphasis | per scenario |
| CD | pulse-sim delta at ±1.7/−0.9 ps/nm | GEN1 0.005 → book 0.01; GEN2 sim 0.015 → book 0.04 (scales ≈ baud²) |
| Jitter | dual-Dirac: $TJ = DJ + 2Q\sigma_{RJ}$; penalty from the equalized eye re-evaluated at $\pm TJ/2$; a closed eye at the offset ⇒ scenario does not close (no finite penalty is booked) | GEN1: RJ 0.010 UI rms, DJ 0.10 UI → TJ 0.241 UI (4.5 ps) → 0.61 dB. GEN2: RJ 0.015 UI (141 fs), DJ 0.14 UI → TJ 0.351 UI (3.30 ps) → 0.95 dB |
| Inter-channel crosstalk | $-10\log_{10}(1-2\varepsilon)$, $\varepsilon = n_{adj}10^{-\mathrm{iso}/10}10^{\Delta\mathrm{OMA}/10}$ | MRM demux isolation 20 dB (assumed), 2 neighbors, +3 dB aggressor ΔOMA → 0.36 dB |
| Threshold offset | $10\log_{10}(1+2\delta)$ | $\delta = 2.5\%$ of swing → 0.21 dB |
| Dark current | $10\log_{10}\sqrt{1 + 2qI_{DK}B_n/i_n^2}$ | 1 µA → 0.003 dB |

---

## 3. GEN1 budget — 53.125 GBd NRZ (script `02`)

### 3.1 Penalty stack

Receiver: design-point TIA (§2.3), Tx = BT4 26.5625 GHz reference, DFE removes
post-cursors. Unequalized peak-distortion ISI is 2.15 dB (cursor 0.809, pre 0.111,
post 0.205); the DFE leaves the pre-cursor-only residual.

| Line | dB | Derivation |
|---|---:|---|
| ER / signal-dependent shot | 0.18 | Q-solve at ER 3.5 dB, $B_n$ 43.9 GHz (1.5× $f_{3\mathrm{dB}}$) |
| RIN (−138 dB/Hz, $Q^2$-scaled) | 0.68 | 4.5× its value at spec BER (0.15 dB) — the $Q^2$ effect |
| MPI (Bhatt UB, $D=0.5$) | 0.24 | ends −24 dB (shared GEN1/GEN2 product line, §3.3), 4 × −35 dB connectors, ER 3.5 |
| ISI residual after EQ | 0.64 | $-10\log_{10}[(0.809-0.111)/0.809]$ |
| Chromatic dispersion | 0.01 | +1.7 ps/nm worst corner (computed 0.005) |
| Jitter | 0.61 | TJ = 0.241 UI, eye at ±TJ/2 |
| Inter-channel crosstalk | 0.36 | 20 dB isolation, +3 dB ΔOMA |
| Decision threshold offset | 0.21 | δ = 2.5 % |
| Dark current | 0.00 | 1 µA |
| **Total** | **2.93** | |

### 3.2 Closure

Required OMA at Rx $= -12.93 + 2.93 = \mathbf{-10.00}$ dBm.

| Scenario | Tx OMA | −IL | −TDEC | At Rx | Margin |
|---|---:|---:|---:|---:|---:|
| Spec-min Tx, TDEC 1.4 dB | −5.5 | 2.5 | 1.4 | −9.40 | **+0.60 dB** |
| Spec-min Tx, TDEC 3.4 dB | −3.5 | 2.5 | 3.4 | −9.40 | **+0.60 dB** |
| Realistic Tx (−3.2 dBm, TDEC ≈ 2 dB) | −3.2 | 2.5 | 2.0 | −7.70 | **+2.30 dB** |

The spec's OMA-min law $\max(-5.5, -6.9+\mathrm{TDEC})$ pins OMA−TDEC at −6.9 dBm for
TDEC ≥ 1.4 dB, so both spec corners close identically. The realistic case is grounded
in the spec's own stressed-test aggressor point (−3.2 dBm), the ELS power budget, and
the ~1.2 V$_{\mathrm{ppd}}$ swing of the `Typ_Txdrv_NL.csv` driver class at ER ≈ 4.5 dB.
TDEC is applied unscaled (defined at BER $2.4\times10^{-4}$; its deterministic content
does not scale with Q — noted caveat).

Two independent cross-checks: (i) the spec itself closes by construction with exactly
its 0.2 dB MPI allowance (−3.5 − 2.5 = −6.0 dBm vs −6.2 dBm SRS); (ii) the COUPE BIDI
simulated waterfall crosses BER $10^{-12}$ at −11.8 dBm OMA — between our analytic
floor (−12.93) and full required OMA (−10.00), consistent with a simulation that
includes ISI/jitter but not MPI/crosstalk stresses.

### 3.3 IEEE Clause 181 cross-check and the MPI finding

Our 2.93 dB stack sits 1.0 dB under Clause 181's 3.9 dB allocation — expected, since
the OCI channel is shorter/lower-loss and NRZ needs no PAM4 level-separation penalty.
At the spec's −19 dB end reflectances the MPI line would be 0.51 dB, matching
Clause 181's 0.5 dB rather than the OCI spec's 0.2 dB allocation: with $S = 0.0304$,
the two −19 dB ends contribute 93 % of $S$ (41 % direct pair + 52 % end-connector
cross terms), and the worst case ($D = 1$) reaches 1.08 dB. Meeting ~0.2 dB at
ER 3.5 dB requires roughly $R_t = R_r \le -24$ dB.

**Requirement adopted:** GEN1 and GEN2 are the same product line, so the GEN2-derived
$\le -24$ dB end-reflectance requirement (§4) is enforced for both generations — the
~0.2 dB MPI line is ensured by the reflectance criterion rather than assumed. The GEN1
budget therefore books MPI at **0.24 dB** ($D = 1$ worst case: 0.49 dB). A part meeting
only the spec's −19 dB would add 0.27 dB back to the stack (0.51 dB line).

### 3.4 Sensitivity to assumptions (vs the +0.60 dB base)

| Variation | Effect | New margin |
|---|---|---:|
| TIA noise 3.17 → 4.26 µA (median usable setting) | floor +1.28 dB | −0.69 dB |
| TIA noise → 6.75 µA (worst usable) | floor +3.28 dB | −2.68 dB |
| $R$ 0.876 → 0.80 / 1.00 A/W | floor +0.39 / −0.58 dB | +0.20 / +1.17 dB |
| MPI: 2 / 6 connectors | 0.24 → 0.14 / 0.36 dB | +0.70 / +0.48 dB |
| MPI: $D = 1$ worst case | 0.24 → 0.49 dB | +0.35 dB |
| MPI: ends at spec −19 dB (shared −24 dB assumption fails) | 0.24 → 0.51 dB | +0.33 dB |
| RIN −138 → −144 dB/Hz (ELS-only) | 0.68 → 0.16 dB | +1.13 dB |
| $B_n$: signal-TF shape integral (28.2 GHz) instead of 1.5× $f_{3\mathrm{dB}}$ | ER/shot+RIN 0.86 → 0.53 dB | +0.93 dB |

TIA noise dominates the GEN1 budget — which is precisely why the GEN2 exercise (§4–5)
is framed as deriving the receiver class the doubled rate requires.

---

## 4. GEN2 CPO architecture and rate scaling — 106.25 GBd NRZ (scripts `03`, `04`)

### 4.1 Architecture

![OCI GEN2 simplified block diagram](./OCI-GEN2_Simplified.png)

```mermaid
flowchart LR
    TX[SerDes Tx] --> PRE(("pre"))
    TX --> UI1[UI]
    UI1 --> MAIN(("main"))
    UI1 --> UI2[UI]
    UI2 --> POST(("post"))
    PRE --> BUMP1[microbump]
    MAIN --> BUMP1
    POST --> BUMP1
    LASER{{Laser}} --> MRM((MRM))
    BUMP1 --> MRM
    MRM --> MD["Mux, Channel, Demux"]
    MD --> PD[PD]
    PD --> BUMP2[microbump]
    BUMP2 --> TIA(("TIA"))
    TIA --> RX[SerDes Rx]
```

Per the block diagram: SerDes Tx feeds a cascaded delay line (two 1-UI / 9.412 ps
delays), with the `pre`/`main`/`post` **limiting driver slices** tapped off the
undelayed, once-delayed, and twice-delayed nodes respectively and summed at the output
node — this is the analog FIR — through an EIC–PIC microbump to the MRM (the laser
feeds the MRM directly), mux → 500 m fiber → demux, PD, second microbump, TIA inside
the SerDes Rx AFE. **Rx EQ is CTLE only; DFE is
not supported.** CPO eliminates the package trace channel (1.61/0.72 dB differential IL
at the new Nyquist, plus its reflections) and replaces it with a microbump parasitic.
The bump is an unterminated direct connection — extra load capacitance, not a matched
interface. Booked as a single 127 GHz pole at 25 fF (§2.4): 0.70 dB droop at 53.1 GHz,
costing +0.22 dB of equalized ISI (1.15 vs 0.93 dB); 50 fF would cost +0.71 dB — hence
the tightened ≤ 25 fF / ≤ 30 pH microbump requirement. A low driver output impedance
shrinks this charge.

### 4.2 What scales with rate

| Quantity | GEN1 → GEN2 | Consequence |
|---|---|---|
| UI | 18.82 → 9.412 ps | all ps-domain tolerances halve (FIR tap spacing ±0.47 ps, slice DCD ≤ 0.47 ps) |
| Nyquist | 26.56 → 53.125 GHz | receiver class must move to 0.5–0.6× of the new baud |
| Noise bandwidth ($1.5\times f_{3\mathrm{dB}}$, §2.3) | 43.9 → 87 GHz | floor rises; shot/RIN integrate over ~2× the bandwidth (ER/shot+RIN 0.86 → 1.16 dB) |
| Jitter in ps | TJ 4.5 → 3.30 ps at similar UI budget | RJ spec becomes 141 fs rms — analog-CDR state of art |
| CD | ~baud²: 0.01 → 0.04 dB booked | still small at 500 m |
| Tx transition | 10/12/17 ps corners are 1.1–1.8 UI | new corners defined as 0.35/0.45/0.60 UI (3.3/4.2/5.6 ps; 2-pole fits: 105/82/61 GHz poles) |

### 4.3 Receiver noise scaling law (measured-family calibration)

A non-negative least-squares regression of $i_n^2$ against the white and $f^2$ noise
integrals ($B_1 = \int|\hat H|^2 df$, $B_2 = \int f^2|\hat H|^2 df$, including the
model's 60 GHz noise-path LPF) across all 152 settings shows the family is
**$f^2$-noise dominated**: single-parameter fits give $R^2 = 0.87$ ($f^2$-only) versus
0.59 (white-only). Scaling the GEN1 design point to a 58 GHz Butterworth-2 response
(white shape-integral $B_1 = 64.4$ GHz, 2.92× GEN1's — these scaling integrals are
distinct from the §2.3 noise-integration-bandwidth convention):

- white ($\sqrt{BW}$) scaling: $i_n = 5.42\ \mu$A → floor −10.60 dBm (the optimistic bound);
- $f^2$ ($BW^{1.5}$) scaling: $i_n = 17\ \mu$A → floor −5.63 dBm (the fit-favored law).

This scaling law — not any pass/fail statement — is the measured data's main
contribution to GEN2: it demonstrates that the GEN2 noise line cannot be reached by
re-tuning this input stage, and quantifies the gap a new design must close. (For
completeness, a full 152-setting re-scan at 106.25 GBd with per-setting CTLE
optimization confirms it: no setting qualifies, which is expected and unremarkable —
the family was designed for the GEN1 rate. The scan's real yield is the group-delay
failure mode in §5.)

### 4.4 GEN2 floor, stack, and closure (derived TIA class)

Target-class TIA: Butterworth-2 at 58 GHz, $i_n = 4.5\ \mu$A rms total; shot/RIN
integrate over $B_n = 1.5 \times 58 = 87$ GHz (§2.3 convention) — in the same range as
100 GBd-class TIAs the team is aware of (roughly 2.5–5 µA at 55–65 GHz), though this
bracket is an internal engineering estimate, not a cited publication (see
Methodology_Provenance.md). Floor:

$$\mathrm{OMA_{floor}} = \frac{2 \times 7.035 \times 4.5\ \mu\mathrm{A}}{0.876} = 72.3\ \mu\mathrm{W} = \mathbf{-11.41\ dBm}.$$

Penalty stack (typical Tx 0.45 UI, 25 fF bump in chain, optimal CTLE
$z = 37$ GHz / $p = 62$ GHz, noise enhancement ×0.99):

| Line | GEN1 CPO @ 53 GBd | GEN2 @ 106 GBd | Driver |
|---|---:|---:|---|
| ER/shot + RIN (Q-solve) | 0.86 | 1.16 | $B_n$ 43.9 → 87 GHz (1.5× $f_{3\mathrm{dB}}$) |
| MPI | 0.21 | 0.21 | rate-independent; −24 dB ends, ER 4.5 |
| ISI + EQ net | 1.86 | 1.15 | both assume a 0.55×-baud TIA (measured at 53 G, derived class at 106 G) |
| CD | 0.01 | 0.04 | ~baud² |
| Jitter | 0.73 | 0.95 | similar UI budget, halved UI |
| Crosstalk | 0.36 | 0.36 | kept |
| Threshold | 0.21 | 0.21 | kept |
| **Total** | **4.23** | **4.07** | the real rate cost is in the floor (+1.5 dB) and component specs, not the stack total |

Closure at TP2 = −3.5 dBm (TP3 = −6.0 dBm after 2.5 dB IL):

| Case | Floor | Stack | Required OMA | Margin |
|---|---:|---:|---:|---:|
| Fast Tx 0.35 UI | −11.41 | 3.74 | −7.67 | **+1.67 dB** |
| Typical Tx 0.45 UI (baseline) | −11.41 | 4.07 | −7.34 | **+1.34 dB** |
| Max Tx 0.60 UI | −11.41 | 4.62 | −6.79 | **+0.79 dB** |
| White-scaled existing input stage (5.4 µA) | −10.60 | 4.04 | −6.57 | +0.57 dB |
| $f^2$-scaled (17 µA) | −5.63 | 3.91 | −1.73 | −4.27 dB |

GEN1 reference at the same Tx OMA: floor −12.93, stack 4.23, margin +2.70 dB. Inverting
the stack for the noise requirement: +2 dB margin needs $i_n \le 4.03\ \mu$A
(13.6 pA/√Hz average over the 87 GHz $B_n$) with the pre-microbump ISI accounting, or
3.83 µA with the bump charged — the spec line is written as ≤ 4.0 µA with the margin
target read as +1.9–2.0 dB. The 4.5 µA target class itself closes at +1.34 dB typical.
Tx OMA at −1.5 dBm is the system-level relief valve: +2 dB to every case.

Supporting GEN2 numbers: TDEC proxy through the 53.125 GHz BT4 reference receiver =
0.77/1.11/1.77 dB (fast/typ/max) → spec TDEC ≤ 1.8 dB; slice-DAC FIR analysis shows
3 taps remain sufficient ($h_{+2} \le 0.01$; a 4th tap buys 0.00 dB even on the worst
measured chain), with tap spacing 9.412 ± 0.47 ps and weight step ≤ 0.02.

---

## 5. Derived GEN2 TIA requirements (script `05`) — the centerpiece

The budget exists to produce this table. Every line is derived from the §2 framework;
the measured family enters as calibration (noise scaling law, §4.3) and as the source
of one lesson learned (group delay, below).

| Parameter | Requirement | Derivation |
|---|---|---|
| Bandwidth ($f_{3\mathrm{dB}}$, differential) | **50–64 GHz window** (53–58 GHz target; 0.50–0.55× baud) | Sweep of total sensitivity (white-scaled floor + ISI+EQ + RIN at $B_n = 1.5 f_{3\mathrm{dB}}$) vs $f_{3\mathrm{dB}}$ is flat at −8.3/−8.4 dBm across 45–64 GHz (−8.38 at 50–53, −8.34 at 58, −8.26 at 64, −8.15 at 70): below the window ISI grows faster than noise saved; above it noise (floor and RIN band) grows ~0.1–0.2 dB/6 GHz for < 0.3 dB ISI benefit. A window spec, not a point spec. Assumed source: PD 30–40 fF + 25 fF bump + ~10 fF pad ≈ 65–75 fF |
| Input-referred noise, total | **≤ 4.0 µA rms** over $B_n = 1.5 \times f_{3\mathrm{dB}}$ (87 GHz at the 58 GHz reference); 6.5 µA absolute fail line | Q-solve inversion of the full stack (§4.4) at $B_n = 87$ GHz: 4.0 µA → ≈ +2 dB margin (pre-bump accounting; 3.83 µA with the bump charged); 6.5 µA → zero margin. The 4.5 µA target class closes at +1.34 dB typical |
| Noise density mask | ≤ 14 pA/√Hz band average; ≤ 16 pA/√Hz spot 1–53 GHz; measure the density to ≥ $1.5 \times f_{3\mathrm{dB}}$ (≈ 90 GHz) before integrating | 4.0 µA ÷ √(87 GHz) = 13.6 pA/√Hz. Shape check: an $f^2$-shaped input density at equal total rms sees **≤ 0 dB** extra post-CTLE penalty vs white (−0.98 to −0.65 dB for corners 15–40 GHz) because the mild optimal CTLE's poles sit where the $f^2$ noise lives. The $f^2$ danger is rms inflation with bandwidth (the §4.3 scaling law), so the spec binds full-band rms + a spot ceiling instead of a CTLE allowance |
| Magnitude peaking | **≤ 1.0 dB** over DC–53 GHz, monotonic rolloff above the peak | Variable-$Q$ 2nd-order sweep at fixed 58 GHz $f_{3\mathrm{dB}}$: 1.25 dB peaking ($Q=1.0$) costs +0.11 dB over the 1.15 dB ISI+EQ line; 2.4 dB costs +0.33; 6.3 dB → 4.27 dB (unusable) |
| Group-delay ripple | **≤ 3 ps p-p over 2–40 GHz** (0.32 UI) | Lesson from characterization data: the widest measured settings are flat to 0.2 dB in magnitude yet carry 12.5 ps of GD ripple → $h_{-1} \approx 0.48$ pre-cursor that no CTLE can remove (CTLE shapes magnitude; pre-cursor needs phase). 3–4 ps keeps $h_{-1} \le 0.12$ and ISI+EQ within +0.1 dB. The GEN1 design point's 7.15 ps is benign at 53 GBd (0.38 UI) — the ripple budget halves in UI terms with the rate. Phase data is a first-class deliverable |
| Transimpedance gain $Z_T$ | **≥ 57 dBΩ** (≥ 700 Ω) differential at max gain | Eye current at sensitivity $= 2Q i_n = 63\ \mu$App; a 10–15 mV$_{\mathrm{ppd}}$ slicer needs only 44–48 dBΩ, but keeping TIA noise ≥ 3× an assumed ≤ 1 mV rms downstream (CTLE+slicer) noise sets 56.5 → 57 dBΩ. Measured family spans 58.7–87.1 dBΩ — met by existing gain classes |
| Overload / dynamic range | No BER degradation 160–700 µApp; gain adjustment ≥ 14 dB in ≤ 1 dB steps | Required-OMA floor −7.34 dBm → 162 µApp; Rx OMA max −1 dBm → 696 µApp (12.7 dB electrical). Output must stay inside the CTLE linear range — hence AGC steps |
| DC handling | Cancellation ≥ 750 µA | Max average power ≈ −0.8 dBm (OMA −1 dBm at ER 4.5) × 0.876 A/W = 731 µA |
| LF cutoff | **≤ 1 MHz**, baseline-wander penalty ≤ 0.05 dB at 72-bit CID | Droop ≈ $2\pi f_{LF} N\,UI$: 1.34 MHz gives 0.05 dB at $N = 72$. Also closes the loop on the §2.4 DC-restoration assumption |

**Rx OMA max governing case (reviewed).** `RX_OMA_MAX_DBM = −1.0` (script `05`) is a
judgment call, not derived from a documented Tx-OMA/link-IL corner. An adversarial
review raised an alternative +1.79 dBm / 1.13 mA$_{\mathrm{pp}}$ max-power case (20.8 dB
electrical dynamic range) from an external "parallel budget"; if a real deployed
variant of this shared TIA macro combines a higher max Tx launch OMA with a lower
minimum link IL than this report's −3.5 to −1.5 dBm / ~2.5–3 dB corners, that variant's
$\mathrm{OMA_{Tx,max}} - \mathrm{IL_{min}}$ would be the true ceiling and the 696 µApp /
750 µA / 14 dB lines below would need to be re-derived against it. No such variant is
documented in this repo's materials, so −1 dBm is retained as the governing case for
now; this is a deliberate decision on unchanged evidence, not an unexamined assumption,
and should be revisited if a higher-power variant of the product line is confirmed to
share this TIA macro.

**Hard gates vs. targets.** The table mixes two kinds of lines, and the distinction
matters at design review:

- **Hard gates** (a part failing any of these does not close the link or violates the
  spec; these are the `verify_tia()` pass/fail lines): $f_{3\mathrm{dB}}$ inside
  50–64 GHz; $i_n \le 4.0\ \mu$A over $B_n = 1.5 f_{3\mathrm{dB}}$ (absolute fail at
  6.5 µA); peaking ≤ 1.0 dB; GD ripple ≤ 3 ps; ISI+EQ ≤ 1.15 dB typ (≤ 1.70 at
  0.60 UI); jitter penalty ≤ 1.0 dB; end-to-end margin ≥ +1.5 dB.
- **Targets** (preferred design points with margin behind them, not pass/fail): the
  53–58 GHz bandwidth center; the 4.5 µA target class (closes at +1.34 dB, i.e. a
  4.5 µA part is *usable*, just below the +2 dB spec intent); Tx 0.45 UI corner
  (0.60 UI still closes at +0.79 dB); Tx OMA −3.5 dBm baseline (−1.5 dBm is the
  relief valve).

**Verification recipe** (implemented as `verify_tia()` in script `05`; runs on the same
data format as the characterization tables):

1. Measure differential TF (100 kHz–≥90 GHz) and output-noise spectrum to
   ≥ $1.5 \times f_{3\mathrm{dB}}$ (≈ 90 GHz); input-refer ($i_n$ = integrated output
   rms ÷ peak single-ended gain); require $i_n \le 4.0\ \mu$A and the density mask.
2. Static response: $f_{3\mathrm{dB}}$ 50–64 GHz; peaking ≤ 1.0 dB with monotonic
   rolloff; GD ripple ≤ 3 ps (2–40 GHz).
3. Analytic floor $2Q i_n/R \le -11.9$ dBm.
4. Pulse-response flow: 2-pole Tx at 0.45 UI × 25 fF bump × measured TF; optimize CTLE
   (zero 10–40 GHz, poles 45–95 GHz); require ISI+EQ ≤ 1.15 dB (≤ 1.70 dB re-run at
   0.60 UI).
5. Jitter: with TJ = 0.351 UI dual-Dirac, eye at ±TJ/2 open with penalty ≤ 1.0 dB.
6. End-to-end: floor + full stack ≤ −7.5 dBm required OMA, i.e. margin ≥ +1.5 dB at
   Tx OMA −3.5 dBm.

**Buildability.** 4.0 µA total (integrated to 1.5× $f_{3\mathrm{dB}}$) with a 65–75 fF
input node is state of the art; it sits in the same 2.5–5 µA / 55–65 GHz range the team
associates with 100 GBd-class TIAs (SiGe or advanced FinFET with T-coil input peaking),
but that range is an unreferenced internal estimate rather than a cited data point (see
Methodology_Provenance.md). The gain line is already met by existing gain
classes; the requirements table defines a new input-stage design class, with the noise
density mask and the phase-quality line as the two genuinely new asks.

---

## 6. Tx/driver requirements and device trade-offs (script `06`)

Real device brackets evaluated as special cases of the GEN2 budget: TIA A (3–4 µA at
50 GHz), TIA B (4–5 µA at 60 GHz), and a no-FIR transmitter whose driver reaches
60 GHz. TIAs modeled as clean Butterworth-2 responses **assumed to meet the §5
peaking/GD lines** — the load-bearing assumption; gate any selection on §5 step 2.

### 6.1 Scenario matrix (margin at Tx OMA −3.5 dBm, BER $10^{-12}$)

| Tx case | A @ 3 µA/50 G | A @ 4 µA/50 G | B @ 4 µA/60 G | B @ 5 µA/60 G |
|---|---:|---:|---:|---:|
| FIR3, typ driver (0.45 UI) | +2.81 | +1.63 | +1.98 | +1.06 |
| FIR3, slow driver (0.60 UI) | +2.22 | +1.04 | +1.40 | +0.48 |
| no-FIR, 60 G driver + MRM 80 GHz | +2.80 | +1.62 | +1.83 | +0.92 |
| no-FIR, 60 G driver + MRM 60 GHz | +2.50 | +1.32 | **+1.63** | +0.72 |
| no-FIR, 60 G driver + MRM 50 GHz | +2.25 | +1.07 | +1.42 | +0.50 |
| no-FIR, 60 G driver + MRM 40 GHz | +1.95 | +0.77 | +1.07 | **+0.16** |

Every cell closes — the trade is margin, risk, and complexity, not feasibility. The
worst-everything cell (+0.16 dB) is now thin, though: it leans on the Tx OMA relief
valve (§8) if any further assumption slips.

### 6.2 What the FIR actually buys: nothing, on this channel

Isolation experiment on an identical 60 + 60 GHz channel (TIA B @ 4 µA): the joint
FIR+CTLE optimizer **converges to zero tap weight** — ISI+EQ = 1.66 dB with or without
the FIR. The channel taps explain it: $h_{-1} = 0.09$, $h_{+1} = 0.22$, nothing beyond
— a mild post-cursor the CTLE removes at ≈ 1.04× noise cost, while the
peak-constrained slice FIR must pay ~1:1 in de-emphasis OMA for the same eye. The
FIR's only net contribution is its slice-DCD jitter charge: DJ 0.14 vs 0.11 UI →
jitter 0.85 vs 0.58 dB — **no-FIR wins by 0.27 dB**, before counting the ±0.47 ps
delay-line accuracy and slice matching it eliminates. Even on the 40 GHz-MRM channel,
re-enabling the FIR buys zero ISI (the optimizer again picks zero taps): a slow MRM
argues for Tx OMA headroom, not for the FIR. The 60 GHz→edge mapping (20–80 % ≈
$0.345/f_p$ per pole; the 60+60 composite measures 5.88 ps = 0.62 UI) and the MRM
sweep (80→40 GHz costs ~0.8 dB, cleanly recoverable post-cursor) bound the risk.

### 6.3 TIA A vs B and the recommendation

At the 4 µA overlap, B beats A by ~0.35 dB in every Tx case (+1.98 vs +1.63 typ): the
50 GHz TIA's extra ISI (+0.54 dB, needing 81–93 GHz CTLE poles at 1.11–1.17× noise)
outweighs its noise-bandwidth savings. The crossover sits at $i_n \approx 3.6\ \mu$A —
below that, A's floor advantage dominates (A @ 3 µA is the best cell, +2.81 dB).

**Recommendation: no-FIR 60 GHz driver + TIA B as the preferred baseline; retain a
single post-cursor tap as a design option pending measured MRM EO response** — and
switch to option A only if it demonstrably lands below ~3.5 µA. This is a baseline
choice, not a closed conclusion: it holds on the modeled clean channel and is
explicitly conditioned on (i) the **phase-quality gate** — verify §5 peaking/GD on the
real silicon before trusting any cell; (ii) the **MRM peaking check** — real MRM
detuning peaking/overshoot is the one thing a Tx FIR fixes that a CTLE cannot, and
strong measured peaking would reverse the no-FIR call in favor of the retained post
tap; (iii) **large-swing edge rate** — if the driver's 60 GHz is a small-signal
number, use the measured large-swing edge (each +0.15 UI of transition costs
~0.5 dB).

---

## 7. Assumptions register

| # | Assumption | Value | Source | Margin sensitivity |
|---|---|---|---|---|
| 1 | Personick Q at $10^{-12}$ | 7.035 | derived (erfc) | definitional |
| 2 | PD responsivity $R$ | 0.876 A/W | measured (`pd` column, TIA TF tables) | ±0.08 A/W → ∓0.4–0.6 dB floor |
| 3 | TIA input-referral convention | SE p-leg peak gain | derived from model structure (conservative) | differential convention would improve floors ~0.3 dB |
| 4 | ER | 3.5 dB (GEN1 spec min) / 4.5 dB (GEN2 target) | spec / assumed | enters shot/RIN/MPI lines |
| 5 | RIN$_{\mathrm{OMA}}$ | −138 dB/Hz | spec (@ 21.4 dB ORL) | −144 (ELS-only): GEN1 RIN line 0.68 → 0.16 dB (margin +1.13 at spec-min) |
| 6 | GEN1 jitter | RJ 0.010 UI rms, DJ 0.10 UI | assumed (DSP-SerDes class) | jitter line 0.61 dB |
| 7 | GEN2 jitter | RJ 0.015 UI = 141 fs, DJ 0.14 UI (incl. 0.05 slice DCD) | assumed; 113 fs judged beyond analog-CDR SOA | jitter line 0.95 dB; no-FIR credits DJ→0.11 (worth 0.27 dB) |
| 8 | Crosstalk isolation | 20 dB adjacent, 2 neighbors, +3 dB ΔOMA | assumed (MRM demux) | 0.36 dB line; 17 dB iso ≈ +0.4 dB |
| 9 | Threshold offset | 2.5 % of swing | assumed (offset cal) | 0.21 dB line |
| 10 | Dark current | 1 µA | assumed worst case | negligible |
| 11 | MPI discount $D$ | 0.5 | Bhatt/King | $D=1$: GEN1 MPI 0.24→0.49 dB |
| 12 | End reflectance | ≤ −24 dB both generations (shared product line; OCI spec only requires −19 dB); connectors 4 × −35 dB | **enforced requirement** (§3.3/§4) — the ~0.2 dB MPI line is ensured by this criterion, not assumed | MPI 0.24 (GEN1) / 0.205 dB (GEN2); a part missing it at −19 dB books 0.51 dB (−0.27 dB margin) |
| 13 | Link IL | 2.5 dB (500 m) | spec | dB-for-dB |
| 14 | Microbump | ≤ 25 fF, ≤ 30 pH; booked as a single 127 GHz pole (unterminated direct drive, §2.4) | derived limit (droop scan); effective node impedance **assumed** pending driver $R_{\mathrm{out}}$ / TIA $R_{\mathrm{in}}$ | 50 fF → +0.5 dB ISI; a low driver output impedance shrinks the +0.22 dB charge |
| 15 | GEN2 Tx corners | 0.35/0.45/0.60 UI 20–80 % | assumed corners | 0.45→0.60 UI costs 0.55 dB |
| 16 | MRM EO bandwidth | 40–80 GHz sweep; no 106 GBd MRM data in repos | user-provided bracket / assumed | 80→40 GHz ≈ −0.8 dB (no-FIR case) |
| 17 | PD capacitance | 30–40 fF | assumed (100G-class waveguide PD; **unmeasured**) | no dB line of its own in the penalty stack — enters the budget only through whether the §5 TIA class ($f_{3\mathrm{dB}}$/noise at a 65–75 fF input node) is buildable; 60 fF would strand the 4.0 µA line |
| 18 | Slicer sensitivity | 10–15 mV$_{\mathrm{ppd}}$; downstream noise ≤ 1 mV rms | assumed (lecture-4 class) | sets $Z_T \ge 57$ dBΩ line |
| 19 | CID run length | 72 bits, 0.05 dB droop | assumed (scrambled NRZ) | sets LF cutoff ≤ 1.34 → 1 MHz |
| 20 | Tx OMA baseline | −3.5 dBm (GEN2) | spec-min at TDEC 3.4 | −1.5 dBm relief adds +2 dB everywhere |
| 21 | TDEC treatment | unscaled from 2.4e-4 to 1e-12 | stated caveat | conservative-neutral |
| 22 | Target-class TIA noise | 4.5 µA total ($B_n = 87$ GHz for shot/RIN) | assumed; internal 2.5–5 µA / 55–65 GHz estimate for the 100 GBd class, **not a cited source** (§5, Methodology_Provenance.md) | ±0.5 µA ≈ ∓0.9–1.0 dB floor |
| 23 | Noise integration bandwidth | $B_n = 1.5 \times f_{3\mathrm{dB}}$, both generations (GEN1 43.9, GEN2 87 GHz) | **convention** — single-pole NEB factor $\pi/2$ rounded; real noise extends beyond $f_{3\mathrm{dB}}$ (§4.3 $f^2$ finding), so shape integrals (0.96–1.10× $f_{3\mathrm{dB}}$) understate it | vs shape-integral accounting: GEN1 stack +0.33 dB, GEN2 stack +0.34 dB |

---

## 8. Risks and open items

**GEN2 margin sensitivity, ranked** (impact on the +1.34 dB typical margin; from the
§7 register sensitivity column and script sweeps — a tornado chart in table form):

| Lever | Swing | Margin impact |
|---|---|---:|
| Tx OMA relief valve | −3.5 → −1.5 dBm | **+2.0 dB** |
| TIA noise | ±0.5 µA around 4.5 µA | **∓0.9–1.0 dB** |
| MRM EO bandwidth | 80 → 40 GHz | −0.8 dB |
| Tx transition corner | 0.45 → 0.60 UI | −0.55 dB |
| Microbump capacitance | 25 → 50 fF | −0.5 dB |
| Crosstalk isolation | 20 → 17 dB | ≈ −0.4 dB |
| $B_n$ convention | 1.5× $f_{3\mathrm{dB}}$ → shape integral | +0.34 dB |
| End reflectance | −24 → −19 dB | −0.31 dB |
| CDR RJ fallback | 141 → 169 fs | −0.19 dB |
| PD capacitance | 30–40 → 60 fF | no direct dB line — **feasibility gate** on the §5 TIA class (strands the 4.0 µA requirement) |

TIA noise and the Tx OMA valve dominate; PD capacitance is not a margin lever but a
buildability gate. This ranking is where validation effort should go first.

1. **MRM peaking and nonlinearity are unmodeled.** The MRM enters as a clean pole. Real
   detuned-MRM peaking/overshoot is the one impairment a Tx FIR fixes that a CTLE
   cannot — it could reverse the no-FIR recommendation (keep one post tap as insurance
   if MRM data shows peaking). 106 GBd MRM EO-bandwidth data does not exist in the repos.
2. **PD capacitance is unmeasured.** The 30–40 fF input assumption underpins the TIA
   bandwidth/noise feasibility argument; a 60 fF PD would make the 4.0 µA line
   materially harder.
3. **TIA phase data is required.** The GD-ripple line (≤ 3 ps) came from
   characterization data showing 12.5 ps ripple with flat magnitude; candidate-TIA
   phase (or time-domain pulse) measurements to 80 GHz must be part of the vendor
   deliverable, or §5 step 4 cannot be run.
4. **Analog-CDR RJ at 141 fs rms** is at the edge of published art at 106 GBd; a
   0.018 UI (169 fs) fallback spec, run through the same typ-Tx/target-TIA jitter chain
   as §4.4, costs an incremental **+0.19 dB** over the 141 fs baseline (script `04`,
   re-evaluated at 8× finer time-grid resolution to avoid a sample-quantization
   artifact — see Methodology_Provenance.md) and should be pre-negotiated in the jitter
   budget.
5. **Tx OMA relief valve.** Raising launch OMA from −3.5 to −1.5 dBm buys 2 dB across
   every scenario — the single most effective system-level knob if any component
   assumption slips (ELS power and MRM insertion loss permitting).
6. **Microbump $R_{\mathrm{eff}}$ is a placeholder.** The 127 GHz bump pole assumes a
   50 Ω effective node impedance (§2.4), but the real driver→MRM and PD→TIA nodes are
   unterminated direct-drive interfaces that will not behave as a simple 50 Ω lump.
   The booked +0.22 dB ISI charge is conservative if the true node impedance is lower
   and optimistic if higher; extracting driver $R_{\mathrm{out}}$ / TIA $R_{\mathrm{in}}$
   from circuit design and re-running the droop scan is required before the ≤ 25 fF
   line can be treated as final.

**Next experiments — the kill-or-confirm set.** The architecture claim reduces to a
finite, measurable list: *106.25 GBd NRZ CPO is feasible provided the TIA achieves the
derived noise/BW/phase class, PD capacitance stays in the assumed range, the MRM
introduces no problematic peaking, and the clock/CDR approaches the RJ target.* The
remaining work is predominantly characterization, not further model iteration — these
four experiments retire the Low-confidence rows of the §1 status table:

1. **Measure PD capacitance and the MRM EO response (S21 magnitude + phase, or
   impulse response) at 106 GBd-relevant bandwidths.** Retires the two unbounded Rx
   and Tx assumptions at once: the 30–40 fF input-node term behind the §5 TIA class,
   and the 40–80 GHz MRM bracket plus the peaking question that gates the no-FIR
   decision (§6.3).
2. **Measure candidate-TIA magnitude, phase, and output-noise spectrum to ≥ 90 GHz**
   ($\ge 1.5 \times f_{3\mathrm{dB}}$). Feeds `verify_tia()` directly (§5 recipe),
   replaces the $B_n$ convention with the measured noise integral (§2.3), and tests
   the GD-ripple line on real silicon.
3. **Characterize the actual clock/CDR RJ** against the 141 fs rms target (and the
   169 fs / 0.018 UI fallback, item 4 above). The jitter line is currently the only
   hard-gate input with no measured-part backing at all — items 1–2 at least start
   from repo characterization data; RJ is a pure forward assumption.
4. **Run the complete measured chain end-to-end** — EIC driver → bump → MRM → fiber →
   PD → bump → TIA — through the §2.4 pulse engine with all-measured blocks, and
   compare against the stack's model-based ISI+EQ, jitter, and TDEC lines. This is
   the closure test that converts the +1.34 dB from a model result into a
   demonstrated one.

If all four land inside the assumptions register, the budget has done its job: it has
converted "can 106G CPO NRZ work?" into a finite set of measurable component
requirements, per the §1 bottom line.

---

## 9. Appendix A: reproduction guide

### Script-to-result map

| Result | Script | Canvas |
|---|---|---|
| 152-setting survey; GEN1 design point (3.17 µA / 29.3 GHz); floor −12.93 dBm | `01_tia_survey.py` | bottom-up §1 |
| GEN1 stack 2.93 dB; required −10.00 dBm; +0.60 / +2.30 dB; sensitivity table | `02_bottom_up_budget_53g.py` | bottom-up §2–5 |
| 53 GBd CPO: Tx corners, EQ scenarios (CTLE-only 1.86 dB), stack 4.23, +2.70 dB; microbump/package | `03_cpo_gen2_53g.py` | GEN2 spec, GEN1 column |
| Noise scaling regression (R² 0.87 vs 0.59); scaled floors −10.60/−5.63; target floor −11.41; ISI+EQ 0.82/1.15/1.70; jitter 0.95; stacks 3.74/4.07/4.62 → +1.67/+1.34/+0.79; required 4.03 µA; TDEC proxy | `04_gen2_106g_feasibility.py` | GEN2 spec §2–6 |
| BW window plateau −8.3/−8.4 dBm; noise-shape ≤ 0 dB; peaking/GD sweeps; 12.45 ps ripple → $h_{-1}$ 0.477; $Z_T$ ≥ 57 dBΩ; 162–696 µApp / 731 µA; 1.34 MHz; `verify_tia()` | `05_tia_requirements.py` | GEN2 spec §7 |
| 24-cell margin matrix; FIR isolation (0.27 dB); MRM sweep; A/B crossover 3.6 µA | `06_device_tradeoffs.py` | device trade-offs |

### Canvas cross-reference

- `canvases/200G-OCI-link-budget.canvas.tsx` — spec-side framing: TDEC-coupled OMA law,
  SRS closure-by-construction, Q table, IEEE parameter table (below), COUPE waterfall
  cross-check.
- `canvases/OCI-link-budget-bottom-up.canvas.tsx` — GEN1 bottom-up budget (§3 here).
- `canvases/OCI-GEN2-CPO-spec.canvas.tsx` — GEN2 budget, proposed spec, TIA
  requirements (§4–5 here).
- `canvases/OCI-GEN2-device-tradeoffs.canvas.tsx` — device trade study (§6 here).

Reproduction status: canvas numbers reproduced exactly or within ±0.01 dB rounding at
the time the canvases were made, but the report has since adopted two deliberate
accounting changes the canvases do not carry:

1. **End reflectance −24 dB for GEN1** (shared GEN1/GEN2 product line, §3.3) — the
   bottom-up canvas's 2.87 dB / +0.66 dB used the spec's −19 dB. Script `02`
   reproduces the canvas with `MPI_REFL_DB=-19`.
2. **Noise integration bandwidth $B_n = 1.5 \times f_{3\mathrm{dB}}$** (§2.3, register
   row 23) — the canvases used signal-TF shape integrals (GEN1 28.2 GHz, GEN2 64 GHz),
   giving GEN1 shot/RIN 0.11/0.41 (now 0.18/0.68), GEN2 RIN+shot 0.82 (now 1.16),
   GEN2 margins +2.00/+1.67/+1.12 (now +1.67/+1.34/+0.79), and the noise ceiling
   4.37 µA / 17 pA/√Hz (now 4.03 µA / 13.6 pA/√Hz). Scripts reproduce the canvases by
   reverting the `BWn`/`BN_T` lines to the shape integrals (see script comments).

One accounting footnote: the spec canvas's "$i_n \le 4.4\ \mu$A → +2 dB margin" was
additionally derived before the 25 fF microbump was charged to the ISI line; the
current equivalents are 4.03 µA pre-bump / 3.83 µA with the bump charged. Script `04`
prints both accountings.

### OCI MSA vs IEEE P802.3dj (D1.3) parameter table

| Parameter | OCI MSA v1.0 | Cl. 181 FR4-500 | Cl. 180 DR |
|---|---|---|---|
| Modulation / baud | 53.125 GBd NRZ × 4λ | 106.25 GBd PAM4 × 4λ | 106.25 GBd PAM4 / fiber |
| Reach / channel IL | 500 m / 2.5 dB | 500 m / 3.5 dB | 500 m / 3.0 dB |
| Penalty allocation | 0.2 dB (MPI only) | 3.9 dB (0.5 MPI+DGD) | 3.5 dB (0.1 MPI+DGD) |
| Tx OMA min (worst TDEC/Q) | −3.5 dBm | +3.3 dBm | +2.2 dBm |
| TDEC(Q) / SEC(Q) max | 3.4 / 3.4 dB | 3.4 / 3.4 dB | 3.4 / 3.4 dB |
| Rx sensitivity (SRS, worst Tx) | −6.2 dBm | −0.7 dBm | −0.9 dBm |
| ER min | 3.5 dB | 3.5 dB | 3.5 dB |
| RIN / ORL tolerance | −138 dB/Hz @ 21.4 dB | −139 dB/Hz @ 17.1 dB | −139 dB/Hz @ 21.4 dB |
| Tx/Rx reflectance max | −19 dB | −26 dB | −26 dB |
| Discrete reflectance | not specified | −25…−41 dB by count (Table 181-10) | −35 dB |
| BER basis | flat pre-FEC 2.4e-4 | block error ratio (174A) | same |

---

## 10. Appendix B: references and inputs

**Standards and specs**

- *200G OCI Optical PHY Specification v1.0* (March 2026) —
  `food/200G-OCI-Optical-Phy-Specification-v1.0.pdf`. Key inputs: Tx OMA min
  $\max(-5.5, -6.9+\mathrm{TDEC})$ dBm, TDEC ≤ 3.4 dB, ER 3.5–4.5 dB, 500 m SMF-28
  link with IL ≤ 2.5 dB and CD −0.9…+1.7 ps/nm, MPI tolerance 0.2 dB, SRS −6.2 dBm,
  RIN$_{\mathrm{OMA}}$ ≤ −138 dB/Hz @ 21.4 dB ORL, Rx/Tx reflectance ≤ −19 dB.
- *IEEE P802.3dj Draft 1.3* (Dec 2024), Clauses 180/181 —
  `food/Copy of P802d3dj draft D1p3 as shared with OIF 2024_12.pdf`. Used as the
  budget-structure template (penalty allocations, Table 181-10 discrete-reflectance
  framework, TDECQ/SRS measurement methods). The OCI MSA closely mirrors Clause 181
  (800GBASE-FR4-500) recast from 106.25 GBd PAM4 to 53.125 GBd NRZ.
- Receiver/transmitter/jitter methodology (Sackinger-style):
  `food/lecture4_ee721_rx_analysis.pdf` (Personick sensitivity, input-referral, power
  penalties), `food/lecture7_ee721_tx_analysis.pdf` (ER, dispersion),
  `food/lecture10_ee720_jitter.pdf` (dual-Dirac total jitter).
- MPI model: Bhatt / King IEEE 802.3bs presentations —
  `food/bhatt_3bs_01a_0116 (1).pdf`, `food/king_01a_0116_smf (1).pdf`.

**Repo data (read directly by the scripts)**

- TIA characterization, 152 settings (TT corner):
  `LM-link-vpiphotonics/Mesa/Components/TIA/Ocelot_TIA_ADFET.vtmg_pack/Inputs/TT_TIA_DATA_ED_ADFET_20250520/`
  — `TT_Tia_Noise.csv` (output noise rms per setting) and `TT_Tia_TF_<key>.csv`
  (complex single-ended p/n-leg transfer functions and the PD column, 0–67 GHz).
- Tx driver class: `LM-link-vpiphotonics/Caribou/COUPE_models/DWDM_TxDrv/DWDM_COUPE_TxDrv.vtmg_pack/Inputs/Typ_Txdrv_NL.csv`
  (~1.2 V$_{\mathrm{ppd}}$ swing class; used to ground the realistic-Tx OMA case).
- Package traces (the channel CPO eliminates): `Caribou_EOE/Package/TL_TX_64G.s4p`,
  `TL_RX_64G.s4p` (differential S21: 1.31/0.55 dB IL at 26.6 GHz; 1.61/0.72 dB at 53.1 GHz).
- GEN2 architecture block diagram: `OCI-GEN2_Simplified.png` (copied into this folder
  from `mydocs/oci_msa/OCI-GEN2 Simplified.png`; reproduced in §4.1). Cascaded 2×
  1-UI delay line feeding pre/main/post limiting driver slices, summed through a
  microbump into the MRM (laser feeds the MRM directly); mux/channel/demux, PD,
  second microbump, TIA; CTLE-only Rx, no DFE.
- TIA options A/B and the 60 GHz-driver trade case in §6 are user-provided device
  brackets (no repo file).

Nothing under `sandbox/alex` feeds the scripts; the independently produced COUPE BIDI
waterfall (−11.8 dBm OMA at BER $10^{-12}$) is cited once in §3 as a sanity
cross-check only.
