/**
 * Reimbursement Hooks - React Query Completo
 *
 * Módulo de Reembolso de Despesas
 * Cobertura: 30 endpoints (100%)
 *
 * Estrutura de Hooks:
 * - Requests: Listagem, detalhes, CRUD, stats, categorias
 * - Items: Criar, atualizar, deletar itens
 * - Attachments: Upload, listagem, download, exclusão
 * - Approvals: Pendentes, análise, aprovar, rejeitar, devolver
 * - Payments: Listar prontos, processar pagamento
 */

// Requests
export {
  useReimbursementRequests,
  useMyReimbursementRequests,
  useReimbursementRequest,
  useReimbursementStats,
  useExpenseCategories,
  useExpenseTypes,
  useAttachmentTypes,
  useCreateReimbursementRequest,
  useUpdateReimbursementRequest,
  useDeleteReimbursementRequest,
  useSubmitReimbursementRequest,
  useCancelReimbursementRequest,
  reimbursementKeys,
} from './useReimbursementRequests';

// Items
export {
  useCreateReimbursementItem,
  useUpdateReimbursementItem,
  useDeleteReimbursementItem,
} from './useReimbursementItems';

// Attachments
export {
  useReimbursementAttachments,
  useUploadReimbursementAttachment,
  useDeleteReimbursementAttachment,
  useDownloadReimbursementAttachment,
  attachmentKeys,
} from './useReimbursementAttachments';

// Approvals
export {
  usePendingReimbursementApprovals,
  useStartReimbursementAnalysis,
  useApproveReimbursement,
  useRejectReimbursement,
  useReturnReimbursementToDraft,
  approvalKeys,
} from './useReimbursementApprovals';

// Payments
export {
  useReadyForPaymentReimbursements,
  useProcessReimbursementPayment,
  paymentKeys,
} from './useReimbursementPayments';

// Re-export types
export type {
  ReimbursementRequestCreate,
  ReimbursementRequestUpdate,
  ReimbursementRequestResponse,
  ReimbursementRequestStats,
  ReimbursementItemCreate,
  ReimbursementItemUpdate,
  ReimbursementItemResponse,
  ReimbursementAttachmentResponse,
  ReimbursementApproveRequest,
  ReimbursementRejectRequest,
  ReimbursementReturnRequest,
  ReimbursementProcessRequest,
  PaginatedReimbursementResponse,
} from '@/types/generated/reimbursement/models';
