'use client';

import Link from 'next/link';
import { MarkdownMath } from '@/components/markdown-math';
import { Clock, MessageSquare } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import {
  InteractiveSeedQuestions,
  type InteractiveSeedQuestion,
} from '@/components/interactive-seed-questions';

export type InteractiveSeedSection = {
  id: string;
  title_en: string;
  title_he: string;
  body_en_md?: string;
  body_he_md?: string;
  body_en?: string;
  body_he?: string;
};

export type InteractiveSeedLesson = {
  id: string;
  title_en: string;
  title_he: string;
  duration_min?: number;
  est_minutes?: number;
  sections?: InteractiveSeedSection[];
  questions?: InteractiveSeedQuestion[];
};

/** Renders AI-authored interactive seed lessons (JSON with sections + open/mcq questions). */
export function InteractiveSeedLessonView({
  lesson,
  locale,
}: {
  lesson: InteractiveSeedLesson;
  locale: 'he' | 'en';
}) {
  const isHe = locale === 'he';
  const dir = isHe ? 'rtl' : 'ltr';
  const title = isHe ? lesson.title_he : lesson.title_en;
  const minutes = lesson.duration_min ?? lesson.est_minutes ?? 20;
  const sections = lesson.sections ?? [];
  const questions = lesson.questions ?? [];

  return (
    <div className="max-w-3xl">
      <PageHeader title={title} backHref="/app/lessons" />

      <div className="mb-6 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <Badge variant="secondary">{isHe ? 'אינטראקטיבי' : 'interactive'}</Badge>
        <span className="flex items-center gap-1">
          <Clock className="h-4 w-4" aria-hidden />
          {minutes} min
        </span>
      </div>

      {sections.map((section) => {
        const secTitle = isHe ? section.title_he : section.title_en;
        const body =
          isHe
            ? section.body_he_md ?? section.body_he ?? ''
            : section.body_en_md ?? section.body_en ?? '';
        return (
          <Card key={section.id} className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">{secTitle}</CardTitle>
            </CardHeader>
            <CardContent dir={dir}>
              <MarkdownMath className="prose-neutral">{body}</MarkdownMath>
            </CardContent>
          </Card>
        );
      })}

      {questions.length > 0 ? (
        <InteractiveSeedQuestions questions={questions} lang={locale} />
      ) : null}

      <div className="mt-8 flex flex-wrap gap-3">
        <Button asChild variant="outline">
          <Link href="/app/chat/tutor">
            <MessageSquare className="h-4 w-4" aria-hidden />
            {isHe ? 'שוחח עם המורה' : 'Discuss with Tutor'}
          </Link>
        </Button>
      </div>
    </div>
  );
}
