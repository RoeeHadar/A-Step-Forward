'use client';

import { useEffect, useState } from 'react';
import { useI18n } from '@/providers/i18n-provider';

type HistoryItem = {
  score_pct: number;
  date: string;
  subject: string;
};

const STR = {
  he: { title: '\u05d4\u05d9\u05e1\u05d8\u05d5\u05e8\u05d9\u05d9\u05ea \u05de\u05d1\u05d7\u05e0\u05d9\u05dd \u05de\u05d3\u05d5\u05de\u05d9\u05dd' },
  en: { title: 'Mock Exam History' },
} as const;

export function MockExamHistoryWidget() {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];

  const [scores, setScores] = useState<number[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetch('/api/quiz/mock-exam/history')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (cancelled || !data || !Array.isArray(data.items)) return;
        const items = data.items as HistoryItem[];
        if (items.length === 0) return;
        const lastThree = items.slice(0, 3).reverse().map((i) => i.score_pct);
        setScores(lastThree);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  if (!scores || scores.length === 0) return null;

  const trend = scores.map((s) => `${s}%`).join(' \u2192 ');

  return (
    <div className="card-punch rounded-2xl px-5 py-3" dir={isHe ? 'rtl' : 'ltr'}>
      <p className="text-xs text-muted-foreground">{t.title}</p>
      <p className="mt-1 text-sm font-medium" aria-label={t.title}>
        {'\uD83D\uDCDD'} {trend}
      </p>
    </div>
  );
}