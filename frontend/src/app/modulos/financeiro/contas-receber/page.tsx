'use client';

import { TrendingUp, Search, RefreshCw, Plus, MoreHorizontal, Eye, Edit, DollarSign, Trash2, AlertCircle, Clock, CheckCircle } from 'lucide-react';
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
import { useCondominio } from '@/contexts/CondominioContext';
import {
  useReceivables,
  useReceivableDashboard,
  useCreateReceivable,
} from '@/hooks/financial/useFinancial';
import { ReceivableFormModal } from '@/components/financeiro/receivable-form-modal';
import { ReceivableDetailModal } from '@/components/financeiro/receivable-detail-modal';
import type { ReceivableAccountListResponse } from '@/types/generated/financial/models/receivableAccountListResponse';
import type { ReceivableAccountCreate } from '@/types/generated/financial/models/receivableAccountCreate';

const formatCurrency = (value: number | null | undefined) =>
  (value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

const formatDate = (date: string | null | undefined) => {
  if (!date) return '-';
  try {
    return new Date(date).toLocaleDateString('pt-BR');
  } catch {
    return date;
  }
};

const getStatusBadge = (status?: string | null) => {
  switch (status) {
    case 'pending':
      return <Badge className="bg-yellow-100 text-yellow-800">Pendente</Badge>;
    case 'overdue':
      return <Badge className="bg-red-100 text-red-800">Atrasada</Badge>;
    case 'paid':
      return <Badge className="bg-green-100 text-green-800">Recebida</Badge>;
    case 'cancelled':
      return <Badge variant="secondary">Cancelada</Badge>;
    default:
      return <Badge variant="outline">{status || '-'}</Badge>;
  }
};

export default function ContasReceberPage() {
  const { condominioId } = useCondominio();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [customerFilter, setCustomerFilter] = useState('');
  const [skip, setSkip] = useState(0);
  const limit = 50;

  // Modals state
  const [formModalOpen, setFormModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [receiveModalOpen, setReceiveModalOpen] = useState(false);
  const [selectedReceivable, setSelectedReceivable] = useState<any>(null);

  // Data hooks
  const {
    data: receivablesData,
    isLoading: loading,
    error: queryError,
    refetch,
  } = useReceivables({
    condominio_id: condominioId,
    skip,
    limit,
    ...(search ? { search } : {}),
    ...(statusFilter !== 'all' ? { status: statusFilter } : {}),
  });

  const { data: dashboard } = useReceivableDashboard();
  const { mutateAsync: createReceivable, isPending: creating } = useCreateReceivable();

  const receivables: ReceivableAccountListResponse[] = Array.isArray(receivablesData)
    ? (receivablesData as ReceivableAccountListResponse[])
    : ((receivablesData as { data?: ReceivableAccountListResponse[] })?.data ?? []);

  // Filter locally by customer if set
  const filteredReceivables = receivables.filter((item: any) => {
    if (!customerFilter) return true;
    return (item.customer_name || '').toLowerCase().includes(customerFilter.toLowerCase());
  });

  const handleCreate = () => {
    setSelectedReceivable(null);
    setFormModalOpen(true);
  };

  const handleEdit = (receivable: any) => {
    setSelectedReceivable(receivable);
    setFormModalOpen(true);
  };

  const handleViewDetail = (receivable: any) => {
    setSelectedReceivable(receivable);
    setDetailModalOpen(true);
  };

  const handleDeleteConfirm = (receivable: any) => {
    setSelectedReceivable(receivable);
    setDeleteModalOpen(true);
  };

  const handleReceiveConfirm = (receivable: any) => {
    setSelectedReceivable(receivable);
    setReceiveModalOpen(true);
  };

  const handleFormSubmit = async (data: ReceivableAccountCreate) => {
    try {
      await createReceivable({ data });
      setFormModalOpen(false);
      setSelectedReceivable(null);
    } catch (err) {
      void err;
    }
  };

  const handleDelete = async () => {
    setDeleteModalOpen(false);
    setSelectedReceivable(null);
  };

  const handleReceive = async () => {
    setReceiveModalOpen(false);
    setSelectedReceivable(null);
  };

  type ReceivableStats = { total_count?: number; overdue_count?: number };
  const dashboardTyped = dashboard as ReceivableStats | undefined;
  const stats = {
    total: dashboardTyped?.total_count ?? 0,
    due_today: 0,
    overdue: dashboardTyped?.overdue_count ?? 0,
    received: 0,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            Contas a Receber
          </h1>
          <p className="text-muted-foreground">
            Gerencie todas as contas a receber e recebimentos pendentes
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button onClick={handleCreate}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Conta
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vencendo Hoje</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.due_today}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Atrasadas</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recebidas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.received}</div>
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
                onChange={(e) => {
                  setSearch(e.target.value);
                  setSkip(0);
                }}
                placeholder="Buscar por descricao, cliente..."
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setSkip(0); }}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os status</SelectItem>
                <SelectItem value="pending">Pendente</SelectItem>
                <SelectItem value="overdue">Atrasada</SelectItem>
                <SelectItem value="paid">Recebida</SelectItem>
                <SelectItem value="cancelled">Cancelada</SelectItem>
              </SelectContent>
            </Select>
            <div className="relative">
              <Input
                value={customerFilter}
                onChange={(e) => setCustomerFilter(e.target.value)}
                placeholder="Filtrar cliente..."
                className="w-[200px]"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error */}
      {queryError && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <div className="flex-1">
            <p className="text-sm text-destructive">{String(queryError)}</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : filteredReceivables.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <TrendingUp className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium">Nenhuma conta a receber encontrada</h3>
              <p className="mt-2">Tente ajustar os filtros ou crie uma nova conta</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Descricao</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Vencimento</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[80px]">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReceivables.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="font-medium">{item.description || '-'}</div>
                    </TableCell>
                    <TableCell>{item.customer_name || '-'}</TableCell>
                    <TableCell className="font-mono">
                      {formatCurrency(item.amount)}
                    </TableCell>
                    <TableCell>{formatDate(item.due_date)}</TableCell>
                    <TableCell>{getStatusBadge(item.status)}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleViewDetail(item)}>
                            <Eye className="h-4 w-4 mr-2" />
                            Ver detalhes
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleEdit(item)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Editar
                          </DropdownMenuItem>
                          {(item.status === 'pending' || item.status === 'overdue') && (
                            <DropdownMenuItem onClick={() => handleReceiveConfirm(item)}>
                              <DollarSign className="h-4 w-4 mr-2" />
                              Registrar Recebimento
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => handleDeleteConfirm(item)}
                            className="text-destructive focus:text-destructive"
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
      {filteredReceivables.length >= limit && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSkip(Math.max(0, skip - limit))}
            disabled={skip === 0}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSkip(skip + limit)}
          >
            Proximo
          </Button>
        </div>
      )}

      {/* Modals */}
      <ReceivableFormModal
        isOpen={formModalOpen}
        onClose={() => { setFormModalOpen(false); setSelectedReceivable(null); }}
        receivable={selectedReceivable}
        onSubmit={handleFormSubmit}
        isLoading={creating}
      />

      <ReceivableDetailModal
        isOpen={detailModalOpen}
        onClose={() => { setDetailModalOpen(false); setSelectedReceivable(null); }}
        receivable={selectedReceivable}
      />

      <ConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => { setDeleteModalOpen(false); setSelectedReceivable(null); }}
        onConfirm={handleDelete}
        title="Cancelar Conta a Receber"
        message={`Tem certeza que deseja cancelar a conta "${selectedReceivable?.description}"? Esta acao nao pode ser desfeita.`}
        confirmText="Cancelar Conta"
        variant="danger"
      />

      <ConfirmModal
        isOpen={receiveModalOpen}
        onClose={() => { setReceiveModalOpen(false); setSelectedReceivable(null); }}
        onConfirm={handleReceive}
        title="Registrar Recebimento"
        message={`Confirmar o recebimento de ${formatCurrency(selectedReceivable?.amount)} referente a "${selectedReceivable?.description}"?`}
        confirmText="Confirmar Recebimento"
        variant="info"
      />
    </div>
  );
}
