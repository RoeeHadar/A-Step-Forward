import Link from 'next/link';
import { notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { PremiumBadge } from '@/components/premium-badge';
import { fetchBagrutExams, fetchSections, fetchSubjects } from '@/lib/content-api';
import { subjectLabel } from '@/lib/subject-labels';
import { SubjectSectionsClient } from '@/components/subject-sections-client';
import { getResourcesForSubject } from '@/lib/external-resources';
import { fetchConceptsWithExplanations } from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';

export const dynamic = 'force-dynamic';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
}
const kgConcepts: KgConcept[] = (kg as { concepts: KgConcept[] }).concepts;

function subjectMatchesConcept(uiSubject: string, kgSubject: string): boolean {
  if (uiSubject === kgSubject) return true;
  // /learn/math card should include concepts tagged in kg as 'math' across levels
  if (uiSubject === 'math' && kgSubject === 'math') return true;
  if (uiSubject === 'physics' && kgSubject === 'physics') return true;
  if (uiSubject === 'calculus' && kgSubject === 'math') return true;
  if (uiSubject === 'linear_algebra' && kgSubject === 'math') return true;
  return false;
}

export default async function SubjectPage({ params }: { params: Promise<{ subject: string }> }) {
  const { subject } = await params;
  const allSubjects = await fetchSubjects();
  const known = allSubjects.some((s) => s.subject === subject);
  const conceptsForSubject = kgConcepts.filter((c) =>
    subjectMatchesConcept(subject, c.subject),
  );
  const [sections, bagrut, external, coverage] = await Promise.all([
    fetchSections(subject),
    fetchBagrutExams(subject),
    getResourcesForSubject(subject),
    fetchConceptsWithExplanations(conceptsForSubject.map((c) => c.id)),
  ]);

  const conceptsWithCoverage = conceptsForSubject
    .map((c) => ({ ...c, langs: coverage.get(c.id) ?? [] }))
    .sort((a, b) => b.langs.length - a.langs.length || a.name.localeCompare(b.name));

  if (
    !known &&
    sections.length === 0 &&
    bagrut.length === 0 &&
    external.length === 0 &&
    conceptsWithCoverage.length === 0
  ) {
    notFound();
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">
            Learn
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{subjectLabel(subject, 'en')}</span>
        </nav>

        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold">{subjectLabel(subject, 'en')}</h1>
            <p className="mt-1 text-muted-foreground" dir="rtl">
              {subjectLabel(subject, 'he')}
            </p>
          </div>
          {bagrut.length > 0 ? (
            <Link
              href={`/learn/${subject}/bagrut`}
              className="rounded-lg border border-border bg-surface-1/50 px-4 py-2 text-sm font-medium hover:border-primary/40"
            >
              Bagrut Exams ({bagrut.length})
            </Link>
          ) : null}
        </header>

        <div className="mb-8 glass-surface rounded-2xl border border-accent-amber/20 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-foreground">Chat with the Tutor about this</h2>
                <PremiumBadge />
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                Ask questions about any section — currently free for all users.
              </p>
            </div>
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(subject)}`}
              className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              Open Tutor Chat
            </Link>
          </div>
        </div>

        <SubjectSectionsClient subject={subject} sections={sections} />

        {conceptsWithCoverage.length > 0 ? (
          <section className="mt-10">
            <h2 className="font-display text-xl font-semibold text-foreground">
              Concept explanations
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              In-house, bilingual explanations of every concept in this subject — adapted from
              open educational sources, rendered natively here with full attribution.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {conceptsWithCoverage.map((c) => {
                const hasContent = c.langs.length > 0;
                return (
                  <Link
                    key={c.id}
                    href={`/learn/${subject}/concept/${c.id}`}
                    className="glass-surface group rounded-xl border-border/60 p-4 transition-all hover:border-primary/40"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <h3 className="font-medium text-foreground group-hover:text-primary">
                        {c.name}
                      </h3>
                      {hasContent ? (
                        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium uppercase text-primary">
                          {c.langs.includes('he') && c.langs.includes('en')
                            ? 'EN · HE'
                            : c.langs[0]?.toUpperCase()}
                        </span>
                      ) : (
                        <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
                          Soon
                        </span>
                      )}
                    </div>
                    {c.name_he ? (
                      <p className="mt-1 text-sm text-muted-foreground" dir="rtl">
                        {c.name_he}
                      </p>
                    ) : null}
                  </Link>
                );
              })}
            </div>
          </section>
        ) : null}

        {external.length > 0 ? (
          <section className="mt-10">
            <h3 className="font-display text-lg font-semibold text-foreground">
              Reference textbooks &amp; courses
            </h3>
            <p className="mt-1 text-sm text-muted-foreground">
              For deeper study, these long-form open courses pair well with the concept
              explanations above. External links — opens in a new tab.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {external.map((r) => (
                <a
                  key={r.url}
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="glass-surface group rounded-xl border-border/60 p-4 transition-all hover:border-primary/40"
                  dir={r.language === 'he' ? 'rtl' : 'ltr'}
                >
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-medium text-foreground group-hover:text-primary">
                      {r.title}
                    </h3>
                    <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
                      {r.source}
                    </span>
                  </div>
                  {r.description ? (
                    <p className="mt-1.5 text-sm text-muted-foreground">{r.description}</p>
                  ) : null}
                </a>
              ))}
            </div>
          </section>
        ) : null}
      </main>
    </div>
  );
}
