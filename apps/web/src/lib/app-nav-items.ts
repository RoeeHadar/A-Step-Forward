import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard,
  MessageSquare,
  BookOpen,
  Brain,
  TrendingUp,
  ClipboardCheck,
  FileClock,
  Bell,
  Users,
  Dumbbell,
} from 'lucide-react';

export type AppNavLabelKey =
  | 'dashboard'
  | 'learn'
  | 'practice'
  | 'chat'
  | 'quiz'
  | 'tests'
  | 'memory'
  | 'progress'
  | 'friends'
  | 'notifications';

export type AppNavItem = {
  href: string;
  icon: LucideIcon;
  labelKey: AppNavLabelKey;
  match?: string;
};

/** Single source of truth for signed-in learner app navigation. */
export const APP_NAV_ITEMS: AppNavItem[] = [
  { href: '/app', icon: LayoutDashboard, labelKey: 'dashboard' },
  { href: '/learn', icon: BookOpen, labelKey: 'learn', match: '/learn' },
  { href: '/app/practice', icon: Dumbbell, labelKey: 'practice', match: '/app/practice' },
  { href: '/app/chat/tutor', icon: MessageSquare, labelKey: 'chat', match: '/app/chat' },
  { href: '/app/quiz', icon: ClipboardCheck, labelKey: 'quiz', match: '/app/quiz' },
  { href: '/app/tests', icon: FileClock, labelKey: 'tests', match: '/app/tests' },
  { href: '/app/memory', icon: Brain, labelKey: 'memory' },
  { href: '/app/progress', icon: TrendingUp, labelKey: 'progress' },
  { href: '/app/friends', icon: Users, labelKey: 'friends', match: '/app/friends' },
  {
    href: '/app/notifications',
    icon: Bell,
    labelKey: 'notifications',
    match: '/app/notifications',
  },
];

/** Primary destinations shown in the mobile bottom bar. */
export const APP_MOBILE_PRIMARY_NAV: AppNavItem[] = [
  APP_NAV_ITEMS.find((i) => i.labelKey === 'chat')!,
  APP_NAV_ITEMS.find((i) => i.labelKey === 'practice')!,
  APP_NAV_ITEMS.find((i) => i.labelKey === 'dashboard')!,
  APP_NAV_ITEMS.find((i) => i.labelKey === 'progress')!,
];

export function isAppNavItemActive(pathname: string, item: AppNavItem): boolean {
  const matchPath = item.match ?? item.href;
  // '/app' is a prefix of every app route — the dashboard item must match exactly,
  // otherwise it shows as active alongside whichever page is actually open.
  if (matchPath === '/app') return pathname === '/app';
  return pathname === item.href || pathname.startsWith(matchPath);
}

export function appMobileMoreNavItems(): AppNavItem[] {
  const primaryHrefs = new Set(APP_MOBILE_PRIMARY_NAV.map((i) => i.href));
  return APP_NAV_ITEMS.filter((i) => !primaryHrefs.has(i.href));
}
