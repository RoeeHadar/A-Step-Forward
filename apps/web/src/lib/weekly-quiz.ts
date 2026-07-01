/**
 * Weekly quiz generator — Neon/Vercel path (no Render dependency).
 *
 * Given a learner, this module:
 *   1. Reads the learner's weakest concepts from `concept_mastery`.
 *   2. Calls Groq to generate 5–10 bilingual MCQ questions targeting those concepts.
 *   3. Caches the result in `weekly_quizzes_ai` (keyed by learner + ISO week start).
 *   4. On subsequent calls within the same week, returns the cached questions.
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
const kgById: Record<string, KgConcept> = (kg as { byId: Record<string, KgConcept> }).byId;
const kgConcepts: KgConcept[] = (kg as { concepts: KgConcept[] }).concepts;

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

const SYSTEM_PROMPT = `You are a bilingual (Hebrew + English) math/physics exam author for Israeli high-school students preparing for Bagrut exams.

Generate multiple-choice (MCQ) questions. Output ONLY valid JSON — no commentary, no markdown fences.

Shape:
{ "questions": [ { "topic": "<concept_id>", "subject": "<subject>", "difficulty": <0.0–1.0>, "stem": "<English question>", "options": [{"key":"A","text":"..."},{"key":"B","text":"..."},{"key":"C","text":"..."},{"key":"D","text":"..."}], "correct": "<A|B|C|D>" } ] }

Rules:
- Each question must have EXACTLY 4 options keyed A, B, C, D.
- "topic" must be one of the supplied concept IDs.
- "difficulty" is a float from 0.0 (easy) to 1.0 (hard). Use 0.3 for easy, 0.6 for medium, 0.9 for hard.
- "stem" ≤ 500 chars. Math in $...$ LaTeX.
- NEVER include names, emails, phones, or addresses.
- Spread questions across concepts; cover different skills per concept.`;

function buildUserPrompt(
  concepts: Array<{ id: string; name: string; subject: string; mastery: number | null; atoms: string[] }>,
  count: number,
  goal: string | null,
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
    return `concept_id: ${c.id}\nname: ${c.name}\nsubject: ${c.subject}\nmastery: ${masteryLabel}\nskill_atoms: ${atomsStr}`;
  }).join('\n\n');

  return `Level: ${levelNote}

Generate exactly ${count} MCQ questions covering the following concepts (distribute evenly):

${conceptBlocks}

Return JSON only.`;
}

async function callLLMForWeeklyQuiz(
  concepts: Array<{ id: string; name: string; subject: string; mastery: number | null; atoms: string[] }>,
  count: number,
  goal: string | null,
): Promise<StoredWeeklyQuestion[] | null> {
  const userPrompt = buildUserPrompt(concepts, count, goal);

  const parsed = await llmCompleteJson<{ questions?: unknown }>({
    system: SYSTEM_PROMPT,
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
        questions   JSONB NOT NULL,
        created_at  TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE (user_id, week_start)
      )
    `;
  } catch {
    // If DDL fails (e.g. concurrent creation), fall through — the select will work.
  }

  // Return cached quiz for this week
  try {
    const cached = (await sql`
      SELECT id::text, questions
      FROM weekly_quizzes_ai
      WHERE user_id = ${userId} AND week_start = ${weekStartStr}::date
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

  const [mastery, profile] = await Promise.all([
    getConceptMastery(userId).catch(() => ({} as Record<string, number>)),
    getLearnerProfile(userId).catch(() => null),
  ]);

  // Pick the learner's weakest KG-known concepts (up to 6)
  const weakEntries = Object.entries(mastery)
    .filter(([id]) => Boolean(kgById[id]))
    .sort((a, b) => a[1] - b[1])
    .slice(0, 6);

  // Fall back to subject roots for brand-new learners
  if (weakEntries.length === 0) {
    const subjects = (profile?.subjects?.length ?? 0) > 0 ? profile!.subjects : ['math'];
    const subjectSet = new Set(subjects.map((s) => s.toLowerCase()));
    const roots = kgConcepts
      .filter((c) => subjectSet.has(c.subject) && c.prerequisites.length === 0)
      .slice(0, 6);
    for (const r of roots) weakEntries.push([r.id, 0.5]);
  }

  if (weakEntries.length === 0) return null;

  const conceptsCtx = weakEntries.map(([id, score]) => {
    const info = kgById[id]!;
    return {
      id,
      name: info.name,
      subject: info.subject,
      mastery: score,
      atoms: info.skill_atoms ?? [],
    };
  });

  const questionCount = Math.min(10, Math.max(5, weakEntries.length + 2));
  const generated = await callLLMForWeeklyQuiz(
    conceptsCtx,
    questionCount,
    profile?.goal ?? null,
  );
  if (!generated || generated.length === 0) return null;

  // Cache the result (with correct answers stored server-side)
  let quizId = randomUUID();
  try {
    const inserted = (await sql`
      INSERT INTO weekly_quizzes_ai (user_id, week_start, plan_id, week_num, questions)
      VALUES (
        ${userId},
        ${weekStartStr}::date,
        ${planId},
        ${weekNum},
        ${JSON.stringify(generated)}::jsonb
      )
      ON CONFLICT (user_id, week_start) DO UPDATE
        SET questions   = EXCLUDED.questions,
            plan_id     = EXCLUDED.plan_id,
            week_num    = EXCLUDED.week_num
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
