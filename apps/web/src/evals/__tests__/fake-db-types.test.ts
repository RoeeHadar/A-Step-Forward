// AS-59: the runner's fake rows must carry the same JS types as @neondatabase/serverless 0.10.4.
// Offline: the driver's fetch is mocked with an HTTP-shaped response (no network, placeholder URL).
import { describe, it, expect, afterAll } from 'vitest';
import { neon, neonConfig } from '@neondatabase/serverless';
import { neonRow, asNeon, COLS, PG_OID, type PgType } from '../fake-db-types';

const prevFetch = neonConfig.fetchFunction;
afterAll(() => { neonConfig.fetchFunction = prevFetch; });

async function driverRow(cols: Array<[string, PgType, string | null]>) {
  neonConfig.fetchFunction = async () => new Response(JSON.stringify({
    command: 'SELECT', rowCount: 1, rowAsArray: true,
    fields: cols.map(([name, t]) => ({ name, dataTypeID: PG_OID[t] })),
    rows: [cols.map(([, , v]) => v)],
  }), { headers: { 'content-type': 'application/json' } });
  const sql = neon('postgresql://user:placeholder@placeholder.invalid/db');
  return ((await sql`SELECT 1`) as Array<Record<string, unknown>>)[0]!;
}
const kind = (v: unknown) => (v === null ? 'null' : v instanceof Date ? 'Date' : typeof v);

describe('AS-59 fake DB types == neon driver types', () => {
  it('driver: 1184 -> Date, 1700 -> string, 20 -> string, 23 -> number', async () => {
    const r = await driverRow([['ts', 'timestamptz', '2026-11-03 10:00:00+00'], ['num', 'numeric', '3.50'], ['big', 'int8', '9007199254740993'], ['i4', 'int4', '7']]);
    expect([kind(r.ts), kind(r.num), kind(r.big), kind(r.i4)]).toEqual(['Date', 'string', 'string', 'number']);
    expect((r.ts as Date).toISOString()).toBe('2026-11-03T10:00:00.000Z');
    expect(r.big).toBe('9007199254740993');
    for (const [k, t] of [['ts', 'timestamptz'], ['num', 'numeric'], ['big', 'int8'], ['i4', 'int4']] as const) {
      const fake = asNeon(k === 'ts' ? '2026-11-03T10:00:00.000Z' : k === 'num' ? 3.5 : k === 'big' ? 9007199254740993n : '7', t);
      expect(kind(fake)).toBe(kind(r[k]));
    }
  });

  it('learner_agent_notes fake row has the driver types per column (incl. null timestamptz)', async () => {
    const r = await driverRow([['created_at', 'timestamptz', '2026-11-03 10:00:00+00'], ['last_referenced_at', 'timestamptz', null], ['importance', 'int4', '3'], ['content', 'text', 'x']]);
    const fake = neonRow({ created_at: '2026-11-03T10:00:00.000Z', last_referenced_at: null, importance: 3, content: 'x' }, COLS.learner_agent_notes);
    for (const k of Object.keys(r)) expect([k, kind((fake as Record<string, unknown>)[k])]).toEqual([k, kind(r[k])]);
    expect((fake.created_at as unknown as Date).getTime()).toBe((r.created_at as Date).getTime());
  });

  it('chat_turns fake row created_at is a Date like the driver', async () => {
    const r = await driverRow([['created_at', 'timestamptz', '2026-11-03 10:00:00+00']]);
    expect(kind(neonRow({ created_at: '2026-11-03T10:00:00.000Z' }, COLS.chat_turns).created_at)).toBe(kind(r.created_at));
  });
});
