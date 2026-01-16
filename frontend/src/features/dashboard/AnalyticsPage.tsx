'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Brain,
  Target,
  AlertTriangle,
  Zap,
  Users,
  DollarSign,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  BarChart3,
  Filter,
  Download,
  RefreshCw,
  Eye,
  ChevronRight,
  ChevronDown,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
  Sparkles,
  Clock,
  Building2,
  FileText,
  Layers,
  GitBranch,
  CircleDot,
  Percent,
  Hash,
  ArrowRight,
  CheckCircle,
  XCircle,
  Settings,
  Info,
  HelpCircle,
  MoreHorizontal,
  Star,
  Lightbulb,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Share2
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  StatCard,
  Badge,
  Button,
  SimpleTabBar,
  Input,
  Select,
  Modal,
  DataTable
} from '@/design-system/components';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ScatterChart,
  Scatter,
  ZAxis,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
  Treemap,
  ComposedChart,
  FunnelChart,
  Funnel,
  LabelList
} from 'recharts';

// ==================== TYPES ====================

interface Anomaly {
  id: string;
  type: 'warning' | 'info' | 'success' | 'danger';
  title: string;
  description: string;
  impact: string;
  suggestion: string;
  confidence: number;
  detectedAt: string;
}

interface AIInsight {
  id: string;
  category: 'revenue' | 'churn' | 'growth' | 'efficiency' | 'risk';
  title: string;
  description: string;
  value: string;
  trend: 'up' | 'down' | 'stable';
  confidence: number;
  action: string;
}

interface MetricDetail {
  id: string;
  name: string;
  atual: number;
  anterior: number;
  meta: number;
  variacao: number;
  status: 'above' | 'below' | 'on_track';
}

interface CohortData {
  cohort: string;
  total: number;
  m1: number;
  m2: number;
  m3: number;
  m4: number;
  m5: number;
  m6: number;
}

interface SegmentData {
  name: string;
  value: number;
  growth: number;
  color: string;
  [key: string]: string | number;
}

interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

// ==================== MOCK DATA ====================

// Revenue forecast data
const forecastData = [
  { month: 'Jul', real: 185000, previsto: 180000, tendencia: 190000, limite_inf: 175000, limite_sup: 195000 },
  { month: 'Ago', real: 210000, previsto: 205000, tendencia: 215000, limite_inf: 200000, limite_sup: 220000 },
  { month: 'Set', real: 195000, previsto: 200000, tendencia: 205000, limite_inf: 190000, limite_sup: 210000 },
  { month: 'Out', real: 240000, previsto: 235000, tendencia: 245000, limite_inf: 225000, limite_sup: 255000 },
  { month: 'Nov', real: 225000, previsto: 230000, tendencia: 240000, limite_inf: 220000, limite_sup: 250000 },
  { month: 'Dez', real: 280000, previsto: 275000, tendencia: 290000, limite_inf: 260000, limite_sup: 300000 },
  { month: 'Jan', real: 295000, previsto: 290000, tendencia: 305000, limite_inf: 275000, limite_sup: 320000 },
  { month: 'Fev', real: null, previsto: 310000, tendencia: 325000, limite_inf: 290000, limite_sup: 345000 },
  { month: 'Mar', real: null, previsto: 325000, tendencia: 345000, limite_inf: 305000, limite_sup: 365000 },
  { month: 'Abr', real: null, previsto: 340000, tendencia: 365000, limite_inf: 320000, limite_sup: 385000 },
];

// Performance radar data
const performanceRadar = [
  { metric: 'Vendas', atual: 85, meta: 100 },
  { metric: 'Retenção', atual: 92, meta: 95 },
  { metric: 'NPS', atual: 78, meta: 85 },
  { metric: 'Conversão', atual: 65, meta: 75 },
  { metric: 'Eficiência', atual: 88, meta: 90 },
  { metric: 'Qualidade', atual: 95, meta: 95 },
];

// Funnel data
const funnelData = [
  { name: 'Leads', value: 1000, fill: '#6366f1' },
  { name: 'Qualificados', value: 650, fill: '#8b5cf6' },
  { name: 'Propostas', value: 340, fill: '#a855f7' },
  { name: 'Negociação', value: 180, fill: '#d946ef' },
  { name: 'Fechados', value: 85, fill: '#10b981' },
];

