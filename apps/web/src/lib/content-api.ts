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
  // Hard cap so a dead Render instance can't time-out the Vercel function.
  // Once /learn fully runs on Neon, the Render fallback is best-effort polish.
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 4000);
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      next: { revalidate: 300 },
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`Content API ${res.status} on ${path}`);
    return (await res.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

const STATIC_SUBJECT_FALLBACK: SubjectSummary[] = [
  { subject: 'math', section_count: 0, sample_grade: null },
  { subject: 'physics', section_count: 0, sample_grade: null },
  { subject: 'biology_4pt', section_count: 0, sample_grade: null },
  { subject: 'biology_5pt', section_count: 0, sample_grade: null },
  { subject: 'makhina', section_count: 0, sample_grade: null },
  { subject: 'calculus', section_count: 0, sample_grade: null },
  { subject: 'linear_algebra', section_count: 0, sample_grade: null },
];

const CURATED_SUBJECT_SLUGS = [
  'biology_4pt',
  'biology_5pt',
  'makhina',
  'calculus',
  'linear_algebra',
] as const;

function mergeCuratedSubjects(rows: SubjectSummary[]): SubjectSummary[] {
  const bySlug = new Map(rows.map((r) => [r.subject, r]));
  for (const slug of CURATED_SUBJECT_SLUGS) {
    if (!bySlug.has(slug)) {
      bySlug.set(slug, { subject: slug, section_count: 0, sample_grade: null });
    }
  }
  return [...bySlug.values()].sort((a, b) => a.subject.localeCompare(b.subject));
}

export async function fetchSubjects(): Promise<SubjectSummary[]> {
  if (neonConfigured) {
    const rows = await neonFetchSubjects();
    if (rows.length > 0) return mergeCuratedSubjects(rows);
  }
  try {
    const rows = await contentFetch<SubjectSummary[]>('/v1/subjects');
    if (rows.length > 0) return mergeCuratedSubjects(rows);
  } catch {
    // Render is best-effort: ignore failures and show the static fallback below.
  }
  return STATIC_SUBJECT_FALLBACK;
}

export async function fetchSections(subject: string): Promise<SectionSummary[]> {
  if (neonConfigured) {
    return await neonFetchSections(subject);
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
    return await neonFetchSection(subject, chunkIndex);
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
    return await neonFetchBagrutExams(subject);
  }
  try {
    return await contentFetch<BagrutExam[]>(
      `/v1/subjects/${encodeURIComponent(subject)}/bagrut`,
    );
  } catch {
    return [];
  }
}
