/**
 * Hooks para o módulo de Medidas Administrativas
 */

import { useState, useEffect, useCallback } from 'react';
import { disciplinaryService } from '@/lib/services/disciplinary';
import { getErrorMessage } from '@/lib/api';
import type {
  DisciplinaryAction,
  DisciplinaryFilter,
  DisciplinaryStats,
  DisciplinaryActionStatus,
  DisciplinaryActionType,
} from '@/types/disciplinary';

interface UseDisciplinaryOptions {
  initialPageSize?: number;
  autoLoad?: boolean;
}

interface UseDisciplinaryReturn {
  actions: DisciplinaryAction[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: DisciplinaryFilter;
  setFilters: (filters: DisciplinaryFilter) => void;
  setPage: (page: number) => void;
  refresh: () => Promise<void>;
}

/**
 * Hook para listar medidas administrativas com paginação e filtros
 */
export function useDisciplinary(options: UseDisciplinaryOptions = {}): UseDisciplinaryReturn {
  const { initialPageSize = 10, autoLoad = true } = options;

  const [actions, setActions] = useState<DisciplinaryAction[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<DisciplinaryFilter>({});

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await disciplinaryService.list({
        ...filters,
        page,
        page_size: pageSize,
      });

      setActions(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
      setActions([]);
    } finally {
      setIsLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    if (autoLoad) {
      fetchData();
    }
  }, [fetchData, autoLoad]);

  const handleSetFilters = useCallback((newFilters: DisciplinaryFilter) => {
    setFilters(newFilters);
    setPage(1);
  }, []);

  return {
    actions,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters: handleSetFilters,
    setPage,
    refresh: fetchData,
  };
}

/**
 * Hook para estatísticas de medidas administrativas
 */
export function useDisciplinaryStats() {
  const [stats, setStats] = useState<DisciplinaryStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await disciplinaryService.getStats();
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
 * Hook para detalhes de uma medida
 */
export function useDisciplinaryDetail(id: string | null) {
  const [action, setAction] = useState<DisciplinaryAction | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAction = useCallback(async () => {
    if (!id) {
      setAction(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await disciplinaryService.getById(id);
      setAction(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAction();
  }, [fetchAction]);

  return {
    action,
    isLoading,
    error,
    refresh: fetchAction,
  };
}

/**
 * Hook para medidas pendentes de aprovação
 */
export function usePendingApprovals() {
  const [actions, setActions] = useState<DisciplinaryAction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPending = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await disciplinaryService.listPending();
      setActions(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPending();
  }, [fetchPending]);

  return {
    actions,
    total: actions.length,
    isLoading,
    error,
    refresh: fetchPending,
  };
}

/**
 * Hook para medidas de um funcionário
 */
export function useEmployeeDisciplinary(employeeId: string | null) {
  const [actions, setActions] = useState<DisciplinaryAction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchActions = useCallback(async () => {
    if (!employeeId) {
      setActions([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await disciplinaryService.listByEmployee(employeeId);
      setActions(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [employeeId]);

  useEffect(() => {
    fetchActions();
  }, [fetchActions]);

  return {
    actions,
    total: actions.length,
    isLoading,
    error,
    refresh: fetchActions,
  };
}
