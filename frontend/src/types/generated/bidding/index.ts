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
