import Link from 'next/link';
import { ArrowLeft, ClipboardList } from 'lucide-react';

export default function MockExamUnavailablePage() {
  return (
    <div className="mx-auto max-w-lg px-4 py-10">
      <Link
        href="/app/quiz"
        className="mb-6 inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
        Back to quiz
      </Link>

      <div
        className="glass-surface rounded-2xl border border-border/60 p-8 text-center"
        dir="rtl"
      >
        <div className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-full bg-primary/10">
          <ClipboardList className="h-6 w-6 text-primary" aria-hidden />
        </div>
        <h1 className="font-display text-2xl font-bold text-foreground">
          המבחן המדומה הוסר בינתיים
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          ניתן לגשת לבוחן מותאם אישית כאן.
        </p>
        <Link
          href="/app/quiz"
          className="mt-6 inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-5 py-2.5 text-sm font-semibold text-primary-foreground"
        >
          לבוחן המותאם אישית
        </Link>
      </div>

      <div
        className="glass-surface mt-4 rounded-2xl border border-border/60 p-8 text-center"
        dir="ltr"
      >
        <h2 className="font-display text-xl font-bold text-foreground">
          Timed mock exams are temporarily unavailable
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          Use the custom quiz below instead.
        </p>
        <Link
          href="/app/quiz"
          className="mt-6 inline-flex rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-5 py-2.5 text-sm font-semibold text-primary-foreground"
        >
          Go to custom quiz
        </Link>
      </div>
    </div>
  );
}
