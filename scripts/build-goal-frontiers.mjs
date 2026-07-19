#!/usr/bin/env node
/**
 * Build the goal-frontier manifest that ADR-0009 (goal-paced adaptive planning)
 * consumes for deadline pacing.
 *
 * The frontier is DERIVED from the knowledge graph — it is not hand-authored.
 * For each goal key we compute the set of KG concepts that fall inside the goal's
 * subject(s) and allowed Bagrut/points levels, plus the goal terminal concept and
 * all of its transitive prerequisites. The set is topologically ordered by
 * prerequisite depth (foundations first), and each concept is flagged with:
 *
 *   - depth      – longest prereq chain within the frontier (0 = a root)
 *   - downstream – number of frontier concepts that depend on it directly
 *   - critical   – true when it is a transitive prereq of the goal terminal OR
 *                  its downstream degree is high (see FANOUT_CRITICAL). This is the
 *                  conservative "critical when ambiguous" default from ADR-0009 §3.
 *
 * A thin, optional override file (goal-frontiers.overrides.json) may reorder,
 * add/remove core concepts, define the stretch set, or flip criticality. Overrides
 * are the ONLY hand-authored layer; everything else stays in sync with the KG.
 *
 * Output: apps/web/src/lib/goal-frontiers.generated.json
 *
 * Run manually when the KG or overrides change:
 *   node scripts/build-goal-frontiers.mjs
 *
 * The generated file is committed and validated in CI by
 * apps/web/src/lib/goal-frontiers.test.ts (coverage gate).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const LIB_DIR = path.join(ROOT, 'apps', 'web', 'src', 'lib');
const KG_FILE = path.join(LIB_DIR, 'kg-data.json');
const CROSS_EDGES_FILE = path.join(LIB_DIR, 'kg-cross-edges.json');
const OVERRIDES_FILE = path.join(LIB_DIR, 'goal-frontiers.overrides.json');
const OUT_FILE = path.join(LIB_DIR, 'goal-frontiers.generated.json');

const MANIFEST_VERSION = 1;
/** Concept is goal_critical when at least this many frontier concepts depend on it directly. */
const FANOUT_CRITICAL = 4;

// ---------------------------------------------------------------------------
// Goal configuration.
//
// These mirror the runtime source of truth and MUST stay in sync:
//   - goal keys + points_group → apps/web/src/lib/plan-catalog.ts (ONBOARDING_GOALS)
//   - goal → terminal concept   → apps/web/src/lib/plan-worklist.ts (DEFAULT_GOAL_CONCEPT_BY_GOAL_KEY)
//   - terminal id fallbacks      → apps/web/src/lib/plan-worklist.ts (PLANNER_GOAL_KG_FALLBACK)
//   - points_group → levels      → apps/web/src/lib/quiz-concept-filter.ts (allowedLevelsForProfile)
// ---------------------------------------------------------------------------

/** goal_key → terminal concept id (may be a synthetic id resolved via TERMINAL_FALLBACK). */
const GOAL_TERMINAL = {
  bagrut_math_3: 'linear_programming_two_variables',
  bagrut_math_4: 'function_analysis_4pt',
  bagrut_math_5: 'function_analysis_5pt',
  bagrut_physics: 'newton_laws',
  calculus1: 'derivatives_intro',
  linear_algebra: 'la_matrices',
  university_prep: 'calculus_intro_makhina',
  makhina: 'calculus_intro_makhina',
};

/** Synthetic/syllabus terminal id → concrete KG concept id. */
const TERMINAL_FALLBACK = {
  function_analysis_4pt: 'function_analysis_extrema',
  function_analysis_5pt: 'function_analysis_asymptotes',
  linear_programming_two_variables: 'functions_linear',
  calculus_intro_makhina: 'limits',
};

/** goal_key → points_group (university_prep has null in onboarding → full HS math scope). */
const GOAL_POINTS_GROUP = {
  bagrut_math_3: '3pt',
  bagrut_math_4: '4pt',
  bagrut_math_5: '5pt',
  bagrut_physics: 'hs_physics',
  calculus1: 'calc1',
  linear_algebra: 'la',
  university_prep: '5pt',
  makhina: '5pt',
};

/** goal_key → subjects the frontier draws from. */
const GOAL_SUBJECTS = {
  bagrut_math_3: ['math'],
  bagrut_math_4: ['math'],
  bagrut_math_5: ['math'],
  bagrut_physics: ['physics'],
  calculus1: ['math'],
  linear_algebra: ['math'],
  university_prep: ['math'],
  makhina: ['math'],
};

