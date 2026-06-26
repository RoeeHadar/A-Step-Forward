import { redirect } from 'next/navigation';

// Legacy PDF chunk URLs are deprecated in favor of AI-authored lessons under
// `/learn/[subject]/concept/[conceptId]`. Permanently redirect to the subject
// index so search engines drop the old URLs and learners land on the new
// lesson grid.
export const dynamic = 'force-dynamic';

export default async function LegacyChunkRedirect({
  params,
}: {
  params: Promise<{ subject: string; chunkIndex: string }>;
}) {
  const { subject } = await params;
  redirect(`/learn/${subject}`);
}
