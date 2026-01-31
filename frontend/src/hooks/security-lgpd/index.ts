/**
 * Security LGPD Hooks
 * React Query hooks para módulo de Compliance LGPD
 *
 * Exporta todos os hooks customizados:
 * - Consent Management (5 hooks)
 * - Encryption (8 hooks)
 * - Audit (12 hooks)
 * - Data Erasure (5 hooks)
 * - PIA/DPIA (5 hooks)
 * - Masking (9 hooks)
 * - Status (4 hooks)
 *
 * Total: 48 hooks React Query
 */

// Consent Management Hooks
export {
  useRegisterConsent,
  useConsents,
  useRevokeConsent,
  usePurposes,
  useLegalBases,
  useActiveConsents,
  useExpiringConsents,
} from './useConsent';

// Encryption Hooks
export {
  useEncryptData,
  useDecryptData,
  useAlgorithms,
  useEncryptCPF,
  useEncryptEmail,
  useEncryptPhone,
  useEncryptBatch,
  useDecryptBatch,
} from './useEncryption';

// Audit Hooks
export {
  useCreateLGPDAuditLog,
  useLGPDAuditLogs,
  useAuditActions,
  useResourceTypes,
  useLogDataAccess,
  useLogDataModification,
  useLogDataDeletion,
  useLogDataExport,
  useLogSecurityIncident,
  useLogsByDateRange,
  useLogsByUser,
  useLogsByResource,
} from './useAudit';

// Data Erasure Hooks
export {
  useRequestErasure,
  useErasureStatus,
  useRequestFullErasure,
  useRequestPersonalDataErasure,
  useRequestTransactionalErasure,
} from './useErasure';

// PIA/DPIA Hooks
export {
  useCreatePIA,
  usePIA,
  useRiskCategories,
  useCreateSimplePIA,
  useCreateCompletePIA,
} from './usePIA';

// Masking Hooks
export {
  useMaskData,
  useMaskingFormats,
  useMaskCPF,
  useMaskEmail,
  useMaskPhone,
  useMaskName,
  useMaskAddress,
  useMaskCreditCard,
  useMaskBatch,
} from './useMasking';

// Status Hooks
export {
  useLGPDStatus,
  useHealthCheck,
  useIsHealthy,
  useComponentsStatus,
} from './useStatus';
