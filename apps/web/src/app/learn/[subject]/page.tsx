import Link from 'next/link';
import { notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { PremiumBadge } from '@/components/premium-badge';
import { fetchBagrutExams, fetchSubjects } from '@/lib/content-api';
import { subjectLabel } from '@/lib/subject-labels';
import {
  fetchConceptsWithExplanations,
  fetchLessonMetaByConceptIds,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';

export const dynamic = 'force-dynamic';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
}
const kgConcepts: KgConcept[] = (kg as { concepts: KgConcept[] }).concepts;

// Concept-ID allowlists for UI subjects that map to a narrowed slice of a KG
// subject (e.g. /learn/calculus is just the calculus chapters of KG math).
const CALCULUS_CONCEPTS = [
  'limits',
  'continuity',
  'derivatives_intro',
  'derivatives_rules',
  'derivatives_applications',
  'integrals_intro',
  'integrals_techniques',
  'integrals_applications',
  'definite_integrals',
  'differential_equations_intro',
];
const LINEAR_ALGEBRA_CONCEPTS = [
  'vectors_basics',
  'vectors_2d',
  'la_matrices',
  'la_vector_spaces',
  'la_eigenvalues',
];
const STATISTICS_CONCEPTS = [
  'descriptive_stats',
  'probability_basic',
  'combinatorics',
  'distributions',
  'hypothesis_testing',
];

type MathTrack = '3pt' | '4pt' | '5pt';

interface UiSubjectFilter {
  kgSubject: 'math' | 'physics' | null;
  mathTrack?: MathTrack;
  conceptAllowlist?: string[];
}

/**
 * Translates a URL-facing subject slug (e.g. `high_school_math_5_points`) into
 * the slice of the AI-authored corpus that should be surfaced on that page:
 * which KG subject to draw from, an optional Bagrut math-track filter, and an
 * optional explicit concept allowlist for sub-domain pages.
 */
function uiSubjectFilter(uiSubject: string): UiSubjectFilter {
  // Pure KG-aligned UI subjects.
  if (uiSubject === 'math') return { kgSubject: 'math' };
  if (uiSubject === 'physics') return { kgSubject: 'physics' };

  // Israeli high-school math tracks: same KG concepts, filtered by math_track.
  if (uiSubject === 'high_school_math_3_points')
    return { kgSubject: 'math', mathTrack: '3pt' };
  if (uiSubject === 'high_school_math_4_points')
    return { kgSubject: 'math', mathTrack: '4pt' };
  if (uiSubject === 'high_school_math_5_points')
    return { kgSubject: 'math', mathTrack: '5pt' };

  // Middle school is treated as the 3-pt prep track until we author dedicated content.
  if (
    uiSubject === 'middle_school_math_7th_grade' ||
    uiSubject === 'middle_school_math_8th_grade' ||
    uiSubject === 'middle_school_math_9th_grade'
  ) {
    return { kgSubject: 'math', mathTrack: '3pt' };
  }

  // Pre-university math has no math_track filter; surface everything.
  if (uiSubject === 'math_pre_university') return { kgSubject: 'math' };

  // University-style sub-domains drawn from KG math.
  if (uiSubject === 'calculus' || uiSubject === 'calculus_1') {
    return { kgSubject: 'math', conceptAllowlist: CALCULUS_CONCEPTS };
  }
  if (uiSubject === 'linear_algebra') {
    return { kgSubject: 'math', conceptAllowlist: LINEAR_ALGEBRA_CONCEPTS };
  }
  if (uiSubject === 'statistics_probability') {
    return { kgSubject: 'math', conceptAllowlist: STATISTICS_CONCEPTS };
  }

  // Physics-flavoured subjects: all map to the KG `physics` corpus. Both
  // `physics_high_school` and the inverse word order `high_school_physics`
  // appear in the seeded content_sections, so we accept both.
  if (
    uiSubject === 'physics_high_school' ||
    uiSubject === 'physics_middle_school' ||
    uiSubject === 'physics_pre_university' ||
    uiSubject === 'physics_1' ||
    uiSubject === 'physics_2' ||
    uiSubject === 'high_school_physics' ||
    uiSubject === 'middle_school_physics' ||
    uiSubject === 'bagrut_physics'
  ) {
    return { kgSubject: 'physics' };
  }

  // Catch-all heuristic so any new physics_*/*_physics subject slug we add
  // to content_sections in the future renders against the physics corpus
  // without code changes; same for math.
  if (uiSubject.includes('physics')) return { kgSubject: 'physics' };
  if (uiSubject.includes('math')) return { kgSubject: 'math' };

  return { kgSubject: null };
}

export default async function SubjectPage({ params }: { params: Promise<{ subject: string }> }) {
  const { subject } = await params;
  const allSubjects = await fetchSubjects();
  const known = allSubjects.some((s) => s.subject === subject);

  const filter = uiSubjectFilter(subject);
  const allowlist = filter.conceptAllowlist ? new Set(filter.conceptAllowlist) : null;
  const conceptsForSubject = filter.kgSubject
    ? kgConcepts.filter((c) => {
        if (c.subject !== filter.kgSubject) return false;
        if (allowlist && !allowlist.has(c.id)) return false;
        return true;
      })
    : [];

  const conceptIds = conceptsForSubject.map((c) => c.id);
  const [bagrut, coverage, lessonMeta] = await Promise.all([
    fetchBagrutExams(subject),
    fetchConceptsWithExplanations(conceptIds),
    fetchLessonMetaByConceptIds(conceptIds),
  ]);

  const conceptsWithCoverage = conceptsForSubject
    .map((c) => {
      const meta = lessonMeta.get(c.id);
      const hasLesson = Boolean(meta);
      // Math-track filter: when on a 3/4/5-pt page, only show concepts whose
      // lesson explicitly opted into that track. Non-math subjects ignore this.
      const inTrack =
        filter.mathTrack && filter.kgSubject === 'math'
          ? Boolean(meta?.math_track?.includes(filter.mathTrack))
          : true;
      return { ...c, langs: coverage.get(c.id) ?? [], hasLesson, inTrack };
    })
    .filter((c) => c.inTrack)
    .sort((a, b) => {
      // Lessons first, then explanation-only, then nothing.
      const aRank = a.hasLesson ? 2 : a.langs.length > 0 ? 1 : 0;
      const bRank = b.hasLesson ? 2 : b.langs.length > 0 ? 1 : 0;
      if (aRank !== bRank) return bRank - aRank;
      return a.name.localeCompare(b.name);
    });

  if (!known && bagrut.length === 0 && conceptsWithCoverage.length === 0) {
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

        {conceptsWithCoverage.length > 0 ? (
          <section className="mt-2">
            <h2 className="font-display text-xl font-semibold text-foreground">
              Lessons
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {filter.mathTrack
                ? `AI-authored, bilingual lessons aligned to the ${filter.mathTrack.replace('pt', '-pt')} Bagrut track. Worked examples, common pitfalls, and a quick quiz at the end.`
                : 'AI-authored, bilingual lessons with worked examples, common pitfalls, and a quick quiz at the end. Open one to start.'}
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {conceptsWithCoverage.map((c) => {
                const hasContent = c.hasLesson || c.langs.length > 0;
                const badgeLabel = c.hasLesson
                  ? 'Lesson · EN · HE'
                  : c.langs.includes('he') && c.langs.includes('en')
                    ? 'EN · HE'
                    : c.langs[0]?.toUpperCase();
                return (
                  <Link
                    key={c.id}
                    href={`/learn/${subject}/concept/${c.id}`}
                    className={`glass-surface group rounded-xl p-4 transition-all ${
                      c.hasLesson
                        ? 'border-primary/30 hover:border-primary/60'
                        : 'border-border/60 hover:border-primary/40'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <h3 className="font-medium text-foreground group-hover:text-primary">
                        {c.name}
                      </h3>
                      {hasContent ? (
                        <span
                          className={`rounded-full px-2 py-0.5 text-[10px] font-medium uppercase ${
                            c.hasLesson
                              ? 'bg-primary/15 text-primary'
                              : 'bg-muted text-muted-foreground'
                          }`}
                        >
                          {badgeLabel}
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
        ) : (
          <section className="mt-2 glass-surface rounded-2xl p-8 text-center">
            <h2 className="font-display text-xl font-semibold text-foreground">
              No lessons in this track yet
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              We&rsquo;re still authoring AI lessons for this slice of the curriculum. In the
              meantime, the AI Tutor can teach any topic on demand and reference your goals.
            </p>
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(subject)}`}
              className="mt-5 inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              Open Tutor Chat
            </Link>
          </section>
        )}

      </main>
    </div>
  );
}
