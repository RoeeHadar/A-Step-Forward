/** Normalize learner subjects for diagnostic sampling. */
export function normalizeLearnerSubjects(subjects?: string[] | null): string[] {
  const cleaned = (subjects ?? []).filter((s) => s === 'math' || s === 'physics');
  if (cleaned.length > 0) return [...new Set(cleaned)];
  return ['math'];
}

/** Map onboarding profile fields to a Bagrut points band, if any. */
export function resolveDiagnosticPointsLevel(input: {
  pointsGroup?: string | null;
  goalKey?: string | null;
  adultGoal?: string | null;
}): string | null {
  const pg = input.pointsGroup;
  if (pg) {
    const num = String(pg).replace(/pt$/i, '').trim();
    if (['3', '4', '5'].includes(num)) return `${num}pt`;
    if (pg === 'hs_physics') return null;
  }

  const key = (input.goalKey || input.adultGoal || '').toLowerCase();
  if (key.includes('math_3') || key === 'bagrut_math_3') return '3pt';
  if (key.includes('math_4') || key === 'bagrut_math_4') return '4pt';
  if (key.includes('math_5') || key === 'bagrut_math_5') return '5pt';
  return null;
}

export const DIAGNOSTIC_SUBJECTS_SESSION_KEY = 'asf_diagnostic_subjects';

export function readDiagnosticSubjectsFromSession(): string[] | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = sessionStorage.getItem(DIAGNOSTIC_SUBJECTS_SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return null;
    const subjects = parsed.filter((s): s is string => typeof s === 'string');
    return subjects.length > 0 ? subjects : null;
  } catch {
    return null;
  }
}

export function clearDiagnosticSubjectsSession(): void {
  if (typeof window === 'undefined') return;
  sessionStorage.removeItem(DIAGNOSTIC_SUBJECTS_SESSION_KEY);
}

export async function readApiErrorMessage(res: Response): Promise<string> {
  const text = await res.text();
  if (!text.trim()) return `Request failed (${res.status})`;
  try {
    const data = JSON.parse(text) as { error?: string; message?: string };
    return data.error ?? data.message ?? text;
  } catch {
    return text;
  }
}
