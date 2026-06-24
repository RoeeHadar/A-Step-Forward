import { defaultLocale, locales, type Locale } from './config';

export const LOCALE_STORAGE_KEY = 'asf-locale';
export const LOCALE_COOKIE = 'asf-locale';

export function isLocale(value: string | null | undefined): value is Locale {
  return value != null && (locales as readonly string[]).includes(value);
}

export function localeDir(locale: Locale): 'ltr' | 'rtl' {
  return locale === 'he' ? 'rtl' : 'ltr';
}

export function resolveLocale(value: string | null | undefined): Locale {
  return isLocale(value) ? value : defaultLocale;
}
