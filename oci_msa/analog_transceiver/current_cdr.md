# Current CDR — comprehensive reference

**Purpose** — a complete, self-contained specification of the CDR that lives in
the simulator today.  Written to (a) freeze the design as of Milestone 9b so
that further work has a known-good baseline, and (b) feed the fixed-point
tables in `OCI_Gen2_PMA_Architecture.md` Chapter 11 once the remaining
Milestone-10 gate is implemented.

**Scope** — the CDR class hierarchy in
`src/optical_serdes/rx/mm_cdr.py`, the LMS channel estimator that drives the
production variant, the lock detector, and the top-level simulator plumbing
(`scripts/analog_rx/oci_msa_analog_txrx.py`,
`scripts/analog_rx/diagnose_analog_run.py`) that wraps all of it.

**Status as of 2026-07-17 (Milestone 9b)** — the estimator-driven MM-CDR is the
production variant.  With `ki = 1 × 10⁻³, freq_max = 1 × 10⁻¹,
updn_threshold = 128` it delivers Q-limited BER on `cpo_interposer_3db` up to
σ ≤ 0.10 (7 counted errors / 400 k bits, matching Q@lk = 2.65).  At σ ≥ 0.16
the integrator winds up because every `e_k`-only anti-windup scheme is
structurally insufficient; the Milestone-10 lock-gated integrator is the
remaining fix.

---

## 1. Where the CDR sits in the receiver

```
symbols (PRBS-31)
   ↓
   ×(1/1.6)                                            (drive_scale)
   ↓
elec IR (EIC→PIC, TX leg)                              (cpo_interposer_3db)
   ↓
SmfLink   [TX driver → RC → MRM → SMF → PD+TIA]        (nonlinear at MRM)
   ↓
elec IR (PIC→EIC, RX leg — same interconnect)
   ↓
tp4 waveform            (percentile-normalised → rx_base ∈ [~-1, ~+1])
   ↓
AWGN                    (add_awgn_waveform, σ = NOISE_RMS_V, seed = NOISE_SEED)
   ↓
CTLE (optional; bypass in the current PEAKING_DB_LIST=[0.0] runs)
   ↓
rx                      (32× oversampled, samples-per-UI = OSR = 32)
   ↓
─────────────────────  the CDR + estimator loop runs here  ────────────────
   │
   │   idx = round(data_pos)  ← sample selector (data_pos advances by
   │                              OSR + Δphase every UI)
   │   y   = rx[idx]
   │                              ┌─── data slicer  d = sign(y) ────────► d_hist
   │                              │
   │                              │    error slicer  z = sign(y − d·ĥ₀)
   │   ┌────────────────────┐    │
   │   │  h₀ SS-LMS         │◄───┘    ĥ₀[n+1] = ĥ₀[n] + μ_h0·d·z
   │   └────────────────────┘
   │
   │   ┌────────────────────┐
   │   │  ChannelEstimator  │◄──── y, d          ĥ_i[n+1] = ĥ_i[n] +
   │   │  (sign-error LMS)  │                             μ_taps·sign(e_n)·d[n-i]
   │   │  ĥ₋₁, ĥ₀, ĥ₁       │
   │   └────────────────────┘
   │             │
   │             │ ĥ₋₁, ĥ₀, ĥ₁ (three taps)
   │             ▼
   │   ┌────────────────────┐
   │   │  EstimatorMmCdr    │  discriminant + polarity + PI filter
   │   │  step()            │  → pi_code, state.phase_accum, state.freq_accum
   │   └────────────────────┘
   │             │
   │             │ Δphase = state.phase_accum − prev_phase
   │             ▼
   │   data_pos += OSR + Δphase   ← closes the timing loop
   │
   │   (in parallel)
   │   ┌────────────────────┐
   │   │  SpeculativeDfe    │   two ±h₁_est comparators + MUX
   │   │  step(y)           │   → produces d (data decision fed to the estimator)
   │   └────────────────────┘
   │
   └── outputs: pi_hist, h0_hist, h1_hist, hm1_hist, dfe_h1_hist, d_hist,
                freq_hist, phase_unwrap_hist
```

Key contract for the CDR:

* **Input each UI** — the three estimated taps `(ĥ₋₁, ĥ₀, ĥ₁)` produced by the
  channel estimator from the pre-CTLE / pre-DFE waveform.  The CDR **never**
  sees the raw ADC sample; that stays in the analog domain.
* **Output each UI** — one `pi_code ∈ [0, OSR)`, which the simulator turns
  into an integer sample-index displacement for the next UI.  In a real
  receiver this is a phase-interpolator code.
* **Latent state** — `state.phase_accum` (continuous float, "unwrapped" phase),
  `state.freq_accum` (integrator), `state.freq_updn_counter` (up/down counter
  for the anti-windup dead-zone).

---

## 2. Three CDR classes live in the tree

The MM-CDR module ships three mutually-substitutable classes.  They differ in
what feeds the timing-error detector (TED) and where the polarity reference
comes from.  Only the third is currently in production use.

