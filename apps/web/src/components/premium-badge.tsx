'use client';

import { cn } from '@asf/ui';

export function PremiumBadge({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex cursor-help items-center gap-1 rounded-full border border-accent-amber/40 bg-accent-amber/10 px-2 py-0.5 text-xs font-medium text-accent-amber',
        className,
      )}
      title="Currently free for all users — subscription coming soon."
    >
      ✨ Premium
    </span>
  );
}
