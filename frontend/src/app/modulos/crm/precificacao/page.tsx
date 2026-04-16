'use client'

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

// ─── Tipos exatos do endpoint /financial/precificacao/simulador ───────────
interface CustoCLT {
  salario_base: number
  encargos_42pct: number
  vr_mensal: number
  vt_medio: number
  custo_total_por_posto: number
}

interface PrecosRecomendados {
  preco_minimo: number
  preco_ideal_35pct: number
  preco_mercado_min: number
  preco_mercado_max: number
  preco_mercado_medio: number
}

interface SimuladorResult {
  timestamp: string
  input: { tipo_servico: string; num_postos: number; turno_noturno: boolean; cct_2026: boolean }
  custo_clt_cct2026: CustoCLT
  custo_direto_total: number
  precos_recomendados: PrecosRecomendados
  margens_no_preco_ideal: { mc_pct: number; mc_valor: number }
  posicionamento_mercado: string
  recomendacao: string
  alertas: string[]
  contratos_similares_ativos: Array<{ nome: string; ticket_atual: number; tipo: string }>
}

// ─── Tipos exatos do endpoint /financial/precificacao/contratos/analise ───
interface ContratoAnalise {
  nome: string
  tipo: string
  ticket_atual: number
  custo_estimado: number
  mc_pct: number
  benchmark_minimo: number
  benchmark_maximo: number
  postos_estimados: number
  status_preco: string
  potencial_reajuste: number
  recomendacao: string
}

interface AnaliseContratos {
  timestamp: string
  total_contratos: number
  contratos_subprecificados: number
  potencial_reajuste_mensal: number
  potencial_reajuste_anual: number
  contratos: ContratoAnalise[]
  alertas: string[]
  nota_cct: string
}

// ─── Helpers ──────────────────────────────────────────────────────────────
const fetchAuth = (url: string) =>
  fetch(url, {
    headers: {
      Authorization: `Bearer ${typeof window !== 'undefined'
        ? (localStorage.getItem('access_token') ?? localStorage.getItem('token') ?? '')
        : ''}`,
    },
  }).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })

