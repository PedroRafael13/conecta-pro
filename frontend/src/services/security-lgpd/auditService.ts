/**
 * Audit Service
 * Trilha de Auditoria LGPD (Art. 46)
 *
 * Serviço para registro e consulta de eventos de auditoria:
 * - Registro de eventos com hash chain
 * - Consulta de logs com filtros
 * - Listagem de ações e tipos de recurso
 * - Severidade e rastreabilidade
 */

import { getLgpdAuditoria } from '@/types/generated/security-lgpd/lgpd-auditoria/lgpd-auditoria';
import type {
  AuditLogRequest,
  ListAuditLogsParams,
  AuditLogRequestSeverity,
  StandardResponse,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';
import { AxiosResponse } from 'axios';

const auditApi = getLgpdAuditoria();

/**
 * Service para trilha de auditoria LGPD
 */
export class AuditService {
  /**
   * Registra evento na trilha de auditoria
   * Cria hash chain para garantir integridade
   */
  static async createAuditLog(
    request: AuditLogRequest
  ): Promise<AxiosResponse<StandardResponse>> {
    return auditApi.createAuditLog(request);
  }

  /**
   * Lista eventos de auditoria com filtros
   */
  static async listAuditLogs(
    params?: ListAuditLogsParams
  ): Promise<AxiosResponse<StandardResponse>> {
    return auditApi.listAuditLogs(params);
  }

  /**
   * Lista ações de auditoria disponíveis
   */
  static async listActions(): Promise<AxiosResponse<StandardResponse>> {
    return auditApi.listActions();
  }

  /**
   * Lista tipos de recurso auditados
   */
  static async listResourceTypes(): Promise<AxiosResponse<StandardResponse>> {
    return auditApi.listResourceTypes();
  }

  /**
   * Registra acesso a dados pessoais
   * Helper específico para acesso a dados
   */
  static async logDataAccess(
    userId: string,
    resourceType: string,
    resourceId: string,
    details?: Record<string, unknown>
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.createAuditLog({
      action: 'ACCESS',
      resource_type: resourceType,
      resource_id: resourceId,
      user_id: userId,
      details,
      severity: 'low',
    });
  }

  /**
   * Registra modificação de dados
   */
  static async logDataModification(
    userId: string,
    resourceType: string,
    resourceId: string,
    changes: Record<string, unknown>
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.createAuditLog({
      action: 'UPDATE',
      resource_type: resourceType,
      resource_id: resourceId,
      user_id: userId,
      details: { changes },
      severity: 'medium',
    });
  }

  /**
   * Registra exclusão de dados
   */
  static async logDataDeletion(
    userId: string,
    resourceType: string,
    resourceId: string,
    reason: string
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.createAuditLog({
      action: 'DELETE',
      resource_type: resourceType,
      resource_id: resourceId,
      user_id: userId,
      details: { reason },
      severity: 'high',
    });
  }

  /**
   * Registra exportação de dados
   */
  static async logDataExport(
    userId: string,
    dataScope: string,
    recordCount: number
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.createAuditLog({
      action: 'EXPORT',
      resource_type: 'personal_data',
      resource_id: dataScope,
      user_id: userId,
      details: { record_count: recordCount },
      severity: 'medium',
    });
  }

  /**
   * Registra incidente de segurança
   */
  static async logSecurityIncident(
    userId: string,
    incidentType: string,
    description: string,
    severity: AuditLogRequestSeverity = 'critical'
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.createAuditLog({
      action: 'SECURITY_INCIDENT',
      resource_type: 'security',
      resource_id: incidentType,
      user_id: userId,
      details: { description, timestamp: new Date().toISOString() },
      severity,
    });
  }

  /**
   * Busca logs por período
   */
  static async getLogsByDateRange(
    startDate: Date,
    endDate: Date,
    limit: number = 100
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.listAuditLogs({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      limit,
    });
  }

  /**
   * Busca logs por usuário
   */
  static async getLogsByUser(
    userId: string,
    limit: number = 100
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.listAuditLogs({
      user_id: userId,
      limit,
    });
  }

  /**
   * Busca logs por recurso
   */
  static async getLogsByResource(
    resourceType: string,
    limit: number = 100
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.listAuditLogs({
      resource_type: resourceType,
      limit,
    });
  }

  /**
   * Formata severidade para exibição
   */
  static formatSeverity(severity: AuditLogRequestSeverity): string {
    const formats: Record<AuditLogRequestSeverity, string> = {
      low: 'Baixa',
      medium: 'Média',
      high: 'Alta',
      critical: 'Crítica',
    };
    return formats[severity];
  }

  /**
   * Retorna cor do badge de severidade
   */
  static getSeverityColor(severity: AuditLogRequestSeverity): string {
    const colors: Record<AuditLogRequestSeverity, string> = {
      low: 'green',
      medium: 'yellow',
      high: 'orange',
      critical: 'red',
    };
    return colors[severity];
  }

  /**
   * Formata ação para exibição
   */
  static formatAction(action: string): string {
    const formats: Record<string, string> = {
      ACCESS: 'Acesso',
      CREATE: 'Criação',
      UPDATE: 'Atualização',
      DELETE: 'Exclusão',
      EXPORT: 'Exportação',
      IMPORT: 'Importação',
      LOGIN: 'Login',
      LOGOUT: 'Logout',
      SECURITY_INCIDENT: 'Incidente de Segurança',
      CONSENT_GRANTED: 'Consentimento Concedido',
      CONSENT_REVOKED: 'Consentimento Revogado',
      DATA_ERASURE: 'Exclusão de Dados',
    };
    return formats[action] || action;
  }

  /**
   * Calcula estatísticas de auditoria
   */
  static calculateStats(logs: any[]): {
    total: number;
    bySeverity: Record<AuditLogRequestSeverity, number>;
    byAction: Record<string, number>;
  } {
    const stats = {
      total: logs.length,
      bySeverity: {
        low: 0,
        medium: 0,
        high: 0,
        critical: 0,
      } as Record<AuditLogRequestSeverity, number>,
      byAction: {} as Record<string, number>,
    };

    logs.forEach((log) => {
      if (log.severity) {
        stats.bySeverity[log.severity as AuditLogRequestSeverity]++;
      }
      if (log.action) {
        stats.byAction[log.action] = (stats.byAction[log.action] || 0) + 1;
      }
    });

    return stats;
  }
}

export default AuditService;
