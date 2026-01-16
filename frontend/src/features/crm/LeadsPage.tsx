'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Phone,
  Mail,
  Building2,
  Calendar,
  TrendingUp,
  Users,
  Target,
  Star,
  CheckCircle2,
  XCircle,
  Eye,
  Edit,
  Trash2,
  Download,
  Upload,
  RefreshCw,
  MessageSquare,
  Activity,
  Zap,
  Globe,
  Linkedin,
  MapPin,
  DollarSign,
  Percent,
  BarChart3,
  MoreHorizontal,
  Copy,
  Clock,
  FileText,
  Tag,
  List,
  LayoutGrid,
  Info,
  Loader2,
  AlertTriangle,
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
  Modal,
  Select,
  SimpleTabBar,
  Skeleton,
} from '@/design-system/components';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

// Importações do módulo CRM
import { useLeads, useLeadStats, useCreateLead, useUpdateLead, useUpdateLeadStatus, useDeleteLead } from './hooks';
import type { Lead, LeadCreate, LeadUpdate, LeadStatus, LeadSource, LeadFilter } from './types';
import { LeadStatus as LeadStatusEnum, LeadSource as LeadSourceEnum } from './types';

// ==================== CONSTANTS ====================

const STATUS_CONFIG: Record<string, { label: string; variant: 'info' | 'primary' | 'secondary' | 'warning' | 'success' | 'danger'; icon: React.ElementType }> = {
  new: { label: 'Novo', variant: 'info', icon: Star },
  contacted: { label: 'Contatado', variant: 'primary', icon: Phone },
  qualified: { label: 'Qualificado', variant: 'secondary', icon: CheckCircle2 },
  proposal: { label: 'Proposta', variant: 'warning', icon: FileText },
  negotiation: { label: 'Negociação', variant: 'primary', icon: TrendingUp },
  won: { label: 'Ganho', variant: 'success', icon: CheckCircle2 },
  lost: { label: 'Perdido', variant: 'danger', icon: XCircle },
};

const SOURCE_CONFIG: Record<string, { label: string; icon: React.ElementType }> = {
  website: { label: 'Website', icon: Globe },
  referral: { label: 'Indicação', icon: Users },
  social_media: { label: 'Redes Sociais', icon: Linkedin },
  event: { label: 'Evento', icon: Calendar },
  cold_call: { label: 'Cold Call', icon: Phone },
  email_campaign: { label: 'Email', icon: Mail },
  partner: { label: 'Parceiro', icon: Target },
  other: { label: 'Outro', icon: Info },
};

const INTEREST_CONFIG: Record<string, { label: string; variant: 'danger' | 'warning' | 'info' }> = {
  hot: { label: 'Quente', variant: 'danger' },
  warm: { label: 'Morno', variant: 'warning' },
  cold: { label: 'Frio', variant: 'info' },
};

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

const getScoreColor = (score: number) => {
  if (score >= 80) return 'text-accent-success';
  if (score >= 60) return 'text-accent-warning';
  return 'text-accent-danger';
};

const getScoreBarColor = (score: number) => {
  if (score >= 80) return 'bg-accent-success';
  if (score >= 60) return 'bg-accent-warning';
  return 'bg-accent-danger';
};

const getInterestLevel = (score: number): 'hot' | 'warm' | 'cold' => {
  if (score >= 70) return 'hot';
  if (score >= 40) return 'warm';
  return 'cold';
};

// Custom Tooltip para gráficos
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

