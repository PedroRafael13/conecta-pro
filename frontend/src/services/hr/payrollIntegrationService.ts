/**
 * Service Layer - HR Payroll Integration
 * Integração Folha de Pagamento (Periods, Events, Export, eSocial)
 */

export const payrollIntegrationService = {
  // Períodos de Folha
  periods: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/payroll/periods',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/periods/${id}`,
      method: 'GET' as const,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/payroll/periods',
      method: 'POST' as const,
      data,
    }),

    close: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/periods/${id}/close`,
      method: 'POST' as const,
    }),

    reopen: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/periods/${id}/reopen`,
      method: 'POST' as const,
    }),

    calculate: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/periods/${id}/calculate`,
      method: 'POST' as const,
    }),

    getCurrent: () => ({
      endpoint: '/api/v1/hr/payroll/periods/current',
      method: 'GET' as const,
    }),
  },

  // Eventos de Folha
  events: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/payroll/events',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/events/${id}`,
      method: 'GET' as const,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/payroll/events',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: any) => ({
      endpoint: `/api/v1/hr/payroll/events/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/events/${id}`,
      method: 'DELETE' as const,
    }),

    approve: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/events/${id}/approve`,
      method: 'POST' as const,
    }),

    reject: (id: string, reason: string) => ({
      endpoint: `/api/v1/hr/payroll/events/${id}/reject`,
      method: 'POST' as const,
      data: { reason },
    }),
  },

  // Exportação
  exports: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/payroll/exports',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/exports/${id}`,
      method: 'GET' as const,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/payroll/exports',
      method: 'POST' as const,
      data,
    }),

    download: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/exports/${id}/download`,
      method: 'GET' as const,
      responseType: 'blob' as const,
    }),

    retry: (id: string) => ({
      endpoint: `/api/v1/hr/payroll/exports/${id}/retry`,
      method: 'POST' as const,
    }),
  },

  // eSocial
  esocial: {
    events: (params?: any) => ({
      endpoint: '/api/v1/hr/payroll/esocial/events',
      method: 'GET' as const,
      params,
    }),

    send: (eventType: string, data: any) => ({
      endpoint: '/api/v1/hr/payroll/esocial/send',
      method: 'POST' as const,
      data: { eventType, ...data },
    }),

    status: (protocolId: string) => ({
      endpoint: `/api/v1/hr/payroll/esocial/status/${protocolId}`,
      method: 'GET' as const,
    }),

    validate: (eventType: string, data: any) => ({
      endpoint: '/api/v1/hr/payroll/esocial/validate',
      method: 'POST' as const,
      data: { eventType, ...data },
    }),

    xml: (eventId: string) => ({
      endpoint: `/api/v1/hr/payroll/esocial/xml/${eventId}`,
      method: 'GET' as const,
    }),
  },

  // Cálculos
  calculations: {
    inss: (grossSalary: number) => ({
      endpoint: '/api/v1/hr/payroll/calculations/inss',
      method: 'POST' as const,
      data: { grossSalary },
    }),

    irrf: (taxableIncome: number, dependents: number) => ({
      endpoint: '/api/v1/hr/payroll/calculations/irrf',
      method: 'POST' as const,
      data: { taxableIncome, dependents },
    }),

    fgts: (salary: number) => ({
      endpoint: '/api/v1/hr/payroll/calculations/fgts',
      method: 'POST' as const,
      data: { salary },
    }),

    netSalary: (employeeId: string, periodId: string) => ({
      endpoint: '/api/v1/hr/payroll/calculations/net-salary',
      method: 'POST' as const,
      data: { employeeId, periodId },
    }),
  },
};
