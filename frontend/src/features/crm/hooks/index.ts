/**
 * React Query hooks para o módulo CRM
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  leadService,
  opportunityService,
  proposalService,
  contractService,
  commissionService,
  crmDashboardService,
} from '../api/services';
import type {
  LeadCreate,
  LeadUpdate,
  LeadStatusUpdate,
  LeadFilter,
  OpportunityCreate,
  OpportunityCreateFromLead,
  OpportunityUpdate,
  OpportunityStageUpdate,
  OpportunityClose,
  OpportunityFilter,
  ProposalCreate,
  ProposalUpdate,
  ProposalFilter,
  ProposalItemCreate,
  ContractCreate,
  ContractUpdate,
  ContractFilter,
  CommissionCreate,
  CommissionFilter,
  CommissionRuleCreate,
} from '../types';

// ==================== QUERY KEYS ====================

export const CRM_QUERY_KEYS = {
  leads: {
    all: ['crm', 'leads'] as const,
    lists: () => [...CRM_QUERY_KEYS.leads.all, 'list'] as const,
    list: (filters: LeadFilter & { page?: number; page_size?: number }) =>
      [...CRM_QUERY_KEYS.leads.lists(), filters] as const,
    details: () => [...CRM_QUERY_KEYS.leads.all, 'detail'] as const,
    detail: (id: string) => [...CRM_QUERY_KEYS.leads.details(), id] as const,
    stats: (assigned_to_id?: string) =>
      [...CRM_QUERY_KEYS.leads.all, 'stats', assigned_to_id] as const,
  },
  opportunities: {
    all: ['crm', 'opportunities'] as const,
    lists: () => [...CRM_QUERY_KEYS.opportunities.all, 'list'] as const,
    list: (filters: OpportunityFilter & { page?: number; page_size?: number }) =>
      [...CRM_QUERY_KEYS.opportunities.lists(), filters] as const,
    details: () => [...CRM_QUERY_KEYS.opportunities.all, 'detail'] as const,
    detail: (id: string) => [...CRM_QUERY_KEYS.opportunities.details(), id] as const,
  },
  proposals: {
    all: ['crm', 'proposals'] as const,
    lists: () => [...CRM_QUERY_KEYS.proposals.all, 'list'] as const,
    list: (filters: ProposalFilter & { page?: number; page_size?: number }) =>
      [...CRM_QUERY_KEYS.proposals.lists(), filters] as const,
    details: () => [...CRM_QUERY_KEYS.proposals.all, 'detail'] as const,
    detail: (id: string) => [...CRM_QUERY_KEYS.proposals.details(), id] as const,
    stats: () => [...CRM_QUERY_KEYS.proposals.all, 'stats'] as const,
    templates: () => [...CRM_QUERY_KEYS.proposals.all, 'templates'] as const,
  },
  contracts: {
    all: ['crm', 'contracts'] as const,
    lists: () => [...CRM_QUERY_KEYS.contracts.all, 'list'] as const,
    list: (filters: ContractFilter & { page?: number; page_size?: number }) =>
      [...CRM_QUERY_KEYS.contracts.lists(), filters] as const,
    details: () => [...CRM_QUERY_KEYS.contracts.all, 'detail'] as const,
    detail: (id: string) => [...CRM_QUERY_KEYS.contracts.details(), id] as const,
    stats: () => [...CRM_QUERY_KEYS.contracts.all, 'stats'] as const,
    alerts: () => [...CRM_QUERY_KEYS.contracts.all, 'alerts'] as const,
  },
  commissions: {
    all: ['crm', 'commissions'] as const,
    lists: () => [...CRM_QUERY_KEYS.commissions.all, 'list'] as const,
    list: (filters: CommissionFilter & { page?: number; page_size?: number }) =>
      [...CRM_QUERY_KEYS.commissions.lists(), filters] as const,
    details: () => [...CRM_QUERY_KEYS.commissions.all, 'detail'] as const,
    detail: (id: string) => [...CRM_QUERY_KEYS.commissions.details(), id] as const,
    stats: () => [...CRM_QUERY_KEYS.commissions.all, 'stats'] as const,
    rules: {
      all: ['crm', 'commissions', 'rules'] as const,
      list: () => [...CRM_QUERY_KEYS.commissions.rules.all, 'list'] as const,
      detail: (id: string) => [...CRM_QUERY_KEYS.commissions.rules.all, 'detail', id] as const,
    },
  },
  dashboard: {
    all: ['crm', 'dashboard'] as const,
    kpis: () => [...CRM_QUERY_KEYS.dashboard.all, 'kpis'] as const,
    funnel: () => [...CRM_QUERY_KEYS.dashboard.all, 'funnel'] as const,
    trends: (type: string, period?: string) =>
      [...CRM_QUERY_KEYS.dashboard.all, 'trends', type, period] as const,
    topPerformers: (params?: { limit?: number; period?: string }) =>
      [...CRM_QUERY_KEYS.dashboard.all, 'top-performers', params] as const,
  },
};

// ==================== LEAD HOOKS ====================

export function useLeads(params?: LeadFilter & { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.leads.list(params || {}),
    queryFn: () => leadService.list(params),
  });
}

export function useLead(id: string) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.leads.detail(id),
    queryFn: () => leadService.getById(id),
    enabled: !!id,
  });
}

export function useLeadStats(assigned_to_id?: string) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.leads.stats(assigned_to_id),
    queryFn: () => leadService.getStats(assigned_to_id),
  });
}

export function useCreateLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LeadCreate) => leadService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.all });
    },
  });
}

export function useUpdateLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: LeadUpdate }) => leadService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.lists() });
    },
  });
}

export function useUpdateLeadStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: LeadStatusUpdate }) =>
      leadService.updateStatus(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.stats() });
    },
  });
}

export function useDeleteLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => leadService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.all });
    },
  });
}

export function useLeadRecommendedAction(id: string) {
  return useQuery({
    queryKey: [...CRM_QUERY_KEYS.leads.detail(id), 'recommended-action'],
    queryFn: () => leadService.getRecommendedAction(id),
    enabled: !!id,
  });
}

// ==================== OPPORTUNITY HOOKS ====================

export function useOpportunities(params?: OpportunityFilter & { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.opportunities.list(params || {}),
    queryFn: () => opportunityService.list(params),
  });
}

export function useOpportunity(id: string) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.opportunities.detail(id),
    queryFn: () => opportunityService.getById(id),
    enabled: !!id,
  });
}

export function useCreateOpportunity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: OpportunityCreate) => opportunityService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.all });
    },
  });
}

export function useCreateOpportunityFromLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: OpportunityCreateFromLead) => opportunityService.createFromLead(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.all });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.leads.detail(variables.lead_id) });
    },
  });
}

export function useUpdateOpportunity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: OpportunityUpdate }) =>
      opportunityService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.lists() });
    },
  });
}

export function useUpdateOpportunityStage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: OpportunityStageUpdate }) =>
      opportunityService.updateStage(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.dashboard.funnel() });
    },
  });
}

export function useCloseOpportunity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: OpportunityClose }) =>
      opportunityService.close(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.dashboard.all });
    },
  });
}

export function useDeleteOpportunity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => opportunityService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.opportunities.all });
    },
  });
}

// ==================== PROPOSAL HOOKS ====================

export function useProposals(params?: ProposalFilter & { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.proposals.list(params || {}),
    queryFn: () => proposalService.list(params),
  });
}

export function useProposal(id: string) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.proposals.detail(id),
    queryFn: () => proposalService.getById(id),
    enabled: !!id,
  });
}

export function useProposalStats() {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.proposals.stats(),
    queryFn: () => proposalService.getStats(),
  });
}

export function useProposalTemplates() {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.proposals.templates(),
    queryFn: () => proposalService.getTemplates(),
  });
}

export function useCreateProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProposalCreate) => proposalService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.all });
    },
  });
}

export function useUpdateProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProposalUpdate }) =>
      proposalService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.lists() });
    },
  });
}

export function useSubmitProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => proposalService.submit(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.lists() });
    },
  });
}

export function useApproveProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comments }: { id: string; comments?: string }) =>
      proposalService.approve(id, comments),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.lists() });
    },
  });
}

export function useSendProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data?: { recipient_email?: string; subject?: string; message?: string; cc_emails?: string[] };
    }) => proposalService.send(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.lists() });
    },
  });
}

export function useDeleteProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => proposalService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.all });
    },
  });
}

export function useAddProposalItems() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, items }: { id: string; items: ProposalItemCreate[] }) =>
      proposalService.addItems(id, items),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(variables.id) });
    },
  });
}

export function useAcceptProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data?: { feedback?: string; signature?: string } }) =>
      proposalService.accept(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.stats() });
    },
  });
}

export function useRejectProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, feedback }: { id: string; feedback?: string }) =>
      proposalService.reject(id, feedback),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.stats() });
    },
  });
}

export function useCreateProposalVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => proposalService.createNewVersion(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.detail(id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.proposals.lists() });
    },
  });
}

// ==================== CONTRACT HOOKS ====================

export function useContracts(params?: ContractFilter & { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.contracts.list(params || {}),
    queryFn: () => contractService.list(params),
  });
}

export function useContract(id: string) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.contracts.detail(id),
    queryFn: () => contractService.getById(id),
    enabled: !!id,
  });
}

export function useContractStats() {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.contracts.stats(),
    queryFn: () => contractService.getStats(),
  });
}

export function useContractAlerts() {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.contracts.alerts(),
    queryFn: () => contractService.getAlerts(),
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ContractCreate) => contractService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.all });
    },
  });
}

export function useUpdateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ContractUpdate }) =>
      contractService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.lists() });
    },
  });
}

export function useActivateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => contractService.activate(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.detail(id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.stats() });
    },
  });
}

export function useSuspendContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      contractService.suspend(id, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.lists() });
    },
  });
}

export function useTerminateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      contractService.terminate(id, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.stats() });
    },
  });
}

export function useRenewContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { new_end_date: string; adjustment_percent?: number; new_monthly_value?: number };
    }) => contractService.renew(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.lists() });
    },
  });
}

export function useDeleteContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => contractService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.contracts.all });
    },
  });
}

// ==================== COMMISSION HOOKS ====================

export function useCommissions(params?: CommissionFilter & { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.commissions.list(params || {}),
    queryFn: () => commissionService.list(params),
  });
}

export function useCommission(id: string) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.commissions.detail(id),
    queryFn: () => commissionService.getById(id),
    enabled: !!id,
  });
}

export function useCommissionStats(params?: { period?: string }) {
  return useQuery({
    queryKey: [...CRM_QUERY_KEYS.commissions.stats(), params],
    queryFn: () => commissionService.getStats(),
  });
}

export function useCommissionRules(params?: { page?: number; page_size?: number; is_active?: boolean }) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.commissions.rules.list(),
    queryFn: () => commissionService.rules.list(params),
  });
}

export function useCreateCommissionRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CommissionRuleCreate) => commissionService.rules.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.rules.all });
    },
  });
}

export function useCalculateCommission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      seller_id: string;
      proposal_id: string;
      sale_value: number;
      sale_margin?: number;
      rule_id?: string;
    }) => commissionService.calculate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.all });
    },
  });
}

export function useApproveCommission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => commissionService.approve(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.detail(id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.stats() });
    },
  });
}

export function usePayCommission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => commissionService.updateStatus(id, { status: 'paid' }),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.detail(id) });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.lists() });
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.stats() });
    },
  });
}

export function useDeleteCommission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => commissionService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.all });
    },
  });
}

export function useCommissionRanking(params?: { period?: string; limit?: number }) {
  return useQuery({
    queryKey: ['crm', 'commissions', 'ranking', params],
    queryFn: () => commissionService.getRanking(params),
  });
}

export function useCreateCommission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CommissionCreate) => commissionService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CRM_QUERY_KEYS.commissions.all });
    },
  });
}

// ==================== DASHBOARD HOOKS ====================

export function useCRMDashboard(params?: { period?: string }) {
  return useQuery({
    queryKey: ['crm', 'dashboard', params],
    queryFn: () => crmDashboardService.getDashboard(params),
  });
}

export function useCRMPipeline(params?: { period?: string }) {
  return useQuery({
    queryKey: ['crm', 'pipeline', params],
    queryFn: () => crmDashboardService.getPipeline(params),
  });
}

export function useCRMDashboardKPIs() {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.dashboard.kpis(),
    queryFn: () => crmDashboardService.getKPIs(),
  });
}

export function useCRMFunnel(params?: { period?: string }) {
  return useQuery({
    queryKey: ['crm', 'funnel', params],
    queryFn: () => crmDashboardService.getFunnel(params),
  });
}

export function useLeadTrends(period?: 'week' | 'month' | 'quarter' | 'year') {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.dashboard.trends('leads', period),
    queryFn: () => crmDashboardService.getLeadTrends({ period }),
  });
}

export function useSalesTrends(period?: 'week' | 'month' | 'quarter' | 'year') {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.dashboard.trends('sales', period),
    queryFn: () => crmDashboardService.getSalesTrends({ period }),
  });
}

export function useTopPerformers(params?: { limit?: number; period?: 'month' | 'quarter' | 'year' }) {
  return useQuery({
    queryKey: CRM_QUERY_KEYS.dashboard.topPerformers(params),
    queryFn: () => crmDashboardService.getTopPerformers(params),
  });
}
