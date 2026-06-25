import { redirect } from 'next/navigation';

export const dynamic = 'force-dynamic';

export default async function BagrutPage({ params }: { params: Promise<{ subject: string }> }) {
  const { subject } = await params;
  redirect(`/learn/${subject}?tab=bagrut`);
}
