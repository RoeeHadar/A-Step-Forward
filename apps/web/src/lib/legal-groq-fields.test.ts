import { describe, expect, it } from 'vitest';
import { LEGAL_DOCS } from './legal-content';

// AS-102: the privacy §4 Groq bullet must name every learner field the code sends
// to Groq (field table: items/AS-102/asf-coder.md). If a prompt starts sending a
// new field, add it to the bullet and to this list.
const FIELDS: Record<'he' | 'en', string[]> = {
  en: [
    'your messages', 'earlier conversation', 'goal', 'grade', 'math units', 'subjects',
    'learning style', 'weekly study hours', 'test and goal dates', 'test stress', 'motivation',
    'preferred study time', 'university or program', 'past experience with teachers',
    'summaries and notes', 'summaries of earlier chats', 'strong and weak topics', 'points and level',
    'study plan', 'lesson or exercise', 'answers you write', 'In the background',
    "We don't add your name, email or phone number",
  ],
  he: [
    'ההודעות שלכם', 'השיחה הקודמת', 'המטרה', 'הכיתה', 'יחידות המתמטיקה', 'המקצועות',
    'סגנון הלמידה', 'שעות הלימוד בשבוע', 'מועדי המבחנים והיעד', 'לחץ ממבחנים', 'מוטיבציה',
    'זמן הלימוד המועדף', 'המוסד או התוכנית', 'ניסיון קודם עם מורים',
    'הסיכומים וההערות', 'סיכומים של שיחות קודמות', 'נושאים חזקים וחלשים', 'נקודות ושלב',
    'תוכנית הלימוד', 'השיעור או התרגיל', 'התשובות שאתם כותבים', 'ברקע',
    'אנחנו לא מוסיפים לבקשות האלה את השם, האימייל או מספר הטלפון שלכם',
  ],
};

describe('privacy §4 Groq bullet (AS-102)', () => {
  it.each(['he', 'en'] as const)('%s lists every field sent to Groq', (locale) => {
    const bullet = LEGAL_DOCS.privacy[locale].body.split('\n').find((l) => l.startsWith('- Groq:'));
    expect(bullet).toBeDefined();
    const missing = FIELDS[locale].filter((f) => !bullet!.includes(f));
    expect(missing).toEqual([]);
  });
});
