/**
 * Service Layer - HR Analytics Dashboard
 * Dashboards, KPIs e Reports de RH
 */

import type {
  DashboardConfigCreate,
  DashboardWidgetCreate,
  KPIDefinitionCreate,
  ScheduledReportCreate,
  DashboardType,
  DashboardVisibility,
  WidgetType,
  KPICategory,
  ReportType,
  ReportFormat,
} from '@/api/hr/generated/models';

export interface DashboardFilters {
  tipo?: DashboardType;
  visibilidade?: DashboardVisibility;
  skip?: number;
  limit?: number;
}

export interface WidgetFilters {
  dashboardId?: string;
  tipo?: WidgetType;
  skip?: number;
  limit?: number;
}

export interface KPIFilters {
  categoria?: KPICategory;
  ativo?: boolean;
  skip?: number;
  limit?: number;
}

export interface ReportFilters {
  tipo?: ReportType;
  formato?: ReportFormat;
  ativo?: boolean;
  skip?: number;
  limit?: number;
}

export interface KPICalculationParams {
  kpiId: string;
  startDate?: string;
  endDate?: string;
  departmentId?: string;
  employeeId?: string;
}

export interface ReportGenerationParams {
  reportId: string;
  format?: ReportFormat;
  startDate?: string;
  endDate?: string;
  parameters?: Record<string, any>;
}

/**
 * HR Analytics Dashboard Service
 */
export const analyticsDashboardService = {
  // Dashboards
  dashboards: {
    list: (filters?: DashboardFilters) => ({
      endpoint: '/api/v1/hr/analytics/dashboards',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/${id}`,
      method: 'GET' as const,
    }),

    create: (data: DashboardConfigCreate) => ({
      endpoint: '/api/v1/hr/analytics/dashboards',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: Partial<DashboardConfigCreate>) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/${id}`,
      method: 'DELETE' as const,
    }),

    duplicate: (id: string, name?: string) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/${id}/duplicate`,
      method: 'POST' as const,
      data: { name },
    }),

    share: (id: string, userIds: string[]) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/${id}/share`,
      method: 'POST' as const,
      data: { userIds },
    }),
  },

  // Widgets
  widgets: {
    list: (filters?: WidgetFilters) => ({
      endpoint: '/api/v1/hr/analytics/dashboards/widgets',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/widgets/${id}`,
      method: 'GET' as const,
    }),

    create: (data: DashboardWidgetCreate) => ({
      endpoint: '/api/v1/hr/analytics/dashboards/widgets',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: Partial<DashboardWidgetCreate>) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/widgets/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/widgets/${id}`,
      method: 'DELETE' as const,
    }),

    reorder: (dashboardId: string, widgetIds: string[]) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/${dashboardId}/widgets/reorder`,
      method: 'POST' as const,
      data: { widgetIds },
    }),

    refreshData: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/dashboards/widgets/${id}/refresh`,
      method: 'POST' as const,
    }),
  },

  // KPIs
  kpis: {
    list: (filters?: KPIFilters) => ({
      endpoint: '/api/v1/hr/analytics/kpis',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/kpis/${id}`,
      method: 'GET' as const,
    }),

    create: (data: KPIDefinitionCreate) => ({
      endpoint: '/api/v1/hr/analytics/kpis',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: Partial<KPIDefinitionCreate>) => ({
      endpoint: `/api/v1/hr/analytics/kpis/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/kpis/${id}`,
      method: 'DELETE' as const,
    }),

    calculate: (params: KPICalculationParams) => ({
      endpoint: `/api/v1/hr/analytics/kpis/${params.kpiId}/calculate`,
      method: 'POST' as const,
      data: {
        startDate: params.startDate,
        endDate: params.endDate,
        departmentId: params.departmentId,
        employeeId: params.employeeId,
      },
    }),

    trend: (id: string, days: number = 30) => ({
      endpoint: `/api/v1/hr/analytics/kpis/${id}/trend`,
      method: 'GET' as const,
      params: { days },
    }),

    compare: (kpiIds: string[], startDate: string, endDate: string) => ({
      endpoint: '/api/v1/hr/analytics/kpis/compare',
      method: 'POST' as const,
      data: { kpiIds, startDate, endDate },
    }),
  },

  // Reports
  reports: {
    list: (filters?: ReportFilters) => ({
      endpoint: '/api/v1/hr/analytics/reports',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/reports/${id}`,
      method: 'GET' as const,
    }),

    create: (data: ScheduledReportCreate) => ({
      endpoint: '/api/v1/hr/analytics/reports',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: Partial<ScheduledReportCreate>) => ({
      endpoint: `/api/v1/hr/analytics/reports/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/analytics/reports/${id}`,
      method: 'DELETE' as const,
    }),

    generate: (params: ReportGenerationParams) => ({
      endpoint: `/api/v1/hr/analytics/reports/${params.reportId}/generate`,
      method: 'POST' as const,
      data: {
        format: params.format,
        startDate: params.startDate,
        endDate: params.endDate,
        parameters: params.parameters,
      },
    }),

    download: (reportId: string, executionId: string) => ({
      endpoint: `/api/v1/hr/analytics/reports/${reportId}/executions/${executionId}/download`,
      method: 'GET' as const,
      responseType: 'blob' as const,
    }),

    executions: (reportId: string, limit: number = 10) => ({
      endpoint: `/api/v1/hr/analytics/reports/${reportId}/executions`,
      method: 'GET' as const,
      params: { limit },
    }),

    schedule: (id: string, enabled: boolean) => ({
      endpoint: `/api/v1/hr/analytics/reports/${id}/schedule`,
      method: 'PATCH' as const,
      data: { enabled },
    }),
  },

  // Métricas em tempo real
  metrics: {
    summary: () => ({
      endpoint: '/api/v1/hr/analytics/metrics/summary',
      method: 'GET' as const,
    }),

    realtime: (metricType: string) => ({
      endpoint: `/api/v1/hr/analytics/metrics/realtime/${metricType}`,
      method: 'GET' as const,
    }),

    history: (metricType: string, days: number = 30) => ({
      endpoint: `/api/v1/hr/analytics/metrics/history/${metricType}`,
      method: 'GET' as const,
      params: { days },
    }),
  },

  // Cache
  cache: {
    clear: () => ({
      endpoint: '/api/v1/hr/analytics/cache/clear',
      method: 'DELETE' as const,
    }),

    stats: () => ({
      endpoint: '/api/v1/hr/analytics/cache/stats',
      method: 'GET' as const,
    }),
  },
};
