import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useDisciplinary,
  useDisciplinaryStats,
  useDisciplinaryDetail,
  usePendingApprovals,
  useEmployeeDisciplinary,
} from '../useDisciplinary';
import { useDisciplinaryActions as useOrvalDisciplinaryActions } from '@/hooks/operacional/useDisciplinary';
import type { DisciplinaryActionStatus, DisciplinaryActionType } from '@/types/disciplinary';
import React from 'react';

// Mocks
const mockRefetch = vi.fn();

vi.mock('@/hooks/operacional/useDisciplinary', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/hooks/operacional/useDisciplinary')>();
  return {
    ...actual,
    useDisciplinaryActions: vi.fn((params, options) => ({
      data: options?.query?.enabled !== false ? {
        items: [
          { id: '1', employee_name: 'John', action_type: 'suspensao' },
          { id: '2', employee_name: 'Jane', action_type: 'advertencia_verbal' },
        ],
        total: 2,
        total_pages: 1,
      } : undefined,
      isLoading: false,
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
    })),
    useDisciplinaryAction: vi.fn((id, options) => ({
      data: options?.query?.enabled !== false ? { id, employee_name: 'John' } : undefined,
      isLoading: false,
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
    })),
    useDisciplinaryActionsByEmployee: vi.fn((id, options) => ({
      data: options?.query?.enabled !== false ? [{ id: '1', action_type: 'advertencia_verbal' }] : [],
      isLoading: false,
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
    })),
    usePendingDisciplinaryApprovals: vi.fn(() => ({
      data: [{ id: '1', status: 'pendente_aprovacao' }],
      isLoading: false,
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
    })),
  };
});

vi.mock('@/types/generated/operacional/operacional-medidas-administrativas/operacional-medidas-administrativas', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/types/generated/operacional/operacional-medidas-administrativas/operacional-medidas-administrativas')>();
  return {
    ...actual,
    useGetDisciplinaryStatsApiV1OperacionalMedidasAdministrativasEstatisticasGet: vi.fn(() => ({
      data: { total: 10, by_type: { advertencia_verbal: 5 } },
      isLoading: false,
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
    })),
  };
});

