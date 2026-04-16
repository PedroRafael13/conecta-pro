'use client'

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

interface ContaReceber {
  id: string
  descricao?: string
  description?: string
  cliente?: string
  customer?: string
  customer_name?: string
  valor?: number
  amount?: number
  net_value?: number
  vencimento?: string
  due_date?: string
  status?: string
  categoria?: string
  category?: string
}

interface ReceivablesResponse {
  data?: ContaReceber[]
  items?: ContaReceber[]
  total?: number
  total_amount?: number
  vencendo_hoje?: number
  atrasadas?: number
  recebidas?: number
}

const fetchWithAuth = async (url: string) => {
  const token = typeof window !== 'undefined'
    ? (localStorage.getItem('access_token') ?? localStorage.getItem('token') ?? '')
    : ''
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

const statusLabel: Record<string, string> = {
  pendente: 'Pendente', pending: 'Pendente',
  paga: 'Paga', paid: 'Paga',
  vencido: 'Vencido', overdue: 'Vencido',
  cancelada: 'Cancelada',
}

const statusColor: Record<string, string> = {
  pendente: 'bg-yellow-100 text-yellow-700',
  pending: 'bg-yellow-100 text-yellow-700',
  paga: 'bg-green-100 text-green-700',
  paid: 'bg-green-100 text-green-700',
  vencido: 'bg-red-100 text-red-700',
  overdue: 'bg-red-100 text-red-700',
}

export default function ContasReceberPage() {
  const [statusFilter, setStatusFilter] = useState('todos')
  const [search, setSearch] = useState('')

  const { data, isLoading, error, refetch } = useQuery<ReceivablesResponse>({
    queryKey: ['receivables', statusFilter],
    queryFn: () => fetchWithAuth(
      `/api/v1/financial/receivables${statusFilter !== 'todos' ? `?status=${statusFilter}` : ''}`
    ),
    staleTime: 2 * 60 * 1000,
    retry: 1,
  })

  const { data: aging } = useQuery({
    queryKey: ['receivables-aging'],
    queryFn: () => fetchWithAuth('/api/v1/financial/receivables/aging'),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  void aging

  const items: ContaReceber[] = data?.data ?? data?.items ?? []
  const total = data?.total ?? items.length
  const totalAmount = data?.total_amount ?? items.reduce((s, i) => s + (i.net_value ?? i.valor ?? i.amount ?? 0), 0)
  const vencendoHoje = data?.vencendo_hoje ?? 0
  const atrasadas = data?.atrasadas ?? 0
  const recebidas = data?.recebidas ?? 0

  const filtered = items.filter(item => {
    const desc = (item.descricao ?? item.description ?? '').toLowerCase()
    const cli = (item.customer_name ?? item.cliente ?? item.customer ?? '').toLowerCase()
    return desc.includes(search.toLowerCase()) || cli.includes(search.toLowerCase())
  })

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            <span>↗</span> Contas a Receber
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Gerencie todas as contas a receber e cobranças pendentes
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => refetch()}
            className="flex items-center gap-1.5 px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            ↺ Atualizar
          </button>
          <button
            className="flex items-center gap-1.5 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Nova Conta
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total', value: total, color: 'text-gray-900' },
          { label: 'Vencendo Hoje', value: vencendoHoje, color: 'text-yellow-600' },
          { label: 'Atrasadas', value: atrasadas, color: 'text-red-600' },
          { label: 'Recebidas', value: recebidas, color: 'text-green-600' },
        ].map(card => (
          <div key={card.label} className="bg-white border border-gray-200 rounded-xl p-4">
            <p className="text-sm text-gray-500">{card.label}</p>
            <p className={`text-3xl font-semibold mt-1 ${card.color}`}>
              {isLoading ? '–' : card.value}
            </p>
          </div>
        ))}
      </div>

      {/* Filtros */}
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Buscar por descrição, cliente..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="todos">Todos os status</option>
          <option value="pendente">Pendente</option>
          <option value="vencido">Vencido</option>
          <option value="paga">Paga</option>
        </select>
      </div>

      {/* Lista */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2" />
            <p className="text-sm text-gray-500">Carregando contas...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center">
            <p className="text-sm text-red-600 mb-3">
              Erro ao carregar contas: {String(error)}
            </p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              Tentar novamente
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-2xl mb-2">↗</p>
            <p className="text-sm text-gray-500">Nenhuma conta a receber encontrada</p>
            <p className="text-xs text-gray-400 mt-1">
              Tente ajustar os filtros ou crie uma nova conta
            </p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">Descrição</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">Cliente</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">Vencimento</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-gray-500">Valor</th>
                <th className="text-center px-4 py-3 text-xs font-medium text-gray-500">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item, idx) => (
                <tr key={item.id ?? idx} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-900">{item.descricao ?? item.description ?? '—'}</td>
                  <td className="px-4 py-3 text-gray-600">{item.customer_name ?? item.description ?? item.cliente ?? item.customer ?? '—'}</td>
                  <td className="px-4 py-3 text-gray-600">
                    {(item.vencimento ?? item.due_date)
                      ? new Date(item.vencimento ?? item.due_date ?? '').toLocaleDateString('pt-BR')
                      : '—'}
                  </td>
                  <td className="px-4 py-3 text-right font-medium text-gray-900">
                    {(item.net_value ?? item.valor ?? item.amount ?? 0).toLocaleString('pt-BR', {
                      style: 'currency', currency: 'BRL'
                    })}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColor[item.status ?? ''] ?? 'bg-gray-100 text-gray-600'}`}>
                      {statusLabel[item.status ?? ''] ?? item.status ?? '—'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Total */}
      {filtered.length > 0 && (
        <div className="flex justify-between items-center text-sm text-gray-500">
          <span>{filtered.length} conta(s) exibida(s)</span>
          <span className="font-medium text-gray-900">
            Total:{' '}
            {totalAmount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </span>
        </div>
      )}
    </div>
  )
}
