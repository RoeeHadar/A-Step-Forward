'use client';

import { subjectLabel } from '@/lib/subject-labels';
import { useI18n } from '@/providers/i18n-provider';

/** Subject title that follows the live locale toggle (not just SSR cookie). */
export function LocalizedSubjectLabel({ subject }: { subject: string }) {
  const { locale } = useI18n();
  return subjectLabel(subject, locale);
}