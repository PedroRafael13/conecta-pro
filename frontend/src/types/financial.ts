/**
 * Domain Types - Módulo Financeiro
 * Tipos centralizados para garantir type-safety em todo o módulo
 */

export interface IFinancialOverview {
  receita_total: number;
  despesa_total: number;
  saldo: number;
  inadimplencia: number;
}

export interface IPayable {
  id: string;
  description: string;
  supplier_id: string;
  supplier_name: string;
  amount: number;
  due_date: string;
  status: 'pending' | 'overdue' | 'paid' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface IReceivable {
  id: string;
  description: string;
  customer_id: string;
  customer_name: string;
  amount: number;
  due_date: string;
  status: 'pending' | 'overdue' | 'paid' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface ISupplier {
  id: string;
  name: string;
  cnpj: string;
  status: 'active' | 'inactive' | 'blocked';
  rating?: number;
  created_at: string;
  updated_at: string;
}

export interface ICustomer {
  id: string;
  name: string;
  cpf_cnpj: string;
  status: 'active' | 'inactive' | 'blocked';
  credit_limit: number;
  created_at: string;
  updated_at: string;
}

export interface IBankAccount {
  id: string;
  bank_name: string;
  account_number: string;
  balance: number;
  type: 'corrente' | 'poupanca' | 'investimento';
  status: 'active' | 'inactive';
  is_main: boolean;
  created_at: string;
  updated_at: string;
}

export interface ICashflowProjection {
  date: string;
  inflow: number;
  outflow: number;
  projected_balance: number;
}

export interface IPurchaseOrder {
  id: string;
  supplier_id: string;
  supplier_name: string;
  status: 'pending' | 'approved' | 'received' | 'cancelled';
  total_amount: number;
  items_count: number;
  created_at: string;
  updated_at: string;
}

export interface IInventoryItem {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  unit_price: number;
  warehouse_id: string;
  created_at: string;
  updated_at: string;
}

export interface INFe {
  id: string;
  nfe_number: string;
  supplier_name: string;
  status: 'draft' | 'authorized' | 'cancelled' | 'denied';
  amount: number;
  issued_date: string;
  created_at: string;
  updated_at: string;
}

export interface IAccountingAccount {
  id: string;
  code: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'suspended';
  balance: number;
  created_at: string;
  updated_at: string;
}
