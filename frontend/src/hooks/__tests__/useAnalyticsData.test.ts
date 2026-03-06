import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useAnalyticsData } from '../useAnalyticsData';

// Mock do api-client
const mockCustomInstance = vi.fn();

vi.mock('@/lib/api-client', () => ({
  customInstance: (...args: unknown[]) => mockCustomInstance(...args),
}));

describe('useAnalyticsData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Estado Inicial', () => {
    it('deve iniciar com data null e isLoading true', () => {
      mockCustomInstance.mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useAnalyticsData());

      expect(result.current.data).toBeNull();
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Fetch de Dados', () => {
    it('deve fazer chamadas para múltiplos endpoints', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ total: 10, filled: 8, by_type: { fixed: 5, mobile: 5 } }) // posts
        .mockResolvedValueOnce({ items: [{ departamento: 'TI' }, { departamento: 'RH' }], total: 2 }) // employees
        .mockResolvedValueOnce({ total: 20, by_status: { total_shifts: 100 } }) // scales
        .mockResolvedValueOnce({ total_active: 15 }); // allocations

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockCustomInstance).toHaveBeenCalledTimes(4);
      expect(mockCustomInstance).toHaveBeenCalledWith(expect.objectContaining({
        url: '/api/v1/operacional/posts/stats',
      }));
      expect(mockCustomInstance).toHaveBeenCalledWith(expect.objectContaining({
        url: '/api/v1/operacional/employees/',
      }));
    });

    it('deve processar dados corretamente', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ total: 10, filled: 8, by_type: { fixed: 6, mobile: 4 } })
        .mockResolvedValueOnce({
          items: [
            { departamento: 'Operacional' },
            { departamento: 'Operacional' },
            { departamento: 'Administrativo' },
          ],
          total: 3,
        })
        .mockResolvedValueOnce({ total: 20, by_status: { total_shifts: 100 } })
        .mockResolvedValueOnce({ total_active: 15 });

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.data).not.toBeNull();
      });

      expect(result.current.data?.summary.totalEmployees).toBe(3);
      expect(result.current.data?.summary.totalPosts).toBe(10);
      expect(result.current.data?.summary.coverageRate).toBe(80);
      expect(result.current.data?.employeesByDepartment).toHaveLength(2);
    });

    it('deve lidar com dados parciais', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ total: 0 }) // posts vazio
        .mockResolvedValueOnce({ items: [], total: 0 }) // employees vazio
        .mockResolvedValueOnce({ total: 0 }) // scales vazio
        .mockResolvedValueOnce({ total_active: 0 }); // allocations vazio

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data?.summary.coverageRate).toBe(0);
      expect(result.current.data?.employeesByDepartment).toEqual([]);
    });
  });

  describe('Error Handling', () => {
    it('deve capturar erro quando requisição falhar', async () => {
      // Como o hook usa Promise.allSettled, erros individuais não falham a requisição
      // O hook processa o que conseguiu buscar
      mockCustomInstance
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ items: [], total: 0 })
        .mockResolvedValueOnce({ total: 0 })
        .mockResolvedValueOnce({ total_active: 0 });

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // O hook ainda retorna dados mesmo com falhas parciais
      expect(result.current.data).not.toBeNull();
    });

    it('deve lidar com dados parciais em caso de erro', async () => {
      mockCustomInstance
        .mockRejectedValueOnce(new Error('Failed'))
        .mockResolvedValueOnce({ items: [], total: 0 })
        .mockResolvedValueOnce({ total: 0 })
        .mockResolvedValueOnce({ total_active: 0 });

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Deve retornar dados mesmo com falhas
      expect(result.current.data).not.toBeNull();
    });

    it('deve lidar com erro em uma das requisições paralelas', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ total: 10, filled: 8, by_type: {} })
        .mockRejectedValueOnce(new Error('Employees failed'))
        .mockResolvedValueOnce({ total: 20, by_status: {} })
        .mockResolvedValueOnce({ total_active: 15 });

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Deve retornar dados processados apesar do erro parcial
      expect(result.current.data).not.toBeNull();
      expect(result.current.data?.summary.totalPosts).toBe(10);
    });
  });

  describe('Refresh', () => {
    it('deve refetch quando refresh é chamado', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ total: 10, filled: 8, by_type: {} })
        .mockResolvedValueOnce({ items: [], total: 0 })
        .mockResolvedValueOnce({ total: 20, by_status: {} })
        .mockResolvedValueOnce({ total_active: 15 })
        .mockResolvedValueOnce({ total: 15, filled: 10, by_type: {} }) // segunda chamada
        .mockResolvedValueOnce({ items: [], total: 0 })
        .mockResolvedValueOnce({ total: 25, by_status: {} })
        .mockResolvedValueOnce({ total_active: 20 });

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(result.current.data?.summary.totalPosts).toBe(15);
      });

      expect(mockCustomInstance).toHaveBeenCalledTimes(8);
    });
  });

  describe('Tendências Mensais', () => {
    it('deve gerar tendências mensais', async () => {
      mockCustomInstance
        .mockResolvedValueOnce({ total: 10, filled: 8, by_type: {} })
        .mockResolvedValueOnce({ items: [], total: 0 })
        .mockResolvedValueOnce({ total: 20, by_status: {} })
        .mockResolvedValueOnce({ total_active: 15 });

      const { result } = renderHook(() => useAnalyticsData());

      await waitFor(() => {
        expect(result.current.data).not.toBeNull();
      });

      expect(result.current.data?.monthlyTrends).toHaveLength(6);
      expect(result.current.data?.monthlyTrends[0]).toHaveProperty('month');
      expect(result.current.data?.monthlyTrends[0]).toHaveProperty('escalas');
      expect(result.current.data?.monthlyTrends[0]).toHaveProperty('colaboradores');
      expect(result.current.data?.monthlyTrends[0]).toHaveProperty('ocorrencias');
    });
  });
});
