/**
 * Closed-drill generator for the practice arena (ADR-0013 next steps).
 * Unlike custom quiz (exam/open), this targets fast sealed closed items.
 */
import 'server-only';
import { llmCompleteJson } from '@/lib/llm-provider';
import { fetchLessonAgentHintsByConceptIds } from '@/lib/neon-db';
import {
  buildHintLadder,
  isPracticeClosedKind,
  type PracticeClosedKind,
  type PracticeDifficulty,
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
  count?: number;
}

interface RawDrillQuestion {
  kind?: string;
  difficulty?: string;
  stem_en?: string;
  stem_he?: string;
  options_en?: string[];
  options_he?: string[];
  correct_index?: number;
  correct_answer?: string;
  correct_bool?: boolean;
  acceptable_answers?: string[];
  explanation_en?: string;
  explanation_he?: string;
  skill_atoms?: string[];
}

const SYSTEM = `You generate CLOSED practice drills for an Israeli bilingual (HE+EN) learning site.
Return JSON only: { "questions": [ ... ] }

Rules:
- kinds ONLY: mcq | true_false | numeric | short_answer
- Every question MUST include stem_en + stem_he (Hebrew default quality)
- Math in $...$ / $$...$$ only; never translate math tokens
- No external links, no PII
- Do NOT put the final answer in the stem
- explanations teach the method AFTER solving — they may contain the answer (they are shown only after submit)
- Keep stems under 400 chars
- For mcq: exactly 4 options_en and options_he; correct_index 0-3
- For true_false: correct_bool
- For numeric: correct_answer as a plain number/string (e.g. "1/3" or "0.5")
- For short_answer: correct_answer + optional acceptable_answers[]
- difficulty must match the requested difficulty
- Stay on the given concept_id / skill atoms — no topic drift`;

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
  const kind = typeof raw.kind === 'string' ? raw.kind : '';
  if (!isPracticeClosedKind(kind)) return null;
  const stem_en = typeof raw.stem_en === 'string' ? raw.stem_en.trim() : '';
  const stem_he = typeof raw.stem_he === 'string' ? raw.stem_he.trim() : '';
  if (stem_en.length < 8 || stem_he.length < 8) return null;
  if (stem_en.length > 600 || stem_he.length > 600) return null;

  const labels = {
    en: kgById[conceptId]?.name || conceptId,
    he: kgById[conceptId]?.name_he || kgById[conceptId]?.name || conceptId,
  };
  const skillAtoms =
    Array.isArray(raw.skill_atoms) && raw.skill_atoms.length
      ? raw.skill_atoms.filter((a): a is string => typeof a === 'string').slice(0, 4)
      : atoms.slice(0, 3);

  const explanation_en =
    typeof raw.explanation_en === 'string' ? raw.explanation_en.trim().slice(0, 600) : '';
  const explanation_he =
    typeof raw.explanation_he === 'string' ? raw.explanation_he.trim().slice(0, 600) : '';

  const base = {
    id: newItemId(),
    source: 'generated' as const,
    lesson_id: null,
    question_id: null,
    kind: kind as PracticeClosedKind,
    difficulty,
    concept_id: conceptId,
    skill_atoms: skillAtoms,
    stem_en,
    stem_he,
    explanation_en,
    explanation_he,
    hints: buildHintLadder({
      conceptLabelEn: labels.en,
      conceptLabelHe: labels.he,
      skillAtoms,
    }),
  };

  if (kind === 'mcq') {
    const options_en = Array.isArray(raw.options_en)
      ? raw.options_en.filter((o): o is string => typeof o === 'string').slice(0, 4)
      : [];
    const options_he = Array.isArray(raw.options_he)
      ? raw.options_he.filter((o): o is string => typeof o === 'string').slice(0, 4)
      : [];
    if (options_en.length < 3 || options_he.length < 3) return null;
    const correct_index =
      typeof raw.correct_index === 'number' && Number.isInteger(raw.correct_index)
        ? raw.correct_index
        : -1;
    if (correct_index < 0 || correct_index >= options_en.length) return null;
    return {
      ...base,
      options_en,
      options_he,
      correct_index,
      correct_answer: null,
      answer_payload: null,
    };
  }

  if (kind === 'true_false') {
    if (typeof raw.correct_bool !== 'boolean') return null;
    return {
      ...base,
      options_en: null,
      options_he: null,
      correct_index: null,
      correct_answer: null,
      answer_payload: { correct_bool: raw.correct_bool },
    };
  }

  if (kind === 'numeric') {
    const correct_answer =
      typeof raw.correct_answer === 'string' ? raw.correct_answer.trim() : '';
    if (!correct_answer) return null;
    return {
      ...base,
      options_en: null,
      options_he: null,
      correct_index: null,
      correct_answer,
      answer_payload: null,
    };
  }

  // short_answer / fill_blank
  const correct_answer =
    typeof raw.correct_answer === 'string' ? raw.correct_answer.trim() : '';
  if (!correct_answer) return null;
  const acceptable = Array.isArray(raw.acceptable_answers)
    ? raw.acceptable_answers.filter((a): a is string => typeof a === 'string' && a.trim().length > 0)
    : [];
  return {
    ...base,
    kind: kind === 'fill_blank' ? 'fill_blank' : 'short_answer',
    options_en: null,
    options_he: null,
    correct_index: null,
    correct_answer,
    answer_payload: {
      acceptable_answers: acceptable.length ? acceptable : [correct_answer],
    },
  };
}

/**
 * Generate one sealed closed drill for a concept. Returns null if LLM/validation fails.
 */
export async function buildPracticeDrillItem(
  req: PracticeDrillRequest,
): Promise<PracticeItemSealed | null> {
  const concept = kgById[req.conceptId];
  if (!concept) return null;
  const difficulty: PracticeDifficulty = req.difficulty ?? 'medium';
  const count = Math.min(3, Math.max(1, req.count ?? 1));

  const hintsRows = await fetchLessonAgentHintsByConceptIds([req.conceptId]).catch(() => []);
  const lessonHints = hintsRows[0]?.agent_hints;
  const atoms =
    (concept.skill_atoms?.length ? concept.skill_atoms : null) ??
    lessonHints?.skill_atoms_unlocked ??
    [];

  const userPrompt = [
    `concept_id: ${req.conceptId}`,
    `name_en: ${concept.name}`,
    `name_he: ${concept.name_he ?? concept.name}`,
    `subject: ${concept.subject}`,
    `difficulty: ${difficulty}`,
    `skill_atoms: ${JSON.stringify(atoms.slice(0, 8))}`,
    lessonHints?.key_insights?.length
      ? `key_insights: ${JSON.stringify(lessonHints.key_insights.slice(0, 4))}`
      : null,
    `Generate exactly ${count} closed drill question(s). Prefer variety of kinds.`,
  ]
    .filter(Boolean)
    .join('\n');

  const result = await llmCompleteJson<{ questions?: RawDrillQuestion[] }>({
    system: SYSTEM,
    messages: [{ role: 'user', content: userPrompt }],
    maxTokens: 1800,
    temperature: 0.4,
  });
  if (!result?.json?.questions?.length) return null;

  for (const raw of result.json.questions) {
    const sealed = validateRaw(raw, req.conceptId, difficulty, atoms);
    if (sealed) return sealed;
  }
  return null;
}