| Class | TED input | Polarity source | Loop filter | Status |
|---|---|---|---|---|
| `MuellerMullerCDR` | ADC samples `y[k]` + slicer `â[k]` | fixed sign | PI, first- or second-order | Digital-DSP receivers only. Not used by the analog RX path. |
| `AnalogMmCdr` (bang-bang) | slicer outputs `d[k], z[k]` (ternary) | `sign(h₁_true)` (heuristic) | PI, first-order default, second-order optional | **Deprecated** for anything but the `cdr_lock_vs_channel_loss.py` polarity sweep. Suffers a ~0.5 UI anti-phase false lock once the combined postcursor flips sign. |
| **`EstimatorMmCdr`** | LMS-estimated `ĥ₋₁, ĥ₀, ĥ₁` | `sign(ĥ₀)` (from LMS) | PI + three-layer anti-windup (freq_max clamp, leaky integrator, up/down-counter dead-zone) | **Production.** Selected by `CDR_MODE = "estimator"` in `oci_msa_analog_txrx.py`. |

There is also `BangBangCDR` in `src/optical_serdes/rx/cdr.py` — a
Sonntag-Stonick Alexander-bang-bang phase detector paired with the same PI
loop filter — used by the *DSP-side* clock recovery, not by the analog RX
chain.  The lock-detector class (`CdrLockDetector`, same file) is shared
between all four CDRs.

Everything below documents `EstimatorMmCdr` and its supporting cast.

---

## 3. Estimator-driven MM CDR — mathematical spec

### 3.1 Timing discriminant

At each UI, the LMS channel estimator supplies `(ĥ₋₁, ĥ₀, ĥ₁)`.  The CDR forms
a scalar **raw discriminant**

$$
  e_{\mathrm{raw}} = w_{\text{post}}\,\hat{h}_1 - w_{\text{pre}}\,\hat{h}_{-1}
$$

* `w_pre = w_post = 1.0` is the symmetric Mueller-Muller balance.  The
  simulator exposes both weights (`W_PRE`, `W_POST`) so the lock point can be
  biased toward matching one cursor more than the other — a lock-phase trim
  rather than a stability knob.
* At the ideal sampling instant `ĥ₋₁ ≈ ĥ₁` (up to loop noise), so
  `e_raw ≈ 0`.  Sampling early ⇒ `ĥ₁` grows, `e_raw > 0`; sampling late ⇒
  `ĥ₋₁` grows, `e_raw < 0`.  (Signs flip with cursor polarity — see 3.2.)

Two **drive modes** consume `e_raw`:

| `drive_mode` | Drive value `d_k` | Notes |
|---|---|---|
| `"proportional"` (default) | `d_k = e_raw` | Uses the magnitude of the smoothed tap estimates → low-variance loop. Requires wider datapaths in RTL. |
| `"bangbang"` | `d_k = sign(e_raw)` ∈ {-1, 0, +1} | Throws away magnitude; matches the classical BBPD idiom. Robust but noisier. |

The choice is orthogonal to the loop filter and to the anti-windup layers.

### 3.2 Polarity handling — `sign(ĥ₀)` is the correct reference

The discriminant's slope at the cursor zero is
`-sign(ĥ₀)`.  If the loop polarity `loop_sign` matches that slope, the
proportional path drives phase back toward zero (stable equilibrium); if it
disagrees, the loop is pushed *away* from the cursor and toward the ~0.5 UI
anti-phase zero.

`EstimatorMmCdr` supports three polarity modes:

| `polarity_mode` | `loop_sign` | Purpose |
|---|---|---|
| `"h0_sign"` (default) | `sign(ĥ₀)` from LMS | Robust to cursor-polarity flips (e.g. MRM through-port operation on some channels). |
| `"h1_sign"` | `sign(ĥ₁)` from LMS | Legacy behaviour matching `AnalogMmCdr`. Kept for A/B testing. |
| `"fixed"` | `fixed_loop_sign` field (±1) | For channels whose polarity is known once and does not change. |

The final CDR error is

$$
  e_k = \operatorname{loop\_sign} \cdot d_k
$$

### 3.3 Loop filter — proportional + integral

Standard second-order digital PI, with an update rule that is chosen by
`freq_updn_threshold`.

**Proportional path (always active):**

$$
  \phi_{n+1} \mathrel{+}= k_{p}\,e_k
$$

**Integral path — three cascaded stages:**

*Stage 1: integrator input selection.*

$$
  \text{if } \texttt{freq\_updn\_threshold} \le 0 \colon
    \quad f_{\text{inc}} = k_i \cdot e_k
$$

$$
  \text{else} \colon \quad \text{a signed up/down counter accumulates}
    \operatorname{sign}(e_k),
$$
$$
  \text{when } |c| \ge \texttt{freq\_updn\_threshold}\!,\ f_{\text{inc}} =
    \pm k_i \text{ and } c \gets 0;
$$
$$
  \text{otherwise } f_{\text{inc}} = 0.
$$

The counter branch is the classical BBPD "digital loop filter" idiom.  Under
balanced bang-bang noise the counter random-walks in a ±√N band and rarely
crosses; a real ppm bias produces persistent same-sign counts and updates
`freq_accum` at a rate ∝ Δppm.  Rule of thumb: `threshold ≳ 3·√(N_avg)` so
noise-driven crossings are ≪ 1 per `N_avg`-UI window.

