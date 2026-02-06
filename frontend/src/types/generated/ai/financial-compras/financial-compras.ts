/**
 * AI Financial Compras Stub
 */
import { customInstance } from '@/lib/api-client';

export const getFinancialCompras = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/financial/compras', method: 'GET', params });
