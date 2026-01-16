'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  type Column,
  Modal,
  Select
} from '@/design-system/components';
import {
  TrendingUp,
  Brain,
  Target,
  AlertTriangle,
  DollarSign,
  Users,
  Clock,
  RefreshCw,
  Play,
  Download,
  Settings,
  Zap,
  BarChart2,
  Activity,
  Calendar,
  ChevronRight,
  CheckCircle,
  XCircle,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
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
  Legend,
  ScatterChart,
  Scatter
} from 'recharts';

// Types
interface Prediction {
  id: string;
  type: 'revenue' | 'churn' | 'demand' | 'cost';
  title: string;
  description: string;
  predictedValue: number;
  confidence: number;
  trend: 'up' | 'down' | 'stable';
  timeframe: string;
  lastUpdated: string;
  accuracy: number;
  factors: string[];
  status: 'active' | 'completed' | 'scheduled';
}

interface ModelMetrics {
  id: string;
  name: string;
  type: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  lastTrained: string;
  dataPoints: number;
  status: 'training' | 'ready' | 'outdated';
}

// Mock data
const mockPredictions: Prediction[] = [
  {
    id: '1',
    type: 'revenue',
    title: 'Previsão de Receita Q1 2026',
    description: 'Projeção baseada em tendências históricas e sazonalidade',
    predictedValue: 2850000,
    confidence: 87,
    trend: 'up',
    timeframe: 'Próximos 3 meses',
    lastUpdated: '2026-01-15',
    accuracy: 92,
    factors: ['Sazonalidade', 'Crescimento de clientes', 'Novos contratos'],
    status: 'active'
  },
  {
    id: '2',
    type: 'churn',
    title: 'Risco de Churn - Clientes Premium',
    description: 'Análise de probabilidade de cancelamento',
    predictedValue: 8.5,
    confidence: 82,
    trend: 'down',
    timeframe: 'Próximos 30 dias',
    lastUpdated: '2026-01-14',
    accuracy: 88,
    factors: ['Engajamento baixo', 'Tickets de suporte', 'Uso decrescente'],
    status: 'active'
  },
  {
    id: '3',
    type: 'demand',
    title: 'Demanda de Serviços - Segurança',
    description: 'Previsão de demanda para serviços de vigilância',
    predictedValue: 450,
    confidence: 79,
    trend: 'up',
    timeframe: 'Próximas 4 semanas',
    lastUpdated: '2026-01-13',
    accuracy: 85,
    factors: ['Eventos regionais', 'Sazonalidade', 'Novos projetos'],
    status: 'active'
  }
];

const mockModels: ModelMetrics[] = [
  {
    id: '1',
    name: 'Revenue Forecaster',
    type: 'Time Series',
    accuracy: 92.5,
    precision: 0.89,
    recall: 0.91,
    f1Score: 0.90,
    lastTrained: '2026-01-10',
    dataPoints: 125000,
    status: 'ready'
  },
  {
    id: '2',
    name: 'Churn Predictor',
    type: 'Classification',
    accuracy: 88.3,
    precision: 0.85,
    recall: 0.87,
    f1Score: 0.86,
    lastTrained: '2026-01-12',
    dataPoints: 45000,
    status: 'ready'
  },
  {
    id: '3',
    name: 'Demand Estimator',
    type: 'Regression',
    accuracy: 85.7,
    precision: 0.82,
    recall: 0.84,
    f1Score: 0.83,
    lastTrained: '2026-01-08',
    dataPoints: 78000,
    status: 'outdated'
  }
];

// Chart data
const revenueChartData = [
  { month: 'Jul', actual: 2100000, predicted: 2050000 },
  { month: 'Ago', actual: 2250000, predicted: 2200000 },
  { month: 'Set', actual: 2180000, predicted: 2220000 },
  { month: 'Out', actual: 2400000, predicted: 2350000 },
  { month: 'Nov', actual: 2550000, predicted: 2500000 },
  { month: 'Dez', actual: 2680000, predicted: 2650000 },
  { month: 'Jan', actual: null, predicted: 2750000 },
  { month: 'Fev', actual: null, predicted: 2800000 },
  { month: 'Mar', actual: null, predicted: 2850000 }
];

const accuracyTrendData = [
  { date: '01/01', accuracy: 85 },
  { date: '05/01', accuracy: 87 },
  { date: '10/01', accuracy: 89 },
  { date: '15/01', accuracy: 88 },
  { date: '20/01', accuracy: 91 },
  { date: '25/01', accuracy: 92 }
];

