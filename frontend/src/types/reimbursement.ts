/**
 * Tipos para o módulo de Reembolso de Despesas
 */

// Enums
export type ReimbursementStatus =
  | 'rascunho'
  | 'pendente'
  | 'em_analise'
  | 'aprovado'
  | 'rejeitado'
  | 'processado'
  | 'cancelado';

export type ApprovalLevel =
  | 'supervisor'
  | 'gerente'
  | 'diretor'
  | 'financeiro';

export type ExpenseCategory =
  | 'transporte'
  | 'alimentacao'
  | 'hospedagem'
  | 'material'
  | 'comunicacao'
  | 'viagem'
  | 'estacionamento'
  | 'pedagio'
  | 'saude'
  | 'cursos'
  | 'outros';

export type DocumentType =
  | 'nota_fiscal'
  | 'cupom_fiscal'
  | 'recibo'
  | 'fatura'
  | 'boleto'
  | 'comprovante'
  | 'outros';

export type AttachmentType =
  | 'nota_fiscal'
  | 'cupom_fiscal'
  | 'recibo'
  | 'fatura'
  | 'comprovante_pagamento'
  | 'comprovante_cartao'
  | 'boleto'
  | 'extrato'
  | 'outros';

// Item de Reembolso
export interface ReimbursementItem {
  id: string;
  request_id: string;
  category_id: string | null;
  category_type: ExpenseCategory;
  category_label: string;
  description: string;
  merchant: string | null;
  expense_date: string;
  amount: number;
  approved_amount: number | null;
  document_type: DocumentType | null;
  document_number: string | null;
  is_approved: boolean;
  rejection_reason: string | null;
  has_attachment: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ReimbursementItemCreate {
  category_type: ExpenseCategory;
  category_id?: string;
  description: string;
  merchant?: string;
  expense_date: string;
  amount: number;
  document_type?: DocumentType;
  document_number?: string;
  notes?: string;
}

export interface ReimbursementItemUpdate {
  category_type?: ExpenseCategory;
  category_id?: string;
  description?: string;
  merchant?: string;
  expense_date?: string;
  amount?: number;
  document_type?: DocumentType;
  document_number?: string;
  notes?: string;
}

// Anexo de Reembolso
export interface ReimbursementAttachment {
  id: string;
  request_id: string;
  item_id: string | null;
  attachment_type: AttachmentType;
  type_label: string;
  file_name: string;
  file_path: string;
  file_size_bytes: number | null;
  file_size_formatted: string;
  mime_type: string | null;
  thumbnail_path: string | null;
  is_valid: boolean;
  validation_notes: string | null;
  original_name: string | null;
  description: string | null;
  is_image: boolean;
  is_pdf: boolean;
  uploaded_by: string | null;
  uploaded_at: string;
  is_active: boolean;
}

export interface ReimbursementAttachmentCreate {
  item_id?: string;
  attachment_type?: AttachmentType;
  description?: string;
}

// Solicitação de Reembolso
export interface ReimbursementRequest {
  id: string;
  code: string;
  title: string;
  description: string | null;
  requester_id: string;
  expense_date_start: string;
  expense_date_end: string;
  total_amount: number;
  approved_amount: number;
  paid_amount: number;
  status: ReimbursementStatus;
  approval_level: ApprovalLevel | null;
  submitted_at: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
  payable_account_id: string | null;
  processed_at: string | null;
  processed_by: string | null;
  bank_code: string | null;
  bank_agency: string | null;
  bank_account: string | null;
  pix_key: string | null;
  cost_center: string | null;
  project: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  // Relacionamentos
  items: ReimbursementItem[];
  attachments: ReimbursementAttachment[];
  // Computed
  items_count: number;
  attachments_count: number;
  can_edit: boolean;
  can_submit: boolean;
  can_approve: boolean;
  can_process: boolean;
}

export interface ReimbursementRequestCreate {
  title: string;
  description?: string;
  expense_date_start: string;
  expense_date_end: string;
  cost_center?: string;
  project?: string;
  notes?: string;
  bank_code?: string;
  bank_agency?: string;
  bank_account?: string;
  pix_key?: string;
  items?: ReimbursementItemCreate[];
}

export interface ReimbursementRequestUpdate {
  title?: string;
  description?: string;
  expense_date_start?: string;
  expense_date_end?: string;
  cost_center?: string;
  project?: string;
  notes?: string;
  bank_code?: string;
  bank_agency?: string;
  bank_account?: string;
  pix_key?: string;
}

// Filtros
export interface ReimbursementFilter {
  status?: ReimbursementStatus;
  approval_level?: ApprovalLevel;
  requester_id?: string;
  expense_date_start?: string;
  expense_date_end?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
  cost_center?: string;
  project?: string;
}

// Estatísticas
export interface ReimbursementStats {
  total: number;
  by_status: Record<string, number>;
  by_approval_level: Record<string, number>;
  total_amount: number;
  total_approved: number;
  total_paid: number;
  pending_count: number;
  pending_amount: number;
  approved_count: number;
  approved_amount: number;
}

// Requisições de aprovação
export interface ReimbursementApproveRequest {
  comments?: string;
  approved_items?: string[];
  rejected_items?: Record<string, string>;
}

export interface ReimbursementRejectRequest {
  reason: string;
}

export interface ReimbursementReturnRequest {
  reason: string;
}

export interface ReimbursementProcessRequest {
  due_date?: string;
  notes?: string;
}

// Resposta paginada
export interface PaginatedReimbursementResponse {
  items: ReimbursementRequest[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Categoria
export interface ReimbursementCategory {
  id: string;
  code: string;
  name: string;
  description: string | null;
  default_limit_per_request: number | null;
  default_limit_monthly: number | null;
  requires_receipt: boolean;
  auto_approve_below: number | null;
  accounting_account: string | null;
  cost_center: string | null;
  is_active: boolean;
}

// Labels
export const REIMBURSEMENT_STATUS_LABELS: Record<ReimbursementStatus, string> = {
  rascunho: 'Rascunho',
  pendente: 'Pendente',
  em_analise: 'Em Análise',
  aprovado: 'Aprovado',
  rejeitado: 'Rejeitado',
  processado: 'Processado',
  cancelado: 'Cancelado',
};

export const APPROVAL_LEVEL_LABELS: Record<ApprovalLevel, string> = {
  supervisor: 'Supervisor (até R$ 500)',
  gerente: 'Gerente (até R$ 2.000)',
  diretor: 'Diretor (até R$ 10.000)',
  financeiro: 'Financeiro (acima R$ 10.000)',
};

export const EXPENSE_CATEGORY_LABELS: Record<ExpenseCategory, string> = {
  transporte: 'Transporte',
  alimentacao: 'Alimentação',
  hospedagem: 'Hospedagem',
  material: 'Material',
  comunicacao: 'Comunicação',
  viagem: 'Viagem',
  estacionamento: 'Estacionamento',
  pedagio: 'Pedágio',
  saude: 'Saúde',
  cursos: 'Cursos/Treinamentos',
  outros: 'Outros',
};

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  nota_fiscal: 'Nota Fiscal',
  cupom_fiscal: 'Cupom Fiscal',
  recibo: 'Recibo',
  fatura: 'Fatura',
  boleto: 'Boleto',
  comprovante: 'Comprovante',
  outros: 'Outros',
};

export const ATTACHMENT_TYPE_LABELS: Record<AttachmentType, string> = {
  nota_fiscal: 'Nota Fiscal',
  cupom_fiscal: 'Cupom Fiscal',
  recibo: 'Recibo',
  fatura: 'Fatura',
  comprovante_pagamento: 'Comprovante de Pagamento',
  comprovante_cartao: 'Comprovante de Cartão',
  boleto: 'Boleto',
  extrato: 'Extrato',
  outros: 'Outros',
};

// Status colors
export const STATUS_COLORS: Record<ReimbursementStatus, string> = {
  rascunho: 'bg-gray-500/10 text-gray-500',
  pendente: 'bg-yellow-500/10 text-yellow-500',
  em_analise: 'bg-blue-500/10 text-blue-500',
  aprovado: 'bg-green-500/10 text-green-500',
  rejeitado: 'bg-red-500/10 text-red-500',
  processado: 'bg-purple-500/10 text-purple-500',
  cancelado: 'bg-gray-500/10 text-gray-400',
};
