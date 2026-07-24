/**
 * Eval harness for concept-resolver (baseline + future tiered resolver).
 *
 * Runs fully offline — no network, no LLM calls.
 *
 * When `apps/web/src/lib/concept-resolver.ts` exists it is imported and used;
 * otherwise falls back to a local reimplementation of the current substring
 * logic from findRelevantConcepts() in apps/web/src/app/api/chat/route.ts so
 * the baseline numbers are measurable today without the new module.
 *
 * Asserted floors (only these fail CI):
 *   - exact-kind recall ≥ 0.90
 *   - negative false-positive rate ≤ 0.20
 *
 * All other kind metrics (morphology, paraphrase, phenomenon) are reported but
 * NOT gated — they exist to measure the gap that the tiered resolver closes.
 */

import fs from 'node:fs';
import path from 'node:path';
import { beforeAll, describe, expect, it } from 'vitest';
import kg from '@/lib/kg-data.json';

// ── types ────────────────────────────────────────────────────────────────────

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
}

type CaseKind = 'exact' | 'morphology' | 'paraphrase' | 'phenomenon' | 'negative';

interface EvalCase {
  message: string;
  subjects: string[];
  expected: string[];
  kind: CaseKind;
  lang: 'he' | 'en';
}

type ResolveResult = { concepts: KgConcept[]; tier: 'exact' | 'alias' | 'none' };
type ResolveFn = (message: string, subjects: string[]) => ResolveResult;

// ── KG setup ─────────────────────────────────────────────────────────────────

const kgConcepts: KgConcept[] = (kg as { concepts: KgConcept[] }).concepts;

/**
 * Reimplementation of findRelevantConcepts() from apps/web/src/app/api/chat/route.ts
 * (exact copy of the production substring logic, used as baseline fallback).
 */
function baselineResolve(message: string, subjects: string[]): ResolveResult {
  if (!message) return { concepts: [], tier: 'none' };
  const lower = message.toLowerCase();
  const matches: KgConcept[] = [];
  for (const concept of kgConcepts) {
    if (subjects.length && !subjects.includes(concept.subject)) continue;
    const idStr = concept.id.replace(/_/g, ' ');
    if (
      lower.includes(idStr) ||
      lower.includes(concept.name.toLowerCase()) ||
      (concept.name_he && lower.includes(concept.name_he.toLowerCase()))
    ) {
      matches.push(concept);
    }
  }
  const sliced = matches.slice(0, 3);
  return { concepts: sliced, tier: sliced.length > 0 ? 'exact' : 'none' };
}

// ── load cases ───────────────────────────────────────────────────────────────

const casesPath = path.resolve(
  __dirname,
  '../../../../../evals/retrieval/concept-resolver/cases.json',
);
const cases: EvalCase[] = JSON.parse(fs.readFileSync(casesPath, 'utf-8')) as EvalCase[];

// ── resolver (tiered if available, else baseline) ─────────────────────────────

let resolveFn: ResolveFn = baselineResolve;
let resolverMode: 'tiered' | 'baseline' = 'baseline';

beforeAll(async () => {
  try {
    // Dynamically import the new module only when it exists.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const mod = (await import('../concept-resolver')) as any;
    if (typeof mod.resolveConceptsTiered === 'function') {
      resolveFn = mod.resolveConceptsTiered as ResolveFn;
      resolverMode = 'tiered';
    }
  } catch {
    // concept-resolver.ts not yet implemented — using baseline substring logic
  }
});

// ── helpers ───────────────────────────────────────────────────────────────────

function caseHit(c: EvalCase): boolean {
  const result = resolveFn(c.message, c.subjects);
  const returnedIds = result.concepts.map((x) => x.id);
  if (c.kind === 'negative') {
    return returnedIds.length === 0;
  }
  // For non-negative cases: recall = 1 if ANY expected concept was returned
  return c.expected.some((id) => returnedIds.includes(id));
}

