'use client'

import { useQuery } from '@tanstack/react-query'

interface CustoCategoria {
  categoria: string
  total: number
  qtd: number
}

interface TipoCusteio {
  tipo: string
  contratos: number
  receita_mensal: number
  ticket_medio: number
  pct_mrr: number
  custeio: {
    custo_direto: number
    overhead_rateado: number
    custo_total: number
  }
  margens: {
    mc_valor: number
    mc_pct: number
    margem_liquida_valor: number
    margem_liquida_pct: number
    meta_mc_pct: number
    gap_meta: number
  }
  classificacao: 'estrela' | 'atencao' | 'abacaxi'
  recomendacao: string
}

interface CusteioABC {
  timestamp: string
  mrr_total: number
  custo_total_mes: number
  resultado_estimado: number
  margem_global_pct: number
  cct_2026: {
    piso_vigilante: number
    custo_all_in_posto: number
    encargos_pct: number
  }
  custo_por_categoria: CustoCategoria[]
  analise_por_tipo: TipoCusteio[]
  alertas: string[]
}

interface ContratoCusteio {
  cliente: string
  tipo: string
  receita_mensal: number
  custo_estimado: number
  mc_valor: number
  mc_pct: number
  status: 'ok' | 'atencao' | 'critico'
}

const fetchWithAuth = (url: string) =>
  fetch(url, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token') ?? ''}` }
  }).then(r => r.json())

const classColor: Record<string, string> = {
  estrela: 'bg-green-100 text-green-800 border-green-200',
  atencao: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  abacaxi: 'bg-red-100 text-red-800 border-red-200',
}

const statusColor: Record<string, string> = {
  ok: 'text-green-600',
  atencao: 'text-yellow-600',
  critico: 'text-red-600',
}

