import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
import { currentUser } from '@clerk/nextjs/server';
import { CheckCircle2, Clock, RefreshCw, BookOpen } from 'lucide-react';
import { SiteHeader } from '@/components/site-header';
import { PremiumBadge } from '@/components/premium-badge';
import { fetchBagrutExams, fetchSubjects } from '@/lib/content-api';
import { LocalizedSubjectLabel } from '@/components/localized-subject-label';
import {
  fetchConceptsWithExplanations,
  fetchLessonMetaByConceptIds,
  fetchConceptMasteryBulk,
} from '@/lib/neon-db';
import { getLessonIndexEntry } from '@/lib/lesson-index';
import kg from '@/lib/kg-data.json';
import { getCategoryById, SUBJECT_TO_CATEGORY } from '@/lib/curriculum-categories';
import { resolveConceptAlias } from '@/lib/concept-aliases';
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

function hasHebrewText(value: string | null | undefined): boolean {
  return Boolean(value && /[\u0590-\u05FF]/.test(value));
}

function resolveConceptForCatalog(
  id: string,
  kgById: Map<string, KgConcept>,
  kgSubject: 'math' | 'physics' | null,
): KgConcept {
  const aliasId = resolveConceptAlias(id);
  const indexEntry =
    getLessonIndexEntry(id) ??
    getLessonIndexEntry(aliasId) ??
    getLessonIndexEntry(resolveConceptAlias(aliasId));
  const fromKg = kgById.get(id) ?? kgById.get(aliasId);

  const titleEn = indexEntry?.title_en ?? fromKg?.name ?? id.replace(/_/g, ' ');
  const titleHe =
    (hasHebrewText(indexEntry?.title_he) ? indexEntry!.title_he : null) ??
    (hasHebrewText(fromKg?.name_he) ? fromKg!.name_he : null);

  if (fromKg) {
    return { ...fromKg, id, name: titleEn, name_he: titleHe };
  }

  return {
    id,
    name: titleEn,
    name_he: titleHe,
    subject: kgSubject ?? 'math',
  };
}

// Legacy allowlists removed — curriculum category concept_ids drive all tracks.

interface UiSubjectFilter {
  kgSubject: 'math' | 'physics' | null;
  conceptAllowlist: string[];
  categoryId: string;
  recognized: boolean;
}

