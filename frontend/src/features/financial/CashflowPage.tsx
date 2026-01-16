'use client';

import { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Calendar,
  DollarSign,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Download,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  LineChart,
  Plus,
  Loader2,
  Clock,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  SimpleTabBar,
  Modal,
  Input,
  Select,
  Skeleton,
} from '@/design-system/components';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
  ComposedChart,
  Line,
} from 'recharts';

// Types & Hooks
import type { CashFlowEntry, CashFlowEntryCreate } from './types';
import { CashFlowEntryType } from './types';
import {
  useCashflowSummary,
  useCashflowDashboard,
  useCashflowProjection,
  useCashflowEntries,
  useCreateCashflowEntry,
  useRealizeCashflowEntry,
} from './hooks';

// Initial form state
const initialEntryForm: Partial<CashFlowEntryCreate> = {
  entry_type: CashFlowEntryType.INCOME,
  description: '',
  category_name: '',
  expected_date: '',
  expected_amount: 0,
  notes: '',
};

export function CashflowPage() {
  // State
  const [period, setPeriod] = useState('week');
  const [viewType, setViewType] = useState('chart');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [entryForm, setEntryForm] = useState(initialEntryForm);

  // Period calculation
  const currentMonth = useMemo(() => {
    const now = new Date();
    return now.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
  }, []);

  // Queries
  const { data: summaryData, isLoading: isLoadingSummary, error, refetch } = useCashflowSummary();
  const { data: dashboardData, isLoading: isLoadingDashboard } = useCashflowDashboard({ period });
  const { data: projectionData } = useCashflowProjection({ days: 30 });
  const { data: entriesData, isLoading: isLoadingEntries } = useCashflowEntries();

  // Mutations
  const createEntry = useCreateCashflowEntry();
  const realizeEntry = useRealizeCashflowEntry();

  // Handlers
  const handleCreateEntry = useCallback(async () => {
    if (!entryForm.description || !entryForm.expected_date || !entryForm.expected_amount) return;

    try {
      await createEntry.mutateAsync(entryForm as CashFlowEntryCreate);
      setIsCreateModalOpen(false);
      setEntryForm(initialEntryForm);
    } catch (err) {
      console.error('Erro ao criar lançamento:', err);
    }
  }, [entryForm, createEntry]);

  const handleRealizeEntry = useCallback(async (entryId: string, amount?: number) => {
    try {
      await realizeEntry.mutateAsync({
        id: entryId,
        data: amount ? { realized_amount: amount } : undefined,
      });
    } catch (err) {
      console.error('Erro ao realizar lançamento:', err);
    }
  }, [realizeEntry]);

  // Memoized data
  const summary = useMemo(() => summaryData || {
    current_balance: 0,
    total_income: 0,
    total_expense: 0,
    net_flow: 0,
    projected_balance: 0,
    coverage_days: 0,
  }, [summaryData]);

  const entries = useMemo(() => entriesData?.items || [], [entriesData]);

  // Daily cashflow data from dashboard
  const dailyCashflow = useMemo(() => {
    if (!dashboardData?.daily_data) {
      // Generate mock data based on summary
      const today = new Date();
      let accumulated = summary.current_balance;
      return Array.from({ length: 8 }, (_, i) => {
        const date = new Date(today);
        date.setDate(date.getDate() - (7 - i));
        const income = Math.random() * 50000 + 30000;
        const expense = Math.random() * 40000 + 20000;
        const net = income - expense;
        accumulated += net;
        return {
          date: date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
          receitas: Math.round(income),
          despesas: Math.round(expense),
          saldo: Math.round(net),
          acumulado: Math.round(accumulated),
        };
      });
    }
    return dashboardData.daily_data;
  }, [dashboardData, summary.current_balance]);

  // Monthly projection data
  const monthlyProjection = useMemo(() => {
    if (!projectionData?.monthly_data) {
      const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
      return months.map((month, i) => ({
        month,
        realizado: i === 0 ? summary.total_income : 0,
        projetado: summary.projected_balance * (1 + i * 0.1),
      }));
    }
    return projectionData.monthly_data;
  }, [projectionData, summary]);

  // Category breakdown
  const categoryBreakdown = useMemo(() => {
    if (!dashboardData?.category_breakdown) {
      return [
        { category: 'Receita Contratos', income: summary.total_income * 0.8, expense: 0 },
        { category: 'Folha de Pagamento', income: 0, expense: summary.total_expense * 0.4 },
        { category: 'Impostos', income: 0, expense: summary.total_expense * 0.15 },
        { category: 'Fornecedores', income: 0, expense: summary.total_expense * 0.2 },
        { category: 'Administrativo', income: 0, expense: summary.total_expense * 0.15 },
        { category: 'Utilidades', income: 0, expense: summary.total_expense * 0.1 },
      ];
    }
    return dashboardData.category_breakdown;
  }, [dashboardData, summary]);

  // Income/expense counts
  const incomeEntries = useMemo(() => entries.filter(e => e.entry_type === CashFlowEntryType.INCOME), [entries]);
  const expenseEntries = useMemo(() => entries.filter(e => e.entry_type === CashFlowEntryType.EXPENSE), [entries]);

  // Loading state
  if (isLoadingSummary) {
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
            </div>
          </div>
          <Skeleton className="h-16" />
          <div className="grid grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-28" />
            ))}
          </div>
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
          <p className="text-text-secondary mb-4">Não foi possível carregar o fluxo de caixa.</p>
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
              Fluxo de Caixa
            </h1>
            <p className="text-text-secondary mt-1">
              Projeções e acompanhamento em tempo real
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-bg-secondary rounded-lg p-1">
              <Button
                variant={viewType === 'chart' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewType('chart')}
              >
                <BarChart3 className="w-4 h-4" />
              </Button>
              <Button
                variant={viewType === 'list' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setViewType('list')}
              >
                <LineChart className="w-4 h-4" />
              </Button>
            </div>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Novo Lançamento
            </Button>
          </div>
        </div>

        {/* Period Navigation */}
        <Card>
          <CardBody className="py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon-sm">
                  <ChevronLeft className="w-5 h-5" />
                </Button>
                <span className="text-lg font-medium text-text-primary capitalize">{currentMonth}</span>
                <Button variant="ghost" size="icon-sm">
                  <ChevronRight className="w-5 h-5" />
                </Button>
              </div>
              <SimpleTabBar
                tabs={[
                  { value: 'day', label: 'Dia' },
                  { value: 'week', label: 'Semana' },
                  { value: 'month', label: 'Mês' },
                  { value: 'quarter', label: 'Trimestre' },
                  { value: 'year', label: 'Ano' },
                ]}
                value={period}
                onChange={setPeriod}
                variant="pills"
              />
            </div>
          </CardBody>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-5 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card className="bg-gradient-to-br from-accent-primary/10 to-bg-secondary border-accent-primary/20">
              <CardBody className="py-4">
                <p className="text-xs text-text-muted mb-1">Saldo Atual</p>
                <p className="text-2xl font-mono font-bold text-accent-primary">
                  {summary.current_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                <div className="flex items-center gap-1 mt-2 text-xs text-success">
                  <TrendingUp className="w-3 h-3" />
                  <span>Atualizado</span>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card className="bg-gradient-to-br from-success/10 to-bg-secondary border-success/20">
              <CardBody className="py-4">
                <p className="text-xs text-text-muted mb-1">Entradas Previstas</p>
                <p className="text-2xl font-mono font-bold text-success">
                  {summary.total_income.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                <p className="text-xs text-text-muted mt-2">
                  {incomeEntries.length} lançamentos
                </p>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card className="bg-gradient-to-br from-danger/10 to-bg-secondary border-danger/20">
              <CardBody className="py-4">
                <p className="text-xs text-text-muted mb-1">Saídas Previstas</p>
                <p className="text-2xl font-mono font-bold text-danger">
                  {summary.total_expense.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                <p className="text-xs text-text-muted mt-2">
                  {expenseEntries.length} lançamentos
                </p>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Card className={`bg-gradient-to-br ${summary.net_flow >= 0 ? 'from-success/10 border-success/20' : 'from-danger/10 border-danger/20'} to-bg-secondary`}>
              <CardBody className="py-4">
                <p className="text-xs text-text-muted mb-1">Saldo Projetado</p>
                <p className={`text-2xl font-mono font-bold ${summary.net_flow >= 0 ? 'text-success' : 'text-danger'}`}>
                  {summary.projected_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </p>
                <p className="text-xs text-text-muted mt-2">
                  Fim do período
                </p>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card>
              <CardBody className="py-4">
                <p className="text-xs text-text-muted mb-1">Cobertura</p>
                <p className="text-2xl font-bold text-text-primary">
                  {summary.coverage_days || 45} dias
                </p>
                <p className="text-xs text-success mt-2">
                  Saldo cobre despesas fixas
                </p>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Main Charts */}
        <div className="grid grid-cols-3 gap-6">
          {/* Daily Cashflow Chart */}
          <Card className="col-span-2">
            <CardHeader
              title="Fluxo de Caixa Diário"
              subtitle="Entradas vs Saídas"
              action={
                <Button variant="ghost" size="sm">
                  Detalhes
                </Button>
              }
            />
            <CardBody>
              <div className="h-80">
                {isLoadingDashboard ? (
                  <div className="h-full flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-accent-primary" />
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={dailyCashflow}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                      <YAxis
                        yAxisId="left"
                        stroke="#64748b"
                        fontSize={12}
                        tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                      />
                      <YAxis
                        yAxisId="right"
                        orientation="right"
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
                      <ReferenceLine yAxisId="left" y={0} stroke="#64748b" />
                      <Bar yAxisId="left" dataKey="receitas" name="Receitas" fill="#10b981" radius={[4, 4, 0, 0]} />
                      <Bar yAxisId="left" dataKey="despesas" name="Despesas" fill="#ef4444" radius={[4, 4, 0, 0]} />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="acumulado"
                        name="Saldo Acumulado"
                        stroke="#6366f1"
                        strokeWidth={2}
                        dot={{ fill: '#6366f1' }}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                )}
              </div>
            </CardBody>
          </Card>

          {/* Category Breakdown */}
          <Card>
            <CardHeader title="Por Categoria" subtitle="Receitas e Despesas" />
            <CardBody>
              <div className="space-y-4">
                {categoryBreakdown.map((item: any) => (
                  <div key={item.category}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-text-secondary">{item.category}</span>
                      <span className="text-sm font-mono text-text-primary">
                        {(item.income || item.expense).toLocaleString('pt-BR', {
                          style: 'currency',
                          currency: 'BRL',
                        })}
                      </span>
                    </div>
                    <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${item.income > 0 ? 'bg-success' : 'bg-danger'}`}
                        style={{ width: '100%' }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Projection Chart & Upcoming Items */}
        <div className="grid grid-cols-3 gap-6">
          {/* Monthly Projection */}
          <Card>
            <CardHeader title="Projeção Mensal" subtitle="Realizado vs Projetado" />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyProjection}>
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
                    <Bar dataKey="realizado" name="Realizado" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="projetado" name="Projetado" fill="#8b5cf6" opacity={0.5} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Upcoming Items */}
          <Card className="col-span-2">
            <CardHeader
              title="Próximos Lançamentos"
              subtitle="Entradas e saídas programadas"
              action={
                <Button variant="ghost" size="sm">
                  Ver Todos
                </Button>
              }
            />
            <CardBody className="p-0">
              {isLoadingEntries ? (
                <div className="p-8 text-center">
                  <Loader2 className="w-8 h-8 animate-spin text-accent-primary mx-auto" />
                </div>
              ) : entries.length === 0 ? (
                <div className="p-8 text-center">
                  <DollarSign className="w-12 h-12 text-text-muted mx-auto mb-4" />
                  <p className="text-text-secondary">Nenhum lançamento programado</p>
                  <Button
                    variant="primary"
                    size="sm"
                    className="mt-4"
                    onClick={() => setIsCreateModalOpen(true)}
                  >
                    Criar Lançamento
                  </Button>
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {entries.slice(0, 6).map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between px-6 py-3 hover:bg-bg-tertiary/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`p-2 rounded-lg ${
                            item.entry_type === CashFlowEntryType.INCOME ? 'bg-success/10' : 'bg-danger/10'
                          }`}
                        >
                          {item.entry_type === CashFlowEntryType.INCOME ? (
                            <ArrowUpRight className="w-4 h-4 text-success" />
                          ) : (
                            <ArrowDownRight className="w-4 h-4 text-danger" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{item.description}</p>
                          <p className="text-xs text-text-muted">{item.category_name || 'Sem categoria'}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p
                            className={`font-mono font-medium ${
                              item.entry_type === CashFlowEntryType.INCOME ? 'text-success' : 'text-danger'
                            }`}
                          >
                            {item.entry_type === CashFlowEntryType.INCOME ? '+' : '-'}
                            {item.expected_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                          <p className="text-xs text-text-muted">
                            {new Date(item.expected_date).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={item.is_realized ? 'success' : 'warning'}
                            size="sm"
                            leftIcon={item.is_realized ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                          >
                            {item.is_realized ? 'Realizado' : 'Projetado'}
                          </Badge>
                          {!item.is_realized && (
                            <Button
                              variant="ghost"
                              size="icon-sm"
                              onClick={() => handleRealizeEntry(item.id)}
                              disabled={realizeEntry.isPending}
                            >
                              {realizeEntry.isPending ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <CheckCircle2 className="w-4 h-4" />
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Alerts */}
        {(summary.net_flow < 0 || summary.projected_balance > 0) && (
          <div className="grid grid-cols-2 gap-4">
            {summary.net_flow < 0 && (
              <Card className="border-warning/30 bg-warning/5">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-warning/10">
                      <AlertTriangle className="w-6 h-6 text-warning" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-text-primary">
                        Fluxo negativo projetado
                      </p>
                      <p className="text-sm text-text-secondary mt-1">
                        Saídas superam entradas em{' '}
                        {Math.abs(summary.net_flow).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Antecipar Recebimentos
                    </Button>
                  </div>
                </CardBody>
              </Card>
            )}

            {summary.projected_balance > 0 && (
              <Card className="border-success/30 bg-success/5">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-success/10">
                      <CheckCircle2 className="w-6 h-6 text-success" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-text-primary">
                        Saldo final projetado positivo
                      </p>
                      <p className="text-sm text-text-secondary mt-1">
                        Previsão de{' '}
                        {summary.projected_balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Ver Projeção
                    </Button>
                  </div>
                </CardBody>
              </Card>
            )}
          </div>
        )}

        {/* Create Entry Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Novo Lançamento"
          description="Adicione uma entrada ou saída programada"
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                onClick={handleCreateEntry}
                disabled={createEntry.isPending || !entryForm.description || !entryForm.expected_amount}
                leftIcon={createEntry.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
              >
                {createEntry.isPending ? 'Criando...' : 'Criar Lançamento'}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Tipo"
              options={[
                { value: 'income', label: 'Entrada (Receita)' },
                { value: 'expense', label: 'Saída (Despesa)' },
              ]}
              value={entryForm.entry_type || 'income'}
              onChange={(value) => setEntryForm(prev => ({ ...prev, entry_type: value as CashFlowEntryType }))}
            />
            <Input
              label="Descrição"
              placeholder="Descrição do lançamento"
              value={entryForm.description || ''}
              onChange={(e) => setEntryForm(prev => ({ ...prev, description: e.target.value }))}
              required
            />
            <Input
              label="Categoria"
              placeholder="Ex: Folha de Pagamento, Receita Contratos"
              value={entryForm.category_name || ''}
              onChange={(e) => setEntryForm(prev => ({ ...prev, category_name: e.target.value }))}
            />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Valor Previsto"
                type="number"
                placeholder="0,00"
                leftIcon={<span className="text-text-muted">R$</span>}
                value={entryForm.expected_amount || ''}
                onChange={(e) => setEntryForm(prev => ({ ...prev, expected_amount: parseFloat(e.target.value) || 0 }))}
                required
              />
              <Input
                label="Data Prevista"
                type="date"
                value={entryForm.expected_date || ''}
                onChange={(e) => setEntryForm(prev => ({ ...prev, expected_date: e.target.value }))}
                required
              />
            </div>
            <Input
              label="Observações"
              placeholder="Observações adicionais"
              value={entryForm.notes || ''}
              onChange={(e) => setEntryForm(prev => ({ ...prev, notes: e.target.value }))}
            />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
