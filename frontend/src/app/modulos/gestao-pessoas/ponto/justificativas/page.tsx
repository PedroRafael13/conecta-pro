'use client';

import { useState } from 'react';
import { FileCheck, Plus, Search, Filter } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Justificativa {
  id: string;
  colaborador: string;
  data: string;
  tipo: string;
  motivo: string;
  status: 'pendente' | 'aprovada' | 'rejeitada';
  anexo: boolean;
}

const justificativas: Justificativa[] = [
  { id: '1', colaborador: 'Carlos Silva', data: '10/03/2026', tipo: 'Falta', motivo: 'Consulta medica', status: 'aprovada', anexo: true },
  { id: '2', colaborador: 'Maria Oliveira', data: '08/03/2026', tipo: 'Atraso', motivo: 'Problema no transporte', status: 'pendente', anexo: false },
  { id: '3', colaborador: 'Joao Santos', data: '07/03/2026', tipo: 'Saida Antecipada', motivo: 'Reuniao escolar do filho', status: 'aprovada', anexo: true },
  { id: '4', colaborador: 'Ana Pereira', data: '05/03/2026', tipo: 'Falta', motivo: 'Motivo pessoal', status: 'rejeitada', anexo: false },
  { id: '5', colaborador: 'Pedro Costa', data: '04/03/2026', tipo: 'Esquecimento', motivo: 'Esqueceu de bater ponto na saida', status: 'pendente', anexo: false },
  { id: '6', colaborador: 'Lucia Ferreira', data: '03/03/2026', tipo: 'Falta', motivo: 'Atestado medico - 2 dias', status: 'aprovada', anexo: true },
];

const statusConfig: Record<string, { label: string; classes: string }> = {
  pendente: { label: 'Pendente', classes: 'bg-yellow-100 text-yellow-800' },
  aprovada: { label: 'Aprovada', classes: 'bg-green-100 text-green-800' },
  rejeitada: { label: 'Rejeitada', classes: 'bg-red-100 text-red-800' },
};

export default function JustificativasPage() {
  const [filtro, setFiltro] = useState('todos');

  const filtered = filtro === 'todos' ? justificativas : justificativas.filter((j) => j.status === filtro);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileCheck className="w-6 h-6 text-amber-600" />
          <h1 className="text-2xl font-bold text-gray-900">Justificativas</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          <Plus className="h-4 w-4" />
          Nova Justificativa
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
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
                  filtered.map((j) => (
                    <tr key={j.id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer">
                      <td className="py-3 px-4 font-medium text-gray-900">{j.colaborador}</td>
                      <td className="py-3 px-4 text-gray-600">{j.data}</td>
                      <td className="py-3 px-4">
                        <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-700">
                          {j.tipo}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600 max-w-xs truncate">{j.motivo}</td>
                      <td className="py-3 px-4">
                        {j.anexo ? (
                          <span className="text-blue-600 text-xs font-medium">Sim</span>
                        ) : (
                          <span className="text-gray-400 text-xs">Nao</span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusConfig[j.status]?.classes}`}>
                          {statusConfig[j.status]?.label}
                        </span>
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
