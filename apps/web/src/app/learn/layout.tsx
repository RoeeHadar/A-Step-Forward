import { OptionalAppShell } from '@/components/optional-app-shell';

export default function LearnLayout({ children }: { children: React.ReactNode }) {
  return <OptionalAppShell>{children}</OptionalAppShell>;
}
