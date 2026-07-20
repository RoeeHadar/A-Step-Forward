/**
 * Bagrut-style timed mock exam generator — Neon/Vercel path (LLM + cache).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';
import { appendLearnerPersonaLine } from './neon-db';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

/**
 * Full-mock pass bar (ADR-0010 Stream E readiness gate). Based on the auto-graded
 * MCQ fraction — open items still need Reviewer grading (deferred). A passed mock
 * is what lets readiness exceed the mock-gated ceiling.
 */
export const MOCK_PASS_THRESHOLD = 0.6;

import type {
  ClientMockExamQuestion,
  MockExamQuestionKind,
  MockExamStartResponse,
  MockExamSubmitFeedback,
  MockExamSubmitResponse,
} from './mock-exam-types';

export type {
  ClientMockExamQuestion,
  MockExamQuestionKind,
  MockExamStartResponse,
  MockExamSubmitFeedback,
  MockExamSubmitResponse,
} from './mock-exam-types';

export interface StoredMockExamQuestion extends ClientMockExamQuestion {
  /** MCQ only — kept server-side for grading */
  correct?: string;
  model_answer_he?: string;
  model_answer_en?: string;
  rubric_he?: string;
  rubric_en?: string;
}

import { llmCompleteJson } from '@/lib/llm-provider';
import { formatExamStyleStem, pickExamStyleItems } from '@/lib/exam-style-corpus';

const VALID_DURATIONS = new Set([45, 60, 90]);

function goalKeyFromLevel(level: string): string | null {
  if (level === '3pt') return 'bagrut_math_3';
  if (level === '4pt') return 'bagrut_math_4';
  if (level === '5pt') return 'bagrut_math_5';
  if (level === 'hs_physics') return 'bagrut_physics';
  if (level === 'calculus') return 'calculus1';
  if (level === 'linear_algebra') return 'linear_algebra';
  return null;
}

function isHighSchoolBagrutLevel(level: string): boolean {
  return level === '3pt' || level === '4pt' || level === '5pt' || level === 'hs_physics';
}

const SUBJECT_LABELS: Record<string, { en: string; he: string }> = {
  math: { en: 'Mathematics', he: 'מתמטיקה' },
  physics: { en: 'Physics', he: 'פיזיקה' },
  makhina: { en: 'Makhina (pre-university)', he: 'מכינה' },
};

const LEVEL_LABELS: Record<string, string> = {
  '3pt': '3 units (יחידות)',
  '4pt': '4 units (יחידות)',
  '5pt': '5 units (יחידות)',
  hs_physics: '5-unit high-school physics',
  calculus: 'Calculus (Makhina) — university-prep, deeper than Bagrut 5pt',
  stats: 'Statistics & Probability (Makhina)',
  linear_algebra: 'Linear Algebra (Makhina)',
};

const MAKHINA_TOPIC_GUIDANCE: Record<string, string> = {
  calculus: `Focus on university-prep calculus (deeper than Bagrut 5pt):
- Limits and continuity; include ε-δ style reasoning where appropriate
- Derivatives: rules, chain rule, implicit differentiation, applications
- Integrals: definite/indefinite integrals, substitution, integration by parts
- Sequences and series basics
Include ε-δ style questions and advanced integration techniques — not just standard Bagrut items.`,
  stats: `Focus on Makhina statistics & probability:
- Descriptive statistics: mean, median, variance, standard deviation
- Probability: sample spaces, conditional probability, independence
- Bayes' theorem applications
- Normal distribution basics (z-scores, standardization)
- Introductory hypothesis testing concepts`,
  linear_algebra: `Focus on Makhina linear algebra:
- Vectors in R²/R³: magnitude, dot product, cross product (where relevant)
- Matrix operations: addition, multiplication, transpose, inverse (2×2, 3×3)
- Systems of linear equations (Gaussian elimination)
- Eigenvalues and eigenvectors (2×2, 3×3)
- Diagonalization basics`,
};

function requireSql() {
  if (!sql) {
    throw new Error('DATABASE_URL is not configured');
  }
  return sql;
}

