'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { FolderOpen, Loader2, FileText, Search, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || '') + '/api/v1/portal';

function getPortalHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface PortalKit {
  id: string;
  reference_month: string;
  status: string;
  completion_percentage: number;
  total_documents: number;
  total_employees: number;
}

interface PaginatedResponse {
  items: PortalKit[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
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

const statusFilterOptions = [
  { key: '', label: 'Todos' },
  { key: 'em_montagem', label: 'Em Montagem' },
  { key: 'completo', label: 'Completo' },
  { key: 'enviado', label: 'Enviado' },
  { key: 'conferido', label: 'Conferido' },
  { key: 'aprovado', label: 'Aprovado' },
];

function formatMonth(dateStr: string): string {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr + (dateStr.length <= 10 ? 'T00:00:00' : ''));
    return d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

export default function KitsPage() {
  const [kits, setKits] = useState<PortalKit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [total, setTotal] = useState(0);
  const pageSize = 12;

  const fetchKits = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      params.set('skip', String((currentPage - 1) * pageSize));
      params.set('limit', String(pageSize));
      if (statusFilter) params.set('status', statusFilter);

      const res = await fetch(`${API_BASE}/kits?${params.toString()}`, {
        headers: getPortalHeaders(),
      });

      if (res.status === 401) {
        toast.error('Sessao expirada. Faca login novamente.', { duration: 5000 });
        return;
      }

      if (!res.ok) {
        throw new Error('Erro ao carregar kits.');
      }

      const data: PaginatedResponse = await res.json();
      setKits(data.items || []);
      setTotal(data.total || 0);
      setTotalPages(data.pages || 0);
    } catch {
      setError('Erro ao carregar kits documentais.');
      toast.error('Erro ao carregar kits. Verifique sua conexao.', { duration: 5000 });
    } finally {
      setLoading(false);
    }
  }, [currentPage, statusFilter]);

  useEffect(() => {
    fetchKits();
  }, [fetchKits]);

  function handleFilterChange(newStatus: string) {
    setStatusFilter(newStatus);
    setCurrentPage(1);
  }

  return (
    <div className="space-y-6 pb-28">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meus Kits</h1>
          <p className="text-gray-500 text-sm mt-1">
            Kits documentais organizados por mes de referencia.
            {total > 0 && <span className="ml-1 font-medium">({total} kits)</span>}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        {statusFilterOptions.map((opt) => (
          <button
            key={opt.key}
            onClick={() => handleFilterChange(opt.key)}
            className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              statusFilter === opt.key
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
          <AlertTriangle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
          <button onClick={fetchKits} className="ml-auto text-red-600 hover:text-red-800 font-medium underline">
            Tentar novamente
          </button>
        </div>
      )}

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
            {statusFilter
              ? 'Tente selecionar outro filtro.'
              : 'Seus kits aparecerao aqui quando disponiveis.'}
          </p>
        </div>
      ) : (
        <>
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
                      {formatMonth(kit.reference_month)}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">Mes de referencia</p>
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
                    <span>Conclusao</span>
                    <span className="font-medium">{Number(kit.completion_percentage) || 0}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full transition-all"
                      style={{ width: `${Number(kit.completion_percentage) || 0}%` }}
                    />
                  </div>
                </div>

                {/* Doc count */}
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <FileText className="h-4 w-4" />
                  <span>{kit.total_documents ?? 0} documentos</span>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
                className="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <span className="text-sm text-gray-600">
                Pagina {currentPage} de {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage >= totalPages}
                className="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Proxima
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
