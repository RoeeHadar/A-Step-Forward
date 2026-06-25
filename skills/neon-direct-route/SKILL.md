---
name: neon-direct-route
description: >
  Build Next.js API routes that talk to Neon Postgres directly (over HTTP via
  @neondatabase/serverless) instead of proxying through the Render FastAPI
  backend. Use this whenever a feature must work even when Render is cold or
  redeploying — diagnostic, onboarding, plans, chat memory.
---

# Neon-direct route

## When to use
- The feature lives in the **free-tier critical path** (onboarding, diagnostic,
  learning plan, chat memory, /learn content).
- We cannot tolerate Render cold-start latency or downtime on this path.
- The data model is already in Neon (no Python ORM business logic needed).

## When NOT to use
- The feature requires the LangGraph orchestrator, vector search, embeddings, or
  any other Python-only logic that lives in `services/*`.
- The route must coordinate Celery jobs or any other async backend work.

In those cases, leave the route proxying to Render and rely on the keep-warm
workflow.

---

## Pattern

### 1. Put all SQL in `apps/web/src/lib/neon-db.ts`
Treat this as the **single Neon access layer for Vercel**. Add new typed
functions there, return plain objects, and reuse them from any route.

```ts
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';

neonConfig.fetchConnectionCache = true;
const sql = process.env.DATABASE_URL ? neon(process.env.DATABASE_URL) : null;
export const dbConfigured = Boolean(sql);

function requireSql() {
  if (!sql) throw new Error('DATABASE_URL not set');
  return sql;
}
```

### 2. Always guard on `dbConfigured`
Never crash the entire site when the env var is missing — return a 503 JSON
response or a friendly fallback page. The site must stay reachable.

```ts
if (!dbConfigured) {
  return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
}
```

### 3. Auth → Clerk → learnerId everywhere
Use the Clerk `userId` directly as the `learner_id` column value. Do **not**
trust client-supplied learner IDs.

```ts
import { auth } from '@clerk/nextjs/server';
const { userId } = await auth();
if (!userId) return new Response('Unauthorized', { status: 401 });
```

### 4. Route file template

```ts
import { auth } from '@clerk/nextjs/server';
import { dbConfigured, myNewQuery } from '@/lib/neon-db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  if (!dbConfigured) {
    return Response.json({ error: 'DATABASE_URL not configured' }, { status: 503 });
  }

  const body = await req.json().catch(() => ({}));
  try {
    const result = await myNewQuery(userId, body);
    return Response.json(result);
  } catch (err) {
    console.error('[my-route]', err);
    return Response.json(
      { error: err instanceof Error ? err.message : 'Internal error' },
      { status: 500 },
    );
  }
}
```

### 5. Server components: skip the API hop
Server components can call `neon-db` functions directly — no internal `/api`
fetch needed. This is preferred for `app/.../page.tsx` reads.

```ts
import { getCurrentPlan } from '@/lib/neon-db';

export default async function DashboardPage() {
  const { userId } = await auth();
  const plan = userId ? await getCurrentPlan(userId).catch(() => null) : null;
  // ...
}
```

### 6. Use the built KG JSON for plan logic
`apps/web/src/lib/kg-data.json` is the prerequisite graph baked into the
deploy. Use it for plan generation, concept matching, and prerequisite walks.
Rebuild with `node scripts/build-kg-json.mjs` after editing
`content/knowledge-graph/*.yaml`.

---

## Tables already wired
| Table | Helper |
|-------|--------|
| `learner_profiles` | `upsertLearnerProfile`, `getLearnerProfile` |
| `concept_mastery` | `getConceptMastery` (and write paths in diagnostic/quiz) |
| `diagnostic_sessions` / `diagnostic_items` / `quiz_responses` | `startDiagnosticSession`, `fetchDiagnosticItems`, `recordDiagnosticAnswer`, `completeDiagnostic` |
| `learning_plans` / `plan_weeks` | `generateLearningPlan`, `getCurrentPlan` |
| `chat_turns` | `recordChatTurn`, `fetchRecentChatTurns` |
| `external_resources` | `fetchExternalResources` |

If you need a new helper, add it to `neon-db.ts` alongside the existing ones.

---

## Acceptance checklist
- [ ] New helper in `apps/web/src/lib/neon-db.ts` with typed return.
- [ ] Route returns 401 on missing auth, 503 on missing DB config, 4xx on bad
      input, 5xx on internal error — never silently fails.
- [ ] No Render `${API_BASE_URL}` call in the critical path of this route.
- [ ] `pnpm --filter @asf/web typecheck` passes.
- [ ] `pnpm --filter @asf/web lint` passes.
- [ ] Manual test against the Vercel preview confirms the flow works with
      `DATABASE_URL` set and degrades gracefully without it.
