'use client';

import { useCallback, useEffect, useState } from 'react';
import { History, MessageSquare } from 'lucide-react';
import { cn } from '@asf/ui';
import type { AgentName } from '@asf/schemas/agents';

export interface ChatSessionRow {
  session_id: string | null;
  agent: string;
  started_at: string;
  last_at: string;
  turn_count: number;
  preview: string;
}

type Lang = 'he' | 'en';

const STR = {
  en: {
    title: 'Past conversations',
    empty: 'No messages yet — start chatting!',
    turns: (n: number) => `${n} messages`,
    newChat: 'New conversation',
  },
  he: {
    title: 'שיחות קודמות',
    empty: 'אין הודעות עדיין — התחילו לשוחח!',
    turns: (n: number) => `${n} הודעות`,
    newChat: 'שיחה חדשה',
  },
};

export function ChatHistoryPanel({
  agent,
  locale,
  activeSessionId,
  onSelectSession,
  onNewChat,
  className,
}: {
  agent: AgentName;
  locale: Lang;
  activeSessionId: string | null;
  onSelectSession: (sessionId: string | null) => void;
  onNewChat: () => void;
  className?: string;
}) {
  const t = STR[locale];
  const [sessions, setSessions] = useState<ChatSessionRow[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `/api/chat/history?mode=sessions&agent=${encodeURIComponent(agent)}&limit=20`,
      );
      if (res.ok) {
        const data = (await res.json()) as { sessions: ChatSessionRow[] };
        setSessions(data.sessions ?? []);
      }
    } finally {
      setLoading(false);
    }
  }, [agent]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <aside
      className={cn(
        'flex flex-col rounded-xl border border-border bg-surface-1/40',
        className,
      )}
      dir={locale === 'he' ? 'rtl' : 'ltr'}
    >
      <div className="flex items-center justify-between gap-2 border-b border-border px-3 py-2">
        <div className="flex items-center gap-2 text-sm font-medium">
          <History className="h-4 w-4 text-muted-foreground" aria-hidden />
          {t.title}
        </div>
        <button
          type="button"
          onClick={onNewChat}
          className="text-xs text-primary hover:underline"
        >
          {t.newChat}
        </button>
      </div>
      <div className="max-h-[420px] flex-1 overflow-y-auto p-2">
        {loading ? (
          <p className="px-2 py-4 text-xs text-muted-foreground">…</p>
        ) : sessions.length === 0 ? (
          <p className="px-2 py-4 text-xs text-muted-foreground">{t.empty}</p>
        ) : (
          <ul className="space-y-1">
            {sessions.map((s) => {
              const sid = s.session_id;
              const active = sid === activeSessionId || (!sid && !activeSessionId);
              return (
                <li key={`${s.agent}-${sid ?? s.started_at}`}>
                  <button
                    type="button"
                    onClick={() => onSelectSession(sid)}
                    className={cn(
                      'w-full rounded-lg px-2 py-2 text-start text-xs transition-colors',
                      active
                        ? 'bg-primary/10 text-foreground'
                        : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground',
                    )}
                  >
                    <div className="flex items-center gap-1.5 font-medium">
                      <MessageSquare className="h-3 w-3 shrink-0" aria-hidden />
                      <span className="truncate">
                        {s.preview?.trim() || (locale === 'he' ? 'שיחה' : 'Chat')}
                      </span>
                    </div>
                    <div className="mt-0.5 text-[10px] text-muted-foreground">
                      {new Date(s.last_at).toLocaleDateString(locale === 'he' ? 'he-IL' : 'en-IL')}{' '}
                      · {t.turns(s.turn_count)}
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </aside>
  );
}
