# GEN2 106.25G NRZ link budget — time-domain simulation cross-check

Repo: `scripts/oci_msa_gen2/link_budget/` · outputs: `runs/oci_msa_gen2/link_budget/` · engine: exact per-pattern ISI ⊕ signal-dependent Gaussian (per-symbol σ_k), PRBS-15, no Monte-Carlo, no Gaussian-blind numbers.

## Verdict

- **Line-by-line (isolated) reproduction:** deltas >0.2 dB: {'isi_eq': 0.31, 'jitter': -0.49} when each impairment is measured the way the budget measures it (alone, against the floor). Additive required OMA -7.57 dBm vs doc -7.34 — the budget's own convention reproduces.
- **Stacking finding (headline):** the penalties do **not add**. With every impairment live simultaneously, RIN (σ ∝ I) at the ISI/jitter-elevated operating point amplifies every eye-closure penalty; the full stack has an asymptotic BER floor and the spec-bump chain **cannot reach 1e-12 at any launch power** with the threshold offset in place. At the delivered −6.0 dBm the exact stacked BER is 1.6e-10 (Q ≈ 6.29 vs 7.035). Closing 1e-12 at −6.0 dBm requires laser RIN ≤ -139.69 dB/Hz — the budget assumes −138, i.e. ~1.7 dB shy.
- **CDR lock-point finding:** the MM-TED locks -0.063 UI from the max-eye phase on this chain, costing +0.59 dB of required OMA — the budget's implicit sample-at-eye-center assumption is optimistic by that much unless the lock point is offset-corrected. Phase wobble itself is negligible (0.18 ps p-p, 6 % of TJ).
- **Bump provenance finding:** the measured EIC↔PIC kernel is -4.8 dB at Nyquist vs the budget's 25 fF pole at -0.7 dB; with two of them the chain loses 9.0 dB of Nyquist response vs the spec-bump assumption. The as-measured interface does not meet the ≤25 fF line the budget books.

## Phase 0 — calibration gates (12/12 PASS)

| Item | Sim | Budget assumption |
|---|---|---|
| TIA kernel | Butterworth-2, f₋₃dB 58.0 GHz, DC 1000 V/A | 58 GHz, 1 kΩ |
| NEB shape integral | 64.4 GHz | Bn = 1.5×f₋₃dB = 87 GHz adopted (conservative by ~0.65 dB, Methodology 2.6a) |
| Operating point | swing 2.62 Vpp direct → chain ER 4.48 dB | ER 4.5 dB |
| TX map | 0.35/0.45/0.60 UI ↔ 72/56/42 GHz Bessel-4 | 20–80 % transition corners |
| MRM ring EO | 95 GHz small-signal; large-signal shows +0.8 dB peaking at Nyquist | 40–80 GHz assumed (Low confidence) |
| Chain FR at Nyquist | spec-bump -4.97 dB vs analytic -6.33 dB (attributed: MRM large-signal + Bessel-4 vs 2-pole) | — |

## Phase 1 — receiver floor (PASS, worst |Δ| = 0.001 dB)

| i_n (µA) | floor sim (dBm) | analytic 2Q·i_n/R | Δ |
|---|---|---|---|
| 3.0 | -13.171 | -13.171 | -0.000 |
| 4.0 | -11.922 | -11.922 | -0.000 |
| 4.5 | -11.409 | -11.410 | +0.001 |
| 5.0 | -10.952 | -10.952 | +0.001 |
| 6.5 | -9.813 | -9.813 | -0.000 |

Floor is flat across TIA f₋₃dB ∈ {50, 58, 60} GHz as the formula predicts.

## Phase 2 — waterfall: sim vs doc

| Line | doc | sim isolated (pole) | Δ | sim cumulative-marginal (pole) | sim isolated (measured bumps) |
|---|---|---|---|---|---|
| ER/shot + RIN | 1.16 | 1.16 | -0.00 | 1.16 | 1.18 |
| MPI (booked) | 0.21 | 0.20 | -0.01 | 0.20 | 0.20 |
| ISI + EQ | 1.15 | 1.46 | +0.31 | 3.07 | 5.24 |
| CD (500 m) | 0.04 | 0.03 | -0.01 | 0.11 | 0.05 |
| Jitter | 0.95 | 0.46 | -0.49 | 1.35 | 0.30 |
| Crosstalk (booked) | 0.36 | 0.36 | +0.00 | 0.36 | 0.36 |
| Threshold offset | 0.21 | 0.16 | -0.05 | n/a | 0.16 |
| **Stack** | **4.07** | **3.84** | -0.23 | — | 7.48 |

