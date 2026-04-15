'use client'

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

interface PrecoRecomendado {
  preco_minimo: number
  preco_ideal_35pct: number
  preco_mercado_min: number
  preco_mercado_max: number
  preco_mercado_medio: number
}

interface SimuladorResult {
  timestamp: string
  input: {
    tipo_servico: string
    num_postos: number
    turno_noturno: boolean
    cct_2026: boolean
  }
  custo_clt_cct2026: {
    salario_base: number
    encargos_42pct: number
    vr_mensal: number
    vt_medio: number
    custo_total_por_posto: number
  }
  custo_direto_total: number
  precos_recomendados: PrecoRecomendado
  margens_no_preco_ideal: {
    mc_pct: number
    mc_valor: number
  }
  posicionamento_mercado: 'abaixo_mercado' | 'adequado' | 'premium'
  recomendacao: string
  alertas: string[]
  contratos_similares_ativos: Array<{ cliente: string; ticket_atual: number }>
}

interface ContratoAnalise {
  cliente: string
  tipo: string
  ticket_atual: number
  custo_estimado: number
  mc_pct: number
  benchmark_minimo: number
  status_preco: 'subprecificado' | 'adequado' | 'atencao'
  potencial_reajuste: number
  recomendacao: string
}

interface AnaliseContratos {
  total_contratos: number
  contratos_subprecificados: number
  potencial_reajuste_mensal: number
  potencial_reajuste_anual: number
  contratos: ContratoAnalise[]
  alertas: string[]
}

const fetchWithAuth = (url: string) =>
  fetch(url, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token') ?? ''}` }
  }).then(r => r.json())

