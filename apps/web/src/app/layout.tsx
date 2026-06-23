import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'A Step Forward',
  description: 'AI-native learning center.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-screen bg-background text-foreground antialiased">{children}</body>
    </html>
  );
}
