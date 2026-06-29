/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
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
      { source: '/learn/biology', destination: '/learn/biology_4pt', permanent: false },
      { source: '/learn/biology-4pt', destination: '/learn/biology_4pt', permanent: false },
      { source: '/learn/biology-5pt', destination: '/learn/biology_5pt', permanent: false },
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
        ],
      },
    ];
  },
};

export default nextConfig;
