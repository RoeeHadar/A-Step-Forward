import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

// Temporary diagnostic endpoint — remove after fix is confirmed
export async function GET() {
  const env = {
    clerkPublishableKeyPresent: !!(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.startsWith('pk_')),
    clerkSecretKeyPresent: !!(process.env.CLERK_SECRET_KEY?.startsWith('sk_')),
    clerkPublishableKeyPrefix: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.slice(0, 12) ?? 'missing',
  };

  try {
    const authObj = await auth();
    return NextResponse.json({ ok: true, hasUserId: !!authObj.userId, ...env });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err), ...env }, { status: 500 });
  }
}
