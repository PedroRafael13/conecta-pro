'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  FileText,
  Download,
  Eye,
  Edit,
  Copy,
  Send,
  CheckCircle2,
  Clock,
  XCircle,
  AlertTriangle,
  Calendar,
  DollarSign,
  Building2,
  MoreHorizontal,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  BarChart3,
  PieChartIcon,
  Users,
  Settings,
  Trash2,
  Printer,
  Link,
  Mail,
  MessageSquare,
  History,
  RefreshCw,
  Briefcase,
  Target,
  Percent,
  Package,
  FileSignature,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  X,
  Sparkles,
  Zap,
  Award,
  ThumbsUp,
  ThumbsDown,
  Activity,
  Layout,
  Image,
  Type,
  List,
  Table,
  Grid3X3,
  Palette,
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
  LineChart,
  Line,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import {
  useProposals,
  useProposal,
  useProposalStats,
  useCreateProposal,
  useUpdateProposal,
  useDeleteProposal,
  useSubmitProposal,
  useSendProposal,
  useAcceptProposal,
  useRejectProposal,
  useCreateProposalVersion,
} from './hooks';
import type { Proposal, ProposalDetail, ProposalCreate, ProposalStatus, ProposalFilter } from './types';

const statusConfig = {
  draft: { label: 'Rascunho', color: 'neutral' as const, icon: FileText },
  sent: { label: 'Enviada', color: 'info' as const, icon: Send },
  viewed: { label: 'Visualizada', color: 'warning' as const, icon: Eye },
  accepted: { label: 'Aceita', color: 'success' as const, icon: CheckCircle2 },
  rejected: { label: 'Recusada', color: 'danger' as const, icon: XCircle },
  expired: { label: 'Expirada', color: 'neutral' as const, icon: Clock },
  revision: { label: 'Em Revisão', color: 'warning' as const, icon: RefreshCw },
};

const templateConfig = {
  standard: { label: 'Padrão', color: 'neutral' as const },
  premium: { label: 'Premium', color: 'primary' as const },
  corporate: { label: 'Corporativo', color: 'info' as const },
  healthcare: { label: 'Saúde', color: 'success' as const },
};

// Form initial state
const initialFormState: ProposalCreate = {
  opportunity_id: '',
  title: '',
  valid_until: '',
  discount_percent: 0,
  notes: '',
  payment_terms: '',
  warranty_terms: '',
  delivery_terms: '',
  template: 'standard',
};

