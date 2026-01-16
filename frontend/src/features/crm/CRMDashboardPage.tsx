'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Users,
  Target,
  DollarSign,
  FileText,
  Calendar,
  Clock,
  ArrowRight,
  BarChart3,
  PieChart,
  Activity,
  Award,
  Zap,
  Phone,
  Mail,
  Building2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Download,
  Filter,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Select,
  StatCard,
  StatGrid,
  Progress,
  Skeleton,
  Avatar,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts';

// Importações do módulo CRM
import {
  useCRMDashboard,
  useCRMPipeline,
  useCRMFunnel,
  useCommissionRanking,
} from './hooks';

// ==================== CONSTANTS ====================

const STAGE_COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#c084fc', '#d8b4fe'];

const SOURCE_COLORS: Record<string, string> = {
  referral: '#6366f1',
  website: '#22c55e',
  linkedin: '#f59e0b',
  cold_call: '#ef4444',
  event: '#8b5cf6',
  other: '#64748b',
};

const DEAL_STAGE_CONFIG: Record<string, { label: string; variant: 'success' | 'danger' | 'warning' | 'info' }> = {
  won: { label: 'Ganho', variant: 'success' },
  lost: { label: 'Perdido', variant: 'danger' },
  negotiation: { label: 'Negociação', variant: 'warning' },
  proposal: { label: 'Proposta', variant: 'info' },
};

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('pt-BR');
};

// ==================== COMPONENT ====================

