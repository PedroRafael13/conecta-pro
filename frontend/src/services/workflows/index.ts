/**
 * Workflows Services
 * Módulo de Workflows e Automações
 *
 * Exporta todos os services do módulo workflows:
 * - WorkflowService: Gestão de workflows (CRUD, ativação, métricas)
 * - ExecutionService: Gestão de execuções (listagem, cancelamento, stats)
 */

export { WorkflowService } from './workflowService';
export { ExecutionService } from './executionService';

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
