'use client';

import Link from 'next/link';
import { Badge } from '@asf/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { Button } from '@asf/ui/button';
import type { LearningPlan, PlanConcept } from '@asf/schemas/learning_path';
import { currentActiveWeek } from '@/lib/learning-path-types';

function masteryBadgeVariant(score: number | null | undefined): 'success' | 'warning' | 'secondary' {
  if (score == null) return 'secondary';
  if (score > 0.7) return 'success';
  if (score >= 0.4) return 'warning';
  return 'secondary';
}

function masteryLabel(score: number | null | undefined): string {
  if (score == null) return 'Not assessed';
  return `${Math.round(score * 100)}% mastery`;
}

function ConceptCard({ concept }: { concept: PlanConcept }) {
  const mastery = concept.mastery ?? 0;
  const progressPct = Math.round(mastery * 100);

  return (
    <Card className="glass-surface border-border/60">
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <CardTitle className="text-base">{concept.name}</CardTitle>
          <Badge variant={masteryBadgeVariant(concept.mastery)}>{masteryLabel(concept.mastery)}</Badge>
        </div>
        <p className="text-xs text-muted-foreground">{concept.concept_id}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <div className="mb-1 flex justify-between text-xs text-muted-foreground">
            <span>Progress</span>
            <span>{progressPct}%</span>
          </div>
          <div className="h-2 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${progressPct}%` }}
              role="progressbar"
              aria-valuenow={progressPct}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${concept.name} mastery`}
            />
          </div>
        </div>

        {concept.suggested_sections.length > 0 ? (
          <div>
            <p className="mb-1 text-xs font-medium text-muted-foreground">Textbook sections</p>
            <ul className="space-y-1">
              {concept.suggested_sections.slice(0, 3).map((section) => (
                <li key={section.id}>
                  <Link
                    href={
                      section.chunk_index != null
                        ? `/learn/${concept.subject}/${section.chunk_index}`
                        : `/learn/${concept.subject}`
                    }
                    className="text-sm text-primary hover:underline"
                    dir="auto"
                  >
                    {section.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <Link href={`/learn/${concept.subject}`} className="text-sm text-primary hover:underline">
            Browse {concept.subject} content
          </Link>
        )}
      </CardContent>
    </Card>
  );
}

export function LearningPlanDashboard({ plan }: { plan: LearningPlan }) {
  const week = currentActiveWeek(plan);

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-display text-3xl font-bold">Your learning plan</h1>
        <p className="mt-2 text-muted-foreground">{plan.goal}</p>
      </header>

      {week ? (
        <section className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold">Week {week.week_number}</h2>
              <p className="text-sm text-muted-foreground">
                {week.concepts.length} concepts · status: {week.status}
              </p>
            </div>
            <Button variant="outline" disabled title="Weekly quiz ships in Phase E">
              Start Week Quiz
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {week.concepts.map((concept) => (
              <ConceptCard key={concept.concept_id} concept={concept} />
            ))}
          </div>
        </section>
      ) : (
        <p className="text-muted-foreground">No weeks in this plan yet.</p>
      )}

      {plan.weeks.length > 1 ? (
        <section>
          <h3 className="mb-3 text-sm font-medium text-muted-foreground">All weeks</h3>
          <div className="flex flex-wrap gap-2">
            {plan.weeks.map((w) => (
              <Badge key={w.id} variant={w.status === 'active' ? 'default' : 'outline'}>
                Week {w.week_number}: {w.concepts.length} concepts
              </Badge>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
