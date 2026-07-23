'use client';

/**
 * KaTeX cheat sheet with live rendered examples for practice open answers.
 */

import { MarkdownMath } from '@/components/markdown-math';
import { useLanguagePreference } from '@/hooks/use-language-preference';

const ROWS: Array<{ he: string; en: string; syntax: string; render: string }> = [
  {
    he: 'עטוף מתמטיקה',
    en: 'Wrap math',
    syntax: '$x^2$ או $$\\frac{a}{b}$$',
    render: '$x^2$ · $$\\frac{a}{b}$$',
  },
  {
    he: 'חזקה / אינדקס',
    en: 'Power / subscript',
    syntax: '$x^{2}$, $a_{n}$',
    render: '$x^{2}$, $a_{n}$',
  },
  {
    he: 'שבר',
    en: 'Fraction',
    syntax: '$\\frac{a}{b}$',
    render: '$\\frac{a}{b}$',
  },
  {
    he: 'שורש',
    en: 'Square root',
    syntax: '$\\sqrt{x}$, $\\sqrt[3]{x}$',
    render: '$\\sqrt{x}$, $\\sqrt[3]{x}$',
  },
  {
    he: 'אינטגרל / סכום',
    en: 'Integral / sum',
    syntax: '$\\int_0^1 x\\,dx$',
    render: '$\\int_0^1 x\\,dx$',
  },
  {
    he: 'יוונית נפוצה',
    en: 'Greek',
    syntax: '$\\alpha$, $\\theta$, $\\pi$',
    render: '$\\alpha$, $\\theta$, $\\pi$',
  },
];

export function PracticeMathCheatSheet() {
  const [lang] = useLanguagePreference();
  const he = lang === 'he';

  return (
    <aside
      className="rounded-xl border border-border/60 bg-surface-1/40 p-4 text-sm lg:sticky lg:top-4"
      aria-label={he ? 'מדריך סימון מתמטי' : 'Math notation cheat sheet'}
    >
      <h2 className="mb-2 text-sm font-semibold text-foreground">
        {he ? 'איך לכתוב מתמטיקה' : 'How to type math'}
      </h2>
      <p className="mb-3 text-xs text-muted-foreground">
        {he
          ? 'רק $...$ או $$...$$. בלי עברית בתוך המתמטיקה. משמאל: תחביר · מימין: איך זה נראה.'
          : 'Use only $...$ or $$...$$. No Hebrew inside math. Left: syntax · right: rendered.'}
      </p>
      <ul className="space-y-3">
        {ROWS.map((row) => (
          <li key={row.en} className="space-y-1.5 border-b border-border/40 pb-3 last:border-0">
            <span className="text-xs font-medium text-foreground">
              {he ? row.he : row.en}
            </span>
            <div className="grid gap-2 sm:grid-cols-2">
              <code
                className="break-all rounded-md bg-surface-2/50 px-2 py-1.5 font-mono text-[11px] text-muted-foreground"
                dir="ltr"
              >
                {row.syntax}
              </code>
              <div
                className="rounded-md border border-border/50 bg-background/80 px-2 py-1.5 text-sm"
                dir="ltr"
              >
                <MarkdownMath>{row.render}</MarkdownMath>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </aside>
  );
}
