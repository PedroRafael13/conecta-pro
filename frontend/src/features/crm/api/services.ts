/**
 * Services para chamadas à API do módulo CRM
 */

import { api } from '@/core/api/client';
import { CRM_ENDPOINTS } from './endpoints';
import type {
  // Lead
  Lead,
  LeadCreate,
  LeadUpdate,
  LeadStatusUpdate,
  LeadFilter,
  LeadStats,
  LeadListResponse,
  // Opportunity
  Opportunity,
  OpportunityCreate,
  OpportunityCreateFromLead,
  OpportunityUpdate,
  OpportunityStageUpdate,
  OpportunityClose,
  OpportunityFilter,
  OpportunityListResponse,
  PipelineStats,
  // Proposal
  Proposal,
  ProposalDetail,
  ProposalCreate,
  ProposalUpdate,
  ProposalFilter,
  ProposalStats,
  ProposalListResponse,
  ProposalItemCreate,
  // Contract
  Contract,
  ContractDetail,
  ContractCreate,
  ContractUpdate,
  ContractFilter,
  ContractStats,
  ContractListResponse,
  // Commission
  Commission,
  CommissionCreate,
  CommissionFilter,
  CommissionStats,
  CommissionListResponse,
  CommissionRule,
  CommissionRuleCreate,
  CommissionRuleListResponse,
  SellerCommissionStats,
  // Dashboard
  CRMDashboardKPIs,
  FunnelData,
  TrendData,
} from '../types';

// ==================== LEAD SERVICES ====================

