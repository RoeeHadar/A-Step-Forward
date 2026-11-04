/**
 * AS-64: end-to-end regression for the AS-61 Date bug class.
 *
 * A fake neon driver (vi.mock of @neondatabase/serverless — no network) serves a learner
 * profile whose DATE columns next_test_date / final_goal_date are JS Dates built the way
 * neon 0.10.4 builds them (LOCAL midnight). We then:
 *   1. call the REAL generateLearningPlan (its writes are captured in-memory), and
 *   2. drive the REAL /api/chat POST, which assembles the context prompt from that
 *      profile + the persisted plan (plan_weeks.quiz_due_at returned as Date),
 * and assert the goal and plan context reach the system prompt.
 * Pre-AS-61 (05371d52) this fails: planHorizon threw `.slice is not a function`, and the
 * route's context build threw on `.trim()` → bare-persona fallback.
 */
import { describe, it, expect, vi, beforeAll, afterAll } from 'vitest';

const db = vi.hoisted(() => ({
  profile: null as Record<string, unknown> | null,
  plan: null as null | { id: string; learner_id: string; goal: string; start_date: string; end_date: string | null },
  weeks: [] as Array<{ id: string; plan_id: string; week_number: number; concepts: string[]; quiz_due_at: Date; status: string }>,
  queries: [] as string[],
  llmSystems: [] as string[],
  warns: [] as string[],
}));

vi.mock('@neondatabase/serverless', () => {
  type Q = { text: string; vals: unknown[]; then: Promise<unknown[]>['then'] };
  const run = (text: string, vals: unknown[]): unknown[] => {
    db.queries.push(text.replace(/\s+/g, ' ').trim().slice(0, 90));
    const t = text.replace(/\s+/g, ' ');
    if (/INSERT INTO learning_plans\b/.test(t)) {
      db.plan = { id: String(vals[0]), learner_id: String(vals[1]), goal: String(vals[2]), start_date: String(vals[3]), end_date: vals[4] == null ? null : String(vals[4]) };
      return [];
    }
    if (/INSERT INTO plan_weeks\b/.test(t)) {
      // neon returns timestamptz as Date
      db.weeks.push({ id: String(vals[0]), plan_id: String(vals[1]), week_number: Number(vals[2]), concepts: vals[3] as string[], quiz_due_at: new Date(String(vals[4])), status: String(vals[5]) });
      return [];
    }
    if (/^\s*DELETE FROM plan_weeks/.test(t) && /learning_plans/.test(t)) { db.weeks = []; return []; }
    if (/^\s*DELETE FROM learning_plans/.test(t)) { db.plan = null; return []; }
    if (/FROM learner_profiles/.test(t)) {
      if (!db.profile) return [];
      if (/SELECT \*/.test(t)) return [{ ...db.profile }];
      const m = /SELECT (.*?) FROM learner_profiles/.exec(t);
      const cols = (m?.[1] ?? '').split(',').map((c) => c.trim().split(/\s|::/)[0]!);
      return [Object.fromEntries(cols.map((c) => [c, db.profile![c] ?? null]))];
    }
    if (/FROM learning_plans/.test(t) && !/^\s*DELETE/.test(t)) {
      if (!db.plan) return [];
      if (/SELECT 1 AS ok/.test(t)) return [{ ok: 1 }];
      return [{ ...db.plan, status: 'active', plan_adjustment_kind: null, plan_last_adjusted_at: null, overflow_concepts: null, created_at: new Date() }];
    }
    if (/FROM plan_weeks/.test(t) && !/^\s*DELETE/.test(t)) return db.weeks.map((w) => ({ ...w }));
    return [];
  };
  const mk = (text: string, vals: unknown[]): Q => {
    let p: Promise<unknown[]> | null = null;
    const go = () => (p ??= Promise.resolve().then(() => run(text, vals)));
    return { text, vals, then: ((a, b) => go().then(a, b)) as Q['then'] };
  };
  const sql = (strings: TemplateStringsArray | string, ...vals: unknown[]) =>
    typeof strings === 'string' ? mk(strings, vals) : mk(strings.join('$?'), vals);
  sql.query = (text: string, vals: unknown[] = []) => mk(text, vals);
  sql.unsafe = (text: string) => text;
  sql.transaction = async (qs: Q[] | ((s: typeof sql) => Q[])) => {
    const list = typeof qs === 'function' ? qs(sql) : qs;
    const out: unknown[] = [];
    for (const q of list) out.push(await q);
    return out;
  };
  return { neon: () => sql, neonConfig: {}, Pool: class {}, NeonQueryPromise: class {} };
});

