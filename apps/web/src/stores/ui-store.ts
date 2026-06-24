import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AgentName } from '@asf/schemas/agents';

interface ChatUiState {
  lastAgent: AgentName;
  sessionId: string | null;
  setLastAgent: (agent: AgentName) => void;
  setSessionId: (id: string | null) => void;
}

export const useChatUiStore = create<ChatUiState>()(
  persist(
    (set) => ({
      lastAgent: 'tutor',
      sessionId: null,
      setLastAgent: (lastAgent) => set({ lastAgent }),
      setSessionId: (sessionId) => set({ sessionId }),
    }),
    { name: 'asf-chat-ui' },
  ),
);

interface SidebarState {
  collapsed: boolean;
  toggle: () => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
  collapsed: false,
  toggle: () => set((s) => ({ collapsed: !s.collapsed })),
}));
