import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/health',
  '/api/debug-auth',
  '/api/debug/concept-content',
  '/lessons(.*)',
  '/learn(.*)',
  '/book',
  '/api/book',
]);

const isAdminRoute = createRouteMatcher(['/admin(.*)']);
const isEducatorRoute = createRouteMatcher(['/educator(.*)']);

export default clerkMiddleware(async (auth, request) => {
  const { userId, sessionClaims } = auth();

  if (!isPublicRoute(request) && !userId) {
    const signInUrl = new URL('/sign-in', request.url);
    signInUrl.searchParams.set('redirect_url', request.url);
    return NextResponse.redirect(signInUrl);
  }
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
