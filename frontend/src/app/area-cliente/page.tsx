'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { FolderOpen, Clock, MessageSquare, HelpCircle, ArrowRight, Loader2, RefreshCw, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { usePortalAuth } from './hooks/usePortalAuth';

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

interface PortalTicket {
  id: string;
  subject: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
}

const statusLabels: Record<string, string> = {
  em_montagem: 'Em Montagem',
  completo: 'Completo',
  enviado: 'Enviado',
  conferido: 'Conferido',
  aprovado: 'Aprovado',
};

const statusColors: Record<string, string> = {
  em_montagem: 'bg-yellow-100 text-yellow-800',
  completo: 'bg-blue-100 text-blue-800',
  enviado: 'bg-green-100 text-green-800',
  conferido: 'bg-purple-100 text-purple-800',
  aprovado: 'bg-emerald-100 text-emerald-800',
};

function formatMonth(dateStr: string): string {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr + (dateStr.length <= 10 ? 'T00:00:00' : ''));
    return d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

export default function DashboardPage() {
  const { clientName } = usePortalAuth();
  const [kits, setKits] = useState<PortalKit[]>([]);
  const [tickets, setTickets] = useState<PortalTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [kitsRes, ticketsRes] = await Promise.all([
        fetch(`${API_BASE}/kits?limit=5`, { headers: getPortalHeaders() }),
        fetch(`${API_BASE}/tickets?limit=5`, { headers: getPortalHeaders() }),
      ]);

      if (kitsRes.status === 401 || ticketsRes.status === 401) {
        toast.error('Sessao expirada. Faca login novamente.', { duration: 5000 });
        return;
      }

      if (kitsRes.ok) {
        const kData = await kitsRes.json();
        setKits(Array.isArray(kData) ? kData : kData.items || []);
      }

      if (ticketsRes.ok) {
        const tData = await ticketsRes.json();
        setTickets(Array.isArray(tData) ? tData : tData.items || []);
      }
    } catch {
      setError('Erro ao carregar dados do painel.');
      toast.error('Erro ao carregar dados do painel. Verifique sua conexao.', { duration: 5000 });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const kitsTotal = kits.length;
  const kitsPending = kits.filter((k) => ['em_montagem', 'enviado'].includes(k.status)).length;
  const ticketsOpen = tickets.filter((t) => t.status !== 'FECHADO').length;

  const statCards = [
    {
      label: 'Kits Disponiveis',
      value: kitsTotal,
      icon: FolderOpen,
      color: 'bg-indigo-50 text-indigo-600',
      iconBg: 'bg-indigo-100',
    },
    {
      label: 'Kits Pendentes',
      value: kitsPending,
      icon: Clock,
      color: 'bg-yellow-50 text-yellow-600',
      iconBg: 'bg-yellow-100',
    },
    {
      label: 'Chamados Abertos',
      value: ticketsOpen,
      icon: MessageSquare,
      color: 'bg-blue-50 text-blue-600',
      iconBg: 'bg-blue-100',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-28">
      {/* Welcome */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Bem-vindo, {clientName || 'Cliente'}!
          </h1>
          <p className="text-gray-500 mt-1">Acompanhe seus kits documentais e chamados.</p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-indigo-600 transition-colors"
          title="Atualizar dados"
        >
          <RefreshCw className="h-4 w-4" />
          Atualizar
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
          <AlertTriangle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
          <button
            onClick={fetchData}
            className="ml-auto text-red-600 hover:text-red-800 font-medium underline"
          >
            Tentar novamente
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${card.iconBg}`}>
                  <Icon className={`h-6 w-6 ${card.color.split(' ')[1]}`} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">{card.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Kits */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Kits Recentes</h2>
          <Link
            href="/area-cliente/kits"
            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1"
          >
            Ver todos <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="divide-y divide-gray-100">
          {kits.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-400 text-sm">
              Nenhum kit disponivel no momento.
            </div>
          ) : (
            kits.map((kit) => (
              <div key={kit.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-sm font-medium text-gray-900">
                    {formatMonth(kit.reference_month)}
                  </div>
                  <span
                    className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
                      statusColors[kit.status] || 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {statusLabels[kit.status] || kit.status}
                  </span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full"
                      style={{ width: `${Number(kit.completion_percentage) || 0}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 w-10 text-right">
                    {Number(kit.completion_percentage) || 0}%
                  </span>
                  <Link
                    href={`/area-cliente/kits/${kit.id}`}
                    className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Ver
                  </Link>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Tickets */}
      {tickets.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Chamados Recentes</h2>
            <Link
              href="/area-cliente/chamados"
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1"
            >
              Ver todos <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="divide-y divide-gray-100">
            {tickets.map((ticket) => (
              <Link
                key={ticket.id}
                href={`/area-cliente/chamados/${ticket.id}`}
                className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-900 truncate max-w-xs">
                    {ticket.subject}
                  </span>
                  <span
                    className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
                      ticket.status === 'ABERTO'
                        ? 'bg-blue-100 text-blue-800'
                        : ticket.status === 'RESPONDIDO'
                        ? 'bg-green-100 text-green-800'
                        : ticket.status === 'FECHADO'
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {ticket.status === 'ABERTO' ? 'Aberto' : ticket.status === 'RESPONDIDO' ? 'Respondido' : ticket.status === 'FECHADO' ? 'Fechado' : ticket.status}
                  </span>
                </div>
                <ArrowRight className="h-4 w-4 text-gray-400" />
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick Action */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-xl p-6 text-white flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="bg-white/20 p-3 rounded-lg">
            <HelpCircle className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Precisa de ajuda?</h3>
            <p className="text-indigo-100 text-sm">
              Abra um chamado e nossa equipe respondera rapidamente.
            </p>
          </div>
        </div>
        <Link
          href="/area-cliente/chamados/novo"
          className="bg-white text-indigo-700 px-5 py-2.5 rounded-lg font-medium hover:bg-indigo-50 transition-colors whitespace-nowrap"
        >
          Abrir Chamado
        </Link>
      </div>
    </div>
  );
}
