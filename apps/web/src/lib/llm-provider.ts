/**
 * Unified OpenAI-compatible LLM provider for the Vercel web runtime.
 *
 * Supports Groq, Ollama, vLLM, Together, Fireworks, OpenRouter, etc. via:
 *   LLM_BASE_URL + LLM_API_KEY + LLM_PRIMARY_MODEL (+ optional LLM_CHEAP_MODEL)
 *
 * Backward compatible with GROQ_API_KEY / GROQ_BASE_URL.
 */
import 'server-only';
import { logger } from '@/lib/logger';

export type LLMModelTier = 'primary' | 'cheap' | 'all';

export interface LLMProviderConfig {
  configured: boolean;
  baseUrl: string;
  apiKey: string;
  primaryModels: string[];
  cheapModels: string[];
  providerLabel: string;
}

export interface LLMChatMessage {
  role: 'system' | 'user' | 'assistant' | string;
  content: string;
}

export interface LLMCompletionOptions {
  /** Prepended as the first system message when set. */
  system?: string;
  messages: LLMChatMessage[];
  maxTokens?: number;
  temperature?: number;
  jsonMode?: boolean;
  timeoutMs?: number;
  modelTier?: LLMModelTier;
  /** Override the model chain entirely. */
  models?: string[];
}

export interface LLMCompletionResult {
  content: string;
  model: string;
}

const DEFAULT_GROQ_BASE = 'https://api.groq.com/openai/v1';
const DEFAULT_PRIMARY = 'llama-3.3-70b-versatile';
const DEFAULT_CHEAP = 'llama-3.1-8b-instant';
const DEFAULT_EXTRA_PRIMARY = ['gemma2-9b-it'];

function trimSlash(url: string): string {
  return url.replace(/\/+$/, '');
}

function parseModelList(raw: string | undefined, fallback: string[]): string[] {
  if (!raw?.trim()) return fallback;
  const parts = raw
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  return parts.length ? parts : fallback;
}

function detectProviderLabel(baseUrl: string): string {
  const lower = baseUrl.toLowerCase();
  if (lower.includes('groq.com')) return 'groq';
  if (lower.includes('11434') || lower.includes('ollama')) return 'ollama';
  if (lower.includes('openrouter')) return 'openrouter';
  if (lower.includes('together')) return 'together';
  if (lower.includes('fireworks')) return 'fireworks';
  if (lower.includes('localhost') || lower.includes('127.0.0.1')) return 'local';
  return 'openai-compatible';
}

/** Resolve runtime LLM configuration from env (cached per process). */
let cachedConfig: LLMProviderConfig | null = null;

export function getLLMConfig(): LLMProviderConfig {
  if (cachedConfig) return cachedConfig;

  const baseUrl = trimSlash(
    process.env.LLM_BASE_URL?.trim() ||
      process.env.GROQ_BASE_URL?.trim() ||
      DEFAULT_GROQ_BASE,
  );

  const apiKey =
    process.env.LLM_API_KEY?.trim() ||
    process.env.GROQ_API_KEY?.trim() ||
    (detectProviderLabel(baseUrl) === 'ollama' ? 'ollama' : '');

  const primaryModels = parseModelList(process.env.LLM_PRIMARY_MODEL, [DEFAULT_PRIMARY]);
  const cheapModels = parseModelList(process.env.LLM_CHEAP_MODEL, [DEFAULT_CHEAP]);
  const fallbackModels = parseModelList(process.env.LLM_FALLBACK_MODELS, DEFAULT_EXTRA_PRIMARY);

  const allPrimary = [...new Set([...primaryModels, ...fallbackModels])];
  const configured = Boolean(apiKey) || detectProviderLabel(baseUrl) === 'ollama';

  cachedConfig = {
    configured,
    baseUrl,
    apiKey: apiKey || 'ollama',
    primaryModels: allPrimary,
    cheapModels,
    providerLabel: process.env.LLM_PROVIDER?.trim() || detectProviderLabel(baseUrl),
  };
  return cachedConfig;
}

/** Clear config cache (tests). */
export function resetLLMConfigCache(): void {
  cachedConfig = null;
}

export function llmConfigured(): boolean {
  return getLLMConfig().configured;
}

export function resolveModelChain(tier: LLMModelTier = 'primary'): string[] {
  const cfg = getLLMConfig();
  if (tier === 'cheap') return [...cfg.cheapModels, ...cfg.primaryModels];
  if (tier === 'all') return [...new Set([...cfg.primaryModels, ...cfg.cheapModels])];
  return [...cfg.primaryModels, ...cfg.cheapModels];
}

