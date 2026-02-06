/**
 * AI GED Documentos Stub
 */
import { customInstance } from '@/lib/api-client';

export const getGedDocumentos = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/ged/documentos', method: 'GET', params });
