/**
 * Reimbursement Services - Service Layer Completo
 *
 * Módulo de Reembolso de Despesas
 * Cobertura: 30 endpoints (100%)
 *
 * Estrutura:
 * - Requests (8 endpoints): CRUD, submissão, cancelamento, stats
 * - Items (3 endpoints): Adicionar, atualizar, remover itens
 * - Attachments (4 endpoints): Upload, listagem, download, exclusão
 * - Approvals (4 endpoints): Pendentes, análise, aprovar, rejeitar, devolver
 * - Payment (2 endpoints): Listar prontos, processar pagamento
 * - Utilities (9 endpoints): Categorias, tipos, enums
 */

export { reimbursementRequestService } from './reimbursementRequestService';
export { reimbursementItemService } from './reimbursementItemService';
export { reimbursementAttachmentService } from './reimbursementAttachmentService';
export { reimbursementApprovalService } from './reimbursementApprovalService';
export { reimbursementPaymentService } from './reimbursementPaymentService';

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
