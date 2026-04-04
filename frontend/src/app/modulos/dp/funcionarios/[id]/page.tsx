'use client';

import { useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';

/**
 * Rota /modulos/dp/funcionarios/[id]
 * Redireciona para a listagem de funcionários com o modal do funcionário aberto.
 */
export default function FuncionarioDetalhe() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;

  useEffect(() => {
    if (id) {
      router.replace(`/modulos/dp/funcionarios?funcionario=${id}`);
    } else {
      router.replace('/modulos/dp/funcionarios');
    }
  }, [id, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  );
}