export function AIPredictionsPage() {
  const [activeTab, setActiveTab] = useState('predictions');
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);
  const [filterPeriod, setFilterPeriod] = useState('month');
  const [showTrainModal, setShowTrainModal] = useState(false);
  const [trainingDataPeriod, setTrainingDataPeriod] = useState('6months');

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value);
  };

  const tabs = [
    { value: 'predictions', label: 'Previsões', icon: <Brain className="h-4 w-4" /> },
    { value: 'models', label: 'Modelos', icon: <Zap className="h-4 w-4" /> },
    { value: 'analytics', label: 'Análises', icon: <BarChart2 className="h-4 w-4" /> }
  ];

  const predictionColumns: Column<Prediction>[] = [
    {
      key: 'title',
      header: 'Previsão',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            row.type === 'revenue' ? 'bg-success/10 text-success' :
            row.type === 'churn' ? 'bg-danger/10 text-danger' :
            row.type === 'demand' ? 'bg-info/10 text-info' :
            'bg-warning/10 text-warning'
          }`}>
            {row.type === 'revenue' ? <DollarSign className="h-4 w-4" /> :
             row.type === 'churn' ? <Users className="h-4 w-4" /> :
             row.type === 'demand' ? <Target className="h-4 w-4" /> :
             <AlertTriangle className="h-4 w-4" />}
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.title}</p>
            <p className="text-sm text-text-secondary">{row.description}</p>
          </div>
        </div>
      )
    },
    {
      key: 'predictedValue',
      header: 'Valor Previsto',
      render: (row) => (
        <div className="flex items-center gap-2">
          <span className="font-semibold text-text-primary">
            {row.type === 'revenue' ? formatCurrency(row.predictedValue) :
             row.type === 'churn' ? `${row.predictedValue}%` :
             row.predictedValue.toLocaleString()}
          </span>
          {row.trend === 'up' ? (
            <ArrowUpRight className="h-4 w-4 text-success" />
          ) : row.trend === 'down' ? (
            <ArrowDownRight className="h-4 w-4 text-danger" />
          ) : null}
        </div>
      )
    },
    {
      key: 'confidence',
      header: 'Confiança',
      render: (row) => (
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-bg-tertiary rounded-full max-w-[100px]">
            <div
              className={`h-full rounded-full ${
                row.confidence >= 85 ? 'bg-success' :
                row.confidence >= 70 ? 'bg-warning' : 'bg-danger'
              }`}
              style={{ width: `${row.confidence}%` }}
            />
          </div>
          <span className="text-sm font-medium">{row.confidence}%</span>
        </div>
      )
    },
    {
      key: 'timeframe',
      header: 'Período',
      render: (row) => (
        <div className="flex items-center gap-2 text-text-secondary">
          <Clock className="h-4 w-4" />
          {row.timeframe}
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={
          row.status === 'active' ? 'success' :
          row.status === 'completed' ? 'neutral' : 'warning'
        }>
          {row.status === 'active' ? 'Ativo' :
           row.status === 'completed' ? 'Concluído' : 'Agendado'}
        </Badge>
      )
    }
  ];

  const modelColumns: Column<ModelMetrics>[] = [
    {
      key: 'name',
      header: 'Modelo',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-sm text-text-secondary">{row.type}</p>
        </div>
      )
    },
    {
      key: 'accuracy',
      header: 'Acurácia',
      render: (row) => (
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-bg-tertiary rounded-full max-w-[100px]">
            <div
              className="h-full rounded-full bg-accent-primary"
              style={{ width: `${row.accuracy}%` }}
            />
          </div>
          <span className="text-sm font-medium">{row.accuracy.toFixed(1)}%</span>
        </div>
      )
    },
    {
      key: 'f1Score',
      header: 'F1 Score',
      render: (row) => (
        <span className="font-mono">{row.f1Score.toFixed(2)}</span>
      )
    },
    {
      key: 'dataPoints',
      header: 'Data Points',
      render: (row) => (
        <span>{row.dataPoints.toLocaleString()}</span>
      )
    },
    {
      key: 'lastTrained',
      header: 'Último Treino',
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.lastTrained).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={
          row.status === 'ready' ? 'success' :
          row.status === 'training' ? 'warning' : 'danger'
        }>
          {row.status === 'ready' ? 'Pronto' :
           row.status === 'training' ? 'Treinando' : 'Desatualizado'}
        </Badge>
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Previsões com IA
            </h1>
            <p className="text-text-secondary mt-1">
              Machine Learning para previsões de negócio
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              value={filterPeriod}
              onChange={setFilterPeriod}
              options={[
                { value: 'week', label: 'Esta semana' },
                { value: 'month', label: 'Este mês' },
                { value: 'quarter', label: 'Este trimestre' },
                { value: 'year', label: 'Este ano' }
              ]}
              className="w-40"
            />
            <Button variant="outline" onClick={() => setShowTrainModal(true)}>
              <Settings className="h-4 w-4 mr-2" />
              Configurar
            </Button>
            <Button>
              <Play className="h-4 w-4 mr-2" />
              Nova Previsão
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Previsões Ativas"
            value="12"
            icon={<Brain className="h-5 w-5" />}
            iconColor="primary"
            change={8}
            changeLabel="vs. mês anterior"
          />
          <StatCard
            title="Acurácia Média"
            value="89.2%"
            icon={<Target className="h-5 w-5" />}
            iconColor="success"
            change={3.5}
            changeLabel="melhoria"
          />
          <StatCard
            title="Modelos Ativos"
            value="8"
            icon={<Zap className="h-5 w-5" />}
            iconColor="info"
            change={2}
            changeLabel="novos modelos"
          />
          <StatCard
            title="Economia Estimada"
            value="R$ 145K"
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="success"
            change={25}
            changeLabel="vs. decisões manuais"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Predictions Tab */}
        {activeTab === 'predictions' && (
          <div className="space-y-6">
            {/* Revenue Chart */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">
                    Previsão de Receita
                  </h3>
                  <p className="text-sm text-text-secondary">
                    Comparativo: Realizado vs Previsto
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Exportar
                </Button>
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={revenueChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis
                      stroke="#64748b"
                      tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="actual"
                      name="Realizado"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.2}
                    />
                    <Area
                      type="monotone"
                      dataKey="predicted"
                      name="Previsto"
                      stroke="#6366f1"
                      fill="#6366f1"
                      fillOpacity={0.2}
                      strokeDasharray="5 5"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Predictions Table */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Previsões Recentes
              </h3>
              <DataTable
                columns={predictionColumns}
                data={mockPredictions}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedPrediction(row)}
              />
            </Card>
          </div>
        )}

        {/* Models Tab */}
        {activeTab === 'models' && (
          <div className="space-y-6">
            {/* Accuracy Trend */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">
                    Evolução da Acurácia
                  </h3>
                  <p className="text-sm text-text-secondary">
                    Performance dos modelos ao longo do tempo
                  </p>
                </div>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={accuracyTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" domain={[80, 100]} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="accuracy"
                      stroke="#6366f1"
                      strokeWidth={2}
                      dot={{ fill: '#6366f1' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Models Table */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Modelos de ML
                </h3>
                <Button variant="outline" onClick={() => setShowTrainModal(true)}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retreinar Modelos
                </Button>
              </div>
              <DataTable
                columns={modelColumns}
                data={mockModels}
                keyExtractor={(row) => row.id}
              />
            </Card>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Fatores de Influência
              </h3>
              <div className="space-y-4">
                {[
                  { name: 'Sazonalidade', impact: 85 },
                  { name: 'Tendência de mercado', impact: 72 },
                  { name: 'Crescimento de clientes', impact: 68 },
                  { name: 'Eventos externos', impact: 45 },
                  { name: 'Promoções', impact: 38 }
                ].map((factor) => (
                  <div key={factor.name} className="flex items-center gap-4">
                    <span className="w-40 text-sm text-text-secondary">
                      {factor.name}
                    </span>
                    <div className="flex-1 h-2 bg-bg-tertiary rounded-full">
                      <div
                        className="h-full rounded-full bg-accent-primary"
                        style={{ width: `${factor.impact}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-12 text-right">
                      {factor.impact}%
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Métricas de Performance
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: 'MAE', value: '2.3%', desc: 'Mean Absolute Error' },
                  { label: 'RMSE', value: '3.1%', desc: 'Root Mean Square Error' },
                  { label: 'R²', value: '0.94', desc: 'Coefficient of Determination' },
                  { label: 'MAPE', value: '4.2%', desc: 'Mean Abs. Percentage Error' }
                ].map((metric) => (
                  <div key={metric.label} className="p-4 rounded-lg bg-bg-tertiary">
                    <p className="text-2xl font-bold text-text-primary">
                      {metric.value}
                    </p>
                    <p className="text-sm font-medium text-accent-primary">
                      {metric.label}
                    </p>
                    <p className="text-xs text-text-muted mt-1">{metric.desc}</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Train Modal */}
        <Modal
          isOpen={showTrainModal}
          onClose={() => setShowTrainModal(false)}
          title="Configurar Treinamento"
          size="md"
        >
          <div className="space-y-4">
            <p className="text-text-secondary">
              Configure os parâmetros para retreinar os modelos de ML.
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Modelos para Retreinar
                </label>
                <div className="space-y-2">
                  {mockModels.map((model) => (
                    <label key={model.id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        className="rounded border-border-default bg-bg-tertiary"
                        defaultChecked={model.status === 'outdated'}
                      />
                      <span className="text-text-primary">{model.name}</span>
                      {model.status === 'outdated' && (
                        <Badge variant="warning" size="sm">Desatualizado</Badge>
                      )}
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Período de Dados
                </label>
                <Select
                  value={trainingDataPeriod}
                  onChange={(value) => setTrainingDataPeriod(value)}
                  options={[
                    { value: '3months', label: 'Últimos 3 meses' },
                    { value: '6months', label: 'Últimos 6 meses' },
                    { value: '12months', label: 'Último ano' },
                    { value: 'all', label: 'Todos os dados' }
                  ]}
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowTrainModal(false)}>
                Cancelar
              </Button>
              <Button onClick={() => setShowTrainModal(false)}>
                <Play className="h-4 w-4 mr-2" />
                Iniciar Treinamento
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
