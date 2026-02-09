import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAllocations } from '../useAllocations';
import { useAllocations as useAllocationsOrval } from '@/hooks/operacional/useAllocations';
import React from 'react';

// Mock do operacional useAllocations
const mockRefetch = vi.fn();

// Helper para criar mock de UseQueryResult completo
 
const createMockQueryResult = (overrides: Record<string, any> = {}): ReturnType<typeof useAllocationsOrval> => ({
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
} as unknown as ReturnType<typeof useAllocationsOrval>);

const mockQueryData = {
  items: [
    { id: '1', post_id: 'post-1', employee_id: 'emp-1', status: 'active' },
    { id: '2', post_id: 'post-2', employee_id: 'emp-2', status: 'inactive' },
  ],
  total: 2,
  total_pages: 1,
};

vi.mock('@/hooks/operacional/useAllocations', () => ({
  useAllocations: vi.fn(),
}));

describe('useAllocations', () => {
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
    vi.mocked(useAllocationsOrval).mockImplementation((params, options) =>
      createMockQueryResult({
        data: options?.query?.enabled !== false ? mockQueryData : undefined,
      })
    );
  });

  describe('Estado Inicial', () => {
    it('deve retornar valores iniciais corretos', () => {
      const { result } = renderHook(() => useAllocations(), { wrapper });

      expect(result.current.allocations).toEqual(mockQueryData.items);
      expect(result.current.total).toBe(2);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(20);
      expect(result.current.totalPages).toBe(1);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('deve aceitar opções iniciais personalizadas', () => {
      const { result } = renderHook(
        () =>
          useAllocations({
            initialPage: 2,
            initialPageSize: 50,
            initialFilters: { post_id: 'post-1' },
          }),
        { wrapper }
      );

      expect(result.current.page).toBe(2);
      expect(result.current.pageSize).toBe(50);
      expect(result.current.filters).toEqual({ post_id: 'post-1' });
    });

    it('deve retornar array vazio quando autoLoad é false', () => {
      vi.mocked(useAllocationsOrval).mockReturnValueOnce(
        createMockQueryResult({ data: undefined })
      );

      const { result } = renderHook(() => useAllocations({ autoLoad: false }), { wrapper });

      expect(result.current.allocations).toEqual([]);
      expect(result.current.total).toBe(0);
    });
  });

  describe('Paginação', () => {
    it('deve atualizar página corretamente', async () => {
      const { result } = renderHook(() => useAllocations(), { wrapper });

      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(3);
      });
    });

    it('deve atualizar pageSize corretamente', async () => {
      const { result } = renderHook(() => useAllocations(), { wrapper });

      await act(async () => {
        result.current.setPageSize(100);
      });

      await waitFor(() => {
        expect(result.current.pageSize).toBe(100);
      });
    });
  });

  describe('Filtros', () => {
    it('deve atualizar filtros e resetar para página 1', async () => {
      const { result } = renderHook(
        () => useAllocations({ initialPage: 3 }),
        { wrapper }
      );

      await act(async () => {
        result.current.setFilters({ status: 'active', employee_id: 'emp-1' });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({ status: 'active', employee_id: 'emp-1' });
        expect(result.current.page).toBe(1);
      });
    });

    it('deve manter filtros anteriores ao atualizar', async () => {
      const { result } = renderHook(
        () => useAllocations({ initialFilters: { status: 'active' } }),
        { wrapper }
      );

      await act(async () => {
        result.current.setFilters({ employee_id: 'emp-1' });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({ employee_id: 'emp-1' });
      });
    });
  });

  describe('Refresh', () => {
    it('deve chamar refetch ao executar refresh', async () => {
      const { result } = renderHook(() => useAllocations(), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('Cálculos', () => {
    it('deve calcular totalPages corretamente', () => {
      const { result } = renderHook(() => useAllocations(), { wrapper });

      expect(result.current.totalPages).toBe(1);
    });

    it('deve retornar allocations como array vazio quando não há dados', () => {
      vi.mocked(useAllocationsOrval).mockReturnValueOnce(
        createMockQueryResult({
          data: { items: [], total: 0, total_pages: 0 },
          isLoading: true,
          isFetching: true,
          fetchStatus: 'fetching',
        }) as unknown as ReturnType<typeof useAllocationsOrval>
      );

      const { result } = renderHook(() => useAllocations(), { wrapper });
      expect(result.current.allocations).toEqual([]);
    });
  });
});
