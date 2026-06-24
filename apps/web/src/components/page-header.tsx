'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';

export function PageHeader({
  title,
  description,
  backHref,
}: {
  title: string;
  description?: string;
  backHref?: string;
}) {
  const { messages } = useI18n();

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
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      {description ? <p className="text-muted-foreground">{description}</p> : null}
    </div>
  );
}
