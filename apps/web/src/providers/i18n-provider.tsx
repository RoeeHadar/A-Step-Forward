'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import type { Locale } from '@/i18n/config';
import { defaultLocale } from '@/i18n/config';
import { LOCALE_STORAGE_KEY, LOCALE_COOKIE, isLocale, localeDir } from '@/i18n/locale-storage';
import { getMessages, type Messages } from '@/i18n/messages';

interface I18nContextValue {
  locale: Locale;
  messages: Messages;
  setLocale: (locale: Locale) => void;
  dir: 'ltr' | 'rtl';
}

const I18nContext = createContext<I18nContextValue | null>(null);

function persistLocale(locale: Locale) {
  localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  document.cookie = `${LOCALE_COOKIE}=${locale};path=/;max-age=31536000;sameSite=lax`;
}

function syncDocumentLocale(locale: Locale) {
  document.documentElement.lang = locale;
  document.documentElement.dir = localeDir(locale);
}

export function I18nProvider({ children, initialLocale = defaultLocale }: { children: React.ReactNode; initialLocale?: Locale }) {
  const [locale, setLocaleState] = useState<Locale>(initialLocale);

  useEffect(() => {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (isLocale(stored)) {
      setLocaleState(stored);
      syncDocumentLocale(stored);
      document.cookie = `${LOCALE_COOKIE}=${stored};path=/;max-age=31536000;sameSite=lax`;
      return;
    }
    persistLocale(initialLocale);
    syncDocumentLocale(initialLocale);
  }, [initialLocale]);

  const setLocale = (next: Locale) => {
    setLocaleState(next);
    persistLocale(next);
    syncDocumentLocale(next);
  };

  useEffect(() => {
    syncDocumentLocale(locale);
  }, [locale]);

  return (
    <I18nContext.Provider value={{ locale, messages: getMessages(locale), setLocale, dir: localeDir(locale) }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}
