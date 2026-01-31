/**
 * Employees Hooks - Gestão de Funcionários Operacionais
 *
 * Re-exports dos hooks Orval do módulo operacional-funcionarios
 */

import {
  useListEmployeesApiV1OperacionalEmployeesGet,
  useCreateEmployeeApiV1OperacionalEmployeesPost,
  useGetEmployeeApiV1OperacionalEmployeesEmployeeIdGet,
  useUpdateEmployeeApiV1OperacionalEmployeesEmployeeIdPatch,
  useDeleteEmployeeApiV1OperacionalEmployeesEmployeeIdDelete,
  useGetEmployeeStatsApiV1OperacionalEmployeesEmployeeIdStatsGet,
  useGetEmployeeHistoryApiV1OperacionalEmployeesEmployeeIdHistoryGet,
  useGetEmployeeDocumentsApiV1OperacionalEmployeesEmployeeIdDocumentsGet,
  useGetActiveEmployeesApiV1OperacionalEmployeesActiveGet,
  useGetEmployeesByPostApiV1OperacionalEmployeesPostPostIdGet,
} from '@/types/generated/operacional/operacional-funcionarios/operacional-funcionarios';

// List & Read
export const useEmployees = useListEmployeesApiV1OperacionalEmployeesGet;
export const useEmployee = useGetEmployeeApiV1OperacionalEmployeesEmployeeIdGet;
export const useActiveEmployees = useGetActiveEmployeesApiV1OperacionalEmployeesActiveGet;
export const useEmployeesByPost = useGetEmployeesByPostApiV1OperacionalEmployeesPostPostIdGet;
export const useEmployeeStats = useGetEmployeeStatsApiV1OperacionalEmployeesEmployeeIdStatsGet;
export const useEmployeeHistory = useGetEmployeeHistoryApiV1OperacionalEmployeesEmployeeIdHistoryGet;
export const useEmployeeDocuments = useGetEmployeeDocumentsApiV1OperacionalEmployeesEmployeeIdDocumentsGet;

// Mutations
export const useCreateEmployee = useCreateEmployeeApiV1OperacionalEmployeesPost;
export const useUpdateEmployee = useUpdateEmployeeApiV1OperacionalEmployeesEmployeeIdPatch;
export const useDeleteEmployee = useDeleteEmployeeApiV1OperacionalEmployeesEmployeeIdDelete;

// Re-export types
export type {
  EmployeeCreate,
  EmployeeUpdate,
  EmployeeResponse,
  EmployeeStats,
  EmployeeHistory,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
