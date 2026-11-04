import Link from 'next/link';
import { AmbientBackground } from '@/components/ambient-background';
import { SiteHeader } from '@/components/site-header';
import { getServerLocale } from '@/i18n/locale-server';
import { LEGAL_DOCS, type LegalDocId } from '@/lib/legal-content';
import { LegalBody } from '@/lib/legal-markup';

const NAV: { id: LegalDocId; href: string; he: string; en: string }[] = [
  { id: 'privacy', href: '/privacy', he: 'מדיניות פרטיות', en: 'Privacy policy' },
  { id: 'terms', href: '/terms', he: 'תנאי שימוש', en: 'Terms of use' },
  { id: 'accessibility', href: '/accessibility', he: 'הצהרת נגישות', en: 'Accessibility statement' },
];

/** Title for <title>; the root layout's template already appends the site name. */
export function legalTitle(id: LegalDocId, locale: 'he' | 'en'): string {
  return LEGAL_DOCS[id][locale].title.replace(/\s*[–-]\s*A Step Forward$/, '');
}

export async function LegalPage({ id }: { id: LegalDocId }) {
  const locale = await getServerLocale();
  const doc = LEGAL_DOCS[id][locale];
  return (
    <div className="relative min-h-screen">
      <AmbientBackground />
      <SiteHeader />
      <main id="main" className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <article>
          <h1 className="text-2xl font-bold sm:text-3xl">{doc.title}</h1>
          <LegalBody body={doc.body} />
        </article>
        <nav
          aria-label={locale === 'he' ? 'מסמכים משפטיים' : 'Legal documents'}
          className="mt-12 flex flex-wrap gap-x-6 gap-y-2 border-t border-border pt-6 text-sm"
        >
          {NAV.map((n) => (
            <Link
              key={n.id}
              href={n.href}
              aria-current={n.id === id ? 'page' : undefined}
              className="underline-offset-2 hover:underline aria-[current=page]:font-semibold"
            >
              {n[locale]}
            </Link>
          ))}
        </nav>
      </main>
    </div>
  );
}
