/**
 * Bidding Module Type Stubs
 * Tipos para hooks e services de licitacoes
 */

export interface TenderResponse {
  id: string;
  number: string;
  title: string;
  description?: string;
  modality: string;
  status: string;
  opening_date: string;
  closing_date?: string;
  estimated_value?: number;
  pncp_id?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface TenderCreate {
  title: string;
  description?: string;
  modality: string;
  opening_date: string;
  closing_date?: string;
  estimated_value?: number;
}

export interface TenderUpdate {
  title?: string;
  description?: string;
  modality?: string;
  status?: string;
  opening_date?: string;
  closing_date?: string;
  estimated_value?: number;
}

export interface TenderListResponse {
  items: TenderResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface PublicContractResponse {
  id: string;
  tender_id: string;
  number: string;
  status: string;
  value: number;
  start_date: string;
  end_date: string;
  created_at: string;
  [key: string]: unknown;
}

export interface PublicContractCreate {
  tender_id: string;
  value: number;
  start_date: string;
  end_date: string;
}

export interface PublicContractUpdate {
  status?: string;
  value?: number;
  end_date?: string;
}

export interface MeasurementSummary {
  total_measurements: number;
  total_value: number;
  pending: number;
  approved: number;
  [key: string]: unknown;
}

export interface CompanyDocumentResponse {
  id: string;
  name: string;
  type: string;
  status: string;
  valid_until?: string;
  file_url?: string;
  created_at: string;
  [key: string]: unknown;
}

export interface CompanyDocumentCreate {
  name: string;
  type: string;
  valid_until?: string;
}

export interface CompanyDocumentUpdate {
  name?: string;
  type?: string;
  status?: string;
  valid_until?: string;
}

export interface CertificateResponse {
  id: string;
  name: string;
  type: string;
  issuer: string;
  status: string;
  valid_from: string;
  valid_until: string;
  auto_renew: boolean;
  created_at: string;
  [key: string]: unknown;
}

export interface CertificateCreate {
  name: string;
  type: string;
  issuer: string;
  valid_from: string;
  valid_until: string;
  auto_renew?: boolean;
}

export interface CertificateUpdate {
  name?: string;
  type?: string;
  status?: string;
  valid_until?: string;
  auto_renew?: boolean;
}

export interface CertificateListResponse {
  items: CertificateResponse[];
  total: number;
}

export interface CertificateRenewResponse {
  success: boolean;
  certificate_id: string;
  new_valid_until: string;
  message?: string;
}

export interface CertificateBulkStatusResponse {
  total: number;
  valid: number;
  expiring: number;
  expired: number;
  items: CertificateResponse[];
}

// ===== AI Agents Types =====

export interface AgentStatus {
  agent: string;
  status: 'operational' | 'development' | 'planned';
  description: string;
}

export interface OpportunityResponse {
  id: string;
  portal: string;
  portal_id?: string;
  objeto: string;
  valor_estimado?: number;
  modalidade?: string;
  orgao_nome?: string;
  orgao_cnpj?: string;
  uf?: string;
  municipio?: string;
  data_publicacao?: string;
  data_abertura?: string;
  data_encerramento?: string;
  url_edital?: string;
  status: string;
  relevancia_score: number;
  created_at?: string;
}

export interface AnalysisResponse {
  id: string;
  tender_id?: string;
  objeto_resumido?: string;
  modalidade_identificada?: string;
  criterio_julgamento?: string;
  requisitos_habilitacao?: Record<string, string[]>;
  red_flags?: Array<{ tipo: string; descricao: string; severidade: string }>;
  documentos_necessarios?: string[];
  recomendacao_participacao?: string;
  created_at?: string;
}

export interface AssessmentResponse {
  id: string;
  tender_id?: string;
  score?: number;
  recomendacao?: 'GO' | 'NO_GO' | 'CONDICIONAL';
  justificativa?: string;
  requisitos_nao_atendidos?: string[];
  acoes_necessarias?: Array<Record<string, unknown>>;
  created_at?: string;
}

export interface PricingResponse {
  id: string;
  tender_id?: string;
  custos_diretos?: number;
  custos_indiretos?: number;
  impostos?: number;
  valor_total?: number;
  cenario?: string;
  cenarios_completos?: Record<string, { margem: number; total: number; descricao: string }>;
  regime_tributario?: string;
  bdi_percentual?: number;
  created_at?: string;
}

export interface DisputeResponse {
  id: string;
  tender_id?: string;
  portal: string;
  status: string;
  posicao_final?: number;
  resultado?: string;
  valor_final?: string;
  created_at?: string;
}
