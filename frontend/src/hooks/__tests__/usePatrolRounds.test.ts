import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  usePatrolRounds,
  usePatrolRoundStats,
  usePatrolRoundDetail,
  usePatrolRoundMutations,
} from '../usePatrolRounds';
import React from 'react';

// Mocks
const mockRefetch = vi.fn();
const mockMutateAsync = vi.fn();

vi.mock('@/hooks/operacional/usePatrolRounds', () => ({
  usePatrolRounds: vi.fn((params, options) => ({
    data: options?.query?.enabled !== false ? {
      items: [
        { id: '1', status: 'in_progress', post_name: 'Posto A' },
        { id: '2', status: 'completed', post_name: 'Posto B' },
      ],
      total: 2,
      pages: 1,
    } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  usePatrolRound: vi.fn((id, options) => ({
    data: options?.query?.enabled !== false ? { id, status: 'in_progress' } : undefined,
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
  useCreatePatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useUpdatePatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useDeletePatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useStartPatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  usePausePatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useResumePatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useCompletePatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useCancelPatrolRound: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
  useCreatePatrolCheckpoint: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
}));

vi.mock('@/types/generated/operacional/operacional-rondas-de-inspecao/operacional-rondas-de-inspecao', () => ({
  useGetStatsApiV1OperacionalRondasStatsGet: vi.fn(() => ({
    data: { total: 10, by_status: { in_progress: 3, completed: 7 } },
    isLoading: false,
    error: null,
    refetch: mockRefetch,
  })),
}));

describe('usePatrolRounds', () => {
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

  describe('usePatrolRounds - Estado Inicial', () => {
    it('deve retornar valores iniciais', () => {
      const { result } = renderHook(() => usePatrolRounds(), { wrapper });

      expect(result.current.patrolRounds).toHaveLength(2);
      expect(result.current.total).toBe(2);
      expect(result.current.page).toBe(1);
      expect(result.current.pageSize).toBe(10);
      expect(result.current.totalPages).toBe(1);
    });

    it('deve aceitar opções personalizadas', () => {
      const { result } = renderHook(
        () => usePatrolRounds({ initialPageSize: 25, autoLoad: false }),
        { wrapper }
      );

      expect(result.current.pageSize).toBe(25);
    });
  });

  describe('usePatrolRounds - Paginação e Filtros', () => {
    it('deve atualizar filtros e resetar página', async () => {
      const { result } = renderHook(() => usePatrolRounds(), { wrapper });

      await act(async () => {
        result.current.setPage(3);
      });

      await waitFor(() => {
        expect(result.current.page).toBe(3);
      });

      await act(async () => {
        result.current.setFilters({ status: 'em_andamento' });
      });

      await waitFor(() => {
        expect(result.current.filters).toEqual({ status: 'em_andamento' });
        expect(result.current.page).toBe(1);
      });
    });

    it('deve atualizar pageSize', async () => {
      const { result } = renderHook(() => usePatrolRounds(), { wrapper });

      await act(async () => {
        result.current.setPageSize(50);
      });

      await waitFor(() => {
        expect(result.current.pageSize).toBe(50);
      });
    });
  });

  describe('usePatrolRounds - Refresh', () => {
    it('deve chamar refetch', async () => {
      const { result } = renderHook(() => usePatrolRounds(), { wrapper });

      await act(async () => {
        await result.current.refresh();
      });

      await waitFor(() => {
        expect(mockRefetch).toHaveBeenCalled();
      });
    });
  });

  describe('usePatrolRoundStats', () => {
    it('deve retornar estatísticas', () => {
      const { result } = renderHook(() => usePatrolRoundStats(), { wrapper });

      expect(result.current.stats).toEqual({ total: 10, by_status: { in_progress: 3, completed: 7 } });
    });
  });

  describe('usePatrolRoundDetail', () => {
    it('deve retornar null quando id é null', () => {
      const { result } = renderHook(() => usePatrolRoundDetail(null), { wrapper });

      expect(result.current.patrolRound).toBeNull();
    });

    it('deve carregar detalhes quando id é fornecido', () => {
      const { result } = renderHook(() => usePatrolRoundDetail('123'), { wrapper });

      expect(result.current.patrolRound).toEqual({ id: '123', status: 'in_progress' });
    });
  });

  describe('usePatrolRoundMutations', () => {
    it('deve criar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', post_name: 'Posto A' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let created: unknown;
      await act(async () => {
        created = await result.current.createPatrolRound({ post_id: '123' } as any);
      });

      await waitFor(() => {
        expect(created).toEqual({ id: '1', post_name: 'Posto A' });
      });
    });

    it('deve atualizar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', notes: 'Updated' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let updated: unknown;
      await act(async () => {
        updated = await result.current.updatePatrolRound('1', { notes: 'Updated' } as any);
      });

      await waitFor(() => {
        expect(updated).toEqual({ id: '1', notes: 'Updated' });
      });
    });

    it('deve deletar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce(undefined);

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let deleted: boolean;
      await act(async () => {
        deleted = await result.current.deletePatrolRound('1');
      });

      await waitFor(() => {
        expect(deleted).toBe(true);
      });
    });

    it('deve iniciar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', status: 'in_progress' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let started: unknown;
      await act(async () => {
        started = await result.current.startRound('1', { latitude: -23.5, longitude: -46.6 });
      });

      await waitFor(() => {
        expect(started).toEqual({ id: '1', status: 'in_progress' });
      });
    });

    it('deve pausar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', status: 'paused' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let paused: unknown;
      await act(async () => {
        paused = await result.current.pauseRound('1');
      });

      await waitFor(() => {
        expect(paused).toEqual({ id: '1', status: 'paused' });
      });
    });

    it('deve retomar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', status: 'in_progress' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let resumed: unknown;
      await act(async () => {
        resumed = await result.current.resumeRound('1');
      });

      await waitFor(() => {
        expect(resumed).toEqual({ id: '1', status: 'in_progress' });
      });
    });

    it('deve completar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', status: 'completed' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let completed: unknown;
      await act(async () => {
        completed = await result.current.completeRound('1', { summary: 'Done' });
      });

      await waitFor(() => {
        expect(completed).toEqual({ id: '1', status: 'completed' });
      });
    });

    it('deve cancelar ronda', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: '1', status: 'cancelled' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let cancelled: unknown;
      await act(async () => {
        cancelled = await result.current.cancelRound('1', 'Motivo');
      });

      await waitFor(() => {
        expect(cancelled).toEqual({ id: '1', status: 'cancelled' });
      });
    });

    it('deve adicionar checkpoint', async () => {
      mockMutateAsync.mockResolvedValueOnce({ id: 'check-1', location: 'Ponto 1' });

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let checkpoint: unknown;
      await act(async () => {
        checkpoint = await result.current.addCheckpoint('1', { location: 'Ponto 1' } as any);
      });

      await waitFor(() => {
        expect(checkpoint).toEqual({ id: 'check-1', location: 'Ponto 1' });
      });
    });

    it('deve retornar null quando operação falha', async () => {
      mockMutateAsync.mockRejectedValueOnce(new Error('Failed'));

      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      let created: unknown;
      await act(async () => {
        created = await result.current.createPatrolRound({} as any);
      });

      await waitFor(() => {
        expect(created).toBeNull();
      });
      expect(result.current.error).toBe('Failed');
    });

    it('deve refletir estado de loading inicial', () => {
      // O hook deve iniciar com isLoading = false quando não há operações pendentes
      const { result } = renderHook(() => usePatrolRoundMutations(), { wrapper });

      expect(result.current.isLoading).toBe(false);
      expect(typeof result.current.createPatrolRound).toBe('function');
      expect(typeof result.current.startRound).toBe('function');
    });
  });
});
