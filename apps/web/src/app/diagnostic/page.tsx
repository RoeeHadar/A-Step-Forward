'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/** Legacy route — diagnostic removed; send learners to plan setup or app. */
export default function DiagnosticRedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/plan-setup');
  }, [router]);
  return null;
}
