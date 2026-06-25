import { API_BASE_URL } from '@/lib/api';
import {
  bagrutExamListSchema,
  contentSectionsPageSchema,
  contentSectionSchema,
  subjectListSchema,
  type BagrutExam,
  type ContentSection,
  type ContentSectionsPage,
  type SubjectSummary,
} from '@asf/schemas/content';

export type { BagrutExam, ContentSection, ContentSectionsPage, SubjectSummary };

export interface SectionSummary {
  chunk_index: number;
  title: string;
  grade: string | null;
}

async function contentFetchServer<T>(path: string, schema: { parse: (data: unknown) => T }): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) {
    throw new Error(`Content API ${res.status} on ${path}`);
  }
  const data: unknown = await res.json();
  return schema.parse(data);
}

async function contentFetchClient<T>(path: string, schema: { parse: (data: unknown) => T }): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Content API ${res.status} on ${path}`);
  }
  const data: unknown = await res.json();
  return schema.parse(data);
}

export async function fetchSubjects(): Promise<SubjectSummary[]> {
  try {
    return await contentFetchServer('/v1/content/subjects', subjectListSchema);
  } catch {
    return [];
  }
}

export async function fetchSectionsPage(
  subject: string,
  options: { grade?: string; page?: number; page_size?: number } = {},
  client = false,
): Promise<ContentSectionsPage> {
  const params = new URLSearchParams();
  if (options.grade) params.set('grade', options.grade);
  if (options.page) params.set('page', String(options.page));
  if (options.page_size) params.set('page_size', String(options.page_size));
  const qs = params.toString();
  const path = `/v1/content/subjects/${encodeURIComponent(subject)}/sections${qs ? `?${qs}` : ''}`;
  const fetcher = client ? contentFetchClient : contentFetchServer;
  return fetcher(path, contentSectionsPageSchema);
}

export async function fetchSection(subject: string, chunkIndex: number): Promise<ContentSection | null> {
  try {
    return await contentFetchServer(
      `/v1/content/subjects/${encodeURIComponent(subject)}/sections/${chunkIndex}`,
      contentSectionSchema,
    );
  } catch {
    return null;
  }
}

export async function fetchSectionSummaries(subject: string): Promise<SectionSummary[]> {
  try {
    const summaries: SectionSummary[] = [];
    let page = 1;
    let total = 0;
    do {
      const result = await fetchSectionsPage(subject, { page, page_size: 100 });
      total = result.total;
      summaries.push(
        ...result.items.map((s) => ({
          chunk_index: s.chunk_index ?? 0,
          title: s.title,
          grade: s.grade,
        })),
      );
      page += 1;
    } while (summaries.length < total);
    return summaries;
  } catch {
    return [];
  }
}

export async function fetchSectionGrades(subject: string): Promise<string[]> {
  try {
    const summaries = await fetchSectionSummaries(subject);
    return [...new Set(summaries.map((s) => s.grade).filter(Boolean))] as string[];
  } catch {
    return [];
  }
}

export async function fetchBagrutExams(subject: string): Promise<BagrutExam[]> {
  try {
    return await contentFetchServer(
      `/v1/content/subjects/${encodeURIComponent(subject)}/bagrut`,
      bagrutExamListSchema,
    );
  } catch {
    return [];
  }
}
