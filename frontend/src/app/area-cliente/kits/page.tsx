'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { FolderOpen, Loader2, FileText, Search } from 'lucide-react';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || '') + '/api/v1/portal';

function getPortalHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Kit {
  id: number;
  mes_referencia: string;
  status: string;
  percentual_conclusao: number;
  total_documentos: number;
}

const statusLabels: Record<string, string> = {
  em_montagem: 'Em Montagem',
  completo: 'Completo',
  enviado: 'Enviado',
  conferido: 'Conferido',
  aprovado: 'Aprovado',
};

const statusColors: Record<string, string> = {
  em_montagem: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  completo: 'bg-blue-100 text-blue-800 border-blue-200',
  enviado: 'bg-green-100 text-green-800 border-green-200',
  conferido: 'bg-purple-100 text-purple-800 border-purple-200',
  aprovado: 'bg-emerald-100 text-emerald-800 border-emerald-200',
};

const cardBorderColors: Record<string, string> = {
  em_montagem: 'border-l-yellow-400',
  completo: 'border-l-blue-400',
  enviado: 'border-l-green-400',
  conferido: 'border-l-purple-400',
  aprovado: 'border-l-emerald-400',
};

export default function KitsPage() {
  const [kits, setKits] = useState<Kit[]>([]);
  const [loading, setLoading] = useState(true);
  const [monthFilter, setMonthFilter] = useState('');

  useEffect(() => {
    fetchKits();
  }, [monthFilter]);

  async function fetchKits() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (monthFilter) params.set('mes_referencia', monthFilter);
      const res = await fetch(`${API_BASE}/kits?${params.toString()}`, {
        headers: getPortalHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setKits(Array.isArray(data) ? data : data.items || []);
      }
    } catch {
      // silently handle
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meus Kits</h1>
          <p className="text-gray-500 text-sm mt-1">Kits documentais organizados por mês de referência.</p>
        </div>
        <div className="flex items-center gap-2">
          <Search className="h-4 w-4 text-gray-400" />
          <input
            type="month"
            value={monthFilter}
            onChange={(e) => setMonthFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-700"
            placeholder="Filtrar por mês"
          />
          {monthFilter && (
            <button
              onClick={() => setMonthFilter('')}
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Limpar
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : kits.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <FolderOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">Nenhum kit encontrado.</p>
          <p className="text-gray-400 text-sm mt-1">
            {monthFilter
              ? 'Tente selecionar outro período.'
              : 'Seus kits aparecerão aqui quando disponíveis.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {kits.map((kit) => (
            <Link
              key={kit.id}
              href={`/area-cliente/kits/${kit.id}`}
              className={`bg-white rounded-xl shadow-sm border border-gray-200 border-l-4 ${
                cardBorderColors[kit.status] || 'border-l-gray-400'
              } p-6 hover:shadow-md transition-shadow group`}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                    {kit.mes_referencia}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">Mês de referência</p>
                </div>
                <span
                  className={`text-xs font-medium px-2.5 py-1 rounded-full border ${
                    statusColors[kit.status] || 'bg-gray-100 text-gray-600 border-gray-200'
                  }`}
                >
                  {statusLabels[kit.status] || kit.status}
                </span>
              </div>

              {/* Progress */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Conclusão</span>
                  <span className="font-medium">{kit.percentual_conclusao}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full transition-all"
                    style={{ width: `${kit.percentual_conclusao}%` }}
                  />
                </div>
              </div>

              {/* Doc count */}
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <FileText className="h-4 w-4" />
                <span>{kit.total_documentos ?? 0} documentos</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
