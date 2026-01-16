'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Calendar,
  DollarSign,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Download,
  Filter,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Eye,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  LineChart,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  StatCard,
  StatGrid,
  SimpleTabBar,
  Select,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
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

// Types
interface CashflowItem {
  date: string;
  description: string;
  category: string;
  type: 'income' | 'expense';
  value: number;
  status: 'realized' | 'projected';
}

// Mock Data
const dailyCashflow = [
  { date: '13/01', receitas: 45000, despesas: 28000, saldo: 17000, acumulado: 485000 },
  { date: '14/01', receitas: 95000, despesas: 45000, saldo: 50000, acumulado: 535000 },
  { date: '15/01', receitas: 128000, despesas: 260000, saldo: -132000, acumulado: 403000 },
  { date: '16/01', receitas: 35000, despesas: 18000, saldo: 17000, acumulado: 420000 },
  { date: '17/01', receitas: 0, despesas: 8500, saldo: -8500, acumulado: 411500 },
  { date: '18/01', receitas: 67000, despesas: 32000, saldo: 35000, acumulado: 446500 },
  { date: '19/01', receitas: 54000, despesas: 25000, saldo: 29000, acumulado: 475500 },
  { date: '20/01', receitas: 185000, despesas: 60000, saldo: 125000, acumulado: 600500 },
];

const monthlyProjection = [
  { month: 'Jan', realizado: 595000, projetado: 620000 },
  { month: 'Fev', realizado: 0, projetado: 680000 },
  { month: 'Mar', realizado: 0, projetado: 720000 },
  { month: 'Abr', realizado: 0, projetado: 750000 },
  { month: 'Mai', realizado: 0, projetado: 780000 },
  { month: 'Jun', realizado: 0, projetado: 850000 },
];

const cashflowItems: CashflowItem[] = [
  { date: '2026-01-20', description: 'Shopping Center Norte - Facilities', category: 'Receita Contratos', type: 'income', value: 128000, status: 'projected' },
  { date: '2026-01-20', description: 'Hospital São Lucas - Limpeza', category: 'Receita Contratos', type: 'income', value: 185000, status: 'projected' },
  { date: '2026-01-20', description: 'INSS Competência 12/2025', category: 'Impostos', type: 'expense', value: 42000, status: 'projected' },
  { date: '2026-01-22', description: 'Aluguel Filial SP', category: 'Administrativo', type: 'expense', value: 12000, status: 'projected' },
  { date: '2026-01-25', description: 'Fornecedor Uniformes', category: 'Operacional', type: 'expense', value: 18500, status: 'projected' },
  { date: '2026-01-25', description: 'Tech Park - Manutenção', category: 'Receita Contratos', type: 'income', value: 54000, status: 'projected' },
  { date: '2026-01-30', description: 'Energia Elétrica - Todas Unidades', category: 'Utilidades', type: 'expense', value: 15000, status: 'projected' },
  { date: '2026-01-31', description: 'Internet e Telefonia', category: 'Utilidades', type: 'expense', value: 8500, status: 'projected' },
];

const categoryBreakdown = [
  { category: 'Receita Contratos', income: 595000, expense: 0 },
  { category: 'Folha de Pagamento', income: 0, expense: 245000 },
  { category: 'Impostos', income: 0, expense: 85000 },
  { category: 'Fornecedores', income: 0, expense: 52000 },
  { category: 'Administrativo', income: 0, expense: 28000 },
  { category: 'Utilidades', income: 0, expense: 18000 },
];

