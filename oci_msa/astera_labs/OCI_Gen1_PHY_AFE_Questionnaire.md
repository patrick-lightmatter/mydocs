# Astera Labs OCI Gen1 PHY + AFE Technical Questionnaire

**Purpose:** Collect the electrical PHY and analog-front-end information needed to estimate end-to-end link performance for an OCI Gen1 proposal.

**Interface context:** 53.125 GBd NRZ per optical lane, four wavelengths per 212.5 Gb/s stream, aligned with the 200G OCI Optical PHY Specification v1.0.

**Requested from:** Astera Labs  
**Prepared for:** Bradford / Astera Labs proposal team  
**Date:** 2026-08-08  
**Status:** Draft for vendor response

---

## 1. Response instructions

Our current understanding is that the proposed Astera Labs device includes the SerDes PHY, electrical transmitter driver, receiver TIA/AFE, clock recovery, and associated equalization/control functions, while the photodiode, optical modulator, laser, and optical mux/demux are external. Please correct this integration boundary if it is inaccurate.

For each item:

- Enter the nominal, minimum, and maximum values where available.
- State the process, voltage, temperature, data pattern, BER, load, bandwidth, and measurement plane used.
- Distinguish guaranteed specifications from simulated, characterized, or typical values.
- If a parameter is not applicable, identify the architecture reason.
- If detailed data is confidential, a bounded range or pass/fail statement is still useful.
- Electronic data files are preferred for frequency responses, spectra, and corner sweeps.

### Priority

| Priority | Meaning |
|---|---|
| **P1** | Required to establish the link model or determine basic feasibility |
| **P2** | Required to produce a credible corner and margin analysis |
| **P3** | Useful for implementation planning, diagnostics, or optimization |

### Reference conditions

Unless otherwise stated, requests apply per optical lane at 53.125 GBd NRZ across supported PVT corners. OCI MSA values below are interface references, not assumed characteristics of the Astera implementation.

---

## 2. Architecture and integration boundary

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| A-1 | PHY/AFE block diagram showing the Tx data path, driver, Rx input, TIA, equalizers, samplers/ADC, CDR, adaptation, deskew, and management interfaces | Diagram with integration boundaries and clock domains | 53.125 GBd NRZ, 4λ per 212.5 Gb/s stream | Establishes the model boundary and prevents double-counting functions | P1 |
| A-2 | Confirm which blocks are integrated and which are external: serializer/deserializer, driver, TIA, PD, modulator, laser, mux/demux, termination, AC coupling, CDR, FEC, and deskew | Integrated / external / optional for each block | OCI PMA includes 4λ deskew and line-side PMA functions | Defines ownership of channel impairments and controls | P1 |
| A-3 | Receiver architecture | Analog slicer, ADC/DSP, or hybrid; sampling rate and ADC resolution if applicable | MSA does not prescribe implementation | Determines applicable noise, equalization, and quantization models | P1 |
| A-4 | Supported line modes and lane mappings | Baud rate, modulation, wavelength count, aggregate rates, lane remapping options | 53.125 GBd NRZ × 4λ | Confirms that the proposed mode matches the optical interface | P1 |
| A-5 | Intended optical transmitter/modulator interface | Modulator type; differential/single-ended drive; expected voltage, capacitance, termination, and bias environment | MSA specifies the optical output, not the electrical modulator interface | Driver performance depends strongly on the actual optical load | P1 |
| A-6 | Intended photodiode interface | PD type; single-ended/differential current; responsivity assumption; capacitance and package/interconnect assumptions | MSA specifies receiver performance at TP3 | TIA bandwidth and noise are inseparable from PD loading | P1 |
| A-7 | Supported process, voltage, and temperature range | PVT corner list and guaranteed operating range | Vendor-defined | Needed to interpret all min/max values consistently | P2 |
| A-8 | Availability and maturity | Silicon revision, simulation-only vs characterized, sample schedule, known errata | — | Determines confidence to assign to the supplied parameters | P3 |

