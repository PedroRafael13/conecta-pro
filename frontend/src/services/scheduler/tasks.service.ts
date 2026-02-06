/**
 * Service Layer - Scheduler Tasks
 *
 * Gerenciamento de tarefas agendadas (cron, interval, one-time)
 * - CRUD de tarefas
 * - Ativação/Pausa/Disparo manual
 * - Estatísticas e métricas
 *
 * Sprint 35 - Task Scheduler
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  TaskCreate,
  TaskUpdate,
  TaskResponse,
  TaskListResponse,
  TaskStatsResponse,
  TriggerTaskApiV1SchedulerTasksTaskIdTriggerPostBody,
  TriggerTaskResponse,
} from '@/types/generated/scheduler/models';

const BASE_PATH = '/api/v1/scheduler';

export interface ListTasksParams {
  status?: string;
  category?: string;
  task_type?: string;
  queue_name?: string;
  tags?: string; // Separadas por vírgula
  search?: string;
  page?: number;
  page_size?: number;
}

// ==================== CRUD ====================

/**
 * Lista tarefas agendadas com filtros
 */
export const listTasks = async (
  params?: ListTasksParams
): Promise<TaskListResponse> => {
  const { data } = await axiosInstance.get<TaskListResponse>(
    `${BASE_PATH}/tasks`,
    { params }
  );
  return data;
};

/**
 * Cria nova tarefa agendada
 */
export const createTask = async (task: TaskCreate): Promise<TaskResponse> => {
  const { data } = await axiosInstance.post<TaskResponse>(
    `${BASE_PATH}/tasks`,
    task
  );
  return data;
};

/**
 * Busca tarefa por ID
 */
export const getTask = async (taskId: string): Promise<TaskResponse> => {
  const { data } = await axiosInstance.get<TaskResponse>(
    `${BASE_PATH}/tasks/${taskId}`
  );
  return data;
};

/**
 * Atualiza tarefa existente
 */
export const updateTask = async (
  taskId: string,
  updates: TaskUpdate
): Promise<TaskResponse> => {
  const { data } = await axiosInstance.patch<TaskResponse>(
    `${BASE_PATH}/tasks/${taskId}`,
    updates
  );
  return data;
};

/**
 * Remove tarefa
 */
export const deleteTask = async (
  taskId: string,
  hardDelete: boolean = false
): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/tasks/${taskId}`, {
    params: { hard_delete: hardDelete },
  });
};

// ==================== Controle de Execução ====================

/**
 * Ativa tarefa pausada
 */
export const activateTask = async (taskId: string): Promise<TaskResponse> => {
  const { data } = await axiosInstance.post<TaskResponse>(
    `${BASE_PATH}/tasks/${taskId}/activate`
  );
  return data;
};

/**
 * Pausa tarefa ativa
 */
export const pauseTask = async (taskId: string): Promise<TaskResponse> => {
  const { data } = await axiosInstance.post<TaskResponse>(
    `${BASE_PATH}/tasks/${taskId}/pause`
  );
  return data;
};

/**
 * Dispara tarefa manualmente
 */
export const triggerTask = async (
  taskId: string,
  body?: TriggerTaskApiV1SchedulerTasksTaskIdTriggerPostBody
): Promise<TriggerTaskResponse> => {
  const { data } = await axiosInstance.post<TriggerTaskResponse>(
    `${BASE_PATH}/tasks/${taskId}/trigger`,
    body
  );
  return data;
};

// ==================== Estatísticas ====================

/**
 * Obtém estatísticas de tarefas
 */
export const getTaskStats = async (
  periodDays: number = 30
): Promise<TaskStatsResponse> => {
  const { data } = await axiosInstance.get<TaskStatsResponse>(
    `${BASE_PATH}/tasks/stats/summary`,
    { params: { period_days: periodDays } }
  );
  return data;
};

// ==================== Operações Admin ====================

/**
 * Lista tarefas que devem executar agora
 */
export const getDueTasks = async (limit: number = 100): Promise<TaskResponse[]> => {
  const { data } = await axiosInstance.get<TaskResponse[]>(
    `${BASE_PATH}/scheduler/due-tasks`,
    { params: { limit } }
  );
  return data;
};
