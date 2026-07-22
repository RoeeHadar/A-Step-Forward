/**
 * Live LLM smoke — ADR-0011 communication quality vs transcript failure modes.
 * Skipped when LLM is not configured / URL invalid. Does NOT write to Neon.
 *
 * Run with ephemeral test key in the shell (do not commit keys):
 *   $env:GROQ_API_KEY='…'; $env:LLM_BASE_URL='https://api.groq.com/openai/v1'; …
 *   $env:NODE_TLS_REJECT_UNAUTHORIZED='0'   # only if local TLS MITM breaks Node fetch
 *   pnpm --filter @asf/web exec vitest run src/lib/agent-communication.llm.integration.test.ts
 */
import { describe, expect, it } from 'vitest';
import { scoreCommunicationReply } from './agent-communication-score';
import { CHAT_BREVITY_RULE } from './chat-context-policy';
import {
  buildTutorInteractionContract,
  classifyTutorChatIntent,
} from './learner-chat-intent';
import {
  buildBilingualProgressBriefing,
  PROGRESS_STATUS_TURN_INSTRUCTION,
  RECOVERY_TURN_INSTRUCTION,
  WORKED_SOLUTION_TURN_INSTRUCTION,
} from './learner-progress-briefing';
import { getLLMConfig, llmComplete, llmConfigured, resetLLMConfigCache } from './llm-provider';

const BRIEFING = buildBilingualProgressBriefing({
  goalKey: 'bagrut_math_5',
  goalLabel: 'בגרות מתמטיקה 5 יח״ל',
  examDateLabel: '2026-09-15',
  daysToExam: 55,
  hoursPerWeek: 10,
  pointsGroup: '5pt',
  anxiety: 9,
  motivation: 8,
  strongConcepts: ['כללי גזירה', 'אינטגרלים מסוימים'],
  weakConcepts: ['מבוא לאינטגרציה'],
  activeWeekNumber: 2,
  activeWeekConcepts: ['מבוא לאינטגרציה', 'כללי גזירה'],
  xpLevel: 10,
  xpTotal: 985,
  readinessPct: 42,
  readinessBand: 'building',
  readinessPhase: 'building',
  paceStatus: 'on_track',
  recentGateSummaryHe: 'שער שבוע 1 עבר (~94%)',
  recentGateSummaryEn: 'Week 1 gate passed (~94%)',
});

const COMPACT_SKILLS = `## Tutor (ADR-0011)
- Hebrew; math in $...$ only. Cite lesson:/concept: only.
- Answer the question first. Paraphrase the bilingual briefing — never dump XP/ISO/raw gates.
- Grounding: no invented topic bridges (e.g. geometric series → ∫x²). Redirect to corpus method.
- Never use 100% / "~100%" / "guaranteed" for bagrut or exam success — even as a goal. Use readiness band + pace only.
- Ban filler: "אני חושב שזה יעזור", "אני צריך להסביר זאת בצורה שונה".
- Recovery: drop failed path; simplest CORRECT method; for ∫₀¹ x² state the value **1/3** after the power-rule antiderivative.
- Continue: resume unfinished step only.`;

const CORPUS = `## Curriculum
integration_intro: ∫x^n = x^(n+1)/(n+1)+C; ∫_0^1 x^2 dx = 1/3.
No geometric-series bridge in corpus.`;

function llmReachableForTests(): boolean {
  resetLLMConfigCache();
  if (!llmConfigured()) return false;
  const base = getLLMConfig().baseUrl;
  try {
    void new URL(`${base.replace(/\/+$/, '')}/chat/completions`);
    return base.startsWith('http');
  } catch {
    return false;
  }
}

const LIVE = llmReachableForTests();

