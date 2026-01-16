'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Target,
  Users,
  DollarSign,
  Calendar,
  Clock,
  Zap,
  BarChart3,
  LineChart as LineChartIcon,
  PieChart as PieChartIcon,
  RefreshCw,
  Download,
  Settings,
  Lightbulb,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Input,
  Badge,
  StatCard,
  SimpleTabBar,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
} from 'recharts';

interface AIInsight {
  id: string;
  type: 'opportunity' | 'risk' | 'trend' | 'anomaly';
  category: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  confidence: number;
  actionable: boolean;
  suggestedAction?: string;
  generatedAt: string;
}

interface Prediction {
  id: string;
  metric: string;
  currentValue: number;
  predictedValue: number;
  variance: number;
  confidence: number;
  period: string;
  trend: 'up' | 'down' | 'stable';
}

const mockInsights: AIInsight[] = [
  {
    id: '1',
    type: 'opportunity',
    category: 'Vendas',
    title: 'Oportunidade de Upsell em Contratos',
    description: '15 clientes com potencial para upgrade de serviços baseado no padrão de uso.',
    impact: 'high',
    confidence: 87,
    actionable: true,
    suggestedAction: 'Entrar em contato com os clientes identificados para oferecer upgrade.',
    generatedAt: '2024-12-20T10:00:00',
  },
  {
    id: '2',
    type: 'risk',
    category: 'Operações',
    title: 'Risco de Turnover Elevado',
    description: 'Modelo prevê aumento de 25% no turnover nos próximos 3 meses baseado em padrões históricos.',
    impact: 'high',
    confidence: 82,
    actionable: true,
    suggestedAction: 'Implementar programa de retenção e pesquisa de clima organizacional.',
    generatedAt: '2024-12-20T09:30:00',
  },
  {
    id: '3',
    type: 'trend',
    category: 'Financeiro',
    title: 'Tendência de Aumento em Inadimplência',
    description: 'Taxa de inadimplência projetada para aumentar 3pp no próximo trimestre.',
    impact: 'medium',
    confidence: 75,
    actionable: true,
    suggestedAction: 'Intensificar ações de cobrança preventiva.',
    generatedAt: '2024-12-20T09:00:00',
  },
  {
    id: '4',
    type: 'anomaly',
    category: 'Operações',
    title: 'Padrão Anormal de Horas Extras',
    description: 'Posto Central registrando 40% mais horas extras que a média.',
    impact: 'medium',
    confidence: 92,
    actionable: true,
    suggestedAction: 'Revisar escala e avaliar necessidade de reforço.',
    generatedAt: '2024-12-19T18:00:00',
  },
  {
    id: '5',
    type: 'opportunity',
    category: 'Clientes',
    title: 'Clientes Propensos a Renovação',
    description: '8 contratos com alta probabilidade de renovação antecipada.',
    impact: 'medium',
    confidence: 79,
    actionable: true,
    suggestedAction: 'Agendar reuniões de renovação antecipada.',
    generatedAt: '2024-12-19T15:00:00',
  },
];

const mockPredictions: Prediction[] = [
  { id: '1', metric: 'Faturamento', currentValue: 1250000, predictedValue: 1380000, variance: 10.4, confidence: 85, period: 'Jan/2025', trend: 'up' },
  { id: '2', metric: 'Novos Contratos', currentValue: 8, predictedValue: 12, variance: 50, confidence: 72, period: 'Jan/2025', trend: 'up' },
  { id: '3', metric: 'Churn Rate', currentValue: 2.5, predictedValue: 3.1, variance: 24, confidence: 78, period: 'Jan/2025', trend: 'up' },
  { id: '4', metric: 'Custo Operacional', currentValue: 920000, predictedValue: 945000, variance: 2.7, confidence: 88, period: 'Jan/2025', trend: 'up' },
  { id: '5', metric: 'NPS Score', currentValue: 72, predictedValue: 75, variance: 4.2, confidence: 65, period: 'Jan/2025', trend: 'up' },
];

