'use client';

import { useState, useEffect, useCallback } from 'react';
import { customInstance } from '@/lib/api-client';
import type { Shift, ShiftFilter, ShiftCreate, ShiftUpdate, ShiftCheckIn, ShiftCheckOut, PaginatedResponse } from '@/types/operacional';

const BASE_URL = '/api/v1/operacional/shifts';

function buildParams(page: number, pageSize: number, filters?: ShiftFilter): string {
  const params = new URLSearchParams();
  params.append('page', String(page));
  params.append('page_size', String(pageSize));
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
  }
  return params.toString();
}

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
      const response = await customInstance<PaginatedResponse<Shift>>({
        url: `${BASE_URL}/?${buildParams(page, pageSize, filters)}`,
        method: 'GET',
      });
      setShifts(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar turnos');
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
      const params = new URLSearchParams();
      if (postId) params.append('post_id', postId);
      const qs = params.toString();

      const response = await customInstance<PaginatedResponse<Shift>>({
        url: `${BASE_URL}/today${qs ? `?${qs}` : ''}`,
        method: 'GET',
      });
      setShifts(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar turnos do dia');
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

interface UseShiftOperationsReturn {
  isLoading: boolean;
  error: string | null;
  createShift: (data: ShiftCreate) => Promise<Shift | null>;
  updateShift: (id: string, data: ShiftUpdate) => Promise<Shift | null>;
  deleteShift: (id: string) => Promise<boolean>;
  checkIn: (id: string, data: ShiftCheckIn) => Promise<Shift | null>;
  checkOut: (id: string, data: ShiftCheckOut) => Promise<Shift | null>;
}

export function useShiftOperations(): UseShiftOperationsReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createShift = useCallback(async (data: ShiftCreate): Promise<Shift | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const shift = await customInstance<Shift>({
        url: `${BASE_URL}/`,
        method: 'POST',
        data,
      });
      return shift;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao criar turno';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateShift = useCallback(async (id: string, data: ShiftUpdate): Promise<Shift | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const shift = await customInstance<Shift>({
        url: `${BASE_URL}/${id}`,
        method: 'PATCH',
        data,
      });
      return shift;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao atualizar turno';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteShift = useCallback(async (id: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      await customInstance<void>({
        url: `${BASE_URL}/${id}`,
        method: 'DELETE',
      });
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao deletar turno';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const checkIn = useCallback(async (id: string, data: ShiftCheckIn): Promise<Shift | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const shift = await customInstance<Shift>({
        url: `${BASE_URL}/${id}/check-in`,
        method: 'POST',
        data,
      });
      return shift;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao registrar entrada';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const checkOut = useCallback(async (id: string, data: ShiftCheckOut): Promise<Shift | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const shift = await customInstance<Shift>({
        url: `${BASE_URL}/${id}/check-out`,
        method: 'POST',
        data,
      });
      return shift;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao registrar saída';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    createShift,
    updateShift,
    deleteShift,
    checkIn,
    checkOut,
  };
}
