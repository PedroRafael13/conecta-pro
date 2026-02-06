/**
 * Hooks para o módulo de Rondas de Inspeção
 * Reescrito para usar hooks Orval (React Query) internamente
 */

import { useState, useCallback, useMemo } from 'react';
import {
  usePatrolRounds as useOrvalPatrolRounds,
  usePatrolRound as useOrvalPatrolRound,
  useCreatePatrolRound as useOrvalCreatePatrolRound,
  useUpdatePatrolRound as useOrvalUpdatePatrolRound,
  useDeletePatrolRound as useOrvalDeletePatrolRound,
  useStartPatrolRound as useOrvalStartPatrolRound,
  usePausePatrolRound as useOrvalPausePatrolRound,
  useResumePatrolRound as useOrvalResumePatrolRound,
  useCompletePatrolRound as useOrvalCompletePatrolRound,
  useCancelPatrolRound as useOrvalCancelPatrolRound,
  useCreatePatrolCheckpoint as useOrvalCreateCheckpoint,
} from '@/hooks/operacional/usePatrolRounds';
import {
  useGetStatsApiV1OperacionalRondasStatsGet,
} from '@/types/generated/operacional/operacional-rondas-de-inspecao/operacional-rondas-de-inspecao';
import type {
  PatrolRound,
  PatrolRoundFilter,
  PatrolRoundStats,
  PatrolRoundCreate,
  PatrolRoundUpdate,
  CheckpointCreate,
  PatrolCheckpoint,
} from '@/types/operacional';

interface UsePatrolRoundsOptions {
  initialPageSize?: number;
  autoLoad?: boolean;
  initialFilters?: PatrolRoundFilter;
}

interface UsePatrolRoundsReturn {
  patrolRounds: PatrolRound[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: PatrolRoundFilter;
  setFilters: (filters: PatrolRoundFilter) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => Promise<void>;
}

export function usePatrolRounds(
  options: UsePatrolRoundsOptions = {}
): UsePatrolRoundsReturn {
  const { initialPageSize = 10, autoLoad = true, initialFilters = {} } = options;

  const [page, setPageState] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFiltersState] = useState<PatrolRoundFilter>(initialFilters);

  const params = useMemo(() => {
    const p: Record<string, unknown> = {
      page,
      page_size: pageSize,
    };
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          p[key] = value;
        }
      });
    }
    return p;
  }, [page, pageSize, filters]);

  const { data, isLoading, error, refetch } = useOrvalPatrolRounds(params, {
    query: { enabled: autoLoad },
  });

  const setFilters = useCallback((newFilters: PatrolRoundFilter) => {
    setFiltersState(newFilters);
    setPageState(1);
  }, []);

  const setPage = useCallback((newPage: number) => {
    setPageState(newPage);
  }, []);

  return {
    patrolRounds: (data?.items ?? []) as PatrolRound[],
    total: data?.total ?? 0,
    page,
    pageSize,
    totalPages: data?.pages ?? 0,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar rondas') : null,
    filters,
    setFilters,
    setPage,
    setPageSize,
    refresh: async () => { await refetch(); },
  };
}

export function usePatrolRoundStats() {
  const { data, isLoading, error, refetch } = useGetStatsApiV1OperacionalRondasStatsGet();

  return {
    stats: (data ?? null) as PatrolRoundStats | null,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar estatísticas') : null,
    refresh: async () => { await refetch(); },
  };
}

export function usePatrolRoundDetail(id: string | null) {
  const { data, isLoading, error, refetch } = useOrvalPatrolRound(id ?? '', {
    query: { enabled: !!id },
  });

  return {
    patrolRound: (data ?? null) as PatrolRound | null,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar ronda') : null,
    refresh: async () => { await refetch(); },
  };
}

