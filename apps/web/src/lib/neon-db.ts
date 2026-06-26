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
  /** Optional HE variants (migration 0015). Null → falls back to EN. */
  stem_he: string | null;
  options_he: { choices: string[]; correct: string } | null;
  explanation_he: string | null;
}

export interface DiagnosticQuestion {
  id: string;
  topic: string;
  subject: string;
  difficulty: number;
  stem: string;
  options: { key: string; text: string }[];
  /** Bilingual companion fields. When `stem_he`/`options_he` are present
   * the UI can render either language; the actual choice happens on the
   * client side from the persisted `asf_lang` preference. */
  stem_he: string | null;
  options_he: { key: string; text: string }[] | null;
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
    SELECT id::text, topic, subject, difficulty::float AS difficulty,
           stem, options, source_concept,
           stem_he, options_he, explanation_he
    FROM diagnostic_items
    WHERE subject = ANY(${subjects})
    ORDER BY random()
    LIMIT ${limit}
  `) as DiagnosticItem[];
  return rows;
}

export function itemToQuestion(item: DiagnosticItem): DiagnosticQuestion {
  const keys = ['A', 'B', 'C', 'D'];
  const toOptions = (opts: { choices: string[] } | null | undefined) =>
    (opts?.choices ?? []).slice(0, 4).map((text, i) => ({
      key: keys[i] ?? String(i),
      text,
    }));
  return {
    id: item.id,
    topic: item.topic,
    subject: item.subject,
    difficulty: item.difficulty,
    stem: item.stem,
    options: toOptions(item.options),
    // HE variants are returned to the client as soon as they exist in the
    // DB. UI picks which language to render based on `useLanguagePreference`.
    stem_he: item.stem_he,
    options_he: item.options_he ? toOptions(item.options_he) : null,
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

// ── AI-authored lessons (table: `lessons` + `lesson_questions`) ───────────────

export interface LessonSection {
  kind: 'intro' | 'theory' | 'worked_example' | 'pitfall' | 'practice_tip' | 'summary';
  title_en: string;
  title_he: string;
  body_en_md: string;
  body_he_md: string;
}

export interface LessonAgentHints {
  key_insights?: string[];
  common_misconceptions?: Array<{
    wrong: string;
    correction: string;
    detect_phrase_en?: string;
    detect_phrase_he?: string;
  }>;
  skill_atoms_unlocked?: string[];
  prerequisites_to_check_before_teaching?: string[];
  tutor_pacing_hint?: string;
  coach_drill_skills?: string[];
  diagnostic_signals?: Record<string, string>;
  next_recommended?: string[];
}

export interface LessonRow {
  id: string;
  concept_id: string;
  subject: string;
  level: string;
  math_track: string[];
  title_en: string;
  title_he: string;
  summary_en: string;
  summary_he: string;
  sections: LessonSection[];
  agent_hints: LessonAgentHints;
  est_minutes: number;
  author: string;
  version: number;
}

export type LessonQuestionKind =
  | 'mcq'
  | 'mcq_multi'
  | 'true_false'
  | 'open'
  | 'short_answer'
  | 'fill_blank'
  | 'numeric'
  | 'match'
  | 'ordering'
  | 'derivation';

export interface LessonAnswerPayload {
  // Common to many kinds; only some fields populated per kind.
  correct_indices?: number[];
  correct_bool?: boolean;
  acceptable_answers?: string[];
  case_sensitive?: boolean;
  left_en?: string[];
  left_he?: string[];
  right_en?: string[];
  right_he?: string[];
  correct_pairs?: number[];
  steps_en?: string[];
  steps_he?: string[];
  correct_order?: number[];
  expected_steps?: string[];
}

export interface LessonQuestionRow {
  id: string;
  lesson_id: string;
  ord: number;
  kind: LessonQuestionKind;
  difficulty: 'easy' | 'medium' | 'hard';
  stem_en: string;
  stem_he: string;
  options_en: string[] | null;
  options_he: string[] | null;
  correct_index: number | null;
  correct_answer: string | null;
  answer_payload: LessonAnswerPayload | null;
  rubric_en: string | null;
  rubric_he: string | null;
  explanation_en: string;
  explanation_he: string;
  skill_atoms: string[];
}

export interface LessonWithQuestions {
  lesson: LessonRow;
  questions: LessonQuestionRow[];
}

export async function fetchLessonByConceptId(
  conceptId: string,
): Promise<LessonWithQuestions | null> {
  if (!sql) return null;
  try {
    const lessonRows = (await sql`
      SELECT id, concept_id, subject, level, math_track,
             title_en, title_he, summary_en, summary_he,
             sections, agent_hints, est_minutes, author, version
      FROM lessons
      WHERE concept_id = ${conceptId}
      LIMIT 1
    `) as LessonRow[];
    const lesson = lessonRows[0];
    if (!lesson) return null;
    const questions = (await sql`
      SELECT id, lesson_id, ord, kind, difficulty,
             stem_en, stem_he, options_en, options_he,
             correct_index, correct_answer, answer_payload,
             rubric_en, rubric_he,
             explanation_en, explanation_he, skill_atoms
      FROM lesson_questions
      WHERE lesson_id = ${lesson.id}
      ORDER BY ord ASC
    `) as LessonQuestionRow[];
    return { lesson, questions };
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('fetchLessonByConceptId failed:', err);
    }
    return null;
  }
}

/**
 * Lightweight fetch of agent hints for one or more concept IDs. Used by the
 * Tutor route to inject `key_insights`, `common_misconceptions`,
 * `tutor_pacing_hint`, and `detect_phrase_*` triggers into the system prompt
 * without paying for the full lesson body.
 */
export async function fetchLessonAgentHintsByConceptIds(
  conceptIds: string[],
): Promise<
  Array<{ concept_id: string; title_en: string; title_he: string; agent_hints: LessonAgentHints }>
> {
  if (!sql || conceptIds.length === 0) return [];
  try {
    const rows = (await sql`
      SELECT concept_id, title_en, title_he, agent_hints
      FROM lessons
      WHERE concept_id = ANY(${conceptIds}::text[])
    `) as Array<{
      concept_id: string;
      title_en: string;
      title_he: string;
      agent_hints: LessonAgentHints;
    }>;
    return rows;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('fetchLessonAgentHintsByConceptIds failed:', err);
    }
    return [];
  }
}

/**
 * Loads the minimal fields needed to grade a single question server-side.
 * Used by /api/lesson/answer so the client's `correct` flag can never be
 * trusted for objective question kinds.
 */
export async function fetchLessonQuestionForGrading(
  questionId: string,
): Promise<Pick<
  LessonQuestionRow,
  'id' | 'kind' | 'correct_index' | 'correct_answer' | 'answer_payload'
> | null> {
  if (!sql) return null;
  try {
    const rows = (await sql`
      SELECT id, kind, correct_index, correct_answer, answer_payload
      FROM lesson_questions
      WHERE id = ${questionId}::uuid
      LIMIT 1
    `) as Array<Pick<
      LessonQuestionRow,
      'id' | 'kind' | 'correct_index' | 'correct_answer' | 'answer_payload'
    >>;
    return rows[0] ?? null;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('fetchLessonQuestionForGrading failed:', err);
    }
    return null;
  }
}

/**
 * Server-side grader. Returns { correct, graded_by } where `graded_by` is
 * 'server' for objective kinds we can verify and 'self' for open/derivation
 * kinds that rely on the learner's self-assessment.
 */
export function gradeLessonAnswer(
  q: Pick<LessonQuestionRow, 'kind' | 'correct_index' | 'correct_answer' | 'answer_payload'>,
  userAnswer: unknown,
  clientCorrect: boolean | undefined,
): { correct: boolean; graded_by: 'server' | 'self'; reason?: string } {
  const norm = (s: string, cs = false) => {
    const t = s.trim().replace(/\s+/g, ' ');
    return cs ? t : t.toLowerCase();
  };
  const numericClose = (a: string, b: string): boolean => {
    const na = Number.parseFloat(a);
    const nb = Number.parseFloat(b);
    if (Number.isNaN(na) || Number.isNaN(nb)) return false;
    const tol = Math.max(1e-3, Math.abs(nb) * 0.01);
    return Math.abs(na - nb) <= tol;
  };
  const arraysEqual = (a: number[], b: number[]) =>
    a.length === b.length && a.every((v, i) => v === b[i]);
  const setEqual = (a: number[], b: number[]) =>
    arraysEqual([...a].sort((x, y) => x - y), [...b].sort((x, y) => x - y));

  switch (q.kind) {
    case 'mcq': {
      if (typeof userAnswer !== 'number' || q.correct_index == null) {
        return { correct: false, graded_by: 'server', reason: 'invalid answer' };
      }
      return { correct: userAnswer === q.correct_index, graded_by: 'server' };
    }
    case 'mcq_multi': {
      const expected = q.answer_payload?.correct_indices ?? [];
      const picked = Array.isArray(userAnswer)
        ? (userAnswer as unknown[]).filter((v): v is number => typeof v === 'number')
        : [];
      return { correct: setEqual(picked, expected), graded_by: 'server' };
    }
    case 'true_false': {
      if (typeof userAnswer !== 'boolean' || typeof q.answer_payload?.correct_bool !== 'boolean') {
        return { correct: false, graded_by: 'server', reason: 'invalid answer' };
      }
      return { correct: userAnswer === q.answer_payload.correct_bool, graded_by: 'server' };
    }
    case 'numeric': {
      if (typeof userAnswer !== 'string' || !q.correct_answer) {
        return { correct: false, graded_by: 'server', reason: 'invalid answer' };
      }
      return { correct: numericClose(userAnswer, q.correct_answer), graded_by: 'server' };
    }
    case 'fill_blank': {
      if (typeof userAnswer !== 'string' || !q.correct_answer) {
        return { correct: false, graded_by: 'server', reason: 'invalid answer' };
      }
      return { correct: norm(userAnswer) === norm(q.correct_answer), graded_by: 'server' };
    }
    case 'short_answer': {
      if (typeof userAnswer !== 'string') {
        return { correct: false, graded_by: 'server', reason: 'invalid answer' };
      }
      const cs = q.answer_payload?.case_sensitive ?? false;
      const accepted = (q.answer_payload?.acceptable_answers ?? []).map((a) => norm(a, cs));
      return { correct: accepted.includes(norm(userAnswer, cs)), graded_by: 'server' };
    }
    case 'match': {
      const expected = q.answer_payload?.correct_pairs ?? [];
      const userPairs = Array.isArray(userAnswer)
        ? (userAnswer as unknown[]).map((v) => (typeof v === 'number' ? v : -1))
        : [];
      return {
        correct: userPairs.length === expected.length && arraysEqual(userPairs, expected),
        graded_by: 'server',
      };
    }
    case 'ordering': {
      const expected = q.answer_payload?.correct_order ?? [];
      const userOrder = Array.isArray(userAnswer)
        ? (userAnswer as unknown[]).filter((v): v is number => typeof v === 'number')
        : [];
      return {
        correct: userOrder.length === expected.length && arraysEqual(userOrder, expected),
        graded_by: 'server',
      };
    }
    case 'open':
    case 'derivation': {
      // No server-side grader for free-form answers yet; fall back to the
      // learner's self-assessment. A future Grader-agent pass could re-score
      // these against `rubric_en` / `explanation_en` and overwrite.
      return { correct: Boolean(clientCorrect), graded_by: 'self' };
    }
    default:
      return { correct: Boolean(clientCorrect), graded_by: 'self', reason: 'unknown kind' };
  }
}

export async function fetchLessonAvailability(
  conceptIds: string[],
): Promise<Set<string>> {
  if (!sql || conceptIds.length === 0) return new Set();
  try {
    const rows = (await sql`
      SELECT concept_id FROM lessons
    `) as Array<{ concept_id: string }>;
    const wanted = new Set(conceptIds);
    return new Set(rows.map((r) => r.concept_id).filter((id) => wanted.has(id)));
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('fetchLessonAvailability failed:', err);
    }
    return new Set();
  }
}

export interface LessonMeta {
  concept_id: string;
  subject: string;
  math_track: string[];
}

/**
 * Returns metadata for any lessons whose `concept_id` is in `conceptIds`.
 * Used by the subject page to decide which concept tiles to show and
 * which math-track (3pt/4pt/5pt) variants to surface.
 */
export async function fetchLessonMetaByConceptIds(
  conceptIds: string[],
): Promise<Map<string, LessonMeta>> {
  const out = new Map<string, LessonMeta>();
  if (!sql || conceptIds.length === 0) return out;
  try {
    const rows = (await sql`
      SELECT concept_id, subject, COALESCE(math_track, '{}'::text[]) AS math_track
      FROM lessons
      WHERE concept_id = ANY(${conceptIds}::text[])
    `) as Array<{ concept_id: string; subject: string; math_track: string[] }>;
    for (const r of rows) out.set(r.concept_id, r);
    return out;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('fetchLessonMetaByConceptIds failed:', err);
    }
    return out;
  }
}

export async function recordLessonAnswer(args: {
  learnerId: string;
  lessonId: string;
  questionId: string;
  conceptId: string;
  correct: boolean;
  skillAtoms: string[];
  timeSpentS?: number | null;
}): Promise<void> {
  const s = requireSql();
  const { learnerId, lessonId, questionId, conceptId, correct, skillAtoms } = args;

  await s`
    INSERT INTO quiz_responses (id, quiz_id, quiz_type, item_id, chosen, correct, created_at)
    VALUES (gen_random_uuid(), ${lessonId}::uuid, 'lesson', ${questionId}::uuid, '', ${correct}, NOW())
  `;

  const newScore = correct ? 0.75 : 0.35;
  await s`
    INSERT INTO concept_mastery (learner_id, concept_id, score, data_points, last_activity, created_at)
    VALUES (${learnerId}, ${conceptId}, ${newScore}, 1, NOW(), NOW())
    ON CONFLICT (learner_id, concept_id) DO UPDATE SET
      score = (concept_mastery.score * concept_mastery.data_points + ${newScore}) /
              (concept_mastery.data_points + 1),
      data_points = concept_mastery.data_points + 1,
      last_activity = NOW()
  `;

  for (const atom of skillAtoms) {
    if (!atom || typeof atom !== 'string') continue;
    await s`
      INSERT INTO skill_practice (learner_id, skill_atom, attempts, successes, last_practiced)
      VALUES (${learnerId}, ${atom}, 1, ${correct ? 1 : 0}, NOW())
      ON CONFLICT (learner_id, skill_atom) DO UPDATE SET
        attempts = skill_practice.attempts + 1,
        successes = skill_practice.successes + ${correct ? 1 : 0},
        last_practiced = NOW()
    `;
  }
}

// ── Learner persona (CLAUDE.md-style, shared across every agent) ─────────────

/**
 * Per-learner, free-form persona string. Agents read it on every turn as the
 * "what this learner is like" baseline; the Memory Steward (and any agent
 * promoted to do so) is allowed to rewrite or append. PII is stripped before
 * write — never store learner names, contact details, or other identifiers.
 *
 * Recommended structure (kept short, < 1200 chars, markdown):
 *
 *   ## How they talk
 *   - Casual Hebrew; uses English math terms; types fast and short.
 *
 *   ## How they like explanations
 *   - One worked example first, then the rule. Hates dense definitions.
 *
 *   ## Triggers / preferences
 *   - Anxiety spikes near exam dates → soften tone.
 *   - Prefers physics intuition over pure math abstraction.
 *
 *   ## Recent observations (last 7d)
 *   - Got SSS vs. SSA confused twice (2026-06-25).
 */
export interface LearnerPersona {
  learner_id: string;
  text: string | null;
  updated_at: string | null;
}

export async function getLearnerPersona(
  learnerId: string,
): Promise<LearnerPersona | null> {
  if (!sql) return null;
  try {
    const rows = (await sql`
      SELECT learner_id,
             learner_persona AS text,
             learner_persona_updated_at AS updated_at
      FROM learner_profiles
      WHERE learner_id = ${learnerId}
      LIMIT 1
    `) as Array<LearnerPersona>;
    return rows[0] ?? null;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[neon-db] getLearnerPersona failed', err);
    }
    return null;
  }
}

/**
 * Overwrite (full replace) the learner persona. We cap at 4000 chars so a
 * runaway agent can't blow out the prompt budget.
 */
export async function setLearnerPersona(
  learnerId: string,
  text: string,
): Promise<void> {
  if (!sql) return;
  const clamped = text.slice(0, 4000);
  await sql`
    UPDATE learner_profiles
    SET learner_persona = ${clamped},
        learner_persona_updated_at = NOW(),
        updated_at = NOW()
    WHERE learner_id = ${learnerId}
  `;
}

/**
 * Append a single bullet line to the learner persona under the given section
 * heading (creating the section if it doesn't exist). Idempotent on exact
 * duplicate lines. Total length stays clamped to 4000 chars.
 */
export async function appendLearnerPersonaLine(
  learnerId: string,
  section: string,
  line: string,
): Promise<void> {
  if (!sql) return;
  const existing = await getLearnerPersona(learnerId);
  const cur = existing?.text ?? '';
  const bullet = `- ${line.trim()}`.replace(/\s+/g, ' ');
  if (cur.includes(bullet)) return;
  const header = `## ${section.trim()}`;
  let next: string;
  if (cur.includes(header)) {
    const lines = cur.split('\n');
    const idx = lines.findIndex((l) => l.trim() === header);
    let insertAt = lines.length;
    for (let i = idx + 1; i < lines.length; i += 1) {
      if (lines[i]?.startsWith('## ')) {
        insertAt = i;
        break;
      }
    }
    lines.splice(insertAt, 0, bullet);
    next = lines.join('\n');
  } else {
    next = cur ? `${cur.trim()}\n\n${header}\n${bullet}\n` : `${header}\n${bullet}\n`;
  }
  await setLearnerPersona(learnerId, next.slice(0, 4000));
}

