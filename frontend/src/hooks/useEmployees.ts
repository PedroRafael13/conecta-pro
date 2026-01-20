'use client';

import { useState, useEffect, useCallback } from 'react';
import { employeesService } from '@/lib/services/employees';
import type { Employee } from '@/types/operacional';
import { getErrorMessage } from '@/lib/api';

interface UseEmployeesOptions {
  autoLoad?: boolean;
  initialPage?: number;
  initialPageSize?: number;
  initialStatus?: string;
}

interface UseEmployeesReturn {
  employees: Employee[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  setPage: (page: number) => void;
  refresh: () => Promise<void>;
}

export function useEmployees(options: UseEmployeesOptions = {}): UseEmployeesReturn {
  const {
    autoLoad = true,
    initialPage = 1,
    initialPageSize = 100,
    initialStatus = 'ativo',
  } = options;

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialPage);
  const [pageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadEmployees = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await employeesService.list(page, pageSize, undefined, initialStatus);
      setEmployees(response.items || []);
      setTotal(response.total || 0);
      setTotalPages(response.total_pages || 0);
    } catch (err) {
      setError(getErrorMessage(err));
      setEmployees([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, initialStatus]);

  useEffect(() => {
    if (autoLoad) {
      loadEmployees();
    }
  }, [autoLoad, loadEmployees]);

  return {
    employees,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    setPage,
    refresh: loadEmployees,
  };
}
