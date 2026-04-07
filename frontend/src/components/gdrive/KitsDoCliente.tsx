'use client'

import { useState, useEffect } from 'react'

interface KitDrive {
  competencia: string
  total_docs: number
  share_link: string
  status: string
  criado_em?: string
}

interface Props {
  clienteId: string
  clienteNome?: string
  token?: string
}

const MESES: Record<string, string> = {
  '01': 'Janeiro',   '02': 'Fevereiro',
  '03': 'Março',     '04': 'Abril',
  '05': 'Maio',      '06': 'Junho',
  '07': 'Julho',     '08': 'Agosto',
  '09': 'Setembro',  '10': 'Outubro',
  '11': 'Novembro',  '12': 'Dezembro',
}

function formatarCompetencia(comp: string): string {
  try {
    const parts = comp.split('-')
    const ano = parts[0] ?? comp
    const mes = parts[1] ?? ''
    return `${(mes && MESES[mes]) ? MESES[mes] : mes} ${ano}`.trim()
  } catch { return comp }
}

function getToken(): string {
  if (typeof window === 'undefined') return ''
  try {
    return (
      localStorage.getItem('portal_token') ||
      localStorage.getItem('access_token') ||
      sessionStorage.getItem('access_token') ||
      ''
    )
  } catch { return '' }
}

export default function KitsDoCliente({
  clienteId, clienteNome, token
}: Props) {
  const [kits, setKits] = useState<KitDrive[]>([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  useEffect(() => {
    const carregar = async () => {
      try {
        const authToken = token || getToken()
        const url = token
          ? `/api/v1/gdrive/portal/${clienteId}/kits?token=${token}`
          : `/api/v1/portal/kits/historico-drive`

        const res = await fetch(url, {
          headers: authToken && !token
            ? { Authorization: `Bearer ${authToken}` }
            : {},
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setKits(data.kits || [])
      } catch {
        setErro('Não foi possível carregar os kits')
      } finally {
        setLoading(false)
      }
    }
    carregar()
  }, [clienteId, token])

  if (loading) return (
    <div className="flex items-center justify-center py-12">
      <div className="w-6 h-6 border-4 border-[#1E3A5F]
                      border-t-[#F97316] rounded-full animate-spin" />
      <span className="ml-3 text-gray-500 text-sm">
        Carregando kits...
      </span>
    </div>
  )

  if (erro) return (
    <div className="text-center py-8 text-red-500 text-sm">
      {erro}
    </div>
  )

  if (kits.length === 0) return (
    <div className="text-center py-12">
      <p className="text-4xl mb-3">📭</p>
      <p className="text-gray-500 text-sm">
        Nenhum kit disponível ainda.
      </p>
    </div>
  )

  return (
    <div className="space-y-3">
      {clienteNome && (
        <div className="bg-[#1E3A5F] rounded-xl px-4 py-3 mb-4">
          <p className="text-white/70 text-xs uppercase tracking-wider">
            Kits Documentais
          </p>
          <p className="text-white font-semibold">{clienteNome}</p>
        </div>
      )}

      {kits.map((kit, i) => (
        <div
          key={i}
          className="border border-gray-200 rounded-xl p-4 bg-white
                     hover:border-[#1E3A5F] hover:shadow-sm transition-all"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-gray-800">
                📁 {formatarCompetencia(kit.competencia)}
              </p>
              <p className="text-sm text-gray-500 mt-0.5">
                {kit.total_docs} documento{kit.total_docs !== 1 ? 's' : ''}
              </p>
            </div>
            <a
              href={kit.share_link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-[#F97316] text-white
                         px-4 py-2 rounded-lg text-sm font-medium
                         hover:bg-orange-600 transition-colors"
            >
              <span>Acessar</span>
              <span>↗</span>
            </a>
          </div>
        </div>
      ))}

      <p className="text-center text-xs text-gray-400 pt-2">
        {kits.length} kit{kits.length !== 1 ? 's' : ''} disponível
        {kits.length !== 1 ? 'is' : ''}
      </p>
    </div>
  )
}
