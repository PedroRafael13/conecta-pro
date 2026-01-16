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
} as const;

export default API_ENDPOINTS;
