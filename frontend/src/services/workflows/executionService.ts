/**
 * Execution Service
 * Gestão de Execuções de Workflows
 *
 * Serviço para gerenciamento de execuções:
 * - Listagem de execuções
 * - Cancelamento de execuções
 * - Status e métricas
 * - Histórico de execução
 */

import {
  listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet,
  cancelExecutionApiV1WorkflowsExecutionsExecutionIdCancelPost,
} from '@/types/generated/workflows/automation-workflows/automation-workflows';
import type {
  ExecutionResponse,
  ExecutionStatus,
  ListExecutionsApiV1WorkflowsWorkflowIdExecutionsGetParams,
} from '@/types/generated/workflows/conectaPROWorkflowsAPI.schemas';

/**
 * Service para gestão de execuções de workflows
 */
export class ExecutionService {
  /**
   * Lista execuções de um workflow
   */
  static async listExecutions(
    workflowId: string,
    params?: ListExecutionsApiV1WorkflowsWorkflowIdExecutionsGetParams
  ): Promise<Awaited<ReturnType<typeof listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet>>> {
    return listExecutionsApiV1WorkflowsWorkflowIdExecutionsGet(workflowId, params);
  }

  /**
   * Cancela uma execução
   */
  static async cancelExecution(
    executionId: string
  ): Promise<Awaited<ReturnType<typeof cancelExecutionApiV1WorkflowsExecutionsExecutionIdCancelPost>>> {
    return cancelExecutionApiV1WorkflowsExecutionsExecutionIdCancelPost(executionId);
  }

  // ==================== HELPERS ====================

  /**
   * Verifica se execução está em andamento
   */
  static isExecutionRunning(execution: ExecutionResponse): boolean {
    return ['PENDING', 'QUEUED', 'RUNNING', 'WAITING', 'RETRYING'].includes(
      execution.status
    );
  }

  /**
   * Verifica se execução foi concluída
   */
  static isExecutionCompleted(execution: ExecutionResponse): boolean {
    return execution.status === 'COMPLETED';
  }

  /**
   * Verifica se execução falhou
   */
  static isExecutionFailed(execution: ExecutionResponse): boolean {
    return execution.status === 'FAILED';
  }

  /**
   * Verifica se execução foi cancelada
   */
  static isExecutionCancelled(execution: ExecutionResponse): boolean {
    return execution.status === 'CANCELLED';
  }

  /**
   * Verifica se execução pode ser cancelada
   */
  static canCancelExecution(execution: ExecutionResponse): boolean {
    return ['PENDING', 'QUEUED', 'RUNNING'].includes(execution.status);
  }

  /**
   * Calcula progresso da execução (%)
   */
  static getExecutionProgress(execution: ExecutionResponse): number {
    if (execution.steps_total === 0) return 0;
    return (execution.steps_completed / execution.steps_total) * 100;
  }

  /**
   * Formata status para exibição
   */
  static formatStatus(status: ExecutionStatus): string {
    const formats: Record<string, string> = {
      PENDING: 'Pendente',
      QUEUED: 'Na Fila',
      RUNNING: 'Em Execução',
      PAUSED: 'Pausado',
      WAITING: 'Aguardando',
      RETRYING: 'Tentando Novamente',
      COMPLETED: 'Concluído',
      FAILED: 'Falhou',
      CANCELLED: 'Cancelado',
      TIMEOUT: 'Tempo Esgotado',
    };
    return formats[status] || status;
  }

  /**
   * Obtém cor do status para UI
   */
  static getStatusColor(
    status: ExecutionStatus
  ): 'default' | 'success' | 'warning' | 'error' | 'info' {
    const colors: Record<
      string,
      'default' | 'success' | 'warning' | 'error' | 'info'
    > = {
      PENDING: 'default',
      QUEUED: 'info',
      RUNNING: 'info',
      PAUSED: 'warning',
      WAITING: 'warning',
      RETRYING: 'warning',
      COMPLETED: 'success',
      FAILED: 'error',
      CANCELLED: 'default',
      TIMEOUT: 'error',
    };
    return colors[status] || 'default';
  }

