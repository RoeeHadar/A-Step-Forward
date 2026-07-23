import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/health',
  '/api/cron/(.*)',
  '/lessons(.*)',
  '/learn(.*)',
  '/book(.*)',
  '/api/book',
  '/api/book/availability',
  '/api/book/r/(.*)',
  '/api/book/gcal/webhook',
  '/api/book/gcal/oauth/callback',
  '/app/lessons(.*)',
  '/progress/share(.*)',
  '/api/progress/public-share',
]);

// NOTE: Do NOT gate /admin or /educator in middleware on Clerk JWT role.
// publicMetadata.role in the Clerk dashboard can say "admin" while the
// session JWT still says "learner" until the next sign-in/refresh.
// Pages and /api/admin/* routes enforce via getAuthContext() + requireRole()
// (currentUser() reads live publicMetadata, not the stale JWT claim).

export default clerkMiddleware(async (auth, request) => {
  const { userId } = auth();
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
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
    '/__clerk/:path*',
  ],
};
