export type GlossaryCategory = 'math';

export type GlossaryEntry = { he: string; en: string; category?: GlossaryCategory };

export const MATH_GLOSSARY: Record<string, GlossaryEntry> = {
  'ממוצע': { he: 'ממוצע', en: 'Mean / Average' },
  'חציון': { he: 'חציון', en: 'Median' },
  'סטיית תקן': { he: 'סטיית תקן', en: 'Standard Deviation' },
  'שונות': { he: 'שונות', en: 'Variance' },
  'נגזרת': { he: 'נגזרת', en: 'Derivative' },
  'אינטגרל': { he: 'אינטגרל', en: 'Integral' },
  'הסתברות': { he: 'הסתברות', en: 'Probability' },
  'הסתברות מותנית': { he: 'הסתברות מותנית', en: 'Conditional Probability' },
  'מרחב מדגם': { he: 'מרחב מדגם', en: 'Sample Space' },
  'אירועים בלתי תלויים': { he: 'אירועים בלתי תלויים', en: 'Independent Events' },
  'תמורות': { he: 'תמורות', en: 'Permutations' },
  'צירופים': { he: 'צירופים', en: 'Combinations' },
  'אינטגרציה בחלקים': { he: 'אינטגרציה בחלקים', en: 'Integration by Parts' },
  'נגזרת שרשרת': { he: 'נגזרת שרשרת', en: 'Chain Rule' },
  'משוואה': { he: 'משוואה', en: 'Equation' },
  'פונקציה': { he: 'פונקציה', en: 'Function' },
  'גבול': { he: 'גבול', en: 'Limit' },
  'משתנה': { he: 'משתנה', en: 'Variable' },
  'מקדם': { he: 'מקדם', en: 'Coefficient' },
  'שיפוע': { he: 'שיפוע', en: 'Slope' },
  'סדרה': { he: 'סדרה', en: 'Sequence' },
  'טור': { he: 'טור', en: 'Series' },
  'וקטור': { he: 'וקטור', en: 'Vector' },
  'מטריצה': { he: 'מטריצה', en: 'Matrix' },
};

/** Flat array form of MATH_GLOSSARY — used by MathGlossaryPanel for table rendering. */
export const MATH_GLOSSARY_TERMS: GlossaryEntry[] = Object.values(MATH_GLOSSARY);
