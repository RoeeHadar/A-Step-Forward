/**
 * AI-driven custom quiz builder.
 *
 * Given a learner + a small set of form inputs (kind mix, time budget,
 * optional topic list), this library:
 *
 *   1. Picks the concepts to test. If the form supplies topics, those win
 *      verbatim; otherwise we pick the learner's weakest concepts from
 *      `concept_mastery` (or, for a brand-new learner, a small bootstrap
 *      set covering the subjects in their profile).
 *   2. Sizes the question count from the user's time budget — closed
 *      questions ~1 min, open questions ~3 min, mixed averages to ~2 min.
 *   3. Calls Groq to author bilingual EN+HE questions, restricted to the
 *      lesson-corpus skill atoms for each chosen concept where available
 *      so the planner can still attribute mastery from the answers.
 *   4. Validates the model output against the same per-kind schema used
 *      by `scripts/seed-lessons.mjs` and drops any malformed item.
 *
 * The result is intentionally NOT persisted as an authored lesson — it's
 * an ephemeral, fit-to-purpose quiz. Submissions are graded client-side
 * for closed kinds; open kinds get a rubric-style self-review on the
 * result screen. Mastery / skill-practice updates happen via the regular
 * `/api/lesson/answer` path when the learner submits a quiz item.
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

export type QuizKindMix = 'closed' | 'open' | 'mixed';

export interface CustomQuizRequest {
  /** Closed = mcq/true_false/numeric. Open = short_answer/open. Mixed = both. */
  kind_mix: QuizKindMix;
  /** Total minutes the learner wants to spend. Clamped to [3, 90]. */
  time_limit_min: number;
  /** Optional list of concept ids to focus on. If empty / omitted we pick
   *  the learner's weakest mastery concepts. */
  topics?: string[];
}

export interface CustomQuizQuestion {
  ord: number;
  kind: 'mcq' | 'true_false' | 'numeric' | 'short_answer' | 'open';
  difficulty: 'easy' | 'medium' | 'hard';
  concept_id: string;
  skill_atoms: string[];
  stem_en: string;
  stem_he: string;
  explanation_en: string;
  explanation_he: string;
  // mcq
  options_en?: string[];
  options_he?: string[];
  correct_index?: number;
  // true_false
  correct_bool?: boolean;
  // numeric
  correct_answer?: string;
  // short_answer
  acceptable_answers?: string[];
  // open
  rubric_en?: string;
  rubric_he?: string;
}

export interface CustomQuizEnvelope {
  /** Local UUID for this ephemeral quiz (not persisted). */
  quiz_id: string;
  kind_mix: QuizKindMix;
  time_limit_s: number;
  concepts: Array<{ id: string; name: string; name_he: string | null; subject: string }>;
  questions: CustomQuizQuestion[];
  /** Reason the AI fell back / picked these — surfaced in the UI. */
  picked_reason: 'user_topics' | 'weakest_mastery' | 'subject_bootstrap';
  model?: string;
}

const MIN_TIME = 3;
const MAX_TIME = 90;

