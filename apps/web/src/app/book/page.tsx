import { SiteHeader } from '@/components/site-header';
import { AmbientBackground } from '@/components/ambient-background';
import { BookLessonClient } from '@/components/book-lesson-client';
import { getAuthContext } from '@/lib/auth';
import type { Metadata } from 'next';
import { absoluteUrl } from '@/lib/site-url';
import { pageOpenGraph } from '@/lib/site-metadata';

export function generateMetadata(): Metadata {
  const url = absoluteUrl('/book');
  return { alternates: { canonical: url }, openGraph: pageOpenGraph({ url }) };
}

export const dynamic = 'force-dynamic';

export default async function BookPage() {
  const auth = await getAuthContext();
  const isAdmin = auth?.role === 'admin';

  return (
    <div className="relative min-h-screen">
      <AmbientBackground />
      <SiteHeader />
      <main>
        <BookLessonClient isAdmin={isAdmin} />
      </main>
    </div>
  );
}
