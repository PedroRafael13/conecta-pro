'use client';
import { useEnrichCEP } from '@/hooks/crm/useEnrichment';
import type { CEPEnrichment } from '@/types/crm/enrichment';

interface Props {
  cep: string;
  onCepChange: (cep: string) => void;
  onAutoFill: (data: CEPEnrichment) => void;
  onError?: (msg: string) => void;
  disabled?: boolean;
  className?: string;
}

export function CepAutoFill({ cep, onCepChange, onAutoFill, onError, disabled, className }: Props) {
  const mutation = useEnrichCEP();

  const handleBlur = async () => {
    const digits = cep.replace(/\D/g, '');
    if (digits.length !== 8) return;
    try {
      const data = await mutation.mutateAsync(cep);
      onAutoFill(data);
    } catch (e: any) {
      const status = e?.response?.status ?? e?.status;
      if (status === 404) onError?.('CEP não encontrado');
      else if (status === 503) onError?.('Serviço indisponível');
    }
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={cep}
        onChange={(e) => onCepChange(e.target.value)}
        onBlur={handleBlur}
        disabled={disabled || mutation.isPending}
        placeholder="00000-000"
        className={`w-full px-3 py-2 border rounded-md text-sm ${className ?? ''} ${mutation.isPending ? 'opacity-70' : ''}`}
      />
      {mutation.isPending && (
        <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">
          buscando…
        </span>
      )}
    </div>
  );
}
