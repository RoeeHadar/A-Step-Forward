'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';

interface LessonCompleteButtonProps {
  conceptId: string;
  lessonId?: string;
  locale?: 'he' | 'en';
  className?: string;
  variant?: 'default' | 'outline' | 'gradient';
}

export function LessonCompleteButton({
  conceptId,
  lessonId,
  locale = 'he',
  className,
  variant = 'gradient',
}: LessonCompleteButtonProps) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const isHe = locale === 'he';

  async function handleComplete() {
    if (saving) return;
    setSaving(true);
    try {
      await fetch('/api/lessons/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept_id: conceptId,
          ...(lessonId ? { lesson_id: lessonId } : {}),
        }),
      });
    } catch {
      // Best-effort — still navigate so the learner is not blocked.
    } finally {
      router.push('/app?completed=1');
    }
  }

  const label = saving
    ? isHe
      ? 'שומר…'
      : 'Saving…'
    : isHe
      ? '✓ סיימתי את השיעור'
      : '✓ Mark lesson complete';

  if (variant === 'outline') {
    return (
      <Button
        type="button"
        variant="outline"
        disabled={saving}
        onClick={() => void handleComplete()}
        className={className}
      >
        {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
        {label}
      </Button>
    );
  }

  return (
    <button
      type="button"
      disabled={saving}
      onClick={() => void handleComplete()}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold transition-opacity disabled:opacity-70',
        variant === 'gradient'
          ? 'bg-gradient-to-r from-primary to-accent-magenta text-primary-foreground'
          : '',
        className,
      )}
    >
      {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
      {label}
    </button>
  );
}
