import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
import { auth } from '@clerk/nextjs/server';
import { SiteHeader } from '@/components/site-header';
import { LocalizedSubjectLabel } from '@/components/localized-subject-label';
import {
  dbConfigured,
  fetchLessonByConceptId,
  fetchLessonById,
  getLearnerProfile,
  type LessonPointsLevel,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';
import { LessonPageClient } from '@/components/lesson-page-client';
import { getServerLocale } from '@/i18n/locale-server';
import { getMessages } from '@/i18n/messages';
import { getLessonIndexEntry } from '@/lib/lesson-index';
import { isConceptInBundle } from '@/lib/lesson-bundle';
import { MathGlossaryPanel } from '@/components/math-glossary-panel';
import {
  resolveConceptTitles,
  pickConceptTitle,
  isCatalogTitleConcept,
} from '@/lib/concept-display-names';
import { isConceptInCurriculumCatalog } from '@/lib/curriculum-categories';

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
import {
  aliasRedirectTarget,
  resolveLessonConceptId,
  resolveVariantLessonId,
  variantLessonIds,
} from '@/lib/lesson-concept-resolve';

/** Level values the user can explicitly select via the ?level= toggle. */
const LEVEL_QUERY_OVERRIDES = new Set<LessonPointsLevel>(['3pt', '4pt', '5pt', 'uni']);

function parseLevelQueryParam(
  value: string | string[] | undefined,
): LessonPointsLevel | null {
  const raw = Array.isArray(value) ? value[0] : value;
  if (!raw) return null;
  const normalized = raw.trim().toLowerCase();
  return LEVEL_QUERY_OVERRIDES.has(normalized as LessonPointsLevel)
    ? (normalized as LessonPointsLevel)
    : null;
}

export default async function ConceptPage({
  params,
  searchParams,
}: {
  params: Promise<{ subject: string; conceptId: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { subject, conceptId: rawConceptId } = await params;
  const resolvedSearchParams = await searchParams;
  const levelOverride = parseLevelQueryParam(resolvedSearchParams.level);

  const redirectTarget = aliasRedirectTarget(rawConceptId);
  if (redirectTarget) {
    const qs = new URLSearchParams();
    for (const [key, value] of Object.entries(resolvedSearchParams)) {
      const raw = Array.isArray(value) ? value[0] : value;
      if (raw) qs.set(key, raw);
    }
    const suffix = qs.toString() ? `?${qs.toString()}` : '';
    redirect(`/learn/${subject}/concept/${redirectTarget}${suffix}`);
  }

  const conceptId = rawConceptId;
  const canonicalLessonId = resolveLessonConceptId(conceptId);
  const locale = await getServerLocale();
  const t = getMessages(locale).learn;
  const isHe = locale === 'he';
  const concept = kgById[conceptId];

  // Infer level from subject slug so unauthenticated users get correct section gating
  function levelFromSubjectSlug(slug: string): LessonPointsLevel | null {
    if (slug.includes('3')) return '3pt';
    if (slug.includes('4')) return '4pt';
    if (slug.includes('5')) return '5pt';
    if (slug.toLowerCase().includes('phys')) return 'hs_physics';
    if (slug.toLowerCase().includes('bio')) return '4pt';
    return null;
  }

  // Resolve learner level — prefer authenticated profile, fall back to URL slug
  let learnerLevel: LessonPointsLevel | null = levelFromSubjectSlug(subject);
  try {
    const { userId } = await auth();
    if (userId) {
      const profile = await getLearnerProfile(userId);
      const pg = profile?.points_group ?? null;
      if (pg) {
        const raw = String(pg).trim().toLowerCase();
        const num = raw.replace(/pt$/i, '').trim();
        if (num === '3') learnerLevel = '3pt';
        else if (num === '4') learnerLevel = '4pt';
        else if (num === '5') learnerLevel = '5pt';
        else if (raw === 'calc1' || raw === 'calc2' || raw === 'la' || raw === 'university') {
          learnerLevel = 'uni';
        }
      } else if (profile?.goal) {
        const g = profile.goal.toLowerCase();
        if (g.includes('3')) learnerLevel = '3pt';
        else if (g.includes('4')) learnerLevel = '4pt';
        else if (g.includes('5')) learnerLevel = '5pt';
        else if (g.includes('phys')) learnerLevel = 'hs_physics';
        else if (
          g.includes('calc') ||
          g.includes('university') ||
          g.includes('אוניבר') ||
          g.includes('linear algebra') ||
          g.includes('אלגברה לינארית')
        ) {
          learnerLevel = 'uni';
        }
      }
    }
  } catch {
    // Auth not available — slug-based level already set above
  }

  if (levelOverride) {
    learnerLevel = levelOverride;
  }

  // Lesson is the new authoritative source. If it exists, render it instead
  // of the wiki-style explanation. Prefer a per-track variant (`<canonical>__<track>`)
  // matching the learner's level, then fall back to the canonical lesson.
  const variantLessonId = resolveVariantLessonId(conceptId, learnerLevel);
  const [lessonData] = await Promise.all([
    (async () => {
      if (variantLessonId !== canonicalLessonId) {
        const variant = await fetchLessonById(variantLessonId);
        if (variant) return variant;
      }
      const byCanonical = await fetchLessonByConceptId(canonicalLessonId);
      if (byCanonical) return byCanonical;
      if (canonicalLessonId !== conceptId) {
        return fetchLessonByConceptId(conceptId);
      }
      return null;
    })(),
  ]);

  const indexEntry =
    getLessonIndexEntry(variantLessonId) ??
    getLessonIndexEntry(conceptId) ??
    getLessonIndexEntry(canonicalLessonId);
  const hasDirectLesson =
    Boolean(indexEntry) ||
    isConceptInBundle(variantLessonId) ||
    isConceptInBundle(conceptId) ||
    Boolean(
      lessonData &&
        (lessonData.lesson.concept_id === conceptId ||
          lessonData.lesson.concept_id === variantLessonId ||
          lessonData.lesson.concept_id === canonicalLessonId),
    );
  const hasAuthoredLesson = hasDirectLesson;

  // Catalog-listed syllabus topics (and title-only stubs) must render a coming-soon
  // page instead of a hard 404 — they appear as clickable cards on /learn grids.
  const inCatalog =
    isConceptInCurriculumCatalog(conceptId) ||
    isConceptInCurriculumCatalog(canonicalLessonId) ||
    isCatalogTitleConcept(conceptId) ||
    isCatalogTitleConcept(canonicalLessonId);

  if (!concept && !hasAuthoredLesson && !inCatalog) {
    notFound();
  }

  const titles = resolveConceptTitles(conceptId, {
    title_en: lessonData?.lesson.title_en ?? indexEntry?.title_en ?? null,
    title_he: lessonData?.lesson.title_he ?? indexEntry?.title_he ?? concept?.name_he ?? null,
  });
  const conceptName = pickConceptTitle(titles, locale);

  const prerequisites = concept?.prerequisites ?? [];

  // Per-track variants of this concept, if any have been authored. Lets a learner
  // jump to the version written for a different Bagrut track (e.g. an "advanced version").
  const trackVariants = variantLessonIds(conceptId);
  const trackLabel: Record<string, string> = isHe
    ? { '3pt': '3 יח״ל', '4pt': '4 יח״ל', '5pt': '5 יח״ל', uni: 'אוניברסיטה' }
    : { '3pt': '3-unit', '4pt': '4-unit', '5pt': '5-unit', uni: 'University' };

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
            <LocalizedSubjectLabel subject={subject} />
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{conceptName}</span>
        </nav>

        <header className="mb-8">
          <h1 className="font-display text-3xl font-bold">{conceptName}</h1>
          <div className="mt-4 flex flex-wrap gap-2">
            <Link
              href={`/app/practice?concept=${encodeURIComponent(conceptId)}`}
              className="inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              {t.practiceThisTopic}
            </Link>
            <Link
              href={`/app/chat/tutor?topic=${encodeURIComponent(conceptId)}`}
              className="inline-flex rounded-lg border border-border bg-surface-1/50 px-4 py-2 text-sm font-medium hover:border-primary/40"
            >
              {t.chatWithTutorAboutTopic}
            </Link>
          </div>
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

        {trackVariants.length > 1 ? (
          <div
            className="mb-6 flex flex-wrap items-center gap-2 text-sm"
            dir={isHe ? 'rtl' : 'ltr'}
          >
            <span className="text-muted-foreground">
              {isHe ? 'גרסה לפי רמה:' : 'Version by track:'}
            </span>
            {trackVariants.map((v) => {
              const active = learnerLevel === v.track;
              return (
                <Link
                  key={v.track}
                  href={`/learn/${subject}/concept/${conceptId}?level=${v.track}`}
                  className={
                    active
                      ? 'rounded-full bg-primary px-3 py-1 font-medium text-primary-foreground'
                      : 'rounded-full border border-border bg-surface-1/50 px-3 py-1 hover:border-primary/40'
                  }
                >
                  {trackLabel[v.track] ?? v.track}
                </Link>
              );
            })}
          </div>
        ) : null}

        {lessonData && hasDirectLesson ? (
          <LessonPageClient data={lessonData} conceptId={conceptId} learnerLevel={learnerLevel} />
        ) : hasAuthoredLesson ? (
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
              href={`/app/chat/tutor?topic=${encodeURIComponent(conceptId)}`}
              className="mt-6 inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              {t.chatWithTutorAboutTopic}
            </Link>
          </div>
        ) : (
          <div
            className="glass-surface mx-auto max-w-lg rounded-2xl border border-border/60 p-10 text-center"
            dir={isHe ? 'rtl' : 'ltr'}
          >
            <h2 className="font-display text-2xl font-bold text-foreground">
              {t.comingSoonPageTitle}
            </h2>
            <p className="mt-3 text-sm text-muted-foreground">
              {t.comingSoonTutorReady}
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Link
                href={`/app/chat/tutor?topic=${encodeURIComponent(conceptId)}`}
                className="inline-flex justify-center rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-5 py-2.5 text-sm font-semibold text-primary-foreground"
              >
                {t.chatWithTutorAboutTopic}
              </Link>
              <Link
                href={`/learn/${subject}`}
                className="inline-flex justify-center rounded-lg border border-border bg-surface-1/50 px-5 py-2.5 text-sm font-medium hover:border-primary/40"
              >
                {t.backToTopicList}
              </Link>
            </div>
          </div>
        )}

        {lessonData ? (
          <section className="mt-10 flex flex-wrap gap-3">
            <Link
              href={`/app/chat/tutor?topic=${encodeURIComponent(conceptId)}`}
              className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              {t.askAiTutor}
            </Link>
            <Link
              href={`/learn/${subject}`}
              className="rounded-lg border border-border bg-surface-1/50 px-4 py-2 text-sm font-medium hover:border-primary/40"
            >
              {t.moreIn} <LocalizedSubjectLabel subject={subject} />
            </Link>
          </section>
        ) : null}

        <MathGlossaryPanel locale={locale} />
      </main>
    </div>
  );
}
