'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useI18n } from '@/providers/i18n-provider';
import type { BagrutExam } from '@/lib/content-api';
import { subjectLabel } from '@/lib/subject-labels';

export function BagrutPageClient({
  subject,
  exams,
}: {
  subject: string;
  exams: BagrutExam[];
}) {
  const { locale, messages } = useI18n();
  const isHe = locale === 'he';
  const t = messages.learn;
  const [selected, setSelected] = useState<BagrutExam | null>(exams[0] ?? null);
  const examHeading = t.bagrutExams.replace('{count}', String(exams.length));

  return (
    <div className="bg-background">
      <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-10 lg:flex-row">
        <div className="lg:w-80 shrink-0" dir={isHe ? 'rtl' : 'ltr'}>
          <nav className="mb-4 text-sm text-muted-foreground">
            <Link href="/learn" className="hover:text-foreground">
              {t.learn}
            </Link>
            <span className="mx-2">/</span>
            <Link href={`/learn/${subject}`} className="hover:text-foreground">
              {subjectLabel(subject, locale)}
            </Link>
            <span className="mx-2">/</span>
            <span className="text-foreground">{examHeading}</span>
          </nav>
          <h1 className="font-display text-2xl font-bold">{examHeading}</h1>
          <ul className="mt-4 space-y-2">
            {exams.map((exam) => (
              <li key={exam.id}>
                <button
                  type="button"
                  onClick={() => setSelected(exam)}
                  className={`w-full rounded-lg border px-3 py-2 text-start text-sm transition-colors ${
                    selected?.id === exam.id
                      ? 'border-primary bg-primary/10 text-foreground'
                      : 'border-border bg-surface-1/40 text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <span className="font-medium">{exam.display_name}</span>
                  <span className="mt-1 flex flex-wrap gap-1">
                    {exam.year ? (
                      <span className="rounded bg-surface-2 px-1.5 py-0.5 text-xs">{exam.year}</span>
                    ) : null}
                    <span className="rounded bg-surface-2 px-1.5 py-0.5 text-xs">{exam.exam_type}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="glass-surface min-h-[70vh] flex-1 overflow-hidden rounded-2xl">
          {selected ? (
            <iframe
              src={selected.file_url}
              title={selected.display_name}
              className="h-[70vh] w-full border-0"
            />
          ) : (
            <p className="p-8 text-muted-foreground" dir={isHe ? 'rtl' : 'ltr'}>
              {isHe ? 'בחרו מבחן כדי לפתוח את ה-PDF.' : 'Select an exam to view the PDF.'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
