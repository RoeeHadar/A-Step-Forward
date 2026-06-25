import Link from 'next/link';
import { notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { PremiumBadge } from '@/components/premium-badge';
import { SubjectContentTabs } from '@/components/subject-content-tabs';
import { fetchBagrutExams, fetchSectionGrades, fetchSectionsPage, fetchSubjects } from '@/lib/content-api';
import { subjectLabel } from '@/lib/subject-labels';

export const dynamic = 'force-dynamic';

export default async function SubjectPage({
  params,
  searchParams,
}: {
  params: Promise<{ subject: string }>;
  searchParams: Promise<{ tab?: string }>;
}) {
  const { subject } = await params;
  const { tab } = await searchParams;
  const allSubjects = await fetchSubjects();
  const known = allSubjects.some((s) => s.subject === subject);
  const sectionsPage = await fetchSectionsPage(subject, { page: 1, page_size: 20 });
  const grades = await fetchSectionGrades(subject);
  const bagrut = await fetchBagrutExams(subject);

  if (!known && sectionsPage.total === 0 && bagrut.length === 0) {
    notFound();
  }

  const defaultTab = tab === 'bagrut' ? 'bagrut' : 'textbook';

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">Free Content</Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{subjectLabel(subject, 'en')}</span>
        </nav>

        <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold">{subjectLabel(subject, 'en')}</h1>
            <p className="mt-1 text-muted-foreground" dir="rtl">{subjectLabel(subject, 'he')}</p>
          </div>
        </header>

        <div className="mb-8 glass-surface rounded-2xl border border-accent-amber/20 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-foreground">Chat with the Tutor about this</h2>
                <PremiumBadge />
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                Ask questions about any section — currently free for all users.
              </p>
            </div>
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(subject)}`}
              className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              Open Tutor Chat
            </Link>
          </div>
        </div>

        <SubjectContentTabs
          subject={subject}
          initialSections={sectionsPage.items}
          initialTotal={sectionsPage.total}
          initialGrades={grades}
          bagrutExams={bagrut}
          defaultTab={defaultTab}
        />
      </main>
    </div>
  );
}