export async function ensureMockExamTables(): Promise<void> {
  const s = requireSql();
  await s`
    CREATE TABLE IF NOT EXISTS mock_exams (
      id SERIAL PRIMARY KEY,
      user_id TEXT NOT NULL,
      subject TEXT NOT NULL,
      level TEXT NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      questions JSONB NOT NULL,
      duration_minutes INT NOT NULL DEFAULT 90
    )
  `;
  await s`
    CREATE TABLE IF NOT EXISTS mock_exam_results (
      id SERIAL PRIMARY KEY,
      exam_id INT NOT NULL,
      user_id TEXT NOT NULL,
      answers JSONB NOT NULL,
      score_mcq INT NOT NULL DEFAULT 0,
      max_mcq INT NOT NULL DEFAULT 0,
      time_taken_seconds INT NOT NULL DEFAULT 0,
      feedback JSONB,
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `;
}

function stripForClient(questions: StoredMockExamQuestion[]): ClientMockExamQuestion[] {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  return questions.map(({ correct, model_answer_he, model_answer_en, rubric_he, rubric_en, ...rest }) => rest);
}

const SYSTEM_PROMPT_BAGRUT = `You are a bilingual (Hebrew primary, English secondary) exam author for Israeli Bagrut (בגרות).

Generate an authentic timed mock exam matching REAL Bagrut papers: open multi-part questions with process grading — NOT multiple-choice quizzes.

Output ONLY valid JSON — no commentary, no markdown fences.

Shape:
{
  "questions": [
    {
      "number": 1,
      "kind": "extended",
      "points": 20,
      "stem_he": "<shared stem + parts א/ב/ג in Hebrew>",
      "stem_en": "<shared stem + parts a/b/c in English>",
      "model_answer_he": "<full worked solution all parts>",
      "model_answer_en": "<full worked solution all parts>",
      "rubric_he": "<points per part/step>",
      "rubric_en": "<points per part/step>"
    }
  ]
}

Rules:
- HIGH-SCHOOL BAGRUT: 4–6 questions ONLY, all kind=extended (short_answer allowed only for short calc blocks). NO mcq.
- Each question: 18–25 points, multi-part (א)–(ג)/(א)–(ד), escalating difficulty, ~20–25 minutes.
- Every part uniquely solvable; name shapes explicitly; consistent numbers; HARD only.
- Invent ORIGINAL items. NEVER copy real Ministry of Education exam stems.
- Math in $...$ LaTeX. Hebrew stems primary; English faithful translation.
- NEVER include names, emails, phones, or external links.
- Number questions sequentially from 1.`;

const SYSTEM_PROMPT_UNI = `You are a bilingual exam author for university / Makhina finals.

Generate an authentic timed mock exam. Output ONLY valid JSON.
Shape: { "questions": [ { "number", "kind": "short_answer"|"extended"|"mcq", "points", "stem_he", "stem_en", "options"?, "correct"?, "model_answer_he", "model_answer_en", "rubric_he", "rubric_en" } ] }
Rules: 6–10 questions; at most 1 MCQ; rest open multi-step HARD finals items; invent ORIGINAL items; math in $...$ LaTeX; number from 1.`;