export default function CusteioPage() {
  const { data: custeioABC, isLoading: loadingABC } = useQuery<CusteioABC>({
    queryKey: ['custeio-abc'],
    queryFn: () => fetchWithAuth('/api/v1/financial/custeio/abc'),
    staleTime: 10 * 60 * 1000,
    refetchInterval: 15 * 60 * 1000,
  })

  const { data: contratos, isLoading: loadingContratos } = useQuery<{
    contratos: ContratoCusteio[]
    total_contratos: number
  }>({
    queryKey: ['custeio-contratos'],
    queryFn: () => fetchWithAuth('/api/v1/financial/custeio/contratos'),
    staleTime: 10 * 60 * 1000,
  })

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          Custeio ABC
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Análise de margem por tipo de serviço — CCT SINDECOMPRESTS 2026
        </p>
      </div>

      {/* KPIs globais */}
      {!loadingABC && custeioABC && (
        <div className="grid grid-cols-4 gap-4">
          {[
            {
              label: 'MRR Total', sub: '10 contratos ativos',
              value: `R$ ${custeioABC.mrr_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
              color: 'text-gray-900'
            },
            {
              label: 'Custo Total Mês', sub: 'banco Inter (mês anterior)',
              value: `R$ ${custeioABC.custo_total_mes.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
              color: 'text-gray-900'
            },
            {
              label: 'Resultado Estimado', sub: 'MRR - custo total',
              value: `R$ ${custeioABC.resultado_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
              color: custeioABC.resultado_estimado > 0 ? 'text-green-600' : 'text-red-600'
            },
            {
              label: 'Margem Global', sub: `meta: ${custeioABC.analise_por_tipo[0]?.margens.meta_mc_pct ?? 35}%`,
              value: `${custeioABC.margem_global_pct}%`,
              color: custeioABC.margem_global_pct >= 25 ? 'text-green-600' :
                     custeioABC.margem_global_pct >= 15 ? 'text-yellow-600' : 'text-red-600'
            },
          ].map(kpi => (
            <div key={kpi.label} className="bg-white border border-gray-200 rounded-xl p-4">
              <p className="text-xs text-gray-500">{kpi.label}</p>
              <p className={`text-xl font-semibold mt-1 ${kpi.color}`}>{kpi.value}</p>
              <p className="text-xs text-gray-400 mt-1">{kpi.sub}</p>
            </div>
          ))}
        </div>
      )}

      {/* CCT 2026 */}
      {custeioABC?.cct_2026 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <p className="text-sm font-medium text-blue-900 mb-2">
            CCT SINDECOMPRESTS 2026 — Base de cálculo vigente
          </p>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-blue-600">Piso vigilante:</span>{' '}
              <strong>R$ {custeioABC.cct_2026.piso_vigilante.toLocaleString('pt-BR', {minimumFractionDigits: 2})}/mês</strong>
            </div>
            <div>
              <span className="text-blue-600">Encargos:</span>{' '}
              <strong>{custeioABC.cct_2026.encargos_pct}%</strong> (INSS+FGTS+férias+13º)
            </div>
            <div>
              <span className="text-blue-600">Custo all-in/posto:</span>{' '}
              <strong>R$ {custeioABC.cct_2026.custo_all_in_posto.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Análise por tipo de serviço */}
      <div>
        <h2 className="text-base font-medium text-gray-900 mb-3">
          Custeio ABC por Tipo de Serviço
        </h2>
        {loadingABC ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-24 bg-gray-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {custeioABC?.analise_por_tipo.map(tipo => (
              <div key={tipo.tipo}
                className="bg-white border border-gray-200 rounded-xl p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-gray-900 capitalize">
                        {tipo.tipo.replace(/_/g, ' ')}
                      </h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${classColor[tipo.classificacao]}`}>
                        {tipo.classificacao === 'estrela' ? '⭐ Estrela' :
                         tipo.classificacao === 'atencao' ? '⚠️ Atenção' : '❌ Abacaxi'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {tipo.contratos} contrato(s) | {tipo.pct_mrr}% do MRR
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">
                      R$ {tipo.receita_mensal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                    </p>
                    <p className="text-xs text-gray-500">receita/mês</p>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-3 text-sm">
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-500">Custo direto</p>
                    <p className="font-medium">
                      R$ {tipo.custeio.custo_direto.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-500">MC valor</p>
                    <p className={`font-medium ${tipo.margens.mc_pct >= 35 ? 'text-green-600' :
                      tipo.margens.mc_pct >= 20 ? 'text-yellow-600' : 'text-red-600'}`}>
                      R$ {tipo.margens.mc_valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-500">MC %</p>
                    <p className={`font-semibold text-lg ${tipo.margens.mc_pct >= 35 ? 'text-green-600' :
                      tipo.margens.mc_pct >= 20 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {tipo.margens.mc_pct}%
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-500">Gap da meta</p>
                    <p className={`font-medium ${tipo.margens.gap_meta <= 0 ? 'text-green-600' : 'text-orange-600'}`}>
                      {tipo.margens.gap_meta > 0 ? `-${tipo.margens.gap_meta}pp` : `+${Math.abs(tipo.margens.gap_meta)}pp`}
                    </p>
                  </div>
                </div>

                {tipo.recomendacao && tipo.classificacao !== 'estrela' && (
                  <p className="mt-2 text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-1.5">
                    {tipo.recomendacao}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alertas */}
      {custeioABC?.alertas && custeioABC.alertas.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-sm font-medium text-red-900 mb-2">⚠️ Alertas de custeio</p>
          {custeioABC.alertas.map((alerta, i) => (
            <p key={i} className="text-sm text-red-700">{alerta}</p>
          ))}
        </div>
      )}

      {/* Custos por categoria */}
      {custeioABC?.custo_por_categoria && custeioABC.custo_por_categoria.length > 0 && (
        <div>
          <h2 className="text-base font-medium text-gray-900 mb-3">
            Custos por Categoria (extrato Inter)
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {custeioABC.custo_por_categoria.slice(0, 9).map(cat => (
              <div key={cat.categoria}
                className="bg-white border border-gray-200 rounded-xl p-3">
                <p className="text-xs text-gray-500 capitalize">
                  {cat.categoria.replace(/_/g, ' ')}
                </p>
                <p className="font-semibold text-gray-900 mt-0.5">
                  R$ {cat.total.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                </p>
                <p className="text-xs text-gray-400">{cat.qtd} lançamentos</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabela de contratos */}
      {!loadingContratos && contratos?.contratos && contratos.contratos.length > 0 && (
        <div>
          <h2 className="text-base font-medium text-gray-900 mb-3">
            Custeio por Contrato Individual ({contratos.total_contratos})
          </h2>
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">Cliente</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">Tipo</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-500">Receita/mês</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-500">Custo est.</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-500">MC%</th>
                  <th className="text-center px-4 py-3 text-xs font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {contratos.contratos.map((c, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900 truncate max-w-[180px]">{c.cliente}</td>
                    <td className="px-4 py-3 text-gray-500 capitalize">{c.tipo?.replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3 text-right text-gray-900">
                      R$ {c.receita_mensal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">
                      R$ {c.custo_estimado.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${statusColor[c.status]}`}>
                      {c.mc_pct}%
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        c.status === 'ok' ? 'bg-green-100 text-green-700' :
                        c.status === 'atencao' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {c.status === 'ok' ? '✅ OK' : c.status === 'atencao' ? '⚠️ Atenção' : '❌ Crítico'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
