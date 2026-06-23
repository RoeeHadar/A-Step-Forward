import type { Metadata, Viewport } from 'next';
import { AppProviders } from '@/providers/app-providers';
import './globals.css';

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://astepforward.app';

const title = 'A Step Forward — an AI learning center that remembers you';
const description =
  'A small team of AI agents — Tutor, Mentor, Coach, Reviewer — that teaches you, assesses you, remembers what you’ve learned, and adapts. Open source, MIT, multi-language.';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: title,
    template: '%s · A Step Forward',
  },
  description,
  applicationName: 'A Step Forward',
  authors: [{ name: 'Roee Hadar' }],
  keywords: [
    'AI tutor',
    'AI learning',
    'AI agents',
    'GraphRAG',
    'memory',
    'education',
    'open source',
  ],
  openGraph: {
    type: 'website',
    url: siteUrl,
    siteName: 'A Step Forward',
    title,
    description,
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
        alt: 'A Step Forward — an AI learning center that remembers you',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title,
    description,
    images: ['/og.png'],
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0b0b0d' },
  ],
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className="h-full">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
