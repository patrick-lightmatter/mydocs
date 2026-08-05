import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  LineChart,
  Pill,
  Row,
  Select,
  Spacer,
  Stack,
  Stat,
  Table,
  Text,
  TextInput,
  useCanvasState,
} from "cursor/canvas";

// ---------------------------------------------------------------------------
// Spec constants — 200G OCI Optical PHY Specification v1.0 (March 11, 2026)
// All optical power values are OMA per DWDM channel in dBm unless noted.
// ---------------------------------------------------------------------------
const SPEC = {
  baud: 53.125, // GBd NRZ per wavelength
  preFecBer: 2.4e-4, // pre-FEC BER threshold used for TDEC / SRS / RxSens
  berFloor: 1e-6, // max BER floor over OMA range (-8.2+TDEC) to -1 dBm
  txOmaMax: -1.0,
  tdecMax: 3.4,
  erMin: 3.5,
  fiberILMax: 2.5, // 500 m SMF-28 reference link, connector-dominated
  cdRange: [-0.9, 1.7] as const, // ps/nm
  mpiTolerance: 0.2, // dB penalty tolerance in the fiber link model
  srs: -6.2, // stressed receiver sensitivity (SEC 3.4 dB, aggressors -3.2 dBm)
  rinOma: -138, // dB/Hz at 21.4 dB ORL
  orlTolerance: 21.4,
};

function txOmaMin(tdec: number): number {
  return Math.max(-5.5, -6.9 + tdec);
}
function rxSensSpec(tdec: number): number {
  return Math.max(-8.2, -9.6 + tdec);
}

// ---------------------------------------------------------------------------
// Alex's simulated Rx sensitivity waterfall.
// Source: LM-link-vpiphotonics/sandbox/alex/COUPE_BIDI_PIC_LINK/Results/
// Waterfall/part1.csv (committed Oct 2025). Processed exactly like his
// plot.py: keep rows with eye amplitude > 20 mV, take min BER per
// attenuation step, Rx OMA = -8.8 dBm - attenuation.
// ---------------------------------------------------------------------------
const WATERFALL: { oma: number; log10Ber: number }[] = [
  { oma: -15.8, log10Ber: -5.0 },
  { oma: -14.8, log10Ber: -7.0 },
  { oma: -14.3, log10Ber: -7.0 },
  { oma: -13.8, log10Ber: -8.52 },
  { oma: -13.3, log10Ber: -9.0 },
  { oma: -12.8, log10Ber: -10.52 },
  { oma: -12.3, log10Ber: -11.52 },
  { oma: -11.8, log10Ber: -12.0 },
  { oma: -11.3, log10Ber: -13.52 },
  { oma: -10.8, log10Ber: -14.52 },
  { oma: -9.8, log10Ber: -15.0 },
  { oma: -8.8, log10Ber: -15.0 },
];

// Personick Q for common BER targets (BER = 0.5 * erfc(Q / sqrt(2))).
const Q_TABLE: { ber: string; q: number; use: string }[] = [
  { ber: "2.4e-4", q: 3.49, use: "OCI spec pre-FEC threshold (TDEC, SRS, RxSens)" },
  { ber: "1e-6", q: 4.75, use: "OCI spec BER floor requirement" },
  { ber: "1e-12", q: 7.03, use: "OUR DESIGN TARGET — internal pre-FEC goal" },
  { ber: "1e-15", q: 7.94, use: "Deep-margin studies (Alex's waterfall floor)" },
];

// Rx sensitivity read off Alex's waterfall at each candidate BER target.
// 1e-12 is a directly measured point; 1e-6 is interpolated between measured
// points; 2.4e-4 is extrapolated ~0.7 dB beyond the last swept attenuation.
const BER_TARGETS: { value: string; label: string; sens: number; q: number; how: string }[] = [
  { value: "1e-12", label: "1e-12 — internal design goal", sens: -11.8, q: 7.03, how: "measured directly on the waterfall" },
  { value: "1e-6", label: "1e-6 — spec BER floor", sens: -15.3, q: 4.75, how: "interpolated between measured points" },
  { value: "2.4e-4", label: "2.4e-4 — spec pre-FEC threshold", sens: -16.5, q: 3.49, how: "extrapolated beyond the sweep" },
];