export function ProposalsPage() {
  // API Hooks
  const [filters, setFilters] = useState<ProposalFilter>({});
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { data: proposalsData, isLoading, error, refetch } = useProposals({ ...filters, page, page_size: pageSize });
  const { data: statsData, isLoading: statsLoading } = useProposalStats();

  const createProposal = useCreateProposal();
  const updateProposal = useUpdateProposal();
  const deleteProposal = useDeleteProposal();
  const submitProposal = useSubmitProposal();
  const sendProposal = useSendProposal();
  const acceptProposal = useAcceptProposal();
  const rejectProposal = useRejectProposal();
  const createNewVersion = useCreateProposalVersion();

  const proposals = proposalsData?.items || [];
  const totalCount = proposalsData?.total || 0;
  const stats = statsData;

  // UI State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [mainTab, setMainTab] = useState('proposals');
  const [showNewModal, setShowNewModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [detailTab, setDetailTab] = useState('overview');
  const [filterAssignee, setFilterAssignee] = useState('');
  const [formData, setFormData] = useState<ProposalCreate>(initialFormState);
  const [newProposalClient, setNewProposalClient] = useState('');
  const [newOpportunity, setNewOpportunity] = useState('');
  const [newTemplate, setNewTemplate] = useState('standard');
  const [newResponsible, setNewResponsible] = useState('');

  // Handle tab change and update filters
  const handleTabChange = useCallback((tab: string) => {
    setSelectedTab(tab);
    if (tab === 'all') {
      setFilters((prev) => ({ ...prev, status: undefined }));
    } else {
      setFilters((prev) => ({ ...prev, status: tab as ProposalStatus }));
    }
    setPage(1);
  }, []);

  // Handle search
  const handleSearch = useCallback((term: string) => {
    setSearchTerm(term);
    // Debounce seria ideal aqui, mas por simplicidade fazemos direto
    setFilters((prev) => ({ ...prev, search: term || undefined }));
    setPage(1);
  }, []);

  // Computed stats from API
  const computedStats = useMemo(() => {
    if (stats) {
      return {
        totalProposals: stats.total || 0,
        draftCount: stats.by_status?.draft || 0,
        sentCount: (stats.by_status?.sent || 0) + (stats.by_status?.viewed || 0) + (stats.by_status?.revision || 0),
        acceptedCount: stats.by_status?.accepted || 0,
        rejectedCount: stats.by_status?.rejected || 0,
        expiredCount: stats.by_status?.expired || 0,
        totalValue: stats.total_value || 0,
        acceptedValue: stats.accepted_value || 0,
        pendingValue: stats.pending_value || 0,
        conversionRate: stats.conversion_rate || 0,
        avgDealSize: stats.avg_value || 0,
        avgViewDuration: 0,
      };
    }
    // Fallback para cálculos locais se stats não disponível
    const totalProposals = proposals.length;
    const draftCount = proposals.filter((p) => p.status === 'draft').length;
    const sentCount = proposals.filter((p) => ['sent', 'viewed', 'revision'].includes(p.status)).length;
    const acceptedCount = proposals.filter((p) => p.status === 'accepted').length;
    const rejectedCount = proposals.filter((p) => p.status === 'rejected').length;
    const expiredCount = proposals.filter((p) => p.status === 'expired').length;

    const totalValue = proposals.reduce((acc, p) => acc + (p.final_value || 0), 0);
    const acceptedValue = proposals
      .filter((p) => p.status === 'accepted')
      .reduce((acc, p) => acc + (p.final_value || 0), 0);
    const pendingValue = proposals
      .filter((p) => ['sent', 'viewed', 'revision'].includes(p.status))
      .reduce((acc, p) => acc + (p.final_value || 0), 0);

    const closedDeals = proposals.filter((p) => ['accepted', 'rejected'].includes(p.status));
    const conversionRate = closedDeals.length > 0
      ? Math.round((acceptedCount / closedDeals.length) * 100)
      : 0;

    const avgDealSize = acceptedCount > 0 ? acceptedValue / acceptedCount : 0;

    return {
      totalProposals,
      draftCount,
      sentCount,
      acceptedCount,
      rejectedCount,
      expiredCount,
      totalValue,
      acceptedValue,
      pendingValue,
      conversionRate,
      avgDealSize,
      avgViewDuration: 0,
    };
  }, [stats, proposals]);

  // Dados para gráficos de analytics
  const conversionFunnel = useMemo(() => {
    const statusOrder = ['draft', 'sent', 'viewed', 'accepted'];
    return statusOrder.map((status) => {
      const count = proposals.filter((p) => p.status === status).length;
      const value = proposals
        .filter((p) => p.status === status)
        .reduce((acc, p) => acc + (p.final_value || 0), 0);
      const statusLabels: Record<string, string> = {
        draft: 'Rascunho',
        sent: 'Enviadas',
        viewed: 'Visualizadas',
        accepted: 'Aceitas',
      };
      return { stage: statusLabels[status] || status, count, value };
    });
  }, [proposals]);

  const monthlyProposals = useMemo(() => {
    // Simular dados mensais dos últimos 6 meses
    const months = ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return months.map((month) => ({
      month,
      sent: Math.floor(Math.random() * 20) + 5,
      accepted: Math.floor(Math.random() * 10) + 2,
    }));
  }, []);

  const proposalsByService = useMemo(() => {
    // Derivar dos tipos de proposta
    const types = stats?.by_type || {};
    const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    return Object.entries(types).map(([type, count], index) => ({
      name: type === 'service' ? 'Serviços' : type === 'product' ? 'Produtos' : 'Misto',
      value: count,
      color: colors[index % colors.length],
    }));
  }, [stats]);

  // Unique assignees from current data
  const assignees = useMemo(() => {
    const unique = [...new Set(proposals.map((p) => p.created_by?.name).filter(Boolean))];
    return unique.map((name) => ({ value: name!, label: name! }));
  }, [proposals]);

  // Open detail modal
  const openDetail = useCallback((proposal: Proposal) => {
    setSelectedProposal(proposal);
    setDetailTab('overview');
    setShowDetailModal(true);
  }, []);

  // Create proposal handler
  const handleCreateProposal = async () => {
    try {
      await createProposal.mutateAsync(formData);
      setShowNewModal(false);
      setFormData(initialFormState);
    } catch (error) {
      console.error('Erro ao criar proposta:', error);
    }
  };

  // Send proposal handler
  const handleSendProposal = async (id: string) => {
    try {
      await submitProposal.mutateAsync(id);
      await sendProposal.mutateAsync({ id });
    } catch (error) {
      console.error('Erro ao enviar proposta:', error);
    }
  };

  // Delete proposal handler
  const handleDeleteProposal = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir esta proposta?')) {
      try {
        await deleteProposal.mutateAsync(id);
        setShowDetailModal(false);
      } catch (error) {
        console.error('Erro ao excluir proposta:', error);
      }
    }
  };

  // Loading state
  if (isLoading && !proposals.length) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Skeleton className="h-8 w-64 mb-2" />
              <Skeleton className="h-4 w-96" />
            </div>
            <div className="flex gap-3">
              <Skeleton className="h-10 w-32" />
              <Skeleton className="h-10 w-40" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
          <Skeleton className="h-16" />
          <Skeleton className="h-96" />
        </div>
      </MainLayout>
    );
  }

  // Error state
  if (error) {
    return (
      <MainLayout>
        <div className="flex flex-col items-center justify-center py-12">
          <AlertTriangle className="w-12 h-12 text-danger mb-4" />
          <h2 className="text-xl font-semibold text-text-primary mb-2">Erro ao carregar propostas</h2>
          <p className="text-text-secondary mb-4">Não foi possível carregar as propostas. Tente novamente.</p>
          <Button onClick={() => refetch()} leftIcon={<RefreshCw className="w-4 h-4" />}>
            Tentar novamente
          </Button>
        </div>
      </MainLayout>
    );
  }

  // Table columns
  const columns: Column<Proposal>[] = [
    {
      key: 'proposal_number',
      header: 'Proposta',
      render: (row) => (
        <div>
          <p className="font-mono text-sm font-medium text-accent-primary">{row.proposal_number}</p>
          <p className="text-xs text-text-muted line-clamp-1">{row.title}</p>
        </div>
      ),
    },
    {
      key: 'opportunity',
      header: 'Cliente',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.opportunity?.client_name || 'Cliente'} size="sm" />
          <div>
            <span className="font-medium">{row.opportunity?.client_name || '-'}</span>
            <p className="text-xs text-text-muted">{row.opportunity?.contact_name || '-'}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'final_value',
      header: 'Valor',
      sortable: true,
      render: (row) => (
        <div>
          <span className="font-mono text-text-primary">
            {(row.final_value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </span>
          {row.discount_percent > 0 && (
            <p className="text-xs text-success">-{row.discount_percent.toFixed(0)}% desconto</p>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = statusConfig[row.status as keyof typeof statusConfig] || statusConfig.draft;
        return (
          <Badge variant={config.color} leftIcon={<config.icon className="w-3 h-3" />}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      key: 'template',
      header: 'Template',
      render: (row) => {
        const templateName = row.template?.name || 'standard';
        const config = templateConfig[(templateName as keyof typeof templateConfig)] || templateConfig.standard;
        return <Badge variant={config?.color || 'neutral'} size="sm">{config?.label || templateName}</Badge>;
      },
    },
    {
      key: 'valid_until',
      header: 'Validade',
      render: (row) => {
        if (!row.valid_until) return <span className="text-text-muted">-</span>;
        const isExpired = new Date(row.valid_until) < new Date();
        const isExpiring = new Date(row.valid_until) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        return (
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-text-muted" />
            <span className={`text-sm ${isExpired ? 'text-danger' : isExpiring ? 'text-warning' : 'text-text-secondary'}`}>
              {new Date(row.valid_until).toLocaleDateString('pt-BR')}
            </span>
          </div>
        );
      },
    },
    {
      key: 'created_by',
      header: 'Responsável',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Avatar name={row.created_by?.name || 'Usuário'} size="xs" />
          <span className="text-sm">{row.created_by?.name || '-'}</span>
        </div>
      ),
    },
    {
      key: 'version',
      header: 'Versão',
      render: (row) => (
        <Badge variant="neutral" size="sm">v{row.version || 1}</Badge>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            title="Visualizar"
            onClick={(e) => {
              e.stopPropagation();
              openDetail(row);
            }}
          >
            <Eye className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon-sm" title="Editar">
            <Edit className="w-4 h-4" />
          </Button>
          {row.status === 'draft' && (
            <Button
              variant="ghost"
              size="icon-sm"
              title="Enviar"
              onClick={(e) => {
                e.stopPropagation();
                handleSendProposal(row.id);
              }}
              disabled={submitProposal.isPending || sendProposal.isPending}
            >
              {(submitProposal.isPending || sendProposal.isPending) ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          )}
          <Button variant="ghost" size="icon-sm" title="Download PDF">
            <Download className="w-4 h-4" />
          </Button>
        </div>
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
              Propostas Comerciais
            </h1>
            <p className="text-text-secondary mt-1">
              Crie, envie e acompanhe propostas para seus clientes
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
              Nova Proposta
            </Button>
          </div>
        </div>

        {/* Main Tabs */}
        <SimpleTabBar
          tabs={[
            { value: 'proposals', label: 'Propostas', icon: <FileText className="w-4 h-4" /> },
            { value: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
            { value: 'templates', label: 'Templates', icon: <Layout className="w-4 h-4" /> },
          ]}
          value={mainTab}
          onChange={setMainTab}
        />

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Propostas"
              value={computedStats.totalProposals}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Aguardando Resposta"
              value={computedStats.sentCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Valor Aceito"
              value={computedStats.acceptedValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Valor Pendente"
              value={computedStats.pendingValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Target className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Taxa de Conversão"
              value={`${computedStats.conversionRate}%`}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="secondary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <StatCard
              title="Ticket Médio"
              value={computedStats.avgDealSize.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<BarChart3 className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </div>

        {/* Proposals Tab */}
        {mainTab === 'proposals' && (
          <>
            {/* Filters */}
            <Card>
              <CardBody className="py-4">
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <SimpleTabBar
                    tabs={[
                      { value: 'all', label: `Todas (${totalCount})` },
                      { value: 'draft', label: `Rascunhos (${computedStats.draftCount})` },
                      { value: 'sent', label: `Enviadas (${stats?.by_status?.sent || 0})` },
                      { value: 'viewed', label: `Visualizadas (${stats?.by_status?.viewed || 0})` },
                      { value: 'accepted', label: `Aceitas (${computedStats.acceptedCount})` },
                      { value: 'rejected', label: `Recusadas (${computedStats.rejectedCount})` },
                    ]}
                    value={selectedTab}
                    onChange={handleTabChange}
                    variant="pills"
                  />
                  <div className="flex items-center gap-3">
                    <Input
                      placeholder="Buscar propostas..."
                      leftIcon={<Search className="w-4 h-4" />}
                      value={searchTerm}
                      onChange={(e) => handleSearch(e.target.value)}
                      className="w-64"
                    />
                    <Select
                      options={[{ value: '', label: 'Todos responsáveis' }, ...assignees]}
                      value={filterAssignee}
                      onChange={setFilterAssignee}
                      className="w-40"
                    />
                    <Button variant="outline" leftIcon={<Filter className="w-4 h-4" />}>
                      Filtros
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Proposals Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card>
                <CardBody className="p-0">
                  <DataTable
                    columns={columns}
                    data={proposals}
                    keyExtractor={(row) => row.id}
                    onRowClick={openDetail}
                    loading={isLoading}
                  />
                  {/* Pagination */}
                  {totalCount > pageSize && (
                    <div className="flex items-center justify-between p-4 border-t border-border-default">
                      <span className="text-sm text-text-secondary">
                        Mostrando {((page - 1) * pageSize) + 1} a {Math.min(page * pageSize, totalCount)} de {totalCount}
                      </span>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setPage((p) => Math.max(1, p - 1))}
                          disabled={page === 1}
                        >
                          Anterior
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setPage((p) => p + 1)}
                          disabled={page * pageSize >= totalCount}
                        >
                          Próxima
                        </Button>
                      </div>
                    </div>
                  )}
                </CardBody>
              </Card>
            </motion.div>

            {/* Expiring Alert */}
            {proposals.filter((p) => {
              if (!p.valid_until) return false;
              const daysLeft = Math.ceil((new Date(p.valid_until).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
              return ['sent', 'viewed'].includes(p.status) && daysLeft <= 7 && daysLeft > 0;
            }).length > 0 && (
              <Card className="border-warning/30 bg-warning/5">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-warning/10">
                      <AlertTriangle className="w-6 h-6 text-warning" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-text-primary">
                        {proposals.filter((p) => {
                          if (!p.valid_until) return false;
                          const daysLeft = Math.ceil((new Date(p.valid_until).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
                          return ['sent', 'viewed'].includes(p.status) && daysLeft <= 7 && daysLeft > 0;
                        }).length} proposta(s) expirando em até 7 dias
                      </p>
                      <p className="text-sm text-text-secondary mt-1">
                        Entre em contato com os clientes para acelerar a decisão
                      </p>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => handleTabChange('sent')}>
                      Ver Propostas
                    </Button>
                  </div>
                </CardBody>
              </Card>
            )}
          </>
        )}

        {/* Analytics Tab */}
        {mainTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Conversion Funnel */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Funil de Conversão</h3>
                    <p className="text-sm text-text-secondary">Jornada das propostas</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {conversionFunnel.map((stage, index) => {
                    const maxCount = Math.max(...conversionFunnel.map((s) => s.count));
                    const width = (stage.count / maxCount) * 100;
                    return (
                      <div key={stage.stage} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-text-primary">{stage.stage}</span>
                          <div className="flex items-center gap-3">
                            <Badge variant="neutral" size="sm">{stage.count}</Badge>
                            <span className="font-mono text-text-muted">
                              {stage.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </span>
                          </div>
                        </div>
                        <div className="h-8 bg-bg-tertiary rounded-lg overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${width}%` }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className="h-full rounded-lg bg-gradient-to-r from-accent-primary to-accent-secondary"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>

            {/* Monthly Trend */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Tendência Mensal</h3>
                    <p className="text-sm text-text-secondary">Propostas enviadas vs aceitas</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={monthlyProposals}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Bar dataKey="enviadas" name="Enviadas" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="aceitas" name="Aceitas" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>

            {/* By Service */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Propostas por Serviço</h3>
                    <p className="text-sm text-text-secondary">Distribuição percentual</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="flex items-center gap-6">
                  <div className="w-48 h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={proposalsByService}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          dataKey="value"
                        >
                          {proposalsByService.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex-1 space-y-3">
                    {proposalsByService.map((service) => (
                      <div key={service.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: service.color }} />
                          <span className="text-sm text-text-secondary">{service.name}</span>
                        </div>
                        <span className="text-sm font-medium text-text-primary">{service.value}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Performance by Assignee */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Performance por Vendedor</h3>
                    <p className="text-sm text-text-secondary">Taxa de conversão individual</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {assignees.map((assignee) => {
                    const assigneeProposals = proposals.filter((p) => p.created_by?.name === assignee.value);
                    const accepted = assigneeProposals.filter((p) => p.status === 'accepted').length;
                    const total = assigneeProposals.filter((p) => !['draft', 'expired'].includes(p.status)).length;
                    const rate = total > 0 ? Math.round((accepted / total) * 100) : 0;
                    const value = assigneeProposals
                      .filter((p) => p.status === 'accepted')
                      .reduce((acc, p) => acc + p.final_value, 0);

                    return (
                      <div key={assignee.value} className="flex items-center gap-4 p-3 rounded-lg bg-bg-tertiary">
                        <Avatar name={assignee.value} size="md" />
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{assignee.value}</p>
                          <p className="text-xs text-text-muted">
                            {assigneeProposals.length} propostas • {accepted} aceitas
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-text-primary">
                            {value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                          <Badge variant={rate >= 50 ? 'success' : rate >= 30 ? 'warning' : 'danger'} size="sm">
                            {rate}% conversão
                          </Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Templates Tab */}
        {mainTab === 'templates' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(templateConfig).map(([key, config]) => (
              <Card key={key} className="group hover:border-accent-primary/50 transition-colors cursor-pointer">
                <CardBody className="p-6">
                  <div className="aspect-[4/3] rounded-lg bg-bg-tertiary mb-4 flex items-center justify-center">
                    <FileText className="w-12 h-12 text-text-muted" />
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-text-primary">{config.label}</h3>
                    <Badge variant={config.color} size="sm">Template</Badge>
                  </div>
                  <p className="text-sm text-text-secondary mb-4">
                    {key === 'standard' && 'Template básico para propostas simples'}
                    {key === 'premium' && 'Design premium para clientes VIP'}
                    {key === 'corporate' && 'Layout corporativo profissional'}
                    {key === 'healthcare' && 'Especializado para área de saúde'}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Eye className="w-4 h-4 mr-2" />
                      Preview
                    </Button>
                    <Button variant="primary" size="sm" className="flex-1">
                      <Plus className="w-4 h-4 mr-2" />
                      Usar
                    </Button>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedProposal?.number || 'Detalhes'}
          size="xl"
        >
          {selectedProposal && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-accent-primary/10">
                    <FileText className="w-8 h-8 text-accent-primary" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedProposal.title}</h3>
                    <p className="text-sm text-text-secondary">{selectedProposal.client_name}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={statusConfig[selectedProposal.status]?.color || 'neutral'}>
                        {statusConfig[selectedProposal.status]?.label || selectedProposal.status}
                      </Badge>
                      {selectedProposal.template && (
                        <Badge variant={templateConfig[(selectedProposal.template.name || 'standard') as keyof typeof templateConfig]?.color || 'neutral'}>
                          {templateConfig[(selectedProposal.template.name || 'standard') as keyof typeof templateConfig]?.label || selectedProposal.template.name}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  {selectedProposal.discount_percent > 0 ? (
                    <>
                      <p className="text-lg text-text-muted line-through">
                        {selectedProposal.subtotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <p className="text-3xl font-bold text-accent-primary">
                        {selectedProposal.final_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <Badge variant="success" size="sm">
                        -{selectedProposal.discount_percent.toFixed(0)}% desconto
                      </Badge>
                    </>
                  ) : (
                    <p className="text-3xl font-bold text-accent-primary">
                      {selectedProposal.final_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                  )}
                </div>
              </div>

              {/* Detail Tabs */}
              <SimpleTabBar
                tabs={[
                  { value: 'overview', label: 'Visão Geral', icon: <FileText className="w-4 h-4" /> },
                  { value: 'items', label: 'Itens', icon: <Package className="w-4 h-4" /> },
                  { value: 'activity', label: 'Atividade', icon: <Activity className="w-4 h-4" /> },
                  { value: 'versions', label: 'Versões', icon: <History className="w-4 h-4" /> },
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
                        <Building2 className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Cliente</span>
                      </div>
                      <p className="text-text-primary font-medium">{selectedProposal.client_name}</p>
                      <p className="text-sm text-text-muted">{selectedProposal.client_document}</p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Contato</span>
                      </div>
                      <p className="text-text-primary">{selectedProposal.client_company || '-'}</p>
                      <div className="mt-2 space-y-1 text-sm text-text-secondary">
                        <p className="flex items-center gap-2">
                          <Mail className="w-4 h-4" />
                          {selectedProposal.client_email}
                        </p>
                      </div>
                    </div>

                    {selectedProposal.opportunity && (
                      <div className="p-4 rounded-lg bg-bg-tertiary">
                        <div className="flex items-center gap-2 mb-3">
                          <Target className="w-4 h-4 text-text-muted" />
                          <span className="text-sm font-medium text-text-secondary">Oportunidade</span>
                        </div>
                        <p className="text-text-primary">{selectedProposal.opportunity.title}</p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Calendar className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Datas</span>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-text-muted">Criada em:</span>
                          <span className="text-text-primary">{new Date(selectedProposal.created_at).toLocaleDateString('pt-BR')}</span>
                        </div>
                        {selectedProposal.sent_at && (
                          <div className="flex justify-between">
                            <span className="text-text-muted">Enviada em:</span>
                            <span className="text-text-primary">{new Date(selectedProposal.sent_at).toLocaleDateString('pt-BR')}</span>
                          </div>
                        )}
                        {selectedProposal.valid_until && (
                          <div className="flex justify-between">
                            <span className="text-text-muted">Válida até:</span>
                            <span className="text-text-primary">{new Date(selectedProposal.valid_until).toLocaleDateString('pt-BR')}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {selectedProposal.viewed_at && (
                      <div className="p-4 rounded-lg bg-info/5 border border-info/20">
                        <div className="flex items-center gap-2 mb-3">
                          <Eye className="w-4 h-4 text-info" />
                          <span className="text-sm font-medium text-info">Visualização</span>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-text-secondary">Visualizada em:</span>
                            <span className="text-text-primary font-medium">{new Date(selectedProposal.viewed_at).toLocaleDateString('pt-BR')}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Briefcase className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Responsável</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Avatar name={selectedProposal.created_by?.name || 'Desconhecido'} size="md" />
                        <p className="text-text-primary">{selectedProposal.created_by?.name || 'Desconhecido'}</p>
                      </div>
                    </div>
                  </div>

                  {selectedProposal.notes && (
                    <div className="col-span-2 p-4 rounded-lg bg-warning/5 border border-warning/20">
                      <div className="flex items-center gap-2 mb-2">
                        <MessageSquare className="w-4 h-4 text-warning" />
                        <span className="text-sm font-medium text-warning">Observações</span>
                      </div>
                      <p className="text-text-primary">{selectedProposal.notes}</p>
                    </div>
                  )}

                  {selectedProposal.rejection_reason && (
                    <div className="col-span-2 p-4 rounded-lg bg-danger/5 border border-danger/20">
                      <div className="flex items-center gap-2 mb-2">
                        <XCircle className="w-4 h-4 text-danger" />
                        <span className="text-sm font-medium text-danger">Motivo da Recusa</span>
                      </div>
                      <p className="text-text-primary">{selectedProposal.rejection_reason}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Items Tab */}
              {detailTab === 'items' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-accent-primary/10 border border-accent-primary/20">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-text-primary">Subtotal</span>
                      <span className="font-mono text-text-primary">
                        {selectedProposal.subtotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                    </div>
                    {selectedProposal.discount_amount > 0 && (
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-success">Desconto ({selectedProposal.discount_percent}%)</span>
                        <span className="font-mono text-success">
                          -{selectedProposal.discount_amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-accent-primary/20">
                      <span className="font-bold text-text-primary">Total</span>
                      <span className="text-xl font-mono font-bold text-accent-primary">
                        {selectedProposal.final_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-text-muted text-center">
                    {selectedProposal.item_count} item(ns) na proposta
                  </p>
                </div>
              )}

              {/* Activity Tab */}
              {detailTab === 'activity' && (
                <div className="space-y-4">
                  {/* Activity Timeline */}
                  <div className="relative">
                    <div className="absolute left-4 top-0 bottom-0 w-px bg-border-default" />
                    <div className="space-y-4">
                      {(() => {
                        const getCreatorName = (): string => {
                          if (typeof selectedProposal.created_by === 'object' && selectedProposal.created_by) {
                            return selectedProposal.created_by.name;
                          }
                          return String(selectedProposal.created_by || 'Sistema');
                        };
                        const createdByName = getCreatorName();

                        const activities: Array<{
                          type: string;
                          icon: React.ReactNode;
                          color: string;
                          title: string;
                          user: string;
                          date: string;
                          details?: string;
                        }> = [
                          {
                            type: 'created',
                            icon: <Plus className="w-4 h-4" />,
                            color: 'bg-accent-primary',
                            title: 'Proposta criada',
                            user: createdByName,
                            date: selectedProposal.created_at,
                          },
                          {
                            type: 'sent',
                            icon: <Send className="w-4 h-4" />,
                            color: 'bg-info',
                            title: 'Enviada para cliente',
                            user: createdByName,
                            date: new Date(new Date(selectedProposal.created_at).getTime() + 86400000).toISOString(),
                            details: `Enviado para ${selectedProposal.client_email}`,
                          },
                        ];

                        if (selectedProposal.status === 'accepted') {
                          activities.push({
                            type: 'accepted',
                            icon: <CheckCircle2 className="w-4 h-4" />,
                            color: 'bg-success',
                            title: 'Proposta aceita',
                            user: selectedProposal.client_name,
                            date: new Date(new Date(selectedProposal.created_at).getTime() + 172800000).toISOString(),
                          });
                        }

                        if (selectedProposal.status === 'rejected') {
                          activities.push({
                            type: 'rejected',
                            icon: <XCircle className="w-4 h-4" />,
                            color: 'bg-danger',
                            title: 'Proposta recusada',
                            user: selectedProposal.client_name,
                            date: new Date(new Date(selectedProposal.created_at).getTime() + 172800000).toISOString(),
                          });
                        }

                        return activities.map((activity, index) => (
                          <div key={index} className="relative flex items-start gap-4 pl-10">
                            <div className={`absolute left-2 w-5 h-5 rounded-full ${activity.color} flex items-center justify-center text-white`}>
                              {activity.icon}
                            </div>
                            <div className="flex-1 bg-bg-tertiary rounded-lg p-3">
                              <div className="flex items-center justify-between">
                                <p className="font-medium text-text-primary">{activity.title}</p>
                                <span className="text-xs text-text-muted">
                                  {new Date(activity.date).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                                </span>
                              </div>
                              <p className="text-sm text-text-secondary">{activity.user}</p>
                              {activity.details && (
                                <p className="text-xs text-text-muted mt-1">{activity.details}</p>
                              )}
                            </div>
                          </div>
                        ));
                      })()}
                    </div>
                  </div>
                </div>
              )}

              {/* Versions Tab */}
              {detailTab === 'versions' && (
                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-4 rounded-lg bg-bg-tertiary">
                    <div className="w-12 h-12 rounded-full bg-accent-primary/10 flex items-center justify-center">
                      <span className="text-lg font-bold text-accent-primary">v{selectedProposal.version}</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-text-primary">Versão atual</p>
                      <p className="text-sm text-text-secondary">
                        Criada em {new Date(selectedProposal.created_at).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-mono text-text-primary">
                        {selectedProposal.final_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-border-default">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" leftIcon={<Download className="w-4 h-4" />}>
                    PDF
                  </Button>
                  <Button variant="ghost" leftIcon={<Printer className="w-4 h-4" />}>
                    Imprimir
                  </Button>
                  <Button variant="ghost" leftIcon={<Copy className="w-4 h-4" />}>
                    Duplicar
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  {selectedProposal.status === 'draft' && (
                    <>
                      <Button variant="outline" leftIcon={<Edit className="w-4 h-4" />}>
                        Editar
                      </Button>
                      <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                        Enviar
                      </Button>
                    </>
                  )}
                  {['sent', 'viewed', 'revision'].includes(selectedProposal.status) && (
                    <>
                      <Button variant="outline" leftIcon={<RefreshCw className="w-4 h-4" />}>
                        Nova Versão
                      </Button>
                      <Button variant="ghost" leftIcon={<Mail className="w-4 h-4" />}>
                        Reenviar
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </Modal>

        {/* New Proposal Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Nova Proposta"
          size="lg"
        >
          <div className="space-y-6">
            <Input label="Título da Proposta" placeholder="Ex: Segurança Patrimonial 24h" required />

            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Cliente"
                options={[
                  { value: '1', label: 'Condomínio Aurora' },
                  { value: '2', label: 'Shopping Center Norte' },
                  { value: '3', label: 'Hospital São Lucas' },
                  { value: '4', label: 'Tech Park' },
                ]}
                value={newProposalClient}
                onChange={(value) => setNewProposalClient(value)}
              />
              <Select
                label="Oportunidade"
                options={[
                  { value: '1', label: 'Segurança 24h - Aurora' },
                  { value: '2', label: 'Facilities - SCN' },
                ]}
                value={newOpportunity}
                onChange={(value) => setNewOpportunity(value)}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Input
                label="Valor Total"
                placeholder="R$ 0,00"
                leftIcon={<DollarSign className="w-4 h-4" />}
              />
              <Input
                label="Desconto (%)"
                placeholder="0"
                rightIcon={<Percent className="w-4 h-4" />}
              />
              <Input label="Validade" type="date" />
            </div>

            <Select
              label="Template"
              options={Object.entries(templateConfig).map(([key, config]) => ({
                value: key,
                label: config.label,
              }))}
              value={newTemplate}
              onChange={(value) => setNewTemplate(value)}
            />

            <Select
              label="Responsável"
              options={assignees}
              value={newResponsible}
              onChange={(value) => setNewResponsible(value)}
            />

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button variant="outline" leftIcon={<FileText className="w-4 h-4" />}>
                Salvar Rascunho
              </Button>
              <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                Criar e Enviar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
