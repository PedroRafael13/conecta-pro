'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  FileText,
  Mail,
  MessageSquare,
  Bell,
  Smartphone,
  Edit2,
  Trash2,
  Copy,
  Eye,
  MoreHorizontal,
  CheckCircle2,
  XCircle,
  Clock,
  Tag,
  Code,
  Send,
  AlertTriangle,
  Settings,
  Zap,
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
  Select,
  Textarea,
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

// Types
interface NotificationTemplate {
  id: string;
  name: string;
  description: string;
  channel: 'email' | 'sms' | 'whatsapp' | 'push' | 'all';
  category: 'security' | 'financial' | 'hr' | 'operations' | 'marketing' | 'system';
  subject: string;
  body: string;
  variables: string[];
  status: 'active' | 'inactive' | 'draft';
  usageCount: number;
  lastUsed: string | null;
  createdAt: string;
  updatedAt: string;
}

// Mock Data
const templates: NotificationTemplate[] = [
  {
    id: '1',
    name: 'Alerta de Ocorrência Crítica',
    description: 'Notificação enviada quando uma ocorrência crítica é registrada',
    channel: 'all',
    category: 'security',
    subject: '[URGENTE] Ocorrência Crítica - {{local}}',
    body: 'Uma ocorrência crítica foi registrada em {{local}}.\n\nDetalhes:\n- Tipo: {{tipo}}\n- Data/Hora: {{data_hora}}\n- Responsável: {{responsavel}}\n\nAcesse o sistema para mais detalhes.',
    variables: ['local', 'tipo', 'data_hora', 'responsavel'],
    status: 'active',
    usageCount: 156,
    lastUsed: '2026-01-15',
    createdAt: '2025-06-01',
    updatedAt: '2026-01-10',
  },
  {
    id: '2',
    name: 'Fatura Vencendo',
    description: 'Lembrete de fatura próxima ao vencimento',
    channel: 'email',
    category: 'financial',
    subject: 'Lembrete: Fatura #{{numero}} vence em {{dias}} dias',
    body: 'Prezado(a) {{cliente}},\n\nInformamos que a fatura #{{numero}} no valor de {{valor}} vence em {{data_vencimento}}.\n\nPor favor, providencie o pagamento para evitar juros e multas.\n\nAtenciosamente,\nEquipe Financeira',
    variables: ['cliente', 'numero', 'valor', 'data_vencimento', 'dias'],
    status: 'active',
    usageCount: 423,
    lastUsed: '2026-01-15',
    createdAt: '2025-01-15',
    updatedAt: '2025-12-01',
  },
  {
    id: '3',
    name: 'Bem-vindo ao Sistema',
    description: 'Email de boas-vindas para novos colaboradores',
    channel: 'email',
    category: 'hr',
    subject: 'Bem-vindo(a) à {{empresa}}!',
    body: 'Olá {{nome}},\n\nÉ com grande prazer que damos as boas-vindas a você!\n\nSeus dados de acesso:\n- Usuário: {{usuario}}\n- Senha temporária: {{senha_temp}}\n\nPor favor, altere sua senha no primeiro acesso.\n\nQualquer dúvida, entre em contato com o RH.',
    variables: ['nome', 'empresa', 'usuario', 'senha_temp'],
    status: 'active',
    usageCount: 87,
    lastUsed: '2026-01-10',
    createdAt: '2025-03-01',
    updatedAt: '2025-11-15',
  },
  {
    id: '4',
    name: 'Ponto Irregular',
    description: 'Alerta de registro de ponto irregular',
    channel: 'push',
    category: 'hr',
    subject: 'Ponto Irregular Detectado',
    body: 'Atenção! Um registro de ponto irregular foi detectado para {{colaborador}} em {{data}}. Motivo: {{motivo}}. Verifique no sistema.',
    variables: ['colaborador', 'data', 'motivo'],
    status: 'active',
    usageCount: 234,
    lastUsed: '2026-01-14',
    createdAt: '2025-07-20',
    updatedAt: '2025-10-05',
  },
  {
    id: '5',
    name: 'Promoção de Serviços',
    description: 'Template para campanhas de marketing',
    channel: 'whatsapp',
    category: 'marketing',
    subject: 'Oferta Especial para Você!',
    body: 'Olá {{nome}}! Temos uma oferta especial de {{servico}} com {{desconto}}% de desconto. Válido até {{validade}}. Entre em contato para saber mais!',
    variables: ['nome', 'servico', 'desconto', 'validade'],
    status: 'draft',
    usageCount: 0,
    lastUsed: null,
    createdAt: '2026-01-05',
    updatedAt: '2026-01-05',
  },
];

