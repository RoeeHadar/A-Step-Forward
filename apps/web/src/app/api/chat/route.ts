import { auth } from '@clerk/nextjs/server';
import { after } from 'next/server';
import { cookies } from 'next/headers';
import { agentNameSchema } from '@asf/schemas/agents';
import { logger } from '@/lib/logger';
import {
  fetchRecentChatTurns,
  recordChatTurn,
  getLearnerProfile,
  getConceptMastery,
  fetchLessonAgentHintsByConceptIds,
  fetchLessonByConceptId,
  getLearnerPersona,
  fetchAgentNotes,
  getDueReviews,
  markAtomPracticed,
  getCurrentPlan,
  computePlanPacing,
  saveWellbeingPlanBias,
  setWellbeingChatTrigger,
  evaluateWellbeingSignals,
  selectMoraleConcepts,
  wellbeingPlanBiasFromProfile,
  PLAN_CHANGE_SESSION_TTL_MS,
  type PlanChangeSession,
} from '@/lib/neon-db';
import { buildLearningPlan } from '@/lib/learning-plan';
import {
  buildLessonCatalogSummary,
  buildPlanAllowlistBlock,
  displayLearnerGoal,
  goalKeyLabel,
  PLAN_GROUNDING_RULES,
} from '@/lib/plan-catalog';
import {
  extractPlanUpdate,
  learnerPlanChangeIntentHeuristic,
  learnerAffirmedProposal,
  learnerCanceledPlanFlow,
  shouldApplyPlanChange,
  shouldApplyPlanImmediately,
  stripPlanMachineTags,
  planModificationProtocol,
} from '@/lib/plan-actions';
import {
  applyPlanFromUserMessage,
  buildPlanClarificationNotice,
  buildPlanApplyFailureNotice,
  buildPlanApplyingNotice,
  executePlanUpdate,
  maybeApplyConfirmedPlanSession,
  resolvePayloadForApply,
  saveProposalFromAssistantTurn,
  type PlanApplyResult,
} from '@/lib/plan-apply';
import {
  llmStream,
  llmComplete,
  llmConfigured,
  resolveChatModelChain,
  getLLMConfig,
  classifyFetchError,
  type LLMFailureInfo,
} from '@/lib/llm-provider';
import { buildChatFailureMessage } from '@/lib/learner-llm-errors';
import {
  CHAT_BREVITY_RULE,
  CHAT_CONTEXT,
  compactMemoryTurns,
  compactStoredTurnContent,
  fitSystemPrompt,
  buildPlanHeaderLine,
  formatPlanWeeksCompact,
  resolveChatMaxTokens,
  trimPersonaForChat,
  truncateChatText,
  truncationContinueNotice,
} from '@/lib/chat-context-policy';
import { buildContextNeeds } from '@/lib/chat-context-needs';
import {
  assembleChatSystemPrompt,
  buildHowToTeachBlock,
  filterNotesByRelevance,
  partitionInjectedContext,
} from '@/lib/chat-context-builder';
import {
  languageInstructionBlock,
  resolveResponseLanguage,
  type ChatResponseLocale,
} from '@/lib/chat-response-language';
import {
  qualityRepairInstruction,
  scoreResponseQuality,
} from '@/lib/chat-response-quality';
import {
  buildBilingualProgressBriefing,
  buildLearnerFacingStatusPack,
  formatLearnerFacingDate,
  AGENT_CORRECTION_TURN_INSTRUCTION,
  CONTEXT_CHALLENGE_TURN_INSTRUCTION,
  PLAN_OWNERSHIP_TURN_INSTRUCTION,
  PRESSURE_FAMILY_TURN_INSTRUCTION,
  RECOVERY_TURN_INSTRUCTION,
  WORKED_SOLUTION_TURN_INSTRUCTION,
} from '@/lib/learner-progress-briefing';
import { pickPressureNextStep } from '@/lib/pressure-next-step';
import {
  formatPracticeArenaChatBlock,
  parsePracticeChatContext,
  type PracticeChatContext,
} from '@/lib/practice-arena';
import { resolveTrustedPracticeChatContext } from '@/lib/practice-session';
import {
  appendTutorContractToContext,
  buildTutorInteractionContract,
  classifyTutorChatIntent,
  isPressureFamilyIntent,
  looksLikeLearnerQuestion,
  wantsAgentCorrection,
  wantsExpandedOutputBudget,
  wantsExamReadinessAnswer,
  wantsProgressStatus,
  wantsStudyHoursIncrease,
  type TutorIntentContext,
} from '@/lib/learner-chat-intent';
import { computeReadiness } from '@/lib/readiness';
import { dreamLearnerMemory } from '@/lib/agent-memory-dream';
import kg from '@/lib/kg-data.json';
import { resolveConceptsWithClassifier } from '@/lib/concept-resolver';
import { buildCompactAgentBaseline } from '@/lib/agent-baseline';
import { getAgentPersona } from '@/lib/agent-prompts';
import { resolveAgentSampling } from '@/lib/agent-sampling';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';
import { normalizePlanChangeMessage, isPlanChangeTemplate } from '@/lib/plan-change-template';
import { resolveWebChatAgent } from '@/lib/web-agents';
import { daysUntilExam, ANXIETY_THRESHOLD } from '@/lib/wellbeing-plan-bias';
import { resolveConceptTitles } from '@/lib/concept-display-names';
import { buildPlanLiveSnapshot } from '@/lib/plan-live-snapshot';
import { masterySignalInScope } from '@/lib/concept-scope';
import { formatDiagnosticSummaryForAgents } from '@/lib/diagnostic-service';
import type { DiagnosticSummary } from '@/lib/diagnostic-plan';
import {
  buildCoachDifficultyInstruction,
  buildCoachExamPrepBlock,
  buildCoachFsrsInstruction,
  coachDaysUntilExam,
  detectCoachDifficultySignal,
  filterDueReviewsForProfile,
  pickCoachPlannerGoal,
} from '@/lib/coach-session-context';
import {
  applyMemoryTagsFromAssistant,
  stripMemoryMachineTags,
} from '@/lib/chat-memory-persist';
import {
  groundingConceptId,
  groundingLessonId,
  logCiteAudit,
  logShadowCitations,
  parseCiteTags,
  stripAllMachineTags,
  stripCiteMachineTags,
} from '@/lib/chat-cite-tags';
import {
  buildHandoffDigest,
  wantsMemoryExpand,
  type LiveAgentId,
} from '@/lib/agent-handoff-digest';
import {
  buildCoachHybridToolPack,
  buildTutorSolverToolPack,
  type WeakAtomPathNode,
} from '@/lib/agent-hybrid-tools';
import {
  buildSolverRevealInstruction,
  countSolverHintCycles,
  learnerConfirmedReveal,
  softRepairNumericReply,
  trySolveAuthoritative,
  wantsFullSolutionNow,
} from '@/lib/agent-solver-verify';
import {
  buildMethodAuthorityBlock,
  buildMethodSourceInventory,
  isMathTeachingTurn,
  lacksMethodCitation,
  looksLikeSocraticStall,
  METHOD_GROUNDING_TURN_INSTRUCTION,
  softRepairSocraticStall,
} from '@/lib/agent-method-grounding';
import { isWithinExamPrepWindow } from '@/lib/exam-prep';
import {
  refusalFor,
  refusalStreamResponse,
  resolveChildMode,
  ruleClassify,
  type SafetyKind,
} from '@/lib/chat-safety';
import { buildWeekTrainingSpec } from '@/lib/week-training-spec';
import { buildActiveWeekBlock } from '@/lib/active-week-block';
import { retrieveChunks } from '@/lib/rag-retrieve';
import { toolCallingAvailable } from '@/lib/llm-provider';
import { getToolsForAgent } from '@/lib/agent-tools';
import { runReactLoop } from '@/lib/react-loop';

export const runtime = 'nodejs';
export const maxDuration = 60;

/**
 * RAG grounding toggle. ON by default; set CHAT_RAG=off (or 0) to disable the
 * authored-corpus retrieval injection without a redeploy.
 */
const RAG_ENABLED = process.env.CHAT_RAG !== 'off' && process.env.CHAT_RAG !== '0';
/** Max retrieved passages injected, and per-passage char budget. */
const RAG_TOP_K = 4;
const RAG_CHUNK_CHARS = 520;

/**
 * ReAct tool-calling loop toggle (ADR-0015, Phase A). ON by default; set
 * CHAT_REACT_AGENT=off (or 0) to disable and fall back to static RAG grounding.
 * Only ever runs when a tool-capable model is available (else it degrades).
 */
const REACT_ENABLED =
  process.env.CHAT_REACT_AGENT !== 'off' && process.env.CHAT_REACT_AGENT !== '0';
/**
 * Bounds for the tool loop. The route is capped at 60s; the loop's overall
 * budget (18s) + per-call ceiling (8s) leave ~40s for the answer generator.
 */
const REACT_MAX_TOOL_CALLS = 4;
const REACT_MAX_ITERATIONS = 2;
const REACT_BUDGET_MS = 18_000;
const REACT_PER_CALL_TIMEOUT_MS = 8_000;
const TOOL_PLANNER_INSTRUCTION = [
  'You are the tool-planning stage for a learner-facing tutoring assistant.',
  'Decide whether calling a tool would materially improve the answer to the',
  'learner’s latest message, and if so call the most relevant tool(s).',
  'Prefer `retrieve` for factual/explanatory questions IN math or physics,',
  '`get_lesson` to point to structured material by concept id,',
  '`get_current_plan` / `learning_plan_next` for “what is my status / what should I',
  'study next / why am I stuck”. If the learner asks about THEIR plan or status,',
  'do NOT call retrieve — the server already has their plan.',
  'If they ask where to practice / take a test / open lessons, do NOT call retrieve;',
  'the answer model already knows in-app routes.',
  'If the question is outside math/physics (history, literature, chemistry as a course,',
  'etc.), do NOT call retrieve hoping for a lesson — there is none. Skip tools.',
  'If no tool is needed (greetings, small talk, pure motivation), do NOT call any tool.',
  'Never write the final answer here.',
].join(' ');

/**
 * Planner instruction for the guided plan-change flow (Phase B). The model runs
 * a slot-filling loop but NEVER applies the change — the site applies it only
 * after the learner explicitly confirms the diff on a later turn.
 */
const PLAN_FLOW_PLANNER_INSTRUCTION = [
  'The learner wants to change their study plan/goal. Drive a guided flow with',
  'the plan tools. First call `get_current_plan`. Then call `propose_plan_change`',
  'with EVERY slot the learner has already given (goal, target_date, optional',
  'hours_per_week, notes). Obey its result:',
  '- "still_collecting": ask the learner ONLY the single question it returns, then stop.',
  '- "ready_to_confirm": show the learner the exact diff it returns and ask them',
  '  to confirm (yes/no). Do NOT say the plan was changed — it is applied only',
  '  after they confirm on the next turn.',
  'Use `validate_goal_scope` only if unsure a goal is specific enough. You may',
  'also use the read-only knowledge tools if genuinely helpful. Never write the',
  'final answer here and never claim the plan is already updated.',
  'Corpus constraint: A Step Forward only teaches math and physics — never offer',
  'history, literature, or any other subject as a plan goal.',
].join(' ');

/**
 * Learner-facing behavior instructions for the guided plan-change flow. Injected
 * into the ANSWER model's context (the tool loop produces the "still_collecting /
 * ready_to_confirm / escalate" observations this refers to). Replaces the
 * template-redirect protocol so the model handles the change conversationally.
 */
