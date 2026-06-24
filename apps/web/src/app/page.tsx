import { SiteHeader } from '@/components/site-header';
import { LandingHero } from '@/components/landing-hero';

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
