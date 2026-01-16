'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Flag,
  ToggleLeft,
  ToggleRight,
  Users,
  Building2,
  Percent,
  Calendar,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  Zap,
  Shield,
  Settings,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Activity,
  Target,
  TrendingUp,
  Code,
  Globe,
  RefreshCw,
  Copy,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Modal,
  Select,
  Textarea,
  StatCard,
  StatGrid,
  DataTable,
  Dropdown,
  EmptyState,
  Tabs,
  TabsList,
  TabsTrigger,
  Progress,
} from '@/design-system/components';

// Types
interface FeatureFlag {
  id: string;
  key: string;
  name: string;
  description: string;
  status: 'enabled' | 'disabled' | 'gradual';
  type: 'boolean' | 'percentage' | 'user_list' | 'tenant_list';
  percentage?: number;
  enabledForUsers?: string[];
  enabledForTenants?: string[];
  category: 'feature' | 'experiment' | 'ops' | 'release';
  environment: 'development' | 'staging' | 'production' | 'all';
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  tags: string[];
}

// Mock data
const mockFeatureFlags: FeatureFlag[] = [
  {
    id: '1',
    key: 'ai_assistant_v2',
    name: 'Assistente IA v2',
    description: 'Nova versão do assistente com recursos avançados de NLP',
    status: 'gradual',
    type: 'percentage',
    percentage: 25,
    category: 'feature',
    environment: 'production',
    createdAt: '2026-01-05',
    updatedAt: '2026-01-15',
    createdBy: 'admin@conectaplus.com.br',
    tags: ['ai', 'beta', 'nlp'],
  },
  {
    id: '2',
    key: 'new_dashboard',
    name: 'Novo Dashboard',
    description: 'Dashboard redesenhado com novos widgets e métricas',
    status: 'enabled',
    type: 'boolean',
    category: 'feature',
    environment: 'all',
    createdAt: '2026-01-01',
    updatedAt: '2026-01-10',
    createdBy: 'admin@conectaplus.com.br',
    tags: ['ui', 'dashboard'],
  },
  {
    id: '3',
    key: 'advanced_reports',
    name: 'Relatórios Avançados',
    description: 'Módulo de relatórios com IA e exportação avançada',
    status: 'enabled',
    type: 'tenant_list',
    enabledForTenants: ['enterprise-1', 'enterprise-2', 'corporate-tower'],
    category: 'feature',
    environment: 'production',
    createdAt: '2025-12-15',
    updatedAt: '2026-01-08',
    createdBy: 'admin@conectaplus.com.br',
    tags: ['reports', 'enterprise'],
  },
  {
    id: '4',
    key: 'dark_mode_v2',
    name: 'Dark Mode Aprimorado',
    description: 'Nova paleta de cores para modo escuro',
    status: 'gradual',
    type: 'percentage',
    percentage: 50,
    category: 'experiment',
    environment: 'production',
    createdAt: '2026-01-10',
    updatedAt: '2026-01-14',
    createdBy: 'design@conectaplus.com.br',
    tags: ['ui', 'experiment', 'theme'],
  },
  {
    id: '5',
    key: 'maintenance_mode',
    name: 'Modo de Manutenção',
    description: 'Ativa mensagem de manutenção no sistema',
    status: 'disabled',
    type: 'boolean',
    category: 'ops',
    environment: 'production',
    createdAt: '2024-06-01',
    updatedAt: '2025-11-20',
    createdBy: 'devops@conectaplus.com.br',
    tags: ['ops', 'maintenance'],
  },
  {
    id: '6',
    key: 'mobile_app_sync',
    name: 'Sincronização App Mobile',
    description: 'Sincronização em tempo real com aplicativo mobile',
    status: 'enabled',
    type: 'boolean',
    category: 'release',
    environment: 'all',
    createdAt: '2025-10-01',
    updatedAt: '2025-12-15',
    createdBy: 'mobile@conectaplus.com.br',
    tags: ['mobile', 'sync'],
  },
  {
    id: '7',
    key: 'beta_billing',
    name: 'Novo Sistema de Cobrança',
    description: 'Sistema de billing redesenhado com suporte a múltiplas moedas',
    status: 'gradual',
    type: 'percentage',
    percentage: 10,
    category: 'release',
    environment: 'staging',
    createdAt: '2026-01-12',
    updatedAt: '2026-01-15',
    createdBy: 'finance@conectaplus.com.br',
    tags: ['billing', 'beta'],
  },
];

