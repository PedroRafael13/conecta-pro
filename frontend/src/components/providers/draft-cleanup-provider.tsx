'use client';

import { useEffect } from 'react';
import { cleanupExpiredDrafts } from '@/hooks/useAutoSave';

/**
 * Provider para limpar rascunhos expirados na inicializacao
 * Deve ser montado uma vez no layout principal
 */
export function DraftCleanupProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Limpar rascunhos expirados ao montar
    cleanupExpiredDrafts();

    // Configurar limpeza periodica (a cada 1 hora)
    const interval = setInterval(() => {
      cleanupExpiredDrafts();
    }, 60 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return <>{children}</>;
}
