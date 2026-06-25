import Link from 'next/link';
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
          <h1 className="font-display text-3xl font-bold text-foreground">Learn</h1>
          <p className="mt-2 text-muted-foreground">
            Free textbooks, practice materials, and Bagrut exams — browse without signing in.
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {subjects.map((s) => (
            <Link
              key={s.subject}
              href={`/learn/${s.subject}`}
              className="glass-surface group rounded-2xl p-5 transition-all hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10"
            >
              <div className="flex items-start justify-between gap-3">
                <span className="text-3xl" aria-hidden>
                  {subjectIcon(s.subject)}
                </span>
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  {s.section_count > 0
                    ? `${s.section_count} sections`
                    : 'Curated resources'}
                </span>
              </div>
              <h2 className="mt-3 font-display text-lg font-semibold text-foreground group-hover:text-primary">
                {subjectLabel(s.subject, 'en')}
              </h2>
              <p className="mt-1 text-sm text-muted-foreground" dir="rtl">
                {subjectLabel(s.subject, 'he')}
              </p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
