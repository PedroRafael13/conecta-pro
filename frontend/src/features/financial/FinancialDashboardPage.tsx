'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Building2,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Wallet,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  DataTable,
  type Column,
  SimpleTabBar,
  Skeleton,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPie,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Types & Hooks
import {
  useFinancialDashboard,
  useFinancialKPIs,
  useFinancialAlerts,
  useReceivableStats,
  usePayableStats,
  useBankAccountStats,
  useBankTransactions,
} from './hooks';
import type { BankTransaction } from './types';
import { TransactionType, TransactionStatus } from './types';

// Chart colors
const EXPENSE_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b', '#64748b'];

export function FinancialDashboardPage() {
  // State
  const [period, setPeriod] = useState('month');

  // Queries
  const { data: dashboardData, isLoading: isLoadingDashboard, error, refetch } = useFinancialDashboard({ period });
  const { data: kpisData, isLoading: isLoadingKPIs } = useFinancialKPIs();
  const { data: alertsData } = useFinancialAlerts();
  const { data: receivableStats } = useReceivableStats();
  const { data: payableStats } = usePayableStats();
  const { data: bankStats } = useBankAccountStats();
  const { data: transactionsData, isLoading: isLoadingTransactions } = useBankTransactions({ page_size: 5 });

  // Memoized data
  const dashboard = useMemo(() => dashboardData || {
    total_income: 0,
    total_expense: 0,
    net_balance: 0,
    monthly_data: [],
    expenses_by_category: [],
    revenue_by_client: [],
  }, [dashboardData]);

  const kpis = useMemo(() => kpisData || {
    revenue_growth: 0,
    expense_growth: 0,
    profit_margin: 0,
  }, [kpisData]);

  const alerts = useMemo(() => alertsData || [], [alertsData]);
  const receivables = useMemo(() => receivableStats || { total_balance: 0, total_accounts: 0, overdue_count: 0 }, [receivableStats]);
  const payables = useMemo(() => payableStats || { total_balance: 0, total_accounts: 0, overdue_count: 0 }, [payableStats]);
  const bank = useMemo(() => bankStats || { total_balance: 0 }, [bankStats]);
  const transactions = useMemo(() => transactionsData?.items || [], [transactionsData]);

  // Chart data
  const cashflowData = useMemo(() => {
    if (dashboard.monthly_data?.length > 0) {
      return dashboard.monthly_data;
    }
    // Generate mock data based on totals
    const months = ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez', 'Jan'];
    const baseIncome = dashboard.total_income / 7;
    const baseExpense = dashboard.total_expense / 7;
    return months.map(month => ({
      month,
      receitas: Math.round(baseIncome * (0.8 + Math.random() * 0.4)),
      despesas: Math.round(baseExpense * (0.8 + Math.random() * 0.4)),
    }));
  }, [dashboard]);

  const expensesByCategory = useMemo(() => {
    if (dashboard.expenses_by_category?.length > 0) {
      return dashboard.expenses_by_category.map((item: any, i: number) => ({
        ...item,
        color: EXPENSE_COLORS[i % EXPENSE_COLORS.length],
      }));
    }
    // Mock data
    return [
      { name: 'Folha de Pagamento', value: dashboard.total_expense * 0.45, color: EXPENSE_COLORS[0] },
      { name: 'Fornecedores', value: dashboard.total_expense * 0.2, color: EXPENSE_COLORS[1] },
      { name: 'Impostos', value: dashboard.total_expense * 0.15, color: EXPENSE_COLORS[2] },
      { name: 'Operacional', value: dashboard.total_expense * 0.1, color: EXPENSE_COLORS[3] },
      { name: 'Administrativo', value: dashboard.total_expense * 0.07, color: EXPENSE_COLORS[4] },
      { name: 'Outros', value: dashboard.total_expense * 0.03, color: EXPENSE_COLORS[5] },
    ];
  }, [dashboard]);

  const revenueByClient = useMemo(() => {
    if (dashboard.revenue_by_client?.length > 0) {
      return dashboard.revenue_by_client.slice(0, 5);
    }
    return [
      { name: 'Cliente 1', value: dashboard.total_income * 0.25 },
      { name: 'Cliente 2', value: dashboard.total_income * 0.2 },
      { name: 'Cliente 3', value: dashboard.total_income * 0.15 },
      { name: 'Cliente 4', value: dashboard.total_income * 0.1 },
      { name: 'Outros', value: dashboard.total_income * 0.3 },
    ];
  }, [dashboard]);

  // Transaction columns
  const transactionColumns: Column<BankTransaction>[] = useMemo(() => [
    {
      key: 'description',
      header: 'Descrição',
      render: (row) => {
        const isIncome = row.transaction_type === TransactionType.CREDIT || row.transaction_type === TransactionType.TRANSFER_IN;
        return (
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${isIncome ? 'bg-success/10' : 'bg-danger/10'}`}>
              {isIncome ? (
                <ArrowUpRight className="w-4 h-4 text-success" />
              ) : (
                <ArrowDownRight className="w-4 h-4 text-danger" />
              )}
            </div>
            <div>
              <p className="font-medium text-text-primary">{row.description}</p>
              <p className="text-xs text-text-muted">{row.category_name || 'Sem categoria'}</p>
            </div>
          </div>
        );
      },
    },
    {
      key: 'amount',
      header: 'Valor',
      render: (row) => {
        const isIncome = row.transaction_type === TransactionType.CREDIT || row.transaction_type === TransactionType.TRANSFER_IN;
        return (
          <span className={`font-mono font-medium ${isIncome ? 'text-success' : 'text-danger'}`}>
            {isIncome ? '+' : '-'}
            {Math.abs(row.amount).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </span>
        );
      },
    },
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
      key: 'account_name',
      header: 'Conta',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-text-muted" />
          <span className="text-sm text-text-secondary">{row.account_name || 'N/A'}</span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config: Record<string, { label: string; color: 'success' | 'warning' | 'info'; icon: typeof CheckCircle2 }> = {
          confirmed: { label: 'Concluído', color: 'success', icon: CheckCircle2 },
          reconciled: { label: 'Conciliado', color: 'success', icon: CheckCircle2 },
          pending: { label: 'Pendente', color: 'warning', icon: Clock },
          cancelled: { label: 'Cancelado', color: 'info', icon: Calendar },
        };
        const status = config[row.status] || config.pending;
        const Icon = status.icon;
        return (
          <Badge variant={status.color} leftIcon={<Icon className="w-3 h-3" />}>
            {status.label}
          </Badge>
        );
      },
    },
  ], []);

  // Loading state
  if (isLoadingDashboard) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Skeleton className="h-8 w-56" />
              <Skeleton className="h-4 w-72 mt-2" />
            </div>
            <Skeleton className="h-10 w-48" />
          </div>
          <div className="grid grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-28" />
            ))}
          </div>
          <div className="grid grid-cols-3 gap-6">
            <Skeleton className="col-span-2 h-96" />
            <Skeleton className="h-96" />
          </div>
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
          <h2 className="text-xl font-semibold text-text-primary mb-2">Erro ao carregar dashboard</h2>
          <p className="text-text-secondary mb-4">Não foi possível carregar os dados financeiros.</p>
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
              Dashboard Financeiro
            </h1>
            <p className="text-text-secondary mt-1">
              Visão geral das finanças da empresa
            </p>
          </div>
          <div className="flex items-center gap-3">
            <SimpleTabBar
              tabs={[
                { value: 'month', label: 'Mês' },
                { value: 'quarter', label: 'Trimestre' },
                { value: 'year', label: 'Ano' },
              ]}
              value={period}
              onChange={setPeriod}
              variant="pills"
            />
          </div>
        </div>

        {/* Main Stats */}
        <div className="grid grid-cols-5 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card className="bg-gradient-to-br from-success/10 to-bg-secondary border-success/20">
              <CardBody className="py-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-success/10">
                    <TrendingUp className="w-5 h-5 text-success" />
                  </div>
                  <span className="text-xs text-text-muted">Receitas</span>
                </div>
                <p className="text-2xl font-mono font-bold text-success">
                  {dashboard.total_income.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                {kpis.revenue_growth !== 0 && (
                  <p className={`text-xs mt-1 ${kpis.revenue_growth >= 0 ? 'text-success' : 'text-danger'}`}>
                    {kpis.revenue_growth >= 0 ? '+' : ''}{kpis.revenue_growth.toFixed(1)}% vs período anterior
                  </p>
                )}
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card className="bg-gradient-to-br from-danger/10 to-bg-secondary border-danger/20">
              <CardBody className="py-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-danger/10">
                    <TrendingDown className="w-5 h-5 text-danger" />
                  </div>
                  <span className="text-xs text-text-muted">Despesas</span>
                </div>
                <p className="text-2xl font-mono font-bold text-danger">
                  {dashboard.total_expense.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                {kpis.expense_growth !== 0 && (
                  <p className={`text-xs mt-1 ${kpis.expense_growth <= 0 ? 'text-success' : 'text-danger'}`}>
                    {kpis.expense_growth >= 0 ? '+' : ''}{kpis.expense_growth.toFixed(1)}% vs período anterior
                  </p>
                )}
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card className="bg-gradient-to-br from-accent-primary/10 to-bg-secondary border-accent-primary/20">
              <CardBody className="py-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-accent-primary/10">
                    <Wallet className="w-5 h-5 text-accent-primary" />
                  </div>
                  <span className="text-xs text-text-muted">Saldo Bancário</span>
                </div>
                <p className="text-2xl font-mono font-bold text-accent-primary">
                  {bank.total_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                {kpis.profit_margin !== 0 && (
                  <p className="text-xs text-accent-primary mt-1">
                    Margem: {kpis.profit_margin.toFixed(1)}%
                  </p>
                )}
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Card className="bg-gradient-to-br from-info/10 to-bg-secondary border-info/20">
              <CardBody className="py-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-info/10">
                    <ArrowUpRight className="w-5 h-5 text-info" />
                  </div>
                  <span className="text-xs text-text-muted">A Receber</span>
                </div>
                <p className="text-2xl font-mono font-bold text-info">
                  {receivables.total_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                <p className="text-xs text-text-muted mt-1">{receivables.total_accounts} títulos</p>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card className="bg-gradient-to-br from-warning/10 to-bg-secondary border-warning/20">
              <CardBody className="py-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-warning/10">
                    <ArrowDownRight className="w-5 h-5 text-warning" />
                  </div>
                  <span className="text-xs text-text-muted">A Pagar</span>
                </div>
                <p className="text-2xl font-mono font-bold text-warning">
                  {payables.total_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                <p className="text-xs text-text-muted mt-1">{payables.total_accounts} títulos</p>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-3 gap-6">
          {/* Cashflow Chart */}
          <Card className="col-span-2">
            <CardHeader
              title="Fluxo de Caixa"
              subtitle="Últimos 7 meses"
              action={
                <Button variant="ghost" size="sm">
                  Ver Detalhes
                </Button>
              }
            />
            <CardBody>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={cashflowData}>
                    <defs>
                      <linearGradient id="colorReceitas" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorDespesas" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
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
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="receitas"
                      name="Receitas"
                      stroke="#10b981"
                      fillOpacity={1}
                      fill="url(#colorReceitas)"
                    />
                    <Area
                      type="monotone"
                      dataKey="despesas"
                      name="Despesas"
                      stroke="#ef4444"
                      fillOpacity={1}
                      fill="url(#colorDespesas)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Expenses by Category */}
          <Card>
            <CardHeader title="Despesas por Categoria" subtitle={`${period === 'month' ? 'Este mês' : period === 'quarter' ? 'Este trimestre' : 'Este ano'}`} />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPie>
                    <Pie
                      data={expensesByCategory}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {expensesByCategory.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
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
                  </RechartsPie>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">
                {expensesByCategory.slice(0, 4).map((item: any) => (
                  <div key={item.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-text-secondary">{item.name}</span>
                    </div>
                    <span className="font-mono text-text-primary">
                      {item.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Revenue by Client & Recent Transactions */}
        <div className="grid grid-cols-3 gap-6">
          {/* Revenue by Client */}
          <Card>
            <CardHeader title="Receita por Cliente" subtitle="Top 5 clientes" />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={revenueByClient} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis
                      type="number"
                      stroke="#64748b"
                      fontSize={12}
                      tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                    />
                    <YAxis
                      type="category"
                      dataKey="name"
                      stroke="#64748b"
                      fontSize={10}
                      width={100}
                      tick={{ fill: '#94a3b8' }}
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
                    <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Recent Transactions */}
          <Card className="col-span-2">
            <CardHeader
              title="Transações Recentes"
              action={
                <Button variant="ghost" size="sm">
                  Ver Todas
                </Button>
              }
            />
            <CardBody className="p-0">
              {isLoadingTransactions ? (
                <div className="p-8 text-center">
                  <Loader2 className="w-8 h-8 animate-spin text-accent-primary mx-auto" />
                </div>
              ) : (
                <DataTable
                  columns={transactionColumns}
                  data={transactions}
                  keyExtractor={(row) => row.id}
                  emptyState={{ title: "Nenhuma transação recente" }}
                />
              )}
            </CardBody>
          </Card>
        </div>

        {/* Alerts */}
        <div className="grid grid-cols-2 gap-4">
          {(payables.overdue_count > 0 || receivables.overdue_count > 0) && (
            <Card className="border-warning/30 bg-warning/5">
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-warning/10">
                    <AlertTriangle className="w-6 h-6 text-warning" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-text-primary">
                      {payables.overdue_count > 0
                        ? `${payables.overdue_count} títulos a pagar vencidos`
                        : `${receivables.overdue_count} títulos a receber vencidos`}
                    </p>
                    <p className="text-sm text-text-secondary mt-1">
                      Verifique os títulos pendentes
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    Ver Títulos
                  </Button>
                </div>
              </CardBody>
            </Card>
          )}

          <Card className="border-success/30 bg-success/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-success/10">
                  <CheckCircle2 className="w-6 h-6 text-success" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    {dashboard.net_balance >= 0 ? 'Saldo positivo no período' : 'Dashboard atualizado'}
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    {dashboard.net_balance >= 0
                      ? `Lucro de ${dashboard.net_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`
                      : 'Dados sincronizados'}
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Ver Relatório
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
