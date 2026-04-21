'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Loader2,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ShieldCheck,
  Search,
  FileText,
  Filter,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const API_BASE = '/api/v1/ged/certidoes';

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

interface Certificate {
  id: string;
  name: string;
  document_type: string;
  issuing_body: string | null;
  issue_date: string | null;
  expiry_date: string | null;
  status: 'valida' | 'vencida' | 'a_vencer' | 'sem_vencimento';
  file_path: string | null;
  file_url: string | null;
  notes: string | null;
  alerta_ativo: boolean;
  created_at: string | null;
  updated_at: string | null;
}

interface CertType {
  key: string;
  document_type: string;
  name: string;
  issuing_body: string;
}

interface Resumo {
  validas: number;
  vencidas: number;
  a_vencer_30d: number;
}

const typeLabels: Record<string, string> = {
  cnd_federal: 'CND Federal (PGFN/RFB)',
  cnd_trabalhista: 'CND Trabalhista (CNDT)',
  crf_fgts: 'CRF/FGTS (CEF)',
  cnd_municipal: 'CND Municipal (ISS)',
  cnd_estadual: 'CND Estadual (SEFAZ)',
  cnd_previdenciaria: 'CND Previdenciária',
  ALVARA: 'Alvará de Funcionamento',
  AUTORIZACAO_PF: 'Autorização Polícia Federal',
};

