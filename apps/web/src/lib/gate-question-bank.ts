/**
 * Weekly-gate item selection from the authored lesson question bank.
 *
 * ADR-0010: gates must assess real understanding at goal level — not LLM-invented
 * easy MCQs. Prefer hard/medium open, numeric, short_answer, derivation from
 * `lessons-bundle.generated.json` / Neon `lesson_questions`.
 */
import { createHash } from 'node:crypto';
import { getBundledLesson } from '@/lib/lesson-bundle';
import { resolveConceptAlias } from '@/lib/concept-aliases';
import { resolveCorrectBool } from '@/lib/answer-normalize';
import type { LessonQuestionRow, LessonPointsLevel } from '@/lib/neon-db';

/** v3: exam-style multipart corpus preferred; v2 lesson-bank hard items still accepted. */
export const GATE_BANK_FORMAT_VERSION = 3 as const;

/** Kinds the week-gate UI + grader support today. */
export type GateQuestionKind =
  | 'mcq'
  | 'true_false'
  | 'numeric'
  | 'short_answer'
  | 'open'
  | 'derivation';

const SUPPORTED: ReadonlySet<string> = new Set<GateQuestionKind>([
  'mcq',
  'true_false',
  'numeric',
  'short_answer',
  'open',
  'derivation',
]);

/** Prefer kinds that force production / reasoning over recognition. */
const KIND_PRIORITY: Record<GateQuestionKind, number> = {
  open: 6,
  derivation: 6,
  numeric: 5,
  short_answer: 5,
  mcq: 2,
  true_false: 1,
};

const DIFF_PRIORITY: Record<string, number> = {
  hard: 3,
  medium: 2,
  easy: 1,
};

const MCQ_LETTERS = ['A', 'B', 'C', 'D'] as const;

export interface GateBankPick {
  /** Stable id for this gate item (hash of source + rotation). */
  id: string;
  topic: string;
  subject: string;
  kind: GateQuestionKind;
  difficulty: number;
  stem: string;
  options: { key: string; text: string }[];
  /** MCQ / true_false letter key. */
  correct?: string;
  correct_answer?: string | null;
  acceptable_answers?: string[];
  rubric?: string | null;
  model_answer?: string | null;
  source_question_id: string;
  source: 'lesson_bank';
  format_version: typeof GATE_BANK_FORMAT_VERSION;
}

export interface PickGateQuestionsInput {
  conceptIds: string[];
  locale: 'he' | 'en';
  count: number;
  /** Gate retake index — rotates which bank items are chosen. */
  rotation?: number;
  /** Optional Bagrut floor; questions below this level are skipped when set. */
  pointsLevelMin?: LessonPointsLevel | null;
  /** Prefer harder items (default true for weekly gates). */
  preferHard?: boolean;
}

function difficultyToFloat(d: LessonQuestionRow['difficulty'] | number | string): number {
  if (typeof d === 'number' && Number.isFinite(d)) {
    if (d <= 1) return Math.max(0, Math.min(1, d));
    return Math.max(0, Math.min(1, d / 5));
  }
  const key = String(d ?? 'medium').toLowerCase();
  if (key === 'hard' || key === 'very_hard') return 0.9;
  if (key === 'easy') return 0.35;
  return 0.6;
}

function levelRank(level: LessonPointsLevel | null | undefined): number {
  if (!level) return 0;
  const map: Record<string, number> = {
    '3pt': 3,
    '4pt': 4,
    '5pt': 5,
    hs_physics: 5,
    calc1: 6,
    la: 6,
  };
  return map[level] ?? 0;
}

function allowedForPoints(
  q: LessonQuestionRow,
  min: LessonPointsLevel | null | undefined,
): boolean {
  if (!min) return true;
  const qMin = q.points_level_min ?? null;
  if (!qMin) return true;
  return levelRank(qMin) <= levelRank(min);
}

function stableId(sourceId: string, topic: string, rotation: number): string {
  const hash = createHash('sha256')
    .update(`gate:${topic}:${sourceId}:r${rotation}`)
    .digest('hex');
  return `${hash.slice(0, 8)}-${hash.slice(8, 12)}-4${hash.slice(13, 16)}-8${hash.slice(17, 20)}-${hash.slice(20, 32)}`;
}

function seededShuffle<T>(items: T[], seed: string): T[] {
  const out = [...items];
  let h = createHash('sha256').update(seed).digest();
  for (let i = out.length - 1; i > 0; i -= 1) {
    const byte = h[i % h.length] ?? 0;
    const j = byte % (i + 1);
    [out[i], out[j]] = [out[j]!, out[i]!];
    if (i % 16 === 0) {
      h = createHash('sha256').update(h).digest();
    }
  }
  return out;
}

