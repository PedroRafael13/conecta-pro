/**
 * Workflow Hooks
 * React Query hooks para gestão de workflows
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions,
} from '@tanstack/react-query';
import { WorkflowService } from '@/services/workflows/workflowService';
import type {
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowResponse,
  WorkflowCategory,
  WorkflowStatus,
  ListWorkflowsApiV1WorkflowsGetParams,
} from '@/types/generated/workflows/conectaPROWorkflowsAPI.schemas';
import { AxiosResponse } from 'axios';

const WORKFLOW_KEYS = {
  all: ['workflows'] as const,
  lists: () => [...WORKFLOW_KEYS.all, 'list'] as const,
  list: (params?: ListWorkflowsApiV1WorkflowsGetParams) =>
    [...WORKFLOW_KEYS.lists(), params] as const,
  detail: (id: string) => [...WORKFLOW_KEYS.all, 'detail', id] as const,
  byCategory: (category: WorkflowCategory) =>
    [...WORKFLOW_KEYS.all, 'by-category', category] as const,
  byStatus: (status: WorkflowStatus) =>
    [...WORKFLOW_KEYS.all, 'by-status', status] as const,
  active: () => [...WORKFLOW_KEYS.all, 'active'] as const,
};

/**
 * Hook para listar workflows
 */
export const useWorkflowList = (
  params: ListWorkflowsApiV1WorkflowsGetParams,
  options?: Omit<
    UseQueryOptions<AxiosResponse<WorkflowResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: WORKFLOW_KEYS.list(params),
    queryFn: () => WorkflowService.listWorkflows(params),
    ...options,
  });
};

/**
 * Hook para obter workflow por ID
 */
export const useWorkflow = (
  workflowId: string,
  options?: Omit<
    UseQueryOptions<AxiosResponse<WorkflowResponse>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: WORKFLOW_KEYS.detail(workflowId),
    queryFn: () => WorkflowService.getWorkflow(workflowId),
    enabled: !!workflowId,
    ...options,
  });
};

/**
 * Hook para criar workflow
 */
export const useCreateWorkflow = (
  options?: UseMutationOptions<
    AxiosResponse<WorkflowResponse>,
    Error,
    WorkflowCreate
  >
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WorkflowCreate) => WorkflowService.createWorkflow(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WORKFLOW_KEYS.lists() });
    },
    ...options,
  });
};

/**
 * Hook para atualizar workflow
 */
export const useUpdateWorkflow = (
  options?: UseMutationOptions<
    AxiosResponse<WorkflowResponse>,
    Error,
    { workflowId: string; data: WorkflowUpdate }
  >
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ workflowId, data }) =>
      WorkflowService.updateWorkflow(workflowId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: WORKFLOW_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: WORKFLOW_KEYS.detail(variables.workflowId),
      });
    },
    ...options,
  });
};

/**
 * Hook para deletar workflow
 */
export const useDeleteWorkflow = (
  options?: UseMutationOptions<AxiosResponse<void>, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (workflowId: string) =>
      WorkflowService.deleteWorkflow(workflowId),
    onSuccess: (_, workflowId) => {
      queryClient.invalidateQueries({ queryKey: WORKFLOW_KEYS.lists() });
      queryClient.removeQueries({ queryKey: WORKFLOW_KEYS.detail(workflowId) });
    },
    ...options,
  });
};

/**
 * Hook para ativar workflow
 */
export const useActivateWorkflow = (
  options?: UseMutationOptions<AxiosResponse<WorkflowResponse>, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (workflowId: string) =>
      WorkflowService.activateWorkflow(workflowId),
    onSuccess: (_, workflowId) => {
      queryClient.invalidateQueries({ queryKey: WORKFLOW_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: WORKFLOW_KEYS.detail(workflowId),
      });
      queryClient.invalidateQueries({ queryKey: WORKFLOW_KEYS.active() });
    },
    ...options,
  });
};

/**
 * Hook para desativar workflow
 */
export const useDeactivateWorkflow = (
  options?: UseMutationOptions<AxiosResponse<WorkflowResponse>, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (workflowId: string) =>
      WorkflowService.deactivateWorkflow(workflowId),
    onSuccess: (_, workflowId) => {
      queryClient.invalidateQueries({ queryKey: WORKFLOW_KEYS.lists() });
      queryClient.invalidateQueries({
        queryKey: WORKFLOW_KEYS.detail(workflowId),
      });
      queryClient.invalidateQueries({ queryKey: WORKFLOW_KEYS.active() });
    },
    ...options,
  });
};

/**
 * Hook para listar workflows por categoria
 */
export const useWorkflowsByCategory = (
  tenantId: string,
  category: WorkflowCategory,
  options?: Omit<
    UseQueryOptions<AxiosResponse<WorkflowResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: WORKFLOW_KEYS.byCategory(category),
    queryFn: () =>
      WorkflowService.listWorkflows({
        tenant_id: tenantId,
        category,
      }),
    enabled: !!tenantId,
    ...options,
  });
};

/**
 * Hook para listar workflows por status
 */
export const useWorkflowsByStatus = (
  tenantId: string,
  status: WorkflowStatus,
  options?: Omit<
    UseQueryOptions<AxiosResponse<WorkflowResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: WORKFLOW_KEYS.byStatus(status),
    queryFn: () =>
      WorkflowService.listWorkflows({
        tenant_id: tenantId,
        status,
      }),
    enabled: !!tenantId,
    ...options,
  });
};

/**
 * Hook para listar workflows ativos
 */
export const useActiveWorkflows = (
  tenantId: string,
  options?: Omit<
    UseQueryOptions<AxiosResponse<WorkflowResponse[]>>,
    'queryKey' | 'queryFn'
  >
) => {
  return useQuery({
    queryKey: WORKFLOW_KEYS.active(),
    queryFn: () =>
      WorkflowService.listWorkflows({
        tenant_id: tenantId,
        status: 'ACTIVE',
      }),
    enabled: !!tenantId,
    ...options,
  });
};
