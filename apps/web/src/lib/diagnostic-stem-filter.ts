import type { LearnerProfileRow } from '@/lib/neon-db';

/** Notation typical of university analysis — not Bagrut high-school framing. */
const ADVANCED_MATH_NOTATION =
  /\\mathbb\{R\}|\\mathbb\{N\}|\\mathbb\{Z\}|\\mathbb\{Q\}|ℝ|ℚ|ℤ|ℕ|\bnumber field\b|שדה המספרים|\bcodomain\b|\bdomain:\s*\\?mathbb/i;

const HEAVY_SYMBOLIC =
  /\\forall|\\exists|\\subseteq|\\cap|\\cup|\\lim_\{|\\int_\{|\\partial/i;

/** Prefer stems that read like comprehension / concept understanding. */
export function isVerbalUnderstandingStem(stem: string): boolean {
  const s = (stem ?? '').trim();
  if (s.length < 35) return false;
  if (/^(which|what|how|why|מתי|מה|איך|למה|איזה)/i.test(s)) return true;
  if (/best describes|main idea|מסביר|הגדרה|משמעות/i.test(s)) return true;
  return s.length >= 80;
}

export function stemAllowedForProfile(stem: string, profile: LearnerProfileRow | null): boolean {
  const s = stem ?? '';
  const pg = profile?.points_group ?? '';
  const hsBand =
    pg === '3pt' ||
    pg === '4pt' ||
    pg === '5pt' ||
    pg === 'hs_physics' ||
    (profile?.personality_profile as { grade_band?: string } | null)?.grade_band ===
      'high_school';

  if (!hsBand) return true;

  if (ADVANCED_MATH_NOTATION.test(s)) return false;
  if (HEAVY_SYMBOLIC.test(s) && !/\$[^$]{1,40}\$/.test(s)) return false;
  return true;
}

export function stemMatchesSlotKind(
  stem: string,
  slotKind: 'basic' | 'medium' | 'hard' | 'verbal',
): boolean {
  if (slotKind !== 'verbal') return true;
  return isVerbalUnderstandingStem(stem);
}
