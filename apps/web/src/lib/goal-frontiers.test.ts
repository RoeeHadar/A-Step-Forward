import { describe, expect, it } from 'vitest';
import frontiers from './goal-frontiers.generated.json';
import kg from './kg-data.json';
import overrides from './goal-frontiers.overrides.json';
import { ONBOARDING_GOALS } from './plan-catalog';

/**
 * Coverage gate for the goal-frontier manifest (ADR-0009 §3, stream 1).
 *
 * These assertions fail CI when `scripts/build-goal-frontiers.mjs` produces a
 * manifest that is empty for a goal or omits the goal's terminal concept — the
 * two failure modes that would silently mis-pace every learner on that goal.
 *
 * Regenerate the manifest with `node scripts/build-goal-frontiers.mjs` after any
 * KG or override change, then commit the updated goal-frontiers.generated.json.
 */

interface CoreEntry {
  id: string;
  depth: number;
  downstream: number;
  critical: boolean;
}
interface Frontier {
  goal_key: string;
  subjects: string[];
  points_group: string;
  allowed_levels: string[];
  stretch_levels: string[];
  terminal_concept: string | null;
  core: CoreEntry[];
  stretch: string[];
  core_count: number;
  critical_count: number;
}
interface Manifest {
  version: number;
  generated_at: string;
  fanout_critical: number;
  goals: Record<string, Frontier>;
}

const manifest = frontiers as Manifest;
const kgById = (kg as { byId: Record<string, unknown> }).byId;
const goalEntries = Object.entries(manifest.goals);

describe('goal-frontier manifest', () => {
  it('has a valid version and at least one goal', () => {
    expect(manifest.version).toBeGreaterThanOrEqual(1);
    expect(goalEntries.length).toBeGreaterThan(0);
  });

  it('covers every onboarding goal a learner can pick', () => {
    for (const goal of ONBOARDING_GOALS) {
      expect(
        manifest.goals[goal.key],
        `missing frontier for onboarding goal "${goal.key}"`,
      ).toBeDefined();
    }
  });

  describe.each(goalEntries)('goal "%s"', (goalKey, g) => {
    it('has a non-empty core frontier', () => {
      expect(g.core.length, `${goalKey} core is empty`).toBeGreaterThan(0);
      expect(g.core_count).toBe(g.core.length);
    });

    it('resolves a terminal concept that exists in the KG', () => {
      expect(g.terminal_concept, `${goalKey} has no terminal concept`).toBeTruthy();
      expect(
        kgById[g.terminal_concept as string],
        `${goalKey} terminal "${g.terminal_concept}" not in KG`,
      ).toBeDefined();
    });

    it('includes the terminal concept in the core, flagged goal-critical', () => {
      const terminal = g.core.find((c) => c.id === g.terminal_concept);
      expect(terminal, `${goalKey} core omits terminal "${g.terminal_concept}"`).toBeDefined();
      expect(terminal?.critical, `${goalKey} terminal not marked critical`).toBe(true);
    });

    it('references only real KG concepts in core and stretch', () => {
      for (const c of g.core) {
        expect(kgById[c.id], `${goalKey} core concept "${c.id}" not in KG`).toBeDefined();
      }
      for (const id of g.stretch) {
        expect(kgById[id], `${goalKey} stretch concept "${id}" not in KG`).toBeDefined();
      }
    });

    it('keeps core and stretch sets disjoint and dedupes core', () => {
      const coreIds = g.core.map((c) => c.id);
      expect(new Set(coreIds).size, `${goalKey} core has duplicates`).toBe(coreIds.length);
      const coreSet = new Set(coreIds);
      for (const id of g.stretch) {
        expect(coreSet.has(id), `${goalKey} stretch "${id}" also in core`).toBe(false);
      }
    });

    it('orders the core foundations-first (non-decreasing depth) with a root', () => {
      // A root (depth 0) must always exist; the manifest is prerequisite-anchored.
      expect(g.core.some((c) => c.depth === 0), `${goalKey} core has no root concept`).toBe(true);
      // Derived ordering is strictly foundations-first. Goals with a hand-authored
      // `order` override intentionally break this, so only enforce it when unpinned.
      const pinned = (overrides as Record<string, { order?: string[] }>)[goalKey]?.order?.length;
      if (!pinned) {
        for (let i = 1; i < g.core.length; i += 1) {
          expect(
            g.core[i]!.depth,
            `${goalKey} core not ordered by depth at index ${i}`,
          ).toBeGreaterThanOrEqual(g.core[i - 1]!.depth);
        }
      }
    });

    it('reports a consistent critical_count', () => {
      expect(g.critical_count).toBe(g.core.filter((c) => c.critical).length);
      expect(g.critical_count, `${goalKey} has no critical concepts`).toBeGreaterThan(0);
    });
  });
});
