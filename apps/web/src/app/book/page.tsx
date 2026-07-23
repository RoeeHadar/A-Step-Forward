import { SiteHeader } from '@/components/site-header';
import { AmbientBackground } from '@/components/ambient-background';
import { BookLessonClient } from '@/components/book-lesson-client';

export const dynamic = 'force-dynamic';

export default function BookPage() {
  return (
    <div className="relative min-h-screen">
      <AmbientBackground />
      <SiteHeader />
      <main>
        <BookLessonClient />
      </main>
    </div>
  );
}
