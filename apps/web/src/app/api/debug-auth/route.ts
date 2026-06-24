import { NextResponse } from 'next/server';
import { headers } from 'next/headers';
import { auth } from '@clerk/nextjs/server';

// Temporary diagnostic endpoint — remove after fix is confirmed
export async function GET() {
  const headersList = await headers();
  const allHeaders: Record<string, string> = {};
  headersList.forEach((value, key) => {
    if (key.startsWith('x-clerk') || key.startsWith('clerk') || key.startsWith('authorization')) {
      allHeaders[key] = value.slice(0, 20) + '...';
    }
  });

  const env = {
    clerkPublishableKeyPresent: !!(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.startsWith('pk_')),
    clerkSecretKeyPresent: !!(process.env.CLERK_SECRET_KEY?.startsWith('sk_')),
    clerkPublishableKeyPrefix: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.slice(0, 12) ?? 'missing',
    clerkHeaders: allHeaders,
  };

  try {
    const authObj = await auth();
    return NextResponse.json({ ok: true, hasUserId: !!authObj.userId, ...env });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err), ...env }, { status: 500 });
  }
}
