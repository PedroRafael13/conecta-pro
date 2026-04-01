'use client';

import { Eye, Search, RefreshCw, MoreHorizontal, AlertCircle, Shield, FileText, User, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
;
import { useLGPDAuditLogs, useAuditActions, useResourceTypes } from '@/hooks/security-lgpd';
import { AuditDetailModal } from '@/components/seguranca/audit-detail-modal';

const PAGE_SIZE = 20;

/** Shape dos dados internos retornados em StandardResponse.data para audit logs */
interface AuditLogsData {
  logs?: unknown[];
  total?: number;
  [key: string]: unknown;
}

// Labels de acao
const ACTION_LABELS: Record<string, string> = {
  data_access: 'Acesso a Dados',
  data_modification: 'Modificacao de Dados',
  data_deletion: 'Exclusao de Dados',
  data_export: 'Exportacao de Dados',
  security_incident: 'Incidente de Seguranca',
};

// Cores dos badges de acao
const ACTION_BADGE_COLORS: Record<string, string> = {
  data_access: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  data_modification: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  data_deletion: 'bg-red-500/10 text-red-500 border-red-500/20',
  data_export: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  security_incident: 'bg-red-500/10 text-red-500 border-red-500/20',
};

// Labels de recurso
const RESOURCE_LABELS: Record<string, string> = {
  user: 'Usuario',
  customer: 'Cliente',
  employee: 'Colaborador',
  document: 'Documento',
};

;

export default function AuditoriaLGPDPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAction, setSelectedAction] = useState<string>('all');
  const [selectedResource, setSelectedResource] = useState<string>('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [page, setPage] = useState(1);

  // Modal state
  const [selectedLog, setSelectedLog] = useState<any>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Query params
  const [queryParams, setQueryParams] = useState<any>({
    limit: PAGE_SIZE,
    skip: 0,
  });

  // Hooks de dados
  const { data: logsResponse, isLoading, refetch } = useLGPDAuditLogs(queryParams);
  const { data: actionsResponse } = useAuditActions();
  const { data: resourceTypesResponse } = useResourceTypes();

  // Extrair dados - cast data para shape esperado
  const responseData = logsResponse?.data as AuditLogsData | undefined;
  const logs = responseData?.logs || (Array.isArray(responseData) ? responseData : []);
  const items = Array.isArray(logs) ? logs : [];
  const total = responseData?.total || items.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  // Debounce para filtros

  useEffect(() => {
    const timer = setTimeout(() => {
      const params: any = {
        limit: PAGE_SIZE,
        skip: (page - 1) * PAGE_SIZE,
      };

      if (searchTerm) params.search = searchTerm;
      if (selectedAction && selectedAction !== 'all') params.action = selectedAction;
      if (selectedResource && selectedResource !== 'all') params.resource_type = selectedResource;
      if (startDate) params.start_date = new Date(startDate).toISOString();
      if (endDate) params.end_date = new Date(endDate).toISOString();


      setQueryParams(params);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm, selectedAction, selectedResource, startDate, endDate, page]);


  // Reset pagina ao alterar filtros
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Form sync
    setPage(1);
  }, [searchTerm, selectedAction, selectedResource, startDate, endDate]);

  const handleView = (log: any) => {
    setSelectedLog(log);
    setShowDetailModal(true);
  };

  const handleRefresh = () => {
    refetch();
  };

  const formatDateTime = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getActionBadge = (action: string) => {
    const colorClass = ACTION_BADGE_COLORS[action] || 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    const label = ACTION_LABELS[action] || action;
    return (
      <span
        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${colorClass}`}
      >
        {label}
      </span>
    );
  };

  const truncateText = (text: string, maxLength: number = 60) => {
    if (!text) return '-';
    if (typeof text === 'object') {
      const str = JSON.stringify(text);
      return str.length > maxLength ? str.substring(0, maxLength) + '...' : str;
    }
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Eye className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                  Auditoria LGPD
                </h1>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">
                  {total} registros
                </p>
              </div>
            </div>
            <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filters */}
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <Input
                placeholder="Buscar por usuario, recurso, detalhes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Action filter */}
            <div className="w-full lg:w-48">
              <Select value={selectedAction} onValueChange={setSelectedAction}>
                <SelectTrigger>
                  <SelectValue placeholder="Acao" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas as Acoes</SelectItem>
                  <SelectItem value="data_access">Acesso a Dados</SelectItem>
                  <SelectItem value="data_modification">Modificacao de Dados</SelectItem>
                  <SelectItem value="data_deletion">Exclusao de Dados</SelectItem>
                  <SelectItem value="data_export">Exportacao de Dados</SelectItem>
                  <SelectItem value="security_incident">Incidente de Seguranca</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Resource filter */}
            <div className="w-full lg:w-48">
              <Select value={selectedResource} onValueChange={setSelectedResource}>
                <SelectTrigger>
                  <SelectValue placeholder="Recurso" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os Recursos</SelectItem>
                  <SelectItem value="user">Usuario</SelectItem>
                  <SelectItem value="customer">Cliente</SelectItem>
                  <SelectItem value="employee">Colaborador</SelectItem>
                  <SelectItem value="document">Documento</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Date range */}
          <div className="flex flex-col sm:flex-row gap-4 mt-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-[hsl(var(--muted-foreground))] whitespace-nowrap">
                De:
              </span>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-44"
              />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-[hsl(var(--muted-foreground))] whitespace-nowrap">
                Ate:
              </span>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-44"
              />
            </div>
            {(startDate || endDate || selectedAction !== 'all' || selectedResource !== 'all' || searchTerm) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchTerm('');
                  setSelectedAction('all');
                  setSelectedResource('all');
                  setStartDate('');
                  setEndDate('');
                }}
              >
                Limpar filtros
              </Button>
            )}
          </div>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-pulse-slow text-[hsl(var(--primary))]">
              <Shield className="w-8 h-8" />
            </div>
          </div>
        )}

        {/* Table */}
        {!isLoading && (
          <>
            <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]">
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Data/Hora
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Acao
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Recurso
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Usuario
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Detalhes
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Acoes
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[hsl(var(--border))]">
                    {items.map((log: any) => (
                      <tr
                        key={log.id}
                        className="hover:bg-[hsl(var(--muted))]/50 transition-colors"
                      >
                        <td className="px-4 py-3">
                          <span className="text-sm text-[hsl(var(--foreground))] whitespace-nowrap">
                            {formatDateTime(log.timestamp || log.created_at)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {getActionBadge(log.action)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                            <span className="text-sm text-[hsl(var(--foreground))]">
                              {RESOURCE_LABELS[log.resource_type] || log.resource_type || '-'}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                            <span className="text-sm text-[hsl(var(--foreground))]">
                              {log.user_name || log.user_id || '-'}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">
                            {truncateText(
                              typeof log.details === 'object'
                                ? JSON.stringify(log.details)
                                : log.details || '-'
                            )}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-end">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm">
                                  <MoreHorizontal className="w-4 h-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => handleView(log)}>
                                  <Eye className="w-4 h-4 mr-2" />
                                  Ver detalhes
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Empty state */}
            {items.length === 0 && (
              <div className="text-center py-12 bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl mt-4">
                <Shield className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhum registro de auditoria encontrado
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1">
                  Ajuste os filtros ou aguarde novos eventos
                </p>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  Mostrando {(page - 1) * PAGE_SIZE + 1} a{' '}
                  {Math.min(page * PAGE_SIZE, total)} de {total} registros
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-sm text-[hsl(var(--foreground))]">
                    Pagina {page} de {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page >= totalPages}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Detail Modal */}
      <AuditDetailModal
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedLog(null);
        }}
        log={selectedLog}
      />
    </div>
  );
}
