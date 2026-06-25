import { API_BASE_URL } from '@/lib/api';
import {
  neonConfigured,
  neonFetchBagrutExams,
  neonFetchSection,
  neonFetchSections,
  neonFetchSubjects,
} from '@/lib/neon-content';
import type {
  BagrutExam,
  SectionDetail,
  SectionSummary,
  SubjectSummary,
} from '@/lib/content-types';

export type { BagrutExam, SectionDetail, SectionSummary, SubjectSummary };

async function contentFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) {
    throw new Error(`Content API ${res.status} on ${path}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchSubjects(): Promise<SubjectSummary[]> {
  if (neonConfigured) {
    const rows = await neonFetchSubjects();
    if (rows.length > 0) return rows;
  }
  try {
    return await contentFetch<SubjectSummary[]>('/v1/subjects');
  } catch {
    return [];
  }
}

export async function fetchSections(subject: string): Promise<SectionSummary[]> {
  if (neonConfigured) {
    const rows = await neonFetchSections(subject);
    if (rows.length > 0) return rows;
  }
  try {
    return await contentFetch<SectionSummary[]>(
      `/v1/subjects/${encodeURIComponent(subject)}/sections`,
    );
  } catch {
    return [];
  }
}

export async function fetchSection(
  subject: string,
  chunkIndex: number,
): Promise<SectionDetail | null> {
  if (neonConfigured) {
    const row = await neonFetchSection(subject, chunkIndex);
    if (row) return row;
  }
  try {
    return await contentFetch<SectionDetail>(
      `/v1/subjects/${encodeURIComponent(subject)}/sections/${chunkIndex}`,
    );
  } catch {
    return null;
  }
}

export async function fetchBagrutExams(subject: string): Promise<BagrutExam[]> {
  if (neonConfigured) {
    const rows = await neonFetchBagrutExams(subject);
    if (rows.length > 0) return rows;
  }
  try {
    return await contentFetch<BagrutExam[]>(
      `/v1/subjects/${encodeURIComponent(subject)}/bagrut`,
    );
  } catch {
    return [];
  }
}
