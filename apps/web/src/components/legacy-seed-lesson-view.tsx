import Link from 'next/link';
import { cookies } from 'next/headers';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { Clock, MessageSquare } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import type { InteractiveSeedLesson } from '@/components/interactive-seed-lesson-view';
import { InteractiveSeedLessonView } from '@/components/interactive-seed-lesson-view';
import 'katex/dist/katex.min.css';
import {
  LegacySeedProgressBar,
  LegacySeedCompleteArea,
} from '@/components/legacy-seed-lesson-engagement';

/** Renders legacy OpenStax seed lessons that are not yet in Neon. */
export async function LegacySeedLessonView({
  lesson,
  interactiveLesson,
  locale: localeProp,
}: {
  lesson?: import('@asf/schemas/curriculum').Lesson;
  interactiveLesson?: InteractiveSeedLesson;
  locale?: 'he' | 'en';
}) {
  const cookieStore = await cookies();
  const locale = localeProp ?? (cookieStore.get('asf-locale')?.value === 'en' ? 'en' : 'he');

  if (interactiveLesson) {
    return <InteractiveSeedLessonView lesson={interactiveLesson} locale={locale} />;
  }

  if (!lesson) {
    return null;
  }
  const isHe = locale === 'he';

  // Use learning-objectives count as the "section" metric for the progress bar.
  const totalTopics = lesson.objectives.length || 1;

  return (
    <div className="max-w-3xl">
      <PageHeader title={lesson.title} backHref="/app/lessons" />

      {/* Subtle reading-progress bar for every legacy lesson */}
      <LegacySeedProgressBar totalTopics={totalTopics} locale={locale} />

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

      {/* Complete button with post-completion motivational message */}
      <div className="flex flex-wrap items-start gap-3">
        <LegacySeedCompleteArea conceptId={lesson.id} locale={locale} />
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
