/**
 * Weekly quiz / competency gate — Neon/Vercel path (no Render dependency).
 *
 * ADR-0010 + exam corpus: prefer original Bagrut-style multi-part items from
 * `exam-style-corpus`, then hard lesson-bank production items. LLM only fills
 * true gaps as hard open/numeric (never easy MCQ).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';
import { appendLearnerPersonaLine, getConceptMastery, getLearnerProfile } from './neon-db';
import { evaluateGatePass, hasFrontier } from './plan-pacing';
import { countGateAttempts, GATE_PASS_THRESHOLD, recordTestAttempt } from './test-attempts';
import {
  GATE_BANK_FORMAT_VERSION,
  isBankSourcedGateQuiz,
  pickGateQuestionsFromBank,
  type GateBankPick,
  type GateQuestionKind,
} from './gate-question-bank';
import {
  formatExamStyleStem,
  pickExamStyleItems,
  type ExamStyleItem,
} from './exam-style-corpus';
import { answersMatch, getAcceptedAnswers, numericClose } from './answer-normalize';
import { llmCompleteJson } from '@/lib/llm-provider';
import kg from './kg-data.json';
import type {
  QuizStartResponse,
  QuizQuestion,
  QuizSubmitResponse,
} from '@asf/schemas/learning_path';
import { sanitizeConceptIds } from '@/lib/plan-catalog';
import { resolveConceptTitles } from '@/lib/concept-display-names';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

const ADAPT_WEAK_THRESHOLD = 0.4;
const MCQ_LETTERS = ['A', 'B', 'C', 'D'] as const;

export interface WeeklyQuizAnswer {
  item_id: string;
  chosen: string;
  time_spent_s?: number | null;
}

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  prerequisites: string[];
  skill_atoms?: string[];
  bagrut_chapter?: string | null;
  level_scope?: Record<string, string>;
}
const kgById: Record<string, KgConcept> = (kg as unknown as { byId: Record<string, KgConcept> }).byId;

// ── Stored shape (with answers, never sent to client) ─────────────────────────

export interface StoredWeeklyPart {
  label: string;
  body: string;
  points?: number;
}

export interface StoredWeeklyQuestion {
  id: string;
  topic: string;
  subject: string;
  difficulty: number;
  kind: GateQuestionKind;
  stem: string;
  options: { key: string; text: string }[];
  parts?: StoredWeeklyPart[];
  total_points?: number;
  correct?: string;
  correct_answer?: string | null;
  acceptable_answers?: string[];
  rubric?: string | null;
  model_answer?: string | null;
  source_question_id?: string;
  source: 'lesson_bank' | 'llm_fallback' | 'exam_corpus';
  format_version: typeof GATE_BANK_FORMAT_VERSION;
}

function fromBankPick(p: GateBankPick): StoredWeeklyQuestion {
  return {
    id: p.id,
    topic: p.topic,
    subject: p.subject,
    difficulty: p.difficulty,
    kind: p.kind,
    stem: p.stem,
    options: p.options,
    correct: p.correct,
    correct_answer: p.correct_answer,
    acceptable_answers: p.acceptable_answers,
    rubric: p.rubric,
    model_answer: p.model_answer,
    source_question_id: p.source_question_id,
    source: 'lesson_bank',
    format_version: GATE_BANK_FORMAT_VERSION,
  };
}

function fromExamStyle(it: ExamStyleItem, locale: 'he' | 'en'): StoredWeeklyQuestion {
  const topic = it.concept_ids?.[0] ?? it.paper_pattern ?? 'exam';
  const parts = (it.parts ?? []).map((p) => ({
    label: p.label,
    body: locale === 'he' ? p.body_he : p.body_en,
    points: p.points,
  }));
  return {
    id: randomUUID(),
    topic,
    subject: it.subject === 'physics' ? 'physics' : 'math',
    difficulty: it.difficulty === 'very_hard' ? 0.95 : 0.88,
    kind: 'open',
    stem: formatExamStyleStem(it, locale),
    options: [],
    parts,
    total_points: it.total_points,
    rubric: locale === 'he' ? it.rubric_he : it.rubric_en,
    model_answer: locale === 'he' ? it.sample_solution_he : it.sample_solution_en,
    source_question_id: it.id,
    source: 'exam_corpus',
    format_version: GATE_BANK_FORMAT_VERSION,
  };
}

function normalizeStored(raw: unknown): StoredWeeklyQuestion | null {
  if (!raw || typeof raw !== 'object') return null;
  const q = raw as Record<string, unknown>;
  if (typeof q.id !== 'string' || typeof q.stem !== 'string' || typeof q.topic !== 'string') {
    return null;
  }
  const kind = (typeof q.kind === 'string' ? q.kind : 'mcq') as GateQuestionKind;
  const options = Array.isArray(q.options)
    ? (q.options as { key: string; text: string }[])
    : [];
  return {
    id: q.id,
    topic: q.topic,
    subject: typeof q.subject === 'string' ? q.subject : 'math',
    difficulty: typeof q.difficulty === 'number' ? q.difficulty : 0.6,
    kind,
    stem: q.stem,
    options,
    correct: typeof q.correct === 'string' ? q.correct : undefined,
    correct_answer: typeof q.correct_answer === 'string' ? q.correct_answer : null,
    acceptable_answers: Array.isArray(q.acceptable_answers)
      ? q.acceptable_answers.filter((a): a is string => typeof a === 'string')
      : undefined,
    rubric: typeof q.rubric === 'string' ? q.rubric : null,
    model_answer: typeof q.model_answer === 'string' ? q.model_answer : null,
    source_question_id: typeof q.source_question_id === 'string' ? q.source_question_id : undefined,
    parts: (() => {
      if (!Array.isArray(q.parts)) return undefined;
      const out: StoredWeeklyPart[] = [];
      for (const p of q.parts) {
        if (!p || typeof p !== 'object') continue;
        const part = p as Record<string, unknown>;
        if (typeof part.label !== 'string' || typeof part.body !== 'string') continue;
        out.push({
          label: part.label,
          body: part.body,
          points: typeof part.points === 'number' ? part.points : undefined,
        });
      }
      return out.length > 0 ? out : undefined;
    })(),
    total_points: typeof q.total_points === 'number' ? q.total_points : undefined,
    source:
      q.source === 'lesson_bank' || q.source === 'llm_fallback' || q.source === 'exam_corpus'
        ? q.source
        : 'llm_fallback',
    format_version: GATE_BANK_FORMAT_VERSION,
  };
}

/** Force option keys to A–D and map correct answer to a letter the client can send back. */
export function normalizeWeeklyMcqOptions(
  options: unknown[],
  correctRaw: string,
): { options: { key: string; text: string }[]; correct: string } | null {
  const texts: string[] = [];
  const origKeys: string[] = [];
  for (const opt of options.slice(0, 4)) {
    if (!opt || typeof opt !== 'object') return null;
    const o = opt as Record<string, unknown>;
    const text =
      typeof o.text === 'string'
        ? o.text
        : typeof o.label === 'string'
          ? o.label
          : null;
    if (!text?.trim()) return null;
    texts.push(text.trim());
    origKeys.push(
      typeof o.key === 'string' ? o.key.trim().toUpperCase() : String(texts.length),
    );
  }
  if (texts.length !== 4) return null;

  const normalizedOptions = MCQ_LETTERS.map((key, i) => ({
    key,
    text: texts[i]!,
  }));

  let correct = correctRaw.trim().toUpperCase();
  if (!MCQ_LETTERS.includes(correct as (typeof MCQ_LETTERS)[number])) {
    const idxByKey = origKeys.findIndex((k) => k === correct);
    if (idxByKey >= 0) {
      correct = MCQ_LETTERS[idxByKey]!;
    } else if (/^[1-4]$/.test(correctRaw.trim())) {
      correct = MCQ_LETTERS[parseInt(correctRaw.trim(), 10) - 1]!;
    } else {
      return null;
    }
  }

  return { options: normalizedOptions, correct };
}

