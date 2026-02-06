/**
 * Hooks React Query - Unit Management (Migrado para Orval)
 * Gestão de Unidades
 *
 * MIGRADO: Re-exports dos hooks Orval gerados
 */

// Re-export dos hooks Orval com nomes simplificados
export {
  useListUnitsApiV1ClientsClientsCondominiumsCondominiumIdUnitsGet as useUnits,
  useGetUnitApiV1ClientsClientsUnitsUnitIdGet as useUnit,
  useCreateUnitApiV1ClientsClientsCondominiumsCondominiumIdUnitsPost as useCreateUnit,
  useUpdateUnitApiV1ClientsClientsUnitsUnitIdPut as useUpdateUnit,
  useDeleteUnitApiV1ClientsClientsUnitsUnitIdDelete as useDeleteUnit,
  useSetUnitOwnerApiV1ClientsClientsUnitsUnitIdSetOwnerPost as useSetUnitOwner,
  useSetUnitResidentApiV1ClientsClientsUnitsUnitIdSetResidentPost as useSetUnitResident,
  useClearUnitResidentApiV1ClientsClientsUnitsUnitIdClearResidentPost as useClearUnitResident,
  useGetUnitStatsApiV1ClientsClientsCondominiumsCondominiumIdUnitsStatsGet as useUnitStats,
} from '@/types/generated/clients/clients-cadastro';