function buildUserPrompt(
  subject: string,
  level: string,
  durationMinutes: number,
  locale: 'he' | 'en' = 'he',
): string {
  const subj = SUBJECT_LABELS[subject] ?? { en: subject, he: subject };
  const levelNote = LEVEL_LABELS[level] ?? level;
  const makhinaTopics =
    subject === 'makhina' ? MAKHINA_TOPIC_GUIDANCE[level] ?? '' : '';
  const primaryLang = locale === 'en' ? 'English' : 'Hebrew';
  const goalKey = goalKeyFromLevel(level);
  const exemplars = pickExamStyleItems({ goalKey, count: 3, rotation: 0, locale: 'he' });
  const exemplarBlock =
    exemplars.length === 0
      ? '(no corpus exemplars)'
      : exemplars
          .map(
            (it, i) =>
              `${i + 1}. [${it.level}/${it.difficulty}] ${formatExamStyleStem(it, 'he').slice(0, 360)}…`,
          )
          .join('\n\n');

  if (isHighSchoolBagrutLevel(level)) {
    return `Subject: ${subj.he} / ${subj.en}
Exam track: ${levelNote}
Exam duration: ${durationMinutes} minutes
Primary display language: ${primaryLang}

ASF exam-style exemplars (match depth; invent NEW solvable items; do not copy):
${exemplarBlock}

Generate a HARD Bagrut-style mock: 4–6 open multi-part questions (no MCQ). Return JSON only.`;
  }

  return `Subject: ${subj.he} / ${subj.en}
Exam track: ${levelNote}
Exam duration: ${durationMinutes} minutes
Primary display language: ${primaryLang}
${makhinaTopics ? `\nTopic guidance:\n${makhinaTopics}\n` : ''}
Exemplars:
${exemplarBlock}

Generate a HARD university/Makhina-style mock (6–10 questions, ≤1 MCQ). Return JSON only.`;
}

/** Compose a mock directly from the exam-style corpus (preferred for HS Bagrut). */
function buildMockFromCorpus(
  level: string,
  durationMinutes: number,
): StoredMockExamQuestion[] | null {
  const goalKey = goalKeyFromLevel(level);
  const n = durationMinutes <= 45 ? 3 : durationMinutes <= 60 ? 4 : 5;
  const items = pickExamStyleItems({
    goalKey,
    count: n,
    rotation: Date.now() % 7,
    requireGoal: Boolean(goalKey),
  });
  if (items.length < 3) return null;
  return items.map((it, index) => ({
    id: randomUUID(),
    number: index + 1,
    kind: 'extended' as const,
    points: Math.min(25, Math.max(15, it.total_points || 20)),
    stem_he: formatExamStyleStem(it, 'he').slice(0, 2000),
    stem_en: formatExamStyleStem(it, 'en').slice(0, 2000),
    model_answer_he: it.sample_solution_he?.slice(0, 1200),
    model_answer_en: it.sample_solution_en?.slice(0, 1200),
    rubric_he: it.rubric_he?.slice(0, 600),
    rubric_en: it.rubric_en?.slice(0, 600),
  }));
}

function validateQuestion(raw: unknown, index: number): StoredMockExamQuestion | null {
  if (!raw || typeof raw !== 'object') return null;
  const q = raw as Record<string, unknown>;
  const kind = q.kind as MockExamQuestionKind;
  if (!['mcq', 'short_answer', 'extended'].includes(kind)) return null;
  if (typeof q.stem_he !== 'string' || q.stem_he.trim().length === 0) return null;
  if (typeof q.stem_en !== 'string' || q.stem_en.trim().length === 0) return null;

  const number = typeof q.number === 'number' ? q.number : index + 1;
  const points =
    typeof q.points === 'number'
      ? Math.max(1, Math.min(25, q.points))
      : kind === 'mcq'
        ? 2
        : kind === 'short_answer'
          ? 3
          : 20;

  const base: StoredMockExamQuestion = {
    id: randomUUID(),
    number,
    kind,
    points,
    stem_he: q.stem_he.trim().slice(0, 2000),
    stem_en: q.stem_en.trim().slice(0, 2000),
    model_answer_he: typeof q.model_answer_he === 'string' ? q.model_answer_he.slice(0, 1200) : undefined,
    model_answer_en: typeof q.model_answer_en === 'string' ? q.model_answer_en.slice(0, 1200) : undefined,
    rubric_he: typeof q.rubric_he === 'string' ? q.rubric_he.slice(0, 600) : undefined,
    rubric_en: typeof q.rubric_en === 'string' ? q.rubric_en.slice(0, 600) : undefined,
  };

  if (kind === 'mcq') {
    if (!Array.isArray(q.options) || q.options.length < 4) return null;
    const options: StoredMockExamQuestion['options'] = [];
    for (const opt of q.options.slice(0, 4)) {
      if (!opt || typeof opt !== 'object') return null;
      const o = opt as Record<string, unknown>;
      if (typeof o.key !== 'string' || typeof o.text_he !== 'string' || typeof o.text_en !== 'string') return null;
      options.push({ key: o.key, text_he: o.text_he, text_en: o.text_en });
    }
    const correct = typeof q.correct === 'string' ? q.correct.toUpperCase() : '';
    if (!['A', 'B', 'C', 'D'].includes(correct)) return null;
    return { ...base, options, correct };
  }

  return base;
}