*Stage 2: leaky integrator update.*

$$
  f_{n+1} = (1 - \lambda_{\text{leak}})\,f_n + f_{\text{inc}}
$$

`λ_leak = freq_leak ∈ [0, 1)`.  Zero recovers a pure integrator.  A positive
value gives `freq_accum` a `1/λ_leak`-UI time constant — noise-driven random
walk decays back toward zero while real frequency offsets larger than
`freq_leak / ki` are still tracked.

*Stage 3: hard clamp.*

$$
  f_{n+1} \gets \operatorname{clip}(f_{n+1},\ \pm F_{\max})
$$

`F_max = freq_max` in codes/UI.  Physical meaning: `F_max / OSR` is the
maximum tracked frequency offset as a fraction of the baud rate.  Default
`2.0` ⇒ ±6.25 % ⇒ ±62 500 ppm — vastly looser than any realistic host/remote
clock budget.  A realistic ±100 ppm budget on a 106.25 GBaud line ⇒
`F_max ≈ 3.2 × 10⁻³`.

**Phase accumulator and PI code:**

$$
  \phi_{n+1} \mathrel{+}= f_{n+1}
$$
$$
  \operatorname{pi\_code}_{n+1} = \operatorname{round}(\phi_{n+1}) \bmod n_{\text{phases}}
$$

`n_phases = OSR = 32`.  The accumulator itself is a Python float — no wrapping
in the simulator — so `state.phase_accum` is the **unwrapped** phase used for
the drift diagnostics (see §7).  Only the reported `pi_code` wraps.

### 3.4 Full step, as executed

```
e_raw = w_post · ĥ₁ − w_pre · ĥ₋₁
if drive_mode == "proportional":   d_k = e_raw
else:                              d_k = sign(e_raw)

loop_sign = { sign(ĥ₀),  sign(ĥ₁),  or  fixed_loop_sign }
e_k = loop_sign · d_k

# integrator input
if freq_updn_threshold ≤ 0:
    f_inc = ki · e_k
else:
    counter += sign(e_k)
    if abs(counter) ≥ freq_updn_threshold:
        f_inc = ki · sign(counter);  counter = 0
    else:
        f_inc = 0

# integrator update
freq_accum = (1 − freq_leak) · freq_accum + f_inc
freq_accum = clip(freq_accum, ±freq_max)

# phase update
phase_accum += kp · e_k + freq_accum
pi_code = round(phase_accum) mod n_phases

lock_detector.step(kp · e_k, freq_accum, kp)     # optional
```

---

## 4. Companion adaptation loops

The CDR is one of several loops that all update every UI.  All are simulated
in `oci_msa_analog_txrx.py::run_cdr_estimator_with_dfe`.

### 4.1 Channel estimator (`ChannelEstimator`, sign-error LMS)

Three-tap estimator (`n_precursor = 1`, `n_postcursor = 1`) supplying
`(ĥ₋₁, ĥ₀, ĥ₁)` to the CDR.  The observation FIFO delays `y` by
`n_precursor + decision_delay` UI so future decisions are available when the
`ĥ₋₁` tap updates.

Prediction error per UI:

$$
  \varepsilon_n = y_{n - D} - \sum_i \hat{h}_i\,d_{n - D - i},\qquad
  D = n_{\text{pre}} + n_{\text{decision-delay}}
$$

Sign-error LMS update (`adaptation = "sign_error"`):

$$
  \hat{h}_i[n+1] = \hat{h}_i[n] + \mu \cdot \operatorname{sign}(\varepsilon_n) \cdot d_{n-D-i}
$$

with `mu = MU_TAPS = 5 × 10⁻⁴`.  Sign-error was chosen (over full LMS) because
its per-tap update reduces to a single `±μ` step — trivially fixed-point
implementable and unbiased against Gaussian input under mild conditions.

The estimator's `ĥ₀` is used **only** as a polarity reference for the CDR.
The error-slicer threshold `h₀_est` used by the physical slicer path is a
*separate* SS-LMS instance (see §4.2), running from `d·z` rather than
from `sign(y − Σĥ_i·d[n-i])·d[n]`.  The two ĥ₀ signals are analytically
equivalent in steady state but track different noise sources, so keeping them
independent is a diagnostic advantage.

### 4.2 h₀ SS-LMS on the error-slicer threshold

```
h₀_est[n+1] = h₀_est[n] + μ_h0 · d[n] · z[n]
```

with `μ_h0 = MU_H0 = 5 × 10⁻⁴`.  Runs entirely in the RX chain (does not
depend on the channel estimator) and provides the threshold consumed by the
error slicer

```
z[n] = sign( y[n] - d[n] · h₀_est )
```

### 4.3 Speculative-DFE h₁

When `ENABLE_SPEC_DFE = True`, the zero-crossing data slicer is replaced by
two programmable-threshold comparators at `±h₁_DAC` and a 1-bit MUX
(`SpeculativeDfe`, `n_taps = 1`, `unrolled_depth = 1`).  The DFE runs its own
SS-LMS on `h₁_DAC` with `μ_h1 = MU_H1 = 5 × 10⁻⁴` and produces `d[n]`.

