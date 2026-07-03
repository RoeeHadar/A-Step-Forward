'use client';

import { useState } from 'react';
import { ClipboardCopy, Check, FileText } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { getPlanChangeTemplate } from '@/lib/plan-change-template';

type PlanChangeTemplateCopy = {
  title: string;
  badge: string;
  whyBody: string;
  howTitle: string;
  howSteps: readonly string[];
  note: string;
  copyLabel: string;
  useLabel: string;
  copiedLabel: string;
};

export function PlanChangeTemplatePanel({
  locale,
  onUseTemplate,
  className,
  copy,
}: {
  locale: 'he' | 'en';
  onUseTemplate: (text: string) => void;
  className?: string;
  copy: PlanChangeTemplateCopy;
}) {
  const [copied, setCopied] = useState(false);
  const template = getPlanChangeTemplate(locale);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(template);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2500);
    } catch {
      /* clipboard blocked — useTemplate still works */
    }
  }

  return (
    <div
      className={cn(
        'rounded-xl border border-primary/25 bg-primary/5 p-4 text-sm',
        className,
      )}
      dir={locale === 'he' ? 'rtl' : 'ltr'}
    >
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <FileText className="h-4 w-4 text-primary" aria-hidden />
        <span className="font-semibold text-foreground">{copy.title}</span>
        <span className="rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
          {copy.badge}
        </span>
      </div>

      <p className="mb-3 text-muted-foreground">{copy.whyBody}</p>

      <div className="mb-3 space-y-1">
        <p className="font-medium text-foreground">{copy.howTitle}</p>
        <ol className="list-decimal space-y-1 ps-5 text-muted-foreground">
          {copy.howSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </div>

      <pre
        className="mb-3 max-h-48 overflow-auto rounded-lg border border-border bg-surface-1/80 p-3 text-xs leading-relaxed whitespace-pre-wrap text-foreground"
        dir={locale === 'he' ? 'rtl' : 'ltr'}
      >
        {template}
      </pre>

      <p className="mb-3 text-xs text-accent-amber">{copy.note}</p>

      <div className="flex flex-wrap gap-2">
        <Button type="button" size="sm" variant="default" onClick={() => onUseTemplate(template)}>
          {copy.useLabel}
        </Button>
        <Button type="button" size="sm" variant="outline" onClick={() => void handleCopy()}>
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
  );
}
