import type { Metadata, Viewport } from 'next';

import { Heebo, Inter, Space_Grotesk } from 'next/font/google';

import { AppProviders } from '@/providers/app-providers';
import { getServerLocale } from '@/i18n/locale-server';
import { localeDir } from '@/i18n/locale-storage';

import './globals.css';

const heebo = Heebo({ subsets: ['hebrew', 'latin'], variable: '--font-heebo', display: 'swap' });
const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });
const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  weight: ['600', '700'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

export const dynamic = 'force-dynamic';

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://astepforward.app';

const title = 'A Step Forward \u2013 an AI learning center that remembers you';

const description =
  'A small team of AI agents \u2013 Tutor, Mentor, Coach, Reviewer \u2013 that teaches you, assesses you, remembers what you\u2019ve learned, and adapts. Open source, MIT, multi-language.';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: title, template: '%s \u00b7 A Step Forward' },
  description,
  applicationName: 'A Step Forward',
  authors: [{ name: 'Roee Hadar' }],
  keywords: ['AI tutor', 'AI learning', 'AI agents', 'GraphRAG', 'memory', 'education', 'open source'],
  openGraph: {
    type: 'website',
    url: siteUrl,
    siteName: 'A Step Forward',
    title,
    description,
    images: [{ url: '/og.png', width: 1200, height: 630, alt: title }],
  },
  twitter: { card: 'summary_large_image', title, description, images: ['/og.png'] },
  robots: { index: true, follow: true },
  icons: { icon: '/favicon.ico', apple: '/apple-touch-icon.png' },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f1113' },
  ],
  width: 'device-width',
  initialScale: 1,
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = await getServerLocale();
  const dir = localeDir(locale);

  return (
    <html
      lang={locale}
      dir={dir}
      suppressHydrationWarning
      className={`${heebo.variable} ${inter.variable} ${spaceGrotesk.variable} h-full`}
    >
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        <AppProviders initialLocale={locale}>{children}</AppProviders>
      </body>
    </html>
  );
}
