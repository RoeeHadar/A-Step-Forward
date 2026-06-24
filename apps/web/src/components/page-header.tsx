'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';

export function PageHeader({
  title,
  description,
  backHref,
  gradientTitle,
}: {
  title: string;
  description?: string;
  backHref?: string;
  gradientTitle?: boolean;
}) {
  const { messages } = useI18n();

  const words = title.split(' ');
  const firstWord = words[0] ?? title;
  const rest = words.slice(1).join(' ');

  return (
    <div className="mb-8 flex flex-col gap-2">
      {backHref ? (
        <Button variant="ghost" size="sm" className="w-fit px-0" asChild>
          <Link href={backHref}>
            <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
            {messages.common.back}
          </Link>
        </Button>
      ) : null}
      <h1 className="font-display text-3xl font-semibold tracking-tight">
        {gradientTitle && words.length > 1 ? (
          <>
            <span className="bg-gradient-to-r from-primary via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
              {firstWord}
            </span>
            {rest ? ` ${rest}` : null}
          </>
        ) : gradientTitle ? (
          <span className="bg-gradient-to-r from-primary via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
            {title}
          </span>
        ) : (
          title
        )}
      </h1>
      {description ? <p className="text-muted-foreground">{description}</p> : null}
    </div>
  );
}
