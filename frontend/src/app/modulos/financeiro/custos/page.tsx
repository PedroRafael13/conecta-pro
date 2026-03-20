'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  PieChart,
  BarChart2,
  Shield,
  Leaf,
  Camera,
  Wifi,
  Plus,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Info,
  X,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { bankingApi } from '@/services/banking/bankingService';

// ─────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────

interface BreakdownItem {
  name: string;
  value: number;
}

interface TipoCusto {
  tipo: string;
  label: string;
  cor: string;
  custo_total: number;
  margem_pct: number;
  breakdown: Record<string, number>;
  fonte: 'real' | 'benchmark' | 'sem_dados';
  unidade?: string;
  aviso?: string;
  registros?: Record<string, unknown>[];
}

interface ResumoTipo {
  tipo: string;
  label: string;
  cor: string;
  custo_total: number;
  margem_contratual: number;
  margem_pct: number;
  fonte: 'real' | 'benchmark' | 'sem_dados';
}

interface Summary {
  mes: string;
  resumo_por_tipo: ResumoTipo[];
  total_custo: number;
  total_margem: number;
  analise_ai?: Record<string, unknown> | null;
}

// ─────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────

const formatCurrency = (v: number | null | undefined) => {
  if (v == null) return 'R$ 0,00';
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const TIPOS = [
  { id: 'portaria',            label: 'Portaria',           icon: Shield,   cor: '#3B82F6' },
  { id: 'limpeza',             label: 'Limpeza',            icon: Leaf,     cor: '#10B981' },
  { id: 'jardinagem',          label: 'Jardinagem',         icon: Leaf,     cor: '#84CC16' },
  { id: 'seguranca_eletronica',label: 'Seg. Eletrônica',    icon: Camera,   cor: '#F59E0B' },
  { id: 'portaria_remota',     label: 'Portaria Remota',    icon: Wifi,     cor: '#8B5CF6' },
];

function getMesAtual() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

// ─────────────────────────────────────────────────────────
// Modal de Registro
// ─────────────────────────────────────────────────────────

interface ModalRegistroProps {
  tipoInicial: string;
  mes: string;
  onClose: () => void;
  onSuccess: () => void;
}

function ModalRegistro({ tipoInicial, mes, onClose, onSuccess }: ModalRegistroProps) {
  const [tipo, setTipo] = useState(tipoInicial);
  const [mesForm, setMesForm] = useState(mes);
  const [custoTotal, setCustoTotal] = useState('');
  const [margemContratual, setMargemContratual] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro('');
    setLoading(true);
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      await bankingApi.post(
        '/api/v1/financial/ai/costing/registrar',
        {
          tipo,
          mes: mesForm,
          custo_total: parseFloat(custoTotal),
          margem_contratual: parseFloat(margemContratual || '0'),
          breakdown: {},
        },
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      onSuccess();
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao registrar custo.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">Registrar Custo Real</h3>
          <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Serviço</label>
            <select
              value={tipo}
              onChange={e => setTipo(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              required
            >
              {TIPOS.map(t => (
                <option key={t.id} value={t.id}>{t.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mês de Referência</label>
            <input
              type="month"
              value={mesForm}
              onChange={e => setMesForm(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Custo Total (R$)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={custoTotal}
              onChange={e => setCustoTotal(e.target.value)}
              placeholder="Ex: 8500.00"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Margem Contratual (R$)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={margemContratual}
              onChange={e => setMargemContratual(e.target.value)}
              placeholder="Ex: 1800.00"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          {erro && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              {erro}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────────────────

export default function CustosPage() {
  const [mes, setMes] = useState(getMesAtual());
  const [tipoAtivo, setTipoAtivo] = useState('portaria');
  const [summary, setSummary] = useState<Summary | null>(null);
  const [detalhe, setDetalhe] = useState<TipoCusto | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingDetalhe, setLoadingDetalhe] = useState(false);
  const [erroSummary, setErroSummary] = useState('');
  const [erroDetalhe, setErroDetalhe] = useState('');
  const [showModal, setShowModal] = useState(false);

  const getAuthHeaders = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const fetchSummary = useCallback(async () => {
    setLoadingSummary(true);
    setErroSummary('');
    try {
      const res = await bankingApi.get('/api/v1/financial/ai/costing/summary', {
        params: { mes },
        headers: getAuthHeaders(),
      });
      setSummary(res.data);
    } catch (err: any) {
      setErroSummary('Erro ao carregar resumo de custos.');
      setSummary(null);
    } finally {
      setLoadingSummary(false);
    }
  }, [mes]);

  const fetchDetalhe = useCallback(async () => {
    setLoadingDetalhe(true);
    setErroDetalhe('');
    try {
      const res = await bankingApi.get('/api/v1/financial/ai/costing/by-type', {
        params: { tipo: tipoAtivo, mes },
        headers: getAuthHeaders(),
      });
      setDetalhe(res.data);
    } catch (err: any) {
      setErroDetalhe('Erro ao carregar detalhe do tipo.');
      setDetalhe(null);
    } finally {
      setLoadingDetalhe(false);
    }
  }, [tipoAtivo, mes]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  useEffect(() => {
    fetchDetalhe();
  }, [fetchDetalhe]);

  const tipoAtualInfo = TIPOS.find(t => t.id === tipoAtivo)!;

  // Build bar chart data from summary
  const barData = summary?.resumo_por_tipo.map(r => ({
    label: r.label.replace('Segurança ', 'Seg. ').replace('Portaria Remota', 'Port. Remota'),
    margem: r.margem_pct,
    cor: r.cor,
  })) ?? [];

  // Build pie data from detalhe breakdown
  const pieData: BreakdownItem[] = detalhe
    ? Object.entries(detalhe.breakdown)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => ({ name: k, value: v }))
    : [];

  const PIE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#06B6D4', '#F97316', '#84CC16'];

  const resumoAtivo = summary?.resumo_por_tipo.find(r => r.tipo === tipoAtivo);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Custo por Tipo de Serviço</h1>
          <p className="text-gray-500 text-sm mt-1">
            Análise detalhada de custos e margens por modalidade de serviço de segurança
          </p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="month"
            value={mes}
            onChange={e => setMes(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
          <button
            onClick={() => { fetchSummary(); fetchDetalhe(); }}
            className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <RefreshCw size={16} />
            Atualizar
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            <Plus size={16} />
            Registrar Custo
          </button>
        </div>
      </div>

      {/* 5 type cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {TIPOS.map(tipo => {
          const resumo = summary?.resumo_por_tipo.find(r => r.tipo === tipo.id);
          const isAtivo = tipoAtivo === tipo.id;
          const Icon = tipo.icon;
          return (
            <button
              key={tipo.id}
              onClick={() => setTipoAtivo(tipo.id)}
              className={`relative p-4 rounded-xl border-2 text-left transition-all ${
                isAtivo
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${tipo.cor}20` }}
                >
                  <Icon size={16} style={{ color: tipo.cor }} />
                </div>
                {resumo?.fonte === 'benchmark' && (
                  <span className="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded-full">Est.</span>
                )}
                {resumo?.fonte === 'sem_dados' && (
                  <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-full">—</span>
                )}
              </div>
              <p className="text-xs font-semibold text-gray-700 leading-tight">{tipo.label}</p>
              <p className="text-lg font-bold mt-1" style={{ color: tipo.cor }}>
                {resumo ? `${resumo.margem_pct.toFixed(1)}%` : '—'}
              </p>
              <p className="text-xs text-gray-400">margem</p>
            </button>
          );
        })}
      </div>

      {/* Main grid: detalhe + summary chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Breakdown do tipo ativo */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-gray-900">{tipoAtualInfo.label}</h2>
              <p className="text-xs text-gray-500">Composição de custos</p>
            </div>
            {detalhe && (
              <div className="text-right">
                <p className="text-sm font-bold text-gray-900">{formatCurrency(detalhe.custo_total)}</p>
                <p className="text-xs text-gray-500">{detalhe.unidade ?? 'por unidade'}</p>
              </div>
            )}
          </div>

          {loadingDetalhe ? (
            <div className="flex items-center justify-center h-48 text-gray-400">
              <RefreshCw size={20} className="animate-spin mr-2" /> Carregando...
            </div>
          ) : erroDetalhe ? (
            <div className="flex items-center gap-2 text-amber-600 text-sm p-4 bg-amber-50 rounded-lg">
              <AlertTriangle size={16} /> {erroDetalhe}
            </div>
          ) : pieData.length > 0 ? (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {pieData.map((_, index) => (
                      <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: unknown) => [`${formatCurrency(value as number)}`, 'Custo']}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-gray-400 text-sm p-4">
              <Info size={16} /> Nenhum dado disponível para este mês.
            </div>
          )}

          {/* Benchmark badge */}
          {detalhe?.fonte === 'sem_dados' && (
            <div className="mt-4 flex items-start gap-2 text-xs text-gray-600 bg-gray-50 rounded-lg p-3">
              <Info size={14} className="mt-0.5 flex-shrink-0" />
              <span>{detalhe.aviso ?? 'Sem custos registrados. Use "Registrar Custo" para lançar dados reais.'}</span>
            </div>
          )}
          {detalhe?.fonte === 'benchmark' && (
            <div className="mt-4 flex items-start gap-2 text-xs text-amber-700 bg-amber-50 rounded-lg p-3">
              <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
              <span>{detalhe.aviso ?? 'Dados baseados em benchmarks de mercado.'}</span>
            </div>
          )}
          {detalhe?.fonte === 'real' && (
            <div className="mt-4 flex items-center gap-2 text-xs text-green-700 bg-green-50 rounded-lg p-3">
              <CheckCircle size={14} />
              <span>Baseado em dados reais registrados.</span>
            </div>
          )}
        </div>

        {/* Margem por tipo — gráfico de barras */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 size={18} className="text-blue-600" />
            <h2 className="text-base font-bold text-gray-900">Margem por Tipo de Serviço</h2>
          </div>

          {loadingSummary ? (
            <div className="flex items-center justify-center h-48 text-gray-400">
              <RefreshCw size={20} className="animate-spin mr-2" /> Carregando...
            </div>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: unknown) => [`${typeof v === 'number' ? v.toFixed(1) : '0'}%`, 'Margem'] as any} />
                  <Bar dataKey="margem" radius={[4, 4, 0, 0]}>
                    {barData.map((entry, index) => (
                      <Cell key={index} fill={entry.cor} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Tabela resumo */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-base font-bold text-gray-900">Resumo por Tipo de Serviço</h2>
          <span className="text-xs text-gray-400">
            {mes.replace('-', '/')}
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Tipo</th>
                <th className="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Custo Total</th>
                <th className="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Margem</th>
                <th className="text-right px-6 py-3 text-xs font-semibold text-gray-500 uppercase">% Margem</th>
                <th className="text-center px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Fonte</th>
              </tr>
            </thead>
            <tbody>
              {(summary?.resumo_por_tipo ?? []).map((r, idx) => (
                <tr
                  key={r.tipo}
                  onClick={() => setTipoAtivo(r.tipo)}
                  className={`border-t border-gray-100 cursor-pointer transition-colors ${
                    tipoAtivo === r.tipo ? 'bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: r.cor }}
                      />
                      <span className="font-medium text-gray-900">{r.label}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-gray-700">
                    {r.custo_total > 0 ? formatCurrency(r.custo_total) : '—'}
                  </td>
                  <td className="px-6 py-4 text-right text-green-600 font-medium">
                    {r.margem_contratual > 0 ? formatCurrency(r.margem_contratual) : '—'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span
                      className={`inline-flex items-center gap-1 font-semibold ${
                        r.margem_pct >= 30
                          ? 'text-green-600'
                          : r.margem_pct >= 20
                          ? 'text-blue-600'
                          : 'text-amber-600'
                      }`}
                    >
                      {r.margem_pct >= 20 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      {r.margem_pct.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span
                      className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                        r.fonte === 'real'
                          ? 'bg-green-100 text-green-700'
                          : r.fonte === 'sem_dados'
                          ? 'bg-gray-100 text-gray-500'
                          : 'bg-amber-100 text-amber-700'
                      }`}
                    >
                      {r.fonte === 'real' ? 'Real' : r.fonte === 'sem_dados' ? 'Sem dados' : 'Benchmark'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
            {(!summary || summary.resumo_por_tipo.length === 0) && (
              <tbody>
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-400">
                    <Info size={24} className="mx-auto mb-2" />
                    <p className="text-sm font-medium">Nenhum custo registrado</p>
                    <p className="text-xs mt-1">Use &quot;Registrar Custo&quot; para lançar dados reais por tipo de serviço.</p>
                  </td>
                </tr>
              </tbody>
            )}
            {summary && (
              <tfoot>
                <tr className="border-t-2 border-gray-200 bg-gray-50">
                  <td className="px-6 py-3 font-bold text-gray-900">Total</td>
                  <td className="px-6 py-3 text-right font-bold text-gray-900">
                    {summary.total_custo > 0 ? formatCurrency(summary.total_custo) : '—'}
                  </td>
                  <td className="px-6 py-3 text-right font-bold text-green-700">
                    {summary.total_margem > 0 ? formatCurrency(summary.total_margem) : '—'}
                  </td>
                  <td className="px-6 py-3 text-right font-bold">
                    {summary.total_custo > 0
                      ? `${((summary.total_margem / (summary.total_custo + summary.total_margem)) * 100).toFixed(1)}%`
                      : '—'}
                  </td>
                  <td />
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>

      {/* AI Analysis block */}
      {summary?.analise_ai && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200 p-6">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <BarChart2 size={16} className="text-white" />
            </div>
            <h2 className="font-bold text-gray-900">Análise de Custeio — IA</h2>
          </div>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
            {typeof summary.analise_ai === 'string'
              ? summary.analise_ai
              : JSON.stringify(summary.analise_ai, null, 2)}
          </pre>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <ModalRegistro
          tipoInicial={tipoAtivo}
          mes={mes}
          onClose={() => setShowModal(false)}
          onSuccess={() => {
            setShowModal(false);
            fetchSummary();
            fetchDetalhe();
          }}
        />
      )}
    </div>
  );
}
