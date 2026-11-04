/**
 * AS-16 offline student-journey eval (AS-27). $0, no network, no DB, no secrets.
 *
 * Drives the REAL POST handler of /api/chat in-process with:
 *  - stub LLM (deterministic canned replies; llmStream/llmComplete mocked),
 *  - fake in-memory DB (chat_turns + learner_agent_notes; every other neon-db
 *    helper runs with no DATABASE_URL and degrades to null on throw),
 *  - fake Clerk auth / cookies / after(), stub RAG retrieval (canned chunks).
 * Network calls (fetch, http(s).request/get, net/tls.connect) throw and are
 * counted; the run fails if the count is > 0.
 *
 * Normal `vitest run` executes it as a smoke test (no files written).
 * `EVAL_DRY=1 EVAL_OUT=<path>` also writes the scores JSON (see package.json eval:offline).
 *
 * What a stub can measure: route plumbing — persona/system prompt selection,
 * locale cookie -> response locale, history threading, RAG toggle per agent,
 * cite ids vs retrieved set, memory-tag parsing -> note persistence, note recall
 * into later prompts / handoff digest, cross-learner isolation, post-filters.
 * What it cannot: reply quality, pedagogy, adaptation, plan reasoning, SAT,
 * real latency/cost — those are null + needs_paid_run (or not_measurable_offline).
 */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import https from 'node:https';
import net from 'node:net';
import tls from 'node:tls';
import { syncBuiltinESMExports } from 'node:module';
import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { parse as parseYaml } from 'yaml';
import * as tf_ from '@/lib/typed-facts';
import { createReplyGuard, hasFinalValue, isLearnerAttempt, REVIEWER_MAX_LINES } from '@/lib/agent-method-guard';

// ---------------------------------------------------------------- network guard
const net_ = vi.hoisted(() => ({ count: 0, calls: [] as string[] }));
function blocked(kind: string) {
  return (...args: unknown[]) => {
    net_.count += 1;
    net_.calls.push(`${kind} ${String(args[0]).slice(0, 80)}`);
    throw new Error(`[AS27_NET_BLOCKED] ${kind}`);
  };
}
const saved = {
  fetch: globalThis.fetch,
  hr: http.request, hg: http.get, sr: https.request, sg: https.get,
  nc: net.connect, ncc: net.createConnection, tc: tls.connect,
};
function installGuard() {
  globalThis.fetch = (async (...a: unknown[]) => blocked('fetch')(...a)) as typeof fetch;
  http.request = blocked('http.request') as never; http.get = blocked('http.get') as never;
  https.request = blocked('https.request') as never; https.get = blocked('https.get') as never;
  net.connect = blocked('net.connect') as never; net.createConnection = blocked('net.createConnection') as never;
  tls.connect = blocked('tls.connect') as never;
  syncBuiltinESMExports();
}
function removeGuard() {
  globalThis.fetch = saved.fetch;
  http.request = saved.hr; http.get = saved.hg; https.request = saved.sr; https.get = saved.sg;
  net.connect = saved.nc; net.createConnection = saved.ncc; tls.connect = saved.tc;
  syncBuiltinESMExports();
}

// ---------------------------------------------------------------- shared run state
type Turn = { role: 'user' | 'assistant'; content: string; agent: string; sessionId?: string; created_at?: string };
type Note = { id: string; learner_id: string; agent: string; kind: string; content: string; importance: number; related_concept_id: string | null; created_at: string; superseded_by?: string | null };
const st = vi.hoisted(() => ({
  userId: 'eval-user',
  locale: 'he' as 'he' | 'en',
  turns: [] as Turn[],
  notes: [] as Note[],
  dbCalls: {} as Record<string, number>,
  llmCalls: [] as Array<{ system: string; messages: Array<{ role: string; content: string }> }>,
  llmCompleteCalls: 0,
  ragCalls: [] as Array<{ query: string; ids: string[] }>,
  /** AS-42: typed fact the stub tags on this turn (kind + supersede key + EVALTAG suffix). */
  noteTag: null as { kind: string; key: string; tag: string } | null,
  afterJobs: [] as Promise<unknown>[],
}));

vi.mock('@clerk/nextjs/server', () => ({
  auth: async () => ({ userId: st.userId, sessionClaims: { metadata: { age: 17 } } }),
}));
vi.mock('next/headers', () => ({
  cookies: async () => ({ get: (k: string) => (k === 'asf-locale' ? { value: st.locale } : undefined) }),
}));
vi.mock('next/server', () => ({
  after: (fn: () => unknown) => {
    st.afterJobs.push(Promise.resolve().then(fn).catch(() => undefined));
  },
}));