---

## 3. Transmitter driver and Tx equalization

### 3.1 Electrical interface and load

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| TX-1 | Driver topology | Limiting/current-mode/voltage-mode/linear; single-ended or differential; segmented or monolithic | MSA does not prescribe electrical driver topology | Selects the correct transfer-function and distortion model | P1 |
| TX-2 | Differential output swing and common-mode range | Nom/min/max Vppd and common mode across PVT and legal EQ settings | Optical OMA and ER are specified at TP2 | Connects electrical drive capability to modulator OMA/ER | P1 |
| TX-3 | Designed output load | Differential and common-mode R, C, L; state whether load is a terminated line or direct capacitive attachment | MSA does not specify the internal electrical load | The loaded response, not unloaded bandwidth, sets optical edge rate and ISI | P1 |
| TX-4 | Output impedance and termination assumptions | DC and frequency-dependent differential output impedance; source/back termination; on-die termination range and tolerance | — | Required to combine the driver with package and modulator parasitics | P1 |
| TX-5 | Interconnect/package assumption between driver and modulator | Trace length/type, bump or wirebond model, S-parameters, insertion/return loss, crosstalk | — | Distinguishes a direct-attach CPO load from a matched electrical channel | P1 |
| TX-6 | Large-signal electrical transfer or edge response | 20–80% and 10–90% rise/fall time at min/nom/max swing, stated load, PVT, and EQ settings | Optical transition time ≤ 17 ps, 20–80% | Converts driver/loading into optical ISI and TDEC | P1 |
| TX-7 | Small-signal bandwidth and peaking | Magnitude and phase response; f3dB; peaking; measurement load and bias | — | Useful for correlation, but must be paired with large-signal data | P2 |
| TX-8 | AC-coupling or low-frequency behavior | High-pass corner, droop, maximum CID supported, baseline-restoration behavior | Training pattern is largely repeating `0xCC`; mission pattern may contain longer runs | Bounds baseline wander and pattern-dependent level errors | P2 |
| TX-9 | Electrical overstress and reliability limits | Maximum differential/single-ended voltage, common mode, current, overshoot, and duty cycle | — | Ensures proposed modulator drive remains inside safe operating limits | P3 |

### 3.2 Tx equalization capability

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| TXE-1 | Tx equalization architecture | FIR/FFE, analog peaking, edge shaping, or none | MSA does not prescribe equalization | Determines how much channel and modulator ISI can be pre-compensated | P1 |
| TXE-2 | FIR tap count and placement | Number of pre-/post-cursor taps and delay spacing in UI | — | Required for pulse-response optimization | P1 |
| TXE-3 | Tap coefficient range, sign, and resolution | Min/max per tap, code width or step, normalization/swing constraint | — | Quantifies equalizable cursor range and OMA cost | P1 |
| TXE-4 | Independent control of rising/falling edges or logic levels | Yes/no; coefficient-bank arrangement and supported asymmetry | — | Optical modulators can exhibit direction-dependent dynamics | P2 |
| TXE-5 | Tap delay accuracy and matching | Nominal UI spacing, static error, PVT drift, jitter contribution | — | Tap skew can turn intended amplitude EQ into timing distortion | P2 |
| TXE-6 | Adaptation and calibration method | Fixed/manual/adaptive; objective function; training pattern; convergence time; background tracking | OCI defines training/release sequences | Determines whether supplied EQ performance is available in operation | P2 |
| TXE-7 | EQ code access and telemetry | Register/API access, default values, readback, per-lane controls | CMIS/management integration is implementation-specific | Enables lab optimization and model correlation | P3 |

