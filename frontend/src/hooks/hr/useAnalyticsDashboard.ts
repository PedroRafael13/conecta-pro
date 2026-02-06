/**
 * React Query Hooks - HR Analytics Dashboard
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analyticsDashboardService } from '@/services/hr';
import { customInstance } from '@/lib/api-client';

// Query Keys
export const analyticsKeys = {
  all: ['hr', 'analytics'] as const,
  dashboards: () => [...analyticsKeys.all, 'dashboards'] as const,
  dashboard: (id: string) => [...analyticsKeys.dashboards(), id] as const,
  widgets: () => [...analyticsKeys.all, 'widgets'] as const,
  widget: (id: string) => [...analyticsKeys.widgets(), id] as const,
  kpis: () => [...analyticsKeys.all, 'kpis'] as const,
  kpi: (id: string) => [...analyticsKeys.kpis(), id] as const,
  reports: () => [...analyticsKeys.all, 'reports'] as const,
  report: (id: string) => [...analyticsKeys.reports(), id] as const,
};

// Dashboards Hooks
export const useDashboards = (filters?: any) => {
  return useQuery({
    queryKey: [...analyticsKeys.dashboards(), filters],
    queryFn: () => customInstance(analyticsDashboardService.dashboards.list(filters)),
  });
};

export const useDashboard = (id: string) => {
  return useQuery({
    queryKey: analyticsKeys.dashboard(id),
    queryFn: () => customInstance(analyticsDashboardService.dashboards.getById(id)),
    enabled: !!id,
  });
};

export const useCreateDashboard = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => customInstance(analyticsDashboardService.dashboards.create(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.dashboards() });
    },
  });
};

export const useUpdateDashboard = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      customInstance(analyticsDashboardService.dashboards.update(id, data)),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.dashboard(id) });
      queryClient.invalidateQueries({ queryKey: analyticsKeys.dashboards() });
    },
  });
};

export const useDeleteDashboard = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => customInstance(analyticsDashboardService.dashboards.delete(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.dashboards() });
    },
  });
};

// KPIs Hooks
export const useKPIs = (filters?: any) => {
  return useQuery({
    queryKey: [...analyticsKeys.kpis(), filters],
    queryFn: () => customInstance(analyticsDashboardService.kpis.list(filters)),
  });
};

export const useKPI = (id: string) => {
  return useQuery({
    queryKey: analyticsKeys.kpi(id),
    queryFn: () => customInstance(analyticsDashboardService.kpis.getById(id)),
    enabled: !!id,
  });
};

export const useCalculateKPI = () => {
  return useMutation({
    mutationFn: (params: any) => customInstance(analyticsDashboardService.kpis.calculate(params)),
  });
};

// Reports Hooks
export const useReports = (filters?: any) => {
  return useQuery({
    queryKey: [...analyticsKeys.reports(), filters],
    queryFn: () => customInstance(analyticsDashboardService.reports.list(filters)),
  });
};

export const useGenerateReport = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: any) => customInstance(analyticsDashboardService.reports.generate(params)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.reports() });
    },
  });
};
