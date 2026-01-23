/**
 * Hooks para o módulo de Rondas de Inspeção
 */

import { useState, useEffect, useCallback } from 'react';
import { patrolRoundsService } from '@/lib/services/patrol-rounds';
import { getErrorMessage } from '@/lib/api';
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

/**
 * Hook para listar rondas com paginação e filtros
 */
export function usePatrolRounds(
  options: UsePatrolRoundsOptions = {}
): UsePatrolRoundsReturn {
  const { initialPageSize = 10, autoLoad = true, initialFilters = {} } = options;

  const [patrolRounds, setPatrolRounds] = useState<PatrolRound[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<PatrolRoundFilter>(initialFilters);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await patrolRoundsService.list(page, pageSize, filters);
      setPatrolRounds(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setPatrolRounds([]);
    } finally {
      setIsLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    if (autoLoad) {
      fetchData();
    }
  }, [fetchData, autoLoad]);

  const setFilters = useCallback((newFilters: PatrolRoundFilter) => {
    setFiltersState(newFilters);
    setPage(1);
  }, []);

  return {
    patrolRounds,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters,
    setPage,
    setPageSize,
    refresh: fetchData,
  };
}

/**
 * Hook para estatísticas de rondas
 */
export function usePatrolRoundStats() {
  const [stats, setStats] = useState<PatrolRoundStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await patrolRoundsService.getStats();
      setStats(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    isLoading,
    error,
    refresh: fetchStats,
  };
}

/**
 * Hook para detalhes de uma ronda
 */
export function usePatrolRoundDetail(id: string | null) {
  const [patrolRound, setPatrolRound] = useState<PatrolRound | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPatrolRound = useCallback(async () => {
    if (!id) {
      setPatrolRound(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await patrolRoundsService.getById(id);
      setPatrolRound(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchPatrolRound();
  }, [fetchPatrolRound]);

  return {
    patrolRound,
    isLoading,
    error,
    refresh: fetchPatrolRound,
  };
}

/**
 * Hook para mutations de rondas (criar, atualizar, deletar)
 */
export function usePatrolRoundMutations() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createPatrolRound = useCallback(
    async (data: PatrolRoundCreate): Promise<PatrolRound | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await patrolRoundsService.create(data);
        return result;
      } catch (err) {
        setError(getErrorMessage(err));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const updatePatrolRound = useCallback(
    async (id: string, data: PatrolRoundUpdate): Promise<PatrolRound | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await patrolRoundsService.update(id, data);
        return result;
      } catch (err) {
        setError(getErrorMessage(err));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const deletePatrolRound = useCallback(async (id: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      await patrolRoundsService.delete(id);
      return true;
    } catch (err) {
      setError(getErrorMessage(err));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startRound = useCallback(
    async (
      id: string,
      data?: { latitude?: number; longitude?: number }
    ): Promise<PatrolRound | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await patrolRoundsService.start(id, data);
        return result;
      } catch (err) {
        setError(getErrorMessage(err));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const pauseRound = useCallback(async (id: string): Promise<PatrolRound | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await patrolRoundsService.pause(id);
      return result;
    } catch (err) {
      setError(getErrorMessage(err));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resumeRound = useCallback(
    async (id: string): Promise<PatrolRound | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await patrolRoundsService.resume(id);
        return result;
      } catch (err) {
        setError(getErrorMessage(err));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const completeRound = useCallback(
    async (
      id: string,
      data?: { summary?: string; latitude?: number; longitude?: number }
    ): Promise<PatrolRound | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await patrolRoundsService.complete(id, data);
        return result;
      } catch (err) {
        setError(getErrorMessage(err));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const cancelRound = useCallback(
    async (id: string, reason?: string): Promise<PatrolRound | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await patrolRoundsService.cancel(id, reason);
        return result;
      } catch (err) {
        setError(getErrorMessage(err));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const addCheckpoint = useCallback(
    async (
      roundId: string,
      checkpoint: CheckpointCreate
    ): Promise<PatrolCheckpoint | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await patrolRoundsService.addCheckpoint(roundId, checkpoint);
        return result;
      } catch (err) {
        setError(getErrorMessage(err));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
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