function parseNum(s: string, fallback: number): number {
  const v = parseFloat(s);
  return Number.isFinite(v) ? v : fallback;
}
function fmt(v: number, digits = 1): string {
  return v.toFixed(digits);
}

// ---------------------------------------------------------------------------
// Budget calculator
// ---------------------------------------------------------------------------
function BudgetCalculator() {
  const [tdecS, setTdec] = useCanvasState("tdec", "3.4");
  const [ilS, setIl] = useCanvasState("fiberIL", "2.5");
  const [txOmaS, setTxOma] = useCanvasState("txOma", "");
  const [sensBasis, setSensBasis] = useCanvasState("sensBasis2", "sim");
  const [targetBer, setTargetBer] = useCanvasState("targetBer", "1e-12");
  const [simSensS, setSimSens] = useCanvasState("simSensOverride", "");
  const [pMpiS, setPMpi] = useCanvasState("penMpi", "0.2");
  const [pSpecXtS, setPSpecXt] = useCanvasState("penSpectralXt", "0");
  const [pElecXtS, setPElecXt] = useCanvasState("penElecXt", "0");
  const [pCdS, setPCd] = useCanvasState("penCd", "0");
  const [pOtherS, setPOther] = useCanvasState("penOther", "0");

  const tdec = parseNum(tdecS, SPEC.tdecMax);
  const il = parseNum(ilS, SPEC.fiberILMax);
  const specTxMin = txOmaMin(tdec);
  const txOma = txOmaS.trim() === "" ? specTxMin : parseNum(txOmaS, specTxMin);
  const omaTp3 = txOma - il;

  const specSens = tdec >= 2.0 ? SPEC.srs : rxSensSpec(tdec);
  const target = BER_TARGETS.find((t) => t.value === targetBer) ?? BER_TARGETS[0];
  const simSens = simSensS.trim() === "" ? target.sens : parseNum(simSensS, target.sens);

  const penalties = [
    { label: "MPI / coherent crosstalk", value: parseNum(pMpiS, 0), set: setPMpi, raw: pMpiS, src: "Results/MPI (spec tolerance 0.2 dB)" },
    { label: "Spectral crosstalk", value: parseNum(pSpecXtS, 0), set: setPSpecXt, raw: pSpecXtS, src: "Results/Spectral_crosstalk" },
    { label: "Electrical crosstalk", value: parseNum(pElecXtS, 0), set: setPElecXt, raw: pElecXtS, src: "Results/Electrical Crosstalk" },
    { label: "Chromatic dispersion", value: parseNum(pCdS, 0), set: setPCd, raw: pCdS, src: "Results/Chromatic_dispersion (spec CD -0.9…1.7 ps/nm)" },
    { label: "Other (aging, polarization, DGD)", value: parseNum(pOtherS, 0), set: setPOther, raw: pOtherS, src: "Results/DGD; allocate as needed" },
  ];
  const penaltySum = penalties.reduce((a, p) => a + p.value, 0);

  // Spec-compliance view: SRS already embeds the stressed-eye + aggressor
  // conditions, so only the MPI tolerance is charged against margin.
  // Implementation view: Alex's waterfall has none of the penalties folded
  // in, so all of them are charged against the simulated sensitivity.
  const isSpec = sensBasis === "spec";
  const sens = isSpec ? specSens : simSens;
  const charged = isSpec ? parseNum(pMpiS, 0) : penaltySum;
  const requiredOma = sens + charged;
  const margin = omaTp3 - requiredOma;
  const marginTone = margin >= 1 ? "success" : margin >= 0 ? "warning" : "danger";

  const inputRow = (
    label: string,
    value: string,
    onChange: (v: string) => void,
    hint: string,
    placeholder?: string,
  ) => (
    <div key={label}>
      <Row gap={8} align="center">
        <div style={{ width: 235 }}>
          <Text size="small">{label}</Text>
        </div>
        <TextInput type="number" value={value} onChange={onChange} placeholder={placeholder} style={{ width: 90 }} />
        <Text size="small" tone="tertiary">
          {hint}
        </Text>
      </Row>
    </div>
  );

  return (
    <Card>
      <CardHeader
        trailing={
          <Pill size="sm" active>
            {isSpec ? "Spec worst-case" : "Alex's simulation"}
          </Pill>
        }
      >
        Interactive budget calculator (per DWDM channel, OMA domain)
      </CardHeader>
      <CardBody>
        <Stack gap={16}>
          <Row gap={16} align="center" wrap>
            <Row gap={8} align="center">
              <Text size="small" weight="semibold">
                Receiver sensitivity basis
              </Text>
              <Select
                value={sensBasis}
                onChange={setSensBasis}
                style={{ width: 340 }}
                options={[
                  { value: "sim", label: "Simulated — Alex's COUPE waterfall (penalties added here)" },
                  { value: "spec", label: "Spec limit — SRS -6.2 dBm (defined only at BER 2.4e-4)" },
                ]}
              />
            </Row>
            {!isSpec && (
              <Row gap={8} align="center">
                <Text size="small" weight="semibold">
                  Target pre-FEC BER
                </Text>
                <Select
                  value={targetBer}
                  onChange={setTargetBer}
                  style={{ width: 280 }}
                  options={BER_TARGETS.map((t) => ({ value: t.value, label: t.label }))}
                />
              </Row>
            )}
          </Row>
          {isSpec && (
            <Text size="small" tone="tertiary">
              Note: the spec's SRS limit is defined at BER 2.4e-4 only. For the internal 1e-12 goal, switch to the
              simulated basis — there is no spec-compliance concept at 1e-12.
            </Text>
          )}

          <Grid columns={2} gap={24}>
            <Stack gap={8}>
              <H3>Transmitter and channel</H3>
              {inputRow("TDEC (dB, spec max 3.4)", tdecS, setTdec, `Tx OMA min = max(-5.5, -6.9+TDEC) = ${fmt(specTxMin)} dBm`)}
              {inputRow("Tx OMA at TP2 (dBm)", txOmaS, setTxOma, "blank = spec minimum", fmt(specTxMin))}
              {inputRow("Fiber link IL (dB, spec max 2.5)", ilS, setIl, "500 m SMF-28, connector-dominated")}
              {!isSpec &&
                inputRow(
                  "Simulated Rx sensitivity (dBm OMA)",
                  simSensS,
                  setSimSens,
                  `blank = ${fmt(target.sens)} dBm from waterfall @ ${target.value} (${target.how})`,
                  fmt(target.sens),
                )}
            </Stack>
            <Stack gap={8}>
              <H3>Power penalties (dB)</H3>
              {penalties.map((p) =>
                inputRow(p.label, p.raw, p.set, p.src),
              )}
              {isSpec && (
                <Text size="small" tone="tertiary">
                  In spec mode only the MPI entry is charged — SEC and aggressor stress are already inside the -6.2 dBm SRS limit.
                </Text>
              )}
            </Stack>
          </Grid>

          <Divider />

          <Table
            headers={["Budget line", "Value", "Running OMA (dBm)"]}
            columnAlign={["left", "right", "right"]}
            rows={[
              ["Tx OMA at TP2", `${fmt(txOma)} dBm`, fmt(txOma)],
              ["Fiber link insertion loss", `-${fmt(il)} dB`, fmt(omaTp3)],
              ["= OMA delivered at TP3", "", fmt(omaTp3)],
              [
                isSpec
                  ? "Rx limit: stressed sensitivity (SRS @ 2.4e-4)"
                  : `Rx limit: simulated sensitivity @ BER ${target.value}`,
                `${fmt(sens)} dBm`,
                "",
              ],
              ["+ penalties charged here", `+${fmt(charged)} dB`, fmt(requiredOma)],
              ["= Required OMA at TP3", "", fmt(requiredOma)],
            ]}
            rowTone={[undefined, undefined, "info", undefined, undefined, "info"]}
          />

          <Row gap={24} align="center">
            <Stat value={`${fmt(margin)} dB`} label="Link margin at TP3" tone={marginTone} />
            <Stat value={`${fmt(omaTp3)} dBm`} label="OMA at TP3 (delivered)" />
            <Stat value={`${fmt(requiredOma)} dBm`} label="Required OMA at TP3" />
            <Spacer />
            <div style={{ maxWidth: 320 }}>
              <Text size="small" tone="tertiary">
                Margin = delivered − required. With spec-minimum Tx OMA, worst-case TDEC and IL, the spec closes with exactly the 0.2 dB MPI allowance — every implementation dB (better TDEC, lower loss, better Rx) becomes real margin.
              </Text>
            </div>
          </Row>
        </Stack>
      </CardBody>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Analytic sensitivity cross-check (lecture 4 methodology)
// ---------------------------------------------------------------------------
function AnalyticSensitivity() {
  const [inRmsS, setInRms] = useCanvasState("inRms", "2.0");
  const [respS, setResp] = useCanvasState("resp", "0.8");
  const [qSel, setQSel] = useCanvasState("qSel2", "7.03");

  const inRms = parseNum(inRmsS, 2.0); // µA rms input-referred
  const resp = parseNum(respS, 0.8); // A/W
  const q = parseNum(qSel, 7.03);
  // OMA sensitivity is peak-to-peak: OMA_pp = 2 * Q * i_n / R  (Sackinger ch.4)
  const omaW = (2 * q * inRms * 1e-6) / resp;
  const omaDbm = 10 * Math.log10(omaW * 1e3);

  return (
    <Card>
      <CardHeader trailing={<Text size="small" tone="tertiary">OMA_sens = 2·Q·i_n,rms / R</Text>}>
        Analytic sensitivity cross-check (Personick Q, Sackinger ch. 4)
      </CardHeader>
      <CardBody>
        <Stack gap={12}>
          <Row gap={16} align="center" wrap>
            <Row gap={8} align="center">
              <Text size="small">Input-referred noise i_n,rms (µA)</Text>
              <TextInput type="number" value={inRmsS} onChange={setInRms} style={{ width: 80 }} />
            </Row>
            <Row gap={8} align="center">
              <Text size="small">PD responsivity R (A/W)</Text>
              <TextInput type="number" value={respS} onChange={setResp} style={{ width: 80 }} />
            </Row>
            <Row gap={8} align="center">
              <Text size="small">Q for target BER</Text>
              <Select
                value={qSel}
                onChange={setQSel}
                style={{ width: 230 }}
                options={Q_TABLE.map((r) => ({ value: String(r.q), label: `BER ${r.ber} → Q = ${r.q}` }))}
              />
            </Row>
            <Stat value={`${fmt(omaDbm)} dBm`} label="Analytic OMA sensitivity" tone="info" />
          </Row>
          <Text size="small" tone="tertiary">
            Use this to sanity-check the AMI/ADS waterfall: pull i_n,rms from the Caribou TIA model
            (`Caribou/COUPE_models/DR_TIA/TiaModel.py`, integrated over ~2/3 x 53.125 GHz noise bandwidth) and R from the
            PD model. If analytic and simulated sensitivity disagree by more than ~1-2 dB, something in the sim setup
            (noise bandwidth, eye-height threshold, CDR) deserves a look before trusting the budget.
          </Text>
        </Stack>
      </CardBody>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Main canvas
// ---------------------------------------------------------------------------
export default function LinkBudgetCanvas() {
  const chartCategories = WATERFALL.map((p) => fmt(p.oma));
  const chartData = WATERFALL.map((p) => p.log10Ber);

  return (
    <Stack gap={24} style={{ maxWidth: 1000, margin: "0 auto", padding: 24 }}>
      <Stack gap={4}>
        <H1>200G OCI v1.0 — Optical Link Budget</H1>
        <Text tone="secondary">
          Per DWDM channel, 53.125 GBd NRZ, OMA domain. Internal design target: pre-FEC BER 1e-12 (spec compliance
          threshold is 2.4e-4). Spec: 200G OCI Optical PHY Specification v1.0 (Mar 2026). Simulation inputs: Alex's
          COUPE 4+4 BIDI link study in `LM-link-vpiphotonics`.
        </Text>
      </Stack>

      <Grid columns={4} gap={16}>
        <Stat value="-3.5 dBm" label="Tx OMA min @ TDEC 3.4 (TP2)" />
        <Stat value="2.5 dB" label="Fiber link IL max (500 m)" />
        <Stat value="-11.8 dBm" label="Simulated sensitivity @ BER 1e-12" tone="success" />
        <Stat value="5.8 dB" label="Gross margin @ 1e-12, before penalties" tone="info" />
      </Grid>

      <Callout tone="success" title="What the 1e-12 goal costs — and what's left">
        Targeting pre-FEC 1e-12 instead of the spec's 2.4e-4 moves the required OMA from ≈ -16.5 to -11.8 dBm on
        Alex's waterfall — a 4.7 dB sensitivity give-up (steeper than the ~3 dB Gaussian prediction from Q 3.49 → 7.03,
        because the measured curve flattens toward its floor). Even so, with spec-minimum Tx OMA (-3.5 dBm) and
        worst-case 2.5 dB link, -6.0 dBm arrives at TP3 against a -11.8 dBm requirement: 5.8 dB of gross margin for
        crosstalk, MPI, dispersion, aging, and model uncertainty. The budget discipline question becomes: do the
        penalties fit inside 5.8 dB?
      </Callout>

      <Callout tone="info" title="How the spec budget closes">
        Tx OMA min is TDEC-coupled: max(-5.5, -6.9+TDEC). At worst-case TDEC = 3.4 dB the minimum compliant transmitter
        launches -3.5 dBm OMA; after the 2.5 dB worst-case link, -6.0 dBm arrives at TP3 against the -6.2 dBm stressed
        sensitivity limit — exactly the 0.2 dB MPI tolerance. The same 0.2 dB result holds at low TDEC (-5.5 - 2.5 = -8.0
        vs -8.2 unstressed). The spec has zero unallocated margin by construction; real margin comes from beating the
        limits.
      </Callout>

      <BudgetCalculator />

      <Stack gap={8}>
        <H2>Simulated receiver waterfall (Alex's COUPE BIDI link)</H2>
        <LineChart
          categories={chartCategories}
          series={[{ name: "log10(BER), best open-eye contour", data: chartData, tone: "info" }]}
          beginAtZero={false}
          height={280}
          referenceLines={[
            { value: -12, label: "our target 1e-12", tone: "success" },
            { value: -6, label: "spec floor 1e-6", tone: "warning" },
            { value: -3.62, label: "spec pre-FEC 2.4e-4", tone: "danger" },
          ]}
        />
        <Text size="small" tone="tertiary">
          x-axis: Rx OMA (dBm) · y-axis: log10(BER). Source: `sandbox/alex/COUPE_BIDI_PIC_LINK/Results/Waterfall/part1.csv`
          (Oct 2025), processed as in Alex's plot.py — minimum BER contour with eye height &gt; 20 mV per attenuation step,
          Rx OMA = -8.8 dBm − attenuation. The 1e-12 design target is crossed at -11.8 dBm — a directly measured point.
          Spec references: 1e-6 floor at ≈ -15.3 dBm (interpolated), 2.4e-4 at ≈ -16.5 dBm (extrapolated). The gap
          between the delivered TP3 OMA and the -11.8 dBm crossing is the total penalty allowance for the 1e-12 budget.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>Spec parameters that set the budget</H2>
        <Table
          headers={["Parameter", "Spec value", "Where it enters the budget"]}
          rows={[
            ["Tx OMA per channel (TP2)", "min max(-5.5, -6.9+TDEC), max -1 dBm", "Budget start; TDEC-coupled"],
            ["TDEC", "≤ 3.4 dB (SSPR, 26.5625 GHz BT4 ref Rx)", "Couples Tx OMA min and Rx sensitivity"],
            ["Extinction ratio", "3.5 – 4.5 dB", "Links OMA to average power / AOP specs"],
            ["Fiber link", "500 m SMF-28, IL ≤ 2.5 dB, CD -0.9…1.7 ps/nm", "Channel loss line"],
            ["MPI penalty tolerance", "0.2 dB", "Only explicit penalty allocation in the spec"],
            ["Rx sensitivity (OMA)", "max(-8.2, -9.6+TDEC) dBm, PRBS31", "Unstressed Rx limit"],
            ["Stressed Rx sensitivity", "-6.2 dBm (SEC 3.4 dB, aggressors -3.2 dBm)", "Budget end at TP3"],
            ["BER floor", "≤ 1e-6 from (-8.2+TDEC) to -1 dBm", "Overload / dynamic-range check"],
            ["Tx RIN(OMA)", "≤ -138 dB/Hz @ 21.4 dB ORL", "Inside TDEC / SRS stress"],
            ["ELS RIN / linewidth", "≤ -144 dB/Hz / ≤ 1 MHz", "Laser bank model inputs"],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>Mapping budget lines to Alex's artifacts</H2>
        <Table
          headers={["Budget line", "Repo artifact", "Status"]}
          rows={[
            [
              "Rx sensitivity waterfall",
              "sandbox/alex/COUPE_BIDI_PIC_LINK/Results/Waterfall + COUPE_4plus4_BIDI_link.vtmu",
              <Pill size="sm" active>Data available</Pill>,
            ],
            [
              "MPI / coherent crosstalk penalty",
              "Results/MPI (BER_vs_loss.csv, ORL_sweep.csv) — compare at spec ORL 21.4 dB",
              <Pill size="sm" active>Data available</Pill>,
            ],
            [
              "Spectral crosstalk penalty",
              "Results/Spectral_crosstalk (crosstalk / filter / interleaver spectra)",
              <Pill size="sm">Extract dB penalty</Pill>,
            ],
            [
              "Electrical crosstalk penalty",
              "Results/Electrical Crosstalk (XSR aggressor S-params + plotting.py)",
              <Pill size="sm">Extract dB penalty</Pill>,
            ],
            [
              "Dispersion penalty (CD -0.9…1.7 ps/nm)",
              "Results/Chromatic_dispersion (500/2000/5000 m eye comparisons)",
              <Pill size="sm" active>500 m case matches spec</Pill>,
            ],
            [
              "DGD / skew",
              "Results/DGD",
              <Pill size="sm" active>Data available</Pill>,
            ],
            [
              "Tx: TDEC of driver + MRM",
              "Caribou/COUPE_models DR_TxDrv, DR_MRM + COUPE_DR_TDECQ.vtmu testbench",
              <Pill size="sm">Re-run for NRZ TDEC</Pill>,
            ],
            [
              "Rx: TIA + SerDes (CTLE, 1-tap DFE in NRZ)",
              "Caribou/COUPE_models DR_TIA + COUPE_ADS AMI_Skipper_20250103 (skipper_rx)",
              <Pill size="sm" active>Models available</Pill>,
            ],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>IEEE P802.3dj D1.3 cross-reference (Dec 2024 draft)</H2>
        <Text size="small" tone="secondary">
          The OCI MSA closely mirrors Clause 181 (800GBASE-FR4-500: 4 WDM lanes, 500 m) with values recast from
          106.25 GBd PAM4 to 53.125 GBd NRZ. Clause 180 (DR, 500 m parallel SMF) is the second reference point.
          Values below from draft D1.3 — verify against the current draft before signoff.
        </Text>
        <Table
          headers={["Parameter", "OCI MSA v1.0", "Cl. 181 FR4-500", "Cl. 180 DR"]}
          rows={[
            ["Modulation / baud", "53.125 GBd NRZ x 4λ", "106.25 GBd PAM4 x 4λ", "106.25 GBd PAM4 / fiber"],
            ["Reach / channel IL", "500 m / 2.5 dB", "500 m / 3.5 dB", "500 m / 3.0 dB"],
            ["Power budget (max TDEC/Q)", "2.7 dB (implied)", "7.4 dB", "6.5 dB"],
            ["Penalty allocation", "0.2 dB (MPI only)", "3.9 dB (0.5 MPI+DGD)", "3.5 dB (0.1 MPI+DGD)"],
            ["Tx OMA min (worst TDEC/Q)", "-3.5 dBm", "+3.3 dBm", "+2.2 dBm"],
            ["TDEC(Q) / SEC(Q) max", "3.4 / 3.4 dB", "3.4 / 3.4 dB", "3.4 / 3.4 dB"],
            ["Rx sensitivity (OMA, worst Tx)", "-6.2 dBm (SRS)", "-0.7 dBm (SRS)", "-0.9 dBm (SRS)"],
            ["ER min / overshoot max", "3.5 dB / 22%", "3.5 dB / 22%", "3.5 dB / 22%"],
            ["RIN / ORL tolerance", "-138 dB/Hz @ 21.4 dB", "-139 dB/Hz @ 17.1 dB", "-139 dB/Hz @ 21.4 dB"],
            ["Tx/Rx reflectance max", "-19 dB", "-26 dB", "-26 dB"],
            ["Discrete reflectance", "not specified", "-25 to -41 dB by count (Table 181-10)", "-35 dB"],
            ["BER basis", "flat pre-FEC 2.4e-4", "block error ratio, BERadded 6.4e-5 (174A)", "same as 181"],
          ]}
        />
        <Text size="small" tone="tertiary">
          Method pointers for gaps the MSA leaves open: test patterns 120.5.11 (PRBS13Q/31Q, SSPRQ); TDECQ procedure
          121.8.5 as modified by 181.9.5 (reference equalizer: 15-tap T-spaced FFE with constrained pre-cursor taps,
          Table 181-13); SRS conditions 181.9.13; connection loss allocation 181.8.2.1 (3.25 dB over the connectors);
          discrete reflectance vs count 181.8.2.2; error-ratio framework 174A.5-7. Note D1.3 still carries an editor's
          note that the BER target for optical measurements is unresolved — the MSA's flat 2.4e-4 is a deliberate
          simplification (no inner FEC, KP4 only).
        </Text>
      </Stack>

      <Grid columns={2} gap={16}>
        <Stack gap={8}>
          <H3>Personick Q for the spec's BER targets</H3>
          <Table
            headers={["BER", "Q", "Used for"]}
            columnAlign={["left", "right", "left"]}
            rows={Q_TABLE.map((r) => [r.ber, fmt(r.q, 2), r.use])}
          />
          <Text size="small" tone="tertiary">
            BER = 0.5·erfc(Q/√2). Our 1e-12 goal needs Q ≈ 7.03 versus 3.49 at the spec's 2.4e-4 threshold — in an
            amplifier-noise-limited receiver that is 10·log10(7.03/3.49) ≈ 3.0 dB more OMA. The measured waterfall gives
            up 4.7 dB, the extra ~1.7 dB reflecting the curve flattening toward its floor (shot noise, residual ISI,
            eye-height quantization in the sim). Designing to 1e-12 pre-FEC means the KP4 FEC becomes pure margin.
          </Text>
        </Stack>
        <AnalyticSensitivity />
      </Grid>

      <Callout tone="warning" title="Caveats before quoting these numbers">
        <Stack gap={4}>
          <Text size="small">
            1. Repo models are the Oct/Nov 2025 commits — the April 2026 Caribou DR OMNI driver/TIA updates referenced in
            Alex's slide are not in these clones. Re-run with current models before signoff.
          </Text>
          <Text size="small">
            2. The waterfall was produced in the ~56G NRZ ADS workspace; verify the sweep was at 53.125 GBd with
            PRBS31-like data before mapping OMA values onto spec test points.
          </Text>
          <Text size="small">
            3. The -11.8 dBm sensitivity at the 1e-12 target is a directly measured waterfall point (good). But it comes
            from statistical eye contours, not bit-by-bit counting — at 1e-12 the contour method's assumptions (Gaussian
            tails, no burst errors) matter. Cross-check with the analytic Q calculation and, ideally, a longer
            bit-by-bit run around the operating point.
          </Text>
          <Text size="small">
            4. Crosstalk/MPI/dispersion penalties are not folded into the waterfall — enter them in the calculator once
            extracted from the Results studies. Re-running the sims needs VPIphotonics + Keysight ADS licenses.
          </Text>
        </Stack>
      </Callout>
    </Stack>
  );
}
