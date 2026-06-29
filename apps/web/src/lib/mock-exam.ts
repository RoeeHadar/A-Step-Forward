/**
 * Bagrut-style timed mock exam generator — Neon/Vercel path (Groq + cache).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

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

const GROQ_MODELS = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];
const GROQ_TIMEOUT_MS = 45_000;

const VALID_DURATIONS = new Set([45, 60, 90]);

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

const SYSTEM_PROMPT = `You are a bilingual (Hebrew primary, English secondary) exam author for Israeli Bagrut (בגרות) high-school exams.

Generate an authentic timed mock exam. Output ONLY valid JSON — no commentary, no markdown fences.

Shape:
{
  "questions": [
    {
      "number": 1,
      "kind": "mcq" | "short_answer" | "extended",
      "points": <int>,
      "stem_he": "<Hebrew question — primary>",
      "stem_en": "<English question — secondary>",
      "options": [{"key":"A","text_he":"...","text_en":"..."}, ...],
      "correct": "A",
      "model_answer_he": "...",
      "model_answer_en": "...",
      "rubric_he": "...",
      "rubric_en": "..."
    }
  ]
}

Rules:
- Generate exactly 20–25 questions total:
  • 8 MCQs (kind=mcq, 2 points each) — exactly 4 options A–D with "correct"
  • 8 short-answer / calculation (kind=short_answer, 3 points each) — NO options; include model_answer_* and rubric_*
  • 4 proof / extended / word-problem (kind=extended, 5–15 points) — NO options; include model_answer_* and rubric_*
- Math in $...$ LaTeX; math always LTR inside delimiters.
- Questions must match the subject and Bagrut level given.
- Hebrew stems are the primary display text; English is a faithful translation.
- NEVER include names, emails, phones, or external links.
- Number questions sequentially from 1.`;

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

  return `Subject: ${subj.he} / ${subj.en}
Exam track: ${levelNote}
Exam duration: ${durationMinutes} minutes
Primary display language: ${primaryLang}
${makhinaTopics ? `\nTopic guidance:\n${makhinaTopics}\n` : ''}
Generate a full ${subject === 'makhina' ? 'Makhina university-prep' : 'Bagrut-style'} mock exam (20–25 questions) appropriate for this subject and level.
Mix difficulty: some easy warm-up, mostly exam-realistic, 2–3 challenging items.
When primary language is English, stem_en must be the main exam text and stem_he a faithful translation.

Return JSON only.`;
}

function validateQuestion(raw: unknown, index: number): StoredMockExamQuestion | null {
  if (!raw || typeof raw !== 'object') return null;
  const q = raw as Record<string, unknown>;
  const kind = q.kind as MockExamQuestionKind;
  if (!['mcq', 'short_answer', 'extended'].includes(kind)) return null;
  if (typeof q.stem_he !== 'string' || q.stem_he.trim().length === 0) return null;
  if (typeof q.stem_en !== 'string' || q.stem_en.trim().length === 0) return null;

  const number = typeof q.number === 'number' ? q.number : index + 1;
  const points = typeof q.points === 'number' ? Math.max(1, Math.min(20, q.points)) : kind === 'mcq' ? 2 : kind === 'short_answer' ? 3 : 10;

  const base: StoredMockExamQuestion = {
    id: randomUUID(),
    number,
    kind,
    points,
    stem_he: q.stem_he.trim().slice(0, 1200),
    stem_en: q.stem_en.trim().slice(0, 1200),
    model_answer_he: typeof q.model_answer_he === 'string' ? q.model_answer_he.slice(0, 800) : undefined,
    model_answer_en: typeof q.model_answer_en === 'string' ? q.model_answer_en.slice(0, 800) : undefined,
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

async function callGroqForMockExam(
  subject: string,
  level: string,
  durationMinutes: number,
  locale: 'he' | 'en' = 'he',
): Promise<StoredMockExamQuestion[] | null> {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) return null;

  const userPrompt = buildUserPrompt(subject, level, durationMinutes, locale);
  const systemPrompt =
    locale === 'en'
      ? SYSTEM_PROMPT.replace(
          'Hebrew stems are the primary display text; English is a faithful translation.',
          'English stems are the primary display text; Hebrew is a faithful translation.',
        )
      : SYSTEM_PROMPT;

  for (const model of GROQ_MODELS) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), GROQ_TIMEOUT_MS);
    try {
      const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt },
          ],
          response_format: { type: 'json_object' },
          max_tokens: 8000,
          temperature: 0.35,
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (!resp.ok) {
        if (resp.status === 401 || resp.status === 403) return null;
        continue;
      }
      const body = (await resp.json()) as { choices?: Array<{ message?: { content?: string } }> };
      const raw = body.choices?.[0]?.message?.content;
      if (!raw) continue;
      const parsed = JSON.parse(raw) as { questions?: unknown[] };
      if (!Array.isArray(parsed.questions)) continue;

      const validated: StoredMockExamQuestion[] = [];
      for (let i = 0; i < parsed.questions.length; i += 1) {
        const q = validateQuestion(parsed.questions[i], i);
        if (q) validated.push(q);
      }
      if (validated.length >= 15) return validated;
    } catch {
      clearTimeout(timeoutId);
    }
  }
  return null;
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
      return {
        exam_id: cached[0].id,
        questions: stripForClient(cached[0].questions),
        duration_minutes: cached[0].duration_minutes,
      };
    }
  } catch {
    // proceed to generate
  }

  const generated = await callGroqForMockExam(subject, level, duration, locale);
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

  for (const q of questions) {
    const chosen = answers[q.id]?.trim() ?? '';
    if (q.kind === 'mcq') {
      maxMcq += 1;
      const correct = (q.correct ?? '').toUpperCase();
      const isCorrect = chosen.toUpperCase() === correct;
      if (isCorrect) scoreMcq += 1;
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

  return { score_mcq: scoreMcq, max_mcq: maxMcq, feedback_by_question: feedback };
}
