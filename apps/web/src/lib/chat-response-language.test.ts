import { describe, expect, it } from 'vitest';
import {
  detectExplicitLanguageRequest,
  detectMessageLanguage,
  languageInstructionBlock,
  resolveResponseLanguage,
} from './chat-response-language';

describe('chat-response-language (ADR-0015)', () => {
  it('detects Hebrew vs English messages', () => {
    expect(detectMessageLanguage('מה החסר בממוצע?')).toBe('he');
    expect(detectMessageLanguage('What is the average?')).toBe('en');
    expect(detectMessageLanguage('123')).toBeNull();
  });

  it('detects explicit language requests', () => {
    expect(detectExplicitLanguageRequest('answer in english please')).toBe('en');
    expect(detectExplicitLanguageRequest('תענה בעברית')).toBe('he');
  });

  it('precedence: explicit > message > profile > UI', () => {
    expect(
      resolveResponseLanguage({
        message: 'תענה באנגלית מה זה נגזרת',
        profileLang: 'he',
        uiLocale: 'he',
      }),
    ).toBe('en');

    expect(
      resolveResponseLanguage({
        message: 'What is a derivative?',
        recentUserMessages: ['תענה בעברית'],
        profileLang: 'he',
        uiLocale: 'he',
      }),
    ).toBe('en');

    expect(
      resolveResponseLanguage({
        message: 'ok',
        recentUserMessages: ['מה לומדים הלאה'],
        profileLang: 'en',
        uiLocale: 'en',
      }),
    ).toBe('he');

    expect(
      resolveResponseLanguage({
        message: '?',
        profileLang: 'en',
        uiLocale: 'he',
      }),
    ).toBe('en');

    expect(
      resolveResponseLanguage({
        message: '?',
        profileLang: null,
        uiLocale: 'he',
      }),
    ).toBe('he');
  });

  it('languageInstructionBlock mentions resolved language', () => {
    expect(languageInstructionBlock('he')).toContain('Hebrew');
    expect(languageInstructionBlock('en')).toContain('English');
  });
});
