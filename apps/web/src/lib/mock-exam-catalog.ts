import type { MockExamIndexEntry, SeedMockExam } from './mock-exam-seed-types';
import index from './mock-exams/index.json';
import math3pt from './mock-exams/math_3pt_mock_1.json';
import math4pt from './mock-exams/math_4pt_mock_1.json';
import math4ptPaper2 from './mock-exams/math_4pt_paper2_mock_1.json';
import math5pt from './mock-exams/math_5pt_mock_1.json';
import math5ptPaper2 from './mock-exams/math_5pt_paper2_mock_1.json';
import calc1 from './mock-exams/calculus_1_mock_1.json';
import la from './mock-exams/linear_algebra_mock_1.json';
import physics from './mock-exams/hs_physics_mock_1.json';
import physicsMechanics from './mock-exams/hs_physics_mechanics_mock_1.json';
import physicsElectricity from './mock-exams/hs_physics_electricity_mock_1.json';
import universityPhysics1 from './mock-exams/university_physics1_mock_1.json';

export type { MockExamIndexEntry, SeedMockExam } from './mock-exam-seed-types';

const EXAMS: Record<string, SeedMockExam> = {
  math_3pt_mock_1: math3pt as SeedMockExam,
  math_4pt_mock_1: math4pt as SeedMockExam,
  math_4pt_paper2_mock_1: math4ptPaper2 as SeedMockExam,
  math_5pt_mock_1: math5pt as SeedMockExam,
  math_5pt_paper2_mock_1: math5ptPaper2 as SeedMockExam,
  calculus_1_mock_1: calc1 as SeedMockExam,
  linear_algebra_mock_1: la as SeedMockExam,
  hs_physics_mock_1: physics as SeedMockExam,
  hs_physics_mechanics_mock_1: physicsMechanics as SeedMockExam,
  hs_physics_electricity_mock_1: physicsElectricity as SeedMockExam,
  university_physics1_mock_1: universityPhysics1 as SeedMockExam,
};

export const mockExamIndex = index as MockExamIndexEntry[];

export function getMockExamById(id: string): SeedMockExam | null {
  return EXAMS[id] ?? null;
}

export function listMockExams(): MockExamIndexEntry[] {
  return mockExamIndex;
}
