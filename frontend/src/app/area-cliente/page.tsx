'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { FolderOpen, Clock, MessageSquare, HelpCircle, ArrowRight, Loader2 } from 'lucide-react';
import { usePortalAuth } from './hooks/usePortalAuth';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || '') + '/api/v1/portal';

function getPortalHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface DashboardStats {
  kits_disponiveis: number;
  kits_pendentes: number;
  chamados_abertos: number;
}

interface RecentKit {
  id: number;
  mes_referencia: string;
  status: string;
  percentual_conclusao: number;
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

export default function DashboardPage() {
  const { clientName } = usePortalAuth();
  const [stats, setStats] = useState<DashboardStats>({ kits_disponiveis: 0, kits_pendentes: 0, chamados_abertos: 0 });
  const [recentKits, setRecentKits] = useState<RecentKit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, kitsRes] = await Promise.all([
          fetch(`${API_BASE}/dashboard/stats`, { headers: getPortalHeaders() }),
          fetch(`${API_BASE}/kits?limit=5`, { headers: getPortalHeaders() }),
        ]);
        if (statsRes.ok) {
          const s = await statsRes.json();
          setStats(s);
        }
        if (kitsRes.ok) {
          const k = await kitsRes.json();
          setRecentKits(Array.isArray(k) ? k : k.items || []);
        }
      } catch {
        // silently handle
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const statCards = [
    {
      label: 'Kits Disponíveis',
      value: stats.kits_disponiveis,
      icon: FolderOpen,
      color: 'bg-indigo-50 text-indigo-600',
      iconBg: 'bg-indigo-100',
    },
    {
      label: 'Kits Pendentes',
      value: stats.kits_pendentes,
      icon: Clock,
      color: 'bg-yellow-50 text-yellow-600',
      iconBg: 'bg-yellow-100',
    },
    {
      label: 'Chamados Abertos',
      value: stats.chamados_abertos,
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
    <div className="space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Bem-vindo, {clientName || 'Cliente'}!
        </h1>
        <p className="text-gray-500 mt-1">Acompanhe seus kits documentais e chamados.</p>
      </div>

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
          {recentKits.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-400 text-sm">
              Nenhum kit disponível no momento.
            </div>
          ) : (
            recentKits.map((kit) => (
              <div key={kit.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-sm font-medium text-gray-900">{kit.mes_referencia}</div>
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
                      style={{ width: `${kit.percentual_conclusao}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 w-10 text-right">
                    {kit.percentual_conclusao}%
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

      {/* Quick Action */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-xl p-6 text-white flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="bg-white/20 p-3 rounded-lg">
            <HelpCircle className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Precisa de ajuda?</h3>
            <p className="text-indigo-100 text-sm">
              Abra um chamado e nossa equipe responderá rapidamente.
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
