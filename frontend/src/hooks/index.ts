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
