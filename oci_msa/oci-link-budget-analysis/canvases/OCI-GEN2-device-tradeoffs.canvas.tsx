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
 * OCI GEN2 device trade-off study — companion to OCI-GEN2-CPO-spec.
 * Evaluates measured device options against the 106.25 GBd NRZ CTLE-only budget
 * (Q = 7.035, Tx OMA -3.5 dBm, 2.5 dB link IL, same pulse-response + optimal-CTLE +
 * full-stack framework). TIA A: 3-4 uA @ 50 GHz. TIA B: 4-5 uA @ 60 GHz.
 * Tx trade: baseline 3-tap slice-DAC FIR vs no-FIR with a 60 GHz driver.
 */

type Cell = {
  tx: string;
  tia: string;
  floor: string;
  isi: string;
  jit: string;
  stack: string;
  margin: number;
};

const MATRIX: Cell[] = [
  { tx: "FIR3, typ driver (0.45 UI)", tia: "A @ 3 µA / 50 GHz", floor: "−13.17", isi: "1.59", jit: "0.88", stack: "4.05", margin: 3.12 },
  { tx: "FIR3, typ driver (0.45 UI)", tia: "A @ 4 µA / 50 GHz", floor: "−11.92", isi: "1.59", jit: "0.88", stack: "4.00", margin: 1.92 },
  { tx: "FIR3, typ driver (0.45 UI)", tia: "B @ 4 µA / 60 GHz", floor: "−11.92", isi: "1.05", jit: "0.84", stack: "3.58", margin: 2.34 },
  { tx: "FIR3, typ driver (0.45 UI)", tia: "B @ 5 µA / 60 GHz", floor: "−10.95", isi: "1.05", jit: "0.84", stack: "3.55", margin: 1.41 },
  { tx: "FIR3, slow driver (0.60 UI)", tia: "A @ 3 µA / 50 GHz", floor: "−13.17", isi: "2.15", jit: "0.92", stack: "4.65", margin: 2.52 },
  { tx: "FIR3, slow driver (0.60 UI)", tia: "A @ 4 µA / 50 GHz", floor: "−11.92", isi: "2.15", jit: "0.92", stack: "4.60", margin: 1.33 },
  { tx: "FIR3, slow driver (0.60 UI)", tia: "B @ 4 µA / 60 GHz", floor: "−11.92", isi: "1.61", jit: "0.86", stack: "4.16", margin: 1.76 },
  { tx: "FIR3, slow driver (0.60 UI)", tia: "B @ 5 µA / 60 GHz", floor: "−10.95", isi: "1.61", jit: "0.86", stack: "4.13", margin: 0.83 },
  { tx: "no-FIR, 60 GHz driver + MRM 60 GHz", tia: "A @ 3 µA / 50 GHz", floor: "−13.17", isi: "2.19", jit: "0.60", stack: "4.37", margin: 2.8 },
  { tx: "no-FIR, 60 GHz driver + MRM 60 GHz", tia: "A @ 4 µA / 50 GHz", floor: "−11.92", isi: "2.19", jit: "0.60", stack: "4.32", margin: 1.6 },
  { tx: "no-FIR, 60 GHz driver + MRM 60 GHz", tia: "B @ 4 µA / 60 GHz", floor: "−11.92", isi: "1.66", jit: "0.58", stack: "3.93", margin: 1.99 },
  { tx: "no-FIR, 60 GHz driver + MRM 60 GHz", tia: "B @ 5 µA / 60 GHz", floor: "−10.95", isi: "1.66", jit: "0.58", stack: "3.89", margin: 1.06 },
];

const MRM_SENS: Array<{ mrm: string; tr: string; a3: number; a4: number; b4: number; b5: number }> = [
  { mrm: "80 GHz", tr: "5.29 ps (0.56 UI)", a3: 3.1, a4: 1.9, b4: 2.2, b5: 1.26 },
  { mrm: "60 GHz", tr: "5.88 ps (0.62 UI)", a3: 2.8, a4: 1.6, b4: 1.99, b5: 1.06 },
  { mrm: "50 GHz", tr: "6.47 ps (0.69 UI)", a3: 2.56, a4: 1.36, b4: 1.78, b5: 0.85 },
  { mrm: "40 GHz", tr: "7.35 ps (0.78 UI)", a3: 2.26, a4: 1.06, b4: 1.44, b5: 0.5 },
];

function marginTone(m: number): "success" | "info" | "warning" {
  if (m >= 1.5) return "success";
  if (m >= 1.0) return "info";
  return "warning";
}

