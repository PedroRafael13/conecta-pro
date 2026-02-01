/**
 * Types gerados para o módulo Config
 * Schemas de request/response para todos os endpoints
 */

// ==================== Tenant ====================

export interface TenantCreate {
  codigo: string;
  nome: string;
  email: string;
  cnpj?: string;
  telefone?: string;
  plan?: 'free' | 'starter' | 'pro' | 'enterprise';
  tenant_type?: string;
  max_users?: number;
  max_units?: number;
  features_enabled?: string[];
  settings?: Record<string, unknown>;
}

export interface TenantUpdate {
  nome?: string;
  email?: string;
  cnpj?: string;
  telefone?: string;
  tenant_type?: string;
  settings?: Record<string, unknown>;
}

export interface TenantPlanUpdate {
  plan: 'free' | 'starter' | 'pro' | 'enterprise';
  max_users?: number;
  max_units?: number;
}

export interface TenantAddressUpdate {
  logradouro?: string;
  numero?: string;
  complemento?: string;
  bairro?: string;
  cidade?: string;
  estado?: string;
  cep?: string;
}

export interface TenantResponse {
  id: string;
  codigo: string;
  nome: string;
  email: string;
  cnpj?: string;
  telefone?: string;
  plan: string;
  tenant_type?: string;
  status: 'active' | 'trial' | 'suspended' | 'canceled' | 'inactive';
  max_users: number;
  max_units: number;
  current_users?: number;
  features_enabled?: string[];
  settings?: Record<string, unknown>;
  address?: TenantAddress;
  ativo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TenantAddress {
  logradouro?: string;
  numero?: string;
  complemento?: string;
  bairro?: string;
  cidade?: string;
  estado?: string;
  cep?: string;
}

export interface TenantList {
  items: TenantResponse[];
  total: number;
  skip: number;
  limit: number;
}

// ==================== Feature Flag ====================

export interface FeatureFlagCreate {
  codigo: string;
  nome: string;
  descricao?: string;
  flag_type?: 'boolean' | 'percentage' | 'gradual' | 'whitelist';
  category?: string;
  owner_team?: string;
}

export interface FeatureFlagUpdate {
  nome?: string;
  descricao?: string;
  flag_type?: 'boolean' | 'percentage' | 'gradual' | 'whitelist';
  category?: string;
  owner_team?: string;
}

export interface FeatureFlagGradualRollout {
  start_percentage: number;
  end_percentage: number;
  start_date: string;
  end_date: string;
}

export interface FeatureFlagTenantToggle {
  tenant_id: string;
  enabled: boolean;
}

export interface FeatureFlagEvaluate {
  flag_key?: string;
  tenant_id?: string;
  user_id?: string;
  context?: Record<string, unknown>;
}

export interface FeatureFlagEvaluateResponse {
  enabled: boolean;
  flag_key: string;
  reason: string;
  variant?: string;
}

export interface FeatureFlagResponse {
  id: string;
  codigo: string;
  nome: string;
  descricao?: string;
  flag_type: string;
  category?: string;
  owner_team?: string;
  status: string;
  rollout_percentage?: number;
  gradual_rollout?: FeatureFlagGradualRollout;
  tenant_overrides?: Record<string, boolean>;
  ativo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface FeatureFlagList {
  items: FeatureFlagResponse[];
  total: number;
  skip: number;
  limit: number;
}

// ==================== System Config ====================

export interface SystemConfigCreate {
  chave: string;
  valor: unknown;
  descricao?: string;
  value_type?: 'string' | 'number' | 'boolean' | 'json';
  category?: string;
  scope?: string;
  admin_only?: boolean;
  cacheable?: boolean;
  requires_restart?: boolean;
}

export interface SystemConfigUpdate {
  valor?: unknown;
  descricao?: string;
  value_type?: 'string' | 'number' | 'boolean' | 'json';
  category?: string;
  scope?: string;
  admin_only?: boolean;
  cacheable?: boolean;
  requires_restart?: boolean;
}

export interface SystemConfigResponse {
  id: string;
  chave: string;
  valor: unknown;
  descricao?: string;
  value_type: string;
  category?: string;
  scope?: string;
  admin_only?: boolean;
  cacheable?: boolean;
  requires_restart?: boolean;
  ativo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SystemConfigList {
  items: SystemConfigResponse[];
  total: number;
  skip: number;
  limit: number;
}

// ==================== Tenant Settings ====================

export interface TenantSettingsCreate {
  chave: string;
  valor: unknown;
  descricao?: string;
  value_type?: 'string' | 'number' | 'boolean' | 'json';
  category?: string;
  default_value?: unknown;
}

export interface TenantSettingsUpdate {
  valor?: unknown;
  descricao?: string;
  value_type?: 'string' | 'number' | 'boolean' | 'json';
  category?: string;
}

export interface TenantSettingsValueUpdate {
  valor: unknown;
}

export interface TenantSettingsResponse {
  id: string;
  tenant_id: string;
  chave: string;
  valor: unknown;
  descricao?: string;
  value_type: string;
  category?: string;
  default_value?: unknown;
  is_custom?: boolean;
  ativo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TenantSettingsList {
  items: TenantSettingsResponse[];
  total: number;
  skip: number;
  limit: number;
}

// ==================== Notification Template ====================

export interface NotificationTemplateCreate {
  codigo: string;
  nome: string;
  descricao?: string;
  channel: 'email' | 'sms' | 'push' | 'whatsapp' | 'in_app';
  category?: string;
  subject?: string;
  body_html?: string;
  body_text?: string;
  email_subject?: string;
  sms_body?: string;
  push_title?: string;
  push_body?: string;
  in_app_title?: string;
  in_app_body?: string;
  variables?: string[];
}

export interface NotificationTemplateUpdate {
  nome?: string;
  descricao?: string;
  channel?: 'email' | 'sms' | 'push' | 'whatsapp' | 'in_app';
  category?: string;
  subject?: string;
  body_html?: string;
  body_text?: string;
  email_subject?: string;
  sms_body?: string;
  push_title?: string;
  push_body?: string;
  in_app_title?: string;
  in_app_body?: string;
  variables?: string[];
}

export interface NotificationTemplateRender {
  variables: Record<string, unknown>;
  channel?: string;
}

export interface NotificationTemplateRenderResponse {
  subject?: string;
  body_html?: string;
  body_text?: string;
  title?: string;
  body?: string;
  channel: string;
}

export interface NotificationTemplateResponse {
  id: string;
  codigo: string;
  nome: string;
  descricao?: string;
  channel: string;
  category?: string;
  subject?: string;
  body_html?: string;
  body_text?: string;
  email_subject?: string;
  sms_body?: string;
  push_title?: string;
  push_body?: string;
  in_app_title?: string;
  in_app_body?: string;
  variables?: string[];
  version?: number;
  ativo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface NotificationTemplateList {
  items: NotificationTemplateResponse[];
  total: number;
  skip: number;
  limit: number;
}

// ==================== Dashboards ====================

export interface ConfigDashboard {
  total_tenants: number;
  active_tenants: number;
  trial_tenants: number;
  suspended_tenants: number;
  total_feature_flags: number;
  active_feature_flags: number;
  total_system_configs: number;
  total_templates: number;
  active_templates: number;
  recent_tenants: TenantResponse[];
  tenants_by_plan: Record<string, number>;
  templates_by_channel: Record<string, number>;
}

export interface TenantDashboard {
  tenant: TenantResponse;
  total_users: number;
  total_settings: number;
  features_count: number;
  storage_used?: number;
  storage_limit?: number;
}
