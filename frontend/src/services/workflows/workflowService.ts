/**
 * Workflow Service
 * Gestão de Workflows e Automações
 *
 * Serviço para gerenciamento completo de workflows:
 * - CRUD de workflows
 * - Ativação/Desativação
 * - Categorização e priorização
 * - Versionamento
 * - Métricas e analytics
 */

import { getAutomationWorkflows } from '@/types/generated/workflows/automation-workflows/automation-workflows';
import type {
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowResponse,
  WorkflowCategory,
  WorkflowStatus,
  ListWorkflowsApiV1WorkflowsGetParams,
} from '@/types/generated/workflows/conectaPROWorkflowsAPI.schemas';
import { AxiosResponse } from 'axios';

const workflowApi = getAutomationWorkflows();

/**
 * Service para gestão de workflows
 */
export class WorkflowService {
  /**
   * Lista workflows do tenant com filtros
   */
  static async listWorkflows(
    params: ListWorkflowsApiV1WorkflowsGetParams
  ): Promise<AxiosResponse<WorkflowResponse[]>> {
    return workflowApi.listWorkflowsApiV1WorkflowsGet(params);
  }

  /**
   * Cria novo workflow
   */
  static async createWorkflow(
    data: WorkflowCreate
  ): Promise<AxiosResponse<WorkflowResponse>> {
    return workflowApi.createWorkflowApiV1WorkflowsPost(data);
  }

  /**
   * Obtém workflow por ID
   */
  static async getWorkflow(
    workflowId: string
  ): Promise<AxiosResponse<WorkflowResponse>> {
    return workflowApi.getWorkflowApiV1WorkflowsWorkflowIdGet(workflowId);
  }

  /**
   * Atualiza workflow
   */
  static async updateWorkflow(
    workflowId: string,
    data: WorkflowUpdate
  ): Promise<AxiosResponse<WorkflowResponse>> {
    return workflowApi.updateWorkflowApiV1WorkflowsWorkflowIdPatch(
      workflowId,
      data
    );
  }

  /**
   * Remove workflow
   */
  static async deleteWorkflow(workflowId: string): Promise<AxiosResponse<void>> {
    return workflowApi.deleteWorkflowApiV1WorkflowsWorkflowIdDelete(workflowId);
  }

  /**
   * Ativa workflow
   */
  static async activateWorkflow(
    workflowId: string
  ): Promise<AxiosResponse<WorkflowResponse>> {
    return workflowApi.activateWorkflowApiV1WorkflowsWorkflowIdActivatePost(
      workflowId
    );
  }

  /**
   * Desativa workflow
   */
  static async deactivateWorkflow(
    workflowId: string
  ): Promise<AxiosResponse<WorkflowResponse>> {
    return workflowApi.deactivateWorkflowApiV1WorkflowsWorkflowIdDeactivatePost(
      workflowId
    );
  }

  // ==================== HELPERS ====================

  /**
   * Verifica se workflow está ativo
   */
  static isWorkflowActive(workflow: WorkflowResponse): boolean {
    return workflow.status === 'ACTIVE';
  }

  /**
   * Calcula taxa de sucesso
   */
  static getSuccessRate(workflow: WorkflowResponse): number {
    if (workflow.total_executions === 0) return 0;
    return (workflow.successful_executions / workflow.total_executions) * 100;
  }

  /**
   * Calcula taxa de falha
   */
  static getFailureRate(workflow: WorkflowResponse): number {
    if (workflow.total_executions === 0) return 0;
    return (workflow.failed_executions / workflow.total_executions) * 100;
  }

  /**
   * Formata categoria para exibição
   */
  static formatCategory(category: WorkflowCategory): string {
    const formats: Record<string, string> = {
      CRM: 'CRM',
      HR: 'Recursos Humanos',
      FINANCE: 'Financeiro',
      OPERATIONS: 'Operações',
      ONBOARDING: 'Onboarding',
      MARKETING: 'Marketing',
      SUPPORT: 'Suporte',
      COMMUNICATION: 'Comunicação',
      DOCUMENT: 'Documentos',
      INTEGRATION: 'Integração',
      MAINTENANCE: 'Manutenção',
      SECURITY: 'Segurança',
      ANALYTICS: 'Analytics',
      CUSTOM: 'Customizado',
    };
    return formats[category] || category;
  }

  /**
   * Formata status para exibição
   */
  static formatStatus(status: WorkflowStatus): string {
    const formats: Record<string, string> = {
      DRAFT: 'Rascunho',
      ACTIVE: 'Ativo',
      INACTIVE: 'Inativo',
      PAUSED: 'Pausado',
      ARCHIVED: 'Arquivado',
      ERROR: 'Erro',
    };
    return formats[status] || status;
  }

  /**
   * Obtém cor do status para UI
   */
  static getStatusColor(
    status: WorkflowStatus
  ): 'default' | 'success' | 'warning' | 'error' | 'info' {
    const colors: Record<
      string,
      'default' | 'success' | 'warning' | 'error' | 'info'
    > = {
      DRAFT: 'default',
      ACTIVE: 'success',
      INACTIVE: 'warning',
      PAUSED: 'info',
      ARCHIVED: 'default',
      ERROR: 'error',
    };
    return colors[status] || 'default';
  }

  /**
   * Obtém ícone do status
   */
  static getStatusIcon(status: WorkflowStatus): string {
    const icons: Record<string, string> = {
      DRAFT: 'FileText',
      ACTIVE: 'PlayCircle',
      INACTIVE: 'StopCircle',
      PAUSED: 'PauseCircle',
      ARCHIVED: 'Archive',
      ERROR: 'AlertCircle',
    };
    return icons[status] || 'HelpCircle';
  }

  /**
   * Valida dados de criação
   */
  static validateCreateData(data: WorkflowCreate): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!data.name || data.name.trim().length === 0) {
      errors.push('Nome é obrigatório');
    }

    if (data.name && data.name.length > 200) {
      errors.push('Nome deve ter no máximo 200 caracteres');
    }

    if (!data.tenant_id) {
      errors.push('Tenant ID é obrigatório');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Gera slug a partir do nome
   */
  static generateSlug(name: string): string {
    return name
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  /**
   * Filtra workflows por categoria
   */
  static filterByCategory(
    workflows: WorkflowResponse[],
    category: WorkflowCategory
  ): WorkflowResponse[] {
    return workflows.filter((w) => w.category === category);
  }

  /**
   * Filtra workflows por status
   */
  static filterByStatus(
    workflows: WorkflowResponse[],
    status: WorkflowStatus
  ): WorkflowResponse[] {
    return workflows.filter((w) => w.status === status);
  }

  /**
   * Ordena workflows por taxa de sucesso
   */
  static sortBySuccessRate(
    workflows: WorkflowResponse[],
    ascending = false
  ): WorkflowResponse[] {
    return [...workflows].sort((a, b) => {
      const rateA = this.getSuccessRate(a);
      const rateB = this.getSuccessRate(b);
      return ascending ? rateA - rateB : rateB - rateA;
    });
  }

  /**
   * Ordena workflows por total de execuções
   */
  static sortByExecutions(
    workflows: WorkflowResponse[],
    ascending = false
  ): WorkflowResponse[] {
    return [...workflows].sort((a, b) => {
      return ascending
        ? a.total_executions - b.total_executions
        : b.total_executions - a.total_executions;
    });
  }
}
