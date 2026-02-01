/**
 * Tipos para o módulo Document Kits.
 * Stub criado manualmente (endpoint não coberto pelo Orval ainda).
 */

// Kit Types enum
export type KitType =
  | 'ADMISSAO'
  | 'DEMISSAO'
  | 'FERIAS'
  | 'AFASTAMENTO'
  | 'PROMOCAO'
  | 'TRANSFERENCIA'
  | 'CONTRATO_CLIENTE'
  | 'ENCERRAMENTO_CONTRATO'
  | 'MENSAL'
  | 'TREINAMENTO'
  | 'CERTIFICACAO'
  | 'VIGILANTE'
  | 'EQUIPAMENTO'
  | 'OUTRO';

// Kit Status enum
export type KitStatus = 'ATIVO' | 'INATIVO' | 'ARQUIVADO' | 'RASCUNHO';

// Entity Type enum
export type EntityType = 'FUNCIONARIO' | 'CLIENTE' | 'CONDOMINIO' | 'CONTRATO';

// Item Status enum
export type ItemStatusEnum = 'PENDENTE' | 'ENVIADO' | 'APROVADO' | 'REJEITADO' | 'VENCIDO';

// Assignment Status
export type AssignmentStatusOutput = 'PENDENTE' | 'EM_ANDAMENTO' | 'CONCLUIDO' | 'VENCIDO' | 'CANCELADO';

// Document Kit Response
export interface DocumentKitResponse {
  id: string;
  codigo: string;
  nome: string;
  descricao?: string | null;
  tipo: KitType;
  status: KitStatus;
  is_template: boolean;
  is_obrigatorio: boolean;
  prazo_dias?: number;
  permite_parcial: boolean;
  requer_aprovacao: boolean;
  condominio_id: string;
  total_itens: number;
  itens_obrigatorios: number;
  uso_count: number;
  versao: number;
  entity_types: string[];
  departamentos: string[];
  cargos: string[];
  tags: string[];
  created_at: string;
  updated_at?: string | null;
}

// Document Kit List Response
export interface DocumentKitListResponse {
  items: DocumentKitResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// Document Kit Create
export interface DocumentKitCreate {
  codigo: string;
  nome: string;
  descricao?: string | null;
  tipo: KitType;
  condominio_id: string;
  is_template?: boolean;
  is_obrigatorio?: boolean;
  prazo_dias?: number;
  permite_parcial?: boolean;
  requer_aprovacao?: boolean;
  entity_types?: string[];
  departamentos?: string[];
  cargos?: string[];
  tags?: string[];
}

// Document Kit Update
export interface DocumentKitUpdate {
  nome?: string;
  descricao?: string | null;
  tipo?: KitType;
  is_template?: boolean;
  is_obrigatorio?: boolean;
  prazo_dias?: number;
  permite_parcial?: boolean;
  requer_aprovacao?: boolean;
  entity_types?: string[];
  departamentos?: string[];
  cargos?: string[];
  tags?: string[];
}

// Kit Stats Response
export interface KitStatsResponse {
  total_kits: number;
  kits_ativos: number;
  kits_inativos: number;
  total_assignments: number;
  assignments_pendentes: number;
  assignments_completos: number;
  assignments_vencidos: number;
  taxa_conclusao: number;
  tempo_medio_conclusao_dias: number;
}

// Document Kit Item Response
export interface DocumentKitItemResponse {
  id: string;
  codigo: string;
  nome: string;
  descricao?: string | null;
  tipo: string;
  prioridade: string;
  ordem: number;
  is_ativo: boolean;
  kit_id: string;
  condominio_id: string;
  formatos_aceitos: string[];
  tamanho_max_mb: number;
  requer_validade: boolean;
  requer_autenticacao: boolean;
  tags: string[];
  created_at: string;
  updated_at?: string | null;
}

// Document Kit Item Create
export interface DocumentKitItemCreate {
  codigo: string;
  nome: string;
  descricao?: string | null;
  tipo: string;
  prioridade?: string;
  ordem?: number;
  kit_id: string;
  condominio_id: string;
  formatos_aceitos?: string[];
  tamanho_max_mb?: number;
  requer_validade?: boolean;
  requer_autenticacao?: boolean;
  tags?: string[];
}

// Document Kit Item Update
export interface DocumentKitItemUpdate {
  nome?: string;
  descricao?: string | null;
  tipo?: string;
  prioridade?: string;
  ordem?: number;
  formatos_aceitos?: string[];
  tamanho_max_mb?: number;
  requer_validade?: boolean;
  requer_autenticacao?: boolean;
  tags?: string[];
}

// Document Kit Item Status Response
export interface DocumentKitItemStatusResponse {
  id: string;
  item_id: string;
  assignment_id: string;
  status: ItemStatusEnum;
  arquivo_url?: string | null;
  observacao?: string | null;
  aprovado_por?: string | null;
  aprovado_em?: string | null;
  created_at: string;
  updated_at?: string | null;
}

// Document Kit Assignment Response
export interface DocumentKitAssignmentResponse {
  id: string;
  kit_id: string;
  entity_type: EntityType;
  entity_id: string;
  condominio_id: string;
  status: AssignmentStatusOutput;
  prazo: string;
  responsavel_id?: string | null;
  observacao?: string | null;
  total_itens: number;
  itens_concluidos: number;
  percentual_conclusao: number;
  created_at: string;
  updated_at?: string | null;
}

// Document Kit Assignment Create
export interface DocumentKitAssignmentCreate {
  kit_id: string;
  entity_type: EntityType;
  entity_id: string;
  condominio_id: string;
  prazo?: string;
  responsavel_id?: string;
  observacao?: string;
}

// Document Kit Assignment Update
export interface DocumentKitAssignmentUpdate {
  status?: AssignmentStatusOutput;
  prazo?: string;
  responsavel_id?: string;
  observacao?: string;
}

// Kit Suggestion Response (AI)
export interface KitSuggestionResponse {
  kit_type: KitType;
  nome_sugerido: string;
  descricao: string;
  itens_sugeridos: Array<{
    nome: string;
    tipo: string;
    prioridade: string;
    descricao: string;
  }>;
  confianca: number;
}
