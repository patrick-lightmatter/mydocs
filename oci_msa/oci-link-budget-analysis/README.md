# OCI link-budget analysis — reproduction package

All of the numeric analysis behind the four canvases in `canvases/` as clean, runnable
Python scripts. Every headline number on the canvases traces to a print statement in one
of the phase scripts below; each script annotates its output with the expected canvas
value in parentheses.

The unified engineering report is `OCI_Link_Budget_Report.md`.

## Setup

```bash
pip install -r requirements.txt   # numpy, pandas, scipy
python 01_tia_survey.py           # etc. — each script is standalone
```

No arguments; runtime is seconds for 01–03/05, ~1 min for 04 and 06 (CTLE/FIR grid
searches). Each script has an `ASSUMPTIONS` dict at the top holding every judgment call
(everything else is computed from data).

## Inputs (real repo paths, read directly)

| Input | Path | Used by |
|---|---|---|
| TIA output-noise table (152 settings, TT corner) | `LM-link-vpiphotonics/Mesa/Components/TIA/Ocelot_TIA_ADFET.vtmg_pack/Inputs/TT_TIA_DATA_ED_ADFET_20250520/TT_Tia_Noise.csv` | all |
| TIA transfer functions (per setting) | same dir, `TT_Tia_TF_<key>.csv` | all |
| Package trace S-parameters (CPO counterfactual) | `Caribou_EOE/Package/TL_TX_64G.s4p`, `TL_RX_64G.s4p` | 03, 04 |

TIA options A/B and the 60 GHz driver in `06` are user-provided device brackets (no repo
file). Nothing under `sandbox/alex` is used.

## Scripts and the numbers they produce

| Script | What it does | Headline outputs (canvas) |
|---|---|---|
| `common.py` | Shared machinery: TIA table loading + input-referral conventions, `Sim` pulse/ISI/EQ/jitter framework, RIN+shot Q-solve, MPI bound | — |
| `01_tia_survey.py` | Scan all 152 TIA settings, pick the GEN1 design point | 55 usable settings; design point `12211111`: iₙ = 3.17 µA, 29.3 GHz; floor **−12.93 dBm** (bottom-up canvas §1) |
| `02_bottom_up_budget_53g.py` | GEN1 bottom-up budget at 53.125 GBd (legacy pulse machinery kept for exact reproduction) | stack **2.87 dB**; required OMA −10.06 dBm; margins **+0.66** (spec-min Tx) / **+2.36 dB** (realistic Tx); sensitivity table (bottom-up canvas §2–5) |
| `03_cpo_gen2_53g.py` | 53 GBd CPO study: Tx corners, slice-DAC FIR + CTLE scenarios, microbump/package | EQ scenarios (CTLE-only 1.86 dB), stack 3.90 dB, margin +3.03 dB (spec canvas GEN1 column) |
| `04_gen2_106g_feasibility.py` | 106.25 GBd rework: 152-setting rescan, noise scaling law, required TIA class, closure | f²-fit R² 0.87 vs 0.59; scaled floors −10.60/−5.63 dBm; target-class floor **−11.41 dBm**; ISI+EQ 0.82/1.15/1.70; stack **3.74 dB** typ; margins **+2.00/+1.67/+1.12**; required iₙ 4.37 µA (spec canvas §2–6) |
| `05_tia_requirements.py` | Derivations behind the TIA requirements table + `verify_tia()` recipe | BW window plateau −8.66 dBm (50–64 GHz); peaking ≤1 dB / GD ripple ≤3 ps sweep; measured 12.5 ps ripple → h₋₁ 0.48; ZT ≥ 57 dBΩ; overload 150–696 µApp, 731 µA DC; LF cutoff 1.34 MHz (spec canvas §7) |
| `06_device_tradeoffs.py` | TIA A/B × Tx FIR/no-FIR scenario matrix, FIR value isolation, MRM sensitivity | full 24-cell matrix (e.g. no-FIR/MRM60 × B@4 µA **+1.99 dB**; worst cell **+0.50 dB**); no-FIR beats FIR3 by 0.27 dB on matched channel; A-vs-B crossover ≈ 3.6 µA (trade-offs canvas) |

## Conventions worth knowing

- **Input-referred noise** iₙ = (output noise rms) / (peak single-ended p-leg
  transimpedance) — the conservative GEN1 reading of the model, kept everywhere.
- **GEN1 vs GEN2 bandwidth conventions**: the GEN1 budget (scripts 01–02) selects and
  integrates on the single-ended p-leg response (`bw_se`, `BWn_se`, no noise LPF); the
  GEN2 work (03–06) uses the differential response with the model's 60 GHz noise-path
  LPF in the integrals (`bw`, `B1`, `B2`). `common.load_tia_settings()` returns both.
- **Script 02 machinery**: intentionally keeps the original GEN1 pulse implementation
  (start-of-array pulse, zero-excess-phase LF flatten, argmax sampling, ±16 UI span) so
  the canvas reproduces exactly; the improved machinery (centered pulse, causal LF
  flatten, phase-optimized sampling) lives in `common.Sim` and is used from 03 onward.

## Reproduction status

All canvas numbers reproduce exactly or within ±0.01 dB rounding. Two footnotes:

1. The spec canvas §2 line "iₙ ≤ 4.4 µA → +2 dB margin" was derived before the 25 fF
   microbump was charged to the ISI line; with the bump charged (as the §6 closure table
   does), 4.4 µA corresponds to ≈ +1.8 dB and +2.0 dB needs ≈ 4.2 µA. Script 04 prints
   both accountings.
2. A superseded 53 GBd draft of the spec canvas claimed "21 settings close with ≥2 dB";
   script 03's improved machinery gives 15. The claim is not on any current canvas; the
   count is sensitive to the sampling-phase optimization and is reported as-is.
