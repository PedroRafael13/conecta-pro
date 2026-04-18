import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

interface FgtsPorTipo {
  tipo: string;
  count: number;
  soma: number;
}

export interface ValoresFiscaisResumo {
  fgts: {
    por_tipo: FgtsPorTipo[];
    total_brl: number;
    total_registros: number;
  };
  inss: {
    total_brl: number;
    total_registros: number;
  };
  consolidado: {
    valor_total_fiscal_brl: number;
    total_docs_sistema: number;
    total_docs_fiscais: number;
    docs_extraidos: number;
    taxa_extracao_pct: number;
  };
  confianca: {
    alta_auto_save: number;
    media_revisao_manual: number;
    baixa_rejeitado: number;
  };
}

export function useValoresFiscaisResumo() {
  return useQuery<ValoresFiscaisResumo>({
    queryKey: ['onvio', 'valores-fiscais-resumo'],
    queryFn: async () => {
      const { data } = await api.get<ValoresFiscaisResumo>('/api/v1/onvio/valores-fiscais-resumo');
      return data;
    },
    staleTime: 60_000,
  });
}
