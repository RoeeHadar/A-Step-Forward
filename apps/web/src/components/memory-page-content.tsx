'use client';

import { PageHeader } from '@/components/page-header';
import { MemoryInspector } from '@/components/memory-inspector';
import { useI18n } from '@/providers/i18n-provider';
import type { MemoryRecord } from '@asf/schemas/memory';

export function MemoryPageContent({ memories }: { memories: MemoryRecord[] }) {
  const { messages } = useI18n();

  return (
    <div>
      <PageHeader
        title={messages.memory.title}
        description={messages.memory.description}
        gradientTitle
      />
      <MemoryInspector memories={memories} />
    </div>
  );
}
