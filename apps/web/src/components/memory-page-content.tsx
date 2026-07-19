'use client';

import { useRouter } from 'next/navigation';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '@/components/page-header';
import { MemoryOverview } from '@/components/memory-overview';
import { Button } from '@asf/ui/button';
import { usePageLiveRefresh } from '@/hooks/use-page-live-refresh';
import { useI18n } from '@/providers/i18n-provider';
import type { LearnerMemorySnapshot } from '@/lib/neon-db';

export function MemoryPageContent({ snapshot }: { snapshot: LearnerMemorySnapshot }) {
  const { messages, locale } = useI18n();
  const router = useRouter();
  usePageLiveRefresh(40_000);
  const refreshLabel = locale === 'he' ? 'רענון' : 'Refresh';

  const lastUpdatedText = snapshot.lastUpdated
    ? new Date(snapshot.lastUpdated).toLocaleString(locale === 'he' ? 'he-IL' : 'en-US', {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : null;
  const lastUpdatedLabel = locale === 'he' ? 'עודכן לאחרונה' : 'Last updated';
  const noMemoryYet = locale === 'he' ? 'עדיין אין זיכרונות שמורות' : 'No memories saved yet';

  return (
    <div>
      <PageHeader
        title={messages.memory.title}
        description={messages.memory.description}
        gradientTitle
        actions={
          <Button type="button" variant="outline" size="sm" onClick={() => router.refresh()}>
            <RefreshCw className="me-2 h-4 w-4" aria-hidden />
            {refreshLabel}
          </Button>
        }
      />
      <p className="mb-4 text-sm text-muted-foreground" aria-live="polite">
        {lastUpdatedText ? `${lastUpdatedLabel}: ${lastUpdatedText}` : noMemoryYet}
      </p>
      <MemoryOverview snapshot={snapshot} />
    </div>
  );
}
