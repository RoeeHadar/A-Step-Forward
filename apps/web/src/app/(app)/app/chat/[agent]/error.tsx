'use client';

import { Button } from '@asf/ui/button';
import { MessageCircleWarning } from 'lucide-react';

export default function ChatError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const friendly =
    typeof error?.message === 'string' && error.message && !/\[object/i.test(error.message)
      ? error.message
      : 'We could not load this chat session. Please try again.';

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-6 text-center">
      <MessageCircleWarning className="h-10 w-10 text-muted-foreground" aria-hidden />
      <h2 className="text-xl font-semibold">Could not load chat</h2>
      <p className="max-w-md text-muted-foreground">{friendly}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
