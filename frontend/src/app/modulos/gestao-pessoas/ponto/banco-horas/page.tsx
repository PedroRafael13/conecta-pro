'use client';

import { useState } from 'react';
import { Hourglass, TrendingUp, TrendingDown, Search, Download, Minus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface BancoHorasItem {
  id: string;
  colaborador: string;
  creditos: string;
  debitos: string;
  saldo: string;
  saldoMinutos: number;
  ultimaAtualizacao: string;
}

const dados: BancoHorasItem[] = [
  { id: '1', colaborador: 'Carlos Silva', creditos: '18:30', debitos: '06:00', saldo: '+12:30', saldoMinutos: 750, ultimaAtualizacao: '12/03/2026' },
  { id: '2', colaborador: 'Maria Oliveira', creditos: '04:00', debitos: '08:15', saldo: '-04:15', saldoMinutos: -255, ultimaAtualizacao: '12/03/2026' },
  { id: '3', colaborador: 'Joao Santos', creditos: '22:00', debitos: '20:00', saldo: '+02:00', saldoMinutos: 120, ultimaAtualizacao: '11/03/2026' },
  { id: '4', colaborador: 'Ana Pereira', creditos: '00:00', debitos: '00:00', saldo: '00:00', saldoMinutos: 0, ultimaAtualizacao: '12/03/2026' },
  { id: '5', colaborador: 'Pedro Costa', creditos: '10:45', debitos: '02:30', saldo: '+08:15', saldoMinutos: 495, ultimaAtualizacao: '10/03/2026' },
  { id: '6', colaborador: 'Lucia Ferreira', creditos: '06:00', debitos: '10:30', saldo: '-04:30', saldoMinutos: -270, ultimaAtualizacao: '12/03/2026' },
];

const resumo = [
  { label: 'Total Creditos', value: '61:15h', icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-50' },
  { label: 'Total Debitos', value: '47:15h', icon: TrendingDown, color: 'text-red-600', bg: 'bg-red-50' },
  { label: 'Saldo Geral', value: '+14:00h', icon: Hourglass, color: 'text-blue-600', bg: 'bg-blue-50' },
  { label: 'Colaboradores', value: '6', icon: Minus, color: 'text-gray-600', bg: 'bg-gray-100' },
];

export default function BancoHorasPage() {
  const [busca, setBusca] = useState('');

  const filtered = busca
    ? dados.filter((d) => d.colaborador.toLowerCase().includes(busca.toLowerCase()))
    : dados;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Hourglass className="w-6 h-6 text-green-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Banco de Horas</h1>
            <p className="text-gray-500 mt-1">Saldos acumulados — Marco 2026</p>
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
                    <p className="text-2xl font-bold mt-1">{r.value}</p>
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

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Buscar colaborador..."
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
                {filtered.map((d) => (
                  <tr key={d.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{d.colaborador}</td>
                    <td className="py-3 px-4 text-center font-mono text-green-600">{d.creditos}</td>
                    <td className="py-3 px-4 text-center font-mono text-red-600">{d.debitos}</td>
                    <td className="py-3 px-4 text-center">
                      <span className={`inline-flex px-2 py-1 text-xs font-bold rounded-full font-mono ${
                        d.saldoMinutos > 0 ? 'bg-green-100 text-green-800' :
                        d.saldoMinutos < 0 ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {d.saldo}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-500">{d.ultimaAtualizacao}</td>
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