  /**
   * Obtém ícone do status
   */
  static getStatusIcon(status: ExecutionStatus): string {
    const icons: Record<string, string> = {
      PENDING: 'Clock',
      QUEUED: 'List',
      RUNNING: 'Play',
      PAUSED: 'Pause',
      WAITING: 'Timer',
      RETRYING: 'RotateCw',
      COMPLETED: 'CheckCircle',
      FAILED: 'XCircle',
      CANCELLED: 'StopCircle',
      TIMEOUT: 'AlertTriangle',
    };
    return icons[status] || 'HelpCircle';
  }

  /**
   * Formata tempo de execução
   */
  static formatExecutionTime(ms: number | null): string {
    if (ms === null) return 'N/A';

    if (ms < 1000) {
      return `${ms}ms`;
    }

    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) {
      return `${seconds}s`;
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes < 60) {
      return remainingSeconds > 0
        ? `${minutes}m ${remainingSeconds}s`
        : `${minutes}m`;
    }

    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0
      ? `${hours}h ${remainingMinutes}m`
      : `${hours}h`;
  }

  /**
   * Filtra execuções por status
   */
  static filterByStatus(
    executions: ExecutionResponse[],
    status: ExecutionStatus
  ): ExecutionResponse[] {
    return executions.filter((e) => e.status === status);
  }

  /**
   * Filtra execuções bem-sucedidas
   */
  static filterSuccessful(
    executions: ExecutionResponse[]
  ): ExecutionResponse[] {
    return executions.filter((e) => e.success === true);
  }

  /**
   * Filtra execuções com falha
   */
  static filterFailed(executions: ExecutionResponse[]): ExecutionResponse[] {
    return executions.filter((e) => e.success === false);
  }

  /**
   * Ordena execuções por tempo de execução
   */
  static sortByExecutionTime(
    executions: ExecutionResponse[],
    ascending = false
  ): ExecutionResponse[] {
    return [...executions].sort((a, b) => {
      const timeA = a.execution_time_ms || 0;
      const timeB = b.execution_time_ms || 0;
      return ascending ? timeA - timeB : timeB - timeA;
    });
  }

  /**
   * Agrupa execuções por status
   */
  static groupByStatus(
    executions: ExecutionResponse[]
  ): Record<ExecutionStatus, ExecutionResponse[]> {
    const grouped: any = {};

    executions.forEach((execution) => {
      if (!grouped[execution.status]) {
        grouped[execution.status] = [];
      }
      grouped[execution.status].push(execution);
    });

    return grouped;
  }

  /**
   * Calcula estatísticas de execuções
   */
  static getExecutionStats(executions: ExecutionResponse[]): {
    total: number;
    successful: number;
    failed: number;
    running: number;
    cancelled: number;
    successRate: number;
    failureRate: number;
    avgExecutionTime: number;
  } {
    const total = executions.length;
    const successful = executions.filter((e) => e.success).length;
    const failed = executions.filter(
      (e) => !e.success && e.status === 'FAILED'
    ).length;
    const running = executions.filter((e) => this.isExecutionRunning(e)).length;
    const cancelled = executions.filter(
      (e) => e.status === 'CANCELLED'
    ).length;

    const successRate = total > 0 ? (successful / total) * 100 : 0;
    const failureRate = total > 0 ? (failed / total) * 100 : 0;

    const executionTimes = executions
      .filter((e) => e.execution_time_ms !== null)
      .map((e) => e.execution_time_ms!);

    const avgExecutionTime =
      executionTimes.length > 0
        ? executionTimes.reduce((a, b) => a + b, 0) / executionTimes.length
        : 0;

    return {
      total,
      successful,
      failed,
      running,
      cancelled,
      successRate,
      failureRate,
      avgExecutionTime,
    };
  }
}
