'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, MessageSquare, Loader2 } from 'lucide-react';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || '') + '/api/v1/portal';

function getPortalHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Ticket {
  id: number;
  assunto: string;
  status: string;
  prioridade: string;
  data_abertura: string;
  ultima_atualizacao: string;
}

const statusLabels: Record<string, string> = {
  ABERTO: 'Aberto',
  EM_ANDAMENTO: 'Em Andamento',
  RESPONDIDO: 'Respondido',
  FECHADO: 'Fechado',
};

const statusColors: Record<string, string> = {
  ABERTO: 'bg-blue-100 text-blue-800',
  EM_ANDAMENTO: 'bg-yellow-100 text-yellow-800',
  RESPONDIDO: 'bg-green-100 text-green-800',
  FECHADO: 'bg-gray-100 text-gray-600',
};

const priorityLabels: Record<string, string> = {
  BAIXA: 'Baixa',
  NORMAL: 'Normal',
  ALTA: 'Alta',
  URGENTE: 'Urgente',
};

const priorityColors: Record<string, string> = {
  BAIXA: 'bg-gray-100 text-gray-600',
  NORMAL: 'bg-blue-100 text-blue-700',
  ALTA: 'bg-orange-100 text-orange-700',
  URGENTE: 'bg-red-100 text-red-700',
};

const filterTabs = [
  { key: '', label: 'Todos' },
  { key: 'ABERTO', label: 'Abertos' },
  { key: 'RESPONDIDO', label: 'Respondidos' },
  { key: 'FECHADO', label: 'Fechados' },
];

function formatDate(dateStr: string): string {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

export default function ChamadosPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('');

  useEffect(() => {
    fetchTickets();
  }, [activeFilter]);

  async function fetchTickets() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (activeFilter) params.set('status', activeFilter);
      const res = await fetch(`${API_BASE}/tickets?${params.toString()}`, {
        headers: getPortalHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setTickets(Array.isArray(data) ? data : data.items || []);
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
          <h1 className="text-2xl font-bold text-gray-900">Chamados</h1>
          <p className="text-gray-500 text-sm mt-1">Gerencie suas solicitações e acompanhe respostas.</p>
        </div>
        <Link
          href="/area-cliente/chamados/novo"
          className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Novo Chamado
        </Link>
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
        {filterTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveFilter(tab.key)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeFilter === tab.key
                ? 'bg-white text-indigo-700 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : tickets.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">Nenhum chamado encontrado.</p>
          <p className="text-gray-400 text-sm mt-1">Abra um novo chamado para entrar em contato conosco.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Table header */}
          <div className="hidden sm:grid grid-cols-12 gap-4 px-6 py-3 bg-gray-50 border-b border-gray-200 text-xs font-medium text-gray-500 uppercase tracking-wider">
            <div className="col-span-4">Assunto</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-2">Prioridade</div>
            <div className="col-span-2">Abertura</div>
            <div className="col-span-2">Atualização</div>
          </div>

          {/* Table rows */}
          <div className="divide-y divide-gray-100">
            {tickets.map((ticket) => (
              <Link
                key={ticket.id}
                href={`/area-cliente/chamados/${ticket.id}`}
                className="grid grid-cols-1 sm:grid-cols-12 gap-2 sm:gap-4 px-6 py-4 hover:bg-gray-50 transition-colors items-center"
              >
                <div className="sm:col-span-4">
                  <p className="text-sm font-medium text-gray-900 truncate">{ticket.assunto}</p>
                  <p className="text-xs text-gray-400 sm:hidden mt-1">
                    {formatDate(ticket.data_abertura)}
                  </p>
                </div>
                <div className="sm:col-span-2">
                  <span
                    className={`inline-block text-xs font-medium px-2.5 py-0.5 rounded-full ${
                      statusColors[ticket.status] || 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {statusLabels[ticket.status] || ticket.status}
                  </span>
                </div>
                <div className="sm:col-span-2">
                  <span
                    className={`inline-block text-xs font-medium px-2.5 py-0.5 rounded-full ${
                      priorityColors[ticket.prioridade] || 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {priorityLabels[ticket.prioridade] || ticket.prioridade}
                  </span>
                </div>
                <div className="hidden sm:block sm:col-span-2 text-xs text-gray-500">
                  {formatDate(ticket.data_abertura)}
                </div>
                <div className="hidden sm:block sm:col-span-2 text-xs text-gray-500">
                  {formatDate(ticket.ultima_atualizacao)}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