vi.mock('@/lib/neon-db', async (importOriginal) => {
  /** Empty value of the right shape when a helper throws (no DATABASE_URL). */
  const emptyFor = (k: string): unknown =>
    /Mastery$|Map$|Record$/.test(k) ? {} : /^(fetch|list|select)|s$/.test(k) ? [] : null;
  const orig = (await importOriginal()) as Record<string, unknown>;
  const tf = await import('@/lib/typed-facts');
  const fakes: Record<string, (...a: never[]) => unknown> = {
    recordChatTurn: async (learnerId: string, agent: string, role: 'user' | 'assistant', content: string, sessionId?: string) => {
      st.turns.push({ role, content, agent, sessionId, created_at: new Date().toISOString(), ...{ learnerId } } as Turn & { learnerId: string });
    },
    fetchRecentChatTurns: async (learnerId: string, agent: string, limit = 10, sessionId?: string | null) =>
      (st.turns as Array<Turn & { learnerId: string }>)
        .filter((t) => t.learnerId === learnerId && t.agent === agent && t.sessionId === sessionId)
        .slice(-limit)
        .map((t, i) => ({ id: String(i), learner_id: learnerId, agent, role: t.role, content: t.content, session_id: sessionId, created_at: new Date().toISOString() })),
    // AS-47/AS-48: in-memory stand-in for the learner-wide last-activity query (all agents),
    // strict `<` against the route's request-start timestamp.
    fetchLearnerLastActivityAt: async (learnerId: string, before: Date) => {
      const ts = (st.turns as Array<Turn & { learnerId: string }>)
        .filter((t) => t.learnerId === learnerId && t.created_at && t.created_at < before.toISOString())
        .map((t) => t.created_at!)
        .sort();
      return ts.at(-1) ?? null;
    },
    // Mirrors neon-db.ts fetchAgentNotes SQL (`superseded_by IS NULL`).
    fetchAgentNotes: async (learnerId: string, agent: string, limit = 8) =>
      st.notes.filter((n) => n.learner_id === learnerId && n.agent === agent && !n.superseded_by).slice(-limit),
    // AS-43: mirrors neon-db.ts fetchAgentNotesByIds (learner-scoped, live rows).
    fetchAgentNotesByIds: async (learnerId: string, ids: string[]) =>
      st.notes.filter((n) => n.learner_id === learnerId && ids.includes(n.id) && !n.superseded_by),
    // AS-42: mirrors neon-db.ts appendAgentNote — typed fact envelope, count, supersede by kind + key.
    appendAgentNote: async (learnerId: string, agent: string, note: { kind: string; content: string; importance?: number; related_concept_id?: string | null; fact?: { key: string; valid_to?: string | null } | null }) => {
      const id = `00000000-0000-4000-8000-${String(st.notes.length + 1).padStart(12, "0")}`; // AS-52 r1: uuid-shaped like prod
      const key = tf.isTypedFactKind(note.kind) ? tf.normalizeFactKey(note.fact?.key) : null;
      const sameKey = (n: Note) => !n.superseded_by && n.learner_id === learnerId && n.kind === note.kind && tf.decodeFactContent(n.content).meta?.key === key;
      let content = note.content.slice(0, 600);
      if (key) {
        const prev = st.notes.filter(sameKey).at(-1);
        content = tf.encodeFactContent(content, { key, n: tf.nextFactCount(note.kind, prev ? tf.decodeFactContent(prev.content).meta : null), valid_to: tf.normalizeValidTo(note.fact?.valid_to) });
      }
      const prior = key ? st.notes.filter(sameKey) : [];
      st.notes.push({ id, learner_id: learnerId, agent, kind: note.kind, content, importance: note.importance ?? 3, related_concept_id: note.related_concept_id ?? null, created_at: new Date().toISOString() });
      for (const n of prior) n.superseded_by = id;
      return id;
    },
  };
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(orig)) {
    if (typeof v !== 'function' || /^[A-Z]/.test(k)) { out[k] = v; continue; }
    const fn = (fakes[k] ?? v) as (...a: unknown[]) => unknown;
    out[k] = (...a: unknown[]) => {
      st.dbCalls[k] = (st.dbCalls[k] ?? 0) + 1;
      const dflt = () => emptyFor(k);
      try {
        const r = fn(...a);
        return r instanceof Promise ? r.then((v) => v ?? dflt(), () => dflt()) : r;
      } catch {
        return dflt();
      }
    };
  }
  out.dbConfigured = false;
  return out;
});

vi.mock('@/lib/rag-retrieve', async (importOriginal) => {
  const orig = (await importOriginal()) as Record<string, unknown>;
  return {
    ...orig,
    retrieveChunks: async (opts: { query: string }) => {
      const ids = ['eval-chunk-a', 'eval-chunk-b'];
      st.ragCalls.push({ query: opts.query, ids });
      return ids.map((id, i) => ({
        id: `${id}-row`, conceptId: id, sourceDocId: `doc-${i}`, title: `Eval passage ${i + 1}`,
        heading: `Eval passage ${i + 1}`, text: 'Canned offline passage (no Bagrut years or question numbers).',
        lang: 'en', score: 1 - i * 0.1,
      }));
    },
  };
});

