import { SiteHeader } from '@/components/site-header';
import { LandingHero } from '@/components/landing-hero';

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main>
        <LandingHero />
      </main>
      <footer className="border-t border-border bg-[#d1fe17] py-8 text-center text-sm text-[#0f1113]">
        © {new Date().getFullYear()} A Step Forward
      </footer>
    </div>
  );
}
