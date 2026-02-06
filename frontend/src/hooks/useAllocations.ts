'use client';

import { useState, useCallback, useMemo } from 'react';
import { useAllocations as useAllocationsOrval } from '@/hooks/operacional/useAllocations';
import type { AllocationFilter } from '@/types/operacional';

interface UseAllocationsOptions {
  autoLoad?: boolean;
  initialPage?: number;
  initialPageSize?: number;
  initialFilters?: AllocationFilter;
}

interface UseAllocationsReturn {
  allocations: any[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: AllocationFilter;
  setFilters: (filters: AllocationFilter) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => Promise<void>;
}

export function useAllocations(options: UseAllocationsOptions = {}): UseAllocationsReturn {
  const {
    autoLoad = true,
    initialPage = 1,
    initialPageSize = 20,
    initialFilters = {},
  } = options;

  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFiltersState] = useState<AllocationFilter>(initialFilters);

  const query = useAllocationsOrval(
    {
      page,
      page_size: pageSize,
      post_id: filters.post_id ?? undefined,
      employee_id: filters.employee_id ?? undefined,
      status: filters.status ?? undefined,
      is_primary: filters.is_primary ?? undefined,
      is_temporary: filters.is_temporary ?? undefined,
      is_current: filters.is_current ?? undefined,
      start_date_from: filters.start_date_from ?? undefined,
      start_date_to: filters.start_date_to ?? undefined,
    },
    { query: { enabled: autoLoad } }
  );

  const allocations = useMemo(() => query.data?.items ?? [], [query.data]);
  const total = useMemo(() => query.data?.total ?? 0, [query.data]);
  const totalPages = useMemo(() => query.data?.total_pages ?? 0, [query.data]);

  const setFilters = useCallback((newFilters: AllocationFilter) => {
    setFiltersState(newFilters);
    setPage(1);
  }, []);

  const refresh = useCallback(async () => {
    await query.refetch();
  }, [query]);

  return {
    allocations,
    total,
    page,
    pageSize,
    totalPages,
    isLoading: query.isLoading,
    error: (query.error as Error | null)?.message ?? (query.isError ? 'Erro ao carregar alocacoes' : null),
    filters,
    setFilters,
    setPage,
    setPageSize,
    refresh,
  };
}
