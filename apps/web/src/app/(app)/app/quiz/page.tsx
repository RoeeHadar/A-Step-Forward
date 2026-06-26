/**
 * /app/quiz — Build a fit-to-purpose AI quiz.
 *
 * Server-side responsibilities are minimal: authenticate the learner, ship
 * the KG concept list down to the client (so the topic picker doesn't need
 * a network round-trip), and render <QuizPageClient/>. The actual quiz
 * generation happens via POST /api/quiz/custom inside the client.
 */
import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { QuizPageClient, type TopicOption } from '@/components/quiz-page-client';
import kg from '@/lib/kg-data.json';

export const dynamic = 'force-dynamic';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
}

const SUBJECT_LABELS: Record<string, { en: string; he: string }> = {
  math: { en: 'Math', he: 'מתמטיקה' },
  physics: { en: 'Physics', he: 'פיזיקה' },
  chemistry: { en: 'Chemistry', he: 'כימיה' },
  biology: { en: 'Biology', he: 'ביולוגיה' },
  cs: { en: 'Computer Science', he: 'מדעי המחשב' },
  english: { en: 'English', he: 'אנגלית' },
};

export default async function QuizPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const concepts = (kg as { concepts: KgConcept[] }).concepts;
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
