# Qualcomm CPO Questions

Markdown transcription of `Qualcomm CPO Questions.pdf` (19 slides).

## Slide 1 — Bump Map

- **Questions**
  - How big are the driver and TIA?
  - What porosity, in terms of TSVs and metal KOZs, are you assuming in the PIC?
    - Hybrid-bond pads do not need to be uniform.
  - Are you assuming a power-grid/geometry translation in the PIC to go from 45 µm µbump pitch to 150 µm C4?

---

## Slide 2 — Link Architecture: Per-Link DAC/ADC Requirements

**Per tile**

| Component | Count |
|---|---:|
| MRM PN-junction DAC | 4 |
| mPD ADC | 18 |
| VOA DAC | 4 |
| Interleaver heater DAC | 8 |
| MRM heater DAC | 4 |
| CRR heater DAC | 8 |
| Polarization-control heater DAC | 6 |

*mPDs and some heaters can be multiplexed to reduce the total number of ADCs/DACs.*

---

## Slide 3 — Bump Map: Photonics Constraints

- Hybrid-bond pads do not need to be uniform. This allows flexibility in photonic placement.
- Are there any keep-out zones on the PIC, such as for inductors?

| Device | Approximate size (x, y) | x-distance to next pad | y-distance to next pad |
|---|---:|---:|---:|
| mPD | 20 × 3 µm | >10 µm | >25 µm |
| CRR* | 75 × 55 µm | TBD, >100 µm | >65 µm |
| MRM* | 55 × 35 µm | ≥45 µm | ≥45 µm |

\* Assumes y is the direction of light propagation shown on the enclosed bump map. Larger spacing is likely required to prevent thermal crosstalk.

\** MRM and CRR heater controls can be electrically routed to different locations on the chip.

---

## Slide 4 — Transmitter Questions

- Do we have control over MRM bias? Can this be increased?
- For the MRM bias network, can you share the R and C values, `Vbias`, and the TIA common mode you have in mind?
- What is the step-size granularity for each TX tap?
- Does AthenaCore implement OCI constant-AOP squelch—modulation off, average power held, and DC bias independent of swing mute—and expose squelch state and timing to an external photonic controller?

---

## Slide 5 — Receiver Questions

- What drives the 2–3 V reverse-bias requirement for the high-speed PD?
- Is there an option to bias the mPDs at a nominal 0 V?
- How do you plan to bias the high-speed PD between `RXP`, `RXN`, and `VDD_PD_RX`?
- How will the DACs reach 2–3 V of reverse bias with a 1.6 V full scale?
- How do you plan to close the loop on RX ring tuning?
- What equalization capabilities are available? Is a one-tap DFE planned?
- Can the CTLE provide more than 3 dB?

---

## Slide 6 — AthenaCore

**1.6T macro**

*This slide is primarily visual; refer to the source PDF for the macro illustration.*

---

## Slide 7 — General EIC Questions

- We will use LM stabilization IP.
- What is the best integration method—a hard macro?
- What are the microcontroller specifications?
- UCIe mux/gearbox:
  - Does it support backpressure?
  - What assumptions are being made?
- Will it support both OCI Gen1 and OCI Gen2?

---

# DO NOT SHARE

## Slide 8 — Internal Section Divider

**DO NOT SHARE**

---

## Slide 9 — Bump Map Comparison

- **Quebec:** 270 µm × 540 µm = 0.146 mm² for four lanes, including driver and TIA
  - 0.0365 mm²/lane
- **Comparisons**
  - Gizmo target: <0.15 mm²/lane, excluding driver and TIA
  - 224G SerDes: 0.6–0.7 mm²/lane
  - Gizmo TIA: 205 µm × 90 µm = 0.018 mm²
    - Multistage Cherry-Hooper with inductors
  - Gizmo driver: 0.04 mm²
- One complete Quebec lane is smaller than the Gizmo driver.
- It is highly unlikely that this is realizable; it is more likely a bump-limited floorplan.

*The source slide includes the Gizmo TIA floorplan from Cliff Ting.*

---

## Slide 10 — Gizmo: BER Performance

- Energy points shown: 0.94, 1.6, 1.9, and 2.4 pJ/bit.
- Fails the OCI Gen1 TP2 maximum-power requirement.
- Gen2 may provide some relief; the working estimate is 1.5 dB.
- At least 10 mW of laser power is needed to reach a BER of `1e-12` with a realistic customer channel.
- The analysis excludes many impairments and corners; performance will worsen as those are included.

*Refer to the source PDF for the plotted BER curves and eye images.*

---

## Slide 11 — Eyes

*Visual eye diagrams; refer to the source PDF.*

---

## Slide 12 — Transmitter

- The targets are similar to Gizmo:
  - Effective swing: 2.5–3 V
  - Three-tap FFE: main + one pre-cursor + one post-cursor

*Refer to the source PDF for the transmitter figure.*

---

## Slide 13 — Receiver Comparison

