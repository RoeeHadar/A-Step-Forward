'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import type { LessonWithQuestions, LessonPointsLevel } from '@/lib/neon-db';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import { LessonReader } from './lesson-reader';
import { LessonQuizPanel } from './lesson-quiz-panel';
import { LessonCompleteButton } from './lesson-complete-button';
import {
  ThreePtCompletionMessage,
  ThreePtProgressBar,
  getLessonEngagementTrack,
} from './three-pt-lesson-engagement';

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
  const pathname = usePathname();
  const [lang, setLang] = useLanguagePreference('he');
  const [currentSection, setCurrentSection] = useState(1);
  const [showMotivation, setShowMotivation] = useState(false);

  const subjectFromPath =
    pathname.match(/\/learn\/([^/]+)/)?.[1] ??
    pathname.match(/\/app\/lessons\/([^/]+)/)?.[1] ??
    null;

  const engagementTrack = getLessonEngagementTrack({
    pathname,
    subject: subjectFromPath,
    levelMin: data.lesson.level,
    mathTrack: data.lesson.math_track,
    learnerLevel: learnerLevel ?? null,
  });
  const showEngagement = engagementTrack !== null;

  const totalSections = data.lesson.sections.length;

  return (
    <div className="space-y-2">
      {showEngagement ? (
        <ThreePtProgressBar
          currentSection={currentSection}
          totalSections={totalSections}
          lang={lang}
        />
      ) : null}
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

      <LessonReader
        data={data}
        lang={lang}
        learnerLevel={learnerLevel}
        onSectionFocus={showEngagement ? setCurrentSection : undefined}
      />
      <LessonQuizPanel data={data} lang={lang} conceptId={conceptId} learnerLevel={learnerLevel} />

      <div className="mt-8 flex flex-col gap-3 border-t border-border/60 pt-8">
        <div className="flex flex-wrap gap-3">
          <LessonCompleteButton
            conceptId={conceptId}
            lessonId={data.lesson.id}
            locale={lang}
            navigateOnComplete={!showEngagement}
            onComplete={
              showEngagement
                ? () => {
                    setShowMotivation(true);
                  }
                : undefined
            }
          />
          <Link
            href="/app"
            className="inline-flex rounded-lg border border-border bg-surface-1/50 px-5 py-2.5 text-sm font-medium hover:border-primary/40"
          >
            {lang === 'he' ? 'חזרה ללוח הבקרה' : 'Back to Dashboard'}
          </Link>
        </div>
        {showEngagement && showMotivation && engagementTrack ? (
          <ThreePtCompletionMessage lang={lang} track={engagementTrack} />
        ) : null}
      </div>
    </div>
  );
}
