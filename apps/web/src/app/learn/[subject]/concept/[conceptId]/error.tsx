'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Button } from '@asf/ui/button';

/**
 * Backstop for lesson pages: if a lesson fails to render (e.g. malformed
 * authored data), show a recoverable message instead of a bare 500 page.
 */
export default function LessonError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const params = useParams<{ subject?: string }>();
  const subject = typeof params?.subject === 'string' ? params.subject : '';
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-6 text-center">
      <h2 className="text-xl font-semibold">
        <span lang="he" dir="rtl">משהו השתבש בטעינת השיעור</span>
        <br />
        <span lang="en" dir="ltr">Something went wrong loading this lesson</span>
      </h2>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Button onClick={reset}>
          <span lang="he">נסו שוב</span> / <span lang="en">Try again</span>
        </Button>
        <Link className="underline" href={subject ? `/learn/${encodeURIComponent(subject)}` : '/learn'}>
          <span lang="he">חזרה לקורס</span> / <span lang="en">Back to the course</span>
        </Link>
      </div>
    </div>
  );
}
