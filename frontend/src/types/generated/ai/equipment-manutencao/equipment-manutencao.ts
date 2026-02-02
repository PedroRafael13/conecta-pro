/**
 * AI Equipment Manutencao Stub
 */
import { customInstance } from '@/lib/api-client';

export const getEquipmentManutencao = (params?: Record<string, unknown>) =>
  customInstance<unknown>({ url: '/api/v1/ai/equipment/manutencao', method: 'GET', params });
