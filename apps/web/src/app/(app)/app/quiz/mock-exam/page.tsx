import Link from 'next/link';
import { Clock, ArrowLeft } from 'lucide-react';

export default function MockExamPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center p-6">
      <div className="glass-surface max-w-lg rounded-2xl border border-border/60 p-8 text-center">
        <div className="mb-5 flex justify-center">
          <span className="grid h-14 w-14 place-items-center rounded-full bg-muted">
            <Clock className="h-7 w-7 text-muted-foreground" />
          </span>
        </div>

        <h1 className="mb-4 text-xl font-semibold text-foreground">
          מבחן מדומה / Mock Exam
        </h1>

        <p
          className="mb-2 text-sm leading-relaxed text-foreground/80"
          dir="rtl"
        >
          המבחן המדומה הוסר בינתיים. ניתן לגשת לבוחן מותאם אישית כאן.
        </p>
        <p className="mb-8 text-sm leading-relaxed text-muted-foreground">
          Timed mock exams are temporarily unavailable. Use the custom quiz
          below instead.
        </p>

        <Link
          href="/app/quiz"
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
        >
          <ArrowLeft className="h-4 w-4" />
          בוחן מותאם אישית / Custom Quiz
        </Link>
      </div>
    </div>
  );
}
