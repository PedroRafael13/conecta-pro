'use client';

import { useState } from 'react';
import {
  FileText,
  Users,
  Shield,
  PenTool,
  Download,
  Loader2,
  Calendar,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const API_BASE = '/api/v1/ged';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface ReportCard {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  endpoint: string;
}

const reports: ReportCard[] = [
  {
    id: 'mensal',
    title: 'Relatorio Mensal',
    description: 'Resumo completo dos kits documentais do periodo selecionado, incluindo status de envio e aprovação.',
    icon: FileText,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    endpoint: '/reports/monthly',
  },
  {
    id: 'cliente',
    title: 'Relatorio por Cliente',
    description: 'Detalhamento por cliente com historico de kits, documentos pendentes e taxa de conclusao.',
    icon: Users,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    endpoint: '/reports/by-client',
  },
  {
    id: 'compliance',
    title: 'Analise de Compliance',
    description: 'Verificacao de conformidade documental, certidoes vencidas e documentos obrigatorios faltantes.',
    icon: Shield,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    endpoint: '/reports/compliance',
  },
  {
    id: 'assinaturas',
    title: 'Historico de Assinaturas',
    description: 'Rastreamento de todas as assinaturas digitais realizadas no periodo, com informacoes de certificado.',
    icon: PenTool,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    endpoint: '/reports/signatures',
  },
];

export default function RelatoriosPage() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [generatingId, setGeneratingId] = useState<string | null>(null);

  async function handleGenerate(report: ReportCard) {
    if (!startDate || !endDate) {
      alert('Selecione o periodo (data inicio e data fim).');
      return;
    }

    setGeneratingId(report.id);
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      });
      const res = await fetch(`${API_BASE}${report.endpoint}?${params.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const ext = res.headers.get('content-type')?.includes('pdf') ? 'pdf' : 'xlsx';
        a.download = `${report.id}-${startDate}-${endDate}.${ext}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Erro ao gerar relatorio. Tente novamente.');
      }
    } catch (err) {
      alert('Erro ao gerar relatorio. Verifique sua conexao.');
    } finally {
      setGeneratingId(null);
    }
  }

  async function handleDownload(report: ReportCard) {
    if (!startDate || !endDate) {
      alert('Selecione o periodo (data inicio e data fim).');
      return;
    }

    setGeneratingId(report.id);
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        format: 'pdf',
      });
      const res = await fetch(`${API_BASE}${report.endpoint}/download?${params.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${report.id}-${startDate}-${endDate}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Erro ao baixar relatorio.');
      }
    } catch (err) {
    } finally {
      setGeneratingId(null);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Relatorios GED</h1>
        <p className="text-gray-500 mt-1">Gere e exporte relatorios do modulo de documentos</p>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-end gap-4">
            <Calendar className="h-5 w-5 text-gray-400 mb-1" />
            <div>
              <label className="block text-xs text-gray-500 mb-1">Data Inicio</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Data Fim</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            {(!startDate || !endDate) && (
              <p className="text-xs text-amber-600 mb-1">Selecione o periodo para gerar os relatorios</p>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((report) => {
          const Icon = report.icon;
          const isGenerating = generatingId === report.id;
          return (
            <Card key={report.id} className="border border-gray-200">
              <CardHeader className="pb-2">
                <div className="flex items-start gap-3">
                  <div className={`p-3 rounded-lg ${report.bgColor}`}>
                    <Icon className={`h-6 w-6 ${report.color}`} />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-base font-semibold">{report.title}</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">{report.description}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => handleGenerate(report)}
                    disabled={isGenerating || !startDate || !endDate}
                    className="flex items-center gap-2 px-3 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    {isGenerating ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <FileText className="h-4 w-4" />
                    )}
                    Gerar
                  </button>
                  <button
                    onClick={() => handleDownload(report)}
                    disabled={isGenerating || !startDate || !endDate}
                    className="flex items-center gap-2 px-3 py-2 text-sm font-medium bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    Download PDF
                  </button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
