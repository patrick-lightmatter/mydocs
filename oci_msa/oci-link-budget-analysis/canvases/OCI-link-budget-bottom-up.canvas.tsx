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
  Row,
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

/**
 * 200G OCI bottom-up optical link budget — derived independently from:
 *  - 200G OCI Optical Phy Spec v1.0 (food/200G-OCI-Optical-Phy-Specification-v1.0.pdf)
 *  - IEEE P802.3dj D1.3 Clause 180/181 (structural template + cross-check)
 *  - Palermo ECEN721 lecture 4 (Rx/Personick), lecture 7 (Tx), ECEN720 lecture 10 (jitter)
 *  - Bhatt/King IEEE 802.3bs MPI upper-bound model (bhatt_3bs_01a_0116, king_01a_0116_smf)
 *  - Lightmatter Ocelot/COUPE ADFET TIA characterization tables (TT corner) in
 *    LM-link-vpiphotonics/Mesa/Components/TIA/Ocelot_TIA_ADFET.vtmg_pack
 * All data below is embedded from the analysis run; nothing from sandbox/alex was used.
 */

const PENALTIES: Array<{
  name: string;
  formula: string;
  inputs: string;
  db: number;
  tone?: "success" | "danger" | "warning" | "info" | "neutral";
}> = [
  {
    name: "ER / signal-dependent shot noise",
    formula: "i²ₙ,₁ = i²amp + 2·q·R·P₁·BWn (Q-solve)",
    inputs: "ER = 3.5 dB (spec min); OMA-domain, so classic (ER+1)/(ER−1) does not apply",
    db: 0.11,
  },
  {
    name: "RIN (Q²-scaled)",
    formula: "σ_RIN,L = R·P_L·√(RIN·BWn); Q = R·OMA/(σ₀+σ₁)",
    inputs: "RIN_OMA = −138 dB/Hz @ 21.4 dB ORL (Tx spec); BWn = 28.2 GHz",
    db: 0.41,
    tone: "info",
  },
  {
    name: "MPI / coherent crosstalk",
    formula: "10·log₁₀(1/(1−x)); x = 4·D·S·E/(E−1)",
    inputs: "Rt = Rr = −19 dB, 4 conn @ −35 dB, ER 3.5 dB, D = 0.5 (Bhatt/King)",
    db: 0.51,
    tone: "danger",
  },
  {
    name: "ISI residual after equalization",
    formula: "−10·log₁₀((cursor − Σ|pre|)/cursor)",
    inputs: "Tx BT4 26.6 GHz + measured TIA TF (29.3 GHz); DFE cancels post-cursors",
    db: 0.64,
  },
  {
    name: "Chromatic dispersion",
    formula: "Δ peak-distortion PP with phase exp(jπDλ²f²/c)",
    inputs: "D·L = +1.7 ps/nm worst (spec −0.9…+1.7), 53.125 GBd NRZ",
    db: 0.01,
    tone: "success",
  },
  {
    name: "Jitter / timing",
    formula: "TJ = DJ + 2·Q·σ_RJ; PP from eye at ±TJ/2",
    inputs: "RJ = 0.010 UI rms, DJ = 0.10 UI → TJ@1e-12 = 0.241 UI (4.5 ps)",
    db: 0.61,
  },
  {
    name: "Inter-channel crosstalk",
    formula: "−10·log₁₀(1 − 2ε); ε = Σ 10^(−iso/10)·10^(ΔOMA/10)",
    inputs: "MRR demux adjacent isolation 20 dB (assumed), 2 neighbors, +3 dB dOMA",
    db: 0.36,
  },
  {
    name: "Decision threshold offset",
    formula: "PP = 1 + 2δ",
    inputs: "δ = 2.5% of swing (offset-cal assumption)",
    db: 0.21,
  },
  {
    name: "Dark current",
    formula: "PP = √(1 + 2·q·I_DK·BWn/i²amp)",
    inputs: "I_DK = 1 µA worst case",
    db: 0.0,
    tone: "success",
  },
];

const PENALTY_TOTAL = 2.87;
const FLOOR_DBM = -12.93;
const REQUIRED_AT_RX = -10.06;

