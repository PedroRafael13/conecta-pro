'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api, { getErrorMessage } from '@/lib/api';

// Tipos baseados no backend real
export interface Lead {
  id: string;
  nome: string;
  contato: string;
  telefone: string;
  email: string;
  origem: string;
  status: string;
  valor_estimado: number;
  observacoes?: string;
  created_at: string;
  updated_at?: string;
  ativo: boolean;
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

      const response = await api.get(`/api/v1/crm/leads?${params}`);
      return response.data;
    },
  });
}

// Hook para buscar um lead específico
export function useLead(id: string | null) {
  return useQuery({
    queryKey: ['lead', id],
    queryFn: async (): Promise<Lead> => {
      const response = await api.get(`/api/v1/crm/leads/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

// Hook para criar lead
export function useCreateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: LeadCreate): Promise<Lead> => {
      const response = await api.post('/api/v1/crm/leads', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
    onError: (error) => {
      console.error('Erro ao criar lead:', getErrorMessage(error));
    },
  });
}

// Hook para atualizar lead
export function useUpdateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: LeadUpdate }): Promise<Lead> => {
      const response = await api.patch(`/api/v1/crm/leads/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['lead', variables.id] });
    },
    onError: (error) => {
      console.error('Erro ao atualizar lead:', getErrorMessage(error));
    },
  });
}

// Hook para deletar lead
export function useDeleteLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await api.delete(`/api/v1/crm/leads/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
    onError: (error) => {
      console.error('Erro ao deletar lead:', getErrorMessage(error));
    },
  });
}

// Hook para estatísticas de leads
export function useLeadsStats() {
  return useQuery({
    queryKey: ['leads', 'stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/crm/leads/stats');
      return response.data;
    },
  });
}
