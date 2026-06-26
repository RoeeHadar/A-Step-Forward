---
name: use-learning-plan
description: How to consume the mastery-aware learning-plan endpoint (/api/learning-plan/next) and the buildLearningPlan() library from agents, UI, or scripts. Read BEFORE adding any "what should I study next?" / "why am I stuck?" feature, or wiring a new agent to the path planner.
---

# Use Learning Plan

## When to use

- Any agent that needs to answer "what should I study next?" or "why am I stuck on X?".
- Any UI that surfaces a learning path, a recommended next lesson, or a root-cause diagnosis.
- The Curriculum Designer's `milestones[]` — always drawn from `path[]`, never hand-walked.
- The Progress Analyzer's `gaps[]` + `interventions[]` — always drawn from `blocking_atoms[]`.

## What the planner does

`apps/web/src/lib/learning-plan.ts` walks the combined knowledge graph
(`kg-data.json` within-subject `prerequisites[]` + `kg-cross-edges.json` curated
cross-subject edges, both loaded into Postgres `kg_edges`) BACKWARD from a goal
concept, weighing each prerequisite by the learner's per-atom mastery in
`skill_practice`. It returns:

```ts
{
  goal: { concept_id, name, name_he, subject },
  path: Array<{
    concept_id: string,
    name: string,
    name_he: string | null,
    relation: 'prereq' | 'applies_to' | 'generalizes' | 'models' | 'tooling_for',
    urgency: number,           // 0..1; higher = study sooner
    hasLesson: boolean,        // is there an authored lesson?
    weak_atoms: Array<{ atom: string, mastery: number }>,
    why_en: string,            // one-line rationale
    why_he: string,
  }>,
  blocking_atoms: Array<{ atom: string, mastery: number, blocks_concepts: string[] }>,
}
```

`urgency` already accounts for the learner's mastery — the planner will never
recommend a concept the learner already nailed. `blocking_atoms[]` is sorted by
"how many distinct downstream concepts each atom touches × (1 - mastery)" — the
single most useful field for root-cause diagnosis.

## From a runtime agent (server-side, recommended)

Import directly — no HTTP round-trip:

```ts
import { buildLearningPlan } from '@/lib/learning-plan';

const plan = await buildLearningPlan({
  learnerId,                    // Clerk userId
  goalConceptId: 'derivatives_applications',
  maxNodes: 6,                  // truncate path length; default 6
}).catch(() => null);

if (plan && plan.path.length > 0) {
  // Use plan.path and plan.blocking_atoms directly.
}
```

This is exactly what `apps/web/src/app/api/chat/route.ts` does to inject the
`## Learning-plan snapshot` block into the chat system prompt for tutor / coach
/ qa_explainer / curriculum_designer / progress_analyzer.

## From a client / external caller

```
GET /api/learning-plan/next?goal=<concept_id>&max=8
Authorization: Clerk JWT (sent automatically by the browser)
```

Returns 200 with the JSON shape above, 401 if unauthenticated, 400 if `goal` is
unknown, 404 if the goal concept has no traversable prerequisites.

## How agents should use the snapshot

### Curriculum Designer
1. Your `milestones[]` MUST be drawn from `path[]` in order. The planner has
   already filtered out concepts the learner mastered.
2. Use `blocking_atoms` to write `rationale`: "I sequenced X before Y because
   your `area_scale_factor` and `proportion_solve` atoms are below 30% mastery
   and both downstream concepts exercise them."
3. If `hasLesson: false` for the next step, surface as a constraint: "we don't
   have an authored lesson yet, so I'll have the Tutor teach it live."
4. `estimated_weeks` = `path.length` × the learner's `hours_per_week` bucket.

### Progress Analyzer
1. Lowest-mastery `blocking_atoms[]` entries are your gaps.
2. For each, name the atom AND the concrete behaviour (use the matching
   lesson's `agent_hints.common_misconceptions` to phrase it concretely).
3. Map each blocking atom to the EARLIEST `path[]` concept that teaches it
   (`hasLesson: true` first). That's the intervention.
4. Set `at_risk` if any blocking atom touches 3+ distinct downstream concepts.

### Tutor
- When the learner asks "what should I study next?", reply with the top 2–3
  `path[]` entries and one `weak_atom` from each as the WHY.
- Don't hand-walk `kg.related_concepts` — that's mastery-blind.

### Coach
- Drill the top-urgency node's `weak_atoms` — that's the atom-level granularity
  Progress Analyzer would point to.
- Skip drilling atoms with mastery > 0.8 even if the concept is on the path —
  the planner already accounts for that, but you should too at the drill level.

### Q&A Explainer
- Only invoke when the learner literally asks "where am I weak?". Don't proactively
  inject paths into factual answers.

## Adding a new edge to the graph

Edges live in two places:

1. **Within-subject prereqs**: `apps/web/src/lib/kg-data.json` (sourced from
   `content/knowledge-graph/<subject>-*.yaml`; rebuild via
   `node scripts/build-kg-json.mjs`).
2. **Cross-subject + high-leverage**: `apps/web/src/lib/kg-cross-edges.json`,
   then re-seed via `gh workflow run "Seed DB (one-shot)" -f target=lessons`
   (the seeder also upserts kg_edges).

See `skills/cross-subject-kg/SKILL.md` for the full edge-authoring workflow.

## Performance

The planner is a BFS with a hard cap of 200 visited nodes and a per-call
budget of ~300ms on Vercel (cold start: ~700ms). It runs server-side and the
chat route awaits it inline, so keep `maxNodes` ≤ 8 in production.

## Pitfalls

- ❌ Don't call `buildLearningPlan` for every chat turn — the chat route already
  caches the relevant concepts and only invokes it when a concept is mentioned.
- ❌ Don't hand-walk `kg-data.json` prerequisites in agent prompts — you'll
  miss the cross-subject edges and won't weigh by mastery. Always use
  `learning_plan.next(goal)`.
- ❌ Don't tell a learner "your urgency for X is 0.82" — that's an internal
  signal. Translate to a sentence like "your `area_scale_factor` mastery is
  ~28%, which blocks volumes, ratios, and similar triangles."
- ❌ Don't trust `hasLesson: false` paths as if they're as good as authored
  ones — degrade gracefully: "no authored lesson yet; the Tutor will teach it
  live or I can generate exercises."
