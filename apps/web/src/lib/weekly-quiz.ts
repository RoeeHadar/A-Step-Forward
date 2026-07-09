/**
 * Weekly quiz generator — Neon/Vercel path (no Render dependency).
 *
 * Given a learner, this module:
 *   1. Reads the selected learning-plan week concepts.
 *   2. Calls Groq to generate locale-specific MCQ questions targeting those concepts.
 *   3. Caches the result in `weekly_quizzes_ai` (keyed by learner + week + plan + locale).
 *   4. On subsequent calls for the same plan/week/locale, returns the cached questions.
 *
 * Returns a `QuizStartResponse`-compatible object that the existing WeekQuizClient
 * can render without modification.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';
import { getConceptMastery, getLearnerProfile } from './neon-db';
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

// ── Stored shape (with correct answer, never sent to client) ─────────────────

interface StoredWeeklyQuestion {
  id: string;
  topic: string;     // concept_id
  subject: string;
  difficulty: number; // 0–1 float
  stem: string;
  options: { key: string; text: string }[];
  correct: string;   // "A" | "B" | "C" | "D"
}

// ── LLM call ─────────────────────────────────────────────────────────────────

function systemPrompt(locale: 'he' | 'en'): string {
  const languageRule =
    locale === 'he'
      ? 'All learner-facing text in "stem" and option "text" MUST be natural Hebrew. Keep math expressions in $...$ LaTeX and left-to-right inside the math only.'
      : 'All learner-facing text in "stem" and option "text" MUST be natural English. Keep math expressions in $...$ LaTeX.';

  return `You are a bilingual (Hebrew + English) math/physics exam author for Israeli students.

Generate multiple-choice (MCQ) questions. Output ONLY valid JSON — no commentary, no markdown fences.

Shape:
{ "questions": [ { "topic": "<concept_id>", "subject": "<subject>", "difficulty": <0.0–1.0>, "stem": "<question>", "options": [{"key":"A","text":"..."},{"key":"B","text":"..."},{"key":"C","text":"..."},{"key":"D","text":"..."}], "correct": "<A|B|C|D>" } ] }

Rules:
- ${languageRule}
- Each question must have EXACTLY 4 options keyed A, B, C, D.
- "topic" must be one of the supplied concept IDs.
- "difficulty" is a float from 0.0 (easy) to 1.0 (hard). Use 0.3 for easy, 0.6 for medium, 0.9 for hard.
- "stem" ≤ 500 chars. Math in $...$ LaTeX.
- Questions must match the supplied weekly plan concepts. Do not introduce prerequisite warmups or unrelated basics unless that exact concept is supplied.
- NEVER include names, emails, phones, or addresses.
- Spread questions across concepts; cover different skills per concept.`;
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

function buildUserPrompt(
  concepts: Array<{ id: string; name: string; name_he: string | null; subject: string; mastery: number | null; atoms: string[] }>,
  count: number,
  goal: string | null,
  locale: 'he' | 'en',
): string {
  const GOAL_LABELS: Record<string, string> = {
    bagrut_math_3: '3-unit math (practical, no calculus)',
    bagrut_math_4: '4-unit math (some calculus, intermediate)',
    bagrut_math_5: '5-unit math (full calculus, proofs)',
    bagrut_physics: 'High-school physics (formula-based, multi-step)',
    calculus1: 'University Calculus 1 (rigorous limits/derivatives/integrals)',
    linear_algebra: 'Linear Algebra',
  };
  const levelNote = goal ? (GOAL_LABELS[goal] ?? goal) : 'general secondary-school level';

  const conceptBlocks = concepts.map((c) => {
    const masteryLabel =
      c.mastery == null ? 'unmeasured'
      : c.mastery >= 0.7 ? 'strong (needs challenge)'
      : c.mastery >= 0.4 ? 'medium (needs consolidation)'
      : 'weak (needs remediation)';
    const atomsStr = c.atoms.length > 0 ? c.atoms.slice(0, 10).join(', ') : '(generate from concept)';
    return `concept_id: ${c.id}\nname_en: ${c.name}\nname_he: ${c.name_he ?? '(none)'}\nsubject: ${c.subject}\nmastery: ${masteryLabel}\nskill_atoms: ${atomsStr}`;
  }).join('\n\n');

  return `Level: ${levelNote}
Question language: ${locale === 'he' ? 'Hebrew' : 'English'}

Generate exactly ${count} MCQ questions covering the following concepts (distribute evenly):

${conceptBlocks}

Return JSON only.`;
}

async function callLLMForWeeklyQuiz(
  concepts: Array<{ id: string; name: string; name_he: string | null; subject: string; mastery: number | null; atoms: string[] }>,
  count: number,
  goal: string | null,
  locale: 'he' | 'en',
): Promise<StoredWeeklyQuestion[] | null> {
  const userPrompt = buildUserPrompt(concepts, count, goal, locale);

  const parsed = await llmCompleteJson<{ questions?: unknown }>({
    system: systemPrompt(locale),
    messages: [{ role: 'user', content: userPrompt }],
    maxTokens: 3000,
    temperature: 0.4,
    timeoutMs: 28_000,
    modelTier: 'primary',
    jsonMode: true,
  });
  if (!parsed || !Array.isArray(parsed.json.questions)) return null;

  const validConcepts = new Set(concepts.map((c) => c.id));
  const validated: StoredWeeklyQuestion[] = [];
  for (const q of parsed.json.questions) {
    if (!q || typeof q !== 'object') continue;
    const { topic, subject, difficulty, stem, options, correct } = q as Record<string, unknown>;
    if (typeof topic !== 'string' || !validConcepts.has(topic)) continue;
    if (typeof subject !== 'string') continue;
    if (typeof stem !== 'string' || stem.trim().length === 0) continue;
    if (!Array.isArray(options) || options.length < 4) continue;
    if (typeof correct !== 'string') continue;
    const normalized = normalizeWeeklyMcqOptions(options, correct);
    if (!normalized) continue;
    validated.push({
      id: randomUUID(),
      topic,
      subject,
      difficulty: typeof difficulty === 'number' ? Math.max(0, Math.min(1, difficulty)) : 0.5,
      stem: stem.trim().slice(0, 600),
      options: normalized.options,
      correct: normalized.correct,
    });
  }
  return validated.length > 0 ? validated : null;
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

// ── Main export ──────────────────────────────────────────────────────────────

/**
 * Generates (or returns cached) a weekly quiz for the given learner.
 *
 * Designed to be called from a server component or API route — no Render
 * dependency, targets <3s (Groq p50 ≈ 1.5s).
 */