### 3.3 Tx signal quality and jitter

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| TXJ-1 | Random jitter | RMS in ps and UI; integration band; pattern and clock source | MSA specifies optical TDEC, not electrical RJ | Inputs the link's dual-Dirac jitter model | P1 |
| TXJ-2 | Deterministic jitter decomposition | DJ, DCD/PWD, data-dependent jitter, periodic/bounded jitter in ps and UI | — | Separates equalizable ISI from non-equalizable timing closure | P1 |
| TXJ-3 | Total jitter | Peak-to-peak value and BER/extrapolation method | CEI-56G-XSR-NRZ context: TJ ≤ 0.28 UI | Required for horizontal eye and BER analysis | P1 |
| TXJ-4 | Output eye / SNDR characterization | Eye diagrams and bathtub curves at the driver output; SNDR if available; specify load and EQ | — | Cross-checks the component jitter and distortion entries | P2 |
| TXJ-5 | Reference-clock requirements and jitter transfer | Input clock type, allowable jitter spectrum, multiplication architecture, output sensitivity | — | Avoids assigning internally generated jitter to the wrong block | P2 |

---

## 4. Receiver TIA and analog front end

### 4.1 Input interface, gain, bandwidth, and phase

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| RX-1 | TIA input interface and termination | Single-ended/differential; input impedance vs frequency; termination/bias network; supported photocurrent polarity | Receiver is specified optically at TP3 | Defines the PD-to-TIA electrical interface | P1 |
| RX-2 | Assumed total input capacitance | PD, pad, bump/package, ESD, and TIA contributions separately; allowed range | Vendor-specific | Bandwidth and noise feasibility depend directly on input capacitance | P1 |
| RX-3 | Transimpedance gain | Differential and single-ended gain in V/A or dBΩ; DC/midband/peak; nom/min/max | — | Converts photocurrent eye and noise into slicer voltage | P1 |
| RX-4 | Gain-control range and step | Total dB range, step size, code count, linearity, update time, per-lane control | Rx OMA can extend to −1 dBm max | Required for sensitivity-to-overload dynamic-range analysis | P1 |
| RX-5 | Frequency response | Complex transfer function (magnitude and phase) by gain/EQ setting and PVT; f3dB definition | — | Direct input to pulse-response and ISI analysis | P1 |
| RX-6 | Magnitude peaking and ripple | Peak dB, frequency, flatness, monotonicity, setting dependence | — | Excess peaking changes noise and pulse tails | P1 |
| RX-7 | Group delay / phase linearity | Group-delay ripple p-p and complex phase, preferably 0.1 GHz through at least 1.5× f3dB | — | Flat magnitude alone can conceal severe pre-cursor ISI | P1 |
| RX-8 | Variation across PVT and settings | Corner envelopes for gain, bandwidth, peaking, and group delay | — | Establishes worst-case receiver performance rather than TT-only performance | P2 |

### 4.2 Noise, sensitivity, overload, and low-frequency behavior

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| RXN-1 | Input-referred total noise current | µA rms; state integration limits, gain used for referral, single-ended vs differential convention, and included/excluded blocks | SRS ≤ −6.2 dBm OMA at BER 2.4×10⁻⁴ | Sets the analytic OMA sensitivity floor | P1 |
| RXN-2 | Input-referred noise-density spectrum | pA/√Hz vs frequency to at least 1.5× f3dB for each relevant gain/EQ setting | — | A single rms number cannot predict EQ noise enhancement or bandwidth scaling | P1 |
| RXN-3 | Output-noise spectrum and integration method | V/√Hz and integrated rms; RBW, de-embedding, and measurement setup | — | Allows independent verification of input referral | P2 |
| RXN-4 | Included noise sources | TIA only vs TIA+CTLE+VGA+slicer/ADC; treatment of shot noise, dark current, and PD noise | — | Prevents omission or double-counting in the link model | P1 |
| RXN-5 | Optical/electrical sensitivity characterization | OMA sensitivity vs BER, pattern, wavelength, ER, and TDEC/SEC; identify FEC state | RxSens ≤ max(−8.2, −9.6+TDEC) dBm; SRS ≤ −6.2 dBm | Cross-checks the analytical sensitivity model | P1 |
| RXN-6 | Overload and linear input range | Min/max OMA and photocurrent without BER degradation; compression point; maximum average current | OMA max −1 dBm; average receive power max 0 dBm; damage threshold 4.5 dBm | Establishes AGC need and upper operating bound | P1 |
| RXN-7 | DC photocurrent handling and cancellation | Maximum DC current, cancellation range/step, loop corner, acquisition time, residual offset | Average receive power can reach 0 dBm/channel | Average optical power can consume TIA headroom | P1 |
| RXN-8 | Low-frequency cutoff and baseline wander | fLF, droop vs CID length, recovery time, interaction with DCOC/AGC | OCI training/release behavior must remain stable | Bounds long-run and pattern-swap penalties | P2 |
| RXN-9 | Input protection and damage limits | Continuous and transient current/power; ESD structure capacitance | Damage threshold 4.5 dBm/channel | Confirms safe operation over the MSA range | P3 |
| RXN-10 | LOS behavior | Assert/deassert thresholds, hysteresis, response time, measurement domain | LOS assert −19…−14 dBm; hysteresis 1…3 dB | Needed for relink behavior and low-power coverage | P3 |

