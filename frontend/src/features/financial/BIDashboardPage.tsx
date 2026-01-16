'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  Download,
  RefreshCw,
  Settings,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  Maximize2,
  GripVertical,
  Sparkles,
  Target,
  Users,
  Building2,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Modal,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Dropdown,
  Input,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts';

// Types
interface KPI {
  id: string;
  name: string;
  value: string | number;
  change: number;
  trend: 'up' | 'down';
  target?: number;
  unit?: string;
  category: string;
}

interface Widget {
  id: string;
  type: 'chart' | 'kpi' | 'table' | 'gauge';
  title: string;
  size: 'small' | 'medium' | 'large';
  data: any;
}

// Mock Data
const revenueData = [
  { month: 'Jul', receita: 980000, despesa: 720000, lucro: 260000 },
  { month: 'Ago', receita: 1050000, despesa: 780000, lucro: 270000 },
  { month: 'Set', receita: 1120000, despesa: 810000, lucro: 310000 },
  { month: 'Out', receita: 1180000, despesa: 850000, lucro: 330000 },
  { month: 'Nov', receita: 1250000, despesa: 890000, lucro: 360000 },
  { month: 'Dez', receita: 1320000, despesa: 940000, lucro: 380000 },
  { month: 'Jan', receita: 1245000, despesa: 895000, lucro: 350000 },
];

const expenseBreakdown = [
  { name: 'Folha de Pagamento', value: 456000, color: '#6366f1' },
  { name: 'Fornecedores', value: 189000, color: '#10b981' },
  { name: 'Operacional', value: 98000, color: '#f59e0b' },
  { name: 'Impostos', value: 87000, color: '#ef4444' },
  { name: 'Outros', value: 65000, color: '#8b5cf6' },
];

const clientRevenue = [
  { cliente: 'Shopping Norte', valor: 128000 },
  { cliente: 'Tech Park', valor: 89000 },
  { cliente: 'Universidade', valor: 67000 },
  { cliente: 'Condomínio Aurora', valor: 45000 },
  { cliente: 'Hospital Central', valor: 38000 },
];

const cashflowData = [
  { dia: '01', entradas: 85000, saidas: 62000, saldo: 23000 },
  { dia: '05', entradas: 120000, saidas: 95000, saldo: 48000 },
  { dia: '10', entradas: 95000, saidas: 78000, saldo: 65000 },
  { dia: '15', entradas: 150000, saidas: 180000, saldo: 35000 },
  { dia: '20', entradas: 110000, saidas: 85000, saldo: 60000 },
  { dia: '25', entradas: 140000, saidas: 92000, saldo: 108000 },
  { dia: '30', entradas: 180000, saidas: 145000, saldo: 143000 },
];

const kpis: KPI[] = [
  { id: '1', name: 'Receita Mensal', value: 'R$ 1.245.678', change: 12.5, trend: 'up', target: 1300000, category: 'Receita' },
  { id: '2', name: 'Margem Líquida', value: '28.3%', change: 2.1, trend: 'up', target: 30, category: 'Margem' },
  { id: '3', name: 'Inadimplência', value: '3.2%', change: -0.8, trend: 'down', target: 3, category: 'Risco' },
  { id: '4', name: 'Ticket Médio', value: 'R$ 45.890', change: 5.3, trend: 'up', target: 50000, category: 'Vendas' },
  { id: '5', name: 'Clientes Ativos', value: 27, change: 2, trend: 'up', target: 30, category: 'Clientes' },
  { id: '6', name: 'ROI', value: '156%', change: 12, trend: 'up', target: 150, category: 'Retorno' },
];

const periods = [
  { value: 'today', label: 'Hoje' },
  { value: 'week', label: 'Esta Semana' },
  { value: 'month', label: 'Este Mês' },
  { value: 'quarter', label: 'Este Trimestre' },
  { value: 'year', label: 'Este Ano' },
  { value: 'custom', label: 'Personalizado' },
];

