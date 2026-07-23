import { redirect } from 'next/navigation';

/** Canonical practice arena lives under the app shell. */
export default async function PracticeRedirect({
  searchParams,
}: {
  searchParams: Promise<{ concept?: string; mode?: string }>;
}) {
  const sp = await searchParams;
  const params = new URLSearchParams();
  if (typeof sp.concept === 'string' && sp.concept.trim()) {
    params.set('concept', sp.concept.trim());
  }
  if (sp.mode === 'due') params.set('mode', 'due');
  const q = params.toString();
  redirect(`/app/practice${q ? `?${q}` : ''}`);
}