---

## 5. Receiver equalization and adaptation

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| EQ-1 | CTLE capability | Zero/pole topology, peaking range and step, max gain, noise effect, per-lane control | MSA does not prescribe Rx EQ | Required to model recoverable high-frequency loss and noise enhancement | P1 |
| EQ-2 | Receiver FFE | Presence, tap count/spacing/range/resolution, pre-/post-cursor coverage | — | Changes residual ISI and may reduce DFE dependence | P1 |
| EQ-3 | DFE capability | Presence, tap count, coefficient range/resolution, adaptation rate, error propagation controls | — | The link penalty changes materially if post-cursors are not cancelled | P1 |
| EQ-4 | Equalization order and signal path | TIA, VGA/AGC, CTLE, ADC/slicers, FFE/DFE ordering | — | Determines where noise, saturation, and gain changes enter | P1 |
| EQ-5 | Adaptation observables and algorithms | Training vs decision-directed, slicer/ADC inputs, objective, dead bands, freeze/hold behavior | MSA uses training and release patterns | Establishes robustness and model assumptions | P2 |
| EQ-6 | Supported patterns for adaptation | PRBS types, OCI training/release pattern, mission data, minimum transition density | Training pattern is 160-bit and largely `0xCC` | Pattern dependence may bias adaptation or prevent convergence | P2 |
| EQ-7 | Acquisition and tracking performance | Initial conditions, convergence time, tracking rate, PVT drift handling | OCI timing budgets are in milliseconds | Confirms EQ is ready before mission data begins | P2 |
| EQ-8 | Controls and telemetry | Manual override, code readback, convergence/rail flags, eye monitor, margining capability | CMIS/VDM support is implementation-specific | Enables bring-up and correlation to link estimates | P3 |

---

