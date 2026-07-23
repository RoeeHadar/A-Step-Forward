'use client';

import type { ComponentType } from 'react';
import Link from 'next/link';
import { Activity, Brain, CalendarDays, Users } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';
import { PageHeader } from '@/components/page-header';
import { useI18n } from '@/providers/i18n-provider';
import type { AdminPlatformStats } from '@/lib/admin-stats-db';

export function AdminDashboardClient({ stats }: { stats: AdminPlatformStats }) {
  const { messages, locale } = useI18n();
  const t = messages.admin;
  const nf = new Intl.NumberFormat(locale === 'he' ? 'he-IL' : 'en-GB');

  const cards: { icon: ComponentType<{ className?: string }>; title: string; value: string }[] = [
    { icon: Users, title: t.learners, value: nf.format(stats.total_learners) },
    { icon: Users, title: t.educators, value: nf.format(stats.total_educators) },
    { icon: Activity, title: t.chatters24h, value: nf.format(stats.active_sessions_24h) },
    { icon: Brain, title: t.memoryWrites24h, value: nf.format(stats.memory_writes_24h) },
    {
      icon: CalendarDays,
      title: t.pendingBookings,
      value: nf.format(stats.pending_bookings),
    },
  ];

  return (
    <>
      <PageHeader title={t.title} description={t.subtitle} />
      {stats.source === 'unavailable' ? (
        <p className="mb-6 text-sm text-muted-foreground" role="status">
          {t.dbUnavailable}
        </p>
      ) : null}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <AdminStatCard key={card.title} {...card} />
        ))}
      </div>
      <p className="mt-8 text-sm">
        <Link href="/admin/bookings" className="text-primary underline-offset-4 hover:underline">
          {t.bookingsLink}
        </Link>
      </p>
    </>
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
        <CardTitle className="text-3xl tabular-nums">{value}</CardTitle>
      </CardHeader>
      <CardContent />
    </Card>
  );
}
