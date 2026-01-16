import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@core/api';
import type {
  AuditRule,
  AuditExecution,
  Anomaly,
  ComplianceScore,
  AuditFilters
} from '../types/audit.types';

// Mock data
const mockComplianceScore: ComplianceScore = {
  overall: 87,
  breakdown: [
    { category: 'LGPD', score: 92, color: '#22c55e' },
    { category: 'Financeiro', score: 85, color: '#3b82f6' },
    { category: 'Operacional', score: 84, color: '#f97316' },
  ],
  trend: [
    { date: '2025-07', score: 78 },
    { date: '2025-08', score: 80 },
    { date: '2025-09', score: 82 },
    { date: '2025-10', score: 84 },
    { date: '2025-11', score: 85 },
    { date: '2025-12', score: 87 },
  ],
};

const mockRules: AuditRule[] = [
  {
    id: '1',
    name: 'Verificacao Consentimento LGPD',
    description: 'Verifica se todos os dados possuem consentimento valido',
    category: 'lgpd',
    severity: 'alta',
    status: 'ativa',
    conditions: ['consent_valid', 'consent_not_expired'],
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z',
  },
  {
    id: '2',
    name: 'Auditoria Financeira Mensal',
    description: 'Verifica consistencia dos lancamentos financeiros',
    category: 'financeiro',
    severity: 'alta',
    status: 'ativa',
    conditions: ['balance_check', 'duplicate_entries'],
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z',
  },
  {
    id: '3',
    name: 'Compliance Operacional',
    description: 'Verifica processos operacionais padronizados',
    category: 'operacional',
    severity: 'media',
    status: 'ativa',
    conditions: ['process_compliance', 'documentation_complete'],
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z',
  },
];

const mockExecutions: AuditExecution[] = [
  {
    id: '1',
    ruleId: '1',
    ruleName: 'Verificacao Consentimento LGPD',
    status: 'completo',
    startedAt: '2026-01-12T10:00:00Z',
    completedAt: '2026-01-12T10:05:00Z',
    results: [],
    anomaliesFound: 2,
  },
  {
    id: '2',
    ruleId: '2',
    ruleName: 'Auditoria Financeira Mensal',
    status: 'executando',
    startedAt: '2026-01-12T11:00:00Z',
    results: [],
    anomaliesFound: 0,
  },
];

const mockAnomalies: Anomaly[] = [
  {
    id: '1',
    executionId: '1',
    title: 'Consentimento Expirado',
    description: '15 registros com consentimento vencido detectados',
    priority: 'alta',
    status: 'pendente',
    detectedAt: '2026-01-12T10:05:00Z',
    comments: [],
    category: 'LGPD',
  },
  {
    id: '2',
    executionId: '1',
    title: 'Dados Sensíveis sem Criptografia',
    description: '3 campos de dados sensiveis sem criptografia adequada',
    priority: 'urgente',
    status: 'em_analise',
    assignedTo: { id: '1', name: 'Maria Silva' },
    detectedAt: '2026-01-12T10:05:00Z',
    comments: [
      {
        id: '1',
        userId: '1',
        userName: 'Maria Silva',
        content: 'Analisando impacto e solucao',
        createdAt: '2026-01-12T11:00:00Z',
      },
    ],
    category: 'LGPD',
  },
  {
    id: '3',
    executionId: '2',
    title: 'Lancamento Duplicado',
    description: 'Possivel lancamento duplicado detectado no modulo financeiro',
    priority: 'media',
    status: 'resolvida',
    resolvedAt: '2026-01-11T15:00:00Z',
    detectedAt: '2026-01-10T10:00:00Z',
    comments: [],
    category: 'Financeiro',
  },
];

export function useComplianceScore() {
  return useQuery({
    queryKey: ['audit', 'compliance-score'],
    queryFn: async () => {
      try {
        return await api.get<ComplianceScore>('/audit/compliance-score');
      } catch {
        return mockComplianceScore;
      }
    },
    staleTime: 1000 * 60 * 5,
  });
}

export function useAuditRules(filters?: AuditFilters) {
  return useQuery({
    queryKey: ['audit', 'rules', filters],
    queryFn: async () => {
      try {
        return await api.get<AuditRule[]>('/audit/rules', { params: filters });
      } catch {
        let filtered = [...mockRules];
        if (filters?.category) {
          filtered = filtered.filter(r => r.category === filters.category);
        }
        if (filters?.status) {
          filtered = filtered.filter(r => r.status === filters.status);
        }
        return filtered;
      }
    },
  });
}

export function useAuditExecutions() {
  return useQuery({
    queryKey: ['audit', 'executions'],
    queryFn: async () => {
      try {
        return await api.get<AuditExecution[]>('/audit/executions');
      } catch {
        return mockExecutions;
      }
    },
    refetchInterval: 5000,
  });
}

export function useAnomalies(filters?: AuditFilters) {
  return useQuery({
    queryKey: ['audit', 'anomalies', filters],
    queryFn: async () => {
      try {
        return await api.get<Anomaly[]>('/audit/anomalies', { params: filters });
      } catch {
        let filtered = [...mockAnomalies];
        if (filters?.status) {
          filtered = filtered.filter(a => a.status === filters.status);
        }
        return filtered;
      }
    },
  });
}

export function useCreateRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (rule: Omit<AuditRule, 'id' | 'createdAt' | 'updatedAt'>) => {
      return await api.post<AuditRule>('/audit/rules', rule);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit', 'rules'] });
    },
  });
}

export function useUpdateAnomaly() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Anomaly> }) => {
      return await api.patch<Anomaly>(`/audit/anomalies/${id}`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit', 'anomalies'] });
    },
  });
}

export function useRunAudit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (ruleId: string) => {
      return await api.post<AuditExecution>(`/audit/rules/${ruleId}/execute`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit', 'executions'] });
    },
  });
}
