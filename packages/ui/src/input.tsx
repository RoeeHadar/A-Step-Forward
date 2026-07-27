import * as React from 'react';

import { cn } from './index';

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => <input ref={ref} className={cn(className)} {...props} />,
);
Input.displayName = 'Input';
