'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
  TrendingUp, TrendingDown, Minus, DollarSign, Users, Building2,
  Percent, Receipt, FileText, Target, AlertTriangle, CheckCircle2,
  Clock, ChevronUp, ChevronDown, BarChart3, RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const API = process.env.NEXT_PUBLIC_API_URL || '';

function getHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(`${API}${url}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Types ──────────────────────────────────────────────────────────────────

interface KPI {
  codigo: string;
  nome: string;
  categoria: string;
  unidade: string;
  valor_atual: number;
  valor_anterior: number;
  meta: number;
  variacao_pct: number;
  tendencia: string;
  historico: Array<{ period: string; value: number }>;
}

interface FiscalItem {
  tipo: string;
  nome: string;
  competencia: string;
  vencimento: string;
  valor: number;
}

interface BiDashboard {
  kpis: KPI[];
  fiscal: {
    obrigacoes_cumpridas: number;
    obrigacoes_pendentes: number;
    proximas: FiscalItem[];
  };
}

interface NfseDashboard {
  totais: { nfse_emitidas: number; clientes_ativos: number; faturamento_bruto: number; iss_total: number; ticket_medio: number };
  por_mes: Array<{ competencia: string; nfse_emitidas: number; faturamento_bruto: number; iss_total: number; faturamento_liquido: number }>;
  por_cliente: Array<{ cliente: string; cnpj: string; nfse_emitidas: number; total_bruto: number; total_iss: number }>;
  por_servico: Array<{ servico: string; quantidade: number; total: number }>;
}

interface HeadcountData {
  total_headcount: number;
  total_folha_bruta: number;
  por_cliente: Array<{ client_id: string; cliente: string; cnpj: string; headcount: number; folha_bruta: number; contrato_mensal: number }>;
}

// ── Helpers ────────────────────────────────────────────────────────────────

const BRL = (v: number) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const PCT = (v: number) => `${v.toFixed(1)}%`;
const NUM = (v: number) => v.toLocaleString('pt-BR');

const BLUE = '#0A2540';
const BLUE2 = '#1E3A5F';
const ORANGE = '#FF6B35';
const GREEN = '#22C55E';
const RED = '#EF4444';
const YELLOW = '#F59E0B';
const PURPLE = '#8B5CF6';
const CYAN = '#06B6D4';
const PINK = '#EC4899';

const PIE_COLORS = [BLUE, ORANGE, BLUE2, GREEN, PURPLE, CYAN, PINK];

// ── KPI Card ───────────────────────────────────────────────────────────────

function KPICard({ kpi }: { kpi: KPI }) {
  const isUp = kpi.variacao_pct > 0;
  const isDown = kpi.variacao_pct < 0;

  const format = (v: number) => {
    if (kpi.unidade === 'BRL') return BRL(v);
    if (kpi.unidade === '%') return PCT(v);
    return NUM(v);
  };

  const icons: Record<string, React.ReactNode> = {
    MRR: <DollarSign className="h-4 w-4" />,
    FOLHA: <DollarSign className="h-4 w-4" />,
    MARGEM: <Percent className="h-4 w-4" />,
    HEADCOUNT: <Users className="h-4 w-4" />,
    CLIENTES: <Building2 className="h-4 w-4" />,
    TICKET: <Target className="h-4 w-4" />,
    RPF: <TrendingUp className="h-4 w-4" />,
    CUSTO_FOLHA: <AlertTriangle className="h-4 w-4" />,
    NFSE_COUNT: <FileText className="h-4 w-4" />,
    ISS_TOTAL: <Receipt className="h-4 w-4" />,
  };

  const trendColor = kpi.codigo === 'CUSTO_FOLHA' || kpi.codigo === 'FOLHA' || kpi.codigo === 'ISS_TOTAL'
    ? (isUp ? 'text-red-500' : isDown ? 'text-green-500' : 'text-gray-400')
    : (isUp ? 'text-green-500' : isDown ? 'text-red-500' : 'text-gray-400');

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-4 pb-3 px-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide truncate">{kpi.nome}</span>
          <span className="text-muted-foreground">{icons[kpi.codigo] || <BarChart3 className="h-4 w-4" />}</span>
        </div>
        <div className="text-xl font-bold text-gray-900 dark:text-white">{format(kpi.valor_atual)}</div>
        <div className="flex items-center gap-1.5 mt-1">
          <span className={`flex items-center text-xs font-medium ${trendColor}`}>
            {isUp ? <ChevronUp className="h-3 w-3" /> : isDown ? <ChevronDown className="h-3 w-3" /> : <Minus className="h-3 w-3" />}
            {Math.abs(kpi.variacao_pct).toFixed(1)}%
          </span>
          <span className="text-xs text-muted-foreground">vs mês ant.</span>
        </div>
        {kpi.meta > 0 && (
          <div className="mt-2">
            <div className="flex justify-between text-xs text-muted-foreground mb-0.5">
              <span>Meta: {format(kpi.meta)}</span>
              <span>{Math.min(Math.round((kpi.valor_atual / kpi.meta) * 100), 999)}%</span>
            </div>
            <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-1.5">
              <div
                className="h-1.5 rounded-full transition-all"
                style={{
                  width: `${Math.min((kpi.valor_atual / kpi.meta) * 100, 100)}%`,
                  backgroundColor: (kpi.valor_atual / kpi.meta) >= 0.9 ? GREEN : (kpi.valor_atual / kpi.meta) >= 0.7 ? YELLOW : RED,
                }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ── Efficiency Card ────────────────────────────────────────────────────────

function EfficiencyCard({ label, value, meta, format, invertColor }: {
  label: string; value: number; meta: number; format: (v: number) => string; invertColor?: boolean;
}) {
  const ratio = value / meta;
  const ok = invertColor ? ratio <= 1 : ratio >= 1;
  const color = ok ? 'border-green-200 bg-green-50 dark:bg-green-950/20' : 'border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20';
  const badge = ok
    ? <span className="text-xs font-medium text-green-700 dark:text-green-400 flex items-center gap-0.5"><CheckCircle2 className="h-3 w-3" /> Dentro da meta</span>
    : <span className="text-xs font-medium text-yellow-700 dark:text-yellow-400 flex items-center gap-0.5"><AlertTriangle className="h-3 w-3" /> Acima da meta</span>;

  return (
    <div className={`border rounded-lg p-3 ${color}`}>
      <div className="text-xs text-muted-foreground mb-0.5">{label}</div>
      <div className="text-lg font-bold">{format(value)}</div>
      <div className="flex items-center justify-between mt-1">
        <span className="text-xs text-muted-foreground">Meta: {format(meta)}</span>
        {badge}
      </div>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function BiDashboardPage() {
  const [tab, setTab] = useState<'overview' | 'fiscal'>('overview');

  const { data: bi, isLoading: biLoading, refetch: refetchBi } = useQuery<BiDashboard>({
    queryKey: ['bi-dashboard'],
    queryFn: () => fetchJSON('/api/v1/financial/bi/dashboard'),
    staleTime: 60_000,
  });

  const { data: nfse, isLoading: nfseLoading } = useQuery<NfseDashboard>({
    queryKey: ['nfse-dashboard'],
    queryFn: () => fetchJSON('/api/v1/financial/nfse/dashboard'),
    staleTime: 60_000,
  });

  const { data: hc } = useQuery<HeadcountData>({
    queryKey: ['headcount'],
    queryFn: () => fetchJSON('/api/v1/financial/headcount'),
    staleTime: 60_000,
  });

  const isLoading = biLoading || nfseLoading;
  const kpis = bi?.kpis || [];

  // Evolução mensal (com projeção)
  const evolucaoData = (() => {
    const mrrKpi = kpis.find(k => k.codigo === 'MRR');
    const folhaKpi = kpis.find(k => k.codigo === 'FOLHA');
    if (!mrrKpi) return [];
    const months = mrrKpi.historico || [];
    const folhaHist = folhaKpi?.historico || [];
    const result = months.map((m, i) => ({
      mes: m.period.replace('2026-', ''),
      label: m.period === '2026-01' ? 'Jan' : m.period === '2026-02' ? 'Fev' : m.period,
      faturamento: m.value,
      folha: folhaHist[i]?.value || 0,
      margem: m.value > 0 ? Math.round(((m.value - (folhaHist[i]?.value || 0)) / m.value) * 100) : 0,
    }));
    // Projeção março
    const lastMrr = months[months.length - 1]?.value || 0;
    const lastFolha = folhaHist[folhaHist.length - 1]?.value || 0;
    result.push({
      mes: '03', label: 'Mar (proj)', faturamento: Math.round(lastMrr * 1.005),
      folha: lastFolha, margem: Math.round(((lastMrr * 1.005 - lastFolha) / (lastMrr * 1.005)) * 100),
    });
    result.push({
      mes: '04', label: 'Abr (proj)', faturamento: Math.round(lastMrr * 1.01),
      folha: lastFolha, margem: Math.round(((lastMrr * 1.01 - lastFolha) / (lastMrr * 1.01)) * 100),
    });
    return result;
  })();

  // Composição receita
  const servicoData = (nfse?.por_servico || []).map(s => {
    const shortName = s.servico
      .replace('Servicos de ', '').replace('Manutencao de ', 'Manut. ')
      .replace('sistema ', '').replace('portaria e servicos gerais', 'Port. + Serv.Gerais')
      .replace('portaria e limpeza', 'Port. + Limpeza')
      .replace('limpeza e jardinagem', 'Limpeza/Jard.')
      .replace('seguranca eletronica', 'Seg. Eletronica')
      .replace('piscina', 'Piscina');
    return { name: shortName.charAt(0).toUpperCase() + shortName.slice(1), value: s.total, qty: s.quantidade };
  });

  // Faturamento por cliente (top 11)
  const clienteData = (nfse?.por_cliente || []).map(c => ({
    name: c.cliente.replace('CONDOMINIO ', '').replace('RESIDENCIAL ', '').replace('DO EDIFICIO ', ''),
    value: c.total_bruto,
    nfse: c.nfse_emitidas,
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: Record<string, unknown>) => {
    if (!active || !payload) return null;
    const items = payload as Array<{ name: string; value: number; color: string }>;
    return (
      <div className="bg-white dark:bg-gray-900 border rounded-lg shadow-lg p-3 text-sm">
        <p className="font-medium mb-1">{String(label || '')}</p>
        {items.map((p, i) => (
          <p key={i} style={{ color: p.color }} className="flex justify-between gap-4">
            <span>{p.name}:</span>
            <span className="font-medium">{p.name === 'Margem' ? `${p.value}%` : BRL(p.value)}</span>
          </p>
        ))}
      </div>
    );
  };

  const projecaoAnual = (kpis.find(k => k.codigo === 'MRR')?.valor_atual || 0) * 12;
  const custoFolha = kpis.find(k => k.codigo === 'CUSTO_FOLHA');
  const margem = kpis.find(k => k.codigo === 'MARGEM');
  const ticket = kpis.find(k => k.codigo === 'TICKET');
  const rpf = kpis.find(k => k.codigo === 'RPF');

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded w-64" />
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-28 bg-gray-200 dark:bg-gray-800 rounded-lg" />
          ))}
        </div>
        <div className="h-80 bg-gray-200 dark:bg-gray-800 rounded-lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="h-6 w-6" style={{ color: BLUE }} />
            Business Intelligence
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">Conecta Mais - Indicadores Executivos</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
            <button onClick={() => setTab('overview')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${tab === 'overview' ? 'bg-white dark:bg-gray-700 shadow-sm' : 'text-muted-foreground'}`}>
              Visao Geral
            </button>
            <button onClick={() => setTab('fiscal')} className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${tab === 'fiscal' ? 'bg-white dark:bg-gray-700 shadow-sm' : 'text-muted-foreground'}`}>
              Fiscal
            </button>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetchBi()}>
            <RefreshCw className="h-4 w-4 mr-1" /> Atualizar
          </Button>
        </div>
      </div>

      {tab === 'overview' ? (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {kpis.map(kpi => <KPICard key={kpi.codigo} kpi={kpi} />)}
          </div>

          {/* Evolução + Composição */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* LineChart evolução */}
            <Card className="lg:col-span-2">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Evolucao Mensal</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={evolucaoData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line type="monotone" dataKey="faturamento" name="Faturamento" stroke={BLUE} strokeWidth={2.5} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="folha" name="Folha" stroke={ORANGE} strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* PieChart composição */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Receita por Servico</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={servicoData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} paddingAngle={2} dataKey="value"
                      label={false}>
                      {servicoData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(value) => BRL(Number(value))} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Faturamento por cliente */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Faturamento por Cliente (acumulado Jan-Fev)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={Math.max(300, clienteData.length * 36)}>
                <BarChart data={clienteData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={180} />
                  <Tooltip formatter={(value) => BRL(Number(value))} />
                  <Bar dataKey="value" name="Faturamento" fill={BLUE} radius={[0, 4, 4, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Indicadores de Eficiência */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            <EfficiencyCard label="Margem Bruta" value={margem?.valor_atual || 0} meta={60} format={PCT} />
            <EfficiencyCard label="Custo Folha / Faturamento" value={custoFolha?.valor_atual || 0} meta={40} format={PCT} invertColor />
            <EfficiencyCard label="Ticket Medio" value={ticket?.valor_atual || 0} meta={20000} format={BRL} />
            <EfficiencyCard label="Receita / Funcionario" value={rpf?.valor_atual || 0} meta={4000} format={BRL} />
            <div className="border border-blue-200 bg-blue-50 dark:bg-blue-950/20 rounded-lg p-3">
              <div className="text-xs text-muted-foreground mb-0.5">Projecao Anual</div>
              <div className="text-lg font-bold text-blue-700 dark:text-blue-400">{BRL(projecaoAnual)}</div>
              <div className="text-xs text-muted-foreground mt-1">Base: MRR atual x 12 meses</div>
            </div>
          </div>

          {/* Headcount por cliente */}
          {hc && hc.por_cliente.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Headcount por Cliente</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left p-2 font-medium">Cliente</th>
                        <th className="text-right p-2 font-medium">Headcount</th>
                        <th className="text-right p-2 font-medium">Folha Bruta</th>
                        <th className="text-right p-2 font-medium">Contrato</th>
                        <th className="text-right p-2 font-medium">% F/C</th>
                      </tr>
                    </thead>
                    <tbody>
                      {hc.por_cliente.map((c, i) => {
                        const pct = c.contrato_mensal > 0 ? (c.folha_bruta / c.contrato_mensal * 100) : 0;
                        return (
                          <tr key={i} className="border-b hover:bg-muted/30">
                            <td className="p-2 font-medium">{c.cliente}</td>
                            <td className="p-2 text-right">{c.headcount}</td>
                            <td className="p-2 text-right">{BRL(c.folha_bruta)}</td>
                            <td className="p-2 text-right">{c.contrato_mensal > 0 ? BRL(c.contrato_mensal) : '—'}</td>
                            <td className="p-2 text-right">
                              {pct > 0 ? (
                                <span className={pct > 50 ? 'text-yellow-600' : 'text-green-600'}>{pct.toFixed(1)}%</span>
                              ) : '—'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                    <tfoot>
                      <tr className="border-t-2 font-bold">
                        <td className="p-2">Total</td>
                        <td className="p-2 text-right">{hc.total_headcount}</td>
                        <td className="p-2 text-right">{BRL(hc.total_folha_bruta)}</td>
                        <td className="p-2 text-right" colSpan={2} />
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      ) : (
        /* Tab Fiscal */
        <div className="space-y-4">
          {/* Summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-green-200 bg-green-50/50 dark:bg-green-950/10">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium">Cumpridas</span>
                </div>
                <div className="text-3xl font-bold text-green-700">{bi?.fiscal.obrigacoes_cumpridas || 0}</div>
              </CardContent>
            </Card>
            <Card className="border-yellow-200 bg-yellow-50/50 dark:bg-yellow-950/10">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="h-5 w-5 text-yellow-600" />
                  <span className="text-sm font-medium">Pendentes</span>
                </div>
                <div className="text-3xl font-bold text-yellow-700">{bi?.fiscal.obrigacoes_pendentes || 0}</div>
              </CardContent>
            </Card>
            <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-950/10">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 mb-1">
                  <Receipt className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-medium">ISS + INSS + FGTS Estimado</span>
                </div>
                <div className="text-3xl font-bold text-blue-700">
                  {BRL((bi?.fiscal.proximas || []).reduce((a, o) => a + o.valor, 0))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Proximas obrigações */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Proximas Obrigacoes Fiscais — Competencia Marco/2026</CardTitle>
            </CardHeader>
            <CardContent>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left p-2 font-medium">Tipo</th>
                    <th className="text-left p-2 font-medium">Obrigacao</th>
                    <th className="text-left p-2 font-medium">Competencia</th>
                    <th className="text-left p-2 font-medium">Vencimento</th>
                    <th className="text-right p-2 font-medium">Valor Estimado</th>
                    <th className="text-center p-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(bi?.fiscal.proximas || []).map((o, i) => {
                    const venc = new Date(o.vencimento);
                    const hoje = new Date();
                    const dias = Math.ceil((venc.getTime() - hoje.getTime()) / 86400000);
                    const statusColor = dias < 0 ? 'bg-red-100 text-red-700' : dias <= 7 ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700';
                    const statusText = dias < 0 ? 'Vencida' : dias <= 7 ? `${dias}d` : `${dias}d`;

                    return (
                      <tr key={i} className="border-b hover:bg-muted/30">
                        <td className="p-2">
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-800">{o.tipo}</span>
                        </td>
                        <td className="p-2 font-medium">{o.nome}</td>
                        <td className="p-2">{o.competencia}</td>
                        <td className="p-2">{venc.toLocaleDateString('pt-BR')}</td>
                        <td className="p-2 text-right font-mono">{o.valor > 0 ? BRL(o.valor) : '—'}</td>
                        <td className="p-2 text-center">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColor}`}>{statusText}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