const PLAN_FLOW_AGENT_INSTRUCTIONS = [
  '## Guided plan-change (in progress)',
  'The learner is updating their study plan through a guided conversation. Follow the tool observations exactly:',
  '- "still_collecting": ask ONLY the single question it gives, in the learner’s language; do not ask anything else about the plan and do not batch questions.',
  '- "ready_to_confirm": present the current→proposed diff it gives and ask the learner to confirm (yes/no). Do NOT claim the plan changed yet — the site applies it only after they confirm.',
  '- "escalate": offer the Mentor handoff or to pause and resume later; do not repeat the same question.',
  'Never tell the learner to open a form or paste a structured update — you are handling this conversationally. Never say the plan was updated unless the system confirms it in this turn.',
  'Corpus constraint: this platform only teaches **math** and **physics**. When clarifying a goal (e.g. pre-academic / makhina), offer ONLY math vs physics (and catalog tracks like Calculus 1, Bagrut units, Mechanics/Electricity). Never invent subjects like history, literature, biology, or chemistry.',
  'Do NOT ask why they want to change the plan — collect goal + target date via the tools, then show the diff.',
].join('\n');

/** Steers the answer on a confirm turn so it acknowledges instead of re-asking. */
const PLAN_CONFIRM_TURN_INSTRUCTION: Record<'he' | 'en', string> = {
  he: '## עדכון תוכנית\nהלומד אישר זה עתה את שינוי התוכנית הממתין. אשר בקצרה שאתה מחיל את השינוי — אל תשאל שוב ואל תבקש פרטים נוספים. המערכת תוסיף הודעת אישור עם הפרטים.',
  en: '## Plan update\nThe learner just confirmed the pending plan change. Briefly acknowledge you are applying it — do NOT ask again or request more details. The system will append a confirmation notice with the details.',
};

// Keep upstream LLM timeout under Vercel maxDuration (60s on Pro).
const CHAT_LLM_TIMEOUT_MS = 45_000;

function applyPostStreamSolverHygiene(
  agent: string,
  userMessage: string,
  assistantVisible: string,
  locale: 'he' | 'en',
): { text: string; repairNotice: string | null } {
  const text = stripCiteMachineTags(assistantVisible);
  if (agent !== 'tutor' && agent !== 'coach') return { text, repairNotice: null };

  const solve = trySolveAuthoritative(userMessage);
  const correctionStall =
    wantsAgentCorrection(userMessage) && looksLikeSocraticStall(text);

  // Stall first: replace empty Socratic loops (learner-facing), then layer verify if any.
  if (correctionStall) {
    const stallFixed = softRepairSocraticStall(text, locale);
    let out = stallFixed.text;
    if (solve) {
      const repaired = softRepairNumericReply(out, solve, locale);
      if (repaired.repaired) out = repaired.text;
    }
    logger.info('chat: method-grounding stall soft repair', {
      agent,
      withVerify: Boolean(solve),
    });
    return { text: out, repairNotice: out };
  }

  if (solve) {
    const repaired = softRepairNumericReply(text, solve, locale);
    if (repaired.repaired) {
      logger.info('chat: solver soft repair', {
        agent,
        kind: solve.kind,
        expected: solve.expected,
        found: repaired.found,
      });
      const notice =
        repaired.text.startsWith(text.trimEnd())
          ? repaired.text.slice(text.trimEnd().length)
          : repaired.text;
      return { text: repaired.text, repairNotice: notice.trim() ? notice : null };
    }
  }

  if (isMathTeachingTurn(userMessage) && lacksMethodCitation(text)) {
    logger.info('chat: method-grounding uncited math (shadow)', {
      agent,
      chars: text.length,
    });
  }

  return { text, repairNotice: null };
}

interface ChatTurnGrounding {
  groundingIds: Set<string>;
}

async function saveAssistantTurn(
  userId: string,
  agent: string,
  content: string,
  sessionId: string | undefined,
  locale: 'he' | 'en',
  childMode: boolean,
  userMessageForVerify?: string,
  groundingIds: Iterable<string> = [],
): Promise<void> {
  const citations = parseCiteTags(content);
  logShadowCitations({
    agent,
    learnerId: userId,
    citations,
  });
  logCiteAudit({ agent, citations, groundingIds });
  const withoutMemory = stripMemoryMachineTags(content);
  const cleaned = userMessageForVerify
    ? applyPostStreamSolverHygiene(agent, userMessageForVerify, withoutMemory, locale).text
    : stripCiteMachineTags(withoutMemory);
  const postHit = ruleClassify(cleaned, { childMode });
  const toStore = postHit ? refusalFor(postHit, undefined, locale) : cleaned;
  if (!postHit) {
    try {
      await applyMemoryTagsFromAssistant(userId, agent, content, { childMode });
    } catch (err) {
      logger.warn('[ASF_MEMORY_WRITE_FAIL] applyMemoryTagsFromAssistant failed', {
        agent,
        err: String(err),
      });
    }
  }
  try {
    await recordChatTurn(
      userId,
      agent,
      'assistant',
      compactStoredTurnContent(toStore, 'assistant', locale),
      sessionId,
    );
  } catch (err) {
    logger.error('[ASF_MEMORY_WRITE_FAIL] recordChatTurn (assistant) failed', {
      agent,
      err: String(err),
    });
  }
  void maybeDreamLearnerNotes(userId, agent);
}

async function maybeDreamLearnerNotes(userId: string, agent: string): Promise<void> {
  try {
    const notes = await fetchAgentNotes(userId, agent, CHAT_CONTEXT.dreamNoteThreshold + 4);
    if (notes.length >= CHAT_CONTEXT.dreamNoteThreshold) {
      await dreamLearnerMemory(userId, { agents: [agent], scope: 'live' });
    }
  } catch (err) {
    logger.warn('chat: post-turn dream failed', { err: String(err) });
  }
}

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  prerequisites: string[];
}
const kgByName: Record<string, KgConcept> = Object.fromEntries(
  ((kg as { concepts: KgConcept[] }).concepts).map((c) => [c.id, c]),
);

