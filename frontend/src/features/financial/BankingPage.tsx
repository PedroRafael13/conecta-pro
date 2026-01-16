'use client';

import { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  RefreshCw,
  Download,
  Building2,
  CreditCard,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Eye,
  Link2,
  DollarSign,
  TrendingUp,
  Loader2,
  ArrowRightLeft,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
  Skeleton,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Types & Hooks
import type { BankAccount, BankTransaction, BankAccountCreate, TransferRequest } from './types';
import { BankAccountType, BankAccountStatus, TransactionType, TransactionStatus } from './types';
import {
  useBankAccounts,
  useBankAccountStats,
  useBankTransactions,
  useBankTransactionSummary,
  usePendingReconciliation,
  useCreateBankAccount,
  useBankTransfer,
  useReconcileBankTransaction,
} from './hooks';

// Type configs
const accountTypeConfig: Record<string, { label: string; color: 'primary' | 'success' | 'warning' }> = {
  checking: { label: 'Conta Corrente', color: 'primary' },
  savings: { label: 'Poupança', color: 'success' },
  investment: { label: 'Investimento', color: 'warning' },
  petty_cash: { label: 'Caixa Pequeno', color: 'primary' },
};

const transactionStatusConfig: Record<string, { label: string; color: 'success' | 'warning' | 'neutral' }> = {
  pending: { label: 'Pendente', color: 'warning' },
  confirmed: { label: 'Confirmado', color: 'success' },
  reconciled: { label: 'Conciliado', color: 'success' },
  cancelled: { label: 'Cancelado', color: 'neutral' },
};

// Initial form state
const initialAccountForm: Partial<BankAccountCreate> = {
  bank_code: '',
  bank_name: '',
  agency: '',
  account_number: '',
  account_type: BankAccountType.CHECKING,
  description: '',
  initial_balance: 0,
};

const initialTransferForm: Partial<TransferRequest> = {
  from_account_id: '',
  to_account_id: '',
  amount: 0,
  description: '',
};

// Bank Account Card Component
function BankAccountCard({ account, onClick }: { account: BankAccount; onClick?: () => void }) {
  const typeConfig = accountTypeConfig[account.account_type] || accountTypeConfig.checking;
  const isMain = account.is_main;

  return (
    <Card
      className={`hover:border-accent-primary/50 transition-colors cursor-pointer ${isMain ? 'border-accent-primary/30 bg-accent-primary/5' : ''}`}
      onClick={onClick}
    >
      <CardBody>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-bg-tertiary rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-accent-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className="font-medium text-text-primary">{account.description || account.bank_name}</p>
                {isMain && (
                  <Badge variant="primary" size="sm">Principal</Badge>
                )}
              </div>
              <p className="text-sm text-text-muted">
                Ag: {account.agency} | Cc: {account.account_number}
              </p>
            </div>
          </div>
          <Badge variant={typeConfig.color} size="sm">
            {typeConfig.label}
          </Badge>
        </div>

        <div className="mb-4">
          <p className="text-xs text-text-muted mb-1">Saldo Atual</p>
          <p className="text-2xl font-mono font-bold text-text-primary">
            {account.current_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </p>
          {account.blocked_balance > 0 && (
            <p className="text-xs text-text-muted mt-1">
              Bloqueado: {account.blocked_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            </p>
          )}
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
          <div className="flex items-center gap-2 text-xs text-text-muted">
            {account.last_reconciled_at ? (
              <>
                <CheckCircle2 className="w-3 h-3 text-success" />
                <span>
                  Conciliado em {new Date(account.last_reconciled_at).toLocaleDateString('pt-BR')}
                </span>
              </>
            ) : (
              <>
                <Clock className="w-3 h-3" />
                <span>Não conciliado</span>
              </>
            )}
          </div>
          <Button variant="ghost" size="sm">
            <Eye className="w-4 h-4" />
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}

export function BankingPage() {
  // State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isAccountModalOpen, setIsAccountModalOpen] = useState(false);
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);
  const [accountForm, setAccountForm] = useState(initialAccountForm);
  const [transferForm, setTransferForm] = useState(initialTransferForm);

  // Queries
  const { data: accountsData, isLoading: isLoadingAccounts, error: accountsError, refetch: refetchAccounts } = useBankAccounts();
  const { data: statsData, isLoading: isLoadingStats } = useBankAccountStats();
  const { data: transactionsData, isLoading: isLoadingTransactions, refetch: refetchTransactions } = useBankTransactions({
    account_id: selectedAccount !== 'all' ? selectedAccount : undefined,
  });
  const { data: summaryData } = useBankTransactionSummary();
  const { data: pendingData } = usePendingReconciliation();

  // Mutations
  const createAccount = useCreateBankAccount();
  const transfer = useBankTransfer();
  const reconcile = useReconcileBankTransaction();

  // Handlers
  const handleCreateAccount = useCallback(async () => {
    if (!accountForm.bank_name || !accountForm.agency || !accountForm.account_number) return;

    try {
      await createAccount.mutateAsync(accountForm as BankAccountCreate);
      setIsAccountModalOpen(false);
      setAccountForm(initialAccountForm);
    } catch (err) {
      console.error('Erro ao criar conta:', err);
    }
  }, [accountForm, createAccount]);

  const handleTransfer = useCallback(async () => {
    if (!transferForm.from_account_id || !transferForm.to_account_id || !transferForm.amount) return;

    try {
      await transfer.mutateAsync(transferForm as TransferRequest);
      setIsTransferModalOpen(false);
      setTransferForm(initialTransferForm);
    } catch (err) {
      console.error('Erro na transferência:', err);
    }
  }, [transferForm, transfer]);

  const handleReconcile = useCallback(async (transactionId: string) => {
    try {
      await reconcile.mutateAsync({ id: transactionId });
    } catch (err) {
      console.error('Erro ao conciliar:', err);
    }
  }, [reconcile]);

  // Memoized data
  const accounts = useMemo(() => accountsData?.items || [], [accountsData]);
  const transactions = useMemo(() => transactionsData?.items || [], [transactionsData]);
  const stats = useMemo(() => statsData || {
    total_accounts: 0,
    total_balance: 0,
    total_available: 0,
    total_blocked: 0,
  }, [statsData]);
  const summary = useMemo(() => summaryData || {
    total_credits: 0,
    total_debits: 0,
    net: 0,
  }, [summaryData]);
  const pendingCount = useMemo(() => pendingData?.length || 0, [pendingData]);

  // Filtered transactions
  const filteredTransactions = useMemo(() => {
    return transactions.filter(t => {
      const matchesSearch = t.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.reference?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTab =
        selectedTab === 'all' ||
        (selectedTab === 'pending' && t.status === TransactionStatus.PENDING) ||
        (selectedTab === 'reconciled' && t.status === TransactionStatus.RECONCILED);
      return matchesSearch && matchesTab;
    });
  }, [transactions, searchTerm, selectedTab]);

  // Balance history (mock for now - could be fetched from API)
  const balanceHistory = useMemo(() => {
    const today = new Date();
    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(today);
      date.setDate(date.getDate() - (6 - i));
      return {
        date: date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
        balance: stats.total_balance * (0.9 + Math.random() * 0.2),
      };
    });
  }, [stats.total_balance]);

  // Transaction columns
  const transactionColumns: Column<BankTransaction>[] = useMemo(() => [
    {
      key: 'transaction_date',
      header: 'Data',
      render: (row) => (
        <span className="text-sm text-text-secondary">
          {new Date(row.transaction_date).toLocaleDateString('pt-BR')}
        </span>
      ),
    },
    {
      key: 'description',
      header: 'Descrição',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${row.transaction_type === TransactionType.CREDIT || row.transaction_type === TransactionType.TRANSFER_IN ? 'bg-success/10' : 'bg-danger/10'}`}>
            {row.transaction_type === TransactionType.CREDIT || row.transaction_type === TransactionType.TRANSFER_IN ? (
              <ArrowUpRight className="w-4 h-4 text-success" />
            ) : (
              <ArrowDownRight className="w-4 h-4 text-danger" />
            )}
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.description}</p>
            {row.category_name && (
              <p className="text-xs text-text-muted">{row.category_name}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'amount',
      header: 'Valor',
      render: (row) => {
        const isCredit = row.transaction_type === TransactionType.CREDIT || row.transaction_type === TransactionType.TRANSFER_IN;
        return (
          <span className={`font-mono font-medium ${isCredit ? 'text-success' : 'text-danger'}`}>
            {isCredit ? '+' : '-'}
            {Math.abs(row.amount).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </span>
        );
      },
    },
    {
      key: 'balance_after',
      header: 'Saldo',
      render: (row) => (
        <span className="font-mono text-text-primary">
          {(row.balance_after || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = transactionStatusConfig[row.status] || transactionStatusConfig.pending;
        return (
          <div className="flex items-center gap-2">
            <Badge
              variant={config.color}
              size="sm"
              leftIcon={row.status === TransactionStatus.RECONCILED ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
            >
              {config.label}
            </Badge>
            {row.reconciled_with_id && (
              <Badge variant="secondary" size="sm" leftIcon={<Link2 className="w-3 h-3" />}>
                Vinculado
              </Badge>
            )}
          </div>
        );
      },
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex items-center gap-1">
          {row.status === TransactionStatus.PENDING && (
            <Button
              variant="primary"
              size="sm"
              leftIcon={reconcile.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Link2 className="w-3 h-3" />}
              onClick={(e) => {
                e.stopPropagation();
                handleReconcile(row.id);
              }}
              disabled={reconcile.isPending}
            >
              Conciliar
            </Button>
          )}
        </div>
      ),
    },
  ], [handleReconcile, reconcile.isPending]);

  // Loading state
  if (isLoadingAccounts) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-64 mt-2" />
            </div>
            <div className="flex gap-3">
              <Skeleton className="h-10 w-28" />
              <Skeleton className="h-10 w-28" />
              <Skeleton className="h-10 w-32" />
            </div>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        </div>
      </MainLayout>
    );
  }

  // Error state
  if (accountsError) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-12">
          <AlertTriangle className="w-12 h-12 text-danger mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Erro ao carregar dados</h2>
          <p className="text-text-secondary mb-4">Não foi possível carregar as contas bancárias.</p>
          <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />} onClick={() => refetchAccounts()}>
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
              Contas Bancárias
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie suas contas e conciliação bancária
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              leftIcon={<ArrowRightLeft className="w-4 h-4" />}
              onClick={() => setIsTransferModalOpen(true)}
            >
              Transferir
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar OFX
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsAccountModalOpen(true)}
            >
              Nova Conta
            </Button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-accent-primary/10 to-bg-secondary border-accent-primary/20">
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-accent-primary/10">
                  <DollarSign className="w-5 h-5 text-accent-primary" />
                </div>
                <span className="text-xs text-text-muted">Saldo Total</span>
              </div>
              <p className="text-2xl font-mono font-bold text-accent-primary">
                {isLoadingStats ? '-' : stats.total_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-success/10">
                  <TrendingUp className="w-5 h-5 text-success" />
                </div>
                <span className="text-xs text-text-muted">Entradas (Mês)</span>
              </div>
              <p className="text-2xl font-mono font-bold text-success">
                {(summary.total_credits || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-danger/10">
                  <ArrowDownRight className="w-5 h-5 text-danger" />
                </div>
                <span className="text-xs text-text-muted">Saídas (Mês)</span>
              </div>
              <p className="text-2xl font-mono font-bold text-danger">
                {(summary.total_debits || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
            </CardBody>
          </Card>

          <Card className={pendingCount > 0 ? 'border-warning/30' : ''}>
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-warning/10">
                  <AlertTriangle className="w-5 h-5 text-warning" />
                </div>
                <span className="text-xs text-text-muted">Pendentes</span>
              </div>
              <p className="text-2xl font-bold text-warning">
                {pendingCount} lançamentos
              </p>
            </CardBody>
          </Card>
        </div>

        {/* Bank Accounts Grid */}
        <div>
          <h2 className="text-lg font-medium text-text-primary mb-4">Minhas Contas</h2>
          {accounts.length === 0 ? (
            <Card>
              <CardBody className="py-12 text-center">
                <Building2 className="w-12 h-12 text-text-muted mx-auto mb-4" />
                <h3 className="text-lg font-medium text-text-primary mb-2">Nenhuma conta cadastrada</h3>
                <p className="text-text-secondary mb-4">Cadastre sua primeira conta bancária para começar.</p>
                <Button variant="primary" onClick={() => setIsAccountModalOpen(true)}>
                  Cadastrar Conta
                </Button>
              </CardBody>
            </Card>
          ) : (
            <div className="grid grid-cols-4 gap-4">
              {accounts.map((account) => (
                <motion.div
                  key={account.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <BankAccountCard account={account} />
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Balance Chart & Transactions */}
        <div className="grid grid-cols-3 gap-6">
          {/* Balance History Chart */}
          <Card>
            <CardHeader title="Evolução do Saldo" subtitle="Últimos 7 dias" />
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={balanceHistory}>
                    <defs>
                      <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                    <YAxis
                      stroke="#64748b"
                      fontSize={12}
                      tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) =>
                        value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                      }
                    />
                    <Area
                      type="monotone"
                      dataKey="balance"
                      stroke="#6366f1"
                      fillOpacity={1}
                      fill="url(#colorBalance)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Recent Transactions */}
          <Card className="col-span-2">
            <CardHeader
              title="Extrato Bancário"
              action={
                <div className="flex items-center gap-3">
                  <Select
                    options={[
                      { value: 'all', label: 'Todas as Contas' },
                      ...accounts.map((a) => ({ value: a.id, label: a.description || a.bank_name })),
                    ]}
                    value={selectedAccount}
                    onChange={setSelectedAccount}
                    className="w-48"
                  />
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => refetchTransactions()}
                  >
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                </div>
              }
            />
            <CardBody className="pt-0">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todos (${transactions.length})` },
                  { value: 'pending', label: `Pendentes (${pendingCount})` },
                  { value: 'reconciled', label: `Conciliados (${transactions.filter(t => t.status === TransactionStatus.RECONCILED).length})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
            </CardBody>
            <CardBody className="p-0 pt-0">
              {isLoadingTransactions ? (
                <div className="p-8 text-center">
                  <Loader2 className="w-8 h-8 animate-spin text-accent-primary mx-auto" />
                </div>
              ) : (
                <DataTable
                  columns={transactionColumns}
                  data={filteredTransactions}
                  keyExtractor={(row) => row.id}
                  emptyState={{ title: "Nenhuma transação encontrada" }}
                />
              )}
            </CardBody>
          </Card>
        </div>

        {/* New Account Modal */}
        <Modal
          isOpen={isAccountModalOpen}
          onClose={() => setIsAccountModalOpen(false)}
          title="Nova Conta Bancária"
          description="Cadastre uma nova conta"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsAccountModalOpen(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                onClick={handleCreateAccount}
                disabled={createAccount.isPending || !accountForm.bank_name || !accountForm.agency}
                leftIcon={createAccount.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
              >
                {createAccount.isPending ? 'Criando...' : 'Cadastrar'}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Banco"
                placeholder="Nome do banco"
                value={accountForm.bank_name || ''}
                onChange={(e) => setAccountForm(prev => ({ ...prev, bank_name: e.target.value }))}
                required
              />
              <Input
                label="Código do Banco"
                placeholder="Ex: 341"
                value={accountForm.bank_code || ''}
                onChange={(e) => setAccountForm(prev => ({ ...prev, bank_code: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Agência"
                placeholder="0000"
                value={accountForm.agency || ''}
                onChange={(e) => setAccountForm(prev => ({ ...prev, agency: e.target.value }))}
                required
              />
              <Input
                label="Conta"
                placeholder="00000-0"
                value={accountForm.account_number || ''}
                onChange={(e) => setAccountForm(prev => ({ ...prev, account_number: e.target.value }))}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Conta"
                options={[
                  { value: 'checking', label: 'Conta Corrente' },
                  { value: 'savings', label: 'Poupança' },
                  { value: 'investment', label: 'Investimento' },
                  { value: 'petty_cash', label: 'Caixa Pequeno' },
                ]}
                value={accountForm.account_type || 'checking'}
                onChange={(value) => setAccountForm(prev => ({ ...prev, account_type: value as BankAccountType }))}
              />
              <Input
                label="Saldo Inicial"
                type="number"
                placeholder="0,00"
                leftIcon={<span className="text-text-muted">R$</span>}
                value={accountForm.initial_balance || ''}
                onChange={(e) => setAccountForm(prev => ({ ...prev, initial_balance: parseFloat(e.target.value) || 0 }))}
              />
            </div>
            <Input
              label="Descrição"
              placeholder="Ex: Conta Principal"
              value={accountForm.description || ''}
              onChange={(e) => setAccountForm(prev => ({ ...prev, description: e.target.value }))}
            />
            <Input
              label="Chave PIX"
              placeholder="CPF, CNPJ, E-mail, Telefone ou Chave aleatória"
              value={accountForm.pix_key || ''}
              onChange={(e) => setAccountForm(prev => ({ ...prev, pix_key: e.target.value }))}
            />
          </div>
        </Modal>

        {/* Transfer Modal */}
        <Modal
          isOpen={isTransferModalOpen}
          onClose={() => setIsTransferModalOpen(false)}
          title="Transferência entre Contas"
          description="Transfira valores entre suas contas"
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsTransferModalOpen(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                onClick={handleTransfer}
                disabled={transfer.isPending || !transferForm.from_account_id || !transferForm.to_account_id || !transferForm.amount}
                leftIcon={transfer.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
              >
                {transfer.isPending ? 'Transferindo...' : 'Confirmar'}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Conta de Origem"
              options={accounts.map(a => ({
                value: a.id,
                label: `${a.description || a.bank_name} - ${a.current_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`,
              }))}
              value={transferForm.from_account_id || ''}
              onChange={(value) => setTransferForm(prev => ({ ...prev, from_account_id: value }))}
              placeholder="Selecione a conta de origem..."
              required
            />
            <Select
              label="Conta de Destino"
              options={accounts
                .filter(a => a.id !== transferForm.from_account_id)
                .map(a => ({
                  value: a.id,
                  label: `${a.description || a.bank_name}`,
                }))}
              value={transferForm.to_account_id || ''}
              onChange={(value) => setTransferForm(prev => ({ ...prev, to_account_id: value }))}
              placeholder="Selecione a conta de destino..."
              required
            />
            <Input
              label="Valor"
              type="number"
              placeholder="0,00"
              leftIcon={<span className="text-text-muted">R$</span>}
              value={transferForm.amount || ''}
              onChange={(e) => setTransferForm(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
              required
            />
            <Input
              label="Descrição"
              placeholder="Motivo da transferência"
              value={transferForm.description || ''}
              onChange={(e) => setTransferForm(prev => ({ ...prev, description: e.target.value }))}
            />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
