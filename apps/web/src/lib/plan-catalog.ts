/**
 * Authoritative allowlist for AI learning-plan mutations.
 * Plans may only reference concept_ids present in our KG + lesson index.
 */
import lessonsIndex from './lessons-index.generated.json';
import { isConceptInBundle } from './lesson-bundle';
import { resolveConceptAlias } from './concept-aliases';
import kg from './kg-data.json';

export interface PlanUpdatePayload {
  confirmed: boolean;
  reason: string;
  action?: 'regenerate' | 'adjust';
  goal?: string;
  goal_key?: string;
  next_test_date?: string | null;
  next_test_name?: string | null;
  final_goal_date?: string | null;
  clear_next_test?: boolean;
  hours_per_week?: number;
  priority_concepts?: string[];
  prepend_concepts?: string[];
  exclude_concepts?: string[];
}

interface LessonIndexEntry {
  id: string;
  subject?: string;
  title_en: string;
  title_he?: string;
  math_track?: string[];
  level_min?: string;
}

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
}

const lessons = lessonsIndex as LessonIndexEntry[];
const kgConcepts = (kg as { concepts: KgConcept[] }).concepts;
const kgById = (kg as { byId: Record<string, KgConcept> }).byId;

/** Goals learners pick in onboarding → canonical goal keys. */
export const ONBOARDING_GOALS = [
  { key: 'bagrut_math_3', label_en: 'Bagrut Math 3 units', label_he: 'בגרות מתמטיקה 3 יח׳', points_group: '3pt' },
  { key: 'bagrut_math_4', label_en: 'Bagrut Math 4 units', label_he: 'בגרות מתמטיקה 4 יח׳', points_group: '4pt' },
  { key: 'bagrut_math_5', label_en: 'Bagrut Math 5 units', label_he: 'בגרות מתמטיקה 5 יח׳', points_group: '5pt' },
  { key: 'bagrut_physics', label_en: 'Bagrut Physics', label_he: 'בגרות פיזיקה', points_group: 'hs_physics' },
  { key: 'calculus1', label_en: 'University Calculus 1', label_he: 'חדו״א 1', points_group: 'calc1' },
  { key: 'linear_algebra', label_en: 'Linear Algebra', label_he: 'אלגברה לינארית', points_group: 'la' },
  { key: 'university_prep', label_en: 'General university prep', label_he: 'הכנה לאוניברסיטה', points_group: null },
] as const;

export type OnboardingGoalKey = (typeof ONBOARDING_GOALS)[number]['key'];

const GOAL_KEY_SET = new Set<string>(ONBOARDING_GOALS.map((g) => g.key));

export function lessonAvailable(conceptId: string): boolean {
  const canonical = resolveConceptAlias(conceptId);
  return (
    lessons.some((l) => l.id === conceptId || l.id === canonical) ||
    isConceptInBundle(conceptId) ||
    isConceptInBundle(canonical)
  );
}

/** True if concept exists in the in-house KG (GraphRAG corpus). */
export function isKnownConceptId(conceptId: string): boolean {
  const id = conceptId.trim();
  if (!id) return false;
  const canonical = resolveConceptAlias(id);
  return Boolean(kgById[id] ?? kgById[canonical]);
}

/** Map alias → canonical KG id for planner persistence. */
export function canonicalConceptId(conceptId: string): string | null {
  const id = conceptId.trim();
  if (!id) return null;
  const canonical = resolveConceptAlias(id);
  if (kgById[canonical]) return canonical;
  if (kgById[id]) return id;
  return null;
}

/** Keep only ids that exist in our KG; dedupe; cap length. */
export function sanitizeConceptIds(ids: string[] | undefined, max = 12): string[] {
  if (!ids?.length) return [];
  const out: string[] = [];
  const seen = new Set<string>();
  for (const raw of ids) {
    const canonical = canonicalConceptId(raw);
    if (!canonical || seen.has(canonical)) continue;
    seen.add(canonical);
    out.push(canonical);
    if (out.length >= max) break;
  }
  return out;
}

export function isValidGoalKey(key: string | undefined | null): key is OnboardingGoalKey {
  return Boolean(key && GOAL_KEY_SET.has(key));
}

export function goalKeyToPointsGroup(key: string | undefined | null): string | null {
  if (!isValidGoalKey(key)) return null;
  return ONBOARDING_GOALS.find((g) => g.key === key)?.points_group ?? null;
}

