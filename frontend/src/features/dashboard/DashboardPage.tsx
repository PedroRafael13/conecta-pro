'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  Users,
  FileText,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  MoreHorizontal,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Briefcase,
  Activity,
  Target,
  Zap,
  Bell,
  Settings,
  RefreshCw,
  Eye,
  Building2,
  UserCheck,
  Shield,
  AlertCircle,
  PieChart as PieChartIcon,
  BarChart3,
  MapPin,
  Phone,
  Mail,
  Star,
  ThumbsUp,
  MessageSquare,
  Wallet,
  CreditCard,
  Receipt,
  CircleDollarSign,
  ChevronRight,
  ExternalLink,
  Filter,
  Download,
  Play,
  Pause,
  XCircle,
  CheckCircle,
  Info,
  Sparkles,
  Brain,
  Bot
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  StatCard,
  Badge,
  Button,
  Avatar,
  DataTable,
  SimpleTabBar,
  Input,
  Select,
  Modal
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  Legend,
  RadialBarChart,
  RadialBar,
  ComposedChart
} from 'recharts';

// ==================== TYPES ====================

interface RecentContract {
  id: string;
  client: string;
  clientLogo?: string;
  type: string;
  value: number;
  status: 'active' | 'pending' | 'renewal' | 'negotiation';
  date: string;
  responsavel: string;
}

interface Alert {
  id: string;
  type: 'warning' | 'danger' | 'info' | 'success';
  title: string;
  description: string;
  timestamp: string;
  link?: string;
  priority: 'high' | 'medium' | 'low';
}

interface ActivityItem {
  id: string;
  type: 'contract' | 'payment' | 'employee' | 'client' | 'task' | 'system';
  title: string;
  description: string;
  timestamp: string;
  user: string;
  userAvatar?: string;
}

interface TopClient {
  id: string;
  name: string;
  revenue: number;
  contracts: number;
  satisfaction: number;
  trend: 'up' | 'down' | 'stable';
}

interface PerformanceMetric {
  name: string;
  atual: number;
  meta: number;
  percentual: number;
}

interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

// ==================== MOCK DATA ====================

// Revenue data for chart
const revenueData = [
  { month: 'Jul', receita: 185000, despesa: 120000, lucro: 65000 },
  { month: 'Ago', receita: 210000, despesa: 135000, lucro: 75000 },
  { month: 'Set', receita: 195000, despesa: 128000, lucro: 67000 },
  { month: 'Out', receita: 240000, despesa: 145000, lucro: 95000 },
  { month: 'Nov', receita: 225000, despesa: 140000, lucro: 85000 },
  { month: 'Dez', receita: 280000, despesa: 160000, lucro: 120000 },
  { month: 'Jan', receita: 295000, despesa: 165000, lucro: 130000 },
];

const contractsStatusData = [
  { name: 'Ativos', value: 45, color: '#10b981' },
  { name: 'Em Renovação', value: 12, color: '#f59e0b' },
  { name: 'Em Negociação', value: 8, color: '#6366f1' },
  { name: 'Encerrados', value: 5, color: '#64748b' },
];

const departmentData = [
  { dept: 'Segurança', funcionarios: 145, alocados: 140, disponiveis: 5 },
  { dept: 'Limpeza', funcionarios: 89, alocados: 85, disponiveis: 4 },
  { dept: 'Manutenção', funcionarios: 34, alocados: 32, disponiveis: 2 },
  { dept: 'Portaria', funcionarios: 67, alocados: 65, disponiveis: 2 },
  { dept: 'Admin', funcionarios: 23, alocados: 23, disponiveis: 0 },
];

const cashflowData = [
  { day: 'Seg', entradas: 45000, saidas: 28000 },
  { day: 'Ter', entradas: 52000, saidas: 31000 },
  { day: 'Qua', entradas: 38000, saidas: 42000 },
  { day: 'Qui', entradas: 61000, saidas: 35000 },
  { day: 'Sex', entradas: 48000, saidas: 29000 },
  { day: 'Sáb', entradas: 15000, saidas: 8000 },
  { day: 'Dom', entradas: 5000, saidas: 3000 },
];

const serviceTypeData = [
  { name: 'Segurança Patrimonial', value: 35 },
  { name: 'Limpeza e Conservação', value: 28 },
  { name: 'Facilities', value: 18 },
  { name: 'Portaria', value: 12 },
  { name: 'Manutenção', value: 7 },
];