const revenueData = [
  { month: 'Jul', real: 980000, previsto: 950000 },
  { month: 'Ago', real: 1050000, previsto: 1020000 },
  { month: 'Set', real: 1120000, previsto: 1100000 },
  { month: 'Out', real: 1180000, previsto: 1150000 },
  { month: 'Nov', real: 1200000, previsto: 1220000 },
  { month: 'Dez', real: 1250000, previsto: 1280000 },
  { month: 'Jan', real: null, previsto: 1380000 },
  { month: 'Fev', real: null, previsto: 1420000 },
];

const categoryData = [
  { name: 'Vigilância', value: 45 },
  { name: 'Portaria', value: 25 },
  { name: 'Limpeza', value: 15 },
  { name: 'Recepção', value: 10 },
  { name: 'Outros', value: 5 },
];

const performanceData = [
  { subject: 'Qualidade', A: 85, fullMark: 100 },
  { subject: 'Pontualidade', A: 78, fullMark: 100 },
  { subject: 'Satisfação', A: 72, fullMark: 100 },
  { subject: 'Eficiência', A: 88, fullMark: 100 },
  { subject: 'Retenção', A: 65, fullMark: 100 },
  { subject: 'Crescimento', A: 82, fullMark: 100 },
];

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const tabs = [
  { value: 'insights', label: 'Insights', icon: <Lightbulb className="h-4 w-4" /> },
  { value: 'predictions', label: 'Previsões', icon: <TrendingUp className="h-4 w-4" /> },
  { value: 'analytics', label: 'Análises', icon: <BarChart3 className="h-4 w-4" /> },
];

const insightTypeColors: Record<AIInsight['type'], 'success' | 'warning' | 'danger' | 'info'> = {
  opportunity: 'success',
  risk: 'danger',
  trend: 'info',
  anomaly: 'warning',
};

const insightTypeLabels: Record<AIInsight['type'], string> = {
  opportunity: 'Oportunidade',
  risk: 'Risco',
  trend: 'Tendência',
  anomaly: 'Anomalia',
};

const insightTypeIcons: Record<AIInsight['type'], React.ReactNode> = {
  opportunity: <Target className="h-5 w-5" />,
  risk: <AlertTriangle className="h-5 w-5" />,
  trend: <TrendingUp className="h-5 w-5" />,
  anomaly: <Zap className="h-5 w-5" />,
};