/** Validate + normalize an AI plan-update payload before writing to Neon. */
export function sanitizePlanUpdatePayload(
  payload: PlanUpdatePayload,
): PlanUpdatePayload | null {
  if (!payload.confirmed || !payload.reason?.trim()) return null;

  const goal_key = isValidGoalKey(payload.goal_key) ? payload.goal_key : undefined;

  return {
    ...payload,
    goal_key,
    priority_concepts: sanitizeConceptIds(payload.priority_concepts),
    prepend_concepts: sanitizeConceptIds(payload.prepend_concepts),
    exclude_concepts: sanitizeConceptIds(payload.exclude_concepts),
    clear_next_test: payload.clear_next_test === true ? true : undefined,
  };
}

export function buildLessonCatalogSummary(subjects: string[]): string {
  const subjectSet = new Set(subjects.length ? subjects : ['math', 'physics']);
  const authored = lessons.filter((l) => !l.subject || subjectSet.has(l.subject));
  const withLesson = authored.filter((l) => lessonAvailable(l.id));
  const withoutLesson = kgConcepts
    .filter((c) => subjectSet.has(c.subject))
    .filter((c) => !lessonAvailable(c.id))
    .slice(0, 15);

  const lines: string[] = [];
  lines.push(`Authored lessons on platform (${withLesson.length}):`);
  for (const l of withLesson.slice(0, 35)) {
    const tracks = l.math_track?.length ? ` [${l.math_track.join(', ')}]` : '';
    lines.push(`- ${l.id}: ${l.title_en}${tracks}`);
  }
  if (withLesson.length > 35) {
    lines.push(`- … and ${withLesson.length - 35} more authored lessons`);
  }
  if (withoutLesson.length) {
    lines.push('');
    lines.push('KG concepts WITHOUT an authored lesson yet (tutor must teach live):');
    for (const c of withoutLesson) {
      lines.push(`- ${c.id}: ${c.name}`);
    }
  }
  lines.push('');
  lines.push('Onboarding goal tracks available (goal_key for plan updates):');
  for (const g of ONBOARDING_GOALS) {
    lines.push(`- ${g.key}: ${g.label_en}`);
  }
  return lines.join('\n');
}

/** Compact allowlist injected into Mentor/Tutor prompts for plan mutations. */
export function buildPlanAllowlistBlock(subjects: string[]): string {
  const subjectSet = new Set(subjects.length ? subjects : ['math', 'physics']);
  const plannable = kgConcepts
    .filter((c) => subjectSet.has(c.subject))
    .map((c) => ({
      id: c.id,
      has_lesson: lessonAvailable(c.id),
      name: c.name,
    }));

  const withLesson = plannable.filter((c) => c.has_lesson);
  const lines = [
    'ALLOWLIST — the ONLY concept_id values you may put in priority_concepts / prepend_concepts / exclude_concepts:',
    ...withLesson.slice(0, 60).map((c) => `- ${c.id} (${c.name})`),
  ];
  if (withLesson.length > 60) {
    lines.push(`- … ${withLesson.length - 60} more concepts with authored lessons`);
  }
  lines.push('');
  lines.push('Valid goal_key values ONLY:', ONBOARDING_GOALS.map((g) => g.key).join(', '));
  return lines.join('\n');
}

export const PLAN_GROUNDING_RULES = `
## Learning-plan grounding (mandatory — in-house corpus only)

When discussing, recommending, or **mutating** the learner's weekly plan:
1. **Source of truth** — our knowledge graph (\`kg-data.json\` + \`kg-cross-edges.json\` / GraphRAG), authored lessons (\`lessons\` / static bundle), \`concept_mastery\`, \`skill_practice\`, and the injected **Current weekly learning plan** + **Platform catalog** blocks. This is your RAG — use it exclusively for plans.
2. **Never invent courses** — do NOT recommend Khan Academy, YouTube playlists, external MOOCs, textbooks, or any material outside A Step Forward. If we lack an authored lesson, say so and offer live Tutor coverage or the nearest in-catalog prerequisite.
3. **Valid ids only** — \`ASF_PLAN_UPDATE\` may only use \`concept_id\` values from the ALLOWLIST and \`goal_key\` from onboarding tracks. Invalid ids are stripped server-side and will NOT appear in the dashboard plan.
4. **Persisted writes** — the weekly plan lives in Neon (\`learning_plans\` + \`plan_weeks\`). It changes ONLY after the learner explicitly confirms AND you emit \`[[ASF_PLAN_UPDATE:...]]\` with \`confirmed:true\`.
5. **Outside research** — general enrichment or motivation may use broad knowledge, but **never** mix external resources into plan construction or weekly milestones.

Use \`GET /api/learning-plan/next?goal=<concept_id>\` for mastery-aware sequencing — do not hand-walk prerequisites.
`.trim();
