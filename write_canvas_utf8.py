canvas = r"""import {
  Stack, Row, Grid, H1, H2, Text, Card, CardHeader, CardBody,
  Table, Pill, Stat, Divider, Spacer, Callout,
  useHostTheme, BarChart,
} from "cursor/canvas";

const PERSONAS = [
  {
    id: "S01", name: "Itay Ben-David", track: "4pt Math", grade: "11th",
    prevScores: [6.0, 7.0, 7.5], r4Score: 7.8, verdict: "improving",
    scenario: "equations_linear, exponents, and algebra_basics are all artifact-free (0 markers confirmed). Artifact removal eliminates broken interstitial content. However, English fallbacks persist: equations_linear 4pt worked-example contains full English prose, and analytic_geometry 4pt body_by_level has truncated LaTeX. Section navigation intact.",
    fixes: ["0 artifacts in equations_linear, exponents, algebra_basics (v3 script confirmed)", "4pt Hebrew body_by_level present across all equations_linear sections", "algebra_basics 3pt/4pt adaptive Hebrew content intact (637-819 chars/section)", "Section label navigation unchanged and functional"],
    pains: ["equations_linear 4pt special-cases body_he_md = English text (EN fallback in Hebrew field)", "analytic_geometry 4pt LaTeX broken: missing opening dollar sign in circle/parabola formulas", "No Bagrut exam mode -- biggest feature gap for exam prep", "Hebrew phrasing unnatural in several sections"],
    delta: "+0.3",
  },
  {
    id: "S02", name: "Noa Levi", track: "5pt Math", grade: "12th",
    prevScores: [7.0, 7.5, 8.0], r4Score: 8.2, verdict: "improving",
    scenario: "4 new 5pt focus-directrix questions in analytic_geometry are present, bilingual, correct. The 5pt body_by_level section has proper Hebrew focus-directrix theory. However, Q7-Q10 use a different schema (body_en/answer_en) vs original Q1-Q6 (stem_en/correct_index), creating a schema inconsistency. limits pitfall and summary sections still have English fallbacks in 5pt Hebrew fields.",
    fixes: ["4 new 5pt questions: focus F(0,3)/directrix, focus from y=x2/8, PF at x=4, vertex-as-midpoint -- all correct", "analytic_geometry 5pt body_by_level: proper Hebrew parabola-as-locus content", "0 artifacts in functions_linear, limits, trigonometry_identities", "Hebrew in trigonometry_identities present and meaningful"],
    pains: ["Q7-Q10 schema mismatch (body_en/answer_en vs stem_en/correct_index) -- may not render via same quiz component", "limits pitfall 5pt Hebrew = English text", "limits summary 5pt Hebrew = English text", "No Bagrut exam mode -- critical for 12th grade"],
    delta: "+0.2",
  },
  {
    id: "S03", name: "Yossi Mizrahi", track: "3pt Math", grade: "10th",
    prevScores: [7.0, 7.5, 7.5], r4Score: 7.5, verdict: "stalled",
    scenario: "Yossi's critical stall point -- the arithmetic 3pt theory section -- remains broken despite artifact removal. body_he_md contains full English text starting with 'The number system is based on four main types...' Since this is the gateway lesson's first theory section, it immediately undermines trust. Exponents 3pt is clean, as is algebra_basics.",
    fixes: ["0 artifacts in exponents -- 6 sections with proper 3pt Hebrew (379-563 chars each)", "0 artifacts in arithmetic -- 5 sections structured correctly", "algebra_basics 3pt content intact (521-819 chars Hebrew per section)", "Section navigation for 3pt curriculum working"],
    pains: ["CRITICAL: arithmetic 3pt theory body_he_md = English text (EN fallback -- gateway lesson broken)", "arithmetic theory Hebrew begins: 'The number system is based on four main types...' -- untranslated", "No explain-simpler button -- Yossi needs more scaffolding", "No Done marking after completing a lesson"],
    delta: "0.0",
  },
  {
    id: "S04", name: "Amir Shapira", track: "HS Physics", grade: "11th",
    prevScores: [7.0, 8.0, 8.0], r4Score: 8.2, verdict: "improving",
    scenario: "All three plateau lessons (electric_potential, electric_circuits, simple_harmonic_motion) are now artifact-free with 5 sections and 6 questions each. Hebrew content is present but thin: electric_potential theory has 452 Hebrew chars vs 1454 English chars (~31%), suggesting translation stubs. Artifact removal alone moves the score up, but Hebrew depth and absence of simulation keep him from 8.5.",
    fixes: ["0 artifacts in electric_potential (5 secs, 6 qs)", "0 artifacts in electric_circuits (5 secs, 6 qs)", "0 artifacts in simple_harmonic_motion (5 secs, 6 qs)", "waves_basics, optics_geometric, optics_physical presence confirmed"],
    pains: ["Hebrew thin in physics: electric_potential theory HE=452 vs EN=1454 chars (~31%)", "electric_circuits theory HE=389 vs EN=1127 chars (~34%) -- abbreviated", "No simulation or interactive diagram for SHM/circuits", "No Done progress marking"],
    delta: "+0.2",
  },
  {
    id: "S05", name: "Maya Stern", track: "Linear Algebra", grade: "Univ prep",
    prevScores: [4.0, 7.0, 8.0], r4Score: 8.3, verdict: "improving",
    scenario: "la_eigenvalues Hebrew is now proper mathematical Hebrew across all 5 sections (terms like erchin atzmiim, polinomien maayen, diagona used correctly). All 4 LA lessons accessible with 5 sections and 6 questions each. However, la_determinants, la_diagonalization, la_orthogonality still have stub-level Hebrew (73-124 chars per section -- barely a sentence). complex_numbers and continuity are artifact-free.",
    fixes: ["la_eigenvalues: all 5 sections have proper mathematical Hebrew (139-368 chars, up from broken R3)", "la_eigenvalues Hebrew confirmed: proper eigen terms, characteristic polynomial, diagonalization", "All 4 LA lessons: 5 sections + 6 questions each -- full chain accessible", "0 artifacts in complex_numbers and continuity"],
    pains: ["la_determinants Hebrew stubs: 92-124 chars per section (incomplete)", "la_diagonalization Hebrew stubs: 73-117 chars per section", "la_orthogonality Hebrew stubs: 90-113 chars per section", "la_eigenvalues worked-example title says complex eigenvalues but shows real eigenvalues -- misleading"],
    delta: "+0.3",
  },
  {
    id: "S06", name: "Tamar Cohen", track: "3pt Math", grade: "10th",
    prevScores: [6.0, 7.0, 7.5], r4Score: 7.5, verdict: "stalled",
    scenario: "Tamar's lesson files are artifact-free but the same English fallback as Yossi hits her: arithmetic theory 3pt body_he_md is English text. For a disengaged student, a Hebrew-platform that shows English theory causes immediate dropout. The critical re-engagement nudge remains unbuilt. functions_linear 3pt Hebrew uses 'hagradvient' for slope -- wrong register for 3pt.",
    fixes: ["0 artifacts in arithmetic, exponents, algebra_basics, functions_linear", "exponents 3pt Hebrew present across 6 sections (379-563 chars each)", "functions_linear 3pt Hebrew present (280-346 chars per section)", "algebra_basics 3pt adaptive content intact"],
    pains: ["CRITICAL: arithmetic 3pt theory body_he_md = English text -- same EN fallback as S03, gateway broken", "No re-engagement nudge after absence -- biggest retention risk for disengaged student", "functions_linear 3pt Hebrew uses incorrect terminology for slope", "No Done progress marking -- no gamification for struggling student"],
    delta: "0.0",
  },
];

const R5_ITEMS = [
  { priority: "P0", item: "Fix arithmetic 3pt theory body_he_md English fallback", impact: "Unblocks S03 (Yossi) + S06 (Tamar) -- 2 stalled students", effort: "Low" },
  { priority: "P0", item: "Normalize analytic_geometry Q7-Q10 schema to match Q1-Q6", impact: "Ensures 5pt questions render for Noa (S02)", effort: "Low" },
  { priority: "P1", item: "Expand la_determinants/diagonalization/orthogonality Hebrew stubs", impact: "Pushes Maya (S05) past 8.5 threshold", effort: "Medium" },
  { priority: "P1", item: "Fix limits pitfall+summary 5pt Hebrew fallbacks", impact: "Improves Noa (S02) calculus Hebrew", effort: "Low" },
  { priority: "P1", item: "Fix analytic_geometry 4pt LaTeX truncation (missing opening $)", impact: "Fixes broken math rendering for Itay (S01)", effort: "Low" },
  { priority: "P2", item: "Add re-engagement nudge for absent learners", impact: "Retention for Tamar (S06) -- biggest behavioral blocker", effort: "High" },
  { priority: "P2", item: "Add Bagrut exam mode (timed past-paper)", impact: "Critical for S01 + S02 exam prep", effort: "High" },
];

const AVG = PERSONAS.reduce((a, b) => a + b.r4Score, 0) / PERSONAS.length;
const SATISFIED = PERSONAS.filter((p) => p.r4Score >= 8.5).length;

function VPill({ v }: { v: string }) {
  const tone = v === "stalled" ? "warning" : v === "improving" ? "success" : "neutral";
  return <Pill tone={tone as any}>{v}</Pill>;
}

export default function QARound4() {
  const { tokens } = useHostTheme();

  const chartData = [
    { name: "R1", ...Object.fromEntries(PERSONAS.map((p) => [p.id, p.prevScores[0]])) },
    { name: "R2", ...Object.fromEntries(PERSONAS.map((p) => [p.id, p.prevScores[1]])) },
    { name: "R3", ...Object.fromEntries(PERSONAS.map((p) => [p.id, p.prevScores[2]])) },
    { name: "R4", ...Object.fromEntries(PERSONAS.map((p) => [p.id, p.r4Score])) },
  ];
  const series = PERSONAS.map((p) => ({ key: p.id, label: p.id }));

  return (
    <Stack gap={24} style={{ padding: 24, maxWidth: 1100 }}>
      <Stack gap={4}>
        <H1>QA Evaluation - Round 4</H1>
        <Text tone="secondary">
          A Step Forward - All 6 student personas - Post-v3 artifact removal + eigenvalues Hebrew + analytic_geometry 5pt questions
        </Text>
      </Stack>
      <Grid columns={4} gap={12}>
        <Card><CardBody><Stat label="Avg Score R4" value={AVG.toFixed(2)} /></CardBody></Card>
        <Card><CardBody><Stat label="Satisfied (>=8.5)" value={SATISFIED + " / 6"} tone="neutral" /></CardBody></Card>
        <Card><CardBody><Stat label="Improving" value={String(PERSONAS.filter((p) => p.verdict === "improving").length)} tone="success" /></CardBody></Card>
        <Card><CardBody><Stat label="Stalled" value={String(PERSONAS.filter((p) => p.verdict === "stalled").length)} tone="warning" /></CardBody></Card>
      </Grid>
      <Stack gap={8}>
        <H2>Score Progression R1-R4</H2>
        <BarChart
          data={chartData}
          series={series}
          xAxisKey="name"
          height={220}
          yDomain={[5, 9]}
          caption="Score per round per student - Scale 0-10 - Satisfaction threshold = 8.5"
        />
      </Stack>
      <Divider />
      <H2>Persona Evaluations</H2>
      <Stack gap={16}>
        {PERSONAS.map((p) => (
          <Card key={p.id}>
            <CardHeader
              label={p.id + " - " + p.name}
              description={p.track + " / " + p.grade}
              trailing={
                <Row gap={8} align="center">
                  <Text
                    weight="bold"
                    style={{
                      color: p.r4Score >= 8.5 ? tokens.text.success : p.r4Score >= 8.0 ? tokens.text.accent : tokens.text.warning,
                      fontSize: 15,
                    }}
                  >
                    {p.r4Score.toFixed(1)}
                  </Text>
                  <VPill v={p.verdict} />
                </Row>
              }
            />
            <CardBody>
              <Stack gap={12}>
                <Text tone="secondary" size="small">{p.scenario}</Text>
                <Divider />
                <Grid columns={2} gap={12}>
                  <Stack gap={6}>
                    <Text weight="semibold" size="small">Verified fixes</Text>
                    {p.fixes.map((f, i) => (
                      <Row key={i} gap={6} align="start">
                        <Text size="small" style={{ color: tokens.text.success }}>+</Text>
                        <Text tone="secondary" size="small">{f}</Text>
                      </Row>
                    ))}
                  </Stack>
                  <Stack gap={6}>
                    <Text weight="semibold" size="small">Remaining pain points</Text>
                    {p.pains.map((pt, i) => (
                      <Row key={i} gap={6} align="start">
                        <Text size="small" style={{ color: tokens.text.warning }}>!</Text>
                        <Text tone="secondary" size="small">{pt}</Text>
                      </Row>
                    ))}
                  </Stack>
                </Grid>
                <Divider />
                <Row gap={8} align="center">
                  <Text tone="secondary" size="small">Score history:</Text>
                  {[...p.prevScores, p.r4Score].map((s, i) => (
                    <Text key={i} size="small" weight={i === 3 ? "bold" : "normal"} tone={i === 3 ? "primary" : "tertiary"}>
                      R{i + 1}: {s.toFixed(1)}{i < 3 ? " ->" : ""}
                    </Text>
                  ))}
                  <Spacer />
                  <Text size="small" weight="semibold" style={{ color: p.delta.startsWith("+") ? tokens.text.success : tokens.text.warning }}>
                    {p.delta}
                  </Text>
                </Row>
              </Stack>
            </CardBody>
          </Card>
        ))}
      </Stack>
      <Divider />
      <H2>Round Summary</H2>
      <Table
        headers={["ID", "Student", "Track", "R3", "R4", "Delta", "Verdict"]}
        rows={PERSONAS.map((p) => [
          p.id,
          p.name,
          p.track,
          p.prevScores[2].toFixed(1),
          p.r4Score.toFixed(1),
          p.delta,
          <VPill key={p.id} v={p.verdict} />,
        ])}
        columnAlign={["left", "left", "left", "center", "center", "center", "left"]}
        rowTone={PERSONAS.map((p) => (p.verdict === "stalled" ? "warning" : p.r4Score >= 8.5 ? "success" : "neutral"))}
        striped
      />
      <Divider />
      <H2>Round 5 Backlog</H2>
      <Table
        headers={["Priority", "Fix", "Impact", "Effort"]}
        rows={R5_ITEMS.map((item) => [
          <Pill key={item.priority} tone={item.priority === "P0" ? "danger" : item.priority === "P1" ? "warning" : "neutral"}>
            {item.priority}
          </Pill>,
          item.item,
          item.impact,
          item.effort,
        ])}
        columnAlign={["center", "left", "left", "left"]}
        striped
      />
      <Divider />
      <Callout tone="info">
        <Text weight="semibold">Recommendation: Continue loop - Round 5</Text>
        <Text tone="secondary" size="small">
          0 of 6 students have reached the 8.5 satisfied threshold. Two P0 data fixes (arithmetic 3pt EN-fallback + analytic_geometry schema normalization) are low-effort and would immediately unblock 2 stalled students and stabilize S02 new questions. Three P1 fixes (LA Hebrew stubs, limits fallbacks, analytic_geometry LaTeX) can be batched. Feature work (exam mode, re-engagement nudge) should be scoped as a separate engineering sprint.
        </Text>
      </Callout>
    </Stack>
  );
}
"""

path = r'C:\Users\roeeh\.cursor\projects\empty-window\canvases\qa-round4-evaluation.canvas.tsx'
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(canvas)
print('Done, bytes:', len(canvas.encode('utf-8')))
