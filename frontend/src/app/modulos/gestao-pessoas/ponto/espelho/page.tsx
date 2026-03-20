'use client';

import { useState } from 'react';
import { FileText, Download, ChevronLeft, ChevronRight, Printer } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface DayRecord {
  dia: string;
  diaSemana: string;
  entrada1: string;
  saida1: string;
  entrada2: string;
  saida2: string;
  total: string;
  obs: string;
}

const sampleData: DayRecord[] = [
  { dia: '01', diaSemana: 'Seg', entrada1: '08:00', saida1: '12:00', entrada2: '13:00', saida2: '17:00', total: '08:00', obs: '' },
  { dia: '02', diaSemana: 'Ter', entrada1: '08:15', saida1: '12:00', entrada2: '13:00', saida2: '17:00', total: '07:45', obs: 'Atraso 15min' },
  { dia: '03', diaSemana: 'Qua', entrada1: '08:00', saida1: '12:00', entrada2: '13:00', saida2: '18:30', total: '09:30', obs: 'HE 1:30' },
  { dia: '04', diaSemana: 'Qui', entrada1: '08:00', saida1: '12:00', entrada2: '13:00', saida2: '17:00', total: '08:00', obs: '' },
  { dia: '05', diaSemana: 'Sex', entrada1: '08:00', saida1: '12:00', entrada2: '13:00', saida2: '17:00', total: '08:00', obs: '' },
  { dia: '06', diaSemana: 'Sab', entrada1: '--:--', saida1: '--:--', entrada2: '--:--', saida2: '--:--', total: '00:00', obs: 'Folga' },
  { dia: '07', diaSemana: 'Dom', entrada1: '--:--', saida1: '--:--', entrada2: '--:--', saida2: '--:--', total: '00:00', obs: 'Folga' },
  { dia: '08', diaSemana: 'Seg', entrada1: '07:55', saida1: '12:00', entrada2: '13:00', saida2: '17:00', total: '08:05', obs: '' },
  { dia: '09', diaSemana: 'Ter', entrada1: '--:--', saida1: '--:--', entrada2: '--:--', saida2: '--:--', total: '00:00', obs: 'Falta' },
  { dia: '10', diaSemana: 'Qua', entrada1: '08:00', saida1: '12:00', entrada2: '13:00', saida2: '17:00', total: '08:00', obs: '' },
];

export default function EspelhoPontoPage() {
  const [mesAtual] = useState('Marco 2026');

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

      <Card className="border border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-semibold">Competencia</CardTitle>
          <div className="flex items-center gap-4">
            <button type="button" className="p-1 hover:bg-gray-100 rounded">
              <ChevronLeft className="h-5 w-5 text-gray-600" />
            </button>
            <span className="text-sm font-medium text-gray-700 min-w-[120px] text-center">{mesAtual}</span>
            <button type="button" className="p-1 hover:bg-gray-100 rounded">
              <ChevronRight className="h-5 w-5 text-gray-600" />
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4 text-sm text-gray-600">
            <span>Colaborador: <strong className="text-gray-900">Selecionar...</strong></span>
            <span>Jornada: <strong className="text-gray-900">44h semanais</strong></span>
          </div>
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
                {sampleData.map((row) => (
                  <tr
                    key={row.dia}
                    className={`border-b border-gray-100 hover:bg-gray-50 ${
                      row.diaSemana === 'Sab' || row.diaSemana === 'Dom' ? 'bg-gray-50/50' : ''
                    }`}
                  >
                    <td className="py-2.5 px-3 font-medium">{row.dia}</td>
                    <td className="py-2.5 px-3 text-gray-600">{row.diaSemana}</td>
                    <td className="py-2.5 px-3 text-center font-mono">{row.entrada1}</td>
                    <td className="py-2.5 px-3 text-center font-mono">{row.saida1}</td>
                    <td className="py-2.5 px-3 text-center font-mono">{row.entrada2}</td>
                    <td className="py-2.5 px-3 text-center font-mono">{row.saida2}</td>
                    <td className="py-2.5 px-3 text-center font-mono font-medium">{row.total}</td>
                    <td className="py-2.5 px-3">
                      {row.obs && (
                        <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${
                          row.obs.includes('Atraso') ? 'bg-amber-100 text-amber-800' :
                          row.obs.includes('HE') ? 'bg-blue-100 text-blue-800' :
                          row.obs.includes('Falta') ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {row.obs}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex justify-between items-center text-sm text-gray-500 border-t border-gray-200 pt-4">
            <span>Total Trabalhado: <strong className="text-gray-900">57:20h</strong></span>
            <span>Horas Esperadas: <strong className="text-gray-900">56:00h</strong></span>
            <span>Saldo: <strong className="text-green-600">+01:20h</strong></span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