export default function OciLinkBudgetBottomUp() {
  return (
    <Stack gap={20} style={{ maxWidth: 980, margin: "0 auto", padding: 16 }}>
      <Stack gap={4}>
        <H1>200G OCI link budget — bottom-up, per DWDM channel</H1>
        <Text tone="secondary">
          53.125 GBd NRZ, OMA domain, internal design target pre-FEC BER = 1e-12 (Q = 7.035).
          Every number derived from the OCI v1.0 spec, IEEE P802.3dj D1.3 Clause 180/181,
          Sackinger/Palermo receiver–transmitter–jitter analysis, and TIA/PD parameters
          extracted from the Ocelot/COUPE ADFET TIA tables. Nothing under sandbox/alex was used.
        </Text>
      </Stack>

      <Grid columns={4} gap={16}>
        <Stat value="−12.9 dBm" label="Analytic Rx floor (OMA @ 1e-12)" />
        <Stat value="2.87 dB" label="Total penalty stack" />
        <Stat value="+0.66 dB" label="Margin vs spec-min Tx" tone="warning" />
        <Stat value="+2.36 dB" label="Margin vs realistic LM Tx" tone="success" />
      </Grid>

      <Callout tone="warning" title="Two red flags">
        (1) The derived MPI penalty (0.51 dB discounted, 1.08 dB worst case) exceeds the OCI
        spec&apos;s 0.2 dB MPI tolerance by 2.5–5x — driven by the −19 dB Tx/Rx reflectance
        limits, which dominate the reflection-pair sum. (2) At Q = 7.03 the RIN penalty triples
        versus its value at the spec BER (0.41 dB vs ~0.13 dB) because RIN penalties scale as Q².
        No RIN-induced BER floor though: RIN-limited Q_max ≈ 18 (floor ~1e-73).
      </Callout>

      <Stack gap={8}>
        <H2>1 · Analytic Rx sensitivity floor</H2>
        <Text tone="secondary">
          Lecture-4 method: input-referred TIA noise from measured output noise divided by
          midband transimpedance, then OMA_sens = 2·Q·iₙ/R. TIA data: TT corner tables in{" "}
          <Text as="span" tone="secondary" italic>
            Ocelot_TIA_ADFET.vtmg_pack/Inputs/TT_TIA_DATA_ED_ADFET_20250520
          </Text>{" "}
          (the tables consumed by `TiaModel.py` in the COUPE DWDM/DR TIA models). Of 152 gain/peaking
          settings, 55 have BW ≥ 0.55x baud; the lowest-noise usable setting (key 12211111) is the
          design point.
        </Text>
        <Table
          headers={["Input", "Value", "Source"]}
          rows={[
            [
              "TIA output noise (rms)",
              "5.28 mV",
              "TT_Tia_Noise.csv, setting 12211111",
            ],
            [
              "Midband transimpedance H₀",
              "1664 V/A (64.4 dBΩ)",
              "TT_Tia_TF_12211111.csv, differential ip−in",
            ],
            [
              "Input-referred noise iₙ = vₙ/H₀",
              "3.17 µA rms",
              "Lecture 4 input-referral",
            ],
            [
              "Rx 3-dB bandwidth",
              "29.3 GHz (0.55 × baud)",
              "Same TF; Personick BWn = 28.2 GHz from ∫|H/H₀|²df",
            ],
            [
              "PD responsivity R",
              "0.876 A/W",
              "pd column of the TIA TF tables (PD-only transfer at DC)",
            ],
            ["Personick Q", "7.035", "BER 1e-12, equal noise statistics"],
          ]}
        />
        <Card>
          <CardHeader>Sensitivity formula and result</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text>
                OMA_sens = 2·Q·iₙ / R = 2 × 7.035 × 3.17 µA / 0.876 A/W = 50.9 µW ={" "}
                <Text as="span" weight="bold">−12.93 dBm OMA</Text>
              </Text>
              <Text tone="secondary" size="small">
                Adding level-dependent shot noise (2qR·P₁·BWn at ER 3.5 dB) moves the floor by only
                +0.11 dB — booked as a penalty line below, consistent with lecture 4&apos;s p-i-n
                conclusion. For reference, at the spec&apos;s BER 2.4e-4 (Q = 3.49) the same
                receiver floors at −15.97 dBm OMA, comfortably inside the spec&apos;s −6.2 dBm
                stressed sensitivity requirement.
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Stack>

      <Stack gap={8}>
        <H2>2 · Power penalty stack</H2>
        <Table
          headers={["Penalty", "Formula", "Inputs", "dB"]}
          rows={PENALTIES.map((p) => [
            <Text as="span" weight="medium">
              {p.name}
            </Text>,
            <Text as="span" size="small" tone="secondary">
              {p.formula}
            </Text>,
            <Text as="span" size="small" tone="secondary">
              {p.inputs}
            </Text>,
            p.db.toFixed(2),
          ]).concat([
            [
              <Text as="span" weight="bold">
                Total
              </Text>,
              "",
              "",
              <Text as="span" weight="bold">
                {PENALTY_TOTAL.toFixed(2)}
              </Text>,
            ],
          ])}
          rowTone={PENALTIES.map((p) => p.tone).concat([undefined])}
          columnAlign={["left", "left", "left", "right"]}
        />
        <BarChart
          categories={PENALTIES.map((p) => p.name)}
          series={[{ name: "Penalty (dB)", data: PENALTIES.map((p) => p.db) }]}
          horizontal
          height={300}
          valueSuffix=" dB"
          referenceLines={[{ value: 0.5, label: "Clause 181 MPI+DGD alloc", tone: "warning" }]}
        />
        <Text tone="tertiary" size="small">
          Source: analytic derivation per lectures 4/7/10 + Bhatt/King MPI upper bound; ISI and
          jitter penalties computed on the measured TIA pulse response (AC-coupling droop flattened
          below 2 GHz, assuming Rx DC restoration). Unequalized peak-distortion ISI would be
          2.15 dB; a standard 53G NRZ SerDes FFE/DFE (post-cursor cancellation) recovers it to
          0.64 dB of residual pre-cursor ISI.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>3 · Budget closure</H2>
        <Text tone="secondary">
          Spec-min Tx OMA = max(−5.5, −6.9+TDEC) dBm pins OMA−TDEC at −6.9 dBm for any TDEC ≥ 1.4 dB,
          so both TDEC corners close identically. Realistic Lightmatter Tx case: OMA = −3.2 dBm with
          TDEC ≈ 2 dB — consistent with the spec&apos;s own stressed-test aggressor operating point
          (Table 2-4, −3.2 dBm), the ELS budget (6 dBm/group → ~0 dBm avg/channel ceiling), and the
          ~1.2 Vppd drive swing in the COUPE TxDrv nonlinearity tables (Typ_Txdrv_NL.csv) driving
          the DWDM MRM at ER ≈ 4.5 dB.
        </Text>
        <BarChart
          categories={["Tx OMA out", "After 2.5 dB link IL", "Effective at Rx (−TDEC)"]}
          series={[
            { name: "Spec-min Tx (−5.5 dBm, TDEC 1.4 dB)", data: [-5.5, -8.0, -9.4], tone: "warning" },
            { name: "Realistic LM Tx (−3.2 dBm, TDEC 2.0 dB)", data: [-3.2, -5.7, -7.7], tone: "info" },
          ]}
          beginAtZero={false}
          yMin={-14}
          yMax={-2}
          height={260}
          valueSuffix=" dBm"
          showValues
          referenceLines={[
            { value: REQUIRED_AT_RX, label: "Required OMA (floor + 2.87 dB penalties)", tone: "danger" },
            { value: FLOOR_DBM, label: "Analytic noise floor", tone: "neutral" },
          ]}
        />
        <Table
          headers={["Scenario", "Tx OMA", "− IL", "− TDEC", "At Rx", "Required", "Margin"]}
          rows={[
            ["Spec-min Tx, TDEC = 1.4 dB", "−5.5 dBm", "2.5 dB", "1.4 dB", "−9.40 dBm", "−10.06 dBm", "+0.66 dB"],
            ["Spec-min Tx, TDEC = 3.4 dB", "−3.5 dBm", "2.5 dB", "3.4 dB", "−9.40 dBm", "−10.06 dBm", "+0.66 dB"],
            ["Realistic LM Tx, TDEC ≈ 2 dB", "−3.2 dBm", "2.5 dB", "2.0 dB", "−7.70 dBm", "−10.06 dBm", "+2.36 dB"],
          ]}
          rowTone={["warning", "warning", "success"]}
          columnAlign={["left", "right", "right", "right", "right", "right", "right"]}
        />
        <Text tone="tertiary" size="small">
          Caveat: TDEC is defined at BER 2.4e-4; its noise-like content would scale slightly at
          Q = 7.03, its deterministic (eye-closure) content does not. It is applied unscaled here.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>4 · IEEE 802.3dj Clause 181 cross-check</H2>
        <Grid columns={2} gap={16}>
          <Card>
            <CardHeader>Penalty allocation comparison</CardHeader>
            <CardBody style={{ padding: 0 }}>
              <Table
                framed={false}
                headers={["Item", "This budget", "802.3dj Cl. 181", "OCI spec"]}
                rows={[
                  ["Channel insertion loss", "2.5 dB", "3.5 dB", "2.5 dB"],
                  ["Total penalties", "2.87 dB", "3.9 dB", "—"],
                  ["MPI (+DGD in Cl. 181)", "0.51 dB (D=0.5)", "0.5 dB", "0.2 dB"],
                  ["Total power budget", "5.4 dB", "7.4 dB", "—"],
                ]}
                columnAlign={["left", "right", "right", "right"]}
                rowTone={[undefined, undefined, "danger", undefined]}
              />
            </CardBody>
          </Card>
          <Card>
            <CardHeader>Cl. 181 Table 181-10 — discrete reflectance limits</CardHeader>
            <CardBody style={{ padding: 0 }}>
              <Table
                framed={false}
                headers={["# reflectances > −55 dB", "Max each", "OCI equivalent"]}
                rows={[
                  ["1", "−25 dB", "Tx/Rx ends are −19 dB (!)"],
                  ["2", "−31 dB", ""],
                  ["4", "−35 dB", "assumed for 4 connectors"],
                  ["6", "−38 dB", ""],
                  ["8", "−40 dB", ""],
                ]}
                columnAlign={["right", "right", "left"]}
              />
            </CardBody>
          </Card>
        </Grid>
        <Text tone="secondary" size="small">
          The stack lands 1.0 dB under Clause 181&apos;s 3.9 dB allocation, mostly because the OCI
          reference channel is shorter/lower-loss and NRZ needs no PAM4 level-separation penalty.
          But the MPI line matches Clause 181&apos;s 0.5 dB — not the OCI spec&apos;s 0.2 dB. With
          S = √(RtRr) + n√(RtRc) + n√(RrRc) + n(n−1)Rc/2 = 0.0304, the two −19 dB end reflectances
          contribute 93% of S (41% direct pair + 52% end-connector cross terms). Meeting 0.2 dB at
          ER 3.5 dB requires roughly Rt = Rr ≤ −24 dB, or budget honesty at 0.5 dB.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>5 · Sensitivity to assumptions</H2>
        <Text tone="secondary">
          Margin deltas versus the base case (spec-min Tx, +0.66 dB margin).
        </Text>
        <Table
          headers={["Assumption varied", "Base value", "Alternative", "Penalty/floor shift", "New margin"]}
          rows={[
            ["TIA input noise", "3.17 µA (best usable)", "4.26 µA (median usable setting)", "floor +1.28 dB", "−0.62 dB"],
            ["TIA input noise", "3.17 µA", "6.75 µA (worst usable setting)", "floor +3.28 dB", "−2.62 dB"],
            ["PD responsivity", "0.876 A/W (model)", "0.80 A/W", "floor +0.39 dB", "+0.27 dB"],
            ["PD responsivity", "0.876 A/W", "1.00 A/W", "floor −0.58 dB", "+1.24 dB"],
            ["MPI reflectance count", "4 conn @ −35 dB", "2 connectors", "MPI 0.51 → 0.34 dB", "+0.83 dB"],
            ["MPI reflectance count", "4 conn @ −35 dB", "6 connectors", "MPI 0.51 → 0.70 dB", "+0.47 dB"],
            ["MPI discount factor", "D = 0.5", "D = 1.0 (worst case)", "MPI 0.51 → 1.08 dB", "+0.09 dB"],
            ["RIN", "−138 dB/Hz (Tx @ ORL)", "−144 dB/Hz (ELS only)", "RIN 0.41 → 0.10 dB", "+0.98 dB"],
          ]}
          rowTone={[
            "danger",
            "danger",
            undefined,
            undefined,
            undefined,
            undefined,
            "warning",
            "success",
          ]}
          columnAlign={["left", "left", "left", "right", "right"]}
        />
        <Callout tone="info" title="What actually moves the budget">
          TIA noise dominates: only the best-decile TIA settings close the spec-minimum case at
          1e-12. The MPI worst case (D = 1) alone consumes essentially the entire margin. The
          realistic-Tx case (+2.36 dB) survives all single-assumption excursions except the
          worst-usable TIA setting.
        </Callout>
      </Stack>

      <Divider />

      <Stack gap={6}>
        <H3>Method notes and provenance</H3>
        <Text tone="tertiary" size="small">
          Rx floor: lecture 4 (Sackinger ch. 4) with iₙ input-referred from the TIA vendor tables;
          Personick noise bandwidth integrated from the measured transfer function rather than
          assumed. ISI/CD/jitter penalties: single pulse-response framework using the measured
          differential TIA TF, a 4th-order 26.5625 GHz Bessel-Thomson reference Tx (spec TDEC
          receiver), quadratic dispersion phase, and dual-Dirac total jitter at Q = 7.035
          (lecture 10). RIN/shot/ER: iterative Q-solve with level-dependent noise (lectures 4/7).
          MPI: Bhatt/King 802.3bs discounted upper bound with the OCI spec&apos;s −19 dB Tx/Rx
          reflectances, 21.4 dB ORL context, and Clause 181-style connector population. Crosstalk
          isolation (20 dB), RJ (0.010 UI rms), DJ (0.10 UI), and threshold offset (2.5%) are
          stated assumptions. Fiber: 500 m SMF-28, 2.5 dB IL, CD −0.9…+1.7 ps/nm per OCI Table 2-5.
        </Text>
      </Stack>
    </Stack>
  );
}
