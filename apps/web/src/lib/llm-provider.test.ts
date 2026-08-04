import { afterEach, describe, expect, it } from 'vitest';
import {
  getLLMConfig,
  getChatProviders,
  isReasoningModel,
  llmConfigured,
  resetLLMConfigCache,
  resolveModelChain,
  resolveChatModelChain,
  resolveProviderForModel,
  resolveSamplingBody,
} from './llm-provider';

describe('llm-provider config', () => {
  const env = process.env;

  afterEach(() => {
    process.env = { ...env };
    resetLLMConfigCache();
  });

  it('defaults to Groq when GROQ_API_KEY is set', () => {
    process.env.GROQ_API_KEY = 'test-key';
    delete process.env.LLM_API_KEY;
    delete process.env.LLM_BASE_URL;
    delete process.env.LLM_PRIMARY_MODEL;
    delete process.env.LLM_FALLBACK_MODELS;
    delete process.env.CHAT_MODEL_POLICY;
    resetLLMConfigCache();
    const cfg = getLLMConfig();
    expect(cfg.configured).toBe(true);
    expect(cfg.baseUrl).toContain('groq.com');
    expect(cfg.primaryModels[0]).toBe('llama-3.3-70b-versatile');
    expect(llmConfigured()).toBe(true);
  });

  it('supports Ollama without API key', () => {
    delete process.env.GROQ_API_KEY;
    delete process.env.LLM_API_KEY;
    process.env.LLM_BASE_URL = 'http://localhost:11434/v1';
    resetLLMConfigCache();
    const cfg = getLLMConfig();
    expect(cfg.configured).toBe(true);
    expect(cfg.providerLabel).toBe('ollama');
    expect(cfg.apiKey).toBe('ollama');
  });

  it('respects LLM_PRIMARY_MODEL and LLM_CHEAP_MODEL lists', () => {
    process.env.LLM_API_KEY = 'k';
    process.env.LLM_PRIMARY_MODEL = 'qwen2.5:32b,llama3.3:70b';
    process.env.LLM_CHEAP_MODEL = 'llama3.1:8b';
    resetLLMConfigCache();
    expect(resolveModelChain('primary')[0]).toBe('qwen2.5:32b');
    expect(resolveModelChain('cheap')[0]).toBe('llama3.1:8b');
  });

  it('prefers LLM_API_KEY over GROQ_API_KEY', () => {
    process.env.GROQ_API_KEY = 'groq-old';
    process.env.LLM_API_KEY = 'unified-key';
    process.env.LLM_BASE_URL = 'https://api.together.xyz/v1';
    resetLLMConfigCache();
    const cfg = getLLMConfig();
    expect(cfg.apiKey).toBe('unified-key');
    expect(cfg.baseUrl).toBe('https://api.together.xyz/v1');
  });

  it('resolveChatModelChain is quality-first by default', () => {
    process.env.LLM_API_KEY = 'k';
    process.env.LLM_CHEAP_MODEL = 'llama3.1:8b';
    process.env.LLM_PRIMARY_MODEL = 'qwen2.5:32b,llama3.3:70b';
    delete process.env.CHAT_MODEL_POLICY;
    resetLLMConfigCache();
    const chain = resolveChatModelChain();
    expect(chain[0]).toBe('qwen2.5:32b');
    expect(chain.length).toBeGreaterThan(1);
  });

  it('CHAT_MODEL_POLICY=cheap restores single cheap model', () => {
    process.env.LLM_API_KEY = 'k';
    process.env.LLM_CHEAP_MODEL = 'llama3.1:8b';
    process.env.LLM_PRIMARY_MODEL = 'qwen2.5:32b';
    process.env.CHAT_MODEL_POLICY = 'cheap';
    resetLLMConfigCache();
    expect(resolveChatModelChain()).toEqual(['llama3.1:8b']);
  });
});

