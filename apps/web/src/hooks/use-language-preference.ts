'use client';

import { useCallback, useEffect, useState } from 'react';
import { LOCALE_COOKIE, LOCALE_STORAGE_KEY } from '@/i18n/locale-storage';

/**
 * Persistent learner language preference (Hebrew by default).
 *
 * Shares storage keys with `I18nProvider` (`asf-locale-v2` / `asf-locale`) so
 * toggling EN/עב in the site header updates every component that reads this
 * hook — quiz builder, lesson pages, learning plan, etc.
 */
export type Lang = 'en' | 'he';

function readInitial(): Lang {
  if (typeof window === 'undefined') return 'he';
  try {
    const ls = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    if (ls === 'en' || ls === 'he') return ls;
  } catch {
    // localStorage unavailable — fall through.
  }
  try {
    const match = document.cookie
      .split(';')
      .map((s) => s.trim())
      .find((s) => s.startsWith(`${LOCALE_COOKIE}=`));
    if (match) {
      const v = match.split('=')[1];
      if (v === 'en' || v === 'he') return v;
    }
  } catch {
    // ignore
  }
  try {
    const htmlLang = document.documentElement?.lang?.toLowerCase();
    if (htmlLang?.startsWith('en')) return 'en';
  } catch {
    // ignore
  }
  return 'he';
}

export function useLanguagePreference(defaultLang: Lang = 'he'): [Lang, (next: Lang) => void] {
  const [lang, setLang] = useState<Lang>(defaultLang);

  useEffect(() => {
    setLang(readInitial());

    const onStorage = (e: StorageEvent) => {
      if (e.key === LOCALE_STORAGE_KEY && (e.newValue === 'en' || e.newValue === 'he')) {
        setLang(e.newValue);
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const update = useCallback((next: Lang) => {
    setLang(next);
    try {
      window.localStorage.setItem(LOCALE_STORAGE_KEY, next);
    } catch {
      // ignore
    }
    try {
      document.cookie = `${LOCALE_COOKIE}=${next}; path=/; max-age=${60 * 60 * 24 * 365}; samesite=lax`;
    } catch {
      // ignore
    }
    document.documentElement.lang = next;
    document.documentElement.dir = next === 'he' ? 'rtl' : 'ltr';
  }, []);

  return [lang, update];
}