## 6. CDR, clocking, and timing

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| CDR-1 | CDR architecture | Analog/digital, baud/oversampled, phase detector, PI/VCO/DCO, frequency-acquisition path | MSA does not prescribe architecture | Establishes tracking and jitter-generation assumptions | P1 |
| CDR-2 | Jitter-tolerance mask | SJ amplitude vs frequency; test pattern, BER criterion, stress conditions, and standard used | MSA publishes SEC/SRS but no explicit JTOL table | Needed to verify operation with the expected Tx/channel jitter spectrum | P1 |
| CDR-3 | Signaling-rate tolerance | Per-end and relative ppm range; acquisition and tracking limits | MSA does not state ppm; CEI context is ±100 ppm | Bounds independent-clock operation | P1 |
| CDR-4 | Loop bandwidth and peaking | Closed-loop bandwidth, damping/jitter peaking, programmable modes | — | Determines tracked vs untracked jitter allocation | P2 |
| CDR-5 | Lock acquisition | Frequency/phase pull-in range and time; gear-shift behavior; initial conditions | `t_lock` ≤ 50 ms after modulation restoration | Confirms compatibility with link startup timing | P2 |
| CDR-6 | Loss-of-lock detection | LOL criteria, assert/deassert times, false-lock protection, exposed status | MSA requires LOL indication within 50 ms | Drives relink and fault handling | P2 |
| CDR-7 | Consecutive-identical-digit behavior | Maximum CID without slip; whether frequency state coasts or holds; include a 72-UI run test if available | OCI training uses repeated `0xCC`; the 72-UI test is an engineering characterization request, not an OCI MSA requirement | Ensures timing remains stable without transitions | P2 |
| CDR-8 | Pattern-swap continuity | Behavior during training → release → mission change; required freeze/reacquisition actions | Swap must be phase-continuous and not lose far-end lock | Prevents startup-induced burst errors | P2 |
| CDR-9 | Recovered-clock/data outputs and observability | Clock rate, phase margining, lock metrics, error counters, diagnostic modes | — | Supports lab validation and root-cause isolation | P3 |

---

## 7. BER, FEC, diagnostics, and protocol compliance

### 7.1 BER and FEC

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| BF-1 | PHY operating BER target | Raw/pre-FEC BER target and guaranteed BER floor; pattern and confidence interval | TDEC/SRS use 2.4×10⁻⁴; BER floor ≤ 1×10⁻⁶ | Defines the Q-factor and required sensitivity | P1 |
| BF-2 | FEC location and type | Internal, host-side, bypassable; code type and thresholds; symbol/lane mapping | OCI interfaces to Ethernet PMA/PCS structures | Prevents inconsistent pre-/post-FEC assumptions | P1 |
| BF-3 | Error monitoring | PRBS generator/checker support, supported polynomials, raw BER, pre-FEC BER, corrected/uncorrectable counts | OCI VDM includes pre-FEC BER and per-channel PRBS BER | Needed to validate modeled margin on hardware | P2 |
| BF-4 | Error propagation behavior | DFE burst behavior, CDR-slip impact, lane-error containment | — | Connects physical errors to FEC effectiveness | P3 |

### 7.2 OCI MSA protocol and management

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| PM-1 | OCI MSA v1.0 compliance statement | Supported, partially supported, or external; list deviations | 200G OCI Optical PHY Specification v1.0 | Identifies functions that the proposal must supply elsewhere | P1 |
| PM-2 | Training and release pattern support | Generation/detection, channel-ID fields, timing, programmability | 160-bit patterns; training ≥ 285 ms; release ≥ 200 ms | Required for OCI link initialization | P1 |
| PM-3 | Four-wavelength deskew | Range, resolution, buffering, acquisition time, tracking, error flags | Compensate 0–7 UI relative skew | Confirms line-side lane alignment capability | P1 |
| PM-4 | Pattern detection robustness | Supported BER during detection, false-detect behavior, MPI sensitivity | Pattern detect functional at BER ≤ 1×10⁻⁴ | Determines startup robustness under a stressed optical link | P2 |
| PM-5 | Squelch and relink behavior | Modulation control/indication, timers, state retention, AOP assumptions | Tx squelch 60–75 ms; AOP remains on | Confirms coordination with optical heater/laser controls | P2 |
| PM-6 | LOS/LOL and relink triggers | Flags, debounce, interrupt behavior, state-machine ownership | LOS, CDR LOL, or repeated uncorrectables trigger relink | Defines system fault handling | P2 |
| PM-7 | Bit and wavelength mapping | Lane order, polarity, remap/invert capabilities | LSB maps to shortest wavelength | Avoids integration and deskew mapping errors | P2 |
| PM-8 | CMIS/VDM support | Version, transport, exposed telemetry, alarms, vendor extensions | OCI references CMIS 5.3 and VDM | Establishes management integration effort | P3 |

