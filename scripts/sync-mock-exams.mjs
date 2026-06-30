import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const srcDir = path.join(root, 'scripts/seed_data/mock_exams');
const destDir = path.join(root, 'apps/web/src/lib/mock-exams');

if (!existsSync(destDir)) mkdirSync(destDir, { recursive: true });

const files = ['index.json', 'math_4pt_mock_1.json', 'math_5pt_mock_1.json', 'calculus_1_mock_1.json', 'linear_algebra_mock_1.json', 'hs_physics_mock_1.json'];

for (const file of files) {
  const src = path.join(srcDir, file);
  const dest = path.join(destDir, file);
  writeFileSync(dest, readFileSync(src, 'utf-8'), 'utf-8');
  console.log(`synced ${file}`);
}
