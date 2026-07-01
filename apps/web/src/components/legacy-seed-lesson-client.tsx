'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MarkdownMath } from '@/components/markdown-math';
import { Clock, MessageSquare } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import { LessonCompleteButton } from '@/components/lesson-complete-button';
import {
  ThreePtCompletionMessage,
  ThreePtProgressBar,
  getLessonEngagementTrack,
} from '@/components/three-pt-lesson-engagement';
import type { Lesson } from '@asf/schemas/curriculum';

type LegacySeedLessonClientProps = {
  lesson: Lesson;
  locale: 'he' | 'en';
  sectionCount: number;
  levelMin?: string | null;
  mathTrack?: string[];
  subject?: string | null;
};

export function LegacySeedLessonClient({
  lesson,
  locale,
  sectionCount,
  levelMin,
  mathTrack,
  subject,
}: LegacySeedLessonClientProps) {
  const pathname = usePathname();
  const isHe = locale === 'he';
  const [showMotivation, setShowMotivation] = useState(false);
  const engagementTrack = getLessonEngagementTrack({
    pathname,
    subject,
    levelMin,
    mathTrack,
  });
  const showEngagement = engagementTrack !== null;

  return (
    <div className="max-w-3xl">
      <PageHeader title={lesson.title} backHref="/app/lessons" />
      {showEngagement ? (
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
        <CardContent className="pt-6">
          {lesson.body_md.trim().length === 0 ? (
            <div className="not-prose space-y-2 text-muted-foreground">
              <p className="text-base font-medium text-foreground">Lesson coming soon</p>
              <p className="text-sm">
                We&apos;re still putting this lesson together. In the meantime, ask the Tutor below
                to walk you through the topic.
              </p>
            </div>
          ) : (
            <MarkdownMath className="prose-neutral">{lesson.body_md}</MarkdownMath>
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
            navigateOnComplete={!showEngagement}
            onComplete={showEngagement ? () => setShowMotivation(true) : undefined}
          />
          <Button asChild>
            <Link href="/app/chat/tutor">
              <MessageSquare className="h-4 w-4" aria-hidden />
              {isHe ? 'שוחח עם המורה' : 'Discuss with Tutor'}
            </Link>
          </Button>
        </div>
        {showEngagement && showMotivation && engagementTrack ? (
          <ThreePtCompletionMessage lang={locale} track={engagementTrack} />
        ) : null}
      </div>
    </div>
  );
}