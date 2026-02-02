/**
 * AI Operacional Diaristas Stub
 */
import { customInstance } from '@/lib/api-client';

export const getOperacionalDiaristas = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/operacional/diaristas', method: 'GET', params });
