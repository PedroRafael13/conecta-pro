/**
 * Tipos TypeScript para o módulo de Medidas Administrativas (Disciplinary)
 */

// Status da medida disciplinar
export type DisciplinaryActionStatus =
  | 'rascunho'
  | 'pendente_aprovacao'
  | 'aprovada'
  | 'rejeitada'
  | 'pendente_assinatura'
  | 'assinada'
  | 'aplicada'
  | 'cancelada';

// Tipo de medida disciplinar
export type DisciplinaryActionType =
  | 'advertencia_verbal'
  | 'advertencia_escrita'
  | 'suspensao'
  | 'demissao_justa_causa';

// Categoria de motivo (Art. 482 CLT)
export type ReasonCategory =
  | 'improbidade'
  | 'incontinencia_conduta'
  | 'mau_procedimento'
  | 'negociacao_habitual'
  | 'condenacao_criminal'
  | 'dessidia'
  | 'embriaguez'
  | 'violacao_segredo'
  | 'indisciplina'
  | 'insubordinacao'
  | 'abandono_emprego'
  | 'ofensas_fisicas'
  | 'ofensas_morais'
  | 'jogos_azar'
  | 'perda_habilitacao'
  | 'outro';

// Tipo de signatário
export type SignerType =
  | 'employee'
  | 'supervisor'
  | 'hr'
  | 'witness'
  | 'manager'
  | 'director';

// Assinatura digital
export interface DigitalSignature {
  id: string;
  action_id: string;
  signer_type: SignerType;
  signer_id: string;
  signer_name: string;
  signer_cpf?: string;
  signature_data?: string; // Base64 do canvas
  signature_hash?: string;
  signed_at?: string;
  ip_address?: string;
  user_agent?: string;
  latitude?: number;
  longitude?: number;
  is_valid: boolean;
  created_at: string;
}

// Medida disciplinar
export interface DisciplinaryAction {
  id: string;
  code: string;
  condominio_id: string;

  // Funcionário
  employee_id: string;
  employee_name: string;
  employee_cpf?: string;
  employee_position?: string;
  employee_department?: string;
  employee_admission_date?: string;

  // Tipo e motivo
  action_type: DisciplinaryActionType;
  reason_category: ReasonCategory;
  reason_description: string;
  occurrence_id?: string;

  // Datas
  incident_date: string;
  application_date?: string;

  // Status
  status: DisciplinaryActionStatus;

  // Suspensão
  suspension_days?: number;
  suspension_start_date?: string;
  suspension_end_date?: string;

  // Documento
  document_text?: string;
  document_template_id?: string;

  // Assinaturas
  employee_signature_id?: string;
  employee_signed_at?: string;
  employee_acknowledged?: boolean;
  employee_refused_sign?: boolean;
  supervisor_signature_id?: string;
  supervisor_signed_at?: string;
  hr_signature_id?: string;
  hr_signed_at?: string;

  // Testemunhas (recusa)
  refusal_witness_1_name?: string;
  refusal_witness_1_cpf?: string;
  refusal_witness_2_name?: string;
  refusal_witness_2_cpf?: string;

  // Aprovação
  requires_approval: boolean;
  approved_by?: string;
  approved_at?: string;
  rejected_by?: string;
  rejected_at?: string;
  rejection_reason?: string;

  // IA
  ai_recommendation?: string;

  // Metadados
  created_at: string;
  updated_at?: string;
  created_by: string;

  // Relacionamentos
  signatures?: DigitalSignature[];
}

// Template de documento
export interface DisciplinaryTemplate {
  id: string;
  name: string;
  action_type: DisciplinaryActionType;
  content: string;
  variables: string[];
  is_active: boolean;
  created_at: string;
}

