/**
 * Service Layer - Task Workers
 *
 * Gerenciamento de workers de processamento
 * - Listar workers ativos
 * - Monitorar status e utilização
 * - Estatísticas de performance
 *
 * Sprint 35 - Task Scheduler
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  WorkerResponse,
  WorkerStatsResponse,
} from '@/types/generated/scheduler/models';

const BASE_PATH = '/api/v1/scheduler';

export interface ListWorkersParams {
  status?: string;
  queue_name?: string;
}

// ==================== Workers ====================

/**
 * Lista workers registrados
 */
export const listWorkers = async (
  params?: ListWorkersParams
): Promise<WorkerResponse[]> => {
  const { data } = await axiosInstance.get<WorkerResponse[]>(
    `${BASE_PATH}/workers`,
    { params }
  );
  return data;
};

/**
 * Busca worker por ID
 */
export const getWorker = async (workerId: string): Promise<WorkerResponse> => {
  const { data } = await axiosInstance.get<WorkerResponse>(
    `${BASE_PATH}/workers/${workerId}`
  );
  return data;
};

// ==================== Estatísticas ====================

/**
 * Obtém estatísticas consolidadas de workers
 */
export const getWorkerStats = async (): Promise<WorkerStatsResponse> => {
  const { data } = await axiosInstance.get<WorkerStatsResponse>(
    `${BASE_PATH}/workers/stats/summary`
  );
  return data;
};
