import Link from 'next/link';
import { redirect } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { Clock, MessageSquare } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import { getAuthContext } from '@/lib/auth';
import { fetchLesson } from '@/lib/data';
import 'katex/dist/katex.min.css';

export default async function LessonPage({ params }: { params: Promise<{ lessonId: string }> }) {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const { lessonId } = await params;
  const lesson = await fetchLesson(auth, lessonId);

  return (
    <div className="max-w-3xl">
      <PageHeader title={lesson.title} backHref="/app" />
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
                We&apos;re still putting this lesson together. In the meantime, ask the Tutor below to
                walk you through the topic.
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

      <Button asChild>
        <Link href="/app/chat/tutor">
          <MessageSquare className="h-4 w-4" aria-hidden />
          Discuss with Tutor
        </Link>
      </Button>
    </div>
  );
}
