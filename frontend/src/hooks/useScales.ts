'use client';

import { useState, useEffect, useCallback } from 'react';
import { scalesService } from '@/lib/services/scales';
import type { Scale, ScaleFilter, ScaleGenerateRequest, ScaleStats, PaginatedResponse } from '@/types/operacional';

/**
 * Hook para listar escalas com paginação e filtros
 */
export function useScales(
  initialPage: number = 1,
  initialPageSize: number = 20,
  initialFilters?: ScaleFilter
) {
  const [scales, setScales] = useState<Scale[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalPages, setTotalPages] = useState(0);
  const [filters, setFilters] = useState<ScaleFilter | undefined>(initialFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchScales = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await scalesService.list(page, pageSize, filters);
      setScales(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (err) {
      console.error('Erro ao buscar escalas:', err);
      setError('Erro ao carregar escalas');
      setScales([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, filters]);

  useEffect(() => {
    fetchScales();
  }, [fetchScales]);

  const refresh = useCallback(() => {
    fetchScales();
  }, [fetchScales]);

  const updateFilters = useCallback((newFilters: ScaleFilter | undefined) => {
    setFilters(newFilters);
    setPage(1);
  }, []);

  return {
    scales,
    total,
    page,
    pageSize,
    totalPages,
    filters,
    isLoading,
    error,
    setPage,
    setPageSize,
    setFilters: updateFilters,
    refresh,
  };
}

/**
 * Hook para gerenciar escala individual
 */
export function useScale(id: string | null) {
  const [scale, setScale] = useState<Scale | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchScale = useCallback(async () => {
    if (!id) {
      setScale(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await scalesService.getById(id);
      setScale(data);
    } catch (err) {
      console.error('Erro ao buscar escala:', err);
      setError('Erro ao carregar escala');
      setScale(null);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchScale();
  }, [fetchScale]);

  return {
    scale,
    isLoading,
    error,
    refresh: fetchScale,
  };
}

/**
 * Hook para operações de escala (CRUD)
 */
export function useScaleOperations() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateScale = useCallback(async (data: ScaleGenerateRequest): Promise<Scale | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const scale = await scalesService.generate(data);
      return scale;
    } catch (err: unknown) {
      console.error('Erro ao gerar escala:', err);
      const message = err instanceof Error ? err.message : 'Erro ao gerar escala';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const submitForApproval = useCallback(async (id: string): Promise<Scale | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const scale = await scalesService.submitForApproval(id);
      return scale;
    } catch (err: unknown) {
      console.error('Erro ao enviar para aprovação:', err);
      const message = err instanceof Error ? err.message : 'Erro ao enviar para aprovação';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const approveScale = useCallback(async (id: string, notes?: string): Promise<Scale | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const scale = await scalesService.approve(id, notes);
      return scale;
    } catch (err: unknown) {
      console.error('Erro ao aprovar escala:', err);
      const message = err instanceof Error ? err.message : 'Erro ao aprovar escala';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const publishScale = useCallback(async (
    id: string,
    notifyEmployees: boolean = true
  ): Promise<Scale | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const scale = await scalesService.publish(id, notifyEmployees);
      return scale;
    } catch (err: unknown) {
      console.error('Erro ao publicar escala:', err);
      const message = err instanceof Error ? err.message : 'Erro ao publicar escala';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteScale = useCallback(async (id: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    try {
      await scalesService.delete(id);
      return true;
    } catch (err: unknown) {
      console.error('Erro ao deletar escala:', err);
      const message = err instanceof Error ? err.message : 'Erro ao deletar escala';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    generateScale,
    submitForApproval,
    approveScale,
    publishScale,
    deleteScale,
  };
}

/**
 * Hook para escalas do mês atual
 */
export function useCurrentMonthScales() {
  const [scales, setScales] = useState<Scale[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchScales = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await scalesService.listCurrentMonth();
      setScales(data);
    } catch (err) {
      console.error('Erro ao buscar escalas do mês:', err);
      setError('Erro ao carregar escalas');
      setScales([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchScales();
  }, [fetchScales]);

  return {
    scales,
    isLoading,
    error,
    refresh: fetchScales,
  };
}

/**
 * Hook para estatísticas de escalas
 */
export function useScaleStats() {
  const [stats, setStats] = useState<ScaleStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await scalesService.getStats();
      setStats(data);
    } catch (err) {
      console.error('Erro ao buscar estatísticas de escalas:', err);
      setError('Erro ao carregar estatísticas');
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