function buildMessages(opts: LLMCompletionOptions): LLMChatMessage[] {
  const out: LLMChatMessage[] = [];
  if (opts.system?.trim()) {
    out.push({ role: 'system', content: opts.system.trim() });
  }
  for (const m of opts.messages) {
    if (m.content?.trim()) out.push({ role: m.role, content: m.content });
  }
  return out;
}

function completionsUrl(baseUrl: string): string {
  return `${trimSlash(baseUrl)}/chat/completions`;
}

function isAuthFailure(status: number): boolean {
  return status === 401 || status === 403;
}

/**
 * Non-streaming chat completion. Tries models in order; returns null if all fail.
 */
export async function llmComplete(
  opts: LLMCompletionOptions,
): Promise<LLMCompletionResult | null> {
  const cfg = getLLMConfig();
  if (!cfg.configured) {
    logger.warn('llm: not configured — set LLM_API_KEY or LLM_BASE_URL (Ollama)');
    return null;
  }

  const models = opts.models ?? resolveModelChain(opts.modelTier ?? 'primary');
  const messages = buildMessages(opts);
  const timeoutMs = opts.timeoutMs ?? 45_000;

  for (const model of models) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const body: Record<string, unknown> = {
        model,
        messages,
        max_tokens: opts.maxTokens ?? 2048,
        temperature: opts.temperature ?? 0.4,
      };
      if (opts.jsonMode) {
        body.response_format = { type: 'json_object' };
      }

      const resp = await fetch(completionsUrl(cfg.baseUrl), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${cfg.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!resp.ok) {
        logger.warn('llm: completion non-ok', {
          status: resp.status,
          model,
          provider: cfg.providerLabel,
        });
        if (isAuthFailure(resp.status)) return null;
        continue;
      }

      const json = (await resp.json()) as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      const content = json.choices?.[0]?.message?.content;
      if (content?.trim()) {
        return { content, model };
      }
    } catch (err) {
      clearTimeout(timeoutId);
      logger.warn('llm: completion attempt failed', { model, err: String(err) });
    }
  }
  return null;
}

/**
 * Streaming chat completion (SSE). Yields text tokens; tries models in order.
 */
export async function* llmStream(
  opts: LLMCompletionOptions,
): AsyncGenerator<string> {
  const cfg = getLLMConfig();
  if (!cfg.configured) {
    logger.warn('llm: stream skipped — not configured');
    return;
  }

  const models = opts.models ?? resolveModelChain(opts.modelTier ?? 'primary');
  const messages = buildMessages(opts);
  const timeoutMs = opts.timeoutMs ?? 25_000;

  for (const model of models) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    let emitted = false;
    try {
      const resp = await fetch(completionsUrl(cfg.baseUrl), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${cfg.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages,
          max_tokens: opts.maxTokens ?? 1024,
          temperature: opts.temperature ?? 0.4,
          stream: true,
        }),
        signal: controller.signal,
      });

      if (!resp.ok || !resp.body) {
        clearTimeout(timeoutId);
        logger.warn('llm: stream non-ok', {
          status: resp.status,
          model,
          provider: cfg.providerLabel,
        });
        if (isAuthFailure(resp.status)) return;
        continue;
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const data = line.slice(6).trim();
          if (data === '[DONE]') break;
          try {
            const parsed = JSON.parse(data) as {
              choices?: Array<{ delta?: { content?: string } }>;
            };
            const token = parsed.choices?.[0]?.delta?.content;
            if (token) {
              emitted = true;
              yield token;
            }
          } catch {
            // ignore malformed SSE chunks
          }
        }
      }
      clearTimeout(timeoutId);
      if (emitted) return;
    } catch (err) {
      clearTimeout(timeoutId);
      logger.warn('llm: stream attempt failed', { model, err: String(err) });
    }
  }
}

/** Parse JSON object from an LLM completion (jsonMode). */
export async function llmCompleteJson<T extends Record<string, unknown>>(
  opts: LLMCompletionOptions,
): Promise<{ json: T; model: string } | null> {
  const result = await llmComplete({ ...opts, jsonMode: true });
  if (!result) return null;
  try {
    return { json: JSON.parse(result.content) as T, model: result.model };
  } catch {
    return null;
  }
}
