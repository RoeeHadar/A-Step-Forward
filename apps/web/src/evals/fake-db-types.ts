/**
 * AS-59: shape fake-DB rows exactly like @neondatabase/serverless 0.10.4 (HTTP, text format):
 *   timestamptz (1184), timestamp (1114), date (1082) -> JS Date
 *   numeric (1700), int8 (20)                         -> string
 *   int2/int4 (21/23), float4/float8 (700/701)        -> number
 * Proven against a mocked driver HTTP response in src/evals/__tests__/fake-db-types.test.ts.
 */
export type PgType = 'timestamptz' | 'numeric' | 'int8' | 'int4' | 'text';
export const PG_OID: Record<PgType, number> = { timestamptz: 1184, numeric: 1700, int8: 20, int4: 23, text: 25 };

export function asNeon(v: unknown, t: PgType): unknown {
  if (v === null || v === undefined) return v ?? null;
  switch (t) {
    case 'timestamptz': return v instanceof Date ? v : new Date(String(v));
    case 'numeric':
    case 'int8': return String(v);
    case 'int4': return typeof v === 'number' ? v : Number(v);
    default: return String(v);
  }
}

/** Column types the fakes return, per neon-db.ts SELECT + alembic schema. */
export const COLS = {
  chat_turns: { created_at: 'timestamptz' },
  learner_agent_notes: { created_at: 'timestamptz', last_referenced_at: 'timestamptz', importance: 'int4' },
} as const satisfies Record<string, Record<string, PgType>>;

export function neonRow<T extends Record<string, unknown>>(row: T, cols: Record<string, PgType>): T {
  const out: Record<string, unknown> = { ...row };
  for (const [k, t] of Object.entries(cols)) if (k in out) out[k] = asNeon(out[k], t);
  return out as T;
}
