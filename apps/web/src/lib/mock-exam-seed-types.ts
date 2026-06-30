/** Static seed mock exams — Bagrut / university open-ended format. */

export interface MockExamOpenQuestion {
  id: string;
  type: 'open';
  points: number;
  body_en: string;
  body_he: string;
  expected_steps_en: string[];
  expected_steps_he: string[];
  sample_solution_en: string;
  sample_solution_he: string;
  rubric_en: string;
  rubric_he: string;
}

export interface MockExamSection {
  id: string;
  title_en: string;
  title_he: string;
  points: number;
  instructions_en: string;
  instructions_he: string;
  choose: number;
  questions: MockExamOpenQuestion[];
}

export interface SeedMockExam {
  id: string;
  subject: string;
  title_en: string;
  title_he: string;
  duration_min: number;
  instructions_en: string;
  instructions_he: string;
  /** e.g. "accumulation" — best N answers count toward max_score */
  scoring?: string;
  max_score?: number;
  sections: MockExamSection[];
}

export interface MockExamIndexEntry {
  id: string;
  subject: string;
  title_en: string;
  title_he: string;
  duration_min: number;
}
