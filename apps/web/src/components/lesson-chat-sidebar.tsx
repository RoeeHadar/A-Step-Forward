'use client';

import { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import { AgentChat } from '@/components/agent-chat';
import { cn } from '@asf/ui';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import { resolveConceptTitles } from '@/lib/concept-display-names';

export function LessonChatSidebar({ conceptId }: { conceptId: string }) {
  const [open, setOpen] = useState(false);
  const [lang] = useLanguagePreference('he');
  const isHe = lang === 'he';
  const titles = resolveConceptTitles(conceptId);
  const topicLabel = isHe ? (titles.title_he ?? titles.title_en) : titles.title_en;

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={cn(
          'fixed bottom-6 z-40 flex items-center gap-2 rounded-full border border-primary/40',
          'bg-gradient-to-r from-primary to-accent-magenta px-4 py-3 text-sm font-semibold',
          'text-primary-foreground shadow-lg transition-transform hover:scale-[1.02]',
          isHe ? 'left-6' : 'right-6',
        )}
        aria-expanded={open}
      >
        <MessageCircle className="h-5 w-5" aria-hidden />
        {isHe ? 'שאל את המורה' : 'Ask the Tutor'}
      </button>

      {open ? (
        <div
          className={cn(
            'fixed inset-y-0 z-50 flex w-full max-w-md flex-col border-border bg-background shadow-2xl',
            isHe ? 'left-0 border-r' : 'right-0 border-l',
          )}
          role="dialog"
          aria-label={isHe ? 'צ׳אט עם המורה' : 'Tutor chat'}
        >
          <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-3">
            <div className="min-w-0">
              <p className="text-sm font-semibold">{isHe ? 'מורה AI' : 'AI Tutor'}</p>
              <p className="truncate text-xs text-muted-foreground">{topicLabel}</p>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
              aria-label={isHe ? 'סגור' : 'Close'}
            >
              <X className="h-5 w-5" />
            </button>
          </header>
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden p-3">
            <AgentChat agent="tutor" topic={conceptId} compact showHistory={false} />
          </div>
        </div>
      ) : null}
    </>
  );
}
