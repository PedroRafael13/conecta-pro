'use client';

import { useState, useEffect, useCallback } from 'react';
import { customInstance } from '@/lib/api-client';
import type { Employee, PaginatedResponse } from '@/types/operacional';

const BASE_URL = '/api/v1/operacional/employees/';

type BackendEmployee = {
  id: string;
  nome: string;
  email?: string | null;
  matricula?: string | null;
  cargo?: string | null;
  departamento?: string | null;
  status?: string | null;
};

const mapEmployee = (item: BackendEmployee): Employee => ({
  id: item.id,
  full_name: item.nome || undefined,
  name: item.nome || undefined,
  email: item.email || undefined,
  registration: item.matricula || undefined,
  status: item.status || undefined,
});

const normalizeEmployeesResponse = (data: unknown): PaginatedResponse<Employee> => {
  if (Array.isArray(data)) {
    const items = (data as BackendEmployee[]).map(mapEmployee);
    return {
      items,
      total: items.length,
      page: 1,
      page_size: items.length,
      total_pages: 1,
    };
  }

  const payload = data as PaginatedResponse<BackendEmployee>;
  if (payload && Array.isArray(payload.items)) {
    return {
      ...payload,
      items: payload.items.map(mapEmployee),
    };
  }

  return {
    items: [],
    total: 0,
    page: 1,
    page_size: 0,
    total_pages: 0,
  };
};

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
      const data = await customInstance<unknown>({
        url: BASE_URL,
        method: 'GET',
        params: { page, page_size: pageSize, status: initialStatus },
      });

      const response = normalizeEmployeesResponse(data);
      setEmployees(response.items || []);
      setTotal(response.total || 0);
      setTotalPages(response.total_pages || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar funcionários');
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
