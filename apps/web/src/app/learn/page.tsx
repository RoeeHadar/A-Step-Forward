import Link from 'next/link';
import { Fragment } from 'react';
import { SiteHeader } from '@/components/site-header';
import { fetchSubjects } from '@/lib/content-api';
import { subjectIcon, subjectLabel } from '@/lib/subject-labels';
import { getServerLocale } from '@/i18n/locale-server';

export const dynamic = 'force-dynamic';

const MAKHINA_CARD = {
  subject: 'makhina',
  section_count: 0,
  sample_grade: null,
};

// Subjects shown in the catalog, grouped by track.
const BAGRUT_SLUGS = [
  'high_school_math_3pt',
  'high_school_math_4pt',
  'high_school_math_5pt',
  'hs_physics',
];

const UNIVERSITY_SLUGS = [
  'university_physics_1',
  'university_physics_2',
  'calculus_1',
  'calculus_2',
  'linear_algebra',
  'statistics_probability',
];

// Legacy slugs to suppress from the catalog when canonical slugs are present.
const SUPPRESS_LEGACY = new Set([
  'calculus',
  'math-hs-3', 'math-hs-4', 'math-hs-5',
  'high_school_math_3_points', 'high_school_math_4_points', 'high_school_math_5_points',
  'physics-hs', 'physics_high_school', 'high_school_physics',
  'linear-algebra',
  'math_pre_university',
]);

type SubjectCard = {
  subject: string;
  section_count: number;
  sample_grade: string | null;
};


function UpgradeTrackBanner({ isHe }: { isHe: boolean }) {
  return (
    <Link
      href="/learn/high_school_math_4pt"
      className="col-span-full block bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-3 text-sm text-foreground transition-colors hover:bg-blue-100 dark:hover:bg-blue-900"
      dir={isHe ? 'rtl' : 'ltr'}
    >
      {isHe
        ? 'שדרוג מ-3 ל-4 יחידות? התחל כאן ←'
        : 'Upgrading from 3pt to 4pt? Start here ←'}
    </Link>
  );
}

function SubjectCard({ s, isMakhina }: { s: SubjectCard; isMakhina: boolean }) {
  return (
    <Link
      href={`/learn/${s.subject}`}
      className="glass-surface group rounded-2xl p-5 transition-all hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-3xl" aria-hidden>
          {subjectIcon(s.subject)}
        </span>
        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
          {isMakhina
            ? 'Bridge track'
            : s.section_count > 0
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
      {isMakhina ? (
        <p className="mt-1.5 text-sm text-muted-foreground" dir="rtl">
          מסלול לבניית בסיס מתמטי לפני האוניברסיטה
        </p>
      ) : null}
    </Link>
  );
}

export default async function LearnPage() {
  const locale = await getServerLocale();
  const isHe = locale === 'he';
  const subjects = await fetchSubjects();

  // Build a slug → card map from DB subjects.
  const bySlug = new Map(subjects.map((s) => [s.subject, s]));

  // Ensure makhina is always present.
  if (!bySlug.has('makhina')) bySlug.set('makhina', MAKHINA_CARD);

  // Helper: get card for a slug (returns placeholder if not in DB yet).
  function card(slug: string): SubjectCard {
    return bySlug.get(slug) ?? { subject: slug, section_count: 0, sample_grade: null };
  }

  const bagrutCards = BAGRUT_SLUGS.map(card);
  const universityCards = UNIVERSITY_SLUGS.map(card);
  const makhinaCard = card('makhina');

  // Collect remaining DB subjects that are not in any group and not suppressed.
  const groupedSlugs = new Set([...BAGRUT_SLUGS, ...UNIVERSITY_SLUGS, 'makhina']);
  const extraCards = subjects.filter(
    (s) => !groupedSlugs.has(s.subject) && !SUPPRESS_LEGACY.has(s.subject),
  );

  const groups = [
    { id: 'bagrut', he: 'בגרות', en: 'Bagrut', cards: bagrutCards },
    { id: 'university', he: 'אוניברסיטה', en: 'University', cards: universityCards },
    { id: 'makhina', he: 'מכינה', en: 'University Prep', cards: [makhinaCard] },
    ...(extraCards.length > 0 ? [{ id: 'other', he: 'נוסף', en: 'Other', cards: extraCards }] : []),
  ];

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10">
        <header className="mb-10">
          <h1 className="font-display text-3xl font-bold text-foreground">Learn</h1>
          <p className="mt-2 text-muted-foreground">
            Free textbooks, practice materials, and Bagrut exams — browse without signing in.
          </p>
        </header>

        <div className="space-y-12">
          {groups.map((group) => (
            <section key={group.id}>
              <div className="mb-4">
                <div className="flex items-center gap-3">
                  <h2 className="font-display text-xl font-semibold text-foreground">{group.en}</h2>
                  <span className="text-muted-foreground" dir="rtl">/ {group.he}</span>
                </div>
                {group.id === 'makhina' ? (
                  <p
                    className="mt-1 text-sm text-muted-foreground"
                    dir={isHe ? 'rtl' : 'ltr'}
                  >
                    {isHe
                      ? 'מסלול לבניית בסיס מתמטי לפני האוניברסיטה'
                      : 'Build your math foundation before university'}
                  </p>
                ) : null}
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {group.cards.map((s) => (
                  <Fragment key={s.subject}>
                    {group.id === 'bagrut' && s.subject === 'high_school_math_4pt' ? (
                      <UpgradeTrackBanner isHe={isHe} />
                    ) : null}
                    <SubjectCard s={s} isMakhina={s.subject === 'makhina'} />
                  </Fragment>
                ))}
              </div>
            </section>
          ))}
        </div>
      </main>
    </div>
  );
}