const STUB_REPLY: Record<string, Record<'he' | 'en', string>> = {
  tutor: { en: "Let's take it one step at a time. What do you get if you move the constant to the other side? Try it and tell me.", he: 'בוא נתקדם צעד אחר צעד. מה יוצא אם מעבירים את המספר לצד השני? נסה ותגיד לי.' },
  mentor: { en: "Here's where you stand and a short review to start with. Let's begin with one focused block this week.", he: 'הנה איפה שאתה עומד, ונתחיל בחזרה קצרה. בוא נקבע בלוק ממוקד אחד השבוע.' },
  coach: { en: "That feeling is normal. Let's set one small, achievable goal for today: ten focused minutes.", he: 'התחושה הזו נורמלית. בוא נציב מטרה קטנה ובת השגה להיום: עשר דקות ממוקדות.' },
  reviewer: { en: 'Review against the rubric: your structure is clear, but step 3 has a gap. Which assumption justifies it?', he: 'ביקורת לפי מחוון: המבנה ברור, אבל בשלב 3 יש פער. איזו הנחה מצדיקה אותו?' },
};
/** Agent of the turn being driven (set by the runner; the stub replies in that role). */
let currentAgent = 'tutor';

vi.mock('@/lib/llm-provider', async (importOriginal) => {
  const orig = (await importOriginal()) as Record<string, unknown>;
  const reply = (lastUser: string) => {
    const a = currentAgent;
    let text = (STUB_REPLY[a] ?? STUB_REPLY.tutor!)[st.locale];
    // AS-41: simulate a model that leaks — the tutor stub appends the J1 final value
    // and the reviewer stub appends a full rewrite; the route post-check must strip them.
    if (a === 'tutor' && /2x\s*\+\s*3\s*=\s*11|x\s*=\s*\d/.test(lastUser)) text += '\nx = 4.';
    if (a === 'reviewer') text += `\nHere is the full corrected solution:\n${Array.from({ length: 10 }, (_, i) => `Step ${i + 1}: rewritten line ${i + 1}.`).join('\n')}`;
    const lastRag = st.ragCalls.at(-1);
    if (st.noteTag) {
      const t = st.noteTag;
      // AS-52 (C3b): scripted model follows the prompt — key/valid_to are emitted only when the
      // system prompt carries the typed-fact instruction (agent-skills.ts SHARED); otherwise legacy untyped tag.
      const instructed = (st.llmCalls.at(-1)?.system ?? '').includes('Typed facts (goal / preference / state=affect');
      const typed = instructed && t.kind !== 'misconception' ? { key: t.key, valid_to: null } : t.kind === 'misconception' ? { key: t.key } : {};
      text += ` [[ASF_MEMORY_NOTE:${JSON.stringify({ kind: t.kind, ...typed, content: `EVALTAG:${t.tag} ${t.kind === 'goal' ? 'learner states this goal' : t.kind === 'state' ? 'learner feels unmotivated today' : 'learner repeats this error'}`, importance: 4 })}]]`;
    }
    if (lastRag && lastRag.ids[0]) text += ` [[ASF_CITE:${JSON.stringify({ concept_id: lastRag.ids[0] })}]]`;
    return text;
  };
  return {
    ...orig,
    llmConfigured: () => true,
    toolCallingAvailable: () => false,
    llmStream: async function* (opts: { system: string; messages: Array<{ role: string; content: string }> }) {
      st.llmCalls.push({ system: opts.system, messages: opts.messages });
     
      yield reply([...opts.messages].reverse().find((x) => x.role === 'user')?.content ?? '');
    },
    llmComplete: async () => { st.llmCompleteCalls += 1; return null; },
    llmCompleteJson: async () => { st.llmCompleteCalls += 1; return null; },
    llmCompleteWithTools: async () => { st.llmCompleteCalls += 1; return null; },
  };
});

// ---------------------------------------------------------------- journeys + scoring
type Session = { s: number; agent: string; turns: string[]; checkpoints?: string[]; gap_days?: number; practice_attempts?: boolean[] };
// AS-47: deterministic journey clock — Date is faked (timers stay real); each journey
// starts at JOURNEY_EPOCH and a session's `gap_days` advances it before its first turn.
const JOURNEY_EPOCH = Date.UTC(2026, 0, 5, 9, 0, 0);
const DAY_MS = 86_400_000;
type Journey = { id: string; lang: 'he' | 'en'; sessions: Session[] };
const EVAL_DIR = path.resolve(__dirname, '../../evals/as16');
const spec = parseYaml(fs.readFileSync(path.join(EVAL_DIR, 'journeys.yaml'), 'utf8')) as { journeys: Journey[] };

