import type { Metadata } from 'next';
import { LegalPage, legalTitle } from '@/components/legal-page';
import { getServerLocale } from '@/i18n/locale-server';

export const dynamic = 'force-dynamic';

export async function generateMetadata(): Promise<Metadata> {
  return { title: legalTitle('accessibility', await getServerLocale()) };
}

export default function Page() {
  return <LegalPage id="accessibility" />;
}