Crucially, the CDR error slicer `z[n]` is still computed from **raw `y[n]`**
— never from the DFE-equalised `y_sel[n]` — so the CDR always sees the full
channel `h₁` regardless of DFE convergence state.  This is a decoupling
requirement: it prevents chicken-and-egg during acquisition and makes the
CDR robust to a mis-adapted DFE.

Under normal operation the DFE's `h₁` and the channel estimator's `ĥ₁` are
close in magnitude and opposite in sign (DFE cancels the postcursor that
the estimator measures).

---

## 5. Lock detector

`CdrLockDetector` in `src/optical_serdes/rx/cdr.py` (adapted from PyBERT).
Optional field on every CDR class.  When set, it runs alongside `step()` and
exposes a `.locked` property.

### 5.1 Metric

Rolling-window statistics on the two loop-filter outputs, `n_lock_ave = 500`
UI by default:

```
mean_prop = mean(kp · e_k over last N)
var_int   = mean((freq_accum)² over last N)

lock = (|mean_prop / kp| < rel_lock_tol) AND (var_int / kp < rel_lock_tol)
```

with `rel_lock_tol = 0.01`.  Result is fed to a `lock_sustain = 500`-UI
hysteresis window: LOCK is asserted when 80 % of the last window is locked,
released when only 20 % is.

### 5.2 Known deficiency — modulo-32 wrap fools it

In Milestone 9 the top-level `lock_frac` metric (fraction of post-settle
`pi_code` within ±5 of the modal code, wrap-aware) declared σ = 0.10 /
`ki = 0` operating points 97 % locked while accumulated drift was **92 UI**.
This is the diagnostic-level `lock_frac`, not the class-level lock detector —
but the same wraparound blindness affects the class detector unless the
integrator saturates, because a slow random walk in `freq_accum` looks
identical to a stable low variance over a 500-UI window.

The Milestone-9b conclusion is that the lock detector *must* be built on the
**unwrapped** phase or on LMS-tap asymmetry, not on `pi_code` mod OSR.  See
§10 for the fix plan.

---

## 6. Complete knob catalogue

### 6.1 Module-level constants (`oci_msa_analog_txrx.py`)

| Constant | Type | Default | Meaning |
|---|---|---|---|
| `OSR` | int | 32 | Oversampling ratio. Sets `n_phases`. |
| `BAUD_RATE` | float | `106.25e9` | Symbol rate. |
| `INITIAL_PI` | int | 0 | Starting `phase_accum` value (integer code). |
| `KP` | float | 1.0 | Proportional gain for `AnalogMmCdr` (bang-bang variant). |
| `SETTLE_UI` | int | 500 | UIs skipped before BER / lock-frac / Q measurement. |
| `CDR_MODE` | str | `"estimator"` | `"instantaneous"` ⇒ `AnalogMmCdr`; `"estimator"` ⇒ `EstimatorMmCdr`. |
| `MU_TAPS` | float | `5e-4` | Sign-error LMS step for the channel estimator (per-tap). |
| `W_PRE` | float | 1.0 | Weight on `ĥ₋₁` in `e_raw`. |
| `W_POST` | float | 1.0 | Weight on `ĥ₁` in `e_raw`. |
| `DRIVE_MODE` | str | `"proportional"` | Feed real-valued `e_raw` (default) or `sign(e_raw)` to the loop filter. |
| `KP_EST` | float | 4.0 | Proportional gain for `EstimatorMmCdr`. Larger than `AnalogMmCdr`'s `KP=1.0` because `e_raw ~ O(0.1)`. |
| `KI_EST` | float | 0.0 | Integral gain. `0` ⇒ proportional-only ⇒ phase random walk under AWGN. Working value at σ ≤ 0.10 is `1e-3`. |
| `FREQ_MAX` | float | 2.0 | Integrator clamp in codes/UI. `2.0` ≈ ±62 500 ppm (unphysical). Realistic ±100 ppm ⇒ `≈ 3.2e-3`. |
| `FREQ_LEAK` | float | 0.0 | Leaky-integrator decay per UI. `0` ⇒ pure accumulator. |
| `FREQ_UPDN_THRESHOLD` | int | 0 | Up/down-counter threshold. `0` ⇒ every-UI direct integrator update. |
| `MU_H0` | float | `5e-4` | SS-LMS step for the error-slicer threshold. |
| `H0_INIT` | float | 0.0 | Initial threshold estimate. |
| `MU_H1` | float | `5e-4` | SS-LMS step for the speculative-DFE `h₁_DAC`. |
| `H1_INIT` | float | 0.0 | Initial DFE tap. |
| `ENABLE_SPEC_DFE` | bool | True | Enables the ±`h₁_DAC` slicer pair for data decisions. CDR is unaffected. |
| `N_DFE_TAPS` | int | 1 | Speculative-DFE depth. Only tested at 1. |

### 6.2 `EstimatorMmCdr` fields (in code order)

