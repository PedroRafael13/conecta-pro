/**
 * Hooks customizados para o modulo de Reembolso
 *
 * Wrappers de compatibilidade sobre os hooks Orval de @/hooks/reimbursement/
 */

import { useState, useCallback, useMemo } from 'react';
import {
  useReimbursementRequests as useReimbursementRequestsOrval,
  useMyReimbursementRequests,
  useReimbursementRequest,
  useReimbursementStats as useReimbursementStatsOrval,
  useExpenseCategories,
  usePendingReimbursementApprovals,
  useReadyForPaymentReimbursements,
} from '@/hooks/reimbursement';
import type {
  ReimbursementRequest,
  ReimbursementFilter,
  ReimbursementStats,
  ReimbursementCategory,
} from '@/types/reimbursement';

// ==============================================================================
// useReimbursements
// ==============================================================================

interface UseReimbursementsOptions {
  initialPageSize?: number;
  myOnly?: boolean;
  autoLoad?: boolean;
}

interface UseReimbursementsResult {
  requests: ReimbursementRequest[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: ReimbursementFilter;
  setFilters: (filters: ReimbursementFilter) => void;
  setPage: (page: number) => void;
  refresh: () => void;
}

export function useReimbursements(
  options: UseReimbursementsOptions = {}
): UseReimbursementsResult {
  const { initialPageSize = 20, myOnly = false, autoLoad = true } = options;

  const [page, setPageState] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [filters, setFiltersState] = useState<ReimbursementFilter>({});

  const queryParams = useMemo(() => ({
    page,
    page_size: pageSize,
    status: filters.status,
    approval_level: filters.approval_level,
    requester_id: filters.requester_id,
    expense_date_start: filters.expense_date_start,
    expense_date_end: filters.expense_date_end,
    min_amount: filters.min_amount,
    max_amount: filters.max_amount,
    search: filters.search,
    cost_center: filters.cost_center,
    project: filters.project,
  }), [page, pageSize, filters]);

  const allQuery = useReimbursementRequestsOrval(
    myOnly ? undefined : queryParams,
    { enabled: autoLoad && !myOnly }
  );

  const myQuery = useMyReimbursementRequests(
    myOnly ? { page, page_size: pageSize, status: filters.status } : undefined,
    { enabled: autoLoad && myOnly }
  );

  const query = myOnly ? myQuery : allQuery;

  const handleSetFilters = useCallback((newFilters: ReimbursementFilter) => {
    setFiltersState(newFilters);
    setPageState(1);
  }, []);

  const setPage = useCallback((p: number) => {
    setPageState(p);
  }, []);

  const refresh = useCallback(() => {
    query.refetch();
  }, [query]);

  return {
    requests: (query.data as any)?.items ?? [],
    total: (query.data as any)?.total ?? 0,
    page,
    pageSize,
    totalPages: (query.data as any)?.total_pages ?? 0,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar reembolsos' : null,
    filters,
    setFilters: handleSetFilters,
    setPage,
    refresh,
  };
}

// ==============================================================================
// useReimbursementStats
// ==============================================================================

interface UseReimbursementStatsOptions {
  myOnly?: boolean;
  autoLoad?: boolean;
}

interface UseReimbursementStatsResult {
  stats: ReimbursementStats | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useReimbursementStats(
  options: UseReimbursementStatsOptions = {}
): UseReimbursementStatsResult {
  const { myOnly = false, autoLoad = true } = options;

  const query = useReimbursementStatsOrval(myOnly, {
    enabled: autoLoad,
  });

  const refresh = useCallback(() => {
    query.refetch();
  }, [query]);

  return {
    stats: (query.data as unknown as ReimbursementStats) ?? null,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar estatisticas' : null,
    refresh,
  };
}

// ==============================================================================
// useReimbursementDetail
// ==============================================================================

interface UseReimbursementDetailResult {
  request: ReimbursementRequest | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useReimbursementDetail(
  requestId: string | null
): UseReimbursementDetailResult {
  const query = useReimbursementRequest(requestId ?? '', {
    enabled: !!requestId,
  });

  const refresh = useCallback(() => {
    query.refetch();
  }, [query]);

  return {
    request: (query.data as unknown as ReimbursementRequest) ?? null,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar solicitação' : null,
    refresh,
  };
}

// ==============================================================================
// usePendingApprovals
// ==============================================================================

interface UsePendingApprovalsOptions {
  initialPageSize?: number;
  approvalLevel?: string;
  autoLoad?: boolean;
}

interface UsePendingApprovalsResult {
  requests: ReimbursementRequest[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  approvalLevel: string | undefined;
  setApprovalLevel: (level: string | undefined) => void;
  setPage: (page: number) => void;
  refresh: () => void;
}

export function usePendingApprovals(
  options: UsePendingApprovalsOptions = {}
): UsePendingApprovalsResult {
  const { initialPageSize = 20, approvalLevel: initialLevel, autoLoad = true } = options;

  const [page, setPageState] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [approvalLevel, setApprovalLevelState] = useState<string | undefined>(initialLevel);

  const query = usePendingReimbursementApprovals(
    { page, page_size: pageSize, approval_level: approvalLevel },
    { enabled: autoLoad }
  );

  const handleSetApprovalLevel = useCallback((level: string | undefined) => {
    setApprovalLevelState(level);
    setPageState(1);
  }, []);

  const setPage = useCallback((p: number) => {
    setPageState(p);
  }, []);

  const refresh = useCallback(() => {
    query.refetch();
  }, [query]);

  return {
    requests: (query.data as any)?.items ?? [],
    total: (query.data as any)?.total ?? 0,
    page,
    pageSize,
    totalPages: (query.data as any)?.total_pages ?? 0,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar aprovações' : null,
    approvalLevel,
    setApprovalLevel: handleSetApprovalLevel,
    setPage,
    refresh,
  };
}

// ==============================================================================
// useReimbursementCategories
// ==============================================================================

interface UseReimbursementCategoriesResult {
  categories: ReimbursementCategory[];
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useReimbursementCategories(): UseReimbursementCategoriesResult {
  const query = useExpenseCategories();

  const refresh = useCallback(() => {
    query.refetch();
  }, [query]);

  return {
    categories: (query.data as ReimbursementCategory[]) ?? [],
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar categorias' : null,
    refresh,
  };
}

// ==============================================================================
// useReadyForPayment
// ==============================================================================

interface UseReadyForPaymentOptions {
  initialPageSize?: number;
  autoLoad?: boolean;
}

interface UseReadyForPaymentResult {
  requests: ReimbursementRequest[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  setPage: (page: number) => void;
  refresh: () => void;
}

export function useReadyForPayment(
  options: UseReadyForPaymentOptions = {}
): UseReadyForPaymentResult {
  const { initialPageSize = 20, autoLoad = true } = options;

  const [page, setPageState] = useState(1);
  const [pageSize] = useState(initialPageSize);

  const query = useReadyForPaymentReimbursements(
    { page, page_size: pageSize },
    { enabled: autoLoad }
  );

  const setPage = useCallback((p: number) => {
    setPageState(p);
  }, []);

  const refresh = useCallback(() => {
    query.refetch();
  }, [query]);

  return {
    requests: (query.data as any)?.items ?? [],
    total: (query.data as any)?.total ?? 0,
    page,
    pageSize,
    totalPages: (query.data as any)?.total_pages ?? 0,
    isLoading: query.isLoading,
    error: query.error ? (query.error as Error).message || 'Erro ao carregar pagamentos' : null,
    setPage,
    refresh,
  };
}
