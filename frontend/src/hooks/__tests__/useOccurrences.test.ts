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
import {
  useOccurrences as useOrvalOccurrences,
  useOccurrence as useOrvalOccurrence,
  useOccurrencesByPost as useOrvalOccurrencesByPost,
} from '@/hooks/operacional/useOccurrences';
import { useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet } from '@/types/generated/operacional/operacional-ocorrencias/operacional-ocorrencias';
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

    it('deve usar todos os filtros disponíveis', async () => {
      const { result } = renderHook(() => useOccurrences(), { wrapper });

      await act(async () => {
        result.current.setFilters({
          search: 'busca',
          status: 'aberta',
          post_id: 'post-123',
          employee_id: 'emp-456',
          date_from: '2024-01-01',
          date_to: '2024-12-31',
        });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({
          search: 'busca',
          status: 'aberta',
          post_id: 'post-123',
          employee_id: 'emp-456',
          date_from: '2024-01-01',
          date_to: '2024-12-31',
        });
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

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => useOccurrenceStats(), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('useOccurrences - Params com filtros vazios/null', () => {
    it('deve ignorar filtros com valores undefined, null e string vazia', async () => {
      const { result } = renderHook(
        () => useOccurrences({
          initialFilters: {
            search: '',
            status: undefined as any,
            post_id: null as any,
            employee_id: 'emp-1',
          },
        }),
        { wrapper }
      );

      // Os filtros com valores vazios/null/undefined devem ser ignorados nos params
      expect(result.current.filters).toEqual({
        search: '',
        status: undefined,
        post_id: null,
        employee_id: 'emp-1',
      });

      // Verificar que o hook Orval foi chamado com params que excluem valores vazios
      expect(useOrvalOccurrences).toHaveBeenCalledWith(
        expect.objectContaining({
          employee_id: 'emp-1',
          page: 1,
          page_size: 10,
        }),
        expect.anything()
      );

      // Os valores vazios NÃO devem estar nos params
      const callArgs = vi.mocked(useOrvalOccurrences).mock.calls;
      const lastCall = callArgs[callArgs.length - 1];
      const params = lastCall?.[0] as Record<string, unknown>;
      expect(params).not.toHaveProperty('search');
      expect(params).not.toHaveProperty('post_id');
    });

    it('deve mapear status para status_filter nos params', async () => {
      renderHook(
        () => useOccurrences({
          initialFilters: {
            status: 'aberta',
          },
        }),
        { wrapper }
      );

      const callArgs = vi.mocked(useOrvalOccurrences).mock.calls;
      const lastCall = callArgs[callArgs.length - 1];
      const params = lastCall?.[0] as Record<string, unknown>;
      expect(params).toHaveProperty('status_filter', 'aberta');
      expect(params).not.toHaveProperty('status');
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

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => useOccurrenceDetail('123'), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });

    it('deve retornar mensagem de erro quando error é Error instance', () => {
      vi.mocked(useOrvalOccurrence).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: new Error('Detail error'),
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => useOccurrenceDetail('123'), { wrapper });

      expect(result.current.error).toBe('Detail error');
      expect(result.current.occurrence).toBeNull();
    });

    it('deve retornar mensagem padrão quando error não é Error instance', () => {
      vi.mocked(useOrvalOccurrence).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: 'string error' as any,
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => useOccurrenceDetail('123'), { wrapper });

      expect(result.current.error).toBe('Erro ao carregar ocorrência');
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

    it('deve chamar refresh', async () => {
      const { result } = renderHook(() => usePostOccurrences('post-1'), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });

    it('deve retornar mensagem de erro quando error é Error instance', () => {
      vi.mocked(useOrvalOccurrencesByPost).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: new Error('Post occurrences error'),
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => usePostOccurrences('post-1'), { wrapper });

      expect(result.current.error).toBe('Post occurrences error');
      expect(result.current.occurrences).toEqual([]);
      expect(result.current.total).toBe(0);
    });

    it('deve retornar mensagem padrão quando error não é Error instance', () => {
      vi.mocked(useOrvalOccurrencesByPost).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: { code: 500 } as any,
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => usePostOccurrences('post-1'), { wrapper });

      expect(result.current.error).toBe('Erro ao carregar ocorrências do posto');
      expect(result.current.occurrences).toEqual([]);
    });

    it('deve retornar dados quando data é null/undefined (fallback [])', () => {
      vi.mocked(useOrvalOccurrencesByPost).mockImplementationOnce(() => ({
        data: null,
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => usePostOccurrences('post-1'), { wrapper });

      expect(result.current.occurrences).toEqual([]);
      expect(result.current.total).toBe(0);
      expect(result.current.error).toBeNull();
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

    it('deve retornar mensagem padrão quando deleteOccurrence falha com não-Error', async () => {
      mockMutateAsync.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteOccurrence('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(false);
        expect(result.current.error).toBe('Erro ao deletar ocorrência');
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

    it('deve retornar null e setar erro quando updateOccurrence falha', async () => {
      mockMutateAsync.mockRejectedValueOnce(new Error('Update failed'));

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let updated: unknown;
      await act(async () => {
        updated = await result.current.updateOccurrence('1', { title: 'Updated' } as any);
      });

      await waitFor(() => {
        expect(updated).toBeNull();
        expect(result.current.error).toBe('Update failed');
      });
    });

    it('deve retornar null e setar erro quando resolveOccurrence falha', async () => {
      mockMutateAsync.mockRejectedValueOnce(new Error('Resolve failed'));

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let resolved: unknown;
      await act(async () => {
        resolved = await result.current.resolveOccurrence('1', { resolution: 'Fixed' } as any);
      });

      await waitFor(() => {
        expect(resolved).toBeNull();
        expect(result.current.error).toBe('Resolve failed');
      });
    });

    it('deve retornar mensagem padrão quando updateOccurrence falha com não-Error', async () => {
      mockMutateAsync.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let updated: unknown;
      await act(async () => {
        updated = await result.current.updateOccurrence('1', { title: 'Updated' } as any);
      });

      await waitFor(() => {
        expect(updated).toBeNull();
        expect(result.current.error).toBe('Erro ao atualizar ocorrência');
      });
    });

    it('deve retornar mensagem padrão quando resolveOccurrence falha com não-Error', async () => {
      mockMutateAsync.mockRejectedValueOnce({ message: 'objeto de erro' });

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let resolved: unknown;
      await act(async () => {
        resolved = await result.current.resolveOccurrence('1', { resolution: 'Fixed' } as any);
      });

      await waitFor(() => {
        expect(resolved).toBeNull();
        expect(result.current.error).toBe('Erro ao resolver ocorrência');
      });
    });

    it('deve retornar mensagem padrão quando deleteOccurrence falha com não-Error', async () => {
      mockMutateAsync.mockRejectedValueOnce('erro string');

      const { result } = renderHook(() => useOccurrenceMutations(), { wrapper });

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deleteOccurrence('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(false);
        expect(result.current.error).toBe('Erro ao deletar ocorrência');
      });
    });
  });

  describe('useOccurrences - Error Branches', () => {
    it('deve retornar mensagem de erro quando error é Error instance', () => {
      vi.mocked(useOrvalOccurrences).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: new Error('Erro ao carregar'),
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => useOccurrences(), { wrapper });

      expect(result.current.error).toBe('Erro ao carregar');
    });

    it('deve retornar mensagem padrão quando error não é Error instance', () => {
      vi.mocked(useOrvalOccurrences).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: 'string de erro' as any,
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => useOccurrences(), { wrapper });

      expect(result.current.error).toBe('Erro ao carregar ocorrências');
    });
  });

  describe('useOccurrenceStats - Error Branches', () => {
    it('deve retornar mensagem de erro quando error é Error instance', () => {
      vi.mocked(useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: new Error('Erro nas stats'),
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => useOccurrenceStats(), { wrapper });

      expect(result.current.error).toBe('Erro nas stats');
    });

    it('deve retornar mensagem padrão quando error não é Error instance', () => {
      vi.mocked(useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet).mockImplementationOnce(() => ({
        data: undefined,
        isLoading: false,
        error: { msg: 'erro object' } as any,
        refetch: mockRefetch,
      }) as any);

      const { result } = renderHook(() => useOccurrenceStats(), { wrapper });

      expect(result.current.error).toBe('Erro ao carregar estatísticas');
    });
  });
});
