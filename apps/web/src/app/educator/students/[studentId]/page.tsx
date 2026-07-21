import { redirect, notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { EducatorStudentWorkspace } from '@/components/educator-student-workspace';
import { getAuthContext, requireRole } from '@/lib/auth';
import { ensureIdentityComplete } from '@/lib/identity-gate';
import {
  assertTeacherOfStudent,
  getAppUser,
  listTeacherNotes,
} from '@/lib/social-db';
import {
  getCurrentPlan,
  getLearnerMemorySnapshot,
  getLearnerProfile,
  getProgressFromNeon,
} from '@/lib/neon-db';
import { listTestAttempts } from '@/lib/test-attempts';
import { pickConceptTitle, resolveConceptTitles } from '@/lib/concept-display-names';

export const dynamic = 'force-dynamic';

export default async function EducatorStudentPage({
  params,
}: {
  params: Promise<{ studentId: string }>;
}) {
  const { studentId } = await params;
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');
  await ensureIdentityComplete(auth.userId, '/educator');
  try {
    requireRole(auth, ['educator', 'admin']);
  } catch {
    redirect('/app');
  }

  const ok = await assertTeacherOfStudent(auth.userId, studentId);
  if (!ok) notFound();

  const student = await getAppUser(studentId);
  if (!student) notFound();

  const [profile, plan, progress, memory, attempts, notes] = await Promise.all([
    getLearnerProfile(studentId).catch(() => null),
    getCurrentPlan(studentId).catch(() => null),
    getProgressFromNeon(studentId).catch(() => null),
    getLearnerMemorySnapshot(studentId).catch(() => null),
    listTestAttempts(studentId, 20).catch(() => []),
    listTeacherNotes(studentId).catch(() => []),
  ]);

  const activeWeek = plan?.weeks.find((w) => w.status === 'active') ?? plan?.weeks[0];
  const planWeekConcepts = activeWeek?.concepts.map((c) => c.concept_id) ?? [];

  const planWeeks =
    plan?.weeks.map((w) => ({
      week_number: w.week_number,
      status: w.status,
      quiz_due_at: w.quiz_due_at ?? null,
      concepts: w.concepts.map((c) => ({
        concept_id: c.concept_id,
        name: c.name_he || c.name || c.concept_id,
        mastery: c.mastery ?? null,
      })),
    })) ?? [];

  const progressView = progress
    ? {
        streak_days: progress.streak.current_days,
        lessons_completed: progress.lessons_completed,
        avg_mastery: progress.avg_mastery,
        atoms_practiced: progress.atoms_practiced,
        total_minutes: progress.total_minutes,
        total_xp: progress.total_xp,
        level: progress.level,
        concepts: progress.concepts.slice(0, 20).map((c) => {
          const titles = resolveConceptTitles(c.concept_id, {
            title_en: c.concept_name,
            title_he: c.concept_name_he,
          });
          return {
            concept_id: c.concept_id,
            title: pickConceptTitle(titles, 'he'),
            score: c.current_score,
          };
        }),
        daily_activity: progress.daily_activity,
      }
    : null;

  const memoryView = memory
    ? {
        persona: memory.persona.text,
        profile_goal: memory.profile?.goal ?? null,
        subjects: memory.profile?.subjects ?? [],
        weak: memory.weakConcepts,
        strong: memory.strongConcepts,
        notes_by_agent: Object.entries(memory.notesByAgent).map(([agent, list]) => ({
          agent,
          count: list.length,
          preview: list[0]?.content ?? null,
        })),
        recent_chat: memory.recentChatTurns.slice(0, 12).map((t) => ({
          agent: t.agent,
          role: t.role,
          content: t.content,
          created_at: t.created_at,
        })),
      }
    : null;

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">
        <EducatorStudentWorkspace
          studentId={studentId}
          studentName={student.real_name}
          username={student.username}
          goal={profile?.goal ?? null}
          hoursPerWeek={profile?.hours_per_week ?? null}
          planWeeks={planWeeks}
          planWeekConcepts={planWeekConcepts}
          progress={progressView}
          memory={memoryView}
          attempts={attempts.map((a) => ({
            id: a.id,
            kind: a.kind,
            score: a.score,
            passed: a.passed,
            created_at: a.created_at,
          }))}
          notes={notes}
        />
      </main>
    </div>
  );
}
