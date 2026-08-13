import { OptionalAppShell } from '@/components/optional-app-shell';

export default function PersonaSettingsLayout({ children }: { children: React.ReactNode }) {
  return <OptionalAppShell>{children}</OptionalAppShell>;
}
