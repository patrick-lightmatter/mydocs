# Astera Labs OCI Gen1 PHY — Succinct Email Summary

**Purpose:** Condensed, email-friendly version of the full `OCI_Gen1_PHY_AFE_Questionnaire.md`,
for an initial outreach to Astera Labs. Follows up on Taylor Groves' Slack draft (2026-08-11),
verified against Section 11 ("Minimum information for an initial link estimate") of the detailed
questionnaire. The larger questionnaire can be shared as a follow-up once engagement progresses.

---

Given we won't begin with an IBIS model, we'd begin modeling using some of the material below.

- **Receiver architecture:** analog slicer-based vs. ADC/DSP-based, and sampling rate/resolution if the latter.
- **Block diagram + integration boundary;** confirm which blocks are integrated (SerDes, driver, TIA, CDR, FEC, deskew) vs. external (PD, modulator, laser, mux/demux).
- **Driver output swing** and intended modulator load Vppd range, terminated line vs. direct capacitive attach, output impedance/termination.
- **Loaded driver edge response** 20–80% rise/fall under the modulator load.
- **Tx equalization capability:** FIR/FFE architecture, tap count/placement, coefficient range and resolution.
- **Tx jitter:** RJ, DJ decomposition, and TJ with the BER at which it's quoted.
- **TIA input capacitance** assumption, transimpedance gain, gain-control (AGC) range, and PD interface assumptions.
- **TIA complex frequency response,** magnitude and phase/group delay to ≥1.5× f3dB, per gain/EQ setting.
- **Input-referred noise** with integration limits — RMS and spectral density.
- **Rx equalization:** CTLE range, FFE/DFE presence and tap counts, and ordering in the signal path.
- **BER/FEC and timing assumptions:** pre-FEC BER target, FEC location and code, ppm tolerance, and JTOL mask.
- **Data files** (Touchstone/CSV for TIA response and noise, driver waveforms) are the preferred format.

---

## Notes on changes vs. Taylor's original draft

1. Added a leading bullet on **receiver architecture** (analog slicer vs. ADC/DSP) — highest-leverage
   question since it determines which downstream noise/quantization model applies (maps to A-3).
2. Broadened "FIR architecture" to **"FIR/FFE architecture"** to match TXE-1, which allows for
   FFE or analog peaking, not just a pure FIR implementation.
3. Made **AGC/gain-control range** explicit on the TIA bullet (RX-4) rather than leaving it implied
   by "per gain/EQ setting".

## Traceability to the full questionnaire

| Summary bullet | Full questionnaire IDs |
|---|---|
| Receiver architecture | A-3 |
| Block diagram + integration boundary | A-1, A-2 |
| Driver output swing / load / termination | TX-2, TX-3, TX-4 |
| Loaded driver edge response | TX-6 |
| Tx equalization capability | TXE-1, TXE-2, TXE-3 |
| Tx jitter | TXJ-1, TXJ-2, TXJ-3 |
| TIA input capacitance / gain / AGC / PD interface | RX-1, RX-2, RX-3, RX-4 |
| TIA complex frequency response | RX-5, RX-7 |
| Input-referred noise | RXN-1, RXN-2 |
| Rx equalization | EQ-1, EQ-2, EQ-3, EQ-4 |
| BER/FEC and timing assumptions | BF-1, BF-2, BF-3, CDR-2, CDR-3 |
| Data files | D-2, D-3, D-5 |
