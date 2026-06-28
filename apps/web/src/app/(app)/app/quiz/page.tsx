/**
 * /app/quiz — Build a fit-to-purpose AI quiz.
 *
 * Server-side responsibilities:
 *  1. Authenticate the learner
 *  2. Fetch the learner's points_group from their profile
 *  3. Filter the KG concept list to only include concepts appropriate for the
 *     learner's level — a 4pt student should NOT see 5pt/calc/LA concepts
 *  4. Render <QuizPageClient/>
 *
 * The actual quiz generation happens via POST /api/quiz/custom inside the client.
 */
import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { getLearnerProfile, dbConfigured } from '@/lib/neon-db';
import { QuizPageClient, type TopicOption } from '@/components/quiz-page-client';
import kg from '@/lib/kg-data.json';

export const dynamic = 'force-dynamic';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  points_levels?: string[];
}

const SUBJECT_LABELS: Record<string, { en: string; he: string }> = {
  math: { en: 'Math', he: 'מתמטיקה' },
  physics: { en: 'Physics', he: 'פיזיקה' },
  chemistry: { en: 'Chemistry', he: 'כימיה' },
  biology: { en: 'Biology', he: 'ביולוגיה' },
  cs: { en: 'Computer Science', he: 'מדעי המחשב' },
  english: { en: 'English', he: 'אנגלית' },
};

/**
 * Given a learner's points_group (e.g. "4pt"), return the set of
 * points_levels that should be visible to them.
 * A 4pt student sees 3pt + 4pt topics (they should master the lower level too).
 * Physics students see hs_physics topics.
 */
function allowedLevels(pointsGroup: string | null | undefined): Set<string> {
  switch (pointsGroup) {
    case '3pt':
      return new Set(['3pt']);
    case '4pt':
      return new Set(['3pt', '4pt']);
    case '5pt':
      return new Set(['3pt', '4pt', '5pt']);
    case 'hs_physics':
      return new Set(['hs_physics', '3pt', '4pt']);
    case 'calc1':
    case 'la':
    case 'physics1':
      return new Set(['3pt', '4pt', '5pt', 'calc1', 'la', 'hs_physics']);
    default:
      return new Set(); // no filter — show everything
  }
}

export default async function QuizPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  // Fetch learner's points_group to filter topics
  let pointsGroup: string | null = null;
  if (dbConfigured) {
    try {
      const profile = await getLearnerProfile(auth.learnerId);
      pointsGroup = profile?.points_group ?? null;
    } catch {
      // silently fall back to showing all concepts
    }
  }

  const allowed = allowedLevels(pointsGroup);
  const allConcepts = (kg as { concepts: KgConcept[] }).concepts;

  // Filter concepts if we know the learner's level; otherwise show all
  const concepts =
    allowed.size > 0
      ? allConcepts.filter((c) => {
          const cLevels: string[] = c.points_levels ?? [];
          // Show concept if it has at least one level the student is allowed to see
          return cLevels.length === 0 || cLevels.some((l) => allowed.has(l));
        })
      : allConcepts;

  const topics: TopicOption[] = concepts.map((c) => ({
    id: c.id,
    name: c.name,
    name_he: c.name_he,
    subject: c.subject,
    subject_label_en: SUBJECT_LABELS[c.subject]?.en ?? c.subject,
    subject_label_he: SUBJECT_LABELS[c.subject]?.he ?? c.subject,
  }));

  return <QuizPageClient topics={topics} />;
}
