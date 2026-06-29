import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
import { auth } from '@clerk/nextjs/server';
import { SiteHeader } from '@/components/site-header';
import { subjectLabel } from '@/lib/subject-labels';
import {
  dbConfigured,
  fetchConceptExplanation,
  fetchConceptExplanationFallback,
  fetchLessonByConceptId,
  getLearnerProfile,
  type LessonPointsLevel,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';
import { ConceptContentClient } from '@/components/concept-content-client';
import { LessonPageClient } from '@/components/lesson-page-client';
import { getServerLocale } from '@/i18n/locale-server';
import { getMessages } from '@/i18n/messages';
import { getLessonIndexEntry } from '@/lib/lesson-index';
import { resolveConceptTitles, pickConceptTitle } from '@/lib/concept-display-names';

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

/** Legacy / catalog slugs that differ from the canonical lesson concept_id. */
const CONCEPT_ID_ALIASES: Record<string, string> = {
  basic_probability: 'probability_basic',
};

export default async function ConceptPage({
  params,
}: {
  params: Promise<{ subject: string; conceptId: string }>;
}) {
  const { subject, conceptId: rawConceptId } = await params;

  if (CONCEPT_ID_ALIASES[rawConceptId]) {
    redirect(`/learn/${subject}/concept/${CONCEPT_ID_ALIASES[rawConceptId]}`);
  }

  const conceptId = rawConceptId;
  const locale = await getServerLocale();
  const t = getMessages(locale).learn;
  const isHe = locale === 'he';
  const concept = kgById[conceptId];

  // Resolve learner level (best-effort; fall back to null if not logged in or no profile)
  let learnerLevel: LessonPointsLevel | null = null;
  try {
    const { userId } = await auth();
    if (userId) {
      const profile = await getLearnerProfile(userId);
      const pg = profile?.points_group ?? null;
      if (pg) {
        const num = String(pg).replace(/pt$/i, '').trim();
        if (num === '3') learnerLevel = '3pt';
        else if (num === '4') learnerLevel = '4pt';
        else if (num === '5') learnerLevel = '5pt';
      } else if (profile?.goal) {
        const g = profile.goal.toLowerCase();
        if (g.includes('3')) learnerLevel = '3pt';
        else if (g.includes('4')) learnerLevel = '4pt';
        else if (g.includes('5')) learnerLevel = '5pt';
        else if (g.includes('phys')) learnerLevel = 'hs_physics';
      }
    }
  } catch {
    // Auth not available in this context — fine, render without level filtering
  }

  // Lesson is the new authoritative source. If it exists, render it instead
  // of the wiki-style explanation. Both queries run in parallel for the
  // fallback case.
  const [lessonData, en, he] = await Promise.all([
    fetchLessonByConceptId(conceptId),
    fetchConceptExplanation(conceptId, 'en'),
    fetchConceptExplanation(conceptId, 'he'),
  ]);

  const indexEntry = getLessonIndexEntry(conceptId);

  const fallback =
    !lessonData && !en && !he
      ? await fetchConceptExplanationFallback(conceptId, 'en')
      : null;

  if (!concept && !lessonData && !indexEntry && !en && !he && !fallback) {
    notFound();
  }

  const display = en ?? he ?? fallback ?? null;
  const conceptNameEn =
    lessonData?.lesson.title_en ??
    indexEntry?.title_en ??
    concept?.name ??
    display?.title ??
    conceptId.replace(/_/g, ' ');
  const conceptNameHe =
    lessonData?.lesson.title_he ?? indexEntry?.title_he ?? concept?.name_he ?? null;
  const conceptName = isHe && conceptNameHe ? conceptNameHe : conceptNameEn;

  const subjectName = subjectLabel(subject, locale);
  const prerequisites = concept?.prerequisites ?? [];

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">
            {t.learn}
          </Link>
          <span className="mx-2">/</span>
          <Link href={`/learn/${subject}`} className="hover:text-foreground">
            {subjectName}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{conceptName}</span>
        </nav>

        <header className="mb-8">
          <h1 className="font-display text-3xl font-bold">{conceptName}</h1>
          {prerequisites.length > 0 ? (
            <p className="mt-3 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">{t.prerequisites}:</span>{' '}
              {prerequisites.map((p, i) => {
                const prereqTitle = pickConceptTitle(resolveConceptTitles(p), locale);
                return (
                <span key={p}>
                  <Link
                    href={`/learn/${subject}/concept/${p}`}
                    className="text-primary hover:underline"
                  >
                    {prereqTitle}
                  </Link>
                  {i < prerequisites.length - 1 ? ', ' : ''}
                </span>
                );
              })}
            </p>
          ) : null}
        </header>

        {lessonData ? (
          <LessonPageClient data={lessonData} conceptId={conceptId} learnerLevel={learnerLevel} />
        ) : !en && !he && !fallback ? (
          <div
            className="glass-surface rounded-2xl p-8 text-center"
            dir={isHe ? 'rtl' : 'ltr'}
          >
            <p className="text-foreground font-medium">
              {dbConfigured ? t.noExplanationIngested : t.dbNotConnected}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              {dbConfigured ? t.adminSeedHint : t.dbSetupHint}
            </p>
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(conceptNameEn)}`}
              className="mt-6 inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              {t.askAiTutorAbout}
            </Link>
          </div>
        ) : (
          <ConceptContentClient
            en={en}
            he={he}
            fallback={fallback}
            conceptId={conceptId}
            subject={subject}
            conceptName={conceptNameEn}
          />
        )}

        <section className="mt-10 flex flex-wrap gap-3">
          <Link
            href={`/app/chat/tutor?context=${encodeURIComponent(conceptNameEn)}`}
            className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
          >
            {t.askAiTutor}
          </Link>
          <Link
            href={`/learn/${subject}`}
            className="rounded-lg border border-border bg-surface-1/50 px-4 py-2 text-sm font-medium hover:border-primary/40"
          >
            {t.moreIn} {subjectName}
          </Link>
        </section>
      </main>
    </div>
  );
}
