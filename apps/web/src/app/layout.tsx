import type { Metadata, Viewport } from 'next';

import { Heebo, Inter, Frank_Ruhl_Libre, Newsreader } from 'next/font/google';

import { AppProviders } from '@/providers/app-providers';
import { getServerLocale } from '@/i18n/locale-server';
import { localeDir } from '@/i18n/locale-storage';

import './globals.css';

const heebo = Heebo({ subsets: ['hebrew', 'latin'], variable: '--font-heebo', display: 'swap' });
const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });
// Editorial serif display face — covers Hebrew + Latin for the "grown, not
// generated" headline voice.
const frankRuhl = Frank_Ruhl_Libre({
  subsets: ['hebrew', 'latin'],
  weight: ['500', '700', '900'],
  variable: '--font-frank-ruhl',
  display: 'swap',
});
const newsreader = Newsreader({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  style: ['normal', 'italic'],
  variable: '--font-newsreader',
  display: 'swap',
});

export const dynamic = 'force-dynamic';

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://astepforward.app';

const title = 'A Step Forward \u2013 an AI learning center that remembers you';

const description =
  'A small team of AI agents \u2013 Tutor, Mentor, Coach, Reviewer \u2013 that teaches you, assesses you, remembers what you\u2019ve learned, and adapts. Personalized weekly plans, bilingual Hebrew and English.';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: title, template: '%s \u00b7 A Step Forward' },
  description,
  applicationName: 'A Step Forward',
  authors: [{ name: 'Roee Hadar' }],
  keywords: ['AI tutor', 'AI learning', 'AI agents', 'Bagrut prep', 'memory', 'education', 'Hebrew'],
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
    { media: '(prefers-color-scheme: light)', color: '#f6f1e7' },
    { media: '(prefers-color-scheme: dark)', color: '#141a17' },
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
      className={`${heebo.variable} ${inter.variable} ${frankRuhl.variable} ${newsreader.variable} h-full dark`}
    >
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        <AppProviders initialLocale={locale}>{children}</AppProviders>
      </body>
    </html>
  );
}
