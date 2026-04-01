import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useKPITrends } from '../useKPITrends';
import { useKPITrends as useKPITrendsOrval } from '@/hooks/operacional/useKPITrends';
import React from 'react';

// Mock do operacional useKPITrends
const mockRefetch = vi.fn();

// Helper para criar mock de UseQueryResult completo
 
const createMockQueryResult = (overrides: Record<string, any> = {}): ReturnType<typeof useKPITrendsOrval> => ({
  data: undefined,
  isLoading: false,
  isError: false,
  error: null,
  refetch: mockRefetch,
  isPending: false,
  isLoadingError: false,
  isRefetchError: false,
  isSuccess: true,
  status: 'success',
  fetchStatus: 'idle',
  isFetched: true,
  isFetching: false,
  isFetchedAfterMount: true,
  isInitialLoading: false,
  isPlaceholderData: false,
  isStale: false,
  isRefetching: false,
  failureCount: 0,
  failureReason: null,
  errorUpdateCount: 0,
  dataUpdatedAt: Date.now(),
  errorUpdatedAt: 0,
  ...overrides,
} as unknown as ReturnType<typeof useKPITrendsOrval>);

vi.mock('@/hooks/operacional/useKPITrends', () => ({
  useKPITrends: vi.fn(),
}));

describe('useKPITrends', () => {
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

    // Configurar o mock padrão
    vi.mocked(useKPITrendsOrval).mockImplementation((params, options) =>
      createMockQueryResult({
        data: options?.query?.enabled !== false
          ? {
              data: {
                labels: ['Jan', 'Feb', 'Mar'],
                datasets: [
                  { label: 'Escalas', data: [10, 20, 30] },
                  { label: 'Ocorrências', data: [5, 8, 12] },
                ],
              },
            }
          : undefined,
      })
    );
  });

  describe('Estado Inicial', () => {
    it('deve retornar dados formatados corretamente', () => {
      const { result } = renderHook(() => useKPITrends(), { wrapper });

      expect(result.current.data).toEqual({
        labels: ['Jan', 'Feb', 'Mar'],
        datasets: [
          { label: 'Escalas', data: [10, 20, 30] },
          { label: 'Ocorrências', data: [5, 8, 12] },
        ],
      });
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('deve usar período padrão de 7 dias', () => {
      renderHook(() => useKPITrends(), { wrapper });

      expect(useKPITrendsOrval).toHaveBeenCalledWith(
        expect.objectContaining({ period: '7d' }),
        expect.any(Object)
      );
    });

    it('deve aceitar período personalizado', () => {
      renderHook(() => useKPITrends({ period: '30d' }), { wrapper });

      expect(useKPITrendsOrval).toHaveBeenCalledWith(
        expect.objectContaining({ period: '30d' }),
        expect.any(Object)
      );
    });
  });

  describe('Opções', () => {
    it('deve respeitar autoLoad = false', () => {
      renderHook(() => useKPITrends({ autoLoad: false }), { wrapper });

      expect(useKPITrendsOrval).toHaveBeenCalledWith(
        expect.any(Object),
        expect.objectContaining({
          query: expect.objectContaining({ enabled: false }),
        })
      );
    });

    it('deve usar autoLoad = true por padrão', () => {
      renderHook(() => useKPITrends(), { wrapper });

      expect(useKPITrendsOrval).toHaveBeenCalledWith(
        expect.any(Object),
        expect.objectContaining({
          query: expect.objectContaining({ enabled: true }),
        })
      );
    });
  });

  describe('Dados Vazios', () => {
    it('deve retornar null quando não há dados', () => {
      vi.mocked(useKPITrendsOrval).mockReturnValueOnce(
        createMockQueryResult({ data: undefined })
      );

      const { result } = renderHook(() => useKPITrends(), { wrapper });

      expect(result.current.data).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('deve retornar mensagem de erro quando isError é true', () => {
      vi.mocked(useKPITrendsOrval).mockReturnValueOnce(
        createMockQueryResult({
          data: undefined,
          isError: true,
          error: new Error('Failed to load'),
        })
      );

      const { result } = renderHook(() => useKPITrends(), { wrapper });

      expect(result.current.error).toBe('Failed to load');
    });

    it('deve retornar mensagem genérica quando erro não tem mensagem', () => {
      vi.mocked(useKPITrendsOrval).mockReturnValueOnce(
        createMockQueryResult({
          data: undefined,
          isError: true,
          error: null,
        })
      );

      const { result } = renderHook(() => useKPITrends(), { wrapper });

      expect(result.current.error).toBe('Erro ao carregar tendencias');
    });
  });

  describe('Refresh', () => {
    it('deve expor função de refresh', () => {
      const { result } = renderHook(() => useKPITrends(), { wrapper });

      expect(typeof result.current.refresh).toBe('function');
    });

    it('deve chamar refetch do orval', async () => {
      const { result } = renderHook(() => useKPITrends(), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('Loading', () => {
    it('deve refletir estado de loading', () => {
      vi.mocked(useKPITrendsOrval).mockReturnValueOnce(
        createMockQueryResult({
          data: undefined,
          isLoading: true,
        })
      );

      const { result } = renderHook(() => useKPITrends(), { wrapper });

      expect(result.current.isLoading).toBe(true);
    });
  });
});