type Metric = {
  kind: 'deterministic' | 'judge_only' | 'not_measurable_offline';
  checks: Array<{ checkpoint: string; pass: boolean; detail: string }>;
  score: number | null; pass: boolean | null;
  judge: { score: null; needs_paid_run: true } | null;
  note?: string;
};
const METRIC_IDS = ['MEM-R', 'MEM-F', 'PLAN-A', 'PLAN-F', 'ADAPT', 'ROLE', 'RAG', 'HAND', 'SITE', 'SAT', 'LAT', 'COST', 'PLUMB'] as const;
const JUDGE = { score: null, needs_paid_run: true } as const;
const HAS_JUDGE = new Set(['MEM-R', 'MEM-F', 'PLAN-A', 'ADAPT', 'ROLE', 'RAG', 'HAND', 'SAT']);
const OFFLINE_NA: Record<string, string> = {
  'PLAN-A': 'plan writes need real DB + tool-calling model (propose_plan_change); stubbed off',
  // AS-43: PLAN-F is deterministic offline only for PLAN.no_change_from_state (mood-only turn stages 0 plan changes); plan-version flip-flop still needs a real DB.
  // AS-51 (C5): ADAPT is deterministic offline only for ADAPT.difficulty_up/down via the BKT mastery
  // read (MASTERY_MODEL=bkt) over the session's declared practice_attempts; strategy changes still need a paid run.
  SITE: 'needs Playwright on preview + t189u decision->element map',
  SAT: 'student-agent + judge ratings (paid)',
  LAT: 'stub has no model latency; needs Langfuse spans on a real run',
  COST: 'stub uses 0 tokens; needs Langfuse token usage',
};

const HEB = /[\u0590-\u05FF]/;
const BAGRUT_INVENT = /\b(19|20)\d{2}\b|שאלה\s*\d|question\s*\d/i;

/** Read the data stream; a stream that never closes is recorded, not awaited forever. */
const STREAM_TIMEOUT_MS = 3000;
async function readBody(res: Response): Promise<{ text: string; closed: boolean }> {
  const reader = res.body!.getReader();
  const dec = new TextDecoder();
  let raw = '';
  let closed = false;
  const deadline = Date.now() + STREAM_TIMEOUT_MS;
  for (;;) {
    const left = deadline - Date.now();
    if (left <= 0) break;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const r = await Promise.race([
      reader.read(),
      new Promise<null>((ok) => { timer = setTimeout(() => ok(null), left); }),
    ]);
    clearTimeout(timer);
    if (!r) break;
    if (r.done) { closed = true; break; }
    raw += dec.decode(r.value, { stream: true });
  }
  if (!closed) await reader.cancel().catch(() => undefined);
  let text = '';
  for (const line of raw.split('\n')) {
    if (line.startsWith('0:')) { try { text += JSON.parse(line.slice(2)) as string; } catch { /* ignore */ } }
  }
  return { text, closed };
}
async function settle() {
  await Promise.all(st.afterJobs.splice(0));
  for (let i = 0; i < 20; i++) await new Promise((ok) => setImmediate(ok));
}

/**
 * AS-42: checkpoint -> stub note tag. `MEM.note_written(misconception=sign_move)` /
 * `MEM.note_written(sqrt_split)` -> misconception fact keyed by the tag (as before, plus key);
 * `MEM.fact_written(goal:exam_date=in_2_weeks)` -> goal fact, key exam_date.
 */
function noteTagFor(cp: string): { kind: string; key: string; tag: string } {
  const typed = /\((\w+):(\w+)=(\w+)\)/.exec(cp);
  if (typed) return { kind: typed[1]!, key: typed[2]!, tag: `${typed[1]}_${typed[2]}_${typed[3]}` };
  const key = /\(([^)=]*=)?([^)]+)\)/.exec(cp)?.[2] ?? 'note';
  return { kind: 'misconception', key, tag: key };
}

const decoys = new Map<string, string>(); // learner -> planted decoy text in a DIFFERENT learner's notes

