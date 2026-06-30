import { MockExamClient } from '@/components/mock-exam-client';
import { getMockExamById, listMockExams } from '@/lib/mock-exam-catalog';

export default async function MockExamPage({
  searchParams,
}: {
  searchParams: Promise<{ id?: string }>;
}) {
  const params = await searchParams;
  const exams = listMockExams();

  return (
    <MockExamClient
      exams={exams}
      getExam={getMockExamById}
      initialExamId={params.id ?? null}
    />
  );
}