// ── Per-(learner, agent) cumulative additive notes ──────────────────────────

export interface LearnerAgentNote {
  id: string;
  learner_id: string;
  agent: string;
  kind: string;
  content: string;
  importance: number;
  related_concept_id: string | null;
  source_turn_id: string | null;
  created_at: string;
  last_referenced_at: string | null;
}

/**
 * Read the top-K most-useful notes for (learner, agent). Sorted by importance
 * desc, then created_at desc. Filters out archived + superseded rows. Each
 * agent only sees its OWN scratchpad — never another agent's.
 */
export async function fetchAgentNotes(
  learnerId: string,
  agent: string,
  limit = 8,
): Promise<LearnerAgentNote[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      SELECT id::text, learner_id, agent, kind, content, importance,
             related_concept_id, source_turn_id::text AS source_turn_id,
             created_at, last_referenced_at
      FROM learner_agent_notes
      WHERE learner_id = ${learnerId}
        AND agent = ${agent}
        AND archived_at IS NULL
        AND superseded_by IS NULL
      ORDER BY importance DESC, created_at DESC
      LIMIT ${limit}
    `) as LearnerAgentNote[];
    return rows;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[neon-db] fetchAgentNotes failed', err);
    }
    return [];
  }
}

export interface NewAgentNote {
  kind?: string;            // 'observation' | 'preference' | 'strategy' | 'open_question' | …
  content: string;
  importance?: number;      // 1..5; default 3
  related_concept_id?: string | null;
  source_turn_id?: string | null;
}

/**
 * Append a new note for (learner, agent). Returns the new note id. Caller
 * is expected to clamp `content` to a reasonable length (we hard-cap at 600).
 */
export async function appendAgentNote(
  learnerId: string,
  agent: string,
  note: NewAgentNote,
): Promise<string | null> {
  if (!sql) return null;
  const id = randomUUID();
  const content = note.content.slice(0, 600);
  const importance = Math.max(1, Math.min(5, note.importance ?? 3));
  try {
    await sql`
      INSERT INTO learner_agent_notes
        (id, learner_id, agent, kind, content, importance,
         related_concept_id, source_turn_id, created_at)
      VALUES
        (${id}, ${learnerId}, ${agent}, ${note.kind ?? 'observation'},
         ${content}, ${importance},
         ${note.related_concept_id ?? null},
         ${note.source_turn_id ?? null},
         NOW())
    `;
    return id;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[neon-db] appendAgentNote failed', err);
    }
    return null;
  }
}

/**
 * Mark a note as superseded by another, or archive it. Used by the dreaming /
 * consolidation pass and by agents that explicitly want to retract a stale
 * note.
 */
export async function supersedeAgentNote(
  noteId: string,
  by: string | null,
): Promise<void> {
  if (!sql) return;
  if (by) {
    await sql`UPDATE learner_agent_notes SET superseded_by = ${by}::uuid WHERE id = ${noteId}::uuid`;
  } else {
    await sql`UPDATE learner_agent_notes SET archived_at = NOW() WHERE id = ${noteId}::uuid`;
  }
}

/**
 * Returns counts of (learner, agent) live notes — used by the dreaming
 * endpoint to decide whether a consolidation pass is needed.
 */
export async function countAgentNotes(
  learnerId: string,
  agent: string,
): Promise<number> {
  if (!sql) return 0;
  const rows = (await sql`
    SELECT COUNT(*)::int AS n
    FROM learner_agent_notes
    WHERE learner_id = ${learnerId} AND agent = ${agent}
      AND archived_at IS NULL AND superseded_by IS NULL
  `) as Array<{ n: number }>;
  return rows[0]?.n ?? 0;
}

// ── Activity streak (used by /dashboard) ────────────────────────────────────

export interface LearnerStreak {
  current_days: number;
  longest_days: number;
  last_active: string | null;
  active_today: boolean;
  active_days_last_30: number;
}

/**
 * Compute the learner's activity streak by union-ing every "something
 * happened" signal that carries a `learner_id`:
 *
 *   - `chat_turns.created_at` (any message sent or received)
 *   - `concept_mastery.last_activity` (bumped by every diagnostic /
 *     lesson / quiz answer that touches a concept)
 *   - `skill_practice.last_practiced` (bumped by every atom-tagged answer)
 *
 * A day counts as active if any of these fired during the learner's local
 * day (we treat the DB's `CURRENT_DATE` as the local day — good enough
 * until per-learner timezones land).
 *
 * NOTE on `quiz_responses`: this table has no `learner_id` column, so we
 * can't filter it directly. Instead, every learner-affecting `quiz_responses`
 * insert is paired with a `concept_mastery` upsert (see `recordLessonAnswer`,
 * `recordDiagnosticAnswer`), which means `concept_mastery.last_activity`
 * already captures the quiz signal transitively.
 */
export async function getLearnerStreak(learnerId: string): Promise<LearnerStreak> {
  if (!sql) {
    return {
      current_days: 0,
      longest_days: 0,
      last_active: null,
      active_today: false,
      active_days_last_30: 0,
    };
  }
  try {
    const rows = (await sql`
      WITH days AS (
        SELECT DISTINCT date_trunc('day', created_at)::date AS d
        FROM chat_turns WHERE learner_id = ${learnerId}
        UNION
        SELECT DISTINCT date_trunc('day', last_activity)::date
        FROM concept_mastery WHERE learner_id = ${learnerId} AND last_activity IS NOT NULL
        UNION
        SELECT DISTINCT date_trunc('day', last_practiced)::date
        FROM skill_practice WHERE learner_id = ${learnerId} AND last_practiced IS NOT NULL
      ),
      ordered AS (
        SELECT d, ROW_NUMBER() OVER (ORDER BY d) AS rn FROM days
      ),
      runs AS (
        SELECT d, d - (rn || ' days')::interval AS grp FROM ordered
      ),
      run_lengths AS (
        SELECT grp, COUNT(*) AS c, MAX(d) AS last_d FROM runs GROUP BY grp
      )
      SELECT
        (SELECT MAX(d)::text FROM days) AS last_active,
        EXISTS (SELECT 1 FROM days WHERE d = CURRENT_DATE) AS active_today,
        (SELECT COUNT(*) FROM days WHERE d >= CURRENT_DATE - 29) AS active_days_last_30,
        COALESCE((
          SELECT c FROM run_lengths
          WHERE last_d >= CURRENT_DATE - 1
          ORDER BY last_d DESC LIMIT 1
        ), 0) AS current_days,
        COALESCE((SELECT MAX(c) FROM run_lengths), 0) AS longest_days
    `) as Array<{
      last_active: string | null;
      active_today: boolean;
      active_days_last_30: number;
      current_days: number;
      longest_days: number;
    }>;
    const r = rows[0];
    return {
      current_days: Number(r?.current_days ?? 0),
      longest_days: Number(r?.longest_days ?? 0),
      last_active: r?.last_active ?? null,
      active_today: Boolean(r?.active_today),
      active_days_last_30: Number(r?.active_days_last_30 ?? 0),
    };
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[neon-db] getLearnerStreak failed', err);
    }
    return {
      current_days: 0,
      longest_days: 0,
      last_active: null,
      active_today: false,
      active_days_last_30: 0,
    };
  }
}

export interface RecentActivityItem {
  kind: 'chat' | 'lesson' | 'quiz';
  agent: string | null;
  concept_id: string | null;
  detail: string;
  created_at: string;
}

/**
 * Returns the learner's last N "real" actions across chat, concept-level
 * answers (from `concept_mastery.last_activity`), and atom practice
 * (from `skill_practice.last_practiced`).
 *
 * We don't query `quiz_responses` directly because it has no `learner_id`
 * column — but every quiz/lesson answer bumps `concept_mastery`, so the
 * activity is captured via the concept stream.
 */
export async function getRecentActivity(
  learnerId: string,
  limit = 8,
): Promise<RecentActivityItem[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      WITH unioned AS (
        SELECT 'chat'::text AS kind, agent::text AS agent, NULL::text AS concept_id,
               left(content, 80) AS detail, created_at
        FROM chat_turns
        WHERE learner_id = ${learnerId} AND role = 'user'
        UNION ALL
        SELECT 'lesson'::text AS kind, NULL::text AS agent, concept_id::text AS concept_id,
               'practiced ' || COALESCE(concept_id, '')
                 || ' (mastery ' || ROUND(score::numeric * 100)::text || '%)' AS detail,
               last_activity AS created_at
        FROM concept_mastery
        WHERE learner_id = ${learnerId} AND last_activity IS NOT NULL
        UNION ALL
        SELECT 'quiz'::text AS kind, NULL::text AS agent, NULL::text AS concept_id,
               'practiced atom ' || skill_atom
                 || ' (' || successes::text || '/' || attempts::text || ')' AS detail,
               last_practiced AS created_at
        FROM skill_practice
        WHERE learner_id = ${learnerId} AND last_practiced IS NOT NULL
      )
      SELECT kind, agent, concept_id, detail, created_at
      FROM unioned
      ORDER BY created_at DESC
      LIMIT ${limit}
    `) as RecentActivityItem[];
    return rows;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[neon-db] getRecentActivity failed', err);
    }
    return [];
  }
}

