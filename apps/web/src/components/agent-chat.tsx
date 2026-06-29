'use client';

import { useChat } from 'ai/react';
import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { Textarea } from '@asf/ui/textarea';
import { cn } from '@asf/ui';
import { agentDisplayNames, agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { PremiumBadge } from '@/components/premium-badge';
import { useI18n } from '@/providers/i18n-provider';
import { useChatUiStore } from '@/stores/ui-store';

const CONNECTING_DELAY_MS = 800;
const WARMUP_BANNER_DELAY_MS = 3000;

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
  const { messages: i18nMessages } = useI18n();
  const parsed = agentNameSchema.safeParse(agent);
  const agentName: AgentName = parsed.success ? parsed.data : 'tutor';
  const bottomRef = useRef<HTMLDivElement>(null);
  const setLastAgent = useChatUiStore((s) => s.setLastAgent);
  const hasAutoRetriedRef = useRef(false);
  const hasReceivedTokensRef = useRef(false);
  const userMessageCountRef = useRef(0);
  const [showConnecting, setShowConnecting] = useState(false);
  const [showWarmupBanner, setShowWarmupBanner] = useState(false);

  useEffect(() => {
    setLastAgent(agentName);
  }, [agentName, setLastAgent]);

  useEffect(() => {
    fetch('/api/warmup').catch(() => {});
  }, []);

  const { messages, input, handleInputChange, handleSubmit, isLoading, error, reload } = useChat({
    api: '/api/chat',
    body: { agent: agentName },
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
      <header className="mb-4 flex items-center gap-3">
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
        <PremiumBadge />
      </header>

      <div className="glass-surface flex flex-1 flex-col overflow-hidden rounded-2xl">
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
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
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
              🔄 {i18nMessages.chat?.warmup ?? 'Waking the AI up… (first response takes up to 30s)'}
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
