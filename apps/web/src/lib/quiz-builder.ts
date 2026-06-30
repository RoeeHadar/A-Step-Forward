/**
 * AI-driven custom quiz builder — Bagrut / University exam style.
 *
 * Generates open-ended, multi-part questions that mirror real Israeli
 * Bagrut exams (HS math/physics) and university finals (calculus, LA, physics).
 *
 * Key design decisions:
 *  - HS students (bagrut_math_3/4/5, bagrut_physics) always get open-ended,
 *    multi-part questions in Hebrew, identical in style to real Bagrut exams.
 *  - University students (calculus1, linear_algebra, physics1/2, statistics)
 *    get open-ended proofs/computations. Rare MCQ allowed in university_mixed mode.
 *  - Timing: 22 min/question for Bagrut, 35 min/question for university.
 *    Capped to 1–4 questions per session.
 *  - Each open question: shared stem + 3-4 sub-parts (א/ב/ג or a/b/c),
 *    complete worked sample solution, point-by-point rubric.
 *
 * Skill reference: `skills/build-custom-quiz/SKILL.md`.
 */
import 'server-only';
import {
  getConceptMastery,
  getLearnerProfile,
  fetchLessonAgentHintsByConceptIds,
  type LearnerProfileRow,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';
import { effectiveGradeLevel } from '@/lib/grade-level';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  points_levels: string[];
  bagrut_chapter: string | null;
  skill_atoms: string[];
  level_scope: Record<string, string>;
  prerequisites: string[];
}

const kgConcepts = (kg as { concepts: KgConcept[] }).concepts;
const kgById: Record<string, KgConcept> =
  (kg as { byId: Record<string, KgConcept> }).byId;

// Keep backward compatibility — the API accepts these as hints but we override
// server-side based on the learner's profile.
export type QuizKindMix = 'closed' | 'open' | 'mixed' | 'bagrut_open' | 'university_open' | 'university_mixed';

export type QuizMode = 'bagrut_open' | 'university_open' | 'university_mixed';

export interface CustomQuizRequest {
  /** Accepted for API compat; server overrides this from student profile. */
  kind_mix?: QuizKindMix;
  /** Total minutes the learner wants to spend. Clamped to [3, 90]. */
  time_limit_min: number;
  /** Optional list of concept ids to focus on. */
  topics?: string[];
}

export interface QuizQuestionPart {
  label: string;       // "א", "ב", "ג", "ד" or "a", "b", "c", "d"
  body_en: string;
  body_he: string;
  points: number;
}

export interface CustomQuizQuestion {
  ord: number;
  kind: 'open' | 'mcq';
  difficulty: 'easy' | 'medium' | 'hard';
  concept_id: string;
  skill_atoms: string[];
  // Main question stem (scenario/context shared by all parts)
  stem_en: string;
  stem_he: string;
  // Multi-part structure (required for open, optional for mcq)
  parts?: QuizQuestionPart[];
  total_points: number;
  // Full worked solution (revealed after submission only)
  sample_solution_en: string;
  sample_solution_he: string;
  // Rubric / marking scheme
  rubric_en: string;
  rubric_he: string;
  // MCQ only (rare, university_mixed mode only)
  options_en?: string[];
  options_he?: string[];
  correct_index?: number;
  explanation_en?: string;
  explanation_he?: string;
}

export interface CustomQuizEnvelope {
  quiz_id: string;
  kind_mix: QuizKindMix;
  mode: QuizMode;
  time_limit_s: number;
  concepts: Array<{ id: string; name: string; name_he: string | null; subject: string }>;
  questions: CustomQuizQuestion[];
  picked_reason: 'user_topics' | 'weakest_mastery' | 'subject_bootstrap';
  model?: string;
}

const MIN_TIME = 3;
const MAX_TIME = 90;

const UNIVERSITY_GOALS = new Set([
  'calculus1', 'linear_algebra', 'physics1', 'physics2', 'statistics',
]);

function getQuizMode(profile: LearnerProfileRow | null): QuizMode {
  const goal = profile?.goal ?? '';
  if (UNIVERSITY_GOALS.has(goal)) return 'university_open';
  return 'bagrut_open';
}

function questionCountFromBudget(
  timeMin: number,
  profile: LearnerProfileRow | null,
): number {
  const goal = profile?.goal ?? '';
  const isUniversity = UNIVERSITY_GOALS.has(goal);
  const minutesPerQuestion = isUniversity ? 35 : 22;
  const raw = Math.floor(timeMin / minutesPerQuestion);
  return Math.max(1, Math.min(4, raw));
}

