/**
 * Direct-from-Neon content fetcher.
 *
 * The /learn page is public free-tier content, so we bypass the Render
 * backend entirely and read straight from Neon over HTTP. This makes the
 * page resilient to backend cold-starts and outages.
 *
 * Uses @neondatabase/serverless which is HTTP-based — no TCP pool, works
 * on Vercel edge/serverless runtimes.
 */
import 'server-only';
import { neon } from '@neondatabase/serverless';
import type {
  BagrutExam,
  SectionDetail,
  SectionSummary,
  SubjectSummary,
} from './content-types';

const databaseUrl = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';

/**
 * `true` when a Neon DATABASE_URL is configured.
 * If false, callers should fall back to the Render API path.
 */
export const neonConfigured = Boolean(databaseUrl);

const sql = neonConfigured ? neon(databaseUrl) : null;

export async function neonFetchSubjects(): Promise<SubjectSummary[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT s.subject,
             COALESCE(cs.cnt, 0)::int AS section_count,
             cs.sample_grade
      FROM (
        SELECT DISTINCT subject FROM content_sections
        UNION
        SELECT DISTINCT subject FROM bagrut_exams
      ) s
      LEFT JOIN (
        SELECT subject, COUNT(*)::int AS cnt, MAX(grade) AS sample_grade
        FROM content_sections
        GROUP BY subject
      ) cs ON s.subject = cs.subject
      ORDER BY s.subject
    `) as Array<{ subject: string; section_count: number; sample_grade: string | null }>;
    return rows;
  } catch (err) {
    console.error('[neon-content] fetchSubjects failed', err);
    return [];
  }
}

export async function neonFetchSections(subject: string): Promise<SectionSummary[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT id::text, subject, grade, source_file, chunk_index, title, title_en, tier
      FROM content_sections
      WHERE subject = ${subject}
      ORDER BY chunk_index
    `) as Array<SectionSummary>;
    return rows;
  } catch (err) {
    console.error('[neon-content] fetchSections failed', err);
    return [];
  }
}

export async function neonFetchSection(
  subject: string,
  chunkIndex: number,
): Promise<SectionDetail | null> {
  if (!sql) return null;
  try {
    const rows = (await sql`
      SELECT id::text, subject, grade, source_file, chunk_index, title, title_en,
             body_md, body_html, page_start, page_end, tier
      FROM content_sections
      WHERE subject = ${subject} AND chunk_index = ${chunkIndex}
      LIMIT 1
    `) as Array<SectionDetail>;
    return rows[0] ?? null;
  } catch (err) {
    console.error('[neon-content] fetchSection failed', err);
    return null;
  }
}

export async function neonFetchBagrutExams(subject: string): Promise<BagrutExam[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT id::text, subject, exam_type, year, source_file, display_name, file_url
      FROM bagrut_exams
      WHERE subject = ${subject}
      ORDER BY year DESC NULLS LAST, display_name
    `) as Array<BagrutExam>;
    return rows;
  } catch (err) {
    console.error('[neon-content] fetchBagrutExams failed', err);
    return [];
  }
}