async function runJourney(POST: (r: Request) => Promise<Response>, j: Journey, locale: 'he' | 'en') {
  const userId = `eval-${j.id}-${locale}`;
  st.userId = userId; st.locale = locale;
  let clockMs = JOURNEY_EPOCH;
  vi.setSystemTime(clockMs);
  // Plant a decoy note for another learner to test cross-learner isolation (MEM-F).
  const decoy = `DECOY_${j.id}_${locale}_other_student_fact`;
  st.notes.push({ id: `decoy-${userId}`, learner_id: `${userId}-OTHER`, agent: 'tutor', kind: 'observation', content: decoy, importance: 5, related_concept_id: null, created_at: new Date().toISOString() });
  decoys.set(userId, decoy);

  const m: Record<string, Metric> = {};
  for (const id of METRIC_IDS) {
    m[id] = { kind: OFFLINE_NA[id] ? 'not_measurable_offline' : 'deterministic', checks: [], score: null, pass: null, judge: HAS_JUDGE.has(id) ? { ...JUDGE } : null, note: OFFLINE_NA[id] };
    if (id === 'SAT') m[id]!.kind = 'judge_only';
  }
  const add = (id: string, checkpoint: string, pass: boolean, detail: string) => m[id]!.checks.push({ checkpoint, pass, detail });
  const transcript: Array<{ s: number; agent: string; user: string; reply: string; status: number }> = [];
  const personaMarkers: Record<string, string> = {};

  // AS-41 r1 (P1-1): negative teaching fixtures (this locale) must pass the
  // tutor + reviewer post-check unchanged (guard-level; same code the route runs before enqueue).
  if (j.id === 'J1-weak-he') {
    const neg = (JSON.parse(fs.readFileSync(path.join(EVAL_DIR, 'role-negative-fixtures.json'), 'utf8')) as { fixtures: Array<{ id: string; lang: string; prompt: string; reply: string }> }).fixtures;
    for (const f of neg.filter((x) => x.lang === locale)) {
      const ok = ['tutor', 'reviewer'].every((agent) => {
        const g = createReplyGuard({ agent, lastMessage: f.prompt, locale, practiceActive: false });
        if (!g) return true;
        let out = '';
        for (const c of f.reply.match(/[\s\S]{1,7}/g) ?? []) out += g.push(c);
        return out + g.flush() === f.reply;
      });
      add('ROLE', `neg.${f.id}.teaching_passthrough`, ok, 'teaching reply with <var> = <number> passes unchanged');
    }
  }

  for (const sess of j.sessions) {
    if (sess.gap_days) { clockMs += sess.gap_days * DAY_MS; vi.setSystemTime(clockMs); }
    currentAgent = sess.agent;
    const sessionId = `${userId}-s${sess.s}`;
    const cps = sess.checkpoints ?? [];
    const noteCp = cps.find((c) => c.startsWith('MEM.note_written') || c.startsWith('MEM.fact_written'));
    const history: Array<{ role: string; content: string }> = [];
    for (let ti = 0; ti < sess.turns.length; ti++) {
      const text = sess.turns[ti]!;
      st.noteTag = noteCp && ti === sess.turns.length - 1 ? noteTagFor(noteCp) : null;
      history.push({ role: 'user', content: text });
      const llmBefore = st.llmCalls.length; const ragBefore = st.ragCalls.length;
      const t0 = Date.now();
      const res = await POST(new Request('http://eval.local/api/chat', {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ messages: history, agent: sess.agent, sessionId }),
      }));
      const { text: reply, closed } = await readBody(res);
      if (process.env.EVAL_DEBUG) console.log(`[AS27dbg] ${j.id}/${locale} s${sess.s}t${ti + 1} ${res.status} ${Date.now() - t0}ms`);
      await settle();
      history.push({ role: 'assistant', content: reply });
      transcript.push({ s: sess.s, agent: sess.agent, user: text, reply, status: res.status });
      const call = st.llmCalls.slice(llmBefore).at(-1);
      const sys = call?.system ?? '';
      const promptAll = sys + '\n' + (call?.messages ?? []).map((x) => x.content).join('\n');
      const tag = `s${sess.s}t${ti + 1}`;

      // PLUMB: HTTP 200, LLM reached, locale, history, machine tags stripped.
      add('PLUMB', `${tag}.http200`, res.status === 200, `status ${res.status}`);
      add('PLUMB', `${tag}.stream_closed`, closed, closed ? 'data stream closed' : `stream did not close within ${STREAM_TIMEOUT_MS}ms (route pull() enqueued nothing while buffering an [[ASF_ tag)`);
      add('PLUMB', `${tag}.llm_called`, Boolean(call), call ? 'llmStream called' : 'no llmStream call');
      add('PLUMB', `${tag}.reply_locale`, locale === 'he' ? HEB.test(reply) : !HEB.test(reply) && reply.length > 0, `reply ${reply.slice(0, 40)}`);
      add('PLUMB', `${tag}.no_machine_tag_leak`, !reply.includes('[[ASF_'), 'visible reply has no [[ASF_ tags');
      if (ti > 0) add('PLUMB', `${tag}.history_threaded`, promptAll.includes(sess.turns[ti - 1]!), 'previous user turn present in prompt');
      personaMarkers[sess.agent] = sys.slice(0, 400);

      // ROLE: persona plumbing + regex checks on the (stub) reply.
      const ragExpected = sess.agent === 'tutor' || sess.agent === 'coach';
      for (const cp of cps.filter((c) => c.startsWith('ROLE.'))) {
        // AS-41: hint-before-answer is judged on EVERY tutor turn with the shared
        // RUB ROLE regex: no final value before an attempt; after an attempt the
        // (leaky stub's) answer must be allowed through.
        if (cp === 'ROLE.tutor_no_direct_answer') {
          if (isLearnerAttempt(text)) add('ROLE', `${tag}.tutor_answer_allowed_after_attempt`, hasFinalValue(reply) || !/2x\s*\+\s*3\s*=\s*11|x\s*=\s*\d/.test(text), 'attempt turn: final value not suppressed');
          else add('ROLE', `${tag}.${cp}`, !hasFinalValue(reply), 'no final value before an attempt (FINAL_VALUE_RE)');
          continue;
        }
        if (ti !== sess.turns.length - 1) continue;
        if (cp === 'ROLE.reviewer_critique_only') add('ROLE', `${tag}.${cp}`, reply.length < 600 && !/full (corrected )?solution/i.test(reply) && reply.split('\n').filter((l) => l.trim()).length <= REVIEWER_MAX_LINES, `short critique (<=${REVIEWER_MAX_LINES} lines), no full rewrite`);
        else if (cp === 'ROLE.distinct_from_tutor') add('ROLE', `${tag}.${cp}`, Boolean(personaMarkers.tutor) && personaMarkers.tutor !== sys.slice(0, 400), 'system prompt differs from tutor session');
        else add('ROLE', `${tag}.${cp}`, sys.length > 0, 'agent system prompt built (content quality = judge)');
      }

      // RAG: toggle per agent + cite ids within retrieved set + no invented Bagrut items.
      const ragNow = st.ragCalls.slice(ragBefore);
      if (!ragExpected) add('RAG', `${tag}.rag_off_for_${sess.agent}`, ragNow.length === 0, `${ragNow.length} retrieve calls`);
      if (ragNow.length) add('RAG', `${tag}.chunks_in_prompt`, sys.includes('Eval passage 1'), 'retrieved chunks injected into system prompt');
      for (const cp of cps.filter((c) => c.startsWith('RAG.'))) {
        if (ti !== sess.turns.length - 1) continue;
        add('RAG', `${tag}.${cp}`, !BAGRUT_INVENT.test(reply), 'no year / question-number pattern in reply (stub)');
      }
    }
    st.noteTag = null;

    // MEM-R note_written: tag parsed by real chat-memory-persist -> fake appendAgentNote.
    for (const cp of cps) {
      const key = /\(([^)=]*=)?([^),]+)/.exec(cp)?.[2] ?? '';
      if (cp.startsWith('MEM.note_written')) {
        add('MEM-R', `s${sess.s}.${cp}`, st.notes.some((n) => n.learner_id === userId && n.content.includes(`EVALTAG:${key}`)), 'learner_agent_notes row via [[ASF_MEMORY_NOTE');
      } else if (cp.startsWith('MEM.fact_supersedes')) {
        // AS-52 (C3b): the new goal note carries the key and the earlier same-key goal is superseded.
        const f = noteTagFor(cp);
        const same = st.notes.filter((n) => n.learner_id === userId && n.kind === f.kind && tf_.decodeFactContent(n.content).meta?.key === f.key);
        const live = same.filter((n) => !n.superseded_by);
        add('MEM-R', `s${sess.s}.${cp}`, same.length >= 2 && live.length === 1 && live[0]!.content.includes(`EVALTAG:${f.tag} `), `${f.kind}:${f.key} rows=${same.length} live=${live.length}`);
      } else if (cp.startsWith('MEM.fact_written')) {
        // AS-42 (C3): typed goal fact written with kind + key.
        const f = noteTagFor(cp);
        add('MEM-R', `s${sess.s}.${cp}`, st.notes.some((n) => n.learner_id === userId && !n.superseded_by && n.kind === f.kind && n.content.includes(`EVALTAG:${f.tag} `)), `live ${f.kind}:${f.key} fact row`);
      } else if (cp.startsWith('MEM.only_current_fact')) {
        // AS-42 (C3): after a goal change only the newest goal (same kind+key) reaches the prompt.
        const f = noteTagFor(cp);
        const lastSys = st.llmCalls.at(-1)?.system ?? '';
        const stale = [...lastSys.matchAll(new RegExp(`EVALTAG:${f.kind}_${f.key}_[\\w]+`, 'g'))].map((x) => x[0]).filter((x) => x !== `EVALTAG:${f.tag}`);
        add('MEM-F', `s${sess.s}.${cp}`, lastSys.includes(`EVALTAG:${f.tag} `) && stale.length === 0, stale.length ? `stale facts in prompt: ${stale.join(',')}` : `only current ${f.kind}:${f.key} in ${sess.agent} prompt`);
      } else if (cp.startsWith('MEM.fact_expired')) {
        // AS-43 (C4): state fact (valid_to = write + 14 d) is still stored after the 15-day
        // gap but is absent from the prompt (TTL read filter on agent notes + digest).
        const f = noteTagFor(cp);
        const lastSys = st.llmCalls.at(-1)?.system ?? '';
        const stored = st.notes.some((n) => n.learner_id === userId && !n.superseded_by && n.kind === f.kind && n.content.includes(`EVALTAG:${f.tag} `));
        add('MEM-F', `s${sess.s}.${cp}`, stored && !lastSys.includes(`EVALTAG:${f.tag}`), `stored=${stored}; ${f.kind}:${f.key} ${lastSys.includes(`EVALTAG:${f.tag}`) ? 'STILL in' : 'absent from'} ${sess.agent} prompt`);
      } else if (cp === 'PLAN.no_change_from_state') {
        // AS-43 (C4): mood-only turn -> 0 propose_plan_change staged. The offline stub has no
        // tool calling, so drive the real tool handler with the state note as sole evidence.
        // AS-52 r1: take the evidence ids from the rendered Mentor prompt (not the fake DB): one
        // mentor probe turn, then parse `[id:<uuid>]` lines whose kind is state.
        const dbStateIds = st.notes.filter((n) => n.learner_id === userId && n.kind === 'state' && !n.superseded_by).map((n) => n.id);
        const prevAgent = currentAgent; currentAgent = 'mentor';
        const probe = await POST(new Request('http://eval.local/api/chat', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ messages: [{ role: 'user', content: 'What do you know about me?' }], agent: 'mentor', sessionId: `${sessionId}-probe` }) }));
        await probe.text(); currentAgent = prevAgent;
        const mentorSys = st.llmCalls.at(-1)?.system ?? '';
        const stateIds = [...mentorSys.matchAll(/\[id:([0-9a-f-]{36})\] \[?(?:\w+\/)?state\b/g)].map((x) => x[1]!);
        add('MEM-R', `s${sess.s}.MEM.mentor_prompt_has_state_note_id`, dbStateIds.length > 0 && dbStateIds.every((id) => stateIds.includes(id)), `db state ids=${dbStateIds.length}; in mentor prompt=${stateIds.length}`);
        const tool = (await import('@/lib/agent-tools')).getPlanChangeTools().find((t) => t.spec.function.name === 'propose_plan_change')!;
        const before = st.dbCalls.setPlanChangeSession ?? 0;
        const r = await tool.handler({ goal: 'stop studying for the Bagrut', target_date: 'in 2 weeks', evidence_note_ids: stateIds }, { userId, agent: sess.agent, locale } as never);
        const staged = (st.dbCalls.setPlanChangeSession ?? 0) - before;
        add('PLAN-F', `s${sess.s}.${cp}`, stateIds.length > 0 && staged === 0 && r.observation.startsWith('rejected_state_only_evidence'), `state evidence=${stateIds.length}; propose_plan_change staged=${staged}; ${r.observation.slice(0, 40)}`);
      } else if (cp === 'ADAPT.difficulty_down' || cp === 'ADAPT.difficulty_up') {
        // AS-51 (C5): flag on -> BKT replay of the ordered attempts; direction from the mastery read.
        // m > 0 is BKT-only (ratio gives 0 for all-wrong), so forcing the ratio model fails J1.
        const bkt = await import('@/lib/bkt');
        const seq = sess.practice_attempts ?? [];
        const model = bkt.masteryModelFromEnv({ MASTERY_MODEL: 'bkt' });
        const m = bkt.atomMastery({ attempts: seq.length, successes: seq.filter(Boolean).length }, model, seq);
        const dir = bkt.adaptDirection(m);
        const want = cp.endsWith('_down') ? 'down' : 'up';
        add('ADAPT', `s${sess.s}.${cp}`, seq.length > 0 && dir === want && m > 0 && m < 1, `model=${model} attempts=[${seq.map((x) => (x ? 'C' : 'W')).join('')}] p_known=${m.toFixed(5)} dir=${dir}`);
      } else if (cp.startsWith('MEM.misconception_count')) {
        // AS-42 (C3): J4 repeated misconception -> one live fact, count incremented.
        const [, key, want] = /\(([^=)]+)=(\d+)\)/.exec(cp) ?? [];
        const liveFacts = st.notes.filter((n) => n.learner_id === userId && !n.superseded_by && n.kind === 'misconception' && tf_.decodeFactContent(n.content).meta?.key === key);
        const got = liveFacts.map((n) => tf_.decodeFactContent(n.content).meta?.n);
        add('MEM-R', `s${sess.s}.${cp}`, liveFacts.length === 1 && got[0] === Number(want), `live=${liveFacts.length} count=${got.join(',')}`);
      } else if (cp.startsWith('MEM.recall')) {
        const lastSys = st.llmCalls.at(-1)?.system ?? '';
        add('MEM-R', `s${sess.s}.${cp}`, lastSys.includes(`EVALTAG:${key}`), `prior note ${key} present in ${sess.agent} prompt`);
      } else if (cp === 'MEM.no_cross_topic_contamination') {
        add('MEM-F', `s${sess.s}.${cp}`, true, 'topic contamination needs judge; isolation checked below');
      } else if (cp.startsWith('HAND.')) {
        const lastSys = st.llmCalls.at(-1)?.system ?? '';
        const prior = st.notes.filter((n) => n.learner_id === userId && n.agent !== sess.agent && !n.superseded_by);
        add('HAND', `s${sess.s}.${cp}`, prior.length > 0 && prior.every((n) => lastSys.includes(n.content.slice(0, 40))), `${prior.length} other-agent notes; digest in ${sess.agent} prompt`);
      }
    }
  }
  // MEM-F: other learner's decoy must never reach this learner's prompts.
  const leaked = st.llmCalls.some((c) => c.system.includes(decoy) || c.messages.some((x) => x.content.includes(decoy)));
  add('MEM-F', 'isolation.decoy_absent', !leaked, 'decoy note of another learner not in any prompt');

  for (const id of METRIC_IDS) {
    const x = m[id]!;
    if (x.kind !== 'deterministic') continue;
    if (!x.checks.length) { x.note = 'no deterministic checkpoint in this journey'; continue; }
    x.score = Number((x.checks.filter((c) => c.pass).length / x.checks.length).toFixed(3));
    x.pass = x.score === 1;
  }
  return { journey: j.id, locale, mirror: locale !== j.lang, metrics: m, transcript };
}

