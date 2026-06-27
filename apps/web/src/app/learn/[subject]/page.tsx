import Link from 'next/link';
import { notFound } from 'next/navigation';
import { currentUser } from '@clerk/nextjs/server';
import { CheckCircle2, Clock, RefreshCw, BookOpen } from 'lucide-react';
import { SiteHeader } from '@/components/site-header';
import { PremiumBadge } from '@/components/premium-badge';
import { fetchBagrutExams, fetchSubjects } from '@/lib/content-api';
import { subjectLabel } from '@/lib/subject-labels';
import {
  fetchConceptsWithExplanations,
  fetchLessonMetaByConceptIds,
  fetchConceptMasteryBulk,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';

export const dynamic = 'force-dynamic';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
}
const kgConcepts: KgConcept[] = (kg as { concepts: KgConcept[] }).concepts;

// Concept-ID allowlists for UI subjects that map to a narrowed slice of a KG subject.
const CALCULUS_CONCEPTS = [
  'limits', 'continuity', 'derivatives_intro', 'derivatives_rules',
  'derivatives_applications', 'integrals_intro', 'integrals_techniques',
  'integrals_applications', 'definite_integrals', 'differential_equations_intro',
];
const LINEAR_ALGEBRA_CONCEPTS = ['vectors_basics', 'vectors_2d', 'la_matrices', 'la_vector_spaces', 'la_eigenvalues'];
const STATISTICS_CONCEPTS = ['descriptive_stats', 'probability_basic', 'combinatorics', 'distributions', 'hypothesis_testing'];

type MathTrack = '3pt' | '4pt' | '5pt';

interface UiSubjectFilter {
  kgSubject: 'math' | 'physics' | null;
  mathTrack?: MathTrack;
  conceptAllowlist?: string[];
  /** Maps to a CurriculumCategory id for section grouping */
  categoryId?: string;
}

function uiSubjectFilter(uiSubject: string): UiSubjectFilter {
  if (uiSubject === 'math') return { kgSubject: 'math' };
  if (uiSubject === 'physics') return { kgSubject: 'physics' };
  if (uiSubject === 'high_school_math_3_points')
    return { kgSubject: 'math', mathTrack: '3pt', categoryId: 'math-hs-3' };
  if (uiSubject === 'high_school_math_4_points')
    return { kgSubject: 'math', mathTrack: '4pt', categoryId: 'math-hs-4' };
  if (uiSubject === 'high_school_math_5_points')
    return { kgSubject: 'math', mathTrack: '5pt', categoryId: 'math-hs-5' };
  if (
    uiSubject === 'middle_school_math_7th_grade' ||
    uiSubject === 'middle_school_math_8th_grade' ||
    uiSubject === 'middle_school_math_9th_grade'
  ) return { kgSubject: 'math', mathTrack: '3pt', categoryId: 'math-hs-3' };
  if (uiSubject === 'math_pre_university') return { kgSubject: 'math' };
  if (uiSubject === 'calculus' || uiSubject === 'calculus_1')
    return { kgSubject: 'math', conceptAllowlist: CALCULUS_CONCEPTS, categoryId: 'calculus' };
  if (uiSubject === 'linear_algebra')
    return { kgSubject: 'math', conceptAllowlist: LINEAR_ALGEBRA_CONCEPTS, categoryId: 'linear-algebra' };
  if (uiSubject === 'statistics_probability')
    return { kgSubject: 'math', conceptAllowlist: STATISTICS_CONCEPTS };
  if (
    uiSubject === 'physics_high_school' || uiSubject === 'physics_middle_school' ||
    uiSubject === 'physics_pre_university' || uiSubject === 'physics_1' ||
    uiSubject === 'physics_2' || uiSubject === 'high_school_physics' ||
    uiSubject === 'middle_school_physics' || uiSubject === 'bagrut_physics'
  ) return { kgSubject: 'physics', categoryId: 'physics-hs' };
  if (uiSubject.includes('physics')) return { kgSubject: 'physics', categoryId: 'physics-hs' };
  if (uiSubject.includes('math')) return { kgSubject: 'math' };
  return { kgSubject: null };
}

/** Mastery score thresholds */
function masteryStatus(score: number | undefined): 'done' | 'in_progress' | 'needs_review' | null {
  if (score === undefined) return null;
  if (score >= 0.70) return 'done';
  if (score >= 0.40) return 'in_progress';
  return 'needs_review';
}

