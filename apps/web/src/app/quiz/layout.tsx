import { OptionalAppShell } from '@/components/optional-app-shell';

export default function QuizLayout({ children }: { children: React.ReactNode }) {
  return <OptionalAppShell>{children}</OptionalAppShell>;
}
