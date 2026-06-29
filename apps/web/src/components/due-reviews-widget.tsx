'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Skeleton } from '@asf/ui/skeleton';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';

const STR = {
  he: {
    due: (n: number) => `יש לך ${n} נושאים לחזרה היום`,
    cta: 'התחל חזרה עם המאמן',
  },
  en: {
    due: (n: number) => `You have ${n} items due for review today`,
    cta: 'Start review with Coach',
  },
} as const;

export function DueReviewsWidget() {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];

  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetch('/api/coach/due-reviews')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled && data && typeof data.count === 'number') {
          setCount(data.count);
        } else if (!cancelled) {
          setCount(0);
        }
      })
      .catch(() => {
        if (!cancelled) setCount(0);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (count === null) {
    return (
      <div className="card-punch rounded-2xl p-5" aria-hidden>
        <Skeleton className="h-5 w-2/3" />
        <Skeleton className="mt-3 h-9 w-40" />
      </div>
    );
  }

  if (count === 0) return null;

  return (
    <div
      className="card-punch flex flex-col gap-3 rounded-2xl p-5 sm:flex-row sm:items-center sm:justify-between"
      dir={isHe ? 'rtl' : 'ltr'}
    >
      <p className="font-medium">{t.due(count)}</p>
      <Button asChild size="sm" className="shrink-0">
        <Link href="/app/chat/coach">{t.cta}</Link>
      </Button>
    </div>
  );
}