'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState, useEffect } from 'react';
import { ThemeProvider } from './ThemeContext';
import { ProductivityProvider } from '@/components/ProductivityProvider';
import { DraftCleanupProvider } from '@/components/providers/draft-cleanup-provider';
import { PushNotificationProvider } from '@/features/notifications';
import { cleanupExpiredDrafts } from '@/hooks/useAutoSave';
import { toast } from '@/components/ui/use-toast';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Extrai mensagem de erro de diferentes tipos de erro
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }
  return 'Erro desconhecido';
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
            onError: (error) => {
              toast({
                title: "Erro na operação",
                description: getErrorMessage(error),
                variant: "destructive",
              });
            },
            // onSuccess pode ser sobrescrito por mutation individual
            // usando meta: { showSuccessToast: false } nas options
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
