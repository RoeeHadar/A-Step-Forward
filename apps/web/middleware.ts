import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/health',
]);

const isAdminRoute = createRouteMatcher(['/admin(.*)']);
const isEducatorRoute = createRouteMatcher(['/educator(.*)']);

function securityHeaders(nonce: string, childMode: boolean): Record<string, string> {
  const connectSrc = [
    "'self'",
    'https://*.clerk.accounts.dev',
    'https://api.clerk.com',
    process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000',
  ];
  if (childMode) {
    // COPPA: no third-party analytics or tracking endpoints in child mode.
    connectSrc.splice(1);
  }

  return {
    'Content-Security-Policy': [
      "default-src 'self'",
      `script-src 'self' 'nonce-${nonce}' https://*.clerk.accounts.dev https://challenges.cloudflare.com`,
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob: https://*.clerk.com https://img.clerk.com",
      "font-src 'self' data:",
      `connect-src ${connectSrc.join(' ')}`,
      'frame-src https://*.clerk.accounts.dev https://challenges.cloudflare.com',
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
    ].join('; '),
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'X-Content-Type-Options': 'nosniff',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  };
}

export default clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth().protect();
  }

  const { sessionClaims } = auth();
  const metadata = (sessionClaims?.metadata ?? {}) as {
    role?: string;
    child_mode?: boolean;
    age?: number;
  };
  const role = metadata.role ?? 'learner';
  const childMode =
    metadata.child_mode === true ||
    (typeof metadata.age === 'number' && metadata.age < 13);

  if (isAdminRoute(request) && role !== 'admin') {
    return NextResponse.redirect(new URL('/app', request.url));
  }

  if (isEducatorRoute(request) && role !== 'educator' && role !== 'admin') {
    return NextResponse.redirect(new URL('/app', request.url));
  }

  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-nonce', nonce);

  const response = NextResponse.next({
    request: { headers: requestHeaders },
  });

  for (const [key, value] of Object.entries(securityHeaders(nonce, childMode))) {
    response.headers.set(key, value);
  }

  return response;
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
    '/__clerk/:path*',
  ],
};
