'use client'

import { useState, useEffect } from 'react'
import { FileText, Eye, Calendar } from 'lucide-react'

const API_BASE = '/api/v1/people-management/portal'

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

export default function ContrachequePortalPage() {
  const [payslips, setPayslips] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPayslip, setSelectedPayslip] = useState<any>(null)

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/my-payslips`, { headers: getAuthHeaders() })
        if (res.ok) {
          const data = await res.json()
          setPayslips(data.items || data || [])
        }
      } catch {
        setPayslips([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3" />
          {[1, 2, 3].map(i => <div key={i} className="h-16 bg-gray-100 rounded" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600" />
          Meus Contracheques
        </h2>

        {payslips.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Nenhum contracheque disponível</p>
        ) : (
          <div className="space-y-3">
            {payslips.map((p: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium">Referência: {p.reference || `${p.month}/${p.year}`}</p>
                    <p className="text-sm text-gray-500">Líquido: R$ {(p.salario_liquido || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedPayslip(p)}
                  className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                >
                  <Eye className="w-4 h-4" /> Ver
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedPayslip && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Detalhes — {selectedPayslip.reference}</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Proventos</p>
              <p className="text-xl font-bold text-green-700">R$ {(selectedPayslip.total_proventos || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Descontos</p>
              <p className="text-xl font-bold text-red-700">R$ {(selectedPayslip.total_descontos || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
            </div>
            <div className="col-span-2 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Salário Líquido</p>
              <p className="text-2xl font-bold text-blue-700">R$ {(selectedPayslip.salario_liquido || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
            </div>
          </div>
          {selectedPayslip.proventos && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Proventos</h4>
              <table className="w-full text-sm">
                <thead><tr className="text-left text-gray-500"><th className="pb-2">Cód</th><th>Descrição</th><th>Ref</th><th className="text-right">Valor</th></tr></thead>
                <tbody>
                  {selectedPayslip.proventos.map((p: any, i: number) => (
                    <tr key={i} className="border-t"><td className="py-1">{p.codigo}</td><td>{p.descricao}</td><td>{p.ref}</td><td className="text-right">R$ {(p.valor || 0).toFixed(2)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {selectedPayslip.descontos && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Descontos</h4>
              <table className="w-full text-sm">
                <thead><tr className="text-left text-gray-500"><th className="pb-2">Cód</th><th>Descrição</th><th className="text-right">Valor</th></tr></thead>
                <tbody>
                  {selectedPayslip.descontos.map((d: any, i: number) => (
                    <tr key={i} className="border-t"><td className="py-1">{d.codigo}</td><td>{d.descricao}</td><td className="text-right text-red-600">R$ {(d.valor || 0).toFixed(2)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <button type="button" onClick={() => setSelectedPayslip(null)} className="mt-4 px-4 py-2 bg-gray-100 rounded-lg text-sm hover:bg-gray-200">Fechar</button>
        </div>
      )}
    </div>
  )
}
