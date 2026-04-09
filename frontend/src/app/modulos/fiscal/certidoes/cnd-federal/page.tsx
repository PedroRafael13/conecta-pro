'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

/**
 * Subpágina CND Federal — redireciona para o painel principal de certidões.
 * O painel principal já exibe a CND Federal com botão "Buscar" individual.
 */
export default function CndFederalPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/modulos/fiscal/certidoes');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <p className="text-sm text-[hsl(var(--muted-foreground))]">Redirecionando...</p>
    </div>
  );
}
