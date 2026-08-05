/**
 * Agent tool registry for the ReAct tool-calling loop (ADR-0015, Phase A).
 *
 * Each tool exposes an OpenAI-style `spec` (advertised to the model) and a
 * server-side `handler` that runs the actual work and returns a compact
 * observation string the model reads on the next loop turn. Handlers are the
 * ONLY place a tool touches data — the model never gets raw DB access.
 *
 * Phase A ships read-only tools (retrieve, get_lesson, learning_plan.next).
 * Phase B adds the plan-change mutation family behind a server-enforced gate.
 */
import 'server-only';
import type { LLMTool } from '@/lib/llm-provider';
import { retrieveChunks, detectLang } from '@/lib/rag-retrieve';
import { fetchLessonByConceptId } from '@/lib/neon-db';
import { buildLearningPlan } from '@/lib/learning-plan';
import { logger } from '@/lib/logger';

export interface ToolContext {
  userId: string;
  agent: string;
  /** Response locale for shaping observation prose ('he' | 'en'). */
  locale: 'he' | 'en';
}

export interface ToolResult {
  /** Compact text the model reads as the tool observation. */
  observation: string;
  /** Concept ids this tool touched, for turn grounding / citations. */
  groundingIds?: string[];
}

export interface AgentTool {
  spec: LLMTool;
  handler: (args: Record<string, unknown>, ctx: ToolContext) => Promise<ToolResult>;
}

const MAX_OBSERVATION_CHARS = 1600;

/** Strip ATX headings + clamp length so a tool body can't hijack prompt sections. */
function sanitizeObservation(text: string): string {
  const cleaned = text.replace(/(^|\n)#{1,6}[ \t]+/g, '$1').trim();
  return cleaned.length > MAX_OBSERVATION_CHARS
    ? `${cleaned.slice(0, MAX_OBSERVATION_CHARS)}…`
    : cleaned;
}

function asString(v: unknown): string {
  return typeof v === 'string' ? v.trim() : '';
}

// ---------------------------------------------------------------------------
// retrieve — hybrid RAG over the authored bilingual corpus
// ---------------------------------------------------------------------------
const retrieveTool: AgentTool = {
  spec: {
    type: 'function',
    function: {
      name: 'retrieve',
      description:
        'Search the authored bilingual course corpus for passages relevant to a ' +
        'learner question or concept. Use this to ground factual/explanatory ' +
        'answers in our own content before replying. Returns numbered passages ' +
        'with their concept ids.',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'The search query, in the learner’s language.',
          },
          lang: {
            type: 'string',
            enum: ['he', 'en'],
            description: 'Optional language filter; auto-detected when omitted.',
          },
        },
        required: ['query'],
      },
    },
  },
  handler: async (args) => {
    const query = asString(args.query);
    if (!query) return { observation: 'No query provided.' };
    const langArg = asString(args.lang);
    const lang = langArg === 'he' || langArg === 'en' ? langArg : detectLang(query);
    try {
      const chunks = await retrieveChunks({ query, lang, topK: 4 });
      if (chunks.length === 0) {
        return { observation: 'No matching passages found in the corpus.' };
      }
      const groundingIds = chunks
        .map((c) => c.conceptId)
        .filter((id): id is string => Boolean(id));
      const body = chunks
        .map((c, i) => {
          const label = c.heading || c.title || c.sourceDocId;
          const cid = c.conceptId ? ` (concept:${c.conceptId})` : '';
          return `[${i + 1}] ${label}${cid}: ${c.text}`;
        })
        .join('\n\n');
      return { observation: sanitizeObservation(body), groundingIds };
    } catch (err) {
      logger.warn('tool retrieve failed', { err: String(err) });
      return { observation: 'Retrieval is temporarily unavailable.' };
    }
  },
};

