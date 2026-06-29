import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
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
import { getLessonIndexEntry } from '@/lib/lesson-index';
import kg from '@/lib/kg-data.json';
import { CURRICULUM_CATEGORIES, conceptIdsForLevel } from '@/lib/curriculum-categories';
import { getServerLocale } from '@/i18n/locale-server';
import { getMessages } from '@/i18n/messages';
import { resolveConceptTitles, pickConceptTitle } from '@/lib/concept-display-names';

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

/**
 * Extra blocklist for HS 5pt — university / advanced LA concepts not on Bagrut 581.
 * Note: all `uni_*` prefixed concepts are also blocked by `isInBagrutScope` directly.
 * Concepts not in MATH_5PT_CONCEPTS are already blocked via the conceptIdsForLevel allowlist.
 */
const FILTER_FROM_HS_5PT = new Set([
  // University linear algebra (not on any Bagrut questionnaire)
  'uni_vector_fields', 'uni_manifolds',
  'la_diagonalization', 'la_eigenvalues', 'la_vector_spaces', 'la_orthogonality',
  'la_determinants', 'la_matrices', 'la_vectors',
  'matrix_spaces', 'orthogonality',
  // Not on Bagrut 581 / 807
  'differential_equations_intro',
  'hypothesis_testing',
  'statistics_descriptive',
  'complex_numbers',
]);

/** Extra blocklist for HS 3pt — no calculus, advanced probability, or university content */
const FILTER_FROM_HS_3PT = new Set([
  'limits',
  'continuity',
  'derivatives_intro',
  'derivatives_rules',
  'derivatives_applications',
  'optimization_problems',
  'integrals_intro',
  'definite_integrals',
  'integrals_techniques',
  'integrals_applications',
  'differential_equations_intro',
  'logarithms',
  'function_transformations',
  'trigonometry_identities',
  'trigonometry_equations',
  'analytic_geometry',
  'vectors_2d',
  'distributions',
  'combinatorics',
  'la_diagonalization',
  'la_eigenvalues',
  'la_vector_spaces',
  'la_orthogonality',
  'la_determinants',
  'la_matrices',
  'la_vectors',
]);

/** Extra blocklist for HS 4pt — 5pt calculus / university content */
const FILTER_FROM_HS_4PT = new Set([
  ...FILTER_FROM_HS_5PT,
  'limits',
  'derivatives_intro',
  'derivatives_rules',
  'derivatives_applications',
  'optimization_problems',
  'integrals_intro',
  'definite_integrals',
  'integrals_techniques',
  'integrals_applications',
  'function_transformations',
  'trigonometry_identities',
  'trigonometry_equations',
  'analytic_geometry',
  'vectors_2d',
  'logarithms',
  'distributions',
]);

function isInBagrutScope(conceptId: string, mathTrack: MathTrack): boolean {
  if (conceptId.startsWith('uni_')) return false;
  const allowlist = new Set(conceptIdsForLevel(mathTrack));
  if (!allowlist.has(conceptId)) return false;
  if (mathTrack === '3pt' && FILTER_FROM_HS_3PT.has(conceptId)) return false;
  if (mathTrack === '5pt' && FILTER_FROM_HS_5PT.has(conceptId)) return false;
  if (mathTrack === '4pt' && FILTER_FROM_HS_4PT.has(conceptId)) return false;
  return true;
}

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
  if (
    uiSubject === 'hs-math-3' ||
    uiSubject === 'math-hs-3' ||
    uiSubject === 'hs_math_3' ||
    uiSubject === 'math_3' ||
    uiSubject === 'math-3'
  )
    return { kgSubject: 'math', mathTrack: '3pt', categoryId: 'math-hs-3' };
  if (uiSubject === 'hs-math-4' || uiSubject === 'hs_math_4' || uiSubject === 'math_4' || uiSubject === 'math-4')
    return { kgSubject: 'math', mathTrack: '4pt', categoryId: 'math-hs-4' };
  if (uiSubject === 'hs-math-5' || uiSubject === 'hs_math_5' || uiSubject === 'math_5' || uiSubject === 'math-5')
    return { kgSubject: 'math', mathTrack: '5pt', categoryId: 'math-hs-5' };
  if (uiSubject === 'hs_physics')
    return { kgSubject: 'physics', categoryId: 'physics-hs' };
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

const SUBJECT_ALIASES: Record<string, string> = {
  'high-school-math-3-pts': 'high_school_math_3_points',
  'high-school-math-4-pts': 'high_school_math_4_points',
  'high-school-math-5-pts': 'high_school_math_5_points',
  'hs-math-3': 'high_school_math_3_points',
  'hs-math-4': 'high_school_math_4_points',
  'hs-math-5': 'high_school_math_5_points',
  'math-hs-3': 'high_school_math_3_points',
  hs_math_3: 'high_school_math_3_points',
  hs_math_4: 'high_school_math_4_points',
  hs_math_5: 'high_school_math_5_points',
};

