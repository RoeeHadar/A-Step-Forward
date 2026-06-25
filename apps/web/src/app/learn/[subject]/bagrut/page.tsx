import { notFound } from 'next/navigation';
import { BagrutPageClient } from '@/components/bagrut-page-client';
import { fetchBagrutExams, fetchSubjects } from '@/lib/content-api';

export const dynamic = 'force-dynamic';

export default async function BagrutPage({ params }: { params: Promise<{ subject: string }> }) {
  const { subject } = await params;
  const allSubjects = await fetchSubjects();
  const exams = await fetchBagrutExams(subject);

  if (exams.length === 0) {
    const known = allSubjects.some((s) => s.subject === subject);
    if (!known) notFound();
    notFound();
  }

  return <BagrutPageClient subject={subject} exams={exams} />;
}
