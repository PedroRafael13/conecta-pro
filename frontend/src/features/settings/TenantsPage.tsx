'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Users,
  Settings,
  CreditCard,
  Calendar,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  Shield,
  Zap,
  Database,
  Globe,
  Mail,
  Phone,
  MapPin,
  Clock,
  TrendingUp,
  Package,
  ToggleLeft,
  ToggleRight,
  RefreshCw,
  Download,
  Upload,
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
  TabsContent,
  Progress,
} from '@/design-system/components';

// Types
interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: 'starter' | 'professional' | 'enterprise' | 'custom';
  status: 'active' | 'suspended' | 'trial' | 'cancelled';
  contact: {
    name: string;
    email: string;
    phone: string;
  };
  address: {
    city: string;
    state: string;
  };
  metrics: {
    users: number;
    maxUsers: number;
    storage: number;
    maxStorage: number;
    apiCalls: number;
    maxApiCalls: number;
  };
  features: string[];
  createdAt: string;
  trialEndsAt: string | null;
  billingCycle: 'monthly' | 'yearly';
  mrr: number;
}

// Mock data
const mockTenants: Tenant[] = [
  {
    id: '1',
    name: 'Condomínio Solar das Flores',
    slug: 'solar-flores',
    plan: 'professional',
    status: 'active',
    contact: {
      name: 'José Silva',
      email: 'jose@solarflores.com.br',
      phone: '(11) 99999-1234',
    },
    address: {
      city: 'São Paulo',
      state: 'SP',
    },
    metrics: {
      users: 45,
      maxUsers: 100,
      storage: 12.5,
      maxStorage: 50,
      apiCalls: 45000,
      maxApiCalls: 100000,
    },
    features: ['crm', 'financial', 'hr', 'operations', 'ai_basic'],
    createdAt: '2024-03-15',
    trialEndsAt: null,
    billingCycle: 'yearly',
    mrr: 2500,
  },
  {
    id: '2',
    name: 'Edifício Corporate Tower',
    slug: 'corporate-tower',
    plan: 'enterprise',
    status: 'active',
    contact: {
      name: 'Maria Santos',
      email: 'maria@corporatetower.com.br',
      phone: '(11) 97777-4321',
    },
    address: {
      city: 'São Paulo',
      state: 'SP',
    },
    metrics: {
      users: 180,
      maxUsers: 500,
      storage: 85.3,
      maxStorage: 200,
      apiCalls: 280000,
      maxApiCalls: 500000,
    },
    features: ['crm', 'financial', 'hr', 'operations', 'ai_advanced', 'integrations', 'api_access'],
    createdAt: '2023-08-20',
    trialEndsAt: null,
    billingCycle: 'yearly',
    mrr: 8500,
  },
  {
    id: '3',
    name: 'Shopping Center Norte',
    slug: 'shopping-norte',
    plan: 'enterprise',
    status: 'active',
    contact: {
      name: 'Pedro Lima',
      email: 'pedro@shoppingnorte.com.br',
      phone: '(11) 95555-9876',
    },
    address: {
      city: 'São Paulo',
      state: 'SP',
    },
    metrics: {
      users: 320,
      maxUsers: 1000,
      storage: 156.8,
      maxStorage: 500,
      apiCalls: 520000,
      maxApiCalls: 1000000,
    },
    features: ['crm', 'financial', 'hr', 'operations', 'ai_advanced', 'integrations', 'api_access', 'white_label'],
    createdAt: '2022-11-10',
    trialEndsAt: null,
    billingCycle: 'yearly',
    mrr: 15000,
  },
  {
    id: '4',
    name: 'Residencial Primavera',
    slug: 'residencial-primavera',
    plan: 'starter',
    status: 'trial',
    contact: {
      name: 'Ana Costa',
      email: 'ana@primavera.com.br',
      phone: '(21) 98888-5432',
    },
    address: {
      city: 'Rio de Janeiro',
      state: 'RJ',
    },
    metrics: {
      users: 8,
      maxUsers: 20,
      storage: 1.2,
      maxStorage: 10,
      apiCalls: 5000,
      maxApiCalls: 20000,
    },
    features: ['crm', 'financial'],
    createdAt: '2026-01-05',
    trialEndsAt: '2026-02-05',
    billingCycle: 'monthly',
    mrr: 0,
  },
  {
    id: '5',
    name: 'Indústria Metalúrgica ABC',
    slug: 'metalurgica-abc',
    plan: 'professional',
    status: 'suspended',
    contact: {
      name: 'Carlos Mendes',
      email: 'carlos@metalurgicaabc.com.br',
      phone: '(11) 94444-3210',
    },
    address: {
      city: 'Santo André',
      state: 'SP',
    },
    metrics: {
      users: 65,
      maxUsers: 100,
      storage: 28.4,
      maxStorage: 50,
      apiCalls: 0,
      maxApiCalls: 100000,
    },
    features: ['crm', 'financial', 'hr', 'operations'],
    createdAt: '2024-06-22',
    trialEndsAt: null,
    billingCycle: 'monthly',
    mrr: 3200,
  },
];

