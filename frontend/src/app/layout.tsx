import type { Metadata, Viewport } from 'next';
import { Providers } from '@/contexts/providers';
import { Toaster } from '@/components/ui/toaster';
import { BartoloChat } from '@/components/BartoloChat';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: {
    default: 'Conecta PRO',
    template: '%s | Conecta PRO',
  },
  description: 'Sistema ERP para gestão de vigilância e segurança patrimonial',
  keywords: ['ERP', 'vigilância', 'segurança', 'gestão', 'Conecta PRO'],
  authors: [{ name: 'Jordan Santos de Jesus LTDA' }],
  robots: 'noindex, nofollow',
  icons: {
    icon: '/favicon.ico',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#0a0c10',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className="dark">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Conecta PRO" />
      </head>
      <body className="min-h-screen bg-[hsl(var(--background))] antialiased">
        <Providers>
          {children}
          <Toaster />
          <BartoloChat />
        </Providers>
      </body>
    </html>
  );
}
