/**
 * Service Layer - Mobile Core
 *
 * Funcionalidades core do módulo mobile: health check, config,
 * dashboard otimizado, offline data e batch operations.
 *
 * Features:
 * - Health check e monitoramento
 * - Configuração dinâmica do app
 * - Dashboard lightweight para mobile
 * - Dados offline essenciais
 * - Batch operations para otimizar rede
 *
 * @module services/mobile/mobileService
 */

import { api } from '@/lib/api';
import type {
  HealthCheckResponse,
  MobileConfigResponse,
  MobileDashboardResponse,
  OfflineDataResponse,
  BatchRequest,
  BatchResponse,
  BatchOperation,
} from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

const BASE_URL = '/api/v1/mobile';

/**
 * Verifica saúde do serviço mobile.
 *
 * @returns Status dos componentes mobile
 */
export async function healthCheck(): Promise<HealthCheckResponse> {
  const response = await api.get<HealthCheckResponse>(`${BASE_URL}/health`);
  return response.data;
}

/**
 * Obtém configuração do app mobile.
 *
 * Retorna versão mínima, features habilitadas,
 * configurações de sync e modo manutenção.
 *
 * @returns Configuração do app
 */
export async function getMobileConfig(): Promise<MobileConfigResponse> {
  const response = await api.get<MobileConfigResponse>(`${BASE_URL}/config`);
  return response.data;
}

/**
 * Obtém dashboard otimizado para mobile.
 *
 * Dashboard com dados reduzidos e opcionalmente
 * sem gráficos para conexões lentas.
 *
 * @returns Dashboard mobile
 */
export async function getMobileDashboard(): Promise<MobileDashboardResponse> {
  const response = await api.get<MobileDashboardResponse>(
    `${BASE_URL}/dashboard`
  );
  return response.data;
}

/**
 * Obtém dados essenciais para funcionamento offline.
 *
 * Retorna perfil do usuário e dados essenciais
 * dos módulos solicitados.
 *
 * @param modules - Módulos a sincronizar (ex: 'leads,tasks,contacts')
 * @returns Dados offline
 */
export async function getOfflineData(
  modules?: string
): Promise<OfflineDataResponse> {
  const response = await api.get<OfflineDataResponse>(
    `${BASE_URL}/offline-data`,
    {
      params: modules ? { modules } : undefined,
    }
  );
  return response.data;
}

/**
 * Executa múltiplas operações em batch.
 *
 * Combina múltiplas chamadas API em uma única requisição
 * para otimizar uso de rede em dispositivos móveis.
 *
 * @param batchRequest - Operações a executar
 * @returns Resultados individuais
 */
export async function executeBatch(
  batchRequest: BatchRequest
): Promise<BatchResponse> {
  const response = await api.post<BatchResponse>(
    `${BASE_URL}/batch`,
    batchRequest
  );
  return response.data;
}

/**
 * Helper: Verifica se app requer atualização.
 *
 * @param currentVersion - Versão atual do app
 * @returns true se atualização é necessária
 */
export async function requiresUpdate(
  currentVersion: string
): Promise<boolean> {
  try {
    const config = await getMobileConfig();
    return config.force_update || false;
  } catch {
    return false;
  }
}

/**
 * Helper: Verifica se está em modo manutenção.
 *
 * @returns true se manutenção ativa
 */
export async function isMaintenanceMode(): Promise<boolean> {
  try {
    const config = await getMobileConfig();
    return config.maintenance_mode || false;
  } catch {
    return false;
  }
}

/**
 * Helper: Obtém features habilitadas.
 *
 * @returns Array de feature IDs habilitadas
 */
export async function getEnabledFeatures(): Promise<string[]> {
  try {
    const config = await getMobileConfig();
    return (
      config.features?.filter((f) => f.enabled).map((f) => f.id || '') || []
    );
  } catch {
    return [];
  }
}

/**
 * Helper: Verifica se feature está habilitada.
 *
 * @param featureId - ID da feature
 * @returns true se habilitada
 */
export async function isFeatureEnabled(featureId: string): Promise<boolean> {
  const enabled = await getEnabledFeatures();
  return enabled.includes(featureId);
}

/**
 * Helper: Cria batch request a partir de múltiplas operações.
 *
 * @param operations - Array de operações
 * @param stopOnError - Parar no primeiro erro (padrão: false)
 * @returns BatchRequest formatado
 */
export function createBatchRequest(
  operations: Array<{
    id: string;
    method: string;
    endpoint: string;
    data?: Record<string, unknown> | null;
    params?: Record<string, unknown> | null;
  }>,
  stopOnError: boolean = false
): BatchRequest {
  const batchOperations: BatchOperation[] = operations.map((op) => ({
    id: op.id,
    method: op.method,
    endpoint: op.endpoint,
    data: op.data ?? undefined,
    params: op.params ?? undefined,
    headers: undefined,
    can_parallelize: true,
    depends_on: undefined,
    timeout_ms: 30000,
    retry_on_failure: false,
    max_retries: 0,
  }));

  return {
    operations: batchOperations,
    stop_on_error: stopOnError,
    parallel_execution: true,
  };
}
