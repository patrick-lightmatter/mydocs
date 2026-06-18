# TIA Responses Data Consumption

## Overview
This document records the steps and results of processing the step and single-bit response (SBR) data of the TIA across multiple settings. The raw data was provided in CSV format under `temp/data/single_bit_response/` and `temp/data/step_response/`.

## Nonlinear Analysis Methodology
To evaluate the large-signal linearity of the TIA, we extracted key metrics from the step responses across varying input swing amplitudes (`Vswing`):

1. **Baseline & Steady-State Extraction**: For each response, the baseline ($Y_{init}$) is computed as the mean of the first 5% of samples (pre-step), and the steady state ($Y_{final}$) is the mean of the last 5% of samples (post-settling). The actual output step amplitude is defined as $\Delta Y = Y_{final} - Y_{init}$.
2. **Steady State Gain**: Calculated as `|Actual Step Amplitude| / Vswing`. This reveals gain compression (saturation) or expansion as the input stimulus grows.
3. **10-90% Rise/Fall Time**: The exact times crossing the 10% and 90% thresholds between baseline and steady state are found via linear interpolation. Increasing rise times at larger voltage swings can indicate slew-rate limiting (inability to charge parasitic capacitances quickly enough).
4. **Overshoot (%)**: Calculated as `(|Peak| - |Steady State|) / |Actual Step Amplitude| * 100`. Variations in overshoot percentage with amplitude often point to voltage-dependent nonlinear junction capacitances (e.g., $C_{bc}$ or $C_{je}$).

## Steps Taken
1. **Resampling**: Resampled the waveforms to put them on a UI/32 time scale, where UI = 1 / 106.25 GHz (~9.41 ps). The time axis is now plotted in Units of Interval (UI). *Note: Linear interpolation was used to prevent artificial ringing at the sharp edges of the input stimuli.*
2. **Impulse Response Extraction**: For the Step Responses, we computed the continuous derivative (`dy/dt`) to extract the impulse response. Both the step response and its derivative are plotted in the time domain.
3. **Frequency Domain Analysis**: We computed the Fast Fourier Transform (FFT) of the derivative of the Step Responses. The frequency domain results include:
   - Magnitude Response (dB)
   - Phase Response (rad)
   - Group Delay (ps)
   - Phase Delay (ps)
4. **Eye Diagrams**: Constructed PAM4 eye diagrams using the upsampled (UI/32) Single Bit Response to reflect realistic baud-rate signal properties, convolved with a sequence of 2000 random pseudo-symbols.
5. **Separated Polarity**: Responses were separated by positive steps (`isign=1`) and negative steps (`isign=-1`).
6. **Visualization**: Generated comprehensive PNG panels to encapsulate time domain, frequency domain, and eye diagram characteristics.
7. **Organization**: Results are grouped by configuration setting below.

## Code Repository
The Python scripts used to process the data and generate the plots are included in the `code/` subdirectory alongside this document:

- [`plot_advanced.py`](code/plot_advanced.py): Resamples waveforms, computes derivatives for impulse responses, and performs FFTs for frequency domain plots.
- [`plot_eyes.py`](code/plot_eyes.py): Constructs PAM4 eye diagrams from the Single Bit Responses.
- [`plot_eyes_ir.py`](code/plot_eyes_ir.py): Constructs PAM4 eye diagrams from the Step Responses (using the derivative and a Zero-Order Hold filter).
- [`plot_nonlin.py`](code/plot_nonlin.py): Extracts 10-90% rise time, steady-state gain, and overshoot for nonlinearity analysis.
- [`plot_normalized_steps.py`](code/plot_normalized_steps.py): Aligns step responses and normalizes them by the input `vswing` for overlay comparisons.
- [`plot_tia_responses.py`](code/plot_tia_responses.py): Initial script for plotting raw CSV data.

## Results
Below are the advanced response plots across the various configurations, organized on a per-node/setting basis.

---

## Configuration: Attenuation 10 (Main 0.7, Tamerolloff Bypass PD)

### Signal: `Ipd`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Ipd positive SBR Time](figures/single_bit_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd positive SBR Eye](figures/single_bit_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd positive Step Time](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_time.png)

*Step Response (Normalized Overlay)*:
![Ipd positive Step Norm](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd positive Step Nonlin](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd positive Step Freq](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd positive Step Eye](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Ipd negative SBR Time](figures/single_bit_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd negative SBR Eye](figures/single_bit_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd negative Step Time](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_time.png)

*Step Response (Normalized Overlay)*:
![Ipd negative Step Norm](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd negative Step Nonlin](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd negative Step Freq](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd negative Step Eye](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_eye.png)

### Signal: `Vbump`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Vbump positive SBR Time](figures/single_bit_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump positive SBR Eye](figures/single_bit_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump positive Step Time](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_time.png)

*Step Response (Normalized Overlay)*:
![Vbump positive Step Norm](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump positive Step Nonlin](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump positive Step Freq](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump positive Step Eye](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Vbump negative SBR Time](figures/single_bit_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump negative SBR Eye](figures/single_bit_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump negative Step Time](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_time.png)

*Step Response (Normalized Overlay)*:
![Vbump negative Step Norm](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump negative Step Nonlin](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump negative Step Freq](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump negative Step Eye](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative_eye.png)

