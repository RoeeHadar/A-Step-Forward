import Link from 'next/link';
import { notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { subjectLabel } from '@/lib/subject-labels';
import {
  dbConfigured,
  fetchConceptExplanation,
  fetchConceptExplanationFallback,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';
import { ConceptContentClient } from '@/components/concept-content-client';

export const dynamic = 'force-dynamic';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  prerequisites: string[];
}

const kgById: Record<string, KgConcept> = Object.fromEntries(
  ((kg as { concepts: KgConcept[] }).concepts).map((c) => [c.id, c]),
);

export default async function ConceptPage({
  params,
}: {
  params: Promise<{ subject: string; conceptId: string }>;
}) {
  const { subject, conceptId } = await params;
  const concept = kgById[conceptId];

  // Try both languages in parallel; if neither has content yet, render a
  // graceful placeholder pointing to the source.
  const [en, he] = await Promise.all([
    fetchConceptExplanation(conceptId, 'en'),
    fetchConceptExplanation(conceptId, 'he'),
  ]);

  const fallback = !en && !he ? await fetchConceptExplanationFallback(conceptId, 'en') : null;

  if (!concept && !en && !he && !fallback) {
    notFound();
  }

  const display = en ?? he ?? fallback ?? null;
  const conceptName = concept?.name ?? display?.title ?? conceptId.replace(/_/g, ' ');
  const conceptNameHe = concept?.name_he ?? null;

  const prerequisites = concept?.prerequisites ?? [];

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">
            Learn
          </Link>
          <span className="mx-2">/</span>
          <Link href={`/learn/${subject}`} className="hover:text-foreground">
            {subjectLabel(subject, 'en')}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{conceptName}</span>
        </nav>

        <header className="mb-8">
          <h1 className="font-display text-3xl font-bold">{conceptName}</h1>
          {conceptNameHe ? (
            <p className="mt-1 text-lg text-muted-foreground" dir="rtl">
              {conceptNameHe}
            </p>
          ) : null}
          {prerequisites.length > 0 ? (
            <p className="mt-3 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Prerequisites:</span>{' '}
              {prerequisites.map((p, i) => (
                <span key={p}>
                  <Link
                    href={`/learn/${subject}/concept/${p}`}
                    className="text-primary hover:underline"
                  >
                    {kgById[p]?.name ?? p.replace(/_/g, ' ')}
                  </Link>
                  {i < prerequisites.length - 1 ? ', ' : ''}
                </span>
              ))}
            </p>
          ) : null}
        </header>

        {!en && !he && !fallback ? (
          <div className="glass-surface rounded-2xl p-8 text-center">
            <p className="text-foreground font-medium">
              {dbConfigured
                ? 'No explanation has been ingested for this concept yet.'
                : 'Concept explanations are unavailable: the site database is not yet connected to this deployment.'}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              {dbConfigured
                ? 'An administrator can run the concept-content seed workflow to fetch it from Wikipedia (CC BY-SA 4.0).'
                : 'A maintainer needs to add DATABASE_URL to the Vercel environment variables. Until then the AI Tutor is the best way to learn this concept.'}
            </p>
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(conceptName)}`}
              className="mt-6 inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              Ask the AI Tutor about this
            </Link>
          </div>
        ) : (
          <ConceptContentClient
            en={en}
            he={he}
            fallback={fallback}
            conceptId={conceptId}
            subject={subject}
            conceptName={conceptName}
          />
        )}

        <section className="mt-10 flex flex-wrap gap-3">
          <Link
            href={`/app/chat/tutor?context=${encodeURIComponent(conceptName)}`}
            className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
          >
            Ask the AI Tutor
          </Link>
          <Link
            href={`/learn/${subject}`}
            className="rounded-lg border border-border bg-surface-1/50 px-4 py-2 text-sm font-medium hover:border-primary/40"
          >
            More in {subjectLabel(subject, 'en')}
          </Link>
        </section>
      </main>
    </div>
  );
}
