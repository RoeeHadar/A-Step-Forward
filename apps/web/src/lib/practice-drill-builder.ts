/**
 * Open exam-style drill generator for practice arena (ADR-0013 v2).
 */
import 'server-only';
import { llmCompleteJson } from '@/lib/llm-provider';
import {
  fetchLessonAgentHintsByConceptIds,
  fetchLessonByConceptId,
  getLearnerProfile,
} from '@/lib/neon-db';
import {
  buildHintLadder,
  isPracticeArenaKind,
  isPracticeExamWorthyItem,
  practiceItemFingerprint,
  stemLooksLanguageMixed,
  stemLooksVagueOrMeta,
  type PracticeDifficulty,
  type PracticeItemKind,
  type PracticeItemSealed,
} from '@/lib/practice-arena';
import kg from '@/lib/kg-data.json';

type KgConcept = {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  skill_atoms?: string[];
};

const kgById = Object.fromEntries(
  (kg.concepts as KgConcept[]).map((c) => [c.id, c]),
);

export interface PracticeDrillRequest {
  conceptId: string;
  difficulty?: PracticeDifficulty;
  learnerId?: string;
  count?: number;
}

interface RawDrillQuestion {
  kind?: string;
  difficulty?: string;
  stem_en?: string;
  stem_he?: string;
  correct_answer?: string;
  acceptable_answers?: string[];
  explanation_en?: string;
  explanation_he?: string;
  rubric_en?: string;
  rubric_he?: string;
  model_answer_en?: string;
  model_answer_he?: string;
  skill_atoms?: string[];
  points_available?: number;
}

const SYSTEM = `You generate OPEN exam-style practice questions for an Israeli bilingual (HE+EN) learning site (Bagrut / university register).
Return JSON only: { "questions": [ ... ] }

Rules:
- kinds PREFERRED: open (multi-step worked solution). Allowed rare: numeric | short_answer
- NEVER generate mcq or true_false
- Every question MUST include stem_en + stem_he
- Each stem must be ONE language only (EN stem has no Hebrew letters; HE stem has no English prose words). Math tokens stay in $...$ / $$...$$
- Math in $...$ / $$...$$ only; never translate math tokens; no Hebrew inside math
- No external links, no PII
- Do NOT put the final answer in the stem
- open items: include rubric_en, rubric_he, model_answer_en, model_answer_he, explanation_en, explanation_he
- Model answers must be a REAL worked solution for THAT stem (numbers, algebra steps) — never meta instructions like "identify which facet applies"
- Stems must look like a real bagrut/university exam item — not lesson pedagogy
- Keep stems under 900 chars
- difficulty must match the requested difficulty
- Stay on the given concept_id — no topic drift

FORBIDDEN stems (instant reject):
- "Apply the lesson facets…" / "יישמו את פני השיעור…"
- "Numeric-first check for this lesson…" / "בדיקה מספרית-תחילה…"
- "give a short worked example" without a concrete problem
- Any prompt that refers to "the lesson", "facets", or skill-atom English ids

Clarity (mandatory):
- Concrete data IN the stem (specific $f$, numbers, lengths, voltages, etc.)
- Clear task verb: compute / prove / find all / show that / explain with calculation
- Multipart OK: (א)/(ב) or (a)/(b)`;


function newItemId(): string {
  return (
    globalThis.crypto?.randomUUID() ||
    `prdrill_${Date.now()}_${Math.random().toString(36).slice(2)}`
  );
}

