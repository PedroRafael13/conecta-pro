/**
 * Employees Hooks - Gestão de Funcionários Operacionais
 *
 * Re-exports dos hooks Orval do módulo operacional-funcionarios
 */

import { useMutation } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import {
  useListEmployeesApiV1OperacionalEmployeesGet,
  useListEmployeesFromSolidesApiV1OperacionalEmployeesSolidesGet,
} from '@/types/generated/operacional/operacional-funcionarios/operacional-funcionarios';
import type { EmployeeResponse } from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';

// List & Read
export const useEmployees = useListEmployeesApiV1OperacionalEmployeesGet;
export const useEmployeesFromSolides = useListEmployeesFromSolidesApiV1OperacionalEmployeesSolidesGet;

// Mutation manual (endpoint não gerado pelo Orval)
export const useUpdateEmployee = () => {
  return useMutation({
    mutationFn: async ({ employeeId, data }: { employeeId: string; data: Record<string, unknown> }) => {
      return customInstance<EmployeeResponse>({
        url: `/api/v1/operacional/employees/${employeeId}`,
        method: 'PATCH',
        data,
      });
    },
  });
};

// Re-export types
export type {
  EmployeeResponse,
  EmployeeListResponse,
} from '@/types/generated/operacional/conectaPROMóduloOPERACIONAL.schemas';
