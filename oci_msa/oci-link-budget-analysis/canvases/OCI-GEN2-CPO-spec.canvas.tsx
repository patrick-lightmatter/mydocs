import {
  BarChart,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

/**
 * OCI GEN2 CPO transceiver at 106.25 GBd NRZ — 1e-12 link budget and proposed device spec.
 * GEN1 = 53.125 GBd NRZ (OCI MSA rate); its CPO analysis is kept as the rate-scaling baseline.
 * Architecture per the block diagram (OCI-GEN2 Simplified.png): analog SerDes, 3-slice
 * output-summed Tx FIR DAC, microbump EIC-PIC attach, TIA in the SerDes AFE. Rx EQ is CTLE
 * only — DFE is not supported. All numbers from the 106.25 GBd analysis run (pulse-response
 * simulation on measured Ocelot ADFET TT tables; hypothetical scaled TIA where noted).
 */

const STACK_COMPARE: Array<{
  line: string;
  gen1: string;
  gen2: string;
  why: string;
  tone?: "success" | "danger" | "warning" | "info" | "neutral";
}> = [
  {
    line: "ER / shot + RIN (Q-solve)",
    gen1: "0.52 (0.11 + 0.41)",
    gen2: "0.82",
    why: "RIN −138 dB/Hz now integrates over BWn 64 GHz vs 22 GHz (RIN-only 0.66, shot 0.15)",
    tone: "warning",
  },
  {
    line: "MPI / coherent crosstalk",
    gen1: "0.21",
    gen2: "0.21",
    why: "Rate-independent in OMA domain; −24 dB ends, ER 4.5 dB kept",
  },
  {
    line: "ISI + EQ net",
    gen1: "1.86 (29.3 GHz TIA = 0.55× baud)",
    gen2: "1.15 (58 GHz TIA = 0.55× baud, incl. 25 fF bump)",
    why: "Comparable ONLY because GEN2 assumes a new 0.55×-baud TIA; the measured TIA gives 7.2 dB",
    tone: "info",
  },
  { line: "Chromatic dispersion", gen1: "0.01", gen2: "0.04", why: "Scales ~baud²; pulse-sim gives 0.013, 0.04 booked" },
  {
    line: "Jitter / timing",
    gen1: "0.73",
    gen2: "0.95",
    why: "TJ budget similar in UI (0.35) but UI halves: RJ 141 fs rms, DJ 1.32 ps — see jitter row in spec",
    tone: "warning",
  },
  { line: "Inter-channel crosstalk", gen1: "0.36", gen2: "0.36", why: "MRR demux isolation 20 dB assumption kept" },
  { line: "Threshold offset", gen1: "0.21", gen2: "0.21", why: "Analog slicer, 2.5% offset-cal kept" },
  { line: "Dark current", gen1: "0.00", gen2: "0.00", why: "Negligible" },
];

export default function OciGen2CpoSpec() {
  return (
    <Stack gap={20} style={{ maxWidth: 1000, margin: "0 auto", padding: 16 }}>
      <Stack gap={4}>
        <H1>OCI GEN2 CPO at 106.25 GBd NRZ — feasibility, EQ calculus, proposed spec</H1>
        <Text tone="secondary">
          GEN2 = 106.25 GBd NRZ (UI 9.412 ps, Nyquist 53.125 GHz); GEN1 = 53.125 GBd NRZ kept as
          the rate-scaling baseline. Bottom-up 1e-12 budget (Q = 7.035, OMA domain, per DWDM
          channel). Analog SerDes, CTLE-only receiver — DFE not supported. Headline: no measured
          TIA setting closes at this rate; closure requires a new 53–64 GHz TIA class.
        </Text>
      </Stack>

      <Grid columns={4} gap={16}>
        <Stat value="0 of 152" label="Measured TIA settings that close at 106 GBd" tone="danger" />
        <Stat value="53–64 GHz, ≤4.4 µA" label="Required TIA class (0.5–0.6× baud)" tone="warning" />
        <Stat value="3.74 dB" label="Penalty stack with required TIA (typ Tx)" />
        <Stat value="+1.7 dB" label="Margin @ Tx OMA −3.5 dBm (required TIA)" tone="info" />
      </Grid>

      <Stack gap={8}>
        <H2>1 · Architecture (from the block diagram) — unchanged, limits tightened</H2>
        <Text tone="secondary">
          SerDes Tx drives a 3-branch analog FIR — pre / main / post limiting driver slices with
          two 1-UI (now 9.412 ps) delay elements — summing at a common output node, through a
          microbump to the MRM (laser from the ELS), mux / 500 m fiber / demux, PD, second
          microbump, TIA in the SerDes Rx AFE. Each slice is nonlinear (limiting) by itself; the
          sum of the three two-level waveforms is a stepped DAC waveform, so slice nonlinearity
          does not degrade tap accuracy for NRZ. Rx EQ is CTLE only.
        </Text>
        <Table
          headers={["Interface", "Model / limit", "Impact at the new 53.125 GHz Nyquist"]}
          rows={[
            [
              "EIC-PIC microbump (Tx and Rx)",
              "Was 30–50 fF; now ≤25 fF, ≤30 pH",
              "25 fF → RC pole 127 GHz, 0.70 dB droop at Nyquist, +0.22 dB equalized-ISI cost (included). 50 fF would cost +0.71 dB — the old budget is no longer free",
            ],
            [
              "Package trace (what CPO avoids)",
              "Caribou_EOE/Package/TL_TX_64G.s4p, TL_RX_64G.s4p",
              "1.61 dB (Tx) / 0.72 dB (Rx) differential IL at 53.1 GHz, plus reflections — eliminated",
            ],
            [
              "Optical channel",
              "500 m SMF, 2.5 dB flat IL, CD −0.9…+1.7 ps/nm",
              "CD penalty scales ~baud²: 0.01 → 0.04 dB booked (pulse-sim 0.013 dB) — still small",
            ],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>2 · TIA feasibility — the central question at 106.25 GBd</H2>
        <Text tone="secondary">
          All 152 measured settings (Ocelot ADFET TT corner) were re-scanned at 106.25 GBd with
          per-setting CTLE optimization. The table tops out at 46.4 GHz — 0.44× baud, and even
          those settings fail on phase, not magnitude: they are flat to 0.2 dB but carry 12.5 ps
          of group-delay ripple over 2–40 GHz (1.3 UI), which produces an h₋₁ ≈ 0.48 pre-cursor
          that no CTLE can remove. The GEN1 design point (29.3 GHz) is 0.28× baud at this rate.
        </Text>
        <Table
          headers={["Receiver", "BW (× baud)", "iₙ rms", "Floor", "ISI + EQ net (CTLE-only, typ Tx)", "Verdict"]}
          rows={[
            [
              "GEN1 design pt 12211111",
              "29.3 GHz (0.28×)",
              "3.17 µA",
              "−12.93 dBm",
              "7.25 dB (CTLE z=20G/p=85G, noise ×1.31)",
              "Fails — jitter eye closed",
            ],
            [
              "Best measured 06131100",
              "46.4 GHz (0.44×)",
              "6.75 µA",
              "−9.65 dBm",
              "6.06 dB (group-delay-ripple pre-cursor uncorrectable by CTLE)",
              "Fails — jitter eye closed",
            ],
            [
              "Best of full 152-scan",
              "—",
              "—",
              "—",
              "≥ 6.2 dB every setting",
              "0 of 152 close; 57 of 60 simulated have the eye closed outright at ±TJ/2, best margin −19 dB",
            ],
            [
              "Required new TIA (hypothetical, Butterworth-2 58 GHz)",
              "58 GHz (0.55×)",
              "4.5 µA target",
              "−11.41 dBm",
              "1.15 dB (CTLE z≈37G/p≈62G, ~2–3 dB peaking, noise ×1.0)",
              "Closes, +1.7 dB margin",
            ],
          ]}
          rowTone={["danger", "danger", "danger", "success"]}
          columnAlign={["left", "right", "right", "right", "left", "left"]}
        />
        <Callout tone="danger" title="Honest verdict: existing silicon does not scale to 106 GBd">
          A regression of iₙ² against noise-bandwidth integrals across all 152 settings says this
          TIA family is f²-noise dominated (f²-only fit R² = 0.87 vs white-only 0.59). Lecture-4
          scaling of the GEN1 design point to 58 GHz then gives iₙ = 17 µA (BW^1.5 law) → floor
          −5.6 dBm — unclosable at any plausible Tx OMA. Even the optimistic pure-white √BW
          scaling gives 5.4 µA → floor −10.6 dBm (+2.3 dB vs GEN1, the top of the expected
          1.5–2.3 dB window; BWn grows ×2.9, not ×2). Closing at Tx OMA −3.5 dBm requires
          iₙ ≤ 4.4 µA rms over a 64 GHz noise bandwidth (≤17 pA/√Hz average density) for
          ≈+1.8 dB margin with the 25 fF microbump charged to the ISI line (+2.0 dB needs
          ≈4.2 µA) — a purpose-built input stage (lower C_T, higher f_T), consistent with
          published 100 GBd-class TIAs but not derivable from this design.
        </Callout>
      </Stack>

      <Stack gap={8}>
        <H2>3 · Tx corners and ISI/EQ at the new rate (required-TIA receiver)</H2>
        <Text tone="secondary">
          The old 10/12/17 ps transition corners are 1.1–1.8 UI at 106 GBd — meaningless. New
          corners are fractions of the 9.412 ps UI. Full chain: 2-pole Tx × 25 fF microbump ×
          58 GHz Butterworth-2 TIA, CTLE-only, net of noise enhancement.
        </Text>
        <Table
          headers={["Tx corner (20–80%)", "Implied poles", "h₋₁ / h₊₁ (before EQ)", "Unequalized PP", "CTLE-only net"]}
          rows={[
            ["Fast, 0.35 UI = 3.3 ps", "2 × 105 GHz (cascade 67 GHz)", "0.04 / 0.07", "0.59 dB", "0.82 dB"],
            ["Typical, 0.45 UI = 4.2 ps", "2 × 82 GHz (cascade 53 GHz)", "0.06 / 0.12", "0.91 dB", "1.15 dB"],
            ["Max, 0.60 UI = 5.6 ps", "2 × 61 GHz (cascade 39 GHz)", "0.09 / 0.19", "1.46 dB", "1.70 dB"],
          ]}
          columnAlign={["left", "left", "right", "right", "right"]}
          rowTone={[undefined, "info", "warning"]}
        />
        <Text tone="tertiary" size="small">
          Achievability: a 4.2 ps 20–80% edge at ~1.2 Vppd (Typ_Txdrv_NL.csv driver class) means
          ~170 V/ns slew and two ~82 GHz poles — driver AND MRM electro-optic each need
          ~60–80 GHz. Published detuned MRMs reach 50–77 GHz EO; the repos contain no 106 GBd MRM
          data, so the typical corner is an assumption. Sensitivity: each corner step
          (0.45 → 0.60 UI) costs 0.55 dB — even the 0.60 UI corner still closes (+1.1 dB margin).
        </Text>
        <Grid columns={2} gap={16}>
          <Card>
            <CardHeader>Slice-DAC FIR at 9.412 ps tap spacing</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text size="small">
                  <Text as="span" weight="semibold">3 taps still sufficient:</Text> with a
                  0.55×-baud receiver, h₊₂ ≤ 0.01 of cursor and a 4th tap buys 0.00 dB (checked
                  on the worst measured-TIA chain too). At the typical corner the optimizer drives
                  the taps to zero — the peak-constrained slice DAC trades OMA for eye ~1:1 on
                  this short channel. The FIR's value is the slow-Tx corner, MRM peaking
                  pre-compensation, and TDEC shaping.
                </Text>
                <Text size="small">
                  <Text as="span" weight="semibold">Tolerances halve in ps:</Text> tap spacing
                  9.412 ps ± 0.47 ps (±5% UI); slice rise/fall mismatch ≤ 0.47 ps (DCD ≤ 0.05 UI,
                  inside the DJ budget). Weight step ≤ 0.02 of full scale (main 32–64 units,
                  3-bit pre, 4-bit post) keeps quantization ISI &lt; 0.1 dB.
                </Text>
              </Stack>
            </CardBody>
          </Card>
          <Card>
            <CardHeader>Rx AFE: CTLE-only (DFE not supported)</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text size="small">
                  <Text as="span" weight="semibold">With the required TIA:</Text> zero ≈ 37 GHz,
                  two poles 62–74 GHz, 2–4 dB peaking, noise enhancement ≈ 1.0× — cheap and
                  effective.
                </Text>
                <Text size="small">
                  <Text as="span" weight="semibold">With the 0.28×-baud measured TIA:</Text> the
                  CTLE would need &gt;10 dB boost at 53 GHz Nyquist; the best found (zero 20 GHz,
                  poles 85 GHz) still leaves 6.1 dB of ISI while multiplying noise ×1.31 — the
                  boost erases its own benefit. CTLE cannot rescue a receiver at a quarter of
                  the baud rate.
                </Text>
                <Text size="small">
                  <Text as="span" weight="semibold">TDEC expectation:</Text> 1.11 dB typical /
                  1.77 dB max corner through the 53.125 GHz BT4 reference receiver → spec
                  ≤ 1.8 dB.
                </Text>
              </Stack>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      <Stack gap={8}>
        <H2>4 · Penalty stack — 53.125 GBd (GEN1) vs 106.25 GBd (GEN2) rate scaling</H2>
        <Table
          headers={["Penalty line", "GEN1 @ 53.125 GBd (dB)", "GEN2 @ 106.25 GBd (dB)", "What changed"]}
          rows={STACK_COMPARE.map((r) => [
            <Text as="span" weight="medium">{r.line}</Text>,
            r.gen1,
            r.gen2,
            <Text as="span" size="small" tone="secondary">{r.why}</Text>,
          ]).concat([
            [
              <Text as="span" weight="bold">Total</Text>,
              <Text as="span" weight="bold">3.90</Text>,
              <Text as="span" weight="bold">3.74</Text>,
              <Text as="span" size="small" tone="secondary">
                Similar totals — but the GEN2 floor is 1.5 dB worse (−11.41 vs −12.93 dBm), so
                required OMA rises from −9.03 to −7.67 dBm
              </Text>,
            ],
          ])}
          rowTone={STACK_COMPARE.map((r) => r.tone).concat([undefined])}
          columnAlign={["left", "right", "right", "left"]}
        />
        <BarChart
          categories={[
            "ER/shot+RIN",
            "MPI",
            "ISI+EQ",
            "CD",
            "Jitter",
            "Xtalk",
            "Threshold",
          ]}
          series={[
            { name: "GEN1 @ 53.125 GBd (measured 29.3 GHz TIA)", data: [0.52, 0.21, 1.86, 0.01, 0.73, 0.36, 0.21], tone: "neutral" },
            { name: "GEN2 @ 106.25 GBd (required 58 GHz TIA)", data: [0.82, 0.21, 1.15, 0.04, 0.95, 0.36, 0.21], tone: "info" },
          ]}
          horizontal
          height={300}
          valueSuffix=" dB"
        />
        <Text tone="tertiary" size="small">
          Per-line penalties (dB, optical OMA), typical Tx corner, CTLE-only, BER 1e-12. Source:
          pulse-response budget runs at each rate. Both columns assume a 0.55×-baud TIA — measured
          silicon at 53 GBd, hypothetical at 106 GBd. The real rate cost hides in the floor
          (+1.5 dB) and in the Tx/TIA component specs, not in the stack total.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>5 · Proposed GEN2 device spec at 106.25 GBd NRZ</H2>
        <Table
          headers={["Parameter", "Proposed value", "Basis"]}
          rows={[
            ["Signaling", "106.25 GBd NRZ, UI 9.412 ps", "GEN2 rate (2× the GEN1 / OCI MSA rate)"],
            ["Tx OMA, each channel (min)", "−3.5 dBm", "Closure at +1.7 dB margin with required TIA; ~1.2 Vppd driver class supports it if MRM efficiency holds at 106 GBd"],
            ["Extinction ratio", "4.5 dB target (4.0 min)", "Keeps MPI at 0.21 dB; higher ER costs OMA at this swing"],
            ["TDEC", "≤ 1.8 dB", "Computed 1.11 (typ) / 1.77 (max corner) through 53.125 GHz BT4 reference Rx"],
            ["Tx transition time (20–80%)", "≤ 5.6 ps (0.60 UI) hard max; 4.2 ps (0.45 UI) target", "0.60 UI still closes (+1.1 dB); requires driver + MRM EO poles ≥ ~61 GHz each — MRM EO bandwidth is an open assumption"],
            ["Tx FIR", "3 taps: 1 pre + main + 1 post, binary-weighted output-summed slices", "h₊₂ ≤ 0.01 with a 0.55×-baud Rx; 4th tap buys 0.00 dB"],
            ["FIR tap ranges / resolution", "pre 0…−0.10, post 0…−0.25 of Σ|w|; step ≤ 0.02 (main 32–64u, pre 3-bit, post 4-bit)", "Taps ≈ 0 at typ corner; range reserved for slow corner and MRM peaking"],
            ["FIR tap spacing", "9.412 ps ± 0.47 ps (±5% UI)", "Residual mis-cancellation ≤ 0.01 of cursor"],
            ["Slice rise/fall mismatch", "≤ 0.47 ps (DCD ≤ 0.05 UI)", "Allocated inside the DJ budget"],
            ["Rx TIA (NEW SILICON REQUIRED)", "f3dB 50–64 GHz, iₙ ≤ 4.4 µA rms, GD ripple ≤ 3 ps — full pass criteria in §7 below", "0 of 152 measured settings close; complete designer-ready requirements and verification recipe in section 7"],
            ["Rx CTLE", "zero ~37 GHz, 2 poles 62–74 GHz, 2–4 dB peaking, noise-enhancement ≤ 0.2 dB", "Optimum vs 58 GHz Butterworth-2 TIA model"],
            ["Rx DFE", "Not supported", "Architecture decision; post-cursor controlled by Tx transition-time limit + CTLE"],
            ["End reflectance (Tx & Rx)", "≤ −24 dB", "MPI 0.21 dB (D=0.5, 4 connectors at −35 dB)"],
            ["Microbump + pad (each interface)", "≤ 25 fF, ≤ 30 pH", "0.70 dB droop at Nyquist, +0.22 dB equalized cost (booked); 50 fF would cost +0.71 dB"],
            ["Jitter budget", "RJ ≤ 0.015 UI rms = 141 fs, DJ ≤ 0.14 UI = 1.32 ps (incl. 0.05 DCD) → TJ@1e-12 = 0.351 UI = 3.30 ps", "Dual-Dirac at Q = 7.035; 113 fs (0.012 UI carryover) judged beyond analog-CDR state of art at 106G"],
            ["Link", "2.5 dB IL, 500 m SMF, bidirectional, 4 conn ≤ −35 dB", "Unchanged from OCI v1.0"],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>6 · Closure at BER 1e-12, 106.25 GBd (Tx OMA −3.5 dBm − 2.5 dB IL = −6.0 dBm at Rx)</H2>
        <Table
          headers={["Case", "Floor", "Stack", "Required OMA", "Margin"]}
          rows={[
            ["Required TIA (58 GHz, 4.5 µA), fast Tx 0.35 UI", "−11.41 dBm", "3.41 dB", "−8.00 dBm", "+2.00 dB"],
            ["Required TIA, typical Tx 0.45 UI — baseline", "−11.41 dBm", "3.74 dB", "−7.67 dBm", "+1.67 dB"],
            ["Required TIA, max Tx 0.60 UI", "−11.41 dBm", "4.29 dB", "−7.12 dBm", "+1.12 dB"],
            ["White-scaled existing design (5.4 µA)", "−10.60 dBm", "3.71 dB", "−6.89 dBm", "+0.89 dB"],
            ["f²-scaled existing design (17 µA, fit-favored)", "−5.63 dBm", "3.41 dB", "−2.22 dBm", "−3.78 dB — fails"],
            ["Any measured TIA setting (best of 152)", "−12.93 dBm", "ISI ≥ 6.2 dB, jitter eye closed", "—", "Does not close"],
          ]}
          rowTone={["success", "success", "success", "warning", "danger", "danger"]}
          columnAlign={["left", "right", "right", "right", "right"]}
        />
        <Text tone="tertiary" size="small">
          Required OMA = analytic floor (2Q·iₙ/R at Q = 7.035, R = 0.876 A/W) + penalty stack; Tx
          eye closure lives inside the ISI line (no separate TDEC subtraction). GEN1 baseline for
          reference: floor −12.93 dBm, stack 3.90 dB, margin +3.03 dB at the same Tx OMA. The
          GEN2 margin is real but thin: it presumes a TIA that does not exist in the measured
          family and a ≤5.6 ps Tx edge. Raising Tx OMA to −1.5 dBm buys 2 dB — the only
          system-level knob if either assumption slips.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>7 · GEN2 TIA requirements — pass criteria (designer-ready, verifiable)</H2>
        <Text tone="secondary">
          What a TIA must measure to pass GEN2 (106.25 GBd NRZ, CTLE-only, 1e-12). Every line is
          tied to the budget above; the verification recipe at the end runs on the same data
          format as the 152-setting tables (differential transfer function + output noise).
          Assumed input node: PD 30–40 fF (no PD capacitance data in the repos — input
          assumption, 100G-class waveguide PD) + 25 fF microbump + ~10 fF pad/ESD ≈ 65–75 fF.
        </Text>
        <Table
          headers={["Parameter", "Requirement", "Basis"]}
          rows={[
            [
              <Text as="span" weight="medium">Bandwidth (f3dB, differential)</Text>,
              "50–64 GHz window; 53–58 GHz target (0.50–0.55× baud)",
              "Total sensitivity (floor + ISI+EQ + RIN) is flat at −8.66 dBm across 50–64 GHz: below 50 GHz ISI grows faster than noise saved; above 64 GHz noise grows (~0.2 dB floor / 6 GHz) for <0.3 dB ISI benefit. Excess BW is pure noise cost",
            ],
            [
              <Text as="span" weight="medium">Input-referred noise, total</Text>,
              "≤ 4.4 µA rms integrated over the measured noise bandwidth (≈64 GHz for the reference response); ≤ 7.0 µA absolute fail line",
              "4.4 µA → floor −11.4 dBm → ≈+1.8 dB margin at Tx OMA −3.5 dBm (microbump charged; +2.0 dB needs ≈4.2 µA); 7.0 µA → zero margin. Derived by Q-solve inversion of the full stack",
            ],
            [
              <Text as="span" weight="medium">Noise density (shape mask)</Text>,
              "≤ 17 pA/√Hz band average; ≤ 20 pA/√Hz spot at any frequency 1–53 GHz; noise measured to ≥ 80 GHz before integrating rms",
              "With the required BW class the optimal CTLE is mild (≤3 dB peaking, poles ≥60 GHz) — computed post-CTLE enhancement of an f²-dominated spectrum is ≤0 dB vs equal-rms white. The f² danger is rms inflation with bandwidth (why the measured family can't scale), so the spec forces full-band rms + a spot ceiling rather than a separate CTLE allowance",
            ],
            [
              <Text as="span" weight="medium">Magnitude peaking</Text>,
              "≤ 1.0 dB over DC–53 GHz, monotonic rolloff above the peak",
              "2nd-order sweep at f3dB 58 GHz: 1.25 dB peaking (Q=1.0) costs +0.11 dB over the 1.15 dB ISI+EQ budget line; 2.4 dB costs +0.33; 6.3 dB → 4.3 dB (unusable)",
            ],
            [
              <Text as="span" weight="medium">Group-delay ripple</Text>,
              "≤ 3 ps peak-to-peak over 2–40 GHz (0.32 UI)",
              "The sleeper spec: the measured 46 GHz settings are flat to 0.2 dB yet fail on 12.5 ps GD ripple → h₋₁ ≈ 0.48 pre-cursor CTLE cannot touch. 3–4 ps keeps h₋₁ ≤ 0.12 and ISI+EQ within +0.1 dB. GEN1 design point has 7.2 ps — fine at 53 GBd (0.38 UI), fatal at 106",
            ],
            [
              <Text as="span" weight="medium">Transimpedance gain (ZT, differential)</Text>,
              "≥ 57 dBΩ (≥700 Ω) at the highest-gain setting",
              "Eye current at the Q=7.035 sensitivity point is 2Q·iₙ = 62 µApp; a 10–15 mVppd slicer (assumption, lecture-4 real-slicer) needs only 44–48 dBΩ, but keeping TIA noise ≥3× an assumed ≤1 mV rms downstream (CTLE+slicer) noise needs 57 dBΩ. Measured family spans 59–87 dBΩ — this line is met by existing gain classes",
            ],
            [
              <Text as="span" weight="medium">Overload / dynamic range</Text>,
              "No BER degradation from 150 to 700 µApp signal input; ZT adjustment ≥ 14 dB (electrical) in ≤3 dB steps",
              "Required-OMA floor −7.67 dBm → 150 µApp; Rx OMA max −1 dBm → 696 µApp (13.4 dB electrical range). NRZ + limiting is tolerant, but the output must stay inside the CTLE linear range — hence AGC steps. Measured family's 28 dB gain range shows this is routine",
            ],
            [
              <Text as="span" weight="medium">DC handling / AGC</Text>,
              "DC photocurrent cancellation ≥ 750 µA",
              "Max average power at Rx ≈ −0.8 dBm (OMA −1 dBm at ER 4.5 dB) × 0.876 A/W = 731 µA average",
            ],
            [
              <Text as="span" weight="medium">Low-frequency cutoff</Text>,
              "≤ 1 MHz, with baseline-wander penalty ≤ 0.05 dB at 72-bit CID",
              "Droop ≈ 2π·f_LF·N·UI: 1.34 MHz gives 0.05 dB at N=72 consecutive identical digits (scrambled NRZ). The pulse analysis assumes flat response below 2 GHz — a DC-restoration loop inside this cutoff is required, matching that assumption",
            ],
          ]}
          columnAlign={["left", "left", "left"]}
        />
        <Card>
          <CardHeader>Verification recipe — how a candidate TIA passes (same data format as the 152-setting tables)</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text size="small">
                1. Measure the differential transfer function (100 kHz to ≥80 GHz) and the output
                noise spectrum to ≥80 GHz. Input-refer: iₙ = (integrated output noise rms) /
                (peak single-ended gain). Require iₙ ≤ 4.4 µA rms and the density mask (≤17
                pA/√Hz average, ≤20 pA/√Hz spot below 53 GHz).
              </Text>
              <Text size="small">
                2. Static response checks: f3dB within 50–64 GHz; magnitude peaking ≤ 1.0 dB over
                DC–53 GHz with monotonic rolloff; group-delay ripple ≤ 3 ps over 2–40 GHz.
              </Text>
              <Text size="small">
                3. Analytic floor: OMA_floor = 2·Q·iₙ/R with Q = 7.035, R = 0.876 A/W. Require
                ≤ −11.4 dBm.
              </Text>
              <Text size="small">
                4. Pulse-response flow: cascade a 2-pole Tx at 0.45 UI (4.24 ps) 20–80% transition,
                a 25 fF microbump pole (127 GHz), and the measured TF. Optimize a CTLE (one zero
                10–40 GHz, two poles 45–95 GHz) for minimum ISI penalty plus noise-enhancement
                cost. Require ISI+EQ net ≤ 1.15 dB (and ≤ 1.70 dB re-run at the 0.60 UI corner).
              </Text>
              <Text size="small">
                5. Jitter check on the equalized eye: with TJ = 0.351 UI (RJ 0.015 UI rms, DJ
                0.14 UI, dual-Dirac at Q = 7.035), the eye at ±TJ/2 must be open with penalty
                ≤ 1.0 dB.
              </Text>
              <Text size="small">
                6. Assemble the stack: RIN+shot by Q-solve at the measured noise bandwidth + MPI
                0.21 + ISI+EQ (step 4) + CD 0.04 + jitter (step 5) + crosstalk 0.36 + threshold
                0.21. Require required-OMA = floor + stack ≤ −7.5 dBm, i.e. end-to-end margin
                ≥ +1.5 dB at Tx OMA −3.5 dBm and 2.5 dB link IL.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Text tone="tertiary" size="small">
          Honest buildability note: 4.4 µA over 64 GHz with a 65–75 fF input node is
          state-of-the-art but consistent with published 100 GBd-class TIAs (typically
          quoting 2.5–5 µA at 55–65 GHz in SiGe or advanced FinFET with T-coil input peaking).
          The measured ADFET family fails the noise line by its f²-dominated scaling law and the
          group-delay line outright — this is a new-design requirement, not a settings search.
        </Text>
      </Stack>

      <Divider />

      <Stack gap={6}>
        <H3>Method notes</H3>
        <Text tone="tertiary" size="small">
          Tx modeled as two cascaded real poles fitted to 20–80% transition time (0.35/0.45/0.60
          UI corners at 9.412 ps UI); the summed slice-DAC waveform is mathematically an ideal
          linear FIR on NRZ data. Measured TIA: differential transfer function + output-noise
          tables (TT corner, Ocelot_TIA_ADFET.vtmg_pack), LF magnitude flattened below 2 GHz with
          bulk-delay phase preserved; noise input-referred with the single-ended p-leg gain (GEN1
          convention, conservative). Noise split: non-negative least squares of iₙ² against white
          (∫|Ĥ|²df) and f² (∫f²|Ĥ|²df) integrals across all 152 settings, including the model's
          60 GHz noise-path LPF; f²-only fit R² = 0.87 vs white-only 0.59. Hypothetical TIA:
          Butterworth-2 at 53–64 GHz; noise via lecture-4 scaling of the GEN1 design point (√BW
          white bound, BW^1.5 f² bound) plus a 4.5 µA target-class point. EQ: grid search over
          FIR taps under Σ|w| = 1 peak-swing constraint and CTLE zero/poles, with de-emphasis OMA
          cost and CTLE noise enhancement charged. Jitter: dual-Dirac, TJ = DJ + 2Q·σ_RJ,
          penalty on the equalized eye at ±TJ/2; cases where the eye is closed at ±TJ/2 are
          reported as non-closing rather than as a finite penalty. RIN/shot by Q-solve at each
          BWn. MPI: Bhatt/King discounted upper bound, D = 0.5. CD: quadratic-phase channel at
          ±1.7 ps/nm in the pulse simulation. Section 7 derivations: peaking/group-delay limits
          from a variable-Q 2nd-order sweep at fixed 58 GHz f3dB run through the same pulse+CTLE
          flow; noise-shape check by comparing post-CTLE rms gain of white vs f²-shaped input
          density at equal total rms; bandwidth window from a 45–70 GHz f3dB sweep of
          floor + ISI+EQ + RIN; LF cutoff from droop ≈ 2π·f_LF·N·UI at 72-bit CID; gain floor
          from eye current 2Q·iₙ vs assumed 10–15 mVppd slicer sensitivity and ≤1 mV rms
          downstream noise. Nothing under sandbox/alex was used.
        </Text>
      </Stack>
    </Stack>
  );
}