async function callLLMForMockExam(
  subject: string,
  level: string,
  durationMinutes: number,
  locale: 'he' | 'en' = 'he',
): Promise<StoredMockExamQuestion[] | null> {
  const userPrompt = buildUserPrompt(subject, level, durationMinutes, locale);
  const systemPrompt = isHighSchoolBagrutLevel(level)
    ? SYSTEM_PROMPT_BAGRUT
    : SYSTEM_PROMPT_UNI;

  const parsed = await llmCompleteJson<{ questions?: unknown[] }>({
    system: systemPrompt,
    messages: [{ role: 'user', content: userPrompt }],
    maxTokens: 8000,
    temperature: 0.35,
    timeoutMs: 45_000,
    modelTier: 'primary',
    jsonMode: true,
  });
  if (!parsed || !Array.isArray(parsed.json.questions)) return null;

  const validated: StoredMockExamQuestion[] = [];
  for (let i = 0; i < parsed.json.questions.length; i += 1) {
    const q = validateQuestion(parsed.json.questions[i], i);
    if (q) validated.push(q);
  }
  return validated.length >= 15 ? validated : null;
}

export async function getOrCreateMockExam(
  userId: string,
  subject: string,
  level: string,
  durationMinutes: number,
  locale: 'he' | 'en' = 'he',
): Promise<MockExamStartResponse | null> {
  const s = requireSql();
  await ensureMockExamTables();

  const duration = VALID_DURATIONS.has(durationMinutes) ? durationMinutes : 90;

  try {
    const cached = (await s`
      SELECT id, questions, duration_minutes
      FROM mock_exams
      WHERE user_id = ${userId}
        AND subject = ${subject}
        AND level = ${level}
        AND created_at > NOW() - INTERVAL '24 hours'
      ORDER BY created_at DESC
      LIMIT 1
    `) as Array<{ id: number; questions: StoredMockExamQuestion[]; duration_minutes: number }>;

    if (cached[0]?.questions?.length) {
      const qs = cached[0].questions;
      const mcqCount = qs.filter((q) => q.kind === 'mcq').length;
      // Discard legacy MCQ-heavy caches for HS Bagrut — they are not exam-realistic.
      const legacyMcqHeavy =
        isHighSchoolBagrutLevel(level) && mcqCount >= Math.ceil(qs.length * 0.3);
      if (!legacyMcqHeavy) {
        return {
          exam_id: cached[0].id,
          questions: stripForClient(qs),
          duration_minutes: cached[0].duration_minutes,
        };
      }
    }
  } catch {
    // proceed to generate
  }

  // Prefer composing from the authored exam-style corpus for HS Bagrut.
  let generated: StoredMockExamQuestion[] | null = null;
  if (isHighSchoolBagrutLevel(level) || subject === 'math' || subject === 'physics') {
    generated = buildMockFromCorpus(level, duration);
  }
  if (!generated || generated.length === 0) {
    generated = await callLLMForMockExam(subject, level, duration, locale);
  }
  if (!generated || generated.length === 0) return null;

  try {
    const inserted = (await s`
      INSERT INTO mock_exams (user_id, subject, level, questions, duration_minutes)
      VALUES (${userId}, ${subject}, ${level}, ${JSON.stringify(generated)}::jsonb, ${duration})
      RETURNING id
    `) as Array<{ id: number }>;
    const examId = inserted[0]?.id;
    if (!examId) return null;
    return {
      exam_id: examId,
      questions: stripForClient(generated),
      duration_minutes: duration,
    };
  } catch {
    return null;
  }
}

