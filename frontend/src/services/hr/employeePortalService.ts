/**
 * Service Layer - HR Employee Portal
 * Portal do Funcionário (Holerites, Férias, Documentos, Notificações, Preferências)
 */

import type {
  PaySlipResponse,
  PaySlipListResponse,
  VacationRequestResponse,
  VacationRequestCreate,
  VacationStatus,
  DocumentResponse,
  DocumentCreate,
  DocumentType,
  NotificationResponse,
  NotificationType,
  NotificationPriority,
  PreferencesResponse,
  PreferencesUpdate,
} from '@/api/hr/generated/models';

export interface PayslipFilters {
  employeeId?: string;
  startDate?: string;
  endDate?: string;
  year?: number;
  month?: number;
  skip?: number;
  limit?: number;
}

export interface VacationFilters {
  employeeId?: string;
  status?: VacationStatus;
  startDate?: string;
  endDate?: string;
  skip?: number;
  limit?: number;
}

export interface DocumentFilters {
  employeeId?: string;
  type?: DocumentType;
  tags?: string[];
  search?: string;
  skip?: number;
  limit?: number;
}

export interface NotificationFilters {
  employeeId?: string;
  type?: NotificationType;
  priority?: NotificationPriority;
  read?: boolean;
  skip?: number;
  limit?: number;
}

/**
 * Employee Portal Service
 */
