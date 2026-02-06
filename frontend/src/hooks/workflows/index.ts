/**
 * Workflows Hooks
 * Módulo de Workflows e Automações
 *
 * Exporta todos os hooks React Query do módulo workflows:
 * - Workflow hooks: Gestão de workflows (CRUD, ativação/desativação)
 * - Execution hooks: Gestão de execuções (listagem, cancelamento, monitoring)
 */

// Workflow Hooks
export {
  useWorkflowList,
  useWorkflow,
  useCreateWorkflow,
  useUpdateWorkflow,
  useDeleteWorkflow,
  useActivateWorkflow,
  useDeactivateWorkflow,
  useWorkflowsByCategory,
  useWorkflowsByStatus,
  useActiveWorkflows,
} from './useWorkflows';

// Execution Hooks
export {
  useExecutionList,
  useExecutionsByStatus,
  useRunningExecutions,
  useRecentExecutions,
  useCancelExecution,
  useExecutionStats,
  useExecutionMonitoring,
} from './useExecutions';

// Re-exporta tipos principais para conveniência
export type {
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowResponse,
  WorkflowCategory,
  WorkflowStatus,
  ExecutionResponse,
  ExecutionStatus,
  ListWorkflowsApiV1WorkflowsGetParams,
  ListExecutionsApiV1WorkflowsWorkflowIdExecutionsGetParams,
} from '@/types/generated/workflows/conectaPROWorkflowsAPI.schemas';
