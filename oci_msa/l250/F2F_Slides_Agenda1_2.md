# Cadence × Lightmatter — High-Speed Analog F2F
## Slide deck: Agenda Items 1–2 (high level, 15 min each)

Sources: `l250/architecture_spec.md`, `oci-link-budget-analysis/OCI_Link_Budget_Report.md`, `LM+CDNS_ Next Gen SerDes (2).pdf` (Oct 2025 — **LM Proprietary/NDA**). **[TBD]** = not in source docs.

---

## AGENDA ITEM 1 — Introductions & Program Context (Both · 15 min)

---

### Slide 1 — Title, Objective & Program Context
**Cadence × Lightmatter — High-Speed Analog Front-End F2F**
- In-person, ~full day · Week of Aug 10, 2026 **[TBD — confirm date]** · analog design leads & architects, both teams
- **Objective:** LM's analog front end (TIA, Driver) meets the Cadence SerDes macro at a fully analog boundary (no ADC/DSP in between) — align today on **signal contracts, simulation methodology, and system interactions** at both boundaries (Rx: PD→TIA→SerDes; Tx: SerDes→Driver→MRM)
- **Program:** OCI-MSA Gen2 CPO link, LM **Passage L-Series**, **106.25 Gbps NRZ**, BER < 1e-12 target, ES target **Q4'27** — interface specs need to close well ahead of tape-out
- **Ownership:** LM owns TIA/CTLE/AGC, driver, MRM/PIC; CDNS owns SerDes Rx/Tx core, CDR, digital loops, D2D/UCIe
- Round-robin intros, confirm decision-makers **[names TBD]** · rest of day: TIA deep-dive → Rx circuitry → lunch/demo → Tx serializer → Tx driver deep-dive → open items · goal per session is a **mutually agreed interface spec**, not just a readout

---
---

## AGENDA ITEM 2 — Architecture Overview: Signal Path Walkthrough (LM · 15 min)

---

### Slide 2 — Top-Level Signal Path
```
NRZ data → Driver (3-tap FIR-DAC) → MRM  →  fiber  →  PD → TIA → SerDes Rx slicers → CDR
  [LM]         [LM]              [LM]                [LM]  [LM]      [CDNS]        [CDNS]
```
- No electrical transmission line anywhere — direct microbump attach at both ends
- **Bandwidth/noise of driver, MRM, PD, TIA dominate the budget, not channel loss**

---

### Slide 3 — Rx Path: PD → TIA → SerDes
- PD: R ≈ 1 A/W (ideal, no noise/BW modeled yet)
- TIA/CTLE/AGC macro: ~1 kΩ transimpedance (62–80 dB range), BW to Nyquist (53.125 GHz), noise ≤ 1.5 µA rms target, CTLE-only (no DFE)
- Hands off to CDNS at TIA output: data slicer + 2 error slicers → CDR (**Item 4's focus**)

---

### Slide 4 — Tx Path: SerDes → Driver → MRM
- CDNS serializer → LM driver interface: **TBD, CDNS deliverable pre-freeze**
- LM driver: 3-tap FIR-DAC, mandatory asymmetric FFE (compensates MRM nonlinearity), 2.0–3.0 Vppd into a 60 fF direct-attach load, no termination
- MRM: carrier-depletion ring, ER ≥ 3.5 dB (**Item 6/7's focus**)

---

### Slide 5 — Grounding: Margin & Scale
- Derived TIA class: 50–64 GHz BW, ≤ 4.0 µA rms noise → link closes at **+1.34 dB typical margin** (feasible, spec-sensitive)
- This lane replicates many times per EIC (~0.04 mm² per DRV/TIA) — the contract we set today isn't a one-off
- Architecture is a deliberate NRZ choice (linear-only EQ, fixed-center slicer) vs. the fuller PAM4 stack — not a placeholder

---

### Slide 6 — Open Boundaries → Next Up
- Two interfaces still open: Serializer→Driver input, TIA output→Rx slicers — today's remaining sessions close them
- Next: **Rx TIA design deep-dive (LM, 60 min)**, then **surrounding Rx circuitry (CDNS, 60 min)**

---
