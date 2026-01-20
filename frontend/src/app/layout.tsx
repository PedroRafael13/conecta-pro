import type { Metadata, Viewport } from 'next';
import { Providers } from '@/contexts/providers';
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
      <body className="min-h-screen bg-[hsl(var(--background))] antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
