import { cn } from '@asf/ui';

/**
 * Signature "A Step Forward" motif — an ascending stepped path with pulsing
 * nodes. Represents learning progression, the weekly plan, and mastery growth.
 * Purely decorative; respects prefers-reduced-motion via CSS.
 */
export function GrowthPathMotif({
  className,
  variant = 'default',
}: {
  className?: string;
  /** `hero` = larger, more visible; `subtle` = faint background wash */
  variant?: 'default' | 'hero' | 'subtle';
}) {
  const faint = variant === 'subtle';
  const hero = variant === 'hero';

  return (
    <svg
      viewBox="0 0 200 120"
      fill="none"
      aria-hidden
      className={cn(
        'pointer-events-none select-none',
        faint && 'opacity-[0.18] dark:opacity-[0.28]',
        !faint && !hero && 'opacity-40 dark:opacity-50',
        hero && 'opacity-55 dark:opacity-65',
        className,
      )}
    >
      {/* Ascending stepped path */}
      <path
        d="M 8 104 H 52 V 76 H 96 V 48 H 140 V 20 H 192"
        className="growth-path-stroke"
        stroke="hsl(var(--primary))"
        strokeWidth={hero ? 2.5 : 2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Step nodes — each lights up in sequence */}
      {[
        { cx: 8, cy: 104, delay: '0s' },
        { cx: 52, cy: 76, delay: '-1.2s' },
        { cx: 96, cy: 48, delay: '-2.4s' },
        { cx: 140, cy: 20, delay: '-3.6s' },
        { cx: 192, cy: 20, delay: '-4.8s' },
      ].map(({ cx, cy, delay }) => (
        <g key={`${cx}-${cy}`}>
          <circle
            cx={cx}
            cy={cy}
            r={hero ? 5 : 4}
            className="growth-path-node"
            style={{ animationDelay: delay }}
            fill="hsl(var(--primary))"
          />
          <circle
            cx={cx}
            cy={cy}
            r={hero ? 9 : 7}
            className="growth-path-node-ring"
            style={{ animationDelay: delay }}
            stroke="hsl(var(--accent-amber))"
            strokeWidth={1.5}
          />
        </g>
      ))}
    </svg>
  );
}
