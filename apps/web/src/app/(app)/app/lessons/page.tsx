'use client';

import Link from 'next/link';
import { useI18n } from '@/providers/i18n-provider';
import { CURRICULUM_CATEGORIES, type CurriculumCategory } from '@/lib/curriculum-categories';

export default function LessonsPage() {
  const { messages, locale } = useI18n();
  const t = messages.lessons;

  return (
    <div>
      <h1 className="font-display text-3xl font-bold">{t.title}</h1>
      <p className="mt-2 text-muted-foreground">{t.pickCategory}</p>
      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {CURRICULUM_CATEGORIES.map((cat) => (
          <CategoryCard key={cat.id} cat={cat} locale={locale} t={t} />
        ))}
      </div>
    </div>
  );
}

function CategoryCard({
  cat,
  locale,
  t,
}: {
  cat: CurriculumCategory;
  locale: string;
  t: { sections: string; browse: string };
}) {
  const label = locale === 'he' ? cat.heLabel : cat.enLabel;
  const sublabel = locale === 'he' ? cat.enLabel : cat.heLabel;

  return (
    <Link href={`/app/lessons/${cat.id}`} className="card-punch block rounded-2xl p-5 transition-transform hover:scale-[1.02]">
      <div className="mb-3 inline-flex rounded-full bg-gradient-to-br from-primary/10 to-accent-cyan/10 p-3">
        <span className="text-2xl" aria-hidden>
          {cat.emoji}
        </span>
      </div>
      <h2 className="font-display text-base font-semibold leading-tight">{label}</h2>
      <p className="mt-1 text-xs text-muted-foreground">{sublabel}</p>
      <div className="mt-3 flex items-center justify-between">
        <span className="rounded-full glass-surface px-2 py-0.5 text-xs text-muted-foreground">
          {cat.sections.length} {t.sections}
        </span>
        <span className="text-xs font-medium text-primary">{t.browse} ›</span>
      </div>
    </Link>
  );
}