const channelDistribution = [
  { name: 'Email', value: 45, color: '#3B82F6' },
  { name: 'Push', value: 25, color: '#10B981' },
  { name: 'WhatsApp', value: 18, color: '#25D366' },
  { name: 'SMS', value: 12, color: '#F59E0B' },
];

const usageByCategory = [
  { category: 'Segurança', count: 156 },
  { category: 'Financeiro', count: 423 },
  { category: 'RH', count: 321 },
  { category: 'Operacional', count: 187 },
  { category: 'Marketing', count: 45 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'active', label: 'Ativos' },
  { id: 'inactive', label: 'Inativos' },
  { id: 'draft', label: 'Rascunhos' },
];

const channelIcons = {
  email: Mail,
  sms: MessageSquare,
  whatsapp: Smartphone,
  push: Bell,
  all: Zap,
};

const channelLabels = {
  email: 'Email',
  sms: 'SMS',
  whatsapp: 'WhatsApp',
  push: 'Push',
  all: 'Todos',
};

const categoryColors = {
  security: 'danger',
  financial: 'warning',
  hr: 'info',
  operations: 'success',
  marketing: 'primary',
  system: 'secondary',
} as const;

const categoryLabels = {
  security: 'Segurança',
  financial: 'Financeiro',
  hr: 'RH',
  operations: 'Operacional',
  marketing: 'Marketing',
  system: 'Sistema',
};

const statusColors = {
  active: 'success',
  inactive: 'secondary',
  draft: 'warning',
} as const;

const statusLabels = {
  active: 'Ativo',
  inactive: 'Inativo',
  draft: 'Rascunho',
};

