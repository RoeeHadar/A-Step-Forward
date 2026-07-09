import Link from 'next/link';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { AgentChat } from '@/components/agent-chat';
import { agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { cn } from '@asf/ui';
import { agentAccentVars } from '@/lib/design-tokens';
import {
  WEB_LIVE_AGENTS,
  WEB_LIVE_AGENT_NAMES,
  isDeprecatedChatAgent,
  resolveWebChatAgent,
  type WebLiveAgent,
} from '@/lib/web-agents';

export default async function ChatPage({ params }: { params: Promise<{ agent: string }> }) {
  const { agent } = await params;
  const parsed = agentNameSchema.safeParse(agent);
  const slug: AgentName = parsed.success ? parsed.data : 'tutor';

  if (isDeprecatedChatAgent(slug)) {
    redirect('/app/chat/tutor');
  }

  const activeAgent: WebLiveAgent = resolveWebChatAgent(slug);

  const cookieStore = await cookies();
  const isHe = (cookieStore.get('asf-locale')?.value ?? 'he') !== 'en';

  return (
    <div
      className="agent-accent-context flex flex-col gap-4"
      style={agentAccentVars(activeAgent)}
    >
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

      <AgentChat agent={activeAgent} />
    </div>
  );
}
