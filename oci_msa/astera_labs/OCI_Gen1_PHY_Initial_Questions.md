# Astera Labs OCI Gen1 PHY — Initial Technical Questions

**Context:** We are evaluating your custom OCI Gen1 PHY with integrated driver and TIA for a proposal built around the *200G Optical Compute Interconnect (OCI) Line Interface Specification, Version 1.0* (53.125 GBd NRZ, four wavelengths per 212.5 Gb/s stream). To put together a first-pass link performance estimate, we would appreciate your help with the questions below.

A few notes up front:

- Typical values or bounded ranges are perfectly fine at this stage — we do not need guaranteed corner data yet.
- If any item is confidential, a pass/fail statement or "available under NDA" is a useful answer.
- We maintain a more detailed parameter-level questionnaire with test conditions and data-format requests; we would propose exchanging that as our engagement progresses.

---

## 1. Device overview

1. Could you share a block diagram of the PHY showing the Tx path, driver, TIA, equalizers, CDR, and management interfaces?
2. What is on-chip versus external? In particular, we assume the photodiode, optical modulator, laser, and mux/demux are external to your device — please correct us if that is wrong.
3. Is the receiver analog (slicer-based) or ADC/DSP-based?
4. What process technology / node is the PHY implemented in?
5. What is the approximate die area of the PHY (per-lane macro and total, including shared PLLs/control)?
6. What is the silicon status (simulation, first silicon, characterized, production) and sample availability?

## 2. Transmitter driver

7. What differential output swing range can the driver deliver, and what modulator type / electrical load is it designed to drive (terminated line vs. direct capacitive attachment)?
8. What are the output impedance and termination assumptions at the driver-to-modulator interface?
9. What 20–80% rise/fall time does the driver achieve under its intended load?
10. What Tx equalization is available (FIR tap count, coefficient ranges)?
11. What is the Tx jitter performance (RJ rms, DJ, total jitter, and the BER at which TJ is quoted)?

## 3. Receiver TIA and AFE

12. What total input capacitance (photodiode + package + pad) is the TIA designed for?
13. What are the transimpedance gain and gain-control (AGC) range?
14. What is the TIA bandwidth, and can you share the frequency response including phase / group delay?
15. What is the input-referred noise (rms), and over what integration bandwidth is it quoted?
16. What is the maximum input (overload) the receiver handles without BER degradation? The OCI spec allows received OMA up to −1 dBm per channel.
17. What receiver equalization is available (CTLE range, FFE/DFE presence and tap counts)?

## 4. Clocking and BER

18. What signaling-rate (ppm) offset does the CDR tolerate, and what jitter-tolerance mask is the receiver characterized against?
19. What pre-FEC BER does the PHY operate at — both the expected operating pre-FEC BER and the correction-threshold pre-FEC BER of the FEC you assume? (The OCI spec's compliance points are defined at 2.4×10⁻⁴.)
20. Where does FEC sit in your architecture (internal to the PHY, host-side, bypassable), and what code is assumed?

## 5. Power

21. What is the power of the solution in pJ/bit — ideally split by driver, TIA/AFE, and total PHY per lane, plus any shared overhead?

## 6. Features we would find valuable

These are not blocking for the link estimate, but they would tell us a lot about bring-up and debug:

22. Is there an Rx eye monitor / on-chip eye scan? If so, can it run non-destructively on live traffic?
23. What loopback modes are supported (host-side, line-side)?
24. Are per-lane PRBS generators/checkers and BER margining available?
25. What telemetry is exposed (EQ/AGC state readback, pre-FEC BER counters, temperature)?

## 7. Models and data

26. Are IBIS-AMI or other behavioral simulation models available for the Tx and Rx paths, and under what terms?
27. Where shareable, TIA frequency-response and noise data plus driver edge/eye data would let us anchor the link model directly to your silicon — even summary plots are helpful at this stage.

---

We appreciate any subset of the above you can answer now; partial answers are more useful than delayed complete ones. We are happy to set up a call to walk through the list, and to share our link-budget assumptions in return.
