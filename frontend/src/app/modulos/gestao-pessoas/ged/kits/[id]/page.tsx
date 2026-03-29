'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Loader2,
  ArrowLeft,
  Send,
  CheckCircle,
  XCircle,
  Download,
  FileText,
  Building2,
  User,
  Eye,
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

interface Document {
  id: string;
  name: string;
  type: string;
  signed: boolean;
  origin: string;
  category: 'employee' | 'company';
  file_url?: string;
}

interface KitDetail {
  id: string;
  client_name: string;
  client_id: string;
  reference_month: string;
  status: string;
  completion_percentage: number;
  total_documents: number;
  signed_documents: number;
  documents: Document[];
  created_at: string;
}

const statusColors: Record<string, string> = {
  em_montagem: 'bg-yellow-100 text-yellow-800',
  completo: 'bg-blue-100 text-blue-800',
  enviado: 'bg-green-100 text-green-800',
  conferido: 'bg-purple-100 text-purple-800',
  aprovado: 'bg-emerald-100 text-emerald-800',
};

const statusLabels: Record<string, string> = {
  em_montagem: 'Em Montagem',
  completo: 'Completo',
  enviado: 'Enviado',
  conferido: 'Conferido',
  aprovado: 'Aprovado',
};

const originLabels: Record<string, string> = {
  dp: 'Depto Pessoal',
  rh: 'Recursos Humanos',
  fiscal: 'Fiscal',
  contabil: 'Contabil',
  financeiro: 'Financeiro',
  operacional: 'Operacional',
};

export default function KitDetailPage() {
  const params = useParams();
  const router = useRouter();
  const kitId = params.id as string;
  const [kit, setKit] = useState<KitDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'employee' | 'company'>('employee');

  useEffect(() => {
    if (kitId) fetchKit();
  }, [kitId]);

  async function fetchKit() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/kits/${kitId}`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setKit(data);
      }
    } catch {
      // silenced
    } finally {
      setLoading(false);
    }
  }

  async function handleSendKit() {
    if (!confirm('Confirma o envio deste kit ao cliente?')) return;
    try {
      await fetch(`${API_BASE}/kits/${kitId}/send`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      fetchKit();
    } catch {
      // silenced
    }
  }

  async function handleApproveKit() {
    if (!confirm('Confirma a aprovação deste kit?')) return;
    try {
      await fetch(`${API_BASE}/kits/${kitId}/approve`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      fetchKit();
    } catch {
      // silenced
    }
  }

  async function handleExport(format: 'zip' | 'pdf') {
    try {
      const res = await fetch(`${API_BASE}/kits/${kitId}/export?format=${format}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kit-${kitId}.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch {
      // silenced
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">Carregando kit...</span>
      </div>
    );
  }

  if (!kit) {
    return (
      <div className="p-6 text-center text-gray-500">
        Kit nao encontrado.
        <button type="button" onClick={() => router.push('/modulos/gestao-pessoas/ged/kits')} className="ml-2 text-blue-600 hover:underline">
          Voltar
        </button>
      </div>
    );
  }

  const employeeDocs = (kit.documents || []).filter((d) => d.category === 'employee');
  const companyDocs = (kit.documents || []).filter((d) => d.category === 'company');
  const activeDocs = activeTab === 'employee' ? employeeDocs : companyDocs;

  return (
    <div className="p-6 space-y-6">
      <button
        onClick={() => router.push('/modulos/gestao-pessoas/ged/kits')}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar para Kits
      </button>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{kit.client_name}</h1>
            <span className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-full ${statusColors[kit.status] || 'bg-gray-100 text-gray-800'}`}>
              {statusLabels[kit.status] || kit.status}
            </span>
          </div>
          <p className="text-gray-500 mt-1">
            Referencia: {kit.reference_month} | {kit.total_documents} documentos
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleSendKit}
            disabled={kit.status === 'enviado' || kit.status === 'aprovado'}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Send className="h-4 w-4" />
            Enviar Kit
          </button>
          <button
            onClick={handleApproveKit}
            disabled={kit.status === 'aprovado'}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            <CheckCircle className="h-4 w-4" />
            Aprovar Kit
          </button>
          <button
            onClick={() => handleExport('zip')}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="h-4 w-4" />
            ZIP
          </button>
          <button
            onClick={() => handleExport('pdf')}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <FileText className="h-4 w-4" />
            PDF
          </button>
        </div>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Progresso do Kit</span>
            <span className="text-sm font-bold text-gray-900">{kit.completion_percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${kit.completion_percentage}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>{kit.signed_documents} assinados</span>
            <span>{kit.total_documents} total</span>
          </div>
        </CardContent>
      </Card>

      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('employee')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'employee'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <User className="h-4 w-4" />
          Documentos do Funcionario ({employeeDocs.length})
        </button>
        <button
          onClick={() => setActiveTab('company')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'company'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Building2 className="h-4 w-4" />
          Documentos da Empresa ({companyDocs.length})
        </button>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Nome</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Tipo</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Assinado</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Origem</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Acoes</th>
                </tr>
              </thead>
              <tbody>
                {activeDocs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-400">
                      Nenhum documento nesta categoria
                    </td>
                  </tr>
                ) : (
                  activeDocs.map((doc) => (
                    <tr key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{doc.name}</td>
                      <td className="py-3 px-4 text-gray-600">{doc.type}</td>
                      <td className="py-3 px-4">
                        {doc.signed ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-400" />
                        )}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {originLabels[doc.origin] || doc.origin}
                      </td>
                      <td className="py-3 px-4">
                        {doc.file_url && (
                          <button
                            onClick={() => window.open(doc.file_url, '_blank')}
                            className="p-1 rounded hover:bg-gray-100"
                            title="Visualizar"
                          >
                            <Eye className="h-4 w-4 text-gray-500" />
                          </button>
                        )}
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
