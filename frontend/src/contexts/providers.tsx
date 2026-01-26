'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState, useEffect } from 'react';
import { ThemeProvider } from './ThemeContext';
import { ProductivityProvider } from '@/components/ProductivityProvider';
import { DraftCleanupProvider } from '@/components/providers/draft-cleanup-provider';
import { PushNotificationProvider } from '@/features/notifications';
import { cleanupExpiredDrafts } from '@/hooks/useAutoSave';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30 * 1000, // 30 segundos
            gcTime: 5 * 60 * 1000, // 5 minutos
            retry: 1,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 0,
          },
        },
      })
  );

  // Limpar rascunhos expirados na inicialização
  useEffect(() => {
    cleanupExpiredDrafts();
  }, []);

  return (
    <ThemeProvider defaultTheme="dark" storageKey="conecta-pro-theme">
      <QueryClientProvider client={queryClient}>
        <PushNotificationProvider>
          <DraftCleanupProvider>
            <ProductivityProvider>
              {children}
            </ProductivityProvider>
          </DraftCleanupProvider>
        </PushNotificationProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
