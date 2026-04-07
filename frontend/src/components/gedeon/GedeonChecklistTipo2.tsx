'use client'

import { useState, useEffect } from 'react'

interface ChecklistTipo2Data {
  score_prontidao: number
  checklist: {
    nfs_e: { ok: boolean; dados?: Record<string, unknown> }
    boleto: { ok: boolean; dados?: Record<string, unknown> }
  }
  pode_enviar: boolean
  pendencias: string[]
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
    return (
      localStorage.getItem('access_token') ||
      sessionStorage.getItem('access_token') ||
      ''
    )
  } catch {
    return ''
  }
}

export default function GedeonChecklistTipo2({
  clienteId,
  competencia,
  clienteNome,
  onConfirmar,
  onCancelar,
}: Props) {
  const [ctx, setCtx] = useState<ChecklistTipo2Data | null>(null)
  const [loading, setLoading] = useState(true)
  const [observacoes, setObservacoes] = useState('')

  useEffect(() => {
    fetch(`/api/v1/gedeon/context/${clienteId}/${competencia}/tipo2`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
      .then((r) => r.json())
      .then(setCtx)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [clienteId, competencia])

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 text-center">
          <div className="w-8 h-8 border-4 border-[#1E3A5F] border-t-[#F97316] rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-500">
            GEDEON verificando {clienteNome}...
          </p>
        </div>
      </div>
    )
  }

  const score = ctx?.score_prontidao ?? 0
  const nfseOk = ctx?.checklist.nfs_e.ok ?? false
  const boletoOk = ctx?.checklist.boleto.ok ?? false

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="bg-[#1E3A5F] rounded-t-2xl px-6 py-4">
          <p className="text-white/70 text-xs uppercase tracking-wider">
            GEDEON — Kit Segurança Eletrônica
          </p>
          <h2 className="text-white font-bold text-lg">{clienteNome}</h2>
          <p className="text-white/60 text-sm">Competência: {competencia}</p>
        </div>

        <div className="p-6 space-y-4">
          {/* NFS-e */}
          <div
            className={`border rounded-xl p-4 ${
              nfseOk
                ? 'border-green-200 bg-green-50'
                : 'border-red-200 bg-red-50'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{nfseOk ? '✅' : '🔴'}</span>
              <div>
                <p className="font-semibold text-gray-800">
                  Nota Fiscal de Serviço (NFS-e)
                </p>
                <p className="text-sm text-gray-500">
                  {nfseOk
                    ? 'Emitida — pronta para o kit'
                    : 'Não emitida — necessária para envio'}
                </p>
                {nfseOk && ctx?.checklist.nfs_e.dados && (
                  <p className="text-xs text-green-700 mt-1">
                    Nº{' '}
                    {
                      (ctx.checklist.nfs_e.dados as Record<string, unknown>)
                        .numero as string
                    }{' '}
                    · R${' '}
                    {Number(
                      (ctx.checklist.nfs_e.dados as Record<string, unknown>)
                        .valor,
                    ).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Boleto */}
          <div
            className={`border rounded-xl p-4 ${
              boletoOk
                ? 'border-green-200 bg-green-50'
                : 'border-orange-200 bg-orange-50'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{boletoOk ? '✅' : '⚠️'}</span>
              <div>
                <p className="font-semibold text-gray-800">
                  Boleto de Cobrança
                </p>
                <p className="text-sm text-gray-500">
                  {boletoOk
                    ? 'Gerado — pronto para o kit'
                    : 'Não gerado — verificar financeiro'}
                </p>
              </div>
            </div>
          </div>

          {/* Pendências */}
          {(ctx?.pendencias.length ?? 0) > 0 && (
            <div className="border border-amber-200 bg-amber-50 rounded-xl p-3">
              <p className="text-xs font-semibold text-amber-800 mb-1">
                Pendências:
              </p>
              <ul className="space-y-0.5">
                {ctx?.pendencias.map((p, i) => (
                  <li key={i} className="text-xs text-amber-700">
                    • {p}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Score */}
          <div className="bg-gray-50 rounded-xl p-4 flex items-center justify-between">
            <span className="text-sm text-gray-600 font-medium">
              Prontidão do kit
            </span>
            <span
              className={`text-2xl font-bold ${
                score === 100
                  ? 'text-green-600'
                  : score >= 50
                    ? 'text-orange-500'
                    : 'text-red-600'
              }`}
            >
              {score}%
            </span>
          </div>

          {/* Observações */}
          <div>
            <p className="text-xs text-gray-500 mb-1">
              Observações (opcional):
            </p>
            <textarea
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              placeholder="ex: Reajuste de 5% a partir deste mês..."
              rows={2}
              className="w-full border border-gray-300 rounded-lg p-2 text-sm resize-none focus:outline-none focus:border-[#1E3A5F]"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="border-t px-6 py-4 flex justify-between bg-gray-50 rounded-b-2xl">
          <button
            onClick={onCancelar}
            className="text-gray-500 text-sm px-4 py-2 hover:text-gray-700"
          >
            Cancelar
          </button>
          <button
            onClick={() =>
              onConfirmar({
                cliente_id: clienteId,
                competencia,
                tipo_kit: 'seguranca_eletronica',
                score,
                observacoes,
              })
            }
            disabled={!ctx?.pode_enviar}
            className={`px-6 py-2 rounded-lg text-sm font-medium text-white transition-colors ${
              ctx?.pode_enviar
                ? 'bg-[#F97316] hover:bg-orange-600'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {ctx?.pode_enviar ? '✅ Montar Kit' : '⏳ Aguardando documentos'}
          </button>
        </div>
      </div>
    </div>
  )
}