function pickConcepts(
  req: CustomQuizRequest,
  mastery: Record<string, number>,
  profile: LearnerProfileRow | null,
): { ids: string[]; reason: CustomQuizEnvelope['picked_reason'] } {
  // User explicitly chose topics → trust them, but drop any that aren't in the KG.
  if (req.topics && req.topics.length > 0) {
    const ids = req.topics.filter((c) => Boolean(kgById[c]));
    if (ids.length > 0) return { ids, reason: 'user_topics' };
  }
  // Otherwise: weakest mastery concepts the learner has actually touched.
  const touched = Object.entries(mastery)
    .sort((a, b) => a[1] - b[1])
    .map(([c]) => c)
    .filter((c) => Boolean(kgById[c]));
  if (touched.length >= 3) {
    return { ids: touched.slice(0, 6), reason: 'weakest_mastery' };
  }
  // Brand-new learner: bootstrap from the subjects in their profile (or a
  // sensible default mix of math + physics roots).
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

function questionCountFromBudget(
  timeMin: number,
  mix: QuizKindMix,
): number {
  const minutesPerQ = mix === 'open' ? 3.5 : mix === 'mixed' ? 2 : 1.2;
  const raw = Math.floor(timeMin / minutesPerQ);
  return Math.max(3, Math.min(20, raw));
}

const SYSTEM_PROMPT = `You are an expert bilingual (Hebrew + English) curriculum author for an AI tutoring platform aimed at Israeli high-school and university students.

You are generating ONE custom diagnostic quiz for ONE specific learner. STRICT requirements:

1. Output ONLY JSON, no commentary. Shape:
   { "questions": [ { ... }, { ... } ] }
2. Each question must include BOTH "stem_en" and "stem_he", BOTH "explanation_en" and "explanation_he", "concept_id" (one of the supplied concept ids), "skill_atoms" (drawn ONLY from the supplied atoms for that concept; empty array is fine), "difficulty" ("easy" | "medium" | "hard"), and "kind".
3. Allowed kinds depend on the requested kind_mix:
   - "closed": mcq, true_false, numeric
   - "open":   short_answer, open
   - "mixed":  any of the five
4. Per-kind shape:
   - mcq:          options_en[], options_he[] (same length, 3-4 items), correct_index (int)
   - true_false:   correct_bool (boolean)
   - numeric:      correct_answer (string, e.g. "12.5" or "12.5 m")
   - short_answer: acceptable_answers (string[]; 1-4 case-insensitive variants)
   - open:         rubric_en (string, 1-3 sentences), rubric_he (string)
5. Difficulty distribution: at least one easy + at least one medium when count >= 3; include at least one hard when count >= 6.
6. Cover DIFFERENT aspects of the supplied concepts; spread questions roughly evenly across them.
7. Math in $...$ / $$...$$ LaTeX in BOTH languages; do not translate LaTeX. Hebrew is right-to-left text; math is left-to-right.
8. Each stem <= 600 chars, each explanation <= 600 chars, each rubric <= 600 chars.
9. NEVER include real names, school names, emails, phones, or addresses.`;

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
  mix: QuizKindMix,
  count: number,
  profile: LearnerProfileRow | null,
): string {
  const goal = profile?.goal ?? null;
  const grade = profile?.grade_level ?? null;

  // Derive the learner's points level from their goal for level_scope lookup
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

  return `${profileLine}

kind_mix: ${mix}
question_count: ${count}

IMPORTANT — depth calibration:
- The learner's goal is ${goal ?? 'general'}.
- Adjust EVERY question to match this level. For example:
  * 3pt math: practical, concrete, no calculus, everyday language.
  * 5pt math: may include derivatives, integrals, proofs, advanced manipulation.
  * hs_physics: Bagrut-level, formula-based, multi-step.
  * calc1: rigorous; limits, derivatives, integrals with proper notation.
- The "depth_for_this_level" lines below specify EXACTLY what depth to expect per concept.

Allowed concepts, their skill atoms, and depth notes:

${conceptBlocks}

Generate exactly ${count} fit-to-purpose questions now.
Each question must test ONE specific skill_atom from the list above (reference it in the skill_atoms field).
Spread questions evenly across the listed concepts.
Follow every rule in the system message. Return JSON only.`;
}

// ── Groq ----------------------------------------------------------------------
const GROQ_MODELS = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'];
const GROQ_TIMEOUT_MS = 35_000;

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
          max_tokens: 4096,
          temperature: 0.45,
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

const ALLOWED_KINDS_BY_MIX: Record<QuizKindMix, Set<string>> = {
  closed: new Set(['mcq', 'true_false', 'numeric']),
  open: new Set(['short_answer', 'open']),
  mixed: new Set(['mcq', 'true_false', 'numeric', 'short_answer', 'open']),
};

function isStr(x: unknown): x is string {
  return typeof x === 'string' && x.trim().length > 0;
}

