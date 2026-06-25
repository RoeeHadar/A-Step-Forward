import { API_BASE_URL } from '@/lib/api';

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

async function contentFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) {
    throw new Error(`Content API ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchSubjects(): Promise<SubjectSummary[]> {
  try {
    return await contentFetch<SubjectSummary[]>('/v1/subjects');
  } catch {
    return [];
  }
}

export async function fetchSections(subject: string): Promise<SectionSummary[]> {
  try {
    return await contentFetch<SectionSummary[]>(`/v1/subjects/${encodeURIComponent(subject)}/sections`);
  } catch {
    return [];
  }
}

export async function fetchSection(subject: string, chunkIndex: number): Promise<SectionDetail | null> {
  try {
    return await contentFetch<SectionDetail>(
      `/v1/subjects/${encodeURIComponent(subject)}/sections/${chunkIndex}`,
    );
  } catch {
    return null;
  }
}

export async function fetchBagrutExams(subject: string): Promise<BagrutExam[]> {
  try {
    return await contentFetch<BagrutExam[]>(`/v1/subjects/${encodeURIComponent(subject)}/bagrut`);
  } catch {
    return [];
  }
}
