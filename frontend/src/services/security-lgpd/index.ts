/**
 * Security LGPD Services
 * Módulo completo de Compliance LGPD - Lei 13.709/2018
 *
 * Exporta todos os services de segurança e proteção de dados:
 * - Gestão de Consentimentos (Art. 7, 8, 9)
 * - Criptografia de Dados Sensíveis
 * - Trilha de Auditoria (Art. 46)
 * - Direito ao Esquecimento (Art. 18)
 * - Avaliação de Impacto PIA/DPIA (Art. 38)
 * - Mascaramento de PII
 * - Status e Monitoring
 *
 * Total: 21 endpoints + helpers
 */

export { ConsentService, default as consentService } from './consentService';
export { EncryptionService, default as encryptionService } from './encryptionService';
export { AuditService, default as auditService } from './auditService';
export { ErasureService, default as erasureService } from './erasureService';
export { PIAService, default as piaService } from './piaService';
export { MaskingService, default as maskingService } from './maskingService';
export { StatusService, default as statusService } from './statusService';

/**
 * Re-export tipos gerados do Orval
 */
export type {
  ConsentRequest,
  RevokeConsentParams,
  EncryptDataRequest,
  DecryptDataRequest,
  EncryptDataRequestAlgorithm,
  AuditLogRequest,
  AuditLogRequestSeverity,
  ListAuditLogsParams,
  ErasureRequestSchema,
  ErasureRequestSchemaScope,
  PIARequest,
  MaskDataRequest,
  MaskDataRequestCategory,
  MaskDataRequestLevel,
  StandardResponse,
  ErrorResponse,
  HealthCheck200,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';
