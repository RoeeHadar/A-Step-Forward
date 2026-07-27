import * as React from 'react';

import { cn } from './index';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number | null;
}

export function Progress({ className, value = 0, ...props }: ProgressProps) {
  const pct = Math.max(0, Math.min(100, Number(value ?? 0)));
  return (
    <div className={cn(className)} {...props}>
      <div style={{ width: `${pct}%` }} />
    </div>
  );
}
