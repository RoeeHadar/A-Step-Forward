import Link from 'next/link';
import { redirect } from 'next/navigation';
import { MessageSquare } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { CardContent, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';
import { Progress } from '@asf/ui/progress';
import { PageHeader } from '@/components/page-header';
import { MotionCard } from '@/components/motion-card';
import { getAuthContext } from '@/lib/auth';
import { fetchDashboard } from '@/lib/data';
import { agentDisplayNames, learnerFacingAgents, type AgentName } from '@asf/schemas/agents';
import { agentColors } from '@/lib/design-tokens';

const progressBarClass =
  'h-2.5 overflow-hidden rounded-full bg-secondary [&>div]:rounded-full [&>div]:bg-gradient-to-r [&>div]:from-primary [&>div]:to-accent';

export default async function DashboardPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const dashboard = await fetchDashboard(auth);

  return (
    <div>
      <PageHeader title={`Welcome back, ${auth.displayName}`} description="Continue your learning journey" />

      <div className="grid gap-6 lg:grid-cols-2">
        <MotionCard className="glass-card border border-white/7 bg-[rgb(26,28,30)]">
          <CardHeader>
            <CardTitle>Recent lessons</CardTitle>
            <CardDescription>Pick up where you left off</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {dashboard.recent_lessons.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No lessons yet — pick an agent below and ask for a topic to get started.
              </p>
            ) : (
              dashboard.recent_lessons.map((lesson) => (
                <div key={lesson.id} className="space-y-2">
                  <div className="flex min-w-0 items-center justify-between gap-2">
                    <Link
                      href={`/app/lessons/${lesson.id}`}
                      className="truncate font-medium hover:underline"
                    >
                      {lesson.title}
                    </Link>
                    <span className="shrink-0 text-xs text-muted-foreground">{lesson.est_minutes} min</span>
                  </div>
                  <Progress value={lesson.progress * 100} className={progressBarClass} aria-label={`${lesson.title} progress`} />
                </div>
              ))
            )}
          </CardContent>
        </MotionCard>

        <MotionCard className="glass-card border border-white/7 bg-[rgb(26,28,30)]">
          <CardHeader>
            <CardTitle>Mastery summary</CardTitle>
            <CardDescription>Concept-level progress</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {dashboard.mastery_summary.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Mastery scores appear once you&apos;ve worked through a few questions.
              </p>
            ) : (
              dashboard.mastery_summary.map((item) => (
                <div key={item.concept_id} className="flex min-w-0 items-center justify-between gap-4">
                  <span className="truncate">{item.concept_name}</span>
                  <div className="flex shrink-0 items-center gap-3">
                    <Progress
                      value={item.score * 100}
                      className={`w-20 sm:w-24 ${progressBarClass}`}
                      aria-label={`${item.concept_name} mastery`}
                    />
                    <Badge variant={item.score >= 0.7 ? 'success' : 'secondary'}>
                      {Math.round(item.score * 100)}%
                    </Badge>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </MotionCard>
      </div>

      <section className="mt-8">
        <h2 className="mb-4 text-xl font-semibold">Your agents</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {learnerFacingAgents.map((agent: AgentName) => (
            <MotionCard key={agent} className="glass-card border border-white/7 bg-[rgb(26,28,30)]">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div
                    className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-white"
                    style={{ backgroundColor: agentColors[agent] ?? 'hsl(221 83% 53%)' }}
                    aria-hidden
                  >
                    <MessageSquare className="h-5 w-5" />
                  </div>
                  <div className="min-w-0">
                    <CardTitle className="truncate text-base">{agentDisplayNames[agent]}</CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full" variant="outline">
                  <Link href={`/app/chat/${agent}`}>Start chat</Link>
                </Button>
              </CardContent>
            </MotionCard>
          ))}
        </div>
      </section>
    </div>
  );
}
