import * as React from 'react';

import { cn } from './index';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning' | 'destructive';
}

export function Badge({ className, ...props }: BadgeProps) {
  return <span className={cn(className)} {...props} />;
}
