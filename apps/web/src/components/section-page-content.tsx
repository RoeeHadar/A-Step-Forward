'use client';

import Link from 'next/link';
import { ArrowLeft, Brain, Clock } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';
import type { CurriculumCategory, CurriculumSection } from '@/lib/curriculum-categories';
import type { LessonSummary } from '@/lib/lessons-by-section';

export function SectionPageContent({
  category,
  section,
  lessons,
}: {
  category: CurriculumCategory;
  section: CurriculumSection;
  lessons: LessonSummary[];
}) {
  const { messages, locale } = useI18n();
  const t = messages.lessons;
  const dashboard = messages.dashboard;
  const categoryLabel = locale === 'he' ? category.heLabel : category.enLabel;
  const sectionLabel = locale === 'he' ? section.heLabel : section.enLabel;
  const sectionSublabel = locale === 'he' ? section.enLabel : section.heLabel;

  return (
    <div>
      <Link
        href={`/app/lessons/${category.id}`}
        className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
        {t.backTo} {categoryLabel}
      </Link>
      <h1 className="font-display text-3xl font-bold">{sectionLabel}</h1>
      <p className="mb-8 text-muted-foreground">{sectionSublabel}</p>

      {lessons.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {lessons.map((lesson) => (
            <div key={lesson.id} className="iridescent-border flex flex-col p-5">
              <h2 className="font-display text-base font-semibold">{lesson.title}</h2>
              <p className="mt-2 flex items-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" aria-hidden />
                {lesson.est_minutes} {dashboard.minutes}
              </p>
              <Link
                href={`/app/lessons/l/${lesson.id}`}
                className="mt-4 text-sm font-medium text-primary transition-colors hover:text-primary/80"
              >
                {t.startLesson} →
              </Link>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-punch rounded-2xl p-8 text-center sm:p-12">
          <p className="font-display text-xl font-bold sm:text-2xl">{sectionLabel}</p>
          <div className="mx-auto mt-6 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-primary/15 to-accent-cyan/15">
            <Brain className="h-7 w-7 text-primary" aria-hidden />
          </div>
          <p className="font-display mt-4 text-lg font-semibold">{t.comingSoonHeading}</p>
          <Button asChild className="mt-6">
            <Link href={`/app/chat/tutor?topic=${encodeURIComponent(section.id)}`}>
              {t.comingSoonCta}
            </Link>
          </Button>
        </div>
      )}
    </div>
  );
}