| Field | Type | Default | Range | Notes |
|---|---|---|---|---|
| `kp` | float | 0.05 | > 0 | Proportional gain. Sim override: `KP_EST = 4.0`. |
| `ki` | float | 0.0 | ≥ 0 | Integral gain. Sim override: `KI_EST`. |
| `freq_leak` | float | 0.0 | `[0, 1)` | Per-UI leak. Sim override: `FREQ_LEAK`. |
| `freq_updn_threshold` | int | 0 | ≥ 0 | Up/down-counter dead-zone. Sim override: `FREQ_UPDN_THRESHOLD`. |
| `n_phases` | int | 32 | > 1 | PI resolution. Set from `OSR`. |
| `freq_max` | float | 2.0 | > 0 | Integrator clamp. Sim override: `FREQ_MAX`. |
| `initial_phase` | float | 0.0 | any | Starting `phase_accum`. Set from `INITIAL_PI`. |
| `w_pre` | float | 1.0 | ≥ 0 | Weight on `ĥ₋₁` in `e_raw`. |
| `w_post` | float | 1.0 | ≥ 0 | Weight on `ĥ₁` in `e_raw`. |
| `drive_mode` | str | `"proportional"` | `{"proportional", "bangbang"}` | See §3.1. |
| `polarity_mode` | str | `"h0_sign"` | `{"h0_sign", "fixed", "h1_sign"}` | See §3.2. |
| `fixed_loop_sign` | int | 1 | ±1 | Used only when `polarity_mode = "fixed"`. |
| `lock_detector` | `CdrLockDetector | None` | None | Optional lock detector; see §5. |

### 6.3 `EstimatorMmCdrState` fields

| Field | Type | Initial | Notes |
|---|---|---|---|
| `phase_accum` | float | `initial_phase` | Unwrapped continuous phase (float, no wrap). |
| `freq_accum` | float | 0.0 | Integrator state. Clamped to `±freq_max`. |
| `freq_updn_counter` | int | 0 | Signed running counter for the up/down-counter path. Reset to 0 on each threshold crossing. |

---

## 7. Instrumentation

Both `run_cdr_estimator` and `run_cdr_estimator_with_dfe` return per-UI
history arrays.  The **last two** are new in Milestone 9b and exist
specifically for the runaway diagnostic.

| Array | Shape | What it is | Why it's captured |
|---|---|---|---|
| `pi_hist` | `(n_ui,)` int32 | `pi_code mod OSR` | Standard CDR trajectory view. **Modulo-wrapped**, so it hides drift that exceeds ±½ UI. |
| `h0_hist` | `(n_ui,)` float64 | `h₀_est` (error-slicer threshold, SS-LMS) | AGC-adjacent tracking. |
| `h1_hist` | `(n_ui,)` float64 | `ĥ₁` from the channel estimator | Direct sensor output. |
| `hm1_hist` | `(n_ui,)` float64 | `ĥ₋₁` from the channel estimator | Direct sensor output. |
| `dfe_h1_hist` | `(n_ui,)` float64 or `None` | `h₁_DAC` from the speculative-DFE SS-LMS | Independent tap; converges to `−ĥ₁`. |
| `d_hist` | `(n_ui,)` int8 | Slicer data decisions ±1 | Fed to counted-BER measurement. |
| `freq_hist` | `(n_ui,)` float64 | `state.freq_accum` per UI | Reveals integrator saturation / runaway. |
| `phase_unwrap_hist` | `(n_ui,)` float64 | `state.phase_accum` per UI (unwrapped) | Reveals slow drift hidden by `pi_code mod OSR`. |

The `diagnose_analog_run.py` script renders three diagnostic PNGs that
consume these arrays:

* `..._adapt.png` — `pi_hist` + `h0/h1/hm1/dfe_h1_hist` (standard convergence panel).
* `..._loop.png` — three-panel loop-internals view (wrapped `pi_code`,
  `freq_accum` with ±`freq_max` markers on a codes/UI axis and a companion
  ppm axis, unwrapped `phase_accum`).  This is the panel that made the
  σ ≥ 0.16 runaway visible.
* `..._slip.png` — three-panel slip-diagnostic view: `pi_hist`, per-block BER
  under a fixed reference alignment (crimson) vs. per-block BER after
  ±8 UI local re-alignment (green), and Δ-lag per block.  Non-zero Δ-lag =
  phase slip.  This panel is produced by `render_block_ber` and consumes the
  dict returned by `compute_block_ber` in `oci_msa_analog_txrx.py`.

Every diagnostic PNG's filename encodes the sweep parameters, so the same
directory can hold dozens of `(σ, ki, freq_max, freq_leak, updn_threshold)`
tuples without collision.

---

## 8. Simulator plumbing — which function does what

