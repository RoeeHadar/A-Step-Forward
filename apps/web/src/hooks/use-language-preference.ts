'use client';

import { useCallback, useEffect, useState } from 'react';

/**
 * Persistent learner language preference (Hebrew by default).
 *
 * Why HE-default: the platform is built for Israeli learners preparing for
 * the Bagrut. English is the SECOND language for most users; opening every
 * lesson in EN created the perception that "some lectures are English-only"
 * even though every authored lesson is fully bilingual.
 *
 * Persistence layers:
 *  - `localStorage["asf.lang"]` so the choice survives reloads on the same
 *    device.
 *  - `document.cookie["asf_lang"]` so a future Server Component refactor can
 *    read the preference at SSR time and skip the FOUC of switching from
 *    HE to EN on hydration.
 */
export type Lang = 'en' | 'he';

const STORAGE_KEY = 'asf.lang';
const COOKIE_KEY = 'asf_lang';

function readInitial(): Lang {
  if (typeof window === 'undefined') return 'he';
  try {
    const ls = window.localStorage.getItem(STORAGE_KEY);
    if (ls === 'en' || ls === 'he') return ls;
  } catch {
    // localStorage unavailable (private mode, SSR snapshot) — fall through.
  }
  try {
    const match = document.cookie.split(';').map((s) => s.trim()).find((s) => s.startsWith(`${COOKIE_KEY}=`));
    if (match) {
      const v = match.split('=')[1];
      if (v === 'en' || v === 'he') return v;
    }
  } catch {
    // ignore
  }
  // No prior preference: detect from <html lang>, then default HE.
  try {
    const htmlLang = document.documentElement?.lang?.toLowerCase();
    if (htmlLang?.startsWith('en')) return 'en';
  } catch {
    // ignore
  }
  return 'he';
}

export function useLanguagePreference(defaultLang: Lang = 'he'): [Lang, (next: Lang) => void] {
  // SSR-safe: start with the requested default; sync to persisted choice in
  // useEffect to avoid a hydration mismatch.
  const [lang, setLang] = useState<Lang>(defaultLang);

  useEffect(() => {
    setLang(readInitial());
  }, []);

  const update = useCallback((next: Lang) => {
    setLang(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // ignore
    }
    try {
      // 1-year persistence.
      document.cookie = `${COOKIE_KEY}=${next}; path=/; max-age=${60 * 60 * 24 * 365}; samesite=lax`;
    } catch {
      // ignore
    }
  }, []);

  return [lang, update];
}
