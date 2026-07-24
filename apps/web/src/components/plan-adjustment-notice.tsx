'use client';

import { useEffect, useState } from 'react';
import { Info, X } from 'lucide-react';
import { Card, CardContent } from '@asf/ui/card';
import { Button } from '@asf/ui/button';
import type { LearningPlan } from '@asf/schemas/learning_path';
import { useLanguagePreference } from '@/hooks/use-language-preference';

const RECENT_MS = 7 * 24 * 60 * 60 * 1000;

const SERVER_DRIVEN_KINDS = new Set([
  'wellbeing',
  'mastery',
  'exam_window',
  'horizon_repair',
  'train_adapt',
]);

function dismissedStorageKey(learnerId: string, adjustedAt: string): string {
  return `asf-plan-adjustment-dismissed-${learnerId}-${adjustedAt}`;
}

const STR = {
  he: {
    message: 'התוכנית עודכנה לפי ההתקדמות שלך',
    horizon_repair:
      'קיצרנו את התוכנית כדי שתגיע/י ליעד בזמן — השבועות הבאים עודכנו.',
    train_adapt:
      'הוספנו יותר אימון השבוע כי את/ה קרוב/ה ליעד או מתרגל/ה בצורה חזקה.',
    close: 'סגור הודעה',
  },
  en: {
    message: 'Your plan was updated based on your progress.',
    horizon_repair:
      'We shortened the plan so you can reach your goal on time — upcoming weeks were adjusted.',
    train_adapt:
      'We added more practice this week because you are close to your goal or training strongly.',
    close: 'Dismiss notice',
  },
} as const;

function messageForKind(
  kind: string,
  t: (typeof STR)['he'] | (typeof STR)['en'],
): string {
  if (kind === 'horizon_repair') return t.horizon_repair;
  if (kind === 'train_adapt') return t.train_adapt;
  return t.message;
}

export function PlanAdjustmentNotice({
  plan,
  learnerId,
}: {
  plan: LearningPlan;
  learnerId: string;
}) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';
  const [visible, setVisible] = useState(false);

  const kind = plan.plan_adjustment_kind ?? null;
  const adjustedAt = plan.plan_last_adjusted_at ?? null;

  useEffect(() => {
    if (!kind || !adjustedAt || !SERVER_DRIVEN_KINDS.has(kind)) {
      setVisible(false);
      return;
    }
    const changedAt = new Date(adjustedAt);
    const isRecent =
      Number.isFinite(changedAt.getTime()) &&
      Date.now() - changedAt.getTime() < RECENT_MS;
    if (!isRecent) {
      setVisible(false);
      return;
    }
    const dismissed = localStorage.getItem(dismissedStorageKey(learnerId, adjustedAt));
    setVisible(dismissed !== '1');
  }, [kind, adjustedAt, learnerId]);

  function dismiss() {
    if (adjustedAt) {
      localStorage.setItem(dismissedStorageKey(learnerId, adjustedAt), '1');
    }
    setVisible(false);
  }

  if (!visible || !kind) return null;

  return (
    <Card
      className="relative mb-6 border-primary/30 bg-primary/5"
      dir={isHe ? 'rtl' : 'ltr'}
      role="status"
    >
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="absolute end-2 top-2 h-8 w-8 text-muted-foreground hover:text-foreground"
        onClick={dismiss}
        aria-label={t.close}
      >
        <X className="h-4 w-4" aria-hidden />
      </Button>
      <CardContent className="flex gap-3 p-4 pe-12">
        <Info className="mt-0.5 h-5 w-5 shrink-0 text-primary" aria-hidden />
        <p className="text-sm font-medium text-foreground">{messageForKind(kind, t)}</p>
      </CardContent>
    </Card>
  );
}
