import Link from 'next/link';
import { notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { getAuthContext } from '@/lib/auth';
import {
  areFriends,
  countTeacherStudents,
  getAppUserByUsername,
} from '@/lib/social-db';
import { getPublicShareStats } from '@/lib/neon-db';

export const dynamic = 'force-dynamic';

export default async function PublicProfilePage({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const { username: raw } = await params;
  const username = decodeURIComponent(raw).trim().toLowerCase();
  const user = await getAppUserByUsername(username);
  if (!user || !user.profile_complete) notFound();

  const auth = await getAuthContext().catch(() => null);
  const isSelf = auth?.userId === user.clerk_user_id;
  const friends =
    auth && user.role === 'learner' && !isSelf
      ? await areFriends(auth.userId, user.clerk_user_id)
      : isSelf;

  const canSeeLearnerStats = user.role === 'learner' && (isSelf || friends);

  const [stats, studentCount] = await Promise.all([
    canSeeLearnerStats ? getPublicShareStats(user.clerk_user_id) : Promise.resolve(null),
    user.role === 'educator' ? countTeacherStudents(user.clerk_user_id) : Promise.resolve(0),
  ]);

  const display =
    user.role === 'learner'
      ? user.nickname?.trim() || user.real_name
      : user.real_name;

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-10">
        <div className="space-y-6">
          <header className="space-y-2">
            <p className="text-sm text-muted-foreground">
              {user.role === 'educator' ? 'Teacher' : 'Student'} · @{user.username}
            </p>
            <h1 className="font-display text-3xl font-bold">{display}</h1>
            {user.role === 'educator' && user.about_me?.trim() ? (
              <p className="text-muted-foreground whitespace-pre-wrap">{user.about_me}</p>
            ) : null}
          </header>

          {user.role === 'educator' ? (
            <section className="rounded-2xl border border-border p-5">
              <p className="text-sm text-muted-foreground">Connected students</p>
              <p className="mt-1 text-3xl font-semibold tabular-nums">{studentCount}</p>
              {isSelf ? (
                <Link href="/educator" className="mt-4 inline-block text-sm text-primary hover:underline">
                  Back to teacher home →
                </Link>
              ) : null}
            </section>
          ) : null}

          {user.role === 'learner' ? (
            canSeeLearnerStats && stats ? (
              <section className="space-y-4 rounded-2xl border border-border p-5">
                <h2 className="font-semibold">High-level progress</h2>
                <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                  <div>
                    <dt className="text-xs text-muted-foreground">Streak</dt>
                    <dd className="text-2xl font-semibold tabular-nums">{stats.streak_days}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">Lessons done</dt>
                    <dd className="text-2xl font-semibold tabular-nums">
                      {stats.lessons_completed_count}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">Avg mastery</dt>
                    <dd className="text-2xl font-semibold tabular-nums">
                      {Math.round(stats.mastery_avg * 100)}%
                    </dd>
                  </div>
                </dl>
                <div>
                  <p className="mb-2 text-xs text-muted-foreground">Activity (28 days)</p>
                  <div className="flex flex-wrap gap-1" aria-hidden>
                    {(stats.activity_heatmap.length > 0
                      ? stats.activity_heatmap
                      : stats.week_activity.map((on, i) => ({
                          date: String(i),
                          count: on ? 1 : 0,
                        }))
                    ).map((d) => {
                      const max = Math.max(
                        1,
                        ...stats.activity_heatmap.map((x) => x.count),
                        1,
                      );
                      const intensity = d.count / max;
                      return (
                        <span
                          key={d.date}
                          title={`${d.date}: ${d.count}`}
                          className="h-3.5 w-3.5 rounded-sm"
                          style={{
                            backgroundColor:
                              d.count === 0
                                ? 'hsl(var(--muted))'
                                : `hsl(var(--primary) / ${0.25 + intensity * 0.75})`,
                          }}
                        />
                      );
                    })}
                  </div>
                </div>
              </section>
            ) : (
              <p className="text-sm text-muted-foreground">
                {isSelf
                  ? 'Your high-level progress appears here for friends.'
                  : 'Add this learner as a friend to see high-level progress.'}
              </p>
            )
          ) : null}

          {auth && user.role === 'learner' && !isSelf && !friends ? (
            <Link href="/app/friends" className="text-sm text-primary hover:underline">
              Go to Friends to send a request →
            </Link>
          ) : null}
        </div>
      </main>
    </div>
  );
}
