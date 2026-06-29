'use client';

import { useEffect, useState } from 'react';
import { TrendingUp } from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';

type GradeLine = {
  key: string;
  label: string;
  grade: number | null;
  masteryAvg: number;
};

const STR = {
  he: {
    title: '\u05de\u05d5\u05db\u05e0\u05d5\u05ea \u05dc\u05d1\u05d2\u05e8\u05d5\u05ea',
    practiceMore: '\u05ea\u05e8\u05d2\u05dc \u05d9\u05d5\u05ea\u05e8 \u05dc\u05e7\u05d1\u05dc\u05ea \u05d4\u05e2\u05e8\u05db\u05d4',
    math: (g: number) => `\u05e6\u05d9\u05d5\u05df \u05de\u05e9\u05d5\u05e2\u05e8: ~${g}`,
    physics: (g: number) => `\u05e6\u05d9\u05d5\u05df \u05de\u05e9\u05d5\u05e2\u05e8 (\u05e4\u05d9\u05d6\u05d9\u05e7\u05d4): ~${g}`,
  },
  en: {
    title: 'Bagrut Readiness',
    practiceMore: 'Practice more for estimate',
    math: (g: number) => `Est. grade: ~${g}`,
    physics: (g: number) => `Est. grade (Physics): ~${g}`,
  },
} as const;

async function fetchGrade(subject?: string): Promise<{ estimatedGrade: number; masteryAvg: number } | null> {
  const url = subject
    ? `/api/progress/estimated-grade?subject=${encodeURIComponent(subject)}`
    : '/api/progress/estimated-grade';
  const res = await fetch(url);
  if (!res.ok) return null;
  const data = (await res.json()) as { estimatedGrade?: number; masteryAvg?: number };
  if (typeof data.estimatedGrade !== 'number') return null;
  return {
    estimatedGrade: data.estimatedGrade,
    masteryAvg: Number(data.masteryAvg ?? 0),
  };
}

export function BagrutReadinessWidget({
  hasPhysicsEnrollment = false,
}: {
  hasPhysicsEnrollment?: boolean;
}) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];

  const [lines, setLines] = useState<GradeLine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      const next: GradeLine[] = [];

      const math = await fetchGrade();
      if (math) {
        next.push({
          key: 'math',
          label: 'math',
          grade: math.masteryAvg >= 0.3 ? math.estimatedGrade : null,
          masteryAvg: math.masteryAvg,
        });
      }

      if (hasPhysicsEnrollment) {
        const physics = await fetchGrade('hs_physics');
        if (physics) {
          next.push({
            key: 'physics',
            label: 'physics',
            grade: physics.masteryAvg >= 0.3 ? physics.estimatedGrade : null,
            masteryAvg: physics.masteryAvg,
          });
        }
      }

      if (!cancelled) {
        setLines(next);
        setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [hasPhysicsEnrollment]);

  const formatLine = (line: GradeLine): string => {
    if (line.grade == null) return t.practiceMore;
    if (line.label === 'physics') return t.physics(line.grade);
    return t.math(line.grade);
  };

  const allInsufficient = lines.length > 0 && lines.every((l) => l.grade == null);

  return (
    <div className="card-punch rounded-2xl p-5" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="flex items-start gap-3">
        <div
          className={cn(
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent-cyan text-primary-foreground',
          )}
        >
          <TrendingUp className="h-5 w-5" aria-hidden />
        </div>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground">{t.title}</p>
          {loading ? (
            <p className="mt-1 text-sm text-muted-foreground">...</p>
          ) : lines.length === 0 || allInsufficient ? (
            <p className="mt-1 text-sm italic text-muted-foreground">{t.practiceMore}</p>
          ) : (
            <div className="mt-1 space-y-0.5">
              {lines.map((line) => (
                <p
                  key={line.key}
                  className={cn(
                    'text-sm',
                    line.grade == null ? 'italic text-muted-foreground' : 'font-semibold text-foreground',
                  )}
                >
                  {formatLine(line)}
                </p>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