export async function generateWeeklyQuizForUser(
  userId: string,
  planId: string,
  weekNum: number,
  locale: 'he' | 'en' = 'he',
): Promise<QuizStartResponse | null> {
  if (!sql) return null;

  // Determine the Monday of the current ISO week (UTC)
  const now = new Date();
  const dow = now.getUTCDay(); // 0 = Sun
  const daysToMonday = dow === 0 ? 6 : dow - 1;
  const weekStart = new Date(now);
  weekStart.setUTCDate(weekStart.getUTCDate() - daysToMonday);
  const weekStartStr = weekStart.toISOString().slice(0, 10);

  // Ensure the cache table exists (idempotent DDL)
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
    await sql`ALTER TABLE weekly_quizzes_ai DROP CONSTRAINT IF EXISTS weekly_quizzes_ai_user_id_week_start_key`;
    await sql`
      CREATE UNIQUE INDEX IF NOT EXISTS weekly_quizzes_ai_user_week_plan_locale_idx
      ON weekly_quizzes_ai (user_id, week_start, plan_id, week_num, locale)
    `;
  } catch {
    // If DDL fails (e.g. concurrent creation), fall through — the select will work.
  }

  // Return cached quiz for this selected plan week and locale.
  try {
    const cached = (await sql`
      SELECT id::text, questions
      FROM weekly_quizzes_ai
      WHERE user_id = ${userId}
        AND week_start = ${weekStartStr}::date
        AND plan_id = ${planId}
        AND week_num = ${weekNum}
        AND locale = ${locale}
      LIMIT 1
    `) as Array<{ id: string; questions: StoredWeeklyQuestion[] }>;

    if (cached.length > 0 && cached[0]) {
      const row = cached[0];
      return buildClientResponse(row.id, planId, weekNum, row.questions, weekStartStr);
    }
  } catch {
    // Cache read failed — proceed to generate.
  }

  // ── Generate new questions ─────────────────────────────────────────────────

  const [mastery, profile, weekConceptIds] = await Promise.all([
    getConceptMastery(userId).catch(() => ({} as Record<string, number>)),
    getLearnerProfile(userId).catch(() => null),
    fetchPlanWeekConceptIds(userId, planId, weekNum),
  ]);

  // Weekly quizzes must assess the selected learning-plan week, not generic weak topics.
  const profileSubjects = new Set(profile?.subjects ?? []);
  const selectedConcepts = weekConceptIds
    .filter((id) => Boolean(kgById[id]))
    .filter((id) => {
      if (profileSubjects.size === 0) return true;
      return profileSubjects.has(kgById[id]!.subject);
    })
    .slice(0, 8)
    .map((id) => [id, mastery[id] ?? null] as const);
  if (selectedConcepts.length === 0) return null;

  const conceptsCtx = selectedConcepts.map(([id, score]) => {
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
      mastery: score,
      atoms: info.skill_atoms ?? [],
    };
  });

  const questionCount = Math.min(10, Math.max(5, selectedConcepts.length + 2));
  const generated = await callLLMForWeeklyQuiz(
    conceptsCtx,
    questionCount,
    profile?.goal ?? null,
    locale,
  );
  if (!generated || generated.length === 0) return null;

  // Cache the result (with correct answers stored server-side)
  let quizId: string = randomUUID();
  try {
    const inserted = (await sql`
      INSERT INTO weekly_quizzes_ai (user_id, week_start, plan_id, week_num, locale, questions)
      VALUES (
        ${userId},
        ${weekStartStr}::date,
        ${planId},
        ${weekNum},
        ${locale},
        ${JSON.stringify(generated)}::jsonb
      )
      ON CONFLICT (user_id, week_start, plan_id, week_num, locale) DO NOTHING
      RETURNING id::text, questions
    `) as Array<{ id: string; questions: StoredWeeklyQuestion[] }>;
    if (inserted[0]?.id) {
      quizId = inserted[0].id;
      return buildClientResponse(quizId, planId, weekNum, inserted[0].questions, weekStartStr);
    }
    const existing = (await sql`
      SELECT id::text, questions
      FROM weekly_quizzes_ai
      WHERE user_id = ${userId}
        AND week_start = ${weekStartStr}::date
        AND plan_id = ${planId}
        AND week_num = ${weekNum}
        AND locale = ${locale}
      LIMIT 1
    `) as Array<{ id: string; questions: StoredWeeklyQuestion[] }>;
    if (existing[0]?.id) {
      quizId = existing[0].id;
      return buildClientResponse(
        quizId,
        planId,
        weekNum,
        existing[0].questions,
        weekStartStr,
      );
    }
  } catch {
    // Cache write failed — still return the freshly-generated questions.
  }

  return buildClientResponse(quizId, planId, weekNum, generated, weekStartStr);
}

