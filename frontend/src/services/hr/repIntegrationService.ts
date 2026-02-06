/**
 * Service Layer - HR REP Integration
 * Integração REP - Registrador Eletrônico de Ponto
 */

export const repIntegrationService = {
  // Dispositivos REP
  devices: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/rep/devices',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/rep/devices/${id}`,
      method: 'GET' as const,
    }),

    register: (data: any) => ({
      endpoint: '/api/v1/hr/rep/devices',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: any) => ({
      endpoint: `/api/v1/hr/rep/devices/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    deactivate: (id: string) => ({
      endpoint: `/api/v1/hr/rep/devices/${id}/deactivate`,
      method: 'POST' as const,
    }),

    testConnection: (id: string) => ({
      endpoint: `/api/v1/hr/rep/devices/${id}/test`,
      method: 'POST' as const,
    }),
  },

  // Sincronização
  sync: {
    manual: (deviceId: string) => ({
      endpoint: `/api/v1/hr/rep/sync/${deviceId}`,
      method: 'POST' as const,
    }),

    status: (deviceId: string) => ({
      endpoint: `/api/v1/hr/rep/sync/${deviceId}/status`,
      method: 'GET' as const,
    }),

    history: (deviceId: string, params?: any) => ({
      endpoint: `/api/v1/hr/rep/sync/${deviceId}/history`,
      method: 'GET' as const,
      params,
    }),

    schedule: (deviceId: string, schedule: any) => ({
      endpoint: `/api/v1/hr/rep/sync/${deviceId}/schedule`,
      method: 'POST' as const,
      data: schedule,
    }),
  },

  // Eventos REP
  events: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/rep/events',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/rep/events/${id}`,
      method: 'GET' as const,
    }),

    import: (deviceId: string, startDate?: string, endDate?: string) => ({
      endpoint: `/api/v1/hr/rep/events/import`,
      method: 'POST' as const,
      data: { deviceId, startDate, endDate },
    }),

    process: (eventIds: string[]) => ({
      endpoint: '/api/v1/hr/rep/events/process',
      method: 'POST' as const,
      data: { eventIds },
    }),
  },

  // AFD - Arquivo Fonte de Dados
  afd: {
    generate: (deviceId: string, startDate: string, endDate: string) => ({
      endpoint: '/api/v1/hr/rep/afd/generate',
      method: 'POST' as const,
      data: { deviceId, startDate, endDate },
    }),

    download: (afdId: string) => ({
      endpoint: `/api/v1/hr/rep/afd/${afdId}/download`,
      method: 'GET' as const,
      responseType: 'blob' as const,
    }),

    validate: (file: File) => ({
      endpoint: '/api/v1/hr/rep/afd/validate',
      method: 'POST' as const,
      data: { file },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

    list: (params?: any) => ({
      endpoint: '/api/v1/hr/rep/afd',
      method: 'GET' as const,
      params,
    }),
  },

  // Webhooks
  webhooks: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/rep/webhooks',
      method: 'GET' as const,
      params,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/rep/webhooks',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: any) => ({
      endpoint: `/api/v1/hr/rep/webhooks/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/rep/webhooks/${id}`,
      method: 'DELETE' as const,
    }),

    test: (id: string) => ({
      endpoint: `/api/v1/hr/rep/webhooks/${id}/test`,
      method: 'POST' as const,
    }),

    logs: (id: string, params?: any) => ({
      endpoint: `/api/v1/hr/rep/webhooks/${id}/logs`,
      method: 'GET' as const,
      params,
    }),
  },
};
