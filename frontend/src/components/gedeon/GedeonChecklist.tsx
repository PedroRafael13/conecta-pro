'use client'

import { useState, useEffect } from 'react'
import { Loader2, X, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'

interface MovimentacaoItem {
  tipo: string
  funcionario?: string
  doc_pendente?: string
  requer_decisao?: boolean
  mensagem?: string
}

interface OcorrenciaItem {
  tipo: string
  data?: string
  requer_doc?: boolean
  mensagem?: string
}

interface PendenciaItem {
  requer_decisao?: boolean
  mensagem?: string
}

interface Certidoes {
  ok: number
  alerta: number
  critico: number
}

interface GedeonContextData {
  score_prontidao: number
  movimentacao_pessoal: MovimentacaoItem[]
  ocorrencias: OcorrenciaItem[]
  certidoes: Certidoes
  pendencias: PendenciaItem[]
  tipo_kit: string | null
}

interface Props {
  clienteId: string
  competencia: string
  clienteNome: string
  onConfirmar: (dados: Record<string, unknown>) => void
  onCancelar: () => void
}

function getToken(): string {
  if (typeof window === 'undefined') return ''
  try {
    return localStorage.getItem('access_token') || localStorage.getItem('token') || ''
  } catch { return '' }
}

export default function GedeonChecklist({ clienteId, competencia, clienteNome, onConfirmar, onCancelar }: Props) {
  const [ctx, setCtx] = useState<GedeonContextData | null>(null)
  const [loading, setLoading] = useState(true)
  const [observacoes, setObservacoes] = useState('')
  const [confirmacoesExtra, setConfirmacoesExtra] = useState<Record<string, boolean>>({})

  useEffect(() => {
    if (!clienteId) { setLoading(false); return }
    const load = async () => {
      try {
        const res = await fetch(`/api/v1/gedeon/context/${clienteId}/${competencia}`, {
          headers: { Authorization: `Bearer ${getToken()}` },
        })
        if (res.ok) setCtx(await res.json())
      } catch (e) {
        console.error('GEDEON context error:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [clienteId, competencia])

  const score = ctx?.score_prontidao ?? 100
  const scoreColor = score >= 90 ? 'text-green-600' : score >= 70 ? 'text-orange-500' : 'text-red-600'

  const handleConfirmar = () => {
    onConfirmar({ cliente_id: clienteId, competencia, observacoes, confirmacoes: confirmacoesExtra, score_gedeon: score, tipo_kit: ctx?.tipo_kit || 'maos_de_obra' })
  }

  const setDecisao = (key: string, val: boolean) => setConfirmacoesExtra(p => ({ ...p, [key]: val }))

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 flex flex-col items-center gap-3 shadow-2xl">
          <Loader2 className="w-8 h-8 text-[#1E3A5F] animate-spin" />
          <p className="text-sm text-gray-500">GEDEON analisando <strong>{clienteNome}</strong>...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 w-full max-w-2xl my-4">
        <div className="bg-[#1E3A5F] rounded-t-2xl px-6 py-4 flex items-start justify-between">
          <div>
            <p className="text-white/60 text-xs uppercase tracking-wider mb-0.5">GEDEON — Checklist de Montagem</p>
            <h2 className="text-white font-bold text-lg">{clienteNome}</h2>
            <p className="text-white/50 text-xs mt-0.5">Competência: {competencia}</p>
          </div>
          <div className="bg-white rounded-xl px-3 py-1.5 mt-1">
            <span className={`text-2xl font-bold ${scoreColor}`}>{score}%</span>
          </div>
        </div>

        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          {!ctx && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-700">
              ℹ️ GEDEON sem dados acumulados para esta competência. A montagem prosseguirá normalmente.
            </div>
          )}

          {ctx && (
            <div className="border rounded-xl p-4">
              <h3 className="font-semibold text-[#1E3A5F] mb-3 text-sm">🔒 Certidões da Empresa</h3>
              {(ctx.certidoes?.critico ?? 0) > 0 ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 space-y-2">
                  <div className="flex items-center gap-2 text-red-700 text-sm font-medium">
                    <XCircle className="w-4 h-4 flex-shrink-0" />
                    {ctx.certidoes.critico} certidão(ões) vencida(s)
                  </div>
                  <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                    <input type="checkbox" className="rounded" checked={!!confirmacoesExtra.montar_com_certidao_vencida}
                      onChange={e => setDecisao('montar_com_certidao_vencida', e.target.checked)} />
                    Montar kit mesmo com certidão vencida
                  </label>
                </div>
              ) : (ctx.certidoes?.alerta ?? 0) > 0 ? (
                <div className="flex items-center gap-2 text-orange-600 text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  {ctx.certidoes.alerta} certidão(ões) próximas do vencimento
                </div>
              ) : (
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircle className="w-4 h-4" />
                  {ctx.certidoes?.ok ?? 0} certidões válidas
                </div>
              )}
            </div>
          )}

          {ctx && ctx.movimentacao_pessoal?.length > 0 && (
            <div className="border rounded-xl p-4">
              <h3 className="font-semibold text-[#1E3A5F] mb-3 text-sm flex items-center gap-2">
                👥 Movimentação de Pessoal
                <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">{ctx.movimentacao_pessoal.length}</span>
              </h3>
              <div className="space-y-2">
                {ctx.movimentacao_pessoal.map((item, i) => (
                  <div key={i} className="flex items-start gap-2 bg-gray-50 rounded-lg p-2">
                    <span className="text-base flex-shrink-0">
                      {item.tipo === 'admissao' ? '🟢' : item.tipo === 'demissao' ? '🔴' : item.tipo === 'atestado' ? '🟡' : item.tipo === 'ferias' ? '🔵' : '⚪'}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-800">
                        {item.tipo?.charAt(0).toUpperCase() + item.tipo?.slice(1)}{item.funcionario ? ` — ${item.funcionario}` : ''}
                      </p>
                      {item.doc_pendente && <p className="text-xs text-orange-600 mt-0.5">📎 {item.doc_pendente}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {ctx && ctx.ocorrencias?.length > 0 && (
            <div className="border rounded-xl p-4">
              <h3 className="font-semibold text-[#1E3A5F] mb-3 text-sm flex items-center gap-2">
                ⚠️ Ocorrências
                <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full">{ctx.ocorrencias.length}</span>
              </h3>
              <div className="space-y-2">
                {ctx.ocorrencias.map((item, i) => (
                  <div key={i} className="bg-yellow-50 border border-yellow-200 rounded-lg p-2 text-sm">
                    <p className="font-medium text-gray-800">{item.tipo}{item.data ? ` — ${item.data}` : ''}</p>
                    {item.requer_doc && <p className="text-xs text-orange-600 mt-0.5">📎 Documento necessário</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {ctx && ctx.pendencias?.some(p => p.requer_decisao) && (
            <div className="border border-orange-200 rounded-xl p-4 bg-orange-50">
              <h3 className="font-semibold text-orange-800 mb-3 text-sm">🤖 GEDEON precisa da sua decisão</h3>
              <div className="space-y-3">
                {ctx.pendencias.filter(p => p.requer_decisao).map((item, i) => (
                  <div key={i} className="bg-white rounded-lg border border-orange-200 p-3">
                    <p className="text-sm text-gray-700 mb-2">{item.mensagem}</p>
                    <div className="flex gap-2">
                      <button onClick={() => setDecisao(`decisao_${i}`, true)}
                        className={`px-3 py-1 rounded text-sm font-medium ${confirmacoesExtra[`decisao_${i}`] === true ? 'bg-[#F97316] text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                        Sim, continuar
                      </button>
                      <button onClick={() => setDecisao(`decisao_${i}`, false)}
                        className={`px-3 py-1 rounded text-sm font-medium ${confirmacoesExtra[`decisao_${i}`] === false ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
                        Não, aguardar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {ctx && score >= 90 && !ctx.movimentacao_pessoal?.length && !ctx.ocorrencias?.length && !(ctx.certidoes?.critico) && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
              <p className="text-sm text-green-700 font-medium">GEDEON não identificou pendências. Kit pronto para montagem.</p>
            </div>
          )}

          <div className="border rounded-xl p-4">
            <h3 className="font-semibold text-[#1E3A5F] mb-1 text-sm">📝 Observações</h3>
            <p className="text-xs text-gray-400 mb-2">Informações que os sistemas não capturam automaticamente:</p>
            <textarea value={observacoes} onChange={e => setObservacoes(e.target.value)}
              placeholder="ex: Funcionário apresentou atestado mas ainda não está no sistema..." rows={3}
              className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none focus:outline-none focus:border-[#1E3A5F]" />
          </div>
        </div>

        <div className="border-t px-6 py-4 flex justify-between items-center bg-gray-50 rounded-b-2xl">
          <button onClick={onCancelar} className="flex items-center gap-1 px-3 py-2 text-gray-500 hover:text-gray-700 text-sm">
            <X className="w-4 h-4" /> Cancelar
          </button>
          <button onClick={handleConfirmar} disabled={score < 50}
            className={`px-6 py-2 rounded-lg text-sm font-medium text-white ${score >= 50 ? 'bg-[#F97316] hover:bg-orange-600' : 'bg-gray-300 cursor-not-allowed'}`}>
            {score >= 90 ? '✅ Confirmar e Montar' : score >= 70 ? '⚠️ Montar com alertas' : '🔴 Score insuficiente'}
          </button>
        </div>
      </div>
    </div>
  )
}
