'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Loader2,
  Eye,
  Send,
  CheckCircle,
  Filter,
  FolderOpen,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/ged';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Kit {
  id: string;
  client_name: string;
  client_id: string;
  reference_month: string;
  status: string;
  total_documents: number;
  signed_documents: number;
  completion_percentage: number;
}

interface Client {
  id: string;
  name: string;
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

const statusOptions = [
  { value: '', label: 'Todos os Status' },
  { value: 'em_montagem', label: 'Em Montagem' },
  { value: 'completo', label: 'Completo' },
  { value: 'enviado', label: 'Enviado' },
  { value: 'conferido', label: 'Conferido' },
  { value: 'aprovado', label: 'Aprovado' },
];

export default function KitsListPage() {
  const router = useRouter();
  const [kits, setKits] = useState<Kit[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterMonth, setFilterMonth] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterClient, setFilterClient] = useState('');

  useEffect(() => {
    fetchClients();
  }, []);

  useEffect(() => {
    fetchKits();
  }, [filterMonth, filterStatus, filterClient]);

  async function fetchClients() {
    try {
      const res = await fetch(`${API_BASE}/clients`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setClients(Array.isArray(data) ? data : data.items || []);
      }
    } catch {
      // silenced
    }
  }

  async function fetchKits() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterMonth) params.append('reference_month', filterMonth);
      if (filterStatus) params.append('status', filterStatus);
      if (filterClient) params.append('client_id', filterClient);
      const res = await fetch(`${API_BASE}/kits/?${params.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setKits(Array.isArray(data) ? data : data.items || []);
      }
    } catch {
      // silenced
    } finally {
      setLoading(false);
    }
  }

  async function handleSend(kitId: string) {
    if (!confirm('Confirma o envio deste kit ao cliente?')) return;
    try {
      await fetch(`${API_BASE}/kits/${kitId}/send`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      fetchKits();
    } catch {
      // silenced
    }
  }

  async function handleApprove(kitId: string) {
    if (!confirm('Confirma a aprovação deste kit?')) return;
    try {
      await fetch(`${API_BASE}/kits/${kitId}/approve`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      fetchKits();
    } catch {
      // silenced
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Kits Documentais</h1>
        <p className="text-gray-500 mt-1">Listagem e gerenciamento de kits</p>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <Filter className="h-4 w-4 text-gray-400" />
            <div>
              <label className="block text-xs text-gray-500 mb-1">Mes Referencia</label>
              <input
                type="month"
                value={filterMonth}
                onChange={(e) => setFilterMonth(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                {statusOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Cliente</label>
              <select
                value={filterClient}
                onChange={(e) => setFilterClient(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">Todos os Clientes</option>
                {clients.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Carregando kits...</span>
        </div>
      ) : (
        <Card className="border border-gray-200">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Cliente</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Mes</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Docs Total</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Assinados</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Conclusao</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Acoes</th>
                  </tr>
                </thead>
                <tbody>
                  {kits.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-gray-400">
                        <FolderOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        Nenhum kit encontrado com os filtros selecionados
                      </td>
                    </tr>
                  ) : (
                    kits.map((kit) => (
                      <tr key={kit.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">{kit.client_name}</td>
                        <td className="py-3 px-4 text-gray-600">{kit.reference_month}</td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusColors[kit.status] || 'bg-gray-100 text-gray-800'}`}>
                            {statusLabels[kit.status] || kit.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-600">{kit.total_documents}</td>
                        <td className="py-3 px-4 text-gray-600">{kit.signed_documents}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full transition-all"
                                style={{ width: `${kit.completion_percentage}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-500">{kit.completion_percentage}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => router.push(`/modulos/gestao-pessoas/ged/kits/${kit.id}`)}
                              className="p-1.5 rounded hover:bg-gray-100"
                              title="Visualizar"
                            >
                              <Eye className="h-4 w-4 text-gray-500" />
                            </button>
                            <button
                              onClick={() => handleSend(kit.id)}
                              className="p-1.5 rounded hover:bg-blue-50"
                              title="Enviar"
                              disabled={kit.status === 'enviado' || kit.status === 'aprovado'}
                            >
                              <Send className="h-4 w-4 text-blue-500" />
                            </button>
                            <button
                              onClick={() => handleApprove(kit.id)}
                              className="p-1.5 rounded hover:bg-green-50"
                              title="Aprovar"
                              disabled={kit.status === 'aprovado'}
                            >
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
