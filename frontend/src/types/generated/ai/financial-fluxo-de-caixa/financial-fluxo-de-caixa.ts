/**
 * AI Financial Fluxo de Caixa Stub
 */
import { customInstance } from '@/lib/api-client';

export const getFinancialFluxoDeCaixa = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/financial/fluxo-de-caixa', method: 'GET', params });