/**
 * points_group → allowed core levels.
 *
 * NOTE: this is intentionally TIGHTER than quiz-concept-filter.ts:allowedLevelsForProfile.
 * That function is a permissive quiz ALLOWLIST (a learner may practice anything at or
 * below their track). A goal FRONTIER is the concept set the goal actually requires, so
 * university tracks include HS foundations + their OWN university level, not every
 * university level (calc1 must not pull in linear-algebra concepts, and vice versa).
 */
const POINTS_GROUP_CORE_LEVELS = {
  '3pt': ['3pt'],
  '4pt': ['3pt', '4pt'],
  '5pt': ['3pt', '4pt', '5pt'],
  hs_physics: ['hs_physics'],
  calc1: ['3pt', '4pt', '5pt', 'calc1'],
  la: ['3pt', '4pt', '5pt', 'la'],
  physics1: ['hs_physics', 'physics1'],
};

/** goal_key → stretch levels (one tier above the goal; drives adaptive ambition, ADR-0009 §5). */
const GOAL_STRETCH_LEVELS = {
  bagrut_math_3: ['4pt'],
  bagrut_math_4: ['5pt'],
  bagrut_math_5: ['calc1', 'la'],
  bagrut_physics: ['physics1'],
  calculus1: ['la'],
  linear_algebra: ['calc1'],
  university_prep: ['calc1', 'la'],
  makhina: ['calc1', 'la'],
};

// ---------------------------------------------------------------------------
// Load inputs.
// ---------------------------------------------------------------------------

const kg = JSON.parse(fs.readFileSync(KG_FILE, 'utf-8'));
const concepts = kg.concepts ?? [];
const byId = kg.byId ?? Object.fromEntries(concepts.map((c) => [c.id, c]));
const prereqMap = kg.prereqMap ?? Object.fromEntries(concepts.map((c) => [c.id, c.prerequisites ?? []]));

let crossEdges = [];
try {
  const cross = JSON.parse(fs.readFileSync(CROSS_EDGES_FILE, 'utf-8'));
  crossEdges = cross.edges ?? [];
} catch {
  crossEdges = [];
}

let overrides = {};
try {
  overrides = JSON.parse(fs.readFileSync(OVERRIDES_FILE, 'utf-8'));
} catch {
  overrides = {};
}

// ---------------------------------------------------------------------------
// Helpers.
// ---------------------------------------------------------------------------

function resolveTerminal(goalKey) {
  const raw = GOAL_TERMINAL[goalKey];
  if (!raw) return null;
  if (byId[raw]) return raw;
  const fb = TERMINAL_FALLBACK[raw];
  if (fb && byId[fb]) return fb;
  return null;
}

/** All transitive prerequisites of `start` (inclusive), restricted to `allowed`. */
function ancestorsOf(start, allowed) {
  const seen = new Set();
  const stack = [start];
  while (stack.length) {
    const id = stack.pop();
    if (seen.has(id)) continue;
    seen.add(id);
    for (const p of prereqMap[id] ?? []) {
      if (allowed.has(p) && !seen.has(p)) stack.push(p);
    }
  }
  return seen;
}

/** Longest prereq chain length within `set` (0 = root). Cycle-safe. */
function depthWithin(id, set, memo, onStack) {
  if (memo.has(id)) return memo.get(id);
  if (onStack.has(id)) return 0; // break cycles defensively
  onStack.add(id);
  let d = 0;
  for (const p of prereqMap[id] ?? []) {
    if (set.has(p)) d = Math.max(d, depthWithin(p, set, memo, onStack) + 1);
  }
  onStack.delete(id);
  memo.set(id, d);
  return d;
}