/**
 * Last-resort fill when a concept has no authored bank items. Demands
 * open/numeric at exam level — never invents easy 4-option recognition MCQs.
 */
async function callLLMFallbackForGaps(
  missingConcepts: Array<{ id: string; name: string; name_he: string | null; subject: string }>,
  exemplars: GateBankPick[],
  count: number,
  goal: string | null,
  locale: 'he' | 'en',
): Promise<StoredWeeklyQuestion[]> {
  if (missingConcepts.length === 0 || count <= 0) return [];

  const languageRule =
    locale === 'he'
      ? 'All learner-facing text MUST be natural Hebrew. Math in $...$ LaTeX LTR.'
      : 'All learner-facing text MUST be natural English. Math in $...$ LaTeX.';

  const exemplarBlock = exemplars.slice(0, 4).map((e) =>
    `- [${e.kind}/${e.difficulty}] ${e.stem.slice(0, 220)}`,
  ).join('\n');

  const system = `You author Israeli Bagrut / university exam questions for a competency GATE.
${languageRule}
Output ONLY valid JSON: { "questions": [ ... ] }
Each question shape:
{ "topic": "<concept_id>", "subject": "<subject>", "kind": "numeric"|"short_answer"|"open", "difficulty": 0.75-1.0, "stem": "...", "correct_answer": "<for numeric>", "acceptable_answers": ["..."], "rubric": "...", "model_answer": "..." }
Rules:
- NEVER generate multiple-choice. Recognition MCQs are forbidden on gates.
- difficulty MUST be ≥ 0.75 (hard). Multi-step reasoning required.
- Match the STYLE and DEPTH of the exemplar stems when provided.
- "topic" must be one of the supplied concept IDs.
- stem ≤ 800 chars.`;

  const user = `Goal: ${goal ?? 'secondary exam'}
Language: ${locale}
Generate exactly ${count} HARD open/numeric/short_answer questions for:
${missingConcepts.map((c) => `- ${c.id} (${c.name_he ?? c.name})`).join('\n')}

Exemplars from the authored bank (match this level):
${exemplarBlock || '(none — still produce exam-hard items)'}

Return JSON only.`;

  const parsed = await llmCompleteJson<{ questions?: unknown }>({
    system,
    messages: [{ role: 'user', content: user }],
    maxTokens: 3500,
    temperature: 0.45,
    timeoutMs: 28_000,
    modelTier: 'primary',
    jsonMode: true,
  });
  if (!parsed || !Array.isArray(parsed.json.questions)) return [];

  const valid = new Set(missingConcepts.map((c) => c.id));
  const out: StoredWeeklyQuestion[] = [];
  for (const raw of parsed.json.questions) {
    if (!raw || typeof raw !== 'object') continue;
    const q = raw as Record<string, unknown>;
    const topic = typeof q.topic === 'string' ? q.topic : '';
    if (!valid.has(topic)) continue;
    const kindRaw = typeof q.kind === 'string' ? q.kind : 'open';
    if (kindRaw !== 'numeric' && kindRaw !== 'short_answer' && kindRaw !== 'open') continue;
    const stem = typeof q.stem === 'string' ? q.stem.trim() : '';
    if (stem.length < 12) continue;
    const subject =
      typeof q.subject === 'string'
        ? q.subject
        : (missingConcepts.find((c) => c.id === topic)?.subject ?? 'math');
    out.push({
      id: randomUUID(),
      topic,
      subject,
      difficulty: typeof q.difficulty === 'number' ? Math.max(0.75, Math.min(1, q.difficulty)) : 0.85,
      kind: kindRaw,
      stem: stem.slice(0, 1200),
      options: [],
      correct_answer: typeof q.correct_answer === 'string' ? q.correct_answer : null,
      acceptable_answers: Array.isArray(q.acceptable_answers)
        ? q.acceptable_answers.filter((a): a is string => typeof a === 'string')
        : undefined,
      rubric: typeof q.rubric === 'string' ? q.rubric : null,
      model_answer: typeof q.model_answer === 'string' ? q.model_answer : null,
      source: 'llm_fallback',
      format_version: GATE_BANK_FORMAT_VERSION,
    });
    if (out.length >= count) break;
  }
  return out;
}

