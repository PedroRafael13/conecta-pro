/**
 * Service Layer - Tenant Settings
 * Configurações específicas por tenant
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  TenantSettingsCreate,
  TenantSettingsUpdate,
  TenantSettingsValueUpdate,
  TenantSettingsResponse,
  TenantSettingsList,
} from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

const BASE_PATH = '/api/v1/config';

export interface ListTenantSettingsParams {
  skip?: number;
  limit?: number;
  category?: string;
  search?: string;
}

/**
 * Lista configurações de um tenant
 */
export const listTenantSettings = async (
  tenantId: string,
  params?: ListTenantSettingsParams
): Promise<TenantSettingsList> => {
  const { data } = await axiosInstance.get<TenantSettingsList>(
    `${BASE_PATH}/tenants/${tenantId}/settings`,
    { params }
  );
  return data;
};

/**
 * Cria nova configuração para tenant
 */
export const createTenantSetting = async (
  tenantId: string,
  setting: TenantSettingsCreate
): Promise<TenantSettingsResponse> => {
  const { data } = await axiosInstance.post<TenantSettingsResponse>(
    `${BASE_PATH}/tenants/${tenantId}/settings`,
    setting
  );
  return data;
};

/**
 * Obtém configuração por ID
 */
export const getTenantSetting = async (
  settingId: string
): Promise<TenantSettingsResponse> => {
  const { data } = await axiosInstance.get<TenantSettingsResponse>(
    `${BASE_PATH}/settings/${settingId}`
  );
  return data;
};

/**
 * Atualiza configuração
 */
export const updateTenantSetting = async (
  settingId: string,
  updates: TenantSettingsUpdate
): Promise<TenantSettingsResponse> => {
  const { data } = await axiosInstance.put<TenantSettingsResponse>(
    `${BASE_PATH}/settings/${settingId}`,
    updates
  );
  return data;
};

/**
 * Deleta configuração
 */
export const deleteTenantSetting = async (settingId: string): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/settings/${settingId}`);
};

// ==================== Gestão de Valores ====================

/**
 * Atualiza apenas o valor da configuração
 */
export const updateTenantSettingValue = async (
  settingId: string,
  valueUpdate: TenantSettingsValueUpdate
): Promise<TenantSettingsResponse> => {
  const { data } = await axiosInstance.put<TenantSettingsResponse>(
    `${BASE_PATH}/settings/${settingId}/value`,
    valueUpdate
  );
  return data;
};

/**
 * Reseta configuração para valor padrão
 */
export const resetTenantSetting = async (
  settingId: string
): Promise<TenantSettingsResponse> => {
  const { data } = await axiosInstance.post<TenantSettingsResponse>(
    `${BASE_PATH}/settings/${settingId}/reset`
  );
  return data;
};

// ==================== Helpers ====================

/**
 * Agrupa configurações por categoria
 */
export const groupSettingsByCategory = (
  settings: TenantSettingsResponse[]
): Record<string, TenantSettingsResponse[]> => {
  return settings.reduce(
    (acc, setting) => {
      const category = setting.category ?? 'general';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(setting);
      return acc;
    },
    {} as Record<string, TenantSettingsResponse[]>
  );
};

/**
 * Busca configuração por chave
 */
export const findSettingByKey = (
  settings: TenantSettingsResponse[],
  key: string
): TenantSettingsResponse | undefined => {
  return settings.find((s) => s.chave === key);
};

/**
 * Obtém valor de configuração por chave
 */
export const getSettingValue = (
  settings: TenantSettingsResponse[],
  key: string,
  defaultValue?: unknown
): unknown => {
  const setting = findSettingByKey(settings, key);
  return setting?.valor ?? defaultValue;
};

/**
 * Verifica se configuração está habilitada (boolean)
 */
export const isSettingEnabled = (
  settings: TenantSettingsResponse[],
  key: string
): boolean => {
  const value = getSettingValue(settings, key, false);
  return Boolean(value);
};

/**
 * Valida tipo do valor da configuração
 */
export const validateSettingValue = (
  value: any,
  valueType: string
): boolean => {
  switch (valueType) {
    case 'string':
      return typeof value === 'string';
    case 'number':
      return typeof value === 'number' && !isNaN(value);
    case 'boolean':
      return typeof value === 'boolean';
    case 'json':
      try {
        if (typeof value === 'string') {
          JSON.parse(value);
        }
        return true;
      } catch {
        return false;
      }
    default:
      return true;
  }
};

// ==================== Categorias Padrão ====================

export const SETTING_CATEGORIES = {
  GENERAL: 'general',
  APPEARANCE: 'appearance',
  NOTIFICATIONS: 'notifications',
  INTEGRATIONS: 'integrations',
  SECURITY: 'security',
  FEATURES: 'features',
  BILLING: 'billing',
} as const;

export type SettingCategory =
  (typeof SETTING_CATEGORIES)[keyof typeof SETTING_CATEGORIES];

/**
 * Obtém label da categoria
 */
export const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    general: 'Geral',
    appearance: 'Aparência',
    notifications: 'Notificações',
    integrations: 'Integrações',
    security: 'Segurança',
    features: 'Funcionalidades',
    billing: 'Faturamento',
  };
  return labels[category] || category;
};
