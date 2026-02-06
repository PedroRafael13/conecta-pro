/**
 * AI Clients Cadastro Stub
 */
import { customInstance } from '@/lib/api-client';

export const getClientsCadastro = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/clients/cadastro', method: 'GET', params });
