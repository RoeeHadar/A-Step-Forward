/**
 * Deterministic response-language resolution for live chat (ADR-0015).
 *
 * Precedence:
 *   1. Explicit language request in the current (or recent) message
 *   2. Language of the latest substantive learner message
 *   3. Profile preference (personality_profile.ui_lang / preferred_lang)
 *   4. UI locale cookie
 */

export type ChatResponseLocale = 'he' | 'en';

const EXPLICIT_HE =
  /(?:עברית|בעברית|תענה בעברית|תכתוב בעברית|speak hebrew|in hebrew|answer in hebrew)/i;
const EXPLICIT_EN =
  /(?:english|באנגלית|תענה באנגלית|תכתוב באנגלית|speak english|in english|answer in english)/i;

/** Heuristic: mostly Hebrew letters → he; mostly Latin → en. */
export function detectMessageLanguage(text: string): ChatResponseLocale | null {
  const t = text.trim();
  if (!t) return null;
  const hebrew = (t.match(/[\u0590-\u05FF]/g) ?? []).length;
  const latin = (t.match(/[A-Za-z]/g) ?? []).length;
  if (hebrew === 0 && latin === 0) return null;
  if (hebrew >= latin * 0.4 && hebrew >= 2) return 'he';
  if (latin > hebrew) return 'en';
  if (hebrew > 0) return 'he';
  return null;
}

export function detectExplicitLanguageRequest(text: string): ChatResponseLocale | null {
  if (EXPLICIT_HE.test(text)) return 'he';
  if (EXPLICIT_EN.test(text)) return 'en';
  return null;
}

export function resolveResponseLanguage(opts: {
  message: string;
  recentUserMessages?: string[];
  profileLang?: string | null;
  uiLocale: ChatResponseLocale;
}): ChatResponseLocale {
  const explicitCurrent = detectExplicitLanguageRequest(opts.message);
  if (explicitCurrent) return explicitCurrent;

  const fromMessage = detectMessageLanguage(opts.message);
  // Skip trivial/short affirmations so profile/recent substantive turns win.
  const trivial = /^\s*(ok|okay|sure|yes|no|כן|לא|בסדר|אוקיי|\?+|\!+)\s*$/i.test(opts.message.trim());
  if (fromMessage && !trivial && opts.message.trim().length >= 8) return fromMessage;

  for (const prev of [...(opts.recentUserMessages ?? [])].reverse()) {
    const d = detectExplicitLanguageRequest(prev) ?? detectMessageLanguage(prev);
    if (d && prev.trim().length >= 8) return d;
  }

  const profile = (opts.profileLang ?? '').trim().toLowerCase();
  if (profile === 'he' || profile === 'he-il' || profile.startsWith('he')) return 'he';
  if (profile === 'en' || profile === 'en-us' || profile.startsWith('en')) return 'en';

  return opts.uiLocale;
}

export function languageInstructionBlock(locale: ChatResponseLocale): string {
  return locale === 'en'
    ? `## Response language\n- Respond in **English** for this turn (resolved from learner request / message / profile / UI).\n- Do not switch to Hebrew unless the learner asks.`
    : `## Response language\n- Respond in **Hebrew** for this turn (resolved from learner request / message / profile / UI).\n- Write complete grammatical Hebrew sentences. Do not mix English filler or raw prompt labels.\n- Do not switch to English unless the learner asks.`;
}