function toGatePick(
  conceptId: string,
  subject: string,
  q: LessonQuestionRow,
  locale: 'he' | 'en',
  rotation: number,
): GateBankPick | null {
  if (!SUPPORTED.has(q.kind)) return null;
  const kind = q.kind as GateQuestionKind;
  const stem =
    (locale === 'he' ? q.stem_he || q.stem_en : q.stem_en || q.stem_he)?.trim() ?? '';
  if (!stem || stem.length < 8) return null;

  const rubric =
    (locale === 'he' ? q.rubric_he || q.rubric_en : q.rubric_en || q.rubric_he) ?? null;
  const model =
    (locale === 'he' ? q.explanation_he || q.explanation_en : q.explanation_en || q.explanation_he) ??
    null;

  const base: GateBankPick = {
    id: stableId(q.id, conceptId, rotation),
    topic: conceptId,
    subject,
    kind,
    difficulty: difficultyToFloat(q.difficulty),
    stem: stem.slice(0, 1200),
    options: [],
    correct_answer: q.correct_answer,
    acceptable_answers: q.answer_payload?.acceptable_answers ?? undefined,
    rubric,
    model_answer: model,
    source_question_id: q.id,
    source: 'lesson_bank',
    format_version: GATE_BANK_FORMAT_VERSION,
  };

  if (kind === 'mcq') {
    const optsRaw =
      locale === 'he'
        ? (q.options_he?.length ? q.options_he : q.options_en) ?? []
        : (q.options_en?.length ? q.options_en : q.options_he) ?? [];
    if (optsRaw.length < 2) return null;
    const opts = optsRaw.slice(0, 4);
    while (opts.length < 4) opts.push('—');
    const idx = Math.max(0, Math.min(opts.length - 1, q.correct_index ?? 0));
    base.options = opts.map((text, i) => ({
      key: MCQ_LETTERS[i]!,
      text: String(text).slice(0, 400),
    }));
    base.correct = MCQ_LETTERS[idx];
    // Gate policy: skip easy recognition MCQs when difficulty is easy.
    if (String(q.difficulty).toLowerCase() === 'easy') return null;
    return base;
  }

  if (kind === 'true_false') {
    const correctBool = resolveCorrectBool(q.answer_payload, {
      correct_answer: q.correct_answer,
    });
    if (correctBool == null) return null;
    const yes = locale === 'he' ? 'נכון' : 'True';
    const no = locale === 'he' ? 'לא נכון' : 'False';
    base.options = [
      { key: 'A', text: yes },
      { key: 'B', text: no },
      { key: 'C', text: '—' },
      { key: 'D', text: '—' },
    ];
    base.correct = correctBool ? 'A' : 'B';
    // True/false only at hard — otherwise too guessable for a gate.
    if (String(q.difficulty).toLowerCase() !== 'hard') return null;
    return base;
  }

  if (kind === 'numeric') {
    if (!q.correct_answer?.trim()) return null;
    return base;
  }

  if (kind === 'short_answer') {
    const accepted = q.answer_payload?.acceptable_answers ?? [];
    if (!q.correct_answer?.trim() && accepted.length === 0) return null;
    return base;
  }

  // open / derivation — need a rubric or model answer for later grading
  if (!rubric?.trim() && !model?.trim()) return null;
  return base;
}

function candidateScore(q: LessonQuestionRow, preferHard: boolean): number {
  const kind = SUPPORTED.has(q.kind) ? KIND_PRIORITY[q.kind as GateQuestionKind] ?? 0 : 0;
  const diffKey = String(q.difficulty ?? 'medium').toLowerCase();
  const diff = DIFF_PRIORITY[diffKey] ?? 2;
  // Soft-penalize easy unless we are desperate (handled by filter order).
  const easyPenalty = diffKey === 'easy' ? (preferHard ? -4 : -1) : 0;
  return kind * 10 + diff * 3 + easyPenalty;
}

/**
 * Collect authored bank candidates for the given concepts (alias-aware).
 */
export function collectGateBankCandidates(
  conceptIds: string[],
  locale: 'he' | 'en',
  rotation: number,
  pointsLevelMin?: LessonPointsLevel | null,
): GateBankPick[] {
  const out: GateBankPick[] = [];
  const seenStems = new Set<string>();

  for (const rawId of conceptIds) {
    const ids = [...new Set([rawId, resolveConceptAlias(rawId)])];
    for (const cid of ids) {
      const lesson = getBundledLesson(cid);
      if (!lesson) continue;
      const subject = lesson.lesson.subject === 'physics' ? 'physics' : 'math';
      for (const q of lesson.questions) {
        if (!allowedForPoints(q, pointsLevelMin)) continue;
        const pick = toGatePick(cid, subject, q, locale, rotation);
        if (!pick) continue;
        const stemKey = pick.stem.replace(/\s+/g, ' ').toLowerCase().slice(0, 160);
        if (seenStems.has(stemKey)) continue;
        seenStems.add(stemKey);
        out.push(pick);
      }
    }
  }
  return out;
}

