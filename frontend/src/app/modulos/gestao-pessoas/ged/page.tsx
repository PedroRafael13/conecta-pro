'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  FolderOpen,
  Clock,
  Send,
  BarChart3,
  Loader2,
  Plus,
  Wand2,
  Eye,
  ChevronRight,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/ged';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Summary {
  total_kits: number;
  kits_pendentes: number;
  kits_enviados: number;
  taxa_conclusao: number;
}

interface Kit {
  id: string;
  client_name: string;
  reference_month: string;
  status: string;
  completion_percentage: number;
}

const statusColors: Record<string, string> = {
  em_montagem: 'bg-yellow-100 text-yellow-800',
  completo: 'bg-blue-100 text-blue-800',
  enviado: 'bg-green-100 text-green-800',
  conferido: 'bg-purple-100 text-purple-800',
  aprovado: 'bg-emerald-100 text-emerald-800',
};

const statusLabels: Record<string, string> = {
  em_montagem: 'Em Montagem',
  completo: 'Completo',
  enviado: 'Enviado',
  conferido: 'Conferido',
  aprovado: 'Aprovado',
};

export default function GEDDashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<Summary>({
    total_kits: 0,
    kits_pendentes: 0,
    kits_enviados: 0,
    taxa_conclusao: 0,
  });
  const [recentKits, setRecentKits] = useState<Kit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    setLoading(true);
    try {
      const [sumRes, kitsRes] = await Promise.all([
        fetch(`${API_BASE}/kits/summary`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/kits?limit=10`, { headers: getAuthHeaders() }),
      ]);
      if (sumRes.ok) {
        const data = await sumRes.json();
        setSummary(data);
      }
      if (kitsRes.ok) {
        const data = await kitsRes.json();
        setRecentKits(Array.isArray(data) ? data : data.items || []);
      }
    } catch (err) {
      console.error('Erro ao carregar dados do GED:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleAutoAssemble() {
    try {
      const res = await fetch(`${API_BASE}/kits/auto-assemble`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error('Erro ao montar kits automaticamente:', err);
    }
  }

  const statCards = [
    { label: 'Total Kits', value: summary.total_kits, icon: FolderOpen, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Kits Pendentes', value: summary.kits_pendentes, icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-50' },
    { label: 'Kits Enviados', value: summary.kits_enviados, icon: Send, color: 'text-green-600', bg: 'bg-green-50' },
    { label: 'Taxa Conclusao', value: `${summary.taxa_conclusao}%`, icon: BarChart3, color: 'text-purple-600', bg: 'bg-purple-50' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">Carregando...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">GED - Gestao Eletronica de Documentos</h1>
          <p className="text-gray-500 mt-1">Kits documentais, certidoes e envios</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleAutoAssemble}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            <Wand2 className="h-4 w-4" />
            Montar Kits Automatico
          </button>
          <button
            onClick={() => router.push('/modulos/gestao-pessoas/ged/kits?new=true')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Novo Kit
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="border border-gray-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-semibold">Kits Recentes</CardTitle>
          <button
            onClick={() => router.push('/modulos/gestao-pessoas/ged/kits')}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            Ver todos <ChevronRight className="h-4 w-4" />
          </button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Cliente</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Mes Ref</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Conclusao</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Acoes</th>
                </tr>
              </thead>
              <tbody>
                {recentKits.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-400">
                      Nenhum kit encontrado
                    </td>
                  </tr>
                ) : (
                  recentKits.map((kit) => (
                    <tr key={kit.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{kit.client_name}</td>
                      <td className="py-3 px-4 text-gray-600">{kit.reference_month}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusColors[kit.status] || 'bg-gray-100 text-gray-800'}`}>
                          {statusLabels[kit.status] || kit.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${kit.completion_percentage}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-500">{kit.completion_percentage}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => router.push(`/modulos/gestao-pessoas/ged/kits/${kit.id}`)}
                          className="p-1 rounded hover:bg-gray-100"
                          title="Visualizar"
                        >
                          <Eye className="h-4 w-4 text-gray-500" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