export async function POST(req: Request) {
  let userId: string | null = null;
  let sessionClaims: Record<string, unknown> | null = null;
  try {
    const a = await auth();
    userId = a.userId;
    sessionClaims = (a.sessionClaims as Record<string, unknown> | null) ?? null;
  } catch (err) {
    logger.error('chat: auth() threw', { err: String(err) });
    return Response.json({ error: 'auth_failed' }, { status: 401 });
  }
  if (!userId) {
    return Response.json({ error: 'unauthorized' }, { status: 401 });
  }

  let body: {
    messages?: { role: string; content: string }[];
    agent?: string;
    quickMode?: boolean;
    quickDuration?: string;
    sessionId?: string;
    topic?: string;
    practiceContext?: unknown;
  };
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return Response.json({ error: 'bad_request' }, { status: 400 });
  }

  const rawLastMessage = body.messages?.filter((m) => m.role === 'user').at(-1)?.content ?? '';
  const lastMessage = normalizePlanChangeMessage(rawLastMessage);
  const parsedAgent = agentNameSchema.safeParse(body.agent);
  const agent = resolveWebChatAgent(parsedAgent.success ? parsedAgent.data : 'tutor');
  const quickMode = body.quickMode === true;
  const quickDuration = body.quickDuration ?? '15';
  const sessionId = body.sessionId?.trim() || undefined;
  const clientPractice = parsePracticeChatContext(body.practiceContext);
  const practiceContext = clientPractice
    ? await resolveTrustedPracticeChatContext(userId, clientPractice).catch(() => null)
    : null;
  const topic =
    body.topic?.trim() || practiceContext?.concept_id || undefined;
  const cookieStore = await cookies();
  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);

  const meta = (sessionClaims?.metadata ??
    sessionClaims?.publicMetadata ??
    {}) as { child_mode?: boolean; age?: number };
  // Neon grade_level fills COPPA gap when Clerk age/child_mode are unset.
  const profileForSafety = await getLearnerProfile(userId).catch(() => null);
  const childMode = resolveChildMode({
    age: typeof meta.age === 'number' ? meta.age : null,
    childModeFlag: Boolean(meta.child_mode),
    gradeLevel: profileForSafety?.grade_level ?? null,
  });

  const preHit = ruleClassify(lastMessage, { childMode });
  if (preHit) {
    logger.warn('chat: safety pre-filter', { kind: preHit as SafetyKind, agent });
    return refusalStreamResponse(refusalFor(preHit, undefined, locale));
  }

  // Record user turn before streaming so memory is durable for retries.
  try {
    await recordChatTurn(
      userId,
      agent,
      'user',
      compactStoredTurnContent(lastMessage, 'user', locale),
      sessionId,
    );
  } catch (err) {
    logger.warn('[ASF_MEMORY_WRITE_FAIL] recordChatTurn (user) failed', { err: String(err) });
  }

  // Notes are model-authored summaries; raw user turns live in chat_turns only.

  // Coach: when learner says drills are too easy, mark due atoms mastered so FSRS stops repeating basics.
  if (agent === 'coach' && lastMessage.trim().length > 10) {
    const difficultySignal = detectCoachDifficultySignal(lastMessage);
    if (difficultySignal === 'too_easy' || difficultySignal === 'harder') {
      after(async () => {
        try {
          const profile = await getLearnerProfile(userId);
          const plan = await getCurrentPlan(userId).catch(() => null);
          const planConceptIds = new Set(
            plan?.weeks.flatMap((w) => w.concepts.map((c) => c.concept_id)) ?? [],
          );
          const due = filterDueReviewsForProfile(await getDueReviews(userId), {
            subjects: profile?.subjects ?? [],
            planConceptIds: planConceptIds.size > 0 ? planConceptIds : undefined,
          });
          for (const item of due.slice(0, 2)) {
            await markAtomPracticed(userId, item.atom_id, 0.92);
          }
        } catch (err) {
          logger.warn('coach markAtomPracticed failed', { err: String(err) });
        }
      });
    }
  }

  const isPlanAgent = agent === 'tutor';
  const templateOnlyPlan = isPlanAgent && shouldApplyPlanImmediately(lastMessage);
  let eagerPlanPromise: Promise<PlanApplyResult | null> | null = null;
  let planEagerResolved = false;
  let streamDone = false;
  const turnGrounding: ChatTurnGrounding = { groundingIds: new Set() };
  let gen: ReturnType<typeof streamAgentResponse> | null = null;

  const getGen = () => {
    if (!gen) {
      gen = streamAgentResponse(userId, lastMessage, agent, {
        quickMode,
        quickDuration,
        topic,
        locale,
        sessionId,
        practiceContext,
        turnGrounding,
      });
    }
    return gen;
  };

  const encoder = new TextEncoder();
  let assistantBuffer = '';
  /** Incomplete [[ASF_CITE:…]] across SSE chunks. */
  let citeCarry = '';

  const encodeToken = (text: string) => encoder.encode(`0:${JSON.stringify(text)}\n`);
  const encodeData = (data: unknown) => encoder.encode(`2:${JSON.stringify([data])}\n`);
  const encodeFinish = () =>
    encoder.encode(`d:${JSON.stringify({ finishReason: 'stop', usage: { promptTokens: 0, completionTokens: 0 } })}\n`);

  const enqueueVisibleToken = (
    controller: ReadableStreamDefaultController<Uint8Array>,
    chunk: string,
  ) => {
    const merged = citeCarry + chunk;
    // Buffer any incomplete [[ASF_… prefix so no tag family leaks into the UI
    // mid-chunk.  The carry drains once the closing ]] arrives.
    const open = merged.lastIndexOf('[[ASF_');
    if (open >= 0 && merged.indexOf(']]', open) < 0) {
      const safe = stripAllMachineTags(merged.slice(0, open));
      citeCarry = merged.slice(open);
      if (safe) controller.enqueue(encodeToken(safe));
      return;
    }
    citeCarry = '';
    // Never trim streaming deltas — BPE models emit leading spaces / newline-only tokens.
    const safe = stripAllMachineTags(merged, { trim: false });
    if (safe) controller.enqueue(encodeToken(safe));
  };
  const finishTemplatePlanTurn = async (
    controller: ReadableStreamDefaultController<Uint8Array>,
    planResult: PlanApplyResult | null,
  ) => {
    if (planResult) appendPlanResult(controller, planResult);
    const visible = stripPlanMachineTags(assistantBuffer).trim();
    if (visible) {
      await saveAssistantTurn(
        userId,
        agent,
        visible,
        sessionId,
        locale,
        childMode,
        lastMessage,
        turnGrounding.groundingIds,
      );
      void maybeDreamLearnerNotes(userId, agent);
    }
    controller.enqueue(encodeFinish());
    controller.close();
    streamDone = true;
  };

  const appendPlanResult = (
    controller: ReadableStreamDefaultController<Uint8Array>,
    planResult: PlanApplyResult | null,
  ) => {
    if (planResult?.applied) {
      const notice = locale === 'en' ? planResult.noticeEn! : planResult.noticeHe!;
      assistantBuffer += notice;
      controller.enqueue(encodeToken(notice));
      controller.enqueue(
        encodeData({
          type: 'plan_updated',
          planId: planResult.planId,
          reason: planResult.reason,
        }),
      );
      return;
    }
    if (planResult?.failureNotice) {
      assistantBuffer += planResult.failureNotice;
      controller.enqueue(encodeToken(planResult.failureNotice));
      controller.enqueue(
        encodeData({
          type: 'plan_failed',
          error: planResult.error,
        }),
      );
    }
  };

  const readable = new ReadableStream({
    start(controller) {
      if (isPlanAgent && shouldApplyPlanImmediately(lastMessage)) {
        controller.enqueue(encodeData({ type: 'plan_applying' }));
        const applying = buildPlanApplyingNotice(locale);
        assistantBuffer += applying;
        controller.enqueue(encodeToken(applying));
        eagerPlanPromise = applyPlanFromUserMessage(userId, agent, lastMessage, locale);
      }
    },
    async pull(controller) {
      try {
        if (templateOnlyPlan && !planEagerResolved) {
          planEagerResolved = true;
          const planResult = eagerPlanPromise
            ? await eagerPlanPromise
            : await applyPlanFromUserMessage(userId, agent, lastMessage, locale);
          await finishTemplatePlanTurn(controller, planResult);
          return;
        }
        if (streamDone) return;

        const { value, done } = await getGen().next();
        if (done) {
          const planResult: PlanApplyResult | null = eagerPlanPromise
            ? await eagerPlanPromise
            : null;
          const planEagerAttempted = eagerPlanPromise != null;
          const planAlreadyApplied = planResult?.applied === true;

          if (planResult && planEagerAttempted) {
            appendPlanResult(controller, planResult);
          }

          // Plan applies / confirm gates must finish before we close the stream
          // (they append notices). Ordinary turns persist in `after()` so a slow
          // Neon write cannot leave the UI stuck on "thinking…" after the reply.
          const mustFinalizeInline =
            planEagerAttempted ||
            shouldApplyPlanChange(lastMessage) ||
            learnerAffirmedProposal(lastMessage);

          if (assistantBuffer) {
            if (mustFinalizeInline) {
              const finalizeResult = await finalizeAssistantTurn(
                userId,
                agent,
                lastMessage,
                assistantBuffer,
                sessionId,
                locale,
                childMode,
                (status) => {
                  if (status === 'applying') {
                    const applying = buildPlanApplyingNotice(locale);
                    assistantBuffer += applying;
                    controller.enqueue(encodeToken(applying));
                    controller.enqueue(encodeData({ type: 'plan_applying' }));
                  }
                },
                planAlreadyApplied,
                planEagerAttempted,
                turnGrounding.groundingIds,
              );
              if (!planEagerAttempted && finalizeResult) {
                appendPlanResult(controller, finalizeResult);
              }
            } else {
              const buf = assistantBuffer;
              const grounding = [...turnGrounding.groundingIds];
              after(() => {
                void finalizeAssistantTurn(
                  userId,
                  agent,
                  lastMessage,
                  buf,
                  sessionId,
                  locale,
                  childMode,
                  undefined,
                  planAlreadyApplied,
                  planEagerAttempted,
                  grounding,
                ).catch((err) =>
                  logger.warn('chat: deferred finalize failed', { err: String(err) }),
                );
              });
            }
            if (citeCarry) {
              const leftover = stripAllMachineTags(citeCarry);
              citeCarry = '';
              if (leftover) controller.enqueue(encodeToken(leftover));
            }
          }
          controller.enqueue(encodeFinish());
          controller.close();
          streamDone = true;
        } else {
          assistantBuffer += value;
          enqueueVisibleToken(controller, value);
        }
      } catch (err) {
        logger.error('chat stream pull failed', { err: String(err) });
        const classified = classifyFetchError(err, getLLMConfig().providerLabel);
        const failure: LLMFailureInfo =
          classified.kind !== 'unknown'
            ? classified
            : { kind: 'stream_interrupted', provider: getLLMConfig().providerLabel };
        const fallback = buildChatFailureMessage({
          agent,
          locale,
          failure,
          messagePreview: lastMessage,
        });
        assistantBuffer += fallback;
        controller.enqueue(encodeToken(fallback));
        const planResult: PlanApplyResult | null = eagerPlanPromise
          ? await eagerPlanPromise
          : null;
        const planEagerAttempted = eagerPlanPromise != null;
        const planAlreadyApplied = planResult?.applied === true;
        if (planResult && planEagerAttempted) {
          appendPlanResult(controller, planResult);
        }
        if (assistantBuffer) {
          const mustFinalizeInline =
            planEagerAttempted ||
            shouldApplyPlanChange(lastMessage) ||
            learnerAffirmedProposal(lastMessage);
          if (mustFinalizeInline) {
            const finalizeResult = await finalizeAssistantTurn(
              userId,
              agent,
              lastMessage,
              assistantBuffer,
              sessionId,
              locale,
              childMode,
              undefined,
              planAlreadyApplied,
              planEagerAttempted,
              turnGrounding.groundingIds,
            );
            if (!planEagerAttempted && finalizeResult) {
              appendPlanResult(controller, finalizeResult);
            }
          } else {
            const buf = assistantBuffer;
            const grounding = [...turnGrounding.groundingIds];
            after(() => {
              void finalizeAssistantTurn(
                userId,
                agent,
                lastMessage,
                buf,
                sessionId,
                locale,
                childMode,
                undefined,
                planAlreadyApplied,
                planEagerAttempted,
                grounding,
              ).catch((err) =>
                logger.warn('chat: deferred finalize (error path) failed', {
                  err: String(err),
                }),
              );
            });
          }
        }
        controller.enqueue(encodeFinish());
        controller.close();
        streamDone = true;
      }
    },
  });

  return new Response(readable, {
    status: 200,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'X-Vercel-AI-Data-Stream': 'v1',
      'Cache-Control': 'no-cache, no-transform',
    },
  });
}

async function finalizeAssistantTurn(
  userId: string,
  agent: string,
  userMessage: string,
  assistantRaw: string,
  sessionId: string | undefined,
  locale: 'he' | 'en',
  childMode: boolean,
  onStatus?: (status: 'applying') => void,
  planAlreadyApplied = false,
  planEagerAttempted = false,
  groundingIds: Iterable<string> = [],
): Promise<PlanApplyResult | null> {
  const visible = stripPlanMachineTags(assistantRaw);

  // Guided plan-change flow confirm gate (Phase B): apply the staged proposal
  // ONLY when an awaiting_confirm session exists AND the learner's latest
  // message is an unambiguous affirmative. Tutor + Mentor. The model can never
  // self-apply; a rejection clears the session inside the helper.
  if (agent === 'tutor' || agent === 'mentor') {
    const guided = await maybeApplyConfirmedPlanSession(
      userId,
      agent,
      userMessage,
      locale,
    ).catch((err) => {
      logger.warn('chat: guided plan confirm gate failed', { err: String(err) });
      return null;
    });
    if (guided) {
      if (guided.applied) onStatus?.('applying');
      const notice = guided.applied
        ? locale === 'en'
          ? guided.noticeEn ?? ''
          : guided.noticeHe ?? ''
        : guided.failureNotice ?? '';
      const full = notice ? `${visible}\n\n${notice}` : visible;
      await saveAssistantTurn(
        userId,
        agent,
        full,
        sessionId,
        locale,
        childMode,
        userMessage,
        groundingIds,
      );
      if (guided.applied) {
        logger.info('chat: plan updated (guided flow)', { agent, planId: guided.planId });
      } else {
        logger.warn('chat: guided plan apply failed', { agent, error: guided.error });
      }
      return guided;
    }
  }

  const isPlanAgent = agent === 'tutor';

  if (!isPlanAgent) {
    await saveAssistantTurn(
      userId,
      agent,
      visible,
      sessionId,
      locale,
      childMode,
      userMessage,
      groundingIds,
    );
    return null;
  }

  const applyNow =
    !planAlreadyApplied && !planEagerAttempted && shouldApplyPlanChange(userMessage);

  try {
    await saveProposalFromAssistantTurn(userId, agent, userMessage, assistantRaw);
  } catch (err) {
    logger.warn('chat: save pending plan proposal failed', { err: String(err) });
  }

  if (applyNow) {
    onStatus?.('applying');
    const payload = await resolvePayloadForApply(userId, userMessage);

    if (!payload) {
      logger.warn('chat: learner confirmed plan change but no resolvable payload', {
        agent,
        userMessage: userMessage.slice(0, 80),
      });
      const failureNotice = buildPlanApplyFailureNotice(locale, 'missing_payload');
      await saveAssistantTurn(
        userId,
        agent,
        `${visible}\n\n${failureNotice}`,
        sessionId,
        locale,
        childMode,
        userMessage,
        groundingIds,
      );
      return { applied: false, error: 'missing_payload', failureNotice };
    }

    try {
      const result = await executePlanUpdate(userId, payload, {
        agent,
        source: 'chat',
      });
      if (result.applied) {
        const notice =
          locale === 'en' ? result.noticeEn ?? '' : result.noticeHe ?? '';
        const full = notice ? `${visible}\n\n${notice}` : visible;
        await saveAssistantTurn(
          userId,
          agent,
          full,
          sessionId,
          locale,
          childMode,
          userMessage,
          groundingIds,
        );
        logger.info('chat: plan updated', {
          agent,
          reason: payload.reason,
          planId: result.planId,
          weeks: result.weekSummaries?.length,
        });
        return result;
      }

      logger.warn('chat: plan update failed', { error: result.error });
      const failureNotice =
        result.error === 'needs_exam_scope' || result.error === 'needs_physics_scope'
          ? buildPlanClarificationNotice(
              locale,
              result.clarificationReason ?? 'physics',
            )
          : buildPlanApplyFailureNotice(locale, result.error);
      const saved = planEagerAttempted
        ? visible
        : `${visible}\n\n${failureNotice}`;
      await saveAssistantTurn(
        userId,
        agent,
        saved,
        sessionId,
        locale,
        childMode,
        userMessage,
        groundingIds,
      );
      return { ...result, failureNotice };
    } catch (err) {
      logger.warn('chat: plan update threw', { err: String(err) });
      const failureNotice = buildPlanApplyFailureNotice(locale, String(err));
      await saveAssistantTurn(
        userId,
        agent,
        `${visible}\n\n${failureNotice}`,
        sessionId,
        locale,
        childMode,
        userMessage,
        groundingIds,
      );
      return { applied: false, error: String(err), failureNotice };
    }
  }

  const { payload: prematureUpdate } = extractPlanUpdate(assistantRaw);
  if (prematureUpdate?.confirmed) {
    logger.warn('chat: ASF_PLAN_UPDATE ignored — learner did not confirm in this turn');
  }

  await saveAssistantTurn(
    userId,
    agent,
    visible,
    sessionId,
    locale,
    childMode,
    userMessage,
    groundingIds,
  );
  return null;
}

