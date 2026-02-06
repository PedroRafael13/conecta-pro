/**
 * Service Layer - Documents Processing
 * Processamento de documentos: OCR, classificação, extração, validação
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  OCRResponse,
  ClassificationResponse,
  ExtractionResponse,
  ValidationResponse,
  DocumentResponse,
  ProcessingRequest,
} from '@/types/generated/documents';

const BASE_PATH = '/api/v1/documents';

// ==================== OCR ====================

export interface RunOCRParams {
  document_id: string;
  provider?: string;
  languages?: string;
}

/**
 * Executa OCR em um documento
 */
export const runOCR = async (
  params: RunOCRParams
): Promise<OCRResponse> => {
  const { document_id, ...queryParams } = params;

  const { data } = await axiosInstance.post<OCRResponse>(
    `${BASE_PATH}/${document_id}/ocr`,
    null,
    { params: queryParams }
  );

  return data;
};

// ==================== Classificação ====================

/**
 * Classifica o tipo de um documento
 */
export const classifyDocument = async (
  document_id: string
): Promise<ClassificationResponse> => {
  const { data } = await axiosInstance.post<ClassificationResponse>(
    `${BASE_PATH}/${document_id}/classify`
  );

  return data;
};

// ==================== Extração ====================

export interface ExtractDataParams {
  document_id: string;
  template_id?: string | null;
}

/**
 * Extrai dados estruturados de um documento
 */
export const extractData = async (
  params: ExtractDataParams
): Promise<ExtractionResponse> => {
  const { document_id, template_id } = params;

  const queryParams = template_id ? { template_id } : {};

  const { data } = await axiosInstance.post<ExtractionResponse>(
    `${BASE_PATH}/${document_id}/extract`,
    null,
    { params: queryParams }
  );

  return data;
};

// ==================== Validação ====================

/**
 * Valida dados extraídos de um documento
 */
export const validateData = async (
  document_id: string
): Promise<ValidationResponse> => {
  const { data } = await axiosInstance.post<ValidationResponse>(
    `${BASE_PATH}/${document_id}/validate`
  );

  return data;
};

// ==================== Processamento Completo ====================

export interface ProcessDocumentParams {
  document_id: string;
  request: ProcessingRequest;
}

/**
 * Processa documento com pipeline completo
 * 1. OCR (se necessário)
 * 2. Classificação (opcional)
 * 3. Extração de dados (opcional)
 * 4. Validação (opcional)
 */
export const processDocument = async (
  params: ProcessDocumentParams
): Promise<DocumentResponse> => {
  const { document_id, request } = params;

  const { data } = await axiosInstance.post<DocumentResponse>(
    `${BASE_PATH}/${document_id}/process`,
    request
  );

  return data;
};