async function fetchPlanWeekConceptIds(
  learnerId: string,
  planId: string,
  weekNum: number,
): Promise<string[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT pw.concepts
      FROM plan_weeks pw
      JOIN learning_plans lp ON lp.id = pw.plan_id
      WHERE lp.id = ${planId}::uuid
        AND lp.learner_id = ${learnerId}
        AND pw.week_number = ${weekNum}
      LIMIT 1
    `) as Array<{ concepts: unknown }>;
    const concepts = rows[0]?.concepts;
    if (!Array.isArray(concepts)) return [];
    return sanitizeConceptIds(concepts.filter((c): c is string => typeof c === 'string'));
  } catch {
    return [];
  }
}

function goalToPointsMin(
  goal: string | null | undefined,
): '3pt' | '4pt' | '5pt' | 'hs_physics' | 'calc1' | 'la' | null {
  if (!goal) return null;
  if (goal.includes('math_3')) return '3pt';
  if (goal.includes('math_4')) return '4pt';
  if (goal.includes('math_5')) return '5pt';
  if (goal === 'linear_algebra') return 'la';
  if (goal.startsWith('calculus')) return 'calc1';
  if (goal.includes('physics')) return 'hs_physics';
  return null;
}

// ── Grading ──────────────────────────────────────────────────────────────────

function gradeClosedItem(q: StoredWeeklyQuestion, chosenRaw: string): boolean {
  const chosen = chosenRaw.trim();
  if (!chosen) return false;
  switch (q.kind) {
    case 'mcq':
    case 'true_false':
      return Boolean(q.correct) && chosen.toUpperCase() === q.correct!.toUpperCase();
    case 'numeric':
      return Boolean(q.correct_answer) && numericClose(chosen, q.correct_answer!);
    case 'short_answer': {
      const accepted = getAcceptedAnswers(q.acceptable_answers, q.correct_answer ?? undefined);
      return answersMatch(chosen, accepted);
    }
    default:
      return false;
  }
}

/**
 * LLM rubric judge for open/derivation gate items. Fail-closed: ungraded → incorrect
 * so a flaky judge cannot advance the plan.
 */
export async function gradeOpenGateItems(
  items: Array<{ id: string; stem: string; rubric?: string | null; model_answer?: string | null; response: string }>,
  locale: 'he' | 'en',
): Promise<Record<string, boolean>> {
  const result: Record<string, boolean> = {};
  if (items.length === 0) return result;

  const system = `You are a strict exam grader for Israeli high-school / university math & physics.
Grade each learner response against the rubric / model answer.
Return ONLY JSON: { "grades": [ { "id": "...", "correct": true|false, "brief": "..." } ] }
Rules:
- correct=true only if the response shows genuine understanding of the required steps/concepts.
- Partial credit does NOT count as correct for a competency gate — require a substantially complete answer.
- Empty, off-topic, or single-word guesses → correct=false.
- Language: learner may answer in Hebrew or English.`;

  const payload = items.map((it) => ({
    id: it.id,
    stem: it.stem.slice(0, 600),
    rubric: (it.rubric ?? '').slice(0, 500),
    model_answer: (it.model_answer ?? '').slice(0, 500),
    response: it.response.slice(0, 2000),
  }));

  const parsed = await llmCompleteJson<{ grades?: unknown }>({
    system,
    messages: [
      {
        role: 'user',
        content: `Locale hint: ${locale}\nGrade these ${payload.length} items:\n${JSON.stringify(payload)}`,
      },
    ],
    maxTokens: 2000,
    temperature: 0.1,
    timeoutMs: 25_000,
    modelTier: 'primary',
    jsonMode: true,
  });

  if (!parsed || !Array.isArray(parsed.json.grades)) {
    for (const it of items) result[it.id] = false;
    return result;
  }
  for (const g of parsed.json.grades) {
    if (!g || typeof g !== 'object') continue;
    const row = g as { id?: unknown; correct?: unknown };
    if (typeof row.id === 'string') result[row.id] = row.correct === true;
  }
  for (const it of items) {
    if (result[it.id] === undefined) result[it.id] = false;
  }
  return result;
}

export function scoreWeeklyQuizAnswers(
  storedQuestions: StoredWeeklyQuestion[],
  answers: WeeklyQuizAnswer[],
  openGrades: Record<string, boolean> = {},
): { score: number; per_topic: Record<string, number>; weak_concepts: string[] } {
  const answerMap = new Map(answers.map((a) => [a.item_id, a.chosen]));
  const topicCorrect: Record<string, number> = {};
  const topicTotal: Record<string, number> = {};

  for (const item of storedQuestions) {
    topicTotal[item.topic] = (topicTotal[item.topic] ?? 0) + 1;
    const chosen = answerMap.get(item.id) ?? '';
    let ok = false;
    if (item.kind === 'open' || item.kind === 'derivation') {
      ok = openGrades[item.id] === true;
    } else {
      ok = gradeClosedItem(item, chosen);
    }
    if (ok) topicCorrect[item.topic] = (topicCorrect[item.topic] ?? 0) + 1;
  }

  const per_topic: Record<string, number> = {};
  for (const [topic, total] of Object.entries(topicTotal)) {
    const correct = topicCorrect[topic] ?? 0;
    per_topic[topic] = total > 0 ? Math.round((correct / total) * 10_000) / 10_000 : 0;
  }

  const correctTotal = Object.values(topicCorrect).reduce((sum, n) => sum + n, 0);
  const score =
    storedQuestions.length > 0
      ? Math.round((correctTotal / storedQuestions.length) * 10_000) / 10_000
      : 0;
  const weak_concepts = Object.entries(per_topic)
    .filter(([, s]) => s < ADAPT_WEAK_THRESHOLD)
    .map(([topic]) => topic);

  return { score, per_topic, weak_concepts };
}

async function ensureWeeklyQuizSubmitColumns(): Promise<void> {
  if (!sql) return;
  try {
    await sql`ALTER TABLE weekly_quizzes_ai ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ`;
    await sql`ALTER TABLE weekly_quizzes_ai ADD COLUMN IF NOT EXISTS score DOUBLE PRECISION`;
    await sql`ALTER TABLE weekly_quizzes_ai ADD COLUMN IF NOT EXISTS per_topic JSONB`;
  } catch {
    // Concurrent DDL — reads/writes may still work.
  }
}

async function updateTopicMasteryFromQuiz(
  learnerId: string,
  conceptId: string,
  topicScore: number,
): Promise<void> {
  if (!sql) return;
  await sql`
    INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
    VALUES (${learnerId}, ${conceptId}, ${topicScore}, 1, NOW(), NOW())
    ON CONFLICT (learner_id, concept_id) DO UPDATE SET
      score = EXCLUDED.score,
      last_activity = NOW()
  `;
}

function buildClientResponse(
  quizId: string,
  planId: string,
  weekNum: number,
  storedQuestions: StoredWeeklyQuestion[],
  weekStartStr: string,
): QuizStartResponse {
  const clientQuestions: QuizQuestion[] = storedQuestions.map((q) => ({
    id: q.id,
    topic: q.topic,
    subject: q.subject,
    difficulty: q.difficulty,
    stem: q.stem,
    options: q.options ?? [],
    kind: q.kind,
    parts: q.parts,
    total_points: q.total_points,
  }));

  // Bagrut-depth: ~18 min per multi-part item, floor 45 min, cap 90.
  const time_limit_s = Math.min(5400, Math.max(2700, storedQuestions.length * 1080));

  return {
    quiz_id: quizId,
    week_id: quizId,
    plan_id: planId,
    week_number: weekNum,
    time_limit_s,
    questions: clientQuestions,
    started_at: `${weekStartStr}T00:00:00Z`,
  };
}

// ── Main export ──────────────────────────────────────────────────────────────

/**
 * Generates (or returns cached) a weekly quiz for the given learner.
 * Exam-style multi-part corpus first; legacy easy-MCQ caches are ignored.
 */
export async function generateWeeklyQuizForUser(
  userId: string,
  planId: string,
  weekNum: number,
  locale: 'he' | 'en' = 'he',
): Promise<QuizStartResponse | null> {
  if (!sql) return null;

  const now = new Date();
  const dow = now.getUTCDay();
  const daysToMonday = dow === 0 ? 6 : dow - 1;
  const weekStart = new Date(now);
  weekStart.setUTCDate(weekStart.getUTCDate() - daysToMonday);
  const weekStartStr = weekStart.toISOString().slice(0, 10);

  try {
    await sql`
      CREATE TABLE IF NOT EXISTS weekly_quizzes_ai (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id     TEXT NOT NULL,
        week_start  DATE NOT NULL,
        plan_id     TEXT,
        week_num    INT,
        locale      TEXT NOT NULL DEFAULT 'he',
        questions   JSONB NOT NULL,
        created_at  TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE (user_id, week_start)
      )
    `;
    await sql`ALTER TABLE weekly_quizzes_ai ADD COLUMN IF NOT EXISTS locale TEXT NOT NULL DEFAULT 'he'`;
    await sql`ALTER TABLE weekly_quizzes_ai ADD COLUMN IF NOT EXISTS rotation INT NOT NULL DEFAULT 0`;
    await sql`ALTER TABLE weekly_quizzes_ai DROP CONSTRAINT IF EXISTS weekly_quizzes_ai_user_id_week_start_key`;
    await sql`DROP INDEX IF EXISTS weekly_quizzes_ai_user_week_plan_locale_idx`;
    await sql`
      CREATE UNIQUE INDEX IF NOT EXISTS weekly_quizzes_ai_user_week_plan_locale_rot_idx
      ON weekly_quizzes_ai (user_id, week_start, plan_id, week_num, locale, rotation)
    `;
  } catch {
    // If DDL fails (e.g. concurrent creation), fall through — the select will work.
  }

  const rotation = await countGateAttempts(userId, planId, weekNum).catch(() => 0);

  try {
    const cached = (await sql`
      SELECT id::text, questions
      FROM weekly_quizzes_ai
      WHERE user_id = ${userId}
        AND week_start = ${weekStartStr}::date
        AND plan_id = ${planId}
        AND week_num = ${weekNum}
        AND locale = ${locale}
        AND rotation = ${rotation}
      LIMIT 1
    `) as Array<{ id: string; questions: unknown }>;

    if (cached.length > 0 && cached[0]) {
      const rawList = Array.isArray(cached[0].questions) ? cached[0].questions : [];
      const normalized = rawList.map(normalizeStored).filter((q): q is StoredWeeklyQuestion => q != null);
      // Ignore pre-bank easy-MCQ caches so learners are not stuck on trivial gates.
      if (normalized.length > 0 && isBankSourcedGateQuiz(normalized)) {
        return buildClientResponse(cached[0].id, planId, weekNum, normalized, weekStartStr);
      }
    }
  } catch {
    // Cache read failed — proceed to generate.
  }

  const [mastery, profile, weekConceptIds] = await Promise.all([
    getConceptMastery(userId).catch(() => ({} as Record<string, number>)),
    getLearnerProfile(userId).catch(() => null),
    fetchPlanWeekConceptIds(userId, planId, weekNum),
  ]);

  const profileSubjects = new Set(profile?.subjects ?? []);
  const selectedConcepts = weekConceptIds
    .filter((id) => Boolean(kgById[id]))
    .filter((id) => {
      if (profileSubjects.size === 0) return true;
      return profileSubjects.has(kgById[id]!.subject);
    })
    .slice(0, 8);
  if (selectedConcepts.length === 0) return null;

  void mastery; // reserved for future weak-atom steering within the bank

  // Fewer, deeper items — real Bagrut questions take ~15–25 min each.
  const questionCount = 4;
  const pointsMin = goalToPointsMin(profile?.goal ?? null);
  const goalKey = profile?.goal ?? null;

  // 1) Primary: original exam-style multi-part corpus (Bagrut/finals depth).
  const examPicks = pickExamStyleItems({
    conceptIds: selectedConcepts,
    goalKey,
    count: questionCount,
    rotation,
    locale,
  });
  let generated: StoredWeeklyQuestion[] = examPicks.map((it) => fromExamStyle(it, locale));

  // 2) Fill with hard lesson-bank production items (no easy MCQ).
  if (generated.length < questionCount) {
    const need = questionCount - generated.length;
    const bankPicks = pickGateQuestionsFromBank({
      conceptIds: selectedConcepts,
      locale,
      count: need,
      rotation,
      pointsLevelMin: pointsMin,
      preferHard: true,
    });
    generated = [...generated, ...bankPicks.map(fromBankPick)];
  }

  // 3) Last resort: LLM hard open/numeric only.
  if (generated.length < questionCount) {
    const covered = new Set(generated.map((q) => q.topic));
    const missing = selectedConcepts
      .filter((id) => !covered.has(id))
      .map((id) => {
        const info = kgById[id]!;
        const titles = resolveConceptTitles(id, {
          title_en: info.name,
          title_he: info.name_he,
        });
        return {
          id,
          name: titles.title_en,
          name_he: titles.title_he,
          subject: info.subject,
        };
      });
    const need = questionCount - generated.length;
    if (missing.length > 0 && need > 0) {
      const bankExemplars = pickGateQuestionsFromBank({
        conceptIds: selectedConcepts,
        locale,
        count: 4,
        rotation,
        preferHard: true,
      });
      const fill = await callLLMFallbackForGaps(
        missing,
        bankExemplars,
        need,
        goalKey,
        locale,
      );
      generated = [...generated, ...fill];
    }
  }

  if (generated.length === 0) return null;

  let quizId: string = randomUUID();
  try {
    const inserted = (await sql`
      INSERT INTO weekly_quizzes_ai (user_id, week_start, plan_id, week_num, locale, rotation, questions)
      VALUES (
        ${userId},
        ${weekStartStr}::date,
        ${planId},
        ${weekNum},
        ${locale},
        ${rotation},
        ${JSON.stringify(generated)}::jsonb
      )
      ON CONFLICT (user_id, week_start, plan_id, week_num, locale, rotation) DO UPDATE
        SET questions = EXCLUDED.questions
      RETURNING id::text, questions
    `) as Array<{ id: string; questions: unknown }>;
    if (inserted[0]?.id) {
      quizId = inserted[0].id;
      const stored = (Array.isArray(inserted[0].questions) ? inserted[0].questions : generated)
        .map(normalizeStored)
        .filter((q): q is StoredWeeklyQuestion => q != null);
      return buildClientResponse(quizId, planId, weekNum, stored.length ? stored : generated, weekStartStr);
    }
  } catch {
    // Cache write failed — still return the freshly-generated questions.
  }

  return buildClientResponse(quizId, planId, weekNum, generated, weekStartStr);
}

/**
 * Grades a cached weekly quiz on Neon (no Render). Idempotent when already submitted.
 */
export async function submitWeeklyQuizForUser(
  userId: string,
  quizId: string,
  args: {
    planId: string;
    weekNum: number;
    answers: WeeklyQuizAnswer[];
    locale?: 'he' | 'en';
  },
): Promise<QuizSubmitResponse | null> {
  if (!sql) return null;
  await ensureWeeklyQuizSubmitColumns();

  type QuizRow = {
    id: string;
    questions: unknown;
    submitted_at: string | null;
    score: number | null;
    per_topic: Record<string, number> | null;
    plan_id: string | null;
    week_num: number | null;
    locale: string | null;
  };

  let row: QuizRow | null = null;
  try {
    const rows = (await sql`
      SELECT id::text, questions, submitted_at, score, per_topic, plan_id, week_num, locale
      FROM weekly_quizzes_ai
      WHERE id = ${quizId}::uuid
        AND user_id = ${userId}
      LIMIT 1
    `) as QuizRow[];
    row = rows[0] ?? null;
  } catch {
    return null;
  }

  if (!row) return null;

  const stored = (Array.isArray(row.questions) ? row.questions : [])
    .map(normalizeStored)
    .filter((q): q is StoredWeeklyQuestion => q != null);
  if (stored.length === 0) return null;

  const answerMap = new Map(args.answers.map((a) => [a.item_id, a.chosen]));
  const openItems = stored
    .filter((q) => q.kind === 'open' || q.kind === 'derivation')
    .map((q) => ({
      id: q.id,
      stem: q.stem,
      rubric: q.rubric,
      model_answer: q.model_answer,
      response: (answerMap.get(q.id) ?? '').trim(),
    }))
    .filter((it) => it.response.length > 0);

  const locale = (args.locale ?? row.locale ?? 'he') === 'en' ? 'en' : 'he';
  const openGrades = await gradeOpenGateItems(openItems, locale);

  // Unanswered open items are incorrect (fail closed).
  for (const q of stored) {
    if ((q.kind === 'open' || q.kind === 'derivation') && openGrades[q.id] === undefined) {
      openGrades[q.id] = false;
    }
  }

  const { score, per_topic, weak_concepts } = scoreWeeklyQuizAnswers(
    stored,
    args.answers,
    openGrades,
  );

  const profile = await getLearnerProfile(userId).catch(() => null);
  const goalKeyRaw =
    (profile?.personality_profile as { goal_key?: unknown } | null | undefined)?.goal_key;
  const goalKey =
    typeof goalKeyRaw === 'string' && hasFrontier(goalKeyRaw)
      ? goalKeyRaw
      : typeof profile?.goal === 'string' && hasFrontier(profile.goal)
        ? profile.goal
        : null;
  const gate = evaluateGatePass({
    aggregateScore: score,
    perTopic: per_topic,
    goalKey,
    passThreshold: GATE_PASS_THRESHOLD,
  });
  const weakForRemediation = Array.from(new Set([...weak_concepts, ...gate.failed_critical]));

  try {
    await sql`
      UPDATE weekly_quizzes_ai
      SET submitted_at = NOW(),
          score = ${score},
          per_topic = ${JSON.stringify(per_topic)}::jsonb
      WHERE id = ${quizId}::uuid
        AND user_id = ${userId}
    `;
  } catch {
    // Still return graded result even if persistence fails.
  }

  for (const [topic, topicScore] of Object.entries(per_topic)) {
    try {
      await updateTopicMasteryFromQuiz(userId, topic, topicScore);
    } catch {
      // Best-effort mastery sync per topic.
    }
  }

  const passed = gate.passed;
  const answerByItem = new Map(args.answers.map((a) => [a.item_id, a.chosen]));
  const attemptId = await recordTestAttempt({
    learnerId: userId,
    kind: 'weekly_gate',
    planId: row.plan_id ?? args.planId,
    weekNum: row.week_num ?? args.weekNum,
    quizId,
    score,
    passThreshold: GATE_PASS_THRESHOLD,
    perTopic: per_topic,
    weakConcepts: weakForRemediation,
    questions: stored.map((q) => ({
      id: q.id,
      topic: q.topic,
      subject: q.subject,
      stem: q.stem,
      options: q.options,
      correct: q.correct ?? q.correct_answer ?? '',
    })),
    answers: stored.map((q) => ({
      item_id: q.id,
      chosen: answerByItem.get(q.id) ?? '',
    })),
  }).catch(() => null);

  // Keep Memory "About me" current — Hebrew-default line about this gate attempt.
  const pct = Math.round(score * 100);
  const personaLine =
    locale === 'en'
      ? `Week ${row.week_num ?? args.weekNum} gate: scored ${pct}% (${passed ? 'passed' : 'needs remediation'}). Weak topics: ${weakForRemediation.slice(0, 4).join(', ') || 'none'}.`
      : `שער שבוע ${row.week_num ?? args.weekNum}: ציון ${pct}% (${passed ? 'עבר/ה' : 'דורש חיזוק'}). נושאים חלשים: ${weakForRemediation.slice(0, 4).join(', ') || 'אין'}.`;
  void appendLearnerPersonaLine(
    userId,
    locale === 'en' ? 'Recent observations' : 'תצפיות אחרונות',
    personaLine,
  ).catch(() => null);

  let planAdvanced = false;
  if (passed) {
    try {
      const updated = (await sql`
        UPDATE plan_weeks
        SET status = 'completed'
        WHERE plan_id = ${row.plan_id ?? args.planId}::uuid
          AND week_number = ${row.week_num ?? args.weekNum}
          AND status = 'active'
        RETURNING id
      `) as Array<{ id: string }>;
      planAdvanced = updated.length > 0;
    } catch {
      // Best-effort; soft-override remains the backstop.
    }
  }

  return {
    quiz_id: quizId,
    score,
    per_topic,
    weak_concepts: weakForRemediation,
    plan_adapted: planAdvanced,
    next_week_concepts: null,
    passed,
    pass_threshold: GATE_PASS_THRESHOLD,
    attempt_id: attemptId,
  };
}
