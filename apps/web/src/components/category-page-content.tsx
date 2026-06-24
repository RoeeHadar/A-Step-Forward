'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { useI18n } from '@/providers/i18n-provider';
import type { CurriculumCategory } from '@/lib/curriculum-categories';

export function CategoryPageContent({ category }: { category: CurriculumCategory }) {
  const { messages, locale } = useI18n();
  const t = messages.lessons;
  const label = locale === 'he' ? category.heLabel : category.enLabel;
  const sublabel = locale === 'he' ? category.enLabel : category.heLabel;

  return (
    <div>
      <Link
        href="/app/lessons"
        className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
        {t.backToCategories}
      </Link>
      <div className="mb-2 flex items-center gap-3">
        <div className="inline-flex rounded-full bg-gradient-to-br from-primary/10 to-accent-cyan/10 p-3">
          <span className="text-3xl" aria-hidden>
            {category.emoji}
          </span>
        </div>
        <h1 className="font-display text-3xl font-bold">{label}</h1>
      </div>
      <p className="mb-8 text-muted-foreground">{sublabel}</p>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {category.sections.map((section) => {
          const sectionLabel = locale === 'he' ? section.heLabel : section.enLabel;
          const sectionSublabel = locale === 'he' ? section.enLabel : section.heLabel;
          return (
            <Link
              key={section.id}
              href={`/app/lessons/${category.id}/${section.id}`}
              className="card-punch block rounded-2xl p-5 transition-transform hover:scale-[1.02]"
            >
              <h2 className="font-display text-base font-semibold">{sectionLabel}</h2>
              <p className="mt-1 text-xs text-muted-foreground">{sectionSublabel}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
