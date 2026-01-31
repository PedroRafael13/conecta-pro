/**
 * Allocations Hooks - Alocações de Funcionários em Postos
 *
 * Re-exports dos hooks Orval do módulo operacional-alocacoes
 */

import {
  useListAllocationsApiV1OperacionalAllocationsGet,
  useCreateAllocationApiV1OperacionalAllocationsPost,
  useGetAllocationApiV1OperacionalAllocationsAllocationIdGet,
  useUpdateAllocationApiV1OperacionalAllocationsAllocationIdPatch,
  useDeleteAllocationApiV1OperacionalAllocationsAllocationIdDelete,
  useTerminateAllocationApiV1OperacionalAllocationsAllocationIdTerminatePost,
  useGetAllocationsByPostApiV1OperacionalAllocationsPostPostIdGet,
  useGetAllocationsByEmployeeApiV1OperacionalAllocationsEmployeeEmployeeIdGet,
  useGetCurrentAllocationsApiV1OperacionalAllocationsCurrentGet,
  useGetAvailableEmployeesApiV1OperacionalAllocationsAvailableEmployeesGet,
} from '@/types/generated/operacional/operacional-alocacoes/operacional-alocacoes';

// List & Read
export const useAllocations = useListAllocationsApiV1OperacionalAllocationsGet;
export const useAllocation = useGetAllocationApiV1OperacionalAllocationsAllocationIdGet;
export const useAllocationsByPost = useGetAllocationsByPostApiV1OperacionalAllocationsPostPostIdGet;
export const useAllocationsByEmployee = useGetAllocationsByEmployeeApiV1OperacionalAllocationsEmployeeEmployeeIdGet;
export const useCurrentAllocations = useGetCurrentAllocationsApiV1OperacionalAllocationsCurrentGet;
export const useAvailableEmployees = useGetAvailableEmployeesApiV1OperacionalAllocationsAvailableEmployeesGet;

// Mutations
export const useCreateAllocation = useCreateAllocationApiV1OperacionalAllocationsPost;
export const useUpdateAllocation = useUpdateAllocationApiV1OperacionalAllocationsAllocationIdPatch;
export const useDeleteAllocation = useDeleteAllocationApiV1OperacionalAllocationsAllocationIdDelete;
export const useTerminateAllocation = useTerminateAllocationApiV1OperacionalAllocationsAllocationIdTerminatePost;

// Re-export types
export type {
  AllocationCreate,
  AllocationUpdate,
  AllocationResponse,
  AllocationTerminate,
  AllocationListResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
