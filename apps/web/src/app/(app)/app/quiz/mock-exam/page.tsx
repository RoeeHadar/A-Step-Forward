import { MockExamClient } from '@/components/mock-exam-client';
import { getMockExamById, listMockExams } from '@/lib/mock-exam-catalog';
import type { SeedMockExam } from '@/lib/mock-exam-seed-types';

export default async function MockExamPage({
  searchParams,
}: {
  searchParams: Promise<{ id?: string }>;
}) {
  const params = await searchParams;
  const exams = listMockExams();
  // Serializable map only — never pass getMockExamById (functions cannot cross RSC → client).
  const examsById: Record<string, SeedMockExam> = {};
  for (const entry of exams) {
    const full = getMockExamById(entry.id);
    if (full) examsById[entry.id] = full;
  }

  return (
    <MockExamClient
      exams={exams}
      examsById={examsById}
      initialExamId={params.id ?? null}
    />
  );
}
