'use client';

import type { ReactNode } from 'react';
import { MATH_GLOSSARY } from '@/lib/math-glossary';

export function GlossaryTooltip({
  term,
  children,
}: {
  term: string;
  children: ReactNode;
}) {
  const entry = MATH_GLOSSARY[term];
  if (!entry) {
    return <>{children}</>;
  }

  return (
    <span className="group relative inline cursor-help border-b border-dotted border-primary/40">
      {children}
      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-1.5 hidden w-max max-w-xs -translate-x-1/2 rounded-md border border-border bg-popover px-2.5 py-1.5 text-xs text-popover-foreground shadow-md group-hover:block"
        dir="ltr"
      >
        {entry.ar} · {entry.en}
      </span>
    </span>
  );
}