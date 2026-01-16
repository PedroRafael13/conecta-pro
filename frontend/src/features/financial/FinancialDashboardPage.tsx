'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  CreditCard,
  Building2,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  PieChart,
  BarChart3,
  Wallet,
  Receipt,
  ArrowRightLeft,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
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

// Mock Data
const cashflowData = [
  { month: 'Jul', receitas: 485000, despesas: 320000, saldo: 165000 },
  { month: 'Ago', receitas: 520000, despesas: 340000, saldo: 180000 },
  { month: 'Set', receitas: 510000, despesas: 355000, saldo: 155000 },
  { month: 'Out', receitas: 545000, despesas: 360000, saldo: 185000 },
  { month: 'Nov', receitas: 580000, despesas: 380000, saldo: 200000 },
  { month: 'Dez', receitas: 620000, despesas: 410000, saldo: 210000 },
  { month: 'Jan', receitas: 595000, despesas: 385000, saldo: 210000 },
];

const expensesByCategory = [
  { name: 'Folha de Pagamento', value: 245000, color: '#6366f1' },
  { name: 'Fornecedores', value: 85000, color: '#8b5cf6' },
  { name: 'Impostos', value: 42000, color: '#ec4899' },
  { name: 'Operacional', value: 28000, color: '#14b8a6' },
  { name: 'Administrativo', value: 18000, color: '#f59e0b' },
  { name: 'Outros', value: 12000, color: '#64748b' },
];

const revenueByClient = [
  { name: 'Shopping Center Norte', value: 128000 },
  { name: 'Hospital São Lucas', value: 95000 },
  { name: 'Tech Park', value: 67000 },
  { name: 'Condomínio Aurora', value: 45000 },
  { name: 'Outros', value: 260000 },
];

interface Transaction {
  id: string;
  description: string;
  category: string;
  type: 'income' | 'expense';
  value: number;
  date: string;
  status: 'completed' | 'pending' | 'scheduled';
  account: string;
}

const recentTransactions: Transaction[] = [
  {
    id: '1',
    description: 'Pagamento - Shopping Center Norte',
    category: 'Receita',
    type: 'income',
    value: 128000,
    date: '2026-01-15',
    status: 'completed',
    account: 'Itaú Empresas',
  },
  {
    id: '2',
    description: 'Folha de Pagamento - Janeiro',
    category: 'RH',
    type: 'expense',
    value: 245000,
    date: '2026-01-10',
    status: 'completed',
    account: 'Bradesco PJ',
  },
  {
    id: '3',
    description: 'Uniforme - Lote 2026/01',
    category: 'Fornecedor',
    type: 'expense',
    value: 18500,
    date: '2026-01-18',
    status: 'pending',
    account: 'Itaú Empresas',
  },
  {
    id: '4',
    description: 'Pagamento - Hospital São Lucas',
    category: 'Receita',
    type: 'income',
    value: 95000,
    date: '2026-01-20',
    status: 'scheduled',
    account: 'Itaú Empresas',
  },
  {
    id: '5',
    description: 'INSS Competência 12/2025',
    category: 'Imposto',
    type: 'expense',
    value: 42000,
    date: '2026-01-20',
    status: 'scheduled',
    account: 'Bradesco PJ',
  },
];

