/**
 * Service Layer - Disciplinary Actions (Medidas Administrativas)
 *
 * Gerencia medidas disciplinares (CRUD, aprovacao, assinatura, IA)
 */

import { apiClient } from '@/lib/api/client';
import type {
  DisciplinaryAction,
  DisciplinaryActionCreate,
  DisciplinaryActionUpdate,
} from '@/types/disciplinary';

const BASE_URL = '/api/v1/operacional/disciplinary';

export const disciplinaryService = {
  /**
   * Cria nova medida disciplinar
   */
  async create(data: DisciplinaryActionCreate): Promise<DisciplinaryAction> {
    const response = await apiClient.post<DisciplinaryAction>(BASE_URL, data);
    return response.data;
  },

  /**
   * Atualiza medida disciplinar (apenas rascunho)
   */
  async update(actionId: string, data: DisciplinaryActionUpdate): Promise<DisciplinaryAction> {
    const response = await apiClient.put<DisciplinaryAction>(`${BASE_URL}/${actionId}`, data);
    return response.data;
  },

  /**
   * Submete para aprovacao
   */
  async submit(actionId: string): Promise<DisciplinaryAction> {
    const response = await apiClient.post<DisciplinaryAction>(`${BASE_URL}/${actionId}/submit`);
    return response.data;
  },

  /**
   * Aprova medida disciplinar
   */
  async approve(actionId: string, comments?: string): Promise<DisciplinaryAction> {
    const response = await apiClient.post<DisciplinaryAction>(
      `${BASE_URL}/${actionId}/approve`,
      { comments }
    );
    return response.data;
  },

  /**
   * Rejeita medida disciplinar
   */
  async reject(actionId: string, reason: string): Promise<DisciplinaryAction> {
    const response = await apiClient.post<DisciplinaryAction>(
      `${BASE_URL}/${actionId}/reject`,
      { reason }
    );
    return response.data;
  },

  /**
   * Assina documento digitalmente
   */
  async sign(
    actionId: string,
    data: {
      signature_data: string;
      signer_type: string;
      latitude?: number;
      longitude?: number;
    }
  ): Promise<DisciplinaryAction> {
    const response = await apiClient.post<DisciplinaryAction>(
      `${BASE_URL}/${actionId}/sign`,
      data
    );
    return response.data;
  },

  /**
   * Registra recusa de assinatura com testemunhas
   */
  async refuseSignature(
    actionId: string,
    data: {
      witness_1_name: string;
      witness_1_cpf: string;
      witness_2_name: string;
      witness_2_cpf: string;
    }
  ): Promise<DisciplinaryAction> {
    const response = await apiClient.post<DisciplinaryAction>(
      `${BASE_URL}/${actionId}/refuse-signature`,
      data
    );
    return response.data;
  },

  /**
   * Valida conformidade CLT via IA
   */
  async validateCompliance(actionId: string): Promise<{
    compliant: boolean;
    issues: string[];
    suggestions: string[];
  }> {
    const response = await apiClient.post<{
      compliant: boolean;
      issues: string[];
      suggestions: string[];
    }>(`${BASE_URL}/${actionId}/validate-compliance`);
    return response.data;
  },

  /**
   * Verifica proporcionalidade da medida via IA
   */
  async checkProportionality(actionId: string): Promise<{
    proportional: boolean;
    analysis: string;
  }> {
    const response = await apiClient.post<{
      proportional: boolean;
      analysis: string;
    }>(`${BASE_URL}/${actionId}/check-proportionality`);
    return response.data;
  },
};

export default disciplinaryService;