const brl = (v: number) =>
  (v ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

const TIPOS_SERVICO = [
  { id: 'portaria_presencial',  label: 'Portaria Presencial',  desc: 'Mão de obra CLT presencial (CCT 2026)' },
  { id: 'portaria_remota',      label: 'Portaria Remota',      desc: 'Monitoramento remoto 24h (Econdos)' },
  { id: 'manutencao_cftv',      label: 'Manutenção CFTV',      desc: 'CFTV e eletrônica' },
  { id: 'seguranca_eletronica', label: 'Seg. Eletrônica',      desc: 'Sistemas de segurança' },
  { id: 'facilities',           label: 'Facilities',           desc: 'Serviços gerais e limpeza' },
]

type AbaId = 'simulador' | 'analise'

// ─── Componente ───────────────────────────────────────────────────────────
export default function PrecificacaoPage() {
  const [tipoServico, setTipoServico]   = useState('portaria_presencial')
  const [numPostos, setNumPostos]       = useState(1)
  const [turnoNoturno, setTurnoNoturno] = useState(false)
  const [abaAtiva, setAbaAtiva]         = useState<AbaId>('simulador')

  const { data: simData, isLoading: simLoading, error: simError } = useQuery<SimuladorResult>({
    queryKey: ['precificacao-simulador', tipoServico, numPostos, turnoNoturno],
    queryFn: () => fetchAuth(
      `/api/v1/financial/precificacao/simulador?tipo_servico=${tipoServico}&num_postos=${numPostos}&turno_noturno=${turnoNoturno}`
    ),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })

  const { data: analiseData, isLoading: analiseLoading } = useQuery<AnaliseContratos>({
    queryKey: ['precificacao-analise'],
    queryFn: () => fetchAuth('/api/v1/financial/precificacao/contratos/analise'),
    staleTime: 10 * 60 * 1000,
    retry: 2,
  })

  const prec  = simData?.precos_recomendados
  const custo = simData?.custo_clt_cct2026
  const contratos = analiseData?.contratos ?? []

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Precificação — Comercial</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Simule preços ideais para propostas comerciais · CCT SINDECOMPRESTS 2026
          </p>
        </div>
        <div className="flex gap-1 bg-gray-100 p-1 rounded-xl">
          {(['simulador', 'analise'] as const).map(aba => (
            <button
              key={aba}
              onClick={() => setAbaAtiva(aba)}
              className={`px-4 py-1.5 text-sm rounded-lg transition-all ${
                abaAtiva === aba
                  ? 'bg-white text-gray-900 font-medium shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {aba === 'simulador' ? '🧮 Simulador' : '📋 Análise Contratos'}
            </button>
          ))}
        </div>
      </div>

      {/* ── ABA: SIMULADOR ─────────────────────────────────────────────── */}
      {abaAtiva === 'simulador' && (
        <div className="grid grid-cols-2 gap-6">

          {/* Parâmetros */}
          <div className="space-y-5">
            <div className="bg-white border border-gray-200 rounded-xl p-5">
              <p className="text-sm font-medium text-gray-900 mb-4">Parâmetros do Contrato</p>

              {/* Tipo de serviço */}
              <div className="mb-5">
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-2">
                  Tipo de Serviço
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {TIPOS_SERVICO.map(t => (
                    <button
                      key={t.id}
                      onClick={() => setTipoServico(t.id)}
                      className={`p-3 text-left rounded-xl border transition-all ${
                        tipoServico === t.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <p className={`text-sm font-medium ${tipoServico === t.id ? 'text-blue-700' : 'text-gray-900'}`}>
                        {t.label}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">{t.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Postos */}
              <div className="mb-5">
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-2">
                  Número de Postos
                </label>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setNumPostos(Math.max(1, numPostos - 1))}
                    className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50"
                  >
                    −
                  </button>
                  <span className="text-2xl font-semibold text-gray-900 w-8 text-center">{numPostos}</span>
                  <button
                    onClick={() => setNumPostos(numPostos + 1)}
                    className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-50"
                  >
                    +
                  </button>
                  <span className="text-sm text-gray-500">posto(s) de trabalho</span>
                </div>
              </div>

              {/* Turno noturno */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-900">Turno noturno</p>
                  <p className="text-xs text-gray-500">Adicional de 20% no salário</p>
                </div>
                <button
                  onClick={() => setTurnoNoturno(!turnoNoturno)}
                  className={`relative w-11 h-6 rounded-full transition-colors ${
                    turnoNoturno ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                    turnoNoturno ? 'translate-x-5' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>
            </div>

            {/* Composição CCT */}
            {custo && (
              <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                <p className="text-xs font-semibold text-blue-800 uppercase tracking-wide mb-3">
                  Composição CCT 2026 — {numPostos} posto(s)
                </p>
                <div className="space-y-2">
                  {[
                    ['Salário base',    (custo.salario_base    ?? 0) * numPostos],
                    ['Encargos 42%',    (custo.encargos_42pct  ?? 0) * numPostos],
                    ['Vale Refeição',   (custo.vr_mensal       ?? 0) * numPostos],
                    ['Vale Transporte', (custo.vt_medio        ?? 0) * numPostos],
                  ].map(([label, value]) => (
                    <div key={label as string} className="flex justify-between text-sm">
                      <span className="text-blue-700">{label}</span>
                      <span className="font-medium text-blue-900">{brl(value as number)}</span>
                    </div>
                  ))}
                  <div className="border-t border-blue-200 pt-2 flex justify-between text-sm font-semibold">
                    <span className="text-blue-800">Custo direto total</span>
                    <span className="text-blue-900">{brl((custo.custo_total_por_posto ?? 0) * numPostos)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Resultado */}
          <div className="space-y-4">
            {simLoading ? (
              <div className="bg-white border border-gray-200 rounded-xl p-8 text-center animate-pulse">
                <div className="h-6 bg-gray-100 rounded w-32 mx-auto mb-3" />
                <div className="h-12 bg-gray-100 rounded w-48 mx-auto" />
              </div>
            ) : simError ? (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                <p className="text-sm text-red-700">{String(simError)}</p>
              </div>
            ) : prec ? (
              <>
                {/* Preço ideal — destaque */}
                <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-6 text-white">
                  <p className="text-sm text-blue-200 mb-1">Preço ideal (MC 35%)</p>
                  <p className="text-4xl font-bold">
                    {brl((prec.preco_ideal_35pct ?? 0) * numPostos)}
                  </p>
                  <p className="text-sm text-blue-200 mt-1">
                    {brl(prec.preco_ideal_35pct ?? 0)}/posto
                    {simData?.posicionamento_mercado
                      ? ` · ${simData.posicionamento_mercado.toUpperCase()}`
                      : ''}
                  </p>
                  {simData?.margens_no_preco_ideal && (
                    <div className="mt-3 bg-blue-500/30 rounded-lg p-2 text-sm">
                      MC {simData.margens_no_preco_ideal.mc_pct}%
                      {' = '}
                      {brl((simData.margens_no_preco_ideal.mc_valor ?? 0) * numPostos)}/mês
                    </div>
                  )}
                </div>

                {/* Faixa de preços */}
                <div className="bg-white border border-gray-200 rounded-xl p-4">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                    Faixa de Preços
                  </p>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center rounded-lg px-3 py-2 bg-red-50">
                      <span className="text-sm text-gray-700">Preço mínimo (sem lucro)</span>
                      <span className="font-semibold text-red-600">
                        {brl((prec.preco_minimo ?? 0) * numPostos)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center rounded-lg px-3 py-2 bg-gray-50">
                      <span className="text-sm text-gray-700">Mercado (mín–máx)</span>
                      <span className="font-semibold text-gray-600">
                        {brl((prec.preco_mercado_min ?? 0) * numPostos)}
                        {' – '}
                        {brl((prec.preco_mercado_max ?? 0) * numPostos)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center rounded-lg px-3 py-2 bg-blue-50">
                      <span className="text-sm font-medium text-gray-700">Ideal Conecta PRO (MC 35%)</span>
                      <span className="font-semibold text-blue-600">
                        {brl((prec.preco_ideal_35pct ?? 0) * numPostos)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Recomendação */}
                {simData?.recomendacao && (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                    <p className="text-sm font-medium text-amber-800 mb-1">💡 Recomendação</p>
                    <p className="text-sm text-amber-700">{simData.recomendacao}</p>
                  </div>
                )}

                {/* Alertas */}
                {(simData?.alertas ?? []).map((a, i) => (
                  <div key={i} className="bg-orange-50 border border-orange-200 rounded-xl p-3">
                    <p className="text-sm text-orange-700">{a}</p>
                  </div>
                ))}
              </>
            ) : null}
          </div>
        </div>
      )}

      {/* ── ABA: ANÁLISE DE CONTRATOS ────────────────────────────────────── */}
      {abaAtiva === 'analise' && (
        <div className="space-y-4">
          {/* Resumo */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Total Contratos',   value: analiseData?.total_contratos ?? 0,                          color: 'text-gray-900',   fmt: false },
              { label: 'Subprecificados',   value: analiseData?.contratos_subprecificados ?? 0,                color: 'text-red-600',    fmt: false },
              { label: 'Potencial Mensal',  value: brl(analiseData?.potencial_reajuste_mensal ?? 0),           color: 'text-green-600',  fmt: true },
              { label: 'Potencial Anual',   value: brl(analiseData?.potencial_reajuste_anual ?? 0),            color: 'text-green-700',  fmt: true },
            ].map(k => (
              <div key={k.label} className="bg-white border border-gray-200 rounded-xl p-4">
                <p className="text-xs text-gray-500">{k.label}</p>
                <p className={`text-xl font-semibold mt-1 ${k.color}`}>
                  {analiseLoading ? '–' : String(k.value)}
                </p>
              </div>
            ))}
          </div>

          {/* Nota CCT */}
          {analiseData?.nota_cct && (
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-3">
              <p className="text-sm text-blue-700">{analiseData.nota_cct}</p>
            </div>
          )}

          {/* Tabela de contratos */}
          {analiseLoading ? (
            <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
              <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto" />
            </div>
          ) : contratos.length === 0 ? (
            <div className="bg-gray-50 rounded-xl p-8 text-center">
              <p className="text-gray-500 text-sm">Nenhum contrato para análise</p>
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100">
                    {['Contrato', 'Tipo', 'Postos', 'Ticket Atual', 'Custo Est.', 'MC %', 'Status', 'Potencial'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium text-gray-500">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {contratos.map((c, i) => (
                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-medium text-gray-900 max-w-[200px] truncate" title={c.nome}>
                        {c.nome}
                      </td>
                      <td className="px-4 py-3 text-gray-600 capitalize">
                        {(c.tipo ?? '').replace(/_/g, ' ')}
                      </td>
                      <td className="px-4 py-3 text-gray-600 text-center">
                        {c.postos_estimados ?? '–'}
                      </td>
                      <td className="px-4 py-3 text-gray-900">{brl(c.ticket_atual)}</td>
                      <td className="px-4 py-3 text-gray-600">{brl(c.custo_estimado)}</td>
                      <td className={`px-4 py-3 font-medium ${
                        (c.mc_pct ?? 0) >= 35
                          ? 'text-green-600'
                          : (c.mc_pct ?? 0) >= 20
                            ? 'text-yellow-600'
                            : 'text-red-600'
                      }`}>
                        {(c.mc_pct ?? 0).toFixed(1)}%
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          c.status_preco === 'adequado'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {c.status_preco ?? '–'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-green-600 font-medium">
                        {(c.potencial_reajuste ?? 0) > 0 ? brl(c.potencial_reajuste) : '–'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