export const employeePortalService = {
  // Holerites (Payslips)
  payslips: {
    list: (filters?: PayslipFilters) => ({
      endpoint: '/api/v1/hr/portal/payslips',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/portal/payslips/${id}`,
      method: 'GET' as const,
    }),

    download: (id: string, format: 'pdf' | 'xml' = 'pdf') => ({
      endpoint: `/api/v1/hr/portal/payslips/${id}/download`,
      method: 'GET' as const,
      params: { format },
      responseType: 'blob' as const,
    }),

    getCurrentMonth: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/payslips/current`,
      method: 'GET' as const,
      params: { employeeId },
    }),

    getByPeriod: (employeeId: string, year: number, month: number) => ({
      endpoint: `/api/v1/hr/portal/payslips/period`,
      method: 'GET' as const,
      params: { employeeId, year, month },
    }),

    getYearSummary: (employeeId: string, year: number) => ({
      endpoint: `/api/v1/hr/portal/payslips/summary`,
      method: 'GET' as const,
      params: { employeeId, year },
    }),

    markAsViewed: (id: string) => ({
      endpoint: `/api/v1/hr/portal/payslips/${id}/view`,
      method: 'POST' as const,
    }),
  },

  // Férias (Vacation Requests)
  vacations: {
    list: (filters?: VacationFilters) => ({
      endpoint: '/api/v1/hr/portal/vacations',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/portal/vacations/${id}`,
      method: 'GET' as const,
    }),

    create: (data: VacationRequestCreate) => ({
      endpoint: '/api/v1/hr/portal/vacations',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: Partial<VacationRequestCreate>) => ({
      endpoint: `/api/v1/hr/portal/vacations/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    cancel: (id: string, reason: string) => ({
      endpoint: `/api/v1/hr/portal/vacations/${id}/cancel`,
      method: 'POST' as const,
      data: { reason },
    }),

    approve: (id: string, comment?: string) => ({
      endpoint: `/api/v1/hr/portal/vacations/${id}/approve`,
      method: 'POST' as const,
      data: { comment },
    }),

    reject: (id: string, reason: string) => ({
      endpoint: `/api/v1/hr/portal/vacations/${id}/reject`,
      method: 'POST' as const,
      data: { reason },
    }),

    getBalance: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/vacations/balance`,
      method: 'GET' as const,
      params: { employeeId },
    }),

    getAvailablePeriods: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/vacations/available-periods`,
      method: 'GET' as const,
      params: { employeeId },
    }),

    checkConflicts: (employeeId: string, startDate: string, endDate: string) => ({
      endpoint: `/api/v1/hr/portal/vacations/check-conflicts`,
      method: 'POST' as const,
      data: { employeeId, startDate, endDate },
    }),
  },

  // Documentos
  documents: {
    list: (filters?: DocumentFilters) => ({
      endpoint: '/api/v1/hr/portal/documents',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/portal/documents/${id}`,
      method: 'GET' as const,
    }),

    upload: (data: DocumentCreate, file: File) => ({
      endpoint: '/api/v1/hr/portal/documents',
      method: 'POST' as const,
      data: {
        ...data,
        file,
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

    update: (id: string, data: Partial<DocumentCreate>) => ({
      endpoint: `/api/v1/hr/portal/documents/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/portal/documents/${id}`,
      method: 'DELETE' as const,
    }),

    download: (id: string) => ({
      endpoint: `/api/v1/hr/portal/documents/${id}/download`,
      method: 'GET' as const,
      responseType: 'blob' as const,
    }),

    preview: (id: string) => ({
      endpoint: `/api/v1/hr/portal/documents/${id}/preview`,
      method: 'GET' as const,
    }),

    share: (id: string, userIds: string[], expiresAt?: string) => ({
      endpoint: `/api/v1/hr/portal/documents/${id}/share`,
      method: 'POST' as const,
      data: { userIds, expiresAt },
    }),

    getByType: (employeeId: string, type: DocumentType) => ({
      endpoint: `/api/v1/hr/portal/documents/by-type`,
      method: 'GET' as const,
      params: { employeeId, type },
    }),
  },

  // Notificações
  notifications: {
    list: (filters?: NotificationFilters) => ({
      endpoint: '/api/v1/hr/portal/notifications',
      method: 'GET' as const,
      params: filters,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/portal/notifications/${id}`,
      method: 'GET' as const,
    }),

    markAsRead: (id: string) => ({
      endpoint: `/api/v1/hr/portal/notifications/${id}/read`,
      method: 'POST' as const,
    }),

    markAllAsRead: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/notifications/mark-all-read`,
      method: 'POST' as const,
      data: { employeeId },
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/portal/notifications/${id}`,
      method: 'DELETE' as const,
    }),

    getUnreadCount: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/notifications/unread-count`,
      method: 'GET' as const,
      params: { employeeId },
    }),

    getRecent: (employeeId: string, limit: number = 10) => ({
      endpoint: `/api/v1/hr/portal/notifications/recent`,
      method: 'GET' as const,
      params: { employeeId, limit },
    }),

    subscribe: (employeeId: string, types: NotificationType[]) => ({
      endpoint: `/api/v1/hr/portal/notifications/subscribe`,
      method: 'POST' as const,
      data: { employeeId, types },
    }),

    unsubscribe: (employeeId: string, types: NotificationType[]) => ({
      endpoint: `/api/v1/hr/portal/notifications/unsubscribe`,
      method: 'POST' as const,
      data: { employeeId, types },
    }),
  },

  // Preferências
  preferences: {
    get: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/preferences`,
      method: 'GET' as const,
      params: { employeeId },
    }),

    update: (employeeId: string, data: PreferencesUpdate) => ({
      endpoint: `/api/v1/hr/portal/preferences`,
      method: 'PUT' as const,
      params: { employeeId },
      data,
    }),

    updatePartial: (employeeId: string, data: Partial<PreferencesUpdate>) => ({
      endpoint: `/api/v1/hr/portal/preferences`,
      method: 'PATCH' as const,
      params: { employeeId },
      data,
    }),

    reset: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/preferences/reset`,
      method: 'POST' as const,
      data: { employeeId },
    }),

    updateLanguage: (employeeId: string, language: string) => ({
      endpoint: `/api/v1/hr/portal/preferences/language`,
      method: 'PATCH' as const,
      data: { employeeId, language },
    }),

    updateTheme: (employeeId: string, theme: 'light' | 'dark' | 'auto') => ({
      endpoint: `/api/v1/hr/portal/preferences/theme`,
      method: 'PATCH' as const,
      data: { employeeId, theme },
    }),

    updateNotificationSettings: (
      employeeId: string,
      settings: {
        email?: boolean;
        sms?: boolean;
        push?: boolean;
      }
    ) => ({
      endpoint: `/api/v1/hr/portal/preferences/notifications`,
      method: 'PATCH' as const,
      data: { employeeId, ...settings },
    }),
  },

  // Dashboard do funcionário
  dashboard: {
    getSummary: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/dashboard/summary`,
      method: 'GET' as const,
      params: { employeeId },
    }),

    getRecentActivity: (employeeId: string, limit: number = 20) => ({
      endpoint: `/api/v1/hr/portal/dashboard/activity`,
      method: 'GET' as const,
      params: { employeeId, limit },
    }),

    getQuickActions: (employeeId: string) => ({
      endpoint: `/api/v1/hr/portal/dashboard/quick-actions`,
      method: 'GET' as const,
      params: { employeeId },
    }),
  },
};
