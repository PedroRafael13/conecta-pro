/**
 * Hooks customizados para o módulo de Reembolso
 */

import { useState, useEffect, useCallback } from 'react';
import { reimbursementService } from '@/lib/services/reimbursement';
import { getErrorMessage } from '@/lib/api';
import type {
  ReimbursementRequest,
  ReimbursementFilter,
  ReimbursementStats,
  ReimbursementCategory,
  ReimbursementStatus,
} from '@/types/reimbursement';

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

/**
 * Hook para listagem de solicitações de reembolso
 */
export function useReimbursements(
  options: UseReimbursementsOptions = {}
): UseReimbursementsResult {
  const { initialPageSize = 20, myOnly = false, autoLoad = true } = options;

  const [requests, setRequests] = useState<ReimbursementRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ReimbursementFilter>({});

  const fetchRequests = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = myOnly
        ? await reimbursementService.listMy(page, pageSize, filters.status)
        : await reimbursementService.list(page, pageSize, filters);

      setRequests(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, filters, myOnly]);

  useEffect(() => {
    if (autoLoad) {
      fetchRequests();
    }
  }, [fetchRequests, autoLoad]);

  const handleSetFilters = useCallback((newFilters: ReimbursementFilter) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  }, []);

  return {
    requests,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters: handleSetFilters,
    setPage,
    refresh: fetchRequests,
  };
}

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

/**
 * Hook para estatísticas de reembolsos
 */
export function useReimbursementStats(
  options: UseReimbursementStatsOptions = {}
): UseReimbursementStatsResult {
  const { myOnly = false, autoLoad = true } = options;

  const [stats, setStats] = useState<ReimbursementStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await reimbursementService.getStats(myOnly);
      setStats(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [myOnly]);

  useEffect(() => {
    if (autoLoad) {
      fetchStats();
    }
  }, [fetchStats, autoLoad]);

  return {
    stats,
    isLoading,
    error,
    refresh: fetchStats,
  };
}

interface UseReimbursementDetailResult {
  request: ReimbursementRequest | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

/**
 * Hook para detalhes de uma solicitação
 */
export function useReimbursementDetail(
  requestId: string | null
): UseReimbursementDetailResult {
  const [request, setRequest] = useState<ReimbursementRequest | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRequest = useCallback(async () => {
    if (!requestId) {
      setRequest(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await reimbursementService.getById(requestId);
      setRequest(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [requestId]);

  useEffect(() => {
    fetchRequest();
  }, [fetchRequest]);

  return {
    request,
    isLoading,
    error,
    refresh: fetchRequest,
  };
}

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

/**
 * Hook para listagem de aprovações pendentes
 */
export function usePendingApprovals(
  options: UsePendingApprovalsOptions = {}
): UsePendingApprovalsResult {
  const { initialPageSize = 20, approvalLevel: initialLevel, autoLoad = true } = options;

  const [requests, setRequests] = useState<ReimbursementRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [approvalLevel, setApprovalLevel] = useState<string | undefined>(initialLevel);

  const fetchRequests = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await reimbursementService.listPendingApprovals(
        page,
        pageSize,
        approvalLevel
      );

      setRequests(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, approvalLevel]);

  useEffect(() => {
    if (autoLoad) {
      fetchRequests();
    }
  }, [fetchRequests, autoLoad]);

  const handleSetApprovalLevel = useCallback((level: string | undefined) => {
    setApprovalLevel(level);
    setPage(1);
  }, []);

  return {
    requests,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    approvalLevel,
    setApprovalLevel: handleSetApprovalLevel,
    setPage,
    refresh: fetchRequests,
  };
}

interface UseReimbursementCategoriesResult {
  categories: ReimbursementCategory[];
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

/**
 * Hook para listagem de categorias
 */
export function useReimbursementCategories(): UseReimbursementCategoriesResult {
  const [categories, setCategories] = useState<ReimbursementCategory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await reimbursementService.listCategories();
      setCategories(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return {
    categories,
    isLoading,
    error,
    refresh: fetchCategories,
  };
}

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

/**
 * Hook para listagem de reembolsos prontos para pagamento
 */
export function useReadyForPayment(
  options: UseReadyForPaymentOptions = {}
): UseReadyForPaymentResult {
  const { initialPageSize = 20, autoLoad = true } = options;

  const [requests, setRequests] = useState<ReimbursementRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRequests = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await reimbursementService.listReadyForPayment(page, pageSize);

      setRequests(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize]);

  useEffect(() => {
    if (autoLoad) {
      fetchRequests();
    }
  }, [fetchRequests, autoLoad]);

  return {
    requests,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    setPage,
    refresh: fetchRequests,
  };
}
