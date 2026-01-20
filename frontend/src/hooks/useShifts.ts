'use client';

import { useState, useEffect, useCallback } from 'react';
import { shiftsService } from '@/lib/services/shifts';
import type { Shift, ShiftFilter } from '@/types/operacional';
import { getErrorMessage } from '@/lib/api';

interface UseShiftsOptions {
  autoLoad?: boolean;
  initialPage?: number;
  initialPageSize?: number;
  initialFilters?: ShiftFilter;
}

interface UseShiftsReturn {
  shifts: Shift[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: ShiftFilter;
  setFilters: (filters: ShiftFilter) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => Promise<void>;
}

export function useShifts(options: UseShiftsOptions = {}): UseShiftsReturn {
  const {
    autoLoad = true,
    initialPage = 1,
    initialPageSize = 50,
    initialFilters = {},
  } = options;

  const [shifts, setShifts] = useState<Shift[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ShiftFilter>(initialFilters);

  const loadShifts = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await shiftsService.list(page, pageSize, filters);
      setShifts(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setShifts([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, filters]);

  useEffect(() => {
    if (autoLoad) {
      loadShifts();
    }
  }, [autoLoad, loadShifts]);

  return {
    shifts,
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
    refresh: loadShifts,
  };
}

interface UseTodayShiftsReturn {
  shifts: Shift[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useTodayShifts(postId?: string): UseTodayShiftsReturn {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadToday = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await shiftsService.listToday(postId);
      setShifts(response.items);
    } catch (err) {
      setError(getErrorMessage(err));
      setShifts([]);
    } finally {
      setIsLoading(false);
    }
  }, [postId]);

  useEffect(() => {
    loadToday();
  }, [loadToday]);

  return { shifts, isLoading, error, refresh: loadToday };
}
