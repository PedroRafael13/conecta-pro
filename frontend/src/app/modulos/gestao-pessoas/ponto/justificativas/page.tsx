'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import { FileCheck, Plus, Search, Filter, Loader2, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Justificativa {
  id?: string | number;
  colaborador?: string;
  employee_name?: string;
  data?: string;
  date?: string;
  tipo?: string;
  type?: string;
  motivo?: string;
  reason?: string;
  status?: 'pendente' | 'aprovada' | 'rejeitada' | string;
  anexo?: boolean;
  has_attachment?: boolean;
}

interface JustificativaPayload {
  employee_id: number;
  data: string;
  tipo: string;
  motivo: string;
}

const statusConfig: Record<string, { label: string; classes: string }> = {
  pendente: { label: 'Pendente', classes: 'bg-yellow-100 text-yellow-800' },
  aprovada: { label: 'Aprovada', classes: 'bg-green-100 text-green-800' },
  rejeitada: { label: 'Rejeitada', classes: 'bg-red-100 text-red-800' },
};

export default function JustificativasPage() {
  const queryClient = useQueryClient();
  const [filtro, setFiltro] = useState('todos');
  const [busca, setBusca] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ employee_id: '', data: '', tipo: 'Falta', motivo: '' });

  const { data: rawData, isLoading, error } = useQuery<Justificativa[]>({
    queryKey: ['ponto', 'justificativas', 'pendentes'],
    queryFn: async () => {
      const res = await customInstance({ url: '/api/v1/people-management/ponto/justificativas/pendentes' }) as unknown;
      if (Array.isArray(res)) return res as Justificativa[];
      const obj = res as Record<string, unknown>;
      return (obj?.items ?? obj?.justificativas ?? []) as Justificativa[];
    },
    staleTime: 30000,
    retry: 2,
  });

  const justificativas: Justificativa[] = rawData ?? [];

  const createMutation = useMutation({
    mutationFn: (body: JustificativaPayload) => customInstance({
      url: '/api/v1/people-management/ponto/justificativa',
      method: 'POST',
      data: body,
    }),
    onSuccess: () => {
      setShowForm(false);
      setFormData({ employee_id: '', data: '', tipo: 'Falta', motivo: '' });
      queryClient.invalidateQueries({ queryKey: ['ponto', 'justificativas'] });
    },
  });

  const filtered = justificativas.filter((j) => {
    const status = j.status || 'pendente';
    const nome = j.colaborador || j.employee_name || '';
    const matchFiltro = filtro === 'todos' || status === filtro;
    const matchBusca = !busca || nome.toLowerCase().includes(busca.toLowerCase());
    return matchFiltro && matchBusca;
  });

  function handleSubmitJustificativa(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.employee_id || !formData.data || !formData.motivo) return;
    createMutation.mutate({
      employee_id: Number(formData.employee_id),
      data: formData.data,
      tipo: formData.tipo,
      motivo: formData.motivo,
    });
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileCheck className="w-6 h-6 text-amber-600" />
          <h1 className="text-2xl font-bold text-gray-900">Justificativas</h1>
        </div>
        <button
          type="button"
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Nova Justificativa
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          Erro ao carregar justificativas: {(error as Error).message}
        </div>
      )}

      {createMutation.isSuccess && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
          Justificativa criada com sucesso!
        </div>
      )}

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar por colaborador..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex gap-2">
          {['todos', 'pendente', 'aprovada', 'rejeitada'].map((f) => (
            <button
              key={f}
              onClick={() => setFiltro(f)}
              className={`px-3 py-1.5 text-xs font-medium rounded-full transition-colors ${
                filtro === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {f === 'todos' ? 'Todos' : statusConfig[f]?.label}
            </button>
          ))}
        </div>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Colaborador</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Data</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Tipo</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Motivo</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Anexo</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-400">
                        Nenhuma justificativa encontrada
                      </td>
                    </tr>
                  ) : (
                    filtered.map((j, idx) => {
                      const status = j.status || 'pendente';
                      const hasAttachment = j.anexo ?? j.has_attachment ?? false;
                      return (
                        <tr key={j.id ?? idx} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer">
                          <td className="py-3 px-4 font-medium text-gray-900">{j.colaborador || j.employee_name || '--'}</td>
                          <td className="py-3 px-4 text-gray-600">{j.data || j.date || '--'}</td>
                          <td className="py-3 px-4">
                            <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-700">
                              {j.tipo || j.type || '--'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-600 max-w-xs truncate">{j.motivo || j.reason || '--'}</td>
                          <td className="py-3 px-4">
                            {hasAttachment ? (
                              <span className="text-blue-600 text-xs font-medium">Sim</span>
                            ) : (
                              <span className="text-gray-400 text-xs">Nao</span>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusConfig[status]?.classes ?? 'bg-gray-100 text-gray-600'}`}>
                              {statusConfig[status]?.label ?? status}
                            </span>
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

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md border border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">Nova Justificativa</h3>
                <button onClick={() => setShowForm(false)} className="p-1 hover:bg-gray-100 rounded">
                  <X className="h-5 w-5 text-gray-500" />
                </button>
              </div>
              {createMutation.isError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm mb-4">
                  {(createMutation.error as Error).message}
                </div>
              )}
              <form onSubmit={handleSubmitJustificativa} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ID do Colaborador</label>
                  <input
                    type="number"
                    value={formData.employee_id}
                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
                  <input
                    type="date"
                    value={formData.data}
                    onChange={(e) => setFormData({ ...formData, data: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                  <select
                    value={formData.tipo}
                    onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Falta">Falta</option>
                    <option value="Atraso">Atraso</option>
                    <option value="Saida Antecipada">Saida Antecipada</option>
                    <option value="Esquecimento">Esquecimento</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
                  <textarea
                    value={formData.motivo}
                    onChange={(e) => setFormData({ ...formData, motivo: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="flex justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    disabled={createMutation.isPending}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={createMutation.isPending}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center gap-2"
                  >
                    {createMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                    Salvar
                  </button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
