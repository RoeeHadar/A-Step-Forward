export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-6 p-8">
      <h1 className="text-4xl font-semibold tracking-tight">A Step Forward</h1>
      <p className="text-lg text-muted-foreground">
        An AI-native learning center where a personalized roster of agents teach, assess,
        remember and evolve with you. This page is a Phase-0 placeholder — sub-agent
        <code className="mx-1 rounded bg-muted px-1 py-0.5 text-sm">01-frontend</code>
        replaces it with the full marketing landing and learner workspace.
      </p>
      <div className="text-sm text-muted-foreground">
        See <code>PLAN.md</code>, <code>.cursor/subagent-briefs/01-frontend.md</code>.
      </div>
    </main>
  );
}