async function* streamAgentResponse(
  userId: string,
  message: string,
  agent: string,
  opts: {
    quickMode?: boolean;
    quickDuration?: string;
    topic?: string;
    locale?: 'he' | 'en';
    sessionId?: string;
    practiceContext?: PracticeChatContext | null;
    turnGrounding?: ChatTurnGrounding;
  } = {},
): AsyncGenerator<string> {
  const locale = opts.locale ?? 'he';
  let emitted = false;
  let failure: LLMFailureInfo | undefined;
  try {
    const gen = streamFromLLM(userId, message, agent, opts);
    let result = await gen.next();
    while (!result.done) {
      emitted = true;
      yield result.value;
      result = await gen.next();
    }
    failure = result.value;
  } catch (err) {
    failure = classifyFetchError(err, getLLMConfig().providerLabel);
    logger.warn('llm stream raised', { err: String(err) });
  }
  if (emitted && failure?.model === 'length_cap') {
    yield truncationContinueNotice(locale);
    return;
  }
  if (!emitted) {
    logger.warn('chat: all LLM attempts failed — learner fallback', {
      agent,
      userId,
      kind: failure?.kind ?? 'unknown',
      preview: message.slice(0, 80),
    });
    yield buildChatFailureMessage({
      agent,
      locale,
      failure: failure ?? { kind: 'unknown', provider: getLLMConfig().providerLabel },
      messagePreview: message,
    });
  }
}

function pickPlannerGoalConcept(
  related: KgConcept[],
  topic: string | undefined,
  currentPlan: Awaited<ReturnType<typeof getCurrentPlan>>,
  weakConcepts: string[],
): string | null {
  if (related[0]?.id) return related[0].id;
  if (topic && kgByName[topic]) return topic;
  const activeWeek =
    currentPlan?.weeks.find((w) => w.status === 'active') ?? currentPlan?.weeks[0];
  if (activeWeek?.concepts[0]?.concept_id) return activeWeek.concepts[0].concept_id;
  if (weakConcepts[0]) return weakConcepts[0];
  return null;
}

function formatConceptLine(conceptId: string): string {
  const titles = resolveConceptTitles(conceptId);
  const kgInfo = kgByName[conceptId];
  const label = titles.title_he || titles.title_en || kgInfo?.name || conceptId;
  return `[${conceptId}] ${label}`;
}

