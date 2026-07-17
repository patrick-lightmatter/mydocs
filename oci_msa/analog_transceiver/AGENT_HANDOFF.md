# Agent Handoff — OCI-Gen2 PMA Architecture Fixed-Point Reshape

> **You are the receiving agent.** This file gives you everything you need to
> continue reshaping [`OCI_Gen2_PMA_Architecture.md`](./OCI_Gen2_PMA_Architecture.md)
> from **rev 0.5** toward a version that carries a complete **fixed-point
> specification skeleton** for every algorithm loop.
>
> **Hard rule:** do **not** import any numeric value from the `optical-serdes`
> simulation into the architecture document. Every numeric cell stays as a
> structured `TBD_*` tag (see §5). Your job is *structural* — build the tables
> the analog and RTL teams will fill later.

---

## 1. Task

Edit `OCI_Gen2_PMA_Architecture.md` **in place** so that every algorithm
chapter carries a **standardised four-part fixed-point specification**
subsection (template in §4). Algorithm chapters, in priority order:

| # | Ch. | Loop | Datapath complexity |
|---|-----|------|---------------------|
| 1 | 10 | LMS channel estimator | Canonical exemplar (mult, shift, wide accum, trim) |
| 2 | 11 | MM-CDR | Phase path + frequency path + lock detect — three sub-datapaths |
| 3 | 5 | CTLE adaptation | Cost accumulator, direction FSM |
| 4 | 6 | AGC | Compare + hysteresis + up/down accumulator |
| 5 | 7 | Offset cancel | Ones counter + margin compare |
| 6 | 8 | Error path (`e(n)`) | Amplitude compare → ternary |
| 7 | 9 | PLL / PI | PI code interface only (heavy analog side) |
| 8 | 3 | Driver FFE | Control-side codes only (analog signal path) |

Do **NOT:**

- Replace `TBD` cells with concrete numbers pulled from `optical-serdes/`.
- Add new algorithm chapters or reorder existing ones.
- Edit Mermaid diagrams unless you find a genuine contradiction (call it out
  in Ch. 15 rather than silently fixing).
- Invent DAC widths, clock frequencies, or process-specific LSB sizes.

---

## 2. Reading list

| # | Path | Why |
|---|------|-----|
| 1 | `OCI_Gen2_PMA_Architecture.md` | The document you are editing (rev 0.5). |
| 2 | `OCI_Gen2_RX_TX_PMA_Architecture_Outline.md` | Canonical outline the doc must stay aligned to. |
| 3 | `OCI-Gen2.png` | Original sketch. Reference the file path in Ch. 1 / Appendix A only. |
| 4 | `diagrams/analog_nrz_rx_106g25.md` | Detailed block diagram + signal definitions. Use only for **signal names and equations**, not numerical values. |

**Do NOT read** any file under `/home/patrick/optical-serdes/` for the purpose of
filling this document. If you find yourself pulling numbers from it, stop.

---

## 3. Guiding principle

The architecture doc is a **contract** between:

- the algorithm designer (who fixes the datapath shape),
- the analog designer (who fixes the DAC/comparator sizing), and
- the RTL / synthesis engineer (who fixes bit widths, pipelining, and
  overflow/rounding policy).

Your reshape freezes the **datapath shape** (columns 1–5 of each table below)
and reserves clearly-labelled slots for the analog and RTL sizing decisions
(columns 6+ or explicit `TBD_*` tokens). No numeric value from a Matlab or
Python model belongs here — that belongs in the correlation report.

---

## 4. Fixed-point template

Every algorithm chapter §X gets a **§X-Y Fixed-point specification** section
(rename the existing "Range, resolution, ..." section) with four sub-headers,
in this exact order:

### §X-Y Fixed-point specification

#### Datapath signals

Every named net that appears in the chapter's block diagram, truth table, or
prose. External inputs, state registers, combinational intermediates, outputs,
and programmable parameters — all live here.

Column shape:

```
| Signal | Role | Width | Format | Range | Consumer / notes |
```