export default async function SubjectPage({ params }: { params: Promise<{ subject: string }> }) {
  const { subject } = await params;

  if (SUBJECT_ALIASES[subject]) {
    redirect(`/learn/${SUBJECT_ALIASES[subject]}`);
  }

  const locale = await getServerLocale();
  const t = getMessages(locale).learn;
  const isHe = locale === 'he';
  const allSubjects = await fetchSubjects();
  const known = allSubjects.some((s) => s.subject === subject);

  const filter = uiSubjectFilter(subject);
  const allowlist = filter.conceptAllowlist ? new Set(filter.conceptAllowlist) : null;
  const conceptsForSubject = filter.kgSubject
    ? kgConcepts.filter((c) => {
        if (c.subject !== filter.kgSubject) return false;
        if (allowlist && !allowlist.has(c.id)) return false;
        if (filter.mathTrack && filter.kgSubject === 'math' && !isInBagrutScope(c.id, filter.mathTrack)) {
          return false;
        }
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
      const indexEntry = getLessonIndexEntry(c.id);
      const hasLesson = Boolean(meta) || Boolean(indexEntry);
      const trackSource = meta?.math_track ?? indexEntry?.math_track;
      const inTrack =
        filter.mathTrack && filter.kgSubject === 'math'
          ? Boolean(trackSource?.includes(filter.mathTrack))
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
      sectionGroups.push({ id: '__all__', label_en: t.allTopics, label_he: t.allTopics, concepts: sorted });
    } else if (ungrouped.length > 0) {
      sectionGroups.push({ id: '__other__', label_en: t.otherTopics, label_he: t.otherTopics, concepts: ungrouped });
    }
  }

  // Stats for header
  const doneCount = conceptsWithCoverage.filter((c) => c.status === 'done').length;
  const totalWithLesson = conceptsWithCoverage.filter((c) => c.hasLesson).length;
  const subjectName = subjectLabel(subject, locale);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">{t.learn}</Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{subjectName}</span>
        </nav>

        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold">{subjectName}</h1>
            {learnerId && totalWithLesson > 0 ? (
              <p className="mt-2 text-sm text-muted-foreground">
                {t.lessonsCompleted
                  .replace('{done}', String(doneCount))
                  .replace('{total}', String(totalWithLesson))}
              </p>
            ) : null}
          </div>
          {bagrut.length > 0 ? (
            <Link
              href={`/learn/${subject}/bagrut`}
              className="rounded-lg border border-border bg-surface-1/50 px-4 py-2 text-sm font-medium hover:border-primary/40"
            >
              {t.bagrutExams.replace('{count}', String(bagrut.length))}
            </Link>
          ) : null}
        </header>

        <div className="mb-8 glass-surface rounded-2xl border border-accent-amber/20 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-foreground">{t.chatWithTutor}</h2>
                <PremiumBadge />
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                {t.chatWithTutorDesc}
              </p>
            </div>
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(subject)}`}
              className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              {t.openTutorChat}
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
                        {isHe ? group.label_he : group.label_en}
                      </h2>
                      {isHe && group.label_en !== group.label_he ? (
                        <p className="text-xs text-muted-foreground" dir="ltr">
                          {group.label_en}
                        </p>
                      ) : null}
                    </div>
                    <div className="ml-auto text-xs text-muted-foreground">
                      {t.lessonsDone
                        .replace('{lessons}', String(group.concepts.filter((c) => c.hasLesson).length))
                        .replace('{done}', String(group.concepts.filter((c) => c.status === 'done').length))}
                    </div>
                  </div>
                ) : null}

                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {group.concepts.map((c) => {
                    const hasContent = c.hasLesson || c.langs.length > 0;
                    const statusCfg = c.status ? STATUS_CONFIG[c.status] : null;
                    const StatusIcon = statusCfg?.icon ?? BookOpen;
                    const titles = resolveConceptTitles(c.id);
                    const cardTitle = pickConceptTitle(titles, locale);
                    const cardTitleAlt = isHe ? titles.title_en : titles.title_he;

                    const contentBadge = c.hasLesson
                      ? isHe
                        ? t.lessonBadge
                        : 'Lesson'
                      : c.langs.includes('he') && c.langs.includes('en')
                        ? isHe
                          ? 'EN · HE'
                          : null
                        : (c.langs[0]?.toUpperCase() ?? null);
                    const statusLabel = statusCfg
                      ? c.status === 'done'
                        ? t.statusDone
                        : c.status === 'in_progress'
                          ? t.statusInProgress
                          : t.statusReview
                      : null;

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
                            {cardTitle}
                          </h3>
                          {/* Completion badge takes precedence over content badge */}
                          {statusCfg ? (
                            <span
                              className={`flex shrink-0 items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${statusCfg.classes}`}
                            >
                              <StatusIcon className="h-3 w-3" />
                              {statusLabel}
                            </span>
                          ) : hasContent && contentBadge ? (
                            <span
                              className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium uppercase ${
                                c.hasLesson
                                  ? 'bg-primary/15 text-primary'
                                  : 'bg-muted text-muted-foreground'
                              }`}
                            >
                              {contentBadge}
                            </span>
                          ) : (
                            <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
                              {t.soon}
                            </span>
                          )}
                        </div>
                        {isHe && cardTitleAlt ? (
                          <p className="mt-1 text-sm text-muted-foreground" dir="ltr">
                            {cardTitleAlt}
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
                              {t.masteryPct.replace('{pct}', String(Math.round(c.mastery.score * 100)))}
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
              {t.noLessonsYet}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {t.noLessonsDesc}
            </p>
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(subject)}`}
              className="mt-5 inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              {t.openTutorChat}
            </Link>
          </section>
        )}
      </main>
    </div>
  );
}
