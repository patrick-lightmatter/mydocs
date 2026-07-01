# Charge-Steering RX — handoff & resume guide

**For the human or agent picking this up later.** This is the short, pragmatic file: where the code lives, what works, what's parked, what to try first if you resume. The rigorous narrative is in [`report.md`](report.md) next to this file.

---

## 1. Status: parked

The work was paused on **Mon Jun 22 2026** with the conclusion that the architecture *as disclosed* (2-UI aperture) cannot close BER = 1e-12 at 106 Gbaud in realistic silicon, but **the architecture with a 3-UI aperture is genuinely competitive** (2.5× more AWGN budget, 6.6 dB less swing penalty, 1.83 mV of headroom over kT/C).

The simulation framework is complete, tested (16/16 tests passing), and rate-agnostic. Nothing is broken or half-finished — work is parked at a clean stopping point.

The two-line verdict for the next person:

1. The geometric ISI tail from the shared analog rail is real, has a clean closed-form per-hop ratio, and is the architecture's central failure mode.
2. The disclosure picked the wrong aperture (2 UI). The optimum is 3 UI, and at 3 UI the architecture is buildable. **This is the single most useful finding.**

If you want to publish the negative result, [`report.md`](report.md) is the publication-ready draft. If you want to push the architecture further, see §6 below for the prioritised next-experiments list.

---

## 2. Read in this order

1. **This file (HANDOFF.md)** — 5 min, what's where and what to do next.
2. **[`report.md`](report.md) TL;DR + §10** — 10 min, the verdict and what was learned.
3. **`temp/current_rx/Invention Disclosure_ TIA-less Charge-Steering Receiver .pdf`** — the original disclosure, if you need the design intent direct from the source.
4. **`src/optical_serdes/rx/charge_steering_frontend.py`** — the per-step KCL engine; everything else is built on it. Read the module docstring (top ~50 lines) first.
5. **`tests/test_rx/test_charge_steering.py`** — 8 tests that pin the invariants ($h_{-1}=0$, $\Sigma G$ flat, fast path ≡ engine, rate-agnostic). Read these to understand what's *contractually* guaranteed.
6. **[`report.md`](report.md) §3 KCL + §5 geometric tail + §6.4 aperture sweep** — the three sections with the actual physics.

If you only have time for one section of `report.md`, read §6.4 (the aperture finding).

---

## 3. Source-tree map

All charge-steering files were **created in this work** and live in the `optical-serdes` repo.  They are **currently untracked in git** (branch `construction`):

| File | LoC | What it is |
|---|---|---|
| `src/optical_serdes/rx/charge_steering_frontend.py` | 479 | The KCL/Forward-Euler analog state engine.  `ChargeSteeringConfig` (params), `ChargeSteeringFrontEnd` (engine), `ChargeSteeringResult` (flight recorder), `CsResponse` (extracted IR), `extract_response()` (probe-with-unit-bit), `fast_samples()` (1-D convolution path). |
| `src/optical_serdes/rx/charge_steering_rx.py` | 372 | End-to-end receiver wrapper.  `ChargeSteeringReceiver` orchestrates Mode A (TX FFE) and Mode B (speculative DFE), handles signal normalisation, AWGN injection at the sample node, and BER counting against a reference bit stream. |
| `src/optical_serdes/tx/charge_steering_cooptim.py` | 125 | TX co-design for Mode A.  `design_tx_ffe_null_postcursors()` (recursive zero-forcing), `effective_channel()` (verify g=c⊗h), `build_tx_ffe()` (L1-normalised TX FIR). |
| `tests/test_rx/test_charge_steering.py` | 107 | 8 tests on the analog engine.  Invariants only. |
| `tests/test_rx/test_charge_steering_rx.py` | 207 | 8 tests on the full receiver (Modes A and B, normalisation, etc). |

The `examples/` directory is `.gitignore`d — these scripts are local-only and won't be committed:

| File | LoC | Generates |
|---|---|---|
| `examples/charge_steering_physics_evidence.py` | 472 | The 3 physics-validation figures (clock physics, current capture, one-arm zoom) for §4. |
| `examples/charge_steering_rx_modes_nrz_106g25.py` | 540 | Per-mode end-to-end figures (Mode A at K=2/3/6, Mode B, linear/optical chains) for §7–§8. |
| `examples/charge_steering_rx_nrz_106g25.py` | 308 | Earlier analog-front-end-only example.  Largely superseded by `charge_steering_rx_modes_nrz_106g25.py`. |
| `examples/charge_steering_awgn_sweep.py` | 337 | The BER-vs-σ AWGN sensitivity sweep for §9, run at 10 fF and 100 fF. |
| `examples/charge_steering_aperture_sweep.py` | 277 | **The aperture-vs-budget sweep that produced the §6.4 finding.** This is the highest-value example. |

