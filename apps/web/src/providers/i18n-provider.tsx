'use client';

import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import type { Locale } from '@/i18n/config';
import { defaultLocale } from '@/i18n/config';
import {
  LOCALE_STORAGE_KEY,
  LOCALE_COOKIE,
  isLocale,
  localeDir,
  dispatchLocaleChanged,
} from '@/i18n/locale-storage';
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

/** Re-fetch server components after cookie locale changes (learn catalog, etc.). */
function LocaleRouterRefresh({ locale }: { locale: Locale }) {
  const router = useRouter();
  const pathname = usePathname();
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    // Keep in-progress onboarding answers when toggling EN/עב.
    if (pathname?.startsWith('/onboarding')) return;
    router.refresh();
  }, [locale, router, pathname]);

  return null;
}

export function I18nProvider({
  children,
  initialLocale = defaultLocale,
}: {
  children: React.ReactNode;
  initialLocale?: Locale;
}) {
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
    dispatchLocaleChanged(next);
  };

  useEffect(() => {
    syncDocumentLocale(locale);
  }, [locale]);

  return (
    <I18nContext.Provider
      value={{ locale, messages: getMessages(locale), setLocale, dir: localeDir(locale) }}
    >
      <LocaleRouterRefresh locale={locale} />
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}

/** Returns null outside I18nProvider (e.g. isolated tests). */
export function useOptionalI18n(): I18nContextValue | null {
  return useContext(I18nContext);
}
