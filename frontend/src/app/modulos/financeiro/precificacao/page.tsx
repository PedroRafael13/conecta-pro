'use client';

import { useState, useEffect } from 'react';
import { Tag, Calculator, TrendingUp, ChevronRight, DollarSign, AlertCircle, Building2, Leaf, Camera, Monitor, RefreshCw, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import axios from 'axios';

// ─── API helper ─────────────────────────────────────────────────────────────

function makeApi() {
  const instance = axios.create({ timeout: 15000 });
  instance.interceptors.request.use((config) => {
    config.baseURL =
      typeof window !== 'undefined' && window.location.hostname === 'localhost'
        ? 'http://localhost:8080'
        : 'https://erp.conectamais.pro';
    const token =
      typeof window !== 'undefined'
        ? localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
        : '';
    if (token) (config.headers as any)['Authorization'] = `Bearer ${token}`;
    return config;
  });
  return instance;
}

// ─── Types ───────────────────────────────────────────────────────────────────

interface ContratoAnalise {
  nome: string;
  tipo: string;
  ticket_atual: number;
  custo_estimado: number;
  mc_pct: number;
  benchmark_minimo: number;
  status_preco: 'subprecificado' | 'adequado' | 'atencao';
  potencial_reajuste: number;
  recomendacao: string;
}

interface AnaliseContratos {
  total_contratos: number;
  contratos_subprecificados: number;
  potencial_reajuste_mensal: number;
  potencial_reajuste_anual: number;
  contratos: ContratoAnalise[];
  alertas: string[];
}

interface PricingResult {
  tipo_servico: string;
  descricao: string;
  unidade: string;
  quantidade: number;
  escala: string;
  localizacao: string;
  custo_estimado: number;
  breakdown_custo: {
    mao_obra_base: number;
    encargos_sociais: number;
    equipamentos_epi: number;
    supervisao: number;
    fator_localizacao: number;
    fator_escala: number;
  };
  precificacao: {
    preco_minimo: number;
    margem_minima_pct: number;
    preco_ideal: number;
    margem_ideal_pct: number;
    preco_premium: number;
    margem_premium_pct: number;
  };
  por_unidade: {
    custo_por_unidade: number;
    preco_minimo_por_unidade: number;
    preco_ideal_por_unidade: number;
  };
  comparativo_mercado: {
    contratos_encontrados: number;
    valor_medio_mercado: number;
    valor_minimo_mercado: number;
    valor_maximo_mercado: number;
  };
  recomendacao: string;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const TIPOS_SERVICO = [
  { value: 'portaria', label: 'Portaria', icon: Building2, unidade: 'postos', cor: 'blue', desc: 'Vigilantes presenciais 24h' },
  { value: 'limpeza', label: 'Limpeza', icon: CheckCircle, unidade: 'm²', cor: 'green', desc: 'Serviços de conservação' },
  { value: 'jardinagem', label: 'Jardinagem', icon: Leaf, unidade: 'm²', cor: 'emerald', desc: 'Manutenção de áreas verdes' },
  { value: 'seguranca_eletronica', label: 'Seg. Eletrônica', icon: Camera, unidade: 'câmeras', cor: 'purple', desc: 'CFTV e monitoramento' },
  { value: 'portaria_remota', label: 'Portaria Remota', icon: Monitor, unidade: 'pontos', cor: 'orange', desc: 'Monitoramento remoto 24h' },
];

const ESCALAS = [
  { value: '12x36', label: '12x36 (padrão)' },
  { value: '44h', label: '44h semanais' },
  { value: '24h', label: '24h contínuo' },
  { value: '12h_diurno', label: '12h diurno' },
  { value: '12h_noturno', label: '12h noturno' },
  { value: '8h', label: '8h comercial' },
];

const LOCALIZACOES = [
  { value: 'sp_capital', label: 'São Paulo Capital (+30%)' },
  { value: 'rj_capital', label: 'Rio de Janeiro Capital (+25%)' },
  { value: 'grandes_capitais', label: 'Grandes Capitais (+20%)' },
  { value: 'interior_sp', label: 'Interior SP (+10%)' },
  { value: 'interior_outros', label: 'Interior outros (padrão)' },
  { value: 'nordeste', label: 'Nordeste (-10%)' },
  { value: 'norte', label: 'Norte (-12%)' },
  { value: 'default', label: 'Padrão / Manaus' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmtCurrency(v: number) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);
}

function getMargemCor(pct: number) {
  if (pct >= 30) return 'text-green-600';
  if (pct >= 15) return 'text-blue-600';
  if (pct >= 10) return 'text-yellow-600';
  return 'text-red-600';
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function PrecificacaoPage() {
  const api = makeApi();

  const [tipo, setTipo] = useState('portaria');
  const [quantidade, setQuantidade] = useState<string>('1');
  const [escala, setEscala] = useState('12x36');
  const [localizacao, setLocalizacao] = useState('default');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PricingResult | null>(null);
  const [error, setError] = useState('');
  const [selectedMargem, setSelectedMargem] = useState<'minima' | 'ideal' | 'premium'>('ideal');

  // ─── Análise contratos ativos (dados reais CCT 2026) ──────────────────────
  const [analiseContratos, setAnaliseContratos] = useState<AnaliseContratos | null>(null);
  const [loadingAnalise, setLoadingAnalise] = useState(true);

  useEffect(() => {
    const fetchAnalise = async () => {
      try {
        const { data } = await api.get('/api/v1/financial/precificacao/contratos/analise');
        setAnaliseContratos(data);
      } catch {
        // silencioso — seção não aparece se falhar
      } finally {
        setLoadingAnalise(false);
      }
    };
    fetchAnalise();
  }, [api]);

  const tipoInfo = TIPOS_SERVICO.find(t => t.value === tipo);

  const handleCalcular = async () => {
    const qtd = parseFloat(quantidade);
    if (!qtd || qtd <= 0) {
      setError('Informe uma quantidade válida maior que zero.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const { data } = await api.post('/api/v1/financial/ai/pricing/calculate', {
        tipo,
        quantidade: qtd,
        escala,
        localizacao,
      });
      setResult(data);
    } catch {
      setError('Erro ao calcular precificação. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const precoSelecionado = result
    ? selectedMargem === 'minima'
      ? result.precificacao.preco_minimo
      : selectedMargem === 'premium'
      ? result.precificacao.preco_premium
      : result.precificacao.preco_ideal
    : 0;

  const margemSelecionada = result
    ? selectedMargem === 'minima'
      ? result.precificacao.margem_minima_pct
      : selectedMargem === 'premium'
      ? result.precificacao.margem_premium_pct
      : result.precificacao.margem_ideal_pct
    : 0;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-100 rounded-lg">
          <Tag className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Precificação Inteligente</h1>
          <p className="text-sm text-gray-500">Calcule o preço ideal para novos contratos com margem otimizada</p>
        </div>
        <div className="ml-auto">
          <Link href="/modulos/financeiro">
            <Button variant="outline" size="sm">← Voltar</Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* ── Formulário ── */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardContent className="p-5 space-y-5">
              <h2 className="font-semibold text-gray-800 flex items-center gap-2">
                <Calculator className="w-4 h-4 text-blue-500" />
                Parâmetros do Contrato
              </h2>

              {/* Tipo de serviço */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Serviço</label>
                <div className="grid grid-cols-1 gap-2">
                  {TIPOS_SERVICO.map(t => {
                    const Icon = t.icon;
                    const active = tipo === t.value;
                    return (
                      <button
                        key={t.value}
                        onClick={() => setTipo(t.value)}
                        className={`flex items-center gap-3 p-3 rounded-lg border-2 text-left transition-all ${
                          active
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-blue-300 text-gray-700'
                        }`}
                      >
                        <Icon className="w-4 h-4 flex-shrink-0" />
                        <div>
                          <div className="font-medium text-sm">{t.label}</div>
                          <div className="text-xs text-gray-500">{t.desc}</div>
                        </div>
                        {active && <ChevronRight className="w-4 h-4 ml-auto text-blue-500" />}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Quantidade */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantidade ({tipoInfo?.unidade ?? 'unidades'})
                </label>
                <input
                  type="number"
                  min="0.1"
                  step="0.5"
                  value={quantidade}
                  onChange={e => setQuantidade(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder={`Ex: 2 ${tipoInfo?.unidade ?? ''}`}
                />
              </div>

              {/* Escala */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Escala de Trabalho</label>
                <select
                  value={escala}
                  onChange={e => setEscala(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                >
                  {ESCALAS.map(e => (
                    <option key={e.value} value={e.value}>{e.label}</option>
                  ))}
                </select>
              </div>

              {/* Localização */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Localização</label>
                <select
                  value={localizacao}
                  onChange={e => setLocalizacao(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                >
                  {LOCALIZACOES.map(l => (
                    <option key={l.value} value={l.value}>{l.label}</option>
                  ))}
                </select>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {error}
                </div>
              )}

              <Button
                onClick={handleCalcular}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" /> Calculando...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Calculator className="w-4 h-4" /> Calcular Precificação
                  </span>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* ── Resultado ── */}
        <div className="lg:col-span-3 space-y-4">
          {!result && !loading && (
            <Card>
              <CardContent className="p-10 text-center">
                <Tag className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">Preencha os parâmetros e clique em Calcular</p>
                <p className="text-sm text-gray-400 mt-1">O sistema usará benchmarks do mercado de segurança patrimonial para gerar a precificação ideal.</p>
              </CardContent>
            </Card>
          )}

          {loading && (
            <Card>
              <CardContent className="p-10 text-center">
                <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
                <p className="text-gray-600">Calculando precificação com IA...</p>
              </CardContent>
            </Card>
          )}

          {result && !loading && (
            <>
              {/* Seleção de margem */}
              <Card>
                <CardContent className="p-5">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-green-500" />
                    Escolha a Margem
                  </h3>
                  <div className="grid grid-cols-3 gap-3">
                    {(
                      [
                        { key: 'minima' as const, label: 'Mínima', pct: result.precificacao.margem_minima_pct, preco: result.precificacao.preco_minimo, desc: 'Mínimo viável', bg: 'bg-yellow-50 border-yellow-300' },
                        { key: 'ideal' as const, label: 'Ideal', pct: result.precificacao.margem_ideal_pct, preco: result.precificacao.preco_ideal, desc: 'Recomendado', bg: 'bg-blue-50 border-blue-400' },
                        { key: 'premium' as const, label: 'Premium', pct: result.precificacao.margem_premium_pct, preco: result.precificacao.preco_premium, desc: 'Alta margem', bg: 'bg-green-50 border-green-400' },
                      ] as { key: 'minima' | 'ideal' | 'premium'; label: string; pct: number; preco: number; desc: string; bg: string }[]
                    ).map(m => (
                      <button
                        key={m.key}
                        onClick={() => setSelectedMargem(m.key)}
                        className={`p-3 rounded-xl border-2 text-center transition-all ${
                          selectedMargem === m.key
                            ? m.bg + ' ring-2 ring-offset-1 ring-blue-400'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className={`text-lg font-bold ${getMargemCor(m.pct)}`}>{m.pct}%</div>
                        <div className="text-sm font-semibold text-gray-700">{m.label}</div>
                        <div className="text-xs text-gray-500">{fmtCurrency(m.preco)}</div>
                        <div className="text-xs text-gray-400 mt-1">{m.desc}</div>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Preço selecionado */}
              <Card className="border-2 border-blue-400 bg-blue-50">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-blue-600 font-medium">Preço Sugerido ({selectedMargem})</p>
                      <p className="text-3xl font-bold text-blue-700">{fmtCurrency(precoSelecionado)}</p>
                      <p className="text-sm text-blue-500">
                        Margem: <span className={`font-semibold ${getMargemCor(margemSelecionada)}`}>{margemSelecionada}%</span>
                        {' '}• Por {result.unidade}: {fmtCurrency(result.por_unidade.preco_ideal_por_unidade)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-blue-500">Custo estimado</p>
                      <p className="text-xl font-bold text-blue-600">{fmtCurrency(result.custo_estimado)}</p>
                      <p className="text-xs text-blue-400">{result.quantidade} {result.unidade} | {result.escala}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Breakdown de custos */}
              <Card>
                <CardContent className="p-5">
                  <h3 className="font-semibold text-gray-800 mb-3">Composição do Custo</h3>
                  <div className="space-y-2">
                    {[
                      { label: 'Mão de obra base', value: result.breakdown_custo.mao_obra_base },
                      { label: 'Encargos sociais (CLT)', value: result.breakdown_custo.encargos_sociais },
                      { label: 'Equipamentos / EPI', value: result.breakdown_custo.equipamentos_epi },
                      { label: 'Supervisão', value: result.breakdown_custo.supervisao },
                    ].map(item => {
                      const pct = result.custo_estimado > 0 ? (item.value / result.custo_estimado * 100) : 0;
                      return (
                        <div key={item.label} className="flex items-center gap-3">
                          <div className="w-36 text-xs text-gray-500 flex-shrink-0">{item.label}</div>
                          <div className="flex-1 bg-gray-100 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${Math.min(100, pct)}%` }}
                            />
                          </div>
                          <div className="w-24 text-xs text-gray-700 text-right font-medium">{fmtCurrency(item.value)}</div>
                          <div className="w-10 text-xs text-gray-400 text-right">{pct.toFixed(0)}%</div>
                        </div>
                      );
                    })}
                    <div className="border-t pt-2 flex justify-between text-sm font-semibold">
                      <span>Total (c/ fator localização {result.breakdown_custo.fator_localizacao}x)</span>
                      <span className="text-blue-700">{fmtCurrency(result.custo_estimado)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Comparativo de mercado */}
              {result.comparativo_mercado.contratos_encontrados > 0 && (
                <Card>
                  <CardContent className="p-5">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-purple-500" />
                      Comparativo com Contratos Existentes
                    </h3>
                    <div className="grid grid-cols-3 gap-3 text-center">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-xs text-gray-500">Contratos similares</p>
                        <p className="text-xl font-bold text-gray-700">{result.comparativo_mercado.contratos_encontrados}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-xs text-gray-500">Valor médio</p>
                        <p className="text-lg font-bold text-blue-600">{fmtCurrency(result.comparativo_mercado.valor_medio_mercado)}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-xs text-gray-500">Faixa</p>
                        <p className="text-xs font-medium text-gray-600">
                          {fmtCurrency(result.comparativo_mercado.valor_minimo_mercado)}
                          {' '}–{' '}
                          {fmtCurrency(result.comparativo_mercado.valor_maximo_mercado)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recomendação do AI */}
              <Card className="border-l-4 border-l-amber-400 bg-amber-50">
                <CardContent className="p-4">
                  <p className="text-sm font-semibold text-amber-700 mb-1">💡 Recomendação do AI</p>
                  <p className="text-sm text-amber-800">{result.recomendacao}</p>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>

      {/* ── Análise dos contratos ativos (dados reais CCT 2026) ─────────────── */}
      {!loadingAnalise && analiseContratos && (
        <div className="space-y-4">
          {/* Alertas de subprecificação */}
          {analiseContratos.contratos_subprecificados > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <p className="text-sm font-semibold text-amber-900">
                ⚠️ {analiseContratos.contratos_subprecificados} contrato(s) subprecificado(s)
              </p>
              <p className="text-sm text-amber-700 mt-1">
                Potencial de reajuste:{' '}
                <strong>+{fmtCurrency(analiseContratos.potencial_reajuste_mensal)}/mês</strong>
                {' '}|{' '}
                <strong>+{fmtCurrency(analiseContratos.potencial_reajuste_anual)}/ano</strong>
              </p>
            </div>
          )}

          {/* Tabela de contratos */}
          <div>
            <h2 className="text-base font-semibold text-gray-900 mb-3">
              Análise dos Contratos Ativos — CCT 2026 ({analiseContratos.total_contratos} contratos)
            </h2>
            <div className="space-y-2">
              {analiseContratos.contratos.map((c, i) => (
                <div key={i}
                  className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-sm truncate">{c.nome}</p>
                    <p className="text-xs text-gray-500 mt-0.5 capitalize">
                      {c.tipo.replace(/_/g, ' ')} · custo est. {fmtCurrency(c.custo_estimado)}
                    </p>
                    {c.recomendacao !== 'OK — precificação adequada' && (
                      <p className="text-xs text-amber-700 mt-0.5">{c.recomendacao}</p>
                    )}
                  </div>
                  <div className="text-right ml-4 flex-shrink-0">
                    <p className="font-semibold text-gray-900">{fmtCurrency(c.ticket_atual)}</p>
                    <p className={`text-sm font-medium ${
                      c.status_preco === 'subprecificado' ? 'text-red-600' :
                      c.status_preco === 'atencao' ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      MC: {c.mc_pct}%
                      {c.status_preco === 'subprecificado' ? ' ⚠️' : ' ✅'}
                    </p>
                    {c.potencial_reajuste > 0 && (
                      <p className="text-xs text-amber-600">
                        +{fmtCurrency(c.potencial_reajuste)}/mês possível
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
