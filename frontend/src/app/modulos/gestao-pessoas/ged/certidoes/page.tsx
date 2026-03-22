'use client';

import { useState, useEffect } from 'react';
import {
  Loader2,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ShieldCheck,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/ged';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface CND {
  id: string;
  type: string;
  company_name: string;
  company_id: string;
  expiration_date: string;
  status: 'valida' | 'vencendo' | 'vencida';
  last_sync: string;
  document_url?: string;
}

interface CndSummary {
  validas: number;
  vencendo_30_dias: number;
  vencidas: number;
}

const typeLabels: Record<string, string> = {
  cnd_federal: 'CND Federal',
  cnd_estadual: 'CND Estadual',
  cnd_municipal: 'CND Municipal',
  cnd_trabalhista: 'CND Trabalhista (CNDT)',
  cnd_fgts: 'CRF/FGTS',
  cnd_previdenciaria: 'CND Previdenciaria',
};

const statusConfig: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  valida: { label: 'Valida', color: 'bg-green-100 text-green-800', icon: CheckCircle },
  vencendo: { label: 'Vencendo', color: 'bg-yellow-100 text-yellow-800', icon: AlertTriangle },
  vencida: { label: 'Vencida', color: 'bg-red-100 text-red-800', icon: XCircle },
};

export default function CertidoesPage() {
  const [cnds, setCnds] = useState<CND[]>([]);
  const [summary, setSummary] = useState<CndSummary>({ validas: 0, vencendo_30_dias: 0, vencidas: 0 });
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    setLoading(true);
    try {
      const [cndsRes, summaryRes] = await Promise.all([
        fetch(`${API_BASE}/certidoes`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/certidoes/summary`, { headers: getAuthHeaders() }),
      ]);
      if (cndsRes.ok) {
        const data = await cndsRes.json();
        setCnds(Array.isArray(data) ? data : data.items || []);
      }
      if (summaryRes.ok) {
        setSummary(await summaryRes.json());
      }
    } catch (err) {
    } finally {
      setLoading(false);
    }
  }

  async function handleSync() {
    setSyncing(true);
    try {
      const res = await fetch(`${API_BASE}/certidoes/sync`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        await fetchData();
      }
    } catch (err) {
    } finally {
      setSyncing(false);
    }
  }

  function formatDate(dateStr: string) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  }

  function formatDateTime(dateStr: string) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('pt-BR');
  }

  const statCards = [
    {
      label: 'Validas',
      value: summary.validas,
      icon: CheckCircle,
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-200',
    },
    {
      label: 'Vencendo em 30 dias',
      value: summary.vencendo_30_dias,
      icon: AlertTriangle,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
    },
    {
      label: 'Vencidas',
      value: summary.vencidas,
      icon: XCircle,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">Carregando certidoes...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Certidoes Negativas (CND)</h1>
          <p className="text-gray-500 mt-1">Acompanhamento de validade e sincronizacao automatica</p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
          {syncing ? 'Sincronizando...' : 'Sincronizar CNDs'}
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className={`border ${stat.border}`}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.label}</p>
                    <p className="text-3xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border border-gray-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold">Todas as Certidoes</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Tipo</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Empresa</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Validade</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Ultimo Sync</th>
                </tr>
              </thead>
              <tbody>
                {cnds.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-gray-400">
                      <ShieldCheck className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      Nenhuma certidao cadastrada
                    </td>
                  </tr>
                ) : (
                  cnds.map((cnd) => {
                    const config = statusConfig[cnd.status] ?? statusConfig['valida']!;
                    const StatusIcon = config!.icon;
                    return (
                      <tr key={cnd.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">{typeLabels[cnd.type] || cnd.type}</td>
                        <td className="py-3 px-4 text-gray-600">{cnd.company_name}</td>
                        <td className="py-3 px-4 text-gray-600">{formatDate(cnd.expiration_date)}</td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${config!.color}`}>
                            <StatusIcon className="h-3 w-3" />
                            {config!.label}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-500 text-xs">{formatDateTime(cnd.last_sync)}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
