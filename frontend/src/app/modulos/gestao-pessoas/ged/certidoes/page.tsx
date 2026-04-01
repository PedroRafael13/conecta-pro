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
  ExternalLink,
  FileText,
  Clock,
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

const API_BASE = '/api/v1/bidding/certificates';

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  const el = document.createElement('div');
  el.className = `fixed top-4 right-4 z-[9999] px-4 py-3 rounded-lg shadow-lg text-sm font-medium text-white transition-opacity ${type === 'error' ? 'bg-red-500' : 'bg-emerald-500'}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

function getAuthHeaders() {
  const token =
    typeof window !== 'undefined'
      ? localStorage.getItem('access_token') || localStorage.getItem('token')
      : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Certificate {
  id: string;
  tipo: string;
  nome: string;
  cnpj: string;
  razao_social: string;
  status: string;
  situacao: string;
  data_emissao: string;
  data_validade: string;
  dias_para_vencer: number;
  esta_valida: boolean;
  esta_vencendo: boolean;
  precisa_renovar: boolean;
  pode_usar_licitacao: boolean;
  orgao_emissor: string;
  orgao_url?: string;
  arquivo_url?: string;
  codigo_verificacao?: string;
  ultima_tentativa?: string;
  fonte: string;
  obtencao_automatica: boolean;
}

interface CertType {
  tipo: string;
  nome: string;
  descricao: string;
  orgao_emissor: string;
  url_emissao: string;
  validade_padrao_dias: number;
  renovacao_automatica_disponivel: boolean;
  obrigatoria: boolean;
}

const typeLabels: Record<string, string> = {
  cnd_federal: 'CND Federal (PGFN/RFB)',
  cnd_trabalhista: 'CND Trabalhista (CNDT)',
  crf_fgts: 'CRF/FGTS (CEF)',
  cnd_municipal: 'CND Municipal (ISS)',
  cnd_estadual: 'CND Estadual (SEFAZ)',
  cnd_previdenciaria: 'CND Previdenciaria',
  ALVARA: 'Alvara de Funcionamento',
  AUTORIZACAO_PF: 'Autorizacao Policia Federal',
};

function getStatusConfig(cert: Certificate) {
  if (!cert.esta_valida && cert.dias_para_vencer <= 0) {
    return { label: 'Vencida', color: 'bg-red-100 text-red-800', icon: XCircle, priority: 0 };
  }
  if (cert.dias_para_vencer <= 7) {
    return { label: 'Critico', color: 'bg-red-100 text-red-800', icon: AlertTriangle, priority: 1 };
  }
  if (cert.dias_para_vencer <= 30) {
    return { label: 'Vencendo', color: 'bg-yellow-100 text-yellow-800', icon: AlertTriangle, priority: 2 };
  }
  return { label: 'Valida', color: 'bg-green-100 text-green-800', icon: CheckCircle, priority: 3 };
}

function getDaysColor(days: number) {
  if (days <= 0) return 'text-red-600 font-bold';
  if (days <= 7) return 'text-red-600 font-semibold';
  if (days <= 30) return 'text-yellow-600 font-semibold';
  return 'text-green-600';
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('pt-BR');
}

export default function CertidoesPage() {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [certTypes, setCertTypes] = useState<CertType[]>([]);
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
        setCertificates(Array.isArray(data) ? data : data.items || []);
      }
      if (typesRes.ok) {
        const data = await typesRes.json();
        setCertTypes(data.tipos || []);
      }
    } catch (err) {
      console.error('Erro ao carregar certidoes:', err);
      showToast('Erro ao carregar certidoes.', 'error');
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
      const res = await fetch(`${API_BASE}/atualizar-status`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        console.error('Erro ao atualizar status:', res.status);
        showToast('Erro ao sincronizar certidoes. Endpoint pode estar indisponivel.', 'error');
      }
      await loadData();
    } catch (err) {
      console.error('Erro ao sincronizar certidoes:', err);
      showToast('Erro de conexao ao sincronizar certidoes.', 'error');
    } finally {
      setSyncing(false);
    }
  };

  // Computed stats
  const validCount = certificates.filter((c) => c.esta_valida && c.dias_para_vencer > 30).length;
  const expiringCount = certificates.filter(
    (c) => c.esta_valida && c.dias_para_vencer > 0 && c.dias_para_vencer <= 30
  ).length;
  const expiredCount = certificates.filter((c) => !c.esta_valida || c.dias_para_vencer <= 0).length;
  const urgentCount = certificates.filter((c) => c.dias_para_vencer <= 7 && c.dias_para_vencer > 0).length;

  // Filter
  const filtered = certificates
    .filter((c) => {
      if (filterType !== 'all' && c.tipo !== filterType) return false;
      if (filterStatus === 'valida' && (!c.esta_valida || c.dias_para_vencer <= 30)) return false;
      if (filterStatus === 'vencendo' && (c.dias_para_vencer > 30 || c.dias_para_vencer <= 0)) return false;
      if (filterStatus === 'vencida' && c.dias_para_vencer > 0) return false;
      if (search) {
        const q = search.toLowerCase();
        return (
          (c.nome || '').toLowerCase().includes(q) ||
          (c.tipo || '').toLowerCase().includes(q) ||
          (c.razao_social || '').toLowerCase().includes(q) ||
          (c.orgao_emissor || '').toLowerCase().includes(q)
        );
      }
      return true;
    })
    .sort((a, b) => a.dias_para_vencer - b.dias_para_vencer);

  // Cards por tipo
  const typeGroups = certTypes.map((t) => {
    const certs = certificates.filter((c) => c.tipo === t.tipo);
    const worst = certs.length > 0 ? certs.sort((a, b) => a.dias_para_vencer - b.dias_para_vencer)[0] : null;
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
            Certidoes Negativas (CND)
          </h1>
          <p className="text-muted-foreground">
            Controle de validade e renovacao de certidoes
          </p>
        </div>
        <Button onClick={handleSync} disabled={syncing}>
          <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
          {syncing ? 'Sincronizando...' : 'Atualizar Status'}
        </Button>
      </div>

      {/* Alert */}
      {(expiredCount > 0 || urgentCount > 0) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">Atencao! Ha certidoes que precisam de acao imediata</p>
            <p className="text-sm text-red-600 mt-1">
              {expiredCount > 0 && `${expiredCount} certidao(oes) vencida(s). `}
              {urgentCount > 0 && `${urgentCount} vence(m) em menos de 7 dias.`}
            </p>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-green-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Validas</CardTitle>
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
            return (
              <Card
                key={g.type.tipo}
                className={`cursor-pointer hover:shadow-md transition-shadow ${
                  filterType === g.type.tipo ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => setFilterType(filterType === g.type.tipo ? 'all' : g.type.tipo)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-muted-foreground truncate">
                        {g.type.orgao_emissor}
                      </p>
                      <p className="text-sm font-semibold mt-0.5 truncate">{g.type.nome}</p>
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
                  {worst && (
                    <p className={`text-xs mt-2 ${getDaysColor(worst.dias_para_vencer)}`}>
                      {worst.dias_para_vencer <= 0
                        ? 'Vencida'
                        : `${worst.dias_para_vencer} dia(s) restante(s)`}
                    </p>
                  )}
                  {g.type.obrigatoria && (
                    <Badge variant="secondary" className="text-xs mt-1">Obrigatoria</Badge>
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
                placeholder="Buscar por nome, tipo, empresa ou orgao..."
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
                  <SelectItem key={t.tipo} value={t.tipo}>{t.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus} aria-label="Filter Status">
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="valida">Validas</SelectItem>
                <SelectItem value="vencendo">Vencendo</SelectItem>
                <SelectItem value="vencida">Vencidas</SelectItem>
              </SelectContent>
            </Select>
            {(filterType !== 'all' || filterStatus !== 'all' || search) && (
              <Button variant="ghost" size="sm" onClick={() => { setFilterType('all'); setFilterStatus('all'); setSearch(''); }}>
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
              <p className="font-medium">Nenhuma certidao encontrada</p>
              <p className="text-sm mt-1">Ajuste os filtros ou sincronize as certidoes</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium text-muted-foreground">Certidao</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Empresa</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Emissao</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Validade</th>
                    <th className="text-center p-3 font-medium text-muted-foreground">Dias</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Status</th>
                    <th className="text-left p-3 font-medium text-muted-foreground">Acoes</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((cert) => {
                    const cfg = getStatusConfig(cert);
                    const StatusIcon = cfg.icon;
                    return (
                      <tr key={cert.id} className="border-b last:border-0 hover:bg-muted/50">
                        <td className="p-3">
                          <div>
                            <p className="font-medium">{typeLabels[cert.tipo] || cert.nome}</p>
                            <p className="text-xs text-muted-foreground">{cert.orgao_emissor}</p>
                          </div>
                        </td>
                        <td className="p-3">
                          <div>
                            <p className="text-sm">{cert.razao_social}</p>
                            <p className="text-xs text-muted-foreground font-mono">
                              {cert.cnpj?.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')}
                            </p>
                          </div>
                        </td>
                        <td className="p-3 text-muted-foreground">{formatDate(cert.data_emissao)}</td>
                        <td className="p-3 text-muted-foreground">{formatDate(cert.data_validade)}</td>
                        <td className="p-3 text-center">
                          <span className={getDaysColor(cert.dias_para_vencer)}>
                            {cert.dias_para_vencer <= 0 ? 'Vencida' : `${cert.dias_para_vencer}d`}
                          </span>
                        </td>
                        <td className="p-3">
                          <Badge className={`${cfg.color} text-xs`}>
                            <StatusIcon className="h-3 w-3 mr-1" />
                            {cfg.label}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1">
                            {cert.arquivo_url && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => window.open(cert.arquivo_url, '_blank')}
                              >
                                <FileText className="h-3.5 w-3.5" />
                              </Button>
                            )}
                            {cert.orgao_url && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => window.open(cert.orgao_url, '_blank')}
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                              </Button>
                            )}
                          </div>
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
