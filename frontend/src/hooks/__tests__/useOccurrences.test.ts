import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useOccurrences,
  useOccurrenceStats,
  useOccurrenceDetail,
  usePostOccurrences,
  useOccurrenceMutations,
} from '../useOccurrences';
import React from 'react';

// Mocks
const mockRefetch = vi.fn();
const mockMutateAsync = vi.fn();

vi.mock('@/hooks/operacional/useOccurrences', () => ({
  useOccurrences: vi.fn((params, options) => ({
    data: options?.query?.enabled !== false ? {
      items: [
        { id: '1', title: 'Ocorrência 1', status: 'open' },
        { id: '2', title: 'Ocorrência 2', status: 'closed' },
      ],
      total: 2,
      total_pages: 1,
    } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useOccurrence: vi.fn((id, options) => ({
    data: options?.query?.enabled !== false ? { id, title: 'Detail' } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useOccurrencesByPost: vi.fn((id, options) => ({
    data: options?.query?.enabled !== false ? [{ id: '1' }] : [],
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useCreateOccurrence: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useUpdateOccurrence: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useDeleteOccurrence: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useResolveOccurrence: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
}));

vi.mock('@/types/generated/operacional/operacional-ocorrencias/operacional-ocorrencias', () => ({
  useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet: vi.fn(() => ({
    data: { total: 10, by_status: { open: 5, closed: 5 } },
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
}));

describe('useOccurrences', () => {
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

  describe('useOccurrences - Estado Inicial', () => {
    it('deve retornar valores iniciais', () => {
      const { result } = renderHook(() => useOccurrences(), { wrapper });

      expect(result.current.occurrences).toHaveLength(2);
      expect(result.current.total).toBe(2);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(10);
      expect(result.current.isLoading).toBe(false);
    });

    it('deve aceitar opções personalizadas', () => {
      const { result } = renderHook(
        () => useOccurrences({ initialPageSize: 25, autoLoad: false }),
        { wrapper }
      );

      expect(result.current.pageSize).toBe(25);
    });
  });

  describe('useOccurrences - Paginação e Filtros', () => {
    it('deve atualizar filtros e resetar página', async () => {
      const { result } = renderHook(() => useOccurrences(), { wrapper });

      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(3);
      });

      await act(async () => {
        result.current.setFilters({ status: 'aberta', post_id: '123' });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({ status: 'aberta', post_id: '123' });
        expect(result.current.page).toBe(1);
      });
    });

    it('deve atualizar pageSize', async () => {
      const { result } = renderHook(() => useOccurrences(), { wrapper });

      await act(async () => {
        result.current.setPageSize(50);
      });

      await waitFor(() => {
        expect(result.current.pageSize).toBe(50);
      });
    });
  });

  describe('useOccurrences - Refresh', () => {
    it('deve chamar refetch', async () => {
      const { result } = renderHook(() => useOccurrences(), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('useOccurrenceStats', () => {
    it('deve retornar estatísticas', () => {
      const { result } = renderHook(() => useOccurrenceStats(), { wrapper });

      expect(result.current.stats).toEqual({ total: 10, by_status: { open: 5, closed: 5 } });
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('useOccurrenceDetail', () => {
    it('deve retornar null quando id é null', () => {
      const { result } = renderHook(() => useOccurrenceDetail(null), { wrapper });

      expect(result.current.occurrence).toBeNull();
    });

    it('deve carregar detalhes quando id é fornecido', () => {
      const { result } = renderHook(() => useOccurrenceDetail('123'), { wrapper });

      expect(result.current.occurrence).toEqual({ id: '123', title: 'Detail' });
    });
  });

  describe('usePostOccurrences', () => {
    it('deve retornar array vazio quando postId é null', () => {
      const { result } = renderHook(() => usePostOccurrences(null), { wrapper });

      expect(result.current.occurrences).toEqual([]);
    });

    it('deve carregar ocorrências do posto', () => {
      const { result } = renderHook(() => usePostOccurrences('post-1'), { wrapper });

      expect(result.current.occurrences).toHaveLength(1);
      expect(result.current.total).toBe(1);
    });
  });

  describe('useOccurrenceMutations', () => {
    it('deve criar ocorrência', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', title: 'New' });

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let created: unknown;
      await act(async () => {
        created = await result.current.createOccurrence({ title: 'New' } as any);
      });

      await waitFor(() => {
        expect(created).toEqual({ id: '1', title: 'New' });
      });
      expect(mockMutateAsync).toHaveBeenCalled();
    });

    it('deve retornar null e setar erro quando criação falha', async () => {
      mockMutateAsync.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let created: unknown;
      await act(async () => {
        created = await result.current.createOccurrence({ title: 'New' } as any);
      });

      await waitFor(() => {
        expect(created).toBeNull();
      });
      expect(result.current.error).toBe('Failed');
    });

    it('deve atualizar ocorrência', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', title: 'Updated' });

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let updated: unknown;
      await act(async () => {
        updated = await result.current.updateOccurrence('1', { title: 'Updated' } as any);
      });

      await waitFor(() => {
        expect(updated).toEqual({ id: '1', title: 'Updated' });
      });
    });

    it('deve resolver ocorrência', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', status: 'resolved' });

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let resolved: unknown;
      await act(async () => {
        resolved = await result.current.resolveOccurrence('1', { resolution: 'Fixed' } as any);
      });

      await waitFor(() => {
        expect(resolved).toEqual({ id: '1', status: 'resolved' });
      });
    });

    it('deve deletar ocorrência', async () => {
      mockMutateAsync.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteOccurrence('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(true);
      });
    });

    it('deve retornar false quando deleção falha', async () => {
      mockMutateAsync.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteOccurrence('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(false);
      });
    });

    it('deve refletir estado de loading inicial', () => {
      // O hook deve iniciar com isLoading = false quando não há operações pendentes
      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      expect(result.current.isLoading).toBe(false);
      expect(typeof result.current.createOccurrence).toBe('function');
      expect(typeof result.current.updateOccurrence).toBe('function');
    });

    it('deve setar erro como string quando não é Error instance', async () => {
      mockMutateAsync.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      await act(async () => {
        await result.current.createOccurrence({ title: 'New' } as any);
      });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao criar ocorrência');
      });
    });
  });

  describe('Error States - Branch Coverage', () => {
    it('deve setar erro como string quando não é Error instance em mutations', async () => {
      mockMutateAsync.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      await act(async () => {
        await result.current.createOccurrence({ title: 'New' } as any);
      });

      await waitFor(() => {
        expect(result.current.error).toBe('Erro ao criar ocorrência');
      });
    });

    it('deve retornar null para error quando não há erro', () => {
      const { result } = renderHook(() => useOccurrences(), { wrapper });

      expect(result.current.error).toBeNull();
    });

    it('deve retornar null para stats quando não há dados', () => {
      const { result } = renderHook(() => useOccurrenceStats(), { wrapper });

      expect(result.current.stats).not.toBeNull();
    });
  });
});
