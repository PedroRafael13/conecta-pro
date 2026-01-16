'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  TrendingUp,
  Users,
  Calendar,
  Download,
  Filter,
  Search,
  Eye,
  Calculator,
  Target,
  Award,
  BarChart3,
  PieChart,
  CheckCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Skeleton,
  Avatar,
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
  Cell,
} from 'recharts';

// Importações do módulo CRM
import {
  useCommissions,
  useCommissionStats,
  useCommissionRanking,
  useCreateCommission,
  useApproveCommission,
  usePayCommission,
} from './hooks';
import type {
  Commission,
  CommissionFilter,
  CommissionStatus,
} from './types';
import { CommissionStatus as CommissionStatusEnum } from './types';

// ==================== CONSTANTS ====================

const STATUS_CONFIG: Record<string, { label: string; color: 'neutral' | 'warning' | 'success' | 'danger' | 'info'; icon: React.ElementType }> = {
  pending: { label: 'Pendente', color: 'warning', icon: Clock },
  approved: { label: 'Aprovada', color: 'info', icon: CheckCircle },
  paid: { label: 'Paga', color: 'success', icon: CheckCircle },
  disputed: { label: 'Contestada', color: 'danger', icon: AlertTriangle },
  cancelled: { label: 'Cancelada', color: 'neutral', icon: AlertTriangle },
};

const TABS = [
  { value: 'commissions', label: 'Comissões', icon: <DollarSign className="h-4 w-4" /> },
  { value: 'ranking', label: 'Ranking', icon: <Award className="h-4 w-4" /> },
  { value: 'simulation', label: 'Simulador', icon: <Calculator className="h-4 w-4" /> },
];

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

// ==================== COMPONENT ====================

