'use client';

import { PageHeader } from '@/components/page-header';
import { ProgressDashboard } from '@/components/progress-dashboard';
import { useI18n } from '@/providers/i18n-provider';
import type { LearnerProgress } from '@asf/schemas/progress';

export function ProgressPageContent({ progress }: { progress: LearnerProgress }) {
  const { messages } = useI18n();

  return (
    <div>
      <PageHeader
        title={messages.progress.title}
        description={messages.progress.description}
        gradientTitle
      />
      <ProgressDashboard progress={progress} />
    </div>
  );
}
