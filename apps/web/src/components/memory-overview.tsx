'use client';

import { useState, type ComponentType } from 'react';
import Link from 'next/link';
import {
  Brain,
  MessageSquare,
  Search,
  UserCircle2,
  Sparkles,
  Target,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import { Badge } from '@asf/ui/badge';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { cn } from '@asf/ui';
import { MarkdownReader } from '@/components/markdown-reader';
import { pickConceptTitle, resolveConceptTitles } from '@/lib/concept-display-names';
import { subjectLabel } from '@/lib/subject-labels';
import type { LearnerMemorySnapshot, LearnerMemoryNote } from '@/lib/neon-db';
import { useI18n } from '@/providers/i18n-provider';

const AGENT_ORDER = ['tutor', 'mentor', 'coach', 'reviewer'] as const;

function formatDate(iso: string | null, locale: 'he' | 'en'): string {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString(locale === 'he' ? 'he-IL' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

function importanceLabel(importance: number, t: ReturnType<typeof useI18n>['messages']['memory']): string {
  if (importance >= 5) return t.importanceHigh;
  if (importance >= 4) return t.importanceMedium;
  return t.importanceNormal;
}

function SectionCard({
  icon: Icon,
  title,
  description,
  children,
  className,
}: {
  icon: ComponentType<{ className?: string }>;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={cn('card-punch rounded-2xl p-5 md:p-6', className)}>
      <div className="mb-4 flex items-start gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <Icon className="h-5 w-5" aria-hidden />
        </span>
        <div className="min-w-0">
          <h2 className="font-display text-lg font-semibold">{title}</h2>
          {description ? (
            <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>
          ) : null}
        </div>
      </div>
      {children}
    </section>
  );
}

function ProfileField({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value?.trim()) return null;
  return (
    <div className="rounded-xl bg-surface-1/50 px-4 py-3">
      <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="mt-1 text-sm font-medium">{value}</dd>
    </div>
  );
}

function NoteCard({
  note,
  lang,
  kindLabel,
  importanceText,
}: {
  note: LearnerMemoryNote;
  lang: 'he' | 'en';
  kindLabel: string;
  importanceText: string;
}) {
  const conceptLabel = note.related_concept_id
    ? pickConceptTitle(resolveConceptTitles(note.related_concept_id), lang)
    : null;

  return (
    <div className="rounded-xl border border-border/60 bg-surface-1/30 px-4 py-3">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <Badge variant="secondary" className="text-xs">
          {kindLabel}
        </Badge>
        {conceptLabel ? (
          <Badge variant="outline" className="text-xs">
            {conceptLabel}
          </Badge>
        ) : null}
        <span className="text-xs text-muted-foreground">{importanceText}</span>
        <span className="text-xs text-muted-foreground">· {formatDate(note.created_at, lang)}</span>
      </div>
      <p className="text-sm leading-relaxed">{note.content}</p>
    </div>
  );
}

export function MemoryOverview({ snapshot }: { snapshot: LearnerMemorySnapshot }) {
  const { messages, locale } = useI18n();
  const t = messages.memory;
  const lang = locale === 'he' ? 'he' : 'en';
  const isHe = lang === 'he';
  const [query, setQuery] = useState('');

  const agentNames = messages.dashboard.agentNames;

  const q = query.trim().toLowerCase();
  const matchesSearch = (text: string) => !q || text.toLowerCase().includes(q);

  const hasProfileContent = Boolean(
    snapshot.profile &&
      (snapshot.profile.goal ||
        snapshot.profile.subjects.length > 0 ||
        snapshot.profile.background_notes ||
        snapshot.profile.next_test_name ||
        snapshot.profile.next_test_date ||
        snapshot.profile.final_goal_date),
  );

  const hasPersona = Boolean(snapshot.persona.text?.trim());
  const hasPlanFocus =
    Boolean(snapshot.activePlanGoal) || snapshot.activeWeekConceptIds.length > 0;
  const hasSignals =
    snapshot.weakConcepts.length > 0 || snapshot.strongConcepts.length > 0;
  const hasNotes = snapshot.totalNoteCount > 0;
  const hasChat = snapshot.recentChatTurns.length > 0;

  const showAnything =
    hasProfileContent || hasPersona || hasPlanFocus || hasSignals || hasNotes || hasChat;

  const filteredNotesByAgent: Record<string, LearnerMemoryNote[]> = {};
  for (const agent of AGENT_ORDER) {
    const notes = snapshot.notesByAgent[agent] ?? [];
    filteredNotesByAgent[agent] = q
      ? notes.filter(
          (n) =>
            matchesSearch(n.content) ||
            matchesSearch(n.kind) ||
            matchesSearch(agentNames[agent as keyof typeof agentNames] ?? agent),
        )
      : notes;
  }

  const profileVisible =
    hasProfileContent &&
    (!q ||
      matchesSearch(snapshot.profile?.goal ?? '') ||
      matchesSearch(snapshot.profile?.background_notes ?? '') ||
      (snapshot.profile?.subjects ?? []).some((s) => matchesSearch(s)));

  const personaVisible =
    hasPersona && (!q || matchesSearch(snapshot.persona.text ?? ''));

  const planVisible =
    hasPlanFocus &&
    (!q ||
      matchesSearch(snapshot.activePlanGoal ?? '') ||
      snapshot.activeWeekConceptIds.some((id) =>
        matchesSearch(pickConceptTitle(resolveConceptTitles(id), lang)),
      ));

  const signalsVisible =
    hasSignals &&
    (!q ||
      snapshot.weakConcepts.some((c) =>
        matchesSearch(pickConceptTitle(resolveConceptTitles(c.concept_id), lang)),
      ) ||
      snapshot.strongConcepts.some((c) =>
        matchesSearch(pickConceptTitle(resolveConceptTitles(c.concept_id), lang)),
      ));

  const anyAgentNotesVisible = AGENT_ORDER.some(
    (a) => (filteredNotesByAgent[a]?.length ?? 0) > 0,
  );

  const nothingMatchesSearch =
    q &&
    !profileVisible &&
    !personaVisible &&
    !planVisible &&
    !signalsVisible &&
    !anyAgentNotesVisible;

  return (
    <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="rounded-2xl border border-primary/25 bg-gradient-to-br from-primary/10 via-transparent to-accent-cyan/5 p-5">
        <div className="flex flex-wrap items-start gap-4">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">
            <Brain className="h-6 w-6" aria-hidden />
          </span>
          <div className="min-w-0 flex-1 space-y-2">
            <p className="text-sm leading-relaxed text-muted-foreground">{t.readOnlyNotice}</p>
            <div className="flex flex-wrap gap-2 pt-1">
              <Button asChild size="sm">
                <Link href="/app/chat/tutor">
                  <MessageSquare className="h-4 w-4" aria-hidden />
                  {t.chatTutor}
                </Link>
              </Button>
              <Button asChild size="sm" variant="outline">
                <Link href="/app/chat/mentor">{t.chatMentor}</Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {showAnything ? (
        <div className="relative max-w-md">
          <Search
            className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t.searchPlaceholder}
            className="ps-9"
            aria-label={t.searchAriaLabel}
          />
        </div>
      ) : null}

      {!showAnything ? (
        <div className="card-punch rounded-2xl p-8 text-center">
          <Brain className="mx-auto h-12 w-12 text-muted-foreground/60" aria-hidden />
          <p className="mt-4 text-muted-foreground">{t.emptyTitle}</p>
          <p className="mt-2 text-sm text-muted-foreground">{t.emptyBody}</p>
          <Button asChild className="mt-5">
            <Link href="/app/chat/tutor">{t.noMemoriesCtaLink}</Link>
          </Button>
        </div>
      ) : nothingMatchesSearch ? (
        <p className="text-center text-muted-foreground">{t.noSearchResults}</p>
      ) : (
        <div className="space-y-6">
          {profileVisible && snapshot.profile ? (
            <SectionCard
              icon={UserCircle2}
              title={t.profileSectionTitle}
              description={t.profileSectionDesc}
            >
              <dl className="grid gap-3 sm:grid-cols-2">
                <ProfileField label={t.fieldGoal} value={snapshot.profile.goal} />
                <ProfileField
                  label={t.fieldSubjects}
                  value={
                    snapshot.profile.subjects.length > 0
                      ? snapshot.profile.subjects
                          .map((s) => subjectLabel(s, lang))
                          .join(', ')
                      : null
                  }
                />
                <ProfileField
                  label={t.fieldHours}
                  value={
                    snapshot.profile.hours_per_week
                      ? `${snapshot.profile.hours_per_week} ${t.hoursPerWeekSuffix}`
                      : null
                  }
                />
                <ProfileField
                  label={t.fieldStyle}
                  value={snapshot.profile.preferred_style}
                />
                <ProfileField
                  label={t.fieldNextTest}
                  value={
                    snapshot.profile.next_test_name
                      ? `${snapshot.profile.next_test_name}${
                          snapshot.profile.next_test_date
                            ? ` · ${formatDate(snapshot.profile.next_test_date, lang)}`
                            : ''
                        }`
                      : snapshot.profile.next_test_date
                        ? formatDate(snapshot.profile.next_test_date, lang)
                        : null
                  }
                />
                <ProfileField
                  label={t.fieldFinalGoal}
                  value={
                    snapshot.profile.final_goal_date
                      ? formatDate(snapshot.profile.final_goal_date, lang)
                      : null
                  }
                />
                {snapshot.profile.background_notes ? (
                  <div className="sm:col-span-2 rounded-xl bg-surface-1/50 px-4 py-3">
                    <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      {t.fieldNotes}
                    </dt>
                    <dd className="mt-1 text-sm leading-relaxed">
                      {snapshot.profile.background_notes}
                    </dd>
                  </div>
                ) : null}
              </dl>
            </SectionCard>
          ) : null}

          {personaVisible ? (
            <SectionCard
              icon={Sparkles}
              title={t.personaSectionTitle}
              description={t.personaSectionDesc}
            >
              {snapshot.persona.updated_at ? (
                <p className="mb-3 text-xs text-muted-foreground">
                  {t.updatedAt} {formatDate(snapshot.persona.updated_at, lang)}
                </p>
              ) : null}
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <MarkdownReader content={snapshot.persona.text ?? ''} />
              </div>
            </SectionCard>
          ) : !hasPersona && !q ? (
            <SectionCard
              icon={Sparkles}
              title={t.personaSectionTitle}
              description={t.personaSectionDesc}
            >
              <p className="text-sm text-muted-foreground">{t.personaEmpty}</p>
            </SectionCard>
          ) : null}

          {planVisible ? (
            <SectionCard
              icon={Target}
              title={t.planSectionTitle}
              description={t.planSectionDesc}
            >
              {snapshot.activePlanGoal ? (
                <p className="mb-3 text-sm font-medium">{snapshot.activePlanGoal}</p>
              ) : null}
              {snapshot.activeWeekConceptIds.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {snapshot.activeWeekConceptIds.map((id) => (
                    <Badge key={id} variant="outline">
                      {pickConceptTitle(resolveConceptTitles(id), lang)}
                    </Badge>
                  ))}
                </div>
              ) : null}
            </SectionCard>
          ) : null}

          {signalsVisible ? (
            <div className="grid gap-6 lg:grid-cols-2">
              {snapshot.weakConcepts.length > 0 &&
              (!q ||
                snapshot.weakConcepts.some((c) =>
                  matchesSearch(
                    pickConceptTitle(resolveConceptTitles(c.concept_id), lang),
                  ),
                )) ? (
                <SectionCard
                  icon={TrendingDown}
                  title={t.weakSectionTitle}
                  description={t.weakSectionDesc}
                >
                  <ul className="space-y-2">
                    {snapshot.weakConcepts.map((c) => {
                      const label = pickConceptTitle(
                        resolveConceptTitles(c.concept_id),
                        lang,
                      );
                      if (q && !matchesSearch(label)) return null;
                      return (
                        <li
                          key={c.concept_id}
                          className="flex items-center justify-between rounded-lg bg-surface-1/40 px-3 py-2 text-sm"
                        >
                          <span>{label}</span>
                          <span className="text-muted-foreground">
                            {Math.round(c.score * 100)}%
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                </SectionCard>
              ) : null}

              {snapshot.strongConcepts.length > 0 &&
              (!q ||
                snapshot.strongConcepts.some((c) =>
                  matchesSearch(
                    pickConceptTitle(resolveConceptTitles(c.concept_id), lang),
                  ),
                )) ? (
                <SectionCard
                  icon={TrendingUp}
                  title={t.strongSectionTitle}
                  description={t.strongSectionDesc}
                >
                  <ul className="space-y-2">
                    {snapshot.strongConcepts.map((c) => {
                      const label = pickConceptTitle(
                        resolveConceptTitles(c.concept_id),
                        lang,
                      );
                      if (q && !matchesSearch(label)) return null;
                      return (
                        <li
                          key={c.concept_id}
                          className="flex items-center justify-between rounded-lg bg-surface-1/40 px-3 py-2 text-sm"
                        >
                          <span>{label}</span>
                          <span className="text-muted-foreground">
                            {Math.round(c.score * 100)}%
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                </SectionCard>
              ) : null}
            </div>
          ) : null}

          {(() => {
            const agentsWithNotes = AGENT_ORDER.filter(
              (a) => (filteredNotesByAgent[a]?.length ?? 0) > 0,
            );

            if (agentsWithNotes.length > 0) {
              return agentsWithNotes.map((agent) => {
                const notes = filteredNotesByAgent[agent] ?? [];
                const agentLabel =
                  agentNames[agent as keyof typeof agentNames] ?? agent;
                return (
                  <SectionCard
                    key={agent}
                    icon={MessageSquare}
                    title={agentLabel}
                    description={t.agentNotesCount(notes.length)}
                  >
                    <div className="space-y-3">
                      {notes.map((note) => (
                        <NoteCard
                          key={note.id}
                          note={note}
                          lang={lang}
                          kindLabel={
                            t.noteKinds[note.kind as keyof typeof t.noteKinds] ??
                            note.kind
                          }
                          importanceText={importanceLabel(note.importance, t)}
                        />
                      ))}
                    </div>
                  </SectionCard>
                );
              });
            }

            if (q) return null;

            return (
              <SectionCard
                icon={MessageSquare}
                title={t.agentNotesSectionTitle}
                description={t.agentNotesSectionDesc}
              >
                <p className="text-sm text-muted-foreground">{t.agentNotesEmptyHint}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {AGENT_ORDER.slice(0, 4).map((agent) => (
                    <Button key={agent} asChild size="sm" variant="outline">
                      <Link href={`/app/chat/${agent}`}>
                        {agentNames[agent as keyof typeof agentNames] ?? agent}
                      </Link>
                    </Button>
                  ))}
                </div>
              </SectionCard>
            );
          })()}

          {hasChat &&
          (!q ||
            snapshot.recentChatTurns.some(
              (turn) => matchesSearch(turn.content) || matchesSearch(turn.agent),
            )) ? (
            <SectionCard
              icon={MessageSquare}
              title={isHe ? 'שיחות אחרונות' : 'Recent conversations'}
              description={
                isHe
                  ? 'תמליל מקוצר מהצ׳אט — מתעדכן אחרי כל שיחה'
                  : 'Short chat transcript — updates after each conversation'
              }
            >
              <ul className="max-h-80 space-y-2 overflow-y-auto text-sm">
                {snapshot.recentChatTurns
                  .filter(
                    (turn) =>
                      !q ||
                      matchesSearch(turn.content) ||
                      matchesSearch(turn.agent),
                  )
                  .slice(-16)
                  .map((turn, idx) => (
                    <li
                      key={`${turn.created_at}-${idx}`}
                      className="rounded-lg bg-surface-1/40 px-3 py-2"
                    >
                      <div className="mb-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                        <Badge variant="outline">{turn.agent}</Badge>
                        <span>{turn.role === 'user' ? (isHe ? 'את/ה' : 'You') : turn.agent}</span>
                        {turn.created_at ? (
                          <span>{formatDate(turn.created_at, lang)}</span>
                        ) : null}
                      </div>
                      <p className="whitespace-pre-wrap leading-relaxed">{turn.content}</p>
                    </li>
                  ))}
              </ul>
            </SectionCard>
          ) : null}
        </div>
      )}
    </div>
  );
}
