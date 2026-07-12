'use client';

import Link from 'next/link';
import { cn } from '@asf/ui';
import { agentAccentVars } from '@/lib/design-tokens';
import { useI18n } from '@/providers/i18n-provider';
import {
  WEB_LIVE_AGENTS,
  WEB_LIVE_AGENT_BLURBS,
  WEB_LIVE_AGENT_NAMES,
  type WebLiveAgent,
} from '@/lib/web-agents';

export function ChatAgentSwitcher({ activeAgent }: { activeAgent: WebLiveAgent }) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const blurb = WEB_LIVE_AGENT_BLURBS[activeAgent][isHe ? 'he' : 'en'];

  return (
    <div className="space-y-2">
      <nav className="flex flex-wrap gap-2" aria-label={isHe ? 'בחר סוכן AI' : 'Switch AI agent'}>
        {WEB_LIVE_AGENTS.map((name) => (
          <Link
            key={name}
            href={`/app/chat/${name}`}
            style={name === activeAgent ? agentAccentVars(name) : undefined}
            className={cn(
              'rounded-full border px-3 py-1.5 text-sm font-medium transition-colors',
              name === activeAgent
                ? 'agent-pill-active'
                : 'border-border bg-surface-1/40 text-muted-foreground hover:border-primary/40 hover:text-foreground',
            )}
            aria-current={name === activeAgent ? 'page' : undefined}
          >
            {WEB_LIVE_AGENT_NAMES[name][isHe ? 'he' : 'en']}
          </Link>
        ))}
      </nav>
      <p className="text-sm text-muted-foreground" dir={isHe ? 'rtl' : 'ltr'}>
        {blurb}
      </p>
    </div>
  );
}
