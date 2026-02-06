/**
 * CRM Contracts API Type Stubs
 * Tipos para hooks e services de gestao de contratos
 */

export interface ContractResponse {
  id: string;
  number: string;
  title: string;
  client_id: string;
  client_name?: string;
  status: string;
  type: string;
  start_date: string;
  end_date: string;
  value: number;
  description?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface ContractCreate {
  title: string;
  client_id: string;
  type: string;
  start_date: string;
  end_date: string;
  value: number;
  description?: string;
}

export interface ContractUpdate {
  title?: string;
  status?: string;
  type?: string;
  start_date?: string;
  end_date?: string;
  value?: number;
  description?: string;
}

export interface ContractDetailResponse extends ContractResponse {
  items: ContractItemResponse[];
  addendums: ContractAddendumResponse[];
  sla_reports: ContractSLAReportResponse[];
}

export interface ContractListResponse {
  items: ContractResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface ContractStats {
  total_contracts: number;
  active_contracts: number;
  expiring_soon: number;
  total_value: number;
  [key: string]: unknown;
}

export interface ContractAlert {
  id: string;
  contract_id: string;
  type: string;
  message: string;
  severity: string;
  created_at: string;
  [key: string]: unknown;
}

export interface ContractRenewal {
  contract_id: string;
  new_end_date: string;
  new_value?: number;
  notes?: string;
}

export interface RenewalResult {
  success: boolean;
  contract_id: string;
  new_end_date: string;
  message?: string;
}

export interface AdjustmentResult {
  success: boolean;
  contract_id: string;
  new_value: number;
  message?: string;
}

export interface ContractItemResponse {
  id: string;
  contract_id: string;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  [key: string]: unknown;
}

export interface ContractItemCreate {
  description: string;
  quantity: number;
  unit_price: number;
}

export interface ContractItemUpdate {
  description?: string;
  quantity?: number;
  unit_price?: number;
}

export interface ContractAddendumResponse {
  id: string;
  contract_id: string;
  number: string;
  type: string;
  description: string;
  status: string;
  signed_at?: string;
  created_at: string;
  [key: string]: unknown;
}

export interface ContractAddendumCreate {
  type: string;
  description: string;
}

export interface ContractAddendumSign {
  signer_name: string;
  signer_role: string;
  signature_date: string;
}

export interface ContractTemplateResponse {
  id: string;
  name: string;
  description?: string;
  content: string;
  type: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface ContractTemplateCreate {
  name: string;
  description?: string;
  content: string;
  type: string;
}

export interface ContractTemplateUpdate {
  name?: string;
  description?: string;
  content?: string;
  type?: string;
  is_active?: boolean;
}

export interface ContractTemplateListResponse {
  items: ContractTemplateResponse[];
  total: number;
}

export interface ContractSLAReportResponse {
  id: string;
  contract_id: string;
  period: string;
  status: string;
  metrics: Record<string, unknown>;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  [key: string]: unknown;
}

export interface ContractSLAReportCreate {
  period: string;
  metrics: Record<string, unknown>;
}

export interface ContractSLAReportApprove {
  approved_by: string;
  notes?: string;
}

export interface SLACalculation {
  target: number;
  actual: number;
  compliance: number;
  status: string;
  [key: string]: unknown;
}
