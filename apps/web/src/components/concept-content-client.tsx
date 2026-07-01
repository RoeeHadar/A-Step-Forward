'use client';

import { useEffect, useMemo } from 'react';
import Link from 'next/link';
import { MarkdownMath } from '@/components/markdown-math';
import { ExternalLink } from 'lucide-react';
import { useLanguagePreference } from '@/hooks/use-language-preference';

interface Explanation {
  language: string;
  title: string;
  body_md: string;
  summary: string | null;
  image_url: string | null;
  source: string;
  source_url: string;
  license: string;
  attribution: string;
  fetched_at: string;
}

export function ConceptContentClient({
  en,
  he,
  fallback,
  conceptId,
  subject,
  conceptName,
}: {
  en: Explanation | null;
  he: Explanation | null;
  fallback: Explanation | null;
  conceptId: string;
  subject: string;
  conceptName: string;
}) {
  const availableLangs = useMemo(() => {
    const langs: Array<'en' | 'he'> = [];
    if (he) langs.push('he');
    if (en) langs.push('en');
    return langs;
  }, [en, he]);

  const [lang, setLang] = useLanguagePreference('he');
  // If the learner's preference isn't an available language (e.g. they prefer
  // HE but only EN was scraped for this concept), fall back to whatever IS
  // available without overwriting their preference for other pages.
  useEffect(() => {
    if (availableLangs.length === 0) return;
    if (!availableLangs.includes(lang)) {
      // Note: don't persist this auto-switch — only the explicit toggle should.
      // We rely on the prop dropdown to call setLang for actual user intent.
    }
  }, [lang, availableLangs]);
  const effective = availableLangs.includes(lang) ? lang : (availableLangs[0] ?? 'en');
  const active = effective === 'en' ? en ?? fallback : he ?? fallback;
  if (!active) return null;

  const dir = active.language === 'he' ? 'rtl' : 'ltr';

  return (
    <article className="space-y-6">
      {availableLangs.length > 1 ? (
        <div className="inline-flex rounded-full border border-border bg-surface-1/50 p-1">
          {availableLangs.map((l) => (
            <button
              key={l}
              type="button"
              onClick={() => setLang(l)}
              className={`rounded-full px-4 py-1.5 text-xs font-semibold transition-colors ${
                effective === l
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {l === 'he' ? 'עברית' : 'English'}
            </button>
          ))}
        </div>
      ) : null}

      <div className="glass-surface rounded-2xl border-border/60 p-6" dir={dir}>
        {active.image_url ? (
          // External Wikipedia thumbnails - using <img> avoids configuring
          // next/image remotePatterns for every Wikimedia subdomain.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={active.image_url}
            alt={conceptName}
            className="mb-5 max-h-72 w-auto rounded-lg border border-border object-contain"
            loading="lazy"
          />
        ) : null}

        {active.summary ? (
          <p className="mb-4 text-sm italic text-muted-foreground">{active.summary}</p>
        ) : null}

        <MarkdownMath className="md:prose-base">{active.body_md}</MarkdownMath>

        <footer className="mt-6 border-t border-border/60 pt-4 text-xs text-muted-foreground">
          <p>
            {active.attribution}{' '}
            <a
              href={active.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-primary hover:underline"
            >
              Original article
              <ExternalLink className="h-3 w-3" />
            </a>
          </p>
          <p className="mt-1">
            Fetched on {new Date(active.fetched_at).toLocaleDateString()} · License:{' '}
            <strong>{active.license}</strong>
          </p>
          <p className="mt-2 text-[11px]">
            Help improve this explanation:{' '}
            <Link
              href={`/app/chat/tutor?context=${encodeURIComponent(`Improve the explanation of ${conceptName}`)}`}
              className="text-primary hover:underline"
            >
              ask the Tutor
            </Link>{' '}
            or contribute on{' '}
            <a
              href={`https://github.com/RoeeHadar/A-Step-Forward/blob/main/content/concept-wikipedia-overrides.yaml`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              GitHub
            </a>
            .
          </p>
        </footer>
      </div>

      <p className="text-xs text-muted-foreground">
        Concept ID: <code className="rounded bg-muted px-1 py-0.5">{conceptId}</code>
        {' · subject: '}
        <code className="rounded bg-muted px-1 py-0.5">{subject}</code>
      </p>
    </article>
  );
}
