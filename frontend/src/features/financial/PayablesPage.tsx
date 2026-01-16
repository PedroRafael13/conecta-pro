'use client';

import { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Calendar,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  Edit,
  CreditCard,
  Loader2,
  RefreshCw,
  Building2,
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

// Types & Hooks
import type { PayableAccount, PayableAccountCreate, PayablePaymentCreate, PayableScheduleRequest } from './types';
import { PayableStatus } from './types';
import {
  usePayables,
  usePayableStats,
  useCreatePayable,
  usePayPayableInstallment,
  useSchedulePayable,
  useBankAccounts,
  useSuppliers,
} from './hooks';

// Status configuration
const statusConfig: Record<string, { label: string; color: 'warning' | 'danger' | 'success' | 'info' | 'neutral'; icon: typeof Clock }> = {
  draft: { label: 'Rascunho', color: 'neutral', icon: Clock },
  pending: { label: 'Pendente', color: 'warning', icon: Clock },
  approved: { label: 'Aprovado', color: 'info', icon: CheckCircle2 },
  scheduled: { label: 'Agendado', color: 'info', icon: Calendar },
  partially_paid: { label: 'Parcial', color: 'warning', icon: Clock },
  paid: { label: 'Pago', color: 'success', icon: CheckCircle2 },
  overdue: { label: 'Vencido', color: 'danger', icon: AlertTriangle },
  cancelled: { label: 'Cancelado', color: 'neutral', icon: XCircle },
};

// Initial form state
const initialFormState: Partial<PayableAccountCreate> = {
  supplier_id: '',
  category_id: '',
  description: '',
  reference: '',
  total_amount: 0,
  due_date: '',
  notes: '',
};

// Initial payment state
const initialPaymentState: Partial<PayablePaymentCreate> = {
  amount: 0,
  payment_date: new Date().toISOString().split('T')[0],
  payment_method: '',
  bank_account_id: '',
  notes: '',
};

// Initial schedule state
const initialScheduleState: Partial<PayableScheduleRequest> = {
  scheduled_date: '',
  bank_account_id: '',
  notes: '',
};

export function PayablesPage() {
  // State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedPayable, setSelectedPayable] = useState<PayableAccount | null>(null);
  const [formData, setFormData] = useState(initialFormState);
  const [paymentData, setPaymentData] = useState(initialPaymentState);
  const [scheduleData, setScheduleData] = useState(initialScheduleState);

  // Queries
  const statusFilter = selectedTab !== 'all' ? selectedTab as PayableStatus : undefined;
  const { data: payablesData, isLoading, error, refetch } = usePayables({
    status: statusFilter,
    search: searchTerm || undefined,
  });
  const { data: statsData, isLoading: isLoadingStats } = usePayableStats();
  const { data: bankAccountsData } = useBankAccounts();
  const { data: suppliersData } = useSuppliers();

  // Mutations
  const createPayable = useCreatePayable();
  const payInstallment = usePayPayableInstallment();
  const schedulePayable = useSchedulePayable();

  // Handlers
  const handleCreatePayable = useCallback(async () => {
    if (!formData.supplier_id || !formData.description || !formData.total_amount || !formData.due_date) return;

    try {
      await createPayable.mutateAsync(formData as PayableAccountCreate);
      setIsCreateModalOpen(false);
      setFormData(initialFormState);
    } catch (err) {
      console.error('Erro ao criar conta:', err);
    }
  }, [formData, createPayable]);

  const handlePayment = useCallback(async () => {
    if (!selectedPayable || !paymentData.amount || !paymentData.payment_method) return;

    try {
      await payInstallment.mutateAsync({
        id: selectedPayable.id,
        data: paymentData as PayablePaymentCreate,
      });
      setIsPaymentModalOpen(false);
      setSelectedPayable(null);
      setPaymentData(initialPaymentState);
    } catch (err) {
      console.error('Erro ao registrar pagamento:', err);
    }
  }, [selectedPayable, paymentData, payInstallment]);

  const handleSchedule = useCallback(async () => {
    if (!selectedPayable || !scheduleData.scheduled_date || !scheduleData.bank_account_id) return;

    try {
      await schedulePayable.mutateAsync({
        id: selectedPayable.id,
        data: scheduleData as PayableScheduleRequest,
      });
      setIsScheduleModalOpen(false);
      setSelectedPayable(null);
      setScheduleData(initialScheduleState);
    } catch (err) {
      console.error('Erro ao agendar pagamento:', err);
    }
  }, [selectedPayable, scheduleData, schedulePayable]);

  const openPaymentModal = useCallback((payable: PayableAccount) => {
    setSelectedPayable(payable);
    setPaymentData({
      ...initialPaymentState,
      amount: payable.balance,
    });
    setIsPaymentModalOpen(true);
  }, []);

  const openScheduleModal = useCallback((payable: PayableAccount) => {
    setSelectedPayable(payable);
    setScheduleData(initialScheduleState);
    setIsScheduleModalOpen(true);
  }, []);

  const openDetailModal = useCallback((payable: PayableAccount) => {
    setSelectedPayable(payable);
    setIsDetailModalOpen(true);
  }, []);

  // Memoized data
  const payables = useMemo(() => payablesData?.items || [], [payablesData]);
  const stats = useMemo(() => statsData || {
    total_accounts: 0,
    total_amount: 0,
    total_paid: 0,
    total_balance: 0,
    overdue_count: 0,
    overdue_amount: 0,
    scheduled_count: 0,
    scheduled_amount: 0,
  }, [statsData]);

  const bankAccounts = useMemo(() => bankAccountsData?.items || [], [bankAccountsData]);
  const suppliers = useMemo(() => suppliersData?.items || [], [suppliersData]);

  // Status counts
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { all: 0 };
    payables.forEach(p => {
      counts.all++;
      counts[p.status] = (counts[p.status] || 0) + 1;
    });
    return counts;
  }, [payables]);

  // Table columns
  const columns: Column<PayableAccount>[] = useMemo(() => [
    {
      key: 'document_number',
      header: 'Título',
      render: (row) => (
        <div>
          <p className="font-mono text-sm font-medium text-accent-primary">
            {row.document_number || row.id.slice(0, 8).toUpperCase()}
          </p>
          <p className="text-xs text-text-muted">{row.category_name || 'Sem categoria'}</p>
        </div>
      ),
    },
    {
      key: 'supplier_name',
      header: 'Fornecedor',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.supplier_name} size="sm" />
          <div>
            <p className="font-medium text-text-primary">{row.supplier_name}</p>
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
          <span className="font-mono font-medium text-danger">
            {row.total_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </span>
          {row.installments_count > 1 && (
            <p className="text-xs text-text-muted mt-0.5">
              Parcela {row.paid_installments_count + 1}/{row.installments_count}
            </p>
          )}
        </div>
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
            <span className={`text-sm ${isOverdue ? 'text-danger font-medium' : 'text-text-secondary'}`}>
              {new Date(row.due_date).toLocaleDateString('pt-BR')}
            </span>
          </div>
        );
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = statusConfig[row.status] || statusConfig.pending;
        const Icon = config.icon;
        return (
          <Badge variant={config.color} leftIcon={<Icon className="w-3 h-3" />}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      key: 'scheduled_date',
      header: 'Agendamento',
      render: (row) => (
        row.scheduled_date ? (
          <div className="flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-text-muted" />
            <span className="text-sm text-text-secondary">
              {new Date(row.scheduled_date).toLocaleDateString('pt-BR')}
            </span>
          </div>
        ) : (
          <span className="text-sm text-text-muted">-</span>
        )
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            title="Visualizar"
            onClick={(e) => {
              e.stopPropagation();
              openDetailModal(row);
            }}
          >
            <Eye className="w-4 h-4" />
          </Button>
          {(row.status === 'pending' || row.status === 'approved') && (
            <>
              <Button
                variant="ghost"
                size="icon-sm"
                title="Agendar"
                onClick={(e) => {
                  e.stopPropagation();
                  openScheduleModal(row);
                }}
              >
                <Calendar className="w-4 h-4" />
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  openPaymentModal(row);
                }}
              >
                Pagar
              </Button>
            </>
          )}
          {row.status === 'overdue' && (
            <Button
              variant="danger"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                openPaymentModal(row);
              }}
            >
              Regularizar
            </Button>
          )}
        </div>
      ),
    },
  ], [openDetailModal, openPaymentModal, openScheduleModal]);

  // Loading state
  if (isLoading) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-64 mt-2" />
            </div>
            <div className="flex gap-3">
              <Skeleton className="h-10 w-24" />
              <Skeleton className="h-10 w-24" />
              <Skeleton className="h-10 w-32" />
            </div>
          </div>
          <StatGrid columns={4}>
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </StatGrid>
          <Skeleton className="h-96" />
        </div>
      </MainLayout>
    );
  }

  // Error state
  if (error) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-12">
          <AlertTriangle className="w-12 h-12 text-danger mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Erro ao carregar dados</h2>
          <p className="text-text-secondary mb-4">Não foi possível carregar as contas a pagar.</p>
          <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />} onClick={() => refetch()}>
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
              Contas a Pagar
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie suas obrigações financeiras
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Upload className="w-4 h-4" />}>
              Importar
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Nova Conta
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Pendente"
              value={isLoadingStats ? '-' : stats.total_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Vencido"
              value={isLoadingStats ? '-' : stats.overdue_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
              changeLabel={`${stats.overdue_count} títulos`}
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Agendado"
              value={isLoadingStats ? '-' : (stats.scheduled_amount || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="info"
              changeLabel={`${stats.scheduled_count || 0} títulos`}
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Pago no Mês"
              value={isLoadingStats ? '-' : stats.total_paid.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todas (${statusCounts.all || 0})` },
                  { value: 'pending', label: `Pendentes (${statusCounts.pending || 0})` },
                  { value: 'overdue', label: `Vencidas (${statusCounts.overdue || 0})` },
                  { value: 'scheduled', label: `Agendadas (${statusCounts.scheduled || 0})` },
                  { value: 'paid', label: `Pagas (${statusCounts.paid || 0})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar contas..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Payables Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={payables}
                keyExtractor={(row) => row.id}
                onRowClick={openDetailModal}
                emptyState={{ title: "Nenhuma conta a pagar encontrada" }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Alert for overdue */}
        {stats.overdue_count > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card className="border-danger/30 bg-danger/5">
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-danger/10">
                    <AlertTriangle className="w-6 h-6 text-danger" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-text-primary">
                      Você possui contas vencidas
                    </p>
                    <p className="text-sm text-text-secondary mt-1">
                      {stats.overdue_count} título(s) vencido(s) totalizando{' '}
                      {stats.overdue_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                  </div>
                  <Button variant="danger" size="sm">
                    Regularizar Agora
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* New Payable Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Nova Conta a Pagar"
          description="Cadastre uma nova obrigação"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                onClick={handleCreatePayable}
                disabled={createPayable.isPending || !formData.supplier_id || !formData.description || !formData.total_amount}
                leftIcon={createPayable.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
              >
                {createPayable.isPending ? 'Criando...' : 'Cadastrar'}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Fornecedor"
              options={suppliers.map(s => ({ value: s.id, label: s.name }))}
              value={formData.supplier_id || ''}
              onChange={(value) => setFormData(prev => ({ ...prev, supplier_id: value }))}
              placeholder="Selecione o fornecedor..."
              required
            />
            <Input
              label="Descrição"
              placeholder="Descrição do pagamento"
              value={formData.description || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              required
            />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Valor"
                type="number"
                placeholder="0,00"
                leftIcon={<span className="text-text-muted">R$</span>}
                value={formData.total_amount || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, total_amount: parseFloat(e.target.value) || 0 }))}
                required
              />
              <Input
                label="Vencimento"
                type="date"
                value={formData.due_date || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
                required
              />
            </div>
            <Input
              label="Referência"
              placeholder="Número da nota, contrato, etc."
              value={formData.reference || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, reference: e.target.value }))}
            />
            <Input
              label="Observações"
              placeholder="Observações adicionais"
              value={formData.notes || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
            />
          </div>
        </Modal>

        {/* Payment Modal */}
        <Modal
          isOpen={isPaymentModalOpen}
          onClose={() => setIsPaymentModalOpen(false)}
          title="Registrar Pagamento"
          description={selectedPayable ? `Pagamento para ${selectedPayable.supplier_name}` : ''}
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsPaymentModalOpen(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                onClick={handlePayment}
                disabled={payInstallment.isPending || !paymentData.amount || !paymentData.payment_method}
                leftIcon={payInstallment.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
              >
                {payInstallment.isPending ? 'Processando...' : 'Confirmar Pagamento'}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            {selectedPayable && (
              <div className="p-4 bg-bg-secondary rounded-lg">
                <p className="text-sm text-text-muted">Valor em aberto</p>
                <p className="text-2xl font-bold text-text-primary">
                  {selectedPayable.balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
              </div>
            )}
            <Input
              label="Valor do Pagamento"
              type="number"
              placeholder="0,00"
              leftIcon={<span className="text-text-muted">R$</span>}
              value={paymentData.amount || ''}
              onChange={(e) => setPaymentData(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
              required
            />
            <Input
              label="Data do Pagamento"
              type="date"
              value={paymentData.payment_date || ''}
              onChange={(e) => setPaymentData(prev => ({ ...prev, payment_date: e.target.value }))}
              required
            />
            <Select
              label="Forma de Pagamento"
              options={[
                { value: 'boleto', label: 'Boleto' },
                { value: 'transferencia', label: 'Transferência' },
                { value: 'pix', label: 'PIX' },
                { value: 'debito', label: 'Débito Automático' },
                { value: 'darf', label: 'DARF' },
              ]}
              value={paymentData.payment_method || ''}
              onChange={(value) => setPaymentData(prev => ({ ...prev, payment_method: value }))}
              placeholder="Selecione..."
              required
            />
            <Select
              label="Conta Bancária"
              options={bankAccounts.map(acc => ({
                value: acc.id,
                label: `${acc.bank_name} - ${acc.account_number}`,
              }))}
              value={paymentData.bank_account_id || ''}
              onChange={(value) => setPaymentData(prev => ({ ...prev, bank_account_id: value }))}
              placeholder="Selecione..."
            />
          </div>
        </Modal>

        {/* Schedule Modal */}
        <Modal
          isOpen={isScheduleModalOpen}
          onClose={() => setIsScheduleModalOpen(false)}
          title="Agendar Pagamento"
          description={selectedPayable ? `Agendamento para ${selectedPayable.supplier_name}` : ''}
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsScheduleModalOpen(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                onClick={handleSchedule}
                disabled={schedulePayable.isPending || !scheduleData.scheduled_date || !scheduleData.bank_account_id}
                leftIcon={schedulePayable.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
              >
                {schedulePayable.isPending ? 'Agendando...' : 'Confirmar Agendamento'}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            {selectedPayable && (
              <div className="p-4 bg-bg-secondary rounded-lg">
                <p className="text-sm text-text-muted">Valor a pagar</p>
                <p className="text-2xl font-bold text-text-primary">
                  {selectedPayable.balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                <p className="text-sm text-text-muted mt-1">
                  Vencimento: {new Date(selectedPayable.due_date).toLocaleDateString('pt-BR')}
                </p>
              </div>
            )}
            <Input
              label="Data do Agendamento"
              type="date"
              value={scheduleData.scheduled_date || ''}
              onChange={(e) => setScheduleData(prev => ({ ...prev, scheduled_date: e.target.value }))}
              required
            />
            <Select
              label="Conta Bancária"
              options={bankAccounts.map(acc => ({
                value: acc.id,
                label: `${acc.bank_name} - ${acc.account_number}`,
              }))}
              value={scheduleData.bank_account_id || ''}
              onChange={(value) => setScheduleData(prev => ({ ...prev, bank_account_id: value }))}
              placeholder="Selecione a conta..."
              required
            />
            <Input
              label="Observações"
              placeholder="Observações do agendamento"
              value={scheduleData.notes || ''}
              onChange={(e) => setScheduleData(prev => ({ ...prev, notes: e.target.value }))}
            />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={isDetailModalOpen}
          onClose={() => setIsDetailModalOpen(false)}
          title="Detalhes da Conta"
          size="lg"
          footer={
            <Button variant="secondary" onClick={() => setIsDetailModalOpen(false)}>
              Fechar
            </Button>
          }
        >
          {selectedPayable && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start gap-4">
                <Avatar name={selectedPayable.supplier_name} size="lg" />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-text-primary">{selectedPayable.supplier_name}</h3>
                  <p className="text-text-secondary">{selectedPayable.description}</p>
                  {selectedPayable.supplier_document && (
                    <p className="text-sm text-text-muted mt-1">CNPJ/CPF: {selectedPayable.supplier_document}</p>
                  )}
                </div>
                <Badge variant={statusConfig[selectedPayable.status]?.color || 'neutral'}>
                  {statusConfig[selectedPayable.status]?.label || selectedPayable.status}
                </Badge>
              </div>

              {/* Values */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-bg-secondary rounded-lg">
                  <p className="text-sm text-text-muted">Valor Total</p>
                  <p className="text-xl font-bold text-text-primary">
                    {selectedPayable.total_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                </div>
                <div className="p-4 bg-bg-secondary rounded-lg">
                  <p className="text-sm text-text-muted">Valor Pago</p>
                  <p className="text-xl font-bold text-success">
                    {selectedPayable.paid_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                </div>
                <div className="p-4 bg-bg-secondary rounded-lg">
                  <p className="text-sm text-text-muted">Saldo</p>
                  <p className="text-xl font-bold text-danger">
                    {selectedPayable.balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                </div>
              </div>

              {/* Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-muted">Vencimento</p>
                  <p className="text-text-primary">{new Date(selectedPayable.due_date).toLocaleDateString('pt-BR')}</p>
                </div>
                <div>
                  <p className="text-sm text-text-muted">Emissão</p>
                  <p className="text-text-primary">{new Date(selectedPayable.issue_date).toLocaleDateString('pt-BR')}</p>
                </div>
                {selectedPayable.document_number && (
                  <div>
                    <p className="text-sm text-text-muted">Nº Documento</p>
                    <p className="text-text-primary">{selectedPayable.document_number}</p>
                  </div>
                )}
                {selectedPayable.invoice_number && (
                  <div>
                    <p className="text-sm text-text-muted">Nº Nota Fiscal</p>
                    <p className="text-text-primary">{selectedPayable.invoice_number}</p>
                  </div>
                )}
                {selectedPayable.category_name && (
                  <div>
                    <p className="text-sm text-text-muted">Categoria</p>
                    <p className="text-text-primary">{selectedPayable.category_name}</p>
                  </div>
                )}
                {selectedPayable.scheduled_date && (
                  <div>
                    <p className="text-sm text-text-muted">Agendado para</p>
                    <p className="text-text-primary">{new Date(selectedPayable.scheduled_date).toLocaleDateString('pt-BR')}</p>
                  </div>
                )}
              </div>

              {/* Notes */}
              {selectedPayable.notes && (
                <div>
                  <p className="text-sm text-text-muted mb-1">Observações</p>
                  <p className="text-text-secondary">{selectedPayable.notes}</p>
                </div>
              )}

              {/* Actions */}
              {(selectedPayable.status === 'pending' || selectedPayable.status === 'approved' || selectedPayable.status === 'overdue') && (
                <div className="flex gap-3 pt-4 border-t border-border">
                  <Button
                    variant="secondary"
                    leftIcon={<Calendar className="w-4 h-4" />}
                    onClick={() => {
                      setIsDetailModalOpen(false);
                      openScheduleModal(selectedPayable);
                    }}
                  >
                    Agendar
                  </Button>
                  <Button
                    variant="primary"
                    leftIcon={<CreditCard className="w-4 h-4" />}
                    onClick={() => {
                      setIsDetailModalOpen(false);
                      openPaymentModal(selectedPayable);
                    }}
                  >
                    Registrar Pagamento
                  </Button>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
