/**
 * Banking Service
 *
 * Consulta saldos, extratos e status dos bancos integrados (Cora, Inter).
 */

import api from '@/lib/api';

export interface BankBalance {
  bank_code: string;
  bank_name: string;
  account: string;
  balance: number;
  available_balance: number;
  blocked_balance: number;
  updated_at: string;
}

export interface BankTransaction {
  id: string;
  bank_code: string;
  date: string;
  description: string;
  amount: number;
  type: 'credit' | 'debit';
  category?: string;
  balance_after?: number;
}

export interface BankConnectionStatus {
  bank_code: string;
  bank_name: string;
  connected: boolean;
  last_sync: string | null;
  error?: string;
}

export interface BankingBalancesResponse {
  balances: BankBalance[];
  total_balance: number;
  updated_at: string;
}

export interface BankingStatementResponse {
  transactions: BankTransaction[];
  total_credits: number;
  total_debits: number;
  period_start: string;
  period_end: string;
}

/**
 * Busca saldos de todas as contas bancárias
 */
export async function fetchBankBalances(): Promise<BankingBalancesResponse> {
  try {
    const { data } = await api.get<BankingBalancesResponse>(
      '/api/v1/integrations/banking/balances'
    );
    return data;
  } catch {
    // Fallback quando endpoint não existe ainda
    return {
      balances: [
        {
          bank_code: '403',
          bank_name: 'Banco Cora',
          account: '****-7',
          balance: 0,
          available_balance: 0,
          blocked_balance: 0,
          updated_at: new Date().toISOString(),
        },
        {
          bank_code: '077',
          bank_name: 'Banco Inter',
          account: '****-3',
          balance: 0,
          available_balance: 0,
          blocked_balance: 0,
          updated_at: new Date().toISOString(),
        },
      ],
      total_balance: 0,
      updated_at: new Date().toISOString(),
    };
  }
}

/**
 * Busca extrato bancário recente
 */
export async function fetchBankStatement(days: number = 30): Promise<BankingStatementResponse> {
  try {
    const { data } = await api.get<BankingStatementResponse>(
      '/api/v1/integrations/banking/statement',
      { params: { days } }
    );
    return data;
  } catch {
    return {
      transactions: [],
      total_credits: 0,
      total_debits: 0,
      period_start: new Date().toISOString(),
      period_end: new Date().toISOString(),
    };
  }
}

/**
 * Busca status de conexão dos bancos
 */
export async function fetchBankStatus(): Promise<BankConnectionStatus[]> {
  try {
    const { data } = await api.get<BankConnectionStatus[]>(
      '/api/v1/integrations/banking/status'
    );
    return data;
  } catch {
    return [
      { bank_code: '403', bank_name: 'Banco Cora', connected: false, last_sync: null, error: 'Endpoint não configurado' },
      { bank_code: '077', bank_name: 'Banco Inter', connected: false, last_sync: null, error: 'Endpoint não configurado' },
    ];
  }
}

const bankingService = {
  fetchBankBalances,
  fetchBankStatement,
  fetchBankStatus,
};

export default bankingService;
