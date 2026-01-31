/**
 * React Query Hooks - Campo Service Principal
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campoServiceMain, monitoringService, securityAuditService } from '@/services/campo';
import type { CampoTechnician, CampoTicket } from '@/services/campo/types';

// Campo Service
const CAMPO_KEYS = {
  all: ['campo', 'service'] as const,
  dashboard: (periodo?: string) => [...CAMPO_KEYS.all, 'dashboard', periodo] as const,
  tecnicos: () => [...CAMPO_KEYS.all, 'tecnicos'] as const,
  tecnico: (id: string) => [...CAMPO_KEYS.tecnicos(), id] as const,
  tickets: () => [...CAMPO_KEYS.all, 'tickets'] as const,
  ticket: (id: string) => [...CAMPO_KEYS.tickets(), id] as const,
};

export const useCampoDashboard = (periodo?: string) => {
  return useQuery({
    queryKey: CAMPO_KEYS.dashboard(periodo),
    queryFn: () => campoServiceMain.dashboard({ periodo }),
  });
};

export const useTecnicos = (params?: any) => {
  return useQuery({
    queryKey: [CAMPO_KEYS.tecnicos(), params],
    queryFn: () => campoServiceMain.listarTecnicos(params),
  });
};

export const useTecnico = (tecnicoId: string) => {
  return useQuery({
    queryKey: CAMPO_KEYS.tecnico(tecnicoId),
    queryFn: () => campoServiceMain.buscarTecnico(tecnicoId),
    enabled: !!tecnicoId,
  });
};

export const useCriarTecnico = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CampoTechnician) => campoServiceMain.criarTecnico(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: CAMPO_KEYS.tecnicos() }),
  });
};

export const useAtualizarTecnico = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ tecnicoId, data }: { tecnicoId: string; data: Partial<CampoTechnician> }) =>
      campoServiceMain.atualizarTecnico(tecnicoId, data),
    onSuccess: (_, { tecnicoId }) => {
      queryClient.invalidateQueries({ queryKey: CAMPO_KEYS.tecnico(tecnicoId) });
      queryClient.invalidateQueries({ queryKey: CAMPO_KEYS.tecnicos() });
    },
  });
};

export const useDesativarTecnico = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (tecnicoId: string) => campoServiceMain.desativarTecnico(tecnicoId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: CAMPO_KEYS.tecnicos() }),
  });
};

export const useTickets = (params?: any) => {
  return useQuery({
    queryKey: [CAMPO_KEYS.tickets(), params],
    queryFn: () => campoServiceMain.listarTickets(params),
  });
};

export const useTicket = (ticketId: string) => {
  return useQuery({
    queryKey: CAMPO_KEYS.ticket(ticketId),
    queryFn: () => campoServiceMain.buscarTicket(ticketId),
    enabled: !!ticketId,
  });
};

export const useCriarTicket = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CampoTicket) => campoServiceMain.criarTicket(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: CAMPO_KEYS.tickets() }),
  });
};

export const useAtribuirTicket = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ ticketId, tecnicoId }: { ticketId: string; tecnicoId: string }) =>
      campoServiceMain.atribuirTicket(ticketId, tecnicoId),
    onSuccess: (_, { ticketId }) => {
      queryClient.invalidateQueries({ queryKey: CAMPO_KEYS.ticket(ticketId) });
      queryClient.invalidateQueries({ queryKey: CAMPO_KEYS.tickets() });
    },
  });
};

// Monitoring
const MONITORING_KEYS = {
  all: ['campo', 'monitoring'] as const,
  health: () => [...MONITORING_KEYS.all, 'health'] as const,
  metrics: () => [...MONITORING_KEYS.all, 'metrics'] as const,
  statistics: (periodo?: string) => [...MONITORING_KEYS.all, 'statistics', periodo] as const,
  status: () => [...MONITORING_KEYS.all, 'status'] as const,
};

export const useMonitoringHealth = () => {
  return useQuery({
    queryKey: MONITORING_KEYS.health(),
    queryFn: () => monitoringService.health(),
    refetchInterval: 30000, // Refetch a cada 30s
  });
};

export const useMonitoringMetrics = () => {
  return useQuery({
    queryKey: MONITORING_KEYS.metrics(),
    queryFn: () => monitoringService.metrics(),
    refetchInterval: 60000, // Refetch a cada 1min
  });
};

export const useMonitoringStatistics = (periodo?: string) => {
  return useQuery({
    queryKey: MONITORING_KEYS.statistics(periodo),
    queryFn: () => {
      // TODO: Implementar quando endpoint de statistics estiver disponível na API
      throw new Error('Endpoint statistics não disponível na API gerada');
    },
  });
};

export const useMonitoringStatus = () => {
  return useQuery({
    queryKey: MONITORING_KEYS.status(),
    queryFn: () => monitoringService.status(),
    refetchInterval: 30000,
  });
};

// Security Audit
const AUDIT_KEYS = {
  all: ['campo', 'security-audit'] as const,
  list: () => [...AUDIT_KEYS.all, 'list'] as const,
  status: (id: string) => [...AUDIT_KEYS.all, 'status', id] as const,
};

export const useSecurityAudits = (params?: any) => {
  return useQuery({
    queryKey: [AUDIT_KEYS.list(), params],
    queryFn: () => securityAuditService.listarAudits(params),
  });
};

export const useIniciarAudit = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { target: string; audit_type?: string; scan_ports?: boolean; check_vulnerabilities?: boolean; deep_scan?: boolean }) =>
      securityAuditService.iniciarAudit(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: AUDIT_KEYS.list() }),
  });
};

export const useAuditStatus = (auditId: string) => {
  return useQuery({
    queryKey: AUDIT_KEYS.status(auditId),
    queryFn: () => securityAuditService.verificarStatus(auditId),
    enabled: !!auditId,
    refetchInterval: 5000, // Poll a cada 5s
  });
};
