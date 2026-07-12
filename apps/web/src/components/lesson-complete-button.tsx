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
  /** When false, stay on the page after a successful save (e.g. show 3pt motivation). */
  navigateOnComplete?: boolean;
  onComplete?: () => void;
}

export function LessonCompleteButton({
  conceptId,
  lessonId,
  locale = 'he',
  className,
  variant = 'gradient',
  navigateOnComplete = true,
  onComplete,
}: LessonCompleteButtonProps) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const isHe = locale === 'he';

  async function handleComplete() {
    if (saving || done) return;
    setSaving(true);
    setError(null);
    try {
      const controller = new AbortController();
      const timer = window.setTimeout(() => controller.abort(), 20_000);
      const res = await fetch('/api/lessons/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept_id: conceptId,
          ...(lessonId ? { lesson_id: lessonId } : {}),
        }),
        signal: controller.signal,
      });
      window.clearTimeout(timer);

      if (!res.ok) {
        const payload = (await res.json().catch(() => null)) as { error?: string } | null;
        throw new Error(payload?.error ?? `HTTP ${res.status}`);
      }

      setDone(true);
      onComplete?.();
      if (navigateOnComplete) {
        router.push('/app?completed=1');
        router.refresh();
      } else {
        router.refresh();
      }
    } catch (err) {
      console.warn('[LessonCompleteButton] save failed', err);
      setError(
        isHe
          ? 'לא הצלחנו לסמן את השיעור כהושלם. נסה/י שוב.'
          : 'Could not mark the lesson complete. Please try again.',
      );
    } finally {
      setSaving(false);
    }
  }

  const label = saving
    ? isHe
      ? 'שומר…'
      : 'Saving…'
    : done
      ? isHe
        ? '✓ השיעור הושלם'
        : '✓ Lesson complete'
      : isHe
        ? '✓ סיימתי את השיעור'
        : '✓ Mark lesson complete';

  const content = (
    <>
      {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
      {label}
    </>
  );

  return (
    <div className="flex flex-col gap-2">
      {variant === 'outline' ? (
        <Button
          type="button"
          variant="outline"
          disabled={saving || done}
          onClick={() => void handleComplete()}
          className={className}
        >
          {content}
        </Button>
      ) : (
        <button
          type="button"
          disabled={saving || done}
          onClick={() => void handleComplete()}
          className={cn(
            'inline-flex items-center justify-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold transition-opacity disabled:opacity-70',
            variant === 'gradient'
              ? 'bg-gradient-to-r from-primary to-accent-magenta text-primary-foreground'
              : '',
            className,
          )}
        >
          {content}
        </button>
      )}
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
