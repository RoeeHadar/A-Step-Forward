'use client';

import { Button } from '@asf/ui/button';

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const friendly =
    typeof error?.message === 'string' && error.message && !/\[object/i.test(error.message)
      ? error.message
      : 'Something went wrong while loading this page.';
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-6 text-center">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="max-w-md text-muted-foreground">{friendly}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
