/**
 * Process-first open-item grader (ADR-0010 feedback-first + sealed release).
 *
 * Grades ONE open/written response at a time against playbook + rubric + model
 * answer + exam-corpus exemplars. Returns structured process feedback + partial
 * credit — never a lone boolean.
 */
import 'server-only';
import { llmCompleteJson } from '@/lib/llm-provider';
import { GRADE_ITEM_MAX_RETRIES } from '@/lib/assessment-grading-logic';
import { pickExamStyleItems } from '@/lib/exam-style-corpus';
import { loadGraderPlaybook } from '@/lib/grader-playbook';

export { loadGraderPlaybook } from '@/lib/grader-playbook';

export const MAX_ITEM_GRADE_RETRIES = GRADE_ITEM_MAX_RETRIES;
/** Soft site-wide cap on concurrent LLM grade calls (free-tier safety). */
export const MAX_CONCURRENT_GRADES = 3;

export type ItemGradeStatus = 'pending' | 'graded' | 'failed';

export interface ProcessFeedback {
  item_id: string;
  status: ItemGradeStatus;
  retries: number;
  strengths: string;
  steps_present: string;
  steps_skipped: string;
  logic: string;
  material_anchoring: string;
  points_earned: number;
  points_available: number;
  process_score: number;
  next_fix: string;
  graded_at?: string;
}

export interface GradeOpenItemInput {
  item_id: string;
  stem: string;
  response: string;
  rubric?: string | null;
  model_answer?: string | null;
  concept_id?: string | null;
  subject?: string | null;
  skill_atoms?: string[];
  points_available?: number;
  locale?: 'he' | 'en';
  prior_retries?: number;
}

function exemplarBlock(
  conceptId: string | null | undefined,
  subject: string | null | undefined,
  locale: 'he' | 'en',
): string {
  try {
    const concepts = conceptId ? [conceptId] : [];
    const picks = pickExamStyleItems({
      conceptIds: concepts,
      goalKey: null,
      count: 2,
      rotation: (conceptId ?? subject ?? 'x').length,
    });
    if (!picks.length) return '';
    return picks
      .map((it, i) => {
        const stem = locale === 'he' ? it.stem_he : it.stem_en;
        const rubric = locale === 'he' ? it.rubric_he : it.rubric_en;
        const parts = (it.parts ?? [])
          .map((p) => `${p.label}(${p.points}pt)`)
          .join(', ');
        return `Exemplar ${i + 1} [${it.subject}/${it.level}]: ${stem.slice(0, 400)}\nParts: ${parts || 'n/a'}\nRubric: ${rubric.slice(0, 400)}`;
      })
      .join('\n\n');
  } catch {
    return '';
  }
}

function emptyFeedback(
  itemId: string,
  retries: number,
  status: ItemGradeStatus,
  pointsAvailable: number,
): ProcessFeedback {
  return {
    item_id: itemId,
    status,
    retries,
    strengths: '',
    steps_present: '',
    steps_skipped: '',
    logic: '',
    material_anchoring: '',
    points_earned: 0,
    points_available: pointsAvailable,
    process_score: 0,
    next_fix: '',
  };
}

/**
 * Grade a single open response. Fail-soft: returns status=failed (not a score).
 */
