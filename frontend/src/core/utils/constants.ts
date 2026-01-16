export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  FORGOT_PASSWORD: '/forgot-password',

  // Analytics
  DASHBOARD: '/dashboard',
  REPORTS: '/reports',
  ANALYTICS: '/analytics',

  // Compliance
  AUDIT: '/audit',
  LGPD: '/lgpd',
  GOVERNMENT: '/government',
  BIDDING: '/bidding',

  // GED
  GED: '/ged',
  GED_CLASSIFICATION: '/ged/classification',
  GED_SEARCH: '/ged/search',

  // CRM
  CRM: '/crm',
  CRM_PIPELINE: '/crm/pipeline',
  PROPOSALS: '/proposals',
  MARKETPLACE: '/marketplace',

  // Operations
  OPERATIONS: '/operations',
  FIELD_SERVICE: '/field-service',
  SCHEDULING: '/scheduling',
  FACILITIES: '/facilities',
  EQUIPMENT: '/equipment',

  // Finance
  FINANCE_CFO: '/finance/cfo',
  FINANCE_CASHFLOW: '/finance/cashflow',
  FINANCE_FORECASTS: '/finance/forecasts',

  // HR
  HR: '/hr',
  HR_RECRUITMENT: '/hr/recruitment',
  HR_HEALTH: '/hr/health',

  // Settings
  SETTINGS: '/settings',
  PROFILE: '/profile',
} as const;

export const PERMISSIONS = {
  // Audit
  AUDIT_VIEW: 'audit:view',
  AUDIT_CREATE: 'audit:create',
  AUDIT_EDIT: 'audit:edit',
  AUDIT_DELETE: 'audit:delete',

  // LGPD
  LGPD_VIEW: 'lgpd:view',
  LGPD_MANAGE: 'lgpd:manage',

  // GED
  GED_VIEW: 'ged:view',
  GED_UPLOAD: 'ged:upload',
  GED_DELETE: 'ged:delete',

  // CRM
  CRM_VIEW: 'crm:view',
  CRM_EDIT: 'crm:edit',
  CRM_DELETE: 'crm:delete',

  // Operations
  OPERATIONS_VIEW: 'operations:view',
  OPERATIONS_MANAGE: 'operations:manage',

  // Finance
  FINANCE_VIEW: 'finance:view',
  FINANCE_MANAGE: 'finance:manage',

  // HR
  HR_VIEW: 'hr:view',
  HR_MANAGE: 'hr:manage',

  // Admin
  ADMIN: 'admin',
  USERS_MANAGE: 'users:manage',
  SETTINGS_MANAGE: 'settings:manage',
} as const;

export const FILE_LIMITS = {
  MAX_SIZE_MB: 50,
  MAX_SIZE_BYTES: 50 * 1024 * 1024,
  ALLOWED_TYPES: {
    DOCUMENTS: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
    IMAGES: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
    ALL: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'webp'],
  },
} as const;

export const DATE_FORMATS = {
  DISPLAY: 'dd/MM/yyyy',
  DISPLAY_TIME: 'dd/MM/yyyy HH:mm',
  DISPLAY_FULL: 'dd/MM/yyyy HH:mm:ss',
  API: 'yyyy-MM-dd',
  API_TIME: "yyyy-MM-dd'T'HH:mm:ss",
  API_FULL: "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'",
} as const;

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PER_PAGE: 20,
  PER_PAGE_OPTIONS: [10, 20, 50, 100],
} as const;

export const STATUS_COLORS = {
  active: 'success',
  inactive: 'default',
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  cancelled: 'default',
  completed: 'success',
  in_progress: 'info',
  draft: 'default',
} as const;

export const BRAZIL_STATES = [
  { value: 'AC', label: 'Acre' },
  { value: 'AL', label: 'Alagoas' },
  { value: 'AP', label: 'Amapa' },
  { value: 'AM', label: 'Amazonas' },
  { value: 'BA', label: 'Bahia' },
  { value: 'CE', label: 'Ceara' },
  { value: 'DF', label: 'Distrito Federal' },
  { value: 'ES', label: 'Espirito Santo' },
  { value: 'GO', label: 'Goias' },
  { value: 'MA', label: 'Maranhao' },
  { value: 'MT', label: 'Mato Grosso' },
  { value: 'MS', label: 'Mato Grosso do Sul' },
  { value: 'MG', label: 'Minas Gerais' },
  { value: 'PA', label: 'Para' },
  { value: 'PB', label: 'Paraiba' },
  { value: 'PR', label: 'Parana' },
  { value: 'PE', label: 'Pernambuco' },
  { value: 'PI', label: 'Piaui' },
  { value: 'RJ', label: 'Rio de Janeiro' },
  { value: 'RN', label: 'Rio Grande do Norte' },
  { value: 'RS', label: 'Rio Grande do Sul' },
  { value: 'RO', label: 'Rondonia' },
  { value: 'RR', label: 'Roraima' },
  { value: 'SC', label: 'Santa Catarina' },
  { value: 'SP', label: 'Sao Paulo' },
  { value: 'SE', label: 'Sergipe' },
  { value: 'TO', label: 'Tocantins' },
] as const;
