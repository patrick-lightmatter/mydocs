# TIA Responses Data Consumption

## Overview
This document records the steps and results of generating plots from the step and single-bit response data of the TIA across multiple settings. The raw data was provided in CSV format under:
- `temp/data/single_bit_response/`
- `temp/data/step_response/`

## Steps Taken
1. **Identified Data Sources**: Examined the structure of the `temp/data` directories which contain CSV files with sweep results for different TIA settings (e.g., `attn10_main0p7_tamerolloff`, `attn11_tamerolloff`, etc.).
2. **Created Plotting Script**: Wrote a Python script (`scripts/plot_tia_responses.py`) to systematically read and plot this data.
   - Utilized `pandas` for CSV parsing and data extraction.
   - Utilized `matplotlib` to generate the step and single-bit response waveforms.
3. **Data Type Coercion**: Handled mixed-type column values that caused plotting to fail initially. Implemented `pd.to_numeric(df[col], errors='coerce')` to clean non-numeric artifacts safely.
4. **Separated Polarity**: Updated the script to split the responses into two plots per CSV—one showing positive steps (`isign=1`) and one showing negative steps (`isign=-1`)—resulting in 4 plots per configuration (Ipd positive/negative and Vbump positive/negative).
5. **Generated Figures**: Executed the script, successfully generating the separated plots for each configuration.
6. **Organized Results**: Consolidated all generated PNG figures into the `figures/` directory located alongside this document.

## Results
Below are the generated response plots for both Single Bit and Step responses across the various configurations, separated by positive and negative steps.

### Single Bit Responses

#### Attenuation 10 (Main 0.7, Tamerolloff Bypass PD)
**Ipd**
![Ipd Positive](figures/single_bit_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive.png)
![Ipd Negative](figures/single_bit_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative.png)
**Vbump**
![Vbump Positive](figures/single_bit_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive.png)
![Vbump Negative](figures/single_bit_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative.png)

#### Attenuation 11 (Tamerolloff)
**Ipd**
![Ipd Positive](figures/single_bit_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive.png)
![Ipd Negative](figures/single_bit_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/single_bit_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive.png)
![Vbump Negative](figures/single_bit_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative.png)

#### Attenuation 11 (Xtmpeak)
**Ipd**
![Ipd Positive](figures/single_bit_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive.png)
![Ipd Negative](figures/single_bit_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/single_bit_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive.png)
![Vbump Negative](figures/single_bit_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative.png)

#### Attenuation 12 (Tamerolloff)
**Ipd**
![Ipd Positive](figures/single_bit_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive.png)
![Ipd Negative](figures/single_bit_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/single_bit_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive.png)
![Vbump Negative](figures/single_bit_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative.png)

#### Attenuation 12 (Xtmpeak)
**Ipd**
![Ipd Positive](figures/single_bit_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive.png)
![Ipd Negative](figures/single_bit_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/single_bit_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive.png)
![Vbump Negative](figures/single_bit_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative.png)

---

### Step Responses

#### Attenuation 10 (Main 0.7, Tamerolloff Bypass PD)
**Ipd**
![Ipd Positive](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_positive.png)
![Ipd Negative](figures/step_response/attn10_main0p7_tamerolloff/Ipd_attn10_main0p7_tamerolloff_sweep_bypassPD_negative.png)
**Vbump**
![Vbump Positive](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_positive.png)
![Vbump Negative](figures/step_response/attn10_main0p7_tamerolloff/Vbump_attn10_main0p7_tamerolloff_sweep_bypassPD_negative.png)

#### Attenuation 11 (Tamerolloff)
**Ipd**
![Ipd Positive](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_positive.png)
![Ipd Negative](figures/step_response/attn11_tamerolloff/Ipd_attn11_tamerolloff_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_positive.png)
![Vbump Negative](figures/step_response/attn11_tamerolloff/Vbump_attn11_tamerolloff_sweep_negative.png)

#### Attenuation 11 (Xtmpeak)
**Ipd**
![Ipd Positive](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_positive.png)
![Ipd Negative](figures/step_response/attn11_xtmpeak/Ipd_attn11_xtmpeak_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_positive.png)
![Vbump Negative](figures/step_response/attn11_xtmpeak/Vbump_attn11_xtmpeak_sweep_negative.png)

#### Attenuation 12 (Tamerolloff)
**Ipd**
![Ipd Positive](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_positive.png)
![Ipd Negative](figures/step_response/attn12_tamerolloff/Ipd_attn12_tamerolloff_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_positive.png)
![Vbump Negative](figures/step_response/attn12_tamerolloff/Vbump_attn12_tamerolloff_sweep_negative.png)

#### Attenuation 12 (Xtmpeak)
**Ipd**
![Ipd Positive](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_positive.png)
![Ipd Negative](figures/step_response/attn12_xtmpeak/Ipd_attn12_xtmpeak_sweep_negative.png)
**Vbump**
![Vbump Positive](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_positive.png)
![Vbump Negative](figures/step_response/attn12_xtmpeak/Vbump_attn12_xtmpeak_sweep_negative.png)