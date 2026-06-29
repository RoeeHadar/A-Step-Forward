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
import { LessonCompleteButton } from '@/components/lesson-complete-button';
import type { Lesson } from '@asf/schemas/curriculum';
import 'katex/dist/katex.min.css';

/** Renders legacy OpenStax seed lessons that are not yet in Neon. */
export async function LegacySeedLessonView({ lesson }: { lesson: Lesson }) {
  const cookieStore = await cookies();
  const locale = cookieStore.get('asf-locale')?.value === 'en' ? 'en' : 'he';
  const isHe = locale === 'he';
  return (
    <div className="max-w-3xl">
      <PageHeader title={lesson.title} backHref="/app/lessons" />
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

      <LessonCompleteButton conceptId={lesson.id} locale={locale} variant="outline" />
      <Button asChild>
        <Link href="/app/chat/tutor">
          <MessageSquare className="h-4 w-4" aria-hidden />
          {isHe ? 'שוחח עם המורה' : 'Discuss with Tutor'}
        </Link>
      </Button>
    </div>
  );
}
