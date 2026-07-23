/**
 * Pure helpers for the intensive practice arena (ADR-0013).
 * No Neon — safe for unit tests.
 */

export const PRACTICE_CLOSED_KINDS = [
  'mcq',
  'true_false',
  'numeric',
  'short_answer',
  'fill_blank',
] as const;

export type PracticeClosedKind = (typeof PRACTICE_CLOSED_KINDS)[number];

export type PracticeDifficulty = 'easy' | 'medium' | 'hard';

export type PracticeQueueMode = 'default' | 'due' | 'explore';

export function parsePracticeQueueMode(v: unknown): PracticeQueueMode {
  if (v === 'due' || v === 'explore') return v;
  return 'default';
}

/** Pure explore picker: weakest mastery outside the active week, else any candidate outside. */
export function pickExploreFocusConceptId(opts: {
  masteryMap: Record<string, number>;
  activeConceptIds: string[];
  candidateConceptIds: string[];
}): string | null {
  const active = new Set(opts.activeConceptIds);
  const candidates = new Set(opts.candidateConceptIds);
  const weakOutside = Object.entries(opts.masteryMap)
    .filter(
      ([id, s]) =>
        typeof s === 'number' && !active.has(id) && candidates.has(id),
    )
    .sort((a, b) => a[1] - b[1]);
  if (weakOutside[0]) return weakOutside[0][0];
  return opts.candidateConceptIds.find((id) => !active.has(id)) ?? null;
}

export interface PracticeHintStep {
  en: string;
  he: string;
}

/** Full sealed item — never send to the client as-is. */
export interface PracticeItemSealed {
  id: string;
  source: 'authored' | 'generated';
  lesson_id?: string | null;
  question_id?: string | null;
  kind: PracticeClosedKind;
  difficulty: PracticeDifficulty;
  concept_id: string;
  skill_atoms: string[];
  stem_en: string;
  stem_he: string;
  options_en?: string[] | null;
  options_he?: string[] | null;
  correct_index?: number | null;
  correct_answer?: string | null;
  answer_payload?: {
    correct_bool?: boolean;
    acceptable_answers?: string[];
    case_sensitive?: boolean;
  } | null;
  explanation_en: string;
  explanation_he: string;
  hints: [PracticeHintStep, PracticeHintStep, PracticeHintStep];
}

/** Client-facing item (keys + unused hints stripped). */
export interface PracticeItemPublic {
  id: string;
  source: 'authored' | 'generated';
  kind: PracticeClosedKind;
  difficulty: PracticeDifficulty;
  concept_id: string;
  skill_atoms: string[];
  stem_en: string;
  stem_he: string;
  options_en?: string[] | null;
  options_he?: string[] | null;
  hint_step: number;
  unlocked_hints: PracticeHintStep[];
}

export interface PracticeSessionPublic {
  session_id: string;
  goal_items: number;
  goal_minutes: number;
  attempted: number;
  correct_count: number;
  hints_used: number;
  concept_filter: string | null;
  focus_concept_id: string | null;
  item: PracticeItemPublic | null;
  /** True after submit/give-up until the client advances via /next. */
  item_graded: boolean;
  queue_mode?: PracticeQueueMode;
  status: 'active' | 'ended';
}

/** Sent from /app/practice Coach panel → /api/chat (ADR-0013). */
export interface PracticeChatContext {
  session_id: string;
  item_id: string;
  concept_id: string;
  kind: string;
  difficulty: string;
  hint_step: number;
  stem_en: string;
  stem_he: string;
  item_graded: boolean;
}