export function CashflowPage() {
  const [period, setPeriod] = useState('week');
  const [viewType, setViewType] = useState('chart');
  const [currentMonth, setCurrentMonth] = useState('Janeiro 2026');

  // Calculate projections
  const projectedIncome = cashflowItems
    .filter((i) => i.type === 'income')
    .reduce((acc, i) => acc + i.value, 0);
  const projectedExpense = cashflowItems
    .filter((i) => i.type === 'expense')
    .reduce((acc, i) => acc + i.value, 0);
  const projectedBalance = projectedIncome - projectedExpense;
  const currentBalance = 485000;

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
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Atualizar
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
                <span className="text-lg font-medium text-text-primary">{currentMonth}</span>
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
          <Card className="bg-gradient-to-br from-accent-primary/10 to-bg-secondary border-accent-primary/20">
            <CardBody className="py-4">
              <p className="text-xs text-text-muted mb-1">Saldo Atual</p>
              <p className="text-2xl font-mono font-bold text-accent-primary">
                {currentBalance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <div className="flex items-center gap-1 mt-2 text-xs text-success">
                <TrendingUp className="w-3 h-3" />
                <span>+5.2% vs ontem</span>
              </div>
            </CardBody>
          </Card>

          <Card className="bg-gradient-to-br from-success/10 to-bg-secondary border-success/20">
            <CardBody className="py-4">
              <p className="text-xs text-text-muted mb-1">Entradas Previstas</p>
              <p className="text-2xl font-mono font-bold text-success">
                {projectedIncome.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-text-muted mt-2">
                {cashflowItems.filter((i) => i.type === 'income').length} lançamentos
              </p>
            </CardBody>
          </Card>

          <Card className="bg-gradient-to-br from-danger/10 to-bg-secondary border-danger/20">
            <CardBody className="py-4">
              <p className="text-xs text-text-muted mb-1">Saídas Previstas</p>
              <p className="text-2xl font-mono font-bold text-danger">
                {projectedExpense.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-text-muted mt-2">
                {cashflowItems.filter((i) => i.type === 'expense').length} lançamentos
              </p>
            </CardBody>
          </Card>

          <Card className={`bg-gradient-to-br ${projectedBalance >= 0 ? 'from-success/10 border-success/20' : 'from-danger/10 border-danger/20'} to-bg-secondary`}>
            <CardBody className="py-4">
              <p className="text-xs text-text-muted mb-1">Saldo Projetado</p>
              <p className={`text-2xl font-mono font-bold ${projectedBalance >= 0 ? 'text-success' : 'text-danger'}`}>
                {(currentBalance + projectedBalance).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-text-muted mt-2">
                Fim do período
              </p>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="py-4">
              <p className="text-xs text-text-muted mb-1">Cobertura</p>
              <p className="text-2xl font-bold text-text-primary">
                45 dias
              </p>
              <p className="text-xs text-success mt-2">
                Saldo cobre despesas fixas
              </p>
            </CardBody>
          </Card>
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
              </div>
            </CardBody>
          </Card>

          {/* Category Breakdown */}
          <Card>
            <CardHeader title="Por Categoria" subtitle="Receitas e Despesas" />
            <CardBody>
              <div className="space-y-4">
                {categoryBreakdown.map((item) => {
                  const total = item.income + item.expense;
                  const incomePercent = total > 0 ? (item.income / total) * 100 : 0;
                  return (
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
                  );
                })}
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
              <div className="divide-y divide-border">
                {cashflowItems.slice(0, 6).map((item) => (
                  <div
                    key={item.description}
                    className="flex items-center justify-between px-6 py-3 hover:bg-bg-tertiary/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`p-2 rounded-lg ${
                          item.type === 'income' ? 'bg-success/10' : 'bg-danger/10'
                        }`}
                      >
                        {item.type === 'income' ? (
                          <ArrowUpRight className="w-4 h-4 text-success" />
                        ) : (
                          <ArrowDownRight className="w-4 h-4 text-danger" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{item.description}</p>
                        <p className="text-xs text-text-muted">{item.category}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p
                          className={`font-mono font-medium ${
                            item.type === 'income' ? 'text-success' : 'text-danger'
                          }`}
                        >
                          {item.type === 'income' ? '+' : '-'}
                          {item.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </p>
                        <p className="text-xs text-text-muted">
                          {new Date(item.date).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      <Badge
                        variant={item.status === 'realized' ? 'success' : 'warning'}
                        size="sm"
                      >
                        {item.status === 'realized' ? 'Realizado' : 'Projetado'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Alerts */}
        <div className="grid grid-cols-2 gap-4">
          <Card className="border-warning/30 bg-warning/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-warning/10">
                  <AlertTriangle className="w-6 h-6 text-warning" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    Dia 20/01 terá saldo negativo projetado
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Saídas de R$ 60.000 superam entradas previstas
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Antecipar Recebimentos
                </Button>
              </div>
            </CardBody>
          </Card>

          <Card className="border-success/30 bg-success/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-success/10">
                  <CheckCircle2 className="w-6 h-6 text-success" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    Saldo final do mês projetado positivo
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Previsão de R$ 600.500 no dia 31/01
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Ver Projeção
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
