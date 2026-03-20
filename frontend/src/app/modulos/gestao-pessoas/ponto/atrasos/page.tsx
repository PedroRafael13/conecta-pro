'use client';

import { useState } from 'react';
import { CalendarX, Search, Download, AlertTriangle, Clock, XCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Ocorrencia {
  id: string;
  colaborador: string;
  data: string;
  tipo: 'atraso' | 'falta_justificada' | 'falta_injustificada' | 'saida_antecipada';
  tempo: string;
  justificado: boolean;
}

const ocorrencias: Ocorrencia[] = [
  { id: '1', colaborador: 'Maria Oliveira', data: '12/03/2026', tipo: 'atraso', tempo: '22 min', justificado: false },
  { id: '2', colaborador: 'Carlos Silva', data: '10/03/2026', tipo: 'falta_justificada', tempo: '1 dia', justificado: true },
  { id: '3', colaborador: 'Pedro Costa', data: '09/03/2026', tipo: 'atraso', tempo: '10 min', justificado: false },
  { id: '4', colaborador: 'Ana Pereira', data: '08/03/2026', tipo: 'falta_injustificada', tempo: '1 dia', justificado: false },
  { id: '5', colaborador: 'Joao Santos', data: '07/03/2026', tipo: 'saida_antecipada', tempo: '45 min', justificado: true },
  { id: '6', colaborador: 'Lucia Ferreira', data: '05/03/2026', tipo: 'atraso', tempo: '5 min', justificado: false },
  { id: '7', colaborador: 'Roberto Lima', data: '04/03/2026', tipo: 'falta_justificada', tempo: '2 dias', justificado: true },
  { id: '8', colaborador: 'Maria Oliveira', data: '03/03/2026', tipo: 'atraso', tempo: '15 min', justificado: true },
];

const tipoConfig: Record<string, { label: string; classes: string; icon: typeof Clock }> = {
  atraso: { label: 'Atraso', classes: 'bg-amber-100 text-amber-800', icon: Clock },
  falta_justificada: { label: 'Falta Justificada', classes: 'bg-blue-100 text-blue-800', icon: CalendarX },
  falta_injustificada: { label: 'Falta Injustificada', classes: 'bg-red-100 text-red-800', icon: XCircle },
  saida_antecipada: { label: 'Saida Antecipada', classes: 'bg-purple-100 text-purple-800', icon: AlertTriangle },
};

const resumo = [
  { label: 'Atrasos', valor: 4, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
  { label: 'Faltas Justificadas', valor: 2, icon: CalendarX, color: 'text-blue-600', bg: 'bg-blue-50' },
  { label: 'Faltas Injustificadas', valor: 1, icon: XCircle, color: 'text-red-600', bg: 'bg-red-50' },
  { label: 'Saidas Antecipadas', valor: 1, icon: AlertTriangle, color: 'text-purple-600', bg: 'bg-purple-50' },
];

export default function AtrasosPage() {
  const [filtroTipo, setFiltroTipo] = useState('todos');

  const filtered = filtroTipo === 'todos' ? ocorrencias : ocorrencias.filter((o) => o.tipo === filtroTipo);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CalendarX className="w-6 h-6 text-red-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Atrasos e Faltas</h1>
            <p className="text-gray-500 mt-1">Marco 2026</p>
          </div>
        </div>
        <button type="button" className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
          <Download className="h-4 w-4" />
          Exportar
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {resumo.map((r) => {
          const Icon = r.icon;
          return (
            <Card key={r.label} className="border border-gray-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{r.label}</p>
                    <p className="text-2xl font-bold mt-1">{r.valor}</p>
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

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar colaborador..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <select
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="todos">Todos os tipos</option>
          <option value="atraso">Atrasos</option>
          <option value="falta_justificada">Faltas Justificadas</option>
          <option value="falta_injustificada">Faltas Injustificadas</option>
          <option value="saida_antecipada">Saidas Antecipadas</option>
        </select>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Colaborador</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Data</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Tipo</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Tempo</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Justificado</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((o) => (
                  <tr key={o.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{o.colaborador}</td>
                    <td className="py-3 px-4 text-gray-600">{o.data}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${tipoConfig[o.tipo]?.classes}`}>
                        {tipoConfig[o.tipo]?.label}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-gray-700">{o.tempo}</td>
                    <td className="py-3 px-4">
                      {o.justificado ? (
                        <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-800">Sim</span>
                      ) : (
                        <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-500">Nao</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
