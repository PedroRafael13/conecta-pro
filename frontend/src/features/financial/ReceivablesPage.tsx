'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Calendar,
  DollarSign,
  Building2,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  Eye,
  Edit,
  Send,
  FileText,
  ArrowUpRight,
  Mail,
  Phone,
  RefreshCw,
  Loader2,
  QrCode,
  Barcode,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
  Skeleton,
} from '@/design-system/components';

// Importações do módulo Financial
import {
  useReceivables,
  useReceivableStats,
  useReceivablesOverdue,
  useCreateReceivable,
  usePayReceivableInstallment,
  useCancelReceivable,
  useGenerateBoleto,
  useGeneratePix,
} from './hooks';
import type {
  ReceivableAccount,
  ReceivableAccountCreate,
  ReceivableFilter,
  ReceivableStatus,
  ReceivablePaymentCreate,
} from './types';
import { ReceivableStatus as ReceivableStatusEnum } from './types';

// ==================== CONSTANTS ====================

const STATUS_CONFIG: Record<string, { label: string; color: 'neutral' | 'warning' | 'success' | 'danger' | 'info'; icon: React.ElementType }> = {
  draft: { label: 'Rascunho', color: 'neutral', icon: FileText },
  pending: { label: 'A Receber', color: 'warning', icon: Clock },
  partially_paid: { label: 'Parcial', color: 'info', icon: DollarSign },
  paid: { label: 'Recebido', color: 'success', icon: CheckCircle2 },
  overdue: { label: 'Vencido', color: 'danger', icon: AlertTriangle },
  suspended: { label: 'Suspenso', color: 'neutral', icon: XCircle },
  protested: { label: 'Protestado', color: 'danger', icon: AlertTriangle },
  written_off: { label: 'Baixado', color: 'neutral', icon: XCircle },
  cancelled: { label: 'Cancelado', color: 'neutral', icon: XCircle },
};

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

// ==================== COMPONENT ====================

