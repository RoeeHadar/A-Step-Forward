'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { Badge } from '@asf/ui/badge';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import type { LearnerStreak, RecentActivityItem } from '@/lib/neon-db';

/**
 * Streak + recent-activity card for /dashboard.
 *
 * The website "remembers" what the user has been doing across all chat,
 * lesson, and quiz interactions. This card surfaces:
 *
 *   - current streak (consecutive days active)
 *   - longest streak
 *   - active days in the last 30
 *   - last 6 actions (chat, lesson answer, quiz response)
 *
 * The underlying data comes from `getLearnerStreak()` + `getRecentActivity()`
 * in `neon-db.ts`, which unions chat_turns + lesson_answers + quiz_responses
 * + concept_mastery activity timestamps.
 */

const STR = {
  he: {
    title: 'הרצף שלך',
    current: 'רצף נוכחי',
    longest: 'רצף שיא',
    active_30: 'ימים פעילים ב-30 הימים האחרונים',
    days: (n: number) => (n === 1 ? 'יום 1' : `${n} ימים`),
    active_today: 'פעיל היום',
    not_today: 'לא פעיל היום',
    recent: 'מה עשית לאחרונה',
    no_recent: 'אין עדיין פעילות. התחל בצ׳אט עם הטיוטור או בשיעור.',
    kind: {
      chat: 'צ׳אט',
      lesson: 'שיעור',
      quiz: 'מבחן',
    } as Record<string, string>,
    detail_map: {} as Record<string, string>,
    detail_he: (s: string) =>
      s.replace(/^practiced /, 'תרגלת ')
        .replace(/\(mastery (\d+)%\)/, '(שליטה $1%)')
        .replace(/^practiced atom /, 'תרגלת מיומנות ')
        .replace(/\((\d+)\/(\d+)\)/, '($1/$2)'),
  },
  en: {
    title: 'Your streak',
    current: 'Current',
    longest: 'Longest',
    active_30: 'Active days in the last 30',
    days: (n: number) => (n === 1 ? '1 day' : `${n} days`),
    active_today: 'Active today',
    not_today: 'Not active today',
    recent: 'What you\u2019ve been doing',
    no_recent: 'No activity yet. Start a chat or open a lesson.',
    kind: {
      chat: 'Chat',
      lesson: 'Lesson',
      quiz: 'Quiz',
    } as Record<string, string>,
    detail_map: {} as Record<string, string>,
  },
} as const;

function relativeTime(iso: string, isHe: boolean): string {
  const t = new Date(iso).getTime();
  const diffMin = Math.max(0, Math.floor((Date.now() - t) / 60000));
  if (diffMin < 1) return isHe ? 'עכשיו' : 'just now';
  if (diffMin < 60) return isHe ? `לפני ${diffMin} ד׳` : `${diffMin}m ago`;
  const hr = Math.floor(diffMin / 60);
  if (hr < 24) return isHe ? `לפני ${hr} ש׳` : `${hr}h ago`;
  const d = Math.floor(hr / 24);
  return isHe ? `לפני ${d} ימים` : `${d}d ago`;
}

export function LearnerStreakCard({
  streak,
  activity,
}: {
  streak: LearnerStreak;
  activity: RecentActivityItem[];
}) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';

  return (
    <Card className="glass-surface border-border/60" dir={isHe ? 'rtl' : 'ltr'}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">{t.title}</CardTitle>
          <Badge variant={streak.active_today ? 'success' : 'secondary'}>
            {streak.active_today ? t.active_today : t.not_today}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid grid-cols-3 gap-3 text-center">
          <Stat label={t.current} value={t.days(streak.current_days)} accent />
          <Stat label={t.longest} value={t.days(streak.longest_days)} />
          <Stat label={t.active_30} value={`${streak.active_days_last_30}/30`} />
        </div>

        <div>
          <p className="mb-2 text-xs font-medium text-muted-foreground">{t.recent}</p>
          {activity.length === 0 ? (
            <p className="text-sm text-muted-foreground">{t.no_recent}</p>
          ) : (
            <ul className="space-y-1.5">
              {activity.slice(0, 6).map((a, i) => {
                const detailRaw = t.detail_map[a.detail] ?? a.detail;
                // Hebrew localisation for the dynamic detail strings emitted
                // by getRecentActivity ("practiced X (mastery Y%)" etc.).
                const detail =
                  isHe && 'detail_he' in t ? t.detail_he(detailRaw) : detailRaw;
                const sub = a.agent ?? a.concept_id ?? '';
                return (
                  <li
                    key={`${a.kind}-${a.created_at}-${i}`}
                    className="flex items-center justify-between gap-3 text-sm"
                  >
                    <span className="flex items-center gap-2 min-w-0">
                      <Badge variant="outline" className="shrink-0">
                        {t.kind[a.kind] ?? a.kind}
                      </Badge>
                      <span className="truncate text-foreground/80">
                        {sub ? `${sub} · ` : ''}{detail}
                      </span>
                    </span>
                    <span className="shrink-0 text-xs text-muted-foreground">
                      {relativeTime(a.created_at, isHe)}
                    </span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-lg border border-border/60 bg-card/50 p-3">
      <div
        className={`text-lg font-semibold ${accent ? 'text-primary' : 'text-foreground'}`}
      >
        {value}
      </div>
      <div className="mt-0.5 text-[10px] uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
    </div>
  );
}
