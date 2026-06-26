/**
 * TEMPORARY diagnostic endpoint. Returns the count, first few rows, and any
 * connection errors for concept_explanations so we can quickly verify the
 * Vercel function is talking to the same Neon DB that the scraper wrote to.
 *
 * Remove once /learn/[subject]/concept/[id] is verified working in prod.
 */
import { neon } from '@neondatabase/serverless';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
  if (!url) {
    return Response.json({ ok: false, reason: 'DATABASE_URL not set' });
  }
  const sql = neon(url);
  try {
    const tableExists = (await sql`
      SELECT EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_name = 'concept_explanations'
      ) AS exists
    `) as Array<{ exists: boolean }>;

    const count = (await sql`SELECT COUNT(*)::int AS c FROM concept_explanations`) as Array<{
      c: number;
    }>;

    const sample = (await sql`
      SELECT concept_id, language, title, LEFT(body_md, 80) AS preview
      FROM concept_explanations
      ORDER BY concept_id, language
      LIMIT 6
    `) as Array<{ concept_id: string; language: string; title: string; preview: string }>;

    const algebra = (await sql`
      SELECT concept_id, language, title
      FROM concept_explanations
      WHERE concept_id = 'algebra_basics'
    `) as Array<{ concept_id: string; language: string; title: string }>;

    return Response.json({
      ok: true,
      database_host: url.split('@')[1]?.split('/')[0] ?? 'unknown',
      table_exists: tableExists[0]?.exists,
      row_count: count[0]?.c ?? 0,
      sample,
      algebra_basics_rows: algebra,
    });
  } catch (err) {
    return Response.json({ ok: false, reason: String(err) }, { status: 500 });
  }
}
