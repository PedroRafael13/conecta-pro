'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';

// Tipos baseados no backend real (suporte a nomes em PT e EN)
export interface Lead {
  id: string;
  nome?: string;
  name?: string;
  contato?: string;
  contact_name?: string;
  company?: string;
  telefone?: string;
  phone?: string;
  email?: string;
  origem?: string;
  source?: string;
  status: string;
  valor_estimado?: number;
  value?: number;
  observacoes?: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  ativo?: boolean;
}

export interface LeadCreate {
  nome: string;
  contato: string;
  telefone?: string;
  email?: string;
  origem?: string;
  status?: string;
  valor_estimado?: number;
  observacoes?: string;
}

export interface LeadUpdate extends Partial<LeadCreate> {}

export interface LeadsResponse {
  items: Lead[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface LeadsFilters {
  search?: string;
  status?: string;
  origem?: string;
  skip?: number;
  limit?: number;
}

const BASE_URL = '/api/v1/crm/leads';

// Hook para listar leads
export function useLeads(filters: LeadsFilters = {}) {
  const { search, status, origem, skip = 0, limit = 50 } = filters;

  return useQuery({
    queryKey: ['leads', { search, status, origem, skip, limit }],
    queryFn: async (): Promise<LeadsResponse> => {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (status) params.append('status', status);
      if (origem) params.append('origem', origem);
      params.append('skip', String(skip));
      params.append('limit', String(limit));

      return customInstance<LeadsResponse>({
        url: `${BASE_URL}?${params}`,
        method: 'GET',
      });
    },
  });
}

// Hook para buscar um lead específico
export function useLead(id: string | null) {
  return useQuery({
    queryKey: ['lead', id],
    queryFn: async (): Promise<Lead> => {
      return customInstance<Lead>({
        url: `${BASE_URL}/${id}`,
        method: 'GET',
      });
    },
    enabled: !!id,
  });
}

// Hook para criar lead
export function useCreateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: LeadCreate): Promise<Lead> => {
      return customInstance<Lead>({
        url: BASE_URL,
        method: 'POST',
        data,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
    onError: () => {
      // error handled by React Query
    },
  });
}

// Hook para atualizar lead
export function useUpdateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: LeadUpdate }): Promise<Lead> => {
      return customInstance<Lead>({
        url: `${BASE_URL}/${id}`,
        method: 'PATCH',
        data,
      });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['lead', variables.id] });
    },
    onError: () => {
      // error handled by React Query
    },
  });
}

// Hook para deletar lead
export function useDeleteLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      return customInstance<void>({
        url: `${BASE_URL}/${id}`,
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
    onError: () => {
      // error handled by React Query
    },
  });
}

// Hook para estatísticas de leads
export function useLeadsStats() {
  return useQuery({
    queryKey: ['leads', 'stats'],
    queryFn: async () => {
      return customInstance<Record<string, unknown>>({
        url: `${BASE_URL}/stats`,
        method: 'GET',
      });
    },
  });
}
