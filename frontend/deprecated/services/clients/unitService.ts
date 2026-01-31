/**
 * Service Layer - Unit Management (DEPRECATED)
 * Gestão de Unidades
 *
 * @deprecated Use hooks Orval de @/types/generated/clients/clients-cadastro/clients-cadastro
 *
 * Mapeamento de hooks:
 * - unitService.list -> useListUnitsApiV1ClientsClientsCondominiumsCondominiumIdUnitsGet
 * - unitService.getById -> useGetUnitApiV1ClientsClientsUnitsUnitIdGet
 * - unitService.create -> useCreateUnitApiV1ClientsClientsCondominiumsCondominiumIdUnitsPost
 * - unitService.update -> useUpdateUnitApiV1ClientsClientsUnitsUnitIdPut
 * - unitService.delete -> useDeleteUnitApiV1ClientsClientsUnitsUnitIdDelete
 * - unitService.setOwner -> useSetUnitOwnerApiV1ClientsClientsUnitsUnitIdSetOwnerPost
 * - unitService.setResident -> useSetUnitResidentApiV1ClientsClientsUnitsUnitIdSetResidentPost
 * - unitService.clearResident -> useClearUnitResidentApiV1ClientsClientsUnitsUnitIdClearResidentPost
 * - unitService.getStats -> useGetUnitStatsApiV1ClientsClientsCondominiumsCondominiumIdUnitsStatsGet
 */

// Re-export dos hooks Orval para compatibilidade
export {
  useListUnitsApiV1ClientsClientsCondominiumsCondominiumIdUnitsGet as useListUnits,
  useGetUnitApiV1ClientsClientsUnitsUnitIdGet as useGetUnit,
  useCreateUnitApiV1ClientsClientsCondominiumsCondominiumIdUnitsPost as useCreateUnit,
  useUpdateUnitApiV1ClientsClientsUnitsUnitIdPut as useUpdateUnit,
  useDeleteUnitApiV1ClientsClientsUnitsUnitIdDelete as useDeleteUnit,
  useSetUnitOwnerApiV1ClientsClientsUnitsUnitIdSetOwnerPost as useSetUnitOwner,
  useSetUnitResidentApiV1ClientsClientsUnitsUnitIdSetResidentPost as useSetUnitResident,
  useClearUnitResidentApiV1ClientsClientsUnitsUnitIdClearResidentPost as useClearUnitResident,
  useGetUnitStatsApiV1ClientsClientsCondominiumsCondominiumIdUnitsStatsGet as useGetUnitStats,
} from '@/types/generated/clients/clients-cadastro';
