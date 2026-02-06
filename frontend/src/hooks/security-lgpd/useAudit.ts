/**
 * React Query Hooks - Audit
 * Hooks para trilha de auditoria LGPD
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AuditService } from '@/services/security-lgpd';
import type {
  AuditLogRequest,
  ListAuditLogsParams,
  AuditLogRequestSeverity,
} from '@/services/security-lgpd';

/**
 * Hook para criar log de auditoria
 */
export function useCreateLGPDAuditLog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: AuditLogRequest) =>
      AuditService.createAuditLog(request),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'audit', 'logs'],
      });
    },
  });
}

/**
 * Hook para listar logs de auditoria LGPD
 */
export function useLGPDAuditLogs(params?: ListAuditLogsParams) {
  return useQuery({
    queryKey: ['lgpd', 'audit', 'logs', params],
    queryFn: () => AuditService.listAuditLogs(params),
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
}

/**
 * Hook para listar ações disponíveis
 */
export function useAuditActions() {
  return useQuery({
    queryKey: ['lgpd', 'audit', 'actions'],
    queryFn: () => AuditService.listActions(),
    staleTime: 30 * 60 * 1000, // 30 minutos
  });
}

/**
 * Hook para listar tipos de recurso
 */
export function useResourceTypes() {
  return useQuery({
    queryKey: ['lgpd', 'audit', 'resource-types'],
    queryFn: () => AuditService.listResourceTypes(),
    staleTime: 30 * 60 * 1000,
  });
}

/**
 * Hook para registrar acesso a dados
 */
export function useLogDataAccess() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      resourceType,
      resourceId,
      details,
    }: {
      userId: string;
      resourceType: string;
      resourceId: string;
      details?: Record<string, unknown>;
    }) => AuditService.logDataAccess(userId, resourceType, resourceId, details),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'audit', 'logs'],
      });
    },
  });
}

/**
 * Hook para registrar modificação
 */
export function useLogDataModification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      resourceType,
      resourceId,
      changes,
    }: {
      userId: string;
      resourceType: string;
      resourceId: string;
      changes: Record<string, unknown>;
    }) => AuditService.logDataModification(userId, resourceType, resourceId, changes),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'audit', 'logs'],
      });
    },
  });
}

/**
 * Hook para registrar exclusão
 */
export function useLogDataDeletion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      resourceType,
      resourceId,
      reason,
    }: {
      userId: string;
      resourceType: string;
      resourceId: string;
      reason: string;
    }) => AuditService.logDataDeletion(userId, resourceType, resourceId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'audit', 'logs'],
      });
    },
  });
}

/**
 * Hook para registrar exportação
 */
export function useLogDataExport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      dataScope,
      recordCount,
    }: {
      userId: string;
      dataScope: string;
      recordCount: number;
    }) => AuditService.logDataExport(userId, dataScope, recordCount),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'audit', 'logs'],
      });
    },
  });
}

/**
 * Hook para registrar incidente de segurança
 */
export function useLogSecurityIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      incidentType,
      description,
      severity,
    }: {
      userId: string;
      incidentType: string;
      description: string;
      severity?: AuditLogRequestSeverity;
    }) =>
      AuditService.logSecurityIncident(userId, incidentType, description, severity),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['lgpd', 'audit', 'logs'],
      });
    },
  });
}

/**
 * Hook para logs por período
 */
export function useLogsByDateRange(startDate: Date, endDate: Date, limit?: number) {
  return useQuery({
    queryKey: ['lgpd', 'audit', 'logs', 'range', startDate, endDate, limit],
    queryFn: () => AuditService.getLogsByDateRange(startDate, endDate, limit),
    enabled: !!startDate && !!endDate,
    staleTime: 1 * 60 * 1000,
  });
}

/**
 * Hook para logs por usuário
 */
export function useLogsByUser(userId: string, limit?: number) {
  return useQuery({
    queryKey: ['lgpd', 'audit', 'logs', 'user', userId, limit],
    queryFn: () => AuditService.getLogsByUser(userId, limit),
    enabled: !!userId,
    staleTime: 1 * 60 * 1000,
  });
}

/**
 * Hook para logs por recurso
 */
export function useLogsByResource(resourceType: string, limit?: number) {
  return useQuery({
    queryKey: ['lgpd', 'audit', 'logs', 'resource', resourceType, limit],
    queryFn: () => AuditService.getLogsByResource(resourceType, limit),
    enabled: !!resourceType,
    staleTime: 1 * 60 * 1000,
  });
}