export const leadService = {
  list: async (params?: LeadFilter & { page?: number; page_size?: number }) => {
    return api.get<LeadListResponse>(CRM_ENDPOINTS.LEADS.LIST, { params });
  },

  create: async (data: LeadCreate) => {
    return api.post<Lead>(CRM_ENDPOINTS.LEADS.CREATE, data);
  },

  getById: async (id: string) => {
    return api.get<Lead>(CRM_ENDPOINTS.LEADS.DETAIL(id));
  },

  update: async (id: string, data: LeadUpdate) => {
    return api.put<Lead>(CRM_ENDPOINTS.LEADS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete<void>(CRM_ENDPOINTS.LEADS.DELETE(id));
  },

  updateStatus: async (id: string, data: LeadStatusUpdate) => {
    return api.patch<Lead>(CRM_ENDPOINTS.LEADS.UPDATE_STATUS(id), data);
  },

  recalculateScore: async (id: string) => {
    return api.post<Lead>(CRM_ENDPOINTS.LEADS.RECALCULATE_SCORE(id));
  },

  getRecommendedAction: async (id: string) => {
    return api.get<{
      lead_id: string;
      score: number;
      status: string;
      recommended_action: string;
      next_contact_date: string | null;
    }>(CRM_ENDPOINTS.LEADS.RECOMMENDED_ACTION(id));
  },

  getStats: async (assigned_to_id?: string) => {
    return api.get<LeadStats>(CRM_ENDPOINTS.LEADS.STATS, {
      params: assigned_to_id ? { assigned_to_id } : undefined,
    });
  },
};

// ==================== OPPORTUNITY SERVICES ====================

export const opportunityService = {
  list: async (params?: OpportunityFilter & { page?: number; page_size?: number }) => {
    return api.get<OpportunityListResponse>(CRM_ENDPOINTS.OPPORTUNITIES.LIST, { params });
  },

  create: async (data: OpportunityCreate) => {
    return api.post<Opportunity>(CRM_ENDPOINTS.OPPORTUNITIES.CREATE, data);
  },

  createFromLead: async (data: OpportunityCreateFromLead) => {
    return api.post<Opportunity>(CRM_ENDPOINTS.OPPORTUNITIES.CREATE_FROM_LEAD, data);
  },

  getById: async (id: string) => {
    return api.get<Opportunity>(CRM_ENDPOINTS.OPPORTUNITIES.DETAIL(id));
  },

  update: async (id: string, data: OpportunityUpdate) => {
    return api.put<Opportunity>(CRM_ENDPOINTS.OPPORTUNITIES.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete<void>(CRM_ENDPOINTS.OPPORTUNITIES.DELETE(id));
  },

  updateStage: async (id: string, data: OpportunityStageUpdate) => {
    return api.patch<Opportunity>(CRM_ENDPOINTS.OPPORTUNITIES.UPDATE_STAGE(id), data);
  },

  close: async (id: string, data: OpportunityClose) => {
    return api.post<Opportunity>(CRM_ENDPOINTS.OPPORTUNITIES.CLOSE(id), data);
  },
};

// ==================== PROPOSAL SERVICES ====================

export const proposalService = {
  list: async (params?: ProposalFilter & { page?: number; page_size?: number }) => {
    return api.get<ProposalListResponse>(CRM_ENDPOINTS.PROPOSALS.LIST, { params });
  },

  create: async (data: ProposalCreate) => {
    return api.post<Proposal>(CRM_ENDPOINTS.PROPOSALS.CREATE, data);
  },

  getById: async (id: string) => {
    return api.get<ProposalDetail>(CRM_ENDPOINTS.PROPOSALS.DETAIL(id));
  },

  update: async (id: string, data: ProposalUpdate) => {
    return api.put<Proposal>(CRM_ENDPOINTS.PROPOSALS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete<void>(CRM_ENDPOINTS.PROPOSALS.DELETE(id));
  },

  submit: async (id: string) => {
    return api.post<Proposal>(CRM_ENDPOINTS.PROPOSALS.SUBMIT(id));
  },

  approve: async (id: string, comments?: string) => {
    return api.post<Proposal>(CRM_ENDPOINTS.PROPOSALS.APPROVE(id), { comments });
  },

  send: async (
    id: string,
    data?: { recipient_email?: string; subject?: string; message?: string; cc_emails?: string[] }
  ) => {
    return api.post<Proposal>(CRM_ENDPOINTS.PROPOSALS.SEND(id), data);
  },

  accept: async (id: string, data?: { feedback?: string; signature?: string }) => {
    return api.post<Proposal>(CRM_ENDPOINTS.PROPOSALS.ACCEPT(id), { accepted: true, ...data });
  },

  reject: async (id: string, feedback?: string) => {
    return api.post<Proposal>(CRM_ENDPOINTS.PROPOSALS.REJECT(id), { accepted: false, feedback });
  },

  createNewVersion: async (id: string) => {
    return api.post<Proposal>(CRM_ENDPOINTS.PROPOSALS.NEW_VERSION(id));
  },

  addItems: async (id: string, items: ProposalItemCreate[]) => {
    return api.post<ProposalDetail>(CRM_ENDPOINTS.PROPOSALS.ADD_ITEMS(id), { items });
  },

  getStats: async () => {
    return api.get<ProposalStats>(CRM_ENDPOINTS.PROPOSALS.STATS);
  },

  getTemplates: async () => {
    return api.get<{ id: string; name: string; description: string }[]>(
      CRM_ENDPOINTS.PROPOSALS.TEMPLATES
    );
  },
};

// ==================== CONTRACT SERVICES ====================

export const contractService = {
  list: async (params?: ContractFilter & { page?: number; page_size?: number }) => {
    return api.get<ContractListResponse>(CRM_ENDPOINTS.CONTRACTS.LIST, { params });
  },

  create: async (data: ContractCreate) => {
    return api.post<Contract>(CRM_ENDPOINTS.CONTRACTS.CREATE, data);
  },

  getById: async (id: string) => {
    return api.get<ContractDetail>(CRM_ENDPOINTS.CONTRACTS.DETAIL(id));
  },

  update: async (id: string, data: ContractUpdate) => {
    return api.put<Contract>(CRM_ENDPOINTS.CONTRACTS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete<void>(CRM_ENDPOINTS.CONTRACTS.DELETE(id));
  },

  submit: async (id: string) => {
    return api.post<Contract>(CRM_ENDPOINTS.CONTRACTS.SUBMIT(id));
  },

  activate: async (id: string) => {
    return api.post<Contract>(CRM_ENDPOINTS.CONTRACTS.ACTIVATE(id));
  },

  suspend: async (id: string, reason?: string) => {
    return api.post<Contract>(CRM_ENDPOINTS.CONTRACTS.SUSPEND(id), { reason });
  },

  terminate: async (id: string, reason?: string) => {
    return api.post<Contract>(CRM_ENDPOINTS.CONTRACTS.TERMINATE(id), { reason });
  },

  renew: async (
    id: string,
    data: { new_end_date: string; adjustment_percent?: number; new_monthly_value?: number }
  ) => {
    return api.post<Contract>(CRM_ENDPOINTS.CONTRACTS.RENEW(id), data);
  },

  calculateAdjustment: async (id: string) => {
    return api.post<{ current_value: number; new_value: number; adjustment_percent: number }>(
      CRM_ENDPOINTS.CONTRACTS.CALCULATE_ADJUSTMENT(id)
    );
  },

  getStats: async () => {
    return api.get<ContractStats>(CRM_ENDPOINTS.CONTRACTS.STATS);
  },

  getAlerts: async () => {
    return api.get<
      { contract_id: string; contract_name: string; alert_type: string; message: string }[]
    >(CRM_ENDPOINTS.CONTRACTS.ALERTS);
  },
};

// ==================== COMMISSION SERVICES ====================

export const commissionService = {
  // Regras
  rules: {
    list: async (params?: { page?: number; page_size?: number; is_active?: boolean }) => {
      return api.get<CommissionRuleListResponse>(CRM_ENDPOINTS.COMMISSIONS.RULES.LIST, { params });
    },

    create: async (data: CommissionRuleCreate) => {
      return api.post<CommissionRule>(CRM_ENDPOINTS.COMMISSIONS.RULES.CREATE, data);
    },

    getById: async (id: string) => {
      return api.get<CommissionRule>(CRM_ENDPOINTS.COMMISSIONS.RULES.DETAIL(id));
    },

    update: async (id: string, data: Partial<CommissionRuleCreate>) => {
      return api.put<CommissionRule>(CRM_ENDPOINTS.COMMISSIONS.RULES.UPDATE(id), data);
    },

    delete: async (id: string) => {
      return api.delete<void>(CRM_ENDPOINTS.COMMISSIONS.RULES.DELETE(id));
    },
  },

  // Comissões
  list: async (params?: CommissionFilter & { page?: number; page_size?: number }) => {
    return api.get<CommissionListResponse>(CRM_ENDPOINTS.COMMISSIONS.LIST, { params });
  },

  calculate: async (data: {
    seller_id: string;
    proposal_id: string;
    sale_value: number;
    sale_margin?: number;
    rule_id?: string;
  }) => {
    return api.post<Commission>(CRM_ENDPOINTS.COMMISSIONS.CALCULATE, data);
  },

  create: async (data: CommissionCreate) => {
    return api.post<Commission>(CRM_ENDPOINTS.COMMISSIONS.CALCULATE, data);
  },

  getById: async (id: string) => {
    return api.get<Commission>(CRM_ENDPOINTS.COMMISSIONS.DETAIL(id));
  },

  update: async (
    id: string,
    data: { adjustments?: number; description?: string; notes?: string; due_date?: string }
  ) => {
    return api.put<Commission>(CRM_ENDPOINTS.COMMISSIONS.UPDATE(id), data);
  },

  delete: async (id: string) => {
    return api.delete<void>(CRM_ENDPOINTS.COMMISSIONS.DELETE(id));
  },

  updateStatus: async (id: string, data: { status: string; notes?: string }) => {
    return api.patch<Commission>(CRM_ENDPOINTS.COMMISSIONS.UPDATE_STATUS(id), data);
  },

  approve: async (id: string, notes?: string) => {
    return api.post<Commission>(CRM_ENDPOINTS.COMMISSIONS.APPROVE(id), { notes });
  },

  getStats: async () => {
    return api.get<CommissionStats>(CRM_ENDPOINTS.COMMISSIONS.STATS);
  },

  getSellerStats: async (sellerId: string) => {
    return api.get<SellerCommissionStats>(CRM_ENDPOINTS.COMMISSIONS.SELLER_STATS(sellerId));
  },

  getRanking: async (params?: { period?: string; limit?: number }) => {
    return api.get<SellerCommissionStats[]>(CRM_ENDPOINTS.DASHBOARD.RANKING, { params });
  },
};

// ==================== DASHBOARD SERVICES ====================

export const crmDashboardService = {
  getDashboard: async (params?: { period?: string }) => {
    return api.get<any>(CRM_ENDPOINTS.DASHBOARD.MAIN, { params });
  },

  getPipeline: async (params?: { period?: string }) => {
    return api.get<any>(CRM_ENDPOINTS.DASHBOARD.PIPELINE, { params });
  },

  getKPIs: async () => {
    return api.get<CRMDashboardKPIs>(CRM_ENDPOINTS.DASHBOARD.KPIS);
  },

  getFunnel: async (params?: { period?: string }) => {
    return api.get<FunnelData[]>(CRM_ENDPOINTS.DASHBOARD.FUNNEL, { params });
  },

  getLeadTrends: async (params?: { period?: 'week' | 'month' | 'quarter' | 'year' }) => {
    return api.get<TrendData[]>(CRM_ENDPOINTS.DASHBOARD.TRENDS_LEADS, { params });
  },

  getSalesTrends: async (params?: { period?: 'week' | 'month' | 'quarter' | 'year' }) => {
    return api.get<TrendData[]>(CRM_ENDPOINTS.DASHBOARD.TRENDS_SALES, { params });
  },

  getCommissionTrends: async (params?: { period?: 'week' | 'month' | 'quarter' | 'year' }) => {
    return api.get<TrendData[]>(CRM_ENDPOINTS.DASHBOARD.TRENDS_COMMISSIONS, { params });
  },

  getConversionRates: async () => {
    return api.get<{ stage: string; rate: number }[]>(CRM_ENDPOINTS.DASHBOARD.CONVERSION_RATES);
  },

  getSellerPerformance: async (sellerId: string) => {
    return api.get<SellerCommissionStats>(CRM_ENDPOINTS.DASHBOARD.SELLER_PERFORMANCE(sellerId));
  },

  getTopPerformers: async (params?: { limit?: number; period?: 'month' | 'quarter' | 'year' }) => {
    return api.get<SellerCommissionStats[]>(CRM_ENDPOINTS.DASHBOARD.TOP_PERFORMERS, { params });
  },
};

export default {
  leads: leadService,
  opportunities: opportunityService,
  proposals: proposalService,
  contracts: contractService,
  commissions: commissionService,
  dashboard: crmDashboardService,
};
