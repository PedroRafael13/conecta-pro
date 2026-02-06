/**
 * Service Layer - Documents Upload
 * Gestão de upload de documentos
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  DocumentUploadResponse,
} from '@/types/generated/documents';

const BASE_PATH = '/api/v1/documents';

export interface UploadDocumentParams {
  file: File;
  tenant_id: string;
  source?: string;
  auto_process?: boolean;
}

export interface UploadBatchParams {
  files: File[];
  tenant_id: string;
}

/**
 * Faz upload de um documento
 */
export const uploadDocument = async (
  params: UploadDocumentParams
): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', params.file);

  const queryParams = new URLSearchParams({
    tenant_id: params.tenant_id,
  });

  if (params.source) {
    queryParams.append('source', params.source);
  }

  if (params.auto_process !== undefined) {
    queryParams.append('auto_process', String(params.auto_process));
  }

  const { data } = await axiosInstance.post<DocumentUploadResponse>(
    `${BASE_PATH}/upload?${queryParams.toString()}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return data;
};

/**
 * Faz upload de múltiplos documentos
 */
export const uploadBatch = async (
  params: UploadBatchParams
): Promise<DocumentUploadResponse[]> => {
  const formData = new FormData();
  params.files.forEach((file) => {
    formData.append('files', file);
  });

  const queryParams = new URLSearchParams({
    tenant_id: params.tenant_id,
  });

  const { data } = await axiosInstance.post<DocumentUploadResponse[]>(
    `${BASE_PATH}/upload/batch?${queryParams.toString()}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return data;
};
