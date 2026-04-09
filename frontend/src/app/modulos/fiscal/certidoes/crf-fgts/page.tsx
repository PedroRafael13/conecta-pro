'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

/**
 * Subpágina CRF/FGTS — redireciona para o painel principal de certidões.
 * O painel principal já exibe a CRF/FGTS com botão "Buscar" individual.
 */
export default function CrfFgtsPage() {
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
