/**
 * Weekly plan quiz — Neon + Groq path (no Render cold-start).
 */
import 'server-only';
import { randomUUID } from 'node:crypto';
import type { QuizStartResponse, QuizQuestion } from '@asf/schemas/learning_path';
import {
  getConceptMastery,
  getLearnerProfile,
  fetchLessonAgentHintsByConceptIds,
  ensureWeeklyQuizCacheTable,
  getCachedWeeklyQuiz,
  saveWeeklyQuiz,
} from '@/lib/neon-db';
import kg from '@/lib/kg-data.json';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  skill_atoms: string[];
  prerequisites?: string[];
}

const kgConcepts = (kg as { concepts: KgConcept[] }).concepts;
const kgById: Record<string, KgConcept> = (kg as { byId: Record<string, KgConcept> }).byId;

export interface StoredWeeklyQuestion {
  id: string;
  topic: string;
  subject: string;
  difficulty: number;
  stem: string;
  stem_he?: string;
  options: { key: string; text: string }[];
  correct: string;
}

const GROQ_MODELS = ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile'];
const GROQ_TIMEOUT_MS = 25_000;

function isoWeekStart(): string {
  const now = new Date();
  const day = now.getUTCDay();
  const diff = day === 0 ? -6 : 1 - day;
  const monday = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + diff));
  return monday.toISOString().slice(0, 10);
}

async function pickWeakConcepts(learnerId: string, limit = 6): Promise<string[]> {
  const mastery = await getConceptMastery(learnerId).catch(() => ({} as Record<string, number>));
  const sorted = Object.entries(mastery)
    .filter(([id]) => Boolean(kgById[id]))
    .sort((a, b) => a[1] - b[1])
    .map(([id]) => id);

  if (sorted.length >= 3) return sorted.slice(0, limit);

  const profile = await getLearnerProfile(learnerId).catch(() => null);
  const subjects = profile?.subjects?.length ? profile.subjects : ['math'];
  const subjectSet = new Set(subjects.map((s) => s.toLowerCase()));
  const roots = kgConcepts
    .filter((c) => subjectSet.has(c.subject) && (c.prerequisites?.length ?? 0) === 0)
    .map((c) => c.id);
  const fallback = roots.length > 0 ? roots : kgConcepts.slice(0, 6).map((c) => c.id);
  return [...new Set([...sorted, ...fallback])].slice(0, limit);
}

const WEEKLY_SYSTEM = `You are a bilingual (Hebrew + English) high-school quiz author for Israeli Bagrut prep.

Output ONLY JSON: { "questions": [ ... ] }

Each question MUST be multiple-choice (mcq) with:
- concept_id (one of the supplied ids)
- stem_en, stem_he (<= 400 chars each)
- options_en, options_he (3-4 strings, same length)
- correct_index (0-based int)
- difficulty: "easy" | "medium" | "hard"

Generate exactly the requested count. Spread across supplied concepts. Math in $...$ LaTeX. No PII.`;