const performanceData: PerformanceMetric[] = [
  { name: 'Receita', atual: 295000, meta: 300000, percentual: 98 },
  { name: 'Novos Contratos', atual: 8, meta: 10, percentual: 80 },
  { name: 'Retenção', atual: 95, meta: 90, percentual: 105 },
  { name: 'NPS', atual: 72, meta: 70, percentual: 103 },
  { name: 'Cobertura', atual: 97, meta: 98, percentual: 99 },
];

const gaugeData = [
  { name: 'Receita', value: 98, fill: '#10b981' },
  { name: 'Contratos', value: 80, fill: '#6366f1' },
  { name: 'Satisfação', value: 92, fill: '#f59e0b' },
];

const recentContracts: RecentContract[] = [
  {
    id: 'CTR001',
    client: 'Condomínio Aurora',
    type: 'Segurança',
    value: 45000,
    status: 'active',
    date: '15/01/2026',
    responsavel: 'João Silva'
  },
  {
    id: 'CTR002',
    client: 'Shopping Center Norte',
    type: 'Limpeza',
    value: 78000,
    status: 'pending',
    date: '14/01/2026',
    responsavel: 'Maria Santos'
  },
  {
    id: 'CTR003',
    client: 'Empresa Tech SA',
    type: 'Facilities',
    value: 32000,
    status: 'renewal',
    date: '13/01/2026',
    responsavel: 'Pedro Costa'
  },
  {
    id: 'CTR004',
    client: 'Hospital São Lucas',
    type: 'Segurança',
    value: 95000,
    status: 'active',
    date: '12/01/2026',
    responsavel: 'Ana Lima'
  },
  {
    id: 'CTR005',
    client: 'Universidade Federal',
    type: 'Manutenção',
    value: 54000,
    status: 'negotiation',
    date: '11/01/2026',
    responsavel: 'Carlos Mendes'
  },
];

const alerts: Alert[] = [
  {
    id: 'ALT001',
    type: 'danger',
    title: '5 Faturas em Atraso',
    description: 'Total de R$ 45.000,00 pendente há mais de 30 dias',
    timestamp: '2 horas atrás',
    link: '/financial/receivables',
    priority: 'high'
  },
  {
    id: 'ALT002',
    type: 'warning',
    title: '3 Contratos p/ Renovar',
    description: 'Vencem nos próximos 30 dias',
    timestamp: '4 horas atrás',
    link: '/crm/contracts',
    priority: 'high'
  },
  {
    id: 'ALT003',
    type: 'info',
    title: 'Integração eSocial',
    description: '12 eventos aguardando envio',
    timestamp: '5 horas atrás',
    link: '/compliance/esocial',
    priority: 'medium'
  },
  {
    id: 'ALT004',
    type: 'warning',
    title: 'Equipamentos p/ Manutenção',
    description: '8 equipamentos com manutenção vencida',
    timestamp: '1 dia atrás',
    link: '/equipment/maintenance',
    priority: 'medium'
  },
  {
    id: 'ALT005',
    type: 'success',
    title: 'Meta de Janeiro Atingida',
    description: 'Receita superou meta em 5%',
    timestamp: '2 dias atrás',
    priority: 'low'
  },
];

const activityFeed: ActivityItem[] = [
  {
    id: 'ACT001',
    type: 'contract',
    title: 'Novo contrato assinado',
    description: 'Hospital São Lucas - Segurança 24h',
    timestamp: '10 min atrás',
    user: 'Ana Lima'
  },
  {
    id: 'ACT002',
    type: 'payment',
    title: 'Pagamento recebido',
    description: 'Shopping Center Norte - R$ 78.000,00',
    timestamp: '25 min atrás',
    user: 'Sistema'
  },
  {
    id: 'ACT003',
    type: 'employee',
    title: 'Funcionário admitido',
    description: 'Roberto Almeida - Segurança',
    timestamp: '1 hora atrás',
    user: 'Maria Santos'
  },
  {
    id: 'ACT004',
    type: 'task',
    title: 'Ordem de serviço concluída',
    description: 'OS #4521 - Manutenção preventiva',
    timestamp: '2 horas atrás',
    user: 'Pedro Costa'
  },
  {
    id: 'ACT005',
    type: 'client',
    title: 'Novo lead cadastrado',
    description: 'Condomínio Ville Park - Facilities',
    timestamp: '3 horas atrás',
    user: 'João Silva'
  },
  {
    id: 'ACT006',
    type: 'system',
    title: 'Backup automático concluído',
    description: 'Todos os dados foram salvos com sucesso',
    timestamp: '4 horas atrás',
    user: 'Sistema'
  },
];

