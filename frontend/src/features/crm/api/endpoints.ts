/**
 * Endpoints da API para o módulo CRM
 * Baseado nos controllers do backend
 */

export const CRM_ENDPOINTS = {
  // ==================== LEADS ====================
  LEADS: {
    LIST: '/crm/leads',
    CREATE: '/crm/leads',
    STATS: '/crm/leads/stats',
    DETAIL: (id: string) => `/crm/leads/${id}`,
    UPDATE: (id: string) => `/crm/leads/${id}`,
    DELETE: (id: string) => `/crm/leads/${id}`,
    UPDATE_STATUS: (id: string) => `/crm/leads/${id}/status`,
    RECALCULATE_SCORE: (id: string) => `/crm/leads/${id}/recalculate-score`,
    RECOMMENDED_ACTION: (id: string) => `/crm/leads/${id}/recommended-action`,
  },

  // ==================== OPPORTUNITIES ====================
  OPPORTUNITIES: {
    LIST: '/crm/opportunities',
    CREATE: '/crm/opportunities',
    CREATE_FROM_LEAD: '/crm/opportunities/from-lead',
    DETAIL: (id: string) => `/crm/opportunities/${id}`,
    UPDATE: (id: string) => `/crm/opportunities/${id}`,
    DELETE: (id: string) => `/crm/opportunities/${id}`,
    UPDATE_STAGE: (id: string) => `/crm/opportunities/${id}/stage`,
    CLOSE: (id: string) => `/crm/opportunities/${id}/close`,
  },

  // ==================== PROPOSALS ====================
  PROPOSALS: {
    LIST: '/crm/proposals',
    CREATE: '/crm/proposals',
    STATS: '/crm/proposals/stats',
    TEMPLATES: '/crm/proposals/templates',
    DETAIL: (id: string) => `/crm/proposals/${id}`,
    UPDATE: (id: string) => `/crm/proposals/${id}`,
    DELETE: (id: string) => `/crm/proposals/${id}`,
    SUBMIT: (id: string) => `/crm/proposals/${id}/submit`,
    APPROVE: (id: string) => `/crm/proposals/${id}/approve`,
    SEND: (id: string) => `/crm/proposals/${id}/send`,
    ACCEPT: (id: string) => `/crm/proposals/${id}/accept`,
    REJECT: (id: string) => `/crm/proposals/${id}/reject`,
    NEW_VERSION: (id: string) => `/crm/proposals/${id}/new-version`,
    ADD_ITEMS: (id: string) => `/crm/proposals/${id}/items`,
  },

  // ==================== CONTRACTS ====================
  CONTRACTS: {
    LIST: '/crm/contracts',
    CREATE: '/crm/contracts',
    STATS: '/crm/contracts/stats',
    ALERTS: '/crm/contracts/alerts',
    DETAIL: (id: string) => `/crm/contracts/${id}`,
    UPDATE: (id: string) => `/crm/contracts/${id}`,
    DELETE: (id: string) => `/crm/contracts/${id}`,
    SUBMIT: (id: string) => `/crm/contracts/${id}/submit`,
    ACTIVATE: (id: string) => `/crm/contracts/${id}/activate`,
    SUSPEND: (id: string) => `/crm/contracts/${id}/suspend`,
    TERMINATE: (id: string) => `/crm/contracts/${id}/terminate`,
    RENEW: (id: string) => `/crm/contracts/${id}/renew`,
    CALCULATE_ADJUSTMENT: (id: string) => `/crm/contracts/${id}/calculate-adjustment`,
    ADD_ITEMS: (id: string) => `/crm/contracts/${id}/items`,
    ADD_ADDENDUM: (id: string) => `/crm/contracts/${id}/addendums`,
  },

  // ==================== COMMISSIONS ====================
  COMMISSIONS: {
    // Regras
    RULES: {
      LIST: '/crm/commissions/rules',
      CREATE: '/crm/commissions/rules',
      DETAIL: (id: string) => `/crm/commissions/rules/${id}`,
      UPDATE: (id: string) => `/crm/commissions/rules/${id}`,
      DELETE: (id: string) => `/crm/commissions/rules/${id}`,
    },
    // Comissões
    LIST: '/crm/commissions',
    CALCULATE: '/crm/commissions/calculate',
    STATS: '/crm/commissions/stats',
    SELLER_STATS: (sellerId: string) => `/crm/commissions/seller/${sellerId}/stats`,
    DETAIL: (id: string) => `/crm/commissions/${id}`,
    UPDATE: (id: string) => `/crm/commissions/${id}`,
    DELETE: (id: string) => `/crm/commissions/${id}`,
    UPDATE_STATUS: (id: string) => `/crm/commissions/${id}/status`,
    APPROVE: (id: string) => `/crm/commissions/${id}/approve`,
  },

  // ==================== DASHBOARD ====================
  DASHBOARD: {
    MAIN: '/crm/dashboard',
    PIPELINE: '/crm/dashboard/pipeline',
    KPIS: '/crm/dashboard/kpis',
    FUNNEL: '/crm/dashboard/funnel',
    TRENDS_LEADS: '/crm/dashboard/trends/leads',
    TRENDS_SALES: '/crm/dashboard/trends/sales',
    TRENDS_COMMISSIONS: '/crm/dashboard/trends/commissions',
    CONVERSION_RATES: '/crm/dashboard/conversion-rates',
    SELLER_PERFORMANCE: (sellerId: string) => `/crm/dashboard/seller/${sellerId}/performance`,
    TOP_PERFORMERS: '/crm/dashboard/top-performers',
    RANKING: '/crm/dashboard/ranking',
  },
} as const;

export default CRM_ENDPOINTS;
