'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import type { LearnerProgress } from '@asf/schemas/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';

export function ProgressDashboard({ progress }: { progress: LearnerProgress }) {
  const masteryData = progress.concepts.map((c) => ({
    name: c.concept_name,
    score: Math.round(c.current_score * 100),
  }));

  const historyData =
    progress.concepts[0]?.history.map((h) => ({
      date: h.date.slice(5),
      score: Math.round(h.score * 100),
    })) ?? [];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Streak" value={`${progress.streak_days} days`} />
        <StatCard title="Total time" value={`${progress.total_minutes} min`} />
        <StatCard title="Lessons done" value={String(progress.lessons_completed)} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Mastery by concept</CardTitle>
          <CardDescription>Current scores across tracked concepts</CardDescription>
        </CardHeader>
        <CardContent className="h-72">
          {masteryData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
              Track your progress as you learn — mastery scores show up after your first session.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={masteryData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="score" fill="hsl(221 83% 53%)" radius={[4, 4, 0, 0]} name="Mastery %" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {historyData.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Mastery over time</CardTitle>
            <CardDescription>{progress.concepts[0]?.concept_name} progress trend</CardDescription>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="hsl(142 71% 45%)"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  name="Mastery %"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-3xl">{value}</CardTitle>
      </CardHeader>
    </Card>
  );
}
