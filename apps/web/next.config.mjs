// M4: Content-Security-Policy in REPORT-ONLY mode. Browsers log violations to
// the console but block nothing, so this cannot break Clerk sign-in. Check the
// console on a Vercel preview (signed in and out) before switching to an
// enforcing Content-Security-Policy header. Clerk dev instances load from
// *.clerk.accounts.dev; a Clerk production instance would use clerk.<domain>.
const CLERK_HOSTS = 'https://*.clerk.accounts.dev https://*.clerk.com';
const cspReportOnly = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline' ${CLERK_HOSTS} https://challenges.cloudflare.com https://vercel.live`,
  `connect-src 'self' ${CLERK_HOSTS} https://clerk-telemetry.com https://vercel.live wss://ws-us3.pusher.com`,
  "img-src 'self' data: blob: https:",
  "style-src 'self' 'unsafe-inline'",
  "font-src 'self' data:",
  `frame-src 'self' https: ${CLERK_HOSTS} https://challenges.cloudflare.com https://vercel.live`,
  "worker-src 'self' blob:",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join('; ');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Don't advertise the framework in an X-Powered-By header (M4).
  poweredByHeader: false,
  // ESM-only packages that Next.js must transpile to CommonJS for the build.
  // react-markdown v9+, remark-*, rehype-* are all pure-ESM.
  transpilePackages: [
    '@asf/ui',
    '@asf/schemas',
    'react-markdown',
    'remark-gfm',
    'remark-math',
    'rehype-katex',
    'rehype-highlight',
    'unified',
    'bail',
    'is-plain-obj',
    'trough',
    'vfile',
    'vfile-message',
    'unist-util-stringify-position',
    'mdast-util-from-markdown',
    'mdast-util-to-markdown',
    'mdast-util-gfm',
    'mdast-util-math',
    'micromark',
    'micromark-util-combine-extensions',
    'micromark-extension-gfm',
    'micromark-extension-math',
  ],
  experimental: {},
  async redirects() {
    return [
      { source: '/learn/calculus', destination: '/learn/calculus_1', permanent: false },
      { source: '/learn/high_school_math_3_points', destination: '/learn/high_school_math_3pt', permanent: false },
      { source: '/learn/high_school_math_4_points', destination: '/learn/high_school_math_4pt', permanent: false },
      { source: '/learn/high_school_math_5_points', destination: '/learn/high_school_math_5pt', permanent: false },
      { source: '/learn/university_prep', destination: '/learn/makhina', permanent: false },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains; preload',
          },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
          { key: 'Content-Security-Policy-Report-Only', value: cspReportOnly },
        ],
      },
    ];
  },
};

export default nextConfig;
