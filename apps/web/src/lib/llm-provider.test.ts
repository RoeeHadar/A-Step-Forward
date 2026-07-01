import { afterEach, describe, expect, it } from 'vitest';
import {
  getLLMConfig,
  llmConfigured,
  resetLLMConfigCache,
  resolveModelChain,
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
});
