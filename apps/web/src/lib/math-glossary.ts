export type GlossaryEntry = { he: string; en: string; ar: string };

export const MATH_GLOSSARY: Record<string, GlossaryEntry> = {
  'ממוצע': { he: 'ממוצע', en: 'Mean / Average', ar: 'المتوسط' },
  'חציון': { he: 'חציון', en: 'Median', ar: 'الوسيط' },
  'סטיית תקן': { he: 'סטיית תקן', en: 'Standard Deviation', ar: 'الانحراف المعياري' },
  'שונות': { he: 'שונות', en: 'Variance', ar: 'التباين' },
  'נגזרת': { he: 'נגזרת', en: 'Derivative', ar: 'المشتقة' },
  'אינטגרל': { he: 'אינטגרל', en: 'Integral', ar: 'التكامل' },
  'הסתברות': { he: 'הסתברות', en: 'Probability', ar: 'الاحتمال' },
  'משוואה': { he: 'משוואה', en: 'Equation', ar: 'المعادلة' },
  'פונקציה': { he: 'פונקציה', en: 'Function', ar: 'الدالة' },
  'גבול': { he: 'גבול', en: 'Limit', ar: 'النهاية' },
  'משתנה': { he: 'משתנה', en: 'Variable', ar: 'المتغير' },
  'מקדם': { he: 'מקדם', en: 'Coefficient', ar: 'المعامل' },
  'שיפוע': { he: 'שיפוע', en: 'Slope', ar: 'الميل' },
  'סדרה': { he: 'סדרה', en: 'Sequence', ar: 'المتتالية' },
  'טור': { he: 'טור', en: 'Series', ar: 'المتسلسلة' },
  'וקטור': { he: 'וקטור', en: 'Vector', ar: 'المتجه' },
  'מטריצה': { he: 'מטריצה', en: 'Matrix', ar: 'المصفوفة' },
  'תא': { he: 'תא', en: 'Cell', ar: 'الخلية' },
  'גרעין': { he: 'גרעין', en: 'Nucleus', ar: 'النواة' },
  'ברירה טבעית': { he: 'ברירה טבעית', en: 'Natural Selection', ar: 'الانتقاء الطبيعي' },
};

/** Flat array form of MATH_GLOSSARY — used by MathGlossaryPanel for table rendering. */
export const MATH_GLOSSARY_TERMS: GlossaryEntry[] = Object.values(MATH_GLOSSARY);