export function usePatrolRoundMutations() {
  const createMutation = useOrvalCreatePatrolRound();
  const updateMutation = useOrvalUpdatePatrolRound();
  const deleteMutation = useOrvalDeletePatrolRound();
  const startMutation = useOrvalStartPatrolRound();
  const pauseMutation = useOrvalPausePatrolRound();
  const resumeMutation = useOrvalResumePatrolRound();
  const completeMutation = useOrvalCompletePatrolRound();
  const cancelMutation = useOrvalCancelPatrolRound();
  const checkpointMutation = useOrvalCreateCheckpoint();

  const isLoading =
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending ||
    startMutation.isPending ||
    pauseMutation.isPending ||
    resumeMutation.isPending ||
    completeMutation.isPending ||
    cancelMutation.isPending ||
    checkpointMutation.isPending;

  const [error, setError] = useState<string | null>(null);

  const createPatrolRound = useCallback(
    async (data: PatrolRoundCreate): Promise<PatrolRound | null> => {
      setError(null);
      try {
        const result = await createMutation.mutateAsync({ data });
        return result as unknown as PatrolRound;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao criar ronda');
        return null;
      }
    },
    [createMutation]
  );

  const updatePatrolRound = useCallback(
    async (id: string, data: PatrolRoundUpdate): Promise<PatrolRound | null> => {
      setError(null);
      try {
        const result = await updateMutation.mutateAsync({ roundId: id, data });
        return result as unknown as PatrolRound;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao atualizar ronda');
        return null;
      }
    },
    [updateMutation]
  );

  const deletePatrolRound = useCallback(async (id: string): Promise<boolean> => {
    setError(null);
    try {
      await deleteMutation.mutateAsync({ roundId: id });
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao deletar ronda');
      return false;
    }
  }, [deleteMutation]);

  const startRound = useCallback(
    async (
      id: string,
      data?: { latitude?: number; longitude?: number }
    ): Promise<PatrolRound | null> => {
      setError(null);
      try {
        const result = await startMutation.mutateAsync({ roundId: id, data: data ?? null });
        return result as unknown as PatrolRound;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao iniciar ronda');
        return null;
      }
    },
    [startMutation]
  );

  const pauseRound = useCallback(async (id: string): Promise<PatrolRound | null> => {
    setError(null);
    try {
      const result = await pauseMutation.mutateAsync({ roundId: id });
      return result as unknown as PatrolRound;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao pausar ronda');
      return null;
    }
  }, [pauseMutation]);

  const resumeRound = useCallback(
    async (id: string): Promise<PatrolRound | null> => {
      setError(null);
      try {
        const result = await resumeMutation.mutateAsync({ roundId: id });
        return result as unknown as PatrolRound;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao retomar ronda');
        return null;
      }
    },
    [resumeMutation]
  );

  const completeRound = useCallback(
    async (
      id: string,
      data?: { summary?: string; latitude?: number; longitude?: number }
    ): Promise<PatrolRound | null> => {
      setError(null);
      try {
        const result = await completeMutation.mutateAsync({ roundId: id, data: data ?? null });
        return result as unknown as PatrolRound;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao concluir ronda');
        return null;
      }
    },
    [completeMutation]
  );

  const cancelRound = useCallback(
    async (id: string, reason?: string): Promise<PatrolRound | null> => {
      setError(null);
      try {
        const result = await cancelMutation.mutateAsync({
          roundId: id,
          params: reason ? { reason } : undefined,
        });
        return result as unknown as PatrolRound;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao cancelar ronda');
        return null;
      }
    },
    [cancelMutation]
  );

  const addCheckpoint = useCallback(
    async (
      roundId: string,
      checkpoint: CheckpointCreate
    ): Promise<PatrolCheckpoint | null> => {
      setError(null);
      try {
        const result = await checkpointMutation.mutateAsync({ roundId, data: checkpoint });
        return result as unknown as PatrolCheckpoint;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao adicionar checkpoint');
        return null;
      }
    },
    [checkpointMutation]
  );

  return {
    isLoading,
    error,
    createPatrolRound,
    updatePatrolRound,
    deletePatrolRound,
    startRound,
    pauseRound,
    resumeRound,
    completeRound,
    cancelRound,
    addCheckpoint,
  };
}