vi.mock('@clerk/nextjs/server', () => ({ auth: async () => ({ userId: 'as64-user', sessionClaims: { metadata: { age: 17 } } }) }));
vi.mock('next/headers', () => ({ cookies: async () => ({ get: (k: string) => (k === 'asf-locale' ? { value: 'en' } : undefined) }) }));
vi.mock('next/server', () => ({ after: (fn: () => unknown) => { void Promise.resolve().then(fn).catch(() => undefined); } }));
vi.mock('@/lib/rag-retrieve', async (orig) => ({ ...((await orig()) as object), retrieveChunks: async () => [] }));
vi.mock('@/lib/logger', async (orig) => {
  const o = (await orig()) as { logger: Record<string, (...a: unknown[]) => void> };
  return { ...o, logger: { ...o.logger, warn: (msg: unknown, ...a: unknown[]) => { db.warns.push(`${String(msg)} ${JSON.stringify(a)}`); } } };
});
vi.mock('@/lib/llm-provider', async (orig) => ({
  ...((await orig()) as object),
  llmConfigured: () => true,
  toolCallingAvailable: () => false,
  llmStream: async function* (opts: { system: string }) { db.llmSystems.push(opts.system); yield 'Here is your plan for this week.'; },
  llmComplete: async () => null,
  llmCompleteJson: async () => null,
  llmCompleteWithTools: async () => null,
}));

const GOAL = 'AS64 goal: pass the 5-unit math Bagrut';
const LEARNER = 'as64-user';

async function readAll(res: Response) {
  const reader = res.body!.getReader();
  const deadline = Date.now() + 5000;
  for (;;) {
    const r = await Promise.race([reader.read(), new Promise<null>((ok) => setTimeout(() => ok(null), Math.max(1, deadline - Date.now())))]);
    if (!r || r.done) break;
  }
}

describe('AS-64: driver-Date profile → generateLearningPlan + /api/chat prompt', () => {
  // Snapshot env so the placeholder DATABASE_URL never leaks into other files in a single-fork run
  // (it would un-skip the live-LLM integration suites).
  const savedEnv: Record<string, string | undefined> = {};
  afterAll(() => {
    for (const [k, v] of Object.entries(savedEnv)) {
      if (v === undefined) delete process.env[k];
      else process.env[k] = v;
    }
  });
  beforeAll(() => {
    for (const k of ['DATABASE_URL', 'GROQ_API_KEY', 'LLM_API_KEY', 'XAI_API_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']) savedEnv[k] = process.env[k];
    process.env.DATABASE_URL = 'postgres://placeholder:placeholder@placeholder.invalid/db'; // fake driver; never dialled
    for (const k of ['GROQ_API_KEY', 'LLM_API_KEY', 'XAI_API_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']) delete process.env[k];
    const now = new Date();
    db.profile = {
      learner_id: LEARNER, goal: GOAL, grade_level: '11', points_group: '5', subjects: ['math'],
      hours_per_week: 6, preferred_style: null, attention_span: null, self_scores: null, background_notes: null,
      next_test_name: 'Bagrut',
      // neon 0.10.4 parses DATE to LOCAL midnight
      next_test_date: new Date(now.getFullYear() + 1, 0, 15),
      final_goal_date: new Date(now.getFullYear() + 1, 5, 1),
      mental_state: {}, personality_profile: { goal_key: 'bagrut_math_5' }, weak_concepts: null, strong_concepts: null,
      wellbeing_plan_bias: null, created_at: now, updated_at: now,
    };
  });

  it('plan is generated and goal + plan context survive into the chat system prompt', async () => {
    expect(db.profile!.next_test_date).toBeInstanceOf(Date);
    expect(db.profile!.final_goal_date).toBeInstanceOf(Date);

    const { generateLearningPlan } = await import('@/lib/neon-db');
    const plan = await generateLearningPlan(LEARNER);
    expect(plan.goal).toBe(GOAL);
    expect(plan.weeks.length).toBeGreaterThan(0);
    expect(db.plan?.goal).toBe(GOAL);
    expect(db.weeks.length).toBe(plan.weeks.length);

    const { POST } = await import('@/app/api/chat/route');
    const res = await POST(new Request('http://eval.local/api/chat', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: 'What is my plan this week?' }], agent: 'mentor', sessionId: 'as64-s1' }),
    }));
    await readAll(res);
    if (process.env.AS64_DEBUG) console.log('QUERIES', db.queries.slice(-40), 'WARNS', db.warns, 'SYS', (db.llmSystems.at(-1) ?? '').slice(0, 3000));
    const system = db.llmSystems.at(-1) ?? '';
    expect(db.warns.filter((w) => /buildContextPrompt failed/.test(w))).toEqual([]);
    expect(system).toMatch(/Current weekly learning plan|Plan:|Week 1/);
    expect(system).toContain(String(new Date().getFullYear() + 1)); // exam/goal date reached the prompt
    expect(system).toContain("AS64 goal"); // goal text reached the prompt
  }, 60_000);
});