```
oci_msa_analog_txrx.main()
   │
   ├─ generate_prbs(31, n_bits=500_000)                       → symbols
   ├─ make_electrical_channel(CHANNEL_MODEL)                  → elec_ir (both legs)
   ├─ make_smf_link(chunk_len).process_block(drive, "tp4")    → tp4 waveform
   ├─ percentile-normalise                                    → rx_base ∈ [~-1, ~+1]
   ├─ add_awgn_waveform(rx_base, NOISE_RMS_V, rng)           → rx
   ├─ CTLE (optional)                                         → rx
   │
   ├─ run_cdr_estimator_with_dfe(rx, INITIAL_PI, spec_dfe=…)  ← THIS IS THE CDR
   │      │
   │      ├─ constructs EstimatorMmCdr(kp, ki, freq_max, freq_leak,
   │      │                            freq_updn_threshold, n_phases,
   │      │                            initial_phase, w_pre, w_post,
   │      │                            drive_mode, polarity_mode)
   │      ├─ constructs ChannelEstimator(n_precursor=1, n_postcursor=1,
   │      │                              mu=mu_taps, adaptation="sign_error")
   │      └─ per-UI loop:
   │            y   = rx[round(data_pos)]
   │            if spec_dfe: (y_sel, d, _) = spec_dfe.step(y)   # DFE data decision
   │            else:        d = sign(y)                        # zero-crossing
   │            z = sign(y − d · h0_est)                        # error slicer
   │            h0_est += mu_h0 · d · z                          # SS-LMS on threshold
   │            estimator.step(y, d)                            # ĥ₋₁, ĥ₀, ĥ₁
   │            state, pi_code = cdr.step(ĥ₋₁, ĥ₀, ĥ₁, state)
   │            data_pos += OSR + (Δphase this step)
   │
   ├─ modal_lock(pi_hist, SETTLE_UI)                          → lock_pi
   ├─ compute_ber(d_hist, symbols, SETTLE_UI, search_range)   → n_err, n_bits, lag, pol, conf
   └─ make_figures(…)                                         → 4 HTML/PNG per sweep point
```

Two secondary scripts consume the CDR the same way but with different sweep
grids:

* `scripts/analog_rx/ber_vs_snr.py` — loops over `σ` at a fixed channel to
  produce BER-vs-SNR curves.  Milestone-9-invalidated results; re-run
  pending.
* `scripts/analog_rx/cdr_lock_vs_channel_loss.py` — sweeps electrical-channel
  IL@Nyquist and (optionally) runs the four physical reference channels as
  anchors.  Uses `run_cdr_estimator` (no DFE) so lock-point behaviour is
  isolated from any DFE dynamics.
* `scripts/analog_rx/diagnose_analog_run.py` — sweep over
  `(σ, ki, freq_max, freq_leak, updn_threshold)` tuples with a matplotlib
  rendering path (no kaleido dependency) and the two extra diagnostic PNGs
  (`_loop.png`, `_slip.png`) that the main script doesn't emit.  This is the
  workhorse for CDR investigations.

---

## 9. Characterised behaviour

All numbers are `cpo_interposer_3db`, 500 k PRBS-31 symbols, `SETTLE_UI = 500`,
`BER_MAX_COMPARE_UI = 400 000`, PEAKING_DB_LIST = `[0.0]` (CTLE bypass),
`ENABLE_SPEC_DFE = True`.  Local-median BER uses the `compute_block_ber`
diagnostic with a ±256 UI local re-alignment window per block.

### 9.1 Baseline (σ = 0)

`ki = 0, freq_max = 2.0` — every operating point clean.  `pi_code` sits at
`lock_pi ≈ 6` with the modulo-wrapping variance below `±1` code.
`freq_accum` ≈ 0 for the entire record.  `ĥ₀ ≈ 0.83`, `ĥ₁ ≈ +0.09`,
`ĥ₋₁ ≈ +0.09`, DFE `h₁_DAC ≈ -0.09` (opposite sign to `ĥ₁` — DFE cancels
the postcursor the estimator measures).  Q@lk = Q_max = 8.  Counted BER
= 0 / 400 k.

### 9.2 σ = 0.10, `ki = 0` (the Milestone-8 bug)

`lock_frac` reports 97 % locked, Q@lk ≈ Q_max, LMS taps converge — yet
counted BER = **33.2 %**.  Local-median BER = 0 %.  Δ-lag panel shows two
discrete step events at ~symbol 235 k and ~symbol 265 k, each aligned with a
`pi_code` excursion to the metastable `pi ≈ 30-31` region.  Diagnosis
(Milestone 9): proportional-only bang-bang has no frequency-tracking; the
phase accumulator does a Brownian random walk and slips by integer UIs
whenever it crosses ±½ UI.  `pi_code mod OSR` hides the slips.

### 9.3 σ = 0.10, `ki = 1 × 10⁻³` (the Milestone-9 fix)

Enabling the integrator arrests the drift.  Counted BER = **2.5 × 10⁻⁵**
(10 errors / 400 k bits), matching the Q@lk = 2.65 prediction to within
counting statistics.  Δ-lag is flat at zero across the whole record.
No slipped blocks.

### 9.4 σ = 0.10, `ki = 1 × 10⁻³, freq_max = 1 × 10⁻¹, updn_th = 128` (Milestone-9b best)

Strict improvement over 9.3 — 7 counted errors / 400 k bits, matching Q@lk =
2.65 exactly.  Cleaner than the direct integrator (10 errors) because the
up/down counter filters the shot-to-shot bang-bang noise before it reaches
`freq_accum`.  This is the current best working configuration at σ ≤ 0.10.