const transactionColumns: Column<Transaction>[] = [
  {
    key: 'description',
    header: 'Descrição',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${row.type === 'income' ? 'bg-success/10' : 'bg-danger/10'}`}>
          {row.type === 'income' ? (
            <ArrowUpRight className="w-4 h-4 text-success" />
          ) : (
            <ArrowDownRight className="w-4 h-4 text-danger" />
          )}
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.description}</p>
          <p className="text-xs text-text-muted">{row.category}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'value',
    header: 'Valor',
    render: (row) => (
      <span className={`font-mono font-medium ${row.type === 'income' ? 'text-success' : 'text-danger'}`}>
        {row.type === 'income' ? '+' : '-'}
        {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'date',
    header: 'Data',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {new Date(row.date).toLocaleDateString('pt-BR')}
      </span>
    ),
  },
  {
    key: 'account',
    header: 'Conta',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Building2 className="w-4 h-4 text-text-muted" />
        <span className="text-sm text-text-secondary">{row.account}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = {
        completed: { label: 'Concluído', color: 'success' as const, icon: CheckCircle2 },
        pending: { label: 'Pendente', color: 'warning' as const, icon: Clock },
        scheduled: { label: 'Agendado', color: 'info' as const, icon: Calendar },
      };
      const status = config[row.status];
      return (
        <Badge variant={status.color} leftIcon={<status.icon className="w-3 h-3" />}>
          {status.label}
        </Badge>
      );
    },
  },
];

export function FinancialDashboardPage() {
  const [period, setPeriod] = useState('month');

  // Calculate totals
  const totalReceitas = 595000;
  const totalDespesas = 385000;
  const saldoAtual = totalReceitas - totalDespesas;
  const contasReceber = 280000;
  const contasPagar = 145000;

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
          <Card className="bg-gradient-to-br from-success/10 to-bg-secondary border-success/20">
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-success/10">
                  <TrendingUp className="w-5 h-5 text-success" />
                </div>
                <span className="text-xs text-text-muted">Receitas</span>
              </div>
              <p className="text-2xl font-mono font-bold text-success">
                {totalReceitas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-success mt-1">+12.5% vs mês anterior</p>
            </CardBody>
          </Card>

          <Card className="bg-gradient-to-br from-danger/10 to-bg-secondary border-danger/20">
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-danger/10">
                  <TrendingDown className="w-5 h-5 text-danger" />
                </div>
                <span className="text-xs text-text-muted">Despesas</span>
              </div>
              <p className="text-2xl font-mono font-bold text-danger">
                {totalDespesas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-danger mt-1">+8.2% vs mês anterior</p>
            </CardBody>
          </Card>

          <Card className="bg-gradient-to-br from-accent-primary/10 to-bg-secondary border-accent-primary/20">
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-accent-primary/10">
                  <Wallet className="w-5 h-5 text-accent-primary" />
                </div>
                <span className="text-xs text-text-muted">Saldo</span>
              </div>
              <p className="text-2xl font-mono font-bold text-accent-primary">
                {saldoAtual.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-accent-primary mt-1">Margem: 35.3%</p>
            </CardBody>
          </Card>

          <Card className="bg-gradient-to-br from-info/10 to-bg-secondary border-info/20">
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-info/10">
                  <ArrowUpRight className="w-5 h-5 text-info" />
                </div>
                <span className="text-xs text-text-muted">A Receber</span>
              </div>
              <p className="text-2xl font-mono font-bold text-info">
                {contasReceber.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-text-muted mt-1">15 títulos</p>
            </CardBody>
          </Card>

          <Card className="bg-gradient-to-br from-warning/10 to-bg-secondary border-warning/20">
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-warning/10">
                  <ArrowDownRight className="w-5 h-5 text-warning" />
                </div>
                <span className="text-xs text-text-muted">A Pagar</span>
              </div>
              <p className="text-2xl font-mono font-bold text-warning">
                {contasPagar.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
              <p className="text-xs text-text-muted mt-1">8 títulos</p>
            </CardBody>
          </Card>
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
            <CardHeader title="Despesas por Categoria" subtitle="Janeiro 2026" />
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
                      {expensesByCategory.map((entry, index) => (
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
                {expensesByCategory.slice(0, 4).map((item) => (
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
              <DataTable
                columns={transactionColumns}
                data={recentTransactions}
                keyExtractor={(row) => row.id}
              />
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
                  <p className="font-medium text-text-primary">3 títulos vencem esta semana</p>
                  <p className="text-sm text-text-secondary mt-1">
                    Total de R$ 65.500,00 em contas a pagar
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Ver Títulos
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
                  <p className="font-medium text-text-primary">Conciliação bancária atualizada</p>
                  <p className="text-sm text-text-secondary mt-1">
                    Última sincronização há 2 horas
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Conciliar Agora
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
