import type { Metadata, Viewport } from 'next';
import { Heebo, Inter } from 'next/font/google';
import { AppProviders } from '@/providers/app-providers';
import { getServerLocale } from '@/i18n/locale-server';
import { localeDir } from '@/i18n/locale-storage';
import './globals.css';

const heebo = Heebo({ subsets: ['hebrew', 'latin'], variable: '--font-heebo', display: 'swap' });
const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });

export const dynamic = 'force-dynamic';

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://astepforward.app';
const title = 'A Step Forward ? an AI learning center that remembers you';
const description =
  "A small team of AI agents ? Tutor, Mentor, Coach, Reviewer ? that teaches you, assesses you, remembers what you've learned, and adapts. Open source, MIT, multi-language.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: title, template: '%s · A Step Forward' },
  description,
  applicationName: 'A Step Forward',
  authors: [{ name: 'Roee Hadar' }],
  keywords: ['AI tutor', 'AI learning', 'AI agents', 'GraphRAG', 'memory', 'education', 'open source'],
  openGraph: { type: 'website', url: siteUrl, siteName: 'A Step Forward', title, description, images: [{ url: '/og.png', width: 1200, height: 630, alt: title }] },
  twitter: { card: 'summary_large_image', title, description, images: ['/og.png'] },
  robots: { index: true, follow: true },
  icons: { icon: '/favicon.ico', apple: '/apple-touch-icon.png' },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0b0b0d' },
  ],
  width: 'device-width',
  initialScale: 1,
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = await getServerLocale();
  const dir = localeDir(locale);

  return (
    <html lang={locale} dir={dir} suppressHydrationWarning className={`${heebo.variable} ${inter.variable} h-full`}>
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        <AppProviders initialLocale={locale}>{children}</AppProviders>
      </body>
    </html>
  );
}