export function BIDashboardPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [configModalOpen, setConfigModalOpen] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsRefreshing(false);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-accent-primary" />
              Business Intelligence
            </h1>
            <p className="text-text-secondary mt-1">
              Dashboard analítico com KPIs configuráveis
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary text-sm"
            >
              {periods.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
            <Button
              variant="secondary"
              leftIcon={<RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />}
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              Atualizar
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant={editMode ? 'primary' : 'secondary'}
              leftIcon={<Edit className="w-4 h-4" />}
              onClick={() => setEditMode(!editMode)}
            >
              {editMode ? 'Salvar' : 'Editar'}
            </Button>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-6 gap-4">
          {kpis.map((kpi, idx) => (
            <motion.div
              key={kpi.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
            >
              <Card className={`${editMode ? 'cursor-move border-dashed' : ''}`}>
                <CardBody className="p-4">
                  {editMode && (
                    <div className="absolute top-2 right-2">
                      <GripVertical className="w-4 h-4 text-text-muted" />
                    </div>
                  )}
                  <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
                    {kpi.name}
                  </p>
                  <p className="text-xl font-bold text-text-primary">{kpi.value}</p>
                  <div className="flex items-center gap-1 mt-1">
                    {kpi.trend === 'up' ? (
                      <ArrowUpRight className="w-4 h-4 text-green-500" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4 text-red-500" />
                    )}
                    <span
                      className={`text-sm ${
                        kpi.trend === 'up' ? 'text-green-500' : 'text-red-500'
                      }`}
                    >
                      {kpi.change > 0 ? '+' : ''}
                      {kpi.change}%
                    </span>
                  </div>
                </CardBody>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="dashboard" label="Dashboard" />
          <Tab value="revenue" label="Receitas" />
          <Tab value="expenses" label="Despesas" />
          <Tab value="cashflow" label="Fluxo de Caixa" />
          <Tab value="clients" label="Clientes" />
        </Tabs>

        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-3 gap-6">
            {/* Revenue Chart */}
            <Card className="col-span-2">
              <CardHeader
                title="Receita vs Despesa"
                subtitle="Últimos 7 meses"
                action={
                  editMode ? (
                    <Button variant="ghost" size="sm">
                      <Maximize2 className="w-4 h-4" />
                    </Button>
                  ) : undefined
                }
              />
              <CardBody>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={revenueData}>
                      <defs>
                        <linearGradient id="colorReceita" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorDespesa" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="receita"
                        name="Receita"
                        stroke="#10b981"
                        fillOpacity={1}
                        fill="url(#colorReceita)"
                      />
                      <Area
                        type="monotone"
                        dataKey="despesa"
                        name="Despesa"
                        stroke="#ef4444"
                        fillOpacity={1}
                        fill="url(#colorDespesa)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            {/* Expense Breakdown */}
            <Card>
              <CardHeader title="Composição de Despesas" />
              <CardBody>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={expenseBreakdown}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        dataKey="value"
                        nameKey="name"
                      >
                        {expenseBreakdown.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-2 mt-4">
                  {expenseBreakdown.map((item) => (
                    <div key={item.name} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-text-muted">{item.name}</span>
                      </div>
                      <span className="text-text-primary">{formatCurrency(item.value)}</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Cashflow Chart */}
            <Card className="col-span-2">
              <CardHeader title="Fluxo de Caixa Diário" subtitle="Janeiro 2026" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={cashflowData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="dia" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="entradas" name="Entradas" stroke="#10b981" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="saidas" name="Saídas" stroke="#ef4444" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="saldo" name="Saldo" stroke="#6366f1" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            {/* Top Clients */}
            <Card>
              <CardHeader title="Top 5 Clientes" subtitle="Por receita" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={clientRevenue} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis type="number" stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                      <YAxis type="category" dataKey="cliente" stroke="#64748b" fontSize={10} width={100} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Bar dataKey="valor" fill="#6366f1" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            {/* AI Insights */}
            <Card className="col-span-3">
              <CardHeader
                title="Insights de IA"
                subtitle="Análises automáticas baseadas nos dados"
                action={
                  <Badge variant="success" leftIcon={<Sparkles className="w-3 h-3" />}>
                    4 novos insights
                  </Badge>
                }
              />
              <CardBody>
                <div className="grid grid-cols-4 gap-4">
                  {[
                    {
                      title: 'Tendência de Receita',
                      description: 'Receita deve crescer 8% no próximo mês baseado no histórico',
                      icon: TrendingUp,
                      color: 'green',
                    },
                    {
                      title: 'Alerta de Inadimplência',
                      description: '3 clientes com risco elevado de atraso identificados',
                      icon: Target,
                      color: 'yellow',
                    },
                    {
                      title: 'Otimização de Custos',
                      description: 'Potencial economia de R$ 15k em despesas operacionais',
                      icon: DollarSign,
                      color: 'blue',
                    },
                    {
                      title: 'Oportunidade',
                      description: 'Cliente Tech Park apresenta potencial de upsell de 20%',
                      icon: Users,
                      color: 'purple',
                    },
                  ].map((insight, idx) => (
                    <div
                      key={idx}
                      className={`p-4 bg-${insight.color}-500/10 rounded-lg border border-${insight.color}-500/30`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <insight.icon className={`w-5 h-5 text-${insight.color}-500`} />
                        <span className="font-medium text-text-primary text-sm">{insight.title}</span>
                      </div>
                      <p className="text-xs text-text-muted">{insight.description}</p>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'revenue' && (
          <Card>
            <CardHeader title="Análise de Receitas" />
            <CardBody>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Legend />
                    <Bar dataKey="receita" name="Receita" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="lucro" name="Lucro" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'expenses' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Despesas por Categoria" />
              <CardBody>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={expenseBreakdown}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {expenseBreakdown.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Detalhamento" />
              <CardBody>
                <div className="space-y-4">
                  {expenseBreakdown.map((item) => (
                    <div key={item.name} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="font-medium text-text-primary">{item.name}</span>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-text-primary">{formatCurrency(item.value)}</p>
                        <p className="text-xs text-text-muted">
                          {((item.value / expenseBreakdown.reduce((s, i) => s + i.value, 0)) * 100).toFixed(1)}% do total
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'cashflow' && (
          <Card>
            <CardHeader title="Fluxo de Caixa Detalhado" />
            <CardBody>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={cashflowData}>
                    <defs>
                      <linearGradient id="colorSaldo" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="dia" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="saldo"
                      name="Saldo"
                      stroke="#6366f1"
                      fillOpacity={1}
                      fill="url(#colorSaldo)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'clients' && (
          <Card>
            <CardHeader title="Receita por Cliente" />
            <CardBody>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={clientRevenue}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="cliente" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Bar dataKey="valor" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        )}
      </div>

      {/* Config Modal */}
      <Modal
        isOpen={configModalOpen}
        onClose={() => setConfigModalOpen(false)}
        title="Configurar Dashboard"
        size="lg"
      >
        <div className="space-y-4">
          <p className="text-text-muted">Configure os widgets e KPIs do seu dashboard.</p>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setConfigModalOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              Salvar
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}

export default BIDashboardPage;
