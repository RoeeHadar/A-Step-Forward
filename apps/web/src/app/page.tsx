import { SiteHeader } from '@/components/site-header';
import { LandingHero } from '@/components/landing-hero';
import type { Metadata } from 'next';
import { absoluteUrl } from '@/lib/site-url';
import { pageOpenGraph } from '@/lib/site-metadata';

export function generateMetadata(): Metadata {
  const url = absoluteUrl('/');
  return { alternates: { canonical: url }, openGraph: pageOpenGraph({ url }) };
}

export const dynamic = 'force-dynamic';

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="flex-1">
        <LandingHero />
      </main>
    </div>
  );
}
