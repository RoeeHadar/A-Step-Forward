'use client';

import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

export function Marquee({
  children,
  speed = 30,
  className = '',
}: {
  children: ReactNode;
  speed?: number;
  className?: string;
}) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <motion.div
        className="flex shrink-0 gap-4 whitespace-nowrap"
        animate={{ x: ['0%', '-50%'] }}
        transition={{ duration: speed, ease: 'linear', repeat: Infinity }}
      >
        <div className="flex shrink-0 gap-4">{children}</div>
        <div className="flex shrink-0 gap-4" aria-hidden>
          {children}
        </div>
      </motion.div>
      <div className="pointer-events-none absolute inset-y-0 start-0 w-16 bg-gradient-to-e from-background to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 end-0 w-16 bg-gradient-to-w from-background to-transparent" />
    </div>
  );
}
