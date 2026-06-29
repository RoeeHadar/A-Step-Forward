'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Skeleton } from '@asf/ui/skeleton';
import { Button } from '@asf/ui/button';
import { Badge } from '@asf/ui/badge';
import { useI18n } from '@/providers/i18n-provider';

interface DueReviewItem {
  atom_id: string;
  concept_id: string;
  concept_name: string;
  last_score: number;
  times_practiced: number;
}

const STR = {
  he: {
    due: (n: number) => `יש לך ${n} נושאים לחזרה היום:`,
    dueOne: 'יש לך נושא אחד לחזרה היום:',
    more: (n: number) => `+${n} נוספים`,
    cta: 'התחל חזרה עם המאמן',
  },
  en: {
    due: (n: number) => `${n} items due for review today:`,
    dueOne: '1 item due for review today:',
    more: (n: number) => `+${n} more`,
    cta: 'Start review with Coach',
  },
} as const;

const MAX_INLINE = 3;

export function DueReviewsWidget() {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];

  const [items, setItems] = useState<DueReviewItem[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetch('/api/coach/due-reviews')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled && data && Array.isArray(data.items)) {
          setItems(data.items as DueReviewItem[]);
        } else if (!cancelled) {
          setItems([]);
        }
      })
      .catch(() => {
        if (!cancelled) setItems([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (items === null) {
    return (
      <div className="card-punch rounded-2xl p-5" aria-hidden>
        <Skeleton className="h-5 w-2/3" />
        <Skeleton className="mt-3 h-9 w-40" />
      </div>
    );
  }

  const count = items.length;
  if (count === 0) return null;

  const visibleItems = items.slice(0, MAX_INLINE);
  const overflowCount = count - visibleItems.length;
  const heading = count === 1 ? t.dueOne : t.due(count);

  return (
    <div
      className="card-punch flex flex-col gap-3 rounded-2xl p-5"
      dir={isHe ? 'rtl' : 'ltr'}
    >
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex flex-col gap-2">
          <p className="font-medium">{heading}</p>
          <div className="flex flex-wrap gap-1.5">
            {visibleItems.map((item) => (
              <Badge key={item.atom_id} variant="secondary" className="text-xs">
                {item.concept_name}
              </Badge>
            ))}
            {overflowCount > 0 && (
              <Badge variant="outline" className="text-xs text-muted-foreground">
                {t.more(overflowCount)}
              </Badge>
            )}
          </div>
        </div>
        <Button asChild size="sm" className="shrink-0 self-start">
          <Link href="/app/chat/coach">{t.cta}</Link>
        </Button>
      </div>
    </div>
  );
}
