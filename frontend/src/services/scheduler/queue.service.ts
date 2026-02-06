/**
 * Service Layer - Task Queue
 *
 * Gerenciamento de filas de execução
 * - Adicionar itens à fila
 * - Listar itens pendentes
 * - Estatísticas de fila
 * - Remover itens
 *
 * Sprint 35 - Task Scheduler
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  QueueItemCreate,
  QueueItemResponse,
  QueueStatsResponse,
} from '@/types/generated/scheduler/models';

const BASE_PATH = '/api/v1/scheduler';

export interface ListQueueItemsParams {
  queue_name?: string;
  status?: string;
  limit?: number;
}

// ==================== Fila ====================

/**
 * Adiciona item diretamente à fila
 */
export const enqueueItem = async (
  item: QueueItemCreate
): Promise<QueueItemResponse> => {
  const { data } = await axiosInstance.post<QueueItemResponse>(
    `${BASE_PATH}/queue`,
    item
  );
  return data;
};

/**
 * Lista itens da fila
 */
export const listQueueItems = async (
  params?: ListQueueItemsParams
): Promise<QueueItemResponse[]> => {
  const { data } = await axiosInstance.get<QueueItemResponse[]>(
    `${BASE_PATH}/queue`,
    { params }
  );
  return data;
};

/**
 * Remove item da fila
 */
export const deleteQueueItem = async (itemId: string): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/queue/${itemId}`);
};

// ==================== Estatísticas ====================

/**
 * Obtém estatísticas de uma fila
 */
export const getQueueStats = async (
  queueName: string = 'default'
): Promise<QueueStatsResponse> => {
  const { data } = await axiosInstance.get<QueueStatsResponse>(
    `${BASE_PATH}/queue/stats`,
    { params: { queue_name: queueName } }
  );
  return data;
};