---

## 8. Power, area, and operating controls

| ID | Requested information | Response format / conditions | OCI Gen1 reference | Why needed | Priority |
|---|---|---|---|---|---|
| PWR-1 | Tx driver power | mW/lane and pJ/bit at nominal mode; min/max swing and EQ dependence | — | Supports proposal power budgeting | P2 |
| PWR-2 | TIA/AFE power | mW/lane and pJ/bit; gain/EQ/ADC dependence | — | Supports proposal power and thermal budgeting | P2 |
| PWR-3 | CDR/digital PHY power | mW/lane plus shared overhead | — | Completes PHY power estimate | P2 |
| PWR-4 | Total PHY power and area | Per-lane and four-lane macro, including shared PLLs/control | — | Enables package and thermal feasibility assessment | P2 |
| PWR-5 | Supply rails and tolerances | Nominal/min/max, sequencing, ripple sensitivity, isolation requirements | — | Required for board/package integration | P3 |
| PWR-6 | Low-power, reset, and state-retention modes | Entry/exit times, calibration retention, link impact | OCI relink timing applies | Defines system power-management behavior | P3 |

---

## 9. Feature and diagnostic capability checklist

For each feature below, please answer supported / not supported / roadmap, and describe the capability where supported. This section expands on the telemetry items referenced in EQ-8, BF-3, and PM-8; cross-reference those answers rather than repeating them where convenient.

| ID | Feature | If supported, please describe | Why needed | Priority |
|---|---|---|---|---|
| FT-1 | Rx eye monitor / on-chip eye scan | 1D (timing or voltage bathtub) vs full 2D eye capture; resolution in UI and mV; capture depth; whether the scan is non-destructive on live mission traffic or requires a dedicated sampler | Primary tool for correlating measured eye margin against the link estimate without external instrumentation | P1 |
| FT-2 | BER margining | Horizontal/vertical decision-point offset sweeps with live BER readout; step sizes; automation support | Converts eye-monitor data into quantified margin at the operating BER | P1 |
| FT-3 | Loopback modes | Host-side (shallow/deep), line-side, and per-block loopbacks; supported rates and any signal-path differences vs mission mode | Isolates Tx, Rx, and channel contributions during bring-up and fault isolation | P1 |
| FT-4 | Pattern generation and checking | Per-lane PRBS generators/checkers (polynomials per BF-3), fixed and user-defined patterns, OCI training/release pattern generation, error injection | Enables lane-level BER validation independent of host traffic | P2 |
| FT-5 | Adaptation-state and AFE telemetry readback | EQ tap/CTLE/AGC/offset code readback, CDR phase/frequency state, signal-level (RSSI-like) indicators, convergence/rail flags | Confirms the AFE is operating where the link model assumes; flags marginal convergence | P2 |
| FT-6 | Eye/link health monitoring during mission traffic | Background eye-opening metric, pre-FEC BER trend, alarm thresholds and interrupts | Supports in-service monitoring and degradation detection | P2 |
| FT-7 | Lane-level controls | Per-lane enable/power-down, polarity inversion, lane swap/remap (see PM-7), independent rate/EQ settings | Simplifies board routing and partial-lane debug | P2 |
| FT-8 | Environmental and supply sensors | On-die temperature and voltage monitors; accuracy; readout path | Correlates performance drift with operating conditions | P3 |
| FT-9 | Diagnostic dump and scripting access | Bulk register/state snapshot, vendor debug tools, API/SDK availability | Reduces lab iteration time and support round trips | P3 |
| FT-10 | Firmware/configuration management | Firmware update mechanism, configuration persistence, version reporting | Establishes maintainability across the proposal lifecycle | P3 |

---

## 10. Requested characterization data and models

Electronic data is preferred over screenshots. Please identify the silicon revision, PVT corner, bias/EQ/gain setting, fixture, calibration plane, and de-embedding applied to every file.

