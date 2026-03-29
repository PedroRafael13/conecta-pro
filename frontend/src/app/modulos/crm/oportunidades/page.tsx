'use client';

import { Target, Search, RefreshCw, Plus, MoreHorizontal, Eye, Edit, Trash2, AlertCircle, TrendingUp, DollarSign } from 'lucide-react';
import { useState } from 'react';
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
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ConfirmModal } from '@/components/ui/modal';
;
import {
  useOpportunities,
  useCreateOpportunity,
  useUpdateOpportunity,
  useDeleteOpportunity,
  usePipelineStats,
} from '@/hooks/crm';
import type { OpportunityResponse } from '@/types/generated/crm/models';
import { OportunidadeFormModal } from '@/components/crm/oportunidade-form-modal';
import { OportunidadeDetailModal } from '@/components/crm/oportunidade-detail-modal';
import { formatCurrency } from '@/lib/utils';

export default function OportunidadesPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'table' | 'kanban'>('kanban');
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const { data: oppData, isLoading, error, refetch } = useOpportunities({
    stage: statusFilter !== 'all' ? statusFilter : undefined,
    search: search || undefined,
    skip: page * pageSize,
    limit: pageSize,
  } as any);

  const { data: pipelineData } = usePipelineStats();

  const createMutation = useCreateOpportunity();
  const updateMutation = useUpdateOpportunity();
  const deleteMutation = useDeleteOpportunity();

  const [formOpen, setFormOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editItem, setEditItem] = useState<any | null>(null);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);

  // Confirm modal state
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{
    title: string;
    message: string;
    action: () => Promise<void>;
    variant: 'danger' | 'warning' | 'info';
  } | null>(null);

  const oportunidades = (oppData as any)?.items || (Array.isArray(oppData) ? oppData : []);
  const total = (oppData as any)?.total || oportunidades.length;

  const pipeline = pipelineData as any;
  const stats = {
    total,
    emNegociacao: pipeline?.by_stage?.negociacao || oportunidades.filter((o: any) => o.stage === 'negociacao').length,
    propostas: pipeline?.by_stage?.proposta || oportunidades.filter((o: any) => o.stage === 'proposta').length,
    valorPipeline: pipeline?.total_value || oportunidades.reduce((acc: number, o: any) => acc + (o.value || o.valor_estimado || 0), 0),
  };

  const openConfirm = (title: string, message: string, action: () => Promise<void>, variant: 'danger' | 'warning' | 'info' = 'warning') => {
    setConfirmAction({ title, message, action, variant });
    setConfirmOpen(true);
  };

  const handleCreate = async (data: any) => {
    await createMutation.mutateAsync({ data });
    setFormOpen(false);
  };

  const handleUpdate = async (data: any) => {
    if (!editItem) return;
    await updateMutation.mutateAsync({ opportunityId: editItem.id, data });
    setFormOpen(false);
    setEditItem(null);
  };

  const getStatusBadge = (status: string) => {
    const map: Record<string, string> = {
      qualificado: 'bg-blue-100 text-blue-800',
      proposta: 'bg-purple-100 text-purple-800',
      negociacao: 'bg-yellow-100 text-yellow-800',
      ganho: 'bg-green-100 text-green-800',
      perdido: 'bg-red-100 text-red-800',
    };
    const labels: Record<string, string> = {
      qualificado: 'Qualificado',
      proposta: 'Proposta',
      negociacao: 'Negociacao',
      ganho: 'Ganho',
      perdido: 'Perdido',
    };
    return <Badge className={map[status] || 'bg-gray-100 text-gray-800'}>{labels[status] || status}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Target className="h-6 w-6" />
            Oportunidades
          </h1>
          <p className="text-muted-foreground">Pipeline de oportunidades comerciais</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex border rounded-lg overflow-hidden">
            <button onClick={() => setViewMode('kanban')} className={`px-3 py-1.5 text-sm ${viewMode === 'kanban' ? 'bg-cyan-600 text-white' : 'bg-white'}`}>Kanban</button>
            <button onClick={() => setViewMode('table')} className={`px-3 py-1.5 text-sm ${viewMode === 'table' ? 'bg-cyan-600 text-white' : 'bg-white'}`}>Tabela</button>
          </div>
          <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button onClick={() => { setEditItem(null); setFormOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Oportunidade
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Em Negociacao</CardTitle>
            <TrendingUp className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.emNegociacao}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Propostas</CardTitle>
            <Target className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats.propostas}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Pipeline</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(stats.valorPipeline)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(0); }}
                placeholder="Buscar por nome, cliente..."
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(0); }}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os status</SelectItem>
                <SelectItem value="qualificado">Qualificado</SelectItem>
                <SelectItem value="proposta">Proposta</SelectItem>
                <SelectItem value="negociacao">Negociacao</SelectItem>
                <SelectItem value="ganho">Ganho</SelectItem>
                <SelectItem value="perdido">Perdido</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive flex-1">Erro ao carregar oportunidades</p>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : oportunidades.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Target className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium">Nenhuma oportunidade encontrada</h3>
              <p className="mt-2">Tente ajustar os filtros ou crie uma nova oportunidade</p>
              <Button className="mt-4" onClick={() => { setEditItem(null); setFormOpen(true); }}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Oportunidade
              </Button>
            </div>
          ) : viewMode === 'kanban' ? (
            /* === KANBAN VIEW === */
            <div className="flex gap-4 overflow-x-auto pb-4">
              {['qualification', 'needs_analysis', 'proposal', 'negotiation', 'closed_won', 'closed_lost'].map(stage => {
                const stageItems = oportunidades.filter((item: any) => item.stage === stage);
                const stageNames: Record<string, string> = { qualification: 'Qualificação', needs_analysis: 'Análise', proposal: 'Proposta', negotiation: 'Negociação', closed_won: 'Ganho', closed_lost: 'Perdido' };
                const stageColors: Record<string, string> = { qualification: 'border-blue-300 bg-blue-50', needs_analysis: 'border-cyan-300 bg-cyan-50', proposal: 'border-yellow-300 bg-yellow-50', negotiation: 'border-orange-300 bg-orange-50', closed_won: 'border-green-300 bg-green-50', closed_lost: 'border-red-300 bg-red-50' };
                return (
                  <div key={stage} className="min-w-[260px] flex-shrink-0">
                    <div className={`rounded-t-lg border-t-4 ${stageColors[stage]?.split(' ')[0] || 'border-gray-300'} p-2 bg-gray-50 font-semibold text-sm flex justify-between`}>
                      <span>{stageNames[stage] || stage}</span>
                      <span className="bg-white px-2 rounded-full text-xs">{stageItems.length}</span>
                    </div>
                    <div className={`space-y-2 p-2 min-h-[200px] rounded-b-lg ${stageColors[stage]?.split(' ')[1] || 'bg-gray-50'}`}>
                      {stageItems.map((item: any) => (
                        <div key={item.id} className="bg-white rounded-lg border p-3 shadow-sm hover:shadow-md transition-shadow cursor-pointer" onClick={() => { setSelectedItem(item); setDetailOpen(true); }}>
                          <p className="font-medium text-sm">{item.title}</p>
                          <p className="text-xs text-gray-500">{item.company_name || item.contact_name}</p>
                          <div className="flex justify-between mt-2">
                            <span className="text-green-600 font-semibold text-sm">R$ {item.value?.toLocaleString('pt-BR')}</span>
                            <span className="text-xs text-gray-400">{item.probability}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Estagio</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Probabilidade</TableHead>
                  <TableHead className="w-[80px]">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {oportunidades.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="font-medium">{item.title || item.nome || '-'}</div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{item.client_name || item.contato || '-'}</TableCell>
                    <TableCell>{getStatusBadge(item.stage || item.status || '')}</TableCell>
                    <TableCell className="text-sm font-medium">
                      {formatCurrency(item.value || item.valor_estimado || 0)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {item.probability != null ? `${item.probability}%` : '-'}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => { setSelectedItem(item); setDetailOpen(true); }}>
                            <Eye className="h-4 w-4 mr-2" />
                            Ver detalhes
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => { setEditItem(item); setFormOpen(true); }}>
                            <Edit className="h-4 w-4 mr-2" />
                            Editar
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() =>
                              openConfirm(
                                'Deletar Oportunidade',
                                `Deletar "${item.title || item.nome}" permanentemente?`,
                                () => deleteMutation.mutateAsync({ opportunityId: item.id }),
                                'danger'
                              )
                            }
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Deletar
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Mostrando {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} de {total}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * pageSize >= total}
            >
              Proximo
            </Button>
          </div>
        </div>
      )}

      {/* Modals */}
      <OportunidadeFormModal
        isOpen={formOpen}
        onClose={() => { setFormOpen(false); setEditItem(null); }}
        oportunidade={editItem}
        onSubmit={editItem ? handleUpdate : handleCreate}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />

      <OportunidadeDetailModal
        isOpen={detailOpen}
        onClose={() => { setDetailOpen(false); setSelectedItem(null); }}
        oportunidade={selectedItem}
      />

      {confirmAction && (
        <ConfirmModal
          isOpen={confirmOpen}
          onClose={() => setConfirmOpen(false)}
          onConfirm={async () => {
            await confirmAction.action();
            setConfirmOpen(false);
          }}
          title={confirmAction.title}
          message={confirmAction.message}
          variant={confirmAction.variant}
          isLoading={deleteMutation.isPending}
        />
      )}
    </div>
  );
}
