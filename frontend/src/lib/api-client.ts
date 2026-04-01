/**
 * Custom Axios instance for Orval-generated API clients
 * Reutiliza a instância configurada do api.ts com interceptors
 */

import { api } from './api';
import type { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// Condominio ID padrão para desenvolvimento
// TODO: Obter dinamicamente do contexto do usuário em produção
const DEFAULT_CONDOMINIO_ID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

export const customInstance = async <T>(
  configOrUrl: AxiosRequestConfig | string,
  options?: RequestInit | AxiosRequestConfig,
): Promise<T> => {
  // Support both (config) and (url, options) calling conventions from orval
  let config: AxiosRequestConfig;
  if (typeof configOrUrl === 'string') {
    config = { url: configOrUrl, ...(options as AxiosRequestConfig) };
  } else {
    config = configOrUrl;
  }

  try {
    if (config.url) {
      // Remove duplicações de path (ex: /suppliers/suppliers -> /suppliers)
      // Padrão: /resource/resource/ ou /resource/resource
      config.url = config.url.replace(/\/([^\/]+)\/\1(?:\/|$)/, '/$1');

      // Adiciona condominio_id automaticamente para endpoints do módulo Financial
      if (config.url.includes('/financial/')) {
        // Adiciona condominio_id como query parameter se não existir
        if (!config.params) {
          config.params = {};
        }
        if (!config.params.condominio_id) {
          config.params.condominio_id = DEFAULT_CONDOMINIO_ID;
        }
      }
    }

    const response: AxiosResponse<T> = await api.request<T>(config);
    return response.data;
  } catch (error) {
    // Propagar erro do Axios para tratamento do React Query
    throw error as AxiosError;
  }
};

export default customInstance;