export function AIAnalyticsPage() {
  const [activeTab, setActiveTab] = useState('insights');
  const [selectedInsight, setSelectedInsight] = useState<AIInsight | null>(null);

  const stats = useMemo(() => {
    const opportunities = mockInsights.filter((i) => i.type === 'opportunity').length;
    const risks = mockInsights.filter((i) => i.type === 'risk').length;
    const highImpact = mockInsights.filter((i) => i.impact === 'high').length;
    const avgConfidence = mockInsights.reduce((acc, i) => acc + i.confidence, 0) / mockInsights.length;

    return { opportunities, risks, highImpact, avgConfidence };
  }, []);

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Analytics IA</h1>
            <p className="text-text-secondary mt-1">Insights e previsões baseadas em inteligência artificial</p>
          </div>
          <div className="flex items-center gap-3">
            {
            <div className="flex gap-2">
              <Button variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Atualizar
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>
          }
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="Oportunidades"
            value={stats.opportunities.toString()}
            icon={<Target className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Riscos Identificados"
            value={stats.risks.toString()}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Alto Impacto"
            value={stats.highImpact.toString()}
            icon={<Zap className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Confiança Média"
            value={`${stats.avgConfidence.toFixed(0)}%`}
            icon={<Brain className="h-5 w-5" />}
            iconColor="primary"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {mockInsights.map((insight) => (
              <Card
                key={insight.id}
                className="p-6 hover:border-accent-primary/50 transition-colors cursor-pointer"
                onClick={() => setSelectedInsight(insight)}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg ${
                    insight.type === 'opportunity' ? 'bg-accent-success/20 text-accent-success' :
                    insight.type === 'risk' ? 'bg-accent-danger/20 text-accent-danger' :
                    insight.type === 'trend' ? 'bg-accent-info/20 text-accent-info' :
                    'bg-accent-warning/20 text-accent-warning'
                  }`}>
                    {insightTypeIcons[insight.type]}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <Badge variant={insightTypeColors[insight.type]}>{insightTypeLabels[insight.type]}</Badge>
                      <span className="text-sm text-text-secondary">{insight.category}</span>
                      <Badge variant={insight.impact === 'high' ? 'danger' : insight.impact === 'medium' ? 'warning' : 'info'}>
                        {insight.impact === 'high' ? 'Alto Impacto' : insight.impact === 'medium' ? 'Médio Impacto' : 'Baixo Impacto'}
                      </Badge>
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary">{insight.title}</h3>
                    <p className="text-text-secondary mt-1">{insight.description}</p>
                    <div className="flex items-center gap-4 mt-3 text-sm">
                      <span className="text-text-secondary">
                        Confiança: <span className="text-text-primary font-medium">{insight.confidence}%</span>
                      </span>
                      <span className="text-text-secondary">
                        Gerado: {new Date(insight.generatedAt).toLocaleString('pt-BR')}
                      </span>
                    </div>
                  </div>
                  {insight.actionable && (
                    <Button size="sm" variant="outline">
                      Ver Ação
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </motion.div>
        )}

        {/* Predictions Tab */}
        {activeTab === 'predictions' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Projeção de Faturamento</h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d', borderRadius: '8px' }}
                      formatter={(value: number | null) => value ? value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'N/A'}
                    />
                    <Legend />
                    <Area type="monotone" dataKey="real" name="Real" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="previsto" name="Previsto" stroke="#10b981" fill="#10b981" fillOpacity={0.2} strokeDasharray="5 5" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mockPredictions.map((prediction) => (
                <Card key={prediction.id} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-text-primary">{prediction.metric}</h4>
                    <Badge variant={prediction.trend === 'up' ? (prediction.metric.includes('Churn') ? 'danger' : 'success') : 'info'}>
                      {prediction.period}
                    </Badge>
                  </div>
                  <div className="flex items-end gap-4">
                    <div>
                      <p className="text-sm text-text-secondary">Atual</p>
                      <p className="text-xl font-bold text-text-primary">
                        {prediction.metric.includes('Rate') || prediction.metric.includes('NPS')
                          ? `${prediction.currentValue}${prediction.metric.includes('Rate') ? '%' : ''}`
                          : prediction.currentValue.toLocaleString('pt-BR', prediction.metric.includes('Contratos') ? {} : { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <div className={`flex items-center gap-1 ${
                      prediction.trend === 'up'
                        ? (prediction.metric.includes('Churn') || prediction.metric.includes('Custo') ? 'text-accent-danger' : 'text-accent-success')
                        : 'text-accent-info'
                    }`}>
                      {prediction.trend === 'up' ? <ArrowUpRight className="h-5 w-5" /> : <ArrowDownRight className="h-5 w-5" />}
                      <span className="font-bold">{prediction.variance.toFixed(1)}%</span>
                    </div>
                    <div className="flex-1 text-right">
                      <p className="text-sm text-text-secondary">Previsto</p>
                      <p className="text-xl font-bold text-accent-primary">
                        {prediction.metric.includes('Rate') || prediction.metric.includes('NPS')
                          ? `${prediction.predictedValue}${prediction.metric.includes('Rate') ? '%' : ''}`
                          : prediction.predictedValue.toLocaleString('pt-BR', prediction.metric.includes('Contratos') ? {} : { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-border-subtle">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-text-secondary">Confiança</span>
                      <span className="text-text-primary font-medium">{prediction.confidence}%</span>
                    </div>
                    <div className="mt-2 h-2 bg-bg-tertiary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                        style={{ width: `${prediction.confidence}%` }}
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </motion.div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Distribuição por Categoria</h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Performance Operacional</h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={performanceData}>
                    <PolarGrid stroke="#2d2d3d" />
                    <PolarAngleAxis dataKey="subject" stroke="#94a3b8" />
                    <PolarRadiusAxis stroke="#94a3b8" />
                    <Radar name="Performance" dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </motion.div>
        )}
      </div>
    </MainLayout>
  );
}
