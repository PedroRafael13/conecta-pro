'use client';

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useServiceOrders } from '../orders/hooks';
import { useTechnicians, useRoutes } from '../technicians/hooks';
import type { FieldServiceKPIs } from '../types';

// Simular delay de API
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock KPIs function
const fetchKPIs = async (): Promise<FieldServiceKPIs> => {
  await delay(400);
  return {
    ordens_abertas: 8,
    ordens_em_atendimento: 4,
    ordens_concluidas_hoje: 12,
    sla_compliance: 94.5,
    tempo_medio_atendimento_min: 45,
    tecnicos_disponiveis: 3,
    tecnicos_total: 6,
  };
};

export interface UseFieldServiceReturn {
  // KPIs
  kpis: FieldServiceKPIs | undefined;
  kpisLoading: boolean;

  // Orders
  orders: ReturnType<typeof useServiceOrders>;

  // Technicians
  technicians: ReturnType<typeof useTechnicians>;

  // Routes
  routes: ReturnType<typeof useRoutes>;

  // Computed
  isLoading: boolean;
  hasErrors: boolean;

  // Actions
  refetchAll: () => void;
}

/**
 * Hook principal do módulo Field Service
 * Centraliza acesso a ordens, técnicos e rotas
 */
export function useFieldService(): UseFieldServiceReturn {
  // KPIs
  const kpisQuery = useQuery({
    queryKey: ['field-service-kpis'],
    queryFn: fetchKPIs,
    staleTime: 60000,
    refetchInterval: 120000,
  });

  // Sub-hooks
  const orders = useServiceOrders();
  const technicians = useTechnicians();
  const routes = useRoutes();

  // Computed states
  const isLoading = useMemo(() => (
    kpisQuery.isLoading ||
    orders.isLoading ||
    technicians.isLoading ||
    routes.isLoading
  ), [kpisQuery.isLoading, orders.isLoading, technicians.isLoading, routes.isLoading]);

  const hasErrors = useMemo(() => (
    !!kpisQuery.error ||
    !!orders.error ||
    !!technicians.error ||
    !!routes.error
  ), [kpisQuery.error, orders.error, technicians.error, routes.error]);

  // Refetch all data
  const refetchAll = () => {
    kpisQuery.refetch();
    orders.refetch();
    technicians.refetch();
    routes.refetch();
  };

  return {
    // KPIs
    kpis: kpisQuery.data,
    kpisLoading: kpisQuery.isLoading,

    // Sub-hooks
    orders,
    technicians,
    routes,

    // Computed
    isLoading,
    hasErrors,

    // Actions
    refetchAll,
  };
}

export default useFieldService;
