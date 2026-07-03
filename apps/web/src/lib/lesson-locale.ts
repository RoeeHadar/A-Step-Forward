export type LessonLang = 'en' | 'he';

function letterCounts(text: string): { hebrew: number; latin: number } {
  const hebrew = (text.match(/[\u0590-\u05FF]/g) ?? []).length;
  const latin = (text.match(/[a-zA-Z]/g) ?? []).length;
  return { hebrew, latin };
}

/** True when text is predominantly Hebrew script. */
export function looksHebrew(text: string): boolean {
  const { hebrew, latin } = letterCounts(text);
  return hebrew > latin && hebrew >= 8;
}

/** True when text is predominantly Latin script. */
export function looksEnglish(text: string): boolean {
  const { hebrew, latin } = letterCounts(text);
  return latin > hebrew && latin >= 8;
}

/**
 * Pick lesson text for the active UI language.
 * - Prefer the field for the requested language when it matches that script.
 * - If the primary field looks like the wrong language (common content bug),
 *   use the alternate field when it matches the requested language.
 * - If primary is empty, fall back to alternate so learners see content.
 */
export function pickLessonText(
  lang: LessonLang,
  he?: string | null,
  en?: string | null,
): string {
  const heT = he?.trim() ?? '';
  const enT = en?.trim() ?? '';

  if (lang === 'he') {
    if (heT && looksHebrew(heT)) return heT;
    if (heT && !looksHebrew(heT) && enT && looksHebrew(enT)) return enT;
    if (heT) return heT;
    return enT;
  }

  if (enT && looksEnglish(enT)) return enT;
  if (enT && !looksEnglish(enT) && heT && looksEnglish(heT)) return heT;
  if (enT) return enT;
  return heT;
}

export function lessonTextDir(lang: LessonLang): 'rtl' | 'ltr' {
  return lang === 'he' ? 'rtl' : 'ltr';
}
