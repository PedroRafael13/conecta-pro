'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileJson,
  Settings,
  Copy,
  Download,
  Upload,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  Filter,
  Code,
  Building2,
  Layers,
  RefreshCw,
  Play,
  Pause,
  FileText,
  Zap,
  Shield,
  Globe,
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
} from '@/design-system/components';

// Types
interface ConfigTemplate {
  id: string;
  name: string;
  description: string;
  category: 'tenant' | 'system' | 'integration' | 'security' | 'notification';
  status: 'active' | 'draft' | 'deprecated';
  version: string;
  schema: object;
  defaults: object;
  appliedTo: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  tags: string[];
}

// Mock data
const mockTemplates: ConfigTemplate[] = [
  {
    id: '1',
    name: 'Tenant Padrão - Starter',
    description: 'Configuração inicial para novos tenants no plano Starter',
    category: 'tenant',
    status: 'active',
    version: '2.1.0',
    schema: {},
    defaults: {},
    appliedTo: 45,
    createdAt: '2025-08-15',
    updatedAt: '2026-01-10',
    createdBy: 'admin@conectaplus.com.br',
    tags: ['starter', 'default', 'tenant'],
  },
  {
    id: '2',
    name: 'Tenant Padrão - Enterprise',
    description: 'Configuração completa para tenants Enterprise com todos os módulos',
    category: 'tenant',
    status: 'active',
    version: '3.0.0',
    schema: {},
    defaults: {},
    appliedTo: 12,
    createdAt: '2025-06-20',
    updatedAt: '2026-01-12',
    createdBy: 'admin@conectaplus.com.br',
    tags: ['enterprise', 'full', 'tenant'],
  },
  {
    id: '3',
    name: 'Integração WhatsApp Business',
    description: 'Template de configuração para integração com WhatsApp Business API',
    category: 'integration',
    status: 'active',
    version: '1.5.0',
    schema: {},
    defaults: {},
    appliedTo: 28,
    createdAt: '2025-09-01',
    updatedAt: '2025-12-15',
    createdBy: 'integrations@conectaplus.com.br',
    tags: ['whatsapp', 'messaging', 'integration'],
  },
  {
    id: '4',
    name: 'Políticas de Segurança LGPD',
    description: 'Configurações de compliance com LGPD para tratamento de dados',
    category: 'security',
    status: 'active',
    version: '2.0.0',
    schema: {},
    defaults: {},
    appliedTo: 52,
    createdAt: '2025-03-10',
    updatedAt: '2025-11-20',
    createdBy: 'security@conectaplus.com.br',
    tags: ['lgpd', 'compliance', 'security'],
  },
  {
    id: '5',
    name: 'Notificações - Email Transacional',
    description: 'Templates e configurações de emails transacionais',
    category: 'notification',
    status: 'active',
    version: '1.8.0',
    schema: {},
    defaults: {},
    appliedTo: 60,
    createdAt: '2025-04-05',
    updatedAt: '2026-01-05',
    createdBy: 'notifications@conectaplus.com.br',
    tags: ['email', 'transactional', 'notification'],
  },
  {
    id: '6',
    name: 'Sistema - Cache Redis',
    description: 'Configurações de cache distribuído com Redis',
    category: 'system',
    status: 'active',
    version: '1.2.0',
    schema: {},
    defaults: {},
    appliedTo: 1,
    createdAt: '2024-12-01',
    updatedAt: '2025-10-15',
    createdBy: 'devops@conectaplus.com.br',
    tags: ['cache', 'redis', 'system'],
  },
  {
    id: '7',
    name: 'Tenant Padrão - Professional (Beta)',
    description: 'Nova configuração para plano Professional em teste',
    category: 'tenant',
    status: 'draft',
    version: '1.0.0-beta',
    schema: {},
    defaults: {},
    appliedTo: 0,
    createdAt: '2026-01-10',
    updatedAt: '2026-01-14',
    createdBy: 'admin@conectaplus.com.br',
    tags: ['professional', 'beta', 'tenant'],
  },
  {
    id: '8',
    name: 'Integração Pix Legado',
    description: 'Template de integração Pix - versão descontinuada',
    category: 'integration',
    status: 'deprecated',
    version: '0.9.0',
    schema: {},
    defaults: {},
    appliedTo: 5,
    createdAt: '2024-06-01',
    updatedAt: '2025-06-01',
    createdBy: 'finance@conectaplus.com.br',
    tags: ['pix', 'legacy', 'deprecated'],
  },
];

