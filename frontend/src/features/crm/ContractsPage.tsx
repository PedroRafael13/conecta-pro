'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  FileText,
  Calendar,
  DollarSign,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Download,
  Eye,
  Edit,
  TrendingUp,
  Building2,
  Users,
  FileSignature,
  History,
  BarChart3,
  Trash2,
  Copy,
  Send,
  Printer,
  MessageSquare,
  Phone,
  Mail,
  MapPin,
  Shield,
  Briefcase,
  Target,
  Percent,
  AlertCircle,
  Info,
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
  Avatar,
  StatCard,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
  Skeleton,
} from '@/design-system/components';
import {
  PieChart as RechartsPie,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  AreaChart,
  Area,
} from 'recharts';

// Importações do módulo CRM
import {
  useContracts,
  useContractStats,
  useCreateContract,
  useUpdateContract,
  useRenewContract,
  useTerminateContract,
} from './hooks';
import type {
  Contract,
  ContractCreate,
  ContractFilter,
  ContractStatus,
  ContractCategory,
} from './types';
import {
  ContractStatus as ContractStatusEnum,
  ContractCategory as ContractCategoryEnum,
  AdjustmentIndex,
} from './types';

// ==================== CONSTANTS ====================

const STATUS_CONFIG: Record<string, { label: string; color: 'neutral' | 'warning' | 'success' | 'danger' | 'info'; icon: React.ElementType }> = {
  draft: { label: 'Rascunho', color: 'neutral', icon: FileText },
  pending_signature: { label: 'Aguard. Assinatura', color: 'warning', icon: Clock },
  active: { label: 'Ativo', color: 'success', icon: CheckCircle2 },
  suspended: { label: 'Suspenso', color: 'danger', icon: AlertTriangle },
  terminated: { label: 'Encerrado', color: 'neutral', icon: XCircle },
  expired: { label: 'Expirado', color: 'warning', icon: RefreshCw },
  cancelled: { label: 'Cancelado', color: 'danger', icon: XCircle },
};

const CATEGORY_CONFIG: Record<string, { label: string; color: 'primary' | 'info' | 'warning' | 'success' | 'secondary' }> = {
  security: { label: 'Segurança', color: 'primary' },
  cleaning: { label: 'Limpeza', color: 'info' },
  maintenance: { label: 'Manutenção', color: 'warning' },
  facilities: { label: 'Facilities', color: 'success' },
  mixed: { label: 'Misto', color: 'secondary' },
  consulting: { label: 'Consultoria', color: 'info' },
  outsourcing: { label: 'Terceirização', color: 'primary' },
};

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

// ==================== COMPONENT ====================

