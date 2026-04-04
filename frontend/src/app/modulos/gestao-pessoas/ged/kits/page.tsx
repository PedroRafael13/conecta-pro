'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Loader2, Eye, Send, CheckCircle, Filter, FolderOpen,
  Plus, X, Wand2,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const API_BASE = '/api/v1/ged';

function getAuthHeaders() {
  if (typeof window === 'undefined') return { 'Content-Type': 'application/json' } as HeadersInit;
  let token: string | null = null;
  try {
    token = localStorage.getItem('access_token') || localStorage.getItem('token');
  } catch {
    token = null;
  }
  if (!token) {
    window.location.href = '/login';
    return { 'Content-Type': 'application/json' } as HeadersInit;
  }
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  } as HeadersInit;
}

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  const el = document.createElement('div');
  el.className = `fixed top-4 right-4 z-[9999] px-4 py-3 rounded-lg shadow-lg text-sm font-medium text-white transition-opacity ${type === 'error' ? 'bg-red-500' : 'bg-emerald-500'}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

interface Kit {
  id: string;
  client_name: string;
  client_id: string;
  reference_month: string;
  status: string;
  total_documents: number;
  documents_signed: number;
  signed_documents: number;
  completion_percentage: number;
}

interface Client {
  id: string;
  name: string;
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

const statusOptions = [
  { value: '', label: 'Todos os Status' },
  { value: 'em_montagem', label: 'Em Montagem' },
  { value: 'completo', label: 'Completo' },
  { value: 'enviado', label: 'Enviado' },
  { value: 'conferido', label: 'Conferido' },
  { value: 'aprovado', label: 'Aprovado' },
];

export default function KitsListPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [kits, setKits] = useState<Kit[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterMonth, setFilterMonth] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterClient, setFilterClient] = useState('');
  const [showNewKit, setShowNewKit] = useState(false);
  const [showMontarConfirm, setShowMontarConfirm] = useState(false);
  const [newKitClient, setNewKitClient] = useState('');
  const [newKitMonth, setNewKitMonth] = useState('');
  const [creatingKit, setCreatingKit] = useState(false);
  const [montando, setMontando] = useState(false);

  useEffect(() => {
    if (searchParams?.get('new') === 'true') setShowNewKit(true);
  }, [searchParams]);

  useEffect(() => { fetchClients(); }, []);
  useEffect(() => { fetchKits(); }, [filterMonth, filterStatus, filterClient]);

  async function fetchClients() {
    try {
      const res = await fetch(`${API_BASE}/clients`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setClients(Array.isArray(data) ? data : data.items || []);
      }
    } catch (err) {
      console.error('fetchClients:', err);
    }
  }

  async function fetchKits() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterMonth) params.append('reference_month', filterMonth);
      if (filterStatus) params.append('status', filterStatus);
      if (filterClient) params.append('client_id', filterClient);
      const qs = params.toString();
      const res = await fetch(`${API_BASE}/kits${qs ? '?' + qs : ''}`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setKits(Array.isArray(data) ? data : data.items || []);
      }
    } catch (err) {
      console.error('fetchKits:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateKit() {
    if (!newKitClient) { showToast('Selecione um cliente', 'error'); return; }
    if (!newKitMonth) { showToast('Selecione o mês', 'error'); return; }
    setCreatingKit(true);
    try {
      const res = await fetch(`${API_BASE}/kits`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ client_id: newKitClient, reference_month: newKitMonth + '-01' }),
      });
      if (res.ok) {
        showToast('Kit criado com sucesso');
        setShowNewKit(false);
        setNewKitClient('');
        setNewKitMonth('');
        fetchKits();
      } else if (res.status === 401 || res.status === 403) {
        showToast('Sessão expirada. Faça login novamente.', 'error');
        setTimeout(() => { window.location.href = '/login'; }, 1500);
      } else {
        const err = await res.json().catch(() => null);
        showToast(err?.detail || `Erro ${res.status}: não foi possível criar o kit`, 'error');
      }
    } catch (error) {
      showToast('Erro de conexão ao criar kit', 'error');
      console.error('createKit:', error);
    } finally {
      setCreatingKit(false);
    }
  }

  async function handleSend(kitId: string) {
    if (!confirm('Confirma o envio deste kit ao cliente?')) return;
    try {
      const res = await fetch(`${API_BASE}/kits/${kitId}/send`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        showToast('Kit enviado com sucesso');
        fetchKits();
      } else {
        const err = await res.json().catch(() => null);
        showToast(err?.detail || `Erro ${res.status} ao enviar kit`, 'error');
      }
    } catch (error) {
      showToast('Erro de conexão ao enviar', 'error');
      console.error('handleSend:', error);
    }
  }

  async function handleApprove(kitId: string) {
    if (!confirm('Confirma a aprovação deste kit?')) return;
    try {
      const res = await fetch(`${API_BASE}/kits/${kitId}/approve`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        showToast('Kit aprovado com sucesso');
        fetchKits();
      } else {
        const err = await res.json().catch(() => null);
        showToast(err?.detail || `Erro ${res.status} ao aprovar kit`, 'error');
      }
    } catch (error) {
      showToast('Erro de conexão ao aprovar', 'error');
      console.error('handleApprove:', error);
    }
  }

  async function handleMontarKits() {
    setMontando(true);
    try {
      const res = await fetch(`${API_BASE}/kits/montar`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`Kits montados: ${data.kits_criados}`);
        fetchKits();
      } else {
        const err = await res.json().catch(() => null);
        showToast(err?.detail || 'Erro ao montar kits', 'error');
      }
    } catch (error) {
      showToast('Erro de conexão', 'error');
      console.error('montarKits:', error);
    } finally {
      setMontando(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Kits Documentais</h1>
          <p className="text-gray-500 mt-1">Listagem e gerenciamento de kits</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowMontarConfirm(true)}
            disabled={montando}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 disabled:opacity-50"
          >
            {montando ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}
            Montar Kits
          </button>
          <button
            onClick={() => setShowNewKit(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />Novo Kit
          </button>
        </div>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <Filter className="h-4 w-4 text-gray-400" />
            <div>
              <label className="block text-xs text-gray-500 mb-1">Mes Referencia</label>
              <input type="month" value={filterMonth} onChange={(e) => setFilterMonth(e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm outline-none" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Status</label>
              <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm outline-none">
                {statusOptions.map((opt) => (<option key={opt.value} value={opt.value}>{opt.label}</option>))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Cliente</label>
              <select value={filterClient} onChange={(e) => setFilterClient(e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm outline-none">
                <option value="">Todos os Clientes</option>
                {clients.map((c) => (<option key={c.id} value={c.id}>{c.name}</option>))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Carregando kits...</span>
        </div>
      ) : (
        <Card className="border border-gray-200">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Cliente</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Mes</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Docs</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Assinados</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Conclusao</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {kits.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-gray-400">
                        <FolderOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        Nenhum kit encontrado
                      </td>
                    </tr>
                  ) : (
                    kits.map((kit) => (
                      <tr key={kit.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium text-gray-900">{kit.client_name || '—'}</td>
                        <td className="py-3 px-4 text-gray-600">{kit.reference_month}</td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusColors[kit.status] || 'bg-gray-100 text-gray-800'}`}>
                            {statusLabels[kit.status] || kit.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-600">{kit.total_documents ?? 0}</td>
                        <td className="py-3 px-4 text-gray-600">{kit.documents_signed ?? kit.signed_documents ?? 0}/{kit.total_documents ?? 0}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${Math.min(100, kit.completion_percentage ?? 0)}%` }} />
                            </div>
                            <span className="text-xs text-gray-500">{Math.round(kit.completion_percentage ?? 0)}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-1">
                            <button onClick={() => router.push(`/modulos/gestao-pessoas/ged/kits/${kit.id}`)} className="p-1.5 rounded hover:bg-gray-100" title="Visualizar">
                              <Eye className="h-4 w-4 text-gray-600" />
                            </button>
                            <button onClick={() => handleSend(kit.id)} className="p-1.5 rounded hover:bg-blue-50" title="Enviar" disabled={kit.status === 'enviado' || kit.status === 'aprovado'}>
                              <Send className="h-4 w-4 text-blue-500" />
                            </button>
                            <button onClick={() => handleApprove(kit.id)} className="p-1.5 rounded hover:bg-green-50" title="Aprovar" disabled={kit.status === 'aprovado'}>
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal Novo Kit */}
      {showNewKit && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 relative">
            <button onClick={() => setShowNewKit(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
              <X className="h-5 w-5" />
            </button>
            <h2 className="text-lg font-bold mb-4">Novo Kit Documental</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Cliente *</label>
                <select value={newKitClient} onChange={e => setNewKitClient(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option value="">Selecione o cliente</option>
                  {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mês Referência *</label>
                <input type="month" value={newKitMonth} onChange={e => setNewKitMonth(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button onClick={() => setShowNewKit(false)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</button>
              <button onClick={handleCreateKit} disabled={creatingKit} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                {creatingKit ? <Loader2 className="h-4 w-4 animate-spin inline mr-1" /> : null}
                Criar Kit
              </button>
            </div>
          </div>
        </div>
      )}
      {showMontarConfirm && (
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
                  handleMontarKits();
                }}
                className="px-4 py-2 bg-[#F97316] text-white rounded-lg text-sm font-medium hover:bg-orange-600"
              >
                Sim, Montar Kits
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
