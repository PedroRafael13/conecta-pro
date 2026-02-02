/**
 * AI Financial Contas a Receber Stub
 */
import { customInstance } from '@/lib/api-client';

export const getFinancialContasAReceber = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/financial/contas-a-receber', method: 'GET', params });
