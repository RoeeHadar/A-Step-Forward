import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { SiteHeader } from '@/components/site-header';

export default function LessonNotFound() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col items-center justify-center px-4 py-16 text-center">
        <h1 className="mb-2 text-3xl font-semibold tracking-tight">Lesson not found</h1>
        <p className="mb-6 text-muted-foreground">
          We couldn&rsquo;t find that lesson. It may have moved, or the link is mistyped.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Button asChild>
            <Link href="/lessons">Browse all lessons</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/">Back to home</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
