'use client';

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Soft-refresh the current RSC page when the tab becomes visible again, and on
 * a slow interval while focused — so Memory / Progress reflect plan changes,
 * mastery bumps, and persona writes without requiring a manual refresh.
 */
export function usePageLiveRefresh(intervalMs = 45_000) {
  const router = useRouter();
  const lastRefresh = useRef(0);

  useEffect(() => {
    const refresh = () => {
      const now = Date.now();
      if (now - lastRefresh.current < 8_000) return;
      lastRefresh.current = now;
      router.refresh();
    };

    const onVisible = () => {
      if (document.visibilityState === 'visible') refresh();
    };

    document.addEventListener('visibilitychange', onVisible);
    window.addEventListener('focus', onVisible);
    const id = window.setInterval(() => {
      if (document.visibilityState === 'visible') refresh();
    }, intervalMs);

    return () => {
      document.removeEventListener('visibilitychange', onVisible);
      window.removeEventListener('focus', onVisible);
      window.clearInterval(id);
    };
  }, [router, intervalMs]);
}
