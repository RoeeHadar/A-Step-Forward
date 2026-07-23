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
} from '@/lib/neon-db';
import { buildLearningPlan } from '@/lib/learning-plan';
import { buildLessonCatalogSummary, buildPlanAllowlistBlock, PLAN_GROUNDING_RULES } from '@/lib/plan-catalog';
import {
  extractPlanUpdate,
  shouldApplyPlanChange,
  shouldApplyPlanImmediately,
  stripPlanMachineTags,
  PLAN_AGENT_INSTRUCTIONS,
} from '@/lib/plan-actions';
import {
  applyPlanFromUserMessage,
  buildPlanClarificationNotice,
  buildPlanApplyFailureNotice,
  buildPlanApplyingNotice,
  executePlanUpdate,
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
  formatPlanWeeksCompact,
  resolveChatMaxTokens,
  trimPersonaForChat,
  truncateChatText,
  truncationContinueNotice,
} from '@/lib/chat-context-policy';
import {
  buildBilingualProgressBriefing,
  buildLearnerFacingStatusPack,
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
  wantsExpandedOutputBudget,
  type TutorIntentContext,
} from '@/lib/learner-chat-intent';
import { computeReadiness } from '@/lib/readiness';
import { dreamLearnerMemory } from '@/lib/agent-memory-dream';
import kg from '@/lib/kg-data.json';
import { buildCompactAgentBaseline } from '@/lib/agent-baseline';
import { getAgentPersona } from '@/lib/agent-prompts';
import { LOCALE_COOKIE, resolveLocale } from '@/i18n/locale-storage';
import { normalizePlanChangeMessage, isPlanChangeTemplate } from '@/lib/plan-change-template';
import { resolveWebChatAgent } from '@/lib/web-agents';
import { daysUntilExam, ANXIETY_THRESHOLD } from '@/lib/wellbeing-plan-bias';
import { resolveConceptTitles } from '@/lib/concept-display-names';
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
  persistThrottledChatObservation,
  stripMemoryMachineTags,
} from '@/lib/chat-memory-persist';
import { isWithinExamPrepWindow } from '@/lib/exam-prep';
import {
  refusalFor,
  refusalStreamResponse,
  resolveChildMode,
  ruleClassify,
  type SafetyKind,
} from '@/lib/chat-safety';

export const runtime = 'nodejs';
export const maxDuration = 60;

// Keep upstream LLM timeout under Vercel maxDuration (60s on Pro).
const CHAT_LLM_TIMEOUT_MS = 45_000;