const STATUS_CONFIG = {
  done: {
    icon: CheckCircle2,
    label_en: 'Done',
    label_he: 'הושלם',
    classes: 'bg-emerald-500/15 text-emerald-500 border-emerald-500/30',
    cardBorder: 'border-emerald-500/30',
  },
  in_progress: {
    icon: Clock,
    label_en: 'In progress',
    label_he: 'בתהליך',
    classes: 'bg-accent-amber/15 text-accent-amber border-accent-amber/30',
    cardBorder: 'border-accent-amber/30',
  },
  needs_review: {
    icon: RefreshCw,
    label_en: 'Review needed',
    label_he: 'דרוש חזרה',
    classes: 'bg-destructive/15 text-destructive border-destructive/30',
    cardBorder: 'border-destructive/30',
  },
} as const;

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
  const [bagrut, coverage, lessonMeta, clerkUser] = await Promise.all([
    fetchBagrutExams(subject),
    fetchConceptsWithExplanations(conceptIds),
    fetchLessonMetaByConceptIds(conceptIds),
    currentUser().catch(() => null),
  ]);

  // Fetch mastery if user is logged in
  const learnerId = clerkUser?.id ?? null;
  const masteryMap = learnerId
    ? await fetchConceptMasteryBulk(learnerId, conceptIds)
    : new Map<string, { score: number; data_points: number; last_activity: string | null; concept_id: string }>();

  const conceptsWithCoverage = conceptsForSubject
    .map((c) => {
      const meta = lessonMeta.get(c.id);
      const hasLesson = Boolean(meta);
      const inTrack =
        filter.mathTrack && filter.kgSubject === 'math'
          ? Boolean(meta?.math_track?.includes(filter.mathTrack))
          : true;
      const mastery = masteryMap.get(c.id);
      const status = masteryStatus(mastery?.score);
      return { ...c, langs: coverage.get(c.id) ?? [], hasLesson, inTrack, mastery, status };
    })
    .filter((c) => c.inTrack);

  if (!known && bagrut.length === 0 && conceptsWithCoverage.length === 0) {
    notFound();
  }

  // Build section groups using the CurriculumCategory if available
  const category = filter.categoryId
    ? CURRICULUM_CATEGORIES.find((cat) => cat.id === filter.categoryId)
    : null;

  const conceptById = new Map(conceptsWithCoverage.map((c) => [c.id, c]));

  // Sections from the curriculum category (ordered), plus an "Other" bucket for anything not in a section
  const coveredBySection = new Set<string>();
  const sectionGroups: Array<{
    id: string;
    label_en: string;
    label_he: string;
    concepts: typeof conceptsWithCoverage;
  }> = [];

  if (category) {
    for (const section of category.sections) {
      const sectionConcepts = (section.concept_ids ?? [])
        .map((id) => conceptById.get(id))
        .filter(Boolean) as typeof conceptsWithCoverage;
      if (sectionConcepts.length === 0) continue;
      for (const c of sectionConcepts) coveredBySection.add(c.id);
      sectionGroups.push({
        id: section.id,
        label_en: section.enLabel,
        label_he: section.heLabel,
        concepts: sectionConcepts,
      });
    }
  }

  // Any concepts not assigned to a section go in a flat fallback group
  const ungrouped = conceptsWithCoverage.filter((c) => !coveredBySection.has(c.id));
  if (sectionGroups.length === 0 || ungrouped.length > 0) {
    if (sectionGroups.length === 0) {
      // No category structure — sort: lessons first, then explanation-only, then nothing.
      const sorted = [...conceptsWithCoverage].sort((a, b) => {
        const aRank = a.hasLesson ? 2 : a.langs.length > 0 ? 1 : 0;
        const bRank = b.hasLesson ? 2 : b.langs.length > 0 ? 1 : 0;
        if (aRank !== bRank) return bRank - aRank;
        return a.name.localeCompare(b.name);
      });
      sectionGroups.push({ id: '__all__', label_en: 'All Topics', label_he: 'כל הנושאים', concepts: sorted });
    } else if (ungrouped.length > 0) {
      sectionGroups.push({ id: '__other__', label_en: 'Other Topics', label_he: 'נושאים נוספים', concepts: ungrouped });
    }
  }

  // Stats for header
  const doneCount = conceptsWithCoverage.filter((c) => c.status === 'done').length;
  const totalWithLesson = conceptsWithCoverage.filter((c) => c.hasLesson).length;

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">Learn</Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{subjectLabel(subject, 'en')}</span>
        </nav>

        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold">{subjectLabel(subject, 'en')}</h1>
            <p className="mt-1 text-muted-foreground" dir="rtl">
              {subjectLabel(subject, 'he')}
            </p>
            {learnerId && totalWithLesson > 0 ? (
              <p className="mt-2 text-sm text-muted-foreground">
                <span className="font-semibold text-emerald-500">{doneCount}</span> of {totalWithLesson} lessons completed
              </p>
            ) : null}
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

        {sectionGroups.length > 0 && conceptsWithCoverage.length > 0 ? (
          <div className="space-y-10">
            {sectionGroups.map((group, groupIdx) => (
              <section key={group.id}>
                {/* Section header — only show if there's more than one group */}
                {sectionGroups.length > 1 || group.id !== '__all__' ? (
                  <div className="mb-4 flex items-center gap-3">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                      {groupIdx + 1}
                    </div>
                    <div>
                      <h2 className="font-display text-lg font-semibold text-foreground">
                        {group.label_en}
                      </h2>
                      <p className="text-xs text-muted-foreground" dir="rtl">
                        {group.label_he}
                      </p>
                    </div>
                    <div className="ml-auto text-xs text-muted-foreground">
                      {group.concepts.filter((c) => c.hasLesson).length} lessons ·{' '}
                      {group.concepts.filter((c) => c.status === 'done').length} done
                    </div>
                  </div>
                ) : null}

                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {group.concepts.map((c) => {
                    const hasContent = c.hasLesson || c.langs.length > 0;
                    const statusCfg = c.status ? STATUS_CONFIG[c.status] : null;
                    const StatusIcon = statusCfg?.icon ?? BookOpen;

                    const badgeLabel = c.hasLesson
                      ? 'Lesson · EN · HE'
                      : c.langs.includes('he') && c.langs.includes('en')
                        ? 'EN · HE'
                        : (c.langs[0]?.toUpperCase() ?? null);

                    return (
                      <Link
                        key={c.id}
                        href={`/learn/${subject}/concept/${c.id}`}
                        className={`glass-surface group rounded-xl p-4 transition-all ${
                          statusCfg
                            ? `${statusCfg.cardBorder} hover:border-primary/60`
                            : c.hasLesson
                              ? 'border-primary/30 hover:border-primary/60'
                              : 'border-border/60 hover:border-primary/40'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="font-medium text-foreground group-hover:text-primary">
                            {c.name}
                          </h3>
                          {/* Completion badge takes precedence over content badge */}
                          {statusCfg ? (
                            <span
                              className={`flex shrink-0 items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${statusCfg.classes}`}
                            >
                              <StatusIcon className="h-3 w-3" />
                              {statusCfg.label_en}
                            </span>
                          ) : hasContent ? (
                            <span
                              className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium uppercase ${
                                c.hasLesson
                                  ? 'bg-primary/15 text-primary'
                                  : 'bg-muted text-muted-foreground'
                              }`}
                            >
                              {badgeLabel}
                            </span>
                          ) : (
                            <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
                              Soon
                            </span>
                          )}
                        </div>
                        {c.name_he ? (
                          <p className="mt-1 text-sm text-muted-foreground" dir="rtl">
                            {c.name_he}
                          </p>
                        ) : null}
                        {/* Score bar if in-progress or needs review */}
                        {c.mastery && c.status && c.status !== 'done' ? (
                          <div className="mt-2">
                            <div className="h-1 w-full overflow-hidden rounded-full bg-muted">
                              <div
                                className={`h-full rounded-full ${c.status === 'in_progress' ? 'bg-accent-amber' : 'bg-destructive/60'}`}
                                style={{ width: `${Math.round(c.mastery.score * 100)}%` }}
                              />
                            </div>
                            <p className="mt-0.5 text-[9px] text-muted-foreground">
                              {Math.round(c.mastery.score * 100)}% mastery
                            </p>
                          </div>
                        ) : null}
                      </Link>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>
        ) : (
          <section className="mt-2 glass-surface rounded-2xl p-8 text-center">
            <h2 className="font-display text-xl font-semibold text-foreground">
              No lessons in this track yet
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              We&rsquo;re still authoring AI lessons for this slice of the curriculum. The AI Tutor
              can teach any topic on demand and reference your goals.
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
