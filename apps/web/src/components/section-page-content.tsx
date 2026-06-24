'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { useI18n } from '@/providers/i18n-provider';
import type { CurriculumCategory, CurriculumSection } from '@/lib/curriculum-categories';

export function SectionPageContent({
  category,
  section,
}: {
  category: CurriculumCategory;
  section: CurriculumSection;
}) {
  const { messages, locale } = useI18n();
  const t = messages.lessons;
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
      <div className="card-punch rounded-2xl border border-dashed p-12 text-center">
        <p className="mb-2 text-2xl" aria-hidden>
          🚧
        </p>
        <p className="font-display text-lg font-semibold">{t.comingSoonTitle}</p>
        <p className="mt-1 text-sm text-muted-foreground">{t.comingSoon}</p>
      </div>
    </div>
  );
}