/**
 * Pick a week-gate quiz from the authored bank: hard/open/numeric first,
 * spread across concepts, rotated on retakes.
 */
export function pickGateQuestionsFromBank(input: PickGateQuestionsInput): GateBankPick[] {
  const {
    conceptIds,
    locale,
    count,
    rotation = 0,
    pointsLevelMin = null,
    preferHard = true,
  } = input;
  if (conceptIds.length === 0 || count <= 0) return [];

  const all = collectGateBankCandidates(conceptIds, locale, rotation, pointsLevelMin);
  if (all.length === 0) return [];

  // Rank then shuffle within similar ranks for rotation variety.
  const ranked = [...all].sort((a, b) => {
    // Reconstruct rough priority from stored fields.
    const ka = KIND_PRIORITY[a.kind];
    const kb = KIND_PRIORITY[b.kind];
    if (kb !== ka) return kb - ka;
    if (preferHard && b.difficulty !== a.difficulty) return b.difficulty - a.difficulty;
    return a.id.localeCompare(b.id);
  });

  const seed = `${conceptIds.join('|')}|r${rotation}|${locale}|gate-v${GATE_BANK_FORMAT_VERSION}`;
  const shuffled = seededShuffle(ranked, seed);

  // Round-robin across concepts so one topic cannot dominate.
  const byTopic = new Map<string, GateBankPick[]>();
  for (const c of conceptIds) byTopic.set(c, []);
  for (const p of shuffled) {
    const list = byTopic.get(p.topic) ?? byTopic.get(resolveConceptAlias(p.topic));
    if (list) list.push(p);
    else {
      const fallback = byTopic.get(conceptIds[0]!) ?? [];
      fallback.push(p);
      byTopic.set(conceptIds[0]!, fallback);
    }
  }

  const picked: GateBankPick[] = [];
  const used = new Set<string>();
  let guard = 0;
  while (picked.length < count && guard < count * conceptIds.length * 3) {
    guard += 1;
    for (const cid of conceptIds) {
      if (picked.length >= count) break;
      const pool = byTopic.get(cid) ?? [];
      const next = pool.find((p) => !used.has(p.id));
      if (!next) continue;
      // Cap recognition items (mcq/tf) at ~25% of the gate.
      const recognition = picked.filter((p) => p.kind === 'mcq' || p.kind === 'true_false').length;
      if (
        (next.kind === 'mcq' || next.kind === 'true_false') &&
        recognition >= Math.max(1, Math.floor(count * 0.25))
      ) {
        used.add(next.id); // skip but don't retry forever
        continue;
      }
      used.add(next.id);
      picked.push(next);
    }
    // If round-robin stalled, take best remaining.
    if (picked.length < count) {
      const rest = shuffled.find((p) => !used.has(p.id));
      if (!rest) break;
      used.add(rest.id);
      picked.push(rest);
    }
  }

  return picked.slice(0, count);
}

/** Exported for tests — ranking helper. */
export function scoreLessonQuestionForGate(
  q: Pick<LessonQuestionRow, 'kind' | 'difficulty'>,
  preferHard = true,
): number {
  if (!SUPPORTED.has(q.kind)) return -100;
  return candidateScore(q as LessonQuestionRow, preferHard);
}

/**
 * True when the cached quiz is post-ADR-0010 hard format (exam corpus,
 * lesson bank, and/or grounded LLM fallback). Legacy easy-MCQ caches return
 * false so they are regenerated.
 */
export function isBankSourcedGateQuiz(
  questions: Array<{ source?: string; format_version?: number; kind?: string; parts?: unknown[] }>,
): boolean {
  if (!questions.length) return false;
  const modern = questions.filter(
    (q) =>
      (typeof q.format_version === 'number' && q.format_version >= 2) ||
      q.source === 'lesson_bank' ||
      q.source === 'exam_corpus' ||
      q.source === 'llm_fallback',
  ).length;
  if (modern < Math.ceil(questions.length * 0.8)) return false;
  // Prefer regenerating caches that have zero multipart / open production items.
  const productive = questions.filter(
    (q) =>
      q.kind === 'open' ||
      q.kind === 'derivation' ||
      q.kind === 'numeric' ||
      q.kind === 'short_answer' ||
      (Array.isArray(q.parts) && q.parts.length >= 2),
  ).length;
  return productive >= Math.ceil(questions.length * 0.5);
}