// ── 30-day activity heatmap + this-week recap ────────────────────────────────

export interface DailyActivity {
  /** ISO date (YYYY-MM-DD) in UTC. */
  date: string;
  /** Total signals for that day across chat + concept + atom streams. */
  count: number;
}

/**
 * Returns one row per day for the last `days` calendar days (default 30),
 * INCLUDING zero-count days so the heatmap can render a stable grid. Counts
 * are the sum of three signals on that day:
 *   - chat_turns from the learner (role='user')
 *   - distinct concepts whose mastery was touched
 *   - distinct skill atoms practiced
 *
 * The series is ordered oldest → newest, so the UI can lay it out left-to-right.
 */
export async function getDailyActivity(
  learnerId: string,
  days = 30,
): Promise<DailyActivity[]> {
  if (!sql) return [];
  try {
    const rows = (await sql`
      WITH series AS (
        SELECT generate_series(
          (CURRENT_DATE - (${days - 1}::int))::date,
          CURRENT_DATE::date,
          interval '1 day'
        )::date AS d
      ),
      chat_d AS (
        SELECT date_trunc('day', created_at)::date AS d, COUNT(*)::int AS n
        FROM chat_turns
        WHERE learner_id = ${learnerId} AND role = 'user'
          AND created_at >= CURRENT_DATE - (${days - 1}::int)
        GROUP BY 1
      ),
      mastery_d AS (
        SELECT date_trunc('day', last_activity)::date AS d, COUNT(DISTINCT concept_id)::int AS n
        FROM concept_mastery
        WHERE learner_id = ${learnerId} AND last_activity IS NOT NULL
          AND last_activity >= CURRENT_DATE - (${days - 1}::int)
        GROUP BY 1
      ),
      atom_d AS (
        SELECT date_trunc('day', last_practiced)::date AS d, COUNT(DISTINCT skill_atom)::int AS n
        FROM skill_practice
        WHERE learner_id = ${learnerId} AND last_practiced IS NOT NULL
          AND last_practiced >= CURRENT_DATE - (${days - 1}::int)
        GROUP BY 1
      )
      SELECT to_char(s.d, 'YYYY-MM-DD') AS date,
             (COALESCE(c.n, 0) + COALESCE(m.n, 0) + COALESCE(a.n, 0))::int AS count
      FROM series s
      LEFT JOIN chat_d c ON c.d = s.d
      LEFT JOIN mastery_d m ON m.d = s.d
      LEFT JOIN atom_d a ON a.d = s.d
      ORDER BY s.d ASC
    `) as DailyActivity[];
    return rows;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[neon-db] getDailyActivity failed', err);
    }
    return [];
  }
}

