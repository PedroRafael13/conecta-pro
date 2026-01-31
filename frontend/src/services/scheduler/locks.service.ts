/**
 * Service Layer - Distributed Locks
 *
 * Gerenciamento de locks distribuídos
 * - Adquirir locks
 * - Liberar locks
 * - Renovar TTL
 * - Listar locks ativos
 *
 * Sprint 35 - Task Scheduler
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  LockCreate,
  LockResponse,
} from '@/types/generated/scheduler/models';

const BASE_PATH = '/api/v1/scheduler';

// ==================== Locks ====================

/**
 * Adquire lock distribuído
 */
export const acquireLock = async (lock: LockCreate): Promise<LockResponse> => {
  const { data } = await axiosInstance.post<LockResponse>(
    `${BASE_PATH}/locks`,
    lock
  );
  return data;
};

/**
 * Libera lock
 */
export const releaseLock = async (lockKey: string): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/locks/${lockKey}`);
};

/**
 * Renova TTL de lock existente
 */
export const renewLock = async (
  lockKey: string,
  ttlSeconds: number = 3600
): Promise<LockResponse> => {
  const { data } = await axiosInstance.post<LockResponse>(
    `${BASE_PATH}/locks/${lockKey}/renew`,
    null,
    { params: { ttl_seconds: ttlSeconds } }
  );
  return data;
};

/**
 * Lista locks ativos do tenant
 */
export const listLocks = async (): Promise<LockResponse[]> => {
  const { data } = await axiosInstance.get<LockResponse[]>(`${BASE_PATH}/locks`);
  return data;
};