### 9.5 σ = 0.16 (the open failure mode)

Every `e_k`-only anti-windup scheme fails.  Summary of the Milestone-9b
sweep, all at `ki = 1 × 10⁻³`:

| Config | fixed-lag BER | local-median BER | slipped blocks | max ‖Δ lag‖ | lock_frac |
|---|---|---|---|---|---|
| `freq_max = 2.0`, no leak, no gate | 4.33e-1 | 4.77e-1 | 89 / 100 | 256 UI (pinned) | 40 % |
| `freq_max = 1e-1` | 4.32e-1 | 4.76e-1 | 89 / 100 | 254 UI | 39 % |
| `freq_max = 1e-2` | 4.33e-1 | 4.71e-1 | 89 / 100 | 250 UI | 59 % |
| `freq_max = 1e-3` (30 ppm) | 3.41e-1 | 3.29e-3 | 73 / 100 | 256 UI | 78 % |
| + `freq_leak = 1e-5` | 3.63e-1 | 6.94e-2 | 77 / 100 | 256 UI | 73 % |
| + `freq_leak = 1e-4` | 3.85e-1 | 4.59e-1 | 90 / 100 | 256 UI | 72 % |
| + `freq_leak = 1e-3` | 3.78e-1 | 4.61e-1 | 80 / 100 | 254 UI | 80 % |
| `ki = 1e-4`, `freq_max = 1e-3` | 4.70e-1 | 4.64e-1 | 95 / 100 | 253 UI | 77 % |
| `ki = 1e-5`, `freq_max = 1e-3` | 4.28e-1 | 4.68e-1 | 88 / 100 | 253 UI | 75 % |
| `updn_threshold = 32`, `freq_max = 1e-1` | 4.39e-1 | 4.76e-1 | 89 / 100 | 254 UI | 39 % |
| `updn_threshold = 128`, `freq_max = 1e-1` | 4.75e-1 | 4.76e-1 | 99 / 100 | 255 UI | 35 % |
| `updn_threshold = 512`, `freq_max = 1e-1` | 3.29e-1 | 2.39e-1 | 99 / 100 | 253 UI | 63 % |

Mechanism (`freq_hist` + `phase_unwrap_hist` make it visible):

1. At σ = 0.16 the proportional path alone can't hold the sample within ±½ UI
   for the full record; the loop briefly wanders.
2. During that excursion the sample lands on the falling flank of the cursor,
   which produces a *persistent one-sided* bias in `e_k`.
3. Because the integrator only inspects `e_k`, that bias walks `freq_accum`
   toward `+freq_max` (or `-freq_max`) and pins it there.
4. Once pinned, `phase_accum` grows linearly at `freq_max` codes/UI —
   `500 k × 2.0 = 1 M codes ≈ 31 000 UI of accumulated drift over the
   500 k-UI record.
5. All `e_k`-only anti-windup schemes are structurally incapable of arresting
   this: none of them can distinguish "persistent bias from a real ppm
   offset" from "persistent bias because we've wandered off lock".

The **structural fix** is a lock signal computed *off `e_k`* — from either
unwrapped phase drift (`phase_unwrap_hist`) or LMS-tap asymmetry
(`|ĥ₋₁ − ĥ₁|`) — that gates integrator updates.  See §10.

---

## 10. Open work — the Milestone-10 gated integrator

Design intent for the next revision of `EstimatorMmCdr.step`:

```python
if lock_ok:                                # from a new lock signal
    if updn_th <= 0:  f_inc = ki · e_k
    else:             (up/down-counter branch as today)
    freq_accum = (1 − freq_leak) · freq_accum + f_inc
else:
    freq_accum = 0                          # anti-windup on unlock
