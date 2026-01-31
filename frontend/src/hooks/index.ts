/**
 * Hooks Centralizados - Conecta Plus
 *
 * Barrel export de todos os hooks do sistema.
 * Organizado por categoria para facilitar importações.
 *
 * @example
 * import { useAuth, usePosts, useAutoSave } from '@/hooks';
 */

// ============================================================================
// AUTENTICAÇÃO E AUTORIZAÇÃO
// ============================================================================

export { useAuth } from './useAuth';
export { usePermission } from './usePermission';

// ============================================================================
// MÓDULO OPERACIONAL - GESTÃO DE OPERAÇÕES
// ============================================================================

/**
 * Postos de Trabalho
 * Hook para gerenciar postos, incluindo listagem, CRUD e estatísticas
 */
export { usePosts, usePost, usePostStats } from './usePosts';

/**
 * Escalas
 * Hooks para gerenciamento de escalas de trabalho
 */
export {
  useScales,
  useScale,
  useScaleStats,
  useScaleOperations,
  useCurrentMonthScales
} from './useScales';

/**
 * Templates de Escala
 * Hooks para templates reutilizáveis de escalas
 */
export {
  useTemplates,
  useTemplate,
  useTemplateOperations
} from './useScaleTemplates';

/**
 * Alocações
 * Gestão de alocação de colaboradores em postos
 */
export { useAllocations } from './useAllocations';

/**
 * Colaboradores
 * Gerenciamento de colaboradores do operacional
 */
export { useEmployees } from './useEmployees';

/**
 * Turnos
 * Gestão de turnos de trabalho
 */
export {
  useShifts,
  useTodayShifts,
  useShiftOperations
} from './useShifts';

/**
 * Rondas de Patrulha
 * Gerenciamento de rondas e check-points
 */
export {
  usePatrolRounds,
  usePatrolRoundStats,
  usePatrolRoundDetail,
  usePatrolRoundMutations
} from './usePatrolRounds';

/**
 * Ocorrências
 * Registro e gestão de ocorrências operacionais
 */
export {
  useOccurrences,
  useOccurrenceStats,
  useOccurrenceDetail,
  usePostOccurrences,
  useOccurrenceMutations
} from './useOccurrences';

/**
 * Processos Disciplinares
 * Gestão de processos disciplinares de colaboradores
 */
export {
  useDisciplinary,
  useDisciplinaryStats,
  useDisciplinaryDetail,
  usePendingApprovals as usePendingDisciplinaryApprovals,
  useEmployeeDisciplinary
} from './useDisciplinary';

/**
 * Comunicados
 * Gestão de comunicados internos
 */
export {
  useAnnouncements,
  useUnreadAnnouncements,
  useAnnouncementDetail,
  useAnnouncementReadStats,
  useAnnouncementMutations
} from './useAnnouncements';

/**
 * Notificações e Alertas Operacionais
 * Gestão de notificações e alertas em tempo real
 */
export {
  useNotifications as useOperationalNotifications,
  useUnreadCount,
  useAlerts,
  useUserAlerts
} from './useNotifications';

/**
 * Reembolsos
 * Gerenciamento de solicitações de reembolso
 */
export {
  useReimbursements,
  useReimbursementStats,
  useReimbursementDetail,
  usePendingApprovals as usePendingReimbursementApprovals,
  useReimbursementCategories,
  useReadyForPayment
} from './useReimbursement';

/**
 * Fiscal de Diaristas
 * Cálculo de retenções, RPA, documentos fiscais
 */
export { diaristFiscalService } from '@/lib/services/diarist-fiscal';
export type {
  RetencoesResponse,
  DocumentoFiscal,
  RelatorioRetencoesResponse,
  RelatorioDiaristaResponse,
  TabelaINSS,
  TabelaIRRF,
} from '@/lib/services/diarist-fiscal';

// ============================================================================
// MÓDULO CRM - GESTÃO DE LEADS
// ============================================================================

/**
 * Leads
 * Gerenciamento de leads e pipeline de vendas
 */
export {
  useLeads,
  useLead,
  useCreateLead,
  useUpdateLead,
  useDeleteLead,
  useLeadsStats
} from './useLeads';

// ============================================================================
// DASHBOARD E ANALYTICS
// ============================================================================

/**
 * Dashboard
 * Dados consolidados do dashboard principal
 */
