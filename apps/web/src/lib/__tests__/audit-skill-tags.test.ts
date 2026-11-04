// AS-77: skill-tag accuracy guard. Reads the real lesson tree; reverts are
// applied to in-memory copies only (no file is written).
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { newCandidates, scanDir, scanLesson, type SkillTagCandidate } from '../../../../../scripts/audit-skill-tags.mjs';

const root = path.resolve(__dirname, '../../../../..');
const dir = path.join(root, 'scripts/seed_data/lessons');
const baseline: SkillTagCandidate[] = JSON.parse(fs.readFileSync(path.join(root, 'scripts/audit-skill-tags.baseline.json'), 'utf8'));
const load = (f: string) => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));

describe('audit-skill-tags', () => {
  it('full tree + baseline: no new candidates, CLI exits 0', () => {
    expect(newCandidates(scanDir(dir), baseline)).toEqual([]);
    const out = execFileSync(process.execPath, ['scripts/audit-skill-tags.mjs'], { cwd: root, encoding: 'utf8' });
    expect(out).toContain('[audit-skill-tags] OK');
  });

  it('vectors q16 is tagged vector_addition', () => {
    expect(load('vectors_basics.json').questions[16].skill_atoms).toEqual(['vector_addition']);
  });

  it.each([
    ['vectors_basics.json', 16, 'vector_addition', 'dot_product'],
    ['3d_solids_volume.json', 2, 'surface_area_cube', 'volume_sphere'],
    ['nuclear_physics.json', 15, 'half_life', 'binding_energy'],
  ])('reverting %s q[%i] %s -> %s is a NEW candidate', (file, i, now, old) => {
    const d = load(file);
    d.questions[i].skill_atoms = d.questions[i].skill_atoms.map((a: string) => (a === now ? old : a));
    const fresh = newCandidates(scanLesson(file, d), baseline);
    expect(fresh.map((r) => [r.file, r.index])).toContainEqual([file, i]);
  });

  it('CLI exits non-zero on a reverted fixture tree', () => {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'skill-tags-'));
    try {
      const d = load('vectors_basics.json');
      d.questions[16].skill_atoms = ['dot_product'];
      fs.writeFileSync(path.join(tmp, 'vectors_basics.json'), JSON.stringify(d));
      let code = 0; let err = '';
      try {
        execFileSync(process.execPath, ['scripts/audit-skill-tags.mjs', `--dir=${tmp}`], { cwd: root, encoding: 'utf8', stdio: 'pipe' });
      } catch (e) { code = (e as { status: number }).status; err = String((e as { stderr: string }).stderr); }
      expect(code).not.toBe(0);
      expect(err).toContain('NEW vectors_basics.json q[16]');
    } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
  });
});
