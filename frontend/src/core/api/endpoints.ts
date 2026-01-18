export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  USERS: {
    LIST: '/users',
    DETAIL: (id: string) => `/users/${id}`,
    CREATE: '/users',
    UPDATE: (id: string) => `/users/${id}`,
    DELETE: (id: string) => `/users/${id}`,
  },
  AUDIT: {
    RULES: '/audit/rules',
    EXECUTIONS: '/audit/executions',
    ANOMALIES: '/audit/anomalies',
    REPORTS: '/audit/reports',
  },
  LGPD: {
    REQUESTS: '/lgpd/requests',
    CONSENTS: '/lgpd/consents',
    REPORTS: '/lgpd/reports',
  },
  GED: {
    DOCUMENTS: '/ged/documents',
    UPLOAD: '/ged/upload',
    SEARCH: '/ged/search',
    CATEGORIES: '/ged/categories',
  },
  CRM: {
    CONTACTS: '/crm/contacts',
    DEALS: '/crm/deals',
    PIPELINE: '/crm/pipeline',
    PROPOSALS: '/crm/proposals',
  },
  OPERATIONS: {
    ORDERS: '/operations/orders',
    FIELD_SERVICE: '/operations/field-service',
    EQUIPMENT: '/operations/equipment',
    FACILITIES: '/operations/facilities',
  },
  DASHBOARD: {
    EXECUTIVE: '/dashboard/executive',
    ANALYTICS: '/dashboard/analytics',
    REALTIME: '/dashboard/realtime',
  },
  INTEGRATIONS: {
    HUB: '/integrations',
    SOLIDES: {
      CONFIG: '/integrations/solides/config',
      STATUS: '/integrations/solides/status',
      HEALTH: '/integrations/solides/health',
      LOGS: '/integrations/solides/logs',
      LOG_DETAIL: (id: string) => `/integrations/solides/logs/${id}`,
      CONFLICTS: '/integrations/solides/conflicts',
      SYNC_FULL: '/integrations/solides/sync/full',
      SYNC_INCREMENTAL: '/integrations/solides/sync/incremental',
      SYNC_ENTITY: (type: string, id: string) => `/integrations/solides/sync/entity/${type}/${id}`,
      RESOLVE_CONFLICT: (id: string) => `/integrations/solides/conflicts/${id}/resolve`,
      IGNORE_CONFLICT: (id: string) => `/integrations/solides/conflicts/${id}/ignore`,
      WEBHOOK: '/integrations/solides/webhook',
    },
  },
} as const;

export default API_ENDPOINTS;
