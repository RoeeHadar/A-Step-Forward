import { redirect } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { EducatorStudentsClient } from '@/components/educator-students-client';
import { getAuthContext, requireRole } from '@/lib/auth';
import { ensureIdentityComplete } from '@/lib/identity-gate';
import { getAppUser, listTeacherStudents } from '@/lib/social-db';

export const dynamic = 'force-dynamic';

export default async function EducatorHomePage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');
  await ensureIdentityComplete(auth.userId, '/educator');

  try {
    requireRole(auth, ['educator', 'admin']);
  } catch {
    redirect('/app');
  }

  const me = await getAppUser(auth.userId);
  if (!me || me.role !== 'educator') redirect('/identity');

  const students = await listTeacherStudents(auth.userId);

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">
        <EducatorStudentsClient
          students={students}
          aboutMe={me.about_me}
        />
      </main>
    </div>
  );
}
