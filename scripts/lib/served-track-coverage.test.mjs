// AS-85 guard: no served concept/track pair that had items in the committed
// baseline may drop to 0 items in content/question-store/generated.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const baseline = JSON.parse(readFileSync(join(root, 'scripts/gen/served-track-baseline.json'), 'utf8'));

test('served concept/track pairs keep >=1 item', () => {
  const lost = [];
  for (const [concept, tracks] of Object.entries(baseline.pairs)) {
    const f = join(root, 'content/question-store/generated', `${concept}.json`);
    const raw = existsSync(f) ? JSON.parse(readFileSync(f, 'utf8')) : [];
    const items = Array.isArray(raw) ? raw : raw.items ?? [];
    for (const t of tracks) {
      if (!items.some((i) => (i.math_track ?? []).includes(t))) lost.push(`${concept}/${t}`);
    }
  }
  assert.deepEqual(lost, [], `${lost.length} served pairs dropped to 0 items: ${lost.join(', ')}`);
});