// Filtros
export interface DisciplinaryFilter {
  search?: string;
  status?: DisciplinaryActionStatus;
  action_type?: DisciplinaryActionType;
  employee_id?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

// Estatísticas
export interface DisciplinaryStats {
  total: number;
  by_status: Record<DisciplinaryActionStatus, number>;
  by_type: Record<DisciplinaryActionType, number>;
  pending_signature: number;
  pending_approval: number;
  this_month: number;
  this_year: number;
}

// Criar medida
export interface DisciplinaryActionCreate {
  employee_id: string;
  employee_name: string;
  employee_cpf: string;
  employee_position?: string;
  action_type: DisciplinaryActionType;
  reason_category: ReasonCategory;
  reason_description: string;
  incident_date: string;
  occurrence_id?: string;
  suspension_days?: number;
  suspension_start_date?: string;
  document_template_id?: string;
}

// Atualizar medida
export interface DisciplinaryActionUpdate {
  reason_description?: string;
  incident_date?: string;
  suspension_days?: number;
  suspension_start_date?: string;
  document_text?: string;
}

// Assinatura
export interface SignatureCreate {
  action_id: string;
  signer_type: SignerType;
  signature_data: string; // Base64
  latitude?: number;
  longitude?: number;
}

// Recusa de assinatura
export interface SignatureRefusal {
  action_id: string;
  witness_1_name: string;
  witness_1_cpf: string;
  witness_2_name: string;
  witness_2_cpf: string;
}

// Labels para exibição
export const ACTION_TYPE_LABELS: Record<DisciplinaryActionType, string> = {
  advertencia_verbal: 'Advertência Verbal',
  advertencia_escrita: 'Advertência Escrita',
  suspensao: 'Suspensão',
  demissao_justa_causa: 'Demissão por Justa Causa',
};

export const STATUS_LABELS: Record<DisciplinaryActionStatus, string> = {
  rascunho: 'Rascunho',
  pendente_aprovacao: 'Pendente Aprovação',
  aprovada: 'Aprovada',
  rejeitada: 'Rejeitada',
  pendente_assinatura: 'Pendente Assinatura',
  assinada: 'Assinada',
  aplicada: 'Aplicada',
  cancelada: 'Cancelada',
};

export const REASON_CATEGORY_LABELS: Record<ReasonCategory, string> = {
  improbidade: 'Improbidade (Art. 482, a)',
  incontinencia_conduta: 'Incontinência de Conduta (Art. 482, b)',
  mau_procedimento: 'Mau Procedimento (Art. 482, b)',
  negociacao_habitual: 'Negociação Habitual (Art. 482, c)',
  condenacao_criminal: 'Condenação Criminal (Art. 482, d)',
  dessidia: 'Desídia (Art. 482, e)',
  embriaguez: 'Embriaguez (Art. 482, f)',
  violacao_segredo: 'Violação de Segredo (Art. 482, g)',
  indisciplina: 'Indisciplina (Art. 482, h)',
  insubordinacao: 'Insubordinação (Art. 482, h)',
  abandono_emprego: 'Abandono de Emprego (Art. 482, i)',
  ofensas_fisicas: 'Ofensas Físicas (Art. 482, j/k)',
  ofensas_morais: 'Ofensas Morais (Art. 482, j/k)',
  jogos_azar: 'Jogos de Azar (Art. 482, l)',
  perda_habilitacao: 'Perda de Habilitação (Art. 482, m)',
  outro: 'Outro Motivo',
};

export const SIGNER_TYPE_LABELS: Record<SignerType, string> = {
  employee: 'Funcionário',
  supervisor: 'Supervisor',
  hr: 'Recursos Humanos',
  witness: 'Testemunha',
  manager: 'Gerente',
  director: 'Diretor',
};

// Cores por status
export const STATUS_COLORS: Record<DisciplinaryActionStatus, string> = {
  rascunho: 'bg-gray-500/10 text-gray-500',
  pendente_aprovacao: 'bg-yellow-500/10 text-yellow-500',
  aprovada: 'bg-blue-500/10 text-blue-500',
  rejeitada: 'bg-red-500/10 text-red-500',
  pendente_assinatura: 'bg-orange-500/10 text-orange-500',
  assinada: 'bg-green-500/10 text-green-500',
  aplicada: 'bg-emerald-500/10 text-emerald-500',
  cancelada: 'bg-gray-500/10 text-gray-400',
};

// Cores por tipo de ação
export const ACTION_TYPE_COLORS: Record<DisciplinaryActionType, string> = {
  advertencia_verbal: 'bg-yellow-500/10 text-yellow-600',
  advertencia_escrita: 'bg-orange-500/10 text-orange-600',
  suspensao: 'bg-red-500/10 text-red-600',
  demissao_justa_causa: 'bg-red-700/10 text-red-700',
};
