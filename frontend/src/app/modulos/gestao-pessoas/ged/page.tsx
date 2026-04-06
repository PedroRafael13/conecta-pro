'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useRouter } from 'next/navigation';

function formatRefMonth(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso + (iso.length === 10 ? 'T12:00:00' : ''));
  return new Intl.DateTimeFormat('pt-BR', { month: '2-digit', year: 'numeric' }).format(d);
}
import {
  FolderOpen,
  Clock,
  Send,
  BarChart3,
  Loader2,
  Plus,
  Wand2,
  Eye,
  ChevronRight,
  Upload,
  PenTool,
  MessageCircle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const API_BASE = '/api/v1/ged';

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  const el = document.createElement('div');
  el.className = `fixed top-4 right-4 z-[9999] px-4 py-3 rounded-lg shadow-lg text-sm font-medium text-white transition-opacity ${type === 'error' ? 'bg-red-500' : 'bg-emerald-500'}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

function getAuthHeaders() {
  let token: string | null = null;
  try {
    token = localStorage.getItem('access_token') || localStorage.getItem('token');
  } catch {
    token = null;
  }
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Summary {
  total_kits: number;
  kits_pendentes: number;
  kits_enviados: number;
  taxa_conclusao: number;
}

interface Kit {
  id: string;
  client_name: string;
  reference_month: string;
  status: string;
  completion_percentage: number;
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

export default function GEDDashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<Summary>({
    total_kits: 0,
    kits_pendentes: 0,
    kits_enviados: 0,
    taxa_conclusao: 0,
  });
  const [recentKits, setRecentKits] = useState<Kit[]>([]);
  const [totalKitsGeral, setTotalKitsGeral] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showMontarConfirm, setShowMontarConfirm] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    setLoading(true);
    try {
      const [sumRes, kitsRes] = await Promise.all([
        fetch(`${API_BASE}/kits/summary`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/kits?page_size=10`, { headers: getAuthHeaders() }),
      ]);
      if (sumRes.ok) {
        const data = await sumRes.json();
        setSummary({
          total_kits: data.total_kits ?? 0,
          kits_pendentes: data.kits_pending_send ?? data.kits_pendentes ?? 0,
          kits_enviados: data.kits_pending_approval ?? data.kits_enviados ?? 0,
          taxa_conclusao: Math.round(parseFloat(data.average_completion ?? data.taxa_conclusao ?? '0')),
        });
      }
      if (kitsRes.ok) {
        const data = await kitsRes.json();
        setRecentKits(Array.isArray(data) ? data : data.items || []);
        setTotalKitsGeral(Array.isArray(data) ? data.length : data.total ?? 0);
      }
    } catch (err) {
      console.error('fetchData:', err);
      showToast('Erro ao carregar dados', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function handleAutoAssemble() {
    try {
      showToast('Montando kits...');
      const res = await fetch(`${API_BASE}/kits/montar`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json().catch(() => null);
        showToast(`Kits montados: ${data?.kits_created ?? data?.total ?? 'OK'}`);
        fetchData();
      } else {
        showToast(`Erro ao montar kits: ${res.status}`, 'error');
      }
    } catch (error) {
      showToast('Erro de conexão ao montar kits', 'error');
      console.error('handleAutoAssemble:', error);
    }
  }

  const statCards = [
    { label: 'Total Kits', value: totalKitsGeral || summary.total_kits, icon: FolderOpen, color: 'text-blue-600', bg: 'bg-blue-50', href: '/modulos/gestao-pessoas/ged/kits' },
    { label: 'Kits Pendentes', value: summary.kits_pendentes, icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-50', href: '/modulos/gestao-pessoas/ged/kits?status=em_montagem' },
    { label: 'Kits Enviados', value: summary.kits_enviados, icon: Send, color: 'text-green-600', bg: 'bg-green-50', href: '/modulos/gestao-pessoas/ged/kits?status=enviado' },
    { label: 'Taxa de Conclusão', value: `${summary.taxa_conclusao}%`, icon: BarChart3, color: 'text-purple-600', bg: 'bg-purple-50', href: '/modulos/gestao-pessoas/ged/kits' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">Carregando...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">GED — Gestão Eletrônica de Documentos</h1>
          <p className="text-gray-500 mt-1">Kits documentais, certidões e envios</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => router.push('/modulos/gestao-pessoas/ged/whatsapp')}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
          >
            <MessageCircle className="h-4 w-4" />
            WhatsApp
          </button>
          <button
            onClick={() => router.push('/modulos/gestao-pessoas/ged/assinaturas')}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            <PenTool className="h-4 w-4" />
            Assinaturas
          </button>
          <button
            onClick={() => router.push('/modulos/gestao-pessoas/ged/upload')}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            <Upload className="h-4 w-4" />
            Upload com IA
          </button>
          <button
            onClick={() => setShowMontarConfirm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            <Wand2 className="h-4 w-4" />
            Montar Kits
          </button>
          <button
            onClick={() => router.push('/modulos/gestao-pessoas/ged/kits/?new=true')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Novo Kit
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card
              key={stat.label}
              className="border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push(stat.href)}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border border-gray-200">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-semibold">Kits Recentes</CardTitle>
          <button
            onClick={() => router.push('/modulos/gestao-pessoas/ged/kits')}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            Ver todos <ChevronRight className="h-4 w-4" />
          </button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Cliente</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Mês Ref.</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Conclusão</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Ações</th>
                </tr>
              </thead>
              <tbody>
                {recentKits.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-400">
                      Nenhum kit encontrado
                    </td>
                  </tr>
                ) : (
                  recentKits.map((kit) => (
                    <tr key={kit.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{kit.client_name}</td>
                      <td className="py-3 px-4 text-gray-600">{formatRefMonth(kit.reference_month)}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusColors[kit.status] || 'bg-gray-100 text-gray-800'}`}>
                          {statusLabels[kit.status] || kit.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${kit.completion_percentage}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-500">{kit.completion_percentage}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => router.push(`/modulos/gestao-pessoas/ged/kits/${kit.id}`)}
                          className="p-1 rounded hover:bg-gray-100"
                          title="Visualizar"
                        >
                          <Eye className="h-4 w-4 text-gray-500" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      {showMontarConfirm && createPortal(
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl border border-gray-200 p-6 max-w-md w-full">
            <h3 className="text-lg font-bold text-[#1E3A5F] mb-2">Confirmar Montagem de Kits</h3>
            <p className="text-gray-600 mb-4 text-sm">
              Esta ação irá criar kits documentais para o mês de referência de todos os clientes
              ativos. Deseja continuar?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowMontarConfirm(false)}
                className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  setShowMontarConfirm(false);
                  handleAutoAssemble();
                }}
                className="px-4 py-2 bg-[#F97316] text-white rounded-lg text-sm font-medium hover:bg-orange-600"
              >
                Sim, Montar Kits
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
