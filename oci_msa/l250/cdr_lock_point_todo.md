# L250 — CDR lock-point steering (todo)

Working punch-list for adding **programmable lock-point bias** to the digital MM CDR (`DigitalMmCdr`). The classical MM null is `h(−1) = h(+1)`; we want the ability to steer the sampling phase off that null to improve the effective discrete-time channel seen by downstream equalization.

Status values: **Open** · **In progress** · **Done**

Related: `architecture_spec.md` §5-3 (currently states lock at `h(−1) = h(+1)` only); float MM CDR reference in `mm_cdr.py` (`ted_pre_weight` / `ted_post_weight`).

---

## 1. Implement asymmetric early / late vote weights in `DigitalMmCdr` (option 3)

**Status:** Open

**Approach:** In the ternary vote path, weight **early** votes (`+1`) and **late** votes (`−1`) differently *before* the voter accumulates them — not a scalar on the whole window sum (which is inert at lock), and not the removed PAM4 X/Y-path split.

**Model / RTL parameters (proposed):**

| Parameter | Placeholder | Meaning |
|---|---|---|
| Early vote weight | `w_early` | Multiplier on `+1` (early) votes in `CdrVoter` |
| Late vote weight | `w_late` | Multiplier on `−1` (late) votes in `CdrVoter` |

Default: `w_early = w_late = 1` ⇒ current behavior (`h(−1) = h(+1)` at lock).

**Lock-point relation (NRZ, symmetric transitions):** at equilibrium the weighted voter expects

\[
w_{\text{early}} \cdot P(\text{early}) = w_{\text{late}} \cdot P(\text{late})
\]

which biases the sampling instant so that the equalized pulse cursors need not satisfy `h(−1) = h(+1)`. With symmetric crossing statistics, target ratio \(h(−1)/h(+1) \approx w_{\text{late}}/w_{\text{early}}\) (verify in simulation).

**Code touchpoints:**

- `src/optical_serdes/rx/mm_cdr_digital.py` — add `w_early`, `w_late` to `DigitalMmCdr` and `CdrVoter`; apply in `CdrVoter.step(vote)` (e.g. `acc += w_early` if vote == +1, `acc -= w_late` if vote == −1).
- Widen `N_diff` accumulator formula if weights > 1: `⌈log2(cdr_width · max(w_early, w_late))⌉ + 2`.

**Acceptance:**

- Defaults reproduce bit-identical behavior to today (`w_early = w_late = 1`).
- With `w_early ≠ w_late`, simulated lock phase shifts measurably vs. equal weights on a known pulse (e.g. fixed `h(−1)`, `h(+1)` channel).

---

## 2. Unit tests for weighted voter and lock-point bias

**Status:** Open

**Where:** `tests/test_rx/test_mm_cdr_digital.py`

**Cases:**

- Voter accumulator: known vote stream with `w_early=2`, `w_late=1` ⇒ expected signed sum.
- `w_early = w_late = 1` regression: existing ternary-vote / voter tests unchanged.
- Optional: synthetic discriminant — injected early/late imbalance drives `diff` sign as expected.

---

## 3. Simulation: validate lock-point shift vs. cursor ratio

**Status:** Open

**Goal:** Quantify where the CDR locks as a function of `w_early` / `w_late` on a controlled channel (pulse with known `h(−1)`, `h(+1)`), and compare to the float MM CDR `w_pre` / `w_post` steering in `mm_cdr.py` for the same channel.

**Deliverable:** short plot or table (can live under `runs/` or `mydocs/oci_msa/l250/`) showing phase offset vs. weight ratio; note any gap between ternary-weight and float-discriminant models.

---

## 4. Update `architecture_spec.md` §5 (parameter table, voter snippet, lock-point text)

**Status:** Open

**Edits:**

- §5-2: add `w_early`, `w_late` rows; update `N_diff` width formula.
- §5-3: replace “Lock occurs at `h(−1) = h(+1)`” with default-null + programmable bias via `w_late/w_early`; keep truth table (votes unchanged, weighting is post-vote in voter).
- §5-4: update `CdrVoter` snippet to show weighted accumulation.
- Cross-check §5-7 loop update (`diff` definition) and any `--ted-pre` / `--ted-post` narrative elsewhere in the repo docs.

---

## 5. (Optional) Static PI skew and target-`diff` bias — document or defer

**Status:** Open

**Context:** Alternatives not chosen for first implementation:

- **Static PI skew** — fixed offset on `pi_code` / `init_pi`; open-loop phase nudge, no change to loop equilibrium.
- **Target-`diff` bias** — subtract constant from each window’s `diff`; servo to nonzero early/late balance.

Decide whether these remain out of scope for silicon or get a one-line “future hook” note in the spec after item 1 lands.

---

## 6. (Optional) Multi-bit soft vote — float `w_pre`/`w_post` in the digital path

**Status:** Open

**Context:** Option 4 from architecture review: compute `w_pre·(pre term) − w_post·(post term)` then quantize, matching `MuellerMullerCDR` more closely than ternary early/late weights. Only pursue if item 1’s ternary weights cannot match required lock-point resolution or if RTL wants explicit pre/post multipliers rather than early/late semantics.

---

<!-- Add completed items with date and one-line outcome when closed. -->
