/**
 * Production-shaped live-model matrix for ADR-0015.
 *
 * Uses the same quality model policy, temperature, persona/skills, context
 * section budgeter, language resolver, and one-retry quality gate as chat.
 * It intentionally avoids Neon and never writes learner data.
 *
 * Run with an ephemeral provider key in the shell:
 *   pnpm --filter @asf/web exec vitest run src/lib/agent-chat-recovery.llm.integration.test.ts
 */
import { describe, expect, it } from 'vitest';
import { buildCompactAgentBaseline } from './agent-baseline';
import { getAgentPersona } from './agent-prompts';
import { assembleChatSystemPrompt } from './chat-context-builder';
import { buildContextNeeds } from './chat-context-needs';
import {
  languageInstructionBlock,
  resolveResponseLanguage,
  type ChatResponseLocale,
} from './chat-response-language';
import { qualityRepairInstruction, scoreResponseQuality } from './chat-response-quality';
import {
  getLLMConfig,
  llmComplete,
  llmConfigured,
  resetLLMConfigCache,
  resolveChatModelChain,
} from './llm-provider';
import type { WebLiveAgent } from './web-agents';

function liveProviderAvailable(): boolean {
  resetLLMConfigCache();
  if (!llmConfigured()) return false;
  try {
    return new URL(getLLMConfig().baseUrl).protocol.startsWith('http');
  } catch {
    return false;
  }
}

const LIVE = liveProviderAvailable();

async function productionShapedAnswer(agent: WebLiveAgent, message: string) {
  const locale: ChatResponseLocale = resolveResponseLanguage({
    message,
    profileLang: null,
    uiLocale: 'he',
  });
  const needs = buildContextNeeds({ agent, message });
  const core = [
    buildCompactAgentBaseline(),
    getAgentPersona(agent),
    languageInstructionBlock(locale),
    `## Context-needs fixture\n${JSON.stringify(needs)}`,
  ].join('\n\n');
  const { system } = assembleChatSystemPrompt(core, []);
  const models = resolveChatModelChain();

  const complete = (repair?: string) =>
    llmComplete({
      system: repair ? `${system}\n\n${repair}` : system,
      messages: [{ role: 'user', content: message }],
      maxTokens: 768,
      temperature: 0.4,
      timeoutMs: 60_000,
      models,
    });

  const first = await complete();
  let text = first?.content?.trim() ?? '';
  let score = scoreResponseQuality(text, locale);
  if (!score.ok) {
    const retried = await complete(qualityRepairInstruction(locale, score.failures));
    text = retried?.content?.trim() ?? '';
    score = scoreResponseQuality(text, locale);
  }
  return { text, score, locale, needs, selectedModels: models };
}

describe.skipIf(!LIVE)('ADR-0015 production-shaped all-agent live matrix', () => {
  const agents: WebLiveAgent[] = ['tutor', 'mentor', 'coach', 'reviewer'];

  for (const agent of agents) {
    it(`${agent}: context-free Hebrew arithmetic is direct and relevant`, async () => {
      const result = await productionShapedAnswer(
        agent,
        'מה החסר אם הממוצע של 5 מספרים הוא 10 וארבעה הם 8, 9, 11, 12?',
      );
      expect(result.selectedModels.length).toBeGreaterThan(0);
      expect(result.locale).toBe('he');
      expect(result.needs.statusPack).toBe(false);
      expect(result.score.ok, `${agent}: ${result.text}`).toBe(true);
      expect(result.text).toMatch(/10/);
      expect(result.text).not.toMatch(/AUTHORITATIVE|סה["״]?כ XP|הצעה להמשך/);
      expect(result.text).not.toMatch(/Sources:/i);
    }, 150_000);

    it(`${agent}: explicit English is respected`, async () => {
      const result = await productionShapedAnswer(
        agent,
        'Answer in English: what is the derivative of x squared?',
      );
      expect(result.locale).toBe('en');
      expect(result.score.ok, `${agent}: ${result.text}`).toBe(true);
      expect(result.text).toMatch(/2\s*\*?\s*x|2x|two x/i);
      expect(result.text).not.toMatch(/AUTHORITATIVE|סה["״]?כ XP/);
    }, 150_000);
  }
});
