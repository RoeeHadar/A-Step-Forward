import { redirect } from 'next/navigation';
import { AgentChat } from '@/components/agent-chat';
import { ChatAgentSwitcher } from '@/components/chat-agent-switcher';
import { agentNameSchema, type AgentName } from '@asf/schemas/agents';
import { agentAccentVars } from '@/lib/design-tokens';
import {
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

  return (
    <div
      className="agent-accent-context flex flex-col gap-4"
      style={agentAccentVars(activeAgent)}
    >
      <ChatAgentSwitcher activeAgent={activeAgent} />
      <AgentChat agent={activeAgent} />
    </div>
  );
}
