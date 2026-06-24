'use client';

import { motion, useReducedMotion } from 'framer-motion';
import { Card } from '@asf/ui/card';
import { cn } from '@asf/ui';
import type { HTMLAttributes } from 'react';

type MotionCardProps = HTMLAttributes<HTMLDivElement> & {
  hoverScale?: number;
};

export function MotionCard({ className, hoverScale = 1.02, children, ...props }: MotionCardProps) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      whileHover={reduceMotion ? undefined : { scale: hoverScale }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      className="h-full"
    >
      <Card className={cn('h-full transition-shadow hover:shadow-md', className)} {...props}>
        {children}
      </Card>
    </motion.div>
  );
}
