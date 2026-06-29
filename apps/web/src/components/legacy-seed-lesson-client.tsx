'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { Clock, MessageSquare } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import { LessonCompleteButton } from '@/components/lesson-complete-button';
import {
  ThreePtCompletionMessage,
  ThreePtProgressBar,
  isThreePtLessonContext,
} from '@/components/three-pt-lesson-engagement';
import type { Lesson } from '@asf/schemas/curriculum';
import 'katex/dist/katex.min.css';

type LegacySeedLessonClientProps = {
  lesson: Lesson;
  locale: 'he' | 'en';
  sectionCount: number;
  levelMin?: string | null;
  mathTrack?: string[];
};

export function LegacySeedLessonClient({
  lesson,
  locale,
  sectionCount,
  levelMin,
  mathTrack,
}: LegacySeedLessonClientProps) {
  const pathname = usePathname();
  const isHe = locale === 'he';
  const [showMotivation, setShowMotivation] = useState(false);
  const is3pt = isThreePtLessonContext({ pathname, levelMin, mathTrack });

  return (
    <div className="max-w-3xl">
      <PageHeader title={lesson.title} backHref="/app/lessons" />
      {is3pt ? (
        <ThreePtProgressBar
          currentSection={1}
          totalSections={Math.max(sectionCount, 1)}
          lang={locale}
        />
      ) : null}
      <div className="mb-6 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <Badge variant="secondary">{lesson.modality}</Badge>
        <span className="flex items-center gap-1">
          <Clock className="h-4 w-4" aria-hidden />
          {lesson.est_minutes} min
        </span>
      </div>

      <Card className="mb-8">
        <CardContent className="prose prose-neutral dark:prose-invert max-w-none pt-6">
          {lesson.body_md.trim().length === 0 ? (
            <div className="not-prose space-y-2 text-muted-foreground">
              <p className="text-base font-medium text-foreground">Lesson coming soon</p>
              <p className="text-sm">
                We&apos;re still putting this lesson together. In the meantime, ask the Tutor below
                to walk you through the topic.
              </p>
            </div>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeKatex]}>
              {lesson.body_md}
            </ReactMarkdown>
          )}
        </CardContent>
      </Card>

      {lesson.objectives.length > 0 ? (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-lg">Learning objectives</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-inside list-disc space-y-2">
              {lesson.objectives.map((obj) => (
                <li key={obj.id}>{obj.statement}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ) : null}

      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap gap-3">
          <LessonCompleteButton
            conceptId={lesson.id}
            locale={locale}
            variant="outline"
            navigateOnComplete={!is3pt}
            onComplete={is3pt ? () => setShowMotivation(true) : undefined}
          />
          <Button asChild>
            <Link href="/app/chat/tutor">
              <MessageSquare className="h-4 w-4" aria-hidden />
              {isHe ? 'שוחח עם המורה' : 'Discuss with Tutor'}
            </Link>
          </Button>
        </div>
        {is3pt && showMotivation ? <ThreePtCompletionMessage lang={locale} /> : null}
      </div>
    </div>
  );
}