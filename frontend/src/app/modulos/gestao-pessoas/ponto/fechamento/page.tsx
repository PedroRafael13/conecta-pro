'use client';

import { useState } from 'react';
import { Lock, Unlock, CheckCircle2, AlertTriangle, Calendar, Users, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface FechamentoMes {
  mes: string;
  periodo: string;
  status: 'aberto' | 'em_revisao' | 'fechado';
  colaboradores: number;
  pendencias: number;
  fechadoPor?: string;
  fechadoEm?: string;
}

const meses: FechamentoMes[] = [
  { mes: 'Marco 2026', periodo: '01/03 - 31/03', status: 'aberto', colaboradores: 44, pendencias: 5 },
  { mes: 'Fevereiro 2026', periodo: '01/02 - 28/02', status: 'fechado', colaboradores: 42, pendencias: 0, fechadoPor: 'Admin', fechadoEm: '05/03/2026' },
  { mes: 'Janeiro 2026', periodo: '01/01 - 31/01', status: 'fechado', colaboradores: 40, pendencias: 0, fechadoPor: 'Admin', fechadoEm: '05/02/2026' },
];

const statusConfig: Record<string, { label: string; classes: string; icon: typeof Lock }> = {
  aberto: { label: 'Aberto', classes: 'bg-green-100 text-green-800', icon: Unlock },
  em_revisao: { label: 'Em Revisao', classes: 'bg-yellow-100 text-yellow-800', icon: AlertTriangle },
  fechado: { label: 'Fechado', classes: 'bg-gray-100 text-gray-600', icon: Lock },
};

const pendencias = [
  { colaborador: 'Maria Oliveira', tipo: 'Atraso sem justificativa', data: '12/03/2026' },
  { colaborador: 'Pedro Costa', tipo: 'Batida faltante', data: '09/03/2026' },
  { colaborador: 'Ana Pereira', tipo: 'Falta injustificada', data: '08/03/2026' },
  { colaborador: 'Carlos Silva', tipo: 'Hora extra nao aprovada', data: '05/03/2026' },
  { colaborador: 'Roberto Lima', tipo: 'Divergencia de horario', data: '04/03/2026' },
];

export default function FechamentoPage() {
  const [confirmando, setConfirmando] = useState(false);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Lock className="w-6 h-6 text-gray-700" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Fechamento Mensal</h1>
            <p className="text-gray-500 mt-1">Controle de fechamento do ponto por competencia</p>
          </div>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          <Download className="h-4 w-4" />
          Relatorio Geral
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {meses.map((m) => {
          const config = statusConfig[m.status]!;
          const StatusIcon = config!.icon;
          return (
            <Card key={m.mes} className={`border ${m.status === 'aberto' ? 'border-blue-300 ring-1 ring-blue-100' : 'border-gray-200'}`}>
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">{m.mes}</h3>
                  <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${config!.classes}`}>
                    <StatusIcon className="h-3 w-3" />
                    {config!.label}
                  </span>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>Periodo</span>
                    <span className="font-medium text-gray-800">{m.periodo}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Colaboradores</span>
                    <span className="font-medium text-gray-800">{m.colaboradores}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Pendencias</span>
                    <span className={`font-medium ${m.pendencias > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {m.pendencias}
                    </span>
                  </div>
                  {m.fechadoPor && (
                    <div className="flex justify-between">
                      <span>Fechado por</span>
                      <span className="font-medium text-gray-800">{m.fechadoPor} em {m.fechadoEm}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border border-gray-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Pendencias — Marco 2026
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Colaborador</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Pendencia</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Data</th>
                </tr>
              </thead>
              <tbody>
                {pendencias.map((p, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{p.colaborador}</td>
                    <td className="py-3 px-4 text-gray-600">{p.tipo}</td>
                    <td className="py-3 px-4 text-gray-500">{p.data}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          Revisar Pendencias
        </button>
        <button
          onClick={() => setConfirmando(true)}
          className="px-6 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors flex items-center gap-2"
        >
          <Lock className="h-4 w-4" />
          Fechar Competencia
        </button>
      </div>

      {confirmando && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md border border-gray-200">
            <CardContent className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Confirmar Fechamento</h3>
              <p className="text-sm text-gray-600 mb-4">
                Tem certeza que deseja fechar a competencia Marco 2026? Existem 5 pendencias nao resolvidas. Apos o fechamento, nao sera possivel alterar batidas.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setConfirmando(false)}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => setConfirmando(false)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700"
                >
                  Confirmar Fechamento
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