export default function PrecificacaoPage() {
  const [tipoServico, setTipoServico] = useState('kit_mensal')
  const [numPostos, setNumPostos] = useState(1)
  const [turnoNoturno, setTurnoNoturno] = useState(false)

  const { data: simulador, isLoading: loadingSim } =
    useQuery<SimuladorResult>({
      queryKey: ['precificacao-simulador', tipoServico, numPostos, turnoNoturno],
      queryFn: () => fetchWithAuth(
        `/api/v1/financial/precificacao/simulador?tipo_servico=${tipoServico}&num_postos=${numPostos}&turno_noturno=${turnoNoturno}`
      ),
      staleTime: 5 * 60 * 1000,
    })

  const { data: analise, isLoading: loadingAnalise } =
    useQuery<AnaliseContratos>({
      queryKey: ['precificacao-analise'],
      queryFn: () => fetchWithAuth('/api/v1/financial/precificacao/contratos/analise'),
      staleTime: 10 * 60 * 1000,
    })

  const posicionamentoColor: Record<string, string> = {
    abaixo_mercado: 'text-red-600 bg-red-50 border-red-200',
    adequado: 'text-green-600 bg-green-50 border-green-200',
    premium: 'text-blue-600 bg-blue-50 border-blue-200',
  }

  const statusColor: Record<string, string> = {
    subprecificado: 'text-red-600',
    adequado: 'text-green-600',
    atencao: 'text-yellow-600',
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Precificação</h1>
        <p className="text-sm text-gray-500 mt-1">
          Simulador CCT SINDECOMPRESTS 2026 + benchmarks mercado Manaus/AM
        </p>
      </div>

      {/* Alertas análise */}
      {analise && analise.contratos_subprecificados > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-sm font-medium text-amber-900">
            ⚠️ {analise.contratos_subprecificados} contrato(s) subprecificado(s)
          </p>
          <p className="text-sm text-amber-700 mt-1">
            Potencial de reajuste:{' '}
            <strong>+R$ {analise.potencial_reajuste_mensal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}/mês</strong>
            {' '}|{' '}
            <strong>+R$ {analise.potencial_reajuste_anual.toLocaleString('pt-BR', {minimumFractionDigits: 2})}/ano</strong>
          </p>
        </div>
      )}

      {/* Simulador */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="text-base font-medium text-gray-900 mb-4">
          Simulador de Precificação
        </h2>

        {/* Inputs */}
        <div className="grid grid-cols-3 gap-4 mb-5">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Tipo de Serviço</label>
            <select
              value={tipoServico}
              onChange={e => setTipoServico(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            >
              <option value="kit_mensal">Kit Mensal (mão de obra)</option>
              <option value="portaria_remota">Portaria Remota</option>
              <option value="manutencao_cftv">Manutenção CFTV</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Número de Postos</label>
            <input
              type="number"
              min={1}
              max={20}
              value={numPostos}
              onChange={e => setNumPostos(Number(e.target.value))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Turno Noturno</label>
            <div className="flex items-center mt-2">
              <input
                type="checkbox"
                id="turno-noturno"
                checked={turnoNoturno}
                onChange={e => setTurnoNoturno(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="turno-noturno" className="text-sm text-gray-700">
                +20% adicional noturno (CCT 2026)
              </label>
            </div>
          </div>
        </div>

        {/* Resultado simulador */}
        {loadingSim ? (
          <div className="h-32 bg-gray-100 rounded-xl animate-pulse" />
        ) : simulador && !('error' in simulador) && (
          <div className="space-y-4">
            {/* Custo CLT */}
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-xs font-medium text-gray-700 mb-2">
                Composição do Custo — CCT 2026
              </p>
              <div className="grid grid-cols-4 gap-3 text-sm">
                {[
                  { label: 'Salário base', value: simulador.custo_clt_cct2026.salario_base },
                  { label: 'Encargos 42%', value: simulador.custo_clt_cct2026.encargos_42pct },
                  { label: 'VR mensal', value: simulador.custo_clt_cct2026.vr_mensal },
                  { label: 'Total/posto', value: simulador.custo_clt_cct2026.custo_total_por_posto },
                ].map(item => (
                  <div key={item.label} className="bg-white border border-gray-100 rounded-lg p-2">
                    <p className="text-xs text-gray-500">{item.label}</p>
                    <p className="font-medium">
                      R$ {item.value.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Preços recomendados */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
                <p className="text-xs text-red-600">Preço Mínimo</p>
                <p className="text-xl font-bold text-red-700 mt-1">
                  R$ {simulador.precos_recomendados.preco_minimo.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                </p>
                <p className="text-xs text-red-500">margem 20%</p>
              </div>
              <div className="bg-green-50 border border-green-300 rounded-xl p-4 text-center ring-2 ring-green-300">
                <p className="text-xs text-green-600 font-medium">✅ Preço Ideal</p>
                <p className="text-xl font-bold text-green-700 mt-1">
                  R$ {simulador.precos_recomendados.preco_ideal_35pct.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                </p>
                <p className="text-xs text-green-500">margem 35% — target</p>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center">
                <p className="text-xs text-gray-500">Mercado Manaus</p>
                <p className="text-sm font-semibold text-gray-700 mt-1">
                  R$ {simulador.precos_recomendados.preco_mercado_min.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                  {' '}—{' '}
                  R$ {simulador.precos_recomendados.preco_mercado_max.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                </p>
                <p className="text-xs text-gray-400">benchmark 2026</p>
              </div>
            </div>

            {/* Posicionamento */}
            <div className={`rounded-xl p-3 border text-sm ${posicionamentoColor[simulador.posicionamento_mercado]}`}>
              <strong>Posicionamento: </strong>{simulador.recomendacao}
            </div>

            {/* Alertas */}
            {simulador.alertas.length > 0 && (
              <div className="space-y-1">
                {simulador.alertas.map((alerta, i) => (
                  <p key={i} className="text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-1.5">
                    {alerta}
                  </p>
                ))}
              </div>
            )}

            {/* Contratos similares */}
            {simulador.contratos_similares_ativos.length > 0 && (
              <div>
                <p className="text-xs font-medium text-gray-700 mb-2">
                  Contratos similares ativos
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {simulador.contratos_similares_ativos.map((c, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-2 text-xs">
                      <p className="font-medium text-gray-700 truncate">{c.cliente}</p>
                      <p className="text-gray-500">
                        R$ {c.ticket_atual.toLocaleString('pt-BR', {minimumFractionDigits: 2})}/mês
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Análise dos contratos ativos */}
      <div>
        <h2 className="text-base font-medium text-gray-900 mb-3">
          Análise dos Contratos Ativos ({analise?.total_contratos ?? 0})
        </h2>
        {loadingAnalise ? (
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {analise?.contratos.map((c, i) => (
              <div key={i}
                className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-gray-900 text-sm">{c.cliente}</p>
                    <span className="text-xs text-gray-400 capitalize">
                      {c.tipo?.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{c.recomendacao}</p>
                </div>
                <div className="text-right ml-4">
                  <p className="font-semibold text-gray-900">
                    R$ {c.ticket_atual.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                  </p>
                  <p className={`text-sm font-medium ${statusColor[c.status_preco]}`}>
                    MC: {c.mc_pct}% {c.status_preco === 'subprecificado' ? '⚠️' : '✅'}
                  </p>
                  {c.potencial_reajuste > 0 && (
                    <p className="text-xs text-amber-600">
                      +R$ {c.potencial_reajuste.toLocaleString('pt-BR', {minimumFractionDigits: 2})}/mês possível
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
