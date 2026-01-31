/**
 * Hooks React Query - Client Management (Migrado para Orval)
 * Gestão de Clientes
 *
 * MIGRADO: Re-exports dos hooks Orval gerados
 */

// Re-export dos hooks Orval com nomes simplificados
export {
  useListClientsApiV1ClientsClientsGet as useClients,
  useGetClientApiV1ClientsClientsClientIdGet as useClient,
  useGetClientFullApiV1ClientsClientsClientIdFullGet as useClientFull,
  useGetClientStatsApiV1ClientsClientsStatsGet as useClientStats,
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
