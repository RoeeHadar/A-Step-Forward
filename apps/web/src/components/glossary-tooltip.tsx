'use client';

import { MATH_GLOSSARY } from '@/lib/math-glossary';

interface GlossaryTooltipProps {
  term: string;
  children: React.ReactNode;
}

/**
 * Wraps a Hebrew math/science term with a hover tooltip showing the Arabic and
 * English translations. Falls back to rendering children unchanged if the term
 * is not in the glossary.
 *
 * Usage: <GlossaryTooltip term="ממוצע">ממוצע</GlossaryTooltip>
 */
export function GlossaryTooltip({ term, children }: GlossaryTooltipProps) {
  const entry = MATH_GLOSSARY[term];
  if (!entry) return <>{children}</>;

  return (
    <span
      className="relative inline-block cursor-help underline decoration-dotted decoration-muted-foreground/50 group"
      aria-label={`${entry.ar} · ${entry.en}`}
    >
      {children}
      <span
        className={[
          'pointer-events-none absolute bottom-full left-1/2 z-50 mb-1.5',
          '-translate-x-1/2 whitespace-nowrap rounded-md border border-border',
          'bg-popover px-2.5 py-1 text-xs text-popover-foreground shadow-md',
          'opacity-0 transition-opacity group-hover:opacity-100',
        ].join(' ')}
        role="tooltip"
      >
        <span dir="rtl" className="font-medium">{entry.ar}</span>
        <span className="mx-1.5 text-muted-foreground">·</span>
        <span>{entry.en}</span>
      </span>
    </span>
  );
}
