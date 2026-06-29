'use client';

type Lang = 'en' | 'he';

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

export function ThreePtCompletionMessage({ lang }: { lang: Lang }) {
  return (
    <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
      {lang === 'he'
        ? 'כל שיעור שמסיים מקרב אותך למטרה. המשיך כך! 🌟'
        : 'Every lesson you finish puts you closer to your goal. Keep it up! 🌟'}
    </p>
  );
}

export function isThreePtLessonContext({
  pathname,
  levelMin,
  mathTrack,
  learnerLevel,
}: {
  pathname: string;
  levelMin?: string | null;
  mathTrack?: string[];
  learnerLevel?: string | null;
}): boolean {
  if (pathname.includes('3pt')) return true;
  if (levelMin === '3pt') return true;
  if (learnerLevel === '3pt') return true;
  if (mathTrack?.includes('3pt')) return true;
  return false;
}