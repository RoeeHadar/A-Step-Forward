import { redirect } from 'next/navigation';

/** Canonical practice arena lives under the app shell. */
export default async function PracticeRedirect({
  searchParams,
}: {
  searchParams: Promise<{ concept?: string }>;
}) {
  const sp = await searchParams;
  const q =
    typeof sp.concept === 'string' && sp.concept.trim()
      ? `?concept=${encodeURIComponent(sp.concept.trim())}`
      : '';
  redirect(`/app/practice${q}`);
}
