/**
 * AS-87 r1: the educator ?points= filter must restore exactly the 45 items that
 * AS-85 retagged to points_level 3pt (functions_exponential 4pt 15,
 * linear_programming 4pt 15, function_transformations 5pt 15) and change no
 * other (points, concept) count.
 *
 * The Neon client is replaced with an in-memory evaluator over the generated
 * store. It understands only the WHERE shapes retrieveQuestions emits (others
 * throw) and records the uncapped match count, so per-pair educator counts are
 * measured through the real SQL builder without a DB.
 */
import fs from 'node:fs';
import path from 'node:path';
import { beforeAll, describe, expect, it, vi } from 'vitest';

type Row = Record<string, unknown> & { id: string; concept_id: string; points_level: string | null; math_track: string[] };

const STORE_DIR = path.resolve(__dirname, '../../../../content/question-store/generated');
const rows: Row[] = [];
for (const f of fs.readdirSync(STORE_DIR).filter((n) => n.endsWith('.json')).sort()) {
  const data = JSON.parse(fs.readFileSync(path.join(STORE_DIR, f), 'utf8'));
  for (const [i, it] of (Array.isArray(data) ? data : data.items ?? []).entries()) {
    // The committed store is all 'unverified'; mark rows verified so gradedOnly retrieval is exercised.
    rows.push({ ...it, id: `${f}#${i}`, math_track: it.math_track ?? [], verification_status: 'auto_verified' });
  }
}

let lastMatches: Row[] = [];
function evaluate(text: string, values: unknown[]): Row[] {
  const where = /WHERE ([\s\S]*?)\n\s*ORDER BY/.exec(text)?.[1] ?? '';
  const preds = where.split(' AND ').map((c) => {
    const v = (n: string) => values[Number(n) - 1];
    let m: RegExpExecArray | null;
    if ((m = /^concept_id = \$(\d+)$/.exec(c))) { const x = v(m[1]!); return (r: Row) => r.concept_id === x; }
    if ((m = /^points_level = \$(\d+)$/.exec(c))) { const x = v(m[1]!); return (r: Row) => r.points_level === x; }
    if ((m = /^math_track @> ARRAY\[\$(\d+)\]::text\[\]$/.exec(c))) { const x = v(m[1]!) as string; return (r: Row) => r.math_track.includes(x); }
    if ((m = /^verification_status = ANY\(\$(\d+)::text\[\]\)$/.exec(c))) { const x = v(m[1]!) as string[]; return (r: Row) => x.includes(r.verification_status as string); }
    throw new Error(`unsupported condition in test evaluator: ${c}`);
  });
  lastMatches = rows.filter((r) => preds.every((p) => p(r)));
  return lastMatches.slice(0, Number(values[values.length - 1]));
}

vi.mock('@neondatabase/serverless', () => ({
  neonConfig: {},
  neon: () => ({ query: async (text: string, values: unknown[]) => evaluate(text, values) }),
}));

let retrieveQuestions: typeof import('./question-store').retrieveQuestions;
beforeAll(async () => {
  process.env.DATABASE_URL = 'postgres://placeholder';
  ({ retrieveQuestions } = await import('./question-store'));
});

const RESTORED: Record<string, { points: string; n: number }> = {
  functions_exponential: { points: '4pt', n: 15 },
  linear_programming: { points: '4pt', n: 15 },
  function_transformations: { points: '5pt', n: 15 },
};
const concepts = [...new Set(rows.map((r) => r.concept_id))].sort();
const levels = [...new Set(rows.flatMap((r) => [r.points_level ?? '', ...r.math_track]).filter(Boolean))].sort();

async function educatorCount(concept: string, points: string): Promise<Row[]> {
  await retrieveQuestions({ conceptId: concept, pointsLevel: points, limit: 50 });
  return lastMatches;
}

describe('educator ?points= filter (AS-87 r1)', () => {
  it('pins the 45 restored items by id', async () => {
    const ids: string[] = [];
    for (const [c, { points }] of Object.entries(RESTORED)) {
      for (const r of await educatorCount(c, points)) if (r.points_level !== points) ids.push(r.id);
    }
    expect(ids.length).toBe(45);
    expect(ids.every((id) => /^(functions_exponential|linear_programming|function_transformations)\.json#\d+$/.test(id))).toBe(true);
  });

  it('per-(points, concept) diff vs exact match: +30 4pt, +15 5pt on the 3 pairs, 0 elsewhere', async () => {
    const lines: string[] = ['points\tconcept\texact\teducator\tdelta'];
    const totals: Record<string, { exact: number; educator: number }> = {};
    let nonzero = 0;
    for (const p of levels) {
      for (const c of concepts) {
        const exact = rows.filter((r) => r.concept_id === c && r.points_level === p).length;
        const edu = (await educatorCount(c, p)).length;
        const t = (totals[p] ??= { exact: 0, educator: 0 });
        t.exact += exact; t.educator += edu;
        const want = RESTORED[c]?.points === p ? RESTORED[c]!.n : 0;
        if (edu - exact !== 0) nonzero++;
        if (exact || edu) lines.push(`${p}\t${c}\t${exact}\t${edu}\t${edu - exact >= 0 ? '+' : ''}${edu - exact}`);
        expect({ p, c, delta: edu - exact }).toEqual({ p, c, delta: want });
      }
    }
    lines.push(`# pairs checked: ${levels.length * concepts.length}; nonzero-delta pairs: ${nonzero}`);
    for (const [p, t] of Object.entries(totals)) lines.push(`# total ${p}: exact ${t.exact} educator ${t.educator} delta ${t.educator - t.exact}`);
    if (process.env.AS87_DIFF_OUT) fs.writeFileSync(process.env.AS87_DIFF_OUT, lines.join('\n') + '\n');
    expect(nonzero).toBe(3);
    // Educator totals equal the pre-AS-85 store for 4pt/5pt (301 / 2145); 3pt keeps AS-85's 715.
    expect(totals['3pt']).toEqual({ exact: 715, educator: 715 });
    expect(totals['4pt']).toEqual({ exact: 271, educator: 301 });
    expect(totals['5pt']).toEqual({ exact: 2130, educator: 2145 });
  });
});