// Cohort retention data
const cohortData: CohortData[] = [
  { cohort: 'Jan/25', total: 45, m1: 100, m2: 92, m3: 88, m4: 85, m5: 82, m6: 80 },
  { cohort: 'Fev/25', total: 52, m1: 100, m2: 94, m3: 90, m4: 87, m5: 84, m6: 0 },
  { cohort: 'Mar/25', total: 48, m1: 100, m2: 91, m3: 86, m4: 83, m5: 0, m6: 0 },
  { cohort: 'Abr/25', total: 55, m1: 100, m2: 93, m3: 89, m4: 0, m5: 0, m6: 0 },
  { cohort: 'Mai/25', total: 61, m1: 100, m2: 95, m3: 0, m4: 0, m5: 0, m6: 0 },
  { cohort: 'Jun/25', total: 58, m1: 100, m2: 0, m3: 0, m4: 0, m5: 0, m6: 0 },
];

// Segment data
const segmentData: SegmentData[] = [
  { name: 'Condomínios', value: 42, growth: 15, color: '#6366f1' },
  { name: 'Empresas', value: 28, growth: 8, color: '#8b5cf6' },
  { name: 'Hospitais', value: 15, growth: 22, color: '#10b981' },
  { name: 'Shoppings', value: 10, growth: -5, color: '#f59e0b' },
  { name: 'Outros', value: 5, growth: 3, color: '#64748b' },
];

// Revenue by service type
const revenueByService = [
  { name: 'Segurança', value: 145000, percentage: 49 },
  { name: 'Limpeza', value: 85000, percentage: 29 },
  { name: 'Facilities', value: 45000, percentage: 15 },
  { name: 'Manutenção', value: 20000, percentage: 7 },
];

// Monthly metrics
const monthlyMetrics: MetricDetail[] = [
  { id: '1', name: 'Receita Total', atual: 295000, anterior: 280000, meta: 300000, variacao: 5.4, status: 'on_track' },
  { id: '2', name: 'Novos Contratos', atual: 8, anterior: 5, meta: 10, variacao: 60, status: 'above' },
  { id: '3', name: 'Churn Rate', atual: 2.3, anterior: 3.1, meta: 2.0, variacao: -25.8, status: 'on_track' },
  { id: '4', name: 'Ticket Médio', atual: 42000, anterior: 38000, meta: 45000, variacao: 10.5, status: 'on_track' },
  { id: '5', name: 'NPS Score', atual: 72, anterior: 68, meta: 75, variacao: 5.9, status: 'on_track' },
  { id: '6', name: 'CAC', atual: 8500, anterior: 9200, meta: 8000, variacao: -7.6, status: 'on_track' },
  { id: '7', name: 'LTV', atual: 156000, anterior: 142000, meta: 160000, variacao: 9.9, status: 'on_track' },
  { id: '8', name: 'LTV/CAC', atual: 18.4, anterior: 15.4, meta: 20, variacao: 19.5, status: 'above' },
];

// Anomalies
const anomalies: Anomaly[] = [
  {
    id: '1',
    type: 'warning',
    title: 'Queda na conversão de leads',
    description: 'Taxa de conversão caiu 15% na última semana, de 28% para 24%',
    impact: 'alto',
    suggestion: 'Revisar processo de qualificação e scripts de vendas',
    confidence: 89,
    detectedAt: '2 horas atrás'
  },
  {
    id: '2',
    type: 'info',
    title: 'Pico de demanda detectado',
    description: 'Previsão de aumento de 25% em consultas de segurança para março',
    impact: 'médio',
    suggestion: 'Preparar escala de funcionários e estoque de uniformes',
    confidence: 82,
    detectedAt: '5 horas atrás'
  },
  {
    id: '3',
    type: 'success',
    title: 'Meta de receita superada',
    description: 'Receita 8% acima do previsto para janeiro',
    impact: 'positivo',
    suggestion: 'Manter estratégia atual e expandir para novos segmentos',
    confidence: 98,
    detectedAt: '1 dia atrás'
  },
  {
    id: '4',
    type: 'danger',
    title: 'Risco de churn elevado',
    description: '3 clientes com probabilidade de cancelamento > 70%',
    impact: 'crítico',
    suggestion: 'Agendar reunião de relacionamento imediatamente',
    confidence: 76,
    detectedAt: '3 horas atrás'
  },
];

