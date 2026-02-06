/**
 * Service Layer - Scheduler Operations
 *
 * Operações administrativas do scheduler
 * - Executar ciclo manual
 * - Listar tarefas pendentes
 *
 * Sprint 35 - Task Scheduler
 * Uso restrito: ADMIN/SYSTEM apenas
 */

import { axiosInstance } from '@/lib/axios-instance';

const BASE_PATH = '/api/v1/scheduler';

export interface RunCycleResponse {
  status: string;
  message: string;
  [key: string]: unknown;
}

// ==================== Operações Admin ====================

/**
 * Executa ciclo do scheduler manualmente
 * Requer permissões admin/system
 */
export const runSchedulerCycle = async (): Promise<RunCycleResponse> => {
  const { data } = await axiosInstance.post<RunCycleResponse>(
    `${BASE_PATH}/scheduler/run-cycle`
  );
  return data;
};