const columns: Column<NotificationTemplate>[] = [
  {
    key: 'name',
    header: 'Template',
    render: (row) => {
      const Icon = channelIcons[row.channel];
      return (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted line-clamp-1">{row.description}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'channel',
    header: 'Canal',
    render: (row) => <Badge variant="info">{channelLabels[row.channel]}</Badge>,
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => <Badge variant={categoryColors[row.category]}>{categoryLabels[row.category]}</Badge>,
  },
  {
    key: 'variables',
    header: 'Variáveis',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Code className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.variables.length}</span>
      </div>
    ),
  },
  {
    key: 'usageCount',
    header: 'Uso',
    render: (row) => <span className="text-sm font-medium">{row.usageCount}x</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => <Badge variant={statusColors[row.status]}>{statusLabels[row.status]}</Badge>,
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Visualizar">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Duplicar">
          <Copy className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function NotificationTemplatesPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<NotificationTemplate | null>(null);

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && template.status === activeTab;
  });

  // Stats
  const totalTemplates = templates.length;
  const activeTemplates = templates.filter((t) => t.status === 'active').length;
  const totalUsage = templates.reduce((acc, t) => acc + t.usageCount, 0);
  const avgVariables = (templates.reduce((acc, t) => acc + t.variables.length, 0) / templates.length).toFixed(1);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Templates de Notificação</h1>
            <p className="text-text-secondary mt-1">Gerencie modelos de mensagens e notificações</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Novo Template
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Templates" value={totalTemplates} icon={<FileText className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Templates Ativos" value={activeTemplates} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Total de Envios" value={totalUsage} icon={<Send className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Média de Variáveis" value={avgVariables} icon={<Code className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Distribuição por Canal</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={channelDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {channelDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {channelDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-text-muted">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Tag className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Uso por Categoria</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={usageByCategory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="category" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex items-center gap-3">
            <Input
              placeholder="Buscar templates..."
              leftIcon={<Search className="w-4 h-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
            <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
              Filtros
            </Button>
          </div>
        </div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredTemplates}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedTemplate(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Novo Template"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="secondary">Salvar Rascunho</Button>
              <Button variant="primary">Criar Template</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome do Template" placeholder="Ex: Alerta de Segurança" required />
            <Textarea label="Descrição" placeholder="Descreva quando este template deve ser usado..." rows={2} />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Canal"
                options={[
                  { value: 'email', label: 'Email' },
                  { value: 'sms', label: 'SMS' },
                  { value: 'whatsapp', label: 'WhatsApp' },
                  { value: 'push', label: 'Push Notification' },
                  { value: 'all', label: 'Todos os Canais' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Categoria"
                options={[
                  { value: 'security', label: 'Segurança' },
                  { value: 'financial', label: 'Financeiro' },
                  { value: 'hr', label: 'RH' },
                  { value: 'operations', label: 'Operacional' },
                  { value: 'marketing', label: 'Marketing' },
                  { value: 'system', label: 'Sistema' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <Input label="Assunto" placeholder="Ex: [ALERTA] {{tipo}} em {{local}}" />
            <div className="p-3 rounded-lg bg-bg-secondary">
              <p className="text-xs text-text-muted mb-2">Use variáveis no formato: {'{{nome_variavel}}'}</p>
              <Textarea label="Corpo da Mensagem" placeholder="Digite o conteúdo da notificação..." rows={6} />
            </div>
            <Input label="Variáveis (separadas por vírgula)" placeholder="nome, email, data, valor" />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={!!selectedTemplate}
          onClose={() => setSelectedTemplate(null)}
          title="Detalhes do Template"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedTemplate(null)}>
                Fechar
              </Button>
              <Button variant="secondary" leftIcon={<Copy className="w-4 h-4" />}>
                Duplicar
              </Button>
              <Button variant="primary" leftIcon={<Edit2 className="w-4 h-4" />}>
                Editar
              </Button>
            </>
          }
        >
          {selectedTemplate && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                {(() => {
                  const Icon = channelIcons[selectedTemplate.channel];
                  return (
                    <div className="p-3 rounded-xl bg-primary/10">
                      <Icon className="w-8 h-8 text-primary" />
                    </div>
                  );
                })()}
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-text-primary">{selectedTemplate.name}</h3>
                    <Badge variant={statusColors[selectedTemplate.status]}>{statusLabels[selectedTemplate.status]}</Badge>
                  </div>
                  <p className="text-text-secondary mt-1">{selectedTemplate.description}</p>
                  <div className="flex items-center gap-4 mt-3">
                    <Badge variant="info">{channelLabels[selectedTemplate.channel]}</Badge>
                    <Badge variant={categoryColors[selectedTemplate.category]}>{categoryLabels[selectedTemplate.category]}</Badge>
                  </div>
                </div>
              </div>

              {/* Subject */}
              <div className="p-4 rounded-lg border border-border">
                <p className="text-xs text-text-muted mb-1">Assunto</p>
                <p className="font-medium text-text-primary">{selectedTemplate.subject}</p>
              </div>

              {/* Body */}
              <div className="p-4 rounded-lg bg-bg-secondary">
                <p className="text-xs text-text-muted mb-2">Corpo da Mensagem</p>
                <pre className="text-sm text-text-primary whitespace-pre-wrap font-sans">{selectedTemplate.body}</pre>
              </div>

              {/* Variables */}
              <div>
                <h4 className="font-medium text-text-primary mb-3">Variáveis Disponíveis</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.variables.map((variable) => (
                    <Badge key={variable} variant="secondary">
                      <Code className="w-3 h-3 mr-1" />
                      {`{{${variable}}}`}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-lg border border-border text-center">
                  <p className="text-2xl font-bold text-primary">{selectedTemplate.usageCount}</p>
                  <p className="text-xs text-text-muted">Vezes Usado</p>
                </div>
                <div className="p-4 rounded-lg border border-border text-center">
                  <p className="text-sm font-medium text-text-primary">
                    {selectedTemplate.lastUsed ? new Date(selectedTemplate.lastUsed).toLocaleDateString('pt-BR') : 'Nunca'}
                  </p>
                  <p className="text-xs text-text-muted">Último Uso</p>
                </div>
                <div className="p-4 rounded-lg border border-border text-center">
                  <p className="text-sm font-medium text-text-primary">
                    {new Date(selectedTemplate.updatedAt).toLocaleDateString('pt-BR')}
                  </p>
                  <p className="text-xs text-text-muted">Última Atualização</p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
