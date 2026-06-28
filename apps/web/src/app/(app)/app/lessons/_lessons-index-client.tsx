'use client';

import Link from 'next/link';
import { BookOpen } from 'lucide-react';
import { useI18n } from '@/providers/i18n-provider';
import { getLessonCountForSection } from '@/lib/lessons-by-section';
import type { CurriculumCategory } from '@/lib/curriculum-categories';

const STR = {
  he: {
    title: 'לימוד',
    subtitle: 'בחר נושא ורמה — כל שיעור מותאם אישית לרמתך',
    lessons: 'שיעורים',
    sections: 'פרקים',
    yourTrack: 'המסלול שלך',
    otherSubjects: 'נושאים נוספים',
  },
  en: {
    title: 'Learn',
    subtitle: 'Choose a subject and level — every lesson is tailored to you',
    lessons: 'lessons',
    sections: 'sections',
    yourTrack: 'Your track',
    otherSubjects: 'Other subjects',
  },
} as const;

interface Props {
  categories: CurriculumCategory[];
  primaryCategoryIds: string[];
}

export function LessonsIndexClient({ categories, primaryCategoryIds }: Props) {
  const { locale } = useI18n();
  const lang = locale === 'he' ? 'he' : 'en';
  const t = STR[lang];
  const isHe = lang === 'he';

  const primaryCats = categories.filter((c) => primaryCategoryIds.includes(c.id));
  const secondaryCats = categories.filter((c) => !primaryCategoryIds.includes(c.id));

  const renderCategory = (cat: CurriculumCategory) => {
    const label = lang === 'he' ? cat.heLabel : cat.enLabel;
    const sublabel = lang === 'he' ? cat.enLabel : cat.heLabel;
    const totalLessons = cat.sections.reduce(
      (sum, s) => sum + getLessonCountForSection(cat.id, s.id),
      0,
    );
    const sectionsWithContent = cat.sections.filter(
      (s) => getLessonCountForSection(cat.id, s.id) > 0,
    ).length;

    return (
      <Link
        key={cat.id}
        href={`/app/lessons/${cat.id}`}
        className="card-punch block rounded-2xl p-5 transition-transform hover:scale-[1.02]"
      >
        <div className="flex items-start justify-between gap-2">
          <span className="text-3xl" aria-hidden>
            {cat.emoji}
          </span>
          {totalLessons > 0 ? (
            <span className="shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
              {totalLessons} {t.lessons}
            </span>
          ) : (
            <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
              {cat.sections.length} {t.sections}
            </span>
          )}
        </div>
        <h2 className="mt-3 font-display text-base font-semibold">{label}</h2>
        <p className="mt-1 text-xs text-muted-foreground">{sublabel}</p>
        {sectionsWithContent > 0 && (
          <div className="mt-3 flex items-center gap-1 text-xs text-primary">
            <BookOpen className="h-3.5 w-3.5" aria-hidden />
            {sectionsWithContent} / {cat.sections.length} {t.sections}
          </div>
        )}
      </Link>
    );
  };

  const hasTrack = primaryCategoryIds.length > 0;

  return (
    <div dir={isHe ? 'rtl' : 'ltr'}>
      <header className="mb-8">
        <h1 className="font-display text-3xl font-bold">{t.title}</h1>
        <p className="mt-2 text-muted-foreground">{t.subtitle}</p>
      </header>

      {hasTrack ? (
        <>
          <section className="mb-8">
            <h2 className="font-display mb-4 text-sm font-semibold uppercase tracking-wide text-primary">
              {t.yourTrack}
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {primaryCats.map(renderCategory)}
            </div>
          </section>
          {secondaryCats.length > 0 && (
            <section>
              <h2 className="font-display mb-4 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                {t.otherSubjects}
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {secondaryCats.map(renderCategory)}
              </div>
            </section>
          )}
        </>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map(renderCategory)}
        </div>
      )}
    </div>
  );
}