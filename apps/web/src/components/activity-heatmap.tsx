'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import type { DailyActivity, WeeklyRecap } from '@/lib/neon-db';

/**
 * 30-day activity heatmap + this-week recap, sat on /dashboard.
 *
 * The heatmap renders a fixed-width grid (oldest → newest) coloured by
 * activity intensity (chat + concept touches + atom practice combined).
 * The recap shows aggregated counts for the current ISO week so the user
 * has a "what did I actually do this week" panel — same as GitHub's
 * contributions surface, but for learning.
 *
 * No interactivity beyond tooltips; data comes from server props.
 */
const STR = {
  he: {
    title: 'הפעילות שלך',
    last_30: '30 הימים האחרונים',
    no_data: 'עוד אין פעילות. צ׳אט או שיעור ראשון יאיר את הריבועים.',
    intensity: (n: number) =>
      n === 0 ? 'אין פעילות' : n === 1 ? 'פעולה אחת' : `${n} פעולות`,
    this_week: 'השבוע',
    chat_turns: 'הודעות צ׳אט',
    concepts: 'נושאים שנגעת בהם',
    atoms: 'מיומנויות שתורגלו',
    mastery_gain: 'נקודות שליטה נצברו',
    best_day: 'היום הכי פעיל',
    best_none: 'אין יום בולט',
    day_count: (n: number) => `${n} פעולות`,
  },
  en: {
    title: 'Your activity',
    last_30: 'Last 30 days',
    no_data: 'No activity yet. Your first chat or lesson will light up the grid.',
    intensity: (n: number) =>
      n === 0 ? 'no activity' : n === 1 ? '1 action' : `${n} actions`,
    this_week: 'This week',
    chat_turns: 'chat turns',
    concepts: 'concepts touched',
    atoms: 'atoms practiced',
    mastery_gain: 'mastery points',
    best_day: 'Best day',
    best_none: 'No standout day yet',
    day_count: (n: number) => `${n} actions`,
  },
} as const;

function levelOf(count: number): 0 | 1 | 2 | 3 | 4 {
  if (count <= 0) return 0;
  if (count <= 1) return 1;
  if (count <= 3) return 2;
  if (count <= 6) return 3;
  return 4;
}

const LEVEL_CLASSES: Record<number, string> = {
  0: 'bg-card border border-border/30',
  1: 'bg-primary/20 border border-primary/30',
  2: 'bg-primary/40 border border-primary/40',
  3: 'bg-primary/70 border border-primary/50',
  4: 'bg-primary border border-primary',
};

function formatShortDate(iso: string, isHe: boolean): string {
  try {
    return new Date(`${iso}T00:00:00Z`).toLocaleDateString(
      isHe ? 'he-IL' : 'en-GB',
      { month: 'short', day: 'numeric' },
    );
  } catch {
    return iso;
  }
}

export function ActivityHeatmap({
  daily,
  weekly,
}: {
  daily: DailyActivity[];
  weekly: WeeklyRecap;
}) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';

  const hasData = daily.some((d) => d.count > 0);

  return (
    <Card className="glass-surface border-border/60" dir={isHe ? 'rtl' : 'ltr'}>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{t.title}</CardTitle>
        <p className="text-xs text-muted-foreground">{t.last_30}</p>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Heatmap: 30-cell grid, oldest → newest. The grid is always shown
            LTR (calendars read left → right in both languages here), and we
            render in chronological order so it's intuitive regardless of UI dir. */}
        <div
          className="grid grid-cols-[repeat(15,minmax(0,1fr))] gap-1 sm:grid-cols-[repeat(30,minmax(0,1fr))]"
          dir="ltr"
          aria-label={t.title}
        >
          {daily.map((d) => {
            const lvl = levelOf(d.count);
            const label = `${formatShortDate(d.date, isHe)} — ${t.intensity(d.count)}`;
            return (
              <div
                key={d.date}
                className={`h-5 w-5 rounded-sm ${LEVEL_CLASSES[lvl]}`}
                title={label}
                aria-label={label}
              />
            );
          })}
        </div>

        {!hasData && (
          <p className="text-sm text-muted-foreground">{t.no_data}</p>
        )}

        <div className="rounded-lg border border-border/60 bg-card/50 p-3">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {t.this_week}
          </p>
          <div className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
            <Stat label={t.chat_turns} value={weekly.chat_turns} />
            <Stat label={t.concepts} value={weekly.concepts_touched} />
            <Stat label={t.atoms} value={weekly.atoms_practiced} />
            <Stat label={t.mastery_gain} value={weekly.mastery_gain} />
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            {weekly.best_day
              ? `${t.best_day}: ${formatShortDate(weekly.best_day.date, isHe)} — ${t.day_count(weekly.best_day.count)}`
              : t.best_none}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="text-lg font-semibold text-foreground">{value}</div>
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
    </div>
  );
}
