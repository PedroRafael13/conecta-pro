'use client';

import { useState } from 'react';
import {
  Search, RefreshCw, AlertCircle, Award, Eye,
  CheckCircle, Clock, XCircle, Filter, Shield,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { CertidaoDetailModal } from '@/components/fiscal/certidao-detail-modal';
import { useListarCertificados, useListarAlertasCertificados } from '@/hooks/government';
import { cn } from '@/lib/utils';

const statusConfig: Record<string, { label: string; color: string }> = {
  valida: { label: 'Valida', color: 'bg-green-100 text-green-800' },
  vencendo: { label: 'Vencendo', color: 'bg-yellow-100 text-yellow-800' },
  vencida: { label: 'Vencida', color: 'bg-red-100 text-red-800' },
  pendente: { label: 'Pendente', color: 'bg-blue-100 text-blue-800' },
};

function getStatusFromDates(certidao: any): string {
  if (certidao.status) return certidao.status;
  if (!certidao.data_validade) return 'pendente';

  const validade = new Date(certidao.data_validade);
  const hoje = new Date();
  const diasRestantes = Math.ceil(
    (validade.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24)
  );

  if (diasRestantes < 0) return 'vencida';
  if (diasRestantes <= 30) return 'vencendo';
  return 'valida';
}

export default function CertidoesPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [page, setPage] = useState(1);
  const [selectedCertidao, setSelectedCertidao] = useState<any | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const {
    data: certificadosData,
    isLoading,
    isError,
    error,
    refetch,
  } = useListarCertificados();

  const { data: alertasData } = useListarAlertasCertificados();

  const certidoesList = Array.isArray(certificadosData)
    ? certificadosData
    : (certificadosData as any)?.items || [];

  // Enrich certidoes with computed status
  const enrichedList = certidoesList.map((c: any) => ({
    ...c,
    _status: getStatusFromDates(c),
  }));

  // Apply filters
  const filteredList = enrichedList.filter((c: any) => {
    const matchSearch = search
      ? (c.tipo || '').toLowerCase().includes(search.toLowerCase()) ||
        (c.orgao || '').toLowerCase().includes(search.toLowerCase()) ||
        (c.numero || '').toLowerCase().includes(search.toLowerCase())
      : true;
    const matchStatus = statusFilter ? c._status === statusFilter : true;
    return matchSearch && matchStatus;
  });

  const totalCertidoes = enrichedList.length;
  const validas = enrichedList.filter((c: any) => c._status === 'valida').length;
  const vencendoOuVencidas = enrichedList.filter(
    (c: any) => c._status === 'vencendo' || c._status === 'vencida'
  ).length;

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">Certidoes</h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Gestao de certidoes e certificados digitais
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          </Button>
        </div>
      </div>

      {/* Alertas */}
      {alertasData && Array.isArray(alertasData) && alertasData.length > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-yellow-500" />
            <span className="font-medium text-yellow-500">
              Alertas de Certificados ({alertasData.length})
            </span>
          </div>
          <div className="space-y-1">
            {alertasData.slice(0, 3).map((alerta: any, i: number) => (
              <p key={i} className="text-sm text-[hsl(var(--foreground))]">
                {alerta.mensagem || alerta.message || `Certificado ${alerta.tipo || ''} requer atencao`}
              </p>
            ))}
            {alertasData.length > 3 && (
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                E mais {alertasData.length - 3} alertas...
              </p>
            )}
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Total</p>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {isLoading ? '...' : totalCertidoes}
                </p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Award className="w-5 h-5 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Validas</p>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {isLoading ? '...' : validas}
                </p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Vencendo / Vencidas</p>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {isLoading ? '...' : vencendoOuVencidas}
                </p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                <XCircle className="w-5 h-5 text-red-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            type="search"
            placeholder="Buscar por tipo, orgao ou numero..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            icon={<Search className="w-4 h-4" />}
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={statusFilter === undefined ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setStatusFilter(undefined)}
          >
            Todos
          </Button>
          <Button
            variant={statusFilter === 'valida' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setStatusFilter('valida')}
          >
            Valida
          </Button>
          <Button
            variant={statusFilter === 'vencendo' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setStatusFilter('vencendo')}
          >
            Vencendo
          </Button>
          <Button
            variant={statusFilter === 'vencida' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setStatusFilter('vencida')}
          >
            Vencida
          </Button>
        </div>
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/30">
          <AlertCircle className="w-5 h-5 text-[hsl(var(--destructive))]" />
          <div>
            <p className="font-medium text-[hsl(var(--destructive))]">Erro ao carregar certidoes</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {(error as Error)?.message || 'Tente novamente em alguns instantes'}
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => refetch()} className="ml-auto">
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="divide-y divide-[hsl(var(--border))]">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="p-4 flex items-center gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-48 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                    <div className="h-3 w-32 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                  </div>
                  <div className="h-6 w-20 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[hsl(var(--border))]">
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Tipo
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                      Orgao
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden lg:table-cell">
                      Numero
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                      Emissao
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Validade
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Status
                    </th>
                    <th className="w-16 p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Acoes
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[hsl(var(--border))]">
                  {filteredList.map((certidao: any) => {
                    const st = statusConfig[certidao._status] || statusConfig.pendente || { label: 'Pendente', color: 'bg-blue-100 text-blue-800' };
                    return (
                      <tr
                        key={certidao.id || certidao.numero}
                        className="hover:bg-[hsl(var(--secondary))]/50 transition-colors"
                      >
                        <td className="p-4">
                          <p className="font-medium text-[hsl(var(--foreground))]">
                            {certidao.tipo || '-'}
                          </p>
                        </td>
                        <td className="p-4 hidden md:table-cell">
                          <span className="text-sm text-[hsl(var(--foreground))]">
                            {certidao.orgao || '-'}
                          </span>
                        </td>
                        <td className="p-4 hidden lg:table-cell">
                          <span className="text-sm font-mono text-[hsl(var(--muted-foreground))]">
                            {certidao.numero || '-'}
                          </span>
                        </td>
                        <td className="p-4 hidden md:table-cell">
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">
                            {formatDate(certidao.data_emissao)}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className="text-sm text-[hsl(var(--foreground))]">
                            {formatDate(certidao.data_validade)}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className={cn('inline-flex px-2 py-1 text-xs font-medium rounded-full', st.color)}>
                            {st.label}
                          </span>
                        </td>
                        <td className="p-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedCertidao(certidao);
                              setShowDetailModal(true);
                            }}
                            title="Ver detalhes"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !isError && filteredList.length === 0 && (
            <div className="text-center py-12">
              <Shield className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
              <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                Nenhuma certidao encontrada
              </h3>
              <p className="text-[hsl(var(--muted-foreground))] mt-1">
                {search || statusFilter
                  ? 'Tente ajustar os filtros'
                  : 'Nenhuma certidao ou certificado registrado'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination info */}
      {!isLoading && filteredList.length > 0 && (
        <div className="text-sm text-[hsl(var(--muted-foreground))] text-center">
          Mostrando {filteredList.length} de {totalCertidoes} certidoes
        </div>
      )}

      {/* Detail Modal */}
      <CertidaoDetailModal
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedCertidao(null);
        }}
        certidao={selectedCertidao}
      />
    </div>
  );
}