export default function OciGen2DeviceTradeoffs() {
  return (
    <Stack gap={20} style={{ maxWidth: 1000, margin: "0 auto", padding: 16 }}>
      <Stack gap={4}>
        <H1>OCI GEN2 device trade-offs — TIA A/B and FIR vs driver bandwidth</H1>
        <Text tone="secondary">
          Companion to the GEN2 spec canvas (OCI-GEN2-CPO-spec). Measured device options
          evaluated against the 106.25 GBd NRZ CTLE-only budget: same pulse-response +
          optimal-CTLE + full penalty stack at Q = 7.035, BER 1e-12, Tx OMA −3.5 dBm, 2.5 dB
          link IL, 25 fF microbump in path. Every scenario cell below closes the link — the
          trade is about margin, risk, and complexity, not feasibility.
        </Text>
      </Stack>

      <Grid columns={4} gap={16}>
        <Stat value="24 / 24" label="Scenario cells that close 1e-12" tone="success" />
        <Stat value="Drop the FIR" label="If the driver hits 60 GHz (+0.27 dB, less complexity)" tone="info" />
        <Stat value="iₙ ≈ 3.6 µA" label="TIA A-vs-B crossover (A wins below it)" />
        <Stat value="+0.50 dB" label="Worst combo (no-FIR, MRM 40 GHz, B @ 5 µA)" tone="warning" />
      </Grid>

      <Stack gap={8}>
        <H2>1 · Devices and modeling assumptions</H2>
        <Callout tone="warning" title="Assumption stated up front: these TIAs are modeled as CLEAN responses">
          TIA A (50 GHz) and TIA B (60 GHz) are modeled as Butterworth-2 responses that MEET the
          spec canvas §7 frequency-response-quality lines (peaking ≤ 1 dB, group-delay ripple
          ≤ 3 ps over 2–40 GHz). The measured ADFET family failed exactly there — 12.5 ps of GD
          ripple produced a CTLE-unrecoverable h₋₁ ≈ 0.48 pre-cursor despite flat magnitude. If
          option A or B carries similar phase distortion, every margin below is invalid: verify
          §7 step 2 (peaking + GD ripple) on the real parts before trusting this table.
        </Callout>
        <Table
          headers={["Item", "Model", "Notes"]}
          rows={[
            [
              "TIA A",
              "Butterworth-2, f3dB 50 GHz (BWn 55.5 GHz); iₙ = 3 or 4 µA rms",
              "Floors −13.17 / −11.92 dBm. Its optimal CTLE needs poles at 81–93 GHz with 1.11–1.17× noise gain — itself aggressive silicon at 106 GBd",
            ],
            [
              "TIA B",
              "Butterworth-2, f3dB 60 GHz (BWn 66.6 GHz); iₙ = 4 or 5 µA rms",
              "Floors −11.92 / −10.95 dBm. Optimal CTLE is mild: poles 63–69 GHz, ≈1.0–1.04× noise gain",
            ],
            [
              "Tx, FIR3 cases",
              "2-pole composite (driver + MRM) at 0.45 UI (4.4 ps) or 0.60 UI (5.6 ps) 20–80%, 3-tap slice-DAC FIR available; DJ = 0.14 UI (incl. 0.05 slice DCD)",
              "Same corners as the spec canvas; FIR optimized jointly with CTLE per cell",
            ],
            [
              "Tx, no-FIR case",
              "Driver = single 60 GHz pole × MRM = single pole at 40/50/60/80 GHz; DJ = 0.11 UI (slice-DCD allocation credited back, 0.02 UI ordinary driver DCD retained)",
              "BW→edge mapping: 20–80% ≈ 0.345/f_pole per pole; the 60+60 GHz composite measures 5.88 ps (0.62 UI) in the pulse framework",
            ],
            [
              "Everything else",
              "MPI 0.205 + CD 0.04 + crosstalk 0.36 + threshold 0.21 dB; RIN+shot Q-solved per TIA BWn; RJ 0.015 UI rms",
              "Carried from the GEN2 budget; jitter penalty computed on each cell's equalized eye",
            ],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>2 · Scenario margin matrix (dB at Tx OMA −3.5 dBm, BER 1e-12)</H2>
        <Table
          headers={["Tx case", "TIA option", "Floor (dBm)", "ISI+EQ", "Jitter", "Stack", "Margin"]}
          rows={MATRIX.map((c) => [
            c.tx,
            c.tia,
            c.floor,
            c.isi,
            c.jit,
            c.stack,
            <Text as="span" weight="bold">{`+${c.margin.toFixed(2)} dB`}</Text>,
          ])}
          rowTone={MATRIX.map((c) => marginTone(c.margin))}
          columnAlign={["left", "left", "right", "right", "right", "right", "right"]}
        />
        <BarChart
          categories={["A @ 3 µA / 50G", "A @ 4 µA / 50G", "B @ 4 µA / 60G", "B @ 5 µA / 60G"]}
          series={[
            { name: "FIR3, typ driver (0.45 UI)", data: [3.12, 1.92, 2.34, 1.41], tone: "neutral" },
            { name: "FIR3, slow driver (0.60 UI)", data: [2.52, 1.33, 1.76, 0.83], tone: "warning" },
            { name: "no-FIR, 60 GHz driver, MRM 60 GHz", data: [2.8, 1.6, 1.99, 1.06], tone: "info" },
          ]}
          height={280}
          valueSuffix=" dB"
          showValues
        />
        <Text tone="tertiary" size="small">
          Closing margin (dB, optical OMA) per TIA option and Tx architecture at 106.25 GBd,
          BER 1e-12, Tx OMA −3.5 dBm, 2.5 dB link. Source: pulse-response + optimal-CTLE + full
          stack per cell. Green ≥ 1.5 dB, blue ≥ 1.0, amber below. The fair driver-team
          comparison is the bottom two series: same driver class, FIR vs no FIR.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>3 · The FIR-vs-bandwidth trade — what does the FIR actually buy?</H2>
        <Text tone="secondary">
          Isolation experiment on an identical 60 + 60 GHz channel (TIA B @ 4 µA): with the FIR
          allowed, the joint FIR+CTLE optimizer converges to zero tap weight — exactly the
          CTLE-only solution (ISI+EQ 1.66 dB in both cases). The channel taps explain why: h₋₁ =
          0.09, h₊₁ = 0.22, nothing beyond — a mild post-cursor that CTLE removes at ≈1.04×
          noise cost, while a peak-swing-constrained slice FIR must pay ~1:1 in de-emphasis OMA
          for the same eye. The FIR's only net contribution on this channel is its slice-DCD
          jitter cost: 0.85 vs 0.58 dB (DJ 0.14 vs 0.11 UI) — the no-FIR architecture is strictly
          better by 0.27 dB, before counting the delay-line accuracy (±0.47 ps) and slice-matching
          complexity it eliminates.
        </Text>
        <Table
          headers={["MRM EO bandwidth (no-FIR, 60 GHz driver)", "Composite 20–80%", "A @ 3 µA", "A @ 4 µA", "B @ 4 µA", "B @ 5 µA"]}
          rows={MRM_SENS.map((r) => [
            r.mrm,
            r.tr,
            `+${r.a3.toFixed(2)}`,
            `+${r.a4.toFixed(2)}`,
            `+${r.b4.toFixed(2)}`,
            `+${r.b5.toFixed(2)}`,
          ])}
          rowTone={["success", "success", "info", "warning"]}
          columnAlign={["left", "left", "right", "right", "right", "right"]}
        />
        <Text tone="tertiary" size="small">
          MRM-bandwidth sensitivity of the no-FIR case (margins in dB). The swing item resolves
          benignly: MRM 80 → 40 GHz costs only ~0.8 dB because the added rolloff is a clean
          post-cursor the CTLE recovers cheaply. Crucially, re-enabling the FIR on the 40 GHz-MRM
          channel buys zero ISI improvement (2.22 dB either way — the optimizer again picks zero
          taps), so a slow MRM is NOT an argument for keeping the FIR; it is an argument for Tx
          OMA headroom.
        </Text>
        <Callout tone="info" title="Verdict: if the driver reaches 60 GHz, drop the FIR">
          At 106 GBd on this flat co-packaged channel, raw driver bandwidth strictly dominates a
          peak-constrained 3-tap slice FIR: matched-channel comparison gives no-FIR +1.99 dB vs
          FIR3 +1.76 dB (B @ 4 µA), and the ordering holds across every TIA and MRM variant
          tested. The FIR's remaining (unmodeled) value is MRM peaking/overshoot pre-compensation
          and TDEC shaping — if the real MRM needs those, a single post tap is the most that is
          justified. The pre-cursor concern does not materialize: these min-phase channels
          produce h₋₁ ≤ 0.09, well inside CTLE reach — pre-cursor only became fatal for the
          measured TIAs&apos; group-delay ripple, which is a §7 compliance issue, not a Tx EQ issue.
        </Callout>
      </Stack>

      <Stack gap={8}>
        <H2>4 · TIA A vs B — recommendation</H2>
        <Grid columns={2} gap={16}>
          <Card>
            <CardHeader>Where each option wins</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text size="small">
                  At the 4 µA overlap point, B beats A by ~0.4 dB in every Tx case (e.g. +2.34 vs
                  +1.92): the 50 GHz TIA&apos;s extra ISI (+0.54 dB, needing a hotter 81–93 GHz-pole
                  CTLE at 1.11–1.17× noise) outweighs its RIN/noise-bandwidth savings (−0.16 dB).
                  The earlier &quot;flat 50–64 GHz&quot; finding held noise density fixed; with fixed
                  total noise, more bandwidth wins.
                </Text>
                <Text size="small">
                  The crossover sits at A ≈ 3.6 µA: below it A&apos;s floor advantage dominates
                  (A @ 3 µA is the best cell in the whole study, +3.12 dB). B @ 5 µA is the risk
                  corner: +0.83–1.41 dB depending on Tx case.
                </Text>
              </Stack>
            </CardBody>
          </Card>
          <Card>
            <CardHeader>Recommendation</CardHeader>
            <CardBody>
              <Stack gap={6}>
                <Text size="small">
                  <Text as="span" weight="semibold">Pick TIA B unless option A demonstrably lands
                  below ~3.5 µA.</Text> B @ 4 µA gives +2.0–2.3 dB with a mild, low-risk CTLE;
                  its 5 µA corner still closes everywhere. A&apos;s 3 µA corner is the best outcome
                  on paper but pairs a wider noise range with a CTLE that itself pushes 90 GHz
                  poles — two stacked bets.
                </Text>
                <Text size="small">
                  Combined with the Tx verdict, the recommended architecture is
                  <Text as="span" weight="semibold"> no-FIR 60 GHz driver + TIA B</Text>:
                  +1.99 dB typical, +1.06 dB at the 5 µA noise corner, +0.50 dB in the
                  worst-everything cell (5 µA and a 40 GHz MRM) — degraded but never broken.
                </Text>
              </Stack>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      <Stack gap={8}>
        <H2>5 · Assumptions that could flip these conclusions</H2>
        <Table
          headers={["Assumption", "If it breaks"]}
          rows={[
            [
              "TIA A/B phase quality (Butterworth-2, GD ripple ≤ 3 ps) — the load-bearing one",
              "The measured family failed on 12.5 ps GD ripple, not magnitude. If the real options ring, ISI+EQ can jump several dB and no Tx choice compensates. Gate any selection on the §7 verification recipe",
            ],
            [
              "MRM modeled as a single clean pole (no peaking, no nonlinearity)",
              "Real MRM detuning peaking / overshoot is the one thing a Tx FIR fixes that CTLE cannot — strong MRM peaking would justify keeping one post tap",
            ],
            [
              "DJ credit for removing the slice DAC (0.14 → 0.11 UI)",
              "0.27 dB of the no-FIR advantage. If the fast 60 GHz driver brings its own DCD above 0.05 UI, the FIR-vs-no-FIR gap narrows to roughly zero — the ISI term is a genuine tie",
            ],
            [
              "BW→transition mapping (20–80% ≈ 0.345/f_pole, 2-pole cascade)",
              "If the driver's 60 GHz is a small-signal number and large-swing edges are slower, use the measured edge: each +0.15 UI of transition time costs ~0.5 dB (per the corner sweep)",
            ],
            [
              "Tx OMA −3.5 dBm at 106 GBd with these driver/MRM combinations",
              "All margins shift dB-for-dB with Tx OMA; the −1.5 dBm relief valve adds 2 dB to every cell if the optics deliver it",
            ],
          ]}
          columnAlign={["left", "left"]}
        />
      </Stack>

      <Divider />

      <Stack gap={6}>
        <H3>Method notes</H3>
        <Text tone="tertiary" size="small">
          Framework identical to the GEN2 spec canvas: pulse response through Tx × 25 fF microbump
          (127 GHz pole) × TIA, CTLE grid (zero 10–40 GHz, two poles 45–100 GHz) minimizing ISI
          penalty plus noise-enhancement cost; FIR cells additionally run the joint 3-tap
          (Σ|w| = 1 peak-constrained) + CTLE optimization and take the better of the two. Jitter:
          dual-Dirac TJ = DJ + 2Q·σ_RJ evaluated on each cell&apos;s equalized eye at ±TJ/2
          (RJ 0.015 UI rms; DJ 0.14 UI FIR cases / 0.11 UI no-FIR). RIN (−138 dB/Hz) + shot
          Q-solved at each TIA&apos;s noise bandwidth. Floors: 2Q·iₙ/R at R = 0.876 A/W.
          Margin = (Tx OMA −3.5 − IL 2.5) − (floor + stack). MPI/CD/crosstalk/threshold carried
          from the GEN2 budget (0.205/0.04/0.36/0.21 dB). Nothing under sandbox/alex was used.
        </Text>
      </Stack>
    </Stack>
  );
}
