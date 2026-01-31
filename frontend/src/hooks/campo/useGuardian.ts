/**
 * React Query Hooks - Guardian (CAMPO)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  guardianAccessLogService,
  guardianOccurrenceService,
  guardianEquipmentService,
  guardianSyncService,
} from '@/services/campo';
import type {
  GuardianAccessLog,
  GuardianOccurrence,
  GuardianEquipmentStatus,
  GuardianSync,
} from '@/services/campo/types';

// Access Logs
const ACCESS_LOG_KEYS = {
  all: ['campo', 'guardian', 'access-logs'] as const,
  list: (params?: any) => [...ACCESS_LOG_KEYS.all, params] as const,
  detail: (id: string) => [...ACCESS_LOG_KEYS.all, id] as const,
};

export const useAccessLogs = (params?: any) => {
  return useQuery({
    queryKey: ACCESS_LOG_KEYS.list(params),
    queryFn: () => guardianAccessLogService.listar(params),
  });
};

export const useCriarAccessLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GuardianAccessLog) => guardianAccessLogService.criar(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ACCESS_LOG_KEYS.all }),
  });
};

export const useCriarAccessLogBatch = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (logs: GuardianAccessLog[]) => guardianAccessLogService.criarBatch(logs),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ACCESS_LOG_KEYS.all }),
  });
};

// Occurrences
const OCCURRENCE_KEYS = {
  all: ['campo', 'guardian', 'occurrences'] as const,
  list: (params?: any) => [...OCCURRENCE_KEYS.all, params] as const,
  detail: (id: string) => [...OCCURRENCE_KEYS.all, id] as const,
  stats: () => [...OCCURRENCE_KEYS.all, 'stats'] as const,
};

export const useOccurrences = (params?: any) => {
  return useQuery({
    queryKey: OCCURRENCE_KEYS.list(params),
    queryFn: () => guardianOccurrenceService.listar(params),
  });
};

export const useOccurrence = (occurrenceId: string) => {
  return useQuery({
    queryKey: OCCURRENCE_KEYS.detail(occurrenceId),
    queryFn: () => guardianOccurrenceService.buscar(occurrenceId),
    enabled: !!occurrenceId,
  });
};

export const useCriarOccurrence = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GuardianOccurrence) => guardianOccurrenceService.criar(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: OCCURRENCE_KEYS.all }),
  });
};

export const useAtualizarOccurrence = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ occurrenceId, data: _data }: { occurrenceId: string; data: Partial<GuardianOccurrence> }) => {
      // TODO: Método atualizar não disponível na API gerada
      // Para atualizar ocorrências, use classificar ou escalar
      console.warn('Método atualizar occurrence não disponível na API. Use classificar ou verificarEscalacao.');
      return guardianOccurrenceService.buscar(occurrenceId);
    },
    onSuccess: (_, { occurrenceId }) => {
      queryClient.invalidateQueries({ queryKey: OCCURRENCE_KEYS.detail(occurrenceId) });
      queryClient.invalidateQueries({ queryKey: OCCURRENCE_KEYS.all });
    },
  });
};

export const useClassificarOccurrence = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: {
      occurrence_id: string;
      title: string;
      description: string;
      severity?: string;
      category?: string;
    }) => guardianOccurrenceService.classificar(params),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: OCCURRENCE_KEYS.all }),
  });
};

export const useEscalarOccurrence = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { occurrence_id: string; nivel: number }) => {
      // TODO: Implementar quando endpoint escalar estiver disponível na API
      throw new Error('Endpoint escalar não disponível na API gerada');
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: OCCURRENCE_KEYS.all }),
  });
};

export const useOccurrenceStats = (params?: any) => {
  return useQuery({
    queryKey: [OCCURRENCE_KEYS.stats(), params],
    queryFn: () => guardianOccurrenceService.estatisticas(params),
  });
};

// Equipment Status
const EQUIPMENT_KEYS = {
  all: ['campo', 'guardian', 'equipment'] as const,
  list: (params?: any) => [...EQUIPMENT_KEYS.all, params] as const,
  detail: (id: string) => [...EQUIPMENT_KEYS.all, id] as const,
  offline: () => [...EQUIPMENT_KEYS.all, 'offline'] as const,
  manutencao: () => [...EQUIPMENT_KEYS.all, 'manutencao'] as const,
  resumo: () => [...EQUIPMENT_KEYS.all, 'resumo'] as const,
};

export const useEquipments = (params?: any) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.list(params),
    queryFn: () => guardianEquipmentService.listar(params),
  });
};

export const useEquipment = (equipmentId: string) => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.detail(equipmentId),
    queryFn: () => guardianEquipmentService.buscar(equipmentId),
    enabled: !!equipmentId,
  });
};

export const useEquipmentOffline = () => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.offline(),
    queryFn: () => guardianEquipmentService.listarOffline(),
  });
};

export const useEquipmentManutencao = () => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.manutencao(),
    queryFn: () => guardianEquipmentService.listarManutencao(),
  });
};

export const useEquipmentResumo = () => {
  return useQuery({
    queryKey: EQUIPMENT_KEYS.resumo(),
    queryFn: () => {
      // TODO: Implementar quando endpoint resumo estiver disponível na API
      throw new Error('Endpoint resumo não disponível na API gerada');
    },
  });
};

export const useCriarEquipment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GuardianEquipmentStatus) => guardianEquipmentService.criar(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.all }),
  });
};

export const useAtualizarEquipment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ equipmentId, data }: { equipmentId: string; data: Partial<GuardianEquipmentStatus> }) =>
      guardianEquipmentService.atualizar(equipmentId, data),
    onSuccess: (_, { equipmentId }) => {
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.detail(equipmentId) });
      queryClient.invalidateQueries({ queryKey: EQUIPMENT_KEYS.all });
    },
  });
};

// Sync
const SYNC_KEYS = {
  all: ['campo', 'guardian', 'sync'] as const,
  list: (params?: any) => [...SYNC_KEYS.all, params] as const,
  detail: (id: string) => [...SYNC_KEYS.all, id] as const,
  pendentes: () => [...SYNC_KEYS.all, 'pendentes'] as const,
  falhas: () => [...SYNC_KEYS.all, 'falhas'] as const,
};

export const useSyncs = (params?: any) => {
  return useQuery({
    queryKey: SYNC_KEYS.list(params),
    queryFn: () => guardianSyncService.listar(params),
  });
};

export const useSync = (syncId: string) => {
  return useQuery({
    queryKey: SYNC_KEYS.detail(syncId),
    queryFn: () => guardianSyncService.buscar(syncId),
    enabled: !!syncId,
  });
};

export const useSyncsPendentes = () => {
  return useQuery({
    queryKey: SYNC_KEYS.pendentes(),
    queryFn: () => guardianSyncService.listarPendentes(),
  });
};

export const useSyncsFalhas = () => {
  return useQuery({
    queryKey: SYNC_KEYS.falhas(),
    queryFn: () => guardianSyncService.listarFalhas(),
  });
};

export const useRetentarSync = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (syncId: string) => guardianSyncService.retentar(syncId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SYNC_KEYS.all }),
  });
};

export const useCriarSync = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GuardianSync) => guardianSyncService.criar(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: SYNC_KEYS.all }),
  });
};