export async function gradeOpenItemProcess(
  input: GradeOpenItemInput,
): Promise<ProcessFeedback> {
  const pointsAvailable = Math.max(1, input.points_available ?? 20);
  const retries = input.prior_retries ?? 0;
  const locale = input.locale ?? 'he';
  const response = (input.response ?? '').trim();

  if (!response) {
    return {
      ...emptyFeedback(input.item_id, retries, 'graded', pointsAvailable),
      strengths: locale === 'he' ? 'לא הוגשה תשובה.' : 'No answer was submitted.',
      steps_skipped: locale === 'he' ? 'כל השלבים חסרים.' : 'All required steps missing.',
      logic: locale === 'he' ? 'אין נימוק לבדיקה.' : 'Nothing to evaluate.',
      material_anchoring:
        locale === 'he' ? 'לא ניתן לעגן לחומר ללא תשובה.' : 'Cannot anchor without a response.',
      next_fix:
        locale === 'he'
          ? 'כתבו פתרון מלא עם שלבים לפני שליחה חוזרת.'
          : 'Write a full worked solution before resubmitting.',
      process_score: 0,
      points_earned: 0,
      graded_at: new Date().toISOString(),
    };
  }

  const playbook = loadGraderPlaybook();
  const exemplars = exemplarBlock(input.concept_id, input.subject, locale);

  const system = `You are a strict Israeli Bagrut / university exam Reviewer (A Step Forward Grader agent).
Grade ONE learner written solution for PROCESS, not just the final answer.
A correct final number with missing/wrong steps must NOT receive full credit.

## Playbook (KPIs)
${playbook}

${exemplars ? `## Exam-style exemplars (style / depth reference)\n${exemplars}\n` : ''}

Return ONLY JSON:
{
  "strengths": "...",
  "steps_present": "...",
  "steps_skipped": "...",
  "logic": "...",
  "material_anchoring": "...",
  "points_earned": <number 0..points_available>,
  "next_fix": "..."
}

Rules:
- Language of all string fields: ${locale === 'he' ? 'Hebrew' : 'English'}.
- Evaluate against the item rubric and model answer below.
- points_earned is partial credit (0 to points_available). Be strict but fair.
- Never invent steps the learner did not write.`;

  const user = JSON.stringify({
    item_id: input.item_id,
    concept_id: input.concept_id ?? null,
    subject: input.subject ?? null,
    skill_atoms: input.skill_atoms ?? [],
    points_available: pointsAvailable,
    stem: input.stem.slice(0, 1500),
    rubric: (input.rubric ?? '').slice(0, 800),
    model_answer: (input.model_answer ?? '').slice(0, 1000),
    learner_response: response.slice(0, 4000),
  });

  const parsed = await llmCompleteJson<{
    strengths?: unknown;
    steps_present?: unknown;
    steps_skipped?: unknown;
    logic?: unknown;
    material_anchoring?: unknown;
    points_earned?: unknown;
    next_fix?: unknown;
  }>({
    system,
    messages: [{ role: 'user', content: user }],
    maxTokens: 1800,
    temperature: 0.15,
    timeoutMs: 28_000,
    modelTier: 'primary',
    jsonMode: true,
  });

  if (!parsed?.json) {
    return emptyFeedback(input.item_id, retries + 1, 'failed', pointsAvailable);
  }

  const j = parsed.json;
  const str = (v: unknown) => (typeof v === 'string' ? v.trim().slice(0, 1200) : '');
  let earned =
    typeof j.points_earned === 'number' && Number.isFinite(j.points_earned)
      ? j.points_earned
      : 0;
  earned = Math.max(0, Math.min(pointsAvailable, earned));
  const processScore =
    pointsAvailable > 0 ? Math.round((earned / pointsAvailable) * 10_000) / 10_000 : 0;

  return {
    item_id: input.item_id,
    status: 'graded',
    retries,
    strengths: str(j.strengths),
    steps_present: str(j.steps_present),
    steps_skipped: str(j.steps_skipped),
    logic: str(j.logic),
    material_anchoring: str(j.material_anchoring),
    points_earned: earned,
    points_available: pointsAvailable,
    process_score: processScore,
    next_fix: str(j.next_fix),
    graded_at: new Date().toISOString(),
  };
}

/** Pure helper: overall mean of per-item process scores (missing → 0). */
export function aggregateProcessScores(
  itemIds: string[],
  scores: Record<string, number>,
): number {
  if (itemIds.length === 0) return 0;
  const sum = itemIds.reduce((s, id) => s + (scores[id] ?? 0), 0);
  return Math.round((sum / itemIds.length) * 10_000) / 10_000;
}

export function perTopicFromItemScores(
  items: Array<{ id: string; topic: string }>,
  scores: Record<string, number>,
): Record<string, number> {
  const topicSum: Record<string, number> = {};
  const topicN: Record<string, number> = {};
  for (const it of items) {
    topicN[it.topic] = (topicN[it.topic] ?? 0) + 1;
    topicSum[it.topic] = (topicSum[it.topic] ?? 0) + (scores[it.id] ?? 0);
  }
  const out: Record<string, number> = {};
  for (const [t, n] of Object.entries(topicN)) {
    out[t] = n > 0 ? Math.round(((topicSum[t] ?? 0) / n) * 10_000) / 10_000 : 0;
  }
  return out;
}
