import { cn } from '@asf/ui';

/** Node layout for the memory / knowledge-graph constellation motif. */
const NODES = [
  { cx: 50, cy: 30, r: 5, delay: '0s', fill: 'primary' },
  { cx: 120, cy: 22, r: 4, delay: '-0.8s', fill: 'accent-cyan' },
  { cx: 170, cy: 55, r: 5, delay: '-1.6s', fill: 'accent-amber' },
  { cx: 90, cy: 70, r: 6, delay: '-2.4s', fill: 'primary' },
  { cx: 30, cy: 80, r: 4, delay: '-3.2s', fill: 'accent-magenta' },
  { cx: 150, cy: 95, r: 4, delay: '-4s', fill: 'accent-cyan' },
] as const;

const EDGES: Array<[number, number]> = [
  [0, 1],
  [1, 2],
  [1, 3],
  [0, 3],
  [3, 4],
  [3, 5],
  [2, 5],
];

const fillVar: Record<(typeof NODES)[number]['fill'], string> = {
  primary: 'hsl(var(--primary))',
  'accent-cyan': 'hsl(var(--accent-cyan))',
  'accent-amber': 'hsl(var(--accent-amber))',
  'accent-magenta': 'hsl(var(--accent-magenta))',
};

/**
 * Signature memory motif — connected nodes that pulse gently, evoking the
 * knowledge graph + persistent learner memory that makes this platform unique.
 */
export function MemoryConstellation({
  className,
  variant = 'default',
}: {
  className?: string;
  variant?: 'default' | 'subtle';
}) {
  const faint = variant === 'subtle';

  return (
    <svg
      viewBox="0 0 200 120"
      fill="none"
      aria-hidden
      className={cn(
        'pointer-events-none select-none',
        faint ? 'opacity-25 dark:opacity-35' : 'opacity-50 dark:opacity-60',
        className,
      )}
    >
      {EDGES.map(([a, b], i) => {
        const na = NODES[a];
        const nb = NODES[b];
        if (!na || !nb) return null;
        return (
          <line
            key={i}
            x1={na.cx}
            y1={na.cy}
            x2={nb.cx}
            y2={nb.cy}
            stroke="hsl(var(--border-bright))"
            strokeWidth={1}
            className="memory-edge"
            style={{ animationDelay: `${-i * 0.4}s` }}
          />
        );
      })}
      {NODES.map(({ cx, cy, r, delay, fill }, i) => (
        <circle
          key={i}
          cx={cx}
          cy={cy}
          r={r}
          className="memory-node"
          style={{ animationDelay: delay }}
          fill={fillVar[fill]}
        />
      ))}
    </svg>
  );
}
