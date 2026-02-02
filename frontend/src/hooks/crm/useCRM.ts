/**
 * Hook Consolidado: useCRM
 *
 * Re-export dos hooks Orval para todo o modulo CRM.
 * Cobertura: Leads, Oportunidades, Propostas, Contratos, Comissoes e Dashboard.
 */

// =============================================================================
// LEADS
// =============================================================================
export * from '@/types/generated/crm/crm-leads';
export {
  useListLeadsApiV1CrmLeadsGet as useOrvalLeads,
  useGetLeadApiV1CrmLeadsLeadIdGet as useOrvalLead,
  useGetLeadStatsApiV1CrmLeadsStatsGet as useOrvalLeadsStats,
  useCreateLeadApiV1CrmLeadsPost as useOrvalCreateLead,
  useUpdateLeadApiV1CrmLeadsLeadIdPut as useOrvalUpdateLead,
  useDeleteLeadApiV1CrmLeadsLeadIdDelete as useOrvalDeleteLead,
  useUpdateLeadStatusApiV1CrmLeadsLeadIdStatusPatch as useUpdateLeadStatus,
  useRecalculateLeadScoreApiV1CrmLeadsLeadIdRecalculateScorePost as useRecalculateLeadScore,
  useGetRecommendedActionApiV1CrmLeadsLeadIdRecommendedActionGet as useLeadRecommendedAction,
  getListLeadsApiV1CrmLeadsGetQueryKey as leadKeys,
} from '@/types/generated/crm/crm-leads';

// =============================================================================
// OPORTUNIDADES (OPPORTUNITIES)
// =============================================================================
export * from '@/types/generated/crm/crm-oportunidades';
export {
  useListOpportunitiesApiV1CrmOpportunitiesGet as useOpportunities,
  useGetOpportunityApiV1CrmOpportunitiesOpportunityIdGet as useOpportunity,
  useGetPipelineStatsApiV1CrmOpportunitiesPipelineStatsGet as usePipelineStats,
  useCreateOpportunityApiV1CrmOpportunitiesPost as useCreateOpportunity,
  useUpdateOpportunityApiV1CrmOpportunitiesOpportunityIdPut as useUpdateOpportunity,
  useDeleteOpportunityApiV1CrmOpportunitiesOpportunityIdDelete as useDeleteOpportunity,
  useUpdateOpportunityStageApiV1CrmOpportunitiesOpportunityIdStagePatch as useUpdateOpportunityStage,
  useCloseOpportunityApiV1CrmOpportunitiesOpportunityIdClosePost as useCloseOpportunity,
  useCreateOpportunityFromLeadApiV1CrmOpportunitiesFromLeadPost as useCreateOpportunityFromLead,
  getListOpportunitiesApiV1CrmOpportunitiesGetQueryKey as opportunityKeys,
} from '@/types/generated/crm/crm-oportunidades';

// =============================================================================
// PROPOSTAS (PROPOSALS)
// =============================================================================
export * from '@/types/generated/crm/crm-propostas';
export {
  useListProposalsApiV1CrmProposalsGet as useProposals,
  useGetProposalApiV1CrmProposalsProposalIdGet as useProposal,
  useGetProposalStatsApiV1CrmProposalsStatsGet as useProposalStats,
  useCreateProposalApiV1CrmProposalsPost as useCreateProposal,
  useUpdateProposalApiV1CrmProposalsProposalIdPut as useUpdateProposal,
  useDeleteProposalApiV1CrmProposalsProposalIdDelete as useDeleteProposal,
  useSubmitProposalForApprovalApiV1CrmProposalsProposalIdSubmitPost as useSubmitProposal,
  useProcessProposalApprovalApiV1CrmProposalsProposalIdApprovePost as useApproveProposal,
  useSendProposalApiV1CrmProposalsProposalIdSendPost as useSendProposal,
  useAcceptProposalApiV1CrmProposalsProposalIdAcceptPost as useAcceptProposal,
  useRejectProposalApiV1CrmProposalsProposalIdRejectPost as useRejectProposal,
  useCreateNewVersionApiV1CrmProposalsProposalIdNewVersionPost as useNewProposalVersion,
  useAddProposalItemApiV1CrmProposalsProposalIdItemsPost as useAddProposalItem,
  useRemoveProposalItemApiV1CrmProposalsProposalIdItemsItemIdDelete as useRemoveProposalItem,
  useCreateProposalFromOpportunityApiV1CrmProposalsFromOpportunityPost as useCreateProposalFromOpportunity,
  useListTemplatesApiV1CrmProposalsTemplatesGet as useProposalTemplates,
  useCreateTemplateApiV1CrmProposalsTemplatesPost as useCreateProposalTemplate,
  useGetTemplateApiV1CrmProposalsTemplatesTemplateIdGet as useProposalTemplate,
  useUpdateTemplateApiV1CrmProposalsTemplatesTemplateIdPut as useUpdateProposalTemplate,
  useDeleteTemplateApiV1CrmProposalsTemplatesTemplateIdDelete as useDeleteProposalTemplate,
  getListProposalsApiV1CrmProposalsGetQueryKey as proposalKeys,
} from '@/types/generated/crm/crm-propostas';

