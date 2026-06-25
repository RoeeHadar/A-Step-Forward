import Link from 'next/link';
import { notFound } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { MarkdownReader } from '@/components/markdown-reader';
import { PremiumBadge } from '@/components/premium-badge';
import { fetchSection, fetchSections } from '@/lib/content-api';
import { subjectLabel } from '@/lib/subject-labels';

export const dynamic = 'force-dynamic';

export default async function SectionPage({
  params,
}: {
  params: Promise<{ subject: string; chunkIndex: string }>;
}) {
  const { subject, chunkIndex: chunkIndexStr } = await params;
  const chunkIndex = Number.parseInt(chunkIndexStr, 10);
  if (Number.isNaN(chunkIndex)) notFound();

  const section = await fetchSection(subject, chunkIndex);
  if (!section) notFound();

  const allSections = await fetchSections(subject);
  const prev = allSections.find((s) => s.chunk_index === chunkIndex - 1);
  const next = allSections.find((s) => s.chunk_index === chunkIndex + 1);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
        <nav className="mb-4 text-sm text-muted-foreground">
          <Link href="/learn" className="hover:text-foreground">
            Learn
          </Link>
          <span className="mx-2">/</span>
          <Link href={`/learn/${subject}`} className="hover:text-foreground">
            {subjectLabel(subject, 'en')}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-foreground">{section.title}</span>
        </nav>

        <header className="mb-6">
          <h1 className="font-display text-3xl font-bold" dir="auto">
            {section.title}
          </h1>
          {section.page_start != null ? (
            <p className="mt-1 text-sm text-muted-foreground">
              Pages {section.page_start}
              {section.page_end != null && section.page_end !== section.page_start
                ? `–${section.page_end}`
                : ''}{' '}
              · {section.source_file}
            </p>
          ) : null}
        </header>

        <article className="glass-surface rounded-2xl p-6" dir="auto">
          <MarkdownReader content={section.body_md} />
        </article>

        <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex gap-2">
            {prev ? (
              <Link
                href={`/learn/${subject}/${prev.chunk_index}`}
                className="rounded-lg border border-border px-4 py-2 text-sm hover:border-primary/40"
              >
                ← Previous
              </Link>
            ) : null}
            {next ? (
              <Link
                href={`/learn/${subject}/${next.chunk_index}`}
                className="rounded-lg border border-border px-4 py-2 text-sm hover:border-primary/40"
              >
                Next →
              </Link>
            ) : null}
          </div>
          <Link
            href={`/app/chat/tutor?context=${encodeURIComponent(section.id)}`}
            className="inline-flex items-center gap-2 rounded-lg bg-primary/10 px-4 py-2 text-sm font-medium text-primary"
          >
            Chat with Tutor about this
            <PremiumBadge />
          </Link>
        </div>
      </main>
    </div>
  );
}