// ── Grading (pure — unit-tested) ─────────────────────────────────────────────

export function scoreWeeklyQuizAnswers(
  storedQuestions: StoredWeeklyQuestion[],
  answers: WeeklyQuizAnswer[],
): { score: number; per_topic: Record<string, number>; weak_concepts: string[] } {
  const answerMap = new Map(
    answers.map((a) => [a.item_id, a.chosen.trim().toUpperCase()]),
  );
  const topicCorrect: Record<string, number> = {};
  const topicTotal: Record<string, number> = {};

  for (const item of storedQuestions) {
    topicTotal[item.topic] = (topicTotal[item.topic] ?? 0) + 1;
    const chosen = answerMap.get(item.id) ?? '';
    if (chosen && chosen === item.correct.toUpperCase()) {
      topicCorrect[item.topic] = (topicCorrect[item.topic] ?? 0) + 1;
    }
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
  },
): Promise<QuizSubmitResponse | null> {
  if (!sql) return null;
  await ensureWeeklyQuizSubmitColumns();

  type QuizRow = {
    id: string;
    questions: StoredWeeklyQuestion[];
    submitted_at: string | null;
    score: number | null;
    per_topic: Record<string, number> | null;
    plan_id: string | null;
    week_num: number | null;
  };

  let row: QuizRow | null = null;
  try {
    const rows = (await sql`
      SELECT id::text, questions, submitted_at, score, per_topic, plan_id, week_num
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

  const stored = Array.isArray(row.questions) ? row.questions : [];
  if (stored.length === 0) return null;

  const { score, per_topic, weak_concepts } = scoreWeeklyQuizAnswers(stored, args.answers);

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

  return {
    quiz_id: quizId,
    score,
    per_topic,
    weak_concepts,
    plan_adapted: false,
    next_week_concepts: null,
  };
}

// ── Helper: strip `correct` before returning to client ───────────────────────

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
    options: q.options,
    // `correct` is intentionally omitted — grading is server-side.
  }));

  return {
    quiz_id: quizId,
    // week_id is used only as the URL path segment in /api/quiz/[week_id]/submit,
    // where the param is actually unused — so we reuse the quiz_id.
    week_id: quizId,
    plan_id: planId,
    week_number: weekNum,
    time_limit_s: 1800, // 30 minutes
    questions: clientQuestions,
    started_at: `${weekStartStr}T00:00:00Z`,
  };
}