export function ReceivablesPage() {
  // State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [showNewModal, setShowNewModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedReceivable, setSelectedReceivable] = useState<ReceivableAccount | null>(null);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Form state
  const [newForm, setNewForm] = useState<Partial<ReceivableAccountCreate>>({});
  const [paymentForm, setPaymentForm] = useState<Partial<ReceivablePaymentCreate>>({
    payment_method: 'pix',
    payment_date: new Date().toISOString().split('T')[0],
  });

  // Construir filtros
  const filters: ReceivableFilter & { page: number; page_size: number } = useMemo(() => ({
    page,
    page_size: pageSize,
    status: selectedTab !== 'all' ? selectedTab as ReceivableStatus : undefined,
    search: searchTerm || undefined,
  }), [page, selectedTab, searchTerm]);

  // Hooks de dados
  const { data: receivablesData, isLoading, isError, error, refetch } = useReceivables(filters);
  const { data: stats, isLoading: isLoadingStats } = useReceivableStats();
  const { data: overdueList } = useReceivablesOverdue({ limit: 10 });
  const createMutation = useCreateReceivable();
  const payMutation = usePayReceivableInstallment();
  const cancelMutation = useCancelReceivable();
  const boletoMutation = useGenerateBoleto();
  const pixMutation = useGeneratePix();

  // Dados processados
  const receivables = receivablesData?.items || [];
  const totalReceivables = receivablesData?.total || 0;

  // Handlers
  const handleCreate = useCallback(async () => {
    if (!newForm.customer_id || !newForm.total_amount || !newForm.due_date) return;

    try {
      await createMutation.mutateAsync(newForm as ReceivableAccountCreate);
      setShowNewModal(false);
      setNewForm({});
    } catch (err) {
      console.error('Erro ao criar conta a receber:', err);
    }
  }, [newForm, createMutation]);

  const handlePayment = useCallback(async () => {
    if (!selectedReceivable || !paymentForm.amount) return;

    try {
      // Usando o primeiro installment como exemplo
      await payMutation.mutateAsync({
        id: selectedReceivable.id, // Seria o installment_id
        data: paymentForm as ReceivablePaymentCreate,
      });
      setShowPaymentModal(false);
      setSelectedReceivable(null);
      setPaymentForm({
        payment_method: 'pix',
        payment_date: new Date().toISOString().split('T')[0],
      });
    } catch (err) {
      console.error('Erro ao registrar pagamento:', err);
    }
  }, [selectedReceivable, paymentForm, payMutation]);

  const openDetail = (receivable: ReceivableAccount) => {
    setSelectedReceivable(receivable);
    setShowDetailModal(true);
  };

  const openPayment = (receivable: ReceivableAccount) => {
    setSelectedReceivable(receivable);
    setPaymentForm({
      ...paymentForm,
      amount: receivable.balance,
    });
    setShowPaymentModal(true);
  };

  // Colunas da tabela
  const columns: Column<ReceivableAccount>[] = [
    {
      key: 'document_number',
      header: 'Título',
      render: (row) => (
        <div>
          <p className="font-mono text-sm font-medium text-accent-primary">{row.document_number || row.id.slice(0, 8)}</p>
          <p className="text-xs text-text-muted">{row.reference || '-'}</p>
        </div>
      ),
    },
    {
      key: 'customer',
      header: 'Cliente',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.customer_name} size="sm" />
          <div>
            <p className="font-medium text-text-primary">{row.customer_name}</p>
            <p className="text-xs text-text-muted line-clamp-1">{row.description}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'total_amount',
      header: 'Valor',
      sortable: true,
      render: (row) => (
        <div>
          <span className="font-mono font-medium text-text-primary">
            {formatCurrency(row.total_amount)}
          </span>
          {row.paid_amount > 0 && row.paid_amount < row.total_amount && (
            <p className="text-xs text-success">Pago: {formatCurrency(row.paid_amount)}</p>
          )}
        </div>
      ),
    },
    {
      key: 'balance',
      header: 'Saldo',
      render: (row) => (
        <span className={`font-mono font-medium ${row.balance > 0 ? 'text-warning' : 'text-success'}`}>
          {formatCurrency(row.balance)}
        </span>
      ),
    },
    {
      key: 'due_date',
      header: 'Vencimento',
      sortable: true,
      render: (row) => {
        const isOverdue = row.is_overdue;
        return (
          <div className="flex items-center gap-2">
            <Calendar className={`w-4 h-4 ${isOverdue ? 'text-danger' : 'text-text-muted'}`} />
            <div>
              <span className={`text-sm ${isOverdue ? 'text-danger font-medium' : 'text-text-secondary'}`}>
                {formatDate(row.due_date)}
              </span>
              {isOverdue && row.days_overdue && (
                <p className="text-xs text-danger">{row.days_overdue} dias</p>
              )}
            </div>
          </div>
        );
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = STATUS_CONFIG[row.status] || STATUS_CONFIG.pending;
        const Icon = config.icon;
        return (
          <Badge variant={config.color} leftIcon={<Icon className="w-3 h-3" />}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            title="Visualizar"
            onClick={(e) => {
              e.stopPropagation();
              openDetail(row);
            }}
          >
            <Eye className="w-4 h-4" />
          </Button>
          {row.status === 'overdue' && (
            <Button variant="ghost" size="sm" title="Cobrar">
              <Send className="w-4 h-4" />
            </Button>
          )}
          {['pending', 'overdue', 'partially_paid'].includes(row.status) && (
            <Button
              variant="success"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                openPayment(row);
              }}
            >
              Baixar
            </Button>
          )}
        </div>
      ),
    },
  ];

  // Estatísticas calculadas
  const displayStats = useMemo(() => {
    return {
      totalPending: stats?.total_balance || 0,
      totalOverdue: stats?.overdue_amount || 0,
      totalReceived: stats?.total_paid || 0,
      overdueCount: stats?.overdue_count || 0,
      pendingCount: stats?.total_accounts || 0,
    };
  }, [stats]);

  // Loading state
  if (isLoading && !receivablesData) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
          </div>
          <Skeleton className="h-96" />
        </div>
      </MainLayout>
    );
  }

  // Error state
  if (isError) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center h-96 gap-4">
          <AlertTriangle className="h-16 w-16 text-accent-danger" />
          <h2 className="text-xl font-semibold">Erro ao carregar contas a receber</h2>
          <p className="text-text-secondary">{(error as Error)?.message}</p>
          <Button onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Tentar novamente
          </Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Contas a Receber
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie os recebimentos dos clientes
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Send className="w-4 h-4" />}>
              Cobrar Vencidos
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setShowNewModal(true)}
            >
              Novo Título
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="A Receber"
              value={isLoadingStats ? '...' : formatCurrency(displayStats.totalPending)}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Vencido"
              value={isLoadingStats ? '...' : formatCurrency(displayStats.totalOverdue)}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
              changeLabel={`${displayStats.overdueCount} títulos`}
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Recebido no Mês"
              value={isLoadingStats ? '...' : formatCurrency(displayStats.totalReceived)}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Total de Títulos"
              value={isLoadingStats ? '...' : displayStats.pendingCount.toString()}
              icon={<FileText className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todos (${totalReceivables})` },
                  { value: 'pending', label: 'A Receber' },
                  { value: 'overdue', label: 'Vencidos' },
                  { value: 'paid', label: 'Recebidos' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar títulos..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="ghost" size="sm" onClick={() => refetch()} disabled={isLoading}>
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Receivables Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={receivables}
                keyExtractor={(row) => row.id}
                onRowClick={openDetail}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Alert for overdue */}
        {displayStats.overdueCount > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card className="border-danger/30 bg-danger/5">
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-danger/10">
                    <AlertTriangle className="w-6 h-6 text-danger" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-text-primary">
                      Títulos vencidos precisam de cobrança
                    </p>
                    <p className="text-sm text-text-secondary mt-1">
                      {displayStats.overdueCount} título(s) vencido(s) totalizando{' '}
                      {formatCurrency(displayStats.totalOverdue)}
                    </p>
                  </div>
                  <Button variant="danger" size="sm" leftIcon={<Send className="w-4 h-4" />}>
                    Enviar Cobrança
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* New Receivable Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Novo Título a Receber"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Cliente *"
                placeholder="Nome do cliente"
                value={newForm.customer_id || ''}
                onChange={(e) => setNewForm(prev => ({ ...prev, customer_id: e.target.value }))}
              />
              <Input
                label="Unidade"
                placeholder="Código da unidade"
                value={newForm.unidade_id || ''}
                onChange={(e) => setNewForm(prev => ({ ...prev, unidade_id: e.target.value }))}
              />
            </div>
            <Input
              label="Descrição *"
              placeholder="Descrição do recebimento"
              value={newForm.description || ''}
              onChange={(e) => setNewForm(prev => ({ ...prev, description: e.target.value }))}
            />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Valor *"
                type="number"
                placeholder="0,00"
                leftIcon={<DollarSign className="w-4 h-4" />}
                value={newForm.total_amount?.toString() || ''}
                onChange={(e) => setNewForm(prev => ({ ...prev, total_amount: parseFloat(e.target.value) || 0 }))}
              />
              <Input
                label="Vencimento *"
                type="date"
                value={newForm.due_date || ''}
                onChange={(e) => setNewForm(prev => ({ ...prev, due_date: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Parcelas"
                type="number"
                placeholder="1"
                value={newForm.installments_count?.toString() || '1'}
                onChange={(e) => setNewForm(prev => ({ ...prev, installments_count: parseInt(e.target.value) || 1 }))}
              />
              <Input
                label="Referência"
                placeholder="Ex: Janeiro/2026"
                value={newForm.reference || ''}
                onChange={(e) => setNewForm(prev => ({ ...prev, reference: e.target.value }))}
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                leftIcon={createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                onClick={handleCreate}
                disabled={!newForm.customer_id || !newForm.total_amount || !newForm.due_date || createMutation.isPending}
              >
                {createMutation.isPending ? 'Criando...' : 'Cadastrar'}
              </Button>
            </div>
          </div>
        </Modal>

        {/* Payment Modal */}
        <Modal
          isOpen={showPaymentModal}
          onClose={() => setShowPaymentModal(false)}
          title="Registrar Pagamento"
          size="md"
        >
          {selectedReceivable && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-bg-tertiary">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedReceivable.customer_name} size="lg" />
                  <div>
                    <h4 className="font-medium text-text-primary">{selectedReceivable.customer_name}</h4>
                    <p className="text-sm text-text-muted">{selectedReceivable.description}</p>
                    <p className="text-lg font-bold text-success mt-1">
                      Saldo: {formatCurrency(selectedReceivable.balance)}
                    </p>
                  </div>
                </div>
              </div>

              <Input
                label="Valor do Pagamento *"
                type="number"
                leftIcon={<DollarSign className="w-4 h-4" />}
                value={paymentForm.amount?.toString() || ''}
                onChange={(e) => setPaymentForm(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
              />

              <Input
                label="Data do Pagamento *"
                type="date"
                value={paymentForm.payment_date || ''}
                onChange={(e) => setPaymentForm(prev => ({ ...prev, payment_date: e.target.value }))}
              />

              <Select
                label="Forma de Pagamento"
                options={[
                  { value: 'pix', label: 'PIX' },
                  { value: 'boleto', label: 'Boleto' },
                  { value: 'transferencia', label: 'Transferência' },
                  { value: 'deposito', label: 'Depósito' },
                  { value: 'cartao', label: 'Cartão' },
                  { value: 'dinheiro', label: 'Dinheiro' },
                ]}
                value={paymentForm.payment_method || 'pix'}
                onChange={(value) => setPaymentForm(prev => ({ ...prev, payment_method: value }))}
              />

              <Input
                label="Referência"
                placeholder="ID da transação, comprovante, etc."
                value={paymentForm.reference || ''}
                onChange={(e) => setPaymentForm(prev => ({ ...prev, reference: e.target.value }))}
              />

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="outline" onClick={() => setShowPaymentModal(false)}>
                  Cancelar
                </Button>
                <Button
                  variant="success"
                  leftIcon={payMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                  onClick={handlePayment}
                  disabled={!paymentForm.amount || payMutation.isPending}
                >
                  {payMutation.isPending ? 'Processando...' : 'Confirmar Pagamento'}
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes do Título"
          size="lg"
        >
          {selectedReceivable && (
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedReceivable.customer_name} size="lg" />
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedReceivable.customer_name}</h3>
                    <p className="text-sm text-text-secondary">{selectedReceivable.customer_document}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={STATUS_CONFIG[selectedReceivable.status]?.color || 'neutral'}>
                        {STATUS_CONFIG[selectedReceivable.status]?.label || selectedReceivable.status}
                      </Badge>
                      {selectedReceivable.is_recurring && (
                        <Badge variant="info">Recorrente</Badge>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-accent-primary">
                    {formatCurrency(selectedReceivable.total_amount)}
                  </p>
                  {selectedReceivable.balance > 0 && selectedReceivable.balance < selectedReceivable.total_amount && (
                    <p className="text-sm text-warning">Saldo: {formatCurrency(selectedReceivable.balance)}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-sm text-text-muted">Descrição</p>
                  <p className="font-medium text-text-primary">{selectedReceivable.description}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-sm text-text-muted">Referência</p>
                  <p className="font-medium text-text-primary">{selectedReceivable.reference || '-'}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-sm text-text-muted">Vencimento</p>
                  <p className={`font-medium ${selectedReceivable.is_overdue ? 'text-danger' : 'text-text-primary'}`}>
                    {formatDate(selectedReceivable.due_date)}
                    {selectedReceivable.is_overdue && selectedReceivable.days_overdue && (
                      <span className="text-sm ml-2">({selectedReceivable.days_overdue} dias atrasado)</span>
                    )}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-sm text-text-muted">Emissão</p>
                  <p className="font-medium text-text-primary">{formatDate(selectedReceivable.issue_date)}</p>
                </div>
              </div>

              {selectedReceivable.paid_amount > 0 && (
                <div className="p-4 rounded-lg bg-success/5 border border-success/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-success">Valor Pago</p>
                      <p className="text-xl font-bold text-success">{formatCurrency(selectedReceivable.paid_amount)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-text-muted">Parcelas Pagas</p>
                      <p className="font-medium text-text-primary">
                        {selectedReceivable.paid_installments_count} / {selectedReceivable.installments_count}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-border-default">
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    leftIcon={<Barcode className="w-4 h-4" />}
                    onClick={() => boletoMutation.mutate(selectedReceivable.id)}
                    disabled={boletoMutation.isPending}
                  >
                    Gerar Boleto
                  </Button>
                  <Button
                    variant="ghost"
                    leftIcon={<QrCode className="w-4 h-4" />}
                    onClick={() => pixMutation.mutate(selectedReceivable.id)}
                    disabled={pixMutation.isPending}
                  >
                    Gerar PIX
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  {['pending', 'overdue', 'partially_paid'].includes(selectedReceivable.status) && (
                    <Button
                      variant="success"
                      leftIcon={<CheckCircle2 className="w-4 h-4" />}
                      onClick={() => {
                        setShowDetailModal(false);
                        openPayment(selectedReceivable);
                      }}
                    >
                      Registrar Pagamento
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