async function saveAssistantTurn(
  userId: string,
  agent: string,
  content: string,
  sessionId: string | undefined,
  locale: 'he' | 'en',
  childMode: boolean,
): Promise<void> {
  const cleaned = stripMemoryMachineTags(content);
  const postHit = ruleClassify(cleaned, { childMode });
  const toStore = postHit ? refusalFor(postHit) : cleaned;
  if (!postHit) {
    await applyMemoryTagsFromAssistant(userId, agent, content, { childMode });
  }
  await recordChatTurn(
    userId,
    agent,
    'assistant',
    compactStoredTurnContent(toStore, 'assistant', locale),
    sessionId,
  );
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
    return refusalStreamResponse(refusalFor(preHit));
  }

  // Record user turn before streaming so memory is durable for retries.
  await recordChatTurn(
    userId,
    agent,
    'user',
    compactStoredTurnContent(lastMessage, 'user', locale),
    sessionId,
  );

  // Memory durability: run the note write via `after()` so Vercel keeps the
  // function alive until it lands. A bare `void` here can be killed when the
  // streamed response closes — a prime cause of "Memory isn't updating".
  after(() =>
    persistThrottledChatObservation(userId, agent, lastMessage, topic).catch((err) =>
      logger.warn('chat: persistChatObservation failed', { err: String(err) }),
    ),
  );

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
      });
    }
    return gen;
  };

  const encoder = new TextEncoder();
  let assistantBuffer = '';

  const encodeToken = (text: string) => encoder.encode(`0:${JSON.stringify(text)}\n`);
  const encodeData = (data: unknown) => encoder.encode(`2:${JSON.stringify([data])}\n`);
  const encodeFinish = () =>
    encoder.encode(`d:${JSON.stringify({ finishReason: 'stop', usage: { promptTokens: 0, completionTokens: 0 } })}\n`);

  const finishTemplatePlanTurn = async (
    controller: ReadableStreamDefaultController<Uint8Array>,
    planResult: PlanApplyResult | null,
  ) => {
    if (planResult) appendPlanResult(controller, planResult);
    const visible = stripPlanMachineTags(assistantBuffer).trim();
    if (visible) {
      await saveAssistantTurn(userId, agent, visible, sessionId, locale, childMode);
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

          if (assistantBuffer) {
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
            );
            if (!planEagerAttempted && finalizeResult) {
              appendPlanResult(controller, finalizeResult);
            }
          }
          controller.enqueue(encodeFinish());
          controller.close();
        } else {
          assistantBuffer += value;
          controller.enqueue(encodeToken(value));
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
          );
          if (!planEagerAttempted && finalizeResult) {
            appendPlanResult(controller, finalizeResult);
          }
        }
        controller.enqueue(encodeFinish());
        controller.close();
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
): Promise<PlanApplyResult | null> {
  const visible = stripPlanMachineTags(assistantRaw);
  const isPlanAgent = agent === 'tutor';

  if (!isPlanAgent) {
    await saveAssistantTurn(userId, agent, visible, sessionId, locale, childMode);
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
      await saveAssistantTurn(userId, agent, `${visible}\n\n${failureNotice}`, sessionId, locale, childMode);
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
        await saveAssistantTurn(userId, agent, full, sessionId, locale, childMode);
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
      await saveAssistantTurn(userId, agent, saved, sessionId, locale, childMode);
      return { ...result, failureNotice };
    } catch (err) {
      logger.warn('chat: plan update threw', { err: String(err) });
      const failureNotice = buildPlanApplyFailureNotice(locale, String(err));
      await saveAssistantTurn(userId, agent, `${visible}\n\n${failureNotice}`, sessionId, locale, childMode);
      return { applied: false, error: String(err), failureNotice };
    }
  }

  const { payload: prematureUpdate } = extractPlanUpdate(assistantRaw);
  if (prematureUpdate?.confirmed) {
    logger.warn('chat: ASF_PLAN_UPDATE ignored — learner did not confirm in this turn');
  }

  await saveAssistantTurn(userId, agent, visible, sessionId, locale, childMode);
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

