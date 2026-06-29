'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  MessageSquare,
  BookOpen,
  Brain,
  TrendingUp,
  ClipboardCheck,
  FileText,
} from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';

const items = [
  { href: '/app', icon: LayoutDashboard, labelKey: 'dashboard' as const },
  { href: '/learn', icon: BookOpen, labelKey: 'learn' as const, match: '/learn' },
  { href: '/app/chat/tutor', icon: MessageSquare, labelKey: 'chat' as const, match: '/app/chat' },
  { href: '/app/exams', icon: FileText, labelKey: 'exams' as const, match: '/app/exams' },
  { href: '/app/quiz', icon: ClipboardCheck, labelKey: 'quiz' as const, match: '/app/quiz' },
  { href: '/app/memory', icon: Brain, labelKey: 'memory' as const },
  { href: '/app/progress', icon: TrendingUp, labelKey: 'progress' as const },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { messages } = useI18n();

  return (
    <aside className="hidden w-56 shrink-0 border-e border-border bg-surface-1/40 backdrop-blur-md md:block">
      <nav className="flex flex-col gap-1 p-4" aria-label={messages.common.appNavigation}>
        {items.map((item) => {
          const matchPath = item.match ?? item.href;
          const active = pathname === item.href || pathname.startsWith(matchPath);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                active
                  ? 'font-semibold text-foreground'
                  : 'text-muted-foreground hover:bg-surface-2/60 hover:text-foreground',
              )}
            >
              {active ? (
                <span
                  className="absolute inset-y-2 start-0 w-0.5 rounded-full bg-gradient-to-b from-primary via-accent-magenta to-accent-cyan"
                  aria-hidden
                />
              ) : null}
              <Icon
                className={cn(
                  'h-4 w-4 shrink-0',
                  active
                    ? 'text-primary'
                    : 'text-muted-foreground group-hover:text-foreground',
                )}
                aria-hidden
              />
              {messages.nav[item.labelKey]}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
