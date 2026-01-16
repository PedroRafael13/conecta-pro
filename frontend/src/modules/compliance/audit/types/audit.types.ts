export interface AuditRule {
  id: string;
  name: string;
  description: string;
  category: 'lgpd' | 'financeiro' | 'operacional';
  severity: 'alta' | 'media' | 'baixa';
  status: 'ativa' | 'inativa';
  conditions: string[];
  createdAt: string;
  updatedAt: string;
}

export interface AuditExecution {
  id: string;
  ruleId: string;
  ruleName: string;
  status: 'executando' | 'completo' | 'erro';
  startedAt: string;
  completedAt?: string;
  results: AuditResult[];
  anomaliesFound: number;
}

export interface AuditResult {
  id: string;
  field: string;
  expected: string;
  actual: string;
  passed: boolean;
  message: string;
}

export interface Anomaly {
  id: string;
  executionId: string;
  title: string;
  description: string;
  priority: 'urgente' | 'alta' | 'media' | 'baixa';
  status: 'pendente' | 'em_analise' | 'resolvida';
  assignedTo?: {
    id: string;
    name: string;
    avatar?: string;
  };
  detectedAt: string;
  resolvedAt?: string;
  comments: AnomalyComment[];
  category: string;
}

export interface AnomalyComment {
  id: string;
  userId: string;
  userName: string;
  content: string;
  createdAt: string;
}

export interface ComplianceScore {
  overall: number;
  breakdown: {
    category: string;
    score: number;
    color: string;
  }[];
  trend: {
    date: string;
    score: number;
  }[];
}

export interface AuditFilters {
  category?: string;
  status?: string;
  dateRange?: {
    start: string;
    end: string;
  };
  severity?: string;
}
