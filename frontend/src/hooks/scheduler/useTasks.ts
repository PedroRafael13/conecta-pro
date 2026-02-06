/**
 * Hooks React Query - Scheduler Tasks
 *
 * Gerenciamento de tarefas agendadas
 * - CRUD de tarefas
 * - Ativação/Pausa/Disparo
 * - Estatísticas
 *
 * Sprint 35 - Task Scheduler
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import {
  listTasks,
  createTask,
  getTask,
  updateTask,
  deleteTask,
  activateTask,
  pauseTask,
  triggerTask,
  getTaskStats,
  getDueTasks,
  type ListTasksParams,
} from '@/services/scheduler/tasks.service';
import type {
  TaskCreate,
  TaskUpdate,
  TaskResponse,
  TaskListResponse,
  TaskStatsResponse,
  TriggerTaskApiV1SchedulerTasksTaskIdTriggerPostBody,
  TriggerTaskResponse,
} from '@/types/generated/scheduler/models';

// Query Keys
export const taskKeys = {
  all: ['scheduler', 'tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (params?: ListTasksParams) => [...taskKeys.lists(), params] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (id: string) => [...taskKeys.details(), id] as const,
  stats: () => [...taskKeys.all, 'stats'] as const,
  due: () => [...taskKeys.all, 'due'] as const,
};

// ==================== Queries ====================

/**
 * Lista tarefas com filtros
 */
export function useTasks(
  params?: ListTasksParams
): UseQueryResult<TaskListResponse, Error> {
  return useQuery({
    queryKey: taskKeys.list(params),
    queryFn: () => listTasks(params),
    staleTime: 30000, // 30s
  });
}

/**
 * Busca tarefa por ID
 */
export function useTask(taskId: string): UseQueryResult<TaskResponse, Error> {
  return useQuery({
    queryKey: taskKeys.detail(taskId),
    queryFn: () => getTask(taskId),
    enabled: !!taskId,
    staleTime: 60000, // 1min
  });
}

/**
 * Estatísticas de tarefas
 */
export function useTaskStats(
  periodDays: number = 30
): UseQueryResult<TaskStatsResponse, Error> {
  return useQuery({
    queryKey: [...taskKeys.stats(), periodDays],
    queryFn: () => getTaskStats(periodDays),
    staleTime: 120000, // 2min
  });
}

/**
 * Tarefas que devem executar agora
 */
export function useDueTasks(
  limit: number = 100
): UseQueryResult<TaskResponse[], Error> {
  return useQuery({
    queryKey: [...taskKeys.due(), limit],
    queryFn: () => getDueTasks(limit),
    refetchInterval: 60000, // Auto-refresh 1min
  });
}

// ==================== Mutations ====================

/**
 * Cria nova tarefa
 */
export function useCreateTask(): UseMutationResult<TaskResponse, Error, TaskCreate> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });
}

/**
 * Atualiza tarefa
 */
export function useUpdateTask(): UseMutationResult<
  TaskResponse,
  Error,
  { taskId: string; updates: TaskUpdate }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, updates }) => updateTask(taskId, updates),
    onSuccess: (_, { taskId }) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
    },
  });
}

/**
 * Remove tarefa
 */
export function useDeleteTask(): UseMutationResult<
  void,
  Error,
  { taskId: string; hardDelete?: boolean }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, hardDelete }) => deleteTask(taskId, hardDelete),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });
}

/**
 * Ativa tarefa
 */
export function useActivateTask(): UseMutationResult<TaskResponse, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: activateTask,
    onSuccess: (_, taskId) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
    },
  });
}

/**
 * Pausa tarefa
 */
export function usePauseTask(): UseMutationResult<TaskResponse, Error, string> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: pauseTask,
    onSuccess: (_, taskId) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
    },
  });
}

/**
 * Dispara tarefa manualmente
 */
export function useTriggerTask(): UseMutationResult<
  TriggerTaskResponse,
  Error,
  { taskId: string; body?: TriggerTaskApiV1SchedulerTasksTaskIdTriggerPostBody }
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, body }) => triggerTask(taskId, body),
    onSuccess: (_, { taskId }) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
      queryClient.invalidateQueries({ queryKey: ['scheduler', 'executions'] });
    },
  });
}