function uiSubjectFilter(uiSubject: string): UiSubjectFilter {
  const categoryId = SUBJECT_TO_CATEGORY[uiSubject] ?? uiSubject;
  const category = getCategoryById(categoryId);
  if (category) {
    const isPhysics = categoryId === 'hs_physics'
      || categoryId === 'university_physics_1'
      || categoryId === 'university_physics_2';
    return {
      kgSubject: isPhysics ? 'physics' : 'math',
      conceptAllowlist: category.concept_ids,
      categoryId: category.id,
      recognized: true,
    };
  }
  if (uiSubject === 'math') return { kgSubject: 'math', conceptAllowlist: [], categoryId: '', recognized: false };
  if (uiSubject === 'physics') return { kgSubject: 'physics', conceptAllowlist: [], categoryId: '', recognized: false };
  return { kgSubject: null, conceptAllowlist: [], categoryId: '', recognized: false };
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

/** Themed section headers for physics subjects grouped by questionnaire */
const PHYSICS_SECTION_THEMES: Record<string, { emoji: string; label_en: string; label_he: string }> = {
  mechanics_hs: { emoji: '⚙️', label_en: 'Mechanics', label_he: 'מכניקה' },
  electricity_hs: { emoji: '⚡', label_en: 'Electricity & Magnetism', label_he: 'חשמל ומגנטיות' },
  radiation_matter_hs: { emoji: '☢️', label_en: 'Radiation & Modern Physics', label_he: 'קרינה ופיזיקה מודרנית' },
  research_lab_hs: { emoji: '🔬', label_en: 'Research & Lab', label_he: 'מחקר ומעבדה' },
  // University Physics 1 — mechanics-focused sections
  kinematics_dynamics_uni: { emoji: '⚙️', label_en: 'Kinematics & Dynamics', label_he: 'קינמטיקה ודינמיקה' },
  energy_momentum_uni: { emoji: '💫', label_en: 'Energy & Momentum', label_he: 'אנרגיה ותנע' },
  rigid_body_statics_uni: { emoji: '🔧', label_en: 'Rigid Body & Statics', label_he: 'גוף קשיח ושיווי משקל' },
  rotation_angular_momentum_uni: { emoji: '🔄', label_en: 'Rotation & Angular Momentum', label_he: 'סיבוב ותנע זוויתי' },
  systems_of_particles_uni: { emoji: '🎯', label_en: 'Systems of Particles', label_he: 'מערכות חלקיקים' },
  oscillations_uni: { emoji: '〰️', label_en: 'Oscillations', label_he: 'תנודות' },
  fluids_uni: { emoji: '💧', label_en: 'Fluids', label_he: 'פלואידים' },
};

function isPhysicsSubject(categoryId: string): boolean {
  return categoryId === 'hs_physics'
    || categoryId === 'university_physics_1'
    || categoryId === 'high_school_physics';
}

function physicsSectionHeader(
  sectionId: string,
  fallbackEn: string,
  fallbackHe: string,
  isHe: boolean,
): string {
  const theme = PHYSICS_SECTION_THEMES[sectionId];
  if (!theme) return isHe ? fallbackHe : fallbackEn;
  return `${theme.emoji} ${isHe ? theme.label_he : theme.label_en}`;
}

const SUBJECT_ALIASES: Record<string, string> = {
  'high-school-math-3-pts': 'high_school_math_3pt',
  'high-school-math-4-pts': 'high_school_math_4pt',
  'high-school-math-5-pts': 'high_school_math_5pt',
  'high_school_math_3_points': 'high_school_math_3pt',
  'high_school_math_4_points': 'high_school_math_4pt',
  'high_school_math_5_points': 'high_school_math_5pt',
  'hs-math-3': 'high_school_math_3pt',
  'hs-math-4': 'high_school_math_4pt',
  'hs-math-5': 'high_school_math_5pt',
  'math-hs-3': 'high_school_math_3pt',
  hs_math_3: 'high_school_math_3pt',
  hs_math_4: 'high_school_math_4pt',
  hs_math_5: 'high_school_math_5pt',
  'physics-hs': 'hs_physics',
  physics_high_school: 'hs_physics',
  high_school_physics: 'hs_physics',
  physics_1: 'university_physics_1',
  physics_2: 'university_physics_2',
  calculus: 'calculus_1',
  university_prep: 'makhina',
  physics_pre_university: 'makhina_physics',
  math_pre_university: 'makhina',
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
  const kgById = new Map(kgConcepts.map((c) => [c.id, c]));

  const conceptsForSubject = filter.conceptAllowlist.map((id) =>
    resolveConceptForCatalog(id, kgById, filter.kgSubject),
  );

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
      const aliasId = resolveConceptAlias(c.id);
      const meta = lessonMeta.get(c.id) ?? lessonMeta.get(aliasId);
      const indexEntry = getLessonIndexEntry(c.id) ?? getLessonIndexEntry(aliasId);
      const hasLesson = Boolean(meta) || Boolean(indexEntry);
      const mastery = masteryMap.get(c.id) ?? masteryMap.get(aliasId);
      const status = masteryStatus(mastery?.score);
      return { ...c, langs: coverage.get(c.id) ?? coverage.get(aliasId) ?? [], hasLesson, inTrack: true, mastery, status };
    })
    .filter((c) => c.inTrack);

  if (!known && !filter.recognized && bagrut.length === 0 && conceptsWithCoverage.length === 0) {
    notFound();
  }

  // Build section groups using the CurriculumCategory if available
  const category = filter.categoryId ? getCategoryById(filter.categoryId) : null;

  const conceptById = new Map(conceptsWithCoverage.map((c) => [c.id, c]));

  // Sections from the curriculum category (ordered), plus an "Other" bucket for anything not in a section
  const coveredBySection = new Set<string>();
  const sectionGroups: Array<{
    id: string;
    label_en: string;
    label_he: string;
    concepts: typeof conceptsWithCoverage;
  }> = [];

  const shownInSection = new Set<string>();

  if (category) {
    for (const section of category.sections) {
      const sectionConcepts = (section.concept_ids ?? [])
        .map((id) => conceptById.get(id))
        .filter(Boolean)
        .filter((c) => !shownInSection.has(c!.id)) as typeof conceptsWithCoverage;
      if (sectionConcepts.length === 0) continue;
      for (const c of sectionConcepts) {
        coveredBySection.add(c.id);
        shownInSection.add(c.id);
      }
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

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">{t.learn}</Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">
            <LocalizedSubjectLabel subject={subject} />
          </span>
        </nav>

        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold">
              <LocalizedSubjectLabel subject={subject} />
            </h1>
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
                        {isPhysicsSubject(filter.categoryId)
                          ? physicsSectionHeader(group.id, group.label_en, group.label_he, isHe)
                          : isHe ? group.label_he : group.label_en}
                      </h2>
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
                    const statusCfg = c.status ? STATUS_CONFIG[c.status] : null;
                    const StatusIcon = statusCfg?.icon ?? BookOpen;
                    const titles = resolveConceptTitles(c.id, {
                      title_en: c.name,
                      title_he: c.name_he,
                    });
                    const cardTitle = pickConceptTitle(titles, locale);

                    const contentBadge = c.hasLesson ? t.lessonBadge : null;
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
                          ) : !c.hasLesson ? (
                            <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase text-muted-foreground">
                              {t.soon}
                            </span>
                          ) : contentBadge ? (
                            <span className="shrink-0 rounded-full bg-primary/15 px-2 py-0.5 text-[10px] font-medium uppercase text-primary">
                              {contentBadge}
                            </span>
                          ) : null}
                        </div>
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
