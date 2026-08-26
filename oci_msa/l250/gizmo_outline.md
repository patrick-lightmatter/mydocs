# Gizmo Arch Spec

## Section 1: Link Overview

### 1-1 Top-level block diagram

### 1-2 Primary goals

### 1-3 Target performance metrics

| Metric | Target | Source / status |
|---|---|---|

### 1-4 OCI-MSA alignment

## Section 2: TX Electrical Jitter Targets at TP1

### 2-1 Adopted standard limits — IEEE P802.3dj D3.1, Table 179-7

| dj metric | dj subclause | Target at TP1 (adopted from Table 179-7) | Abs. @ 9.412 ps UI | What it bounds |
|---|---|---|---|---|

### 2-2 Internal dual-Dirac jitter budget — normative allocations at raw BER 1e-12

| Quantity | Symbol | Requirement at TP1 | Abs. @ 9.412 ps UI |
|---|---|---|---|

### 2-3 Correlation between the §2-1 dj limits and the §2-2 internal budget

| dj metric (§2-1) | dj limit | Internal analog (§2-2) | Internal value | Status |
|---|---|---|---|---|

## Section 3: TX Pre-Driver & Driver Specification

### 3-1 Input pre-driver — CDNS deliverable

| Parameter | Placeholder / symbol | Target / Default | Notes / Basis |
|---|---|---|---|

### 3-2 TX driver — analog TX FIR and electrical limits at TP1

| Parameter | Placeholder / symbol | Target / Default | Notes / Basis |
|---|---|---|---|

### 3-3 Physical output network and MRM interface

### 3-4 TX electrical eye mask — normative definition

## Section 4: TIA Specification

### 4-1 Parameters

| Parameter | Placeholder | Default | Notes |
|---|---|---|---|

### 4-1a Device trade study and recommended TIA class (link budget)

| TIA option | Response | Noise | Margin, typ. Tx (0.38 UI), no-FIR driver |
|---|---|---:|---:|

## Section 5: Clock and Data Recovery (CDR)

### 5-1 Block architecture

| RTL block | Class | Function |
|---|---|---|

### 5-2 Parameter table

| Parameter | Placeholder | Model/RTL name | Range | Default | Meaning |
|---|---|---|---|---|---|

| Register | Placeholder | Width formula | Default width |
|---|---|---|---|

### 5-3 Phase detector and vote truth table

| `d(k−1)` | `d(k+1)` | `e(k)` | vote | Verdict |
|---|---|---|---|---|

### 5-4 Downsampling: the windowed voter

### 5-5 Data paths: phase and frequency

### 5-6 Frequency accumulator: sizing for a ppm offset, and saturation

| Quantity | Value (defaults) |
|---|---|

### 5-7 Loop update summary (per `cdr_width` = 128 UI)

### 5-8 PI resolution and loop-gain rationale

### 5-9 Closed-loop bandwidth target

| Bound | Value | Basis |
|---|---|---|

### 5-10 Cycle-slip policy and damping

### 5-11 Signal-valid gate — CDR state hold

### 5-12 Pattern robustness — consecutive-identical-digit coast

## Section 6: Digital Adaptation Loops

| Outline loop | Implemented as | Block |
|---|---|---|

### 6-1 Common architecture: vote → scale → accumulate → DAC

| Placeholder | Meaning | Formula |
|---|---|---|

### 6-2 Loop inventory and shared error path

| Loop | Controls | Input | Order | Block |
|---|---|---|---|---|

### 6-3 Vp_top / Vp_bot — error-slicer threshold (h₀ digitisation)

| `d(k)` | `e₊(k)` (sample vs `+Vp_top`) | Vote | Action |
|---|---|---|---|

| `d(k)` | `e₋(k)` (sample vs `−Vp_bot`) | Vote | Action |
|---|---|---|---|

| Placeholder | Model/RTL name | Default | Meaning |
|---|---|---|---|

### 6-4 AGC — front-end gain (h₀ amplitude to target)

| Condition on window mean | Vote | Action |
|---|---|---|

| Placeholder | Model/RTL name | Default | Meaning |
|---|---|---|---|

### 6-5 Offset / BLW — common vertical offset

| Condition on window-mean imbalance | Vote | Action |
|---|---|---|

| Placeholder | Model/RTL name | Default | Meaning |
|---|---|---|---|

### 6-6 CTLE — peaking code (residual post-cursor h₁)

| Condition on window-mean correlation | Vote | Action |
|---|---|---|

| Placeholder | Model/RTL name | Default | Meaning |
|---|---|---|---|

### 6-6a Channel estimator — baud-spaced cursor readback ĥ_i (observe-only, all-digital)

| `d(k−i)` | `e(k)` | Product | Meaning |
|---|---|---|---|

| Placeholder | Model/RTL name | Default | Meaning |
|---|---|---|---|

### 6-7 h₋₁ (pre-cursor): no dedicated loop

### 6-8 Loop interaction commentary

| Actor ↓ steps… | …and disturbs | Mechanism | Mitigation |
|---|---|---|---|

### 6-9 Recommended step sizes and bandwidth plan

| Loop | Knobs (default) | UI per code LSB (min) | Time per LSB @ 9.41 ps UI | Separation vs inner neighbour |
|---|---|---|---|---|

### 6-10 Bring-up sequence

| Stage | Active | Frozen / state | Exit criterion |
|---|---|---|---|

### 6-11 Dead-band / hysteresis summary (whole receiver)

| Loop | Mechanism | Variable | Default | Implementation |
|---|---|---|---|---|

## Section 7: Optical Transmitter & Modulator (MRM) Specification

### 7-1 Architecture and electro-optic rationale

### 7-2 Optical launch power, OMA & eye closure (TDEC)

| Parameter | Placeholder / symbol | Target / Default | Notes / Basis |
|---|---|---|---|

### 7-3 MRM electro-optic & physical properties

| Parameter | Placeholder / symbol | Target / Default | Notes / Basis |
|---|---|---|---|

### 7-4 Reflectance, noise (RIN) & protocol squelch

| Parameter | Placeholder / symbol | Target / Default | Notes / Basis |
|---|---|---|---|

## Section 8: TX Disparity Checker

### 8-1 Motivation — MRM sensitivity to transmit-data disparity

### 8-2 Block placement and datapath tap

### 8-3 Disparity metric, accumulation, and readback

### 8-4 Notification interface to the MRM thermal-tuning loop

| Export | Type | Meaning |
|---|---|---|

| Condition on window snapshot | Action | Meaning |
|---|---|---|

### 8-5 Parameter table

| Placeholder | Model/RTL name | Default | Meaning |
|---|---|---|---|

### 8-6 Interaction, timescales, and open items

## Appendix A: Basic Background & Terminology

### A-1 Terminology

| Term | Meaning |
|---|---|

| Acronym | Expansion |
|---|---|

### A-2 Error slicers vs. data slicers

| Slicer | Threshold | Output |
|---|---|---|

### A-3 Channel response: `h_{−1}`, `h_0`, `h_{+1}`

| Cursor | Name | Meaning |
|---|---|---|