describe('useDisciplinary', () => {
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

  describe('useDisciplinary - Estado Inicial', () => {
    it('deve retornar valores iniciais', () => {
      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      expect(result.current.actions).toHaveLength(2);
      expect(result.current.total).toBe(2);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(10);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('deve aceitar opções personalizadas', () => {
      const { result } = renderHook(
        () => useDisciplinary({ initialPageSize: 25, autoLoad: false }),
        { wrapper }
      );

      expect(result.current.pageSize).toBe(25);
    });
  });

  describe('useDisciplinary - Paginação e Filtros', () => {
    it('deve atualizar filtros e resetar página', async () => {
      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(3);
      });

      await act(async () => {
        result.current.setFilters({
          status: 'aprovada' as DisciplinaryActionStatus,
          action_type: 'advertencia_verbal' as DisciplinaryActionType,
        });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({
          status: 'aprovada',
          action_type: 'advertencia_verbal',
        });
        expect(result.current.page).toBe(1);
      });
    });

    it('deve atualizar página', async () => {
      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      await act(async () => {
        result.current.setPage(5);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(5);
      });
    });
  });

  describe('useDisciplinary - Refresh', () => {
    it('deve chamar refetch', async () => {
      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('useDisciplinaryStats', () => {
    it('deve retornar estatísticas', () => {
      const { result } = renderHook(() => useDisciplinaryStats(), { wrapper });

      expect(result.current.stats).toEqual({ total: 10, by_type: { advertencia_verbal: 5 } });
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => useDisciplinaryStats(), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('useDisciplinaryDetail', () => {
    it('deve retornar null quando id é null', () => {
      const { result } = renderHook(() => useDisciplinaryDetail(null), { wrapper });

      expect(result.current.action).toBeNull();
      expect(result.current.isLoading).toBe(false);
    });

    it('deve carregar detalhes quando id é fornecido', () => {
      const { result } = renderHook(() => useDisciplinaryDetail('123'), { wrapper });

      expect(result.current.action).toEqual({ id: '123', employee_name: 'John' });
    });
  });

  describe('usePendingApprovals', () => {
    it('deve retornar aprovações pendentes', () => {
      const { result } = renderHook(() => usePendingApprovals(), { wrapper });

      expect(result.current.actions).toHaveLength(1);
      expect(result.current.total).toBe(1);
    });

    it('deve retornar dados iniciais corretos', () => {
      // Verifica que o hook retorna estrutura válida
      const { result } = renderHook(() => usePendingApprovals(), { wrapper });

      expect(Array.isArray(result.current.actions)).toBe(true);
      expect(result.current).toHaveProperty('total');
    });
  });

  describe('useEmployeeDisciplinary', () => {
    it('deve retornar null quando employeeId é null', () => {
      const { result } = renderHook(() => useEmployeeDisciplinary(null), { wrapper });

      expect(result.current.actions).toEqual([]);
    });

    it('deve carregar medidas do funcionário', () => {
      const { result } = renderHook(() => useEmployeeDisciplinary('emp-1'), { wrapper });

      expect(result.current.actions).toHaveLength(1);
      expect(result.current.total).toBe(1);
    });
  });

  describe('Error Handling', () => {
    it('deve retornar estado de erro quando configurado', () => {
      // Verifica que o hook retorna estrutura correta para erros
      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      // O hook deve retornar uma estrutura válida
      expect(result.current).toHaveProperty('actions');
      expect(result.current).toHaveProperty('error');
      expect(Array.isArray(result.current.actions)).toBe(true);
    });
  });

  describe('Error States - Branch Coverage', () => {
    it('deve retornar mensagem de erro quando error é Error instance', () => {
      vi.mocked(useOrvalDisciplinaryActions).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: new Error('Erro de conexão'),
        refetch: mockRefetch,
        isPending: false,
        isLoadingError: true,
        isRefetchError: false,
        isSuccess: false,
        status: 'error',
        fetchStatus: 'idle',
        isFetched: true,
        isFetching: false,
        isFetchedAfterMount: true,
        isInitialLoading: false,
        isPlaceholderData: false,
        isStale: false,
        isRefetching: false,
        failureCount: 1,
        failureReason: new Error('Erro de conexão'),
        errorUpdateCount: 1,
        dataUpdatedAt: 0,
        errorUpdatedAt: Date.now(),
      }));

      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      expect(result.current.error).toBe('Erro de conexão');
    });

    it('deve retornar mensagem padrão quando error não é Error instance', () => {
      vi.mocked(useOrvalDisciplinaryActions).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: 'string de erro',
        refetch: mockRefetch,
        isPending: false,
        isLoadingError: true,
        isRefetchError: false,
        isSuccess: false,
        status: 'error',
        fetchStatus: 'idle',
        isFetched: true,
        isFetching: false,
        isFetchedAfterMount: true,
        isInitialLoading: false,
        isPlaceholderData: false,
        isStale: false,
        isRefetching: false,
        failureCount: 1,
        failureReason: 'string de erro',
        errorUpdateCount: 1,
        dataUpdatedAt: 0,
        errorUpdatedAt: Date.now(),
      }));

      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      expect(result.current.error).toBe('Erro ao carregar medidas');
    });

    it('deve retornar null quando não há error', () => {
      vi.mocked(useOrvalDisciplinaryActions).mockImplementationOnce(() => ({
        data: { items: [], total: 0, total_pages: 0 },
        isLoading: false,
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
      }));

      const { result } = renderHook(() => useDisciplinary(), { wrapper });

      expect(result.current.error).toBeNull();
    });
  });
});
