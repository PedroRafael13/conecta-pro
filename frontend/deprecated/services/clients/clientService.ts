/**
 * Service Layer - Client Management (DEPRECATED)
 * Gestão de Clientes
 *
 * @deprecated Use hooks Orval de @/types/generated/clients/clients-cadastro/clients-cadastro
 *
 * Mapeamento de hooks:
 * - clientService.list -> useListClientsApiV1ClientsClientsGet
 * - clientService.getById -> useGetClientApiV1ClientsClientsClientIdGet
 * - clientService.getFullById -> useGetClientFullApiV1ClientsClientsClientIdFullGet
 * - clientService.getStats -> useGetClientStatsApiV1ClientsClientsStatsGet
 * - clientService.create -> useCreateClientApiV1ClientsClientsPost
 * - clientService.update -> useUpdateClientApiV1ClientsClientsClientIdPut
 * - clientService.delete -> useDeleteClientApiV1ClientsClientsClientIdDelete
 * - clientService.activate -> useActivateClientApiV1ClientsClientsClientIdActivatePost
 * - clientService.suspend -> useSuspendClientApiV1ClientsClientsClientIdSuspendPost
 * - clientService.block -> useBlockClientApiV1ClientsClientsClientIdBlockPost
 * - clientService.setDefaulter -> useSetDefaulterApiV1ClientsClientsClientIdSetDefaulterPost
 * - clientService.clearDefaulter -> useClearDefaulterApiV1ClientsClientsClientIdClearDefaulterPost
 * - clientService.enableGuardian -> useEnableGuardianApiV1ClientsClientsClientIdEnableGuardianPost
 * - clientService.enablePlus -> useEnablePlusApiV1ClientsClientsClientIdEnablePlusPost
 */

// Re-export dos hooks Orval para compatibilidade
export {
  useListClientsApiV1ClientsClientsGet as useListClients,
  useGetClientApiV1ClientsClientsClientIdGet as useGetClient,
  useGetClientFullApiV1ClientsClientsClientIdFullGet as useGetClientFull,
  useGetClientStatsApiV1ClientsClientsStatsGet as useGetClientStats,
  useCreateClientApiV1ClientsClientsPost as useCreateClient,
  useUpdateClientApiV1ClientsClientsClientIdPut as useUpdateClient,
  useDeleteClientApiV1ClientsClientsClientIdDelete as useDeleteClient,
  useActivateClientApiV1ClientsClientsClientIdActivatePost as useActivateClient,
  useSuspendClientApiV1ClientsClientsClientIdSuspendPost as useSuspendClient,
  useBlockClientApiV1ClientsClientsClientIdBlockPost as useBlockClient,
  useSetDefaulterApiV1ClientsClientsClientIdSetDefaulterPost as useSetDefaulter,
  useClearDefaulterApiV1ClientsClientsClientIdClearDefaulterPost as useClearDefaulter,
  useEnableGuardianApiV1ClientsClientsClientIdEnableGuardianPost as useEnableGuardian,
  useEnablePlusApiV1ClientsClientsClientIdEnablePlusPost as useEnablePlus,
} from '@/types/generated/clients/clients-cadastro';
