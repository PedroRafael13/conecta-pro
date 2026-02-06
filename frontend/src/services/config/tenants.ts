/**
 * Service Layer - Tenants (Multi-tenant)
 * Gestão de tenants/condomínios
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  TenantCreate,
  TenantUpdate,
  TenantPlanUpdate,
  TenantAddressUpdate,
  TenantResponse,
  TenantList,
} from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

const BASE_PATH = '/api/v1/config/tenants';

export interface ListTenantsParams {
  skip?: number;
  limit?: number;
  status?: string;
  plan?: string;
  tenant_type?: string;
  search?: string;
}

/**
 * Lista tenants com filtros e paginação
 */
export const listTenants = async (
  params?: ListTenantsParams
): Promise<TenantList> => {
  const { data } = await axiosInstance.get<TenantList>(BASE_PATH, { params });
  return data;
};

/**
 * Cria novo tenant
 */
export const createTenant = async (
  tenant: TenantCreate
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.post<TenantResponse>(BASE_PATH, tenant);
  return data;
};

/**
 * Obtém tenant por ID
 */
export const getTenant = async (tenantId: string): Promise<TenantResponse> => {
  const { data } = await axiosInstance.get<TenantResponse>(
    `${BASE_PATH}/${tenantId}`
  );
  return data;
};

/**
 * Atualiza dados do tenant
 */
export const updateTenant = async (
  tenantId: string,
  updates: TenantUpdate
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.put<TenantResponse>(
    `${BASE_PATH}/${tenantId}`,
    updates
  );
  return data;
};

/**
 * Deleta tenant
 */
export const deleteTenant = async (tenantId: string): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/${tenantId}`);
};

// ==================== Gestão de Plano ====================

/**
 * Atualiza plano do tenant
 */
export const updateTenantPlan = async (
  tenantId: string,
  plan: TenantPlanUpdate
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.put<TenantResponse>(
    `${BASE_PATH}/${tenantId}/plan`,
    plan
  );
  return data;
};

// ==================== Gestão de Endereço ====================

/**
 * Atualiza endereço do tenant
 */
export const updateTenantAddress = async (
  tenantId: string,
  address: TenantAddressUpdate
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.put<TenantResponse>(
    `${BASE_PATH}/${tenantId}/address`,
    address
  );
  return data;
};

// ==================== Gestão de Status ====================

/**
 * Ativa tenant
 */
export const activateTenant = async (
  tenantId: string
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.post<TenantResponse>(
    `${BASE_PATH}/${tenantId}/activate`
  );
  return data;
};

/**
 * Suspende tenant
 */
export const suspendTenant = async (
  tenantId: string
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.post<TenantResponse>(
    `${BASE_PATH}/${tenantId}/suspend`
  );
  return data;
};

/**
 * Cancela tenant
 */
export const cancelTenant = async (
  tenantId: string
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.post<TenantResponse>(
    `${BASE_PATH}/${tenantId}/cancel`
  );
  return data;
};

/**
 * Converte tenant trial para pago
 */
export const convertTrialTenant = async (
  tenantId: string
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.post<TenantResponse>(
    `${BASE_PATH}/${tenantId}/convert-trial`
  );
  return data;
};

// ==================== Gestão de Features ====================

/**
 * Habilita feature para tenant
 */
export const enableTenantFeature = async (
  tenantId: string,
  feature: string
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.post<TenantResponse>(
    `${BASE_PATH}/${tenantId}/features/${feature}/enable`
  );
  return data;
};

/**
 * Desabilita feature para tenant
 */
export const disableTenantFeature = async (
  tenantId: string,
  feature: string
): Promise<TenantResponse> => {
  const { data } = await axiosInstance.post<TenantResponse>(
    `${BASE_PATH}/${tenantId}/features/${feature}/disable`
  );
  return data;
};

// ==================== Estatísticas ====================

export interface TenantStats {
  total: number;
  active: number;
  trial: number;
  suspended: number;
  canceled: number;
  by_plan: Record<string, number>;
  by_type: Record<string, number>;
}

/**
 * Calcula estatísticas dos tenants
 */
export const calculateTenantStats = (
  tenants: TenantResponse[]
): TenantStats => {
  const stats: TenantStats = {
    total: tenants.length,
    active: 0,
    trial: 0,
    suspended: 0,
    canceled: 0,
    by_plan: {},
    by_type: {},
  };

  tenants.forEach((tenant) => {
    // Contar por status
    if (tenant.status === 'active') stats.active++;
    else if (tenant.status === 'trial') stats.trial++;
    else if (tenant.status === 'suspended') stats.suspended++;
    else if (tenant.status === 'canceled') stats.canceled++;

    // Contar por plano
    if (tenant.plan) {
      stats.by_plan[tenant.plan] = (stats.by_plan[tenant.plan] || 0) + 1;
    }

    // Contar por tipo
    if (tenant.tenant_type) {
      stats.by_type[tenant.tenant_type] =
        (stats.by_type[tenant.tenant_type] || 0) + 1;
    }
  });

  return stats;
};

// ==================== Helpers ====================

/**
 * Verifica se tenant está ativo
 */
export const isTenantActive = (tenant: TenantResponse): boolean => {
  return tenant.status === 'active';
};

/**
 * Verifica se tenant está em trial
 */
export const isTenantTrial = (tenant: TenantResponse): boolean => {
  return tenant.status === 'trial';
};

/**
 * Verifica se tenant está suspenso
 */
export const isTenantSuspended = (tenant: TenantResponse): boolean => {
  return tenant.status === 'suspended';
};

/**
 * Verifica se tenant possui feature habilitada
 */
export const hasTenantFeature = (
  tenant: TenantResponse,
  feature: string
): boolean => {
  return tenant.features_enabled?.includes(feature) ?? false;
};