| Specification | Quebec value | Gizmo / Cliff Ting TIA |
|---|---|---|
| Data rate | 100 Gb/s NRZ | 106.25 Gb/s NRZ |
| BER target | `1e-12` | `1e-9` is the likely landing zone |
| Responsivity | ≥0.85 A/W | 0.9 A/W assumed |
| PD capacitance | ≤20 fF | TBD |
| Small-signal bandwidth, including PD | 50 GHz | 50.2 GHz, without PD |
| Input RMS noise | 3.1–4 µA | 3.5 µA full band; 2.7–3.1 µA to `f_3dB` |
| CTLE | 3 dB at Nyquist, 1 dB steps | 0.33 dB fixed peaking; no CTLE |
| Input-referred noise density | 15–20 pA/√Hz | 8 pA/√Hz at 1 GHz; 16 at 25 GHz; 19 at 50 GHz |
| OMA sensitivity at PD, BER `1e-12` | −9.5 dBm | Approximately −7.5 dBm |

It is unlikely that Gizmo will reach `1e-12` after impairments are included.

---

## Slide 14 — Gizmo: Data-Path Insight Enables Better MRM Control

- **Pattern-dependent self-heating is the MRM control problem at 106.25 GBd**
  - Deterministic, zero-mean resonance wander is driven by run length and disparity; the thermal response extends from tens of nanoseconds to approximately microseconds.
  - The budget is tight: OCI Gen1 allows `dTDEC(SSPR vs. PRBS13) ≤ 0.4 dB`, while 400G mode absorbs 3 dB more power on the same allocation.
- **Today's observables cannot see it**
  - L2V average-power lock: DC-balanced data has zero mean shift, so it reports “locked” while the eye closes and cannot separate a disparity change from resonance drift.
  - PGT dither lock-in: bandwidth is bounded by dither/integration in the kilohertz class, while dither amplitude consumes TDEC budget.
  - Both are feedback through the thermal plant and observe the drop port after the heat has moved.
- **Gizmo owns the serializer—the pattern is known before it reaches the ring**
  - A TX disparity checker is already in the Gizmo architecture, with heater-servo gating defined; the feedforward path is the next step.
  - Feedforward can filter running disparity into a pre-emphasized heater code plus a bias-VDAC term for the nanosecond-scale edge.
  - Drop-port power then becomes a calibration input instead of the only error signal.
  - Precedent: Sun et al., JSSC 2016 demonstrated bit-statistics tracking and self-heating cancellation that held the eye open under arbitrary disparity.
- **AthenaCore hides the serializer; using it off the shelf requires a TX disparity/data-path tap**
  - Export running disparity to the photonic controller—or give up this control advantage.

---

## Slide 15 — Gizmo: Squelch Is a Known Event, Not a Disturbance

- **Squelch is a mandated MRM plant change on every relink (OCI Gen1 Table 1-3)**
  - RF is removed, OMA is ≤−15 dBm in 200G mode or ≤−12 dBm in 400G mode, and average power is held within ±0.5 dB.
  - The transmitter dwells for 60–75 ms, then enters the 160-bit deskew training pattern.
  - Removing modulation changes intracavity energy and carrier self-heating, creating a resonance step that the heater must absorb with zero unlock events; the target is ≤10 ms.
- **To a drop-port-only controller (L2V/PGT), squelch looks like sudden drift**
  - The servo chases the step, dither leaks into the squelched-OMA margin, and a wrong-direction excursion risks a spurious far-end LOS.
  - Exit enters the training pattern while the ring is still walking back, so pattern heating resumes on top of the step.
- **Gizmo's squelch sequencer commands the event: instant, direction, `V_sq`, and exit target**
  - Already architected: heater ramp-limit freeze at entry/exit; disparity path gated so the static HOLD code is not interpreted as data; and `V_sq` calibrated per lane against the drop port.
  - This enables a mode switch: feed forward the calibrated heater offset at entry/exit, use average-power lock while the pattern is static, and return to disparity feedforward at exit.
  - Constant-AOP squelch requires independent swing-mute and DC-bias paths in the driver—a Gizmo driver decision, not a generic SerDes electrical idle.
- **AthenaCore executes squelch inside the macro; we would see only the optical aftermath**
  - Ask Qualcomm to export squelch state, timing, and exit target.
  - Confirm bias-hold squelch—not swing collapse or laser blanking—with swing-independent DC bias.

---

## Slide 16 — Bump Map: COUPE OCI Gen2

- LM/MA lane pitch: 450 µm
- Quebec lane pitch: 135 µm
- There is no way to meet such a tight pitch.
- The bank requires depopulated bumps to fit CRRs and associated path-length matching.
- TSV/C4 bumps and hybrid-bond pads need to be relatively sparse.
- Waveguide density is a concern.
- This does not include the additional space required for analog keep-out zones.

*The source slide includes the Gizmo TIA floorplan from Cliff Ting.*

---

## Slide 17 — Photonic-Control Count Comparison

Assumptions:

- Architecture mitigates nonlinear absorption and four-wave mixing.
- Interleavers on both sides mitigate back-reflections.
- High-power MRMs are used.

| Control or monitor | Count | Scope |
|---|---:|---|
| PN dither | 4 | Per bank |
| mPD | 16 | Per bank |
| Interleaver heater | 8 | Per bank |
| MRM heater | 4 | Per bank |
| CRR heater | 8 | Per bank |
| Polarization-control heater | 6 | Per bank |
| mPD per laser | 1 | Per bank |

---

## Slide 18 — Laser Split

- Assumes a 1:4 laser split.
- The source slide shows an alternate 1:6 split.

*Refer to the source PDF for the optical-layout diagram.*

---

## Slide 19 — Bump-Count Warning

**The number of bumps is undercounted.**

*Refer to the source PDF for the annotated bump-map figure.*
