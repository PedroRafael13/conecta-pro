/**
 * Service Layer - Contract Management (DEPRECATED)
 * Gestão de Contratos de Clientes
 *
 * @deprecated Use hooks Orval de @/types/generated/clients/clients-cadastro/clients-cadastro
 *
 * Mapeamento de hooks:
 * - contractService.list -> useListContractsApiV1ClientsClientsClientIdContractsGet
 * - contractService.getById -> useGetContractApiV1ClientsClientsContractsContractIdGet
 * - contractService.create -> useCreateContractApiV1ClientsClientsClientIdContractsPost
 * - contractService.update -> useUpdateContractApiV1ClientsClientsContractsContractIdPut
 * - contractService.activate -> useActivateContractApiV1ClientsClientsContractsContractIdActivatePost
 * - contractService.suspend -> useSuspendContractApiV1ClientsClientsContractsContractIdSuspendPost
 * - contractService.cancel -> useCancelContractApiV1ClientsClientsContractsContractIdCancelPost
 */

// Re-export dos hooks Orval para compatibilidade
export {
  useListContractsApiV1ClientsClientsClientIdContractsGet as useListContracts,
  useGetContractApiV1ClientsClientsContractsContractIdGet as useGetContract,
  useCreateContractApiV1ClientsClientsClientIdContractsPost as useCreateContract,
  useUpdateContractApiV1ClientsClientsContractsContractIdPut as useUpdateContract,
  useActivateContractApiV1ClientsClientsContractsContractIdActivatePost as useActivateContract,
  useSuspendContractApiV1ClientsClientsContractsContractIdSuspendPost as useSuspendContract,
  useCancelContractApiV1ClientsClientsContractsContractIdCancelPost as useCancelContract,
} from '@/types/generated/clients/clients-cadastro';