Run outputs land in `runs/charge_steering_*/`.  The figures copied into [`figures/`](figures/) next to this file are the curated subset used in `report.md`.

---

## 4. What works (validated)

`uv run pytest tests/test_rx/test_charge_steering.py tests/test_rx/test_charge_steering_rx.py -q` → **16 passed**, ~5 s.

Key invariants pinned by tests:

| Test | Invariant |
|---|---|
| `test_ideal_clock_has_zero_precursor` | $h_{-1}=0$ to ≤ 1e-12 for ideal clocks |
| `test_sinusoidal_clock_small_precursor` | $h_{-1}$ negligible for sinusoidal clocks |
| `test_overlap_conductance_sum_constant` | $\Sigma G(t)$ constant to FP precision |
| `test_fast_path_matches_engine` | `fast_samples` (np.convolve) ≡ full engine, to ≤ 1e-9 |
| `test_postcursor_grows_with_capacitance` | $h_1/h_0$ monotonic in $C_\text{int}$ |
| `test_reset_removes_long_tail` | cap reset prevents long-period drift ISI |
| `test_rate_agnostic[106.25e9, 53.125e9]` | engine works at any baud rate |
| `test_mode_b_ber_zero_ideal_clock_linear` | Mode B → BER = 0 on linear chain |
| `test_mode_a_two_tap_matches_disclosure_closed_form` | Mode A 2-tap === disclosure's `c1 = -c0 h1/h0` |
| `test_mode_a_nulls_n_minus_1_postcursors` | $K$-tap Mode A nulls $g_1, \dots, g_{K-1}$ |
| `test_mode_a_end_to_end_zero_ber` | Mode A → BER = 0 on linear chain |
| `test_normalisation_matches_analytical_for_known_levels` | sample normalisation correct |

Anything that touches these invariants and breaks a test should be reverted, not patched.

---

## 5. Operating point cheatsheet

Default `ChargeSteeringConfig()` values, and the rest of the moving pieces:

| Parameter | Default | Where it lives | Comment |
|---|---|---|---|
| `baud_rate` | 106.25e9 | `ChargeSteeringConfig` | Engine is rate-agnostic — only `dt` enters. |
| `sps` | 32 | `ChargeSteeringConfig` | $dt = 1/(\text{baud}\cdot\text{sps}) = 294$ fs. |
| `n_arms` | 8 | `ChargeSteeringConfig` | 1/8-rate macro. |
| `aperture_ui` | **2.0** | `ChargeSteeringConfig` | **THE DISCLOSURE'S CHOICE BUT NOT OPTIMUM.** Optimum is 3.0–3.25 UI (§6.4). |
| `arm_stride_ui` | 1.0 | `ChargeSteeringConfig` | One sample per UI. |
| `c_int_f` | 10e-15 | `ChargeSteeringConfig` | $\tau_\text{on}=R_\text{on}C_\text{int}=2$ ps. |
| `r_on_ohm` | 200.0 | `ChargeSteeringConfig` | Switch on-resistance. |
| `r_off_ohm` | 1e9 | `ChargeSteeringConfig` | Switch off-resistance (1 GΩ ⇒ negligible off-leakage). |
| `clock` | `'sinusoidal'` | `ChargeSteeringConfig` | Real bandlimited clock; `'ideal'` for the rect-aperture invariant tests. |
| `reset_after_sample` | `True` | `ChargeSteeringConfig` | **Don't disable** unless you want to see the off-leakage failure mode. |
| `I_low`/`I_high` | 5 µA / 100 µA | example scripts | 95 µA photocurrent swing. |
| AWGN injection point | sample node | `ChargeSteeringReceiver.sample_noise_rms_v` | Inject AWGN after the front-end, before slicing. |

**Key numbers worth knowing without re-running:**

| Metric | 2 UI (disclosure) | **3 UI (optimum)** | 100 fF / 2 UI |
|---|---|---|---|
| $h_0$ | 390.8 V/A | **472.9** | 47.0 |
| $h_1/h_0$ | 0.914 | **0.289** | 0.945 |
| Optimal K | 6 | **2** | 6 |
| L1 swing penalty | 9.46 dB | **2.20 dB** | 13.6 dB |
| Full eye | 12.49 mV | **34.86 mV** | 0.93 mV |
| Linear σ@1e-12 | 0.887 mV | **2.478 mV** | 0.066 mV |
| Headroom over kT/C | +244 µV | **+1834 µV** | **−138 µV (unviable)** |

kT/C noise: 643 µV at 10 fF, 204 µV at 100 fF, 910 µV at 5 fF.

---

## 6. What to try next, in priority order

The aperture-sweep script can answer most of these in 5–60 s of compute.

