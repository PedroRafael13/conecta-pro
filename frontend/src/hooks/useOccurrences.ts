/**
 * Hooks para o módulo de Ocorrências Disciplinares
 * Reescrito para usar hooks Orval (React Query) internamente
 */

import { useState, useCallback, useMemo } from 'react';
import {
  useOccurrences as useOrvalOccurrences,
  useOccurrence as useOrvalOccurrence,
  useOccurrencesByPost as useOrvalOccurrencesByPost,
  useCreateOccurrence as useOrvalCreateOccurrence,
  useUpdateOccurrence as useOrvalUpdateOccurrence,
  useDeleteOccurrence as useOrvalDeleteOccurrence,
  useResolveOccurrence as useOrvalResolveOccurrence,
} from '@/hooks/operacional/useOccurrences';
import {
  useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet,
} from '@/types/generated/operacional/operacional-ocorrencias/operacional-ocorrencias';
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

export function useOccurrences(options: UseOccurrencesOptions = {}): UseOccurrencesReturn {
  const { initialPageSize = 10, autoLoad = true, initialFilters = {} } = options;

  const [page, setPageState] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFiltersState] = useState<OccurrenceFilter>(initialFilters);

  const params = useMemo(() => {
    const p: Record<string, unknown> = {
      page,
      page_size: pageSize,
    };
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          const paramKey = key === 'status' ? 'status_filter' : key;
          p[paramKey] = value;
        }
      });
    }
    return p;
  }, [page, pageSize, filters]);

  const { data, isLoading, error, refetch } = useOrvalOccurrences(params, {
    query: { enabled: autoLoad },
  });

  const setFilters = useCallback((newFilters: OccurrenceFilter) => {
    setFiltersState(newFilters);
    setPageState(1);
  }, []);

  const setPage = useCallback((newPage: number) => {
    setPageState(newPage);
  }, []);

  return {
    occurrences: (data?.items ?? []) as unknown as Occurrence[],
    total: data?.total ?? 0,
    page,
    pageSize,
    totalPages: data?.total_pages ?? 0,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar ocorrências') : null,
    filters,
    setFilters,
    setPage,
    setPageSize,
    refresh: async () => { await refetch(); },
  };
}

export function useOccurrenceStats() {
  const { data, isLoading, error, refetch } = useGetOccurrenceStatsApiV1OperacionalOccurrencesStatsGet();

  return {
    stats: (data ?? null) as OccurrenceStats | null,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar estatísticas') : null,
    refresh: async () => { await refetch(); },
  };
}

export function useOccurrenceDetail(id: string | null) {
  const { data, isLoading, error, refetch } = useOrvalOccurrence(id ?? '', {
    query: { enabled: !!id },
  });

  return {
    occurrence: (data ?? null) as Occurrence | null,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar ocorrência') : null,
    refresh: async () => { await refetch(); },
  };
}

export function usePostOccurrences(postId: string | null) {
  const { data, isLoading, error, refetch } = useOrvalOccurrencesByPost(postId ?? '', {
    query: { enabled: !!postId },
  });

  const occurrences = (data ?? []) as unknown as Occurrence[];

  return {
    occurrences,
    total: occurrences.length,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar ocorrências do posto') : null,
    refresh: async () => { await refetch(); },
  };
}

export function useOccurrenceMutations() {
  const createMutation = useOrvalCreateOccurrence();
  const updateMutation = useOrvalUpdateOccurrence();
  const deleteMutation = useOrvalDeleteOccurrence();
  const resolveMutation = useOrvalResolveOccurrence();

  const isLoading = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending || resolveMutation.isPending;

  const [error, setError] = useState<string | null>(null);

  const createOccurrence = useCallback(async (data: OccurrenceCreate): Promise<Occurrence | null> => {
    setError(null);
    try {
      const result = await createMutation.mutateAsync({ data: data as Parameters<typeof createMutation.mutateAsync>[0]['data'] });
      return result as unknown as Occurrence;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Erro ao criar ocorrência';
      setError(msg);
      return null;
    }
  }, [createMutation]);

  const updateOccurrence = useCallback(async (id: string, data: OccurrenceUpdate): Promise<Occurrence | null> => {
    setError(null);
    try {
      const result = await updateMutation.mutateAsync({ occurrenceId: id, data: data as Parameters<typeof updateMutation.mutateAsync>[0]['data'] });
      return result as unknown as Occurrence;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Erro ao atualizar ocorrência';
      setError(msg);
      return null;
    }
  }, [updateMutation]);

  const resolveOccurrence = useCallback(async (id: string, data: OccurrenceResolve): Promise<Occurrence | null> => {
    setError(null);
    try {
      const result = await resolveMutation.mutateAsync({ occurrenceId: id, data: data as Parameters<typeof resolveMutation.mutateAsync>[0]['data'] });
      return result as unknown as Occurrence;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Erro ao resolver ocorrência';
      setError(msg);
      return null;
    }
  }, [resolveMutation]);

  const deleteOccurrence = useCallback(async (id: string): Promise<boolean> => {
    setError(null);
    try {
      await deleteMutation.mutateAsync({ occurrenceId: id });
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Erro ao deletar ocorrência';
      setError(msg);
      return false;
    }
  }, [deleteMutation]);

  return {
    isLoading,
    error,
    createOccurrence,
    updateOccurrence,
    resolveOccurrence,
    deleteOccurrence,
  };
}
