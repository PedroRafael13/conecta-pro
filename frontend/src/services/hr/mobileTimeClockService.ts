/**
 * Service Layer - HR Mobile Time Clock
 * Ponto Mobile (Devices, Check-ins, Geofencing, Offline Sync)
 */

export const mobileTimeClockService = {
  // Devices
  devices: {
    list: (params?: { employeeId?: string; status?: string; skip?: number; limit?: number }) => ({
      endpoint: '/api/v1/hr/mobile/devices',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/mobile/devices/${id}`,
      method: 'GET' as const,
    }),

    register: (data: any) => ({
      endpoint: '/api/v1/hr/mobile/devices',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: any) => ({
      endpoint: `/api/v1/hr/mobile/devices/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    deactivate: (id: string) => ({
      endpoint: `/api/v1/hr/mobile/devices/${id}/deactivate`,
      method: 'POST' as const,
    }),

    activate: (id: string) => ({
      endpoint: `/api/v1/hr/mobile/devices/${id}/activate`,
      method: 'POST' as const,
    }),
  },

  // Check-ins
  checkins: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/mobile/checkins',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/mobile/checkins/${id}`,
      method: 'GET' as const,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/mobile/checkins',
      method: 'POST' as const,
      data,
    }),

    validate: (id: string) => ({
      endpoint: `/api/v1/hr/mobile/checkins/${id}/validate`,
      method: 'POST' as const,
    }),

    reject: (id: string, reason: string) => ({
      endpoint: `/api/v1/hr/mobile/checkins/${id}/reject`,
      method: 'POST' as const,
      data: { reason },
    }),

    getByEmployee: (employeeId: string, startDate: string, endDate: string) => ({
      endpoint: `/api/v1/hr/mobile/checkins/employee/${employeeId}`,
      method: 'GET' as const,
      params: { startDate, endDate },
    }),
  },

  // Geofencing
  geofences: {
    list: (params?: any) => ({
      endpoint: '/api/v1/hr/mobile/geofences',
      method: 'GET' as const,
      params,
    }),

    getById: (id: string) => ({
      endpoint: `/api/v1/hr/mobile/geofences/${id}`,
      method: 'GET' as const,
    }),

    create: (data: any) => ({
      endpoint: '/api/v1/hr/mobile/geofences',
      method: 'POST' as const,
      data,
    }),

    update: (id: string, data: any) => ({
      endpoint: `/api/v1/hr/mobile/geofences/${id}`,
      method: 'PATCH' as const,
      data,
    }),

    delete: (id: string) => ({
      endpoint: `/api/v1/hr/mobile/geofences/${id}`,
      method: 'DELETE' as const,
    }),

    checkLocation: (lat: number, lng: number) => ({
      endpoint: '/api/v1/hr/mobile/geofences/check-location',
      method: 'POST' as const,
      data: { latitude: lat, longitude: lng },
    }),
  },

  // Offline Sync
  offline: {
    queue: (params?: any) => ({
      endpoint: '/api/v1/hr/mobile/offline/queue',
      method: 'GET' as const,
      params,
    }),

    sync: (data: any[]) => ({
      endpoint: '/api/v1/hr/mobile/offline/sync',
      method: 'POST' as const,
      data,
    }),

    clear: (deviceId: string) => ({
      endpoint: `/api/v1/hr/mobile/offline/clear/${deviceId}`,
      method: 'DELETE' as const,
    }),

    status: (deviceId: string) => ({
      endpoint: `/api/v1/hr/mobile/offline/status/${deviceId}`,
      method: 'GET' as const,
    }),
  },
};
