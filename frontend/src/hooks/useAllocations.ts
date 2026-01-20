'use client';

import { useState, useEffect, useCallback } from 'react';
import { allocationsService } from '@/lib/services/allocations';
import type { Allocation, AllocationFilter } from '@/types/operacional';
import { getErrorMessage } from '@/lib/api';

interface UseAllocationsOptions {
  autoLoad?: boolean;
  initialPage?: number;
  initialPageSize?: number;
  initialFilters?: AllocationFilter;
}

interface UseAllocationsReturn {
  allocations: Allocation[];
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

  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<AllocationFilter>(initialFilters);

  const loadAllocations = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await allocationsService.list(page, pageSize, filters);
      setAllocations(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setAllocations([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, filters]);

  useEffect(() => {
    if (autoLoad) {
      loadAllocations();
    }
  }, [autoLoad, loadAllocations]);

  return {
    allocations,
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
    refresh: loadAllocations,
  };
}
