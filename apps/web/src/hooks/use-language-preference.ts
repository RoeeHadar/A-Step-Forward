'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  LOCALE_CHANGED_EVENT,
  LOCALE_COOKIE,
  LOCALE_STORAGE_KEY,
  dispatchLocaleChanged,
} from '@/i18n/locale-storage';
import { useOptionalI18n } from '@/providers/i18n-provider';

/**
 * Persistent learner language preference (Hebrew by default).
 *
 * When rendered inside `I18nProvider`, delegates to `useI18n()` so the site
 * header toggle and lesson inline controls share one locale source. Falls back
 * to local state + storage when outside the provider (tests, Storybook).
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

function persistLocaleLocal(next: Lang) {
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
}

export function useLanguagePreference(defaultLang: Lang = 'he'): [Lang, (next: Lang) => void] {
  const i18n = useOptionalI18n();
  const [localLang, setLocalLang] = useState<Lang>(defaultLang);

  useEffect(() => {
    if (i18n) return;

    setLocalLang(readInitial());

    const onStorage = (e: StorageEvent) => {
      if (e.key === LOCALE_STORAGE_KEY && (e.newValue === 'en' || e.newValue === 'he')) {
        setLocalLang(e.newValue);
      }
    };

    const onLocaleChanged = (e: Event) => {
      const next = (e as CustomEvent<{ locale: Lang }>).detail?.locale;
      if (next === 'en' || next === 'he') setLocalLang(next);
    };

    window.addEventListener('storage', onStorage);
    window.addEventListener(LOCALE_CHANGED_EVENT, onLocaleChanged);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener(LOCALE_CHANGED_EVENT, onLocaleChanged);
    };
  }, [i18n]);

  const updateLocal = useCallback((next: Lang) => {
    setLocalLang(next);
    persistLocaleLocal(next);
    dispatchLocaleChanged(next);
  }, []);

  const update = useCallback(
    (next: Lang) => {
      if (i18n) {
        i18n.setLocale(next);
      } else {
        updateLocal(next);
      }
    },
    [i18n, updateLocal],
  );

  const lang = i18n ? (i18n.locale as Lang) : localLang;
  return [lang, update];
}
