'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  RefreshCw,
  Wallet,
  FileText,
  Barcode,
  QrCode,
  CreditCard,
  Receipt,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  AlertCircle,
  Copy,
  Download,
  Plus,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

// ─── API constants ────────────────────────────────────────────────────────────
const API = '/api/v1/integrations/banking';
const PAYMENT_API = '/api/v1/banking/payment';

// ─── Helpers ──────────────────────────────────────────────────────────────────
const fmtCurrency = (v: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v ?? 0);

const fmtDate = (d: string) => {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('pt-BR');
};

async function getToken(): Promise<string> {
  const form = new URLSearchParams();
  form.set('username', 'jjesus@conectamais.pro');
  form.set('password', 'Conecta@2025');
  const r = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
  });
  if (!r.ok) throw new Error('Login failed');
  const data = await r.json();
  return data.access_token;
}

async function apiFetch(path: string, opts: RequestInit = {}) {
  const token = await getToken();
  const r = await fetch(path, {
    ...opts,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...(opts.headers ?? {}),
    },
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`${r.status}: ${text.slice(0, 200)}`);
  }
  return r.json();
}

// ─── Types ────────────────────────────────────────────────────────────────────
interface Balance {
  bank_code: string;
  bank_name: string;
  account: string;
  balance: number;
  available_balance: number;
  blocked_balance: number;
  updated_at: string;
}

interface Transaction {
  id: string;
  bank_code: string;
  date: string;
  description: string;
  amount: number;
  type: 'credit' | 'debit';
  balance_after?: number;
  category?: string;
}

interface Boleto {
  id: string;
  nosso_numero?: string;
  valor: number;
  vencimento: string;
  pagador?: { nome?: string; cpf_cnpj?: string };
  status?: string;
  linha_digitavel?: string;
  barcode?: string;
  pdf_url?: string;
}

interface PixCharge {
  id: string;
  txid?: string;
  valor: number;
  status?: string;
  qr_code?: string;
  qr_code_image?: string;
  expiracao?: number;
  pix_copia_cola?: string;
}

// ─── Tab definition ───────────────────────────────────────────────────────────
const TABS = [
  { id: 'saldo', label: 'Saldo', icon: Wallet },
  { id: 'extrato', label: 'Extrato', icon: FileText },
  { id: 'boleto', label: 'Emitir Boleto', icon: Barcode },
  { id: 'pix', label: 'PIX', icon: QrCode },
  { id: 'pagar', label: 'Pagar', icon: CreditCard },
  { id: 'darf', label: 'DARF', icon: Receipt },
] as const;

type TabId = (typeof TABS)[number]['id'];

