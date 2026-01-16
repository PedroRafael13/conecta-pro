/**
 * Tipos TypeScript para o módulo Financial
 * Baseado nos schemas Pydantic do backend
 */

// ==================== ENUMS ====================

export enum PayableStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  APPROVED = 'approved',
  SCHEDULED = 'scheduled',
  PARTIALLY_PAID = 'partially_paid',
  PAID = 'paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
}

export enum ReceivableStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  PARTIALLY_PAID = 'partially_paid',
  PAID = 'paid',
  OVERDUE = 'overdue',
  SUSPENDED = 'suspended',
  PROTESTED = 'protested',
  WRITTEN_OFF = 'written_off',
  CANCELLED = 'cancelled',
}

export enum BankAccountType {
  CHECKING = 'checking',
  SAVINGS = 'savings',
  INVESTMENT = 'investment',
  PETTY_CASH = 'petty_cash',
}

export enum BankAccountStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  CLOSED = 'closed',
}

export enum TransactionType {
  CREDIT = 'credit',
  DEBIT = 'debit',
  TRANSFER_IN = 'transfer_in',
  TRANSFER_OUT = 'transfer_out',
}

export enum TransactionStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  RECONCILED = 'reconciled',
  CANCELLED = 'cancelled',
}

export enum CashFlowEntryType {
  INCOME = 'income',
  EXPENSE = 'expense',
}

export enum SupplierType {
  INDIVIDUAL = 'individual',
  COMPANY = 'company',
}

export enum CustomerType {
  INDIVIDUAL = 'individual',
  COMPANY = 'company',
  RESIDENT = 'resident',
}

// ==================== BASE INTERFACES ====================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ==================== RECEIVABLES (CONTAS A RECEBER) ====================

