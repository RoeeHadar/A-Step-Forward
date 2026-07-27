import * as React from 'react';

import { cn } from './index';

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => <textarea ref={ref} className={cn(className)} {...props} />,
);
Textarea.displayName = 'Textarea';