export {
  useDashboardStats,
  useRecentActivities,
  useHealthCheck
} from './useDashboard';
// Nota: useNotifications do useDashboard conflita com o de notifications
// Use o de @/features/notifications para notificações push

/**
 * KPI Trends
 * Tendências de KPIs ao longo do tempo
 */
export { useKPITrends } from './useKPITrends';

// ============================================================================
// PRODUTIVIDADE E UX
// ============================================================================

/**
 * Auto-save
 * Salvamento automático de formulários com localStorage
 * Previne perda de dados em formulários longos
 */
export {
  useAutoSave,
  cleanupExpiredDrafts
} from './useAutoSave';
export type { UseAutoSaveOptions, UseAutoSaveReturn } from './useAutoSave';

/**
 * Keyboard Shortcuts
 * Atalhos de teclado globais e contextuais
 */
export {
  useKeyboardShortcuts,
  useGlobalShortcuts
} from './useKeyboardShortcuts';
export type { KeyboardShortcut } from './useKeyboardShortcuts';

// ============================================================================
// MÓDULO RECRUITMENT - RECRUTAMENTO E SELEÇÃO
// ============================================================================

/**
 * Recruitment - Recrutamento e Seleção
 * Hooks para gerenciamento de vagas, candidatos, candidaturas e entrevistas
 */
export * from './useRecruitment';

// ============================================================================
// MÓDULO AUDIT - AUDITORIA E COMPLIANCE
// ============================================================================

/**
 * Audit - Auditoria e Compliance
 * Hooks para logs de auditoria, regras de compliance e retenção de dados
 */
export * from './audit';

// ============================================================================
// MÓDULO CONFIG - CONFIGURAÇÕES DO SISTEMA
// ============================================================================

/**
 * Config - Configurações do Sistema
 * Hooks para tenants, settings, feature flags e dashboards
 */
export * from './useConfig';

// ============================================================================
// MÓDULO DOCUMENT KITS - KITS DOCUMENTAIS
// ============================================================================

/**
 * Document Kits - Gestão de Kits Documentais
 * Hooks para kits, items, assignments e IA
 */
export * from './document-kits';

// ============================================================================
// MÓDULO GOVERNMENT - INTEGRAÇÃO GOVERNAMENTAL
// ============================================================================

/**
 * Government - Integração com Órgãos Governamentais
 * Hooks para Receita Federal, NFS-e, eSocial, SEFAZ, SPED
 */
export * from './government';

// ============================================================================
// MÓDULO NOTIFICATIONS - NOTIFICAÇÕES MULTI-CANAL
// ============================================================================

/**
 * Notifications - Sistema de Notificações
 * Hooks para envio, templates, preferências e analytics
 */
export * from './notifications';

// ============================================================================
// MÓDULO BIDDING - LICITAÇÕES E CONTRATOS
// ============================================================================

/**
 * Bidding - Licitações e Contratos
 * Hooks para editais, propostas, contratos e certidões
 */
export * from './bidding';

// ============================================================================
// MÓDULO DOCUMENTS - DOCUMENT INTELLIGENCE
// ============================================================================

/**
 * Documents - Document Intelligence (OCR, Classificação, Extração)
 * Hooks para upload, OCR, classificação automática, extração de dados e templates
 */
export * from './documents';

// ============================================================================
// MÓDULO SECURITY LGPD - COMPLIANCE LGPD
// ============================================================================

/**
 * Security LGPD - Compliance LGPD (Lei 13.709/2018)
 * Hooks para consentimentos, criptografia, auditoria, direito ao esquecimento, PIA/DPIA, mascaramento
 */
export * from './security-lgpd';

// ============================================================================
// FEATURES - HOOKS DE FUNCIONALIDADES ESPECÍFICAS
// ============================================================================

/**
 * Notificações Push
 * Sistema de notificações em tempo real
 *
 * @example
 * import { useNotifications } from '@/features/notifications';
 */
export { useNotifications } from '@/features/notifications/hooks/useNotifications';
export { usePushNotifications } from '@/features/notifications/hooks/usePushNotifications';

/**
 * Onboarding / Tour
 * Sistema de tour guiado para novos usuários
 *
 * @example
 * import { useTour } from '@/features/onboarding';
 */
export {
  useTour,
  useShouldShowTour,
  useTourProgress
} from '@/features/onboarding/hooks/useTour';

// ============================================================================
// TIPOS EXPORTADOS (Re-export de tipos úteis)
// ============================================================================

// Tipos são exportados pelos próprios hooks acima
