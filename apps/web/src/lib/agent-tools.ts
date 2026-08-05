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
import {
  fetchLessonByConceptId,
  getCurrentPlan,
  getLearnerProfile,
  getPlanChangeSession,
  setPlanChangeSession,
  type PlanChangeSession,
} from '@/lib/neon-db';
import { buildLearningPlan } from '@/lib/learning-plan';
import {
  buildProposalDiff,
  buildProposalFromSlots,
  bumpReask,
  escalationPrompt,
  goalScopeIssue,
  mergeSlots,
  missingRequiredSlots,
  shouldEscalate,
  slotPrompt,
  type CurrentPlanFacts,
} from '@/lib/plan-change-slots';
import type { LearnerPlanContext } from '@/lib/plan-scope-enrichment';
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

// ---------------------------------------------------------------------------
// Plan-change tool family (Phase B) — Tutor + Mentor only. These tools only
// COLLECT slots and stage a proposal; they NEVER mutate the plan. The actual
// apply is server-enforced in the chat route on an explicit learner confirm.
// ---------------------------------------------------------------------------

async function loadLearnerCtx(userId: string): Promise<{
  ctx: LearnerPlanContext;
  facts: CurrentPlanFacts;
}> {
  const [profile, plan] = await Promise.all([
    getLearnerProfile(userId).catch(() => null),
    getCurrentPlan(userId).catch(() => null),
  ]);
  const ctx: LearnerPlanContext = {
    subjects: profile?.subjects,
    goal_key:
      (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ?? undefined,
    points_group: profile?.points_group ?? null,
    goal: profile?.goal ?? null,
    planConceptIds: plan?.weeks.flatMap((w) => w.concepts.map((c) => c.concept_id)) ?? [],
    planGoal: plan?.goal ?? null,
  };
  const facts: CurrentPlanFacts = {
    goal: profile?.goal ?? plan?.goal ?? null,
    final_goal_date:
      (profile?.personality_profile as { final_goal_date?: string } | null)?.final_goal_date ??
      plan?.end_date ??
      null,
    hours_per_week:
      (profile?.personality_profile as { hours_per_week?: number } | null)?.hours_per_week ?? null,
  };
  return { ctx, facts };
}

const getCurrentPlanTool: AgentTool = {
  spec: {
    type: 'function',
    function: {
      name: 'get_current_plan',
      description:
        'Read THIS learner’s current goal, target date, and weekly-hours before ' +
        'proposing a plan change. Call this first when the learner asks to change ' +
        'their plan or goal.',
      parameters: { type: 'object', properties: {} },
    },
  },
  handler: async (_args, ctx) => {
    try {
      const { facts } = await loadLearnerCtx(ctx.userId);
      const he = ctx.locale === 'he';
      const parts = [
        `${he ? 'מטרה נוכחית' : 'Current goal'}: ${facts.goal || (he ? 'לא הוגדרה' : 'none set')}`,
        `${he ? 'תאריך יעד' : 'Target date'}: ${facts.final_goal_date || (he ? 'לא הוגדר' : 'none')}`,
        facts.hours_per_week
          ? `${he ? 'שעות בשבוע' : 'Hours/week'}: ${facts.hours_per_week}`
          : '',
      ].filter(Boolean);
      return { observation: parts.join('\n') };
    } catch (err) {
      logger.warn('tool get_current_plan failed', { err: String(err) });
      return { observation: 'Current plan is temporarily unavailable.' };
    }
  },
};

const validateGoalScopeTool: AgentTool = {
  spec: {
    type: 'function',
    function: {
      name: 'validate_goal_scope',
      description:
        'Check whether a proposed goal is specific enough to build a plan. Returns ' +
        'ok, or that it is too broad (e.g. "physics"/"a math test") and must be ' +
        'narrowed to a concrete exam/scope before proposing.',
      parameters: {
        type: 'object',
        properties: {
          goal: { type: 'string', description: 'The proposed goal / exam text.' },
        },
        required: ['goal'],
      },
    },
  },
  handler: async (args, ctx) => {
    const goal = asString(args.goal);
    if (!goal) return { observation: 'No goal provided.' };
    try {
      const { ctx: learnerCtx } = await loadLearnerCtx(ctx.userId);
      const issue = goalScopeIssue(goal, learnerCtx);
      if (!issue) return { observation: 'ok: goal is specific enough.' };
      return {
        observation:
          issue === 'math'
            ? 'too_broad: the goal is a generic "math" goal — ask which exam (Bagrut 3/4/5, Calculus 1, Discrete math, Linear algebra, …).'
            : 'too_broad: the goal is a generic "physics" goal — ask for the scope (Mechanics/036-361, Electricity/036-371, Radiation & Matter/036-282, or the topic list).',
      };
    } catch (err) {
      logger.warn('tool validate_goal_scope failed', { err: String(err) });
      return { observation: 'Scope validation is temporarily unavailable.' };
    }
  },
};

const proposePlanChangeTool: AgentTool = {
  spec: {
    type: 'function',
    function: {
      name: 'propose_plan_change',
      description:
        'Record the plan-change slots the learner has provided so far (goal, ' +
        'target date, optional hours/week, optional focus notes). Pass every slot ' +
        'the learner already gave. Returns either the remaining required question ' +
        'to ask (one at a time) or, when goal + date are set and specific, a ' +
        'current→proposed DIFF to show the learner and ask them to confirm. This ' +
        'NEVER applies the change — the site applies it only after the learner ' +
        'explicitly confirms.',
      parameters: {
        type: 'object',
        properties: {
          goal: { type: 'string', description: 'Goal or exam (specific).' },
          target_date: {
            type: 'string',
            description: 'Target date, e.g. "2026-09-15" or "in two weeks".',
          },
          hours_per_week: { type: 'number', description: 'Optional weekly study hours.' },
          notes: { type: 'string', description: 'Optional focus topics.' },
        },
      },
    },
  },
  handler: async (args, ctx) => {
    try {
      const existing = await getPlanChangeSession(ctx.userId).catch(() => null);
      const { ctx: learnerCtx, facts } = await loadLearnerCtx(ctx.userId);
      const merged = mergeSlots(existing?.slots ?? {}, {
        goal: asString(args.goal) || undefined,
        target_date: asString(args.target_date) || undefined,
        hours_per_week:
          typeof args.hours_per_week === 'number' ? args.hours_per_week : undefined,
        notes: asString(args.notes) || undefined,
      });

      // Determine the single blocking slot (if any): a too-broad goal blocks on
      // 'goal'; otherwise the first missing required slot. Bounded re-asks with
      // escalation to Mentor handoff / pause after SLOT_REASK_LIMIT re-asks.
      const scope = goalScopeIssue(merged.goal, learnerCtx);
      const broadGoal = Boolean(merged.goal && scope);
      const missing = missingRequiredSlots(merged);
      const blockingKey = broadGoal ? 'goal' : missing[0];

      if (blockingKey) {
        const bumped = bumpReask(existing?.reask, blockingKey);
        const escalate = shouldEscalate(bumped.count);
        // Reset this slot's counter on escalation so a later retry starts fresh.
        const reask = escalate ? { ...bumped.reask, [blockingKey]: 0 } : bumped.reask;
        const session: PlanChangeSession = {
          status: 'collecting',
          agent: ctx.agent,
          updated_at: new Date().toISOString(),
          slots: merged,
          reask,
        };
        await setPlanChangeSession(ctx.userId, session).catch(() => undefined);

        if (escalate) {
          return { observation: escalationPrompt(ctx.agent, ctx.locale) };
        }
        if (broadGoal) {
          return {
            observation:
              scope === 'math'
                ? 'still_collecting: the goal is too broad ("math"). Ask the learner which specific exam (Bagrut 3/4/5, Calculus 1, Discrete math, Linear algebra, …).'
                : 'still_collecting: the goal is too broad ("physics"). Ask for the exact scope (Mechanics/036-361, Electricity/036-371, Radiation & Matter/036-282, or the topics).',
          };
        }
        return {
          observation: `still_collecting: ask the learner this one question next → ${slotPrompt(
            blockingKey as Parameters<typeof slotPrompt>[0],
            ctx.locale,
          )}`,
        };
      }

      // All required slots present + specific → stage the proposal + diff.
      const proposal = buildProposalFromSlots(merged, ctx.agent);
      const diff = buildProposalDiff(facts, proposal, ctx.locale);
      const session: PlanChangeSession = {
        status: 'awaiting_confirm',
        agent: ctx.agent,
        updated_at: new Date().toISOString(),
        slots: merged,
        proposal,
        reask: existing?.reask,
      };
      // The proposal MUST be durably persisted before we invite the learner to
      // confirm — otherwise a later "yes" would find no session and silently do
      // nothing while the learner was told the change is pending. On persist
      // failure, be honest and do NOT present a confirmable diff.
      try {
        await setPlanChangeSession(ctx.userId, session);
      } catch (err) {
        logger.warn('tool propose_plan_change persist (confirm) failed', { err: String(err) });
        return {
          observation:
            'staging_unavailable: could not save the pending change. Tell the learner plan updates are temporarily unavailable and to try again shortly. Do NOT present a change to confirm and do NOT claim anything was updated.',
        };
      }
      return {
        observation: [
          'ready_to_confirm: show the learner this exact change summary and ask them to confirm (yes/no). Do NOT say the plan was updated yet — the site applies it only after they confirm.',
          '',
          diff,
        ].join('\n'),
        groundingIds: proposal.priority_concepts,
      };
    } catch (err) {
      logger.warn('tool propose_plan_change failed', { err: String(err) });
      return { observation: 'Plan-change staging is temporarily unavailable.' };
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

/** Plan-change slot-filling tools (Tutor + Mentor). Never mutate — staging only. */
export function getPlanChangeTools(): AgentTool[] {
  return [getCurrentPlanTool, validateGoalScopeTool, proposePlanChangeTool];
}

/**
 * Tools available to a given agent this turn. Tutor / Mentor / Coach get the
 * read-only set; on a plan-change turn Tutor + Mentor additionally get the
 * plan-change slot-filling tools. Reviewer is unchanged (no tools yet).
 */
export function getToolsForAgent(
  agent: string,
  opts: { planChange?: boolean } = {},
): AgentTool[] {
  const readOnly =
    agent === 'tutor' || agent === 'mentor' || agent === 'coach' ? getReadOnlyTools() : [];
  if (opts.planChange && (agent === 'tutor' || agent === 'mentor')) {
    return [...readOnly, ...getPlanChangeTools()];
  }
  return readOnly;
}