// =============================================================================
// CONTRATOS (CONTRACTS)
// =============================================================================
export * from '@/types/generated/crm/crm-contratos';
export {
  useListContractsApiV1CrmContractsGet as useContracts,
  useGetContractApiV1CrmContractsContractIdGet as useContract,
  useGetContractStatsApiV1CrmContractsStatsGet as useContractStats,
  useCreateContractApiV1CrmContractsPost as useCreateContract,
  useUpdateContractApiV1CrmContractsContractIdPut as useUpdateContract,
  useDeleteContractApiV1CrmContractsContractIdDelete as useDeleteContract,
  useGetContractAlertsApiV1CrmContractsAlertsGet as useContractAlerts,
  useSubmitContractForSignatureApiV1CrmContractsContractIdSubmitPost as useSubmitContract,
  useActivateContractApiV1CrmContractsContractIdActivatePost as useActivateContract,
  useSuspendContractApiV1CrmContractsContractIdSuspendPost as useSuspendContract,
  useTerminateContractApiV1CrmContractsContractIdTerminatePost as useTerminateContract,
  useCalculateRenewalApiV1CrmContractsContractIdRenewPost as useRenewContract,
  useCalculateAdjustmentApiV1CrmContractsContractIdCalculateAdjustmentPost as useContractAdjustment,
  useAddContractItemApiV1CrmContractsContractIdItemsPost as useAddContractItem,
  useUpdateContractItemApiV1CrmContractsContractIdItemsItemIdPut as useUpdateContractItem,
  useRemoveContractItemApiV1CrmContractsContractIdItemsItemIdDelete as useRemoveContractItem,
  useCreateAddendumApiV1CrmContractsContractIdAddendumsPost as useCreateAddendum,
  useListAddendumsApiV1CrmContractsContractIdAddendumsGet as useAddendums,
  useSignAddendumApiV1CrmContractsAddendumsAddendumIdSignPost as useSignAddendum,
  useCreateTemplateApiV1CrmContractsTemplatesPost as useCreateContractTemplate,
  useListTemplatesApiV1CrmContractsTemplatesGet as useContractTemplates,
  useGetTemplateApiV1CrmContractsTemplatesTemplateIdGet as useContractTemplate,
  useUpdateTemplateApiV1CrmContractsTemplatesTemplateIdPut as useUpdateContractTemplate,
  useDeleteTemplateApiV1CrmContractsTemplatesTemplateIdDelete as useDeleteContractTemplate,
  useApproveTemplateApiV1CrmContractsTemplatesTemplateIdApprovePost as useApproveContractTemplate,
  useCreateSlaReportApiV1CrmContractsContractIdSlaReportsPost as useCreateSlaReport,
  useListSlaReportsApiV1CrmContractsContractIdSlaReportsGet as useSlaReports,
  useApproveSlaReportApiV1CrmContractsSlaReportsReportIdApprovePost as useApproveSlaReport,
  useCalculateSlaApiV1CrmContractsContractIdCalculateSlaPost as useCalculateSla,
  getListContractsApiV1CrmContractsGetQueryKey as contractKeys,
} from '@/types/generated/crm/crm-contratos';

