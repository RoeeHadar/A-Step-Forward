export interface SubjectSummary {
  subject: string;
  section_count: number;
  sample_grade: string | null;
}

export interface SectionSummary {
  id: string;
  subject: string;
  grade: string | null;
  source_file: string;
  chunk_index: number;
  title: string;
  title_en: string | null;
  tier: string;
}

export interface SectionDetail extends SectionSummary {
  body_md: string;
  body_html: string | null;
  page_start: number | null;
  page_end: number | null;
}

export interface BagrutExam {
  id: string;
  subject: string;
  exam_type: string;
  year: number | null;
  source_file: string;
  display_name: string;
  file_url: string;
}