const categoryConfig: Record<ConfigTemplate['category'], { label: string; variant: 'primary' | 'success' | 'warning' | 'info' | 'danger'; icon: typeof Settings }> = {
  tenant: { label: 'Tenant', variant: 'primary', icon: Building2 },
  system: { label: 'Sistema', variant: 'info', icon: Settings },
  integration: { label: 'Integração', variant: 'success', icon: Globe },
  security: { label: 'Segurança', variant: 'danger', icon: Shield },
  notification: { label: 'Notificação', variant: 'warning', icon: Zap },
};

const statusConfig: Record<ConfigTemplate['status'], { label: string; variant: 'success' | 'warning' | 'secondary' }> = {
  active: { label: 'Ativo', variant: 'success' },
  draft: { label: 'Rascunho', variant: 'warning' },
  deprecated: { label: 'Descontinuado', variant: 'secondary' },
};

export default function ConfigTemplatesPage() {
  const [templates] = useState<ConfigTemplate[]>(mockTemplates);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<ConfigTemplate | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  // Stats
  const stats = {
    total: templates.length,
    active: templates.filter(t => t.status === 'active').length,
    draft: templates.filter(t => t.status === 'draft').length,
    totalApplied: templates.reduce((acc, t) => acc + t.appliedTo, 0),
  };

  // Filter
  const filteredTemplates = templates.filter(template => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || template.category === categoryFilter;
    const matchesTab = activeTab === 'all' || template.status === activeTab;
    return matchesSearch && matchesCategory && matchesTab;
  });

  const columns = [
    {
      key: 'template',
      header: 'Template',
      render: (row: ConfigTemplate) => {
        const CategoryIcon = categoryConfig[row.category].icon;
        return (
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-${categoryConfig[row.category].variant}/20`}>
              <CategoryIcon className={`w-5 h-5 text-${categoryConfig[row.category].variant}`} />
            </div>
            <div>
              <p className="font-medium">{row.name}</p>
              <p className="text-xs text-text-secondary line-clamp-1">{row.description}</p>
            </div>
          </div>
        );
      },
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row: ConfigTemplate) => (
        <Badge variant={categoryConfig[row.category].variant}>
          {categoryConfig[row.category].label}
        </Badge>
      ),
    },
    {
      key: 'version',
      header: 'Versão',
      render: (row: ConfigTemplate) => (
        <span className="font-mono text-sm">{row.version}</span>
      ),
    },
    {
      key: 'appliedTo',
      header: 'Aplicado em',
      render: (row: ConfigTemplate) => (
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-text-secondary" />
          <span>{row.appliedTo} {row.appliedTo === 1 ? 'tenant' : 'tenants'}</span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: ConfigTemplate) => (
        <Badge variant={statusConfig[row.status].variant}>
          {statusConfig[row.status].label}
        </Badge>
      ),
    },
    {
      key: 'updatedAt',
      header: 'Atualizado',
      render: (row: ConfigTemplate) => (
        <span className="text-text-secondary">
          {new Date(row.updatedAt).toLocaleDateString('pt-BR')}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row: ConfigTemplate) => (
        <Dropdown
          trigger={
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          }
          items={[
            { label: 'Ver Detalhes', icon: <Eye className="w-4 h-4" />, onClick: () => { setSelectedTemplate(row); setShowDetailModal(true); } },
            { label: 'Editar', icon: <Edit className="w-4 h-4" />, onClick: () => {} },
            { label: 'Duplicar', icon: <Copy className="w-4 h-4" />, onClick: () => {} },
            { label: 'Exportar JSON', icon: <Download className="w-4 h-4" />, onClick: () => {} },
            { label: 'Aplicar a Tenant', icon: <Play className="w-4 h-4" />, onClick: () => {} },
            { label: row.status === 'active' ? 'Descontinuar' : 'Ativar', icon: row.status === 'active' ? <Pause className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />, onClick: () => {} },
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
              Templates de Configuração
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie templates de configuração para tenants, integrações e sistema
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<Upload className="w-4 h-4" />}>
              Importar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setShowNewModal(true)}>
              Novo Template
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Templates"
              value={stats.total}
              icon={<FileJson className="w-6 h-6" />}
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
              title="Em Rascunho"
              value={stats.draft}
              icon={<FileText className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Total de Aplicações"
              value={stats.totalApplied}
              icon={<Layers className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">Todos</TabsTrigger>
            <TabsTrigger value="active">Ativos</TabsTrigger>
            <TabsTrigger value="draft">Rascunhos</TabsTrigger>
            <TabsTrigger value="deprecated">Descontinuados</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Filters & Table */}
        <Card>
          <CardHeader
            title="Lista de Templates"
            action={
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar templates..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todas Categorias' },
                    { value: 'tenant', label: 'Tenant' },
                    { value: 'system', label: 'Sistema' },
                    { value: 'integration', label: 'Integração' },
                    { value: 'security', label: 'Segurança' },
                    { value: 'notification', label: 'Notificação' },
                  ]}
                  value={categoryFilter}
                  onChange={setCategoryFilter}
                  className="w-40"
                />
              </div>
            }
          />
          <CardBody className="p-0">
            {filteredTemplates.length > 0 ? (
              <DataTable
                columns={columns}
                data={filteredTemplates}
                onRowClick={(row) => { setSelectedTemplate(row); setShowDetailModal(true); }}
              />
            ) : (
              <EmptyState
                icon={<FileJson className="w-12 h-12" />}
                title="Nenhum template encontrado"
                description="Não há templates que correspondam aos filtros."
                action={{
                  label: 'Novo Template',
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
          title={selectedTemplate?.name || ''}
          size="lg"
        >
          {selectedTemplate && (
            <div className="space-y-6">
              {/* Status e Versão */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge variant={statusConfig[selectedTemplate.status].variant} size="lg">
                    {statusConfig[selectedTemplate.status].label}
                  </Badge>
                  <Badge variant={categoryConfig[selectedTemplate.category].variant}>
                    {categoryConfig[selectedTemplate.category].label}
                  </Badge>
                </div>
                <span className="font-mono text-lg">{selectedTemplate.version}</span>
              </div>

              {/* Description */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-text-secondary">{selectedTemplate.description}</p>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-secondary">Aplicado em</span>
                    <span className="text-xl font-bold">{selectedTemplate.appliedTo} tenants</span>
                  </div>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-secondary">Criado por</span>
                    <span className="text-sm">{selectedTemplate.createdBy}</span>
                  </div>
                </div>
              </div>

              {/* Tags */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">{tag}</Badge>
                  ))}
                </div>
              </div>

              {/* JSON Preview */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-text-secondary">Schema Preview</h4>
                  <Button variant="ghost" size="sm" leftIcon={<Copy className="w-4 h-4" />}>
                    Copiar
                  </Button>
                </div>
                <pre className="text-xs font-mono text-text-secondary bg-bg-elevated p-3 rounded overflow-auto max-h-40">
{`{
  "tenant": {
    "maxUsers": 100,
    "maxStorage": "50GB",
    "features": ["crm", "financial", "hr"]
  },
  "modules": {
    "crm": { "enabled": true },
    "financial": { "enabled": true },
    "hr": { "enabled": true }
  }
}`}
                </pre>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fechar
                </Button>
                <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
                  Exportar
                </Button>
                <Button variant="primary" leftIcon={<Play className="w-4 h-4" />}>
                  Aplicar
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New Template Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Novo Template"
          size="lg"
        >
          <div className="space-y-4">
            <Input
              label="Nome do Template"
              placeholder="Ex: Tenant Padrão - Premium"
              required
            />
            <Textarea
              label="Descrição"
              placeholder="Descreva o propósito deste template..."
              rows={2}
            />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Categoria"
                options={[
                  { value: 'tenant', label: 'Tenant' },
                  { value: 'system', label: 'Sistema' },
                  { value: 'integration', label: 'Integração' },
                  { value: 'security', label: 'Segurança' },
                  { value: 'notification', label: 'Notificação' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
              <Input
                label="Versão"
                placeholder="Ex: 1.0.0"
                required
              />
            </div>
            <Textarea
              label="Schema JSON"
              placeholder='{"key": "value"}'
              rows={6}
            />
            <Input
              label="Tags"
              placeholder="Separe por vírgulas: premium, tenant, full"
            />
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                Criar Template
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
