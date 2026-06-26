'use client';

import type { LessonWithQuestions } from '@/lib/neon-db';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import { LessonReader } from './lesson-reader';
import { LessonQuizPanel } from './lesson-quiz-panel';

export function LessonPageClient({
  data,
  conceptId,
}: {
  data: LessonWithQuestions;
  conceptId: string;
}) {
  // Default Hebrew — see hooks/use-language-preference.ts for rationale.
  const [lang, setLang] = useLanguagePreference('he');

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3">
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
        <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
          AI-authored · {data.lesson.author}
        </span>
      </div>

      <LessonReader data={data} lang={lang} />
      <LessonQuizPanel data={data} lang={lang} conceptId={conceptId} />
    </div>
  );
}