const topClients: TopClient[] = [
  { id: '1', name: 'Hospital São Lucas', revenue: 95000, contracts: 3, satisfaction: 98, trend: 'up' },
  { id: '2', name: 'Shopping Center Norte', revenue: 78000, contracts: 2, satisfaction: 92, trend: 'stable' },
  { id: '3', name: 'Universidade Federal', revenue: 54000, contracts: 2, satisfaction: 88, trend: 'up' },
  { id: '4', name: 'Condomínio Aurora', revenue: 45000, contracts: 1, satisfaction: 95, trend: 'up' },
  { id: '5', name: 'Empresa Tech SA', revenue: 32000, contracts: 1, satisfaction: 90, trend: 'down' },
];

const upcomingEvents = [
  { id: '1', title: 'Reunião com Hospital São Lucas', date: '16/01', time: '10:00', type: 'meeting' },
  { id: '2', title: 'Vencimento Contrato Aurora', date: '20/01', time: '-', type: 'contract' },
  { id: '3', title: 'Treinamento Equipe Segurança', date: '22/01', time: '14:00', type: 'training' },
  { id: '4', title: 'Entrega Proposta Tech SA', date: '25/01', time: '09:00', type: 'proposal' },
];

const aiInsights = [
  {
    id: '1',
    title: 'Oportunidade de Upsell',
    description: 'Hospital São Lucas pode aumentar contrato em 30% baseado no crescimento recente',
    confidence: 87,
    action: 'Agendar reunião'
  },
  {
    id: '2',
    title: 'Risco de Churn',
    description: 'Empresa Tech SA apresenta sinais de insatisfação nos últimos 30 dias',
    confidence: 72,
    action: 'Contatar cliente'
  },
  {
    id: '3',
    title: 'Otimização de Escala',
    description: 'Realocação de 3 funcionários pode reduzir custos em 8%',
    confidence: 91,
    action: 'Ver detalhes'
  },
];

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const getAlertIcon = (type: string) => {
  switch (type) {
    case 'danger': return <XCircle className="h-5 w-5 text-accent-danger" />;
    case 'warning': return <AlertTriangle className="h-5 w-5 text-accent-warning" />;
    case 'success': return <CheckCircle className="h-5 w-5 text-accent-success" />;
    default: return <Info className="h-5 w-5 text-accent-info" />;
  }
};

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'contract': return <FileText className="h-4 w-4" />;
    case 'payment': return <DollarSign className="h-4 w-4" />;
    case 'employee': return <Users className="h-4 w-4" />;
    case 'task': return <CheckCircle2 className="h-4 w-4" />;
    case 'client': return <Building2 className="h-4 w-4" />;
    default: return <Settings className="h-4 w-4" />;
  }
};

const getStatusBadge = (status: string) => {
  const config: Record<string, { label: string; variant: any }> = {
    active: { label: 'Ativo', variant: 'success' },
    pending: { label: 'Pendente', variant: 'warning' },
    renewal: { label: 'Renovação', variant: 'info' },
    negotiation: { label: 'Negociação', variant: 'primary' },
  };
  const { label, variant } = config[status] || { label: status, variant: 'neutral' };
  return <Badge variant={variant}>{label}</Badge>;
};

// Custom Tooltip for charts
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-3 shadow-lg">
        <p className="text-text-secondary text-sm mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === 'number' && entry.value > 1000
              ? formatCurrency(entry.value)
              : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// ==================== COMPONENT ====================