type KindStats = {
  total: number;
  hits: number;
  recall: number;
};

function computeStats(subset: EvalCase[]): KindStats {
  const hits = subset.filter(caseHit).length;
  return { total: subset.length, hits, recall: subset.length ? hits / subset.length : 0 };
}

// ── eval suite ────────────────────────────────────────────────────────────────

describe('concept-resolver eval', () => {
  it('reports per-kind metrics and asserts floors', () => {
    const byKind: Record<CaseKind, EvalCase[]> = {
      exact: [],
      morphology: [],
      paraphrase: [],
      phenomenon: [],
      negative: [],
    };
    for (const c of cases) byKind[c.kind].push(c);

    const stats = {
      exact: computeStats(byKind.exact),
      morphology: computeStats(byKind.morphology),
      paraphrase: computeStats(byKind.paraphrase),
      phenomenon: computeStats(byKind.phenomenon),
      // For negatives, "hit" = no false positive returned
      negative: computeStats(byKind.negative),
    };

    const negFpRate =
      byKind.negative.length > 0
        ? byKind.negative.filter((c) => !caseHit(c)).length / byKind.negative.length
        : 0;

    // ── summary table ──────────────────────────────────────────────────────
    const pad = (s: string, n: number) => s.padEnd(n);
    const pct = (r: number) => (r * 100).toFixed(0).padStart(5) + '%';

    console.log('\n');
    console.log(`=== concept-resolver eval  [mode: ${resolverMode}] ===`);
    console.log(
      `${'kind'.padEnd(12)} ${'total'.padStart(5)} ${'hits'.padStart(5)} ${'recall'.padStart(8)}`,
    );
    console.log('-'.repeat(34));
    for (const kind of ['exact', 'morphology', 'paraphrase', 'phenomenon'] as const) {
      const s = stats[kind];
      console.log(`${pad(kind, 12)} ${String(s.total).padStart(5)} ${String(s.hits).padStart(5)} ${pct(s.recall)}`);
    }
    console.log('-'.repeat(34));
    const negStats = stats.negative;
    const negFpCount = negStats.total - negStats.hits;
    console.log(
      `${pad('negative', 12)} ${String(negStats.total).padStart(5)}   FP=${negFpCount}  FP-rate=${pct(negFpRate)}`,
    );
    console.log('');

    // ── floors (only these fail CI) ───────────────────────────────────────
    expect(
      stats.exact.recall,
      `exact recall too low (${stats.exact.hits}/${stats.exact.total}); expected ≥ 0.90`,
    ).toBeGreaterThanOrEqual(0.9);

    expect(
      negFpRate,
      `negative false-positive rate too high (${negFpCount}/${negStats.total}); expected ≤ 0.20`,
    ).toBeLessThanOrEqual(0.2);
  });

  // ── per-case detail on failures (informational only, never throws) ─────────
  it('logs failing cases per kind for diagnostics', () => {
    const failing: Record<string, EvalCase[]> = {};
    for (const c of cases) {
      if (!caseHit(c)) {
        const key = c.kind;
        if (!failing[key]) failing[key] = [];
        failing[key].push(c);
      }
    }

    if (Object.keys(failing).length === 0) {
      console.log('[concept-resolver eval] All cases passed!');
      return;
    }

    console.log('\n=== Failing cases by kind ===');
    for (const [kind, fails] of Object.entries(failing)) {
      console.log(`\n-- ${kind} (${fails.length} failing) --`);
      for (const f of fails) {
        const result = resolveFn(f.message, f.subjects);
        const got = result.concepts.map((c) => c.id).join(', ') || '(none)';
        const want = f.expected.join(', ') || '(none)';
        console.log(`  msg:  "${f.message}" [${f.lang}]`);
        console.log(`  want: ${want}  →  got: ${got}  (tier: ${result.tier})`);
      }
    }
    // Intentionally no expect() here — diagnostic only.
  });
});
