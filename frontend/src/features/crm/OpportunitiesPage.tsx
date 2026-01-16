'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  DollarSign,
  Calendar,
  Building2,
  ArrowRight,
  Phone,
  Mail,
  GripVertical,
  TrendingUp,
  TrendingDown,
  Target,
  BarChart3,
  Clock,
  CheckCircle2,
  XCircle,
  Eye,
  Edit,
  Trash2,
  MessageSquare,
  FileText,
  ChevronRight,
  AlertTriangle,
  Zap,
  Award,
  Users,
  Download,
  RefreshCw,
  Percent,
  Activity,
  ThumbsUp,
  ThumbsDown,
  X,
  List,
  Loader2,
  LayoutGrid,
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
  Modal,
  Select,
  StatCard,
  SimpleTabBar,
  DataTable,
  Skeleton,
} from '@/design-system/components';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Importações do módulo CRM
import {
  useOpportunities,
  useCreateOpportunity,
  useUpdateOpportunity,
  useUpdateOpportunityStage,
  useCloseOpportunity,
  useDeleteOpportunity,
} from './hooks';
import type {
  Opportunity,
  OpportunityCreate,
  OpportunityFilter,
  OpportunityStage,
  OpportunityPriority,
  LossReason,
} from './types';
import {
  OpportunityStage as OpportunityStageEnum,
  OpportunityPriority as OpportunityPriorityEnum,
  LossReason as LossReasonEnum,
} from './types';

// ==================== CONSTANTS ====================

const STAGE_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  qualification: { label: 'Qualificação', color: '#6366f1', icon: Target },
  needs_analysis: { label: 'Análise de Necessidades', color: '#8b5cf6', icon: Activity },
  proposal: { label: 'Proposta', color: '#f59e0b', icon: FileText },
  negotiation: { label: 'Negociação', color: '#ef4444', icon: TrendingUp },
  closed_won: { label: 'Ganho', color: '#10b981', icon: CheckCircle2 },
  closed_lost: { label: 'Perdido', color: '#64748b', icon: XCircle },
};

const PRIORITY_CONFIG: Record<string, { label: string; variant: 'info' | 'warning' | 'danger' | 'secondary' }> = {
  low: { label: 'Baixa', variant: 'secondary' },
  medium: { label: 'Média', variant: 'info' },
  high: { label: 'Alta', variant: 'warning' },
  critical: { label: 'Crítica', variant: 'danger' },
};

const LOSS_REASON_LABELS: Record<string, string> = {
  price: 'Preço',
  competitor: 'Concorrente',
  no_budget: 'Sem Orçamento',
  no_decision: 'Sem Decisão',
  timing: 'Timing',
  product_fit: 'Produto Inadequado',
  no_response: 'Sem Resposta',
  other: 'Outro',
};

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

const getValueColor = (value: number) => {
  if (value >= 100000) return 'text-accent-success';
  if (value >= 50000) return 'text-accent-warning';
  return 'text-text-primary';
};

// ==================== COMPONENT ====================

