'use client';

import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import type { LessonWithQuestions, LessonPointsLevel } from '@/lib/neon-db';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import { LessonReader } from './lesson-reader';
import { LessonQuizPanel } from './lesson-quiz-panel';
import { LessonCompleteButton } from './lesson-complete-button';

const MATH_TRACK_LEVELS: LessonPointsLevel[] = ['3pt', '4pt', '5pt'];

function levelLabel(level: LessonPointsLevel, isHe: boolean): string {
  const n = level.replace('pt', '');
  return isHe ? `${n} יח'` : `${n}-pt`;
}

function LessonLevelToggle({
  tracks,
  activeLevel,
}: {
  tracks: string[];
  activeLevel: LessonPointsLevel | null;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [locale] = useLanguagePreference();
  const isHe = locale === 'he';

  const options = MATH_TRACK_LEVELS.filter((level) => tracks.includes(level));
  if (options.length <= 1) return null;

  const current = activeLevel && options.includes(activeLevel) ? activeLevel : options[0];

  function selectLevel(level: LessonPointsLevel) {
    const params = new URLSearchParams(searchParams.toString());
    params.set('level', level);
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
  }

  return (
    <div className="inline-flex rounded-full border border-border bg-surface-1/50 p-1">
      {options.map((level) => (
        <button
          key={level}
          type="button"
          onClick={() => selectLevel(level)}
          className={`rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
            current === level
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          {levelLabel(level, isHe)}
        </button>
      ))}
    </div>
  );
}

export function LessonPageClient({
  data,
  conceptId,
  learnerLevel,
}: {
  data: LessonWithQuestions;
  conceptId: string;
  learnerLevel?: LessonPointsLevel | null;
}) {
  const [lang, setLang] = useLanguagePreference('he');

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-full border border-border bg-surface-1/50 p-1">
            <button
              type="button"
              onClick={() => setLang('en')}
              className={`rounded-full px-4 py-1.5 text-xs font-semibold transition-colors ${
                lang === 'en'
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => setLang('he')}
              className={`rounded-full px-4 py-1.5 text-xs font-semibold transition-colors ${
                lang === 'he'
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              עברית
            </button>
          </div>
          <LessonLevelToggle tracks={data.lesson.math_track} activeLevel={learnerLevel ?? null} />
        </div>
        <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
          AI-authored · {data.lesson.author}
        </span>
      </div>

      <LessonReader data={data} lang={lang} learnerLevel={learnerLevel} />
      <LessonQuizPanel data={data} lang={lang} conceptId={conceptId} learnerLevel={learnerLevel} />

      <div className="mt-8 flex flex-wrap gap-3 border-t border-border/60 pt-8">
        <LessonCompleteButton
          conceptId={conceptId}
          lessonId={data.lesson.id}
          locale={lang}
        />
        <Link
          href="/app"
          className="inline-flex rounded-lg border border-border bg-surface-1/50 px-5 py-2.5 text-sm font-medium hover:border-primary/40"
        >
          {lang === 'he' ? 'חזרה ללוח הבקרה' : 'Back to Dashboard'}
        </Link>
      </div>
    </div>
  );
}