export function ContractsPage() {
  // State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [mainTab, setMainTab] = useState('contracts');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [showRenewalModal, setShowRenewalModal] = useState(false);
  const [detailTab, setDetailTab] = useState('overview');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Form state
  const [newContractForm, setNewContractForm] = useState<Partial<ContractCreate>>({
    category: ContractCategoryEnum.FACILITIES,
    auto_renewal: true,
    adjustment_index: AdjustmentIndex.IGPM,
  });

  // Renewal form state
  const [renewalForm, setRenewalForm] = useState({
    new_end_date: '',
    adjustment_percentage: 0,
    notes: '',
  });

  // Construir filtros
  const filters: ContractFilter & { page: number; page_size: number } = useMemo(() => ({
    page,
    page_size: pageSize,
    status: selectedTab !== 'all' ? selectedTab as ContractStatus : undefined,
    category: categoryFilter ? categoryFilter as ContractCategory : undefined,
    search: searchTerm || undefined,
  }), [page, selectedTab, categoryFilter, searchTerm]);

  // Hooks de dados
  const { data: contractsData, isLoading, isError, error, refetch } = useContracts(filters);
  const { data: stats, isLoading: isLoadingStats } = useContractStats();
  const createMutation = useCreateContract();
  const updateMutation = useUpdateContract();
  const renewMutation = useRenewContract();
  const terminateMutation = useTerminateContract();

  // Dados processados
  const contracts = contractsData?.items || [];
  const totalContracts = contractsData?.total || 0;

  // Handlers
  const handleCreate = useCallback(async () => {
    if (!newContractForm.client_name || !newContractForm.monthly_value) return;

    try {
      await createMutation.mutateAsync(newContractForm as ContractCreate);
      setShowNewModal(false);
      setNewContractForm({
        category: ContractCategoryEnum.FACILITIES,
        auto_renewal: true,
        adjustment_index: AdjustmentIndex.IGPM,
      });
    } catch (err) {
      console.error('Erro ao criar contrato:', err);
    }
  }, [newContractForm, createMutation]);

  const handleRenew = useCallback(async () => {
    if (!selectedContract || !renewalForm.new_end_date) return;

    try {
      await renewMutation.mutateAsync({
        id: selectedContract.id,
        data: renewalForm,
      });
      setShowRenewalModal(false);
      setSelectedContract(null);
      setRenewalForm({ new_end_date: '', adjustment_percentage: 0, notes: '' });
    } catch (err) {
      console.error('Erro ao renovar contrato:', err);
    }
  }, [selectedContract, renewalForm, renewMutation]);

  const openContractDetail = (contract: Contract) => {
    setSelectedContract(contract);
    setDetailTab('overview');
    setShowDetailModal(true);
  };

  // Colunas da tabela
  const columns: Column<Contract>[] = [
    {
      key: 'contract_number',
      header: 'Contrato',
      render: (row) => (
        <div>
          <p className="font-mono text-sm font-medium text-accent-primary">{row.contract_number}</p>
          <p className="text-xs text-text-muted">{row.title}</p>
        </div>
      ),
    },
    {
      key: 'client',
      header: 'Cliente',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.client_name} size="sm" />
          <div>
            <span className="font-medium">{row.client_name}</span>
            <p className="text-xs text-text-muted">{row.client_document}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => {
        const config = CATEGORY_CONFIG[row.category] || CATEGORY_CONFIG.facilities;
        return <Badge variant={config.color} size="sm">{config.label}</Badge>;
      },
    },
    {
      key: 'value',
      header: 'Valor Mensal',
      sortable: true,
      render: (row) => (
        <span className="font-mono text-text-primary">
          {formatCurrency(row.monthly_value)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = STATUS_CONFIG[row.status] || STATUS_CONFIG.draft;
        const Icon = config.icon;
        return (
          <Badge variant={config.color} leftIcon={<Icon className="w-3 h-3" />}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      key: 'period',
      header: 'Vigência',
      render: (row) => (
        <div className="text-sm">
          <p className="text-text-primary">{formatDate(row.start_date)}</p>
          <p className="text-text-muted">
            até {row.end_date ? formatDate(row.end_date) : 'Indeterminado'}
          </p>
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              openContractDetail(row);
            }}
          >
            <Eye className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="w-4 h-4" />
          </Button>
        </div>
      ),
    },
  ];

  // Estatísticas calculadas
  const displayStats = useMemo(() => {
    return {
      activeCount: stats?.active_count || 0,
      totalMonthlyValue: stats?.total_monthly_value || 0,
      avgSla: stats?.avg_sla || 0,
      expiringCount: stats?.expiring_soon || 0,
      pendingCount: stats?.pending_signature || 0,
      employeeTotal: stats?.total_employees || 0,
    };
  }, [stats]);

  // Loading state
  if (isLoading && !contractsData) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-24" />)}
          </div>
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
          <h2 className="text-xl font-semibold">Erro ao carregar contratos</h2>
          <p className="text-text-secondary">{(error as Error)?.message}</p>
          <Button onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Tentar novamente
          </Button>
        </div>
      </MainLayout>
    );
  }

  // Dados para gráficos (baseados em estatísticas da API)
  const contractsByCategory = stats?.by_category
    ? Object.entries(stats.by_category).map(([category, count], index) => ({
        name: CATEGORY_CONFIG[category]?.label || category,
        value: count,
        color: ['#6366f1', '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'][index % 5],
      }))
    : [];

  const contractsByStatus = stats?.by_status
    ? Object.entries(stats.by_status).map(([status, count]) => ({
        name: STATUS_CONFIG[status]?.label || status,
        value: count,
      }))
    : [];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Contratos
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão completa de contratos com renovação automática e SLA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setShowNewModal(true)}
            >
              Novo Contrato
            </Button>
          </div>
        </div>

        {/* Main Tabs */}
        <SimpleTabBar
          tabs={[
            { value: 'contracts', label: 'Contratos', icon: <FileText className="w-4 h-4" /> },
            { value: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
            { value: 'renewals', label: 'Renovações', icon: <RefreshCw className="w-4 h-4" /> },
          ]}
          value={mainTab}
          onChange={setMainTab}
        />

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Contratos Ativos"
              value={isLoadingStats ? '...' : displayStats.activeCount.toString()}
              change={8}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Receita Mensal"
              value={isLoadingStats ? '...' : formatCurrency(displayStats.totalMonthlyValue)}
              change={12.5}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="SLA Médio"
              value={isLoadingStats ? '...' : `${displayStats.avgSla}%`}
              change={2.1}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Colaboradores"
              value={isLoadingStats ? '...' : displayStats.employeeTotal.toString()}
              icon={<Users className="w-6 h-6" />}
              iconColor="secondary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Renovação em 90 dias"
              value={isLoadingStats ? '...' : displayStats.expiringCount.toString()}
              icon={<RefreshCw className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <StatCard
              title="Aguard. Assinatura"
              value={isLoadingStats ? '...' : displayStats.pendingCount.toString()}
              icon={<FileSignature className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </div>

        {/* Contracts Tab */}
        {mainTab === 'contracts' && (
          <>
            {/* Filters */}
            <Card>
              <CardBody className="py-4">
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <SimpleTabBar
                    tabs={[
                      { value: 'all', label: `Todos (${totalContracts})` },
                      { value: 'active', label: 'Ativos' },
                      { value: 'pending_signature', label: 'Pendentes' },
                      { value: 'suspended', label: 'Suspensos' },
                      { value: 'expired', label: 'Expirados' },
                    ]}
                    value={selectedTab}
                    onChange={setSelectedTab}
                    variant="pills"
                  />
                  <div className="flex items-center gap-3">
                    <Input
                      placeholder="Buscar contratos..."
                      leftIcon={<Search className="w-4 h-4" />}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-64"
                    />
                    <Select
                      options={[
                        { value: '', label: 'Todas categorias' },
                        ...Object.entries(CATEGORY_CONFIG).map(([key, config]) => ({
                          value: key,
                          label: config.label,
                        }))
                      ]}
                      value={categoryFilter}
                      onChange={setCategoryFilter}
                      className="w-40"
                    />
                    <Button variant="ghost" size="sm" onClick={() => refetch()} disabled={isLoading}>
                      <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Contracts Table */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              <Card>
                <CardHeader title={`${totalContracts} contratos encontrados`} />
                <CardBody className="p-0">
                  <DataTable
                    columns={columns}
                    data={contracts}
                    keyExtractor={(row) => row.id}
                    onRowClick={openContractDetail}
                  />
                </CardBody>
              </Card>
            </motion.div>

            {/* Alerts */}
            {displayStats.expiringCount > 0 && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <Card className="border-warning/30 bg-warning/5">
                  <CardBody>
                    <div className="flex items-center gap-4">
                      <div className="p-3 rounded-xl bg-warning/10">
                        <AlertTriangle className="w-6 h-6 text-warning" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-text-primary">
                          {displayStats.expiringCount} contrato(s) vencem nos próximos 90 dias
                        </p>
                        <p className="text-sm text-text-secondary mt-1">
                          Revise os contratos e inicie o processo de renovação
                        </p>
                      </div>
                      <Button variant="outline" size="sm" onClick={() => setMainTab('renewals')}>
                        Ver Renovações
                      </Button>
                    </div>
                  </CardBody>
                </Card>
              </motion.div>
            )}
          </>
        )}

        {/* Analytics Tab */}
        {mainTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Contratos por Categoria" />
              <CardBody>
                <div className="flex items-center gap-6">
                  <div className="w-48 h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPie>
                        <Pie
                          data={contractsByCategory}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          dataKey="value"
                        >
                          {contractsByCategory.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }} />
                      </RechartsPie>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex-1 space-y-3">
                    {contractsByCategory.map((cat) => (
                      <div key={cat.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                          <span className="text-sm text-text-secondary">{cat.name}</span>
                        </div>
                        <span className="text-sm font-medium text-text-primary">{cat.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Contratos por Status" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={contractsByStatus}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }} />
                      <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Renewals Tab */}
        {mainTab === 'renewals' && (
          <div className="space-y-6">
            <Card>
              <CardHeader title="Próximas Renovações" subtitle="Contratos que vencem em até 90 dias" />
              <CardBody>
                {contracts.filter(c => c.status === 'active' && c.days_until_expiry && c.days_until_expiry <= 90).length > 0 ? (
                  <div className="space-y-4">
                    {contracts
                      .filter(c => c.status === 'active' && c.days_until_expiry && c.days_until_expiry <= 90)
                      .sort((a, b) => (a.days_until_expiry || 0) - (b.days_until_expiry || 0))
                      .map((contract) => {
                        const daysLeft = contract.days_until_expiry || 0;
                        const urgency = daysLeft <= 30 ? 'danger' : daysLeft <= 60 ? 'warning' : 'info';

                        return (
                          <div
                            key={contract.id}
                            className="flex items-center gap-4 p-4 rounded-lg bg-bg-tertiary hover:bg-bg-hover transition-colors cursor-pointer"
                            onClick={() => openContractDetail(contract)}
                          >
                            <Avatar name={contract.client_name} size="md" />
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <p className="font-medium text-text-primary">{contract.client_name}</p>
                                <Badge variant={urgency} size="sm">{daysLeft} dias</Badge>
                              </div>
                              <p className="text-sm text-text-secondary">{contract.contract_number} • {contract.title}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-mono font-medium text-text-primary">
                                {formatCurrency(contract.monthly_value)}
                              </p>
                              <p className="text-xs text-text-muted">
                                Vence em {formatDate(contract.end_date)}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              {contract.auto_renewal ? (
                                <Badge variant="success" size="sm">
                                  <RefreshCw className="w-3 h-3 mr-1" />
                                  Auto
                                </Badge>
                              ) : (
                                <Button
                                  variant="primary"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedContract(contract);
                                    setShowRenewalModal(true);
                                  }}
                                >
                                  Renovar
                                </Button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                  </div>
                ) : (
                  <div className="text-center py-12 text-text-muted">
                    <RefreshCw className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhum contrato próximo ao vencimento</p>
                  </div>
                )}
              </CardBody>
            </Card>
          </div>
        )}

        {/* Contract Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedContract?.contract_number || 'Detalhes do Contrato'}
          size="xl"
        >
          {selectedContract && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedContract.client_name} size="lg" />
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedContract.client_name}</h3>
                    <p className="text-sm text-text-secondary">{selectedContract.client_document}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={STATUS_CONFIG[selectedContract.status]?.color || 'neutral'}>
                        {STATUS_CONFIG[selectedContract.status]?.label || selectedContract.status}
                      </Badge>
                      <Badge variant={CATEGORY_CONFIG[selectedContract.category]?.color || 'secondary'}>
                        {CATEGORY_CONFIG[selectedContract.category]?.label || selectedContract.category}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-accent-primary">
                    {formatCurrency(selectedContract.monthly_value)}
                  </p>
                  <p className="text-sm text-text-muted">/mês</p>
                </div>
              </div>

              {/* Detail Tabs */}
              <SimpleTabBar
                tabs={[
                  { value: 'overview', label: 'Visão Geral', icon: <FileText className="w-4 h-4" /> },
                  { value: 'history', label: 'Histórico', icon: <History className="w-4 h-4" /> },
                ]}
                value={detailTab}
                onChange={setDetailTab}
                variant="pills"
              />

              {/* Overview Tab */}
              {detailTab === 'overview' && (
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Calendar className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Vigência</span>
                      </div>
                      <p className="text-text-primary">
                        {formatDate(selectedContract.start_date)} até{' '}
                        {selectedContract.end_date ? formatDate(selectedContract.end_date) : 'Indeterminado'}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <RefreshCw className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Renovação</span>
                      </div>
                      <p className="text-text-primary">
                        {selectedContract.auto_renewal ? 'Automática' : 'Manual'}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Percent className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Reajuste</span>
                      </div>
                      <p className="text-text-primary">
                        Índice: {selectedContract.adjustment_index || 'Não definido'}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <DollarSign className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Valor Total</span>
                      </div>
                      <p className="text-text-primary">
                        {formatCurrency(selectedContract.total_value)}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {selectedContract.description && (
                      <div className="p-4 rounded-lg bg-bg-tertiary">
                        <div className="flex items-center gap-2 mb-3">
                          <Info className="w-4 h-4 text-text-muted" />
                          <span className="text-sm font-medium text-text-secondary">Descrição</span>
                        </div>
                        <p className="text-text-primary">{selectedContract.description}</p>
                      </div>
                    )}

                    {selectedContract.notes && (
                      <div className="p-4 rounded-lg bg-warning/5 border border-warning/20">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertCircle className="w-4 h-4 text-warning" />
                          <span className="text-sm font-medium text-warning">Observações</span>
                        </div>
                        <p className="text-text-primary">{selectedContract.notes}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* History Tab */}
              {detailTab === 'history' && (
                <div className="text-center py-12 text-text-muted">
                  <History className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Histórico será carregado da API</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-border-default">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" leftIcon={<Download className="w-4 h-4" />}>PDF</Button>
                  <Button variant="ghost" leftIcon={<Printer className="w-4 h-4" />}>Imprimir</Button>
                  <Button variant="ghost" leftIcon={<Copy className="w-4 h-4" />}>Duplicar</Button>
                </div>
                <div className="flex items-center gap-2">
                  {selectedContract.status === 'active' && (
                    <Button
                      variant="primary"
                      leftIcon={<RefreshCw className="w-4 h-4" />}
                      onClick={() => {
                        setShowDetailModal(false);
                        setShowRenewalModal(true);
                      }}
                    >
                      Renovar
                    </Button>
                  )}
                  {selectedContract.status === 'pending_signature' && (
                    <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                      Enviar para Assinatura
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}
        </Modal>

        {/* New Contract Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Novo Contrato"
          size="lg"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Nome do Cliente *"
                placeholder="Nome do cliente"
                value={newContractForm.client_name || ''}
                onChange={(e) => setNewContractForm(prev => ({ ...prev, client_name: e.target.value }))}
              />
              <Input
                label="CNPJ/CPF"
                placeholder="00.000.000/0000-00"
                value={newContractForm.client_document || ''}
                onChange={(e) => setNewContractForm(prev => ({ ...prev, client_document: e.target.value }))}
              />
            </div>

            <Input
              label="Título do Contrato"
              placeholder="Ex: Segurança 24h"
              value={newContractForm.title || ''}
              onChange={(e) => setNewContractForm(prev => ({ ...prev, title: e.target.value }))}
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Data de Início"
                type="date"
                value={newContractForm.start_date || ''}
                onChange={(e) => setNewContractForm(prev => ({ ...prev, start_date: e.target.value }))}
              />
              <Input
                label="Data de Término"
                type="date"
                value={newContractForm.end_date || ''}
                onChange={(e) => setNewContractForm(prev => ({ ...prev, end_date: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Valor Mensal *"
                type="number"
                placeholder="0,00"
                leftIcon={<DollarSign className="w-4 h-4" />}
                value={newContractForm.monthly_value?.toString() || ''}
                onChange={(e) => setNewContractForm(prev => ({ ...prev, monthly_value: parseFloat(e.target.value) || 0 }))}
              />
              <Select
                label="Categoria"
                options={Object.entries(CATEGORY_CONFIG).map(([key, config]) => ({
                  value: key,
                  label: config.label
                }))}
                value={newContractForm.category || 'facilities'}
                onChange={(value) => setNewContractForm(prev => ({ ...prev, category: value as ContractCategory }))}
              />
            </div>

            <div className="p-4 rounded-lg bg-bg-tertiary">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={newContractForm.auto_renewal || false}
                  onChange={(e) => setNewContractForm(prev => ({ ...prev, auto_renewal: e.target.checked }))}
                  className="w-5 h-5 rounded border-border-default bg-bg-primary text-accent-primary focus:ring-accent-primary"
                />
                <div>
                  <span className="text-text-primary font-medium">Renovação Automática</span>
                  <p className="text-sm text-text-muted">O contrato será renovado automaticamente ao final da vigência</p>
                </div>
              </label>
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button
                variant="primary"
                leftIcon={createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                onClick={handleCreate}
                disabled={!newContractForm.client_name || !newContractForm.monthly_value || createMutation.isPending}
              >
                {createMutation.isPending ? 'Criando...' : 'Criar Contrato'}
              </Button>
            </div>
          </div>
        </Modal>

        {/* Renewal Modal */}
        <Modal
          isOpen={showRenewalModal}
          onClose={() => setShowRenewalModal(false)}
          title="Renovar Contrato"
          size="md"
        >
          {selectedContract && (
            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-bg-tertiary">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedContract.client_name} size="lg" />
                  <div>
                    <h4 className="font-medium text-text-primary">{selectedContract.client_name}</h4>
                    <p className="text-sm text-text-muted">{selectedContract.contract_number}</p>
                  </div>
                </div>
              </div>

              <Input
                label="Nova Data de Término *"
                type="date"
                value={renewalForm.new_end_date}
                onChange={(e) => setRenewalForm(prev => ({ ...prev, new_end_date: e.target.value }))}
              />

              <Input
                label="Reajuste (%)"
                type="number"
                placeholder="0"
                leftIcon={<Percent className="w-4 h-4" />}
                value={renewalForm.adjustment_percentage.toString()}
                onChange={(e) => setRenewalForm(prev => ({ ...prev, adjustment_percentage: parseFloat(e.target.value) || 0 }))}
              />

              {renewalForm.adjustment_percentage > 0 && (
                <div className="p-4 rounded-lg bg-success/5 border border-success/20">
                  <div className="flex items-center justify-between">
                    <span className="text-text-secondary">Novo Valor Mensal</span>
                    <span className="text-xl font-bold text-success">
                      {formatCurrency(selectedContract.monthly_value * (1 + renewalForm.adjustment_percentage / 100))}
                    </span>
                  </div>
                </div>
              )}

              <Input
                label="Observações"
                placeholder="Notas sobre a renovação..."
                value={renewalForm.notes}
                onChange={(e) => setRenewalForm(prev => ({ ...prev, notes: e.target.value }))}
              />

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowRenewalModal(false)}>
                  Cancelar
                </Button>
                <Button
                  variant="primary"
                  leftIcon={renewMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                  onClick={handleRenew}
                  disabled={!renewalForm.new_end_date || renewMutation.isPending}
                >
                  {renewMutation.isPending ? 'Renovando...' : 'Confirmar Renovação'}
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