function pickConcepts(
  req: CustomQuizRequest,
  mastery: Record<string, number>,
  profile: LearnerProfileRow | null,
): { ids: string[]; reason: CustomQuizEnvelope['picked_reason'] } {
  if (req.topics && req.topics.length > 0) {
    const ids = req.topics.filter((c) => Boolean(kgById[c]));
    if (ids.length > 0) return { ids, reason: 'user_topics' };
  }
  const touched = Object.entries(mastery)
    .sort((a, b) => a[1] - b[1])
    .map(([c]) => c)
    .filter((c) => Boolean(kgById[c]));
  if (touched.length >= 3) {
    return { ids: touched.slice(0, 6), reason: 'weakest_mastery' };
  }
  const subjects = (profile?.subjects && profile.subjects.length > 0)
    ? profile.subjects
    : ['math'];
  const subjectSet = new Set(subjects.map((s) => s.toLowerCase()));
  const roots = kgConcepts
    .filter((c) => subjectSet.has(c.subject) && c.prerequisites.length === 0)
    .map((c) => c.id);
  const fallback = roots.length > 0
    ? roots.slice(0, 6)
    : kgConcepts.slice(0, 6).map((c) => c.id);
  return { ids: fallback, reason: 'subject_bootstrap' };
}

const SYSTEM_PROMPT = `You are an expert bilingual (Hebrew + English) Israeli math and physics exam author.
You write exam questions that are IDENTICAL in style and difficulty to real Israeli Bagrut exams and university final exams.

CRITICAL RULES FOR BAGRUT-STYLE QUESTIONS (mode: bagrut_open):
1. Questions are ALWAYS open-ended, multi-part (parts א, ב, ג). NEVER multiple-choice.
2. Each question has a shared context/scenario at the top (the "stem"), then 3 sub-parts building on it.
3. Students must show all work. Each part requires written computation or proof.
4. Parts are sequenced: Part א is foundational (easy-medium), Parts ב/ג increase in difficulty.
5. Allocate points per part: typically total 20-25 points spread across parts.
6. Language: Hebrew is default. stem_he and all part body_he fields MUST be in proper Hebrew.
7. Math ALWAYS in $...$ or $$...$$ LaTeX, in both languages.
8. Question style matches real Bagrut: geometric proofs, algebraic manipulation, function analysis, trigonometry, sequences, statistics — depending on the concept.
9. Each question should take a student ~20-25 minutes to complete in full.
10. sample_solution_en/he must show COMPLETE worked solutions for every part, step by step.
11. rubric_en/he must specify points per step (e.g. "2 pts for setting up equation, 3 pts for correct computation").

CRITICAL RULES FOR UNIVERSITY QUESTIONS (mode: university_open or university_mixed):
1. Questions are mostly open-ended proofs or computations showing all work.
2. In university_mixed mode: up to 1 MCQ question per quiz (for concept verification), rest are open.
3. University questions require rigorous notation: limits, ε-δ proofs, formal linear algebra notation, etc.
4. Each question takes ~35 minutes and has 2-3 sub-parts.
5. Calculus questions: limits, derivatives with chain rule/product rule, integrals (including by parts/substitution), series convergence.
6. Linear Algebra questions: matrix operations, eigenvalues, linear transformations, vector spaces.
7. Physics questions: mechanics (forces, energy, momentum), electricity (circuits, fields), with SI units.

OUTPUT FORMAT (JSON only, no commentary):
{
  "questions": [
    {
      "ord": 1,
      "kind": "open",
      "difficulty": "medium",
      "concept_id": "...",
      "skill_atoms": ["..."],
      "stem_en": "Context/scenario in English...",
      "stem_he": "הקשר/תרחיש בעברית...",
      "parts": [
        { "label": "א", "body_en": "Find...", "body_he": "מצא את...", "points": 8 },
        { "label": "ב", "body_en": "Prove that...", "body_he": "הוכח ש...", "points": 8 },
        { "label": "ג", "body_en": "Calculate...", "body_he": "חשב את...", "points": 9 }
      ],
      "total_points": 25,
      "sample_solution_en": "Part א: [full worked solution...] Part ב: [full worked solution...] Part ג: [full worked solution...]",
      "sample_solution_he": "חלק א: [פתרון מלא...] חלק ב: [פתרון מלא...] חלק ג: [פתרון מלא...]",
      "rubric_en": "Part א: 4pts for setup, 4pts for correct answer. Part ב: 4pts for proof structure, 4pts for completing proof. Part ג: 5pts for method, 4pts for result.",
      "rubric_he": "חלק א: 4 נקודות להצבה, 4 נקודות לתשובה. חלק ב: 4 נקודות למבנה ההוכחה, 4 נקודות להשלמה. חלק ג: 5 נקודות לשיטה, 4 נקודות לתוצאה."
    }
  ]
}

For MCQ (university_mixed only):
{
  "ord": 1,
  "kind": "mcq",
  "difficulty": "easy",
  "concept_id": "...",
  "skill_atoms": ["..."],
  "stem_en": "...",
  "stem_he": "...",
  "total_points": 5,
  "sample_solution_en": "The correct answer is option B because...",
  "sample_solution_he": "התשובה הנכונה היא אפשרות ב' כי...",
  "rubric_en": "5pts for correct answer.",
  "rubric_he": "5 נקודות לתשובה נכונה.",
  "options_en": ["option A", "option B", "option C", "option D"],
  "options_he": ["אפשרות א", "אפשרות ב", "אפשרות ג", "אפשרות ד"],
  "correct_index": 1,
  "explanation_en": "...",
  "explanation_he": "..."
}

NEVER output: true_false, numeric, short_answer.
NEVER output MCQ without university_mixed mode.
NEVER output questions shorter than 3 parts for bagrut_open mode (university mode may have 2+ parts).
ALWAYS produce complete sample solutions — do not abbreviate them.
ALWAYS write stem_he and part body_he in proper modern Hebrew.`;

