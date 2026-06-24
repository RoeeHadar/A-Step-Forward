import { NextResponse } from 'next/server';
import { API_BASE_URL } from '@/lib/api';

export const runtime = 'nodejs';

export async function GET() {
  try {
    await fetch(`${API_BASE_URL}/v1/warmup`, {
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    // best-effort — ignore failures
  }
  return NextResponse.json({ status: 'ok' });
}