### Priority 1 — verify the 3-UI sweet spot end-to-end at full BER

The §6.4 analysis is linear (`extract_response` + analytical Q-factor).  An end-to-end Mode A BER sweep at aperture = 3 UI with $K\in\{2, 4, 8\}$ across $\sigma_\text{slicer}\in[0, 3 \text{ mV}]$ would land the headline result with hard counted BER.  Run:

```bash
# pseudo-code: extend charge_steering_awgn_sweep.py to accept --aperture-ui
python examples/charge_steering_awgn_sweep.py --aperture-ui 3.0 --n-tx-taps-list 2,4,8
```

The current `charge_steering_awgn_sweep.py` doesn't expose `--aperture-ui` — adding a 3-line flag in `argparse` and passing it through to `ChargeSteeringConfig` is the change.  Then publish a new §9.4 figure side-by-side with the existing §9.1 figure.  **This is the single highest-value follow-up.**

### Priority 2 — the rail-cap pole

The current model treats $C_\text{rail}=0$ (quasi-static rail).  In silicon $C_\text{rail}$ from bond pad + photodiode + 8 switch parasitic caps is realistically 20–50 fF.  Adding the rail pole into the KCL is a one-line change in `ChargeSteeringFrontEnd.integrate`:

```python
# replace v_shared with a low-pass-filtered version
v_shared_filt += (dt / (R_eff * C_rail)) * (v_shared_raw - v_shared_filt)
# then drive v_int from v_shared_filt instead of v_shared
```

Expected impact: introduces a small non-zero $h_{-1}$, rounds the signal edges, and quantifies whether the bond-pad parasitic eats the 3-UI margin.  This is the most important *fidelity* upgrade to the model.

### Priority 3 — `R_on` sweep at the 3-UI operating point

The §10.3 hypothesis says $\mathrm{SNR}\propto 1/R_\text{on}$.  Adding `--r-on-ohm 50,100,200,400` to `charge_steering_aperture_sweep.py` (already supported via the `--r-on-ohm` flag, but needs to be a loop instead of a scalar) would confirm or refute that scaling.  Combined with the rail-cap fidelity upgrade in Priority 2, this gives the actual practical "smallest-switch-that-works" answer.

### Priority 4 — Mode B (speculative DFE) at 3 UI

§7–§9 of the report focus on Mode A (TX FFE) at 2 UI.  At 3 UI with $h_1/h_0=0.29$, Mode B's 1-tap speculative slicer should be *easier* than at 2 UI (smaller threshold spread).  Rerun `charge_steering_rx_modes_nrz_106g25.py --mode spec_dfe --chain linear` with `aperture_ui=3.0` and compare BER and slicer-offset sensitivity to Mode A.

### Priority 5 — the "small TIA-like buffer" hybrid

§10.3 lists this as the leading way to break the rail.  Worth modelling: a unity-gain Gm/Cs stage between $I_\text{pd}$ and the switch matrix, with finite GBW and finite noise.  Probably 100–200 lines of new code in a `BufferedChargeSteeringFrontEnd` class that wraps the existing engine.  This would let you quantify whether the buffer is worth its power.

### Priority 6 — Mode A on a *real* optical chain (MRM nonlinearity)

The current `charge_steering_rx_modes_nrz_106g25.py --chain optical` shows Mode A fails on the MRM because the modulator nonlinearity invalidates the TX FFE's linearity assumption.  Adding a `TxPredistortionLut` upstream of the TX FFE (already exists in the toolbox) and quantifying the residual closure penalty would fix this and validate the architecture against a more realistic photocurrent waveform.

---

## 7. Things that surprised us

These are worth knowing because they were not obvious at the start:

1. **The 2-tap model is wrong by 10× in tap count.**  Shared-rail coupling creates a geometric tail of 10–30 post-cursors with ratio ≈ $1/N_\text{active}$.  The disclosure's "$V_n = h_0 D_n + h_1 D_{n-1}$" framing under-states the equaliser depth by 4×.  See §5 of report.
2. **The cap is a tracker, not an integrator.**  $\tau_\text{on}=2$ ps ≪ $T_\text{UI}=9.4$ ps, so the cap settles in ~5 time-constants per UI.  This is why wider apertures *suppress* the geometric tail rather than amplifying it — they give the cap more flat-on tracking time.  Counter-intuitive but the central physical insight (§6.4.2).
3. **The 2-UI aperture is the *worst* on the curve.**  3 UI gives 2.5× the AWGN budget.  This is a non-obvious "free" architectural improvement.
4. **L1 normalisation of the TX FFE is mandatory.**  Without it, the pre-emphasised symbol stream violates the $[I_\text{low}, I_\text{high}]$ envelope and the simulation gives unrealistically large eye amplitudes.  See §7.2.
5. **Going from 10 fF to 100 fF is *worse* for SNR**, not better.  Signal shrinks faster ($1/C_\text{int}$) than kT/C improves ($1/\sqrt{C_\text{int}}$) in the slow-charging regime.  See §6.
6. **A sampling tree (1:4 → 1:4 → 16 caps) does not help.**  Passive charge-transfer between stages costs ≥6 dB; active buffering reintroduces an active stage and abandons the "TIA-less" claim.  Discussed in chat but not in the report.
7. **MRM nonlinearity breaks Mode A but not Mode B.**  Mode A's TX FFE design assumes a linear channel; the MRM's Lorentzian-shaped transfer function violates that.  Mode B adapts to whatever sample distribution it sees and is robust.

