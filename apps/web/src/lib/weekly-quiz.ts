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
import type { QuizStartResponse, QuizQuestion } from '@asf/schemas/learning_path';
import { sanitizeConceptIds } from '@/lib/plan-catalog';
import { resolveConceptTitles } from '@/lib/concept-display-names';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

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
    if (typeof correct !== 'string' || !['A', 'B', 'C', 'D'].includes(correct.toUpperCase())) continue;
    const mappedOptions: { key: string; text: string }[] = [];
    for (const opt of options.slice(0, 4)) {
      if (!opt || typeof opt !== 'object') break;
      const o = opt as Record<string, unknown>;
      if (typeof o.key !== 'string' || typeof o.text !== 'string') break;
      mappedOptions.push({ key: o.key, text: o.text });
    }
    if (mappedOptions.length !== 4) continue;
    validated.push({
      id: randomUUID(),
      topic,
      subject,
      difficulty: typeof difficulty === 'number' ? Math.max(0, Math.min(1, difficulty)) : 0.5,
      stem: stem.trim().slice(0, 600),
      options: mappedOptions,
      correct: (correct as string).toUpperCase(),
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
  const selectedConcepts = weekConceptIds
    .filter((id) => Boolean(kgById[id]))
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
  let quizId = randomUUID();
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
      ON CONFLICT (user_id, week_start, plan_id, week_num, locale) DO UPDATE
        SET questions   = EXCLUDED.questions,
            plan_id     = EXCLUDED.plan_id,
            week_num    = EXCLUDED.week_num,
            locale      = EXCLUDED.locale
      RETURNING id::text
    `) as Array<{ id: string }>;
    if (inserted[0]?.id) quizId = inserted[0].id as ReturnType<typeof randomUUID>;
  } catch {
    // Cache write failed — still return the freshly-generated questions.
  }

  return buildClientResponse(quizId, planId, weekNum, generated, weekStartStr);
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
