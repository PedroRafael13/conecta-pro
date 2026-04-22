import { useMutation, useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import type { CEPEnrichment, CNPJEnrichment, TaxasResponse } from '@/types/crm/enrichment';

// UC-01: CNPJ on-demand (backend cacheia em Redis — sem cache React Query)
export function useEnrichCNPJ() {
  return useMutation({
    mutationFn: async (cnpj: string): Promise<CNPJEnrichment> => {
      const digits = cnpj.replace(/\D/g, '');
      return customInstance<CNPJEnrichment>({
        url: `/api/v1/crm/enrichment/cnpj/${digits}`,
        method: 'GET',
      });
    },
  });
}

// UC-02: CEP on-demand — chamado no onBlur dos campos CEP
export function useEnrichCEP() {
  return useMutation({
    mutationFn: async (cep: string): Promise<CEPEnrichment> => {
      const digits = cep.replace(/\D/g, '');
      return customInstance<CEPEnrichment>({
        url: `/api/v1/crm/enrichment/cep/${digits}`,
        method: 'GET',
      });
    },
  });
}

// UC-03: Widget Dashboard — busca no mount, revalida a cada 6h
export function useTaxasVigentes() {
  return useQuery({
    queryKey: ['taxas-vigentes'],
    queryFn: (): Promise<TaxasResponse> =>
      customInstance<TaxasResponse>({
        url: '/api/v1/crm/enrichment/taxas',
        method: 'GET',
      }),
    staleTime: 6 * 60 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