---

## 8. Known limitations / gotchas

- The `ChargeSteeringConfig` does have a `c_rail_f` field (default 10 fF) but the engine **does not currently use it**.  The rail is modelled as quasi-static.  See Priority 2 above.
- `examples/` is gitignored.  If you want to share the examples with another agent, either include them in the handoff manually or change `.gitignore`.
- The `R_off = 1 GΩ` default makes off-state leakage negligible.  If you want to model a real silicon switch's off-resistance (~10 MΩ), the `reset_after_sample=True` mechanism handles that fine, but disabling reset will *not* — the engine assumes the cap was discharged or `R_off` is high enough that off-leakage didn't matter.
- The `extract_response` truncates the tail at `rel_tol=1e-12` and `max_post=40` by default.  At very large $C_\text{int}$ or very wide apertures the tail can exceed `max_post` and silently truncate.  Increase `max_post` if `len(taps)-cursor` saturates at the default.
- The `ChargeSteeringReceiver`'s BER counter does cross-correlation alignment internally; it can produce a *transient* error at the very last UI if the engine fails to sample it.  This is handled in `receive()` by trimming trailing NaNs but is worth knowing if you write a new ber-counting wrapper.

---

## 9. Reproduce the headline figures

All commands assume `cd /home/patrick/optical-serdes` and `uv run python …`.

```bash
# §4–§5 physics-evidence figures (clock physics, current capture, one-arm zoom)
uv run python examples/charge_steering_physics_evidence.py
uv run python examples/charge_steering_physics_evidence.py --clock ideal

# §7 Mode A end-to-end (K=2 and K=6) on linear chain
uv run python examples/charge_steering_rx_modes_nrz_106g25.py --mode tx_ffe --chain linear --n-tx-taps 2
uv run python examples/charge_steering_rx_modes_nrz_106g25.py --mode tx_ffe --chain linear --n-tx-taps 6

# §8 Mode B speculative DFE on linear chain
uv run python examples/charge_steering_rx_modes_nrz_106g25.py --mode spec_dfe --chain linear

# §9 AWGN sensitivity sweep (10 fF and 100 fF)
uv run python examples/charge_steering_awgn_sweep.py --c-int-f 10e-15
uv run python examples/charge_steering_awgn_sweep.py --c-int-f 100e-15

# §6.4 aperture sweep — the most important figure
uv run python examples/charge_steering_aperture_sweep.py
```

Outputs land in `runs/charge_steering_*/`.  Curated figures are also in [`figures/`](figures/) next to this file.

---

## 10. If you have time for exactly one thing

Add `--aperture-ui` to `examples/charge_steering_awgn_sweep.py` and run it at aperture = 3.0 UI with $K\in\{2, 4, 8\}$.  That single figure — counted BER vs $\sigma$ at the *correct* aperture — is the missing piece that turns the linear analysis in §6.4 into a hard end-to-end result.  Everything else is incremental.

---

## 11. Files outside this nugget that matter

- `optical-serdes/temp/current_rx/Invention Disclosure_ TIA-less Charge-Steering Receiver .pdf` — the original disclosure.
- `optical-serdes/temp/current_rx/context_message.md` — system specifications (106.25 Gb/s, 8-phase, target $h_{-1}=0$, etc).
- `optical-serdes/temp/current_rx/Gemini_Generated_Image_*.png` — three architecture / timing reference figures (copied into [`figures/`](figures/) as `disclosure_*.png`).
- `optical-serdes/CLAUDE.md` — project-level conventions.  Mentions skills like `/rx-optimise`, `/channel-characterise`, etc. — relevant if you want to apply the same RX-tuning playbook the rest of the toolbox uses.

---

*Last updated: 2026-06-22.*  *Original chat:* [`f8cefc88-5b1b-4c74-8b42-0b04b6234a8f`](../../../.cursor/projects/home-patrick-optical-serdes/agent-transcripts/f8cefc88-5b1b-4c74-8b42-0b04b6234a8f).
