import Link from 'next/link';
import { Fragment } from 'react';
import { SiteHeader } from '@/components/site-header';
import { fetchSubjects } from '@/lib/content-api';
import { subjectIcon, subjectLabel } from '@/lib/subject-labels';
import { getServerLocale } from '@/i18n/locale-server';

export const dynamic = 'force-dynamic';

const MAKHINA_MATH_CARD = {
  subject: 'makhina',
  section_count: 0,
  sample_grade: null,
};

const MAKHINA_PHYSICS_CARD = {
  subject: 'makhina_physics',
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

function cardDescription(subject: string, isHe: boolean): string | null {
  if (subject === 'high_school_math_3pt') {
    return isHe
      ? 'מסלול 372 החדש — כולל תכנון לינארי, ללא חדו״א'
      : 'New 372 track — includes linear programming, no calculus';
  }
  if (subject === 'high_school_math_4pt') {
    return isHe
      ? 'שני שאלונים: 471 (65%) + 472 (35%)'
      : 'Two exam papers: 471 (65%) + 472 (35%)';
  }
  if (subject === 'high_school_math_5pt') {
    return isHe
      ? 'כולל אינduction, מספרים מרוכבים ושני שאלונים'
      : 'Includes induction, complex numbers, and two exam papers';
  }
  if (subject === 'makhina') {
    return isHe
      ? 'מסלול לבניית בסיס מתמטי לפני האוניברסיטה'
      : 'Build your math foundation before university';
  }
  if (subject === 'makhina_physics') {
    return isHe
      ? 'יסודות הפיזיקה לפני האוניברסיטה'
      : 'Physics foundations before university';
  }
  return null;
}

function SubjectCard({
  s,
  isHe,
}: {
  s: SubjectCard;
  isHe: boolean;
}) {
  const locale = isHe ? 'he' : 'en';
  const isMakhinaTrack = s.subject === 'makhina' || s.subject === 'makhina_physics';
  const description = cardDescription(s.subject, isHe);
  const badgeLabel = isMakhinaTrack
    ? isHe
      ? 'מסלול גשר'
      : 'Bridge track'
    : s.section_count > 0
      ? isHe
        ? `${s.section_count} פרקים`
        : `${s.section_count} sections`
      : isHe
        ? 'חומרים נבחרים'
        : 'Curated resources';

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
          {badgeLabel}
        </span>
      </div>
      <h2 className="mt-3 font-display text-lg font-semibold text-foreground group-hover:text-primary" dir={isHe ? 'rtl' : 'ltr'}>
        {subjectLabel(s.subject, locale)}
      </h2>
      {!isHe ? (
        <p className="mt-1 text-sm text-muted-foreground" dir="rtl">
          {subjectLabel(s.subject, 'he')}
        </p>
      ) : null}
      {description ? (
        <p className="mt-1.5 text-sm text-muted-foreground" dir={isHe ? 'rtl' : 'ltr'}>
          {description}
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

  // Ensure makhina tracks are always present.
  if (!bySlug.has('makhina')) bySlug.set('makhina', MAKHINA_MATH_CARD);
  if (!bySlug.has('makhina_physics')) bySlug.set('makhina_physics', MAKHINA_PHYSICS_CARD);

  // Helper: get card for a slug (returns placeholder if not in DB yet).
  function card(slug: string): SubjectCard {
    return bySlug.get(slug) ?? { subject: slug, section_count: 0, sample_grade: null };
  }

  const bagrutCards = BAGRUT_SLUGS.map(card);
  const universityCards = UNIVERSITY_SLUGS.map(card);
  const makhinaCards = [card('makhina'), card('makhina_physics')];

  const groups = [
    { id: 'bagrut', he: 'בגרות', en: 'Bagrut', cards: bagrutCards },
    { id: 'university', he: 'אוניברסיטה', en: 'University', cards: universityCards },
    {
      id: 'makhina',
      he: 'מכינה',
      en: 'University Preparation',
      cards: makhinaCards,
    },
  ];

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10">
        <header className="mb-10">
          <h1 className="font-display text-3xl font-bold text-foreground">
            {isHe ? 'לימוד' : 'Learn'}
          </h1>
          <p className="mt-2 text-muted-foreground" dir={isHe ? 'rtl' : 'ltr'}>
            {isHe
              ? 'ספרי לימוד, חומרי תרגול ומבחני בגרות — ללא צורך בהרשמה.'
              : 'Free textbooks, practice materials, and Bagrut exams — browse without signing in.'}
          </p>
        </header>

        <div className="space-y-12">
          {groups.map((group) => (
            <section key={group.id}>
              <div className="mb-4">
                <div className="flex items-center gap-3" dir={isHe ? 'rtl' : 'ltr'}>
                  <h2 className="font-display text-xl font-semibold text-foreground">
                    {isHe ? group.he : group.en}
                  </h2>
                  <span className="text-muted-foreground" dir={isHe ? 'ltr' : 'rtl'}>
                    / {isHe ? group.en : group.he}
                  </span>
                </div>
                {group.id === 'bagrut' ? (
                  <p
                    className="mt-1 text-sm text-muted-foreground"
                    dir={isHe ? 'rtl' : 'ltr'}
                  >
                    {isHe
                      ? 'לא בטוח/ה באיזה מסלול את/ה? שאל/י את המורה — מסלול חדש (372/472/572) מ-2023, מסלול ישן (382/482/582) לבגרויות חוזרות'
                      : 'Not sure which track? Ask your teacher — new track (372/472/572) from 2023; old track (382/482/582) for external candidates'}
                  </p>
                ) : group.id === 'makhina' ? (
                  <p
                    className="mt-1 text-sm text-muted-foreground"
                    dir={isHe ? 'rtl' : 'ltr'}
                  >
                    {isHe
                      ? 'הכנה לאוניברסיטה — מתמטיקה ופיזיקה'
                      : 'University preparation — math and physics'}
                  </p>
                ) : null}
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {group.cards.map((s) => (
                  <Fragment key={s.subject}>
                    {group.id === 'bagrut' && s.subject === 'high_school_math_4pt' ? (
                      <UpgradeTrackBanner isHe={isHe} />
                    ) : null}
                    <SubjectCard s={s} isHe={isHe} />
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
