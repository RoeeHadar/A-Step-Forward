'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';

export function PageHeader({
  title,
  description,
  backHref,
  gradientTitle,
  eyebrow,
  icon,
  actions,
}: {
  title: string;
  description?: string;
  backHref?: string;
  gradientTitle?: boolean;
  /** Small kicker label above the title (e.g. section name). */
  eyebrow?: string;
  /** Optional leading icon, rendered in a tokenized surface tile. */
  icon?: ReactNode;
  /** Optional trailing controls (buttons, filters) aligned to the row end. */
  actions?: ReactNode;
}) {
  const { messages } = useI18n();

  const words = title.split(' ');
  const firstWord = words[0] ?? title;
  const rest = words.slice(1).join(' ');

  return (
    <div className="mb-8">
      {backHref ? (
        <Button variant="ghost" size="sm" className="mb-2 w-fit px-0" asChild>
          <Link href={backHref}>
            <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
            {messages.common.back}
          </Link>
        </Button>
      ) : null}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex items-start gap-4">
          {icon ? (
            <span
              className="mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border bg-surface-1 text-primary shadow-sm [&>svg]:h-5 [&>svg]:w-5"
              aria-hidden
            >
              {icon}
            </span>
          ) : null}

          <div className="flex flex-col gap-1.5">
            {eyebrow ? (
              <span className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" aria-hidden />
                {eyebrow}
              </span>
            ) : null}

            <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              {gradientTitle && words.length > 1 ? (
                <>
                  <span className="text-primary">{firstWord}</span>
                  {rest ? ` ${rest}` : null}
                </>
              ) : gradientTitle ? (
                <span className="text-primary">{title}</span>
              ) : (
                title
              )}
            </h1>

            {description ? (
              <p className="max-w-2xl text-pretty leading-relaxed text-muted-foreground">
                {description}
              </p>
            ) : null}
          </div>
        </div>

        {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
      </div>

      <div
        className="mt-6 h-px w-full bg-gradient-to-r from-border-bright/80 via-border to-transparent rtl:bg-gradient-to-l"
        aria-hidden
      />
    </div>
  );
}
