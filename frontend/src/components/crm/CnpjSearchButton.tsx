'use client';
import { useEnrichCNPJ } from '@/hooks/crm/useEnrichment';
import type { CNPJEnrichment } from '@/types/crm/enrichment';

interface Props {
  cnpj: string;
  disabled?: boolean;
  onSuccess: (data: CNPJEnrichment) => void;
  onError?: (msg: string) => void;
}

export function CnpjSearchButton({ cnpj, disabled, onSuccess, onError }: Props) {
  const mutation = useEnrichCNPJ();

  const handleClick = async () => {
    const digits = cnpj.replace(/\D/g, '');
    if (digits.length !== 14) {
      onError?.('CNPJ deve ter 14 dígitos');
      return;
    }
    try {
      const data = await mutation.mutateAsync(cnpj);
      onSuccess(data);
    } catch (e: any) {
      const status = e?.response?.status ?? e?.status;
      const detail = e?.response?.data?.detail ?? e?.detail;
      if (status === 404) onError?.('CNPJ não encontrado na Receita Federal');
      else if (status === 422) onError?.('Formato de CNPJ inválido');
      else if (status === 503) onError?.('Serviço temporariamente indisponível');
      else onError?.(detail || 'Erro ao buscar CNPJ');
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || mutation.isPending}
      className="px-3 py-2 bg-[#1E3A5F] text-white rounded-md text-sm hover:bg-[#2E5984] disabled:opacity-50 whitespace-nowrap flex items-center gap-1"
    >
      {mutation.isPending ? (
        <>
          <span className="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
          Buscando…
        </>
      ) : (
        '🔍 Buscar CNPJ'
      )}
    </button>
  );
}
