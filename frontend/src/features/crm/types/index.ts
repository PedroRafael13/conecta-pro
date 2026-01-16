/**
 * Tipos TypeScript para o módulo CRM
 * Espelha os schemas Pydantic do backend
 */

// ==================== ENUMS ====================

export enum LeadStatus {
  NEW = 'new',
  CONTACTED = 'contacted',
  QUALIFIED = 'qualified',
  PROPOSAL = 'proposal',
  NEGOTIATION = 'negotiation',
  WON = 'won',
  LOST = 'lost',
}

export enum LeadSource {
  WEBSITE = 'website',
  REFERRAL = 'referral',
  SOCIAL_MEDIA = 'social_media',
  COLD_CALL = 'cold_call',
  EMAIL_CAMPAIGN = 'email_campaign',
  EVENT = 'event',
  PARTNER = 'partner',
  OTHER = 'other',
}

export enum OpportunityStage {
  QUALIFICATION = 'qualification',
  NEEDS_ANALYSIS = 'needs_analysis',
  PROPOSAL = 'proposal',
  NEGOTIATION = 'negotiation',
  CLOSED_WON = 'closed_won',
  CLOSED_LOST = 'closed_lost',
}

export enum OpportunityPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum LossReason {
  PRICE = 'price',
  COMPETITOR = 'competitor',
  NO_BUDGET = 'no_budget',
  NO_DECISION = 'no_decision',
  TIMING = 'timing',
  PRODUCT_FIT = 'product_fit',
  NO_RESPONSE = 'no_response',
  OTHER = 'other',
}

export enum ProposalStatus {
  DRAFT = 'draft',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  SENT = 'sent',
  VIEWED = 'viewed',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled',
}

export enum ProposalType {
  SERVICE = 'service',
  PRODUCT = 'product',
  MIXED = 'mixed',
}

export enum DiscountType {
  PERCENTAGE = 'percentage',
  FIXED = 'fixed',
}

export enum ContractStatus {
  DRAFT = 'draft',
  PENDING_SIGNATURE = 'pending_signature',
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  TERMINATED = 'terminated',
  EXPIRED = 'expired',
}

export enum ContractType {
  RECURRING = 'recurring',
  FIXED = 'fixed',
}

export enum AdjustmentIndex {
  IPCA = 'ipca',
  IGPM = 'igpm',
  INPC = 'inpc',
  FIXED = 'fixed',
}

export enum CommissionStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  PAID = 'paid',
  CANCELLED = 'cancelled',
}

export enum CommissionType {
  PERCENTAGE = 'percentage',
  FIXED = 'fixed',
  PROGRESSIVE = 'progressive',
}

export enum CommissionTrigger {
  ON_CLOSE = 'on_close',
  ON_FIRST_PAYMENT = 'on_first_payment',
  ON_FULL_PAYMENT = 'on_full_payment',
  MONTHLY = 'monthly',
}

export enum PaymentMethod {
  PAYROLL = 'payroll',
  TRANSFER = 'transfer',
  PIX = 'pix',
  CHECK = 'check',
}

export enum ContractCategory {
  SECURITY = 'security',
  CLEANING = 'cleaning',
  MAINTENANCE = 'maintenance',
  FACILITIES = 'facilities',
  MIXED = 'mixed',
  CONSULTING = 'consulting',
  OUTSOURCING = 'outsourcing',
}

// ==================== LEAD TYPES ====================

export interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  company: string | null;
  position: string | null;
  company_size: string | null;
  industry: string | null;
  source: LeadSource;
  status: LeadStatus;
  score: number;
  probability: number;
  expected_value: number;
  notes: string | null;
  assigned_to_id: string | null;
  last_contact_at: string | null;
  next_contact_at: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Propriedades calculadas
  is_hot: boolean;
  is_qualified: boolean;
  weighted_value: number;
}

export interface LeadCreate {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  position?: string;
  company_size?: string;
  industry?: string;
  source?: LeadSource;
  notes?: string;
  assigned_to_id?: string;
  expected_value?: number;
}

export interface LeadUpdate {
  name?: string;
  email?: string;
  phone?: string;
  company?: string;
  position?: string;
  company_size?: string;
  industry?: string;
  source?: LeadSource;
  status?: LeadStatus;
  notes?: string;
  assigned_to_id?: string;
  expected_value?: number;
  next_contact_at?: string;
}

