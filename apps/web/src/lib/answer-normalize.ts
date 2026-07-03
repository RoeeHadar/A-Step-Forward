/**
 * Shared answer normalization for lesson question grading (client + server).
 */

const UNICODE_MINUS = /[\u2212\u2013\u2014]/g;
const LATEX_DELIMS = /\$\$/g;
const LATEX_INLINE = /\$/g;

/** Strip common LaTeX / formatting noise before comparing text answers. */
export function normalizeAnswerForGrading(s: string, caseSensitive = false): string {
  let t = s.trim();
  t = t.replace(LATEX_DELIMS, '').replace(LATEX_INLINE, '');
  t = t.replace(UNICODE_MINUS, '-');
  t = t.replace(/\s+/g, ' ');
  t = t.replace(/[.,;:]+$/g, '');
  return caseSensitive ? t : t.toLowerCase();
}

function isPlausibleAcceptedAnswer(a: string): boolean {
  const t = a.trim();
  if (!t || t.length > 300) return false;
  if (/\[\[|\]\]|TODO|acceptable_answers|correct_answer/i.test(t)) return false;
  if (/^[=+\-*_]{2,}$/.test(t)) return false;
  return true;
}

/** Build the list of strings to grade short_answer / fill_blank against. */
export function getAcceptedAnswers(
  acceptable: string[] | undefined | null,
  correctAnswer?: string | null,
): string[] {
  const fromPayload = (acceptable ?? []).filter(isPlausibleAcceptedAnswer);
  const out = [...fromPayload];
  const ca = correctAnswer?.trim();
  if (ca && !out.some((a) => normalizeAnswerForGrading(a) === normalizeAnswerForGrading(ca))) {
    out.push(ca);
  }
  if (out.length === 0 && ca) out.push(ca);
  return out;
}

export function answersMatch(
  userAnswer: string,
  accepted: string[],
  caseSensitive = false,
): boolean {
  const user = normalizeAnswerForGrading(userAnswer, caseSensitive);
  if (!user) return false;
  return accepted.some((a) => normalizeAnswerForGrading(a, caseSensitive) === user);
}

/** Best display string for feedback after a wrong short/fill answer. */
export function displayCorrectAnswer(
  acceptable: string[] | undefined | null,
  correctAnswer?: string | null,
): string {
  const list = getAcceptedAnswers(acceptable, correctAnswer);
  const preferred = correctAnswer?.trim() || list[0] || '';
  return preferred;
}

export function numericClose(a: string, b: string): boolean {
  const strip = (s: string) =>
    s
      .replace(LATEX_DELIMS, '')
      .replace(LATEX_INLINE, '')
      .replace(UNICODE_MINUS, '-')
      .trim();
  const na = Number.parseFloat(strip(a));
  const nb = Number.parseFloat(strip(b));
  if (Number.isNaN(na) || Number.isNaN(nb)) return false;
  const tol = Math.max(1e-3, Math.abs(nb) * 0.01);
  return Math.abs(na - nb) <= tol;
}
