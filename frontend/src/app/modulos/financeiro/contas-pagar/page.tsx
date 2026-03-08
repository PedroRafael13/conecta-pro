'use client';

import { TrendingDown, Search, RefreshCw, Plus, MoreHorizontal, Eye, Edit, DollarSign, Trash2, AlertCircle, Clock, CheckCircle } from 'lucide-react';
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
import {
  usePayables,
  usePayableDashboard,
  useCreatePayable,
  useUpdatePayable,
  useProcessPayment,
} from '@/hooks/financial/useFinancial';
import { PayableFormModal } from '@/components/financeiro/payable-form-modal';
import { PayableDetailModal } from '@/components/financeiro/payable-detail-modal';
import type { PayableAccountListResponse } from '@/types/generated/financial/models/payableAccountListResponse';
import type { PayableAccountStats } from '@/types/generated/financial/models/payableAccountStats';
import type { PayableAccountCreate } from '@/types/generated/financial/models/payableAccountCreate';
import type { PayableAccountUpdate } from '@/types/generated/financial/models/payableAccountUpdate';

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
      return <Badge className="bg-green-100 text-green-800">Paga</Badge>;
    case 'cancelled':
      return <Badge variant="secondary">Cancelada</Badge>;
    default:
      return <Badge variant="outline">{status || '-'}</Badge>;
  }
};