function findRelevantConcepts(message: string, subjects: string[]): KgConcept[] {
  if (!message) return [];
  const lower = message.toLowerCase();
  const matches: KgConcept[] = [];
  for (const concept of Object.values(kgByName)) {
    if (subjects.length && !subjects.includes(concept.subject)) continue;
    const id = concept.id.replace(/_/g, ' ');
    if (
      lower.includes(id) ||
      lower.includes(concept.name.toLowerCase()) ||
      (concept.name_he && lower.includes(concept.name_he.toLowerCase()))
    ) {
      matches.push(concept);
    }
  }
  return matches.slice(0, 3);
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
): Promise<{ system: string; memory: Array<{ role: 'user' | 'assistant'; content: string }> }> {
  const {
    quickMode = false,
    quickDuration = '15',
    topic,
    sessionId,
    minimal = false,
    practiceContext = null,
  } = opts;
  // Each helper catches its own errors so a single DB issue cannot break chat.
  const [profile, mastery, recent, persona, agentNotes, cookieStore] = await Promise.all([
    getLearnerProfile(userId).catch(() => null),
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

  const locale = resolveLocale(cookieStore.get(LOCALE_COOKIE)?.value);
  const recentForIntent = recent.map((t) => ({ role: t.role, content: t.content }));

  let tutorContract: ReturnType<typeof buildTutorInteractionContract> | null = null;
  let tutorIntent: ReturnType<typeof classifyTutorChatIntent> | null = null;
  const liveAgents = agent === 'tutor' || agent === 'mentor' || agent === 'coach' || agent === 'reviewer';
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
    if (agent === 'tutor') {
      tutorContract = buildTutorInteractionContract(tutorIntent, locale, intentCtx);
    }

    if (tutorIntent === 'exam_anxiety') {
      void setWellbeingChatTrigger(userId, 'exam_anxiety').catch((err) =>
        logger.warn('chat: wellbeing chat trigger persist failed', { err: String(err) }),
      );
    }
  }

  let context = `${buildCompactAgentBaseline()}\n\n${getAgentPersona(agent)}`;

  if (agent === 'tutor' && tutorContract?.learnerPreferenceOverride) {
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

  context += `\n\n## Response language`;
  context += `\n- Language preference: ${locale === 'en' ? 'English' : 'Hebrew'} — respond in this language by default`;

  if (!profile) {
    // Onboarded learners always have a profile row. A missing row means
    // either a brand-new user or a probe before onboarding. Tell the
    // agent explicitly so it doesn't pretend it knows their context.
    context += `\n\n## Brand-new learner`;
    context += `\nNo learner profile is on file yet. Open with a one-sentence orientation in Hebrew (or match the language the learner just used), and invite them to complete the 4-step onboarding at \`/onboarding\` so the rest of the agent network can plan a personalised path. Do NOT improvise a curriculum or recommend specific lessons until a profile exists.`;
  }

  // CLAUDE.md-style learner persona — shared across every agent, written by
  // the Memory Steward (and any agent allowed to). Tells you HOW this
  // learner thinks/talks/learns, NOT what they know (that's mastery).
  if (!minimal && persona?.text && persona.text.trim().length > 0) {
    context += `\n\n## What I know about this learner (shared persona)`;
    context += `\n${trimPersonaForChat(persona.text)}`;
    context += `\n- Persona hygiene: do not paste gate-score lines or observations verbatim; paraphrase into learner language.`;
  }

  let xpSnapForBriefing: {
    total_xp: number;
    level: number;
  } | null = null;
  if (!minimal) {
    try {
      const { ensureXpSnapshot, formatXpContextBlock } = await import('@/lib/learner-xp');
      const xpSnap = await ensureXpSnapshot(userId);
      xpSnapForBriefing = { total_xp: xpSnap.total_xp, level: xpSnap.level };
      const xpLocale = locale === 'en' ? 'en' : 'he';
      context += `\n\n${formatXpContextBlock(xpSnap, xpLocale)}`;
    } catch {
      // XP is optional context
    }
  }

  if (!minimal && agentNotes.length > 0) {
    context += `\n\n## My private notes on this learner (agent: ${agent})`;
    for (const n of agentNotes) {
      const tag = n.related_concept_id ? ` [${n.related_concept_id}]` : '';
      context += `\n- (${n.kind})${tag} ${truncateChatText(n.content, CHAT_CONTEXT.maxAgentNoteChars)}`;
    }
  }
  if (profile) {
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
  if (weakConcepts.length || strongConcepts.length) {
    context += `\n\n## Mastery so far`;
    if (weakConcepts.length) context += `\n- Weak areas: ${weakConcepts.join(', ')}`;
    if (strongConcepts.length) context += `\n- Strong areas: ${strongConcepts.join(', ')}`;
  }

  const diagnosticSummary = (
    profile?.mental_state as { diagnostic_summary?: { agent_brief_en?: string; agent_brief_he?: string } } | null
  )?.diagnostic_summary;
  if (profile && diagnosticSummary?.agent_brief_en) {
    const lang =
      (profile.personality_profile as { ui_lang?: string } | null)?.ui_lang === 'he'
        ? 'he'
        : 'en';
    context += `\n\n${formatDiagnosticSummaryForAgents(diagnosticSummary as DiagnosticSummary, lang)}`;
  }

  if (profile && (agent === 'mentor' || agent === 'tutor')) {
    const plan = currentPlan;
    const normalizedMsg = normalizePlanChangeMessage(message);
    const needsPlanCatalog =
      tutorContract?.injectPlanCatalog ||
      isPlanChangeTemplate(normalizedMsg) ||
      shouldApplyPlanImmediately(message);

    if (plan?.weeks?.length) {
      context += `\n\n## Current weekly learning plan`;
      context += `\nGoal: ${plan.goal} · ${plan.start_date} → ${plan.end_date ?? 'open'}`;
      context += `\n${formatPlanWeeksCompact(plan.weeks, minimal ? 'minimal' : 'full')}`;
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
      context += `\n\n${PLAN_AGENT_INSTRUCTIONS}`;
    } else if (!minimal && agent === 'tutor' && tutorContract) {
      context = appendTutorContractToContext(context, tutorContract);
    } else if (!minimal && agent === 'mentor') {
      context += `\n\n## Plan guidance`;
      context += `\nAnswer timeline/readiness from the plan above. Plan edits need the Tutor sidebar template.`;
    }
  }

  if (topic && !practiceContext) {
    context += `\n\n## Active study context`;
    context += `\nThe learner is currently studying concept \`${topic}\` on the lesson page. Ground your answer in this topic when relevant.`;
    const topicConcept = kgByName[topic];
    if (topicConcept) {
      context += `\n- ${topicConcept.name} (${topicConcept.id})`;
      if (topicConcept.prerequisites?.length) {
        context += ` — prerequisites: ${topicConcept.prerequisites.join(', ')}`;
      }
    }
  } else if (topic && practiceContext) {
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
  const related = minimal ? [] : findRelevantConcepts(searchMessage, profile?.subjects ?? []);
  if (related.length) {
    context += `\n\n## Relevant curriculum context`;
    for (const c of related) {
      context += `\n- ${c.name} (${c.id})`;
      if (c.prerequisites?.length) context += ` — prerequisites: ${c.prerequisites.join(', ')}`;
    }

    // Inject agent_hints from the matching AI-authored lessons so the Tutor
    // can ground its reply in the canonical key insights, pacing hints, and
    // common-misconception triggers we authored per concept.
    if (agent === 'tutor' || agent === 'coach') {
      const hintsRows = await fetchLessonAgentHintsByConceptIds(related.map((c) => c.id)).catch(
        () => [] as Awaited<ReturnType<typeof fetchLessonAgentHintsByConceptIds>>,
      );
      if (hintsRows.length) {
        context += `\n\n## Lesson-level guidance for the AI-authored corpus`;
        const lowerMsg = message.toLowerCase();
        for (const row of hintsRows.slice(0, 2)) {
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

  const profileAnxiety =
    typeof (profile?.mental_state as { anxiety?: number } | null)?.anxiety === 'number'
      ? (profile!.mental_state as { anxiety: number }).anxiety
      : null;
  const injectWellbeingSnapshot =
    !minimal &&
    profile &&
    (agent === 'tutor' || agent === 'mentor') &&
    (tutorIntent === 'exam_anxiety' ||
      (profileAnxiety != null && profileAnxiety >= ANXIETY_THRESHOLD));

  let wellbeingBiasForChat: Awaited<ReturnType<typeof evaluateWellbeingSignals>>['bias'] | null =
    null;
  if (profile && (agent === 'tutor' || agent === 'mentor') && !minimal) {
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
    tutorContract?.injectLearningPlanSnapshot ||
    Boolean(topic) ||
    agent === 'coach' ||
    agent === 'progress_analyzer';
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

  // ADR-0011/0012: bilingual briefing + authoritative learner-facing pack + turn blocks
  if (!minimal && liveAgents && profile) {
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
      goalLabel: profile.goal,
      examDateLabel: profile.next_test_date
        ? String(profile.next_test_date).slice(0, 10)
        : null,
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
    context += `\n\n${buildBilingualProgressBriefing(briefingInput)}`;
    context += `\n\n${buildLearnerFacingStatusPack(briefingInput)}`;

    if (tutorIntent && isPressureFamilyIntent(tutorIntent)) {
      context += `\n\n${PRESSURE_FAMILY_TURN_INSTRUCTION}`;
      if (tutorIntent === 'context_challenge') {
        context += `\n\n${CONTEXT_CHALLENGE_TURN_INSTRUCTION}`;
      }
      if (tutorIntent === 'plan_ownership') {
        context += `\n\n${PLAN_OWNERSHIP_TURN_INSTRUCTION}`;
      }
    }
    if (tutorIntent === 'recovery_simplify') {
      context += `\n\n${RECOVERY_TURN_INSTRUCTION}`;
    }
    if (tutorIntent === 'worked_solution' || tutorIntent === 'conversation_advance') {
      context += `\n\n${WORKED_SOLUTION_TURN_INSTRUCTION}`;
    }
  }

  context += `\n\n${CHAT_BREVITY_RULE}`;

  const system = fitSystemPrompt(context);
  if (system.length > 14_000) {
    logger.warn('chat: large system prompt', {
      chars: system.length,
      agent,
      memoryTurns: recent.length,
      sessionId: sessionId ?? null,
      minimal,
    });
  }

  return {
    system,
    memory: compactMemoryTurns(
      recent.map((t) => ({
        role: t.role,
        content: t.content,
      })),
    ),
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
  } = {},
): AsyncGenerator<string, LLMFailureInfo | undefined> {
  const cfg = getLLMConfig();
  if (!llmConfigured()) {
    logger.warn('LLM not configured — set LLM_API_KEY + LLM_BASE_URL (or GROQ_API_KEY)');
    return { kind: 'not_configured', provider: cfg.providerLabel };
  }

  const attempts: Array<{ label: string; context: Awaited<ReturnType<typeof buildContextPrompt>> }> = [];

  try {
    attempts.push({
      label: 'full',
      context: await buildContextPrompt(userId, agent, message, opts),
    });
  } catch (err) {
    logger.warn('buildContextPrompt failed, using bare persona', { err: String(err) });
    attempts.push({
      label: 'bare',
      context: {
        system: fitSystemPrompt(`${buildCompactAgentBaseline()}\n\n${getAgentPersona(agent)}`),
        memory: [],
      },
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
    const llmOpts = {
      system: context.system,
      messages: [...context.memory, { role: 'user' as const, content: message }],
      maxTokens,
      temperature: 0.4,
      timeoutMs: CHAT_LLM_TIMEOUT_MS,
      models: resolveChatModelChain(),
      failureSink,
      finishSink,
    };

    let emitted = false;
    for await (const chunk of llmStream(llmOpts)) {
      emitted = true;
      yield chunk;
    }

    if (!emitted) {
      logger.warn('chat: stream empty — trying non-stream completion', { agent, userId, label });
      const backup = await llmComplete(llmOpts);
      if (backup?.content) {
        logger.info('chat: non-stream backup succeeded', { model: backup.model, agent, label });
        yield backup.content;
        return undefined;
      }
    } else {
      if (finishSink.current === 'length') {
        // Signal truncation to the outer stream via a sentinel return kind.
        return { kind: 'stream_interrupted', provider: cfg.providerLabel, model: 'length_cap' };
      }
      return undefined;
    }

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
        attempts.push({
          label: 'minimal',
          context: await buildContextPrompt(userId, agent, message, { ...opts, minimal: true }),
        });
      } catch (err) {
        logger.warn('chat: minimal context build failed', { err: String(err) });
      }
      continue;
    }

    return failure ?? { kind: 'unknown', provider: cfg.providerLabel };
  }

  return { kind: 'unknown', provider: cfg.providerLabel };
}
