'use client';

import React from 'react';
import Link from 'next/link';
import type { Route } from 'next';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  MessageSquare,
  BookOpen,
  Brain,
  TrendingUp,
} from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';

const items: { href: Route; icon: React.ElementType; labelKey: 'dashboard' | 'chat' | 'lessons' | 'memory' | 'progress'; match?: string }[] = [
  { href: '/app', icon: LayoutDashboard, labelKey: 'dashboard' },
  { href: '/app/chat/tutor', icon: MessageSquare, labelKey: 'chat', match: '/app/chat' },
  { href: '/app/lessons/lesson-intro-fractions', icon: BookOpen, labelKey: 'lessons', match: '/app/lessons' },
  { href: '/app/memory', icon: Brain, labelKey: 'memory' },
  { href: '/app/progress', icon: TrendingUp, labelKey: 'progress' },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { messages } = useI18n();

  return (
    <aside className="hidden w-56 shrink-0 border-r border-border bg-muted/30 md:block">
      <nav className="flex flex-col gap-1 p-4" aria-label="App navigation">
        {items.map((item) => {
          const matchPath = item.match ?? item.href;
          const active = pathname === item.href || pathname.startsWith(matchPath);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-muted',
                active ? 'bg-muted font-medium text-foreground' : 'text-muted-foreground',
              )}
            >
              <Icon className="h-4 w-4" aria-hidden />
              {messages.nav[item.labelKey]}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
