import { describe, expect, it } from 'vitest';
import { detectLang, formatChunksForPrompt, type RagChunk } from './rag-retrieve';

describe('detectLang', () => {
  it('detects Hebrew from any Hebrew character', () => {
    expect(detectLang('מה זה גבול של פונקציה?')).toBe('he');
    expect(detectLang('What is a limit? גבול')).toBe('he');
  });

  it('defaults to English for Latin/other scripts', () => {
    expect(detectLang('What is the derivative of sin(x)?')).toBe('en');
    expect(detectLang('12345 + f(x)')).toBe('en');
    expect(detectLang('')).toBe('en');
  });
});

describe('formatChunksForPrompt', () => {
  const chunks: RagChunk[] = [
    {
      id: 'lesson:limits:en:0',
      text: 'A limit describes the value a function approaches.',
      heading: 'Limits — Intro',
      sourceType: 'lesson',
      sourceDocId: 'limits',
      conceptId: 'limits',
      title: 'Limits',
      score: 0.5,
      channel: 'hybrid',
    },
  ];

  it('returns empty string with no chunks', () => {
    expect(formatChunksForPrompt([], 'en')).toBe('');
    expect(formatChunksForPrompt([], 'he')).toBe('');
  });

  it('numbers passages and includes a citable label', () => {
    const out = formatChunksForPrompt(chunks, 'en');
    expect(out).toContain('[1]');
    expect(out).toContain('Limits — Intro');
    expect(out).toContain('value a function approaches');
  });

  it('uses a Hebrew header for he', () => {
    const out = formatChunksForPrompt(chunks, 'he');
    expect(out).toContain('[1]');
    // Hebrew header contains the word "מקור" (source)
    expect(out).toMatch(/מקור/);
  });
});
