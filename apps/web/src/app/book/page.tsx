import { SiteHeader } from '@/components/site-header';
import { AmbientBackground } from '@/components/ambient-background';
import { BookLessonClient } from '@/components/book-lesson-client';
import { getAuthContext } from '@/lib/auth';

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
