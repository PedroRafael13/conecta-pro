'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  getKPITrends,
  type KPITrendsData,
  type KPITrendsPeriod,
} from '@/lib/services/kpi-trends';

interface UseKPITrendsOptions {
  period?: KPITrendsPeriod;
  autoLoad?: boolean;
}

export function useKPITrends(options: UseKPITrendsOptions = {}) {
  const { period = '7d', autoLoad = true } = options;

  const [data, setData] = useState<KPITrendsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrends = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getKPITrends(period);
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar tendências');
      console.error('Erro ao buscar tendências de KPI:', err);
    } finally {
      setIsLoading(false);
    }
  }, [period]);

  useEffect(() => {
    if (autoLoad) {
      fetchTrends();
    }
  }, [autoLoad, fetchTrends]);

  return {
    data,
    isLoading,
    error,
    refresh: fetchTrends,
  };
}