async function buildContextPrompt(
  userId: string,
  agent: string,
  message: string,
  opts: {
    quickMode?: boolean;
    quickDuration?: string;
    topic?: string;
    sessionId?: string;
    minimal?: boolean;
    practiceContext?: PracticeChatContext | null;
  } = {},
): Promise<{
  system: string;
  memory: Array<{ role: 'user' | 'assistant'; content: string }>;
  groundingIds: Set<string>;
  responseLocale: ChatResponseLocale;
  planChangeFlow: boolean;
}> {
  const {
    quickMode = false,
    quickDuration = '15',
    topic,
    sessionId,
    minimal = false,
    practiceContext = null,
  } = opts;
  const groundingIds = new Set<string>();
  const addConceptGrounding = (id: string | null | undefined) => {
    if (id) groundingIds.add(groundingConceptId(id));
  };
  const addLessonGrounding = (id: string | null | undefined) => {
    if (id) groundingIds.add(groundingLessonId(id));
  };
  // Each helper catches its own errors so a single DB issue cannot break chat.
  const [profileFetch, mastery, recent, persona, agentNotes, cookieStore] = await Promise.all([
    getLearnerProfile(userId)
      .then((profile) => ({ profile, dbUnavailable: false as const }))
      .catch(() => ({ profile: null, dbUnavailable: true as const })),
    getConceptMastery(userId).catch(() => ({})),
    fetchRecentChatTurns(
      userId,
      agent,
      CHAT_CONTEXT.maxMemoryTurns,
      sessionId,
    ).catch(() => []),
    minimal ? Promise.resolve(null) : getLearnerPersona(userId).catch(() => null),
    minimal ? Promise.resolve([]) : fetchAgentNotes(userId, agent, CHAT_CONTEXT.maxAgentNotes).catch(() => []),
    cookies(),
  ]);
  const profile = profileFetch.profile;
  const profileDbUnavailable = profileFetch.dbUnavailable;

  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);

  // The route records the user turn BEFORE calling buildContextPrompt.
  // On reload/retry the same content may appear multiple times — drop all
  // trailing consecutive duplicates of the just-recorded user message.
  const justRecordedContent = compactStoredTurnContent(message, 'user', locale);
  let recentForLLM = recent;
  while (
    recentForLLM.length > 0 &&
    recentForLLM[recentForLLM.length - 1]?.role === 'user' &&
    recentForLLM[recentForLLM.length - 1]?.content === justRecordedContent
  ) {
    recentForLLM = recentForLLM.slice(0, -1);
  }

  const recentForIntent = recent.map((t) => ({ role: t.role, content: t.content }));
  const recentUserMsgs = recent
    .filter((t) => t.role === 'user')
    .map((t) => t.content)
    .slice(-4);

  let tutorContract: ReturnType<typeof buildTutorInteractionContract> | null = null;
  let tutorIntent: ReturnType<typeof classifyTutorChatIntent> | null = null;
  const liveAgents = agent === 'tutor' || agent === 'mentor' || agent === 'coach' || agent === 'reviewer';

  const responseLocale: ChatResponseLocale = resolveResponseLanguage({
    message,
    recentUserMessages: recentUserMsgs,
    profileLang:
      (profile?.personality_profile as { ui_lang?: string; preferred_lang?: string } | null)
        ?.ui_lang ??
      (profile?.personality_profile as { preferred_lang?: string } | null)?.preferred_lang ??
      null,
    uiLocale: locale,
  });

  let contextNeeds = buildContextNeeds({
    agent,
    message,
    minimal,
    hasTopic: Boolean(topic),
    hasPractice: Boolean(practiceContext),
  });
  if (liveAgents && !minimal) {
    const tutorMode =
      (profile?.personality_profile as { tutor_mode?: string } | null)?.tutor_mode ?? null;
    const wellbeingProfileInput = profile
      ? {
          subjects: profile.subjects,
          mental_state: profile.mental_state,
          next_test_date: profile.next_test_date,
          personality_profile: profile.personality_profile,
          points_group: profile.points_group,
          wellbeing_plan_bias: profile.wellbeing_plan_bias,
        }
      : null;
    const intentCtx: TutorIntentContext = {
      recentTurns: recentForIntent,
      tutorModePreference: tutorMode === 'direct' ? 'direct' : 'socratic',
      subjects: profile?.subjects,
      goalKey:
        (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ?? null,
      hoursPerWeek: profile?.hours_per_week ?? null,
      daysUntilExam: wellbeingProfileInput
        ? daysUntilExam(wellbeingProfileInput, new Date())
        : null,
    };
    tutorIntent = classifyTutorChatIntent(message, intentCtx);
    contextNeeds = buildContextNeeds({
      agent,
      message,
      intentCtx,
      minimal,
      hasTopic: Boolean(topic),
      hasPractice: Boolean(practiceContext),
    });
    // Prefer classifier intent when needs were built without full ctx earlier.
    if (contextNeeds.intent !== tutorIntent) {
      contextNeeds = { ...contextNeeds, intent: tutorIntent };
    }
    if (agent === 'tutor') {
      tutorContract = buildTutorInteractionContract(tutorIntent, responseLocale, intentCtx);
    }

    if (tutorIntent === 'exam_anxiety') {
      void setWellbeingChatTrigger(userId, 'exam_anxiety').catch((err) =>
        logger.warn('chat: wellbeing chat trigger persist failed', { err: String(err) }),
      );
    }
  }

  // ── Guided plan-change flow flags (Phase B) ───────────────────────────────
  // Computed early because the tutor preference override, the plan-instruction
  // injection, and the ReAct tool loop all depend on them. `planChangeTurn` is
  // the legacy template/imperative path; `planChangeFlow` is the new
  // conversational flow.
  const planChangeTurn =
    isPlanChangeTemplate(normalizePlanChangeMessage(message)) ||
    shouldApplyPlanImmediately(message);
  const planSessionRaw = (
    profile?.personality_profile as { plan_change_session?: PlanChangeSession } | null
  )?.plan_change_session;
  // Session only drives THIS agent's turns (a tutor session must not hijack a
  // mentor turn) and must be unexpired.
  const planSessionActive = Boolean(
    planSessionRaw &&
      planSessionRaw.agent === agent &&
      Number.isFinite(Date.parse(planSessionRaw.updated_at ?? '')) &&
      Date.now() - Date.parse(planSessionRaw.updated_at ?? '') < PLAN_CHANGE_SESSION_TTL_MS,
  );
  const planFlowAffirmative = learnerAffirmedProposal(message);
  const planFlowCancel = learnerCanceledPlanFlow(message);
  // While a guided session is open, the learner's reply is almost always part of
  // the flow — a goal answer (which can be long), a date, an edit, or yes/no. So
  // engage on ANY reply EXCEPT an unrelated question (has "?" or an interrogative
  // lead), which falls through to static RAG / the normal tools. This both keeps
  // long goal answers in the flow AND stops an open session from hijacking a
  // spontaneous factual question.
  const planStatusAsk = wantsProgressStatus(message) || wantsExamReadinessAnswer(message);
  const trimmedMsg = message.trim();
  const looksLikeQuestion = looksLikeLearnerQuestion(trimmedMsg);
  const planSessionEngaged =
    planSessionActive &&
    !planStatusAsk &&
    (planFlowAffirmative || planFlowCancel || !looksLikeQuestion);
  const planChangeFlow =
    REACT_ENABLED &&
    (agent === 'tutor' || agent === 'mentor') &&
    !planChangeTurn &&
    !planStatusAsk &&
    (learnerPlanChangeIntentHeuristic(message) ||
      wantsStudyHoursIncrease(message) ||
      planSessionEngaged);
  // On a confirm turn the server applies the staged proposal in finalize; we
  // skip the tool loop and steer the answer to acknowledge (below).
  const planConfirmTurn =
    planSessionActive &&
    planSessionRaw?.status === 'awaiting_confirm' &&
    planFlowAffirmative;

  let context = `${buildCompactAgentBaseline()}\n\n${getAgentPersona(agent)}`;

  // Skip Tutor THIS-TURN overrides when ReAct is off: casual plan-change
  // would promise a confirmable flow we cannot stage. Other teaching-mode
  // overrides (direct/Socratic) are also skipped in that kill-switch window.
  if (
    agent === 'tutor' &&
    tutorContract?.learnerPreferenceOverride &&
    !planChangeFlow &&
    REACT_ENABLED
  ) {
    context = `${tutorContract.learnerPreferenceOverride}\n\n${context}`;
  } else if (agent === 'tutor') {
    const tutorMode =
      (profile?.personality_profile as { tutor_mode?: string } | null)?.tutor_mode ?? null;
    const learnerPref =
      tutorMode === 'direct'
        ? 'LEARNER PREFERENCE: This learner prefers direct explanations. Explain concepts clearly and fully before asking follow-up questions. Do not withhold the answer — explain first, then check understanding.'
        : 'LEARNER PREFERENCE: This learner prefers Socratic guidance. Guide with questions; do not give away the answer directly.';
    context = `${learnerPref}\n\n${context}`;
  }

  context += `\n\n${languageInstructionBlock(responseLocale)}`;
  context += `\n- Trust hierarchy: current learner message > verified profile/plan/mastery > recent turns > inferred persona/notes. Do not let stale notes redirect the topic.`;

  if (!minimal && liveAgents) {
    const tutorModeHow =
      (profile?.personality_profile as { tutor_mode?: string } | null)?.tutor_mode ?? null;
    context += `\n\n${buildHowToTeachBlock({
      tutorMode: tutorModeHow,
      preferredStyle: profile?.preferred_style ?? null,
      attentionSpanMin: profile?.attention_span ?? null,
    })}`;
  }

  if (profileDbUnavailable) {
    context += `\n\n## Learner context temporarily unavailable`;
    context += `\nThe learner profile could not be loaded due to a temporary database issue. Do NOT treat them as brand-new or send them to onboarding. Continue helping with their question using the conversation and any other context below.`;
  } else if (!profile) {
    // Onboarded learners always have a profile row. A missing row means
    // either a brand-new user or a probe before onboarding. Tell the
    // agent explicitly so it doesn't pretend it knows their context.
    context += `\n\n## Brand-new learner`;
    context += `\nNo learner profile is on file yet. Open with a one-sentence orientation in Hebrew (or match the language the learner just used), and invite them to complete the 4-step onboarding at \`/onboarding\` so the rest of the agent network can plan a personalised path. Do NOT improvise a curriculum or recommend specific lessons until a profile exists.`;
  }

  // CLAUDE.md-style learner persona — shared across every agent, written by
  // the Memory Steward (and any agent allowed to). Tells you HOW this
  // learner thinks/talks/learns, NOT what they know (that's mastery).
  if (!minimal && contextNeeds.durableMemory && persona?.text && persona.text.trim().length > 0) {
    context += `\n\n## What I know about this learner (shared persona)`;
    context += `\n${trimPersonaForChat(persona.text)}`;
    context += `\n- Persona hygiene: paraphrase into learner language. Hints only — current message wins on conflicts.`;
  }

  let xpSnapForBriefing: {
    total_xp: number;
    level: number;
  } | null = null;
  if (!minimal && contextNeeds.xp) {
    try {
      const { ensureXpSnapshot, formatXpContextBlock } = await import('@/lib/learner-xp');
      const xpSnap = await ensureXpSnapshot(userId);
      xpSnapForBriefing = { total_xp: xpSnap.total_xp, level: xpSnap.level };
      const xpLocale = responseLocale === 'en' ? 'en' : 'he';
      context += `\n\n${formatXpContextBlock(xpSnap, xpLocale)}`;
    } catch {
      // XP is optional context
    }
  }

  if (!minimal && contextNeeds.durableMemory && agentNotes.length > 0) {
    const relevantNotes = filterNotesByRelevance(agentNotes, message);
    if (relevantNotes.length > 0) {
      context += `\n\n## My private notes on this learner (agent: ${agent})`;
      context += `\n(These are hints — do not let them override the current question.)`;
      for (const n of relevantNotes) {
        const tag = n.related_concept_id ? ` [${n.related_concept_id}]` : '';
        context += `\n- (${n.kind})${tag} ${truncateChatText(n.content, CHAT_CONTEXT.maxAgentNoteChars)}`;
      }
    }
  }
  if (profile && contextNeeds.profile) {
    context += `\n\n## Learner profile (internal facts — paraphrase; never dump field-by-field)`;
    context += `\n- Goal: ${profile.goal}`;
    if (profile.grade_level) context += `\n- Grade level: ${profile.grade_level}`;
    if (profile.points_group) context += `\n- Math units: ${profile.points_group}`;
    if (profile.subjects?.length) context += `\n- Subjects: ${profile.subjects.join(', ')}`;
    if (profile.preferred_style) context += `\n- Preferred style: ${profile.preferred_style}`;
    const personality = profile.personality_profile as Record<string, unknown> | null;
    if (personality?.learning_style_unknown === true && agent === 'tutor') {
      context += `\n- Preferred learning style: learner is unsure — observe how they respond in early sessions and adapt (theory vs practice vs mixed) from their feedback.`;
    }
    if (profile.hours_per_week) context += `\n- Available study time: ${profile.hours_per_week} hours/week`;
    if (profile.next_test_name && profile.next_test_date) {
      context += `\n- Next big event: ${profile.next_test_name} on ${profile.next_test_date}`;
    }
    if (profile.final_goal_date) {
      context += `\n- Final goal date: ${profile.final_goal_date}`;
    }
    const mental = profile.mental_state as Record<string, unknown> | null;
    if (mental && Object.keys(mental).length > 0) {
      const anxiety = typeof mental.anxiety === 'number' ? mental.anxiety : null;
      const motivation = typeof mental.motivation === 'number' ? mental.motivation : null;
      const preferredTime =
        typeof mental.preferred_study_time === 'string' ? mental.preferred_study_time : null;
      const targetUniversity =
        typeof mental.target_university === 'string' ? mental.target_university : null;
      if (anxiety != null) context += `\n- Test anxiety: ${anxiety}/10`;
      if (motivation != null) context += `\n- Motivation: ${motivation}/10`;
      if (preferredTime) {
        context += `\n- Preferred study window: ${preferredTime}`;
        if (agent === 'tutor') {
          context += `\n- Pacing hint: suggest a brief review or overview during their ${preferredTime} window when appropriate; schedule heavier drills or new material for later in the day if they seem tired.`;
        }
      }
      if (targetUniversity) context += `\n- Target university/program: ${targetUniversity}`;
      if (anxiety != null && anxiety >= 7) {
        context += `\n- IMPORTANT: This learner has high test anxiety. Be extra reassuring; avoid time pressure cues; celebrate small wins.`;
      }
    }
    if (personality && agent === 'tutor') {
      const subjectExperience = personality.subject_experience;
      const subjectExperienceEntries =
        subjectExperience && typeof subjectExperience === 'object'
          ? Object.entries(subjectExperience as Record<string, unknown>).filter(
              ([, raw]) => raw && typeof raw === 'object',
            )
          : [];
      if (subjectExperienceEntries.length > 0) {
        for (const [sub, raw] of subjectExperienceEntries) {
          const exp = raw as Record<string, unknown>;
          const mode = typeof exp.mode === 'string' ? exp.mode : 'share';
          const label = sub === 'physics' ? 'Physics' : 'Math';
          if (mode === 'prefer_skip') {
            context += `\n- ${label} background: learner prefers not to discuss prior experience.`;
            continue;
          }
          if (mode === 'no_prior') {
            context += `\n- ${label} background: no prior formal experience — start from foundations.`;
            continue;
          }
          const rating = typeof exp.selfRating === 'number' ? exp.selfRating : null;
          const teacher =
            typeof exp.teacherOverall === 'string' ? exp.teacherOverall : null;
          if (rating != null) {
            context += `\n- ${label} past learning experience (self-rated): ${rating}/10`;
          }
          if (teacher && teacher !== 'unknown') {
            context += `\n- ${label} teachers (learner view): ${teacher.replace(/_/g, ' ')}`;
          }
          const notes =
            typeof exp.teacherNotes === 'string' ? exp.teacherNotes.trim() : '';
          if (notes) {
            context += `\n- ${label} teacher notes: ${notes}`;
          }
        }
      } else {
        const teacherExp = personality.past_teacher_experience;
        const teacherNotes = personality.past_teacher_notes;
        if (typeof teacherExp === 'string' && teacherExp !== 'unknown') {
          context += `\n- Past teacher experience (learner view): ${teacherExp.replace(/_/g, ' ')}`;
        }
        if (typeof teacherNotes === 'string' && teacherNotes.trim()) {
          context += `\n- What worked / did not work with past teachers: ${teacherNotes.trim()}`;
        }
      }
      if (personality.attention_span_unknown === true) {
        context += `\n- Focus duration: learner is unsure — start with short blocks (~20 min) and adjust from session feedback.`;
      }
    }
  }

  const currentPlan =
    profile ? await getCurrentPlan(userId).catch(() => null) : null;

  // Identify active week for the training-spec fetch (≤2 Neon queries).
  const activeWeekForSpec =
    currentPlan?.weeks.find((w) => w.status === 'active') ?? currentPlan?.weeks[0];

  // Fetch the week training spec for all four live agents when an active week exists.
  // Runs ≤2 queries (getWeekAtomMastery + getGatePassed) in parallel internally.
  const weekSpec =
    !minimal && liveAgents && activeWeekForSpec && currentPlan
      ? await buildWeekTrainingSpec(userId, activeWeekForSpec, currentPlan.id).catch(() => null)
      : null;

  const planConceptIds = new Set(
    currentPlan?.weeks.flatMap((w) => w.concepts.map((c) => c.concept_id)) ?? [],
  );
  const profileSubjects = profile?.subjects ?? [];
  const masteryInScope = (conceptId: string) =>
    masterySignalInScope(conceptId, { subjects: profileSubjects, planConceptIds });

  const weakConcepts = Object.entries(mastery)
    .filter(([id, score]) => score < 0.4 && masteryInScope(id))
    .sort((a, b) => a[1] - b[1])
    .slice(0, CHAT_CONTEXT.maxWeakStrongConcepts)
    .map(([id]) => id);
  const strongConcepts = Object.entries(mastery)
    .filter(([id, score]) => score > 0.7 && masteryInScope(id))
    .sort((a, b) => b[1] - a[1])
    .slice(0, CHAT_CONTEXT.maxWeakStrongConcepts)
    .map(([id]) => id);
  if (contextNeeds.mastery && (weakConcepts.length || strongConcepts.length)) {
    context += `\n\n## Mastery so far`;
    if (weakConcepts.length) context += `\n- Weak areas: ${weakConcepts.join(', ')}`;
    if (strongConcepts.length) context += `\n- Strong areas: ${strongConcepts.join(', ')}`;
  }

  // A1: Universal "Active week" block — injected for all four live agents when a plan exists.
  // Placed in the middle layer (trimmable under pressure) but early enough to survive typical trims.
  if (!minimal && liveAgents && weekSpec && activeWeekForSpec && contextNeeds.activeWeek) {
    const activeWeekBlock = buildActiveWeekBlock({
      weekNumber: activeWeekForSpec.week_number,
      concepts: activeWeekForSpec.concepts,
      spec: weekSpec,
      planHealth: {
        needs_replan: currentPlan?.needs_replan ?? false,
        overflow_count: currentPlan?.overflow_concepts?.length ?? 0,
      },
    });
    context += `\n\n${activeWeekBlock}`;
  }

  const diagnosticSummary = (
    profile?.mental_state as { diagnostic_summary?: { agent_brief_en?: string; agent_brief_he?: string } } | null
  )?.diagnostic_summary;
  if (profile && diagnosticSummary?.agent_brief_en && (contextNeeds.planCatalog || contextNeeds.statusPack || contextNeeds.bilingualBriefing)) {
    const lang = responseLocale;
    context += `\n\n${formatDiagnosticSummaryForAgents(diagnosticSummary as DiagnosticSummary, lang)}`;
  }

  if (profile && (agent === 'mentor' || agent === 'tutor')) {
    const plan = currentPlan;
    const normalizedMsg = normalizePlanChangeMessage(message);
    const needsPlanCatalog =
      contextNeeds.planCatalog ||
      tutorContract?.injectPlanCatalog ||
      planChangeFlow ||
      isPlanChangeTemplate(normalizedMsg) ||
      shouldApplyPlanImmediately(message);

    if (plan?.weeks?.length) {
      if (weekSpec) {
        // Active week block already injected above — append a compact one-liner
        // to avoid duplicating ~900 chars of plan detail for tutor/mentor.
        context += `\n\n${buildPlanHeaderLine(plan)}`;
      } else {
        context += `\n\n## Current weekly learning plan`;
        context += `\nGoal: ${plan.goal} · ${plan.start_date} → ${plan.end_date ?? 'open'}`;
        context += `\n${formatPlanWeeksCompact(plan.weeks, minimal ? 'minimal' : 'full')}`;
      }
    } else if (!minimal) {
      context += `\n\n## Current weekly learning plan`;
      context += `\nNo active plan yet — invite onboarding at /onboarding if the learner asks.`;
    }

    if (needsPlanCatalog && !minimal) {
      context += `\n\n## Platform catalog (in-house only)`;
      context += `\n${buildLessonCatalogSummary(profile.subjects ?? [])}`;
      context += `\n\n## Plan mutation allowlist`;
      context += `\n${buildPlanAllowlistBlock(profile.subjects ?? [])}`;
      context += `\n\n${PLAN_GROUNDING_RULES}`;
      // During the guided conversational flow, use the guided instructions
      // instead of the template-redirect protocol (which would contradict it by
      // telling the model to send the learner to the sidebar template).
      context += `\n\n${planChangeFlow ? PLAN_FLOW_AGENT_INSTRUCTIONS : planModificationProtocol(REACT_ENABLED)}`;
    } else if (!minimal && agent === 'tutor' && tutorContract) {
      context = appendTutorContractToContext(context, tutorContract);
    } else if (!minimal && agent === 'mentor') {
      context += `\n\n## Plan guidance`;
      context += `\nAnswer timeline/readiness from the plan above. If they want to change the plan, handle it in this chat (propose → confirm). Never send them to a form.`;
    }
  }

  if (topic && !practiceContext) {
    context += `\n\n## Active study context`;
    context += `\nThe learner is currently studying concept \`${topic}\` on the lesson page. Ground your answer in this topic when relevant.`;
    addConceptGrounding(topic);
    const topicConcept = kgByName[topic];
    if (topicConcept) {
      context += `\n- ${topicConcept.name} (${topicConcept.id})`;
      if (topicConcept.prerequisites?.length) {
        context += ` — prerequisites: ${topicConcept.prerequisites.join(', ')}`;
      }
    }
  } else if (topic && practiceContext) {
    addConceptGrounding(topic);
    const topicConcept = kgByName[topic];
    if (topicConcept) {
      context += `\n\n## Practice concept grounding`;
      context += `\n- ${topicConcept.name} (${topicConcept.id})`;
      if (topicConcept.prerequisites?.length) {
        context += ` — prerequisites: ${topicConcept.prerequisites.join(', ')}`;
      }
    }
  }

  if (practiceContext) {
    context += `\n\n${formatPracticeArenaChatBlock(practiceContext)}`;
  }

  const searchMessage = topic && !message.trim() ? topic.replace(/_/g, ' ') : message;
  const resolved =
    minimal || !contextNeeds.curriculumHints
      ? { concepts: [] as Awaited<ReturnType<typeof resolveConceptsWithClassifier>>['concepts'], tier: 'none' as const }
      : await resolveConceptsWithClassifier(searchMessage, profile?.subjects ?? []);
  // ADR-0015: attach curriculum only when needs say so and resolver found something.
  // Classifier miss (tier none / empty) → ordinary general-knowledge answer, no fabricated ASF map.
  const related = resolved.concepts;
  if (resolved.tier !== 'none' || related.length > 0) {
    logger.info('chat: concept resolver', {
      tier: resolved.tier,
      attached: related.length,
    });
  }
  for (const c of related) {
    addConceptGrounding(c.id);
  }
  if (related.length) {
    context += `\n\n## Relevant curriculum context`;
    for (const c of related) {
      context += `\n- ${c.name} (${c.id})`;
      if (c.prerequisites?.length) context += ` — prerequisites: ${c.prerequisites.join(', ')}`;
    }

    // Inject agent_hints from the matching AI-authored lessons so the Tutor
    // can ground its reply in the canonical key insights, pacing hints, and
    // common-misconception triggers we authored per concept.
    if ((agent === 'tutor' || agent === 'coach') && contextNeeds.curriculumHints) {
      const hintsRows = await fetchLessonAgentHintsByConceptIds(related.map((c) => c.id)).catch(
        () => [] as Awaited<ReturnType<typeof fetchLessonAgentHintsByConceptIds>>,
      );
      if (hintsRows.length) {
        context += `\n\n## Lesson-level guidance for the AI-authored corpus`;
        const lowerMsg = message.toLowerCase();
        for (const row of hintsRows.slice(0, 2)) {
          addConceptGrounding(row.concept_id);
          const h = row.agent_hints ?? {};
          context += `\n\n### ${row.concept_id}`;
          if (h.key_insights?.length) {
            for (const k of h.key_insights.slice(0, CHAT_CONTEXT.maxHintInsights)) {
              context += `\n- ${k}`;
            }
          }
          if (h.common_misconceptions?.length) {
            const triggered = h.common_misconceptions.filter((m) => {
              const en = m.detect_phrase_en?.toLowerCase();
              const he = m.detect_phrase_he;
              return (
                (en && lowerMsg.includes(en)) ||
                (he && message.includes(he))
              );
            });
            if (triggered.length > 0) {
              context += `\n- Misconception:`;
              for (const m of triggered.slice(0, 1)) {
                context += ` "${m.wrong}" → ${m.correction}`;
              }
            }
          }
        }
      }
    }
  }

  // RAG grounding (ADR-0015 hybrid knowledge): retrieve authored passages from
  // the bilingual corpus so Tutor/Coach answers are grounded in — and can cite —
  // our own content. Trimmable pack; degrades to lexical-only or nothing on
  // failure. Flag-gated (CHAT_RAG) and skipped for plan-change/minimal turns.
  // (planChangeTurn / planChangeFlow / planConfirmTurn were computed above with
  // the plan-instruction block so both surfaces stay in lock-step.)

  // ReAct tool loop (Phase A): the model plans read-only tool calls (retrieve,
  // get_lesson, learning_plan_next); we execute them and inject the observations.
  // Phase B additionally exposes the plan-change tool family when planChangeFlow
  // is active. Supersedes the static RAG block when it runs. Degrades to static
  // RAG when the flag is off, no tool-capable model is available, or it fails.
  let reactHandledGrounding = false;
  const reactTools = getToolsForAgent(agent, { planChange: planChangeFlow });
  const reactCandidateTurn =
    REACT_ENABLED &&
    !minimal &&
    !planChangeTurn &&
    !planConfirmTurn &&
    !planStatusAsk &&
    !(tutorIntent && isPressureFamilyIntent(tutorIntent)) &&
    (searchMessage.trim().length >= 10 || planChangeFlow) &&
    reactTools.length > 0 &&
    toolCallingAvailable();
  if (reactCandidateTurn) {
    try {
      const loop = await runReactLoop({
        system: `${buildCompactAgentBaseline()}\n\n${
          planChangeFlow ? PLAN_FLOW_PLANNER_INSTRUCTION : TOOL_PLANNER_INSTRUCTION
        }`,
        memory: recentForIntent.slice(-2).map((t) => ({
          role: t.role === 'assistant' ? ('assistant' as const) : ('user' as const),
          content: t.content,
        })),
        userMessage: searchMessage,
        tools: reactTools,
        ctx: { userId, agent, locale: responseLocale === 'en' ? 'en' : 'he' },
        maxToolCalls: REACT_MAX_TOOL_CALLS,
        maxIterations: REACT_MAX_ITERATIONS,
        budgetMs: REACT_BUDGET_MS,
        perCallTimeoutMs: REACT_PER_CALL_TIMEOUT_MS,
      });
      if (!loop.degraded) {
        for (const id of loop.groundingIds) addConceptGrounding(id);
        if (loop.observations.trim()) {
          // Only suppress the static-RAG fallback when the loop actually
          // produced grounding; if the model chose no tools, let static RAG run
          // for tutor/coach so we don't lose corpus grounding on a factual turn.
          reactHandledGrounding = true;
          context += `\n\n## Retrieved context (from tools — ground your answer in these when relevant)`;
          context += `\nIf you materially use one, soft-cite once at the very end (stripped from the learner's view): [[ASF_CITE:{"concept_id":"<id>"}]]. Never invent citations, name the tools, or print these ids/headings in your reply.`;
          context += `\n\n${loop.observations.replace(/(^|\n)#{1,6}[ \t]+/g, '$1')}`;
          logger.info('chat: react tool grounding injected', {
            agent,
            toolCalls: loop.toolCallsMade,
            grounding: loop.groundingIds.length,
          });
        }
      }
    } catch (err) {
      logger.warn('chat: react loop failed', { err: String(err) });
    }
  }

  // On a confirm turn the tool loop is skipped; steer the answer to acknowledge
  // the change the server is about to apply (in finalize) instead of re-asking.
  if (planConfirmTurn) {
    context += `\n\n${PLAN_CONFIRM_TURN_INSTRUCTION[responseLocale === 'en' ? 'en' : 'he']}`;
  }

  const ragCandidateTurn =
    !reactHandledGrounding &&
    !planChangeFlow &&
    !planConfirmTurn &&
    !planStatusAsk &&
    RAG_ENABLED &&
    !minimal &&
    (agent === 'tutor' || agent === 'coach') &&
    searchMessage.trim().length >= 10 &&
    !planChangeTurn;
  if (ragCandidateTurn) {
    try {
      // Language is auto-detected from the query inside retrieveChunks so a
      // Hebrew question retrieves Hebrew passages regardless of response locale.
      const chunks = await retrieveChunks({
        query: searchMessage,
        topK: RAG_TOP_K,
      });
      if (chunks.length > 0) {
        for (const ch of chunks) addConceptGrounding(ch.conceptId);
        // Soft-cite convention (ADR-0015): if the model materially uses a passage
        // it emits ONE [[ASF_CITE:…]] at the end. That tag is audit-only — it is
        // stripped from the learner's view — so this is grounding, not a visible
        // footnote. Never ask for visible "[heading]" text (breaks the invented-
        // Sources eval and leaks internal ids to learners).
        context += `\n\n## Source passages (authored corpus — ground your answer in these when relevant)`;
        context += `\nIf you materially use one, soft-cite once at the very end (stripped from the learner's view): [[ASF_CITE:{"concept_id":"<id>"}]]. Never invent citations or print these ids/headings in your reply.`;
        chunks.forEach((c, i) => {
          const label = c.heading || c.title || c.sourceDocId;
          const cid = c.conceptId ? ` · concept:${c.conceptId}` : '';
          // Strip markdown ATX headings so a chunk body can't create a spurious
          // "## " section split in partitionInjectedContext.
          const bodyText = truncateChatText(c.text, RAG_CHUNK_CHARS).replace(
            /(^|\n)#{1,6}[ \t]+/g,
            '$1',
          );
          context += `\n\n[${i + 1}] (${label}${cid}) ${bodyText}`;
        });
        logger.info('chat: rag grounding injected', {
          agent,
          chunks: chunks.length,
          channel: chunks[0]?.channel,
        });
      }
    } catch (err) {
      logger.warn('chat: rag retrieve failed', { err: String(err) });
    }
  }

  const profileAnxiety =
    typeof (profile?.mental_state as { anxiety?: number } | null)?.anxiety === 'number'
      ? (profile!.mental_state as { anxiety: number }).anxiety
      : null;
  const injectWellbeingSnapshot =
    !minimal &&
    profile &&
    contextNeeds.wellbeing &&
    (agent === 'tutor' || agent === 'mentor') &&
    (tutorIntent === 'exam_anxiety' ||
      (profileAnxiety != null && profileAnxiety >= ANXIETY_THRESHOLD));

  let wellbeingBiasForChat: Awaited<ReturnType<typeof evaluateWellbeingSignals>>['bias'] | null =
    null;
  if (profile && (agent === 'tutor' || agent === 'mentor') && !minimal && contextNeeds.wellbeing) {
    const wellbeingInput = {
      subjects: profile.subjects,
      mental_state: profile.mental_state,
      next_test_date: profile.next_test_date,
      personality_profile: {
        ...(profile.personality_profile ?? {}),
        ...(tutorIntent === 'exam_anxiety' ? { wellbeing_chat_trigger: 'exam_anxiety' } : {}),
      },
      points_group: profile.points_group,
      wellbeing_plan_bias: profile.wellbeing_plan_bias,
    };
    const previousBias = wellbeingPlanBiasFromProfile(wellbeingInput, new Date());
    const evaluated = evaluateWellbeingSignals(
      wellbeingInput,
      mastery,
      previousBias,
      new Date(),
    );
    wellbeingBiasForChat = evaluated.bias;
    if (wellbeingBiasForChat.active) {
      const morale =
        wellbeingBiasForChat.morale_concepts.length > 0
          ? wellbeingBiasForChat.morale_concepts
          : await selectMoraleConcepts({
              learnerId: userId,
              profile: wellbeingInput,
              mastery,
              strengthAnchors: wellbeingBiasForChat.strength_anchors,
            }).catch(() => [] as string[]);
      wellbeingBiasForChat = { ...wellbeingBiasForChat, morale_concepts: morale };
      void saveWellbeingPlanBias(userId, wellbeingBiasForChat).catch((err) =>
        logger.warn('chat: wellbeing bias persist failed', { err: String(err) }),
      );
    }
  }

  const showWellbeingBlock =
    injectWellbeingSnapshot || (wellbeingBiasForChat?.active ?? false);
  if (showWellbeingBlock && wellbeingBiasForChat && (agent === 'tutor' || agent === 'mentor')) {
    context += `\n\n## Wellbeing-aware plan snapshot (internal — soft framing only)`;
    context += `\nUse server-selected concepts below with reassuring, rational copy. Do NOT reveal selection mechanism or strength-based logic unless the learner asks directly.`;
    if (wellbeingBiasForChat.morale_concepts.length) {
      context += `\n- Topics that may support confidence/pacing:`;
      for (const cid of wellbeingBiasForChat.morale_concepts.slice(0, 4)) {
        context += `\n  - ${formatConceptLine(cid)}`;
      }
    }
    if (wellbeingBiasForChat.strength_anchors.length && agent === 'tutor') {
      context += `\n- (Internal only — do not cite to learner) strength anchors: ${wellbeingBiasForChat.strength_anchors.slice(0, 3).join(', ')}`;
    }
    if (agent === 'mentor') {
      context += `\n- Mentor owns wellbeing bias policy; document rationale in private notes when relevant.`;
    }
  }

  const needsPlanner =
    contextNeeds.learningPlanSnapshot ||
    Boolean(topic) ||
    agent === 'coach' ||
    agent === 'progress_analyzer';

  let hybridPathNodes: WeakAtomPathNode[] = [];
  let hybridBlockingAtoms: Array<{ atom: string }> = [];
  let coachDueForPack: Awaited<ReturnType<typeof getDueReviews>> = [];

  if (
    needsPlanner &&
    (agent === 'tutor' ||
      agent === 'coach' ||
      agent === 'curriculum_designer' ||
      agent === 'progress_analyzer')
  ) {
    const goalKey =
      (profile?.personality_profile as { goal_key?: string } | null)?.goal_key ?? null;

    // Goal-pacing signal (ADR-0009): makes the agent trajectory-aware — how ready
    // the learner is for the goal, how much time is left, and whether they are on
    // pace. Read-only; framing only. Null when the goal has no derived frontier.
    const pacing = computePlanPacing(profile, mastery);
    if (pacing) {
      const readinessPct = Math.round(pacing.goal_readiness * 100);
      const mastered = pacing.frontier_size - pacing.remaining_scope;
      const paceHint =
        pacing.status === 'at_risk'
          ? 'behind pace — prioritize goal-critical concepts, keep scope tight, protect morale'
          : pacing.status === 'ahead'
            ? 'ahead of pace — you may offer a stretch concept or a deeper challenge'
            : 'on track — maintain a steady, sustainable pace';
      context += `\n\n## Goal pacing (internal — adaptive framing only, do not read out verbatim)`;
      context += `\n- Goal readiness: ${readinessPct}% (${mastered}/${pacing.frontier_size} goal concepts)`;
      context += `\n- Time to goal: ~${pacing.weeks_left} week(s); pace: ${pacing.status} (need ${pacing.required_velocity.toFixed(1)} vs capacity ${pacing.capacity}/wk)`;
      context += `\n- Guidance: ${paceHint}`;
    }

    const coachExamDays =
      agent === 'coach' && profile
        ? coachDaysUntilExam(profile.next_test_date, profile.final_goal_date)
        : null;
    const goalConcept =
      agent === 'coach'
        ? pickCoachPlannerGoal({
            relatedConceptId: related[0]?.id ?? null,
            topic,
            topicInKg: Boolean(topic && kgByName[topic]),
            currentPlan,
            weakConcepts,
            goalKey,
            daysUntilExam: coachExamDays,
          })
        : pickPlannerGoalConcept(related, topic, currentPlan, weakConcepts);
    if (goalConcept) {
      const plan = await buildLearningPlan({
        learnerId: userId,
        goalConceptId: goalConcept,
        maxNodes: 4,
      }).catch(() => null);
      if (plan && plan.path.length > 0) {
        hybridPathNodes = plan.path.map((node) => ({
          concept_id: node.concept_id,
          name: node.name,
          name_he: node.name_he,
          weak_atoms: node.weak_atoms.map((a) => ({
            atom: a.atom,
            mastery: a.mastery,
          })),
        }));
        for (const node of plan.path) {
          addConceptGrounding(node.concept_id);
        }
        hybridBlockingAtoms = plan.blocking_atoms.map((a) => ({ atom: a.atom }));
        context += `\n\n## Learning-plan snapshot (goal: ${plan.goal.name})`;
        for (const node of plan.path.slice(0, 4)) {
          const pct = Math.round((1 - node.urgency) * 100);
          context += `\n- [${node.concept_id}] ${node.name_he || node.name} ~${pct}%`;
          if (agent === 'coach' && node.weak_atoms.length > 0) {
            const atoms = node.weak_atoms
              .slice(0, 3)
              .map((a) => `${a.atom} (${Math.round(a.mastery * 100)}%)`)
              .join(', ');
            context += ` — weak atoms: ${atoms}`;
          }
        }
        if (plan.blocking_atoms.length > 0) {
          const tops = plan.blocking_atoms.slice(0, 3).map((a) => a.atom).join(', ');
          context += `\n- Blocking: ${tops}`;
        }
      }
    }
  }

  if (!minimal && agent === 'coach') {
    const coachExamDays = profile
      ? coachDaysUntilExam(profile.next_test_date, profile.final_goal_date)
      : null;
    if (coachExamDays != null && isWithinExamPrepWindow(coachExamDays)) {
      context += buildCoachExamPrepBlock({
        daysLeft: coachExamDays,
        testName: profile?.next_test_name,
        quickMode,
        quickDuration,
        locale,
      });
    }
    const dueRaw = await getDueReviews(userId).catch(() => [] as Awaited<ReturnType<typeof getDueReviews>>);
    const due = filterDueReviewsForProfile(dueRaw, {
      subjects: profileSubjects,
      planConceptIds: planConceptIds.size > 0 ? planConceptIds : undefined,
    });
    coachDueForPack = due;
    context += buildCoachFsrsInstruction({
      due,
      strongConcepts,
      daysUntilExam: coachExamDays,
      inQuickMode: quickMode,
    });
    const difficultyInstruction = buildCoachDifficultyInstruction(
      detectCoachDifficultySignal(message, recentForIntent),
      locale,
    );
    if (difficultyInstruction) {
      context += difficultyInstruction;
    }
  }

  // ADR-0014: handoff digests + hybrid tool packs + solver reveal policy (Coach + Tutor)
  if (!minimal && (agent === 'coach' || agent === 'tutor') && (contextNeeds.hybridTools || contextNeeds.handoffDigest || contextNeeds.methodAuthority)) {
    const conceptId = related[0]?.id ?? topic ?? null;
    const expand = wantsMemoryExpand(message) || Boolean(conceptId && agentNotes.length < 2);

    if (contextNeeds.handoffDigest) {
    const peerIds = (['tutor', 'mentor', 'coach', 'reviewer'] as LiveAgentId[]).filter(
      (a) => a !== agent,
    );
    const peerNoteLists = await Promise.all(
      peerIds.map((a) =>
        fetchAgentNotes(userId, a, 4).catch(() => [] as Awaited<ReturnType<typeof fetchAgentNotes>>),
      ),
    );
    const digestNotes = peerNoteLists.flatMap((notes, i) =>
      notes.map((n) => ({
        agent: peerIds[i]!,
        kind: n.kind,
        content: n.content,
        importance: n.importance,
        related_concept_id: n.related_concept_id,
        created_at: n.created_at,
      })),
    );
    const digest = buildHandoffDigest({
      readingAgent: agent as LiveAgentId,
      notes: digestNotes,
      conceptFilter: expand ? conceptId : null,
    });
    if (digest) context += `\n\n${digest}`;
    }

    if (contextNeeds.hybridTools || contextNeeds.methodAuthority) {
    const lesson = conceptId
      ? await fetchLessonByConceptId(conceptId).catch(() => null)
      : null;
    if (lesson?.lesson) {
      addConceptGrounding(lesson.lesson.concept_id);
      addLessonGrounding(lesson.lesson.id);
    }
    const expandNotes = expand
      ? await fetchAgentNotes(userId, agent, 12).catch(() => agentNotes)
      : agentNotes;

    if (contextNeeds.hybridTools) {
    if (agent === 'coach') {
      const pack = buildCoachHybridToolPack({
        due: coachDueForPack,
        pathNodes: hybridPathNodes,
        blockingAtoms: hybridBlockingAtoms,
        lesson,
        expandNotes,
        expand,
        userMessage: message,
        locale: responseLocale,
        conceptId,
      });
      context += `\n\n${pack.block}`;
    } else {
      const pack = buildTutorSolverToolPack({
        lesson,
        expandNotes,
        expand,
        userMessage: message,
        locale: responseLocale,
        conceptId,
      });
      context += `\n\n${pack.block}`;
    }

    const cycles = countSolverHintCycles(recentForIntent);
    const authoritativeSolve = trySolveAuthoritative(message);
    context += `\n\n${buildSolverRevealInstruction({
      cycles,
      wantsFull: wantsFullSolutionNow(message) || tutorIntent === 'worked_solution',
      confirmed: learnerConfirmedReveal(message),
      inPracticeArena: Boolean(practiceContext),
      practiceGraded: practiceContext?.item_graded === true,
      hasAuthoritativeSolve: Boolean(authoritativeSolve),
    })}`;
    }

    if (contextNeeds.methodAuthority) {
    const authoritativeSolve = trySolveAuthoritative(message);
    const methodInventory = buildMethodSourceInventory({
      conceptId,
      lesson,
      verify: authoritativeSolve,
    });
    context += `\n\n${buildMethodAuthorityBlock(methodInventory, responseLocale)}`;
    if (isMathTeachingTurn(message) || tutorIntent === 'agent_correction') {
      context += `\n\n${METHOD_GROUNDING_TURN_INSTRUCTION}`;
    }
    }
    }
  }

  // ADR-0011/0012: bilingual briefing + authoritative learner-facing pack + turn blocks
  if (!minimal && liveAgents && profile && (contextNeeds.bilingualBriefing || contextNeeds.statusPack)) {
    const goalKey =
      (profile.personality_profile as { goal_key?: string } | null)?.goal_key ?? null;
    const mental = profile.mental_state as Record<string, unknown> | null;
    const pacingForBrief = computePlanPacing(profile, mastery);
    const daysLeft = daysUntilExam(
      {
        subjects: profile.subjects,
        mental_state: profile.mental_state,
        next_test_date: profile.next_test_date,
        personality_profile: profile.personality_profile,
        points_group: profile.points_group,
        wellbeing_plan_bias: profile.wellbeing_plan_bias,
      },
      new Date(),
    );
    const readiness = computeReadiness({
      goalKey,
      masteryScores: mastery,
      daysToExam: daysLeft,
    });
    const activeWeek =
      currentPlan?.weeks.find((w) => w.status === 'active') ?? currentPlan?.weeks[0];
    const weakConceptLabels = weakConcepts.map((id) => {
      const titles = resolveConceptTitles(id);
      return titles.title_he || titles.title_en || id;
    });
    const activeLessonLabels = (activeWeek?.concepts ?? [])
      .filter((c) => c.kind !== 'rest' && c.kind !== 'train')
      .map((c) => c.name_he || c.name);
    const activeTrainLabels = (activeWeek?.concepts ?? [])
      .filter((c) => c.kind === 'train')
      .map((c) => c.name_he || c.name);
    const liveSnap = buildPlanLiveSnapshot({
      goal: profile.goal,
      goalKey,
      nextTestDate: profile.next_test_date,
      finalGoalDate: profile.final_goal_date,
      planStartIso: currentPlan?.start_date ?? null,
      readiness: currentPlan?.pacing?.readiness ?? null,
      weakConceptLabels,
      activeLessonLabels,
      activeTrainLabels,
    });
    context += `\n\n${responseLocale === 'en' ? liveSnap.contextBlockEn : liveSnap.contextBlockHe}`;
    const nameOf = (id: string) => {
      const kgInfo = kgByName[id];
      return kgInfo?.name_he || kgInfo?.name || id;
    };
    const masteryScores = mastery as Record<string, number>;
    const nextStep = pickPressureNextStep({
      activeWeekConcepts: activeWeek?.concepts.map((c) => ({
        conceptId: c.concept_id,
        nameHe: c.name_he,
        nameEn: c.name,
        mastery: masteryScores[c.concept_id] ?? null,
      })),
      plannerPathIds: weakConcepts,
    });
    const briefingInput = {
      goalKey,
      goalLabel:
        displayLearnerGoal(profile.goal, responseLocale) ||
        goalKeyLabel(goalKey, responseLocale) ||
        null,
      examDateLabel: formatLearnerFacingDate(
        profile.next_test_date ?? profile.final_goal_date,
        responseLocale,
      ),
      daysToExam: daysLeft,
      hoursPerWeek: profile.hours_per_week,
      pointsGroup: profile.points_group,
      subjects: profile.subjects,
      anxiety: typeof mental?.anxiety === 'number' ? mental.anxiety : null,
      motivation: typeof mental?.motivation === 'number' ? mental.motivation : null,
      strongConcepts: strongConcepts.map(nameOf),
      weakConcepts: weakConcepts.map(nameOf),
      activeWeekNumber: activeWeek?.week_number ?? null,
      activeWeekConcepts: activeWeek?.concepts.map(
        (c) => c.name_he || c.name || c.concept_id,
      ),
      xpLevel: xpSnapForBriefing?.level ?? null,
      xpTotal: xpSnapForBriefing?.total_xp ?? null,
      readinessPct: readiness ? Math.round(readiness.readiness * 100) : null,
      readinessBand: readiness?.band ?? null,
      readinessPhase: readiness?.phase ?? null,
      paceStatus: pacingForBrief?.status ?? null,
      nextStepHe: nextStep?.labelHe ?? null,
      nextStepEn: nextStep?.labelEn ?? null,
      nextStepConceptId: nextStep?.conceptId ?? null,
    };
    if (contextNeeds.bilingualBriefing) {
      context += `\n\n${buildBilingualProgressBriefing(briefingInput)}`;
    }

    const skipStatusPack =
      Boolean(practiceContext) ||
      tutorIntent === 'agent_correction' ||
      !contextNeeds.statusPack;
    if (!skipStatusPack) {
      context += `\n\n${buildLearnerFacingStatusPack(briefingInput)}`;
    }
  }

  // Build protected tail: THIS TURN overrides — Tutor only for tutor contracts;
  // other agents get brevity only (ADR-0015: stop intent leakage).
  let promptTail = '';
  if (agent === 'tutor' && liveAgents && !minimal && tutorIntent) {
    if (tutorIntent === 'agent_correction') {
      promptTail += `\n\n${AGENT_CORRECTION_TURN_INSTRUCTION}`;
    } else if (isPressureFamilyIntent(tutorIntent) && !practiceContext && contextNeeds.statusPack) {
      promptTail += `\n\n${PRESSURE_FAMILY_TURN_INSTRUCTION}`;
      if (tutorIntent === 'context_challenge') {
        promptTail += `\n\n${CONTEXT_CHALLENGE_TURN_INSTRUCTION}`;
      }
      if (tutorIntent === 'plan_ownership') {
        promptTail += `\n\n${PLAN_OWNERSHIP_TURN_INSTRUCTION}`;
      }
    }
    if (tutorIntent === 'recovery_simplify') {
      promptTail += `\n\n${RECOVERY_TURN_INSTRUCTION}`;
    }
    if (tutorIntent === 'worked_solution' || tutorIntent === 'conversation_advance') {
      promptTail += `\n\n${WORKED_SOLUTION_TURN_INSTRUCTION}`;
    }
  }
  promptTail += `\n\n${CHAT_BREVITY_RULE}`;
  const { core, packs } = partitionInjectedContext(context);
  const fitted = assembleChatSystemPrompt(core, packs, promptTail);
  const system = fitted.system;
  if (fitted.dropped.length) {
    logger.info('chat: context sections dropped', { agent, dropped: fitted.dropped });
  }
  if (system.length > 14_000) {
    logger.warn('chat: large system prompt', {
      chars: system.length,
      agent,
      memoryTurns: recent.length,
      sessionId: sessionId ?? null,
      minimal,
      responseLocale,
    });
  }

  return {
    system,
    memory: compactMemoryTurns(
      recentForLLM.map((t) => ({
        role: t.role,
        content: t.content,
      })),
    ),
    groundingIds,
    responseLocale,
    planChangeFlow,
  };
}