function buildFrontier(goalKey) {
  const subjects = new Set(GOAL_SUBJECTS[goalKey] ?? ['math']);
  const pointsGroup = GOAL_POINTS_GROUP[goalKey] ?? '5pt';
  const allowedLevels = new Set(POINTS_GROUP_CORE_LEVELS[pointsGroup] ?? []);
  const stretchLevels = new Set(GOAL_STRETCH_LEVELS[goalKey] ?? []);
  const terminal = resolveTerminal(goalKey);
  const ov = overrides[goalKey] ?? {};

  const inSubject = (c) => subjects.has(c.subject);
  const levelMatch = (c, levels) => {
    const pl = c.points_levels ?? [];
    if (pl.length === 0) return true; // untagged concepts are level-agnostic
    return pl.some((l) => levels.has(l));
  };

  // Core set: subject-scoped concepts at or below the goal level ...
  const core = new Set();
  for (const c of concepts) {
    if (inSubject(c) && levelMatch(c, allowedLevels)) core.add(c.id);
  }
  // ... always union the terminal + its transitive prerequisites so the goal is
  // reachable even if a spine concept is tagged at an unexpected level.
  if (terminal) {
    const subjectUniverse = new Set(concepts.filter(inSubject).map((c) => c.id));
    for (const id of ancestorsOf(terminal, subjectUniverse)) core.add(id);
  }
  // Apply overrides.
  for (const id of ov.add_core ?? []) if (byId[id]) core.add(id);
  for (const id of ov.remove_core ?? []) core.delete(id);

  // Depth + direct downstream degree within the core set.
  const depthMemo = new Map();
  const downstream = new Map();
  for (const id of core) downstream.set(id, 0);
  for (const id of core) {
    for (const p of prereqMap[id] ?? []) {
      if (core.has(p)) downstream.set(p, (downstream.get(p) ?? 0) + 1);
    }
  }

  // Criticality: transitive prereqs of the terminal, or high fan-out. Overridable.
  const criticalSet = terminal ? ancestorsOf(terminal, core) : new Set();
  const forceCritical = new Set(ov.critical ?? []);
  const forceNotCritical = new Set(ov.not_critical ?? []);
  const isCritical = (id) => {
    if (forceNotCritical.has(id)) return false;
    if (forceCritical.has(id)) return true;
    if (criticalSet.has(id)) return true;
    return (downstream.get(id) ?? 0) >= FANOUT_CRITICAL;
  };

  // Order: overrides.order first (in given order), then by (depth asc, downstream desc, id).
  const onStack = new Set();
  const coreArr = [...core].map((id) => ({
    id,
    depth: depthWithin(id, core, depthMemo, onStack),
    downstream: downstream.get(id) ?? 0,
    critical: isCritical(id),
  }));
  const pinned = (ov.order ?? []).filter((id) => core.has(id));
  const pinnedRank = new Map(pinned.map((id, i) => [id, i]));
  coreArr.sort((a, b) => {
    const pa = pinnedRank.has(a.id) ? pinnedRank.get(a.id) : Number.POSITIVE_INFINITY;
    const pb = pinnedRank.has(b.id) ? pinnedRank.get(b.id) : Number.POSITIVE_INFINITY;
    if (pa !== pb) return pa - pb;
    if (a.depth !== b.depth) return a.depth - b.depth;
    if (a.downstream !== b.downstream) return b.downstream - a.downstream;
    return a.id.localeCompare(b.id);
  });

  // Stretch set: one tier above the goal (subject-scoped) + applies_to/generalizes
  // cross-edge neighbors of core concepts. Excludes anything already in core.
  const stretch = new Set();
  if (ov.stretch && ov.stretch.length) {
    for (const id of ov.stretch) if (byId[id] && !core.has(id)) stretch.add(id);
  } else {
    for (const c of concepts) {
      if (inSubject(c) && !core.has(c.id) && levelMatch(c, stretchLevels) && (c.points_levels ?? []).length > 0) {
        stretch.add(c.id);
      }
    }
    for (const e of crossEdges) {
      if (e.relation !== 'applies_to' && e.relation !== 'generalizes') continue;
      // A concept the goal work "applies to" or "generalizes into" is enrichment.
      if (core.has(e.src) && byId[e.dst] && !core.has(e.dst)) stretch.add(e.dst);
    }
  }

  return {
    goal_key: goalKey,
    subjects: [...subjects],
    points_group: pointsGroup,
    allowed_levels: [...allowedLevels],
    stretch_levels: [...stretchLevels],
    terminal_concept: terminal,
    core: coreArr,
    stretch: [...stretch].sort(),
    core_count: coreArr.length,
    critical_count: coreArr.filter((c) => c.critical).length,
  };
}

// ---------------------------------------------------------------------------
// Build all goals + write output.
// ---------------------------------------------------------------------------

const goals = {};
for (const goalKey of Object.keys(GOAL_TERMINAL)) {
  goals[goalKey] = buildFrontier(goalKey);
}

const output = {
  version: MANIFEST_VERSION,
  generated_at: new Date().toISOString(),
  fanout_critical: FANOUT_CRITICAL,
  goals,
};

fs.writeFileSync(OUT_FILE, `${JSON.stringify(output, null, 2)}\n`);

// Human-readable summary.
console.log(`Wrote goal frontiers → ${path.relative(ROOT, OUT_FILE)}`);
for (const [key, g] of Object.entries(goals)) {
  const flag = g.terminal_concept && g.core.some((c) => c.id === g.terminal_concept) ? 'ok' : 'MISSING TERMINAL';
  console.log(
    `  ${key.padEnd(16)} core=${String(g.core_count).padStart(3)} critical=${String(g.critical_count).padStart(3)} stretch=${String(g.stretch.length).padStart(3)} terminal=${g.terminal_concept ?? 'none'} [${flag}]`,
  );
}
