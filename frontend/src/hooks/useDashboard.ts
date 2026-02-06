'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

// Estatísticas do dashboard
export interface DashboardStats {
  leads: {
    total: number;
    novos: number;
    em_negociacao: number;
    valor_pipeline: number;
  };
  clientes: {
    total: number;
    ativos: number;
  };
  financeiro: {
    receita_mes: number;
    despesas_mes: number;
    saldo: number;
    contas_receber: number;
    contas_pagar: number;
  };
  operacional: {
    vigilantes_ativos: number;
    postos_ativos: number;
    escalas_mes: number;
    ocorrencias_abertas: number;
  };
}

// Hook para buscar estatísticas do dashboard
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: async (): Promise<DashboardStats> => {
      const response = await api.get('/api/v1/reports/dashboard/stats');
      return response.data;
    },
    staleTime: 60 * 1000, // 1 minuto
  });
}

// Hook para buscar atividades recentes
export function useRecentActivities(limit = 10) {
  return useQuery({
    queryKey: ['dashboard', 'activities', limit],
    queryFn: async () => {
      const response = await api.get(`/api/v1/audit/recent?limit=${limit}`);
      return response.data;
    },
  });
}

// Hook para buscar notificações
export function useNotifications() {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await api.get('/api/v1/users/me/notifications');
      return response.data;
    },
    refetchInterval: 30 * 1000, // 30 segundos
  });
}

// Hook para verificar saúde do sistema
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.get('/health');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}
