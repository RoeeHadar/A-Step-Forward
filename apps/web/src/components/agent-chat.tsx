'use client';

import { useChat } from 'ai/react';
import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { Textarea } from '@asf/ui/textarea';
import { Card } from '@asf/ui/card';
import { agentDisplayNames, agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { agentColors } from '@/lib/design-tokens';
import { useI18n } from '@/providers/i18n-provider';
import { useChatUiStore } from '@/stores/ui-store';

const CONNECTING_DELAY_MS = 800;
const COLD_START_RETRY_MS = 15000;

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

  useEffect(() => {
    setLastAgent(agentName);
  }, [agentName, setLastAgent]);

  useEffect(() => {
    fetch('/api/warmup').catch(() => {});
  }, []);

  const { messages, input, handleInputChange, handleSubmit, isLoading, error, reload, stop } = useChat({
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
      return;
    }

    if (userMessageCountRef.current > 1) {
      setShowConnecting(false);
      return;
    }

    hasReceivedTokensRef.current = false;

    const connectTimer = window.setTimeout(() => setShowConnecting(true), CONNECTING_DELAY_MS);
    const retryTimer = window.setTimeout(() => {
      if (!hasAutoRetriedRef.current && !hasReceivedTokensRef.current) {
        hasAutoRetriedRef.current = true;
        stop();
        reload();
      }
    }, COLD_START_RETRY_MS);

    return () => {
      window.clearTimeout(connectTimer);
      window.clearTimeout(retryTimer);
    };
  }, [isLoading, reload, stop]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const statusMessage =
    showConnecting && isLoading ? i18nMessages.chat.connecting : i18nMessages.chat.thinking;

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <header className="mb-4 flex items-center gap-3">
        <div
          className="h-3 w-3 rounded-full"
          style={{ backgroundColor: agentColors[agentName] ?? 'hsl(221 83% 53%)' }}
          aria-hidden
        />
        <h1 className="text-2xl font-semibold">{agentDisplayNames[agentName]}</h1>
      </header>

      <Card className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 space-y-4 overflow-y-auto p-4" role="log" aria-live="polite" aria-label="Chat messages">
          {messages.length === 0 ? (
            <p className="text-center text-muted-foreground">{i18nMessages.chat.empty}</p>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={
                  m.role === 'user'
                    ? 'ml-auto max-w-[85%] rounded-lg bg-primary px-4 py-2 text-primary-foreground'
                    : 'mr-auto max-w-[85%] rounded-lg bg-muted px-4 py-2'
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
            {friendlyChatError(error)}
          </p>
        ) : null}

        <form onSubmit={handleSubmit} className="flex gap-2 border-t border-border p-4">
          <label htmlFor="chat-input" className="sr-only">
            Message
          </label>
          <Textarea
            id="chat-input"
            value={input}
            onChange={handleInputChange}
            placeholder={i18nMessages.chat.placeholder}
            rows={2}
            className="min-h-[44px] resize-none"
            disabled={isLoading}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>);
              }
            }}
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()} aria-label="Send message">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </Card>
    </div>
  );
}

function friendlyChatError(error: unknown): string {
  if (error instanceof Error && error.message) {
    if (/401|unauthor/i.test(error.message)) {
      return 'Please sign in to continue chatting.';
    }
    if (/network|fetch|failed/i.test(error.message)) {
      return 'We hit a network hiccup reaching the agent. Please try again in a moment.';
    }
    return error.message;
  }
  return 'Something went wrong. Please try again.';
}