interface ConceptCtx {
  id: string;
  name_en: string;
  name_he: string | null;
  subject: string;
  level: string;
  bagrut_chapter: string | null;
  atoms: string[];
  level_scope_note: string | null;
  mastery: number | null;
  insights: string[];
}

function buildUserPrompt(
  ctx: ConceptCtx[],
  mode: QuizMode,
  count: number,
  profile: LearnerProfileRow | null,
): string {
  const goal = profile?.goal ?? null;
  const grade = effectiveGradeLevel(profile?.grade_level ?? null);

  const GOAL_TO_LEVEL_KEY: Record<string, string> = {
    bagrut_math_3: '3pt', bagrut_math_4: '4pt', bagrut_math_5: '5pt',
    bagrut_physics: 'hs_physics', calculus1: 'calc1', linear_algebra: 'la',
  };
  const levelKey = goal ? (GOAL_TO_LEVEL_KEY[goal] ?? null) : null;

  const profileLine = profile
    ? [
        `Profile: goal=${goal ?? 'n/a'}, grade=${grade ?? 'n/a'}`,
        `subjects=${(profile.subjects ?? []).join(',')}`,
        levelKey ? `points_level=${levelKey}` : null,
      ].filter(Boolean).join(', ') + '.'
    : 'Profile: brand-new learner (no profile).';

  const conceptBlocks = ctx.map((c) => {
    const masteryLabel =
      c.mastery == null
        ? 'unmeasured'
        : c.mastery >= 0.7 ? 'strong'
        : c.mastery >= 0.4 ? 'medium'
        : 'weak';
    const atoms = c.atoms.length > 0
      ? c.atoms.slice(0, 15).join(' | ')
      : '(no atoms — generate from concept name)';
    const insights = c.insights.length > 0
      ? `learner_insights: ${c.insights.slice(0, 3).join(' | ')}`
      : null;
    const scopeNote = c.level_scope_note
      ? `depth_for_this_level: ${c.level_scope_note}`
      : null;
    return [
      `### concept: ${c.id}`,
      `name_en: ${c.name_en}`,
      c.name_he ? `name_he: ${c.name_he}` : null,
      `subject: ${c.subject} | chapter: ${c.bagrut_chapter ?? 'general'} | mastery: ${masteryLabel}`,
      `skill_atoms: ${atoms}`,
      scopeNote,
      insights,
    ].filter(Boolean).join('\n');
  }).join('\n\n');

  const modeInstructions =
    mode === 'bagrut_open'
      ? `MODE: bagrut_open
Each question MUST have exactly 3 parts labeled א, ב, ג.
Questions mirror real Bagrut exam questions — multi-step, open-ended, in Hebrew.
Total points per question: 20-25. Each part: 7-9 points.
Language: stem_he and all part body_he in proper modern Hebrew. stem_en is the English translation.`
      : mode === 'university_open'
      ? `MODE: university_open
Questions are open-ended proofs and computations, university exam style.
Each question has 2-3 sub-parts (a, b, c or א, ב, ג).
Rigorous mathematical/physical notation required.
Total points per question: 20-30.`
      : `MODE: university_mixed
Mostly open questions. You MAY include at most 1 MCQ question total (for a basic concept check).
The rest must be open-ended proofs/computations with sub-parts.`;

  return `${profileLine}

exam_mode: ${mode}
question_count: ${count}

${modeInstructions}

DEPTH CALIBRATION:
- The learner's goal is ${goal ?? 'general'}.
- Adjust EVERY question to match this level.
  * 3pt math: practical, concrete, no calculus, everyday language.
  * 5pt math: may include derivatives, integrals, proofs, advanced manipulation.
  * hs_physics: Bagrut-level, formula-based, multi-step problems.
  * calc1: rigorous; limits, derivatives, integrals with proper notation.
- The "depth_for_this_level" lines below specify EXACTLY what depth to expect per concept.

Allowed concepts, their skill atoms, and depth notes:

${conceptBlocks}

Generate exactly ${count} exam-style question(s) now.
Each question must test at least one skill_atom from the list above.
Spread questions across the listed concepts where possible.
Follow ALL rules in the system message. Return JSON only.`;
}