export function parsePracticeChatContext(raw: unknown): PracticeChatContext | null {
  if (!raw || typeof raw !== 'object') return null;
  const o = raw as Record<string, unknown>;
  const session_id = typeof o.session_id === 'string' ? o.session_id.trim() : '';
  const item_id = typeof o.item_id === 'string' ? o.item_id.trim() : '';
  const concept_id = typeof o.concept_id === 'string' ? o.concept_id.trim() : '';
  const stem_en = typeof o.stem_en === 'string' ? o.stem_en : '';
  const stem_he = typeof o.stem_he === 'string' ? o.stem_he : '';
  if (!session_id || !item_id || !concept_id || (!stem_en && !stem_he)) return null;
  return {
    session_id,
    item_id,
    concept_id,
    kind: typeof o.kind === 'string' ? o.kind : 'unknown',
    difficulty: typeof o.difficulty === 'string' ? o.difficulty : 'medium',
    hint_step:
      typeof o.hint_step === 'number' && Number.isFinite(o.hint_step)
        ? Math.max(0, Math.min(3, Math.floor(o.hint_step)))
        : 0,
    stem_en,
    stem_he,
    item_graded: o.item_graded === true,
  };
}

export function formatPracticeArenaChatBlock(ctx: PracticeChatContext): string {
  return [
    '## PRACTICE ARENA context (ADR-0013 — mandatory)',
    `session_id=${ctx.session_id}; item_id=${ctx.item_id}; concept=${ctx.concept_id}; kind=${ctx.kind}; difficulty=${ctx.difficulty}; hint_step=${ctx.hint_step}; graded=${ctx.item_graded}`,
    `Stem (EN): ${ctx.stem_en.slice(0, 400)}`,
    `Stem (HE): ${ctx.stem_he.slice(0, 400)}`,
    '',
    '### THIS TURN — practice help contract',
    '- The learner is mid-arena on the stem above. Help with the 3-step ladder only: concept → strategy → setup scaffold.',
    '- NEVER reveal the final numeric/MCQ/true-false answer or a full worked solution unless graded=true (already submitted/gave up).',
    '- Ask clarifying questions; point back to the stem. Prefer sending them to use the arena Hint button for ladder unlocks.',
    '- Do not invent a replacement exercise; stay on this item.',
  ].join('\n');
}

export function isPracticeClosedKind(kind: string): kind is PracticeClosedKind {
  return (PRACTICE_CLOSED_KINDS as readonly string[]).includes(kind);
}

export function stripPracticeItemForClient(
  item: PracticeItemSealed,
  hintStep: number,
): PracticeItemPublic {
  const step = Math.max(0, Math.min(3, Math.floor(hintStep)));
  return {
    id: item.id,
    source: item.source,
    kind: item.kind,
    difficulty: item.difficulty,
    concept_id: item.concept_id,
    skill_atoms: item.skill_atoms,
    stem_en: item.stem_en,
    stem_he: item.stem_he,
    options_en: item.options_en ?? null,
    options_he: item.options_he ?? null,
    hint_step: step,
    unlocked_hints: item.hints.slice(0, step),
  };
}

export function buildHintLadder(opts: {
  conceptLabelEn: string;
  conceptLabelHe: string;
  skillAtoms: string[];
  /** Intentionally unused — authored explanations often contain the answer. */
  explanationEn?: string | null;
  explanationHe?: string | null;
}): [PracticeHintStep, PracticeHintStep, PracticeHintStep] {
  const atom = opts.skillAtoms[0];
  const conceptEn = opts.conceptLabelEn || 'this topic';
  const conceptHe = opts.conceptLabelHe || 'הנושא הזה';
  // Never paraphrase explanations into hints — they frequently open with the keyed result.
  void opts.explanationEn;
  void opts.explanationHe;

  return [
    {
      en: `This targets ${conceptEn}${atom ? ` — skill: ${atom}` : ''}.`,
      he: `השאלה על ${conceptHe}${atom ? ` — מיומנות: ${atom}` : ''}.`,
    },
    {
      en: `Recall the core definition or rule for ${conceptEn}, then decide which form applies here.`,
      he: `הזכר את ההגדרה או הכלל המרכזי של ${conceptHe}, ואז בחר איזו צורה מתאימה כאן.`,
    },
    {
      en: `Set up the work: write the formula / first step for ${conceptEn}, but do not evaluate the final answer yet.`,
      he: `כתוב את הנוסחה / הצעד הראשון עבור ${conceptHe} — בלי לחשב את התשובה הסופית עדיין.`,
    },
  ];
}