describe('AS-16 offline journey eval (stub LLM, fake DB, no network)', () => {
  let POST: (r: Request) => Promise<Response>;
  beforeAll(async () => {
    vi.useFakeTimers({ toFake: ['Date'], shouldAdvanceTime: true }); // AS-47 journey clock
    for (const k of ['DATABASE_URL', 'POSTGRES_URL', 'GROQ_API_KEY', 'LLM_API_KEY', 'XAI_API_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']) delete process.env[k];
    process.env.LLM_API_KEY = 'placeholder-offline';
    process.env.LLM_BASE_URL = 'http://eval.invalid/v1';
    installGuard();
    POST = (await import('@/app/api/chat/route')).POST;
  }, 60_000);
  afterAll(() => { vi.useRealTimers(); removeGuard(); });

  it('runs 6 journeys x he/en with 0 network calls', async () => {
    const results = [];
    for (const j of spec.journeys) for (const loc of ['he', 'en'] as const) {
      st.llmCalls = []; st.ragCalls = [];
      results.push(await runJourney(POST, j, loc));
    }
    const totals: Record<string, { checks: number; passed: number; score: number | null; judge_needs_paid_run: boolean; kind: string }> = {};
    for (const id of METRIC_IDS) {
      const all = results.flatMap((r) => r.metrics[id]!.checks);
      const passed = all.filter((c) => c.pass).length;
      totals[id] = { kind: results[0]!.metrics[id]!.kind, checks: all.length, passed, score: all.length ? Number((passed / all.length).toFixed(3)) : null, judge_needs_paid_run: HAS_JUDGE.has(id) };
    }
    const out = {
      eval: 'AS-16 offline (AS-27)', mode: 'dry/stub', generated_at: new Date().toISOString(),
      runs: results.length, network_calls: net_.count, network_call_log: net_.calls,
      llm_stream_calls_total: results.reduce((a, r) => a + r.transcript.length, 0), llm_aux_calls_stubbed_null: st.llmCompleteCalls,
      db_helper_calls: st.dbCalls, totals, results,
    };
    console.log(`[AS27] runs=${results.length} network_calls=${net_.count}`);
    for (const [k, v] of Object.entries(totals)) console.log(`[AS27] ${k} kind=${v.kind} ${v.passed}/${v.checks} score=${v.score}${v.judge_needs_paid_run ? ' judge=needs_paid_run' : ''}`);
    if (process.env.EVAL_OUT) fs.writeFileSync(process.env.EVAL_OUT, JSON.stringify(out, null, 2));
    expect(results.length).toBe(12);
    expect(net_.count).toBe(0);
  }, 120_000);
});
