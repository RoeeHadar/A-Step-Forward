'use client';

import { useState } from 'react';
import { ClipboardCopy, Check, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import {
  getPlanChangeDisplayTemplate,
  getPlanChangeGuidedOpener,
  wrapPlanChangeMessage,
} from '@/lib/plan-change-template';

type PlanChangeTemplateCopy = {
  title: string;
  badge: string;
  whyBody: string;
  howTitle: string;
  howSteps: readonly string[];
  memoryNote: string;
  guidedLabel: string;
  guidedHint: string;
  copyLabel: string;
  useLabel: string;
  copiedLabel: string;
  collapseLabel: string;
  expandLabel: string;
};

export function PlanChangeTemplatePanel({
  locale,
  onUseTemplate,
  className,
  copy,
  variant = 'sidebar',
}: {
  locale: 'he' | 'en';
  onUseTemplate: (text: string) => void;
  className?: string;
  copy: PlanChangeTemplateCopy;
  variant?: 'sidebar' | 'inline';
}) {
  const [copied, setCopied] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const displayTemplate = getPlanChangeDisplayTemplate(locale);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(displayTemplate);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2500);
    } catch {
      /* clipboard blocked */
    }
  }

  function handleUse() {
    onUseTemplate(wrapPlanChangeMessage(displayTemplate));
  }

  function handleStartGuided() {
    onUseTemplate(getPlanChangeGuidedOpener(locale));
  }

  if (collapsed && variant === 'sidebar') {
    return (
      <aside
        className={cn(
          'hidden shrink-0 lg:flex lg:w-52 xl:w-60 flex-col',
          className,
        )}
        dir={locale === 'he' ? 'rtl' : 'ltr'}
      >
        <button
          type="button"
          onClick={() => setCollapsed(false)}
          className="glass-surface flex items-center gap-2 rounded-xl border border-primary/25 px-3 py-2 text-sm font-medium text-primary hover:bg-primary/5"
        >
          <FileText className="h-4 w-4" aria-hidden />
          {copy.expandLabel}
          <ChevronDown className="ms-auto h-4 w-4" aria-hidden />
        </button>
      </aside>
    );
  }

  return (
    <aside
      className={cn(
        variant === 'sidebar'
          ? 'hidden shrink-0 lg:flex lg:w-52 xl:w-60 flex-col'
          : 'w-full',
        className,
      )}
      dir={locale === 'he' ? 'rtl' : 'ltr'}
      aria-label={copy.title}
    >
      <div
        className={cn(
          'flex flex-col rounded-xl border border-primary/25 bg-primary/5 text-sm',
          variant === 'sidebar' ? 'sticky top-4 max-h-[calc(100vh-10rem)] overflow-y-auto p-3' : 'p-4',
        )}
      >
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <FileText className="h-4 w-4 shrink-0 text-primary" aria-hidden />
          <span className="font-semibold text-foreground">{copy.title}</span>
          {variant === 'sidebar' ? (
            <button
              type="button"
              onClick={() => setCollapsed(true)}
              className="ms-auto rounded p-0.5 text-muted-foreground hover:text-foreground"
              aria-label={copy.collapseLabel}
            >
              <ChevronUp className="h-4 w-4" />
            </button>
          ) : (
            <span className="rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
              {copy.badge}
            </span>
          )}
        </div>

        <p className="mb-2 text-xs leading-relaxed text-muted-foreground">{copy.whyBody}</p>

        <div className="mb-2 space-y-1">
          <p className="text-xs font-medium text-foreground">{copy.howTitle}</p>
          <ol className="list-decimal space-y-0.5 ps-4 text-xs text-muted-foreground">
            {copy.howSteps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>

        <div
          className="mb-2 rounded-lg border border-border bg-surface-1/80 p-2.5 text-xs leading-relaxed whitespace-pre-wrap text-foreground"
        >
          {displayTemplate}
        </div>

        <p className="mb-2 text-xs text-muted-foreground">{copy.memoryNote}</p>

        <div className="mt-auto flex flex-col gap-1.5 pt-1">
          <Button
            type="button"
            size="sm"
            variant="default"
            className="w-full"
            onClick={handleStartGuided}
          >
            {copy.guidedLabel}
          </Button>
          <p className="text-[11px] leading-snug text-muted-foreground">{copy.guidedHint}</p>
          <Button type="button" size="sm" variant="outline" className="w-full" onClick={handleUse}>
            {copy.useLabel}
          </Button>
          <Button type="button" size="sm" variant="ghost" className="w-full" onClick={() => void handleCopy()}>
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5" aria-hidden />
                {copy.copiedLabel}
              </>
            ) : (
              <>
                <ClipboardCopy className="h-3.5 w-3.5" aria-hidden />
                {copy.copyLabel}
              </>
            )}
          </Button>
        </div>
      </div>
    </aside>
  );
}
