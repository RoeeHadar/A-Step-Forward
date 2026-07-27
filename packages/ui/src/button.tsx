import * as React from 'react';

import { cn } from './index';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  size?: 'default' | 'sm' | 'lg' | 'icon';
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'link';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ asChild: _asChild, className, type = 'button', ...props }, ref) => (
    <button ref={ref} type={type} className={cn(className)} {...props} />
  ),
);
Button.displayName = 'Button';