- **Role**: `in` / `state` / `intermediate` / `out` / `param`.
- **Width**: `TBD_rtl_floorplan` or `TBD_analog_design` (never a number).
- **Format**: `signed sN.F` / `unsigned uN.F` / `shift-N` (shift-encoded
  gain, i.e. `x ≫ k` where `k` is a `⌈log₂ K⌉`-bit code) /
  `1b` / `2b ternary {-1,0,+1}` / `k-hot` (thermometer) / etc.
- **Range**: symbolic when width is TBD (`[-1,+1]` for normalised taps;
  `[0, 2^N-1]` for unsigned codes; `TBD` otherwise).
- **Consumer / notes**: which downstream stage or table uses this signal;
  cross-references into other chapters welcome.

#### Arithmetic stages

Every arithmetic operation from the datapath diagram or truth table, in
signal-flow order. If the loop has more than one path (e.g. Ch. 11's phase +
frequency + lock-detect paths), give one table per path with a mini header.

Column shape:

```
| # | Stage | Operation | Input widths | Output width | Overflow | Rounding |
```

- **Stage**: `S1`, `S2`, ... matching the datapath signal names.
- **Operation**: `mult`, `add`, `subtract`, `abs`, `shift-right N` (shift by
  a parameter), `compare-±ε`, `LUT`, `counter++`, `mux`, `saturate to N-bit`,
  `trim (round-half-up to N-bit)`, `dead-band clip`, `sign()`.
- **Input widths**: symbolic (`Wa × Wb` for a multiply). Reference §X-Y
  Datapath signals by name when unambiguous.
- **Output width**: e.g. `Wa+Wb` (full product), `max(Wa,Wb)+1` (add),
  `Wa` (shift), `2b` (ternary), `1b` (compare), or the trim target.
- **Overflow**: `wrap`, `saturate`, `—` (impossible / not applicable).
- **Rounding**: `truncate`, `round-half-up`, `stochastic`, `—`.

#### Programmable parameters

Reuse the six-column shape that already appears in the current rev-0.5 doc:

```
| Parameter | Symbol | Width / format | Range | Default | Notes |
```

Only knobs the RTL / firmware exposes: DAC codes, µ, gains, dividers,
dead-bands, freezes, target values, direction registers, lock windows,
saturation limits. Widths and defaults stay `TBD_*`.

#### Overflow / rounding policy

1–3 sentences of prose. Reference the global rule from **Ch. 2-2**:

> Only the CDR phase accumulator / PI path may wrap; all other adaptation
> registers saturate.

Then say what this specific loop does inside that rule (typically:
`truncate after every multiplier; round-half-up on the accumulator-to-storage
trim; saturate at storage width`).

---

## 5. TBD taxonomy

Replace bare `TBD` with one of these tokens (keep table formatting intact):

| Tag | Meaning |
|---|---|
| `TBD_rtl_floorplan` | Needs synthesis / APR result — bit widths, clock periods, pipeline latencies. |
| `TBD_analog_design` | Needs schematic-level analog decision — DAC LSB, comparator offset budget, TIA linearity range, PI code width. |
| `TBD_from_sim_sweep` | Waiting on a specific simulation sweep the team will run later. |
| `TBD_from_link_budget` | Needs product-level target — BER, ppm tolerance, jitter mask. |
| `TBD_from_partner` | Needs LightMatter-side spec — PD polarity, laser power window, MZM Vπ. |
| `TBD_convention` | Sign / index convention that must match SI or RTL — safe to pick a default but flag it. |

Every `TBD_*` cell should have a short Notes-column entry explaining what
resolves it. Example:

```
| Tap register width | — | TBD_analog_design | ± TBD | 0 | Set once DAC LSB and tap normalisation are frozen. |
```

---

## 6. Priority order

Do highest first; the doc is usable at any point in the sequence.

