'use client';

import { useChat } from 'ai/react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useMemo, useRef, useState } from 'react';
import { MarkdownMath } from '@/components/markdown-math';
import { Send, Loader2, X } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { Textarea } from '@asf/ui/textarea';
import { cn } from '@asf/ui';
import { agentDisplayNames, agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { PremiumBadge } from '@/components/premium-badge';
import { useI18n } from '@/providers/i18n-provider';
import { useChatUiStore } from '@/stores/ui-store';

const CONNECTING_DELAY_MS = 800;
const WARMUP_BANNER_DELAY_MS = 3000;

function formatCountdown(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function timerBadgeClass(remaining: number, total: number): string {
  if (total <= 0) return 'bg-muted text-muted-foreground';
  const ratio = remaining / total;
  if (ratio <= 0.15) return 'bg-destructive/15 text-destructive border-destructive/30';
  if (ratio <= 0.4) return 'bg-accent-amber/15 text-accent-amber border-accent-amber/30';
  return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30';
}

const agentGradients: Partial<Record<AgentName, string>> = {
  tutor: 'from-primary to-accent-magenta',
  mentor: 'from-accent-amber to-accent-magenta',
  coach: 'from-accent-cyan to-primary',
  reviewer: 'from-accent-magenta to-accent-cyan',
  qa_explainer: 'from-accent-cyan to-primary',
  note_taker: 'from-accent-magenta to-accent-cyan',
  accessibility: 'from-primary to-accent-cyan',
};

export function AgentChat({ agent }: { agent: string }) {
  const { messages: i18nMessages, locale } = useI18n();
  const isHe = locale === 'he';
  const parsed = agentNameSchema.safeParse(agent);
  const agentName: AgentName = parsed.success ? parsed.data : 'tutor';
  const bottomRef = useRef<HTMLDivElement>(null);
  const setLastAgent = useChatUiStore((s) => s.setLastAgent);
  const hasAutoRetriedRef = useRef(false);
  const hasReceivedTokensRef = useRef(false);
  const userMessageCountRef = useRef(0);
  const [showConnecting, setShowConnecting] = useState(false);
  const [showWarmupBanner, setShowWarmupBanner] = useState(false);
  const searchParams = useSearchParams();
  const quickMode = searchParams.get('mode') === 'quick';
  const quickDuration = searchParams.get('duration') ?? '15';
  const totalQuickSeconds = useMemo(
    () => Math.max(1, Number.parseInt(quickDuration, 10) || 15) * 60,
    [quickDuration],
  );
  const [remainingSeconds, setRemainingSeconds] = useState(totalQuickSeconds);
  const [timeUp, setTimeUp] = useState(false);
  const [timeUpDismissed, setTimeUpDismissed] = useState(false);

  useEffect(() => {
    if (!quickMode) return;
    setRemainingSeconds(totalQuickSeconds);
    setTimeUp(false);
    setTimeUpDismissed(false);

    const intervalId = window.setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          setTimeUp(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => window.clearInterval(intervalId);
  }, [quickMode, totalQuickSeconds]);

  useEffect(() => {
    setLastAgent(agentName);
  }, [agentName, setLastAgent]);

  useEffect(() => {
    fetch('/api/warmup').catch(() => {});
  }, []);

  const { messages, input, handleInputChange, handleSubmit, isLoading, error, reload } = useChat({
    api: '/api/chat',
    body: { agent: agentName, quickMode, quickDuration: quickMode ? quickDuration : undefined },
    onError: () => {
      if (!hasAutoRetriedRef.current && userMessageCountRef.current <= 1) {
        hasAutoRetriedRef.current = true;
        window.setTimeout(() => reload(), 500);
      }
    },
  });

  useEffect(() => {
    userMessageCountRef.current = messages.filter((m) => m.role === 'user').length;
    const assistantContent = messages.find((m) => m.role === 'assistant')?.content;
    if (assistantContent) {
      hasReceivedTokensRef.current = true;
    }
  }, [messages]);

  useEffect(() => {
    if (!isLoading) {
      setShowConnecting(false);
      setShowWarmupBanner(false);
      return;
    }

    if (userMessageCountRef.current > 1) {
      setShowConnecting(false);
      setShowWarmupBanner(false);
      return;
    }

    hasReceivedTokensRef.current = false;
    setShowWarmupBanner(false);

    const connectTimer = window.setTimeout(() => setShowConnecting(true), CONNECTING_DELAY_MS);
    const warmupTimer = window.setTimeout(() => {
      if (!hasReceivedTokensRef.current) {
        setShowWarmupBanner(true);
      }
    }, WARMUP_BANNER_DELAY_MS);

    return () => {
      window.clearTimeout(connectTimer);
      window.clearTimeout(warmupTimer);
    };
  }, [isLoading]);

  useEffect(() => {
    const assistantContent = messages.find((m) => m.role === 'assistant')?.content;
    if (assistantContent && isLoading) {
      hasReceivedTokensRef.current = true;
      setShowWarmupBanner(false);
    }
  }, [messages, isLoading]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const statusMessage =
    showConnecting && isLoading ? i18nMessages.chat.connecting : i18nMessages.chat.thinking;

  const gradient = agentGradients[agentName] ?? 'from-primary to-accent-cyan';

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <header className="mb-4 flex flex-wrap items-center gap-3">
        <div
          className={cn('h-3 w-3 rounded-full bg-gradient-to-br', gradient)}
          aria-hidden
        />
        <h1
          className={cn(
            'font-display text-2xl font-semibold bg-gradient-to-r bg-clip-text text-transparent',
            gradient,
          )}
        >
          {(i18nMessages.dashboard?.agentNames as Record<string, string>)?.[agentName] ?? agentDisplayNames[agentName]}
        </h1>
        {quickMode ? (
          <span
            className={cn(
              'rounded-full border px-2.5 py-0.5 text-xs font-semibold tabular-nums',
              timerBadgeClass(remainingSeconds, totalQuickSeconds),
            )}
            role="timer"
            aria-live="polite"
          >
            {isHe
              ? `⏱ ${formatCountdown(remainingSeconds)} נותרו`
              : `⏱ ${formatCountdown(remainingSeconds)} remaining`}
          </span>
        ) : null}
        <PremiumBadge />
      </header>

      <div className="glass-surface flex flex-1 flex-col overflow-hidden rounded-2xl">
        {quickMode && timeUp && !timeUpDismissed ? (
          <div
            className="flex flex-wrap items-center justify-between gap-3 border-b border-accent-amber/30 bg-accent-amber/10 px-4 py-3 text-sm"
            role="status"
          >
            <span className="font-medium text-foreground">
              {isHe ? 'הגיע הזמן לסיים — עשית עבודה טובה!' : "Time's up — great work!"}
            </span>
            <div className="flex items-center gap-2">
              <Link
                href="/app?completed=1"
                className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-3 py-1.5 text-xs font-semibold text-primary-foreground"
              >
                {isHe ? 'חזרה ללוח הבקרה' : 'Back to Dashboard'}
              </Link>
              <button
                type="button"
                onClick={() => setTimeUpDismissed(true)}
                className="rounded-md p-1 text-muted-foreground hover:text-foreground"
                aria-label={isHe ? 'סגור' : 'Dismiss'}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        ) : null}
        <div
          className="flex-1 space-y-4 overflow-y-auto p-4"
          role="log"
          aria-live="polite"
          aria-label="Chat messages"
        >
          {messages.length === 0 ? (
            <p className="text-center text-muted-foreground">{i18nMessages.chat.empty}</p>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={
                  m.role === 'user'
                    ? 'ms-auto max-w-[85%] rounded-2xl rounded-ee-sm bg-primary/90 px-4 py-2 text-primary-foreground'
                    : 'me-auto max-w-[85%] rounded-2xl rounded-es-sm border border-border glass-surface px-4 py-2 text-foreground'
                }
              >
                {m.role === 'assistant' ? (
                  <MarkdownMath>{m.content}</MarkdownMath>
                ) : (
                  m.content
                )}
              </div>
            ))
          )}
          {showWarmupBanner && isLoading ? (
            <div
              className="rounded-lg border border-accent-cyan/30 bg-accent-cyan/10 px-4 py-2 text-sm text-accent-cyan"
              role="status"
            >
              {i18nMessages.chat?.warmup ?? '🔄 Waking the AI up… (first response takes up to 30s)'}
            </div>
          ) : null}
          {isLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground" role="status">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              <span>{statusMessage}</span>
            </div>
          ) : null}
          <div ref={bottomRef} />
        </div>

        {error ? (
          <p className="border-t border-border px-4 py-2 text-sm text-destructive" role="alert">
            {friendlyChatError(error, i18nMessages.chat)}
          </p>
        ) : null}

        <form onSubmit={handleSubmit} className="glass-surface flex gap-2 border-t border-border p-4">
          <label htmlFor="chat-input" className="sr-only">
            {i18nMessages.chat.messageLabel}
          </label>
          <Textarea
            id="chat-input"
            value={input}
            onChange={handleInputChange}
            placeholder={i18nMessages.chat.placeholder}
            rows={2}
            className="min-h-[44px] resize-none border-border bg-surface-1/50"
            disabled={isLoading}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>);
              }
            }}
          />
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !input.trim()}
            aria-label={i18nMessages.chat.sendAriaLabel}
          >
            <Send className="h-4 w-4 rtl:rotate-180" />
          </Button>
        </form>
      </div>
    </div>
  );
}

function friendlyChatError(
  error: unknown,
  chat: { signInRequired: string; networkError: string; genericError: string },
): string {
  if (error instanceof Error && error.message) {
    if (/401|unauthor/i.test(error.message)) {
      return chat.signInRequired;
    }
    if (/network|fetch|failed/i.test(error.message)) {
      return chat.networkError;
    }
    return error.message;
  }
  return chat.genericError;
}
