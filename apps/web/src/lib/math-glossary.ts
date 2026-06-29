export type GlossaryEntry = { he: string; en: string; ar: string };

export const MATH_GLOSSARY: Record<string, GlossaryEntry> = {
  'ממוצע': { he: 'ממוצע', en: 'Mean / Average', ar: 'المتوسط' },
  'חציון': { he: 'חציון', en: 'Median', ar: 'الوسيط' },
  'סטיית תקן': { he: 'סטיית תקן', en: 'Standard Deviation', ar: 'الانحراف المعياري' },
  'שונות': { he: 'שונות', en: 'Variance', ar: 'التباين' },
  'נגזרת': { he: 'נגזרת', en: 'Derivative', ar: 'المشتقة' },
  'אינטגרל': { he: 'אינטגרל', en: 'Integral', ar: 'التكامل' },
  'הסתברות': { he: 'הסתברות', en: 'Probability', ar: 'الاحتمال' },
  'הסתברות מותנת': { he: 'הסתברות מותנת', en: 'Conditional Probability', ar: 'الاحتمال الشرطي' },
  'מרחב מדגם': { he: 'מרחב מדגם', en: 'Sample Space', ar: 'فضاء العينة' },
  'אירועים בלתי תלויים': { he: 'אירועים בלתי תלויים', en: 'Independent Events', ar: 'أحداث مستقلة' },
  'תמורות': { he: 'תמורות', en: 'Permutations', ar: 'التباديل' },
  'צירופים': { he: 'צירופים', en: 'Combinations', ar: 'التوافيق' },
  'אינטגרציה בחלקים': { he: 'אינטגרציה בחלקים', en: 'Integration by Parts', ar: 'التكامل بالأجزاء' },
  'נגזרת שרשרת': { he: 'נגזרת שרשרת', en: 'Chain Rule', ar: 'قاعدة السلسلة' },
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
  'תורשה': { he: 'תורשה', en: 'Heredity', ar: 'الوراثة' },
  'ברירה טבעית': { he: 'ברירה טבעית', en: 'Natural Selection', ar: 'الانتقاء الطبيعي' },
  'אלל': { he: 'אלל', en: 'Allele', ar: 'الأليل' },
};

/** Flat array form of MATH_GLOSSARY — used by MathGlossaryPanel for table rendering. */
export const MATH_GLOSSARY_TERMS: GlossaryEntry[] = Object.values(MATH_GLOSSARY);