export function DashboardPage() {
  const [period, setPeriod] = useState('month');
  const [showAIInsights, setShowAIInsights] = useState(true);

  const contractColumns: Column<RecentContract>[] = [
    {
      key: 'client',
      header: 'Cliente',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.client} size="sm" />
          <div>
            <p className="font-medium text-text-primary">{row.client}</p>
            <p className="text-xs text-text-secondary">{row.id}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => <span className="text-text-secondary">{row.type}</span>
    },
    {
      key: 'value',
      header: 'Valor Mensal',
      render: (row) => (
        <span className="font-mono font-medium text-text-primary">
          {formatCurrency(row.value)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status),
    },
    {
      key: 'responsavel',
      header: 'Responsável',
      render: (row) => <span className="text-text-secondary">{row.responsavel}</span>
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => <span className="text-text-secondary">{row.date}</span>
    },
    {
      key: 'actions',
      header: '',
      render: () => (
        <Button variant="ghost" size="sm">
          <Eye className="h-4 w-4" />
        </Button>
      ),
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Dashboard Executivo
            </h1>
            <p className="text-text-secondary mt-1">
              Visão geral do desempenho do Conecta PRO • Atualizado há 5 minutos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              options={[
                { value: 'today', label: 'Hoje' },
                { value: 'week', label: 'Esta Semana' },
                { value: 'month', label: 'Este Mês' },
                { value: 'quarter', label: 'Este Trimestre' },
                { value: 'year', label: 'Este Ano' },
              ]}
              value={period}
              onChange={setPeriod}
            />
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Atualizar
            </Button>
          </div>
        </div>

        {/* AI Insights Banner */}
        {showAIInsights && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 border-accent-primary/30">
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-accent-primary/20">
                      <Brain className="h-6 w-6 text-accent-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-text-primary flex items-center gap-2">
                        Insights da IA
                        <Badge variant="primary">3 novos</Badge>
                      </h3>
                      <p className="text-sm text-text-secondary">
                        Análise preditiva identificou oportunidades e riscos
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="primary" size="sm">
                      <Sparkles className="h-4 w-4 mr-2" />
                      Ver Insights
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setShowAIInsights(false)}>
                      <XCircle className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mt-4">
                  {aiInsights.map((insight) => (
                    <div
                      key={insight.id}
                      className="p-3 rounded-lg bg-bg-secondary/50 border border-border-subtle"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-text-primary">{insight.title}</span>
                        <Badge variant="outline">{insight.confidence}%</Badge>
                      </div>
                      <p className="text-xs text-text-secondary mb-3">{insight.description}</p>
                      <Button variant="outline" size="sm" className="w-full">
                        {insight.action}
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Main Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Receita Mensal"
              value="R$ 295.000"
              change={12.5}
              changeLabel="vs mês anterior"
              icon={<DollarSign className="h-5 w-5" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Contratos Ativos"
              value="70"
              change={8.2}
              changeLabel="+5 novos"
              icon={<FileText className="h-5 w-5" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Funcionários Ativos"
              value="358"
              change={3.1}
              changeLabel="97% alocados"
              icon={<Users className="h-5 w-5" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Inadimplência"
              value="2.3%"
              change={-15.4}
              changeLabel="redução"
              icon={<TrendingDown className="h-5 w-5" />}
              iconColor="warning"
            />
          </motion.div>
        </div>

        {/* Secondary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent-success/20">
                <Wallet className="h-5 w-5 text-accent-success" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">R$ 1.2M</p>
                <p className="text-xs text-text-secondary">A Receber</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent-danger/20">
                <CreditCard className="h-5 w-5 text-accent-danger" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">R$ 890K</p>
                <p className="text-xs text-text-secondary">A Pagar</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent-primary/20">
                <Target className="h-5 w-5 text-accent-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">98%</p>
                <p className="text-xs text-text-secondary">Meta Atingida</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent-warning/20">
                <Star className="h-5 w-5 text-accent-warning" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">4.8</p>
                <p className="text-xs text-text-secondary">NPS Score</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent-info/20">
                <Activity className="h-5 w-5 text-accent-info" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">156</p>
                <p className="text-xs text-text-secondary">OS Abertas</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent-secondary/20">
                <UserCheck className="h-5 w-5 text-accent-secondary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-text-primary">12</p>
                <p className="text-xs text-text-secondary">Leads Quentes</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Revenue Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="lg:col-span-2"
          >
            <Card className="h-full">
              <CardHeader
                title="Receita vs Despesa"
                description="Evolução mensal dos últimos 7 meses"
                action={
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-5 w-5" />
                  </Button>
                }
              />
              <CardBody>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={revenueData}>
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
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="receita"
                        name="Receita"
                        stroke="#10b981"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorReceita)"
                      />
                      <Area
                        type="monotone"
                        dataKey="despesa"
                        name="Despesa"
                        stroke="#ef4444"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorDespesa)"
                      />
                      <Line
                        type="monotone"
                        dataKey="lucro"
                        name="Lucro"
                        stroke="#6366f1"
                        strokeWidth={2}
                        dot={{ fill: '#6366f1' }}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          {/* Contracts Pie Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card className="h-full">
              <CardHeader
                title="Status dos Contratos"
                action={
                  <Badge variant="primary">70 total</Badge>
                }
              />
              <CardBody>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={contractsStatusData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={70}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {contractsStatusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-2 mt-4">
                  {contractsStatusData.map((item) => (
                    <div key={item.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-sm text-text-secondary">{item.name}</span>
                      </div>
                      <span className="text-sm font-medium text-text-primary">{item.value}</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cashflow Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card className="h-full">
              <CardHeader
                title="Fluxo de Caixa Semanal"
                description="Entradas vs Saídas"
              />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={cashflowData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Bar dataKey="entradas" name="Entradas" fill="#10b981" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="saidas" name="Saídas" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          {/* Department Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Card className="h-full">
              <CardHeader title="Funcionários por Setor" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={departmentData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" horizontal={false} />
                      <XAxis type="number" stroke="#64748b" fontSize={12} />
                      <YAxis dataKey="dept" type="category" stroke="#64748b" fontSize={12} width={80} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Bar dataKey="alocados" name="Alocados" fill="#6366f1" radius={[0, 4, 4, 0]} stackId="a" />
                      <Bar dataKey="disponiveis" name="Disponíveis" fill="#10b981" radius={[0, 4, 4, 0]} stackId="a" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          {/* Performance Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <Card className="h-full">
              <CardHeader title="Metas do Mês" />
              <CardBody>
                <div className="space-y-4">
                  {performanceData.map((metric) => (
                    <div key={metric.name}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-text-secondary">{metric.name}</span>
                        <span className={`text-sm font-medium ${
                          metric.percentual >= 100 ? 'text-accent-success' :
                          metric.percentual >= 80 ? 'text-accent-warning' : 'text-accent-danger'
                        }`}>
                          {metric.percentual}%
                        </span>
                      </div>
                      <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            metric.percentual >= 100 ? 'bg-accent-success' :
                            metric.percentual >= 80 ? 'bg-accent-warning' : 'bg-accent-danger'
                          }`}
                          style={{ width: `${Math.min(metric.percentual, 100)}%` }}
                        />
                      </div>
                      <div className="flex justify-between mt-1">
                        <span className="text-xs text-text-muted">
                          Atual: {typeof metric.atual === 'number' && metric.atual > 100
                            ? formatCurrency(metric.atual)
                            : metric.atual}
                        </span>
                        <span className="text-xs text-text-muted">
                          Meta: {typeof metric.meta === 'number' && metric.meta > 100
                            ? formatCurrency(metric.meta)
                            : metric.meta}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Recent Contracts & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Contracts */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="lg:col-span-2"
          >
            <Card>
              <CardHeader
                title="Contratos Recentes"
                description="Últimos 5 contratos adicionados ou atualizados"
                action={
                  <Button variant="ghost" size="sm">
                    Ver todos
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                }
              />
              <CardBody className="p-0">
                <DataTable
                  columns={contractColumns}
                  data={recentContracts}
                  keyExtractor={(row) => row.id}
                />
              </CardBody>
            </Card>
          </motion.div>

          {/* Alerts */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1 }}
          >
            <Card className="h-full">
              <CardHeader
                title="Alertas e Pendências"
                action={
                  <Badge variant="danger">{alerts.filter(a => a.priority === 'high').length} urgentes</Badge>
                }
              />
              <CardBody>
                <div className="space-y-3">
                  {alerts.slice(0, 5).map((alert) => (
                    <div
                      key={alert.id}
                      className={`p-3 rounded-lg border cursor-pointer hover:bg-bg-hover transition-colors ${
                        alert.type === 'danger' ? 'bg-accent-danger/5 border-accent-danger/20' :
                        alert.type === 'warning' ? 'bg-accent-warning/5 border-accent-warning/20' :
                        alert.type === 'success' ? 'bg-accent-success/5 border-accent-success/20' :
                        'bg-accent-info/5 border-accent-info/20'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {getAlertIcon(alert.type)}
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary text-sm">{alert.title}</p>
                          <p className="text-xs text-text-secondary mt-0.5">{alert.description}</p>
                          <p className="text-xs text-text-muted mt-1">{alert.timestamp}</p>
                        </div>
                        {alert.link && (
                          <ExternalLink className="h-4 w-4 text-text-muted flex-shrink-0" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Activity Feed */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
          >
            <Card className="h-full">
              <CardHeader
                title="Atividade Recente"
                action={
                  <Button variant="ghost" size="sm">Ver tudo</Button>
                }
              />
              <CardBody>
                <div className="space-y-4">
                  {activityFeed.slice(0, 6).map((activity, index) => (
                    <div key={activity.id} className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${
                        activity.type === 'contract' ? 'bg-accent-primary/20 text-accent-primary' :
                        activity.type === 'payment' ? 'bg-accent-success/20 text-accent-success' :
                        activity.type === 'employee' ? 'bg-accent-info/20 text-accent-info' :
                        activity.type === 'task' ? 'bg-accent-warning/20 text-accent-warning' :
                        activity.type === 'client' ? 'bg-accent-secondary/20 text-accent-secondary' :
                        'bg-bg-tertiary text-text-secondary'
                      }`}>
                        {getActivityIcon(activity.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary">{activity.title}</p>
                        <p className="text-xs text-text-secondary truncate">{activity.description}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-text-muted">{activity.timestamp}</span>
                          <span className="text-xs text-text-muted">•</span>
                          <span className="text-xs text-text-muted">{activity.user}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>

          {/* Top Clients */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3 }}
          >
            <Card className="h-full">
              <CardHeader
                title="Top Clientes"
                description="Por receita mensal"
              />
              <CardBody>
                <div className="space-y-3">
                  {topClients.map((client, index) => (
                    <div key={client.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-hover transition-colors">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-bg-tertiary text-text-secondary font-medium">
                        {index + 1}
                      </div>
                      <Avatar name={client.name} size="sm" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary truncate">{client.name}</p>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-text-secondary">{formatCurrency(client.revenue)}</span>
                          {client.trend === 'up' && <TrendingUp className="h-3 w-3 text-accent-success" />}
                          {client.trend === 'down' && <TrendingDown className="h-3 w-3 text-accent-danger" />}
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="h-3 w-3 text-accent-warning" />
                        <span className="text-xs text-text-secondary">{client.satisfaction}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>

          {/* Upcoming Events */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.4 }}
          >
            <Card className="h-full">
              <CardHeader
                title="Próximos Eventos"
                action={
                  <Button variant="ghost" size="sm">
                    <Calendar className="h-4 w-4 mr-1" />
                    Calendário
                  </Button>
                }
              />
              <CardBody>
                <div className="space-y-3">
                  {upcomingEvents.map((event) => (
                    <div key={event.id} className="flex items-center gap-3 p-3 rounded-lg bg-bg-tertiary">
                      <div className={`p-2 rounded-lg ${
                        event.type === 'meeting' ? 'bg-accent-primary/20 text-accent-primary' :
                        event.type === 'contract' ? 'bg-accent-warning/20 text-accent-warning' :
                        event.type === 'training' ? 'bg-accent-info/20 text-accent-info' :
                        'bg-accent-success/20 text-accent-success'
                      }`}>
                        {event.type === 'meeting' && <Users className="h-4 w-4" />}
                        {event.type === 'contract' && <FileText className="h-4 w-4" />}
                        {event.type === 'training' && <Target className="h-4 w-4" />}
                        {event.type === 'proposal' && <Briefcase className="h-4 w-4" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary truncate">{event.title}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs text-text-secondary">{event.date}</span>
                          {event.time !== '-' && (
                            <>
                              <span className="text-xs text-text-muted">•</span>
                              <span className="text-xs text-text-secondary">{event.time}</span>
                            </>
                          )}
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5 }}
        >
          <Card>
            <CardHeader title="Ações Rápidas" />
            <CardBody>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                <Button variant="outline" className="flex flex-col h-auto py-4 gap-2">
                  <FileText className="h-6 w-6 text-accent-primary" />
                  <span className="text-sm">Novo Contrato</span>
                </Button>
                <Button variant="outline" className="flex flex-col h-auto py-4 gap-2">
                  <Users className="h-6 w-6 text-accent-info" />
                  <span className="text-sm">Admitir Funcionário</span>
                </Button>
                <Button variant="outline" className="flex flex-col h-auto py-4 gap-2">
                  <Receipt className="h-6 w-6 text-accent-success" />
                  <span className="text-sm">Emitir NF</span>
                </Button>
                <Button variant="outline" className="flex flex-col h-auto py-4 gap-2">
                  <Activity className="h-6 w-6 text-accent-warning" />
                  <span className="text-sm">Criar OS</span>
                </Button>
                <Button variant="outline" className="flex flex-col h-auto py-4 gap-2">
                  <Building2 className="h-6 w-6 text-accent-secondary" />
                  <span className="text-sm">Novo Cliente</span>
                </Button>
                <Button variant="outline" className="flex flex-col h-auto py-4 gap-2">
                  <PieChartIcon className="h-6 w-6 text-text-secondary" />
                  <span className="text-sm">Relatórios</span>
                </Button>
              </div>
            </CardBody>
          </Card>
        </motion.div>
      </div>
    </MainLayout>
  );
}
