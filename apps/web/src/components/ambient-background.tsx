'use client';

import type { CSSProperties } from 'react';
import { cn } from '@asf/ui';
import { useScrollProgress } from '@/hooks/use-scroll-y';

/**
 * Subtle ambient canvas — soft, warm natural light washes + a faint masked
 * dot grid. Orb strength eases down as the user scrolls so content stays focal.
 * Purely decorative; sits behind content via a negative z-index. The parent
 * must be `relative` (and ideally `isolate`) for the layering to work.
 */
export function AmbientBackground({
  variant = 'subtle',
  className,
}: {
  variant?: 'subtle' | 'hero';
  className?: string;
}) {
  const hero = variant === 'hero';
  const scrollProgress = useScrollProgress(hero ? 600 : 400);
  // Orbs soften as you scroll — canvas recedes, content advances.
  const orbStrength = 1 - scrollProgress * 0.45;
  const gridOpacity = 0.28 + scrollProgress * 0.12;

  return (
    <div
      aria-hidden
      className={cn('pointer-events-none absolute inset-0 -z-10 overflow-hidden', className)}
      style={{ '--ambient-strength': orbStrength } as CSSProperties}
    >
      <div
        className={cn(
          'orb-violet absolute rounded-full transition-opacity duration-300',
          hero
            ? 'orb-float -start-32 -top-40 h-[520px] w-[520px]'
            : '-start-40 -top-48 h-[360px] w-[360px]',
        )}
        style={{ opacity: (hero ? 1 : 0.6) * orbStrength }}
      />
      <div
        className={cn(
          'orb-cyan absolute rounded-full transition-opacity duration-300',
          hero
            ? 'orb-float -end-24 top-10 h-[460px] w-[460px]'
            : '-end-40 top-0 h-[320px] w-[320px]',
        )}
        style={{ opacity: (hero ? 1 : 0.5) * orbStrength, animationDelay: '-7s' }}
      />
      {hero ? (
        <div
          className="orb-float orb-magenta absolute bottom-[-120px] start-1/2 h-[420px] w-[720px] -translate-x-1/2 rounded-full transition-opacity duration-300"
          style={{ opacity: orbStrength, animationDelay: '-14s' }}
        />
      ) : null}
      <div
        className="bg-dot-grid absolute inset-0 transition-opacity duration-300"
        style={{ opacity: gridOpacity }}
      />
    </div>
  );
}
