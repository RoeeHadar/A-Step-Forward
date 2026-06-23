import { redirect } from 'next/navigation';
import { Users, AlertTriangle, TrendingUp } from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import { SiteHeader } from '@/components/site-header';
import { getAuthContext, requireRole } from '@/lib/auth';
import { fetchEducatorDashboard } from '@/lib/data';

export default async function EducatorPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  try {
    requireRole(auth, ['educator', 'admin']);
  } catch {
    redirect('/app');
  }

  const dashboard = await fetchEducatorDashboard(auth);

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl p-6">
        <PageHeader title="Educator dashboard" description="Monitor learner progress and identify at-risk students" />

        <div className="mb-8 grid gap-4 sm:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <Users className="h-4 w-4" aria-hidden />
                Active today
              </CardDescription>
              <CardTitle className="text-3xl">{dashboard.active_today}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" aria-hidden />
                Class avg mastery
              </CardDescription>
              <CardTitle className="text-3xl">{Math.round(dashboard.class_avg_mastery * 100)}%</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" aria-hidden />
                At-risk learners
              </CardDescription>
              <CardTitle className="text-3xl">
                {dashboard.learners.filter((l) => l.at_risk).length}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Learners</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="divide-y divide-border">
              {dashboard.learners.map((learner) => (
                <li key={learner.learner_id} className="flex items-center justify-between py-4">
                  <div>
                    <p className="font-medium">{learner.display_name}</p>
                    <p className="text-sm text-muted-foreground">
                      Last active{' '}
                      {learner.last_active_at
                        ? new Date(learner.last_active_at).toLocaleDateString()
                        : 'unknown'}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm">{Math.round(learner.avg_mastery * 100)}% mastery</span>
                    {learner.at_risk ? <Badge variant="warning">At risk</Badge> : <Badge variant="success">On track</Badge>}
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