// ─── Main Component ───────────────────────────────────────────────────────────
export default function BankingPage() {
  const [tab, setTab] = useState<TabId>('saldo');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Saldo
  const [balances, setBalances] = useState<Balance[]>([]);
  const [totalBalance, setTotalBalance] = useState(0);

  // Extrato
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  // Boleto form
  const [boletoForm, setBoletoForm] = useState({
    pagador_nome: '',
    pagador_cpf_cnpj: '',
    valor: '',
    vencimento: '',
    descricao: '',
  });
  const [boletoResult, setBoletoResult] = useState<Boleto | null>(null);

  // PIX form
  const [pixForm, setPixForm] = useState({ valor: '', descricao: '' });
  const [pixResult, setPixResult] = useState<PixCharge | null>(null);

  // Pagar boleto form
  const [pagarForm, setPagarForm] = useState({
    codigo_barras: '',
    valor: '',
    descricao: '',
  });
  const [pagarResult, setPagarResult] = useState<Record<string, unknown> | null>(null);

  // DARF form
  const [darfForm, setDarfForm] = useState({
    periodo_apuracao: '',
    numero_referencia: '',
    valor_principal: '',
    codigo_receita: '6015',
    data_vencimento: '',
    descricao: 'Pagamento DARF',
  });
  const [darfResult, setDarfResult] = useState<Record<string, unknown> | null>(null);

  const notify = (msg: string, isError = false) => {
    if (isError) {
      setError(msg);
      setSuccess('');
    } else {
      setSuccess(msg);
      setError('');
    }
    setTimeout(() => {
      setError('');
      setSuccess('');
    }, 5000);
  };

  // ── Saldo ──────────────────────────────────────────────────────────────────
  const loadBalances = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`${API}/balances`);
      setBalances(data.balances ?? []);
      setTotalBalance(data.total_balance ?? 0);
    } catch (e) {
      notify(`Erro ao carregar saldo: ${(e as Error).message}`, true);
    } finally {
      setLoading(false);
    }
  }, []);

  // ── Extrato ────────────────────────────────────────────────────────────────
  const loadStatement = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`${API}/statement/full`);
      setTransactions(data.transactions ?? []);
    } catch (e) {
      notify(`Erro ao carregar extrato: ${(e as Error).message}`, true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (tab === 'saldo') loadBalances();
    if (tab === 'extrato') loadStatement();
  }, [tab, loadBalances, loadStatement]);

  // ── Emitir Boleto ──────────────────────────────────────────────────────────
  const emitirBoleto = async () => {
    setLoading(true);
    setBoletoResult(null);
    try {
      const body = {
        pagador: {
          nome: boletoForm.pagador_nome,
          cpf_cnpj: boletoForm.pagador_cpf_cnpj.replace(/\D/g, ''),
        },
        valor: parseFloat(boletoForm.valor),
        vencimento: boletoForm.vencimento,
        descricao: boletoForm.descricao || 'Serviços Conecta Mais',
      };
      const data = await apiFetch(`${API}/boleto/generate`, {
        method: 'POST',
        body: JSON.stringify(body),
      });
      setBoletoResult(data);
      notify('Boleto emitido com sucesso!');
    } catch (e) {
      notify(`Erro ao emitir boleto: ${(e as Error).message}`, true);
    } finally {
      setLoading(false);
    }
  };

  // ── PIX ───────────────────────────────────────────────────────────────────
  const gerarPix = async () => {
    setLoading(true);
    setPixResult(null);
    try {
      const body = {
        valor: parseFloat(pixForm.valor),
        descricao: pixForm.descricao || 'PIX Conecta Mais',
      };
      const data = await apiFetch(`${API}/pix/generate`, {
        method: 'POST',
        body: JSON.stringify(body),
      });
      setPixResult(data);
      notify('Cobrança PIX gerada!');
    } catch (e) {
      notify(`Erro ao gerar PIX: ${(e as Error).message}`, true);
    } finally {
      setLoading(false);
    }
  };

  // ── Pagar Boleto ───────────────────────────────────────────────────────────
  const pagarBoleto = async () => {
    setLoading(true);
    setPagarResult(null);
    try {
      const body = {
        codigo_barras: pagarForm.codigo_barras.replace(/\s/g, ''),
        valor: pagarForm.valor ? parseFloat(pagarForm.valor) : undefined,
        descricao: pagarForm.descricao,
      };
      const data = await apiFetch(`${PAYMENT_API}/barcode`, {
        method: 'POST',
        body: JSON.stringify(body),
      });
      setPagarResult(data);
      notify('Pagamento registrado com sucesso!');
    } catch (e) {
      notify(`Erro ao pagar boleto: ${(e as Error).message}`, true);
    } finally {
      setLoading(false);
    }
  };

  // ── DARF ──────────────────────────────────────────────────────────────────
  const pagarDarf = async () => {
    setLoading(true);
    setDarfResult(null);
    try {
      const body = {
        cnpj_cpf: '35710481000103',
        periodo_apuracao: darfForm.periodo_apuracao,
        numero_referencia: darfForm.numero_referencia,
        valor_principal: parseFloat(darfForm.valor_principal),
        codigo_receita: darfForm.codigo_receita,
        data_vencimento: darfForm.data_vencimento || undefined,
        descricao: darfForm.descricao,
      };
      const data = await apiFetch(`${PAYMENT_API}/darf`, {
        method: 'POST',
        body: JSON.stringify(body),
      });
      setDarfResult(data);
      notify('DARF enviado com sucesso!');
    } catch (e) {
      notify(`Erro ao pagar DARF: ${(e as Error).message}`, true);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => notify('Copiado!'));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/modulos/financeiro">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Módulo Bancário</h1>
            <p className="text-sm text-gray-500">Banco Inter — CNPJ 35.710.481/0001-03</p>
          </div>
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          <CheckCircle className="h-4 w-4 shrink-0" />
          {success}
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 flex flex-wrap gap-2">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={cn(
              'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
              tab === id
                ? 'bg-green-600 text-white shadow'
                : 'bg-white text-gray-600 shadow-sm hover:bg-green-50 hover:text-green-700'
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {/* ── SALDO ── */}
      {tab === 'saldo' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800">Saldos Bancários</h2>
            <Button variant="outline" size="sm" onClick={loadBalances} disabled={loading}>
              <RefreshCw className={cn('mr-2 h-4 w-4', loading && 'animate-spin')} />
              Atualizar
            </Button>
          </div>

          {/* Total */}
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <p className="text-sm text-green-700">Saldo Total Consolidado</p>
              <p className="mt-1 text-3xl font-bold text-green-800">{fmtCurrency(totalBalance)}</p>
            </CardContent>
          </Card>

          {/* Per bank */}
          <div className="grid gap-4 sm:grid-cols-2">
            {balances.length === 0 && !loading && (
              <p className="col-span-2 text-center text-sm text-gray-500">
                Nenhuma conta conectada.
              </p>
            )}
            {balances.map((b) => (
              <Card key={b.bank_code} className="shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between text-base">
                    <span>{b.bank_name}</span>
                    <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700">
                      {b.bank_code}
                    </span>
                  </CardTitle>
                  <p className="text-xs text-gray-500">Conta {b.account}</p>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Saldo disponível</span>
                    <span className="font-semibold text-green-700">
                      {fmtCurrency(b.available_balance)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Saldo bloqueado</span>
                    <span className="text-red-600">{fmtCurrency(b.blocked_balance)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Saldo total</span>
                    <span className="font-bold">{fmtCurrency(b.balance)}</span>
                  </div>
                  <p className="text-right text-xs text-gray-400">
                    Atualizado: {fmtDate(b.updated_at)}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* ── EXTRATO ── */}
      {tab === 'extrato' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800">Extrato Bancário</h2>
            <Button variant="outline" size="sm" onClick={loadStatement} disabled={loading}>
              <RefreshCw className={cn('mr-2 h-4 w-4', loading && 'animate-spin')} />
              Atualizar
            </Button>
          </div>

          <Card>
            <CardContent className="p-0">
              {transactions.length === 0 && !loading && (
                <p className="p-6 text-center text-sm text-gray-500">Sem transações no período.</p>
              )}
              <div className="divide-y">
                {transactions.map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between px-4 py-3">
                    <div className="flex items-center gap-3">
                      {tx.type === 'credit' ? (
                        <TrendingUp className="h-5 w-5 text-green-500" />
                      ) : (
                        <TrendingDown className="h-5 w-5 text-red-500" />
                      )}
                      <div>
                        <p className="text-sm font-medium text-gray-800">{tx.description}</p>
                        <p className="text-xs text-gray-400">
                          {fmtDate(tx.date)}
                          {tx.category ? ` · ${tx.category}` : ''}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className={cn(
                          'text-sm font-semibold',
                          tx.type === 'credit' ? 'text-green-600' : 'text-red-600'
                        )}
                      >
                        {tx.type === 'credit' ? '+' : '-'}
                        {fmtCurrency(tx.amount)}
                      </p>
                      {tx.balance_after !== undefined && (
                        <p className="text-xs text-gray-400">Saldo: {fmtCurrency(tx.balance_after)}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── EMITIR BOLETO ── */}
      {tab === 'boleto' && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Emitir Boleto</h2>

          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Nome do Pagador
                  </label>
                  <Input
                    placeholder="Razão Social ou Nome"
                    value={boletoForm.pagador_nome}
                    onChange={(e) => setBoletoForm({ ...boletoForm, pagador_nome: e.target.value })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    CPF/CNPJ do Pagador
                  </label>
                  <Input
                    placeholder="00.000.000/0001-00"
                    value={boletoForm.pagador_cpf_cnpj}
                    onChange={(e) =>
                      setBoletoForm({ ...boletoForm, pagador_cpf_cnpj: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Valor (R$)
                  </label>
                  <Input
                    type="number"
                    placeholder="0,00"
                    min="0"
                    step="0.01"
                    value={boletoForm.valor}
                    onChange={(e) => setBoletoForm({ ...boletoForm, valor: e.target.value })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Vencimento</label>
                  <Input
                    type="date"
                    value={boletoForm.vencimento}
                    onChange={(e) =>
                      setBoletoForm({ ...boletoForm, vencimento: e.target.value })
                    }
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="mb-1 block text-sm font-medium text-gray-700">Descrição</label>
                  <Input
                    placeholder="Descrição do serviço"
                    value={boletoForm.descricao}
                    onChange={(e) =>
                      setBoletoForm({ ...boletoForm, descricao: e.target.value })
                    }
                  />
                </div>
              </div>
              <Button
                onClick={emitirBoleto}
                disabled={loading || !boletoForm.pagador_nome || !boletoForm.valor}
                className="bg-green-600 hover:bg-green-700"
              >
                <Plus className="mr-2 h-4 w-4" />
                {loading ? 'Emitindo...' : 'Emitir Boleto'}
              </Button>
            </CardContent>
          </Card>

          {boletoResult && (
            <Card className="border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  Boleto Emitido
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Valor:</span>
                  <span className="font-semibold">{fmtCurrency(boletoResult.valor)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Vencimento:</span>
                  <span>{fmtDate(boletoResult.vencimento)}</span>
                </div>
                {boletoResult.linha_digitavel && (
                  <div>
                    <p className="mb-1 text-xs font-medium text-gray-600">Linha Digitável</p>
                    <div className="flex items-center gap-2 rounded bg-gray-100 p-2">
                      <code className="flex-1 break-all text-xs">
                        {boletoResult.linha_digitavel}
                      </code>
                      <button
                        onClick={() => copyToClipboard(boletoResult.linha_digitavel!)}
                        className="text-gray-400 hover:text-green-600"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
                {boletoResult.pdf_url && (
                  <a
                    href={boletoResult.pdf_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-2 text-sm text-green-600 hover:underline"
                  >
                    <Download className="h-4 w-4" />
                    Baixar PDF do Boleto
                  </a>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ── PIX ── */}
      {tab === 'pix' && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Gerar Cobrança PIX</h2>

          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Valor (R$)
                  </label>
                  <Input
                    type="number"
                    placeholder="0,00"
                    min="0"
                    step="0.01"
                    value={pixForm.valor}
                    onChange={(e) => setPixForm({ ...pixForm, valor: e.target.value })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Descrição</label>
                  <Input
                    placeholder="Descrição do pagamento"
                    value={pixForm.descricao}
                    onChange={(e) => setPixForm({ ...pixForm, descricao: e.target.value })}
                  />
                </div>
              </div>
              <Button
                onClick={gerarPix}
                disabled={loading || !pixForm.valor}
                className="bg-green-600 hover:bg-green-700"
              >
                <QrCode className="mr-2 h-4 w-4" />
                {loading ? 'Gerando...' : 'Gerar QR Code PIX'}
              </Button>
            </CardContent>
          </Card>

          {pixResult && (
            <Card className="border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  PIX Gerado
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Valor:</span>
                  <span className="font-semibold">{fmtCurrency(pixResult.valor)}</span>
                </div>
                {pixResult.qr_code_image && (
                  <div className="flex justify-center">
                    <img
                      src={pixResult.qr_code_image}
                      alt="QR Code PIX"
                      className="h-48 w-48 rounded border"
                    />
                  </div>
                )}
                {pixResult.pix_copia_cola && (
                  <div>
                    <p className="mb-1 text-xs font-medium text-gray-600">PIX Copia e Cola</p>
                    <div className="flex items-center gap-2 rounded bg-gray-100 p-2">
                      <code className="flex-1 break-all text-xs">{pixResult.pix_copia_cola}</code>
                      <button
                        onClick={() => copyToClipboard(pixResult.pix_copia_cola!)}
                        className="text-gray-400 hover:text-green-600"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ── PAGAR BOLETO ── */}
      {tab === 'pagar' && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Pagar Boleto / Código de Barras</h2>

          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Código de Barras / Linha Digitável
                </label>
                <Input
                  placeholder="Insira o código de barras"
                  value={pagarForm.codigo_barras}
                  onChange={(e) =>
                    setPagarForm({ ...pagarForm, codigo_barras: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Valor (opcional)
                  </label>
                  <Input
                    type="number"
                    placeholder="Deixe em branco para valor do boleto"
                    min="0"
                    step="0.01"
                    value={pagarForm.valor}
                    onChange={(e) => setPagarForm({ ...pagarForm, valor: e.target.value })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Descrição</label>
                  <Input
                    placeholder="Descrição do pagamento"
                    value={pagarForm.descricao}
                    onChange={(e) =>
                      setPagarForm({ ...pagarForm, descricao: e.target.value })
                    }
                  />
                </div>
              </div>
              <Button
                onClick={pagarBoleto}
                disabled={loading || !pagarForm.codigo_barras}
                className="bg-green-600 hover:bg-green-700"
              >
                <CreditCard className="mr-2 h-4 w-4" />
                {loading ? 'Processando...' : 'Registrar Pagamento'}
              </Button>
            </CardContent>
          </Card>

          {pagarResult && (
            <Card className="border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  Pagamento Registrado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="overflow-auto rounded bg-gray-50 p-3 text-xs text-gray-700">
                  {JSON.stringify(pagarResult, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ── DARF ── */}
      {tab === 'darf' && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">Pagar DARF</h2>
          <p className="text-sm text-gray-500">
            CNPJ: 35.710.481/0001-03 — Jordan Santos de Jesus Ltda
          </p>

          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Período de Apuração
                  </label>
                  <Input
                    placeholder="MM/AAAA"
                    value={darfForm.periodo_apuracao}
                    onChange={(e) =>
                      setDarfForm({ ...darfForm, periodo_apuracao: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Código da Receita
                  </label>
                  <Input
                    placeholder="Ex: 6015 (CSLL)"
                    value={darfForm.codigo_receita}
                    onChange={(e) =>
                      setDarfForm({ ...darfForm, codigo_receita: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Número de Referência
                  </label>
                  <Input
                    placeholder="Número de referência"
                    value={darfForm.numero_referencia}
                    onChange={(e) =>
                      setDarfForm({ ...darfForm, numero_referencia: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Valor Principal (R$)
                  </label>
                  <Input
                    type="number"
                    placeholder="0,00"
                    min="0"
                    step="0.01"
                    value={darfForm.valor_principal}
                    onChange={(e) =>
                      setDarfForm({ ...darfForm, valor_principal: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Data de Vencimento
                  </label>
                  <Input
                    type="date"
                    value={darfForm.data_vencimento}
                    onChange={(e) =>
                      setDarfForm({ ...darfForm, data_vencimento: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Descrição</label>
                  <Input
                    placeholder="Descrição do pagamento"
                    value={darfForm.descricao}
                    onChange={(e) =>
                      setDarfForm({ ...darfForm, descricao: e.target.value })
                    }
                  />
                </div>
              </div>
              <Button
                onClick={pagarDarf}
                disabled={
                  loading ||
                  !darfForm.periodo_apuracao ||
                  !darfForm.valor_principal ||
                  !darfForm.numero_referencia
                }
                className="bg-green-600 hover:bg-green-700"
              >
                <Receipt className="mr-2 h-4 w-4" />
                {loading ? 'Processando...' : 'Pagar DARF'}
              </Button>
            </CardContent>
          </Card>

          {darfResult && (
            <Card className="border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  DARF Enviado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="overflow-auto rounded bg-gray-50 p-3 text-xs text-gray-700">
                  {JSON.stringify(darfResult, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
