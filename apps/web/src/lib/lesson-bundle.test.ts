import { describe, expect, it } from 'vitest';
import {
  getBundledLesson,
  hasMeaningfulAgentHints,
  resolveAgentHintsRow,
} from './lesson-bundle';

describe('hasMeaningfulAgentHints', () => {
  it('returns false for null, undefined, and empty objects', () => {
    expect(hasMeaningfulAgentHints(null)).toBe(false);
    expect(hasMeaningfulAgentHints(undefined)).toBe(false);
    expect(hasMeaningfulAgentHints({})).toBe(false);
  });

  it('returns true when key_insights are present', () => {
    expect(hasMeaningfulAgentHints({ key_insights: ['Area uses base times height.'] })).toBe(true);
  });
});

describe('resolveAgentHintsRow', () => {
  it('prefers Neon row when agent_hints are meaningful', () => {
    const fromDb = {
      concept_id: 'area_perimeter',
      title_en: 'DB title',
      title_he: 'כותרת DB',
      agent_hints: { key_insights: ['From Neon'] },
    };
    const row = resolveAgentHintsRow('area_perimeter', fromDb);
    expect(row).toEqual(fromDb);
  });

  it('falls back to bundle when Neon row is missing', () => {
    const bundled = getBundledLesson('3d_solids_volume');
    expect(bundled).not.toBeNull();
    expect(hasMeaningfulAgentHints(bundled!.lesson.agent_hints)).toBe(true);

    const row = resolveAgentHintsRow('3d_solids_volume', null);
    expect(row).not.toBeNull();
    expect(row!.agent_hints).toEqual(bundled!.lesson.agent_hints);
    expect(row!.title_en).toBe(bundled!.lesson.title_en);
  });

  it('falls back to bundle when Neon agent_hints are empty', () => {
    const bundled = getBundledLesson('3d_solids_volume');
    const row = resolveAgentHintsRow('3d_solids_volume', {
      concept_id: '3d_solids_volume',
      title_en: 'Thin DB',
      title_he: 'דק',
      agent_hints: {},
    });
    expect(row).not.toBeNull();
    expect(row!.agent_hints).toEqual(bundled!.lesson.agent_hints);
    expect(row!.title_en).toBe('Thin DB');
  });

  it('returns null when neither Neon nor bundle has hints', () => {
    expect(
      resolveAgentHintsRow('definitely_not_a_real_concept_xyz', {
        concept_id: 'definitely_not_a_real_concept_xyz',
        title_en: 'x',
        title_he: 'x',
        agent_hints: {},
      }),
    ).toBeNull();
  });
});
