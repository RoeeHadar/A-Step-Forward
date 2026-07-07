import { describe, expect, it } from 'vitest';
import { looksEnglish, looksHebrew, pickLessonText } from './lesson-locale';

describe('lesson-locale', () => {
  it('prefers Hebrew script in Hebrew mode', () => {
    const he = 'זהו טקסט בעברית עם מספיק אותיות עבריות';
    const en = 'This is English text with enough letters';
    expect(pickLessonText('he', he, en)).toBe(he);
  });

  it('falls back when Hebrew field is empty', () => {
    expect(pickLessonText('he', '', 'English fallback')).toBe('English fallback');
  });

  it('detects English pasted into Hebrew field', () => {
    const heWrong = 'This section was mistakenly stored in body_he';
    const heReal = 'זהו הסבר בעברית על נגזרות ואינטגרלים';
    expect(looksEnglish(heWrong)).toBe(true);
    expect(looksHebrew(heReal)).toBe(true);
    expect(pickLessonText('he', heWrong, heReal)).toBe(heReal);
  });

  it('prefers English script in English mode', () => {
    const he = 'זהו טקסט בעברית עם מספיק אותיות עבריות';
    const en = 'This is English text with enough letters';
    expect(pickLessonText('en', he, en)).toBe(en);
  });

  it('detects Hebrew pasted into English title field', () => {
    const enWrong = 'כותרת שגויה באנגלית אבל בעברית';
    const enReal = 'Correct English lesson title here';
    expect(pickLessonText('en', enWrong, enReal)).toBe(enReal);
  });
});
