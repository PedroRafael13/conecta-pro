/**
 * Service Layer - HR Time Tracking
 * Ponto Eletrônico (Marcações, Folha Ponto, Horas Extras, Justificativas)
 */

export const timeTrackingService = {
  // Marcações de Ponto (Time Entries)
  entries: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/time-tracking/entries',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/entries/${id}`,
      method: 'GET' as const,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/time-tracking/entries',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: any) => ({
      endpoint: `/api/v1/hr/time-tracking/entries/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/entries/${id}`,
      method: 'DELETE' as const,
    }),

    getByEmployee: (employeeId: string, date: string) => ({
      endpoint: `/api/v1/hr/time-tracking/entries/employee/${employeeId}`,
      method: 'GET' as const,
      params: { date },
    }),

    validate: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/entries/${id}/validate`,
      method: 'POST' as const,
    }),

    bulkImport: (file: File) => ({
      endpoint: '/api/v1/hr/time-tracking/entries/import',
      method: 'POST' as const,
      data: { file },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  },

  // Folha de Ponto (Time Sheets)
  timesheets: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/time-tracking/timesheets',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/timesheets/${id}`,
      method: 'GET' as const,
    }),

    generate: (employeeId: string, startDate: string, endDate: string) => ({
      endpoint: '/api/v1/hr/time-tracking/timesheets/generate',
      method: 'POST' as const,
      data: { employeeId, startDate, endDate },
    }),

    approve: (id: string, comment?: string) => ({
      endpoint: `/api/v1/hr/time-tracking/timesheets/${id}/approve`,
      method: 'POST' as const,
      data: { comment },
    }),

    reject: (id: string, reason: string) => ({
      endpoint: `/api/v1/hr/time-tracking/timesheets/${id}/reject`,
      method: 'POST' as const,
      data: { reason },
    }),

    export: (id: string, format: 'pdf' | 'xlsx' | 'csv') => ({
      endpoint: `/api/v1/hr/time-tracking/timesheets/${id}/export`,
      method: 'GET' as const,
      params: { format },
      responseType: 'blob' as const,
    }),

    summary: (employeeId: string, month: number, year: number) => ({
      endpoint: `/api/v1/hr/time-tracking/timesheets/summary`,
      method: 'GET' as const,
      params: { employeeId, month, year },
    }),
  },

  // Horas Extras (Overtime)
  overtime: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/time-tracking/overtime',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/overtime/${id}`,
      method: 'GET' as const,
    }),

    request: (data: any) => ({
      endpoint: '/api/v1/hr/time-tracking/overtime',
      method: 'POST' as const,
      data,
    }),

    approve: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/overtime/${id}/approve`,
      method: 'POST' as const,
    }),

    reject: (id: string, reason: string) => ({
      endpoint: `/api/v1/hr/time-tracking/overtime/${id}/reject`,
      method: 'POST' as const,
      data: { reason },
    }),

    calculate: (employeeId: string, startDate: string, endDate: string) => ({
      endpoint: '/api/v1/hr/time-tracking/overtime/calculate',
      method: 'POST' as const,
      data: { employeeId, startDate, endDate },
    }),

    getBalance: (employeeId: string) => ({
      endpoint: `/api/v1/hr/time-tracking/overtime/balance`,
      method: 'GET' as const,
      params: { employeeId },
    }),
  },

  // Justificativas
  justifications: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/time-tracking/justifications',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/justifications/${id}`,
      method: 'GET' as const,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/time-tracking/justifications',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: any) => ({
      endpoint: `/api/v1/hr/time-tracking/justifications/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/justifications/${id}`,
      method: 'DELETE' as const,
    }),

    approve: (id: string) => ({
      endpoint: `/api/v1/hr/time-tracking/justifications/${id}/approve`,
      method: 'POST' as const,
    }),

    reject: (id: string, reason: string) => ({
      endpoint: `/api/v1/hr/time-tracking/justifications/${id}/reject`,
      method: 'POST' as const,
      data: { reason },
    }),

    uploadAttachment: (id: string, file: File) => ({
      endpoint: `/api/v1/hr/time-tracking/justifications/${id}/attachment`,
      method: 'POST' as const,
      data: { file },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  },

  // Dashboard e Relatórios
  dashboard: {
    getSummary: (employeeId: string) => ({
      endpoint: '/api/v1/hr/time-tracking/dashboard/summary',
      method: 'GET' as const,
      params: { employeeId },
    }),

    getAbsenteeism: (startDate: string, endDate: string, departmentId?: string) => ({
      endpoint: '/api/v1/hr/time-tracking/dashboard/absenteeism',
      method: 'GET' as const,
      params: { startDate, endDate, departmentId },
    }),

    getLateness: (startDate: string, endDate: string, departmentId?: string) => ({
      endpoint: '/api/v1/hr/time-tracking/dashboard/lateness',
      method: 'GET' as const,
      params: { startDate, endDate, departmentId },
    }),

    getOvertimeReport: (month: number, year: number, departmentId?: string) => ({
      endpoint: '/api/v1/hr/time-tracking/dashboard/overtime-report',
      method: 'GET' as const,
      params: { month, year, departmentId },
    }),
  },
};