| ID | Requested deliverable | Preferred format / coverage | Why needed | Priority |
|---|---|---|---|---|
| D-1 | Detailed PHY/AFE block diagram and programming guide | PDF plus register/API documentation | Defines model boundary and usable controls | P1 |
| D-2 | TIA complex transfer functions | Touchstone, CSV, or complex V/A vs frequency; magnitude and unwrapped phase for relevant gain/EQ settings and PVT; 0.1 GHz to ≥ 1.5× f3dB (approximately 45 GHz if f3dB is ~30 GHz) | Produces pulse response, ISI, peaking, and group delay | P1 |
| D-3 | TIA output-noise spectra | CSV V/√Hz vs frequency and integrated rms; same settings/corners as D-2; measure to ≥ 1.5× f3dB | Establishes input-referred noise and EQ noise enhancement | P1 |
| D-4 | TIA input/interface model | Input impedance or S-parameters; package/interconnect model; PD-capacitance assumption | Allows PD, package, and TIA to be cascaded correctly | P1 |
| D-5 | Driver large-signal waveforms | Time-domain differential waveforms for representative PRBS/SSPR patterns, loaded with intended modulator interface, across swing/EQ/PVT | Captures edge rate, DCD, nonlinear settling, and ISI | P1 |
| D-6 | Driver output/interface model | Output impedance or S-parameters plus package/interconnect model; state bias and load reference | Allows the actual modulator load to be applied | P1 |
| D-7 | Tx jitter and eye characterization | Jitter component report, eye diagrams, bathtub curves, patterns, BER/extrapolation, clock conditions | Inputs horizontal eye closure | P1 |
| D-8 | End-to-end receiver BER data | BER vs OMA for clean and stressed eyes; PRBS31; TDEC/SEC, ER, wavelength, aggressor, and FEC state documented | Validates the analytic sensitivity and penalty model | P1 |
| D-9 | Equalizer capability data | Tap/CTLE/DFE tables, convergence logs, before/after pulse/eye data | Quantifies equalization gain and limitations | P2 |
| D-10 | CDR JTOL and clock-jitter data | Mask/table plus measured margin and test setup | Validates timing feasibility | P2 |
| D-11 | Behavioral simulation model | IBIS-AMI, Verilog-A/AMS, Python/MATLAB, encrypted circuit macro, or equivalent | Enables proposal-specific channel simulations | P2 |
| D-12 | PVT and Monte Carlo summary | Corner distributions for gain, BW, noise, jitter, offsets, and power | Converts typical performance into production margin | P2 |
| D-13 | OCI compliance or interoperability report | Test report against OCI MSA v1.0, including deviations | Reduces duplicate compliance work | P2 |

---

## 11. Minimum information for an initial link estimate

If a full response is not immediately available, the following subset is sufficient for a first-pass feasibility estimate:

1. Confirmed PHY/AFE block diagram and integration boundary (**A-1/A-2**).
2. Driver swing, intended electrical load/termination, loaded edge rate, Tx EQ, and jitter (**TX-2 through TX-6, TXE-1 through TXE-3, TXJ-1 through TXJ-3**).
3. TIA input capacitance assumption, transimpedance, complex frequency response, and input-referred noise with integration limits (**RX-2, RX-3, RX-5 through RX-7, RXN-1/RXN-2**).
4. Receiver CTLE/FFE/DFE capability (**EQ-1 through EQ-4**).
5. Raw/pre-FEC BER target and FEC placement (**BF-1/BF-2**).
6. Signaling-rate tolerance and available JTOL information (**CDR-2/CDR-3**).
7. TIA transfer/noise files and driver loaded waveforms (**D-2 through D-7**).

---

## 12. Vendor notes and identified deviations

Please use this section for architectural clarifications, unavailable/confidential items, alternate metrics, and known deviations from OCI MSA v1.0.

| Topic / ID | Vendor note |
|---|---|
|  |  |
|  |  |
|  |  |

