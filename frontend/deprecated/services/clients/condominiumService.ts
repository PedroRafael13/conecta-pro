/**
 * Service Layer - Condominium Management (DEPRECATED)
 * Gestão de Condomínios
 *
 * @deprecated Use hooks Orval de @/types/generated/clients/clients-cadastro/clients-cadastro
 *
 * Mapeamento de hooks:
 * - condominiumService.list -> useListCondominiumsApiV1ClientsClientsClientIdCondominiumsGet
 * - condominiumService.getById -> useGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGet
 * - condominiumService.getStats -> useGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGet
 * - condominiumService.create -> useCreateCondominiumApiV1ClientsClientsClientIdCondominiumsPost
 * - condominiumService.update -> useUpdateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdPut
 * - condominiumService.delete -> useDeleteCondominiumApiV1ClientsClientsCondominiumsCondominiumIdDelete
 * - condominiumService.activate -> useActivateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdActivatePost
 * - condominiumService.startImplantation -> useStartImplantationApiV1ClientsClientsCondominiumsCondominiumIdStartImplantationPost
 * - condominiumService.finishImplantation -> useFinishImplantationApiV1ClientsClientsCondominiumsCondominiumIdFinishImplantationPost
 */

// Re-export dos hooks Orval para compatibilidade
export {
  useListCondominiumsApiV1ClientsClientsClientIdCondominiumsGet as useListCondominiums,
  useGetCondominiumApiV1ClientsClientsCondominiumsCondominiumIdGet as useGetCondominium,
  useGetCondominiumStatsApiV1ClientsClientsCondominiumsStatsGet as useGetCondominiumStats,
  useCreateCondominiumApiV1ClientsClientsClientIdCondominiumsPost as useCreateCondominium,
  useUpdateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdPut as useUpdateCondominium,
  useDeleteCondominiumApiV1ClientsClientsCondominiumsCondominiumIdDelete as useDeleteCondominium,
  useActivateCondominiumApiV1ClientsClientsCondominiumsCondominiumIdActivatePost as useActivateCondominium,
  useStartImplantationApiV1ClientsClientsCondominiumsCondominiumIdStartImplantationPost as useStartImplantation,
  useFinishImplantationApiV1ClientsClientsCondominiumsCondominiumIdFinishImplantationPost as useFinishImplantation,
} from '@/types/generated/clients/clients-cadastro';
