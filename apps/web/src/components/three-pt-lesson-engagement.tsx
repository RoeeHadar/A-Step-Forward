'use client';

type Lang = 'en' | 'he';

export type LessonEngagementTrack = '3pt' | 'makhina';

export type LessonEngagementContext = {
  pathname: string;
  subject?: string | null;
  levelMin?: string | null;
  mathTrack?: string[];
  learnerLevel?: string | null;
};

function isPureThreePtLessonContext({
  pathname,
  levelMin,
  mathTrack,
  learnerLevel,
}: LessonEngagementContext): boolean {
  if (pathname.includes('3pt')) return true;
  if (levelMin === '3pt') return true;
  if (learnerLevel === '3pt') return true;
  if (mathTrack?.includes('3pt')) return true;
  return false;
}

function isMakhinaLessonContext({
  pathname,
  subject,
  levelMin,
  mathTrack,
  learnerLevel,
}: LessonEngagementContext): boolean {
  if (subject === 'makhina' || subject?.includes('makhina')) return true;
  if (levelMin === 'makhina') return true;
  if (learnerLevel === 'makhina') return true;
  if (mathTrack?.includes('makhina')) return true;
  if (pathname.includes('/learn/makhina') || pathname.includes('/app/lessons/makhina')) {
    return true;
  }
  return false;
}

/** Returns the engagement track when progress + completion UX should activate. */
export function getLessonEngagementTrack(
  params: LessonEngagementContext,
): LessonEngagementTrack | null {
  if (isMakhinaLessonContext(params)) return 'makhina';
  if (isPureThreePtLessonContext(params)) return '3pt';
  return null;
}

/** True for 3pt and מכינה lesson contexts (progress bar + completion message). */
export function isThreePtLessonContext(params: LessonEngagementContext): boolean {
  return getLessonEngagementTrack(params) !== null;
}

export function ThreePtProgressBar({
  currentSection,
  totalSections,
  lang,
}: {
  currentSection: number;
  totalSections: number;
  lang: Lang;
}) {
  if (totalSections <= 0) return null;

  const clampedCurrent = Math.min(Math.max(currentSection, 1), totalSections);
  const pct = Math.round((clampedCurrent / totalSections) * 100);

  return (
    <div className="mb-4" aria-label={lang === 'he' ? 'התקדמות בשיעור' : 'Lesson progress'}>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
        <div
          className="h-full rounded-full bg-blue-200 transition-all duration-300 dark:bg-blue-900"
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="mt-1.5 text-xs text-muted-foreground">
        {lang === 'he'
          ? `סעיף ${clampedCurrent} / ${totalSections}`
          : `Section ${clampedCurrent} / ${totalSections}`}
      </p>
    </div>
  );
}

const COMPLETION_MESSAGES: Record<
  LessonEngagementTrack,
  Record<Lang, string>
> = {
  '3pt': {
    he: 'כל שיעור שמסיים מקרב אותך למטרה. המשיך כך! 🌟',
    en: 'Every lesson you finish puts you closer to your goal. Keep it up! 🌟',
  },
  makhina: {
    he: 'כל שיעור מקרב אותך לאוניברסיטה. ממשיכים! 🎓',
    en: 'Every lesson brings you closer to university. Keep going! 🎓',
  },
};

export function ThreePtCompletionMessage({
  lang,
  track = '3pt',
}: {
  lang: Lang;
  track?: LessonEngagementTrack;
}) {
  return (
    <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
      {COMPLETION_MESSAGES[track][lang]}
    </p>
  );
}
