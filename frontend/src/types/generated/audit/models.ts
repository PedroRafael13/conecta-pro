/**
 * Audit Module Type Stubs
 * Tipos para hooks e services de auditoria
 */

export interface AuditLogResponse {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  user_name?: string;
  details?: Record<string, unknown>;
  ip_address?: string;
  created_at: string;
  [key: string]: unknown;
}

export interface AuditLogCreate {
  action: string;
  entity_type: string;
  entity_id: string;
  details?: Record<string, unknown>;
}

export interface AuditLogList {
  items: AuditLogResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface AuditLogStats {
  total_logs: number;
  logs_today: number;
  logs_this_week: number;
  top_actions: Array<{ action: string; count: number }>;
  top_users: Array<{ user_id: string; user_name: string; count: number }>;
  [key: string]: unknown;
}

export interface AccessHistoryResponse {
  id: string;
  user_id: string;
  user_name?: string;
  action: string;
  resource: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
  [key: string]: unknown;
}

export interface AccessHistoryCreate {
  user_id: string;
  action: string;
  resource: string;
  ip_address?: string;
  user_agent?: string;
}

export interface AccessHistoryList {
  items: AccessHistoryResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface AccessHistoryStats {
  total_accesses: number;
  unique_users: number;
  accesses_today: number;
  top_resources: Array<{ resource: string; count: number }>;
  [key: string]: unknown;
}

export interface ComplianceRuleResponse {
  id: string;
  name: string;
  description?: string;
  category: string;
  severity: string;
  is_active: boolean;
  conditions?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface ComplianceRuleCreate {
  name: string;
  description?: string;
  category: string;
  severity: string;
  conditions?: Record<string, unknown>;
}

export interface ComplianceRuleUpdate {
  name?: string;
  description?: string;
  category?: string;
  severity?: string;
  is_active?: boolean;
  conditions?: Record<string, unknown>;
}

export interface ComplianceRuleList {
  items: ComplianceRuleResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface ComplianceCheckResponse {
  id: string;
  rule_id: string;
  rule_name?: string;
  status: string;
  result?: string;
  details?: Record<string, unknown>;
  checked_at: string;
  [key: string]: unknown;
}

export interface ComplianceCheckCreate {
  rule_id: string;
  details?: Record<string, unknown>;
}

export interface ComplianceCheckList {
  items: ComplianceCheckResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface ComplianceOverview {
  total_rules: number;
  active_rules: number;
  compliant: number;
  non_compliant: number;
  pending: number;
  compliance_rate: number;
  [key: string]: unknown;
}

export interface DataRetentionResponse {
  id: string;
  name: string;
  entity_type: string;
  retention_days: number;
  is_active: boolean;
  last_execution?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface DataRetentionCreate {
  name: string;
  entity_type: string;
  retention_days: number;
}

export interface DataRetentionUpdate {
  name?: string;
  retention_days?: number;
  is_active?: boolean;
}

export interface DataRetentionList {
  items: DataRetentionResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface DataRetentionExecution {
  id: string;
  policy_id: string;
  status: string;
  records_processed: number;
  records_deleted: number;
  started_at: string;
  completed_at?: string;
  [key: string]: unknown;
}

export interface AuditDashboard {
  total_logs: number;
  logs_today: number;
  compliance_rate: number;
  active_rules: number;
  recent_logs: AuditLogResponse[];
  compliance_overview: ComplianceOverview;
  [key: string]: unknown;
}

export interface SecurityOverview {
  total_events: number;
  critical_events: number;
  warnings: number;
  compliance_status: string;
  [key: string]: unknown;
}
