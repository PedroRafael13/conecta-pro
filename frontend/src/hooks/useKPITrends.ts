'use client';

import { useMemo } from 'react';
import { useKPITrends as useKPITrendsOrval } from '@/hooks/operacional/useKPITrends';
import type {
  GetKpiTrendsApiV1OperacionalKpiTrendsGetPeriod,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';

type KPITrendsPeriod = GetKpiTrendsApiV1OperacionalKpiTrendsGetPeriod;

interface UseKPITrendsOptions {
  period?: KPITrendsPeriod;
  autoLoad?: boolean;
}

export function useKPITrends(options: UseKPITrendsOptions = {}) {
  const { period = '7d', autoLoad = true } = options;

  const query = useKPITrendsOrval(
    { period },
    { query: { enabled: autoLoad } }
  );

  const data = useMemo(() => query.data?.data ?? null, [query.data]);

  return {
    data,
    isLoading: query.isLoading,
    error: query.error?.message ?? (query.isError ? 'Erro ao carregar tendencias' : null),
    refresh: query.refetch,
  };
}