// ── Groq ----------------------------------------------------------------------
const GROQ_MODELS = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];
const GROQ_TIMEOUT_MS = 45_000; // longer timeout — open questions need more tokens

async function callGroq(systemPrompt: string, userPrompt: string) {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) return null;
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
          max_tokens: 6000, // open questions with solutions need more space
          temperature: 0.4,
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (!resp.ok) {
        if (resp.status === 401 || resp.status === 403) return null;
        continue;
      }
      const body = (await resp.json()) as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      const raw = body.choices?.[0]?.message?.content;
      if (!raw) continue;
      try {
        const parsed = JSON.parse(raw) as { questions?: unknown };
        if (Array.isArray(parsed.questions)) {
          return { questions: parsed.questions, model };
        }
      } catch {
        // try next model
      }
    } catch {
      clearTimeout(timeoutId);
    }
  }
  return null;
}

function isStr(x: unknown): x is string {
  return typeof x === 'string' && x.trim().length > 0;
}

function validateQuestion(
  raw: unknown,
  mode: QuizMode,
  allowedConcepts: Set<string>,
  ord: number,
): CustomQuizQuestion | null {
  if (!raw || typeof raw !== 'object') return null;
  const q = raw as Record<string, unknown>;

  // Kind validation — mode-aware
  if (typeof q.kind !== 'string') return null;
  const kind = q.kind as string;
  if (kind !== 'open' && kind !== 'mcq') {
    // Legacy fallback: treat short_answer/numeric/true_false as open with a textarea
    if (!['short_answer', 'numeric', 'true_false'].includes(kind)) return null;
    // coerce to open
    (q as Record<string, unknown>).kind = 'open';
  }
  // MCQ only allowed in university_mixed
  if (q.kind === 'mcq' && mode !== 'university_mixed') return null;

  if (q.difficulty !== 'easy' && q.difficulty !== 'medium' && q.difficulty !== 'hard') return null;
  if (typeof q.concept_id !== 'string' || !allowedConcepts.has(q.concept_id)) return null;
  if (!isStr(q.stem_en) || !isStr(q.stem_he)) return null;

  const atoms = Array.isArray(q.skill_atoms) ? q.skill_atoms.filter(isStr) : [];

  const totalPoints =
    typeof q.total_points === 'number' && q.total_points > 0
      ? q.total_points
      : 25;

  const sampleSolEn = isStr(q.sample_solution_en) ? (q.sample_solution_en as string) : '';
  const sampleSolHe = isStr(q.sample_solution_he) ? (q.sample_solution_he as string) : '';
  const rubricEn = isStr(q.rubric_en) ? (q.rubric_en as string) : '';
  const rubricHe = isStr(q.rubric_he) ? (q.rubric_he as string) : '';

  const base: CustomQuizQuestion = {
    ord,
    kind: q.kind as 'open' | 'mcq',
    difficulty: q.difficulty as 'easy' | 'medium' | 'hard',
    concept_id: q.concept_id as string,
    skill_atoms: atoms,
    stem_en: q.stem_en as string,
    stem_he: q.stem_he as string,
    total_points: totalPoints,
    sample_solution_en: sampleSolEn,
    sample_solution_he: sampleSolHe,
    rubric_en: rubricEn,
    rubric_he: rubricHe,
  };

  if (q.kind === 'open') {
    // Parse parts
    if (Array.isArray(q.parts) && q.parts.length >= 2) {
      const parts: QuizQuestionPart[] = [];
      for (const p of q.parts) {
        if (!p || typeof p !== 'object') continue;
        const part = p as Record<string, unknown>;
        if (!isStr(part.label) || !isStr(part.body_en) || !isStr(part.body_he)) continue;
        const pts = typeof part.points === 'number' && part.points > 0 ? part.points : 8;
        parts.push({
          label: part.label as string,
          body_en: part.body_en as string,
          body_he: part.body_he as string,
          points: pts,
        });
      }
      if (parts.length >= 2) base.parts = parts;
    }
    // For open questions without parts (shouldn't happen with good prompting),
    // still valid — client shows single textarea
    return base;
  }

  if (q.kind === 'mcq') {
    if (!Array.isArray(q.options_en) || !Array.isArray(q.options_he)) return null;
    const en = q.options_en.filter(isStr) as string[];
    const he = q.options_he.filter(isStr) as string[];
    if (en.length !== he.length || en.length < 2) return null;
    if (typeof q.correct_index !== 'number' || q.correct_index < 0 || q.correct_index >= en.length) return null;
    base.options_en = en;
    base.options_he = he;
    base.correct_index = q.correct_index;
    base.explanation_en = isStr(q.explanation_en) ? (q.explanation_en as string) : undefined;
    base.explanation_he = isStr(q.explanation_he) ? (q.explanation_he as string) : undefined;
    return base;
  }

  return null;
}

