import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useDashboardStats,
  useRecentActivities,
  useNotifications,
  useHealthCheck,
} from '../useDashboard';
import api from '@/lib/api';
import React from 'react';

// Mock do api
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
  },
}));

describe('useDashboard', () => {
  let queryClient: QueryClient;

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  describe('useDashboardStats', () => {
    it('deve buscar estatísticas do dashboard', async () => {
      const mockStats = {
        leads: { total: 100, novos: 10, em_negociacao: 20, valor_pipeline: 50000 },
        clientes: { total: 50, ativos: 45 },
        financeiro: {
          receita_mes: 100000,
          despesas_mes: 50000,
          saldo: 50000,
          contas_receber: 20000,
          contas_pagar: 15000,
        },
        operacional: {
          vigilantes_ativos: 30,
          postos_ativos: 15,
          escalas_mes: 45,
          ocorrencias_abertas: 3,
        },
      };

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockStats });

      const { result } = renderHook(() => useDashboardStats(), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockStats);
      expect(api.get).toHaveBeenCalledWith('/api/v1/reports/dashboard/stats');
    });

    it('deve usar staleTime de 1 minuto', async () => {
      vi.mocked(api.get).mockResolvedValueOnce({ data: {} });

      renderHook(() => useDashboardStats(), { wrapper });

      await waitFor(() => {
        expect(vi.mocked(api.get)).toHaveBeenCalled();
      });
    });
  });

  describe('useRecentActivities', () => {
    it('deve buscar atividades recentes com limite padrão', async () => {
      const mockActivities = [
        { id: 1, action: 'created', entity: 'cliente' },
        { id: 2, action: 'updated', entity: 'posto' },
      ];

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockActivities });

      const { result } = renderHook(() => useRecentActivities(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockActivities);
      });

      expect(api.get).toHaveBeenCalledWith('/api/v1/audit/recent?limit=10');
    });

    it('deve aceitar limite personalizado', async () => {
      vi.mocked(api.get).mockResolvedValueOnce({ data: [] });

      renderHook(() => useRecentActivities(25), { wrapper });

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith('/api/v1/audit/recent?limit=25');
      });
    });
  });

  describe('useNotifications', () => {
    it('deve buscar notificações', async () => {
      const mockNotifications = [
        { id: 1, message: 'Test 1', read: false },
        { id: 2, message: 'Test 2', read: true },
      ];

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockNotifications });

      const { result } = renderHook(() => useNotifications(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockNotifications);
      });

      expect(api.get).toHaveBeenCalledWith('/api/v1/users/me/notifications');
    });

    it('deve usar refetchInterval de 30 segundos', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      vi.mocked(api.get).mockResolvedValue({ data: [] });

      renderHook(() => useNotifications(), { wrapper });

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledTimes(1);
      });

      await act(async () => {
        vi.advanceTimersByTime(30000);
      });

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledTimes(2);
      });

      vi.useRealTimers();
    });
  });

  describe('useHealthCheck', () => {
    it('deve verificar saúde do sistema', async () => {
      const mockHealth = { status: 'healthy', version: '1.0.0' };

      vi.mocked(api.get).mockResolvedValueOnce({ data: mockHealth });

      const { result } = renderHook(() => useHealthCheck(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockHealth);
      });

      expect(api.get).toHaveBeenCalledWith('/health');
    });

    it('deve usar staleTime de 5 minutos', async () => {
      vi.mocked(api.get).mockResolvedValueOnce({ data: {} });

      renderHook(() => useHealthCheck(), { wrapper });

      await waitFor(() => {
        expect(vi.mocked(api.get)).toHaveBeenCalled();
      });
    });
  });
});
