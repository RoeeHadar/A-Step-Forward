/**
 * /settings/persona — let the learner view + edit the shared CLAUDE.md-style
 * persona that every agent reads on every turn, and see (read-only) the
 * per-(learner, agent) private notes counts.
 *
 * Why this page exists: every agent reads from this body; the learner has
 * the right to inspect, redact, or rebuild it. The agent-memory API
 * already enforces userId scoping; this page is just a thin client over
 * GET/POST/PATCH /api/agent-memory/persona + POST /api/agent-memory/consolidate.
 */
import { auth } from '@clerk/nextjs/server';
import { SiteHeader } from '@/components/site-header';
import { ensureOnboarded } from '@/lib/onboarding-gate';
import {
  getLearnerPersona,
  countAgentNotes,
  dbConfigured,
} from '@/lib/neon-db';
import { PersonaEditor } from '@/components/persona-editor';

export const dynamic = 'force-dynamic';

const AGENT_NAMES = [
  'tutor',
  'mentor',
  'coach',
  'reviewer',
  'qa_explainer',
  'note_taker',
] as const;

export default async function PersonaSettingsPage() {
  const { userId } = await auth();
  if (!userId) return null;
  await ensureOnboarded(userId, '/settings/persona');

  const [persona, ...noteCounts] = dbConfigured
    ? await Promise.all([
        getLearnerPersona(userId).catch(() => null),
        ...AGENT_NAMES.map((a) => countAgentNotes(userId, a).catch(() => 0)),
      ])
    : [null, ...AGENT_NAMES.map(() => 0)];

  const noteCountsByAgent: Record<string, number> = {};
  AGENT_NAMES.forEach((a, i) => {
    noteCountsByAgent[a] = noteCounts[i] ?? 0;
  });

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
        <PersonaEditor
          initialText={persona?.text ?? null}
          updatedAt={persona?.updated_at ?? null}
          noteCountsByAgent={noteCountsByAgent}
        />
      </main>
    </div>
  );
}