freq_accum = clip(freq_accum, ±freq_max)
phase_accum += kp · e_k + freq_accum        # phase path unchanged
```

Candidate lock signals (any one, or a majority vote):

1. **Unwrapped-phase drift rate.**  Compute
   `Δφ = phase_accum[n] − phase_accum[n − T_win]` and compare `|Δφ / T_win|`
   against a physical ppm budget.  A real frequency offset produces bounded
   drift equal to the ppm; runaway produces sustained large-magnitude drift.
2. **LMS-tap asymmetry.**  When the loop is on lock, `|ĥ₋₁| ≈ |ĥ₁|`
   (Mueller-Muller balance condition).  During runaway the sample point is
   on the flank and one of the taps grows much larger than the other.
   `|ĥ₋₁ − ĥ₁| > E_bal` is an off-lock indicator that reuses the same taps
   the discriminant already consumes.
3. **Majority-vote lock indicator on the unwrapped phase.**  Simpler filter
   than the drift-rate test but coarser.

Deliverables:

* `EstimatorMmCdr.lock_gate: bool` field (or a new `CdrLockDetector` subclass)
  and matching state.
* `run_cdr_estimator{,_with_dfe}` argument to enable / configure the gate.
* Diagnose script sweep at σ ∈ {0.10, 0.16, 0.22} to verify Q-limited BER at
  every point.
* Update dev log with a Milestone-10 entry; update arch-doc Ch. 11-4 / 11-6.

---

## 11. Mapping to `OCI_Gen2_PMA_Architecture.md`

The current CDR maps into the arch doc's Chapter 11 as follows.  Cells marked
"populated by this doc" are ready to lift into the arch doc as fixed-point
defaults; cells marked "Milestone 10 blocker" cannot be populated until the
gated integrator is in place.

| Arch-doc section | Consumer of | Populated by this doc | Milestone 10 blocker |
|---|---|---|---|
| Ch. 11-2 phase-detector truth table (`e_PD_raw = ĥ₋₁ − α ĥ₁`) | discriminant §3.1 | `α = w_post / w_pre = 1` (symmetric); dead-band `ε_PD = 0`; polarity source `sign(ĥ₀)` per §3.2 | — |
| Ch. 11-3 phase-path fixed-point (S1–S9) | proportional path §3.3 | `kp = KP_EST = 4.0` (float ref); `CDR_MODE = proportional` per §3.1; `n_phases = 32`; `initial_phase = INITIAL_PI = 0` | — |
| Ch. 11-4 frequency-path fixed-point (F1–F3) | integral path §3.3 | `ki = KI_EST = 1e-3` (working ref at σ ≤ 0.10); `F_max = 1e-1` (3000 ppm, working ref); `updn_th = 128` (F1 dead-zone); `freq_leak = 0` (leak provides no benefit) | The update-enable signal (§10) is the missing structural input; without it, the σ ≥ 0.16 numbers in `Ch. 14` can't be populated. |
| Ch. 11-4 anti-windup update rule | integrator §3.3 stage 1 | up/down-counter idiom with `threshold = 128` is a strict improvement at σ ≤ 0.10 | Combined with LOCK-gate for σ ≥ 0.16 tolerance. |
| Ch. 11-6 lock-detect truth table | §5 + §10 | The existing `CdrLockDetector` (rolling proportional / integral statistics) is a *soft* lock detector fit for status output; it is **not** adequate as an integrator gate. | The unwrapped-phase drift detector or the LMS-tap asymmetry detector — one of these is the RTL lock detector spec once Milestone 10 lands. |
| Ch. 12 acquisition order | §4 + acquisition sequence | LMS enable **before** CDR lock is the correct order; the sign-error LMS keeps updating while `LOCK = 0` (matches `LMS_GATE_UNLK = 0` default in the arch doc). | — |
| Ch. 14 link targets | end-to-end BER | σ ≤ 0.10 numbers with the working config (§9.4) are population-ready. | σ ≥ 0.16 rows explicit TBD until Milestone 10. |

**Fixed-point pass items (out of scope of this doc)** — once Milestone 10
lands:

* Bit-widths for `phase_accum` (wraps) and `freq_accum` (saturates), sized
  from `F_max` and the phase-precision requirement.
* Shift encoding for `kp`, `ki` (both are pure powers of 2 in the working
  reference set).
* `updn_th` counter width (`⌈log₂ threshold⌉ + sign` bit) — 128 fits in 8 bits
  plus sign.
* `w_pre`, `w_post` — either drop as parameters (fix at 1) or shift-encoded
  `{1, 2, 4}`.

---

## 12. Test coverage

* `tests/test_rx/test_mm_cdr.py`
  * `TestEstimatorMmCdrDiscriminant` — verifies `e_raw = w_post ĥ₁ − w_pre ĥ₋₁`
    at each polarity-mode setting.
  * `TestEstimatorMmCdrLock` — closed-loop convergence test against a known
    channel with ±cursor polarity and both drive modes.
* Manual regression: `scripts/analog_rx/diagnose_analog_run.py` sweep list —
  the Milestone-9b table in §9 above is reproducible by running the script
  as checked in.

---

## 13. Where the CDR is *not* (deliberate exclusions)

* **Not** in the analog frontend.  The CDR is entirely in the digital domain
  in the simulator; in silicon it is the digital half of the CDR loop with a
  phase interpolator closing back to the sampling clock.  The analog side
  (comparators, T/H, ±h₀ threshold DAC) is modelled functionally but its
  fixed-point spec lives in Ch. 7-8 of the arch doc, not here.
* **Not** the h₀ or h₁ SS-LMS tap adaptations — those are separate loops
  (§4.2, §4.3) and get their own fixed-point spec in Ch. 6 (AGC / offset)
  and Ch. 10 (LMS).
* **Not** the PLL.  The PLL provides the high-frequency clock; the CDR
  steers only the fine phase via `pi_code`.  See Ch. 9 of the arch doc.
* **Not** the eye-monitor scan slicer.  Optional diagnostic path, not in the
  CDR loop.

---

## 14. Change log for this document

| Date | Change |
|---|---|
| 2026-07-17 | Initial draft — freezes the CDR state at Milestone 9b. Covers `EstimatorMmCdr`, its two anti-windup extensions (`freq_leak`, `freq_updn_threshold`), the two new instrumentation signals (`freq_hist`, `phase_unwrap_hist`), and the σ ≥ 0.16 open failure mode. |
