import { AgentChat } from '@/components/agent-chat';

export default async function ChatPage({ params }: { params: Promise<{ agent: string }> }) {
  const { agent } = await params;
  return <AgentChat agent={agent} />;
}