export function CommissionsPage() {
  // State
  const [activeTab, setActiveTab] = useState('commissions');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('2026-01');
  const [statusFilter, setStatusFilter] = useState<CommissionStatus | ''>('');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedCommission, setSelectedCommission] = useState<Commission | null>(null);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Simulation state
  const [simulationValues, setSimulationValues] = useState({
    sales: 100000,
    rate: 5,
    bonus: 0,
  });

  // Construir filtros
  const filters: CommissionFilter & { page: number; page_size: number } = useMemo(() => ({
    page,
    page_size: pageSize,
    status: statusFilter || undefined,
    period: selectedPeriod || undefined,
    search: searchTerm || undefined,
  }), [page, statusFilter, selectedPeriod, searchTerm]);

  // Hooks de dados
  const { data: commissionsData, isLoading, isError, error, refetch } = useCommissions(filters);
  const { data: stats, isLoading: isLoadingStats } = useCommissionStats({ period: selectedPeriod });
  const { data: rankingData, isLoading: isLoadingRanking } = useCommissionRanking({ period: selectedPeriod, limit: 10 });
  const approveMutation = useApproveCommission();
  const payMutation = usePayCommission();

  // Dados processados
  const commissions = commissionsData?.items || [];
  const totalCommissions = commissionsData?.total || 0;

  // Handlers
  const handleApprove = useCallback(async (id: string) => {
    try {
      await approveMutation.mutateAsync(id);
      setShowDetailModal(false);
      setSelectedCommission(null);
    } catch (err) {
      console.error('Erro ao aprovar comissão:', err);
    }
  }, [approveMutation]);

  const handlePay = useCallback(async (id: string) => {
    try {
      await payMutation.mutateAsync(id);
      setShowDetailModal(false);
      setSelectedCommission(null);
    } catch (err) {
      console.error('Erro ao pagar comissão:', err);
    }
  }, [payMutation]);

  const openCommissionDetail = (commission: Commission) => {
    setSelectedCommission(commission);
    setShowDetailModal(true);
  };

  // Colunas da tabela
  const columns: Column<Commission>[] = [
    {
      key: 'salesperson',
      header: 'Vendedor',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.salesperson_name} size="sm" />
          <div>
            <p className="font-medium text-text-primary">{row.salesperson_name}</p>
            <p className="text-xs text-text-secondary">{row.salesperson_code}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'period',
      header: 'Período',
      sortable: true,
      render: (row) => <span className="text-text-primary">{row.period}</span>,
    },
    {
      key: 'total_sales',
      header: 'Vendas',
      sortable: true,
      render: (row) => (
        <span className="font-medium text-text-primary">
          {formatCurrency(row.total_sales)}
        </span>
      ),
    },
    {
      key: 'commission_rate',
      header: 'Taxa',
      sortable: true,
      render: (row) => <Badge variant="info">{row.commission_rate}%</Badge>,
    },
    {
      key: 'net_commission',
      header: 'Comissão Líquida',
      sortable: true,
      render: (row) => (
        <span className="font-semibold text-accent-success">
          {formatCurrency(row.net_commission)}
        </span>
      ),
    },
    {
      key: 'contracts_count',
      header: 'Contratos',
      sortable: true,
      render: (row) => <span className="text-text-primary">{row.contracts_count}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row) => {
        const config = STATUS_CONFIG[row.status] || STATUS_CONFIG.pending;
        const Icon = config.icon;
        return (
          <Badge variant={config.color} leftIcon={<Icon className="w-3 h-3" />}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            openCommissionDetail(row);
          }}
        >
          <Eye className="h-4 w-4" />
        </Button>
      ),
    },
  ];

  // Estatísticas calculadas
  const displayStats = useMemo(() => {
    return {
      totalCommissions: stats?.total_commissions || 0,
      totalSales: stats?.total_sales || 0,
      avgRate: stats?.avg_rate || 0,
      salespeoplCount: stats?.salespeople_count || 0,
      pendingCount: stats?.pending_count || 0,
    };
  }, [stats]);

  // Dados para gráfico de tendência
  const trendData = useMemo(() => {
    return stats?.trend_data || [];
  }, [stats]);

  // Cálculo da simulação
  const simulatedCommission = (simulationValues.sales * simulationValues.rate / 100) + simulationValues.bonus;

  // Loading state
  if (isLoading && !commissionsData) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-24" />)}
          </div>
          <Skeleton className="h-64" />
          <Skeleton className="h-96" />
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
          <h2 className="text-xl font-semibold">Erro ao carregar comissões</h2>
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
              Comissões de Vendas
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão e cálculo de comissões dos vendedores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary"
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <option value="2026-01">Janeiro/2026</option>
              <option value="2025-12">Dezembro/2025</option>
              <option value="2025-11">Novembro/2025</option>
            </select>
            <Button variant="outline" leftIcon={<Download className="h-4 w-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Calculator className="h-4 w-4" />}>
              Calcular Período
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <StatCard
            title="Total Comissões"
            value={isLoadingStats ? '...' : formatCurrency(displayStats.totalCommissions)}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Total Vendas"
            value={isLoadingStats ? '...' : formatCurrency(displayStats.totalSales)}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Taxa Média"
            value={isLoadingStats ? '...' : `${displayStats.avgRate.toFixed(1)}%`}
            icon={<Target className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Vendedores"
            value={isLoadingStats ? '...' : displayStats.salespeoplCount.toString()}
            icon={<Users className="h-5 w-5" />}
          />
          <StatCard
            title="Pendentes"
            value={isLoadingStats ? '...' : displayStats.pendingCount.toString()}
            changeLabel="aguardando aprovação"
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
        </StatGrid>

        {/* Chart */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Evolução de Comissões vs Meta
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                  <XAxis dataKey="month" stroke="#64748b" />
                  <YAxis stroke="#64748b" tickFormatter={(v) => `R$ ${(v/1000)}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px',
                    }}
                    formatter={(value: number) => [formatCurrency(value), '']}
                  />
                  <Area
                    type="monotone"
                    dataKey="total"
                    name="Total Comissões"
                    stroke="#10b981"
                    fillOpacity={1}
                    fill="url(#colorTotal)"
                  />
                  <Area
                    type="monotone"
                    dataKey="meta"
                    name="Meta"
                    stroke="#6366f1"
                    strokeDasharray="5 5"
                    fill="none"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Tabs */}
        <SimpleTabBar
          tabs={TABS}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Commissions Tab Content */}
        {activeTab === 'commissions' && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-text-primary">
                  Comissões do Período
                </h3>
                <div className="flex items-center gap-3">
                  <Input
                    placeholder="Buscar vendedor..."
                    leftIcon={<Search className="h-4 w-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-64"
                  />
                  <Button variant="ghost" size="sm" onClick={() => refetch()} disabled={isLoading}>
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardBody className="p-0">
              <DataTable<Commission>
                data={commissions}
                columns={columns}
                keyExtractor={(row) => row.id}
                onRowClick={openCommissionDetail}
              />
            </CardBody>
          </Card>
        )}

        {/* Ranking Tab Content */}
        {activeTab === 'ranking' && (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Ranking de Vendedores
              </h3>
            </CardHeader>
            <CardBody>
              {isLoadingRanking ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-20" />)}
                </div>
              ) : (rankingData?.length || 0) > 0 ? (
                <div className="space-y-4">
                  {rankingData?.map((seller, index) => (
                    <motion.div
                      key={seller.seller_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg"
                    >
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                        index === 0 ? 'bg-yellow-500/20 text-yellow-500' :
                        index === 1 ? 'bg-gray-400/20 text-gray-400' :
                        index === 2 ? 'bg-orange-500/20 text-orange-500' :
                        'bg-bg-secondary text-text-secondary'
                      }`}>
                        {index + 1}º
                      </div>
                      <Avatar name={seller.name} size="md" />
                      <div className="flex-1">
                        <p className="font-semibold text-text-primary">{seller.name}</p>
                        <p className="text-sm text-text-secondary">
                          {seller.contracts_count} contratos | Taxa conversão: {seller.conversion_rate}%
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-text-primary">
                          {formatCurrency(seller.total_sales)}
                        </p>
                        <p className="text-sm text-accent-success">
                          Comissão: {formatCurrency(seller.total_commission)}
                        </p>
                      </div>
                      <div className={`flex items-center gap-1 ${seller.trend === 'up' || seller.trend === 'stable' ? 'text-accent-success' : 'text-accent-danger'}`}>
                        <TrendingUp className={`h-4 w-4 ${seller.trend === 'down' ? 'rotate-180' : ''}`} />
                        <span className="font-medium">{seller.trend === 'up' ? '↑' : seller.trend === 'down' ? '↓' : '→'}</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-text-muted">
                  <Award className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Nenhum dado de ranking disponível</p>
                </div>
              )}
            </CardBody>
          </Card>
        )}

        {/* Simulation Tab Content */}
        {activeTab === 'simulation' && (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Simulador de Comissões
              </h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Valor Total de Vendas
                    </label>
                    <Input
                      type="number"
                      leftIcon={<DollarSign className="h-4 w-4" />}
                      value={simulationValues.sales}
                      onChange={(e) => setSimulationValues(prev => ({ ...prev, sales: Number(e.target.value) }))}
                      placeholder="100000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Taxa de Comissão (%)
                    </label>
                    <Input
                      type="number"
                      step="0.5"
                      value={simulationValues.rate}
                      onChange={(e) => setSimulationValues(prev => ({ ...prev, rate: Number(e.target.value) }))}
                      placeholder="5"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Bônus Adicional
                    </label>
                    <Input
                      type="number"
                      leftIcon={<DollarSign className="h-4 w-4" />}
                      value={simulationValues.bonus}
                      onChange={(e) => setSimulationValues(prev => ({ ...prev, bonus: Number(e.target.value) }))}
                      placeholder="0"
                    />
                  </div>
                </div>
                <div className="flex flex-col items-center justify-center p-8 bg-bg-tertiary rounded-xl">
                  <p className="text-text-secondary mb-2">Comissão Estimada</p>
                  <p className="text-4xl font-bold text-accent-success">
                    {formatCurrency(simulatedCommission)}
                  </p>
                  <div className="mt-4 text-sm text-text-secondary">
                    <p>Base: {formatCurrency(simulationValues.sales * simulationValues.rate / 100)}</p>
                    {simulationValues.bonus > 0 && (
                      <p>+ Bônus: {formatCurrency(simulationValues.bonus)}</p>
                    )}
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes da Comissão"
          size="lg"
        >
          {selectedCommission && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
                <Avatar name={selectedCommission.salesperson_name} size="lg" />
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedCommission.salesperson_name}</h3>
                  <p className="text-text-secondary">{selectedCommission.period}</p>
                  <Badge variant={STATUS_CONFIG[selectedCommission.status]?.color || 'neutral'} className="mt-2">
                    {STATUS_CONFIG[selectedCommission.status]?.label || selectedCommission.status}
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary">Total Vendas</p>
                  <p className="text-xl font-semibold text-text-primary">
                    {formatCurrency(selectedCommission.total_sales)}
                  </p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary">Contratos</p>
                  <p className="text-xl font-semibold text-text-primary">{selectedCommission.contracts_count}</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between p-3 bg-bg-secondary rounded-lg">
                  <span className="text-text-secondary">Comissão Base ({selectedCommission.commission_rate}%)</span>
                  <span className="text-text-primary">
                    {formatCurrency(selectedCommission.commission_value)}
                  </span>
                </div>
                {selectedCommission.bonuses > 0 && (
                  <div className="flex justify-between p-3 bg-accent-success/10 rounded-lg">
                    <span className="text-accent-success">+ Bônus</span>
                    <span className="text-accent-success">
                      {formatCurrency(selectedCommission.bonuses)}
                    </span>
                  </div>
                )}
                {selectedCommission.deductions > 0 && (
                  <div className="flex justify-between p-3 bg-accent-danger/10 rounded-lg">
                    <span className="text-accent-danger">- Deduções</span>
                    <span className="text-accent-danger">
                      {formatCurrency(selectedCommission.deductions)}
                    </span>
                  </div>
                )}
                <div className="flex justify-between p-4 bg-accent-primary/10 rounded-lg border border-accent-primary/30">
                  <span className="font-semibold text-text-primary">Total Líquido</span>
                  <span className="font-bold text-xl text-accent-success">
                    {formatCurrency(selectedCommission.net_commission)}
                  </span>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fechar
                </Button>
                {selectedCommission.status === 'pending' && (
                  <Button
                    variant="primary"
                    leftIcon={approveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
                    onClick={() => handleApprove(selectedCommission.id)}
                    disabled={approveMutation.isPending}
                  >
                    {approveMutation.isPending ? 'Aprovando...' : 'Aprovar Comissão'}
                  </Button>
                )}
                {selectedCommission.status === 'approved' && (
                  <Button
                    variant="primary"
                    leftIcon={payMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <DollarSign className="h-4 w-4" />}
                    onClick={() => handlePay(selectedCommission.id)}
                    disabled={payMutation.isPending}
                  >
                    {payMutation.isPending ? 'Processando...' : 'Marcar como Paga'}
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}

export default CommissionsPage;