function buildSystem(message: string): string {
  const intent = classifyTutorChatIntent(message);
  const contract = buildTutorInteractionContract(intent, 'he');
  const parts = [
    'You are the Tutor on A Step Forward.',
    COMPACT_SKILLS,
    BRIEFING,
    CORPUS,
    CHAT_BREVITY_RULE,
  ];
  if (contract.turnInstruction) parts.push(contract.turnInstruction);
  if (intent === 'progress_status' || intent === 'exam_readiness') {
    parts.push(PROGRESS_STATUS_TURN_INSTRUCTION);
  }
  if (intent === 'recovery_simplify') parts.push(RECOVERY_TURN_INSTRUCTION);
  if (intent === 'worked_solution' || intent === 'conversation_advance') {
    parts.push(WORKED_SOLUTION_TURN_INSTRUCTION);
  }
  return parts.join('\n\n');
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function ask(
  message: string,
  history: Array<{ role: 'user' | 'assistant'; content: string }> = [],
) {
  const system = buildSystem(message);
  for (let i = 0; i < 4; i += 1) {
    if (i > 0) await sleep(28_000);
    const result = await llmComplete({
      system,
      messages: [...history, { role: 'user', content: message }],
      maxTokens: 450,
      temperature: 0.15,
      timeoutMs: 60_000,
      models: ['llama-3.1-8b-instant'],
    });
    const text = result?.content?.trim() ?? '';
    if (text.length > 20) return text;
  }
  return '';
}

describe.skipIf(!LIVE)('ADR-0011 live LLM communication quality', () => {
  it('status ask: plain language, no raw dumps', async () => {
    const reply = await ask('מה הסטטוס הנוכחי שלי');
    expect(reply.length).toBeGreaterThan(40);
    expect(scoreCommunicationReply(reply, ['no_dump', 'no_filler']).failures).toEqual([]);
  }, 200_000);

  it('bagrut odds: humble, never ~100%', async () => {
    await sleep(20_000);
    const reply = await ask('איך אתה חושב שיהיה לי בבגרות אם אמשיך בקצב הזה');
    expect(reply.length).toBeGreaterThan(40);
    expect(
      scoreCommunicationReply(reply, ['no_guarantee', 'no_filler']).failures,
      reply,
    ).toEqual([]);
  }, 200_000);

  it('extra material: no invented geometric-series bridge', async () => {
    await sleep(20_000);
    const reply = await ask(
      'האם היית ממליץ לי ללמוד עוד חומר מעבר לחומר המומלץ כרגע? אם כן, מה היית ממליץ?',
    );
    expect(reply.length).toBeGreaterThan(30);
    expect(
      scoreCommunicationReply(reply, ['no_fake_bridge', 'no_filler']).failures,
      reply,
    ).toEqual([]);
  }, 200_000);

  it('fake link ask: refuse/redirect away from geometric series proof', async () => {
    await sleep(20_000);
    const history = [
      { role: 'user' as const, content: 'האם ללמוד עוד חומר?' },
      {
        role: 'assistant' as const,
        content: 'אולי סדרות גאומטריות יעזרו לאינטגרלים.',
      },
    ];
    const reply = await ask('מה הקשר בין סדרות גיאומטריות לאינטגרלים', history);
    expect(reply.length).toBeGreaterThan(40);
    expect(scoreCommunicationReply(reply, ['no_filler']).failures, reply).toEqual([]);
    expect(reply).not.toMatch(/סדר(?:ה|ות)\s*ג[יא]ומטריות.{0,80}x\^?2/i);
  }, 200_000);

  it('simplify integral: correct 1/3 path, no wrong area=1', async () => {
    await sleep(20_000);
    const history = [
      { role: 'user' as const, content: 'תסביר סדרות גאומטריות לאינטגרלים' },
      {
        role: 'assistant' as const,
        content: 'סדרות גאומטריות עוזרות לחשב אינטגרל של x²…',
      },
    ];
    const reply = await ask(
      'תסביר לי איך לפתור את האינטגרל בצורה יותר פשוטה בבקשה',
      history,
    );
    expect(reply.length).toBeGreaterThan(40);
    expect(
      scoreCommunicationReply(reply, ['no_filler', 'no_wrong_area', 'has_correct_third'])
        .failures,
      reply,
    ).toEqual([]);
  }, 200_000);

  it('continue after cut-off: no explain-differently restart', async () => {
    await sleep(20_000);
    const history = [
      { role: 'user' as const, content: 'פתור ∫x² מ-0 עד 1 בשלבים' },
      {
        role: 'assistant' as const,
        content: 'שלב 1: כלל חזקה.\nשלב 2: קדומה x³/3.\nשלב 3: מציבים ב-',
      },
    ];
    const reply = await ask('המשך, התגובה שלך נעצרה באמצע', history);
    expect(reply.length).toBeGreaterThan(20);
    expect(scoreCommunicationReply(reply, ['no_filler']).failures, reply).toEqual([]);
  }, 200_000);
});
