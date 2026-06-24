import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

// Temporary diagnostic endpoint — remove after fix is confirmed
export async function GET() {
  try {
    const authObj = await auth();
    return NextResponse.json({
      ok: true,
      hasUserId: !!authObj.userId,
      clerkKeyPresent: !!(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.startsWith('pk_')),
      clerkSecretPresent: !!(process.env.CLERK_SECRET_KEY?.startsWith('sk_')),
    });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}
