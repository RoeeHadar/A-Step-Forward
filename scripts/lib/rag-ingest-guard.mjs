/**
 * Pure target guard for RAG ingest (AS-72 / AS-13 R4). No I/O, no env reads:
 * callers pass parsed flags so it can be unit-tested without a DB or network.
 *
 * Rules:
 *  - target defaults to 'dev'; must be one of dev | staging | production.
 *  - production + a destructive step (recreate_schema or fresh/TRUNCATE) is
 *    refused unless confirmProduction is set (--confirm-production /
 *    workflow input confirm_production=true).
 */
export const INGEST_TARGETS = ['dev', 'staging', 'production'];

/**
 * @param {{ target?: string, recreateSchema?: boolean, fresh?: boolean, confirmProduction?: boolean }} o
 * @returns {{ ok: true, target: string } | { ok: false, target: string, reason: string }}
 */
export function checkIngestTarget(o = {}) {
  const target = (o.target ?? 'dev').trim() || 'dev';
  if (!INGEST_TARGETS.includes(target)) {
    return { ok: false, target, reason: `unknown target '${target}' (expected ${INGEST_TARGETS.join(' | ')})` };
  }
  const destructive = Boolean(o.recreateSchema) || Boolean(o.fresh);
  if (target === 'production' && destructive && !o.confirmProduction) {
    return {
      ok: false,
      target,
      reason:
        'REFUSING: production + recreate_schema/fresh without explicit confirmation. ' +
        'Pass --confirm-production (workflow: confirm_production=true) if intentional.',
    };
  }
  return { ok: true, target };
}

/** Parse the guard-relevant flags from an argv array. */
export function parseIngestArgs(argv) {
  const i = argv.indexOf('--target');
  return {
    target: i >= 0 ? argv[i + 1] : undefined,
    recreateSchema: argv.includes('--recreate-schema') || argv.includes('--recreate'),
    fresh: argv.includes('--fresh'),
    confirmProduction: argv.includes('--confirm-production'),
    guardOnly: argv.includes('--guard-only'),
  };
}
