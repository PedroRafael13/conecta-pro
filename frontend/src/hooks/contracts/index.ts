/**
 * Hooks Contracts - Barrel Export
 * Exporta todos os hooks de contratos
 */

// Contract Management
export {
  useContracts,
  useContractStats,
  useContractAlerts,
  useContract,
  useCreateContract,
  useUpdateContract,
  useSubmitContract,
  useActivateContract,
  useSuspendContract,
  useTerminateContract,
  useCalculateRenewal,
  useCalculateAdjustment,
  useDeleteContract,
  contractKeys,
} from './useContracts';

// Contract Items
export {
  useAddContractItem,
  useUpdateContractItem,
  useRemoveContractItem,
} from './useContractItems';

// Contract Addendums
export {
  useContractAddendums,
  useCreateAddendum,
  useSignAddendum,
  addendumKeys,
} from './useContractAddendums';

// Contract Templates
export {
  useContractTemplates,
  useContractTemplate,
  useCreateTemplate,
  useUpdateTemplate,
  useApproveTemplate,
  useDeleteTemplate,
  templateKeys,
} from './useContractTemplates';

// Contract SLA
export {
  useContractSLAReports,
  useCreateSLAReport,
  useApproveSLAReport,
  useCalculateSLA,
  slaKeys,
} from './useContractSLA';
