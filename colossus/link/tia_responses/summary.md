# TIA Responses Data Consumption

## Overview
This document records the steps and results of processing the step and single-bit response (SBR) data of the TIA across multiple settings. The raw data was provided in CSV format under `temp/data/single_bit_response/` and `temp/data/step_response/`.

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

*Derived Impulse Response (Frequency Domain)*:
![Vbump negative Step Freq](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_freq.png)

*Step Response Derived IR (Eye Diagram)*:
![Vbump negative Step Eye](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative_eye.png)