function validateRaw(
  raw: RawDrillQuestion,
  conceptId: string,
  difficulty: PracticeDifficulty,
  atoms: string[],
): PracticeItemSealed | null {
  if (!raw || typeof raw !== 'object') return null;
  let kind = typeof raw.kind === 'string' ? raw.kind : 'open';
  if (kind === 'mcq' || kind === 'true_false' || kind === 'fill_blank') return null;
  if (!isPracticeArenaKind(kind)) kind = 'open';
  if (kind !== 'open' && kind !== 'numeric' && kind !== 'short_answer') return null;

  const stem_en = typeof raw.stem_en === 'string' ? raw.stem_en.trim() : '';
  const stem_he = typeof raw.stem_he === 'string' ? raw.stem_he.trim() : '';
  if (stem_en.length < 12 || stem_he.length < 12) return null;
  if (stem_en.length > 1200 || stem_he.length > 1200) return null;
  if (stemLooksLanguageMixed(stem_en) || stemLooksLanguageMixed(stem_he)) return null;
  if (stemLooksVagueOrMeta(stem_en) || stemLooksVagueOrMeta(stem_he)) return null;

  const explanation_en =
    typeof raw.explanation_en === 'string' ? raw.explanation_en.trim().slice(0, 1200) : '';
  const explanation_he =
    typeof raw.explanation_he === 'string' ? raw.explanation_he.trim().slice(0, 1200) : '';
  const model_answer_en =
    typeof raw.model_answer_en === 'string'
      ? raw.model_answer_en.trim().slice(0, 1200)
      : explanation_en;
  const model_answer_he =
    typeof raw.model_answer_he === 'string'
      ? raw.model_answer_he.trim().slice(0, 1200)
      : explanation_he;

  if (
    !isPracticeExamWorthyItem({
      stemEn: stem_en,
      stemHe: stem_he,
      explanationEn: explanation_en || model_answer_en,
      explanationHe: explanation_he || model_answer_he,
    })
  ) {
    return null;
  }
  if (stemLooksVagueOrMeta(model_answer_en) || stemLooksVagueOrMeta(model_answer_he)) {
    return null;
  }

  const labels = {
    en: kgById[conceptId]?.name || conceptId,
    he: kgById[conceptId]?.name_he || kgById[conceptId]?.name || conceptId,
  };
  const skillAtoms =
    Array.isArray(raw.skill_atoms) && raw.skill_atoms.length
      ? raw.skill_atoms.filter((a): a is string => typeof a === 'string').slice(0, 4)
      : atoms.slice(0, 3);

  const rubric_en =
    typeof raw.rubric_en === 'string' ? raw.rubric_en.trim().slice(0, 800) : explanation_en;
  const rubric_he =
    typeof raw.rubric_he === 'string' ? raw.rubric_he.trim().slice(0, 800) : explanation_he;

  const fingerprint = practiceItemFingerprint({
    conceptId,
    stemEn: stem_en,
    stemHe: stem_he,
  });

  const base = {
    id: newItemId(),
    source: 'generated' as const,
    lesson_id: null,
    question_id: null,
    fingerprint,
    kind: kind as PracticeItemKind,
    difficulty,
    concept_id: conceptId,
    skill_atoms: skillAtoms,
    stem_en,
    stem_he,
    explanation_en: explanation_en || model_answer_en,
    explanation_he: explanation_he || model_answer_he,
    rubric_en,
    rubric_he,
    model_answer_en,
    model_answer_he,
    points_available: kind === 'open' ? 20 : 5,
    hints: buildHintLadder({
      conceptLabelEn: labels.en,
      conceptLabelHe: labels.he,
      skillAtoms,
    }),
    options_en: null,
    options_he: null,
    correct_index: null,
  };

  if (kind === 'open') {
    if (!model_answer_en && !model_answer_he) return null;
    return {
      ...base,
      correct_answer: null,
      answer_payload: null,
    };
  }

  const correct_answer =
    typeof raw.correct_answer === 'string' ? raw.correct_answer.trim() : '';
  if (!correct_answer) return null;
  const acceptable = Array.isArray(raw.acceptable_answers)
    ? raw.acceptable_answers.filter(
        (a): a is string => typeof a === 'string' && a.trim().length > 0,
      )
    : [];
  return {
    ...base,
    correct_answer,
    answer_payload:
      kind === 'short_answer'
        ? { acceptable_answers: acceptable.length ? acceptable : [correct_answer] }
        : null,
  };
}

/**
 * Generate one sealed open exam-style drill. Returns null if LLM/validation fails.
 */
export async function buildPracticeDrillItem(
  req: PracticeDrillRequest,
): Promise<PracticeItemSealed | null> {
  const concept = kgById[req.conceptId];
  if (!concept) return null;
  const difficulty: PracticeDifficulty = req.difficulty ?? 'medium';
  const count = Math.min(2, Math.max(1, req.count ?? 1));

  const [hintsRows, profile, lesson] = await Promise.all([
    fetchLessonAgentHintsByConceptIds([req.conceptId]).catch(() => []),
    req.learnerId
      ? getLearnerProfile(req.learnerId).catch(() => null)
      : Promise.resolve(null),
    fetchLessonByConceptId(req.conceptId).catch(() => null),
  ]);
  const lessonHints = hintsRows[0]?.agent_hints;
  const atoms =
    (concept.skill_atoms?.length ? concept.skill_atoms : null) ??
    lessonHints?.skill_atoms_unlocked ??
    [];
  const goal =
    (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ??
    profile?.goal ??
    'bagrut_math_5';

  const exemplars = (lesson?.questions ?? [])
    .filter((q) =>
      isPracticeExamWorthyItem({
        stemEn: q.stem_en ?? '',
        stemHe: q.stem_he ?? '',
        explanationEn: q.explanation_en,
        explanationHe: q.explanation_he,
        questionId: q.id,
      }),
    )
    .slice(0, 2)
    .map((q) => ({
      stem_he: (q.stem_he ?? '').slice(0, 280),
      stem_en: (q.stem_en ?? '').slice(0, 280),
    }));

  const userPrompt = [
    `concept_id: ${req.conceptId}`,
    `name_en: ${concept.name}`,
    `name_he: ${concept.name_he ?? concept.name}`,
    `subject: ${concept.subject}`,
    `learner_goal_register: ${goal}`,
    `difficulty: ${difficulty}`,
    `skill_atoms: ${JSON.stringify(atoms.slice(0, 8))}`,
    lessonHints?.key_insights?.length
      ? `key_insights: ${JSON.stringify(lessonHints.key_insights.slice(0, 4))}`
      : null,
    exemplars.length
      ? `Style exemplars from the same lesson bank (imitate concreteness, do NOT copy):\n${JSON.stringify(exemplars)}`
      : null,
    `Generate exactly ${count} OPEN bagrut/uni exam-style question(s). Prefer kind "open".`,
    `Each stem must be self-contained with concrete data. Model answer = full worked solution for that stem.`,
  ]
    .filter(Boolean)
    .join('\n');

  const result = await llmCompleteJson<{ questions?: RawDrillQuestion[] }>({
    system: SYSTEM,
    messages: [{ role: 'user', content: userPrompt }],
    maxTokens: 2800,
    temperature: 0.4,
  });
  if (!result?.json?.questions?.length) return null;

  for (const raw of result.json.questions) {
    const sealed = validateRaw(raw, req.conceptId, difficulty, atoms);
    if (sealed) return sealed;
  }
  return null;
}
