import Link from 'next/link';
import { SiteHeader } from '@/components/site-header';

export const metadata = { title: 'Diagnostic Assessment — A Step Forward' };

export default function DiagnosticPage() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <SiteHeader />
      <main className="mx-auto max-w-xl px-4 py-20 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-accent-cyan/30 bg-accent-cyan/10 px-4 py-1.5 text-xs text-accent-cyan mb-6">
          Coming soon
        </div>
        <h1 className="text-3xl font-bold mb-4">Diagnostic Assessment</h1>
        <p className="text-white/50 mb-8 text-sm leading-relaxed">
          The adaptive diagnostic engine is being built. It will ask you ~15–18 questions,
          calibrate difficulty in real time, and produce a mastery profile across your subjects.
        </p>
        <Link
          href="/app/chat/tutor"
          className="inline-block px-6 py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm hover:bg-cyan-300 transition-colors"
        >
          Chat with your AI Tutor in the meantime →
        </Link>
      </main>
    </div>
  );
}
