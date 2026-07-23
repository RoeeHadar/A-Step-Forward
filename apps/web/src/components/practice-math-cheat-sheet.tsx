'use client';

/**
 * Compact KaTeX cheat sheet for practice open answers (ADR-0013 v2).
 */

import { useLanguagePreference } from '@/hooks/use-language-preference';

const ROWS: Array<{ he: string; en: string; example: string }> = [
  { he: 'עטוף מתמטיקה', en: 'Wrap math', example: '$x^2$ או $$\\frac{a}{b}$$' },
  { he: 'חזקה / אינדקס', en: 'Power / subscript', example: '$x^{2}$, $a_{n}$' },
  { he: 'שבר', en: 'Fraction', example: '$\\frac{a}{b}$' },
  { he: 'שורש', en: 'Square root', example: '$\\sqrt{x}$, $\\sqrt[3]{x}$' },
  { he: 'אינטגרל / סכום', en: 'Integral / sum', example: '$\\int_0^1 x\\,dx$, $\\sum_{n=1}^{n}$' },
  { he: 'יוונית נפוצה', en: 'Greek', example: '$\\alpha$, $\\theta$, $\\pi$' },
];

export function PracticeMathCheatSheet() {
  const [lang] = useLanguagePreference();
  const he = lang === 'he';

  return (
    <aside
      className="rounded-xl border border-border/60 bg-surface-1/40 p-4 text-sm"
      aria-label={he ? 'מדריך סימון מתמטי' : 'Math notation cheat sheet'}
    >
      <h2 className="mb-2 text-sm font-semibold text-foreground">
        {he ? 'איך לכתוב מתמטיקה' : 'How to type math'}
      </h2>
      <p className="mb-3 text-xs text-muted-foreground">
        {he
          ? 'רק $...$ או $$...$$. בלי עברית בתוך המתמטיקה.'
          : 'Use only $...$ or $$...$$. No Hebrew inside math.'}
      </p>
      <ul className="space-y-2">
        {ROWS.map((row) => (
          <li key={row.en} className="grid gap-0.5 border-b border-border/40 pb-2 last:border-0">
            <span className="text-xs font-medium text-foreground">
              {he ? row.he : row.en}
            </span>
            <code className="break-all font-mono text-[11px] text-muted-foreground" dir="ltr">
              {row.example}
            </code>
          </li>
        ))}
      </ul>
    </aside>
  );
}
