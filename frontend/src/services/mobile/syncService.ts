/**
 * Service Layer - Sync Operations
 *
 * Gerencia sincronização offline-online, resolução de conflitos
 * e status de sync para dispositivos móveis.
 *
 * Features:
 * - Sync bidirecional (offline -> server -> offline)
 * - Resolução automática e manual de conflitos
 * - Tracking de status de sincronização
 * - Support para multiple devices
 *
 * @module services/mobile/syncService
 */

import { api } from '@/lib/api';
import type {
  MobileSyncRequest,
  MobileSyncResponse,
} from '@/types/generated/mobile/conectaPROMobileAPI.schemas';

const BASE_URL = '/api/v1/mobile';

/**
 * Sincroniza dados offline com o servidor.
 *
 * Envia operações pendentes do cliente e recebe mudanças do servidor.
 * Detecta e reporta conflitos para resolução.
 *
 * @param syncRequest - Operações offline e token de última sync
 * @returns Resultado da sincronização com conflitos e mudanças do servidor
 */
export async function syncData(
  syncRequest: MobileSyncRequest
): Promise<MobileSyncResponse> {
  const response = await api.post<MobileSyncResponse>(
    `${BASE_URL}/sync`,
    syncRequest
  );
  return response.data;
}

/**
 * Obtém status de sincronização do dispositivo atual.
 *
 * Retorna informações sobre última sync, operações pendentes
 * e status de conectividade.
 *
 * @returns Status de sincronização do dispositivo
 */
export async function getSyncStatus(): Promise<{
  last_sync: string;
  pending_operations: number;
  conflicts_count: number;
  sync_token: string;
  is_online: boolean;
}> {
  const response = await api.get(`${BASE_URL}/sync/status`);
  return response.data;
}

/**
 * Resolve conflito de sincronização.
 *
 * Permite resolução manual de conflitos que não puderam ser
 * resolvidos automaticamente.
 *
 * @param conflictId - ID do conflito
 * @param resolution - Estratégia: 'use_client', 'use_server', 'merge'
 * @param mergedData - Dados merged (obrigatório se resolution = 'merge')
 * @returns Resultado da resolução
 */
export async function resolveSyncConflict(
  conflictId: string,
  resolution: 'use_client' | 'use_server' | 'merge',
  mergedData?: Record<string, unknown>
): Promise<{
  status: string;
  resolved_conflict: unknown;
}> {
  const response = await api.post(
    `${BASE_URL}/sync/resolve-conflict`,
    mergedData || {},
    {
      params: {
        conflict_id: conflictId,
        resolution,
      },
    }
  );
  return response.data;
}

/**
 * Helper: Cria token de sincronização para nova sessão.
 *
 * @returns Novo sync token
 */
export function generateSyncToken(): string {
  const timestamp = Date.now();
  const randomPart = Math.random().toString(36).substring(7);
  return `${timestamp}:${randomPart}`;
}

/**
 * Helper: Verifica se sync é necessária baseado no tempo.
 *
 * @param lastSyncTime - Timestamp da última sync
 * @param intervalMinutes - Intervalo mínimo entre syncs (padrão: 5min)
 * @returns true se sync é necessária
 */
export function shouldSync(
  lastSyncTime: number,
  intervalMinutes: number = 5
): boolean {
  const now = Date.now();
  const elapsed = now - lastSyncTime;
  const intervalMs = intervalMinutes * 60 * 1000;
  return elapsed >= intervalMs;
}
