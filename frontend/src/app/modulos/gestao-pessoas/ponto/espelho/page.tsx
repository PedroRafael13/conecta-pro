'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import { FileText, Download, ChevronLeft, ChevronRight, Printer, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Employee {
  id: number;
  name?: string;
  nome?: string;
  full_name?: string;
}

interface EspelhoDay {
  dia: string;
  dia_semana?: string;
  diaSemana?: string;
  entrada1?: string;
  saida1?: string;
  entrada2?: string;
  saida2?: string;
  total?: string;
  obs?: string;
  observacao?: string;
}

interface EspelhoData {
  employee_id: number;
  employee_name?: string;
  competencia?: string;
  jornada?: string;
  total_trabalhado?: string;
  horas_esperadas?: string;
  saldo?: string;
  dias?: EspelhoDay[];
  registros?: EspelhoDay[];
}

export default function EspelhoPontoPage() {
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());

  const monthNames = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
  const mesAtual = `${monthNames[month - 1]} ${year}`;

  const { data: employees, isLoading: loadingEmployees } = useQuery<Employee[]>({
    queryKey: ['ponto', 'employees'],
    queryFn: async () => {
      const res = await customInstance({ url: '/api/v1/people-management/hr/employees', params: { page_size: 100 } }) as unknown as { items?: Employee[] } | Employee[];
      return Array.isArray(res) ? res : res?.items ?? [];
    },
    staleTime: 60000,
    retry: 2,
  });

  const { data: espelho, isLoading: loadingEspelho, error: espelhoError } = useQuery<EspelhoData>({
    queryKey: ['ponto', 'espelho', selectedEmployeeId, month, year],
    queryFn: () => customInstance({
      url: `/api/v1/people-management/ponto/espelho/${selectedEmployeeId}`,
      params: { mes: month, ano: year },
    }) as Promise<EspelhoData>,
    enabled: !!selectedEmployeeId,
    staleTime: 30000,
    retry: 2,
  });

  const dias: EspelhoDay[] = espelho?.dias ?? espelho?.registros ?? [];

  function handlePrevMonth() {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else { setMonth(month - 1); }
  }

  function handleNextMonth() {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else { setMonth(month + 1); }
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="w-6 h-6 text-indigo-600" />
          <h1 className="text-2xl font-bold text-gray-900">Espelho de Ponto</h1>
        </div>
        <div className="flex gap-2">
          <button type="button" className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
            <Printer className="h-4 w-4" />
            Imprimir
          </button>
          <button type="button" className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
            <Download className="h-4 w-4" />
            Exportar PDF
          </button>
        </div>
      </div>

      {espelhoError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          Erro ao carregar espelho: {(espelhoError as Error).message}
        </div>
      )}

      <Card className="border border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-semibold">Competencia</CardTitle>
          <div className="flex items-center gap-4">
            <button type="button" className="p-1 hover:bg-gray-100 rounded" onClick={handlePrevMonth}>
              <ChevronLeft className="h-5 w-5 text-gray-600" />
            </button>
            <span className="text-sm font-medium text-gray-700 min-w-[120px] text-center">{mesAtual}</span>
            <button type="button" className="p-1 hover:bg-gray-100 rounded" onClick={handleNextMonth}>
              <ChevronRight className="h-5 w-5 text-gray-600" />
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4 text-sm text-gray-600 items-center">
            <span>Colaborador:</span>
            {loadingEmployees ? (
              <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
            ) : (
              <select
                value={selectedEmployeeId ?? ''}
                onChange={(e) => setSelectedEmployeeId(e.target.value ? Number(e.target.value) : null)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Selecionar...</option>
                {(employees ?? []).map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.full_name || emp.nome || emp.name || `Funcionario #${emp.id}`}
                  </option>
                ))}
              </select>
            )}
            {espelho?.jornada && (
              <span>Jornada: <strong className="text-gray-900">{espelho.jornada}</strong></span>
            )}
          </div>

          {loadingEspelho && selectedEmployeeId && (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          )}

          {!selectedEmployeeId && !loadingEspelho && (
            <div className="text-center py-12 text-gray-400">
              Selecione um colaborador para visualizar o espelho de ponto.
            </div>
          )}

          {dias.length > 0 && (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      <th className="text-left py-3 px-3 font-medium text-gray-500">Dia</th>
                      <th className="text-left py-3 px-3 font-medium text-gray-500">Sem</th>
                      <th className="text-center py-3 px-3 font-medium text-gray-500">Entrada</th>
                      <th className="text-center py-3 px-3 font-medium text-gray-500">Saida</th>
                      <th className="text-center py-3 px-3 font-medium text-gray-500">Entrada</th>
                      <th className="text-center py-3 px-3 font-medium text-gray-500">Saida</th>
                      <th className="text-center py-3 px-3 font-medium text-gray-500">Total</th>
                      <th className="text-left py-3 px-3 font-medium text-gray-500">Obs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dias.map((row, idx) => {
                      const sem = row.dia_semana || row.diaSemana || '';
                      const obs = row.obs || row.observacao || '';
                      return (
                        <tr
                          key={idx}
                          className={`border-b border-gray-100 hover:bg-gray-50 ${
                            sem === 'Sab' || sem === 'Dom' || sem === 'Sabado' || sem === 'Domingo' ? 'bg-gray-50/50' : ''
                          }`}
                        >
                          <td className="py-2.5 px-3 font-medium">{row.dia}</td>
                          <td className="py-2.5 px-3 text-gray-600">{sem}</td>
                          <td className="py-2.5 px-3 text-center font-mono">{row.entrada1 || '--:--'}</td>
                          <td className="py-2.5 px-3 text-center font-mono">{row.saida1 || '--:--'}</td>
                          <td className="py-2.5 px-3 text-center font-mono">{row.entrada2 || '--:--'}</td>
                          <td className="py-2.5 px-3 text-center font-mono">{row.saida2 || '--:--'}</td>
                          <td className="py-2.5 px-3 text-center font-mono font-medium">{row.total || '00:00'}</td>
                          <td className="py-2.5 px-3">
                            {obs && (
                              <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${
                                obs.toLowerCase().includes('atraso') ? 'bg-amber-100 text-amber-800' :
                                obs.toLowerCase().includes('he') || obs.toLowerCase().includes('extra') ? 'bg-blue-100 text-blue-800' :
                                obs.toLowerCase().includes('falta') ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-600'
                              }`}>
                                {obs}
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <div className="mt-4 flex justify-between items-center text-sm text-gray-500 border-t border-gray-200 pt-4">
                <span>Total Trabalhado: <strong className="text-gray-900">{espelho?.total_trabalhado || '--'}</strong></span>
                <span>Horas Esperadas: <strong className="text-gray-900">{espelho?.horas_esperadas || '--'}</strong></span>
                <span>Saldo: <strong className={espelho?.saldo?.startsWith('-') ? 'text-red-600' : 'text-green-600'}>{espelho?.saldo || '--'}</strong></span>
              </div>
            </>
          )}

          {selectedEmployeeId && !loadingEspelho && dias.length === 0 && !espelhoError && (
            <div className="text-center py-12 text-gray-400">
              Nenhum registro encontrado para este periodo.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