function daysUntilExpiry(expiry_date: string | null): number {
  if (!expiry_date) return 9999;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const expiry = new Date(expiry_date);
  expiry.setHours(0, 0, 0, 0);
  return Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

function getStatusConfig(cert: Certificate) {
  const days = daysUntilExpiry(cert.expiry_date);
  if (cert.status === 'vencida' || days <= 0) {
    return { label: 'Vencida', color: 'bg-red-100 text-red-800', icon: XCircle, priority: 0 };
  }
  if (days <= 7) {
    return { label: 'Crítico', color: 'bg-red-100 text-red-800', icon: AlertTriangle, priority: 1 };
  }
  if (cert.status === 'a_vencer' || days <= 30) {
    return { label: 'Vencendo', color: 'bg-yellow-100 text-yellow-800', icon: AlertTriangle, priority: 2 };
  }
  return { label: 'Válida', color: 'bg-green-100 text-green-800', icon: CheckCircle, priority: 3 };
}

function getDaysColor(days: number) {
  if (days <= 0) return 'text-red-600 font-bold';
  if (days <= 7) return 'text-red-600 font-semibold';
  if (days <= 30) return 'text-yellow-600 font-semibold';
  return 'text-green-600';
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('pt-BR');
}

export default function CertidoesPage() {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [certTypes, setCertTypes] = useState<CertType[]>([]);
  const [resumo, setResumo] = useState<Resumo>({ validas: 0, vencidas: 0, a_vencer_30d: 0 });
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  const loadData = useCallback(async () => {
    try {
      const [certsRes, typesRes] = await Promise.all([
        fetch(API_BASE, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/tipos`, { headers: getAuthHeaders() }),
      ]);

      if (certsRes.ok) {
        const data = await certsRes.json();
        setCertificates(data.certidoes || []);
        setResumo(data.resumo || { validas: 0, vencidas: 0, a_vencer_30d: 0 });
      }
      if (typesRes.ok) {
        const data = await typesRes.json();
        setCertTypes(data.tipos || []);
      }
    } catch (err) {
      console.error('Erro ao carregar certidões:', err);
      showToast('Erro ao carregar certidões.', 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      const res = await fetch(`${API_BASE}/sync`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        console.error('Erro ao sincronizar certidões:', res.status);
        showToast('Erro ao sincronizar certidões. Endpoint pode estar indisponível.', 'error');
      } else {
        showToast('Sincronização iniciada com sucesso.');
      }
      await loadData();
    } catch (err) {
      console.error('Erro ao sincronizar certidões:', err);
      showToast('Erro de conexão ao sincronizar certidões.', 'error');
    } finally {
      setSyncing(false);
    }
  };

  const validCount = resumo.validas;
  const expiringCount = resumo.a_vencer_30d;
  const expiredCount = resumo.vencidas;
  const urgentCount = certificates.filter((c) => {
    const days = daysUntilExpiry(c.expiry_date);
    return days > 0 && days <= 7;
  }).length;

  const filtered = certificates
    .filter((c) => {
      if (filterType !== 'all' && c.document_type !== filterType) return false;
      if (filterStatus === 'valida' && c.status !== 'valida') return false;
      if (filterStatus === 'vencendo' && c.status !== 'a_vencer') return false;
      if (filterStatus === 'vencida' && c.status !== 'vencida') return false;
      if (search) {
        const q = search.toLowerCase();
        return (
          (c.name || '').toLowerCase().includes(q) ||
          (c.document_type || '').toLowerCase().includes(q) ||
          (c.issuing_body || '').toLowerCase().includes(q)
        );
      }
      return true;
    })
    .sort((a, b) => daysUntilExpiry(a.expiry_date) - daysUntilExpiry(b.expiry_date));

  const typeGroups = certTypes.map((t) => {
    const certs = certificates.filter((c) => c.document_type === t.document_type);
    const worst =
      certs.length > 0
        ? [...certs].sort(
            (a, b) => daysUntilExpiry(a.expiry_date) - daysUntilExpiry(b.expiry_date)
          )[0]
        : null;
    return { type: t, certs, worst };
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ShieldCheck className="h-6 w-6" />
            Certidões Negativas (CND)
          </h1>
          <p className="text-muted-foreground">
            Controle de validade e renovação de certidões
          </p>
        </div>
        <Button onClick={handleSync} disabled={syncing}>
          <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
          {syncing ? 'Sincronizando...' : 'Sincronizar'}
        </Button>
      </div>

      {/* Alert */}
      {(expiredCount > 0 || urgentCount > 0) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">Atenção! Há certidões que precisam de ação imediata</p>
            <p className="text-sm text-red-600 mt-1">
              {expiredCount > 0 && `${expiredCount} certidão(ões) vencida(s). `}
              {urgentCount > 0 && `${urgentCount} vence(m) em menos de 7 dias.`}
            </p>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-green-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Válidas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{validCount}</div>
          </CardContent>
        </Card>
        <Card className="border-yellow-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vencendo (30d)</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{expiringCount}</div>
          </CardContent>
        </Card>
        <Card className="border-red-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vencidas</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{expiredCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{certificates.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Type cards */}
      {typeGroups.length > 0 && (
        <div className="grid gap-3 md:grid-cols-3 lg:grid-cols-4">
          {typeGroups.map((g) => {
            const worst = g.worst;
            const cfg = worst ? getStatusConfig(worst) : null;
            const StatusIcon = cfg?.icon || CheckCircle;
            const days = worst ? daysUntilExpiry(worst.expiry_date) : null;
            return (
              <Card
                key={g.type.document_type}
                className={`cursor-pointer hover:shadow-md transition-shadow ${
                  filterType === g.type.document_type ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() =>
                  setFilterType(filterType === g.type.document_type ? 'all' : g.type.document_type)
                }
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-muted-foreground truncate">
                        {g.type.issuing_body}
                      </p>
                      <p className="text-sm font-semibold mt-0.5 truncate">{g.type.name}</p>
                    </div>
                    {cfg && (
                      <Badge className={`${cfg.color} text-xs ml-2 flex-shrink-0`}>
                        <StatusIcon className="h-3 w-3 mr-0.5" />
                        {g.certs.length}
                      </Badge>
                    )}
                    {g.certs.length === 0 && (
                      <Badge variant="outline" className="text-xs ml-2 flex-shrink-0">0</Badge>
                    )}
                  </div>
                  {worst && days !== null && (
                    <p className={`text-xs mt-2 ${getDaysColor(days)}`}>
                      {days <= 0 ? 'Vencida' : `${days} dia(s) restante(s)`}
                    </p>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-4 pb-3">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por nome, tipo ou órgão emissor..."
                className="pl-10"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType} aria-label="Filter Type">
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os tipos</SelectItem>
                {certTypes.map((t) => (
                  <SelectItem key={t.document_type} value={t.document_type}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus} aria-label="Filter Status">
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="valida">Válidas</SelectItem>
                <SelectItem value="vencendo">Vencendo</SelectItem>
                <SelectItem value="vencida">Vencidas</SelectItem>
              </SelectContent>
            </Select>
            {(filterType !== 'all' || filterStatus !== 'all' || search) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => { setFilterType('all'); setFilterStatus('all'); setSearch(''); }}
              >
                <Filter className="h-4 w-4 mr-1" /> Limpar
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {filtered.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <ShieldCheck className="h-12 w-12 mx-auto mb-3 opacity-40" />
              <p className="font-medium">Nenhuma certidão encontrada</p>
              <p className="text-sm mt-1">Ajuste os filtros ou sincronize as certidões</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium text-muted-foreground">Certidão</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Emissão</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Validade</th>
                    <th className="text-center p-3 font-medium text-muted-foreground">Dias</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Status</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((cert) => {
                    const cfg = getStatusConfig(cert);
                    const StatusIcon = cfg.icon;
                    const days = daysUntilExpiry(cert.expiry_date);
                    return (
                      <tr key={cert.id} className="border-b last:border-0 hover:bg-muted/50">
                        <td className="p-3">
                          <div>
                            <p className="font-medium">
                              {typeLabels[cert.document_type] || cert.name}
                            </p>
                            <p className="text-xs text-muted-foreground">{cert.issuing_body}</p>
                          </div>
                        </td>
                        <td className="p-3 text-muted-foreground">{formatDate(cert.issue_date)}</td>
                        <td className="p-3 text-muted-foreground">{formatDate(cert.expiry_date)}</td>
                        <td className="p-3 text-center">
                          <span className={getDaysColor(days)}>
                            {days <= 0 ? 'Vencida' : `${days}d`}
                          </span>
                        </td>
                        <td className="p-3">
                          <Badge className={`${cfg.color} text-xs`}>
                            <StatusIcon className="h-3 w-3 mr-1" />
                            {cfg.label}
                          </Badge>
                        </td>
                        <td className="p-3">
                          {cert.file_url && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7"
                              onClick={() => window.open(cert.file_url!, '_blank')}
                            >
                              <FileText className="h-3.5 w-3.5" />
                            </Button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
