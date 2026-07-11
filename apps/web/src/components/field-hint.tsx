'use client';

import type { ReactNode } from 'react';
import { HelpCircle } from 'lucide-react';
import { cn } from '@asf/ui';

interface FieldHintProps {
  text: string;
  className?: string;
  label?: string;
}

/** Hover/focus tooltip for ambiguous onboarding or form labels. */
export function FieldHint({ text, className, label }: FieldHintProps) {
  return (
    <span className={cn('group relative inline-flex align-middle', className)}>
      <button
        type="button"
        className="inline-flex h-4 w-4 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label={label ?? text}
      >
        <HelpCircle className="h-3.5 w-3.5" aria-hidden />
      </button>
      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-full z-50 mb-2 hidden w-56 rounded-lg border border-border bg-popover px-3 py-2 text-xs leading-relaxed text-popover-foreground shadow-md group-hover:block group-focus-within:block start-1/2 -translate-x-1/2"
      >
        {text}
      </span>
    </span>
  );
}

export function FieldLabel({
  children,
  hint,
  hintLabel,
  htmlFor,
  className,
}: {
  children: ReactNode;
  hint?: string;
  hintLabel?: string;
  htmlFor?: string;
  className?: string;
}) {
  return (
    <span className={cn('inline-flex items-center gap-1.5', className)}>
      {htmlFor ? (
        <label htmlFor={htmlFor} className="text-sm text-muted-foreground">
          {children}
        </label>
      ) : (
        <span className="text-sm text-muted-foreground">{children}</span>
      )}
      {hint ? <FieldHint text={hint} label={hintLabel} /> : null}
    </span>
  );
}
