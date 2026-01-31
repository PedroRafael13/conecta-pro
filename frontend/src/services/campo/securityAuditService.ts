/**
 * Service Layer - Security Audit (CAMPO)
 * Auditoria de segurança do sistema CAMPO
 */

import * as SecurityAuditAPI from '@/api/campo/generated/security-audit/security-audit';
import type {
  AuditRequest,
  ListAuditsApiV1CampoSecurityAuditSecurityAuditListGetParams,
} from '@/api/campo/generated/models';

export class SecurityAuditService {
  /**
   * Inicia nova auditoria de segurança
   */
  async iniciarAudit(data: AuditRequest) {
    return SecurityAuditAPI.startSecurityAuditApiV1CampoSecurityAuditSecurityAuditStartPost(data);
  }

  /**
   * Verifica status da auditoria
   */
  async verificarStatus(auditId: string) {
    return SecurityAuditAPI.getAuditStatusApiV1CampoSecurityAuditSecurityAuditStatusAuditIdGet(
      auditId
    );
  }

  /**
   * Lista todas as auditorias
   */
  async listarAudits(params?: ListAuditsApiV1CampoSecurityAuditSecurityAuditListGetParams) {
    return SecurityAuditAPI.listAuditsApiV1CampoSecurityAuditSecurityAuditListGet(params);
  }
}

export const securityAuditService = new SecurityAuditService();
