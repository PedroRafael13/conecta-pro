/**
 * Hooks React Query - Contract Management (Migrado para Orval)
 * Gestão de Contratos
 *
 * MIGRADO: Re-exports dos hooks Orval gerados
 */

// Re-export dos hooks Orval com nomes simplificados
export {
  useListContractsApiV1ClientsClientsClientIdContractsGet as useContracts,
  useGetContractApiV1ClientsClientsContractsContractIdGet as useContract,
  useCreateContractApiV1ClientsClientsClientIdContractsPost as useCreateContract,
  useUpdateContractApiV1ClientsClientsContractsContractIdPut as useUpdateContract,
  useActivateContractApiV1ClientsClientsContractsContractIdActivatePost as useActivateContract,
  useSuspendContractApiV1ClientsClientsContractsContractIdSuspendPost as useSuspendContract,
  useCancelContractApiV1ClientsClientsContractsContractIdCancelPost as useCancelContract,
} from '@/types/generated/clients/clients-cadastro';
