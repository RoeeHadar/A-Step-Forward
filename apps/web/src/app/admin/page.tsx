import type { ComponentType } from 'react';
import { redirect } from 'next/navigation';
import { Activity, Brain, Users, Zap } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import { SiteHeader } from '@/components/site-header';
import { getAuthContext, requireRole } from '@/lib/auth';
import { fetchAdminStats } from '@/lib/data';

export default async function AdminPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  try {
    requireRole(auth, ['admin']);
  } catch {
    redirect('/app');
  }

  const stats = await fetchAdminStats(auth);

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl p-6">
        <PageHeader title="Admin" description="System overview and platform metrics" />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <AdminStatCard
            icon={Users}
            title="Total learners"
            value={stats.total_learners.toLocaleString()}
          />
          <AdminStatCard
            icon={Users}
            title="Educators"
            value={stats.total_educators.toLocaleString()}
          />
          <AdminStatCard
            icon={Activity}
            title="Active sessions (24h)"
            value={stats.active_sessions_24h.toLocaleString()}
          />
          <AdminStatCard
            icon={Brain}
            title="Memory writes (24h)"
            value={stats.memory_writes_24h.toLocaleString()}
          />
          <AdminStatCard
            icon={Zap}
            title="Avg latency"
            value={`${stats.avg_latency_ms} ms`}
          />
        </div>
      </main>
    </div>
  );
}

function AdminStatCard({
  icon: Icon,
  title,
  value,
}: {
  icon: ComponentType<{ className?: string }>;
  title: string;
  value: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="flex items-center gap-2">
          <Icon className="h-4 w-4" aria-hidden />
          {title}
        </CardDescription>
        <CardTitle className="text-3xl">{value}</CardTitle>
      </CardHeader>
      <CardContent />
    </Card>
  );
}
