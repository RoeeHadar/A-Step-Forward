import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { Badge } from '@asf/ui/badge';
import { SiteHeader } from '@/components/site-header';
import { fetchSubjects } from '@/lib/content-api';
import { subjectIcon, subjectLabel } from '@/lib/subject-labels';

export const dynamic = 'force-dynamic';

export default async function LearnPage() {
  const subjects = await fetchSubjects();

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10">
        <header className="mb-8">
          <h1 className="font-display text-3xl font-bold text-foreground">Free Content</h1>
          <p className="mt-2 text-muted-foreground">
            Free textbooks, practice materials, and Bagrut exams — browse without signing in.
          </p>
        </header>

        {subjects.length === 0 ? (
          <Card className="glass-surface">
            <CardContent className="p-8 text-center text-muted-foreground">
              <p>
                Content is being prepared. Run <code className="text-foreground">make ingest</code> locally to load
                the Learning Database.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {subjects.map((s) => (
              <Link key={s.subject} href={`/learn/${s.subject}`} className="group block">
                <Card className="glass-surface transition-all hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-3">
                      <span className="text-3xl" aria-hidden>{subjectIcon(s.subject)}</span>
                      <Badge variant="secondary">{s.section_count} sections</Badge>
                    </div>
                    <CardTitle className="group-hover:text-primary">{subjectLabel(s.subject, 'en')}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground" dir="rtl">
                      {subjectLabel(s.subject, 'he')}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
