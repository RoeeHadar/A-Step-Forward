/**
 * Pure helpers for the intensive practice arena (ADR-0013 v2).
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

/** Preferred arena kinds — open-first; closed only as rare exam-faithful exceptions. */
export const PRACTICE_ARENA_KINDS = [
  'open',
  'numeric',
  'short_answer',
  'mcq',
  'true_false',
  'fill_blank',
] as const;

export type PracticeItemKind = (typeof PRACTICE_ARENA_KINDS)[number];

export type PracticeDifficulty = 'easy' | 'medium' | 'hard';

export type PracticeQueueMode = 'default' | 'due' | 'explore';

/** Process score at or above this counts as success for adaptation / XP. */
export const PRACTICE_SUCCESS_PROCESS_SCORE = 0.6;

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
  /** Durable de-dupe key (authored id or fingerprint). */
  fingerprint: string;
  kind: PracticeItemKind;
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
  /** Rubric / model answer for open grading (sealed until after grade). */
  rubric_en?: string | null;
  rubric_he?: string | null;
  model_answer_en?: string | null;
  model_answer_he?: string | null;
  explanation_en: string;
  explanation_he: string;
  points_available?: number;
  hints: [PracticeHintStep, PracticeHintStep, PracticeHintStep];
}

/** Client-facing item (keys + unused hints stripped). */
export interface PracticeItemPublic {
  id: string;
  source: 'authored' | 'generated';
  kind: PracticeItemKind;
  difficulty: PracticeDifficulty;
  concept_id: string;
  skill_atoms: string[];
  stem_en: string;
  stem_he: string;
  options_en?: string[] | null;
  options_he?: string[] | null;
  points_available?: number;
  hint_step: number;
  unlocked_hints: PracticeHintStep[];
}

export interface PracticeAttemptLogEntry {
  item_id: string;
  concept_id: string;
  kind: string;
  difficulty: string;
  correct: boolean;
  process_score: number | null;
  gave_up: boolean;
  stem_en: string;
  stem_he: string;
}

