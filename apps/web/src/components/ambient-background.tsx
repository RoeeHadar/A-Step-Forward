import { cn } from '@asf/ui';

/**
 * Subtle ambient canvas — soft, warm natural light washes + a faint masked
 * dot grid — that gives inner pages gentle depth without competing with
 * content. Purely decorative; sits behind content via a negative z-index. The
 * parent must be `relative` (and ideally `isolate`) for the layering to work.
 *
 * Use `variant="hero"` for focal, above-the-fold moments and the default
 * `"subtle"` for everyday app/content pages.
 */
export function AmbientBackground({
  variant = 'subtle',
  className,
}: {
  variant?: 'subtle' | 'hero';
  className?: string;
}) {
  const hero = variant === 'hero';

  return (
    <div
      aria-hidden
      className={cn('pointer-events-none absolute inset-0 -z-10 overflow-hidden', className)}
    >
      <div
        className={cn(
          'orb-violet absolute rounded-full',
          hero
            ? 'orb-float -start-32 -top-40 h-[520px] w-[520px]'
            : '-start-40 -top-48 h-[360px] w-[360px] opacity-60',
        )}
      />
      <div
        className={cn(
          'orb-cyan absolute rounded-full',
          hero
            ? 'orb-float -end-24 top-10 h-[460px] w-[460px]'
            : '-end-40 top-0 h-[320px] w-[320px] opacity-50',
        )}
        style={{ animationDelay: '-7s' }}
      />
      {hero ? (
        <div
          className="orb-float orb-magenta absolute bottom-[-120px] start-1/2 h-[420px] w-[720px] -translate-x-1/2 rounded-full"
          style={{ animationDelay: '-14s' }}
        />
      ) : null}
      <div className="bg-dot-grid absolute inset-0 opacity-30 dark:opacity-40" />
    </div>
  );
}