describe('llm-provider multi-provider (NVIDIA fallback)', () => {
  const env = process.env;

  afterEach(() => {
    process.env = { ...env };
    resetLLMConfigCache();
  });

  function baseGroqEnv() {
    process.env.LLM_API_KEY = 'groq-key';
    process.env.LLM_BASE_URL = 'https://api.groq.com/openai/v1';
    process.env.LLM_PRIMARY_MODEL = 'llama-3.3-70b-versatile';
    process.env.LLM_CHEAP_MODEL = 'llama-3.1-8b-instant';
    delete process.env.LLM_FALLBACK_MODELS;
    delete process.env.CHAT_MODEL_POLICY;
  }

  it('only primary provider when NVIDIA env is absent', () => {
    baseGroqEnv();
    delete process.env.NVIDIA_API_KEY;
    delete process.env.NVIDIA_FALLBACK_MODELS;
    resetLLMConfigCache();
    const providers = getChatProviders();
    expect(providers).toHaveLength(1);
    expect(providers[0]!.label).toBe('groq');
  });

  it('appends NVIDIA provider + models when configured', () => {
    baseGroqEnv();
    process.env.NVIDIA_API_KEY = 'nvapi-xxx';
    process.env.NVIDIA_BASE_URL = 'https://integrate.api.nvidia.com/v1';
    process.env.NVIDIA_FALLBACK_MODELS =
      'meta/llama-3.3-70b-instruct,qwen/qwen2.5-72b-instruct';
    resetLLMConfigCache();

    const providers = getChatProviders();
    expect(providers).toHaveLength(2);
    expect(providers[1]!.label).toBe('nvidia');

    const chain = resolveChatModelChain();
    expect(chain).toContain('llama-3.3-70b-versatile');
    expect(chain).toContain('meta/llama-3.3-70b-instruct');
    expect(chain).toContain('qwen/qwen2.5-72b-instruct');
    // Primary model comes before the NVIDIA fallback.
    expect(chain.indexOf('llama-3.3-70b-versatile')).toBeLessThan(
      chain.indexOf('meta/llama-3.3-70b-instruct'),
    );
  });

  it('routes each model to the provider that lists it', () => {
    baseGroqEnv();
    process.env.NVIDIA_API_KEY = 'nvapi-xxx';
    process.env.NVIDIA_FALLBACK_MODELS = 'meta/llama-3.3-70b-instruct';
    resetLLMConfigCache();

    expect(resolveProviderForModel('llama-3.3-70b-versatile').label).toBe('groq');
    expect(resolveProviderForModel('meta/llama-3.3-70b-instruct').label).toBe('nvidia');
    // Unknown model falls back to the primary provider.
    expect(resolveProviderForModel('some-unknown-model').label).toBe('groq');
  });

  it('ignores NVIDIA when key present but no models listed', () => {
    baseGroqEnv();
    process.env.NVIDIA_API_KEY = 'nvapi-xxx';
    delete process.env.NVIDIA_FALLBACK_MODELS;
    resetLLMConfigCache();
    expect(getChatProviders()).toHaveLength(1);
  });
});

describe('isReasoningModel', () => {
  it('flags reasoning families', () => {
    expect(isReasoningModel('deepseek-r1')).toBe(true);
    expect(isReasoningModel('deepseek-ai/deepseek-r1')).toBe(true);
    expect(isReasoningModel('qwen/qwq-32b')).toBe(true);
    expect(isReasoningModel('qwen3-32b-thinking')).toBe(true);
  });

  it('does not flag standard instruct models', () => {
    expect(isReasoningModel('meta/llama-3.3-70b-instruct')).toBe(false);
    expect(isReasoningModel('qwen/qwen2.5-72b-instruct')).toBe(false);
    expect(isReasoningModel('llama-3.3-70b-versatile')).toBe(false);
  });
});

describe('resolveSamplingBody', () => {
  it('passes through per-agent temperature and top_p for standard models', () => {
    expect(
      resolveSamplingBody('meta/llama-3.3-70b-instruct', {
        messages: [],
        temperature: 0.2,
        topP: 0.9,
      }),
    ).toEqual({ temperature: 0.2, top_p: 0.9 });
  });

  it('omits top_p when undefined', () => {
    const body = resolveSamplingBody('llama-3.3-70b-versatile', {
      messages: [],
      temperature: 0.3,
    });
    expect(body).toEqual({ temperature: 0.3 });
    expect('top_p' in body).toBe(false);
  });

  it('defaults temperature to 0.4 when unset', () => {
    expect(resolveSamplingBody('llama-3.3-70b-versatile', { messages: [] })).toEqual({
      temperature: 0.4,
    });
  });

  it('clamps reasoning models regardless of requested sampling', () => {
    expect(
      resolveSamplingBody('deepseek-r1', {
        messages: [],
        temperature: 0.1,
        topP: 0.5,
      }),
    ).toEqual({ temperature: 0.6, top_p: 0.95 });
  });
});