async function* streamFromLLM(
  userId: string,
  message: string,
  agent: string,
  opts: {
    quickMode?: boolean;
    quickDuration?: string;
    topic?: string;
    sessionId?: string;
    practiceContext?: PracticeChatContext | null;
    turnGrounding?: ChatTurnGrounding;
  } = {},
): AsyncGenerator<string, LLMFailureInfo | undefined> {
  const cfg = getLLMConfig();
  if (!llmConfigured()) {
    logger.warn('LLM not configured — set LLM_API_KEY + LLM_BASE_URL (or GROQ_API_KEY)');
    return { kind: 'not_configured', provider: cfg.providerLabel };
  }

  const attempts: Array<{ label: string; context: Awaited<ReturnType<typeof buildContextPrompt>> }> = [];

  const publishGrounding = (context: Awaited<ReturnType<typeof buildContextPrompt>>) => {
    if (opts.turnGrounding) {
      opts.turnGrounding.groundingIds = new Set(context.groundingIds);
    }
  };

  try {
    const fullContext = await buildContextPrompt(userId, agent, message, opts);
    publishGrounding(fullContext);
    attempts.push({
      label: 'full',
      context: fullContext,
    });
  } catch (err) {
    logger.warn('buildContextPrompt failed, using bare persona', { err: String(err) });
    const bareContext = {
      system: fitSystemPrompt(`${buildCompactAgentBaseline()}\n\n${getAgentPersona(agent)}`),
      memory: [] as Array<{ role: 'user' | 'assistant'; content: string }>,
      groundingIds: new Set<string>(),
      responseLocale: 'he' as ChatResponseLocale,
      planChangeFlow: false,
    };
    publishGrounding(bareContext);
    attempts.push({
      label: 'bare',
      context: bareContext,
    });
  }

  const maxTokens = resolveChatMaxTokens({
    wantsWorkedSolution: wantsExpandedOutputBudget(message),
    wantsContinue: wantsExpandedOutputBudget(message),
  });

  for (let i = 0; i < attempts.length; i++) {
    const { label, context } = attempts[i]!;
    const failureSink = { current: null as LLMFailureInfo | null };
    const finishSink = { current: null as string | null };
    const responseLocale = context.responseLocale ?? 'he';

    const sampling = resolveAgentSampling(agent);
    const runOnce = async (system: string): Promise<string | null> => {
      const llmOpts = {
        system,
        messages: [...context.memory, { role: 'user' as const, content: message }],
        maxTokens,
        temperature: sampling.temperature,
        topP: sampling.topP,
        timeoutMs: CHAT_LLM_TIMEOUT_MS,
        models: resolveChatModelChain(),
        failureSink,
        finishSink,
      };
      // Buffer first (ADR-0015 quality gate) — do not stream a bad draft.
      let buffer = '';
      for await (const chunk of llmStream(llmOpts)) {
        buffer += chunk;
      }
      if (!buffer.trim()) {
        const backup = await llmComplete(llmOpts);
        if (backup?.content) buffer = backup.content;
      }
      return buffer.trim() ? buffer : null;
    };

    let draft = await runOnce(context.system);
    if (!draft) {
      const failure = failureSink.current;
      const shouldRetryMinimal =
        i === 0 &&
        attempts.length === 1 &&
        (failure?.kind === 'context_too_large' ||
          (failure?.kind === 'provider_error' &&
            context.system.length > CHAT_CONTEXT.maxSystemChars * 0.85) ||
          (failure?.kind === 'unknown' &&
            context.system.length > CHAT_CONTEXT.maxSystemChars * 0.9));
      if (shouldRetryMinimal) {
        logger.warn('chat: payload too large — retrying with minimal context', {
          agent,
          userId,
          systemChars: context.system.length,
          memoryTurns: context.memory.length,
        });
        try {
          const minimalContext = await buildContextPrompt(userId, agent, message, {
            ...opts,
            minimal: true,
          });
          publishGrounding(minimalContext);
          attempts.push({
            label: 'minimal',
            context: minimalContext,
          });
        } catch (err) {
          logger.warn('chat: minimal context build failed', { err: String(err) });
        }
        continue;
      }
      return failure ?? { kind: 'empty_response', provider: cfg.providerLabel };
    }

    const quality = scoreResponseQuality(draft, responseLocale);
    // Guided plan-change turns are short slot questions — a quality "repair"
    // rewrite burns another full LLM pass and can blow the Vercel budget so the
    // stream never closes (UI stuck on "thinking…" after the reply appears).
    if (!quality.ok && !context.planChangeFlow) {
      logger.info('chat: quality retry', {
        agent,
        failures: quality.failures,
        responseLocale,
        label,
      });
      const repaired = await runOnce(
        `${context.system}\n\n${qualityRepairInstruction(responseLocale, quality.failures)}`,
      );
      if (repaired) {
        const q2 = scoreResponseQuality(repaired, responseLocale);
        if (q2.ok || q2.failures.length <= quality.failures.length) {
          draft = repaired;
        }
      }
    }

    // Solver / stall hygiene BEFORE the learner sees tokens (no append-after-display).
    const hygiened = applyPostStreamSolverHygiene(agent, message, draft, responseLocale);
    draft = hygiened.text;

    // Emit in small chunks so the existing data-stream client still feels streaming.
    const chunkSize = 48;
    for (let c = 0; c < draft.length; c += chunkSize) {
      yield draft.slice(c, c + chunkSize);
    }

    if (finishSink.current === 'length') {
      return { kind: 'stream_interrupted', provider: cfg.providerLabel, model: 'length_cap' };
    }
    return undefined;
  }

  return { kind: 'unknown', provider: cfg.providerLabel };
}
