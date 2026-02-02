/**
 * AI Document Kits Stub
 */
import { customInstance } from '@/lib/api-client';

export const getDocumentKits = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/document-kits', method: 'GET', params });
