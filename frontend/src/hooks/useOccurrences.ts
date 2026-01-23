/**
 * Hooks para o módulo de Ocorrências Disciplinares
 */

import { useState, useEffect, useCallback } from 'react';
import { occurrencesService } from '@/lib/services/occurrences';
import { getErrorMessage } from '@/lib/api';
import type {
  Occurrence,
  OccurrenceFilter,
  OccurrenceStats,
  OccurrenceCreate,
  OccurrenceUpdate,
  OccurrenceResolve,
} from '@/types/operacional';

interface UseOccurrencesOptions {
  initialPageSize?: number;
  autoLoad?: boolean;
  initialFilters?: OccurrenceFilter;
}

interface UseOccurrencesReturn {
  occurrences: Occurrence[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: OccurrenceFilter;
  setFilters: (filters: OccurrenceFilter) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => Promise<void>;
}

/**
 * Hook para listar ocorrências com paginação e filtros
 */
export function useOccurrences(options: UseOccurrencesOptions = {}): UseOccurrencesReturn {
  const { initialPageSize = 10, autoLoad = true, initialFilters = {} } = options;

  const [occurrences, setOccurrences] = useState<Occurrence[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<OccurrenceFilter>(initialFilters);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await occurrencesService.list(page, pageSize, filters);
      setOccurrences(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setOccurrences([]);
    } finally {
      setIsLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    if (autoLoad) {
      fetchData();
    }
  }, [fetchData, autoLoad]);

  const setFilters = useCallback((newFilters: OccurrenceFilter) => {
    setFiltersState(newFilters);
    setPage(1);
  }, []);

  return {
    occurrences,
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
 * Hook para estatísticas de ocorrências
 */
export function useOccurrenceStats() {
  const [stats, setStats] = useState<OccurrenceStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await occurrencesService.getStats();
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
 * Hook para detalhes de uma ocorrência
 */
export function useOccurrenceDetail(id: string | null) {
  const [occurrence, setOccurrence] = useState<Occurrence | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOccurrence = useCallback(async () => {
    if (!id) {
      setOccurrence(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await occurrencesService.getById(id);
      setOccurrence(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchOccurrence();
  }, [fetchOccurrence]);

  return {
    occurrence,
    isLoading,
    error,
    refresh: fetchOccurrence,
  };
}

/**
 * Hook para ocorrências de um posto específico
 */
export function usePostOccurrences(postId: string | null) {
  const [occurrences, setOccurrences] = useState<Occurrence[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOccurrences = useCallback(async () => {
    if (!postId) {
      setOccurrences([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await occurrencesService.listByPost(postId);
      setOccurrences(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [postId]);

  useEffect(() => {
    fetchOccurrences();
  }, [fetchOccurrences]);

  return {
    occurrences,
    total: occurrences.length,
    isLoading,
    error,
    refresh: fetchOccurrences,
  };
}

/**
 * Hook para mutations de ocorrências (criar, atualizar, resolver)
 */
export function useOccurrenceMutations() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createOccurrence = useCallback(async (data: OccurrenceCreate): Promise<Occurrence | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await occurrencesService.create(data);
      return result;
    } catch (err) {
      setError(getErrorMessage(err));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateOccurrence = useCallback(async (id: string, data: OccurrenceUpdate): Promise<Occurrence | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await occurrencesService.update(id, data);
      return result;
    } catch (err) {
      setError(getErrorMessage(err));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resolveOccurrence = useCallback(async (id: string, data: OccurrenceResolve): Promise<Occurrence | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await occurrencesService.resolve(id, data);
      return result;
    } catch (err) {
      setError(getErrorMessage(err));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteOccurrence = useCallback(async (id: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      await occurrencesService.delete(id);
      return true;
    } catch (err) {
      setError(getErrorMessage(err));
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    createOccurrence,
    updateOccurrence,
    resolveOccurrence,
    deleteOccurrence,
  };
}