Additive required OMA (floor + isolated stack): **-7.57 dBm** (doc -7.34). The cumulative exact engine finds **no OMA that reaches 1e-12** with the full stack live (asymptotic signal-dependent-noise floor) — the n/a cells above are that floor, not missing data.

## Phase 3 — closure and realism checks

- **pole**: cumulative margin at Rx OMA −6.0 dBm = n/a dB (doc +1.34); exact stacked BER at the operating point 1.56e-10 (Q≈6.29); max RIN for 1e-12: -139.69 dB/Hz (assumed −138); CTLE z=37/p=80^2
- **measured**: cumulative margin at Rx OMA −6.0 dBm = n/a dB (doc +1.34); exact stacked BER at the operating point 4.40e-04 (Q≈3.33); does not reach 1e-12 even at RIN −165 dB/Hz; CTLE z=20/p=95^2
- **CDR** (live digital MM CDR, frozen EQ): lock -0.0626 UI from the static best phase; settled wobble 0.18 ps p-p (6 % of the 3.30 ps TJ budget); counted errors 0/20661; the lock point costs +0.590 dB of required OMA vs the max-eye phase (see verdict).
- **TDEC** of the simulated TX eye (requirement ≤ 1.8 dB): measured TX bump: 4.33 dB; no TX bump (clean driver): 1.60 dB.

## Phase 3b — corner matrix (doc §5)

Additive-stack margins (doc's convention, exact-engine isolated lines), sim (doc) in dB at Rx OMA −6.0 dBm:

| Tx case | A@3µA/50G | A@4µA/50G | B@4µA/60G | B@5µA/60G |
|---|---|---|---|---|
| FIR3 typ 0.45UI | +2.92 (+2.81) | +1.74 (+1.63) | +2.15 (+1.98) | +1.24 (+1.06) |
| FIR3 slow 0.60UI | +1.96 (+2.22) | +0.79 (+1.04) | +1.10 (+1.40) | +0.18 (+0.48) |
| noFIR 60G + MRM 80 | +3.04 (+2.80) | +1.87 (+1.62) | +2.23 (+1.83) | +1.32 (+0.92) |
| noFIR 60G + MRM 60 | +2.43 (+2.50) | +1.25 (+1.32) | +1.51 (+1.63) | +0.60 (+0.72) |
| noFIR 60G + MRM 50 | +1.91 (+2.25) | +0.73 (+1.07) | +1.15 (+1.42) | +0.23 (+0.50) |
| noFIR 60G + MRM 40 | +1.21 (+1.95) | +0.03 (+0.77) | +0.55 (+1.07) | -0.37 (+0.16) |

Exact **stacked** BER at the −6.0 dBm operating point (full noise + jitter + threshold offset; target 1e-12) — the non-additive companion metric:

| Tx case | A@3µA/50G | A@4µA/50G | B@4µA/60G | B@5µA/60G |
|---|---|---|---|---|
| FIR3 typ 0.45UI | 3.9e-11 | 1.7e-10 | 1.3e-10 | 5.0e-10 |
| FIR3 slow 0.60UI | 6.4e-08 | 1.6e-07 | 1.9e-08 | 6.3e-08 |
| noFIR 60G + MRM 80 | 1.8e-11 | 9.7e-11 | 4.4e-11 | 2.1e-10 |
| noFIR 60G + MRM 60 | 3.0e-09 | 1.0e-08 | 1.5e-09 | 6.5e-09 |
| noFIR 60G + MRM 50 | 3.0e-08 | 9.9e-08 | 3.6e-08 | 1.1e-07 |
| noFIR 60G + MRM 40 | 1.2e-06 | 2.7e-06 | 8.1e-07 | 2.1e-06 |

FIR3 check on the 60 GHz-driver channel: FIR buys +0.00 dB of ISI (doc: 0) and the slice-DCD DJ delta costs +0.21 dB (doc: 0.27).

## Known limits

- MPI and crosstalk are **booked analytically** (`common.mpi_penalty`, eye-closure allocation) — the incoherent power-domain fiber model cannot represent interferometric MPI. Same status as the doc.
- 1e-12 via exact ISI ⊕ Gaussian tails (per-symbol σ), the doc's own assumption; no Monte-Carlo counting anywhere.
- The measured bump kernel stands in for the ≤25 fF spec bump; its provenance and the gap to the spec assumption are flagged above.
- Figures: `phase0_chain_fr`, `phase1_floor`, `phase2_waterfall`, `tornado` (.html/.png in the runs directory).
