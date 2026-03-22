'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import { Hourglass, TrendingUp, TrendingDown, Search, Download, Minus, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Employee {
  id: number;
  name?: string;
  nome?: string;
  full_name?: string;
}

interface BancoHorasData {
  employee_id: number;
  employee_name?: string;
  saldo_horas?: number;
  saldo?: string;
  creditos?: string;
  debitos?: string;
  total_credito?: number;
  total_debito?: number;
  ultima_atualizacao?: string;
  registros?: BancoHorasEntry[];
  items?: BancoHorasEntry[];
}

interface BancoHorasEntry {
  id?: string | number;
  colaborador?: string;
  employee_name?: string;
  creditos?: string;
  debitos?: string;
  saldo?: string;
  saldo_minutos?: number;
  saldoMinutos?: number;
  ultima_atualizacao?: string;
}

export default function BancoHorasPage() {
  const [busca, setBusca] = useState('');
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);

  const { data: employees, isLoading: loadingEmployees } = useQuery<Employee[]>({
    queryKey: ['ponto', 'employees'],
    queryFn: async () => {
      const res = await customInstance({ url: '/api/v1/people-management/hr/employees/', params: { page_size: 100 } }) as unknown as { items?: Employee[] } | Employee[];
      return Array.isArray(res) ? res : res?.items ?? [];
    },
    staleTime: 60000,
    retry: 2,
  });

  const { data: bancoHoras, isLoading: loadingBanco, error: bancoError } = useQuery<BancoHorasData>({
    queryKey: ['ponto', 'banco-horas', selectedEmployeeId],
    queryFn: () => customInstance({
      url: `/api/v1/people-management/ponto/banco-horas/${selectedEmployeeId}`,
    }) as Promise<BancoHorasData>,
    enabled: !!selectedEmployeeId,
    staleTime: 30000,
    retry: 2,
  });

  const entries: BancoHorasEntry[] = bancoHoras?.registros ?? bancoHoras?.items ?? [];

  const filteredEntries = busca
    ? entries.filter((d) => {
        const nome = d.colaborador || d.employee_name || '';
        return nome.toLowerCase().includes(busca.toLowerCase());
      })
    : entries;

  function formatMinutes(mins: number | undefined): string {
    if (mins === undefined || mins === null) return '00:00';
    const sign = mins >= 0 ? '+' : '-';
    const abs = Math.abs(mins);
    const h = Math.floor(abs / 60);
    const m = abs % 60;
    return `${sign}${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
  }

  const resumo = [
    { label: 'Total Creditos', value: bancoHoras?.creditos ?? (bancoHoras?.total_credito ? `${bancoHoras.total_credito}h` : '--'), icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-50' },
    { label: 'Total Debitos', value: bancoHoras?.debitos ?? (bancoHoras?.total_debito ? `${bancoHoras.total_debito}h` : '--'), icon: TrendingDown, color: 'text-red-600', bg: 'bg-red-50' },
    { label: 'Saldo', value: bancoHoras?.saldo ?? (bancoHoras?.saldo_horas !== undefined ? formatMinutes(bancoHoras.saldo_horas) : '--'), icon: Hourglass, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Colaborador', value: bancoHoras?.employee_name ?? (selectedEmployeeId ? `#${selectedEmployeeId}` : '--'), icon: Minus, color: 'text-gray-600', bg: 'bg-gray-100' },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Hourglass className="w-6 h-6 text-green-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Banco de Horas</h1>
            <p className="text-gray-500 mt-1">Saldos acumulados</p>
          </div>
        </div>
        <button type="button" className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          <Download className="h-4 w-4" />
          Exportar
        </button>
      </div>

      {bancoError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          Erro ao carregar banco de horas: {(bancoError as Error).message}
        </div>
      )}

      <div className="flex items-center gap-4">
        <label className="text-sm text-gray-600">Colaborador:</label>
        {loadingEmployees ? (
          <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
        ) : (
          <select
            value={selectedEmployeeId ?? ''}
            onChange={(e) => setSelectedEmployeeId(e.target.value ? Number(e.target.value) : null)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Selecionar colaborador...</option>
            {(employees ?? []).map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.full_name || emp.nome || emp.name || `Funcionario #${emp.id}`}
              </option>
            ))}
          </select>
        )}
      </div>

      {selectedEmployeeId && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {resumo.map((r) => {
            const Icon = r.icon;
            return (
              <Card key={r.label} className="border border-gray-200">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">{r.label}</p>
                      {loadingBanco ? (
                        <Loader2 className="h-5 w-5 animate-spin text-gray-400 mt-2" />
                      ) : (
                        <p className="text-2xl font-bold mt-1">{r.value}</p>
                      )}
                    </div>
                    <div className={`p-3 rounded-lg ${r.bg}`}>
                      <Icon className={`h-5 w-5 ${r.color}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {!selectedEmployeeId && (
        <div className="text-center py-12 text-gray-400">
          Selecione um colaborador para visualizar o banco de horas.
        </div>
      )}

      {selectedEmployeeId && entries.length > 0 && (
        <>
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              placeholder="Buscar nos registros..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <Card className="border border-gray-200">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      <th className="text-left py-3 px-4 font-medium text-gray-500">Colaborador</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-500">Creditos</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-500">Debitos</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-500">Saldo</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-500">Ultima Atualizacao</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEntries.map((d, idx) => {
                      const saldoMins = d.saldo_minutos ?? d.saldoMinutos ?? 0;
                      return (
                        <tr key={d.id ?? idx} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium text-gray-900">{d.colaborador || d.employee_name || '--'}</td>
                          <td className="py-3 px-4 text-center font-mono text-green-600">{d.creditos || '--'}</td>
                          <td className="py-3 px-4 text-center font-mono text-red-600">{d.debitos || '--'}</td>
                          <td className="py-3 px-4 text-center">
                            <span className={`inline-flex px-2 py-1 text-xs font-bold rounded-full font-mono ${
                              saldoMins > 0 ? 'bg-green-100 text-green-800' :
                              saldoMins < 0 ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {d.saldo || formatMinutes(saldoMins)}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-500">{d.ultima_atualizacao || '--'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {selectedEmployeeId && !loadingBanco && entries.length === 0 && !bancoError && (
        <div className="text-center py-8 text-gray-400">
          Nenhum registro de banco de horas encontrado para este colaborador.
        </div>
      )}
    </div>
  );
}
