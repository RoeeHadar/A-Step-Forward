/**
 * Unified Neon access layer for Vercel server actions / API routes.
 *
 * All reads + writes that the free-tier UI needs go through this module.
 * The Render backend is treated as an optional accelerator — when present
 * it can override stuff (e.g. provide real CAT diagnostic logic) but its
 * absence must not break the user flow.
 *
 * Uses @neondatabase/serverless (HTTP, no TCP pool).
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { randomUUID } from 'node:crypto';
import kg from './kg-data.json';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
export const dbConfigured = Boolean(url);
const sql = dbConfigured ? neon(url) : null;

function requireSql() {
  if (!sql) {
    throw new Error(
      'DATABASE_URL is not set on this Vercel deployment. Add it in Project Settings → Environment Variables.',
    );
  }
  return sql;
}

// ── Onboarding / learner profile ─────────────────────────────────────────────

export interface OnboardingPayload {
  goal: string;
  grade_level?: string | null;
  points_group?: string | null;
  subjects: string[];
  hours_per_week: number;
  preferred_style?: string | null;
  attention_span?: number | null;
  self_scores?: Record<string, number>;
  background_notes?: string | null;
  next_test_name?: string | null;
  next_test_date?: string | null; // ISO date
  final_goal_date?: string | null;
  mental_state?: Record<string, unknown> | null;
  personality_profile?: Record<string, unknown> | null;
}

export interface LearnerProfileRow {
  learner_id: string;
  goal: string;
  grade_level: string | null;
  points_group: string | null;
  subjects: string[];
  hours_per_week: number;
  preferred_style: string | null;
  attention_span: number | null;
  self_scores: Record<string, number> | null;
  background_notes: string | null;
  next_test_name: string | null;
  next_test_date: string | null;
  final_goal_date: string | null;
  mental_state: Record<string, unknown> | null;
  personality_profile: Record<string, unknown> | null;
  weak_concepts: string[] | null;
  strong_concepts: string[] | null;
  created_at: string;
  updated_at: string;
}

export async function upsertLearnerProfile(
  learnerId: string,
  p: OnboardingPayload,
): Promise<void> {
  const s = requireSql();
  await s`
    INSERT INTO learner_profiles (
      learner_id, goal, grade_level, points_group, subjects, hours_per_week,
      preferred_style, attention_span, self_scores, background_notes,
      next_test_name, next_test_date, final_goal_date, mental_state, personality_profile,
      created_at, updated_at
    )
    VALUES (
      ${learnerId}, ${p.goal}, ${p.grade_level ?? null}, ${p.points_group ?? null},
      ${p.subjects}, ${p.hours_per_week},
      ${p.preferred_style ?? null}, ${p.attention_span ?? null},
      ${JSON.stringify(p.self_scores ?? {})}::jsonb, ${p.background_notes ?? null},
      ${p.next_test_name ?? null}, ${p.next_test_date ?? null}, ${p.final_goal_date ?? null},
      ${JSON.stringify(p.mental_state ?? {})}::jsonb,
      ${JSON.stringify(p.personality_profile ?? {})}::jsonb,
      NOW(), NOW()
    )
    ON CONFLICT (learner_id) DO UPDATE SET
      goal = EXCLUDED.goal,
      grade_level = EXCLUDED.grade_level,
      points_group = EXCLUDED.points_group,
      subjects = EXCLUDED.subjects,
      hours_per_week = EXCLUDED.hours_per_week,
      preferred_style = EXCLUDED.preferred_style,
      attention_span = EXCLUDED.attention_span,
      self_scores = EXCLUDED.self_scores,
      background_notes = EXCLUDED.background_notes,
      next_test_name = EXCLUDED.next_test_name,
      next_test_date = EXCLUDED.next_test_date,
      final_goal_date = EXCLUDED.final_goal_date,
      mental_state = EXCLUDED.mental_state,
      personality_profile = EXCLUDED.personality_profile,
      updated_at = NOW()
  `;

  // Seed concept_mastery from self_scores (1-10 → 0.1-0.9)
  const entries = Object.entries(p.self_scores ?? {});
  for (const [conceptId, score] of entries) {
    const clamped = Math.max(1, Math.min(10, score));
    const mastery = 0.1 + ((clamped - 1) * 0.8) / 9;
    await s`
      INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
      VALUES (${learnerId}, ${conceptId}, ${mastery}, 1, NOW(), NOW())
      ON CONFLICT (learner_id, concept_id) DO UPDATE SET
        score = EXCLUDED.score,
        last_activity = NOW()
    `;
  }
}

export async function getLearnerProfile(
  learnerId: string,
): Promise<LearnerProfileRow | null> {
  const s = requireSql();
  const rows = (await s`
    SELECT * FROM learner_profiles WHERE learner_id = ${learnerId} LIMIT 1
  `) as LearnerProfileRow[];
  return rows[0] ?? null;
}

export async function getConceptMastery(
  learnerId: string,
): Promise<Record<string, number>> {
  const s = requireSql();
  const rows = (await s`
    SELECT concept_id, score::float AS score FROM concept_mastery WHERE learner_id = ${learnerId}
  `) as Array<{ concept_id: string; score: number }>;
  const result: Record<string, number> = {};
  for (const r of rows) result[r.concept_id] = r.score;
  return result;
}

// ── Diagnostic ───────────────────────────────────────────────────────────────

export interface DiagnosticItem {
  id: string;
  topic: string;
  subject: string;
  difficulty: number;
  stem: string;
  options: { choices: string[]; correct: string };
  source_concept: string;
}

export interface DiagnosticQuestion {
  id: string;
  topic: string;
  subject: string;
  difficulty: number;
  stem: string;
  options: { key: string; text: string }[];
}

export async function startDiagnosticSession(
  learnerId: string,
  topics: string[],
): Promise<string> {
  const s = requireSql();
  const id = randomUUID();
  await s`
    INSERT INTO diagnostic_sessions (id, learner_id, status, topics, question_idx, created_at)
    VALUES (${id}, ${learnerId}, 'active', ${topics}, 0, NOW())
  `;
  return id;
}

export async function fetchDiagnosticItems(
  subjects: string[],
  limit: number,
): Promise<DiagnosticItem[]> {
  const s = requireSql();
  const rows = (await s`
    SELECT id::text, topic, subject, difficulty::float AS difficulty, stem, options, source_concept
    FROM diagnostic_items
    WHERE subject = ANY(${subjects})
    ORDER BY random()
    LIMIT ${limit}
  `) as DiagnosticItem[];
  return rows;
}

export function itemToQuestion(item: DiagnosticItem): DiagnosticQuestion {
  const keys = ['A', 'B', 'C', 'D'];
  return {
    id: item.id,
    topic: item.topic,
    subject: item.subject,
    difficulty: item.difficulty,
    stem: item.stem,
    options: (item.options.choices ?? []).slice(0, 4).map((text, i) => ({
      key: keys[i] ?? String(i),
      text,
    })),
  };
}

export async function getDiagnosticSession(
  sessionId: string,
): Promise<{
  id: string;
  learner_id: string;
  status: string;
  topics: string[];
  question_idx: number;
  results: Record<string, unknown> | null;
} | null> {
  const s = requireSql();
  const rows = (await s`
    SELECT id::text, learner_id, status, topics, question_idx, results
    FROM diagnostic_sessions WHERE id = ${sessionId} LIMIT 1
  `) as Array<{
    id: string;
    learner_id: string;
    status: string;
    topics: string[];
    question_idx: number;
    results: Record<string, unknown> | null;
  }>;
  return rows[0] ?? null;
}

export async function recordDiagnosticAnswer(
  sessionId: string,
  itemId: string,
  correct: boolean,
  topic: string,
  learnerId: string,
): Promise<void> {
  const s = requireSql();
  await s`
    INSERT INTO quiz_responses (id, quiz_id, quiz_type, item_id, chosen, correct, created_at)
    VALUES (gen_random_uuid(), ${sessionId}::uuid, 'diagnostic', ${itemId}::uuid, '', ${correct}, NOW())
  `;

  // Update running mastery for this topic
  const newScore = correct ? 0.7 : 0.3;
  await s`
    INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
    VALUES (${learnerId}, ${topic}, ${newScore}, 1, NOW(), NOW())
    ON CONFLICT (learner_id, concept_id) DO UPDATE SET
      score = (concept_mastery.score * concept_mastery.data_points + ${newScore}) /
              (concept_mastery.data_points + 1),
      data_points = concept_mastery.data_points + 1,
      last_activity = NOW()
  `;
}

export async function bumpDiagnosticIdx(sessionId: string): Promise<number> {
  const s = requireSql();
  const rows = (await s`
    UPDATE diagnostic_sessions SET question_idx = question_idx + 1 WHERE id = ${sessionId}
    RETURNING question_idx
  `) as Array<{ question_idx: number }>;
  return rows[0]?.question_idx ?? 0;
}

export async function completeDiagnostic(
  sessionId: string,
  learnerId: string,
): Promise<Record<string, number>> {
  const s = requireSql();
  const mastery = await getConceptMastery(learnerId);
  await s`
    UPDATE diagnostic_sessions
    SET status = 'completed',
        completed_at = NOW(),
        results = ${JSON.stringify({ mastery_by_topic: mastery })}::jsonb
    WHERE id = ${sessionId}
  `;
  return mastery;
}

// ── Plan generation ──────────────────────────────────────────────────────────

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  prerequisites: string[];
}
const kgConcepts: KgConcept[] = (kg as { concepts: KgConcept[] }).concepts;
const kgPrereqMap: Record<string, string[]> = (kg as { prereqMap: Record<string, string[]> }).prereqMap;
const kgById: Record<string, KgConcept> = (kg as { byId: Record<string, KgConcept> }).byId;

const WEAK_THRESHOLD = 0.4;
const PHYSICS_HINTS = new Set([
  'kinematics', 'dynamics', 'electricity', 'magnetism', 'waves', 'optics',
  'nuclear', 'momentum', 'energy', 'newton', 'rotation',
]);

function inferSubject(conceptId: string, subjects: string[]): string {
  if (!subjects.length) return 'math';
  if (subjects.length === 1) return subjects[0]!;
  const lower = conceptId.toLowerCase();
  for (const h of PHYSICS_HINTS) {
    if (lower.includes(h)) return subjects.includes('physics') ? 'physics' : subjects[0]!;
  }
  return subjects.includes('math') ? 'math' : subjects[0]!;
}

function depthOf(concept: string, universe: Set<string>, memo: Map<string, number>): number {
  if (memo.has(concept)) return memo.get(concept)!;
  const prereqs = (kgPrereqMap[concept] ?? []).filter((p) => universe.has(p));
  if (prereqs.length === 0) {
    memo.set(concept, 0);
    return 0;
  }
  memo.set(concept, 0); // breaks cycles
  const d = Math.max(...prereqs.map((p) => depthOf(p, universe, memo))) + 1;
  memo.set(concept, d);
  return d;
}

function collectWorklist(
  mastery: Record<string, number>,
  selfScores: Record<string, number> | null,
  subjects: string[],
): Set<string> {
  const worklist = new Set<string>();
  for (const [c, score] of Object.entries(mastery)) {
    if (score < WEAK_THRESHOLD) worklist.add(c);
  }
  // expand with prerequisites of weak concepts
  for (const c of [...worklist]) {
    for (const prereq of kgPrereqMap[c] ?? []) {
      if ((mastery[prereq] ?? 0.5) < WEAK_THRESHOLD) worklist.add(prereq);
    }
  }
  // if nothing weak yet, seed from self-scores or subject roots
  if (worklist.size === 0) {
    if (selfScores) {
      for (const c of Object.keys(selfScores)) worklist.add(c);
    } else if (subjects.length > 0) {
      const roots = kgConcepts.filter(
        (c) => subjects.includes(c.subject) && c.prerequisites.length === 0,
      );
      for (const r of roots.slice(0, 5)) worklist.add(r.id);
    }
  }
  return worklist;
}

export interface PlanWeek {
  id: string;
  plan_id: string;
  week_number: number;
  concepts: PlanConcept[];
  quiz_due_at: string | null;
  status: string;
}

export interface PlanConcept {
  concept_id: string;
  name: string;
  subject: string;
  mastery: number | null;
  suggested_sections: Array<{ id: string; title: string; chunk_index: number | null; page_start: number | null }>;
  recommended_bagrut: Array<{ display_name: string; file_url: string; year: number | null; exam_type: string | null }>;
}

export interface LearningPlan {
  id: string;
  learner_id: string;
  goal: string;
  start_date: string;
  end_date: string | null;
  status: string;
  weeks: PlanWeek[];
}

export async function generateLearningPlan(learnerId: string): Promise<LearningPlan> {
  const s = requireSql();
  const profile = await getLearnerProfile(learnerId);
  if (!profile) {
    throw new Error('Complete onboarding before generating a learning plan');
  }

  const mastery = await getConceptMastery(learnerId);
  const worklist = collectWorklist(mastery, profile.self_scores, profile.subjects);

  // Determine number of weeks from next_test_date / final_goal_date
  let numWeeks = 4;
  if (profile.next_test_date) {
    const days = Math.ceil(
      (new Date(profile.next_test_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
    );
    numWeeks = Math.max(1, Math.min(12, Math.ceil(days / 7)));
  } else if (profile.final_goal_date) {
    const days = Math.ceil(
      (new Date(profile.final_goal_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
    );
    numWeeks = Math.max(2, Math.min(16, Math.ceil(days / 7)));
  }

  // Sort by prerequisite depth (roots first)
  const memo = new Map<string, number>();
  const sorted = [...worklist].sort(
    (a, b) => depthOf(a, worklist, memo) - depthOf(b, worklist, memo),
  );

  // Chunk into weeks (round-robin so each week has roughly equal load)
  const weekGroups: string[][] = Array.from({ length: numWeeks }, () => []);
  const maxPerWeek = Math.max(3, Math.ceil(sorted.length / numWeeks));
  let weekIdx = 0;
  for (const concept of sorted) {
    while (weekGroups[weekIdx]!.length >= maxPerWeek) {
      weekIdx = (weekIdx + 1) % numWeeks;
    }
    weekGroups[weekIdx]!.push(concept);
    weekIdx = (weekIdx + 1) % numWeeks;
  }

  // Persist plan + weeks
  const planId = randomUUID();
  const startDate = new Date();
  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + 7 * numWeeks);
  const startStr = startDate.toISOString().slice(0, 10);
  const endStr = endDate.toISOString().slice(0, 10);

  await s`DELETE FROM plan_weeks WHERE plan_id IN (SELECT id FROM learning_plans WHERE learner_id = ${learnerId})`;
  await s`DELETE FROM learning_plans WHERE learner_id = ${learnerId}`;
  await s`
    INSERT INTO learning_plans (id, learner_id, goal, start_date, end_date, status, created_at, updated_at)
    VALUES (${planId}, ${learnerId}, ${profile.goal}, ${startStr}, ${endStr}, 'active', NOW(), NOW())
  `;

  const weeks: PlanWeek[] = [];
  for (let i = 0; i < weekGroups.length; i++) {
    const concepts = weekGroups[i]!;
    const weekId = randomUUID();
    const quizDue = new Date(startDate);
    quizDue.setDate(quizDue.getDate() + 7 * (i + 1));
    const status = i === 0 ? 'active' : 'upcoming';
    await s`
      INSERT INTO plan_weeks (id, plan_id, week_number, concepts, quiz_due_at, status)
      VALUES (${weekId}, ${planId}, ${i + 1}, ${concepts}, ${quizDue.toISOString()}, ${status})
    `;
    const hydrated: PlanConcept[] = [];
    for (const cid of concepts) {
      const kgInfo = kgById[cid];
      const subject = kgInfo?.subject ?? inferSubject(cid, profile.subjects);
      const sections = (await s`
        SELECT id::text, title, chunk_index, page_start
        FROM content_sections WHERE subject = ${subject} ORDER BY chunk_index LIMIT 3
      `) as Array<{ id: string; title: string; chunk_index: number | null; page_start: number | null }>;
      const bagrut = (await s`
        SELECT display_name, file_url, year, exam_type
        FROM bagrut_exams WHERE subject = ${subject} ORDER BY year DESC NULLS LAST LIMIT 2
      `) as Array<{ display_name: string; file_url: string; year: number | null; exam_type: string | null }>;
      hydrated.push({
        concept_id: cid,
        name: kgInfo?.name ?? cid.replace(/_/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase()),
        subject,
        mastery: mastery[cid] ?? null,
        suggested_sections: sections,
        recommended_bagrut: bagrut,
      });
    }
    weeks.push({
      id: weekId,
      plan_id: planId,
      week_number: i + 1,
      concepts: hydrated,
      quiz_due_at: quizDue.toISOString(),
      status,
    });
  }

  return {
    id: planId,
    learner_id: learnerId,
    goal: profile.goal,
    start_date: startStr,
    end_date: endStr,
    status: 'active',
    weeks,
  };
}

export async function getCurrentPlan(learnerId: string): Promise<LearningPlan | null> {
  const s = requireSql();
  const planRows = (await s`
    SELECT id::text, learner_id, goal, start_date::text, end_date::text, status
    FROM learning_plans WHERE learner_id = ${learnerId} AND status = 'active' LIMIT 1
  `) as Array<{
    id: string;
    learner_id: string;
    goal: string;
    start_date: string;
    end_date: string | null;
    status: string;
  }>;
  const plan = planRows[0];
  if (!plan) return null;

  const weekRows = (await s`
    SELECT id::text, week_number, concepts, quiz_due_at, status
    FROM plan_weeks WHERE plan_id = ${plan.id}::uuid ORDER BY week_number
  `) as Array<{
    id: string;
    week_number: number;
    concepts: string[];
    quiz_due_at: string | null;
    status: string;
  }>;

  const mastery = await getConceptMastery(learnerId);
  const profile = await getLearnerProfile(learnerId);
  const subjects = profile?.subjects ?? [];

  const weeks: PlanWeek[] = [];
  for (const w of weekRows) {
    const hydrated: PlanConcept[] = [];
    for (const cid of w.concepts) {
      const kgInfo = kgById[cid];
      const subject = kgInfo?.subject ?? inferSubject(cid, subjects);
      const sections = (await s`
        SELECT id::text, title, chunk_index, page_start
        FROM content_sections WHERE subject = ${subject} ORDER BY chunk_index LIMIT 3
      `) as Array<{ id: string; title: string; chunk_index: number | null; page_start: number | null }>;
      const bagrut = (await s`
        SELECT display_name, file_url, year, exam_type
        FROM bagrut_exams WHERE subject = ${subject} ORDER BY year DESC NULLS LAST LIMIT 2
      `) as Array<{ display_name: string; file_url: string; year: number | null; exam_type: string | null }>;
      hydrated.push({
        concept_id: cid,
        name: kgInfo?.name ?? cid.replace(/_/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase()),
        subject,
        mastery: mastery[cid] ?? null,
        suggested_sections: sections,
        recommended_bagrut: bagrut,
      });
    }
    weeks.push({
      id: w.id,
      plan_id: plan.id,
      week_number: w.week_number,
      concepts: hydrated,
      quiz_due_at: w.quiz_due_at,
      status: w.status,
    });
  }

  return { ...plan, weeks };
}

// ── Chat memory ──────────────────────────────────────────────────────────────

export interface ChatTurn {
  role: 'user' | 'assistant';
  content: string;
  agent: string;
  created_at: string;
}

export async function recordChatTurn(
  learnerId: string,
  agent: string,
  role: 'user' | 'assistant',
  content: string,
  sessionId?: string,
): Promise<void> {
  if (!sql) return;
  try {
    await sql`
      INSERT INTO chat_turns (id, learner_id, agent, role, content, session_id, created_at)
      VALUES (gen_random_uuid(), ${learnerId}, ${agent}, ${role}, ${content}, ${sessionId ?? null}, NOW())
    `;
  } catch (err) {
    console.warn('[neon-db] recordChatTurn failed', err);
  }
}

export async function fetchRecentChatTurns(
  learnerId: string,
  agent: string,
  limit = 10,
): Promise<ChatTurn[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT role, content, agent, created_at
      FROM chat_turns
      WHERE learner_id = ${learnerId} AND agent = ${agent}
      ORDER BY created_at DESC
      LIMIT ${limit}
    `) as ChatTurn[];
    return rows.reverse(); // oldest first for chat context
  } catch (err) {
    console.warn('[neon-db] fetchRecentChatTurns failed', err);
    return [];
  }
}

// ── External resources ──────────────────────────────────────────────────────

export interface ExternalResource {
  title: string;
  url: string;
  source: string;
  language: string;
  description: string | null;
}

export async function fetchExternalResources(subject: string): Promise<ExternalResource[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT title, url, source, language, description
      FROM external_resources
      WHERE subject = ${subject}
      ORDER BY sort_order, title
    `) as ExternalResource[];
    return rows;
  } catch {
    return [];
  }
}

// ── Concept explanations (in-house adapted from CC sources) ────────────────

export interface ConceptExplanation {
  concept_id: string;
  language: string;
  title: string;
  body_md: string;
  body_html: string | null;
  summary: string | null;
  image_url: string | null;
  source: string;
  source_url: string;
  source_lang: string;
  license: string;
  attribution: string;
  fetched_at: string;
}

export interface ConceptCoverage {
  concept_id: string;
  languages: string[];
}

export async function fetchConceptExplanation(
  conceptId: string,
  language: string,
): Promise<ConceptExplanation | null> {
  if (!sql) return null;
  try {
    const rows = (await sql`
      SELECT concept_id, language, title, body_md, body_html, summary, image_url,
             source, source_url, source_lang, license, attribution, fetched_at
      FROM concept_explanations
      WHERE concept_id = ${conceptId} AND language = ${language}
      ORDER BY fetched_at DESC
      LIMIT 1
    `) as ConceptExplanation[];
    return rows[0] ?? null;
  } catch {
    return null;
  }
}

export async function fetchConceptExplanationFallback(
  conceptId: string,
  preferredLang: string,
): Promise<ConceptExplanation | null> {
  if (!sql) return null;
  try {
    const rows = (await sql`
      SELECT concept_id, language, title, body_md, body_html, summary, image_url,
             source, source_url, source_lang, license, attribution, fetched_at
      FROM concept_explanations
      WHERE concept_id = ${conceptId}
      ORDER BY CASE WHEN language = ${preferredLang} THEN 0 ELSE 1 END, fetched_at DESC
      LIMIT 1
    `) as ConceptExplanation[];
    return rows[0] ?? null;
  } catch {
    return null;
  }
}

export async function fetchConceptsWithExplanations(
  conceptIds: string[],
): Promise<Map<string, string[]>> {
  if (!sql || conceptIds.length === 0) return new Map();
  try {
    // Neon HTTP driver has flaky semantics for `ANY(${array})` parameter binding,
    // so we pull all rows and filter in JS. The table is small (~200 rows) and
    // this read happens at most once per /learn/[subject] render.
    const rows = (await sql`
      SELECT concept_id, ARRAY_AGG(DISTINCT language) AS langs
      FROM concept_explanations
      GROUP BY concept_id
    `) as Array<{ concept_id: string; langs: string[] }>;
    const wanted = new Set(conceptIds);
    return new Map(
      rows.filter((r) => wanted.has(r.concept_id)).map((r) => [r.concept_id, r.langs]),
    );
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('fetchConceptsWithExplanations failed:', err);
    }
    return new Map();
  }
}