function randomId() {
  return globalThis.crypto?.randomUUID() ?? `q_${Date.now()}_${Math.random().toString(36).slice(2)}`;
}

/**
 * Build a fit-to-purpose AI quiz for one learner in Bagrut/university exam style.
 * Returns `null` if Groq is unavailable or output couldn't be parsed.
 */
export async function buildCustomQuiz(
  learnerId: string,
  reqIn: CustomQuizRequest,
): Promise<CustomQuizEnvelope | null> {
  const req: CustomQuizRequest = {
    kind_mix: reqIn.kind_mix ?? 'open',
    time_limit_min: Math.max(MIN_TIME, Math.min(MAX_TIME, Math.floor(reqIn.time_limit_min))),
    topics: reqIn.topics,
  };

  const [mastery, profile] = await Promise.all([
    getConceptMastery(learnerId).catch(() => ({} as Record<string, number>)),
    getLearnerProfile(learnerId).catch(() => null),
  ]);

  const mode = getQuizMode(profile);
  const picked = pickConcepts(req, mastery, profile);
  const hintsRows = await fetchLessonAgentHintsByConceptIds(picked.ids).catch(() => []);
  const hintsByConcept = new Map(hintsRows.map((r) => [r.concept_id, r.agent_hints]));

  const GOAL_TO_LEVEL_KEY: Record<string, string> = {
    bagrut_math_3: '3pt', bagrut_math_4: '4pt', bagrut_math_5: '5pt',
    bagrut_physics: 'hs_physics', calculus1: 'calc1', linear_algebra: 'la',
  };
  const levelKey = profile?.goal ? (GOAL_TO_LEVEL_KEY[profile.goal] ?? null) : null;

  const ctx: ConceptCtx[] = picked.ids
    .map((id) => kgById[id])
    .filter((c): c is KgConcept => Boolean(c))
    .map((c) => {
      const hints = hintsByConcept.get(c.id) ?? null;
      const kgAtoms = c.skill_atoms ?? [];
      const lessonAtoms = hints?.skill_atoms_unlocked ?? [];
      const mergedAtoms = kgAtoms.length > 0 ? kgAtoms : lessonAtoms;
      const scopeNote = levelKey && c.level_scope
        ? (c.level_scope[levelKey] ?? null)
        : null;
      return {
        id: c.id,
        name_en: c.name,
        name_he: c.name_he,
        subject: c.subject,
        level: c.level,
        bagrut_chapter: c.bagrut_chapter,
        atoms: mergedAtoms,
        level_scope_note: scopeNote,
        mastery: mastery[c.id] ?? null,
        insights: hints?.key_insights ?? [],
      };
    });

  if (ctx.length === 0) return null;

  const count = questionCountFromBudget(req.time_limit_min, profile);
  const conceptSet = new Set(ctx.map((c) => c.id));

  const groq = await callGroq(SYSTEM_PROMPT, buildUserPrompt(ctx, mode, count, profile));
  if (!groq) return null;

  const validated: CustomQuizQuestion[] = [];
  for (const raw of groq.questions) {
    const q = validateQuestion(raw, mode, conceptSet, validated.length + 1);
    if (q) validated.push(q);
  }
  if (validated.length === 0) return null;

  return {
    quiz_id: randomId(),
    kind_mix: req.kind_mix ?? 'open',
    mode,
    time_limit_s: req.time_limit_min * 60,
    concepts: ctx.map((c) => ({
      id: c.id,
      name: c.name_en,
      name_he: c.name_he,
      subject: c.subject,
    })),
    questions: validated,
    picked_reason: picked.reason,
    model: groq.model,
  };
}