// AI Insights
const aiInsights: AIInsight[] = [
  {
    id: '1',
    category: 'revenue',
    title: 'Oportunidade de Upsell',
    description: '12 clientes elegíveis para upgrade de plano baseado em uso',
    value: 'R$ 85.000/mês',
    trend: 'up',
    confidence: 91,
    action: 'Ver clientes'
  },
  {
    id: '2',
    category: 'churn',
    title: 'Prevenção de Churn',
    description: 'Modelo identificou 3 clientes em risco de cancelamento',
    value: 'R$ 45.000/mês',
    trend: 'down',
    confidence: 87,
    action: 'Intervir agora'
  },
  {
    id: '3',
    category: 'growth',
    title: 'Expansão Geográfica',
    description: 'Demanda crescente identificada na região Sul (+35%)',
    value: 'R$ 120.000/ano',
    trend: 'up',
    confidence: 78,
    action: 'Analisar mercado'
  },
  {
    id: '4',
    category: 'efficiency',
    title: 'Otimização de Escalas',
    description: 'Realocação sugerida pode reduzir horas extras em 20%',
    value: 'R$ 15.000/mês',
    trend: 'up',
    confidence: 94,
    action: 'Aplicar sugestão'
  },
  {
    id: '5',
    category: 'risk',
    title: 'Concentração de Receita',
    description: '28% da receita vem de apenas 3 clientes',
    value: 'Risco médio',
    trend: 'stable',
    confidence: 99,
    action: 'Diversificar'
  },
];

// Correlation scatter data
const correlationData = [
  { x: 10, y: 30, z: 200, name: 'Cliente A', segment: 'Condomínio' },
  { x: 30, y: 50, z: 400, name: 'Cliente B', segment: 'Empresa' },
  { x: 45, y: 80, z: 600, name: 'Cliente C', segment: 'Hospital' },
  { x: 50, y: 60, z: 350, name: 'Cliente D', segment: 'Condomínio' },
  { x: 70, y: 90, z: 800, name: 'Cliente E', segment: 'Shopping' },
  { x: 80, y: 70, z: 500, name: 'Cliente F', segment: 'Empresa' },
  { x: 90, y: 95, z: 900, name: 'Cliente G', segment: 'Hospital' },
  { x: 35, y: 45, z: 280, name: 'Cliente H', segment: 'Condomínio' },
  { x: 65, y: 75, z: 550, name: 'Cliente I', segment: 'Empresa' },
  { x: 55, y: 85, z: 720, name: 'Cliente J', segment: 'Hospital' },
];

// Time series seasonality
const seasonalityData = [
  { month: 'Jan', valor: 100, sazonal: 95, tendencia: 98 },
  { month: 'Fev', valor: 105, sazonal: 102, tendencia: 100 },
  { month: 'Mar', valor: 118, sazonal: 115, tendencia: 102 },
  { month: 'Abr', valor: 112, sazonal: 108, tendencia: 104 },
  { month: 'Mai', valor: 125, sazonal: 120, tendencia: 106 },
  { month: 'Jun', valor: 130, sazonal: 125, tendencia: 108 },
  { month: 'Jul', valor: 122, sazonal: 118, tendencia: 110 },
  { month: 'Ago', valor: 135, sazonal: 130, tendencia: 112 },
  { month: 'Set', valor: 140, sazonal: 135, tendencia: 114 },
  { month: 'Out', valor: 145, sazonal: 140, tendencia: 116 },
  { month: 'Nov', valor: 155, sazonal: 150, tendencia: 118 },
  { month: 'Dez', valor: 165, sazonal: 160, tendencia: 120 },
];

// Weekly performance comparison
const weeklyComparison = [
  { day: 'Seg', atual: 45, anterior: 42 },
  { day: 'Ter', atual: 52, anterior: 48 },
  { day: 'Qua', atual: 48, anterior: 55 },
  { day: 'Qui', atual: 61, anterior: 58 },
  { day: 'Sex', atual: 55, anterior: 52 },
  { day: 'Sáb', atual: 25, anterior: 22 },
  { day: 'Dom', atual: 12, anterior: 10 },
];

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatPercent = (value: number) => {
  return `${value.toFixed(1)}%`;
};

const getAnomalyIcon = (type: string) => {
  switch (type) {
    case 'danger': return <XCircle className="h-5 w-5 text-accent-danger" />;
    case 'warning': return <AlertTriangle className="h-5 w-5 text-accent-warning" />;
    case 'success': return <CheckCircle className="h-5 w-5 text-accent-success" />;
    default: return <Info className="h-5 w-5 text-accent-info" />;
  }
};

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'revenue': return <DollarSign className="h-4 w-4" />;
    case 'churn': return <Users className="h-4 w-4" />;
    case 'growth': return <TrendingUp className="h-4 w-4" />;
    case 'efficiency': return <Zap className="h-4 w-4" />;
    case 'risk': return <AlertTriangle className="h-4 w-4" />;
    default: return <Activity className="h-4 w-4" />;
  }
};