async function generateQuestionsViaGroq(
  conceptIds: string[],
  count: number,
): Promise<StoredWeeklyQuestion[] | null> {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) return null;

  const hintsRows = await fetchLessonAgentHintsByConceptIds(conceptIds).catch(() => []);
  const hintsByConcept = new Map(hintsRows.map((r) => [r.concept_id, r.agent_hints]));

  const blocks = conceptIds
    .map((id) => {
      const c = kgById[id];
      if (!c) return null;
      const hints = hintsByConcept.get(id);
      const atoms = (c.skill_atoms?.length ? c.skill_atoms : hints?.skill_atoms_unlocked ?? []).slice(0, 8);
      return `### ${id}\nname: ${c.name}\nsubject: ${c.subject}\natoms: ${atoms.join(' | ') || 'general'}`;
    })
    .filter(Boolean)
    .join('\n\n');

  const userPrompt = `Generate exactly ${count} mcq questions (count between 5 and 10).\n\nConcepts:\n${blocks}`;

  for (const model of GROQ_MODELS) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), GROQ_TIMEOUT_MS);
    try {
      const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages: [
            { role: 'system', content: WEEKLY_SYSTEM },
            { role: 'user', content: userPrompt },
          ],
          response_format: { type: 'json_object' },
          max_tokens: 3072,
          temperature: 0.4,
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (!resp.ok) continue;

      const body = (await resp.json()) as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      const raw = body.choices?.[0]?.message?.content;
      if (!raw) continue;

      const parsed = JSON.parse(raw) as { questions?: unknown[] };
      if (!Array.isArray(parsed.questions)) continue;

      const keys = ['A', 'B', 'C', 'D'];
      const out: StoredWeeklyQuestion[] = [];
      const allowed = new Set(conceptIds);

      for (const item of parsed.questions) {
        if (!item || typeof item !== 'object') continue;
        const q = item as Record<string, unknown>;
        const conceptId = typeof q.concept_id === 'string' ? q.concept_id : '';
        if (!allowed.has(conceptId)) continue;
        const c = kgById[conceptId];
        if (!c) continue;
        if (typeof q.stem_en !== 'string' || typeof q.stem_he !== 'string') continue;
        if (!Array.isArray(q.options_en) || !Array.isArray(q.options_he)) continue;
        const en = q.options_en.filter((x): x is string => typeof x === 'string');
        const he = q.options_he.filter((x): x is string => typeof x === 'string');
        if (en.length !== he.length || en.length < 2) continue;
        if (typeof q.correct_index !== 'number' || q.correct_index < 0 || q.correct_index >= en.length) continue;

        const diff =
          q.difficulty === 'hard' ? 0.8 : q.difficulty === 'medium' ? 0.5 : 0.3;

        out.push({
          id: randomUUID(),
          topic: conceptId,
          subject: c.subject,
          difficulty: diff,
          stem: q.stem_en,
          stem_he: q.stem_he,
          options: en.map((text, i) => ({ key: keys[i] ?? String(i), text })),
          correct: keys[q.correct_index] ?? 'A',
        });
      }

      if (out.length >= 3) return out.slice(0, 10);
    } catch {
      clearTimeout(timeoutId);
    }
  }
  return null;
}

function toClientQuestions(stored: StoredWeeklyQuestion[]): QuizQuestion[] {
  return stored.map((q) => ({
    id: q.id,
    topic: q.topic,
    subject: q.subject,
    difficulty: q.difficulty,
    stem: q.stem,
    options: q.options,
  }));
}

export async function getOrCreateWeeklyQuiz(args: {
  learnerId: string;
  planId: string;
  weekNum: number;
  weekId: string;
}): Promise<QuizStartResponse | null> {
  await ensureWeeklyQuizCacheTable();
  const weekStart = isoWeekStart();

  const cached = await getCachedWeeklyQuiz(args.learnerId, weekStart);
  if (cached && cached.length > 0) {
    return {
      quiz_id: randomUUID(),
      week_id: args.weekId,
      plan_id: args.planId,
      week_number: args.weekNum,
      time_limit_s: 30 * 60,
      questions: toClientQuestions(cached),
      started_at: new Date().toISOString(),
    };
  }

  const concepts = await pickWeakConcepts(args.learnerId);
  if (concepts.length === 0) return null;

  const count = Math.min(10, Math.max(5, concepts.length + 2));
  const generated = await generateQuestionsViaGroq(concepts, count);
  if (!generated || generated.length === 0) return null;

  await saveWeeklyQuiz(args.learnerId, weekStart, generated);

  return {
    quiz_id: randomUUID(),
    week_id: args.weekId,
    plan_id: args.planId,
    week_number: args.weekNum,
    time_limit_s: 30 * 60,
    questions: toClientQuestions(generated),
    started_at: new Date().toISOString(),
  };
}
