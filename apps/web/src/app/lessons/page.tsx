import Link from 'next/link';
import type { Metadata } from 'next';
import { ArrowRight, Clock } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';
import { SiteHeader } from '@/components/site-header';
import { seedCourse, seedLessons } from '@/lib/seed-lessons';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: `${seedCourse.title} \u2014 Lessons`,
  description: seedCourse.summary,
};

export default function LessonsIndexPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10">
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-semibold tracking-tight">{seedCourse.title}</h1>
          <p className="text-muted-foreground">{seedCourse.summary}</p>
        </div>

        <div className="space-y-8">
          {seedCourse.units.map((unit) => {
            const unitLessons = unit.lesson_ids
              .map((id) => seedLessons.find((l) => l.id === id))
              .filter((l): l is (typeof seedLessons)[number] => l !== undefined);

            return (
              <section key={unit.id}>
                <h2 className="mb-3 text-xl font-semibold">{unit.title}</h2>
                <p className="mb-4 text-sm text-muted-foreground">{unit.summary}</p>
                <div className="grid gap-3 sm:grid-cols-2">
                  {unitLessons.map((lesson) => (
                    <Link
                      key={lesson.id}
                      href={`/lessons/${lesson.id}`}
                      className="group block focus-visible:outline-none"
                    >
                      <Card className="h-full transition-colors group-hover:border-primary">
                        <CardHeader className="pb-2">
                          <div className="flex items-start justify-between gap-3">
                            <CardTitle className="text-base">{lesson.title}</CardTitle>
                            <ArrowRight
                              className="h-4 w-4 flex-shrink-0 text-muted-foreground transition-transform group-hover:translate-x-1"
                              aria-hidden
                            />
                          </div>
                          <CardDescription className="flex items-center gap-3 text-xs">
                            <Badge variant="secondary">{lesson.modality}</Badge>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" aria-hidden />
                              {lesson.est_minutes} min
                            </span>
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="text-sm text-muted-foreground">
                          {lesson.objectives[0]?.statement}
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </main>
      <footer className="border-t border-border py-8 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} A Step Forward
      </footer>
    </div>
  );
}
