'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Key, RefreshCw, Copy, Check, Power, FileText, Search,
  Shield, AlertTriangle, Clock, Eye, X, Loader2, Users,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const API = '/api/v1/portal/access-management';

function getHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface ClientAccess {
  client_id: string;
  nome: string;
  cnpj: string;
  email: string;
  portal_ativo: boolean;
  portal_username: string;
  ultimo_acesso: string | null;
  data_criacao: string | null;
}

interface LogEntry {
  id: string;
  acao: string;
  detalhes: string;
  ip: string | null;
  dispositivo: string | null;
  data: string | null;
}

interface ProvisionResult {
  portal_username: string;
  senha_temporaria: string;
  portal_url: string;
  cnpj: string;
  nome: string;
}

function fmtDate(iso: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('pt-BR') + ' ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function StatusBadge({ client }: { client: ClientAccess }) {
  if (!client.portal_ativo) {
    return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">Inativo</span>;
  }
  if (!client.ultimo_acesso) {
    return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">Aguardando</span>;
  }
  return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Ativo</span>;
}

export default function GerenciamentoAcessosPage() {
  const [clients, setClients] = useState<ClientAccess[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [provisionModal, setProvisionModal] = useState<ProvisionResult | null>(null);
  const [logsModal, setLogsModal] = useState<{ clientId: string; nome: string; logs: LogEntry[] } | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [toast, setToast] = useState('');

  const fetchClients = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(API, { headers: getHeaders() });
      if (res.ok) setClients(await res.json());
    } catch { /* silenciar */ } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchClients(); }, [fetchClients]);

  const filtered = useMemo(() => {
    if (!search) return clients;
    const s = search.toLowerCase();
    return clients.filter(c =>
      c.nome.toLowerCase().includes(s) || c.cnpj.toLowerCase().includes(s)
    );
  }, [clients, search]);

  const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(''), 4000); };

  async function handleProvision(clientId: string) {
    setActionLoading(clientId);
    try {
      const res = await fetch(`${API}/${clientId}/provision`, { method: 'POST', headers: getHeaders() });
      if (res.ok) {
        const data: ProvisionResult = await res.json();
        setProvisionModal(data);
        fetchClients();
      } else { showToast('Erro ao provisionar acesso'); }
    } catch { showToast('Erro de conexão'); }
    finally { setActionLoading(null); }
  }

  async function handleToggle(clientId: string, nome: string, ativo: boolean) {
    if (ativo && !confirm(`Desativar acesso de "${nome}" ao portal?`)) return;
    setActionLoading(clientId);
    try {
      const res = await fetch(`${API}/${clientId}/toggle`, { method: 'POST', headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        showToast(`Acesso ${data.acao} para ${nome}`);
        fetchClients();
      }
    } catch { showToast('Erro ao alterar acesso'); }
    finally { setActionLoading(null); }
  }

  async function handleLogs(clientId: string, nome: string) {
    setActionLoading(clientId);
    try {
      const res = await fetch(`${API}/${clientId}/logs`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        setLogsModal({ clientId, nome, logs: data.logs || [] });
      }
    } catch { showToast('Erro ao carregar logs'); }
    finally { setActionLoading(null); }
  }

  async function handleCopy() {
    if (!provisionModal) return;
    const text = `Portal do Cliente — Conecta PRO\nUsername: ${provisionModal.portal_username}\nSenha: ${provisionModal.senha_temporaria}\nURL: ${provisionModal.portal_url}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const activeCount = clients.filter(c => c.portal_ativo).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6 text-indigo-600" />
            Gerenciamento de Acessos
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Portal do Cliente — provisionar, ativar e auditar</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400">
            <Users className="w-3 h-3 inline mr-1" />{activeCount}/{clients.length} ativos
          </span>
          <Button variant="outline" size="sm" onClick={fetchClients} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} /> Atualizar
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Buscar por nome ou CNPJ..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-left p-3 font-medium">Cliente</th>
                  <th className="text-left p-3 font-medium">CNPJ</th>
                  <th className="text-left p-3 font-medium">Status Portal</th>
                  <th className="text-left p-3 font-medium">Último Acesso</th>
                  <th className="text-right p-3 font-medium">Ações</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" /> Carregando...
                  </td></tr>
                ) : filtered.length === 0 ? (
                  <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Nenhum cliente encontrado</td></tr>
                ) : filtered.map(c => (
                  <tr key={c.client_id} className="border-b hover:bg-muted/30 transition-colors">
                    <td className="p-3">
                      <div className="font-medium">{c.nome}</div>
                      <div className="text-xs text-muted-foreground">{c.email}</div>
                    </td>
                    <td className="p-3 font-mono text-xs">{c.cnpj}</td>
                    <td className="p-3"><StatusBadge client={c} /></td>
                    <td className="p-3 text-muted-foreground text-xs">{fmtDate(c.ultimo_acesso)}</td>
                    <td className="p-3">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost" size="sm"
                          onClick={() => handleProvision(c.client_id)}
                          disabled={actionLoading === c.client_id}
                          title="Provisionar ou resetar senha"
                        >
                          {actionLoading === c.client_id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Key className="h-4 w-4" />}
                        </Button>
                        <Button
                          variant="ghost" size="sm"
                          onClick={() => handleToggle(c.client_id, c.nome, c.portal_ativo)}
                          disabled={actionLoading === c.client_id}
                          title={c.portal_ativo ? 'Desativar acesso' : 'Ativar acesso'}
                        >
                          <Power className={`h-4 w-4 ${c.portal_ativo ? 'text-green-600' : 'text-gray-400'}`} />
                        </Button>
                        <Button
                          variant="ghost" size="sm"
                          onClick={() => handleLogs(c.client_id, c.nome)}
                          disabled={actionLoading === c.client_id}
                          title="Ver logs de acesso"
                        >
                          <FileText className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Modal Provisionar */}
      {provisionModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => { setProvisionModal(null); setCopied(false); }}>
          <div className="bg-white dark:bg-gray-900 rounded-xl max-w-md w-full p-6 space-y-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold flex items-center gap-2"><Key className="h-5 w-5 text-indigo-600" /> Acesso Provisionado</h3>
              <button type="button" onClick={() => { setProvisionModal(null); setCopied(false); }} className="text-gray-400 hover:text-gray-600"><X className="h-5 w-5" /></button>
            </div>
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 text-sm text-amber-800 dark:text-amber-300 flex gap-2">
              <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>Esta senha será exibida apenas uma vez. Copie antes de fechar.</span>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-muted-foreground">Cliente</label>
                <p className="font-medium">{provisionModal.nome}</p>
              </div>
              <div>
                <label className="text-xs text-muted-foreground">CNPJ</label>
                <p className="font-mono">{provisionModal.cnpj}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 space-y-2">
                <div>
                  <label className="text-xs text-muted-foreground">Username</label>
                  <p className="font-mono font-bold text-lg">{provisionModal.portal_username}</p>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Senha temporária</label>
                  <p className="font-mono font-bold text-lg text-indigo-600">{provisionModal.senha_temporaria}</p>
                </div>
              </div>
              <div>
                <label className="text-xs text-muted-foreground">URL do portal</label>
                <p className="text-sm text-blue-600">{provisionModal.portal_url}</p>
              </div>
            </div>
            <Button onClick={handleCopy} className="w-full" variant={copied ? 'default' : 'outline'}>
              {copied ? <><Check className="h-4 w-4 mr-1" /> Copiado!</> : <><Copy className="h-4 w-4 mr-1" /> Copiar credenciais</>}
            </Button>
          </div>
        </div>
      )}

      {/* Modal Logs */}
      {logsModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setLogsModal(null)}>
          <div className="bg-white dark:bg-gray-900 rounded-xl max-w-2xl w-full p-6 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2"><Clock className="h-5 w-5" /> Logs — {logsModal.nome}</h3>
              <button type="button" onClick={() => setLogsModal(null)} className="text-gray-400 hover:text-gray-600"><X className="h-5 w-5" /></button>
            </div>
            {logsModal.logs.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">Nenhum log registrado</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2">Data/Hora</th><th className="pb-2">Ação</th><th className="pb-2">IP</th><th className="pb-2">Detalhes</th>
                  </tr>
                </thead>
                <tbody>
                  {logsModal.logs.slice(0, 20).map(l => (
                    <tr key={l.id} className="border-b">
                      <td className="py-2 text-xs text-muted-foreground whitespace-nowrap">{fmtDate(l.data)}</td>
                      <td className="py-2 font-medium">{l.acao}</td>
                      <td className="py-2 font-mono text-xs">{l.ip || '—'}</td>
                      <td className="py-2 text-xs text-muted-foreground max-w-[200px] truncate">{l.detalhes || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-4 right-4 bg-gray-900 text-white px-4 py-2 rounded-lg text-sm shadow-lg z-50 animate-in fade-in slide-in-from-bottom-2">
          {toast}
        </div>
      )}
    </div>
  );
}
