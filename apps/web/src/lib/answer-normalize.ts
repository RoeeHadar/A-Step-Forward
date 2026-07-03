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
  if (/^\*\*(?:Solution|Check)/i.test(t)) return false;
  if (/^Solution path:/i.test(t)) return false;
  return true;
}

/** Pull concise math answers out of long seeded explanation strings. */
function extractInlineAnswers(raw: string): string[] {
  const out: string[] = [];
  const t = raw.trim();
  if (!t) return out;

  const latexMatches = t.matchAll(/\$([^$]+)\$/g);
  for (const m of latexMatches) {
    const inner = m[1]?.trim();
    if (inner && inner.length <= 120) out.push(inner);
  }

  const boldAnswer = t.match(/\*\*(?:Answer|תשובה):\*\*\s*([^\n]+)/i);
  if (boldAnswer?.[1]) out.push(boldAnswer[1].trim());

  const trailingEq = t.match(/=\s*([^=\n]{1,80})$/);
  if (trailingEq?.[1]) {
    const tail = trailingEq[1].replace(/\.\s*$/, '').trim();
    if (tail.length >= 1 && tail.length <= 80) out.push(tail);
  }

  return out;
}

/** Build the list of strings to grade short_answer / fill_blank against. */
export function getAcceptedAnswers(
  acceptable: string[] | undefined | null,
  correctAnswer?: string | null,
): string[] {
  const expanded: string[] = [];
  for (const entry of acceptable ?? []) {
    if (isPlausibleAcceptedAnswer(entry)) {
      expanded.push(entry);
    }
    expanded.push(...extractInlineAnswers(entry));
  }

  const seen = new Set<string>();
  const out: string[] = [];
  for (const candidate of expanded) {
    const norm = normalizeAnswerForGrading(candidate);
    if (!norm || seen.has(norm)) continue;
    seen.add(norm);
    out.push(candidate.trim());
  }

  const ca = correctAnswer?.trim();
  if (ca && !seen.has(normalizeAnswerForGrading(ca))) {
    out.push(ca);
  }
  if (out.length === 0 && ca) out.push(ca);
  return out;
}

/** Coerce DB/JSON values to a finite option index (MCQ). */
export function coerceOptionIndex(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const n = Number.parseInt(value, 10);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

/** Coerce DB/JSON boolean flags (true_false). */
export function coerceBooleanAnswer(value: unknown): boolean | null {
  if (typeof value === 'boolean') return value;
  if (value === 'true') return true;
  if (value === 'false') return false;
  return null;
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
