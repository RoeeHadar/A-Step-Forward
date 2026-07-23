/**
 * /app/practice — intensive practice arena (ADR-0013).
 */
import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { PracticeArenaClient } from '@/components/practice-arena-client';

export const dynamic = 'force-dynamic';

export default async function PracticePage({
  searchParams,
}: {
  searchParams: Promise<{ concept?: string }>;
}) {
  const ctx = await getAuthContext();
  if (!ctx) redirect('/sign-in');
  const sp = await searchParams;
  const concept =
    typeof sp.concept === 'string' && sp.concept.trim() ? sp.concept.trim() : null;

  return <PracticeArenaClient initialConceptId={concept} />;
}
