'use client';

import { useEffect, useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import { AgentChat } from '@/components/agent-chat';
import { cn } from '@asf/ui';
import { agentAccentVars } from '@/lib/design-tokens';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import { useChatUiStore } from '@/stores/ui-store';
import {
  WEB_LIVE_AGENTS,
  WEB_LIVE_AGENT_BLURBS,
  WEB_LIVE_AGENT_NAMES,
  resolveWebChatAgent,
  type WebLiveAgent,
} from '@/lib/web-agents';
import { resolveConceptTitles } from '@/lib/concept-display-names';
import type { PracticeChatContext } from '@/lib/practice-arena';

export interface AgentSidePanelProps {
  /** Primary concept id passed to chat context. */
  topic?: string;
  topicLabel?: string;
  defaultAgent?: WebLiveAgent;
  fabLabel?: { he: string; en: string };
  /** When set (practice arena), binds Coach to the current sealed item. */
  practiceContext?: PracticeChatContext | null;
}

export function AgentSidePanel({
  topic,
  topicLabel,
  defaultAgent = 'tutor',
  fabLabel,
  practiceContext = null,
}: AgentSidePanelProps) {
  const [open, setOpen] = useState(false);
  const [lang] = useLanguagePreference('he');
  const isHe = lang === 'he';
  const lastAgent = useChatUiStore((s) => s.lastAgent);
  const setLastAgent = useChatUiStore((s) => s.setLastAgent);
  const effectiveDefault = practiceContext ? 'coach' : defaultAgent;
  const [agent, setAgent] = useState<WebLiveAgent>(() =>
    resolveWebChatAgent(
      WEB_LIVE_AGENTS.includes(lastAgent as WebLiveAgent)
        ? lastAgent
        : effectiveDefault,
    ),
  );

  useEffect(() => {
    if (practiceContext) {
      setAgent('coach');
      return;
    }
    const resolved = resolveWebChatAgent(
      WEB_LIVE_AGENTS.includes(lastAgent as WebLiveAgent)
        ? lastAgent
        : effectiveDefault,
    );
    setAgent(resolved);
  }, [lastAgent, effectiveDefault, practiceContext]);

  const studyTopic = practiceContext?.concept_id ?? topic;

  const resolvedTopicLabel =
    topicLabel ??
    (studyTopic
      ? (isHe
          ? (resolveConceptTitles(studyTopic).title_he ??
            resolveConceptTitles(studyTopic).title_en)
          : resolveConceptTitles(studyTopic).title_en)
      : isHe
        ? 'למידה'
        : 'Learning');

  const fabText =
    fabLabel?.[isHe ? 'he' : 'en'] ??
    (practiceContext
      ? isHe
        ? 'עזרה ממאמן'
        : 'Ask Coach'
      : isHe
        ? 'שאל את הסוכן'
        : 'Ask an agent');

  function selectAgent(next: WebLiveAgent) {
    setAgent(next);
    setLastAgent(next);
  }

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
        {fabText}
      </button>

      {open ? (
        <div
          className={cn(
            'fixed inset-y-0 z-50 flex w-full max-w-md flex-col border-border bg-background shadow-2xl',
            isHe ? 'left-0 border-r' : 'right-0 border-l',
          )}
          role="dialog"
          aria-label={isHe ? 'צ׳אט עם סוכן AI' : 'AI agent chat'}
          style={agentAccentVars(agent)}
        >
          <header className="flex flex-col gap-3 border-b border-border px-4 py-3">
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0">
                <p className="text-sm font-semibold">
                  {WEB_LIVE_AGENT_NAMES[agent][isHe ? 'he' : 'en']}
                </p>
                <p className="text-xs text-muted-foreground">
                  {WEB_LIVE_AGENT_BLURBS[agent][isHe ? 'he' : 'en']}
                </p>
                <p className="truncate text-xs text-muted-foreground" dir="auto">
                  {resolvedTopicLabel}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
                aria-label={isHe ? 'סגור' : 'Close'}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <nav
              className="flex flex-wrap gap-1.5"
              aria-label={isHe ? 'בחר סוכן' : 'Choose agent'}
            >
              {WEB_LIVE_AGENTS.map((name) => (
                <button
                  key={name}
                  type="button"
                  onClick={() => selectAgent(name)}
                  style={name === agent ? agentAccentVars(name) : undefined}
                  className={cn(
                    'rounded-full border px-2.5 py-1 text-xs font-medium transition-colors',
                    name === agent
                      ? 'agent-pill-active'
                      : 'border-border bg-surface-1/40 text-muted-foreground hover:border-primary/40 hover:text-foreground',
                  )}
                  aria-pressed={name === agent}
                >
                  {WEB_LIVE_AGENT_NAMES[name][isHe ? 'he' : 'en']}
                </button>
              ))}
            </nav>
          </header>
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden p-3">
            <AgentChat
              key={`${agent}-${practiceContext?.item_id ?? 'none'}`}
              agent={agent}
              topic={studyTopic}
              practiceContext={practiceContext}
              compact
              showHistory={false}
            />
          </div>
        </div>
      ) : null}
    </>
  );
}
