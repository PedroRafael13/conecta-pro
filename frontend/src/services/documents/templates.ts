/**
 * Service Layer - Documents Templates
 * Gestão de templates de extração de documentos
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  TemplateRequest,
  TemplateResponse,
} from '@/types/generated/documents';

const BASE_PATH = '/api/v1/documents/templates';

export interface ListTemplatesParams {
  category?: string | null;
  document_type?: string | null;
  include_builtin?: boolean;
}

/**
 * Lista templates de extração disponíveis
 */
export const listTemplates = async (
  params?: ListTemplatesParams
): Promise<TemplateResponse[]> => {
  const { data } = await axiosInstance.get<TemplateResponse[]>(BASE_PATH, {
    params,
  });

  return data;
};

/**
 * Cria novo template de extração
 */
export const createTemplate = async (
  tenant_id: string,
  template: TemplateRequest
): Promise<TemplateResponse> => {
  const { data } = await axiosInstance.post<TemplateResponse>(
    BASE_PATH,
    template,
    {
      params: { tenant_id },
    }
  );

  return data;
};

/**
 * Obtém detalhes de um template
 */
export const getTemplate = async (
  template_id: string
): Promise<Record<string, unknown>> => {
  const { data } = await axiosInstance.get<Record<string, unknown>>(
    `${BASE_PATH}/${template_id}`
  );

  return data;
};

/**
 * Remove um template customizado
 */
export const deleteTemplate = async (template_id: string): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/${template_id}`);
};
