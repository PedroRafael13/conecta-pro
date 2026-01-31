/**
 * Service Layer - Feature Flags
 * Controle de features e gradual rollout
 */

import { axiosInstance } from '@/lib/axios-instance';
import type {
  FeatureFlagCreate,
  FeatureFlagUpdate,
  FeatureFlagGradualRollout,
  FeatureFlagTenantToggle,
  FeatureFlagEvaluate,
  FeatureFlagEvaluateResponse,
  FeatureFlagResponse,
  FeatureFlagList,
} from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

const BASE_PATH = '/api/v1/config/flags';

export interface ListFeatureFlagsParams {
  skip?: number;
  limit?: number;
  status?: string;
  category?: string;
  search?: string;
}

/**
 * Lista feature flags
 */
export const listFeatureFlags = async (
  params?: ListFeatureFlagsParams
): Promise<FeatureFlagList> => {
  const { data } = await axiosInstance.get<FeatureFlagList>(BASE_PATH, {
    params,
  });
  return data;
};

/**
 * Cria nova feature flag
 */
export const createFeatureFlag = async (
  flag: FeatureFlagCreate
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.post<FeatureFlagResponse>(
    BASE_PATH,
    flag
  );
  return data;
};

/**
 * Obtém feature flag por ID
 */
export const getFeatureFlag = async (
  flagId: string
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.get<FeatureFlagResponse>(
    `${BASE_PATH}/${flagId}`
  );
  return data;
};

/**
 * Atualiza feature flag
 */
export const updateFeatureFlag = async (
  flagId: string,
  updates: FeatureFlagUpdate
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.put<FeatureFlagResponse>(
    `${BASE_PATH}/${flagId}`,
    updates
  );
  return data;
};

/**
 * Deleta feature flag
 */
export const deleteFeatureFlag = async (flagId: string): Promise<void> => {
  await axiosInstance.delete(`${BASE_PATH}/${flagId}`);
};

// ==================== Controle de Status ====================

/**
 * Habilita feature flag globalmente
 */
export const enableFeatureFlag = async (
  flagId: string
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.post<FeatureFlagResponse>(
    `${BASE_PATH}/${flagId}/enable`
  );
  return data;
};

/**
 * Desabilita feature flag globalmente
 */
export const disableFeatureFlag = async (
  flagId: string
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.post<FeatureFlagResponse>(
    `${BASE_PATH}/${flagId}/disable`
  );
  return data;
};

// ==================== Gradual Rollout ====================

export interface SetPercentageParams {
  percentage: number;
}

/**
 * Define percentual de rollout
 */
export const setFeatureFlagPercentage = async (
  flagId: string,
  percentage: number
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.post<FeatureFlagResponse>(
    `${BASE_PATH}/${flagId}/percentage`,
    { percentage }
  );
  return data;
};

/**
 * Configura gradual rollout
 */
export const setGradualRollout = async (
  flagId: string,
  rollout: FeatureFlagGradualRollout
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.post<FeatureFlagResponse>(
    `${BASE_PATH}/${flagId}/gradual-rollout`,
    rollout
  );
  return data;
};

// ==================== Controle por Tenant ====================

/**
 * Toggle de feature flag para tenant específico
 */
export const toggleFeatureFlagForTenant = async (
  flagId: string,
  toggle: FeatureFlagTenantToggle
): Promise<FeatureFlagResponse> => {
  const { data } = await axiosInstance.post<FeatureFlagResponse>(
    `${BASE_PATH}/${flagId}/toggle-tenant`,
    toggle
  );
  return data;
};

// ==================== Avaliação ====================

/**
 * Avalia se feature flag está habilitada para contexto
 */
export const evaluateFeatureFlag = async (
  evaluation: FeatureFlagEvaluate
): Promise<FeatureFlagEvaluateResponse> => {
  const { data } = await axiosInstance.post<FeatureFlagEvaluateResponse>(
    `${BASE_PATH}/evaluate`,
    evaluation
  );
  return data;
};

// ==================== Helpers ====================

/**
 * Verifica se flag está habilitada
 * Usa 'ativo' e 'status' conforme schema gerado
 */
export const isFeatureFlagEnabled = (flag: FeatureFlagResponse): boolean => {
  return flag.ativo && flag.status === 'active';
};

/**
 * Verifica se flag está em rollout
 */
export const isFeatureFlagInRollout = (flag: FeatureFlagResponse): boolean => {
  return (
    flag.rollout_percentage !== undefined &&
    flag.rollout_percentage > 0 &&
    flag.rollout_percentage < 100
  );
};

/**
 * Calcula se tenant está no percentual de rollout
 */
export const isTenantInRollout = (
  tenantId: string,
  percentage: number
): boolean => {
  // Hash simples do tenantId para distribuição consistente
  let hash = 0;
  for (let i = 0; i < tenantId.length; i++) {
    hash = (hash << 5) - hash + tenantId.charCodeAt(i);
    hash = hash & hash; // Convert to 32bit integer
  }
  const normalizedHash = Math.abs(hash) % 100;
  return normalizedHash < percentage;
};

/**
 * Agrupa flags por categoria
 */
export const groupFlagsByCategory = (
  flags: FeatureFlagResponse[]
): Record<string, FeatureFlagResponse[]> => {
  return flags.reduce(
    (acc, flag) => {
      const category = flag.category ?? 'general';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(flag);
      return acc;
    },
    {} as Record<string, FeatureFlagResponse[]>
  );
};

/**
 * Busca flag por código
 */
export const findFlagByKey = (
  flags: FeatureFlagResponse[],
  key: string
): FeatureFlagResponse | undefined => {
  return flags.find((f) => f.codigo === key);
};

/**
 * Filtra flags por status ativo
 */
export const filterFlagsByStatus = (
  flags: FeatureFlagResponse[],
  enabled: boolean
): FeatureFlagResponse[] => {
  return flags.filter((f) => f.ativo === enabled);
};

// ==================== Categorias e Status ====================

export const FLAG_CATEGORIES = {
  FEATURES: 'features',
  EXPERIMENTAL: 'experimental',
  MAINTENANCE: 'maintenance',
  PERFORMANCE: 'performance',
  UI: 'ui',
  INTEGRATIONS: 'integrations',
} as const;

export type FlagCategory =
  (typeof FLAG_CATEGORIES)[keyof typeof FLAG_CATEGORIES];

/**
 * Obtém label da categoria
 */
export const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    features: 'Funcionalidades',
    experimental: 'Experimental',
    maintenance: 'Manutenção',
    performance: 'Performance',
    ui: 'Interface',
    integrations: 'Integrações',
  };
  return labels[category] || category;
};

/**
 * Obtém status legível
 */
export const getStatusLabel = (flag: FeatureFlagResponse): string => {
  if (!flag.ativo) return 'Desabilitado';
  if (flag.rollout_percentage === 100) return 'Habilitado (100%)';
  if (flag.rollout_percentage > 0) {
    return `Rollout (${flag.rollout_percentage}%)`;
  }
  return 'Habilitado';
};

/**
 * Obtém cor do status
 */
export const getStatusColor = (flag: FeatureFlagResponse): string => {
  if (!flag.ativo) return 'gray';
  if (flag.rollout_percentage === 100) return 'green';
  if (flag.rollout_percentage > 0) {
    return 'yellow';
  }
  return 'blue';
};