const planConfig: Record<Tenant['plan'], { label: string; variant: 'primary' | 'success' | 'warning' | 'info' }> = {
  starter: { label: 'Starter', variant: 'primary' },
  professional: { label: 'Professional', variant: 'info' },
  enterprise: { label: 'Enterprise', variant: 'success' },
  custom: { label: 'Custom', variant: 'warning' },
};

const statusConfig: Record<Tenant['status'], { label: string; variant: 'success' | 'warning' | 'danger' | 'info' }> = {
  active: { label: 'Ativo', variant: 'success' },
  suspended: { label: 'Suspenso', variant: 'danger' },
  trial: { label: 'Trial', variant: 'warning' },
  cancelled: { label: 'Cancelado', variant: 'danger' },
};

const featureLabels: Record<string, string> = {
  crm: 'CRM',
  financial: 'Financeiro',
  hr: 'RH',
  operations: 'Operações',
  ai_basic: 'IA Básica',
  ai_advanced: 'IA Avançada',
  integrations: 'Integrações',
  api_access: 'API Access',
  white_label: 'White Label',
};

export default function TenantsPage() {
  const [tenants] = useState<Tenant[]>(mockTenants);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  // Stats
  const stats = {
    total: tenants.length,
    active: tenants.filter(t => t.status === 'active').length,
    trial: tenants.filter(t => t.status === 'trial').length,
    suspended: tenants.filter(t => t.status === 'suspended').length,
    totalMRR: tenants.reduce((acc, t) => acc + t.mrr, 0),
    totalUsers: tenants.reduce((acc, t) => acc + t.metrics.users, 0),
  };

  // Filter
  const filteredTenants = tenants.filter(tenant => {
    const matchesSearch =
      tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tenant.slug.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tenant.contact.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || tenant.status === statusFilter;
    const matchesTab = activeTab === 'all' || tenant.status === activeTab;
    return matchesSearch && matchesStatus && matchesTab;
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  const columns = [
    {
      key: 'name',
      header: 'Tenant',
      render: (row: Tenant) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
            <Building2 className="w-5 h-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium">{row.name}</p>
            <p className="text-xs text-text-secondary">{row.slug}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'plan',
      header: 'Plano',
      render: (row: Tenant) => (
        <Badge variant={planConfig[row.plan].variant}>
          {planConfig[row.plan].label}
        </Badge>
      ),
    },
    {
      key: 'users',
      header: 'Usuários',
      render: (row: Tenant) => (
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-text-secondary" />
          <span>{row.metrics.users} / {row.metrics.maxUsers}</span>
        </div>
      ),
    },
    {
      key: 'mrr',
      header: 'MRR',
      render: (row: Tenant) => (
        <span className="font-semibold text-success">
          {row.mrr > 0 ? formatCurrency(row.mrr) : '-'}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: Tenant) => (
        <Badge variant={statusConfig[row.status].variant}>
          {statusConfig[row.status].label}
        </Badge>
      ),
    },
    {
      key: 'createdAt',
      header: 'Criado em',
      render: (row: Tenant) => (
        <span className="text-text-secondary">
          {new Date(row.createdAt).toLocaleDateString('pt-BR')}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row: Tenant) => (
        <Dropdown
          trigger={
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          }
          items={[
            { label: 'Ver Detalhes', icon: <Eye className="w-4 h-4" />, onClick: () => { setSelectedTenant(row); setShowDetailModal(true); } },
            { label: 'Editar', icon: <Edit className="w-4 h-4" />, onClick: () => {} },
            { label: 'Gerenciar Features', icon: <Zap className="w-4 h-4" />, onClick: () => {} },
            { label: row.status === 'active' ? 'Suspender' : 'Reativar', icon: row.status === 'active' ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />, onClick: () => {} },
            { label: 'Excluir', icon: <Trash2 className="w-4 h-4" />, danger: true, onClick: () => {} },
          ]}
        />
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
              Gestão de Tenants
            </h1>
            <p className="text-text-secondary mt-1">
              Administre organizações, planos e recursos do sistema multi-tenant
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setShowNewModal(true)}>
              Novo Tenant
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Tenants"
              value={stats.total}
              icon={<Building2 className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Ativos"
              value={stats.active}
              icon={<CheckCircle className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Em Trial"
              value={stats.trial}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="MRR Total"
              value={formatCurrency(stats.totalMRR)}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="success"
              change={12}
              changeLabel="vs mês anterior"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Total de Usuários"
              value={stats.totalUsers.toLocaleString()}
              icon={<Users className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">Todos</TabsTrigger>
            <TabsTrigger value="active">Ativos</TabsTrigger>
            <TabsTrigger value="trial">Trial</TabsTrigger>
            <TabsTrigger value="suspended">Suspensos</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Filters & Table */}
        <Card>
          <CardHeader
            title="Lista de Tenants"
            action={
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar tenants..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todos os Status' },
                    { value: 'active', label: 'Ativo' },
                    { value: 'trial', label: 'Trial' },
                    { value: 'suspended', label: 'Suspenso' },
                  ]}
                  value={statusFilter}
                  onChange={setStatusFilter}
                  className="w-40"
                />
              </div>
            }
          />
          <CardBody className="p-0">
            {filteredTenants.length > 0 ? (
              <DataTable
                columns={columns}
                data={filteredTenants}
                onRowClick={(row) => { setSelectedTenant(row); setShowDetailModal(true); }}
              />
            ) : (
              <EmptyState
                icon={<Building2 className="w-12 h-12" />}
                title="Nenhum tenant encontrado"
                description="Não há tenants que correspondam aos filtros selecionados."
                action={{
                  label: 'Novo Tenant',
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
          title={selectedTenant?.name || ''}
          size="lg"
        >
          {selectedTenant && (
            <div className="space-y-6">
              {/* Status e Plano */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge variant={statusConfig[selectedTenant.status].variant} size="lg">
                    {statusConfig[selectedTenant.status].label}
                  </Badge>
                  <Badge variant={planConfig[selectedTenant.plan].variant}>
                    {planConfig[selectedTenant.plan].label}
                  </Badge>
                </div>
                <span className="text-2xl font-bold text-success">
                  {formatCurrency(selectedTenant.mrr)}/mês
                </span>
              </div>

              {/* Métricas de Uso */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-text-secondary">Usuários</span>
                    <Users className="w-4 h-4 text-text-muted" />
                  </div>
                  <p className="text-xl font-bold">{selectedTenant.metrics.users} / {selectedTenant.metrics.maxUsers}</p>
                  <Progress value={(selectedTenant.metrics.users / selectedTenant.metrics.maxUsers) * 100} size="sm" className="mt-2" />
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-text-secondary">Storage</span>
                    <Database className="w-4 h-4 text-text-muted" />
                  </div>
                  <p className="text-xl font-bold">{selectedTenant.metrics.storage} / {selectedTenant.metrics.maxStorage} GB</p>
                  <Progress value={(selectedTenant.metrics.storage / selectedTenant.metrics.maxStorage) * 100} size="sm" className="mt-2" />
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-text-secondary">API Calls</span>
                    <Globe className="w-4 h-4 text-text-muted" />
                  </div>
                  <p className="text-xl font-bold">{(selectedTenant.metrics.apiCalls / 1000).toFixed(0)}k / {(selectedTenant.metrics.maxApiCalls / 1000).toFixed(0)}k</p>
                  <Progress value={(selectedTenant.metrics.apiCalls / selectedTenant.metrics.maxApiCalls) * 100} size="sm" className="mt-2" />
                </div>
              </div>

              {/* Contato */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Contato Principal</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-text-muted" />
                    <span>{selectedTenant.contact.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-text-muted" />
                    <span>{selectedTenant.contact.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-text-muted" />
                    <span>{selectedTenant.contact.phone}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-text-muted" />
                    <span>{selectedTenant.address.city}, {selectedTenant.address.state}</span>
                  </div>
                </div>
              </div>

              {/* Features */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Features Habilitadas</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedTenant.features.map((feature) => (
                    <Badge key={feature} variant="primary">
                      {featureLabels[feature] || feature}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Trial Info */}
              {selectedTenant.trialEndsAt && (
                <div className="p-4 bg-warning/10 border border-warning/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-warning" />
                    <span className="font-medium text-warning">
                      Trial expira em {new Date(selectedTenant.trialEndsAt).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fechar
                </Button>
                <Button variant="outline" leftIcon={<Settings className="w-4 h-4" />}>
                  Configurações
                </Button>
                <Button variant="primary" leftIcon={<Edit className="w-4 h-4" />}>
                  Editar
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New Tenant Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Novo Tenant"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Nome da Organização"
                placeholder="Ex: Condomínio Solar"
                required
              />
              <Input
                label="Slug"
                placeholder="Ex: cond-solar"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Plano"
                options={[
                  { value: 'starter', label: 'Starter' },
                  { value: 'professional', label: 'Professional' },
                  { value: 'enterprise', label: 'Enterprise' },
                  { value: 'custom', label: 'Custom' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
              <Select
                label="Ciclo de Cobrança"
                options={[
                  { value: 'monthly', label: 'Mensal' },
                  { value: 'yearly', label: 'Anual' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Nome do Contato"
                placeholder="Nome do responsável"
                required
              />
              <Input
                label="Email"
                type="email"
                placeholder="email@empresa.com.br"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Telefone"
                placeholder="(11) 99999-9999"
              />
              <Input
                label="Cidade/Estado"
                placeholder="São Paulo, SP"
              />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                Criar Tenant
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
