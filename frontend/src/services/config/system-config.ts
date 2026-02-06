/**
 * Service Layer - System Config
 * Configurações globais do sistema
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  SystemConfigCreate,
  SystemConfigUpdate,
  SystemConfigResponse,
  SystemConfigList,
} from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

const BASE_PATH = '/api/v1/config/system';

export interface ListSystemConfigParams {
  skip?: number;
  limit?: number;
  category?: string;
  search?: string;
  scope?: string;
}

/**
 * Lista configurações do sistema
 */
export const listSystemConfigs = async (
  params?: ListSystemConfigParams
): Promise<SystemConfigList> => {
  const { data } = await axiosInstance.get<SystemConfigList>(BASE_PATH, {
    params,
  });
  return data;
};

/**
 * Cria nova configuração de sistema
 */
export const createSystemConfig = async (
  config: SystemConfigCreate
): Promise<SystemConfigResponse> => {
  const { data } = await axiosInstance.post<SystemConfigResponse>(
    BASE_PATH,
    config
  );
  return data;
};

/**
 * Obtém configuração por ID
 */
export const getSystemConfig = async (
  configId: string
): Promise<SystemConfigResponse> => {
  const { data } = await axiosInstance.get<SystemConfigResponse>(
    `${BASE_PATH}/${configId}`
  );
  return data;
};

/**
 * Atualiza configuração
 */
export const updateSystemConfig = async (
  configId: string,
  updates: SystemConfigUpdate
): Promise<SystemConfigResponse> => {
  const { data } = await axiosInstance.put<SystemConfigResponse>(
    `${BASE_PATH}/${configId}`,
    updates
  );
  return data;
};

/**
 * Deleta configuração
 */
export const deleteSystemConfig = async (configId: string): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/${configId}`);
};

// ==================== Helpers ====================

/**
 * Agrupa configurações por categoria
 */
export const groupConfigsByCategory = (
  configs: SystemConfigResponse[]
): Record<string, SystemConfigResponse[]> => {
  return configs.reduce(
    (acc, config) => {
      const category = config.category ?? 'general';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(config);
      return acc;
    },
    {} as Record<string, SystemConfigResponse[]>
  );
};

/**
 * Agrupa configurações por escopo
 */
export const groupConfigsByScope = (
  configs: SystemConfigResponse[]
): Record<string, SystemConfigResponse[]> => {
  return configs.reduce(
    (acc, config) => {
      const scope = config.scope ?? 'global';
      if (!acc[scope]) {
        acc[scope] = [];
      }
      acc[scope].push(config);
      return acc;
    },
    {} as Record<string, SystemConfigResponse[]>
  );
};

/**
 * Busca configuração por chave
 */
export const findConfigByKey = (
  configs: SystemConfigResponse[],
  key: string
): SystemConfigResponse | undefined => {
  return configs.find((c) => c.chave === key);
};

/**
 * Obtém valor de configuração por chave
 */
export const getConfigValue = (
  configs: SystemConfigResponse[],
  key: string,
  defaultValue?: unknown
): unknown => {
  const config = findConfigByKey(configs, key);
  return config?.valor ?? defaultValue;
};

/**
 * Verifica se configuração está habilitada (boolean)
 */
export const isConfigEnabled = (
  configs: SystemConfigResponse[],
  key: string
): boolean => {
  const value = getConfigValue(configs, key, false);
  return Boolean(value);
};

/**
 * Valida tipo do valor da configuração
 */
export const validateConfigValue = (value: any, valueType: string): boolean => {
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

// ==================== Categorias e Escopos ====================

export const CONFIG_CATEGORIES = {
  SYSTEM: 'system',
  APPLICATION: 'application',
  INTEGRATIONS: 'integrations',
  SECURITY: 'security',
  PERFORMANCE: 'performance',
  MAINTENANCE: 'maintenance',
  FEATURES: 'features',
} as const;

export const CONFIG_SCOPES = {
  GLOBAL: 'global',
  TENANT: 'tenant',
  USER: 'user',
  MODULE: 'module',
} as const;

export type ConfigCategory =
  (typeof CONFIG_CATEGORIES)[keyof typeof CONFIG_CATEGORIES];
export type ConfigScope = (typeof CONFIG_SCOPES)[keyof typeof CONFIG_SCOPES];

/**
 * Obtém label da categoria
 */
export const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    system: 'Sistema',
    application: 'Aplicação',
    integrations: 'Integrações',
    security: 'Segurança',
    performance: 'Performance',
    maintenance: 'Manutenção',
    features: 'Funcionalidades',
  };
  return labels[category] || category;
};

/**
 * Obtém label do escopo
 */
export const getScopeLabel = (scope: string): string => {
  const labels: Record<string, string> = {
    global: 'Global',
    tenant: 'Por Tenant',
    user: 'Por Usuário',
    module: 'Por Módulo',
  };
  return labels[scope] || scope;
};

/**
 * Verifica se config é sensível (não deve ser exposta)
 */
export const isConfigSensitive = (config: SystemConfigResponse): boolean => {
  const sensitiveKeys = [
    'api_key',
    'secret',
    'password',
    'token',
    'credential',
    'private_key',
  ];
  return sensitiveKeys.some((key) =>
    config.chave.toLowerCase().includes(key.toLowerCase())
  );
};

/**
 * Mascara valor sensível para exibição
 */
export const maskSensitiveValue = (value: any): string => {
  const str = String(value);
  if (str.length <= 8) {
    return '***';
  }
  return str.substring(0, 4) + '***' + str.substring(str.length - 4);
};
