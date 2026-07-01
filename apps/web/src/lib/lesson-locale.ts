export type LessonLang = 'en' | 'he';

/**
 * Pick lesson text for the active UI language only.
 * Never cross-fallback to the other language — mixed-language sections
 * are a content bug, not something the UI should paper over.
 */
export function pickLessonText(
  lang: LessonLang,
  he?: string | null,
  en?: string | null,
): string {
  const primary = lang === 'he' ? he : en;
  return primary?.trim() ?? '';
}

export function lessonTextDir(lang: LessonLang): 'rtl' | 'ltr' {
  return lang === 'he' ? 'rtl' : 'ltr';
}
