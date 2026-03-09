/**
 * Banking Service
 *
 * Consulta saldos, extratos e status dos bancos integrados (Cora, Inter).
 * Usa instância axios própria (sem interceptor de redirect) para evitar
 * que falhas de auth nas chamadas bancárias redirecionem para /login.
 */

import axios from 'axios';

const API_URLS = {
  production: 'https://erp.conectamais.pro',
  staging: 'https://staging.conectamais.pro',
  development: 'http://localhost:8080',
} as const;

const getBankingBaseURL = (): string => {
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || API_URLS.production;
  }
  const hostname = window.location.hostname;
  if (hostname === 'localhost' && ['3000', '3001', '3002'].includes(window.location.port)) {
    return API_URLS.development;
  }
  if (hostname === 'staging.conectamais.pro') return API_URLS.staging;
  return API_URLS.production;
};

export const bankingApi = axios.create({ timeout: 10000 });

bankingApi.interceptors.request.use((config) => {
  config.baseURL = getBankingBaseURL();
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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
    const { data } = await bankingApi.get<BankingBalancesResponse>(
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
    const { data } = await bankingApi.get<BankingStatementResponse>(
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
    const { data } = await bankingApi.get<BankConnectionStatus[]>(
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

export interface BankTransactionFull {
  id: string;
  bank_code: string;
  bank_name: string;
  date: string;
  description: string;
  amount: number;
  type: 'credit' | 'debit';
  transaction_type: string;   // PIX, TED, BOLETO, etc
  category?: string;
  balance_after?: number;
  counterpart_name?: string;
  counterpart_document?: string;
  counterpart_bank?: string;
  reference?: string;
}

export interface BankStatementFullResponse {
  transactions: BankTransactionFull[];
  total_credits: number;
  total_debits: number;
  period_start: string;
  period_end: string;
  opening_balance?: number;
  closing_balance?: number;
}

export interface BoletoGenerateRequest {
  bank_code: string;        // "403" = Cora, "077" = Inter
  amount: number;
  due_date: string;         // "YYYY-MM-DD"
  payer_name: string;
  payer_document: string;   // CPF ou CNPJ (só dígitos)
  description: string;
}

export interface BoletoResponse {
  success: boolean;
  bank_code: string;
  bank_name: string;
  boleto_id?: string;
  barcode?: string;
  digitable_line?: string;
  pdf_url?: string;
  pix_qrcode?: string;
  pix_copy_paste?: string;
  amount: number;
  due_date: string;
  payer_name: string;
  created_at: string;
  error?: string;
}

export interface BoletoListItem {
  boleto_id: string;
  bank_code: string;
  bank_name: string;
  amount: number;
  due_date: string;
  payer_name: string;
  status: string;
  barcode?: string;
  digitable_line?: string;
  pdf_url?: string;
  created_at?: string;
}

export interface BoletoListResponse {
  boletos: BoletoListItem[];
  total: number;
}

/**
 * Busca extrato completo com todos os campos (counterpart, balance, etc.)
 */
export async function fetchBankStatementFull(days: number = 30, bankCode?: string): Promise<BankStatementFullResponse> {
  try {
    const params: Record<string, unknown> = { days };
    if (bankCode) params.bank_code = bankCode;
    const { data } = await bankingApi.get<BankStatementFullResponse>(
      '/api/v1/integrations/banking/statement/full',
      { params }
    );
    return data;
  } catch {
    // Fallback: usa endpoint simples e converte
    try {
      const simple = await fetchBankStatement(days);
      return {
        ...simple,
        transactions: simple.transactions.map(t => ({
          ...t,
          bank_name: t.bank_code === '403' ? 'Banco Cora' : 'Banco Inter',
          transaction_type: t.category || 'Outros',
        })),
      };
    } catch {
      return { transactions: [], total_credits: 0, total_debits: 0, period_start: '', period_end: '' };
    }
  }
}

/**
 * Emite um boleto bancário
 */
export async function emitirBoleto(req: BoletoGenerateRequest): Promise<BoletoResponse> {
  const { data } = await bankingApi.post<BoletoResponse>(
    '/api/v1/integrations/banking/boleto/generate',
    req
  );
  return data;
}

export interface PixChargeRequest {
  bank_code: string;
  amount: number;
  description: string;
  payer_name?: string;
  payer_document?: string;
  chave_pix?: string;
  expiracao_horas?: number;
}

export interface PixChargeResponse {
  success: boolean;
  bank_code: string;
  bank_name: string;
  charge_id?: string;
  pix_qrcode?: string;
  pix_copy_paste?: string;
  amount: number;
  description: string;
  chave_pix: string;
  expires_at?: string;
  created_at: string;
  error?: string;
}

/**
 * Gera cobrança PIX com QR Code dinâmico
 */
export async function gerarCobrancaPix(req: PixChargeRequest): Promise<PixChargeResponse> {
  const { data } = await bankingApi.post<PixChargeResponse>(
    '/api/v1/integrations/banking/pix/generate',
    req
  );
  return data;
}

/**
 * Lista boletos emitidos
 */
export async function listarBoletos(bankCode?: string, status?: string, days: number = 30): Promise<BoletoListResponse> {
  try {
    const params: Record<string, unknown> = { days };
    if (bankCode) params.bank_code = bankCode;
    if (status) params.status = status;
    const { data } = await bankingApi.get<BoletoListResponse>(
      '/api/v1/integrations/banking/boleto/list',
      { params }
    );
    return data;
  } catch {
    return { boletos: [], total: 0 };
  }
}

const bankingService = {
  fetchBankBalances,
  fetchBankStatement,
  fetchBankStatementFull,
  fetchBankStatus,
  emitirBoleto,
  listarBoletos,
};

export default bankingService;
