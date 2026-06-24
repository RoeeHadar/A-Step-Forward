import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { ArrowLeft, BookOpen, Clock, MessageSquare } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { SiteHeader } from '@/components/site-header';
import { fetchLessonPublic } from '@/lib/data';
import { listSeedLessonIds, seedCourse } from '@/lib/seed-lessons';
import 'katex/dist/katex.min.css';

export const dynamic = 'force-dynamic';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lessonId: string }>;
}): Promise<Metadata> {
  const { lessonId } = await params;
  const lesson = await fetchLessonPublic(lessonId);
  if (!lesson) return { title: 'Lesson not found' };
  return {
    title: lesson.title,
    description: `${seedCourse.title} \u2014 ${lesson.title}`,
  };
}

export function generateStaticParams() {
  return listSeedLessonIds().map((lessonId) => ({ lessonId }));
}

export default async function PublicLessonPage({
  params,
}: {
  params: Promise<{ lessonId: string }>;
}) {
  const { lessonId } = await params;
  const lesson = await fetchLessonPublic(lessonId);
  if (!lesson) notFound();

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8">
        <div className="mb-6">
          <Button variant="ghost" size="sm" className="px-0" asChild>
            <Link href="/lessons">
              <ArrowLeft className="h-4 w-4" aria-hidden />
              All lessons
            </Link>
          </Button>
        </div>

        <h1 className="mb-3 text-3xl font-semibold tracking-tight">{lesson.title}</h1>
        <div className="mb-6 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          <Badge variant="secondary">{lesson.modality}</Badge>
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" aria-hidden />
            {lesson.est_minutes} min
          </span>
          <span className="flex items-center gap-1">
            <BookOpen className="h-4 w-4" aria-hidden />
            {seedCourse.title}
          </span>
        </div>

        <Card className="mb-8">
          <CardContent className="prose prose-neutral dark:prose-invert max-w-none pt-6">
            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeKatex]}>
              {lesson.body_md}
            </ReactMarkdown>
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

        <div className="flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/sign-up">
              <MessageSquare className="h-4 w-4" aria-hidden />
              Sign up to discuss with Tutor
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/lessons">Browse more lessons</Link>
          </Button>
        </div>
      </main>
      <footer className="border-t border-border py-8 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} A Step Forward
      </footer>
    </div>
  );
}
