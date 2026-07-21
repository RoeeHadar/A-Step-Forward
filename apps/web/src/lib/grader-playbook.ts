/**
 * Versioned Grader playbook loader (no server-only — unit-testable).
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

let cachedPlaybook: string | null = null;

const FALLBACK = [
  'Process over final answer. Partial credit bands 0-15 / 16-50 / 51-84 / 85-100.',
  'Never invent steps the learner did not write. Hebrew default.',
].join(' ');

/** Load versioned Grader playbook (KPIs from Bagrut-style scoring). */
export function loadGraderPlaybook(): string {
  if (cachedPlaybook != null) return cachedPlaybook;
  const candidates = [
    join(process.cwd(), '..', '..', 'prompts', 'grader', 'playbook-v1.md'),
    join(process.cwd(), 'prompts', 'grader', 'playbook-v1.md'),
    join(process.cwd(), '..', 'prompts', 'grader', 'playbook-v1.md'),
  ];
  for (const path of candidates) {
    try {
      cachedPlaybook = readFileSync(path, 'utf8').slice(0, 6000);
      return cachedPlaybook;
    } catch {
      // try next
    }
  }
  cachedPlaybook = FALLBACK;
  return cachedPlaybook;
}

/** Test helper */
export function resetGraderPlaybookCache(): void {
  cachedPlaybook = null;
}