export default function CRMDashboardPage() {
  const [period, setPeriod] = useState('month');

  // Hooks de dados
  const { data: dashboardData, isLoading, isError, error, refetch } = useCRMDashboard({ period });
  const { data: pipelineData, isLoading: isLoadingPipeline } = useCRMPipeline({ period });
  const { data: funnelData, isLoading: isLoadingFunnel } = useCRMFunnel({ period });
  const { data: rankingData, isLoading: isLoadingRanking } = useCommissionRanking({ period, limit: 5 });

  // Stats calculados
  const stats = useMemo(() => ({
    totalRevenue: dashboardData?.total_revenue || 0,
    totalPipeline: dashboardData?.total_pipeline || 0,
    avgDealSize: dashboardData?.avg_deal_size || 0,
    winRate: dashboardData?.win_rate || 0,
    avgCycleTime: dashboardData?.avg_cycle_time || 0,
    revenueChange: dashboardData?.revenue_change || 0,
    pipelineChange: dashboardData?.pipeline_change || 0,
    dealSizeChange: dashboardData?.deal_size_change || 0,
    winRateChange: dashboardData?.win_rate_change || 0,
    cycleTimeChange: dashboardData?.cycle_time_change || 0,
  }), [dashboardData]);

  // Dados para gráficos
  const revenueChartData = dashboardData?.revenue_trend || [];
  const conversionBySource = dashboardData?.conversion_by_source || [];
  const activityData = dashboardData?.activity_data || [];
  const recentDeals = dashboardData?.recent_deals || [];
  const topSellers = rankingData || [];
  const pipeline = pipelineData?.stages || [];
  const funnel = funnelData || [];

  // Loading state
  if (isLoading && !dashboardData) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Skeleton className="h-10 w-48" />
            <Skeleton className="h-10 w-64" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-28" />)}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Skeleton className="h-96 lg:col-span-2" />
            <Skeleton className="h-96" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Skeleton className="h-80" />
            <Skeleton className="h-80" />
          </div>
        </div>
      </MainLayout>
    );
  }

  // Error state
  if (isError) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center h-96 gap-4">
          <AlertTriangle className="h-16 w-16 text-accent-danger" />
          <h2 className="text-xl font-semibold">Erro ao carregar dashboard</h2>
          <p className="text-text-secondary">{(error as Error)?.message}</p>
          <Button onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Tentar novamente
          </Button>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Dashboard CRM
            </h1>
            <p className="text-text-secondary mt-1">
              Visão geral de vendas, pipeline e performance da equipe
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              options={[
                { value: 'week', label: 'Esta Semana' },
                { value: 'month', label: 'Este Mês' },
                { value: 'quarter', label: 'Este Trimestre' },
                { value: 'year', label: 'Este Ano' },
              ]}
              value={period}
              onChange={setPeriod}
              className="w-40"
            />
            <Button variant="outline" leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />} onClick={() => refetch()}>
              Atualizar
            </Button>
            <Button variant="primary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
          </div>
        </div>

        {/* KPIs */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Receita do Mês"
              value={formatCurrency(stats.totalRevenue)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
              change={stats.revenueChange}
              changeLabel="vs mês anterior"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Pipeline Total"
              value={formatCurrency(stats.totalPipeline)}
              icon={<Target className="w-6 h-6" />}
              iconColor="primary"
              change={stats.pipelineChange}
              changeLabel="vs mês anterior"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Ticket Médio"
              value={formatCurrency(stats.avgDealSize)}
              icon={<BarChart3 className="w-6 h-6" />}
              iconColor="info"
              change={stats.dealSizeChange}
              changeLabel="vs mês anterior"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Taxa de Conversão"
              value={`${stats.winRate}%`}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="success"
              change={stats.winRateChange}
              changeLabel="vs mês anterior"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Ciclo Médio"
              value={`${stats.avgCycleTime} dias`}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
              change={stats.cycleTimeChange}
              changeLabel="vs mês anterior"
            />
          </motion.div>
        </StatGrid>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Revenue Chart */}
          <Card className="lg:col-span-2">
            <CardHeader title="Evolução de Receita" />
            <CardBody>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={revenueChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#8b8b9a" />
                    <YAxis stroke="#8b8b9a" tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d', borderRadius: '8px' }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Legend />
                    <Bar dataKey="previous" name="Ano Anterior" fill="#6366f1" opacity={0.5} radius={[4, 4, 0, 0]} />
                    <Line type="monotone" dataKey="current" name="Ano Atual" stroke="#22c55e" strokeWidth={3} dot={{ fill: '#22c55e', r: 4 }} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Conversion by Source */}
          <Card>
            <CardHeader title="Conversão por Origem" />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={conversionBySource}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {conversionBySource.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={SOURCE_COLORS[entry.source] || entry.color || STAGE_COLORS[index % 5]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">
                {conversionBySource.map((item: any) => (
                  <div key={item.name || item.source} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: SOURCE_COLORS[item.source] || item.color }} />
                      <span className="text-sm text-text-secondary">{item.name || item.source}</span>
                    </div>
                    <span className="text-sm font-medium">{item.value}%</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Funnel and Pipeline */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sales Funnel */}
          <Card>
            <CardHeader title="Funil de Vendas" />
            <CardBody>
              {isLoadingFunnel ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12" />)}
                </div>
              ) : funnel.length > 0 ? (
                <div className="space-y-4">
                  {funnel.map((stage: any, index: number) => (
                    <div key={stage.stage || stage.name}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-medium">{stage.stage || stage.name}</span>
                          <Badge variant="secondary" size="sm">{stage.count}</Badge>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-sm text-text-secondary">{formatCurrency(stage.value)}</span>
                          {index > 0 && (
                            <span className="text-xs text-success">{stage.conversion}%</span>
                          )}
                        </div>
                      </div>
                      <div className="relative">
                        <div className="h-8 bg-bg-tertiary rounded-lg overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${stage.conversion || 100}%` }}
                            transition={{ duration: 0.8, delay: index * 0.1 }}
                            className="h-full rounded-lg"
                            style={{
                              background: `linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)`,
                              opacity: 1 - (index * 0.15),
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-text-muted">
                  <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Sem dados de funil disponíveis</p>
                </div>
              )}
            </CardBody>
          </Card>

          {/* Pipeline by Stage */}
          <Card>
            <CardHeader title="Pipeline por Estágio" />
            <CardBody>
              {isLoadingPipeline ? (
                <Skeleton className="h-72" />
              ) : pipeline.length > 0 ? (
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={pipeline} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis type="number" stroke="#8b8b9a" tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`} />
                      <YAxis type="category" dataKey="name" stroke="#8b8b9a" width={100} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-12 text-text-muted">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Sem dados de pipeline disponíveis</p>
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Activity and Top Sellers */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Activity Chart */}
          <Card>
            <CardHeader title="Atividades da Equipe" />
            <CardBody>
              {activityData.length > 0 ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={activityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="day" stroke="#8b8b9a" />
                      <YAxis stroke="#8b8b9a" />
                      <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }} />
                      <Legend />
                      <Bar dataKey="calls" name="Ligações" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="emails" name="Emails" fill="#22c55e" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="meetings" name="Reuniões" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-12 text-text-muted">
                  <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Sem dados de atividades disponíveis</p>
                </div>
              )}
            </CardBody>
          </Card>

          {/* Top Sellers */}
          <Card>
            <CardHeader
              title="Top Vendedores"
              action={
                <Button variant="ghost" size="sm" rightIcon={<ChevronRight className="w-4 h-4" />}>
                  Ver Todos
                </Button>
              }
            />
            <CardBody>
              {isLoadingRanking ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-14" />)}
                </div>
              ) : topSellers.length > 0 ? (
                <div className="space-y-4">
                  {topSellers.map((seller: any, index: number) => (
                    <div key={seller.id} className="flex items-center gap-4">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-accent-primary/20 text-accent-primary font-bold text-sm">
                        {index + 1}
                      </div>
                      <Avatar name={seller.name} size="sm" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{seller.name}</span>
                          <span className="text-sm font-semibold text-success">{formatCurrency(seller.total_sales || seller.revenue || 0)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={(seller.total_sales || seller.revenue || 0) / (seller.target || 100) * 100} size="sm" className="flex-1" />
                          <span className="text-xs text-text-secondary">{seller.contracts_count || seller.deals || 0} deals</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-text-muted">
                  <Award className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Sem dados de vendedores disponíveis</p>
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Recent Deals */}
        <Card>
          <CardHeader
            title="Negociações Recentes"
            action={
              <Button variant="ghost" size="sm" rightIcon={<ChevronRight className="w-4 h-4" />}>
                Ver Todas
              </Button>
            }
          />
          <CardBody className="p-0">
            {recentDeals.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-bg-tertiary border-b border-border-subtle">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase">Cliente</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase">Valor</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase">Vendedor</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase">Data</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-subtle">
                    {recentDeals.map((deal: any) => {
                      const stageConfig = DEAL_STAGE_CONFIG[deal.stage] || { label: deal.stage, variant: 'info' as const };
                      return (
                        <tr key={deal.id} className="hover:bg-bg-tertiary transition-colors">
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <Building2 className="w-4 h-4 text-text-secondary" />
                              <span className="font-medium">{deal.client || deal.client_name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 font-semibold">{formatCurrency(deal.value)}</td>
                          <td className="px-4 py-3 text-text-secondary">{deal.seller || deal.seller_name}</td>
                          <td className="px-4 py-3 text-text-secondary">
                            {formatDate(deal.date || deal.created_at)}
                          </td>
                          <td className="px-4 py-3">
                            <Badge variant={stageConfig.variant}>
                              {stageConfig.label}
                            </Badge>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-text-muted">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Sem negociações recentes</p>
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </MainLayout>
  );
}