export default function ContasPagarPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [supplierFilter, setSupplierFilter] = useState('');
  const [skip, setSkip] = useState(0);
  const limit = 50;

  // Modals state
  const [formModalOpen, setFormModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [selectedPayable, setSelectedPayable] = useState<any>(null);

  // Data hooks
  const {
    data: payablesData,
    isLoading: loading,
    error: queryError,
    refetch,
  } = usePayables({
    condominio_id: '',
    skip,
    limit,
    ...(search ? { search } : {}),
    ...(statusFilter !== 'all' ? { status: statusFilter } : {}),
  });

  const { data: dashboard } = usePayableDashboard();
  const { mutateAsync: createPayable, isPending: creating } = useCreatePayable();
  const { mutateAsync: updatePayable, isPending: updating } = useUpdatePayable();
  const { mutateAsync: processPayment, isPending: processing } = useProcessPayment();

  const payables: PayableAccountListResponse[] = Array.isArray(payablesData)
    ? (payablesData as PayableAccountListResponse[])
    : ((payablesData as { data?: PayableAccountListResponse[] })?.data ?? []);

  // Filter locally by supplier if set
  const filteredPayables = payables.filter((item: any) => {
    if (!supplierFilter) return true;
    return (item.supplier_name || '').toLowerCase().includes(supplierFilter.toLowerCase());
  });

  const handleCreate = () => {
    setSelectedPayable(null);
    setFormModalOpen(true);
  };

  const handleEdit = (payable: any) => {
    setSelectedPayable(payable);
    setFormModalOpen(true);
  };

  const handleViewDetail = (payable: any) => {
    setSelectedPayable(payable);
    setDetailModalOpen(true);
  };

  const handleDeleteConfirm = (payable: any) => {
    setSelectedPayable(payable);
    setDeleteModalOpen(true);
  };

  const handlePaymentConfirm = (payable: any) => {
    setSelectedPayable(payable);
    setPaymentModalOpen(true);
  };

  const handleFormSubmit = async (data: PayableAccountCreate | PayableAccountUpdate) => {
    try {
      if (selectedPayable?.id) {
        await updatePayable({ accountId: selectedPayable.id, data: data as PayableAccountUpdate });
      } else {
        await createPayable({ data: data as PayableAccountCreate });
      }
      setFormModalOpen(false);
      setSelectedPayable(null);
    } catch (err) {
      console.error('Erro ao salvar conta a pagar:', err);
    }
  };

  const handleDelete = async () => {
    if (!selectedPayable?.id) return;
    try {
      const cancelUpdate: PayableAccountUpdate = { notes: 'Cancelado' };
      await updatePayable({ accountId: selectedPayable.id, data: cancelUpdate });
      setDeleteModalOpen(false);
      setSelectedPayable(null);
    } catch (err) {
      console.error('Erro ao cancelar conta:', err);
    }
  };

  const handlePayment = async () => {
    if (!selectedPayable?.id) return;
    try {
      await processPayment({ installmentId: selectedPayable.id, data: { installment_id: selectedPayable.id, paid_value: parseFloat(selectedPayable?.balance ?? selectedPayable?.net_value ?? '0'), payment_date: new Date().toISOString().split('T')[0] ?? '' } });
      setPaymentModalOpen(false);
      setSelectedPayable(null);
      // refetch() removido - mutations já invalidam queries automaticamente
    } catch (err) {
      console.error('Erro ao registrar pagamento:', err);
    }
  };

  const dashboardTyped = dashboard as PayableAccountStats | undefined;
  const stats = {
    total: dashboardTyped?.total_count ?? 0,
    due_today: 0,
    overdue: dashboardTyped?.overdue_count ?? 0,
    paid: 0,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <TrendingDown className="h-6 w-6" />
            Contas a Pagar
          </h1>
          <p className="text-muted-foreground">
            Gerencie todas as contas a pagar e pagamentos pendentes
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
            <CardTitle className="text-sm font-medium">Pagas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.paid}</div>
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
                placeholder="Buscar por descricao, fornecedor..."
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
                <SelectItem value="paid">Paga</SelectItem>
                <SelectItem value="cancelled">Cancelada</SelectItem>
              </SelectContent>
            </Select>
            <div className="relative">
              <Input
                value={supplierFilter}
                onChange={(e) => setSupplierFilter(e.target.value)}
                placeholder="Filtrar fornecedor..."
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
          ) : filteredPayables.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <TrendingDown className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium">Nenhuma conta a pagar encontrada</h3>
              <p className="mt-2">Tente ajustar os filtros ou crie uma nova conta</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Descricao</TableHead>
                  <TableHead>Fornecedor</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Vencimento</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[80px]">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredPayables.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="font-medium">{item.description || '-'}</div>
                    </TableCell>
                    <TableCell>{item.supplier_name || '-'}</TableCell>
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
                            <DropdownMenuItem onClick={() => handlePaymentConfirm(item)}>
                              <DollarSign className="h-4 w-4 mr-2" />
                              Registrar Pagamento
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
      {filteredPayables.length >= limit && (
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
      <PayableFormModal
        isOpen={formModalOpen}
        onClose={() => { setFormModalOpen(false); setSelectedPayable(null); }}
        payable={selectedPayable}
        onSubmit={handleFormSubmit}
        isLoading={creating || updating}
      />

      <PayableDetailModal
        isOpen={detailModalOpen}
        onClose={() => { setDetailModalOpen(false); setSelectedPayable(null); }}
        payable={selectedPayable}
      />

      <ConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => { setDeleteModalOpen(false); setSelectedPayable(null); }}
        onConfirm={handleDelete}
        title="Cancelar Conta a Pagar"
        message={`Tem certeza que deseja cancelar a conta "${selectedPayable?.description}"? Esta acao nao pode ser desfeita.`}
        confirmText="Cancelar Conta"
        variant="danger"
        isLoading={updating}
      />

      <ConfirmModal
        isOpen={paymentModalOpen}
        onClose={() => { setPaymentModalOpen(false); setSelectedPayable(null); }}
        onConfirm={handlePayment}
        title="Registrar Pagamento"
        message={`Confirmar o pagamento de ${formatCurrency(selectedPayable?.amount)} referente a "${selectedPayable?.description}"?`}
        confirmText="Confirmar Pagamento"
        variant="info"
        isLoading={processing}
      />
    </div>
  );
}
