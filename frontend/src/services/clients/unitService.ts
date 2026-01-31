/**
 * Service Layer - Unit Management
 * Gestão de Unidades
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  UnitCreate,
  UnitUpdate,
  UnitResponse,
  UnitListResponse,
  UnitStats,
} from '@/types/generated/clients/conectaPROMóduloCLIENTS.schemas';

const BASE_URL = '/api/v1/clients';

/**
 * Service de Unidades
 */
export const unitService = {
  /**
   * Cria nova unidade
   */
  create: async (
    condominiumId: string,
    data: UnitCreate
  ): Promise<UnitResponse> => {
    const response = await axiosInstance.post<UnitResponse>(
      `${BASE_URL}/condominiums/${condominiumId}/units`,
      data
    );
    return response.data;
  },

  /**
   * Lista unidades do condomínio
   */
  list: async (
    condominiumId: string,
    params?: {
      skip?: number;
      limit?: number;
    }
  ): Promise<UnitListResponse[]> => {
    const response = await axiosInstance.get<UnitListResponse[]>(
      `${BASE_URL}/condominiums/${condominiumId}/units`,
      { params }
    );
    return response.data;
  },

  /**
   * Obtém unidade por ID
   */
  getById: async (unitId: string): Promise<UnitResponse> => {
    const response = await axiosInstance.get<UnitResponse>(
      `${BASE_URL}/units/${unitId}`
    );
    return response.data;
  },

  /**
   * Atualiza unidade
   */
  update: async (unitId: string, data: UnitUpdate): Promise<UnitResponse> => {
    const response = await axiosInstance.put<UnitResponse>(
      `${BASE_URL}/units/${unitId}`,
      data
    );
    return response.data;
  },

  /**
   * Remove unidade
   */
  delete: async (unitId: string): Promise<void> => {
    await axiosInstance.delete(`${BASE_URL}/units/${unitId}`);
  },

  /**
   * Define proprietário da unidade
   */
  setOwner: async (
    unitId: string,
    params: {
      name: string;
      document?: string;
      phone?: string;
      email?: string;
    }
  ): Promise<UnitResponse> => {
    const response = await axiosInstance.post<UnitResponse>(
      `${BASE_URL}/units/${unitId}/set-owner`,
      null,
      { params }
    );
    return response.data;
  },

  /**
   * Define morador/inquilino da unidade
   */
  setResident: async (
    unitId: string,
    params: {
      name: string;
      document?: string;
      phone?: string;
      email?: string;
      is_tenant?: boolean;
    }
  ): Promise<UnitResponse> => {
    const response = await axiosInstance.post<UnitResponse>(
      `${BASE_URL}/units/${unitId}/set-resident`,
      null,
      { params }
    );
    return response.data;
  },

  /**
   * Remove morador da unidade
   */
  clearResident: async (unitId: string): Promise<UnitResponse> => {
    const response = await axiosInstance.post<UnitResponse>(
      `${BASE_URL}/units/${unitId}/clear-resident`
    );
    return response.data;
  },

  /**
   * Obtém estatísticas de unidades
   */
  getStats: async (condominiumId: string): Promise<UnitStats> => {
    const response = await axiosInstance.get<UnitStats>(
      `${BASE_URL}/condominiums/${condominiumId}/units/stats`
    );
    return response.data;
  },
};