1. **Ch. 10 LMS** — canonical exemplar. Get the template pattern right here first, then replicate the shape in the other chapters.
2. **Ch. 11 MM-CDR** — richest loop (three sub-datapaths). Cross-references Ch. 10 tap widths heavily.
3. **Ch. 5 CTLE adapt** — cross-references Ch. 10 tap magnitudes.
4. **Ch. 6 AGC** — cross-references Ch. 10 `h₀`.
5. **Ch. 7 Offset**.
6. **Ch. 8 Error path** (`e(n)` formation only — the Error Truth Table already exists as a decision table; add the fixed-point companion).
7. **Ch. 9 PLL / PI** — mostly interface (PI code width, cyclic period). Keep short.
8. **Ch. 3 Driver FFE** — control side only (three DAC codes + swing-limit compare + freeze). Keep short.

Chs. 4 (TIA) and 13 (Optical channel interface) are pure analog / partner
interfaces — do **not** add a fixed-point section to them.

After all algorithm chapters are reshaped, bump the **Appendix G** revision
history to `0.6` with a one-line description of the reshape pass.

---

## 7. Style rules

- Voice: technical, no marketing.
- Math: keep the doc's LaTeX (`\(h_0\)`, `\(\mu\)`) — do not switch to `$`.
- Tables: pipe-separated markdown. Six-column parameter tables. Seven-column
  arithmetic-stage tables. Six-column signals tables.
- New sub-headers use markdown `####` (h4) under the existing `## X-Y` (h2)
  subsection header — matches the current convention for "Decision truth
  table" sub-tables.
- **Never** rewrite an existing truth table (LMS enable, MM-CDR PD, AGC
  hysteresis, etc.). You are *adding* four tables per chapter, not replacing.
- Mermaid diagrams are frozen. Do not touch.

---

## 8. Definition of done

- [ ] Chs. 3, 5, 6, 7, 8, 9, 10, 11 each carry a `X-Y Fixed-point specification` section with all four sub-tables.
- [ ] Every parameter, signal, and stage width is either the shape template value (`s N.F`, `Wa × Wb`, ...) or a `TBD_*` tag from §5.
- [ ] No numeric value in the reshape traces back to `optical-serdes/`.
- [ ] Mermaid diagrams unchanged.
- [ ] Existing truth tables (LMS enable, MM PD, AGC, Offset, CTLE direction, CDR lock) unchanged.
- [ ] Appendix G has a rev-0.6 line summarising the reshape.

---

## 9. When to stop and ask

Stop and escalate (do **not** invent) when:

- A chapter's block diagram or truth table names a signal that isn't clearly
  an input / state / intermediate / output — flag the ambiguity in Ch. 15.
- Two chapters disagree on a signal's role or width symbol.
- You find a datapath operation in the sim's code (`optical-serdes/`) that
  the doc does not describe. Do **not** import it. Describe the divergence
  in Ch. 15 and stop.
- Any `TBD_*` value would need to become concrete for the datapath shape
  to make sense (e.g. "accumulator width TBD" is fine; "accumulator width
  greater than tap-register width" is a shape constraint — write it in the
  Notes column, do not resolve it).

---

## 10. Introductory message

Paste this into a fresh Cursor chat with `/home/patrick/mydocs` and
`/home/patrick/optical-serdes` in the workspace. Fill in `[SESSION TASK]`
with what this session should accomplish.

---

> Read `mydocs/oci_msa/analog_transceiver/AGENT_HANDOFF.md` end-to-end
> before you touch anything. It is the source of truth for the task
> shape, TBD taxonomy (§5), style rules, priority order, and hard-stop
> conditions.
>
> The document you will be editing is
> `mydocs/oci_msa/analog_transceiver/OCI_Gen2_PMA_Architecture.md`
> (rev 0.6). Follow the handoff — do not deviate from §5 or §9.
>
> Task this session: **[SESSION TASK]**.
>
> When done, bump Appendix G to the next rev with a one-line summary
> and list in your final chat message which cells you filled (grouped
> by chapter) and which `TBD_*` tags remain.