export interface WeeklyRecap {
  /** Monday of the current ISO week in UTC (YYYY-MM-DD). */
  week_start: string;
  /** Sunday of the current ISO week in UTC (YYYY-MM-DD). */
  week_end: string;
  chat_turns: number;
  concepts_touched: number;
  atoms_practiced: number;
  mastery_gain: number;
  best_day: { date: string; count: number } | null;
}

/**
 * Recap of the current ISO week (Mon→Sun, UTC) — used by the dashboard
 * "this week" panel. All counts are confined to the current week so a
 * fresh week starts clean.
 */
export async function getWeeklyRecap(learnerId: string): Promise<WeeklyRecap> {
  const empty: WeeklyRecap = {
    week_start: '',
    week_end: '',
    chat_turns: 0,
    concepts_touched: 0,
    atoms_practiced: 0,
    mastery_gain: 0,
    best_day: null,
  };
  if (!sql) return empty;
  try {
    const rows = (await sql`
      WITH bounds AS (
        SELECT
          (date_trunc('week', CURRENT_DATE))::date AS week_start,
          (date_trunc('week', CURRENT_DATE) + interval '6 days')::date AS week_end
      ),
      chat_count AS (
        SELECT COUNT(*)::int AS n
        FROM chat_turns, bounds
        WHERE learner_id = ${learnerId}
          AND role = 'user'
          AND created_at >= bounds.week_start
          AND created_at <  bounds.week_end + interval '1 day'
      ),
      concept_count AS (
        SELECT COUNT(DISTINCT concept_id)::int AS n,
               COALESCE(SUM(GREATEST(score::numeric, 0)), 0)::numeric AS mastery_sum
        FROM concept_mastery, bounds
        WHERE learner_id = ${learnerId}
          AND last_activity IS NOT NULL
          AND last_activity >= bounds.week_start
          AND last_activity <  bounds.week_end + interval '1 day'
      ),
      atom_count AS (
        SELECT COUNT(DISTINCT skill_atom)::int AS n
        FROM skill_practice, bounds
        WHERE learner_id = ${learnerId}
          AND last_practiced IS NOT NULL
          AND last_practiced >= bounds.week_start
          AND last_practiced <  bounds.week_end + interval '1 day'
      ),
      per_day AS (
        SELECT date_trunc('day', created_at)::date AS d, COUNT(*)::int AS n
        FROM chat_turns, bounds
        WHERE learner_id = ${learnerId}
          AND created_at >= bounds.week_start
          AND created_at <  bounds.week_end + interval '1 day'
        GROUP BY 1
      ),
      best AS (
        SELECT to_char(d, 'YYYY-MM-DD') AS date, n AS count
        FROM per_day ORDER BY n DESC LIMIT 1
      )
      SELECT
        to_char((SELECT week_start FROM bounds), 'YYYY-MM-DD') AS week_start,
        to_char((SELECT week_end   FROM bounds), 'YYYY-MM-DD') AS week_end,
        (SELECT n FROM chat_count) AS chat_turns,
        (SELECT n FROM concept_count) AS concepts_touched,
        (SELECT n FROM atom_count) AS atoms_practiced,
        ROUND((SELECT mastery_sum FROM concept_count) * 100)::int AS mastery_gain,
        (SELECT date FROM best) AS best_date,
        (SELECT count FROM best) AS best_count
    `) as Array<{
      week_start: string;
      week_end: string;
      chat_turns: number;
      concepts_touched: number;
      atoms_practiced: number;
      mastery_gain: number;
      best_date: string | null;
      best_count: number | null;
    }>;
    const r = rows[0];
    if (!r) return empty;
    return {
      week_start: r.week_start,
      week_end: r.week_end,
      chat_turns: Number(r.chat_turns ?? 0),
      concepts_touched: Number(r.concepts_touched ?? 0),
      atoms_practiced: Number(r.atoms_practiced ?? 0),
      mastery_gain: Number(r.mastery_gain ?? 0),
      best_day: r.best_date
        ? { date: r.best_date, count: Number(r.best_count ?? 0) }
        : null,
    };
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[neon-db] getWeeklyRecap failed', err);
    }
    return empty;
  }
}