export interface PracticeSessionSummary {
  topic_ids: string[];
  attempted: number;
  correct_count: number;
  hints_used: number;
  avg_process_score: number | null;
  difficulty_end: PracticeDifficulty | null;
  weak_concepts: string[];
  attempts: PracticeAttemptLogEntry[];
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
  topic_ids: string[];
  item: PracticeItemPublic | null;
  /** True after submit/give-up until the client advances via /next. */
  item_graded: boolean;
  queue_mode?: PracticeQueueMode;
  status: 'active' | 'ended';
  summary?: PracticeSessionSummary | null;
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

export function isPracticeArenaKind(kind: string): kind is PracticeItemKind {
  return (PRACTICE_ARENA_KINDS as readonly string[]).includes(kind);
}

export function isPracticeOpenKind(kind: string): boolean {
  return kind === 'open';
}

export function normalizeStemForFingerprint(s: string): string {
  return s
    .toLowerCase()
    .replace(/\$+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 600);
}

/** Stable content fingerprint for generated (and authored fallback) de-dupe. */
export function practiceItemFingerprint(opts: {
  conceptId: string;
  stemEn: string;
  stemHe: string;
  questionId?: string | null;
}): string {
  if (opts.questionId && opts.questionId.trim()) {
    return `q:${opts.questionId.trim()}`;
  }
  const raw = [
    opts.conceptId,
    normalizeStemForFingerprint(opts.stemEn),
    normalizeStemForFingerprint(opts.stemHe),
  ].join('|');
  let h = 2166136261;
  for (let i = 0; i < raw.length; i++) {
    h ^= raw.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return `fp:${(h >>> 0).toString(16)}`;
}

export function practiceSuccessFromProcess(score: number | null | undefined): boolean {
  if (typeof score !== 'number' || !Number.isFinite(score)) return false;
  return score >= PRACTICE_SUCCESS_PROCESS_SCORE;
}

export function buildPracticeSessionSummary(opts: {
  topicIds: string[];
  attempted: number;
  correctCount: number;
  hintsUsed: number;
  attempts: PracticeAttemptLogEntry[];
  difficultyEnd?: PracticeDifficulty | null;
}): PracticeSessionSummary {
  const scores = opts.attempts
    .map((a) => a.process_score)
    .filter((s): s is number => typeof s === 'number' && Number.isFinite(s));
  const avg =
    scores.length > 0
      ? scores.reduce((a, b) => a + b, 0) / scores.length
      : null;
  const failByConcept = new Map<string, number>();
  for (const a of opts.attempts) {
    if (!a.correct) {
      failByConcept.set(a.concept_id, (failByConcept.get(a.concept_id) ?? 0) + 1);
    }
  }
  const weak_concepts = [...failByConcept.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([id]) => id);

  return {
    topic_ids: opts.topicIds,
    attempted: opts.attempted,
    correct_count: opts.correctCount,
    hints_used: opts.hintsUsed,
    avg_process_score: avg,
    difficulty_end: opts.difficultyEnd ?? null,
    weak_concepts,
    attempts: opts.attempts,
  };
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
    points_available: item.points_available ?? (item.kind === 'open' ? 20 : 5),
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
export const PRACTICE_MAX_GENERATED_PER_SESSION = 8;

/**
 * Grade a sealed practice item server-side (closed kinds only).
 * Open kinds must use process grading.
 */
export function gradePracticeItem(
  item: PracticeItemSealed,
  userAnswer: unknown,
): { correct: boolean; reason?: string } {
  if (item.kind === 'open') {
    return { correct: false, reason: 'open_requires_process_grade' };
  }
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

/** Reject stems that mix Hebrew letters with English prose outside math. Simple heuristic. */
export function stemLooksLanguageMixed(stem: string): boolean {
  const withoutMath = stem.replace(/\$\$[\s\S]*?\$\$/g, ' ').replace(/\$[^$]+\$/g, ' ');
  const hasHe = /[\u0590-\u05FF]/.test(withoutMath);
  const hasEnWord = /[A-Za-z]{3,}/.test(withoutMath);
  return hasHe && hasEnWord;
}

export function stemLooksVagueOrMeta(stem: string): boolean {
  const s = stem.replace(/\s+/g, ' ').trim();
  const lower = s.toLowerCase();
  const patterns: RegExp[] = [
    /if (given|provided|shown) in (the )?lesson/i,
    /from the (graph|formula) if /i,
    /from (this )?the lesson/i,
    /from (this )?lesson/i,
    /או מנוסחה מפורשת אם ניתנה/,
    /אם ניתנ[הה] בשיעור/,
    /מהגרף של\s*\$?y\s*=\s*f\s*\(\s*x\s*\)/i,
    /\(או מנוסחה/,
    /as (the|a) horizontal line .{0,40}moves/i,
    /כשהישר האופקי .{0,40}זז/,
    /how many solutions can .{0,80}have/i,
    /כמה פתרונות יכולה להיות/,
    // Lesson pedagogy / expansion templates — not exam items
    /יישמו את פני השיעור/,
    /apply the lesson facets?/i,
    /תרגול פנים/,
    /בדיקה מספרית-תחילה/,
    /numeric-first check/i,
    /give a short worked example/i,
    /תנו דוגמה פתורה קצרה/,
    /core skill from/i,
    /מיומנות (השיעור|המרכזית)/,
    /ראו את סעיף הפנים/,
    /see the facets? section/i,
    /תרגיל מסלול/,
    /route drill/i,
    /מהשיעור/,
    /לשיעור זה/,
    /פריט מהשיעור/,
    /פריט (סטנדרטי |מרכזי )?מהשיעור/,
    /יישמו את הרגל/,
    /apply the (habit|habits)/i,
    /תארו והציבו/,
    /תאר והצב/,
    /describe and (plug|substitute|evaluate)/i,
    /סקצו או תארו/,
    /sketch or describe/i,
    /בנקודת ציון/,
    /landmark point/i,
    /שרשרת הצדקה/,
    /תרגיל פרמטר:\s*הכניסו פרמטר/,
    /\b[a-z]{3,}(?:_[a-z0-9]+){1,}\b/, // skill-atom / habit ids like free_body_diagram
  ];
  return patterns.some((re) => re.test(s) || re.test(lower));
}

/** Auto-authored filler ids from lesson expansion (not bagrut/uni exam items). */
export function practiceQuestionIdLooksBoilerplate(questionId: string | null | undefined): boolean {
  if (!questionId) return false;
  return /-(facet-auto|facet|algebra-depth|depth-auto|numeric-first|moe-remainder|[a-z0-9-]*depth)(-|$)/i.test(
    questionId,
  );
}

/** Exam stems must ask a clear computable/provable task — not “describe and plug”. */
export function stemHasClearExamTask(stem: string): boolean {
  const s = stem.replace(/\s+/g, ' ').trim();
  if (s.length < 24) return false;
  // Clear bagrut/uni task verbs (HE + EN)
  return /(מצא[ווי]?|חשב[ווי]?|הוכ[חי]|הראה[ווי]?|הצג[ווי]?|פתחו|פתרו|פתור|פתח|כמה|מהו|מהי|מהם|למה|הסבירו|הסבר|find|compute|calculate|evaluate|prove|show that|\bshow\b|solve|determine|obtain|derive|simplify|expand|factor)/i.test(
    s,
  );
}

/**
 * True when stem (+ optional explanation / id) is suitable for the practice arena:
 * concrete exam-style prompt, not lesson-meta pedagogy.
 */
export function isPracticeExamWorthyItem(opts: {
  stemEn: string;
  stemHe: string;
  explanationEn?: string | null;
  explanationHe?: string | null;
  questionId?: string | null;
}): boolean {
  if (practiceQuestionIdLooksBoilerplate(opts.questionId)) return false;
  const stemEn = opts.stemEn.trim();
  const stemHe = opts.stemHe.trim();
  if (stemEn.length < 24 || stemHe.length < 24) return false;
  if (stemLooksLanguageMixed(stemEn) || stemLooksLanguageMixed(stemHe)) return false;
  if (stemLooksVagueOrMeta(stemEn) || stemLooksVagueOrMeta(stemHe)) return false;
  if (!stemHasClearExamTask(stemHe) && !stemHasClearExamTask(stemEn)) return false;
  const explEn = (opts.explanationEn ?? '').trim();
  const explHe = (opts.explanationHe ?? '').trim();
  if (explEn && stemLooksVagueOrMeta(explEn)) return false;
  if (explHe && stemLooksVagueOrMeta(explHe)) return false;
  // Require concrete math (or a long clearly numeric word problem)
  const heHasMath = /\$/.test(stemHe);
  const enHasMath = /\$/.test(stemEn);
  if (!heHasMath && !enHasMath) return false;
  // Reject ultra-short "plug in" shells even if they contain $
  if (stemHe.length < 40 && /הצב|הציבו|plug|substitute/i.test(stemHe + stemEn)) return false;
  return true;
}

/** Rank authored candidates — higher = more exam-like. */
export function practiceExamWorthinessScore(stem: string, kind: string): number {
  let score = 0;
  if (/\$/.test(stem)) score += 4;
  if (stem.length >= 80) score += 2;
  if (stem.length >= 140) score += 1;
  if (kind === 'open' || kind === 'derivation') score += 2;
  if (kind === 'numeric' || kind === 'short_answer') score += 1;
  if (/\(א\)|\(ב\)|\(a\)|\(b\)/i.test(stem)) score += 1;
  if (stemHasClearExamTask(stem)) score += 2;
  if (/תרגיל מסלול|מהשיעור|תארו והציבו/i.test(stem)) score -= 10;
  return score;
}
