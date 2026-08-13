import { redirect } from 'next/navigation';

/** Canonical practice arena lives under the app shell. */
export default async function PracticeRedirect({
  searchParams,
}: {
  searchParams: Promise<{ concept?: string; mode?: string; topics?: string }>;
}) {
  const sp = await searchParams;
  const params = new URLSearchParams();
  if (typeof sp.concept === 'string' && sp.concept.trim()) {
    params.set('concept', sp.concept.trim());
  }
  if (typeof sp.mode === 'string' && sp.mode.trim()) {
    params.set('mode', sp.mode.trim());
  }
  if (typeof sp.topics === 'string' && sp.topics.trim()) {
    params.set('topics', sp.topics.trim());
  }
  const q = params.toString();
  redirect(`/app/practice${q ? `?${q}` : ''}`);
}