export function LeadsPage() {
  // State
  const [activeTab, setActiveTab] = useState('list');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [selectedInterest, setSelectedInterest] = useState('all');
  const [showNewLeadModal, setShowNewLeadModal] = useState(false);
  const [showLeadDetailModal, setShowLeadDetailModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Form state para novo lead
  const [newLeadForm, setNewLeadForm] = useState<Partial<LeadCreate>>({
    source: LeadSourceEnum.OTHER,
  });

  // Construir filtros
  const filters: LeadFilter & { page: number; page_size: number } = useMemo(() => ({
    page,
    page_size: pageSize,
    status: selectedStatus !== 'all' ? selectedStatus as LeadStatus : undefined,
    source: selectedSource !== 'all' ? selectedSource as LeadSource : undefined,
    is_hot: selectedInterest === 'hot' ? true : undefined,
    search: searchTerm || undefined,
  }), [page, selectedStatus, selectedSource, selectedInterest, searchTerm]);

  // Hooks de dados
  const { data: leadsData, isLoading, isError, error, refetch } = useLeads(filters);
  const { data: stats, isLoading: isLoadingStats } = useLeadStats();
  const createLeadMutation = useCreateLead();
  const updateLeadMutation = useUpdateLead();
  const updateStatusMutation = useUpdateLeadStatus();
  const deleteLeadMutation = useDeleteLead();

  // Dados processados
  const leads = leadsData?.items || [];
  const totalLeads = leadsData?.total || 0;
  const totalPages = leadsData?.total_pages || 1;

  // Calcular estatísticas para gráficos
  const sourceDistribution = useMemo(() => {
    if (!stats?.by_source) return [];
    return Object.entries(stats.by_source).map(([source, count], index) => ({
      name: SOURCE_CONFIG[source]?.label || source,
      value: count,
      color: ['#6366f1', '#10b981', '#0077b5', '#f59e0b', '#ef4444', '#64748b'][index % 6],
    }));
  }, [stats]);

  const statusDistribution = useMemo(() => {
    if (!stats?.by_status) return [];
    return Object.entries(stats.by_status).map(([status, count]) => ({
      stage: STATUS_CONFIG[status]?.label || status,
      count,
    }));
  }, [stats]);

  // Handlers
  const handleCreateLead = useCallback(async () => {
    if (!newLeadForm.name || !newLeadForm.email) return;

    try {
      await createLeadMutation.mutateAsync(newLeadForm as LeadCreate);
      setShowNewLeadModal(false);
      setNewLeadForm({ source: LeadSourceEnum.OTHER });
    } catch (err) {
      console.error('Erro ao criar lead:', err);
    }
  }, [newLeadForm, createLeadMutation]);

  const handleDeleteLead = useCallback(async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este lead?')) return;

    try {
      await deleteLeadMutation.mutateAsync(id);
    } catch (err) {
      console.error('Erro ao excluir lead:', err);
    }
  }, [deleteLeadMutation]);

  const handleUpdateStatus = useCallback(async (id: string, status: LeadStatus) => {
    try {
      await updateStatusMutation.mutateAsync({ id, data: { status } });
    } catch (err) {
      console.error('Erro ao atualizar status:', err);
    }
  }, [updateStatusMutation]);

  // Tabs
  const tabs = [
    { value: 'list', label: 'Lista', icon: <List className="h-4 w-4" /> },
    { value: 'overview', label: 'Overview', icon: <BarChart3 className="h-4 w-4" /> },
    { value: 'funnel', label: 'Funil', icon: <TrendingUp className="h-4 w-4" /> },
  ];

  // Colunas da tabela
  const columns = [
    {
      key: 'name',
      header: 'Lead',
      render: (row: Lead) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.name} size="sm" />
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.company || '-'}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'contact',
      header: 'Contato',
      render: (row: Lead) => (
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Mail className="h-3 w-3" />
            <span className="truncate max-w-[180px]">{row.email}</span>
          </div>
          {row.phone && (
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <Phone className="h-3 w-3" />
              {row.phone}
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'source',
      header: 'Origem',
      render: (row: Lead) => {
        const source = SOURCE_CONFIG[row.source] || SOURCE_CONFIG.other;
        const Icon = source.icon;
        return (
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4 text-text-muted" />
            <span className="text-sm">{source.label}</span>
          </div>
        );
      },
    },
    {
      key: 'score',
      header: 'Score',
      sortable: true,
      render: (row: Lead) => (
        <div className="flex items-center gap-2">
          <div className="w-14 h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${getScoreBarColor(row.score)}`}
              style={{ width: `${row.score}%` }}
            />
          </div>
          <span className={`text-sm font-medium ${getScoreColor(row.score)}`}>{row.score}</span>
        </div>
      ),
    },
    {
      key: 'interest',
      header: 'Interesse',
      render: (row: Lead) => {
        const interest = INTEREST_CONFIG[getInterestLevel(row.score)];
        return <Badge variant={interest.variant}>{interest.label}</Badge>;
      },
    },
    {
      key: 'value',
      header: 'Valor',
      sortable: true,
      render: (row: Lead) => (
        <span className="font-mono font-medium text-text-primary">
          {formatCurrency(row.expected_value)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: Lead) => {
        const status = STATUS_CONFIG[row.status] || STATUS_CONFIG.new;
        const Icon = status.icon;
        return (
          <Badge variant={status.variant}>
            <Icon className="h-3 w-3 mr-1" />
            {status.label}
          </Badge>
        );
      },
    },
    {
      key: 'actions',
      header: '',
      render: (row: Lead) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedLead(row);
              setShowLeadDetailModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleDeleteLead(row.id)}
          >
            <Trash2 className="h-4 w-4 text-accent-danger" />
          </Button>
        </div>
      ),
    },
  ];

  // Loading state
  if (isLoading && !leadsData) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-64 mt-2" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
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
          <h2 className="text-xl font-semibold text-text-primary">Erro ao carregar leads</h2>
          <p className="text-text-secondary">{(error as Error)?.message || 'Tente novamente mais tarde'}</p>
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
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Leads
            </h1>
            <p className="text-text-secondary mt-1">
              Pipeline de prospecção e qualificação de leads
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Upload className="h-4 w-4 mr-2" />
              Importar
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewLeadModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Lead
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Leads"
              value={isLoadingStats ? '...' : (stats?.total || 0).toString()}
              change={12}
              changeLabel="este mês"
              icon={<Users className="h-5 w-5" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Leads Quentes"
              value={isLoadingStats ? '...' : (stats?.hot_leads || 0).toString()}
              change={25}
              changeLabel="prioridade alta"
              icon={<Zap className="h-5 w-5" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Valor no Pipeline"
              value={isLoadingStats ? '...' : formatCurrency(stats?.total_expected_value || 0)}
              change={8.5}
              changeLabel="potencial"
              icon={<DollarSign className="h-5 w-5" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Score Médio"
              value={isLoadingStats ? '...' : Math.round(stats?.avg_score || 0).toString()}
              change={5.2}
              changeLabel="qualidade"
              icon={<Target className="h-5 w-5" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Valor Ponderado"
              value={isLoadingStats ? '...' : formatCurrency(stats?.total_weighted_value || 0)}
              change={3.1}
              changeLabel="expectativa"
              icon={<Percent className="h-5 w-5" />}
              iconColor="warning"
            />
          </motion.div>
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Tab: List */}
        {activeTab === 'list' && (
          <div className="space-y-4">
            {/* Filters */}
            <Card>
              <CardBody className="py-4">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Input
                      placeholder="Buscar leads por nome, empresa ou email..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select
                    options={[
                      { value: 'all', label: 'Todos os Status' },
                      ...Object.entries(STATUS_CONFIG).map(([key, config]) => ({
                        value: key,
                        label: config.label
                      }))
                    ]}
                    value={selectedStatus}
                    onChange={setSelectedStatus}
                  />
                  <Select
                    options={[
                      { value: 'all', label: 'Todas as Origens' },
                      ...Object.entries(SOURCE_CONFIG).map(([key, config]) => ({
                        value: key,
                        label: config.label
                      }))
                    ]}
                    value={selectedSource}
                    onChange={setSelectedSource}
                  />
                  <Select
                    options={[
                      { value: 'all', label: 'Todo Interesse' },
                      { value: 'hot', label: 'Quente' },
                      { value: 'warm', label: 'Morno' },
                      { value: 'cold', label: 'Frio' },
                    ]}
                    value={selectedInterest}
                    onChange={setSelectedInterest}
                  />
                  <div className="flex items-center gap-1 border-l border-border-subtle pl-4">
                    <Button
                      variant={viewMode === 'table' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('table')}
                    >
                      <List className="h-4 w-4" />
                    </Button>
                    <Button
                      variant={viewMode === 'cards' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('cards')}
                    >
                      <LayoutGrid className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Table View */}
            {viewMode === 'table' && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
                <Card>
                  <CardHeader
                    title={`${totalLeads} leads encontrados`}
                    action={
                      <Button variant="ghost" size="sm" onClick={() => refetch()} disabled={isLoading}>
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Atualizar
                      </Button>
                    }
                  />
                  <CardBody className="p-0">
                    <DataTable
                      columns={columns}
                      data={leads}
                      keyExtractor={(row) => row.id}
                    />
                  </CardBody>
                </Card>

                {/* Paginação */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2 mt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page <= 1}
                      onClick={() => setPage(p => p - 1)}
                    >
                      Anterior
                    </Button>
                    <span className="text-sm text-text-secondary">
                      Página {page} de {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page >= totalPages}
                      onClick={() => setPage(p => p + 1)}
                    >
                      Próxima
                    </Button>
                  </div>
                )}
              </motion.div>
            )}

            {/* Cards View */}
            {viewMode === 'cards' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {leads.map((lead) => (
                  <motion.div key={lead.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                    <Card className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                      <CardBody>
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <Avatar name={lead.name} size="md" />
                            <div>
                              <p className="font-semibold text-text-primary">{lead.name}</p>
                              <p className="text-sm text-text-secondary">{lead.company || '-'}</p>
                            </div>
                          </div>
                          <Badge variant={STATUS_CONFIG[lead.status]?.variant || 'info'}>
                            {STATUS_CONFIG[lead.status]?.label || lead.status}
                          </Badge>
                        </div>

                        <div className="space-y-2 mb-4">
                          <div className="flex items-center gap-2 text-sm text-text-secondary">
                            <Mail className="h-4 w-4" />
                            <span className="truncate">{lead.email}</span>
                          </div>
                          {lead.phone && (
                            <div className="flex items-center gap-2 text-sm text-text-secondary">
                              <Phone className="h-4 w-4" />
                              {lead.phone}
                            </div>
                          )}
                        </div>

                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <p className="text-xs text-text-muted">Score</p>
                            <div className="flex items-center gap-2">
                              <div className="w-16 h-2 bg-bg-tertiary rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${getScoreBarColor(lead.score)}`}
                                  style={{ width: `${lead.score}%` }}
                                />
                              </div>
                              <span className={`text-sm font-medium ${getScoreColor(lead.score)}`}>
                                {lead.score}
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-text-muted">Valor</p>
                            <p className="font-mono font-semibold text-text-primary">
                              {formatCurrency(lead.expected_value)}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
                          <span className="text-xs text-text-muted">
                            {formatDate(lead.created_at)}
                          </span>
                          <div className="flex items-center gap-1">
                            <Button variant="ghost" size="sm">
                              <Phone className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Mail className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedLead(lead);
                                setShowLeadDetailModal(true);
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardBody>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab: Overview */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Source Distribution */}
            <Card>
              <CardHeader title="Leads por Origem" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sourceDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {sourceDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-2 mt-4">
                  {sourceDistribution.map((item) => (
                    <div key={item.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm text-text-secondary">{item.name}</span>
                      </div>
                      <span className="text-sm font-medium text-text-primary">{item.value}</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Status Distribution */}
            <Card>
              <CardHeader title="Leads por Status" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={statusDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="stage" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="count" name="Quantidade" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Tab: Funnel */}
        {activeTab === 'funnel' && (
          <div className="space-y-6">
            <Card>
              <CardHeader
                title="Funil de Conversão"
                description="Acompanhe a jornada dos leads pelo pipeline"
              />
              <CardBody>
                <div className="space-y-4">
                  {statusDistribution.map((stage, index) => {
                    const maxCount = Math.max(...statusDistribution.map(s => s.count));
                    const widthPercent = maxCount > 0 ? (stage.count / maxCount) * 100 : 0;

                    return (
                      <div key={stage.stage}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-text-primary font-medium">{stage.stage}</span>
                          <span className="text-sm text-text-secondary">{stage.count} leads</span>
                        </div>
                        <div className="h-10 bg-bg-tertiary rounded-lg overflow-hidden">
                          <div
                            className="h-full rounded-lg transition-all flex items-center justify-center bg-accent-primary"
                            style={{
                              width: `${widthPercent}%`,
                              opacity: 1 - (index * 0.12)
                            }}
                          >
                            {widthPercent > 10 && (
                              <span className="text-sm font-medium text-white">
                                {widthPercent.toFixed(0)}%
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* New Lead Modal */}
        <Modal
          isOpen={showNewLeadModal}
          onClose={() => setShowNewLeadModal(false)}
          title="Novo Lead"
          size="lg"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Nome Completo *"
                placeholder="Nome do contato"
                value={newLeadForm.name || ''}
                onChange={(e) => setNewLeadForm(prev => ({ ...prev, name: e.target.value }))}
              />
              <Input
                label="Email *"
                type="email"
                placeholder="email@empresa.com"
                value={newLeadForm.email || ''}
                onChange={(e) => setNewLeadForm(prev => ({ ...prev, email: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Telefone"
                placeholder="(00) 00000-0000"
                value={newLeadForm.phone || ''}
                onChange={(e) => setNewLeadForm(prev => ({ ...prev, phone: e.target.value }))}
              />
              <Input
                label="Empresa"
                placeholder="Nome da empresa"
                value={newLeadForm.company || ''}
                onChange={(e) => setNewLeadForm(prev => ({ ...prev, company: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Cargo"
                placeholder="Cargo/Posição"
                value={newLeadForm.position || ''}
                onChange={(e) => setNewLeadForm(prev => ({ ...prev, position: e.target.value }))}
              />
              <Select
                label="Origem"
                options={Object.entries(SOURCE_CONFIG).map(([key, config]) => ({
                  value: key,
                  label: config.label
                }))}
                value={newLeadForm.source || 'other'}
                onChange={(value) => setNewLeadForm(prev => ({ ...prev, source: value as LeadSource }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Setor/Indústria"
                placeholder="Ex: Tecnologia, Saúde, Varejo"
                value={newLeadForm.industry || ''}
                onChange={(e) => setNewLeadForm(prev => ({ ...prev, industry: e.target.value }))}
              />
              <Input
                label="Valor Estimado"
                placeholder="R$ 0,00"
                type="number"
                value={newLeadForm.expected_value?.toString() || ''}
                onChange={(e) => setNewLeadForm(prev => ({ ...prev, expected_value: parseFloat(e.target.value) || 0 }))}
              />
            </div>
            <Input
              label="Observações"
              placeholder="Notas sobre o lead..."
              value={newLeadForm.notes || ''}
              onChange={(e) => setNewLeadForm(prev => ({ ...prev, notes: e.target.value }))}
            />

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewLeadModal(false)}>
                Cancelar
              </Button>
              <Button
                onClick={handleCreateLead}
                disabled={!newLeadForm.name || !newLeadForm.email || createLeadMutation.isPending}
              >
                {createLeadMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Criando...
                  </>
                ) : (
                  'Criar Lead'
                )}
              </Button>
            </div>
          </div>
        </Modal>

        {/* Lead Detail Modal */}
        <Modal
          isOpen={showLeadDetailModal}
          onClose={() => setShowLeadDetailModal(false)}
          title={selectedLead?.name || 'Detalhes do Lead'}
          size="xl"
        >
          {selectedLead && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedLead.name} size="lg" />
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedLead.name}</h3>
                    <p className="text-text-secondary">
                      {selectedLead.position || 'Sem cargo'} {selectedLead.company ? `em ${selectedLead.company}` : ''}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={STATUS_CONFIG[selectedLead.status]?.variant || 'info'}>
                        {STATUS_CONFIG[selectedLead.status]?.label || selectedLead.status}
                      </Badge>
                      <Badge variant={INTEREST_CONFIG[getInterestLevel(selectedLead.score)].variant}>
                        {INTEREST_CONFIG[getInterestLevel(selectedLead.score)].label}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <Edit className="h-4 w-4 mr-2" />
                    Editar
                  </Button>
                  <Button size="sm">
                    <Phone className="h-4 w-4 mr-2" />
                    Ligar
                  </Button>
                </div>
              </div>

              {/* Info Grid */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Score</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-2xl font-bold ${getScoreColor(selectedLead.score)}`}>
                      {selectedLead.score}
                    </span>
                    <div className="flex-1 h-2 bg-bg-secondary rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${getScoreBarColor(selectedLead.score)}`}
                        style={{ width: `${selectedLead.score}%` }}
                      />
                    </div>
                  </div>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Valor Potencial</p>
                  <p className="text-2xl font-bold text-accent-success mt-1">
                    {formatCurrency(selectedLead.expected_value)}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Valor Ponderado</p>
                  <p className="text-2xl font-bold text-text-primary mt-1">
                    {formatCurrency(selectedLead.weighted_value)}
                  </p>
                </div>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Informações de Contato</h4>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Mail className="h-4 w-4 text-text-muted" />
                      <span className="text-text-secondary">{selectedLead.email}</span>
                      <Button variant="ghost" size="sm">
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                    {selectedLead.phone && (
                      <div className="flex items-center gap-3">
                        <Phone className="h-4 w-4 text-text-muted" />
                        <span className="text-text-secondary">{selectedLead.phone}</span>
                      </div>
                    )}
                    {selectedLead.company && (
                      <div className="flex items-center gap-3">
                        <Building2 className="h-4 w-4 text-text-muted" />
                        <span className="text-text-secondary">{selectedLead.company}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Informações Adicionais</h4>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Tag className="h-4 w-4 text-text-muted" />
                      <span className="text-text-secondary">Origem: {SOURCE_CONFIG[selectedLead.source]?.label || selectedLead.source}</span>
                    </div>
                    {selectedLead.industry && (
                      <div className="flex items-center gap-3">
                        <Activity className="h-4 w-4 text-text-muted" />
                        <span className="text-text-secondary">Setor: {selectedLead.industry}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-3">
                      <Calendar className="h-4 w-4 text-text-muted" />
                      <span className="text-text-secondary">Criado em: {formatDate(selectedLead.created_at)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Notes */}
              {selectedLead.notes && (
                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Observações</h4>
                  <p className="text-text-secondary p-4 rounded-lg bg-bg-tertiary">
                    {selectedLead.notes}
                  </p>
                </div>
              )}

              {/* Quick Actions */}
              <div className="pt-4 border-t border-border-subtle">
                <h4 className="font-semibold text-text-primary mb-3">Alterar Status</h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(STATUS_CONFIG).map(([key, config]) => (
                    <Button
                      key={key}
                      variant={selectedLead.status === key ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => handleUpdateStatus(selectedLead.id, key as LeadStatus)}
                      disabled={updateStatusMutation.isPending}
                    >
                      {config.label}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