export function OpportunitiesPage() {
  // State
  const [activeTab, setActiveTab] = useState('kanban');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStage, setSelectedStage] = useState('all');
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [showNewModal, setShowNewModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null);
  const [page, setPage] = useState(1);
  const pageSize = 50;

  // Form state
  const [newOppForm, setNewOppForm] = useState<Partial<OpportunityCreate>>({
    stage: OpportunityStageEnum.QUALIFICATION,
    priority: OpportunityPriorityEnum.MEDIUM,
    probability: 20,
  });

  // Close modal state
  const [closeData, setCloseData] = useState<{
    won: boolean;
    loss_reason?: LossReason;
    notes?: string;
  }>({ won: false });

  // Construir filtros
  const filters: OpportunityFilter & { page: number; page_size: number } = useMemo(() => ({
    page,
    page_size: pageSize,
    stage: selectedStage !== 'all' ? selectedStage as OpportunityStage : undefined,
    priority: selectedPriority !== 'all' ? selectedPriority as OpportunityPriority : undefined,
    search: searchTerm || undefined,
    is_open: true, // Por padrão, mostrar apenas abertas
  }), [page, selectedStage, selectedPriority, searchTerm]);

  // Hooks de dados
  const { data: oppData, isLoading, isError, error, refetch } = useOpportunities(filters);
  const createMutation = useCreateOpportunity();
  const updateMutation = useUpdateOpportunity();
  const updateStageMutation = useUpdateOpportunityStage();
  const closeMutation = useCloseOpportunity();
  const deleteMutation = useDeleteOpportunity();

  // Dados processados
  const opportunities = oppData?.items || [];
  const totalOpps = oppData?.total || 0;

  // Agrupar por estágio para Kanban
  const oppsByStage = useMemo(() => {
    const grouped: Record<string, Opportunity[]> = {};
    Object.keys(STAGE_CONFIG).forEach(stage => {
      grouped[stage] = [];
    });
    opportunities.forEach(opp => {
      if (grouped[opp.stage]) {
        grouped[opp.stage].push(opp);
      }
    });
    return grouped;
  }, [opportunities]);

  // Calcular estatísticas
  const stats = useMemo(() => {
    const open = opportunities.filter(o => o.is_open);
    const won = opportunities.filter(o => o.is_won);
    return {
      totalValue: open.reduce((sum, o) => sum + o.value, 0),
      weightedValue: open.reduce((sum, o) => sum + o.weighted_value, 0),
      avgProbability: open.length > 0
        ? Math.round(open.reduce((sum, o) => sum + o.probability, 0) / open.length)
        : 0,
      overdue: opportunities.filter(o => o.is_overdue).length,
      wonCount: won.length,
      wonValue: won.reduce((sum, o) => sum + o.value, 0),
    };
  }, [opportunities]);

  // Dados para gráficos
  const stageDistribution = useMemo(() => {
    return Object.entries(oppsByStage).map(([stage, opps]) => ({
      name: STAGE_CONFIG[stage]?.label || stage,
      value: opps.reduce((sum, o) => sum + o.value, 0),
      count: opps.length,
      color: STAGE_CONFIG[stage]?.color || '#64748b',
    }));
  }, [oppsByStage]);

  // Handlers
  const handleCreate = useCallback(async () => {
    if (!newOppForm.title || !newOppForm.contact_name || !newOppForm.contact_email) return;

    try {
      await createMutation.mutateAsync(newOppForm as OpportunityCreate);
      setShowNewModal(false);
      setNewOppForm({
        stage: OpportunityStageEnum.QUALIFICATION,
        priority: OpportunityPriorityEnum.MEDIUM,
        probability: 20,
      });
    } catch (err) {
      console.error('Erro ao criar oportunidade:', err);
    }
  }, [newOppForm, createMutation]);

  const handleStageChange = useCallback(async (id: string, newStage: OpportunityStage) => {
    try {
      await updateStageMutation.mutateAsync({ id, data: { stage: newStage } });
    } catch (err) {
      console.error('Erro ao atualizar estágio:', err);
    }
  }, [updateStageMutation]);

  const handleClose = useCallback(async () => {
    if (!selectedOpp) return;

    try {
      await closeMutation.mutateAsync({
        id: selectedOpp.id,
        data: closeData,
      });
      setShowCloseModal(false);
      setSelectedOpp(null);
      setCloseData({ won: false });
    } catch (err) {
      console.error('Erro ao fechar oportunidade:', err);
    }
  }, [selectedOpp, closeData, closeMutation]);

  const handleDelete = useCallback(async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir esta oportunidade?')) return;

    try {
      await deleteMutation.mutateAsync(id);
    } catch (err) {
      console.error('Erro ao excluir oportunidade:', err);
    }
  }, [deleteMutation]);

  // Tabs
  const tabs = [
    { value: 'kanban', label: 'Kanban', icon: <LayoutGrid className="h-4 w-4" /> },
    { value: 'list', label: 'Lista', icon: <List className="h-4 w-4" /> },
    { value: 'analytics', label: 'Analytics', icon: <BarChart3 className="h-4 w-4" /> },
  ];

  // Colunas da tabela
  const columns = [
    {
      key: 'title',
      header: 'Oportunidade',
      render: (row: Opportunity) => (
        <div>
          <p className="font-medium text-text-primary">{row.title}</p>
          <p className="text-xs text-text-muted">{row.company_name || row.contact_name}</p>
        </div>
      ),
    },
    {
      key: 'value',
      header: 'Valor',
      sortable: true,
      render: (row: Opportunity) => (
        <span className={`font-mono font-medium ${getValueColor(row.value)}`}>
          {formatCurrency(row.value)}
        </span>
      ),
    },
    {
      key: 'probability',
      header: 'Probabilidade',
      render: (row: Opportunity) => (
        <div className="flex items-center gap-2">
          <div className="w-16 h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-accent-primary"
              style={{ width: `${row.probability}%` }}
            />
          </div>
          <span className="text-sm">{row.probability}%</span>
        </div>
      ),
    },
    {
      key: 'stage',
      header: 'Estágio',
      render: (row: Opportunity) => {
        const stage = STAGE_CONFIG[row.stage];
        return (
          <Badge style={{ backgroundColor: stage?.color + '20', color: stage?.color }}>
            {stage?.label || row.stage}
          </Badge>
        );
      },
    },
    {
      key: 'priority',
      header: 'Prioridade',
      render: (row: Opportunity) => {
        const priority = PRIORITY_CONFIG[row.priority];
        return <Badge variant={priority?.variant}>{priority?.label || row.priority}</Badge>;
      },
    },
    {
      key: 'expected_close_date',
      header: 'Previsão',
      render: (row: Opportunity) => (
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-text-muted" />
          <span className={row.is_overdue ? 'text-accent-danger' : 'text-text-secondary'}>
            {formatDate(row.expected_close_date)}
          </span>
          {row.is_overdue && <AlertTriangle className="h-4 w-4 text-accent-danger" />}
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row: Opportunity) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedOpp(row);
              setShowDetailModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.is_open && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSelectedOpp(row);
                setShowCloseModal(true);
              }}
            >
              <CheckCircle2 className="h-4 w-4 text-accent-success" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleDelete(row.id)}
          >
            <Trash2 className="h-4 w-4 text-accent-danger" />
          </Button>
        </div>
      ),
    },
  ];

  // Loading state
  if (isLoading && !oppData) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-24" />)}
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
          <h2 className="text-xl font-semibold">Erro ao carregar oportunidades</h2>
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
              Pipeline de Vendas
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie suas oportunidades de negócio
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Oportunidade
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total no Pipeline"
              value={formatCurrency(stats.totalValue)}
              change={12}
              changeLabel="vs. mês anterior"
              icon={<DollarSign className="h-5 w-5" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Valor Ponderado"
              value={formatCurrency(stats.weightedValue)}
              change={8}
              changeLabel="expectativa"
              icon={<Percent className="h-5 w-5" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Prob. Média"
              value={`${stats.avgProbability}%`}
              change={5}
              changeLabel="qualidade"
              icon={<Target className="h-5 w-5" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Ganhos"
              value={stats.wonCount.toString()}
              change={25}
              changeLabel={formatCurrency(stats.wonValue)}
              icon={<Award className="h-5 w-5" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Atrasados"
              value={stats.overdue.toString()}
              change={-10}
              changeLabel="atenção"
              icon={<AlertTriangle className="h-5 w-5" />}
              iconColor="danger"
            />
          </motion.div>
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Filters */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar oportunidades..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'Todos os Estágios' },
                  ...Object.entries(STAGE_CONFIG).map(([key, config]) => ({
                    value: key,
                    label: config.label
                  }))
                ]}
                value={selectedStage}
                onChange={setSelectedStage}
              />
              <Select
                options={[
                  { value: 'all', label: 'Todas Prioridades' },
                  ...Object.entries(PRIORITY_CONFIG).map(([key, config]) => ({
                    value: key,
                    label: config.label
                  }))
                ]}
                value={selectedPriority}
                onChange={setSelectedPriority}
              />
              <Button variant="ghost" size="sm" onClick={() => refetch()} disabled={isLoading}>
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </CardBody>
        </Card>

        {/* Kanban View */}
        {activeTab === 'kanban' && (
          <div className="flex gap-4 overflow-x-auto pb-4">
            {Object.entries(STAGE_CONFIG).filter(([key]) => key !== 'closed_won' && key !== 'closed_lost').map(([stage, config]) => {
              const stageOpps = oppsByStage[stage] || [];
              const stageValue = stageOpps.reduce((sum, o) => sum + o.value, 0);

              return (
                <div key={stage} className="flex-shrink-0 w-80">
                  <div className="bg-bg-secondary rounded-lg p-4">
                    {/* Column Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: config.color }} />
                        <span className="font-medium text-text-primary">{config.label}</span>
                        <Badge variant="secondary">{stageOpps.length}</Badge>
                      </div>
                      <span className="text-sm text-text-muted">{formatCurrency(stageValue)}</span>
                    </div>

                    {/* Cards */}
                    <div className="space-y-3 max-h-[600px] overflow-y-auto">
                      {stageOpps.map((opp) => (
                        <motion.div
                          key={opp.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="bg-bg-primary rounded-lg p-4 border border-border-subtle hover:border-accent-primary/50 cursor-pointer transition-colors"
                          onClick={() => {
                            setSelectedOpp(opp);
                            setShowDetailModal(true);
                          }}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium text-text-primary line-clamp-2">{opp.title}</h4>
                            <Badge variant={PRIORITY_CONFIG[opp.priority]?.variant}>
                              {PRIORITY_CONFIG[opp.priority]?.label}
                            </Badge>
                          </div>

                          <p className="text-sm text-text-secondary mb-3">
                            {opp.company_name || opp.contact_name}
                          </p>

                          <div className="flex items-center justify-between text-sm">
                            <span className="font-mono font-semibold text-accent-success">
                              {formatCurrency(opp.value)}
                            </span>
                            <span className="text-text-muted">{opp.probability}%</span>
                          </div>

                          {opp.expected_close_date && (
                            <div className={`flex items-center gap-1 mt-2 text-xs ${opp.is_overdue ? 'text-accent-danger' : 'text-text-muted'}`}>
                              <Calendar className="h-3 w-3" />
                              {formatDate(opp.expected_close_date)}
                              {opp.is_overdue && <AlertTriangle className="h-3 w-3" />}
                            </div>
                          )}
                        </motion.div>
                      ))}

                      {stageOpps.length === 0 && (
                        <div className="text-center py-8 text-text-muted">
                          <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">Nenhuma oportunidade</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* List View */}
        {activeTab === 'list' && (
          <Card>
            <CardHeader title={`${totalOpps} oportunidades`} />
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={opportunities}
                keyExtractor={(row) => row.id}
              />
            </CardBody>
          </Card>
        )}

        {/* Analytics View */}
        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Valor por Estágio" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={stageDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                        formatter={(value: number) => [formatCurrency(value), 'Valor']}
                      />
                      <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Distribuição por Estágio" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={stageDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={3}
                        dataKey="count"
                      >
                        {stageDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-2 mt-4">
                  {stageDistribution.map((item) => (
                    <div key={item.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm text-text-secondary">{item.name}</span>
                      </div>
                      <span className="text-sm font-medium">{item.count} ({formatCurrency(item.value)})</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* New Opportunity Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Nova Oportunidade"
          size="lg"
        >
          <div className="space-y-6">
            <Input
              label="Título *"
              placeholder="Nome da oportunidade"
              value={newOppForm.title || ''}
              onChange={(e) => setNewOppForm(prev => ({ ...prev, title: e.target.value }))}
            />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Nome do Contato *"
                placeholder="Nome completo"
                value={newOppForm.contact_name || ''}
                onChange={(e) => setNewOppForm(prev => ({ ...prev, contact_name: e.target.value }))}
              />
              <Input
                label="Email *"
                type="email"
                placeholder="email@empresa.com"
                value={newOppForm.contact_email || ''}
                onChange={(e) => setNewOppForm(prev => ({ ...prev, contact_email: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Empresa"
                placeholder="Nome da empresa"
                value={newOppForm.company_name || ''}
                onChange={(e) => setNewOppForm(prev => ({ ...prev, company_name: e.target.value }))}
              />
              <Input
                label="Telefone"
                placeholder="(00) 00000-0000"
                value={newOppForm.contact_phone || ''}
                onChange={(e) => setNewOppForm(prev => ({ ...prev, contact_phone: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Input
                label="Valor"
                type="number"
                placeholder="0,00"
                value={newOppForm.value?.toString() || ''}
                onChange={(e) => setNewOppForm(prev => ({ ...prev, value: parseFloat(e.target.value) || 0 }))}
              />
              <Input
                label="Probabilidade %"
                type="number"
                placeholder="0-100"
                value={newOppForm.probability?.toString() || ''}
                onChange={(e) => setNewOppForm(prev => ({ ...prev, probability: parseInt(e.target.value) || 0 }))}
              />
              <Input
                label="Previsão de Fechamento"
                type="date"
                value={newOppForm.expected_close_date || ''}
                onChange={(e) => setNewOppForm(prev => ({ ...prev, expected_close_date: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Prioridade"
                options={Object.entries(PRIORITY_CONFIG).map(([key, config]) => ({
                  value: key,
                  label: config.label
                }))}
                value={newOppForm.priority || 'medium'}
                onChange={(value) => setNewOppForm(prev => ({ ...prev, priority: value as OpportunityPriority }))}
              />
              <Select
                label="Estágio"
                options={Object.entries(STAGE_CONFIG).slice(0, 4).map(([key, config]) => ({
                  value: key,
                  label: config.label
                }))}
                value={newOppForm.stage || 'qualification'}
                onChange={(value) => setNewOppForm(prev => ({ ...prev, stage: value as OpportunityStage }))}
              />
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button
                onClick={handleCreate}
                disabled={!newOppForm.title || !newOppForm.contact_name || !newOppForm.contact_email || createMutation.isPending}
              >
                {createMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Criando...
                  </>
                ) : (
                  'Criar Oportunidade'
                )}
              </Button>
            </div>
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedOpp?.title || 'Detalhes'}
          size="xl"
        >
          {selectedOpp && (
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <Badge style={{ backgroundColor: STAGE_CONFIG[selectedOpp.stage]?.color + '20', color: STAGE_CONFIG[selectedOpp.stage]?.color }}>
                      {STAGE_CONFIG[selectedOpp.stage]?.label}
                    </Badge>
                    <Badge variant={PRIORITY_CONFIG[selectedOpp.priority]?.variant}>
                      {PRIORITY_CONFIG[selectedOpp.priority]?.label}
                    </Badge>
                    {selectedOpp.is_overdue && (
                      <Badge variant="danger">Atrasado</Badge>
                    )}
                  </div>
                  <p className="text-text-secondary">
                    {selectedOpp.company_name || selectedOpp.contact_name}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-accent-success">{formatCurrency(selectedOpp.value)}</p>
                  <p className="text-sm text-text-muted">Ponderado: {formatCurrency(selectedOpp.weighted_value)}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-muted text-sm">Probabilidade</p>
                  <p className="text-2xl font-bold">{selectedOpp.probability}%</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-muted text-sm">Dias no Pipeline</p>
                  <p className="text-2xl font-bold">{selectedOpp.days_in_pipeline}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-muted text-sm">Previsão</p>
                  <p className="text-2xl font-bold">{formatDate(selectedOpp.expected_close_date)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Contato</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Users className="h-4 w-4 text-text-muted" />
                      {selectedOpp.contact_name}
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="h-4 w-4 text-text-muted" />
                      {selectedOpp.contact_email}
                    </div>
                    {selectedOpp.contact_phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="h-4 w-4 text-text-muted" />
                        {selectedOpp.contact_phone}
                      </div>
                    )}
                    {selectedOpp.company_name && (
                      <div className="flex items-center gap-2 text-sm">
                        <Building2 className="h-4 w-4 text-text-muted" />
                        {selectedOpp.company_name}
                      </div>
                    )}
                  </div>
                </div>

                {selectedOpp.notes && (
                  <div>
                    <h4 className="font-semibold mb-3">Observações</h4>
                    <p className="text-sm text-text-secondary p-3 rounded-lg bg-bg-tertiary">
                      {selectedOpp.notes}
                    </p>
                  </div>
                )}
              </div>

              {selectedOpp.is_open && (
                <div className="pt-4 border-t border-border-subtle">
                  <h4 className="font-semibold mb-3">Mover para Estágio</h4>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(STAGE_CONFIG).slice(0, 4).map(([key, config]) => (
                      <Button
                        key={key}
                        variant={selectedOpp.stage === key ? 'primary' : 'outline'}
                        size="sm"
                        onClick={() => handleStageChange(selectedOpp.id, key as OpportunityStage)}
                        disabled={updateStageMutation.isPending}
                      >
                        {config.label}
                      </Button>
                    ))}
                    <Button
                      variant="outline"
                      size="sm"
                      className="ml-4"
                      onClick={() => {
                        setShowDetailModal(false);
                        setShowCloseModal(true);
                      }}
                    >
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                      Fechar Negócio
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </Modal>

        {/* Close Opportunity Modal */}
        <Modal
          isOpen={showCloseModal}
          onClose={() => setShowCloseModal(false)}
          title="Fechar Oportunidade"
          size="md"
        >
          <div className="space-y-6">
            <div className="flex gap-4">
              <Button
                variant={closeData.won ? 'primary' : 'outline'}
                className="flex-1 h-24 flex-col"
                onClick={() => setCloseData({ ...closeData, won: true })}
              >
                <ThumbsUp className="h-8 w-8 mb-2" />
                <span>Ganho</span>
              </Button>
              <Button
                variant={!closeData.won ? 'danger' : 'outline'}
                className="flex-1 h-24 flex-col"
                onClick={() => setCloseData({ ...closeData, won: false })}
              >
                <ThumbsDown className="h-8 w-8 mb-2" />
                <span>Perdido</span>
              </Button>
            </div>

            {!closeData.won && (
              <Select
                label="Motivo da Perda"
                options={Object.entries(LOSS_REASON_LABELS).map(([key, label]) => ({
                  value: key,
                  label
                }))}
                value={closeData.loss_reason || ''}
                onChange={(value) => setCloseData({ ...closeData, loss_reason: value as LossReason })}
              />
            )}

            <Input
              label="Observações"
              placeholder="Notas sobre o fechamento..."
              value={closeData.notes || ''}
              onChange={(e) => setCloseData({ ...closeData, notes: e.target.value })}
            />

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowCloseModal(false)}>
                Cancelar
              </Button>
              <Button
                onClick={handleClose}
                disabled={closeMutation.isPending}
              >
                {closeMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Fechando...
                  </>
                ) : (
                  'Confirmar'
                )}
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