// =============================================================================
// COMISSOES (COMMISSIONS)
// =============================================================================
export * from '@/types/generated/crm/crm-comissoes';
export {
  useListCommissionsApiV1CrmCommissionsGet as useCommissions,
  useGetCommissionApiV1CrmCommissionsCommissionIdGet as useCommission,
  useGetCommissionStatsApiV1CrmCommissionsStatsGet as useCommissionStats,
  useCreateCommissionApiV1CrmCommissionsPost as useCreateCommission,
  useUpdateCommissionApiV1CrmCommissionsCommissionIdPut as useUpdateCommission,
  useDeleteCommissionApiV1CrmCommissionsCommissionIdDelete as useDeleteCommission,
  useUpdateCommissionStatusApiV1CrmCommissionsCommissionIdStatusPatch as useUpdateCommissionStatus,
  useApproveCommissionApiV1CrmCommissionsCommissionIdApprovePost as useApproveCommission,
  useCalculateCommissionApiV1CrmCommissionsCalculatePost as useCalculateCommission,
  useCreateCommissionPaymentApiV1CrmCommissionsCommissionIdPaymentsPost as useCreateCommissionPayment,
  useConfirmCommissionPaymentApiV1CrmCommissionsPaymentsPaymentIdConfirmPost as useConfirmCommissionPayment,
  useListCommissionSummariesApiV1CrmCommissionsSummariesGet as useCommissionSummaries,
  useGetCommissionSummaryApiV1CrmCommissionsSummariesSellerIdYearMonthGet as useCommissionSummary,
  useCloseCommissionSummaryApiV1CrmCommissionsSummariesSellerIdYearMonthClosePost as useCloseCommissionSummary,
  useCreateCommissionRuleApiV1CrmCommissionsRulesPost as useCreateCommissionRule,
  useListCommissionRulesApiV1CrmCommissionsRulesGet as useCommissionRules,
  useGetCommissionRuleApiV1CrmCommissionsRulesRuleIdGet as useCommissionRule,
  useUpdateCommissionRuleApiV1CrmCommissionsRulesRuleIdPut as useUpdateCommissionRule,
  useDeleteCommissionRuleApiV1CrmCommissionsRulesRuleIdDelete as useDeleteCommissionRule,
  useAssignRuleToSellerApiV1CrmCommissionsRulesAssignPost as useAssignCommissionRule,
  useGetSellerCommissionStatsApiV1CrmCommissionsSellerSellerIdStatsGet as useSellerCommissionStats,
  getListCommissionsApiV1CrmCommissionsGetQueryKey as commissionKeys,
} from '@/types/generated/crm/crm-comissoes';

// =============================================================================
// DASHBOARD CRM
// =============================================================================
export * from '@/types/generated/crm/crm-dashboard';
export {
  useGetDashboardKpisApiV1CrmDashboardKpisGet as useCRMDashboardKpis,
  useGetSalesFunnelApiV1CrmDashboardFunnelGet as useSalesFunnel,
  useGetLeadsTrendsApiV1CrmDashboardTrendsLeadsGet as useLeadsTrends,
  useGetSalesTrendsApiV1CrmDashboardTrendsSalesGet as useSalesTrends,
  useGetCommissionsTrendsApiV1CrmDashboardTrendsCommissionsGet as useCommissionsTrends,
  useGetConversionRatesApiV1CrmDashboardConversionRatesGet as useConversionRates,
  useGetSellerPerformanceApiV1CrmDashboardSellerSellerIdPerformanceGet as useSellerPerformance,
  useGetTopPerformersApiV1CrmDashboardTopPerformersGet as useTopPerformers,
  useGetLeadsByStatusChartApiV1CrmDashboardChartsLeadsByStatusGet as useLeadsByStatusChart,
  useGetOpportunitiesByStageChartApiV1CrmDashboardChartsOpportunitiesByStageGet as useOpportunitiesByStageChart,
  useGetProposalsByStatusChartApiV1CrmDashboardChartsProposalsByStatusGet as useProposalsByStatusChart,
  useGetCommissionsByStatusChartApiV1CrmDashboardChartsCommissionsByStatusGet as useCommissionsByStatusChart,
  getGetDashboardKpisApiV1CrmDashboardKpisGetQueryKey as crmDashboardKeys,
} from '@/types/generated/crm/crm-dashboard';