const statusConfig: Record<FeatureFlag['status'], { label: string; variant: 'success' | 'danger' | 'warning'; icon: typeof CheckCircle }> = {
  enabled: { label: 'Ativo', variant: 'success', icon: CheckCircle },
  disabled: { label: 'Inativo', variant: 'danger', icon: XCircle },
  gradual: { label: 'Gradual', variant: 'warning', icon: Activity },
};

const categoryConfig: Record<FeatureFlag['category'], { label: string; variant: 'primary' | 'success' | 'warning' | 'info' }> = {
  feature: { label: 'Feature', variant: 'primary' },
  experiment: { label: 'Experimento', variant: 'warning' },
  ops: { label: 'Operacional', variant: 'info' },
  release: { label: 'Release', variant: 'success' },
};

const environmentConfig: Record<FeatureFlag['environment'], { label: string; color: string }> = {
  development: { label: 'Dev', color: 'text-info' },
  staging: { label: 'Staging', color: 'text-warning' },
  production: { label: 'Prod', color: 'text-success' },
  all: { label: 'Todos', color: 'text-accent-primary' },
};

export default function FeatureFlagsPage() {
  const [flags, setFlags] = useState<FeatureFlag[]>(mockFeatureFlags);
  const [editingFlag, setEditingFlag] = useState<FeatureFlag | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [selectedFlag, setSelectedFlag] = useState<FeatureFlag | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [newFlagType, setNewFlagType] = useState('');
  const [newFlagCategory, setNewFlagCategory] = useState('');
  const [newFlagEnvironment, setNewFlagEnvironment] = useState('');

  // Stats
  const stats = {
    total: flags.length,
    enabled: flags.filter(f => f.status === 'enabled').length,
    disabled: flags.filter(f => f.status === 'disabled').length,
    gradual: flags.filter(f => f.status === 'gradual').length,
    experiments: flags.filter(f => f.category === 'experiment').length,
  };

  // Handlers
  const handleToggleFlag = (flagId: string) => {
    setFlags(prevFlags =>
      prevFlags.map(flag =>
        flag.id === flagId
          ? {
              ...flag,
              status: flag.status === 'enabled' ? 'disabled' : 'enabled',
              updatedAt: new Date().toISOString().split('T')[0],
            }
          : flag
      )
    );
  };

  const handleEditFlag = (flag: FeatureFlag) => {
    setEditingFlag(flag);
    setShowEditModal(true);
  };

  const handleDeleteFlag = (flagId: string) => {
    if (confirm('Tem certeza que deseja excluir esta feature flag?')) {
      setFlags(prevFlags => prevFlags.filter(flag => flag.id !== flagId));
    }
  };

  // Filter
  const filteredFlags = flags.filter(flag => {
    const matchesSearch =
      flag.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      flag.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      flag.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || flag.category === categoryFilter;
    const matchesTab = activeTab === 'all' || flag.status === activeTab;
    return matchesSearch && matchesCategory && matchesTab;
  });

  const columns = [
    {
      key: 'flag',
      header: 'Feature Flag',
      render: (row: FeatureFlag) => (
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            row.status === 'enabled' ? 'bg-success/20' : row.status === 'gradual' ? 'bg-warning/20' : 'bg-bg-tertiary'
          }`}>
            <Flag className={`w-5 h-5 ${
              row.status === 'enabled' ? 'text-success' : row.status === 'gradual' ? 'text-warning' : 'text-text-muted'
            }`} />
          </div>
          <div>
            <p className="font-medium">{row.name}</p>
            <p className="text-xs text-text-secondary font-mono">{row.key}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: FeatureFlag) => {
        const config = statusConfig[row.status];
        const Icon = config.icon;
        return (
          <div className="flex items-center gap-2">
            <Icon className={`w-4 h-4 ${row.status === 'enabled' ? 'text-success' : row.status === 'gradual' ? 'text-warning' : 'text-danger'}`} />
            <Badge variant={config.variant}>{config.label}</Badge>
            {row.status === 'gradual' && row.percentage && (
              <span className="text-xs text-text-secondary">{row.percentage}%</span>
            )}
          </div>
        );
      },
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row: FeatureFlag) => (
        <Badge variant={categoryConfig[row.category].variant}>
          {categoryConfig[row.category].label}
        </Badge>
      ),
    },
    {
      key: 'environment',
      header: 'Ambiente',
      render: (row: FeatureFlag) => (
        <span className={`text-sm font-medium ${environmentConfig[row.environment].color}`}>
          {environmentConfig[row.environment].label}
        </span>
      ),
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row: FeatureFlag) => {
        const typeLabels: Record<FeatureFlag['type'], string> = {
          boolean: 'Boolean',
          percentage: 'Percentual',
          user_list: 'Lista Usuários',
          tenant_list: 'Lista Tenants',
        };
        return <span className="text-text-secondary">{typeLabels[row.type]}</span>;
      },
    },
    {
      key: 'updatedAt',
      header: 'Atualizado',
      render: (row: FeatureFlag) => (
        <span className="text-text-secondary">
          {new Date(row.updatedAt).toLocaleDateString('pt-BR')}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row: FeatureFlag) => (
        <div className="flex items-center gap-2">
          <Button
            variant={row.status === 'enabled' ? 'success' : 'ghost'}
            size="sm"
            onClick={() => handleToggleFlag(row.id)}
            title={row.status === 'enabled' ? 'Desativar' : 'Ativar'}
          >
            {row.status === 'enabled' ? <ToggleRight className="w-5 h-5" /> : <ToggleLeft className="w-5 h-5" />}
          </Button>
          <Dropdown
            trigger={
              <Button variant="ghost" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
            }
            items={[
              { label: 'Ver Detalhes', icon: <Eye className="w-4 h-4" />, onClick: () => { setSelectedFlag(row); setShowDetailModal(true); } },
              { label: 'Editar', icon: <Edit className="w-4 h-4" />, onClick: () => handleEditFlag(row) },
              { label: 'Copiar Key', icon: <Copy className="w-4 h-4" />, onClick: () => navigator.clipboard.writeText(row.key) },
              { label: 'Excluir', icon: <Trash2 className="w-4 h-4" />, danger: true, onClick: () => handleDeleteFlag(row.id) },
            ]}
          />
        </div>
      ),
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Feature Flags
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie flags de funcionalidades, experimentos e rollouts graduais
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Sincronizar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setShowNewModal(true)}>
              Nova Flag
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Flags"
              value={stats.total}
              icon={<Flag className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Ativas"
              value={stats.enabled}
              icon={<CheckCircle className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Rollout Gradual"
              value={stats.gradual}
              icon={<Percent className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Inativas"
              value={stats.disabled}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Experimentos"
              value={stats.experiments}
              icon={<Zap className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">Todas</TabsTrigger>
            <TabsTrigger value="enabled">Ativas</TabsTrigger>
            <TabsTrigger value="gradual">Gradual</TabsTrigger>
            <TabsTrigger value="disabled">Inativas</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Filters & Table */}
        <Card>
          <CardHeader
            title="Lista de Feature Flags"
            action={
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar flags..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todas Categorias' },
                    { value: 'feature', label: 'Feature' },
                    { value: 'experiment', label: 'Experimento' },
                    { value: 'ops', label: 'Operacional' },
                    { value: 'release', label: 'Release' },
                  ]}
                  value={categoryFilter}
                  onChange={setCategoryFilter}
                  className="w-40"
                />
              </div>
            }
          />
          <CardBody className="p-0">
            {filteredFlags.length > 0 ? (
              <DataTable
                columns={columns}
                data={filteredFlags}
                onRowClick={(row) => { setSelectedFlag(row); setShowDetailModal(true); }}
              />
            ) : (
              <EmptyState
                icon={<Flag className="w-12 h-12" />}
                title="Nenhuma flag encontrada"
                description="Não há feature flags que correspondam aos filtros."
                action={{
                  label: 'Nova Flag',
                  onClick: () => setShowNewModal(true),
                }}
              />
            )}
          </CardBody>
        </Card>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedFlag?.name || ''}
          size="lg"
        >
          {selectedFlag && (
            <div className="space-y-6">
              {/* Status e Key */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge variant={statusConfig[selectedFlag.status].variant} size="lg">
                    {statusConfig[selectedFlag.status].label}
                  </Badge>
                  <Badge variant={categoryConfig[selectedFlag.category].variant}>
                    {categoryConfig[selectedFlag.category].label}
                  </Badge>
                </div>
                <Button variant="outline" size="sm" leftIcon={<Copy className="w-4 h-4" />} onClick={() => navigator.clipboard.writeText(selectedFlag.key)}>
                  Copiar Key
                </Button>
              </div>

              {/* Key e Description */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Code className="w-4 h-4 text-text-muted" />
                  <span className="font-mono text-accent-primary">{selectedFlag.key}</span>
                </div>
                <p className="text-text-secondary">{selectedFlag.description}</p>
              </div>

              {/* Configuration */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Tipo</h4>
                  <p className="font-medium">
                    {selectedFlag.type === 'boolean' && 'Boolean (Liga/Desliga)'}
                    {selectedFlag.type === 'percentage' && 'Rollout Percentual'}
                    {selectedFlag.type === 'user_list' && 'Lista de Usuários'}
                    {selectedFlag.type === 'tenant_list' && 'Lista de Tenants'}
                  </p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Ambiente</h4>
                  <span className={`font-medium ${environmentConfig[selectedFlag.environment].color}`}>
                    {environmentConfig[selectedFlag.environment].label}
                  </span>
                </div>
              </div>

              {/* Percentage Rollout */}
              {selectedFlag.type === 'percentage' && selectedFlag.percentage !== undefined && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-text-secondary">Rollout Percentual</h4>
                    <span className="text-xl font-bold text-accent-primary">{selectedFlag.percentage}%</span>
                  </div>
                  <Progress value={selectedFlag.percentage} variant="gradient" />
                </div>
              )}

              {/* Tenant List */}
              {selectedFlag.type === 'tenant_list' && selectedFlag.enabledForTenants && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-3">Tenants Habilitados</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedFlag.enabledForTenants.map((tenant) => (
                      <Badge key={tenant} variant="primary">
                        <Building2 className="w-3 h-3 mr-1" />
                        {tenant}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Tags */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedFlag.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">{tag}</Badge>
                  ))}
                </div>
              </div>

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2 text-text-secondary">
                  <Calendar className="w-4 h-4" />
                  Criado em: {new Date(selectedFlag.createdAt).toLocaleDateString('pt-BR')}
                </div>
                <div className="flex items-center gap-2 text-text-secondary">
                  <Clock className="w-4 h-4" />
                  Atualizado em: {new Date(selectedFlag.updatedAt).toLocaleDateString('pt-BR')}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fechar
                </Button>
                <Button
                  variant={selectedFlag.status === 'enabled' ? 'danger' : 'success'}
                  leftIcon={selectedFlag.status === 'enabled' ? <ToggleLeft className="w-4 h-4" /> : <ToggleRight className="w-4 h-4" />}
                >
                  {selectedFlag.status === 'enabled' ? 'Desativar' : 'Ativar'}
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New Flag Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Nova Feature Flag"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Nome"
                placeholder="Ex: Novo Dashboard"
                required
              />
              <Input
                label="Key"
                placeholder="Ex: new_dashboard"
                required
              />
            </div>
            <Textarea
              label="Descrição"
              placeholder="Descreva a funcionalidade desta flag..."
              rows={2}
            />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo"
                options={[
                  { value: 'boolean', label: 'Boolean (Liga/Desliga)' },
                  { value: 'percentage', label: 'Rollout Percentual' },
                  { value: 'user_list', label: 'Lista de Usuários' },
                  { value: 'tenant_list', label: 'Lista de Tenants' },
                ]}
                value={newFlagType}
                onChange={(value) => setNewFlagType(value)}
                required
              />
              <Select
                label="Categoria"
                options={[
                  { value: 'feature', label: 'Feature' },
                  { value: 'experiment', label: 'Experimento' },
                  { value: 'ops', label: 'Operacional' },
                  { value: 'release', label: 'Release' },
                ]}
                value={newFlagCategory}
                onChange={(value) => setNewFlagCategory(value)}
                required
              />
            </div>
            <Select
              label="Ambiente"
              options={[
                { value: 'development', label: 'Desenvolvimento' },
                { value: 'staging', label: 'Staging' },
                { value: 'production', label: 'Produção' },
                { value: 'all', label: 'Todos' },
              ]}
              value={newFlagEnvironment}
              onChange={(value) => setNewFlagEnvironment(value)}
              required
            />
            <Input
              label="Tags"
              placeholder="Separe por vírgulas: beta, feature, ui"
            />
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                Criar Flag
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