export interface LeadStatusUpdate {
  status: LeadStatus;
  notes?: string;
}

export interface LeadFilter {
  status?: LeadStatus;
  source?: LeadSource;
  assigned_to_id?: string;
  min_score?: number;
  max_score?: number;
  is_hot?: boolean;
  company?: string;
  search?: string;
}

export interface LeadStats {
  total: number;
  by_status: Record<string, number>;
  by_source: Record<string, number>;
  hot_leads: number;
  avg_score: number;
  total_expected_value: number;
  total_weighted_value: number;
}

// ==================== OPPORTUNITY TYPES ====================

export interface Opportunity {
  id: string;
  title: string;
  description: string | null;
  lead_id: string | null;
  contact_name: string;
  contact_email: string;
  contact_phone: string | null;
  company_name: string | null;
  stage: OpportunityStage;
  priority: OpportunityPriority;
  value: number;
  probability: number;
  weighted_value: number;
  expected_close_date: string | null;
  actual_close_date: string | null;
  owner_id: string | null;
  loss_reason: LossReason | null;
  competitor: string | null;
  win_notes: string | null;
  loss_notes: string | null;
  notes: string | null;
  is_open: boolean;
  is_won: boolean;
  is_lost: boolean;
  is_overdue: boolean;
  days_in_pipeline: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OpportunityCreate {
  title: string;
  description?: string;
  contact_name: string;
  contact_email: string;
  contact_phone?: string;
  company_name?: string;
  lead_id?: string;
  stage?: OpportunityStage;
  priority?: OpportunityPriority;
  value?: number;
  probability?: number;
  expected_close_date?: string;
  owner_id?: string;
  notes?: string;
}

export interface OpportunityCreateFromLead {
  lead_id: string;
  title: string;
  description?: string;
  value?: number;
  probability?: number;
  expected_close_date?: string;
  priority?: OpportunityPriority;
  owner_id?: string;
  notes?: string;
}

export interface OpportunityUpdate {
  title?: string;
  description?: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  company_name?: string;
  stage?: OpportunityStage;
  priority?: OpportunityPriority;
  value?: number;
  probability?: number;
  expected_close_date?: string;
  owner_id?: string;
  notes?: string;
}

export interface OpportunityStageUpdate {
  stage: OpportunityStage;
  notes?: string;
}

export interface OpportunityClose {
  won: boolean;
  actual_close_date?: string;
  notes?: string;
  loss_reason?: LossReason;
  competitor?: string;
}

export interface OpportunityFilter {
  stage?: OpportunityStage;
  priority?: OpportunityPriority;
  owner_id?: string;
  is_open?: boolean;
  is_overdue?: boolean;
  min_value?: number;
  max_value?: number;
  company_name?: string;
  search?: string;
}

export interface PipelineStats {
  total_opportunities: number;
  open_opportunities: number;
  won_opportunities: number;
  lost_opportunities: number;
  total_value: number;
  weighted_value: number;
  won_value: number;
  lost_value: number;
  win_rate: number;
  avg_deal_size: number;
  avg_days_to_close: number;
  by_stage: Record<string, number>;
  by_priority: Record<string, number>;
  overdue_count: number;
}

// ==================== PROPOSAL TYPES ====================

export interface ProposalItem {
  id: string;
  proposal_id: string;
  code: string | null;
  name: string;
  description: string | null;
  unit: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  total: number;
  subtotal: number;
  discount_amount: number;
  is_optional: boolean;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProposalItemCreate {
  code?: string;
  name: string;
  description?: string;
  unit?: string;
  quantity?: number;
  unit_price?: number;
  discount_percent?: number;
  is_optional?: boolean;
  sort_order?: number;
}

export interface Proposal {
  id: string;
  number: string;
  proposal_number: string;
  version: number;
  parent_id: string | null;
  opportunity_id: string | null;
  opportunity: { id: string; title: string; company_name: string | null; client_name?: string; contact_name?: string } | null;
  template_id: string | null;
  template: { id: string; name: string } | null;
  // Cliente
  client_name: string;
  client_email: string;
  client_phone: string | null;
  client_company: string | null;
  client_document: string | null;
  client_address: string | null;
  // Conteudo
  title: string;
  description: string | null;
  proposal_type: ProposalType;
  terms_conditions: string | null;
  notes: string | null;
  // Valores
  subtotal: number;
  discount_type: DiscountType | null;
  discount_value: number;
  discount_percent: number;
  discount_reason: string | null;
  discount_amount: number;
  taxes: number;
  total: number;
  final_value: number;
  // Pagamento
  payment_terms: string | null;
  payment_conditions: string | null;
  installments: number;
  // Datas
  issue_date: string;
  valid_until: string | null;
  sent_at: string | null;
  viewed_at: string | null;
  responded_at: string | null;
  // Status
  status: ProposalStatus;
  rejection_reason: string | null;
  // Responsaveis
  created_by_id: string | null;
  created_by: { id: string; name: string } | null;
  approved_by_id: string | null;
  approved_at: string | null;
  // Propriedades calculadas
  is_draft: boolean;
  is_pending: boolean;
  is_approved: boolean;
  is_sent: boolean;
  is_closed: boolean;
  is_accepted: boolean;
  is_expired: boolean;
  days_until_expiry: number | null;
  item_count: number;
  // Controle
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProposalDetail extends Proposal {
  items: ProposalItem[];
}

export interface ProposalCreate {
  title: string;
  description?: string;
  proposal_type?: ProposalType;
  client_name?: string;
  client_email?: string;
  client_phone?: string;
  client_company?: string;
  client_document?: string;
  client_address?: string;
  opportunity_id?: string;
  template_id?: string;
  template?: string;
  terms_conditions?: string;
  payment_terms?: string;
  payment_conditions?: string;
  warranty_terms?: string;
  delivery_terms?: string;
  installments?: number;
  notes?: string;
  valid_until?: string;
  discount_type?: DiscountType;
  discount_value?: number;
  discount_percent?: number;
  discount_reason?: string;
  taxes?: number;
  items?: ProposalItemCreate[];
}

export interface ProposalUpdate {
  title?: string;
  description?: string;
  proposal_type?: ProposalType;
  client_name?: string;
  client_email?: string;
  client_phone?: string;
  client_company?: string;
  client_document?: string;
  client_address?: string;
  terms_conditions?: string;
  payment_terms?: string;
  payment_conditions?: string;
  installments?: number;
  notes?: string;
  valid_until?: string;
  discount_type?: DiscountType;
  discount_value?: number;
  discount_reason?: string;
  taxes?: number;
}

export interface ProposalFilter {
  status?: ProposalStatus;
  proposal_type?: ProposalType;
  opportunity_id?: string;
  created_by_id?: string;
  is_expired?: boolean;
  min_value?: number;
  max_value?: number;
  client_name?: string;
  search?: string;
  date_from?: string;
  date_to?: string;
}

export interface ProposalStats {
  total: number;
  total_proposals: number;
  draft_count: number;
  pending_count: number;
  sent_count: number;
  accepted_count: number;
  rejected_count: number;
  expired_count: number;
  total_value: number;
  accepted_value: number;
  pending_value: number;
  acceptance_rate: number;
  conversion_rate: number;
  avg_value: number;
  avg_proposal_value: number;
  avg_response_time_days: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
}

// ==================== CONTRACT TYPES ====================

export interface ContractItem {
  id: string;
  service_type: string;
  service_name: string;
  description: string | null;
  quantity: number;
  unit_price: number;
  total_price: number;
  notes: string | null;
  created_at: string;
}

export interface Contract {
  id: string;
  contract_number: string;
  name: string;
  title: string;
  description: string | null;
  notes: string | null;
  contract_type: ContractType;
  status: ContractStatus;
  category: ContractCategory;
  client_id: string;
  client_name: string;
  client_document: string | null;
  monthly_value: number;
  total_value: number;
  start_date: string;
  end_date: string | null;
  auto_renewal: boolean;
  adjustment_enabled: boolean;
  adjustment_index: AdjustmentIndex | null;
  has_sla: boolean;
  created_at: string;
  updated_at: string | null;
  // Propriedades calculadas
  is_active_contract: boolean;
  is_expiring_soon: boolean;
  days_until_end: number | null;
  days_until_expiry: number | null;
  needs_adjustment: boolean;
}

export interface ContractDetail extends Contract {
  description: string | null;
  opportunity_id: string | null;
  proposal_id: string | null;
  template_id: string | null;
  setup_fee: number;
  grace_period_days: number;
  notice_period_days: number;
  renewal_period_months: number;
  renewal_notification_days: number;
  adjustment_index: AdjustmentIndex | null;
  adjustment_fixed_percent: number | null;
  adjustment_base_date: string | null;
  last_adjustment_date: string | null;
  next_adjustment_date: string | null;
  sla_config: Record<string, unknown> | null;
  content: string | null;
  clauses: Record<string, unknown>[] | null;
  signature_required: boolean;
  signature_provider: string | null;
  signed_at: string | null;
  signed_by_client: string | null;
  signed_by_company: string | null;
  pdf_file_path: string | null;
  commercial_manager_id: string | null;
  account_manager_id: string | null;
  created_by: string | null;
  items: ContractItem[];
}

export interface ContractCreate {
  name: string;
  title?: string;
  description?: string;
  contract_type?: ContractType;
  category?: ContractCategory;
  monthly_value: number;
  total_value?: number;
  setup_fee?: number;
  start_date: string;
  end_date?: string;
  grace_period_days?: number;
  notice_period_days?: number;
  auto_renewal?: boolean;
  renewal_period_months?: number;
  renewal_notification_days?: number;
  adjustment_enabled?: boolean;
  adjustment_index?: AdjustmentIndex;
  adjustment_fixed_percent?: number;
  adjustment_base_date?: string;
  has_sla?: boolean;
  sla_config?: Record<string, unknown>;
  signature_required?: boolean;
  signature_provider?: string;
  client_id: string;
  client_name?: string;
  client_document?: string;
  opportunity_id?: string;
  proposal_id?: string;
  template_id?: string;
  content?: string;
  clauses?: Record<string, unknown>[];
  commercial_manager_id?: string;
  account_manager_id?: string;
}

export interface ContractUpdate {
  name?: string;
  description?: string;
  monthly_value?: number;
  total_value?: number;
  setup_fee?: number;
  end_date?: string;
  grace_period_days?: number;
  notice_period_days?: number;
  auto_renewal?: boolean;
  renewal_period_months?: number;
  renewal_notification_days?: number;
  adjustment_enabled?: boolean;
  adjustment_index?: AdjustmentIndex;
  adjustment_fixed_percent?: number;
  has_sla?: boolean;
  sla_config?: Record<string, unknown>;
  commercial_manager_id?: string;
  account_manager_id?: string;
}

export interface ContractFilter {
  status?: ContractStatus;
  contract_type?: ContractType;
  client_id?: string;
  commercial_manager_id?: string;
  account_manager_id?: string;
  is_expiring_soon?: boolean;
  needs_adjustment?: boolean;
  has_sla?: boolean;
  min_value?: number;
  max_value?: number;
  start_date_from?: string;
  start_date_to?: string;
  end_date_from?: string;
  end_date_to?: string;
  search?: string;
}

export interface ContractStats {
  total_contracts: number;
  active_contracts: number;
  active_count: number;
  total_monthly_revenue: number;
  total_monthly_value: number;
  average_contract_value: number;
  expiring_soon: number;
  needs_adjustment: number;
  avg_sla: number;
  pending_signature: number;
  total_employees: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
}

// ==================== COMMISSION TYPES ====================

export interface CommissionRule {
  id: string;
  name: string;
  description: string | null;
  commission_type: CommissionType;
  base_value: number;
  min_value: number | null;
  max_value: number | null;
  trigger: CommissionTrigger;
  trigger_delay_days: number;
  progressive_scale: string | null;
  applies_to_all: boolean;
  product_categories: string | null;
  service_types: string | null;
  min_sale_value: number | null;
  max_sale_value: number | null;
  valid_from: string;
  valid_until: string | null;
  priority: number;
  is_valid: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by_id: string | null;
}

export interface CommissionRuleCreate {
  name: string;
  description?: string;
  commission_type?: CommissionType;
  base_value?: number;
  min_value?: number;
  max_value?: number;
  trigger?: CommissionTrigger;
  trigger_delay_days?: number;
  progressive_scale?: { min: number; max: number; rate: number }[];
  applies_to_all?: boolean;
  product_categories?: string[];
  service_types?: string[];
  min_sale_value?: number;
  max_sale_value?: number;
  valid_from?: string;
  valid_until?: string;
  priority?: number;
}

export interface Commission {
  id: string;
  reference_number: string;
  seller_id: string | null;
  proposal_id: string | null;
  rule_id: string | null;
  // Vendedor
  salesperson_name: string;
  salesperson_code: string | null;
  // Período
  period: string;
  period_start: string | null;
  period_end: string | null;
  // Valores da venda
  sale_value: number;
  sale_margin: number;
  total_sales: number;
  contracts_count: number;
  // Cálculo
  commission_type: string;
  commission_rate: number;
  base_commission: number;
  commission_value: number;
  bonuses: number;
  deductions: number;
  adjustments: number;
  final_commission: number;
  net_commission: number;
  // Status
  status: CommissionStatus;
  trigger: string;
  trigger_date: string | null;
  due_date: string | null;
  paid_date: string | null;
  // Descrição
  description: string | null;
  notes: string | null;
  // Propriedades calculadas
  is_pending: boolean;
  is_approved: boolean;
  is_paid: boolean;
  paid_amount: number;
  pending_amount: number;
  is_overdue: boolean;
  days_until_due: number | null;
  // Controle
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by_id: string | null;
  approved_by_id: string | null;
  approved_at: string | null;
}

export interface CommissionCreate {
  seller_id: string;
  proposal_id?: string;
  sale_value: number;
  sale_margin?: number;
  description?: string;
  notes?: string;
  rule_id?: string;
  commission_type?: CommissionType;
  commission_rate?: number;
  trigger?: CommissionTrigger;
  trigger_date?: string;
  due_date?: string;
  period_start?: string;
  period_end?: string;
}

export interface CommissionFilter {
  seller_id?: string;
  proposal_id?: string;
  status?: CommissionStatus;
  trigger?: CommissionTrigger;
  is_overdue?: boolean;
  min_value?: number;
  max_value?: number;
  date_from?: string;
  date_to?: string;
  due_date_from?: string;
  due_date_to?: string;
}

export interface CommissionStats {
  total_commissions: number;
  pending_count: number;
  approved_count: number;
  paid_count: number;
  cancelled_count: number;
  total_value: number;
  pending_value: number;
  approved_value: number;
  paid_value: number;
  overdue_count: number;
  overdue_value: number;
  avg_commission_value: number;
  avg_days_to_payment: number;
  // Propriedades adicionais para dashboard
  total_sales: number;
  avg_rate: number;
  salespeople_count: number;
  trend_data: { period: string; value: number; sales: number }[];
  by_status: Record<string, number>;
  by_trigger: Record<string, number>;
  by_month: Record<string, number>;
}

export interface SellerCommissionStats {
  seller_id: string;
  seller_name: string | null;
  name: string;
  total_sales: number;
  total_commission: number;
  total_commissions: number;
  pending_commissions: number;
  paid_commissions: number;
  commission_rate_avg: number;
  sales_count: number;
  contracts_count: number;
  conversion_rate: number;
  current_month_sales: number;
  current_month_commissions: number;
  target: number | null;
  target_percentage: number | null;
  trend: 'up' | 'down' | 'stable';
}

// ==================== DASHBOARD TYPES ====================

export interface CRMDashboardKPIs {
  total_leads: number;
  hot_leads: number;
  lead_conversion_rate: number;
  total_opportunities: number;
  open_opportunities: number;
  pipeline_value: number;
  weighted_pipeline_value: number;
  win_rate: number;
  avg_deal_size: number;
  avg_sales_cycle: number;
  total_proposals: number;
  pending_proposals: number;
  acceptance_rate: number;
  active_contracts: number;
  mrr: number;
  pending_commissions: number;
}

export interface FunnelData {
  stage: string;
  count: number;
  value: number;
  conversion_rate: number;
}

export interface TrendData {
  period: string;
  leads: number;
  opportunities: number;
  won: number;
  value: number;
}

// ==================== PAGINATED RESPONSES ====================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type LeadListResponse = PaginatedResponse<Lead>;
export type OpportunityListResponse = PaginatedResponse<Opportunity>;
export type ProposalListResponse = PaginatedResponse<Proposal>;
export type ContractListResponse = PaginatedResponse<Contract>;
export type CommissionListResponse = PaginatedResponse<Commission>;
export type CommissionRuleListResponse = PaginatedResponse<CommissionRule>;
