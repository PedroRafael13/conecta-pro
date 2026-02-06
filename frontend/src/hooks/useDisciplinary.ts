/**
 * Hooks para o módulo de Medidas Administrativas
 * Reescrito para usar hooks Orval (React Query) internamente
 */

import { useState, useCallback, useMemo } from 'react';
import {
  useDisciplinaryActions as useOrvalDisciplinaryActions,
  useDisciplinaryAction as useOrvalDisciplinaryAction,
  useDisciplinaryActionsByEmployee as useOrvalDisciplinaryActionsByEmployee,
  usePendingDisciplinaryApprovals as useOrvalPendingApprovals,
} from '@/hooks/operacional/useDisciplinary';
import {
  useGetDisciplinaryStatsApiV1OperacionalMedidasAdministrativasEstatisticasGet,
} from '@/types/generated/operacional/operacional-medidas-administrativas/operacional-medidas-administrativas';
import type {
  DisciplinaryAction,
  DisciplinaryFilter,
  DisciplinaryStats,
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

export function useDisciplinary(options: UseDisciplinaryOptions = {}): UseDisciplinaryReturn {
  const { initialPageSize = 10, autoLoad = true } = options;

  const [page, setPageState] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [filters, setFiltersState] = useState<DisciplinaryFilter>({});

  const params = useMemo(() => {
    const p: Record<string, unknown> = {
      page,
      page_size: pageSize,
    };
    if (filters.search) p.search = filters.search;
    if (filters.status) p.status = filters.status;
    if (filters.action_type) p.action_type = filters.action_type;
    if (filters.employee_id) p.employee_id = filters.employee_id;
    if (filters.date_from) p.incident_date_from = filters.date_from;
    if (filters.date_to) p.incident_date_to = filters.date_to;
    return p;
  }, [page, pageSize, filters]);

  const { data, isLoading, error, refetch } = useOrvalDisciplinaryActions(params, {
    query: { enabled: autoLoad },
  });

  const setFilters = useCallback((newFilters: DisciplinaryFilter) => {
    setFiltersState(newFilters);
    setPageState(1);
  }, []);

  const setPage = useCallback((newPage: number) => {
    setPageState(newPage);
  }, []);

  return {
    actions: (data?.items ?? []) as unknown as DisciplinaryAction[],
    total: data?.total ?? 0,
    page,
    pageSize,
    totalPages: data?.total_pages ?? 0,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar medidas') : null,
    filters,
    setFilters: setFilters,
    setPage,
    refresh: async () => { await refetch(); },
  };
}

export function useDisciplinaryStats() {
  const { data, isLoading, error, refetch } = useGetDisciplinaryStatsApiV1OperacionalMedidasAdministrativasEstatisticasGet();

  return {
    stats: (data ?? null) as DisciplinaryStats | null,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar estatísticas') : null,
    refresh: async () => { await refetch(); },
  };
}

export function useDisciplinaryDetail(id: string | null) {
  const { data, isLoading, error, refetch } = useOrvalDisciplinaryAction(id ?? '', {
    query: { enabled: !!id },
  });

  return {
    action: (data ?? null) as DisciplinaryAction | null,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar medida') : null,
    refresh: async () => { await refetch(); },
  };
}

export function usePendingApprovals() {
  const { data, isLoading, error, refetch } = useOrvalPendingApprovals();

  const actions = (data ?? []) as unknown as DisciplinaryAction[];

  return {
    actions,
    total: actions.length,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar pendentes') : null,
    refresh: async () => { await refetch(); },
  };
}

export function useEmployeeDisciplinary(employeeId: string | null) {
  const { data, isLoading, error, refetch } = useOrvalDisciplinaryActionsByEmployee(
    employeeId ?? '',
    { query: { enabled: !!employeeId } }
  );

  const actions = (data ?? []) as unknown as DisciplinaryAction[];

  return {
    actions,
    total: actions.length,
    isLoading,
    error: error ? (error instanceof Error ? error.message : 'Erro ao carregar medidas do funcionário') : null,
    refresh: async () => { await refetch(); },
  };
}