export function nextDifficulty(
  recentCorrect: boolean[],
  current: PracticeDifficulty = 'medium',
): PracticeDifficulty {
  const last3 = recentCorrect.slice(-3);
  if (last3.length >= 2 && last3.every(Boolean)) {
    return current === 'easy' ? 'medium' : 'hard';
  }
  if (last3.length >= 2 && last3.every((c) => !c)) {
    return current === 'hard' ? 'medium' : 'easy';
  }
  return current;
}

export function practiceXpSourceId(sessionId: string, itemId: string): string {
  return `practice:${sessionId}:${itemId}`;
}

/** Soft defaults from ADR grilling. */
export const PRACTICE_DEFAULT_GOAL_ITEMS = 10;
export const PRACTICE_DEFAULT_GOAL_MINUTES = 15;
export const PRACTICE_MAX_GENERATED_PER_SESSION = 6;

/**
 * Grade a sealed practice item server-side (closed kinds only).
 */
export function gradePracticeItem(
  item: PracticeItemSealed,
  userAnswer: unknown,
): { correct: boolean; reason?: string } {
  switch (item.kind) {
    case 'mcq': {
      const expected = item.correct_index;
      const picked =
        typeof userAnswer === 'number'
          ? userAnswer
          : typeof userAnswer === 'string' && /^\d+$/.test(userAnswer)
            ? Number(userAnswer)
            : null;
      if (picked == null || expected == null) {
        return { correct: false, reason: 'invalid answer' };
      }
      return { correct: picked === expected };
    }
    case 'true_false': {
      const expected = item.answer_payload?.correct_bool;
      const picked =
        typeof userAnswer === 'boolean'
          ? userAnswer
          : userAnswer === 'true' || userAnswer === 'yes' || userAnswer === 'נכון'
            ? true
            : userAnswer === 'false' || userAnswer === 'no' || userAnswer === 'לא נכון'
              ? false
              : null;
      if (picked == null || expected == null) {
        return { correct: false, reason: 'invalid answer' };
      }
      return { correct: picked === expected };
    }
    case 'numeric': {
      if (typeof userAnswer !== 'string' || !item.correct_answer) {
        return { correct: false, reason: 'invalid answer' };
      }
      const a = Number(String(userAnswer).replace(/,/g, '').trim());
      const b = Number(String(item.correct_answer).replace(/,/g, '').trim());
      if (!Number.isFinite(a) || !Number.isFinite(b)) {
        return {
          correct:
            String(userAnswer).trim().toLowerCase() ===
            String(item.correct_answer).trim().toLowerCase(),
        };
      }
      return { correct: Math.abs(a - b) <= Math.max(1e-6, Math.abs(b) * 1e-4) };
    }
    case 'short_answer':
    case 'fill_blank': {
      if (typeof userAnswer !== 'string') {
        return { correct: false, reason: 'invalid answer' };
      }
      const accepted = [
        ...(item.answer_payload?.acceptable_answers ?? []),
        ...(item.correct_answer ? [item.correct_answer] : []),
      ]
        .map((s) => s.trim())
        .filter(Boolean);
      if (!accepted.length) return { correct: false, reason: 'no key' };
      const cs = item.answer_payload?.case_sensitive ?? false;
      const norm = (s: string) => (cs ? s.trim() : s.trim().toLowerCase());
      const u = norm(userAnswer);
      return { correct: accepted.some((a) => norm(a) === u) };
    }
    default:
      return { correct: false, reason: 'unsupported kind' };
  }
}
