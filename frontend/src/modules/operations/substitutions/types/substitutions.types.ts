/**
 * Tipos para o módulo de Substituições
 * Gestão de solicitações de substituição e workflow de aprovação
 */

export interface Substitution {
  id: string;
  solicitante_id: string;
  solicitante_nome: string;
  solicitante_avatar?: string;
  solicitante_funcao: string;
  substituto_id?: string;
  substituto_nome?: string;
  substituto_avatar?: string;
  substituto_funcao?: string;
  posto_id: string;
  posto_nome: string;
  schedule_id: string;
  data: string;
  turno: string;
  horario_inicio: string;
  horario_fim: string;
  motivo: SubstitutionReason;
  motivo_descricao?: string;
  status: SubstitutionStatus;
  aprovador_id?: string;
  aprovador_nome?: string;
  aprovado_em?: string;
  rejeitado_em?: string;
  motivo_rejeicao?: string;
  urgente: boolean;
  documentos?: Documento[];
  historico: SubstitutionHistoryItem[];
  created_at: string;
  updated_at: string;
}

export type SubstitutionStatus =
  | 'pendente'
  | 'aprovada'
  | 'rejeitada'
  | 'cancelada'
  | 'aguardando_substituto'
  | 'substituto_confirmado'
  | 'concluida';

export type SubstitutionReason =
  | 'atestado_medico'
  | 'emergencia_pessoal'
  | 'problema_transporte'
  | 'ferias'
  | 'licenca'
  | 'folga_compensatoria'
  | 'troca_turno'
  | 'outro';

export interface SubstitutionHistoryItem {
  id: string;
  acao: string;
  descricao: string;
  usuario_id: string;
  usuario_nome: string;
  timestamp: string;
  dados_anteriores?: Record<string, unknown>;
  dados_novos?: Record<string, unknown>;
}

export interface Documento {
  id: string;
  nome: string;
  tipo: 'atestado' | 'comprovante' | 'documento' | 'outro';
  url: string;
  tamanho: number;
  uploaded_at: string;
}

export interface SubstitutionFilters {
  status?: SubstitutionStatus[];
  motivo?: SubstitutionReason[];
  posto_id?: string;
  solicitante_id?: string;
  substituto_id?: string;
  data_inicio?: string;
  data_fim?: string;
  urgente?: boolean;
}

export interface SubstitutionStats {
  total_solicitacoes: number;
  pendentes: number;
  aprovadas: number;
  rejeitadas: number;
  aguardando_substituto: number;
  concluidas: number;
  taxa_aprovacao: number;
  tempo_medio_aprovacao: number; // em horas
  motivos_frequentes: {
    motivo: SubstitutionReason;
    quantidade: number;
    percentual: number;
  }[];
}

export interface SubstitutionFormData {
  schedule_id: string;
  motivo: SubstitutionReason;
  motivo_descricao?: string;
  substituto_id?: string;
  urgente: boolean;
  documentos?: File[];
}

export interface ApprovalAction {
  tipo: 'aprovar' | 'rejeitar';
  substitution_id: string;
  substituto_id?: string;
  observacao?: string;
  motivo_rejeicao?: string;
}

export interface AvailableSubstitute {
  id: string;
  nome: string;
  avatar?: string;
  funcao: string;
  telefone: string;
  email: string;
  disponibilidade: 'disponivel' | 'parcial' | 'indisponivel';
  horas_trabalhadas_semana: number;
  distancia_posto?: number; // em km
  avaliacao: number;
  total_substituicoes: number;
  ultima_substituicao?: string;
}

export interface WorkflowStep {
  id: string;
  ordem: number;
  titulo: string;
  descricao: string;
  status: 'pendente' | 'atual' | 'concluido' | 'pulado';
  responsavel?: string;
  data_conclusao?: string;
  icone: string;
}
