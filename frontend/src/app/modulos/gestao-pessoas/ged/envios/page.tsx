'use client';

import { useState, useEffect } from 'react';
import {
  Loader2,
  Mail,
  HardDrive,
  Globe,
  Printer,
  Send,
  Filter,
  CheckCircle,
  Clock,
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

interface Delivery {
  id: string;
  kit_id: string;
  kit_name: string;
  client_name: string;
  method: string;
  sent_at: string;
  received_at: string | null;
  confirmed: boolean;
}

const methodConfig: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  email: { label: 'Email', color: 'bg-blue-100 text-blue-800', icon: Mail },
  google_drive: { label: 'Google Drive', color: 'bg-green-100 text-green-800', icon: HardDrive },
  portal: { label: 'Portal', color: 'bg-purple-100 text-purple-800', icon: Globe },
  impresso: { label: 'Impresso', color: 'bg-gray-100 text-gray-800', icon: Printer },
};

const methodOptions = [
  { value: '', label: 'Todos os Metodos' },
  { value: 'email', label: 'Email' },
  { value: 'google_drive', label: 'Google Drive' },
  { value: 'portal', label: 'Portal' },
  { value: 'impresso', label: 'Impresso' },
];

export default function EnviosPage() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterMethod, setFilterMethod] = useState('');

  useEffect(() => {
    fetchDeliveries();
  }, [filterMethod]);

  async function fetchDeliveries() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterMethod) params.append('method', filterMethod);
      const res = await fetch(`${API_BASE}/deliveries?${params.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setDeliveries(Array.isArray(data) ? data : data.items || []);
      }
    } catch (err) {
    } finally {
      setLoading(false);
    }
  }

  function formatDateTime(dateStr: string | null) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('pt-BR');
  }

  const totalByMethod = deliveries.reduce(
    (acc, d) => {
      acc[d.method] = (acc[d.method] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Controle de Envios</h1>
        <p className="text-gray-500 mt-1">Acompanhe os envios de kits documentais</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {Object.entries(methodConfig).map(([key, config]) => {
          const Icon = config.icon;
          return (
            <Card
              key={key}
              className={`border border-gray-200 cursor-pointer hover:shadow-md transition-shadow ${
                filterMethod === key ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => setFilterMethod(filterMethod === key ? '' : key)}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${config.color.split(' ')[0]}`}>
                    <Icon className={`h-5 w-5 ${config.color.split(' ')[1]}`} />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">{config.label}</p>
                    <p className="text-xl font-bold">{totalByMethod[key] || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border border-gray-200">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold">Historico de Envios</CardTitle>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={filterMethod}
                onChange={(e) => setFilterMethod(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                {methodOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              <span className="ml-2 text-gray-500">Carregando envios...</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Kit</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Cliente</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Metodo</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Data Envio</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Confirmacao Recebimento</th>
                  </tr>
                </thead>
                <tbody>
                  {deliveries.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-gray-400">
                        <Send className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        Nenhum envio encontrado
                      </td>
                    </tr>
                  ) : (
                    deliveries.map((delivery) => {
                      const config = methodConfig[delivery.method] ?? methodConfig['email']!;
                      const MethodIcon = config!.icon;
                      return (
                        <tr key={delivery.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium">{delivery.kit_name}</td>
                          <td className="py-3 px-4 text-gray-600">{delivery.client_name}</td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex items-center gap-1.5 px-2 py-1 text-xs font-medium rounded-full ${config!.color}`}>
                              <MethodIcon className="h-3 w-3" />
                              {config!.label}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-600">{formatDateTime(delivery.sent_at)}</td>
                          <td className="py-3 px-4">
                            {delivery.confirmed ? (
                              <div className="flex items-center gap-1.5 text-green-600">
                                <CheckCircle className="h-4 w-4" />
                                <span className="text-xs">{formatDateTime(delivery.received_at)}</span>
                              </div>
                            ) : (
                              <div className="flex items-center gap-1.5 text-yellow-600">
                                <Clock className="h-4 w-4" />
                                <span className="text-xs">Aguardando</span>
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
