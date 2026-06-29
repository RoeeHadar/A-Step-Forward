import Link from 'next/link';
import { cookies } from 'next/headers';
import { AgentChat } from '@/components/agent-chat';
import { agentDisplayNames, agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { cn } from '@asf/ui';

const LEARNER_AGENTS: AgentName[] = [
  'tutor',
  'mentor',
  'coach',
  'reviewer',
  'qa_explainer',
  'note_taker',
];

const AGENT_NAMES_HE: Partial<Record<AgentName, string>> = {
  tutor: 'מורה',
  mentor: 'מנטור',
  coach: 'מאמן',
  reviewer: 'מבקר',
  qa_explainer: 'שאלות ותשובות',
  note_taker: 'רושם הערות',
};

export default async function ChatPage({ params }: { params: Promise<{ agent: string }> }) {
  const { agent } = await params;
  const parsed = agentNameSchema.safeParse(agent);
  const activeAgent: AgentName = parsed.success ? parsed.data : 'tutor';

  const cookieStore = await cookies();
  const isHe = (cookieStore.get('asf-locale')?.value ?? 'he') !== 'en';

  return (
    <div className="flex flex-col gap-4">
      {/* Agent switcher */}
      <nav className="flex flex-wrap gap-2" aria-label={isHe ? 'בחר סוכן AI' : 'Switch AI agent'}>
        {LEARNER_AGENTS.map((name) => (
          <Link
            key={name}
            href={`/app/chat/${name}`}
            className={cn(
              'rounded-full border px-3 py-1.5 text-sm font-medium transition-colors',
              name === activeAgent
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border bg-surface-1/40 text-muted-foreground hover:border-primary/40 hover:text-foreground',
            )}
            aria-current={name === activeAgent ? 'page' : undefined}
          >
            {isHe ? (AGENT_NAMES_HE[name] ?? agentDisplayNames[name]) : agentDisplayNames[name]}
          </Link>
        ))}
      </nav>

      <AgentChat agent={activeAgent} />
    </div>
  );
}
