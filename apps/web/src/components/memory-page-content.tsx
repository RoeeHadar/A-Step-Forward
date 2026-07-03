'use client';

import { PageHeader } from '@/components/page-header';
import { MemoryOverview } from '@/components/memory-overview';
import { useI18n } from '@/providers/i18n-provider';
import type { LearnerMemorySnapshot } from '@/lib/neon-db';

export function MemoryPageContent({ snapshot }: { snapshot: LearnerMemorySnapshot }) {
  const { messages } = useI18n();

  return (
    <div>
      <PageHeader
        title={messages.memory.title}
        description={messages.memory.description}
        gradientTitle
      />
      <MemoryOverview snapshot={snapshot} />
    </div>
  );
}
