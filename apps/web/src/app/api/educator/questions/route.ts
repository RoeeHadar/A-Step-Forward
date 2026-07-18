/**
 * GET /api/educator/questions
 *
 * Educator/admin-only retrieval from the internal question store for building
 * quizzes/tests on the fly. Structured-filter-first; returns verified items
 * only. Learners are never authorized here (RBAC per .cursor/skills/security-safety).
 *
 * Query params:
 *   concept   (required) concept_id
 *   difficulty  easy|medium|hard
 *   atoms       comma-separated skill_atom ids (match ANY)
 *   level       high_school|university|...
 *   points      3pt|4pt|5pt
 *   limit       1..50 (default 10)
 */
import { getAuthContext, requireRole } from '@/lib/auth';
import { retrieveQuestions, type QuestionDifficulty } from '@/lib/question-store';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function parseDifficulty(value: string | null): QuestionDifficulty | undefined {
  if (value === 'easy' || value === 'medium' || value === 'hard') return value;
  return undefined;
}

export async function GET(req: Request) {
  const ctx = await getAuthContext();
  if (!ctx) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  try {
    requireRole(ctx, ['educator', 'admin']);
  } catch {
    return Response.json({ error: 'Forbidden' }, { status: 403 });
  }

  const { searchParams } = new URL(req.url);
  const conceptId = searchParams.get('concept')?.trim();
  if (!conceptId) {
    return Response.json({ error: 'concept is required' }, { status: 400 });
  }

  const atomsRaw = searchParams.get('atoms');
  const skillAtoms = atomsRaw
    ? atomsRaw.split(',').map((a) => a.trim()).filter(Boolean)
    : undefined;
  const limitRaw = Number(searchParams.get('limit') ?? '10');
  const limit = Number.isFinite(limitRaw) ? limitRaw : 10;

  try {
    const items = await retrieveQuestions({
      conceptId,
      difficulty: parseDifficulty(searchParams.get('difficulty')),
      skillAtoms,
      level: searchParams.get('level')?.trim() || undefined,
      pointsLevel: searchParams.get('points')?.trim() || undefined,
      limit,
      gradedOnly: true,
    });
    return Response.json({ items, count: items.length });
  } catch (err) {
    return Response.json(
      { error: 'question retrieval failed', detail: err instanceof Error ? err.message : String(err) },
      { status: 503 },
    );
  }
}
