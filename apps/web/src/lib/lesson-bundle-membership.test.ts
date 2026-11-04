import fs from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import bundle from './lessons-bundle.generated.json';
import lessonsIndex from './lessons-index.generated.json';
import { CONCEPT_ID_ALIASES, resolveConceptAlias } from './concept-aliases';
import { isConceptInBundle } from './lesson-bundle-membership';

const byId = bundle as unknown as Record<string, unknown>;
const has = (id: string) => Object.hasOwn(byId, id);

/** The pre-M6 lookup, reimplemented against the full bundle. */
function oldIsConceptInBundle(id: string): boolean {
  if (has(id)) return true;
  const canonical = resolveConceptAlias(id);
  if (has(canonical)) return true;
  const mapped = Object.hasOwn(CONCEPT_ID_ALIASES, id) ? CONCEPT_ID_ALIASES[id] : undefined;
  return mapped != null && has(mapped);
}

describe('isConceptInBundle without the bundle (M6)', () => {
  it('lesson index and bundle hold exactly the same concept ids', () => {
    const indexIds = (lessonsIndex as { id: string }[]).map((e) => e.id).sort();
    expect(indexIds).toEqual(Object.keys(byId).sort());
  });

  it('gives the same answer as the bundle lookup', () => {
    const probes = new Set<string>([
      ...Object.keys(byId),
      ...Object.keys(CONCEPT_ID_ALIASES),
      ...Object.values(CONCEPT_ID_ALIASES),
      ...Object.keys(byId).map((k) => `${k}_x`),
      'not_a_concept',
      '',
    ]);
    const diffs = [...probes].filter((id) => isConceptInBundle(id) !== oldIsConceptInBundle(id));
    expect(diffs).toEqual([]);
    expect(isConceptInBundle(Object.keys(byId)[0] ?? '')).toBe(true);
    const alias = Object.keys(CONCEPT_ID_ALIASES).find((a) => !has(a) && has(CONCEPT_ID_ALIASES[a] ?? ''));
    if (alias) expect(isConceptInBundle(alias)).toBe(true);
    expect(isConceptInBundle('not_a_concept')).toBe(false);
  });

  it('does not treat Object.prototype keys as lessons', () => {
    expect(isConceptInBundle('constructor')).toBe(false);
    expect(isConceptInBundle('__proto__')).toBe(false);
  });
});

describe('client components cannot reach the lesson bundle (M6)', () => {
  const SRC = path.resolve(__dirname, '..');
  const IMPORT_RE = /(?:import|export)\s[^'"]*?from\s*['"]([^'"]+)['"]|import\s*\(\s*['"]([^'"]+)['"]\s*\)|import\s+['"]([^'"]+)['"]/g;
  const EXTS = ['', '.ts', '.tsx', '/index.ts', '/index.tsx'];

  function resolve(from: string, spec: string): string | null {
    let base: string;
    if (spec.startsWith('@/')) base = path.join(SRC, spec.slice(2));
    else if (spec.startsWith('.')) base = path.resolve(path.dirname(from), spec);
    else return null;
    for (const ext of EXTS) {
      const f = base + ext;
      if (fs.existsSync(f) && fs.statSync(f).isFile()) return f;
    }
    return null;
  }

  function walk(dir: string, out: string[] = []): string[] {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p, out);
      else if (/\.(ts|tsx)$/.test(e.name) && !/\.test\.tsx?$/.test(e.name)) out.push(p);
    }
    return out;
  }

  it('no import path from a "use client" file leads to lessons-bundle.generated.json', () => {
    const clientRoots = walk(SRC).filter((f) =>
      /^\s*(?:\/\/[^\n]*\n|\/\*[\s\S]*?\*\/\s*)*['"]use client['"]/.test(fs.readFileSync(f, 'utf8')),
    );
    expect(clientRoots.length).toBeGreaterThan(20);

    const parent = new Map<string, string | null>();
    const queue: string[] = [];
    for (const r of clientRoots) {
      parent.set(r, null);
      queue.push(r);
    }
    const offenders: string[] = [];
    while (queue.length) {
      const file = queue.shift()!;
      if (file.endsWith('.json')) continue;
      const src = fs.readFileSync(file, 'utf8');
      for (const m of src.matchAll(IMPORT_RE)) {
        const spec = m[1] ?? m[2] ?? m[3];
        if (!spec || /^import\s+type\b/.test(m[0])) continue;
        // `import('x').SomeType` in a type position is erased by TypeScript.
        if (m[2] && /^\.[A-Z]/.test(src.slice((m.index ?? 0) + m[0].length))) continue;
        const target = resolve(file, spec);
        if (!target || parent.has(target)) continue;
        parent.set(target, file);
        if (target.endsWith('lessons-bundle.generated.json')) {
          const chain: string[] = [];
          for (let f: string | null | undefined = target; f; f = parent.get(f)) {
            chain.unshift(path.relative(SRC, f));
          }
          offenders.push(chain.join(' -> '));
        } else if (/\.(ts|tsx)$/.test(target)) {
          queue.push(target);
        }
      }
    }
    expect(offenders).toEqual([]);
  });
});
