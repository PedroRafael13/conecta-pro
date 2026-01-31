/**
 * Service Layer - Documents Metadata
 * Tipos de documentos, providers OCR, estatísticas e validações
 */

import { axiosInstance } from '@/lib/axios-instance';

const BASE_PATH = '/api/v1/documents';

// ==================== Tipos de Documentos ====================

export interface DocumentType {
  [key: string]: string;
}

/**
 * Lista todos os tipos de documentos suportados
 */
export const listDocumentTypes = async (): Promise<DocumentType[]> => {
  const { data } = await axiosInstance.get<DocumentType[]>(
    `${BASE_PATH}/types`
  );

  return data;
};

// ==================== Providers OCR ====================

export interface OCRProviders {
  [key: string]: unknown;
}

/**
 * Lista providers de OCR disponíveis
 */
export const listOCRProviders = async (): Promise<OCRProviders> => {
  const { data } = await axiosInstance.get<OCRProviders>(
    `${BASE_PATH}/providers`
  );

  return data;
};

// ==================== Estatísticas ====================

export interface StorageStats {
  [key: string]: unknown;
}

/**
 * Obtém estatísticas de armazenamento do tenant
 */
export const getStorageStats = async (
  tenant_id: string
): Promise<StorageStats> => {
  const { data } = await axiosInstance.get<StorageStats>(
    `${BASE_PATH}/stats`,
    {
      params: { tenant_id },
    }
  );

  return data;
};

// ==================== Validações ====================

export interface ValidationResult {
  valid: boolean;
}

/**
 * Valida um CPF
 */
export const validateCPF = async (cpf: string): Promise<ValidationResult> => {
  const { data } = await axiosInstance.post<ValidationResult>(
    `${BASE_PATH}/validate/cpf`,
    null,
    {
      params: { cpf },
    }
  );

  return data;
};

/**
 * Valida um CNPJ
 */
export const validateCNPJ = async (cnpj: string): Promise<ValidationResult> => {
  const { data } = await axiosInstance.post<ValidationResult>(
    `${BASE_PATH}/validate/cnpj`,
    null,
    {
      params: { cnpj },
    }
  );

  return data;
};
