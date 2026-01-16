import React from 'react';
import {
  FileText,
  BarChart3,
  PieChart,
  TrendingUp,
  Download,
  Calendar,
  Filter,
} from 'lucide-react';

export function ReportsPage() {
  const reports = [
    {
      id: '1',
      name: 'Relatorio Executivo Mensal',
      description: 'Visao consolidada de todos os indicadores',
      type: 'executive',
      lastGenerated: '2024-01-10',
    },
    {
      id: '2',
      name: 'Analise de Desempenho',
      description: 'Metricas de performance operacional',
      type: 'performance',
      lastGenerated: '2024-01-09',
    },
    {
      id: '3',
      name: 'Relatorio Financeiro',
      description: 'Demonstrativos e fluxo de caixa',
      type: 'financial',
      lastGenerated: '2024-01-08',
    },
    {
      id: '4',
      name: 'Compliance e Auditoria',
      description: 'Status de conformidade e auditorias',
      type: 'compliance',
      lastGenerated: '2024-01-07',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="h-7 w-7 text-conecta-escuro" />
            Relatorios
          </h1>
          <p className="text-gray-600 mt-1">
            Gere e visualize relatorios do sistema
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Filter className="h-4 w-4" />
            Filtros
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
            <FileText className="h-4 w-4" />
            Novo Relatorio
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Gerados</p>
              <p className="text-xl font-bold text-gray-900">156</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <BarChart3 className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Este Mes</p>
              <p className="text-xl font-bold text-gray-900">23</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Download className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Downloads</p>
              <p className="text-xl font-bold text-gray-900">89</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Calendar className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Agendados</p>
              <p className="text-xl font-bold text-gray-900">12</p>
            </div>
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Relatorios Disponiveis</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {reports.map((report) => (
            <div key={report.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    {report.type === 'executive' && <TrendingUp className="h-5 w-5 text-blue-600" />}
                    {report.type === 'performance' && <BarChart3 className="h-5 w-5 text-green-600" />}
                    {report.type === 'financial' && <PieChart className="h-5 w-5 text-purple-600" />}
                    {report.type === 'compliance' && <FileText className="h-5 w-5 text-orange-600" />}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{report.name}</h3>
                    <p className="text-sm text-gray-600">{report.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">
                    Ultimo: {new Date(report.lastGenerated).toLocaleDateString('pt-BR')}
                  </span>
                  <div className="flex items-center gap-2">
                    <button className="px-3 py-1.5 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                      Visualizar
                    </button>
                    <button className="px-3 py-1.5 text-sm bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
                      Gerar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ReportsPage;