export async function submitMockExam(
  userId: string,
  examId: number,
  answers: Record<string, string>,
  timeTakenSeconds: number,
): Promise<MockExamSubmitResponse | null> {
  const s = requireSql();
  await ensureMockExamTables();

  const rows = (await s`
    SELECT id, user_id, questions
    FROM mock_exams
    WHERE id = ${examId}
    LIMIT 1
  `) as Array<{ id: number; user_id: string; questions: StoredMockExamQuestion[] }>;

  const exam = rows[0];
  if (!exam || exam.user_id !== userId) return null;

  const questions = exam.questions ?? [];
  let scoreMcq = 0;
  let maxMcq = 0;
  const feedback: MockExamSubmitFeedback[] = [];
  const closedScores: Record<string, number> = {};

  for (const q of questions) {
    const chosen = answers[q.id]?.trim() ?? '';
    if (q.kind === 'mcq') {
      maxMcq += 1;
      const correct = (q.correct ?? '').toUpperCase();
      const isCorrect = chosen.toUpperCase() === correct;
      if (isCorrect) scoreMcq += 1;
      closedScores[q.id] = isCorrect ? 1 : 0;
      feedback.push({
        question_id: q.id,
        correct: isCorrect,
        chosen: chosen || undefined,
        correct_answer: correct,
        explanation_he: q.rubric_he ?? q.model_answer_he,
        explanation_en: q.rubric_en ?? q.model_answer_en,
      });
    } else {
      feedback.push({
        question_id: q.id,
        correct: null,
        chosen: chosen || undefined,
        explanation_he: q.model_answer_he ?? q.rubric_he,
        explanation_en: q.model_answer_en ?? q.rubric_en,
      });
    }
  }

  await s`
    INSERT INTO mock_exam_results (exam_id, user_id, answers, score_mcq, max_mcq, time_taken_seconds, feedback)
    VALUES (
      ${examId},
      ${userId},
      ${JSON.stringify(answers)}::jsonb,
      ${scoreMcq},
      ${maxMcq},
      ${Math.max(0, timeTakenSeconds)},
      ${JSON.stringify(feedback)}::jsonb
    )
  `;

  const { createPendingAttempt } = await import('./assessment-grading');
  const view = await createPendingAttempt({
    learnerId: userId,
    kind: 'mock_exam',
    quizId: String(examId),
    locale: 'he',
    questions: questions.map((q) => ({
      id: q.id,
      topic: q.id,
      subject: '',
      stem: q.stem_he || q.stem_en || '',
      kind: q.kind === 'mcq' ? 'mcq' : 'open',
      options: (q.options ?? []).map((o) => ({
        key: o.key,
        text: o.text_he || o.text_en || '',
      })),
      correct: (q.correct ?? '').toUpperCase(),
      rubric: q.rubric_he ?? q.rubric_en,
      model_answer: q.model_answer_he ?? q.model_answer_en,
      total_points: q.kind === 'mcq' ? 5 : 20,
    })),
    answers: Object.entries(answers).map(([item_id, chosen]) => ({
      item_id,
      chosen: String(chosen ?? ''),
    })),
    closedScores,
    passThreshold: MOCK_PASS_THRESHOLD,
  });

  // Persona line only when already complete (closed-only); otherwise after grade-next.
  if (view?.grading_status === 'complete' && view.score != null) {
    const pct = Math.round(view.score * 100);
    void appendLearnerPersonaLine(
      userId,
      'תצפיות אחרונות',
      `מבחן לדוגמה: ציון ${pct}% לאחר בדיקה — ${view.passed ? 'עבר את רף המוכנות' : 'מתחת לרף המוכנות'}.`,
    ).catch(() => null);
  }

  return {
    score_mcq: scoreMcq,
    max_mcq: maxMcq,
    feedback_by_question: feedback,
    attempt_id: view?.attempt_id ?? null,
    grading_status: view?.grading_status,
    score: view?.score ?? null,
    passed: view?.passed ?? null,
    item_feedback: view?.item_feedback,
    open_pending: view?.open_pending,
    open_total: view?.open_total,
    graded_open: view?.graded_open,
  };
}
