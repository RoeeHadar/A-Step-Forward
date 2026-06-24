import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/health',
  '/api/debug-auth',
  '/lessons(.*)',
]);

const isAdminRoute = createRouteMatcher(['/admin(.*)']);
const isEducatorRoute = createRouteMatcher(['/educator(.*)']);

export default clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect();
  }

  const { sessionClaims } = await auth();
  const metadata = (sessionClaims?.metadata ?? {}) as {
    role?: string;
    child_mode?: boolean;
    age?: number;
  };
  const role = metadata.role ?? 'learner';

  if (isAdminRoute(request) && role !== 'admin') {
    return NextResponse.redirect(new URL('/app', request.url));
  }

  if (isEducatorRoute(request) && role !== 'educator' && role !== 'admin') {
    return NextResponse.redirect(new URL('/app', request.url));
  }
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
    '/__clerk/:path*',
  ],
};