// ---------------------------------------------------------------------------
// get_lesson — compact authored-lesson summary by concept id
// ---------------------------------------------------------------------------
const getLessonTool: AgentTool = {
  spec: {
    type: 'function',
    function: {
      name: 'get_lesson',
      description:
        'Fetch a compact summary of the authored lesson for a knowledge-graph ' +
        'concept id (e.g. from a retrieve result). Returns title, summary, and ' +
        'section headings so you can point the learner to structured material.',
      parameters: {
        type: 'object',
        properties: {
          concept_id: {
            type: 'string',
            description: 'The knowledge-graph concept id, e.g. "limit_of_function".',
          },
        },
        required: ['concept_id'],
      },
    },
  },
  handler: async (args, ctx) => {
    const conceptId = asString(args.concept_id);
    if (!conceptId) return { observation: 'No concept_id provided.' };
    try {
      const lesson = await fetchLessonByConceptId(conceptId).catch(() => null);
      if (!lesson) {
        return { observation: `No authored lesson found for concept "${conceptId}".` };
      }
      const l = lesson.lesson;
      const he = ctx.locale === 'he';
      const title = (he ? l.title_he : l.title_en) || l.title_en || l.title_he;
      const summary = (he ? l.summary_he : l.summary_en) || l.summary_en || l.summary_he;
      const headings = (l.sections ?? [])
        .map((s) => (he ? s.title_he : s.title_en) || s.title_en || s.title_he)
        .filter(Boolean)
        .slice(0, 12);
      const parts = [
        `Lesson: ${title} (concept:${l.concept_id}, subject:${l.subject}, level:${l.level})`,
        summary ? `Summary: ${summary}` : '',
        headings.length ? `Sections: ${headings.join(' · ')}` : '',
      ].filter(Boolean);
      return {
        observation: sanitizeObservation(parts.join('\n')),
        groundingIds: [l.concept_id],
      };
    } catch (err) {
      logger.warn('tool get_lesson failed', { conceptId, err: String(err) });
      return { observation: 'Lesson lookup is temporarily unavailable.' };
    }
  },
};

// ---------------------------------------------------------------------------
// learning_plan_next — mastery-aware next steps toward a goal concept
// ---------------------------------------------------------------------------
const learningPlanNextTool: AgentTool = {
  spec: {
    type: 'function',
    function: {
      name: 'learning_plan_next',
      description:
        'Given a goal concept id, return the mastery-aware next study steps for ' +
        'THIS learner (ordered path + weakest blocking skill atoms). Use to answer ' +
        '"what should I study next?" / "why am I stuck?".',
      parameters: {
        type: 'object',
        properties: {
          goal_concept_id: {
            type: 'string',
            description: 'The goal concept id from the knowledge graph.',
          },
        },
        required: ['goal_concept_id'],
      },
    },
  },
  handler: async (args, ctx) => {
    const goalConceptId = asString(args.goal_concept_id);
    if (!goalConceptId) return { observation: 'No goal_concept_id provided.' };
    try {
      const plan = await buildLearningPlan({
        learnerId: ctx.userId,
        goalConceptId,
        maxNodes: 8,
      });
      if (!plan) {
        return {
          observation: `No plan could be built for goal "${goalConceptId}" (unknown concept?).`,
        };
      }
      const he = ctx.locale === 'he';
      const steps = plan.path
        .slice(0, 6)
        .map((n, i) => {
          const name = (he ? n.name_he : n.name) || n.name;
          return `${i + 1}. ${name} (concept:${n.concept_id}, urgency:${n.urgency.toFixed(2)})`;
        })
        .join('\n');
      const atoms = plan.blocking_atoms
        .slice(0, 5)
        .map((a) => `${a.atom} (mastery:${a.mastery.toFixed(2)})`)
        .join(', ');
      const goalName = (he ? plan.goal.name_he : plan.goal.name) || plan.goal.name;
      const parts = [
        `Goal: ${goalName} (concept:${plan.goal.concept_id})`,
        steps ? `Next steps:\n${steps}` : 'No open steps — goal appears mastered.',
        atoms ? `Weak atoms: ${atoms}` : '',
      ].filter(Boolean);
      return {
        observation: sanitizeObservation(parts.join('\n')),
        groundingIds: [plan.goal.concept_id, ...plan.path.map((n) => n.concept_id)],
      };
    } catch (err) {
      logger.warn('tool learning_plan_next failed', { goalConceptId, err: String(err) });
      return { observation: 'Plan lookup is temporarily unavailable.' };
    }
  },
};

/**
 * Read-only tool set for a learner-facing agent. All four chat agents may use
 * these; plan-mutation tools (Phase B) are added only for Tutor + Mentor.
 */
export function getReadOnlyTools(): AgentTool[] {
  return [retrieveTool, getLessonTool, learningPlanNextTool];
}

/**
 * Tools available to a given agent this turn. Phase A: Tutor / Mentor / Coach
 * get the read-only set; Reviewer is unchanged (no tools yet).
 */
export function getToolsForAgent(agent: string): AgentTool[] {
  if (agent === 'tutor' || agent === 'mentor' || agent === 'coach') {
    return getReadOnlyTools();
  }
  return [];
}
