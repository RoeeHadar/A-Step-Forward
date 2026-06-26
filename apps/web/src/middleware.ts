import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/health',
  '/api/debug-auth',
  '/api/debug/env-status',
  '/lessons(.*)',
  '/learn(.*)',
  '/book',
  '/api/book',
]);

const isAdminRoute = createRouteMatcher(['/admin(.*)']);
const isEducatorRoute = createRouteMatcher(['/educator(.*)']);

export default clerkMiddleware(async (auth, request) => {
  const { userId, sessionClaims } = auth();
  const isApiRoute = request.nextUrl.pathname.startsWith('/api/');

  if (!isPublicRoute(request) && !userId) {
    // API routes MUST return a clean 401 — never an HTML redirect. Without
    // this, fetch-based clients (useChat, react-query, etc.) follow the
    // redirect and try to parse the sign-in HTML page as their expected
    // content (JSON / SSE / AI data stream), surfacing as opaque
    // "network hiccup" errors to the user.
    if (isApiRoute) {
      return NextResponse.json(
        { error: 'unauthorized', message: 'Authentication required' },
        { status: 401 },
      );
    }
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
    return isApiRoute
      ? NextResponse.json({ error: 'forbidden' }, { status: 403 })
      : NextResponse.redirect(new URL('/app', request.url));
  }

  if (isEducatorRoute(request) && role !== 'educator' && role !== 'admin') {
    return isApiRoute
      ? NextResponse.json({ error: 'forbidden' }, { status: 403 })
      : NextResponse.redirect(new URL('/app', request.url));
  }
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
    '/__clerk/:path*',
  ],
};
