/**
 * Bagrut / finals exam-style corpus — original ASF multi-part items used as
 * the primary source for weekly gates, custom quizzes, and mock exams.
 *
 * Copyright: items are authored practice material (`source: asf_original`).
 * Official MoE PDFs under public/content/bagrut/ are style reference only and
 * MUST NOT be transcribed into this corpus.
 */
import { createHash } from 'node:crypto';
import corpus from './exam-style-corpus.generated.json';

export interface ExamStylePart {
  label: string;
  body_he: string;
  body_en: string;
  points: number;
}

export interface ExamStyleItem {
  id: string;
  goal_keys: string[];
  concept_ids: string[];
  subject: string;
  level: string;
  paper_pattern: string;
  difficulty: 'hard' | 'very_hard' | string;
  total_points: number;
  stem_he: string;
  stem_en: string;
  parts: ExamStylePart[];
  sample_solution_he: string;
  sample_solution_en: string;
  rubric_he: string;
  rubric_en: string;
  style_tags: string[];
  source: string;
}

interface CorpusFile {
  generated_at: string;
  count: number;
  by_goal: Record<string, number>;
  items: ExamStyleItem[];
}

const data = corpus as unknown as CorpusFile;
const ALL: ExamStyleItem[] = Array.isArray(data.items) ? data.items : [];

export function examStyleCorpusStats(): { count: number; by_goal: Record<string, number> } {
  return { count: data.count ?? ALL.length, by_goal: data.by_goal ?? {} };
}

export function listExamStyleItems(): readonly ExamStyleItem[] {
  return ALL;
}

function seededShuffle<T>(items: T[], seed: string): T[] {
  const out = [...items];
  let h = createHash('sha256').update(seed).digest();
  for (let i = out.length - 1; i > 0; i -= 1) {
    const byte = h[i % h.length] ?? 0;
    const j = byte % (i + 1);
    [out[i], out[j]] = [out[j]!, out[i]!];
    if (i % 16 === 0) h = createHash('sha256').update(h).digest();
  }
  return out;
}

function scoreItem(
  it: ExamStyleItem,
  conceptIds: Set<string>,
  goalKey: string | null,
): number {
  let score = 0;
  if (goalKey && it.goal_keys?.includes(goalKey)) score += 50;
  const overlap = (it.concept_ids ?? []).filter((c) => conceptIds.has(c)).length;
  score += overlap * 30;
  if (it.difficulty === 'very_hard') score += 8;
  else if (it.difficulty === 'hard') score += 5;
  if ((it.parts?.length ?? 0) >= 3) score += 10;
  else if ((it.parts?.length ?? 0) >= 2) score += 6;
  if ((it.style_tags ?? []).includes('multipart')) score += 8;
  if ((it.style_tags ?? []).includes('investigation')) score += 4;
  if ((it.style_tags ?? []).includes('proof')) score += 3;
  // Prefer authored / mock multipart over single-part question-store drills.
  if ((it.style_tags ?? []).includes('from_question_store') && (it.parts?.length ?? 0) < 2) {
    score -= 12;
  }
  if ((it.concept_ids?.length ?? 0) > 0) score += 2;
  if ((it.id ?? '').startsWith('exam_')) score += 5;
  return score;
}

export interface PickExamStyleInput {
  conceptIds?: string[];
  goalKey?: string | null;
  count: number;
  rotation?: number;
  locale?: 'he' | 'en';
  /** If true, require goal_keys match when goalKey is set (default false — soft prefer). */
  requireGoal?: boolean;
}

/**
 * Pick multi-part exam-style items for a gate/quiz. Prefers goal + concept overlap.
 */
export function pickExamStyleItems(input: PickExamStyleInput): ExamStyleItem[] {
  const {
    conceptIds = [],
    goalKey = null,
    count,
    rotation = 0,
    requireGoal = false,
  } = input;
  if (count <= 0) return [];

  const conceptSet = new Set(conceptIds);
  let pool = ALL.filter((it) => (it.parts?.length ?? 0) >= 2 && it.stem_en && it.stem_he);
  if (requireGoal && goalKey) {
    const tight = pool.filter((it) => it.goal_keys?.includes(goalKey));
    if (tight.length > 0) pool = tight;
  }

  const ranked = pool
    .map((it) => ({ it, s: scoreItem(it, conceptSet, goalKey) }))
    .filter((r) => r.s > 0 || conceptSet.size === 0)
    .sort((a, b) => b.s - a.s || a.it.id.localeCompare(b.it.id));

  // If nothing scored (unknown concepts), fall back to goal-tagged hard items.
  let candidates = ranked.map((r) => r.it);
  if (candidates.length === 0 && goalKey) {
    candidates = pool.filter((it) => it.goal_keys?.includes(goalKey));
  }
  if (candidates.length === 0) candidates = pool;

  const seed = `${goalKey ?? ''}|${conceptIds.join(',')}|r${rotation}|exam-style`;
  const shuffledTop = seededShuffle(candidates.slice(0, Math.max(count * 4, 12)), seed);

  const picked: ExamStyleItem[] = [];
  const usedConcepts = new Set<string>();
  for (const it of shuffledTop) {
    if (picked.length >= count) break;
    const primary = it.concept_ids?.[0];
    if (primary && usedConcepts.has(primary) && picked.length < count - 1) {
      // Soft diversity — skip if we already have this concept unless we need fill.
      continue;
    }
    picked.push(it);
    for (const c of it.concept_ids ?? []) usedConcepts.add(c);
  }
  // Fill remainder without diversity constraint.
  if (picked.length < count) {
    for (const it of shuffledTop) {
      if (picked.length >= count) break;
      if (picked.some((p) => p.id === it.id)) continue;
      picked.push(it);
    }
  }
  return picked.slice(0, count);
}

/** Render stem + parts into a single open-response prompt for graders / UI. */
export function formatExamStyleStem(it: ExamStyleItem, locale: 'he' | 'en'): string {
  const stem = locale === 'he' ? it.stem_he : it.stem_en;
  const parts = (it.parts ?? [])
    .map((p) => {
      const body = locale === 'he' ? p.body_he : p.body_en;
      return `**(${p.label})** (${p.points} ${locale === 'he' ? 'נק\'' : 'pts'})\n${body}`;
    })
    .join('\n\n');
  return `${stem}\n\n${parts}`.trim();
}

/** Compact exemplars for LLM grounding (no full solutions — avoid leaking). */
export function examStyleExemplarsForPrompt(
  conceptIds: string[],
  goalKey: string | null,
  n = 3,
): string {
  const items = pickExamStyleItems({ conceptIds, goalKey, count: n, rotation: 0 });
  if (items.length === 0) return '(no exam-style exemplars)';
  return items
    .map((it, i) => {
      const preview = formatExamStyleStem(it, 'he').slice(0, 420);
      return `${i + 1}. [${it.level}/${it.paper_pattern}/${it.difficulty}] ${preview}${preview.length >= 420 ? '…' : ''}`;
    })
    .join('\n\n');
}
