'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';

const STR = {
  he: '\u05DB\u05DC \u05D4\u05DB\u05D1\u05D5\u05D3! \u05E1\u05D9\u05D9\u05DE\u05EA \u05E0\u05D5\u05E9\u05D0 \u05D4\u05D9\u05D5\u05DD \uD83C\uDF89',
  en: 'Well done! You finished a topic today \uD83C\uDF89',
} as const;

export function MicroWinToast() {
  const searchParams = useSearchParams();
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const completed =
      searchParams.get('completed') === '1' || searchParams.get('lesson_done') === 'true';
    if (!completed) return;

    setVisible(true);
    const timer = window.setTimeout(() => setVisible(false), 4000);
    return () => window.clearTimeout(timer);
  }, [searchParams]);

  if (!visible) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-xl border border-border bg-card px-5 py-3 text-sm font-medium shadow-lg',
        'animate-in fade-in slide-in-from-bottom-4 duration-300',
      )}
      dir={isHe ? 'rtl' : 'ltr'}
    >
      {STR[isHe ? 'he' : 'en']}
    </div>
  );
}