'use client';

import { useRouter } from 'next/navigation';
import { RefreshCw } from 'lucide-react';
import { PageHeader } from '@/components/page-header';
import { MemoryOverview } from '@/components/memory-overview';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';
import type { LearnerMemorySnapshot } from '@/lib/neon-db';

export function MemoryPageContent({ snapshot }: { snapshot: LearnerMemorySnapshot }) {
  const { messages, locale } = useI18n();
  const router = useRouter();
  const refreshLabel = locale === 'he' ? 'רענון' : 'Refresh';

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
      <MemoryOverview snapshot={snapshot} />
    </div>
  );
}