---

## Configuration: Attenuation 11 (Tamerolloff)

### Signal: `Ipd`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Ipd positive SBR Time](figures/single_bit_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd positive SBR Eye](figures/single_bit_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd positive Step Time](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Ipd positive Step Norm](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd positive Step Nonlin](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd positive Step Freq](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd positive Step Eye](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Ipd negative SBR Time](figures/single_bit_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd negative SBR Eye](figures/single_bit_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd negative Step Time](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Ipd negative Step Norm](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd negative Step Nonlin](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd negative Step Freq](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd negative Step Eye](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative_eye.png)

### Signal: `Vbump`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Vbump positive SBR Time](figures/single_bit_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump positive SBR Eye](figures/single_bit_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump positive Step Time](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Vbump positive Step Norm](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump positive Step Nonlin](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump positive Step Freq](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump positive Step Eye](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Vbump negative SBR Time](figures/single_bit_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump negative SBR Eye](figures/single_bit_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump negative Step Time](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Vbump negative Step Norm](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump negative Step Nonlin](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump negative Step Freq](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump negative Step Eye](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative_eye.png)

---

## Configuration: Attenuation 11 (Xtmpeak)

### Signal: `Ipd`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Ipd positive SBR Time](figures/single_bit_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd positive SBR Eye](figures/single_bit_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd positive Step Time](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Ipd positive Step Norm](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd positive Step Nonlin](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd positive Step Freq](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd positive Step Eye](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Ipd negative SBR Time](figures/single_bit_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd negative SBR Eye](figures/single_bit_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd negative Step Time](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Ipd negative Step Norm](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd negative Step Nonlin](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd negative Step Freq](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd negative Step Eye](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative_eye.png)

### Signal: `Vbump`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Vbump positive SBR Time](figures/single_bit_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump positive SBR Eye](figures/single_bit_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump positive Step Time](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Vbump positive Step Norm](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump positive Step Nonlin](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump positive Step Freq](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump positive Step Eye](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Vbump negative SBR Time](figures/single_bit_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump negative SBR Eye](figures/single_bit_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump negative Step Time](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Vbump negative Step Norm](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump negative Step Nonlin](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump negative Step Freq](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump negative Step Eye](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative_eye.png)

---

## Configuration: Attenuation 12 (Tamerolloff)

### Signal: `Ipd`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Ipd positive SBR Time](figures/single_bit_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd positive SBR Eye](figures/single_bit_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd positive Step Time](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Ipd positive Step Norm](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd positive Step Nonlin](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd positive Step Freq](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd positive Step Eye](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Ipd negative SBR Time](figures/single_bit_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd negative SBR Eye](figures/single_bit_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd negative Step Time](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Ipd negative Step Norm](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd negative Step Nonlin](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd negative Step Freq](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd negative Step Eye](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative_eye.png)

### Signal: `Vbump`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Vbump positive SBR Time](figures/single_bit_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump positive SBR Eye](figures/single_bit_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump positive Step Time](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Vbump positive Step Norm](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump positive Step Nonlin](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump positive Step Freq](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump positive Step Eye](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Vbump negative SBR Time](figures/single_bit_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump negative SBR Eye](figures/single_bit_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump negative Step Time](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Vbump negative Step Norm](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump negative Step Nonlin](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump negative Step Freq](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump negative Step Eye](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative_eye.png)

---

## Configuration: Attenuation 12 (Xtmpeak)

### Signal: `Ipd`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Ipd positive SBR Time](figures/single_bit_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd positive SBR Eye](figures/single_bit_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd positive Step Time](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Ipd positive Step Norm](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd positive Step Nonlin](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd positive Step Freq](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd positive Step Eye](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Ipd negative SBR Time](figures/single_bit_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Ipd negative SBR Eye](figures/single_bit_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Ipd negative Step Time](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Ipd negative Step Norm](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Ipd negative Step Nonlin](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Ipd negative Step Freq](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Ipd negative Step Eye](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative_eye.png)

### Signal: `Vbump`

#### Polarity: Positive Steps

*Single Bit Response (Time Domain)*:
![Vbump positive SBR Time](figures/single_bit_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump positive SBR Eye](figures/single_bit_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump positive Step Time](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive_time.png)

*Step Response (Normalized Overlay)*:
![Vbump positive Step Norm](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump positive Step Nonlin](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump positive Step Freq](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump positive Step Eye](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive_eye.png)

#### Polarity: Negative Steps

*Single Bit Response (Time Domain)*:
![Vbump negative SBR Time](figures/single_bit_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_time.png)

*Single Bit Response (Eye Diagram)*:
![Vbump negative SBR Eye](figures/single_bit_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_eye.png)

*Step Response & Derived Impulse Response (Time Domain)*:
![Vbump negative Step Time](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_time.png)

*Step Response (Normalized Overlay)*:
![Vbump negative Step Norm](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_norm.png)

*Step Response (Non-linearity Analysis)*:
![Vbump negative Step Nonlin](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_nonlin.png)

*Derived Impulse Response (Frequency Domain)*:
![Vbump negative Step Freq](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump negative Step Eye](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_eye.png)

