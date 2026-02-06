/**
 * Service Layer - Task Executions
 *
 * Gerenciamento de execuções de tarefas
 * - Histórico de execuções
 * - Logs detalhados
 * - Cancelamento de execuções
 *
 * Sprint 35 - Task Scheduler
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  ExecutionResponse,
  ExecutionLogResponse,
} from '@/types/generated/scheduler/models';

const BASE_PATH = '/api/v1/scheduler';

export interface ListExecutionsParams {
  task_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export interface GetExecutionLogsParams {
  level?: string;
  limit?: number;
}

// ==================== Execuções ====================

/**
 * Lista execuções com filtros
 */
export const listExecutions = async (
  params?: ListExecutionsParams
): Promise<ExecutionResponse[]> => {
  const { data } = await axiosInstance.get<ExecutionResponse[]>(
    `${BASE_PATH}/executions`,
    { params }
  );
  return data;
};

/**
 * Busca execução por ID
 */
export const getExecution = async (
  executionId: string
): Promise<ExecutionResponse> => {
  const { data } = await axiosInstance.get<ExecutionResponse>(
    `${BASE_PATH}/executions/${executionId}`
  );
  return data;
};

// ==================== Logs ====================

/**
 * Lista logs de uma execução
 */
export const getExecutionLogs = async (
  executionId: string,
  params?: GetExecutionLogsParams
): Promise<ExecutionLogResponse[]> => {
  const { data } = await axiosInstance.get<ExecutionLogResponse[]>(
    `${BASE_PATH}/executions/${executionId}/logs`,
    { params }
  );
  return data;
};

// ==================== Controle ====================

/**
 * Cancela execução pendente
 */
export const cancelExecution = async (
  executionId: string,
  reason: string = 'Cancelled by user'
): Promise<ExecutionResponse> => {
  const { data } = await axiosInstance.post<ExecutionResponse>(
    `${BASE_PATH}/executions/${executionId}/cancel`,
    null,
    { params: { reason } }
  );
  return data;
};
