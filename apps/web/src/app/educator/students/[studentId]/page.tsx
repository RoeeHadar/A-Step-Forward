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
  getConceptMastery,
  getCurrentPlan,
  getLearnerPersona,
  getLearnerProfile,
} from '@/lib/neon-db';
import { listTestAttempts } from '@/lib/test-attempts';

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

  const [profile, plan, mastery, persona, attempts, notes] = await Promise.all([
    getLearnerProfile(studentId).catch(() => null),
    getCurrentPlan(studentId).catch(() => null),
    getConceptMastery(studentId).catch(() => ({}) as Record<string, number>),
    getLearnerPersona(studentId).catch(() => null),
    listTestAttempts(studentId, 20).catch(() => []),
    listTeacherNotes(studentId).catch(() => []),
  ]);

  const activeWeek = plan?.weeks.find((w) => w.status === 'active') ?? plan?.weeks[0];
  const planWeekConcepts = activeWeek?.concepts.map((c) => c.concept_id) ?? [];
  const masterySample = Object.entries(mastery)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([concept_id, score]) => ({ concept_id, score }));

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
          planWeekConcepts={planWeekConcepts}
          masterySample={masterySample}
          attempts={attempts.map((a) => ({
            id: a.id,
            kind: a.kind,
            score: a.score,
            passed: a.passed,
            created_at: a.created_at,
          }))}
          personaPreview={persona?.text ?? null}
          notes={notes}
        />
      </main>
    </div>
  );
}
