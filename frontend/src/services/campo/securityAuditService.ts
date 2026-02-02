/**
 * Service Layer - Security Audit (CAMPO)
 * Auditoria de segurança do sistema CAMPO
 */

import * as SecurityAuditAPI from '@/api/campo/generated/cyber/cyber';
import type {
  AuditRequest,
  ListAuditsApiV1CampoGuardianCyberSecurityAuditListGetParams,
} from '@/api/campo/generated/models';

export class SecurityAuditService {
  /**
   * Inicia nova auditoria de segurança
   */
  async iniciarAudit(data: AuditRequest) {
    return SecurityAuditAPI.startSecurityAuditApiV1CampoGuardianCyberSecurityAuditStartPost(data);
  }

  /**
   * Verifica status da auditoria
   */
  async verificarStatus(auditId: string) {
    return SecurityAuditAPI.getAuditStatusApiV1CampoGuardianCyberSecurityAuditStatusAuditIdGet(
      auditId
    );
  }

  /**
   * Lista todas as auditorias
   */
  async listarAudits(params?: ListAuditsApiV1CampoGuardianCyberSecurityAuditListGetParams) {
    return SecurityAuditAPI.listAuditsApiV1CampoGuardianCyberSecurityAuditListGet(params);
  }
}

export const securityAuditService = new SecurityAuditService();