function validateQuestion(
  raw: unknown,
  allowedKinds: Set<string>,
  allowedConcepts: Set<string>,
): CustomQuizQuestion | null {
  if (!raw || typeof raw !== 'object') return null;
  const q = raw as Record<string, unknown>;
  if (typeof q.kind !== 'string' || !allowedKinds.has(q.kind)) return null;
  if (q.difficulty !== 'easy' && q.difficulty !== 'medium' && q.difficulty !== 'hard') return null;
  if (typeof q.concept_id !== 'string' || !allowedConcepts.has(q.concept_id)) return null;
  if (!isStr(q.stem_en) || !isStr(q.stem_he)) return null;
  if (!isStr(q.explanation_en) || !isStr(q.explanation_he)) return null;
  const atoms = Array.isArray(q.skill_atoms) ? q.skill_atoms.filter(isStr) : [];
  // Keep all atoms the model returned — we now verify concept_id (which is strict)
  // but don't restrict the exact atom text since the model may paraphrase.
  const filteredAtoms = atoms;
  const base: CustomQuizQuestion = {
    ord: 0,
    kind: q.kind as CustomQuizQuestion['kind'],
    difficulty: q.difficulty,
    concept_id: q.concept_id,
    skill_atoms: filteredAtoms,
    stem_en: q.stem_en,
    stem_he: q.stem_he,
    explanation_en: q.explanation_en,
    explanation_he: q.explanation_he,
  };
  if (q.kind === 'mcq') {
    if (!Array.isArray(q.options_en) || !Array.isArray(q.options_he)) return null;
    const en = q.options_en.filter(isStr);
    const he = q.options_he.filter(isStr);
    if (en.length !== he.length || en.length < 2) return null;
    if (typeof q.correct_index !== 'number' || q.correct_index < 0 || q.correct_index >= en.length) return null;
    base.options_en = en;
    base.options_he = he;
    base.correct_index = q.correct_index;
  } else if (q.kind === 'true_false') {
    if (typeof q.correct_bool !== 'boolean') return null;
    base.correct_bool = q.correct_bool;
  } else if (q.kind === 'numeric') {
    if (!isStr(q.correct_answer)) return null;
    base.correct_answer = q.correct_answer;
  } else if (q.kind === 'short_answer') {
    if (!Array.isArray(q.acceptable_answers)) return null;
    const ans = q.acceptable_answers.filter(isStr);
    if (ans.length === 0) return null;
    base.acceptable_answers = ans;
  } else if (q.kind === 'open') {
    if (!isStr(q.rubric_en) || !isStr(q.rubric_he)) return null;
    base.rubric_en = q.rubric_en;
    base.rubric_he = q.rubric_he;
  }
  return base;
}

function randomId() {
  // crypto.randomUUID is available in Node 19+ which Next.js targets.
  return globalThis.crypto?.randomUUID() ?? `q_${Date.now()}_${Math.random().toString(36).slice(2)}`;
}

/**
 * Build a fit-to-purpose AI quiz for one learner. Returns `null` if Groq
 * is unavailable / output couldn't be parsed; the route should turn that
 * into a 503 so the UI can show a retry CTA.
 */
export async function buildCustomQuiz(
  learnerId: string,
  reqIn: CustomQuizRequest,
): Promise<CustomQuizEnvelope | null> {
  const req: CustomQuizRequest = {
    kind_mix: reqIn.kind_mix,
    time_limit_min: Math.max(MIN_TIME, Math.min(MAX_TIME, Math.floor(reqIn.time_limit_min))),
    topics: reqIn.topics,
  };
  const [mastery, profile] = await Promise.all([
    getConceptMastery(learnerId).catch(() => ({} as Record<string, number>)),
    getLearnerProfile(learnerId).catch(() => null),
  ]);
  const picked = pickConcepts(req, mastery, profile);
  const hintsRows = await fetchLessonAgentHintsByConceptIds(picked.ids).catch(() => []);
  const hintsByConcept = new Map(hintsRows.map((r) => [r.concept_id, r.agent_hints]));

  // Derive level key from the learner's goal for depth calibration
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
      // Prefer KG skill_atoms from YAML over lesson agent hints — the YAML is now
      // much richer after the Bagrut-aligned rebuild.
      const kgAtoms = c.skill_atoms ?? [];
      const lessonAtoms = hints?.skill_atoms_unlocked ?? [];
      const mergedAtoms = kgAtoms.length > 0 ? kgAtoms : lessonAtoms;

      // Get level-specific scope note so the AI calibrates explanation depth
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

  const count = questionCountFromBudget(req.time_limit_min, req.kind_mix);
  const allowedKinds = ALLOWED_KINDS_BY_MIX[req.kind_mix];
  const conceptSet = new Set(ctx.map((c) => c.id));

  const groq = await callGroq(SYSTEM_PROMPT, buildUserPrompt(ctx, req.kind_mix, count, profile));
  if (!groq) return null;

  const validated: CustomQuizQuestion[] = [];
  for (const raw of groq.questions) {
    const q = validateQuestion(raw, allowedKinds, conceptSet);
    if (q) {
      q.ord = validated.length + 1;
      validated.push(q);
    }
  }
  if (validated.length === 0) return null;

  return {
    quiz_id: randomId(),
    kind_mix: req.kind_mix,
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