export interface ReceivableAccount {
  id: string;
  condominio_id: string;
  customer_id: string;
  customer_name: string;
  customer_document?: string;
  unidade_id?: string;
  unidade_codigo?: string;
  category_id?: string;
  category_name?: string;
  description: string;
  reference?: string;
  document_number?: string;
  total_amount: number;
  paid_amount: number;
  balance: number;
  due_date: string;
  issue_date: string;
  status: ReceivableStatus;
  is_recurring: boolean;
  is_overdue: boolean;
  days_overdue?: number;
  installments_count: number;
  paid_installments_count: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ReceivableInstallment {
  id: string;
  account_id: string;
  installment_number: number;
  due_date: string;
  amount: number;
  paid_amount: number;
  balance: number;
  status: ReceivableStatus;
  boleto_number?: string;
  boleto_barcode?: string;
  pix_code?: string;
  paid_at?: string;
  payment_method?: string;
}

export interface ReceivablePayment {
  id: string;
  installment_id: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference?: string;
  bank_account_id?: string;
  is_reconciled: boolean;
  reconciled_at?: string;
  notes?: string;
}

export interface ReceivableAccountCreate {
  customer_id: string;
  unidade_id?: string;
  category_id?: string;
  description: string;
  reference?: string;
  total_amount: number;
  due_date: string;
  issue_date?: string;
  installments_count?: number;
  is_recurring?: boolean;
  recurrence_rule?: string;
  notes?: string;
}

export interface ReceivableAccountUpdate {
  description?: string;
  reference?: string;
  category_id?: string;
  due_date?: string;
  notes?: string;
}

export interface ReceivablePaymentCreate {
  amount: number;
  payment_date: string;
  payment_method: string;
  reference?: string;
  bank_account_id?: string;
  notes?: string;
}

export interface ReceivableFilter {
  customer_id?: string;
  unidade_id?: string;
  category_id?: string;
  status?: ReceivableStatus;
  due_date_start?: string;
  due_date_end?: string;
  is_recurring?: boolean;
  is_overdue?: boolean;
  min_value?: number;
  max_value?: number;
  search?: string;
}

export interface ReceivableStats {
  total_accounts: number;
  total_amount: number;
  total_paid: number;
  total_balance: number;
  overdue_count: number;
  overdue_amount: number;
  due_soon_count: number;
  due_soon_amount: number;
  by_status: Record<string, { count: number; amount: number }>;
  by_category: Record<string, { count: number; amount: number }>;
}

// ==================== PAYABLES (CONTAS A PAGAR) ====================

export interface PayableAccount {
  id: string;
  condominio_id: string;
  supplier_id: string;
  supplier_name: string;
  supplier_document?: string;
  category_id?: string;
  category_name?: string;
  description: string;
  reference?: string;
  document_number?: string;
  invoice_number?: string;
  total_amount: number;
  paid_amount: number;
  balance: number;
  due_date: string;
  issue_date: string;
  status: PayableStatus;
  is_recurring: boolean;
  is_overdue: boolean;
  days_overdue?: number;
  installments_count: number;
  paid_installments_count: number;
  approved_by?: string;
  approved_at?: string;
  scheduled_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PayableInstallment {
  id: string;
  account_id: string;
  installment_number: number;
  due_date: string;
  amount: number;
  paid_amount: number;
  balance: number;
  status: PayableStatus;
  scheduled_date?: string;
  paid_at?: string;
  payment_method?: string;
}

export interface PayablePayment {
  id: string;
  installment_id: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference?: string;
  bank_account_id?: string;
  is_reconciled: boolean;
  reconciled_at?: string;
  notes?: string;
}

export interface PayableAccountCreate {
  supplier_id: string;
  category_id?: string;
  description: string;
  reference?: string;
  document_number?: string;
  invoice_number?: string;
  total_amount: number;
  due_date: string;
  issue_date?: string;
  installments_count?: number;
  is_recurring?: boolean;
  recurrence_rule?: string;
  notes?: string;
}

export interface PayableAccountUpdate {
  description?: string;
  reference?: string;
  category_id?: string;
  due_date?: string;
  notes?: string;
}

export interface PayablePaymentCreate {
  amount: number;
  payment_date: string;
  payment_method: string;
  reference?: string;
  bank_account_id?: string;
  notes?: string;
}

export interface PayableScheduleRequest {
  scheduled_date: string;
  bank_account_id: string;
  notes?: string;
}

export interface PayableFilter {
  supplier_id?: string;
  category_id?: string;
  status?: PayableStatus;
  due_date_start?: string;
  due_date_end?: string;
  is_recurring?: boolean;
  is_overdue?: boolean;
  min_value?: number;
  max_value?: number;
  search?: string;
}

export interface PayableStats {
  total_accounts: number;
  total_amount: number;
  total_paid: number;
  total_balance: number;
  overdue_count: number;
  overdue_amount: number;
  due_soon_count: number;
  due_soon_amount: number;
  pending_approval_count: number;
  pending_approval_amount: number;
  scheduled_count: number;
  scheduled_amount: number;
  by_status: Record<string, { count: number; amount: number }>;
  by_category: Record<string, { count: number; amount: number }>;
}

// ==================== BANK ACCOUNTS ====================

export interface BankAccount {
  id: string;
  condominio_id: string;
  bank_code: string;
  bank_name: string;
  agency: string;
  account_number: string;
  account_digit?: string;
  account_type: BankAccountType;
  account_status: BankAccountStatus;
  description?: string;
  is_main: boolean;
  current_balance: number;
  available_balance: number;
  blocked_balance: number;
  last_reconciled_at?: string;
  last_reconciled_balance?: number;
  pix_key?: string;
  pix_key_type?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface BankAccountCreate {
  bank_code: string;
  bank_name: string;
  agency: string;
  account_number: string;
  account_digit?: string;
  account_type: BankAccountType;
  description?: string;
  is_main?: boolean;
  initial_balance?: number;
  pix_key?: string;
  pix_key_type?: string;
  notes?: string;
}

export interface BankAccountUpdate {
  description?: string;
  pix_key?: string;
  pix_key_type?: string;
  notes?: string;
}

export interface TransferRequest {
  from_account_id: string;
  to_account_id: string;
  amount: number;
  description?: string;
  transfer_date?: string;
}

export interface BankAccountFilter {
  account_type?: BankAccountType;
  account_status?: BankAccountStatus;
  is_main?: boolean;
}

export interface BankAccountStats {
  total_accounts: number;
  total_balance: number;
  total_available: number;
  total_blocked: number;
  by_type: Record<string, { count: number; balance: number }>;
  by_status: Record<string, number>;
}

// ==================== BANK TRANSACTIONS ====================

export interface BankTransaction {
  id: string;
  bank_account_id: string;
  bank_account_description?: string;
  account_name?: string;
  transaction_type: TransactionType;
  amount: number;
  balance_after: number;
  transaction_date: string;
  description: string;
  reference?: string;
  category?: string;
  category_name?: string;
  counterpart_name?: string;
  counterpart_document?: string;
  status: TransactionStatus;
  is_reconciled: boolean;
  reconciled_with_id?: string;
  reconciled_with_type?: string;
  import_source?: string;
  import_id?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface BankTransactionCreate {
  bank_account_id: string;
  transaction_type: TransactionType;
  amount: number;
  transaction_date: string;
  description: string;
  reference?: string;
  category?: string;
  counterpart_name?: string;
  counterpart_document?: string;
  notes?: string;
}

export interface BankTransactionUpdate {
  description?: string;
  category?: string;
  notes?: string;
}

export interface BankTransactionFilter {
  account_id?: string;
  transaction_type?: TransactionType;
  status?: TransactionStatus;
  date_start?: string;
  date_end?: string;
  is_reconciled?: boolean;
  search?: string;
}

export interface BankTransactionStats {
  total_transactions: number;
  total_credits: number;
  total_debits: number;
  net_flow: number;
  pending_count: number;
  unreconciled_count: number;
  by_type: Record<string, { count: number; amount: number }>;
}

// ==================== CASHFLOW ====================

export interface CashFlowEntry {
  id: string;
  condominio_id: string;
  entry_type: CashFlowEntryType;
  category: string;
  category_name?: string;
  subcategory?: string;
  description: string;
  amount: number;
  expected_amount: number;
  expected_date: string;
  realized_date?: string;
  realized_amount?: number;
  bank_account_id?: string;
  bank_account_description?: string;
  source_type?: string;
  source_id?: string;
  is_recurring: boolean;
  is_realized: boolean;
  recurrence_rule?: string;
  status: 'expected' | 'realized' | 'cancelled';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CashFlowEntryCreate {
  entry_type: CashFlowEntryType;
  category?: string;
  category_name?: string;
  subcategory?: string;
  description: string;
  expected_amount: number;
  expected_date: string;
  bank_account_id?: string;
  is_recurring?: boolean;
  recurrence_rule?: string;
  notes?: string;
}

export interface CashFlowEntryUpdate {
  description?: string;
  amount?: number;
  expected_date?: string;
  category?: string;
  notes?: string;
}

export interface CashFlowForecast {
  id: string;
  condominio_id: string;
  period_start: string;
  period_end: string;
  forecast_type: string;
  opening_balance: number;
  expected_income: number;
  expected_expenses: number;
  expected_closing: number;
  realized_income: number;
  realized_expenses: number;
  realized_closing: number;
  variance: number;
  variance_percentage: number;
  status: 'draft' | 'active' | 'closed';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CashFlowSummary {
  period?: string;
  opening_balance?: number;
  current_balance: number;
  total_income: number;
  total_expense: number;
  total_expenses?: number;
  net_flow: number;
  closing_balance?: number;
  projected_balance: number;
  coverage_days?: number;
  income_by_category?: Record<string, number>;
  expenses_by_category?: Record<string, number>;
}

export interface CashFlowProjection {
  date: string;
  expected_income: number;
  expected_expenses: number;
  expected_balance: number;
  realized_income?: number;
  realized_expenses?: number;
  realized_balance?: number;
}

export interface CashFlowFilter {
  entry_type?: CashFlowEntryType;
  category?: string;
  status?: string;
  date_start?: string;
  date_end?: string;
  bank_account_id?: string;
}

export interface CashFlowDashboard {
  summary: CashFlowSummary;
  daily_data: Array<{
    date: string;
    receitas: number;
    despesas: number;
    saldo: number;
    acumulado: number;
  }>;
  category_breakdown: Array<{
    category: string;
    income: number;
    expense: number;
  }>;
}

export interface CashFlowProjectionResponse {
  items: CashFlowProjection[];
  monthly_data?: Array<{
    month: string;
    realizado: number;
    projetado: number;
  }>;
}

// ==================== SUPPLIERS ====================

export interface Supplier {
  id: string;
  condominio_id: string;
  supplier_type: SupplierType;
  name: string;
  trade_name?: string;
  document: string;
  state_registration?: string;
  municipal_registration?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address?: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  bank_info?: {
    bank_code: string;
    agency: string;
    account: string;
    account_type: string;
    pix_key?: string;
  };
  category?: string;
  status: 'active' | 'blocked' | 'inactive';
  is_qualified: boolean;
  qualification_score?: number;
  qualification_date?: string;
  payment_terms?: string;
  credit_limit?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface SupplierCreate {
  supplier_type: SupplierType;
  name: string;
  trade_name?: string;
  document: string;
  state_registration?: string;
  municipal_registration?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address?: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  bank_info?: {
    bank_code: string;
    agency: string;
    account: string;
    account_type: string;
    pix_key?: string;
  };
  category?: string;
  payment_terms?: string;
  credit_limit?: number;
  notes?: string;
}

export interface SupplierUpdate {
  name?: string;
  trade_name?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address?: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  bank_info?: {
    bank_code: string;
    agency: string;
    account: string;
    account_type: string;
    pix_key?: string;
  };
  category?: string;
  payment_terms?: string;
  credit_limit?: number;
  notes?: string;
}

export interface SupplierFilter {
  supplier_type?: SupplierType;
  status?: 'active' | 'blocked' | 'inactive';
  category?: string;
  is_qualified?: boolean;
  search?: string;
}

export interface SupplierStats {
  total_suppliers: number;
  active_count: number;
  blocked_count: number;
  qualified_count: number;
  avg_qualification_score: number;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
}

// ==================== CUSTOMERS ====================

export interface Customer {
  id: string;
  condominio_id: string;
  customer_type: CustomerType;
  name: string;
  document: string;
  email?: string;
  phone?: string;
  mobile?: string;
  morador_id?: string;
  unidade_id?: string;
  unidade_codigo?: string;
  address?: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  status: 'active' | 'blocked' | 'inactive';
  credit_limit?: number;
  total_debt: number;
  overdue_debt: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerCreate {
  customer_type: CustomerType;
  name: string;
  document: string;
  email?: string;
  phone?: string;
  mobile?: string;
  morador_id?: string;
  unidade_id?: string;
  address?: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  credit_limit?: number;
  notes?: string;
}

export interface CustomerUpdate {
  name?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  address?: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  credit_limit?: number;
  notes?: string;
}

export interface CustomerFilter {
  customer_type?: CustomerType;
  status?: 'active' | 'blocked' | 'inactive';
  has_debt?: boolean;
  search?: string;
}

// ==================== BILLING RULES ====================

export interface BillingRule {
  id: string;
  condominio_id: string;
  name: string;
  description?: string;
  category_id?: string;
  category_name?: string;
  billing_type: 'fixed' | 'variable' | 'calculated';
  base_amount?: number;
  calculation_formula?: string;
  recurrence: 'monthly' | 'bimonthly' | 'quarterly' | 'semiannual' | 'annual';
  day_of_month: number;
  applies_to: 'all_units' | 'selected_units' | 'unit_type';
  unit_filter?: Record<string, any>;
  status: 'active' | 'paused' | 'cancelled';
  last_generated_at?: string;
  next_generation_at?: string;
  generation_count: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface BillingRuleCreate {
  name: string;
  description?: string;
  category_id?: string;
  billing_type: 'fixed' | 'variable' | 'calculated';
  base_amount?: number;
  calculation_formula?: string;
  recurrence: 'monthly' | 'bimonthly' | 'quarterly' | 'semiannual' | 'annual';
  day_of_month: number;
  applies_to: 'all_units' | 'selected_units' | 'unit_type';
  unit_filter?: Record<string, any>;
  notes?: string;
}

export interface BillingRuleUpdate {
  name?: string;
  description?: string;
  base_amount?: number;
  day_of_month?: number;
  notes?: string;
}

// ==================== RECEIVABLE CATEGORIES ====================

export interface ReceivableCategory {
  id: string;
  condominio_id: string;
  code: string;
  name: string;
  description?: string;
  parent_id?: string;
  parent_name?: string;
  level: number;
  path: string;
  accounting_account_id?: string;
  is_system: boolean;
  is_active: boolean;
  children_count: number;
  created_at: string;
  updated_at: string;
}

export interface ReceivableCategoryCreate {
  code: string;
  name: string;
  description?: string;
  parent_id?: string;
  accounting_account_id?: string;
}

export interface ReceivableCategoryUpdate {
  code?: string;
  name?: string;
  description?: string;
  accounting_account_id?: string;
}

// ==================== DASHBOARD ====================

export interface FinancialDashboard {
  period?: string;
  // Saldos
  total_balance?: number;
  available_balance?: number;
  // Para página de Dashboard
  total_income: number;
  total_expense: number;
  net_balance: number;
  monthly_data?: Array<{ month: string; receitas: number; despesas: number }>;
  expenses_by_category?: Array<{ name: string; value: number; color?: string }>;
  revenue_by_client?: Array<{ name: string; value: number }>;
  // Receitas
  total_receivables?: number;
  received_amount?: number;
  pending_receivables?: number;
  overdue_receivables?: number;
  // Despesas
  total_payables?: number;
  paid_amount?: number;
  pending_payables?: number;
  overdue_payables?: number;
  // Fluxo
  net_flow?: number;
  projected_balance?: number;
  // Tendências
  income_trend?: Array<{ date: string; amount: number }>;
  expense_trend?: Array<{ date: string; amount: number }>;
  balance_trend?: Array<{ date: string; amount: number }>;
  // Breakdowns
  receivables_by_category?: Array<{ category: string; amount: number; percentage: number }>;
  payables_by_category?: Array<{ category: string; amount: number; percentage: number }>;
  // Alertas
  alerts?: Array<{
    type: 'overdue' | 'due_soon' | 'low_balance' | 'pending_approval';
    severity: 'info' | 'warning' | 'danger';
    message: string;
    count?: number;
    amount?: number;
  }>;
}

export interface FinancialKPIs {
  revenue_growth: number;
  expense_growth: number;
  profit_margin: number;
  collection_rate?: number;
  payment_rate?: number;
}

// ==================== EXPORT TYPES ====================

export type ReceivableStatusType = `${ReceivableStatus}`;
export type PayableStatusType = `${PayableStatus}`;
export type BankAccountTypeType = `${BankAccountType}`;
export type TransactionTypeType = `${TransactionType}`;
