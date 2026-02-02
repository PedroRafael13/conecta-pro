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
  config: AxiosRequestConfig,
): Promise<T> => {
  try {
    if (config.url) {
      // Remove barra final das URLs para evitar redirect 307
      if (config.url.endsWith('/') && !config.url.endsWith('://')) {
        config.url = config.url.slice(0, -1);
        console.log('[API Client] Removed trailing slash from URL');
      }

      // Remove duplicações de path (ex: /suppliers/suppliers -> /suppliers)
      // Padrão: /resource/resource/ ou /resource/resource
      config.url = config.url.replace(/\/([^\/]+)\/\1(?:\/|$)/, '/$1');

      // Adiciona condominio_id automaticamente para endpoints do módulo Financial
      if (config.url.includes('/financial/')) {
        console.log('[API Client] Financial endpoint:', config.url);

        // Adiciona condominio_id como query parameter se não existir
        if (!config.params) {
          config.params = {};
        }
        if (!config.params.condominio_id) {
          config.params.condominio_id = DEFAULT_CONDOMINIO_ID;
          console.log('[API Client] Added condominio_id:', DEFAULT_CONDOMINIO_ID);
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