const getCohortColor = (value: number) => {
  if (value === 0) return 'bg-bg-tertiary';
  if (value >= 90) return 'bg-accent-success';
  if (value >= 80) return 'bg-accent-success/70';
  if (value >= 70) return 'bg-accent-warning';
  if (value >= 60) return 'bg-accent-warning/70';
  return 'bg-accent-danger/70';
};

// Custom Tooltip
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-3 shadow-lg">
        <p className="text-text-secondary text-sm mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === 'number' && entry.value > 100
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

export function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedPeriod, setSelectedPeriod] = useState('6m');
  const [showInsightModal, setShowInsightModal] = useState(false);
  const [selectedInsight, setSelectedInsight] = useState<AIInsight | null>(null);

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <BarChart3 className="h-4 w-4" /> },
    { value: 'predictions', label: 'Previsões IA', icon: <Brain className="h-4 w-4" /> },
    { value: 'cohorts', label: 'Cohorts', icon: <Users className="h-4 w-4" /> },
    { value: 'segments', label: 'Segmentação', icon: <PieChartIcon className="h-4 w-4" /> },
    { value: 'anomalies', label: 'Anomalias', icon: <AlertTriangle className="h-4 w-4" /> },
  ];

  const metricColumns: Column<MetricDetail>[] = [
    {
      key: 'name',
      header: 'Métrica',
      render: (row) => <span className="font-medium text-text-primary">{row.name}</span>
    },
    {
      key: 'atual',
      header: 'Atual',
      render: (row) => (
        <span className="font-mono text-text-primary">
          {row.atual >= 1000 ? formatCurrency(row.atual) : row.atual}
        </span>
      )
    },
    {
      key: 'anterior',
      header: 'Anterior',
      render: (row) => (
        <span className="font-mono text-text-secondary">
          {row.anterior >= 1000 ? formatCurrency(row.anterior) : row.anterior}
        </span>
      )
    },
    {
      key: 'meta',
      header: 'Meta',
      render: (row) => (
        <span className="font-mono text-text-secondary">
          {row.meta >= 1000 ? formatCurrency(row.meta) : row.meta}
        </span>
      )
    },
    {
      key: 'variacao',
      header: 'Variação',
      render: (row) => (
        <div className="flex items-center gap-1">
          {row.variacao > 0 ? (
            <TrendingUp className="h-4 w-4 text-accent-success" />
          ) : (
            <TrendingDown className="h-4 w-4 text-accent-danger" />
          )}
          <span className={row.variacao > 0 ? 'text-accent-success' : 'text-accent-danger'}>
            {row.variacao > 0 ? '+' : ''}{row.variacao.toFixed(1)}%
          </span>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={
          row.status === 'above' ? 'success' :
          row.status === 'below' ? 'danger' : 'info'
        }>
          {row.status === 'above' ? 'Acima' :
           row.status === 'below' ? 'Abaixo' : 'No alvo'}
        </Badge>
      )
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Analytics & Inteligência
            </h1>
            <p className="text-text-secondary mt-1">
              Análises avançadas e previsões com IA • Modelo: 94.2% acurácia
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              options={[
                { value: '1m', label: 'Último Mês' },
                { value: '3m', label: 'Últimos 3 Meses' },
                { value: '6m', label: 'Últimos 6 Meses' },
                { value: '1y', label: 'Último Ano' },
                { value: 'ytd', label: 'Ano até hoje' },
              ]}
              value={selectedPeriod}
              onChange={setSelectedPeriod}
            />
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button>
              <Brain className="h-4 w-4 mr-2" />
              Gerar Insights
            </Button>
          </div>
        </div>

        {/* AI Insights Banner */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="bg-gradient-to-r from-accent-primary/10 via-accent-secondary/10 to-accent-success/10 border-accent-primary/30">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-accent-primary/20">
                    <Sparkles className="h-6 w-6 text-accent-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary flex items-center gap-2">
                      Insights da IA
                      <Badge variant="success">5 novos</Badge>
                    </h3>
                    <p className="text-sm text-text-secondary">
                      Oportunidades identificadas: R$ 265.000/ano em potencial
                    </p>
                  </div>
                </div>
                <Button variant="primary" size="sm">
                  Ver Todos
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>

              <div className="grid grid-cols-5 gap-3">
                {aiInsights.map((insight) => (
                  <div
                    key={insight.id}
                    className="p-3 rounded-lg bg-bg-secondary/80 border border-border-subtle cursor-pointer hover:border-accent-primary/50 transition-colors"
                    onClick={() => {
                      setSelectedInsight(insight);
                      setShowInsightModal(true);
                    }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`p-1.5 rounded ${
                        insight.category === 'revenue' ? 'bg-accent-success/20 text-accent-success' :
                        insight.category === 'churn' ? 'bg-accent-danger/20 text-accent-danger' :
                        insight.category === 'growth' ? 'bg-accent-primary/20 text-accent-primary' :
                        insight.category === 'efficiency' ? 'bg-accent-info/20 text-accent-info' :
                        'bg-accent-warning/20 text-accent-warning'
                      }`}>
                        {getCategoryIcon(insight.category)}
                      </div>
                      <Badge variant="outline" className="text-xs">{insight.confidence}%</Badge>
                    </div>
                    <p className="text-sm font-medium text-text-primary line-clamp-1">{insight.title}</p>
                    <p className="text-xs text-text-secondary line-clamp-2 mt-1">{insight.description}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className={`text-sm font-semibold ${
                        insight.trend === 'up' ? 'text-accent-success' :
                        insight.trend === 'down' ? 'text-accent-danger' : 'text-text-secondary'
                      }`}>
                        {insight.value}
                      </span>
                      {insight.trend === 'up' && <TrendingUp className="h-3 w-3 text-accent-success" />}
                      {insight.trend === 'down' && <TrendingDown className="h-3 w-3 text-accent-danger" />}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Acurácia do Modelo"
              value="94.2%"
              change={2.1}
              changeLabel="vs último treino"
              icon={<Brain className="h-5 w-5" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Previsão Próx. Mês"
              value="R$ 310.000"
              change={5.1}
              changeLabel="tendência"
              icon={<TrendingUp className="h-5 w-5" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Anomalias Detectadas"
              value="4"
              change={1}
              changeLabel="nova hoje"
              icon={<AlertTriangle className="h-5 w-5" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Score de Saúde"
              value="87/100"
              change={4.2}
              changeLabel="melhoria"
              icon={<Activity className="h-5 w-5" />}
              iconColor="info"
            />
          </motion.div>
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Tab Content: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Revenue Forecast */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="lg:col-span-2"
              >
                <Card>
                  <CardHeader
                    title="Previsão de Receita"
                    description="Modelo preditivo com intervalo de confiança 95%"
                    action={
                      <Badge variant="success">
                        <Zap className="h-3 w-3 mr-1" />
                        IA Ativa
                      </Badge>
                    }
                  />
                  <CardBody>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={forecastData}>
                          <defs>
                            <linearGradient id="colorReal" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                          <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                          <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          <Area
                            type="monotone"
                            dataKey="limite_sup"
                            name="Limite Superior"
                            stroke="transparent"
                            fill="#8b5cf6"
                            fillOpacity={0.1}
                          />
                          <Area
                            type="monotone"
                            dataKey="limite_inf"
                            name="Limite Inferior"
                            stroke="transparent"
                            fill="#0a0a0f"
                            fillOpacity={1}
                          />
                          <Line
                            type="monotone"
                            dataKey="real"
                            name="Real"
                            stroke="#6366f1"
                            strokeWidth={3}
                            dot={{ fill: '#6366f1', strokeWidth: 2 }}
                            connectNulls={false}
                          />
                          <Line
                            type="monotone"
                            dataKey="previsto"
                            name="Previsto"
                            stroke="#8b5cf6"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={{ fill: '#8b5cf6' }}
                          />
                          <Line
                            type="monotone"
                            dataKey="tendencia"
                            name="Tendência"
                            stroke="#10b981"
                            strokeWidth={2}
                            strokeDasharray="3 3"
                            dot={false}
                          />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </div>
                  </CardBody>
                </Card>
              </motion.div>

              {/* Performance Radar */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Card className="h-full">
                  <CardHeader title="Performance vs Meta" />
                  <CardBody>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={performanceRadar}>
                          <PolarGrid stroke="#2d2d3d" />
                          <PolarAngleAxis dataKey="metric" stroke="#64748b" fontSize={11} />
                          <PolarRadiusAxis stroke="#64748b" fontSize={10} domain={[0, 100]} />
                          <Radar
                            name="Atual"
                            dataKey="atual"
                            stroke="#6366f1"
                            fill="#6366f1"
                            fillOpacity={0.4}
                          />
                          <Radar
                            name="Meta"
                            dataKey="meta"
                            stroke="#10b981"
                            fill="#10b981"
                            fillOpacity={0.1}
                          />
                          <Tooltip />
                          <Legend />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="mt-4 space-y-2">
                      {performanceRadar.map((item) => {
                        const diff = item.atual - item.meta;
                        return (
                          <div key={item.metric} className="flex items-center justify-between text-sm">
                            <span className="text-text-secondary">{item.metric}</span>
                            <span className={diff >= 0 ? 'text-accent-success' : 'text-accent-danger'}>
                              {diff >= 0 ? '+' : ''}{diff}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </CardBody>
                </Card>
              </motion.div>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Funnel */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
              >
                <Card>
                  <CardHeader
                    title="Funil de Vendas"
                    description="Conversão por etapa do processo"
                  />
                  <CardBody>
                    <div className="space-y-4">
                      {funnelData.map((item, index) => {
                        const prevValue = index > 0 ? funnelData[index - 1].value : item.value;
                        const conversionRate = ((item.value / prevValue) * 100).toFixed(1);
                        const widthPercent = (item.value / funnelData[0].value) * 100;

                        return (
                          <div key={item.name}>
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm text-text-secondary">{item.name}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-text-primary">{item.value}</span>
                                {index > 0 && (
                                  <Badge variant="outline" className="text-xs">
                                    {conversionRate}%
                                  </Badge>
                                )}
                              </div>
                            </div>
                            <div className="h-8 bg-bg-tertiary rounded-lg overflow-hidden">
                              <div
                                className="h-full rounded-lg transition-all flex items-center justify-center"
                                style={{
                                  width: `${widthPercent}%`,
                                  backgroundColor: item.fill
                                }}
                              >
                                <span className="text-xs font-medium text-white">
                                  {widthPercent.toFixed(0)}%
                                </span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    <div className="mt-6 p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center justify-between">
                        <span className="text-text-secondary">Taxa de conversão geral</span>
                        <span className="text-2xl font-bold text-accent-success">
                          {((funnelData[funnelData.length - 1].value / funnelData[0].value) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              </motion.div>

              {/* Client Correlation */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
              >
                <Card>
                  <CardHeader
                    title="Correlação de Clientes"
                    description="Engajamento vs Satisfação vs Valor"
                  />
                  <CardBody>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart>
                          <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                          <XAxis
                            type="number"
                            dataKey="x"
                            name="Engajamento"
                            stroke="#64748b"
                            fontSize={12}
                            label={{ value: 'Engajamento %', position: 'bottom', fill: '#64748b' }}
                          />
                          <YAxis
                            type="number"
                            dataKey="y"
                            name="Satisfação"
                            stroke="#64748b"
                            fontSize={12}
                            label={{ value: 'Satisfação %', angle: -90, position: 'left', fill: '#64748b' }}
                          />
                          <ZAxis
                            type="number"
                            dataKey="z"
                            name="Valor"
                            range={[50, 400]}
                          />
                          <Tooltip
                            cursor={{ strokeDasharray: '3 3' }}
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                const data = payload[0].payload;
                                return (
                                  <div className="bg-bg-secondary border border-border-subtle rounded-lg p-3 shadow-lg">
                                    <p className="font-medium text-text-primary">{data.name}</p>
                                    <p className="text-xs text-text-muted">{data.segment}</p>
                                    <div className="mt-2 space-y-1">
                                      <p className="text-sm text-text-secondary">Engajamento: {data.x}%</p>
                                      <p className="text-sm text-text-secondary">Satisfação: {data.y}%</p>
                                      <p className="text-sm text-text-secondary">
                                        Valor: {formatCurrency(data.z * 100)}
                                      </p>
                                    </div>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Scatter
                            data={correlationData}
                            fill="#6366f1"
                            fillOpacity={0.7}
                          />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="mt-4 text-sm text-text-secondary">
                      <p>
                        <strong>Insight:</strong> Clientes com engajamento {'>'}70% têm 85% mais probabilidade de renovação.
                      </p>
                    </div>
                  </CardBody>
                </Card>
              </motion.div>
            </div>

            {/* Metrics Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <Card>
                <CardHeader
                  title="Métricas Detalhadas"
                  description="Comparativo do período selecionado"
                  action={
                    <Button variant="ghost" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Exportar
                    </Button>
                  }
                />
                <CardBody className="p-0">
                  <DataTable
                    columns={metricColumns}
                    data={monthlyMetrics}
                    keyExtractor={(row) => row.id}
                  />
                </CardBody>
              </Card>
            </motion.div>
          </div>
        )}

        {/* Tab Content: Predictions */}
        {activeTab === 'predictions' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Seasonality Analysis */}
              <Card>
                <CardHeader
                  title="Análise de Sazonalidade"
                  description="Decomposição da série temporal"
                />
                <CardBody>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={seasonalityData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                        <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="valor"
                          name="Valor Real"
                          stroke="#6366f1"
                          strokeWidth={2}
                          dot={{ fill: '#6366f1' }}
                        />
                        <Line
                          type="monotone"
                          dataKey="sazonal"
                          name="Componente Sazonal"
                          stroke="#f59e0b"
                          strokeWidth={2}
                          strokeDasharray="5 5"
                        />
                        <Line
                          type="monotone"
                          dataKey="tendencia"
                          name="Tendência"
                          stroke="#10b981"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardBody>
              </Card>

              {/* Weekly Comparison */}
              <Card>
                <CardHeader
                  title="Comparativo Semanal"
                  description="Semana atual vs anterior"
                />
                <CardBody>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={weeklyComparison}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                        <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Bar dataKey="atual" name="Atual" fill="#6366f1" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="anterior" name="Anterior" fill="#8b5cf6" radius={[4, 4, 0, 0]} opacity={0.5} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Model Information */}
            <Card>
              <CardHeader title="Informações do Modelo" />
              <CardBody>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div className="p-4 rounded-lg bg-bg-tertiary">
                    <p className="text-text-secondary text-sm">Algoritmo</p>
                    <p className="text-xl font-semibold text-text-primary mt-1">LSTM + XGBoost</p>
                  </div>
                  <div className="p-4 rounded-lg bg-bg-tertiary">
                    <p className="text-text-secondary text-sm">Última Atualização</p>
                    <p className="text-xl font-semibold text-text-primary mt-1">Há 2 horas</p>
                  </div>
                  <div className="p-4 rounded-lg bg-bg-tertiary">
                    <p className="text-text-secondary text-sm">Features Utilizadas</p>
                    <p className="text-xl font-semibold text-text-primary mt-1">24 variáveis</p>
                  </div>
                  <div className="p-4 rounded-lg bg-bg-tertiary">
                    <p className="text-text-secondary text-sm">Horizonte de Previsão</p>
                    <p className="text-xl font-semibold text-text-primary mt-1">90 dias</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Tab Content: Cohorts */}
        {activeTab === 'cohorts' && (
          <Card>
            <CardHeader
              title="Análise de Cohorts"
              description="Retenção mensal por coorte de aquisição"
            />
            <CardBody>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border-subtle">
                      <th className="px-4 py-3 text-left text-sm font-medium text-text-secondary">Cohort</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-text-secondary">Clientes</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-text-secondary">Mês 1</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-text-secondary">Mês 2</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-text-secondary">Mês 3</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-text-secondary">Mês 4</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-text-secondary">Mês 5</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-text-secondary">Mês 6</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cohortData.map((cohort) => (
                      <tr key={cohort.cohort} className="border-b border-border-subtle">
                        <td className="px-4 py-3 text-sm font-medium text-text-primary">{cohort.cohort}</td>
                        <td className="px-4 py-3 text-center text-sm text-text-secondary">{cohort.total}</td>
                        {[cohort.m1, cohort.m2, cohort.m3, cohort.m4, cohort.m5, cohort.m6].map((value, index) => (
                          <td key={index} className="px-4 py-3">
                            <div className={`mx-auto w-12 h-8 rounded flex items-center justify-center text-xs font-medium ${getCohortColor(value)} ${value > 0 ? 'text-white' : 'text-text-muted'}`}>
                              {value > 0 ? `${value}%` : '-'}
                            </div>
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-6 flex items-center gap-4 justify-center">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-success" />
                  <span className="text-sm text-text-secondary">≥90%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-success/70" />
                  <span className="text-sm text-text-secondary">80-89%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-warning" />
                  <span className="text-sm text-text-secondary">70-79%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-warning/70" />
                  <span className="text-sm text-text-secondary">60-69%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-danger/70" />
                  <span className="text-sm text-text-secondary">{'<'}60%</span>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Tab Content: Segments */}
        {activeTab === 'segments' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Segment Distribution */}
            <Card>
              <CardHeader title="Distribuição por Segmento" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={segmentData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {segmentData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3 mt-4">
                  {segmentData.map((segment) => (
                    <div key={segment.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: segment.color }} />
                        <span className="text-sm text-text-secondary">{segment.name}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-text-primary">{segment.value}%</span>
                        <Badge variant={segment.growth > 0 ? 'success' : segment.growth < 0 ? 'danger' : 'neutral'}>
                          {segment.growth > 0 ? '+' : ''}{segment.growth}%
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Revenue by Service */}
            <Card>
              <CardHeader title="Receita por Tipo de Serviço" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={revenueByService} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" horizontal={false} />
                      <XAxis type="number" stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                      <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={12} width={100} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3 mt-4">
                  {revenueByService.map((service) => (
                    <div key={service.name} className="flex items-center justify-between">
                      <span className="text-sm text-text-secondary">{service.name}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-text-primary">{formatCurrency(service.value)}</span>
                        <Badge variant="outline">{service.percentage}%</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Tab Content: Anomalies */}
        {activeTab === 'anomalies' && (
          <div className="space-y-4">
            {anomalies.map((anomaly) => (
              <Card key={anomaly.id}>
                <div className={`p-6 border-l-4 ${
                  anomaly.type === 'danger' ? 'border-l-accent-danger' :
                  anomaly.type === 'warning' ? 'border-l-accent-warning' :
                  anomaly.type === 'success' ? 'border-l-accent-success' :
                  'border-l-accent-info'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-lg ${
                        anomaly.type === 'danger' ? 'bg-accent-danger/10' :
                        anomaly.type === 'warning' ? 'bg-accent-warning/10' :
                        anomaly.type === 'success' ? 'bg-accent-success/10' :
                        'bg-accent-info/10'
                      }`}>
                        {getAnomalyIcon(anomaly.type)}
                      </div>
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold text-text-primary">{anomaly.title}</h3>
                          <Badge variant={
                            anomaly.impact === 'crítico' ? 'danger' :
                            anomaly.impact === 'alto' ? 'warning' :
                            anomaly.impact === 'positivo' ? 'success' :
                            'info'
                          }>
                            Impacto: {anomaly.impact}
                          </Badge>
                        </div>
                        <p className="text-text-secondary mt-1">{anomaly.description}</p>
                        <div className="flex items-center gap-4 mt-3">
                          <div className="flex items-center gap-2">
                            <Lightbulb className="h-4 w-4 text-accent-warning" />
                            <span className="text-sm text-text-secondary">{anomaly.suggestion}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-3 text-sm text-text-muted">
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {anomaly.detectedAt}
                          </span>
                          <span className="flex items-center gap-1">
                            <Target className="h-4 w-4" />
                            Confiança: {anomaly.confidence}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        Detalhes
                      </Button>
                      <Button size="sm">
                        Resolver
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Insight Detail Modal */}
        <Modal
          isOpen={showInsightModal}
          onClose={() => setShowInsightModal(false)}
          title="Detalhe do Insight"
          size="md"
        >
          {selectedInsight && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${
                  selectedInsight.category === 'revenue' ? 'bg-accent-success/20 text-accent-success' :
                  selectedInsight.category === 'churn' ? 'bg-accent-danger/20 text-accent-danger' :
                  selectedInsight.category === 'growth' ? 'bg-accent-primary/20 text-accent-primary' :
                  selectedInsight.category === 'efficiency' ? 'bg-accent-info/20 text-accent-info' :
                  'bg-accent-warning/20 text-accent-warning'
                }`}>
                  {getCategoryIcon(selectedInsight.category)}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">{selectedInsight.title}</h3>
                  <Badge variant="outline">{selectedInsight.confidence}% confiança</Badge>
                </div>
              </div>

              <p className="text-text-secondary">{selectedInsight.description}</p>

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <p className="text-text-secondary text-sm">Impacto estimado</p>
                <p className="text-2xl font-bold text-text-primary mt-1">{selectedInsight.value}</p>
              </div>

              <div className="flex gap-3">
                <Button className="flex-1">
                  {selectedInsight.action}
                </Button>
                <Button variant="outline" onClick={() => setShowInsightModal(false)}>
                  Fechar
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
