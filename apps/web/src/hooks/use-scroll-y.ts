'use client';

import { useEffect, useState } from 'react';

/** True once the window has scrolled past `threshold` px. */
export function useScrollY(threshold = 8): boolean {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > threshold);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [threshold]);

  return scrolled;
}

/** Normalized scroll progress 0–1 over the first `max` px of scroll. */
export function useScrollProgress(max = 400): number {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const onScroll = () => setProgress(Math.min(1, window.scrollY / max));
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [max]);

  return progress;
}
