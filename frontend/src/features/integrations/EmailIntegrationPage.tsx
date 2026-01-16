'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  Modal,
  Select
} from '@/design-system/components';
import type { Column, SelectOption } from '@/design-system/components';
import {
  Mail,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Send,
  Eye,
  Edit,
  Trash2,
  Copy,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  BarChart3,
  FileText,
  Users,
  Calendar,
  ArrowUpRight,
  Inbox,
  SendHorizontal,
  Settings,
  Zap,
  Play,
  Pause
} from 'lucide-react';
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
  Legend,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';

// Types
interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  category: 'transactional' | 'marketing' | 'notification' | 'reminder';
  status: 'active' | 'draft' | 'archived';
  lastUsed: string;
  usageCount: number;
  openRate: number;
  clickRate: number;
  createdAt: string;
}

interface EmailCampaign {
  id: string;
  name: string;
  templateId: string;
  templateName: string;
  status: 'scheduled' | 'sending' | 'completed' | 'paused' | 'failed';
  recipients: number;
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  bounced: number;
  scheduledAt: string;
  completedAt?: string;
}

interface EmailLog {
  id: string;
  recipient: string;
  recipientName: string;
  subject: string;
  templateName: string;
  status: 'delivered' | 'opened' | 'clicked' | 'bounced' | 'failed';
  sentAt: string;
  openedAt?: string;
  clickedAt?: string;
  errorMessage?: string;
}

// Mock data
const mockTemplates: EmailTemplate[] = [
  {
    id: '1',
    name: 'Boas-vindas',
    subject: 'Bem-vindo ao Conecta PRO!',
    category: 'transactional',
    status: 'active',
    lastUsed: '2024-01-15T10:30:00',
    usageCount: 1234,
    openRate: 78,
    clickRate: 45,
    createdAt: '2023-06-01'
  },
  {
    id: '2',
    name: 'Fatura Vencendo',
    subject: 'Sua fatura vence em 3 dias',
    category: 'reminder',
    status: 'active',
    lastUsed: '2024-01-15T08:00:00',
    usageCount: 856,
    openRate: 65,
    clickRate: 32,
    createdAt: '2023-07-15'
  },
  {
    id: '3',
    name: 'Newsletter Mensal',
    subject: 'Novidades de Janeiro',
    category: 'marketing',
    status: 'active',
    lastUsed: '2024-01-01T09:00:00',
    usageCount: 5432,
    openRate: 42,
    clickRate: 18,
    createdAt: '2023-03-10'
  },
  {
    id: '4',
    name: 'Recuperação de Senha',
    subject: 'Redefinir sua senha',
    category: 'transactional',
    status: 'active',
    lastUsed: '2024-01-15T14:22:00',
    usageCount: 234,
    openRate: 92,
    clickRate: 88,
    createdAt: '2023-06-01'
  },
  {
    id: '5',
    name: 'Promoção Especial',
    subject: 'Oferta exclusiva para você!',
    category: 'marketing',
    status: 'draft',
    lastUsed: '',
    usageCount: 0,
    openRate: 0,
    clickRate: 0,
    createdAt: '2024-01-10'
  }
];

const mockCampaigns: EmailCampaign[] = [
  {
    id: '1',
    name: 'Newsletter Janeiro',
    templateId: '3',
    templateName: 'Newsletter Mensal',
    status: 'completed',
    recipients: 5432,
    sent: 5432,
    delivered: 5280,
    opened: 2217,
    clicked: 950,
    bounced: 152,
    scheduledAt: '2024-01-01T09:00:00',
    completedAt: '2024-01-01T09:45:00'
  },
  {
    id: '2',
    name: 'Cobrança Vencimentos',
    templateId: '2',
    templateName: 'Fatura Vencendo',
    status: 'sending',
    recipients: 234,
    sent: 156,
    delivered: 150,
    opened: 98,
    clicked: 45,
    bounced: 6,
    scheduledAt: '2024-01-15T08:00:00'
  },
  {
    id: '3',
    name: 'Campanha Fevereiro',
    templateId: '5',
    templateName: 'Promoção Especial',
    status: 'scheduled',
    recipients: 3500,
    sent: 0,
    delivered: 0,
    opened: 0,
    clicked: 0,
    bounced: 0,
    scheduledAt: '2024-02-01T10:00:00'
  },
  {
    id: '4',
    name: 'Black Friday',
    templateId: '5',
    templateName: 'Promoção Especial',
    status: 'paused',
    recipients: 8000,
    sent: 2500,
    delivered: 2400,
    opened: 1200,
    clicked: 580,
    bounced: 100,
    scheduledAt: '2024-01-10T06:00:00'
  }
];

const mockLogs: EmailLog[] = [
  {
    id: '1',
    recipient: 'joao.silva@email.com',
    recipientName: 'João Silva',
    subject: 'Bem-vindo ao Conecta PRO!',
    templateName: 'Boas-vindas',
    status: 'clicked',
    sentAt: '2024-01-15T10:30:00',
    openedAt: '2024-01-15T10:35:00',
    clickedAt: '2024-01-15T10:36:00'
  },
  {
    id: '2',
    recipient: 'maria.santos@empresa.com',
    recipientName: 'Maria Santos',
    subject: 'Sua fatura vence em 3 dias',
    templateName: 'Fatura Vencendo',
    status: 'opened',
    sentAt: '2024-01-15T08:00:00',
    openedAt: '2024-01-15T09:15:00'
  },
  {
    id: '3',
    recipient: 'invalid@test',
    recipientName: 'Teste Inválido',
    subject: 'Newsletter Janeiro',
    templateName: 'Newsletter Mensal',
    status: 'bounced',
    sentAt: '2024-01-01T09:00:00',
    errorMessage: 'Invalid email address'
  },
  {
    id: '4',
    recipient: 'pedro.costa@gmail.com',
    recipientName: 'Pedro Costa',
    subject: 'Redefinir sua senha',
    templateName: 'Recuperação de Senha',
    status: 'delivered',
    sentAt: '2024-01-15T14:22:00'
  },
  {
    id: '5',
    recipient: 'ana.oliveira@corp.com',
    recipientName: 'Ana Oliveira',
    subject: 'Novidades de Janeiro',
    templateName: 'Newsletter Mensal',
    status: 'failed',
    sentAt: '2024-01-01T09:00:00',
    errorMessage: 'Mailbox full'
  }
];

// Chart data
const emailVolumeData = [
  { date: '01/01', sent: 1234, opened: 823, clicked: 412 },
  { date: '05/01', sent: 567, opened: 345, clicked: 156 },
  { date: '10/01', sent: 890, opened: 534, clicked: 267 },
  { date: '15/01', sent: 1456, opened: 987, clicked: 456 }
];

const deliveryStatusData = [
  { name: 'Entregues', value: 4560, color: '#10b981' },
  { name: 'Abertos', value: 2850, color: '#6366f1' },
  { name: 'Clicados', value: 1250, color: '#8b5cf6' },
  { name: 'Bounces', value: 180, color: '#ef4444' }
];

const categoryData = [
  { name: 'Transacional', emails: 1234 },
  { name: 'Marketing', emails: 5432 },
  { name: 'Notificação', emails: 890 },
  { name: 'Lembrete', emails: 456 }
];

const hourlyData = [
  { hour: '06h', sent: 45 },
  { hour: '08h', sent: 234 },
  { hour: '10h', sent: 456 },
  { hour: '12h', sent: 123 },
  { hour: '14h', sent: 345 },
  { hour: '16h', sent: 567 },
  { hour: '18h', sent: 234 }
];

export function EmailIntegrationPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<EmailTemplate | null>(null);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState<EmailCampaign | null>(null);
  const [categoryFilter, setCategoryFilter] = useState('all');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <BarChart3 className="h-4 w-4" /> },
    { value: 'templates', label: 'Templates', icon: <FileText className="h-4 w-4" /> },
    { value: 'campaigns', label: 'Campanhas', icon: <Send className="h-4 w-4" /> },
    { value: 'logs', label: 'Histórico', icon: <Inbox className="h-4 w-4" /> }
  ];

  const categoryOptions: SelectOption[] = [
    { value: 'all', label: 'Todas Categorias' },
    { value: 'transactional', label: 'Transacional' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'notification', label: 'Notificação' },
    { value: 'reminder', label: 'Lembrete' }
  ];

  const getCategoryBadge = (category: EmailTemplate['category']) => {
    const categoryConfig = {
      transactional: { label: 'Transacional', variant: 'primary' as const },
      marketing: { label: 'Marketing', variant: 'success' as const },
      notification: { label: 'Notificação', variant: 'info' as const },
      reminder: { label: 'Lembrete', variant: 'warning' as const }
    };
    const config = categoryConfig[category];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getStatusBadge = (status: EmailTemplate['status']) => {
    const statusConfig = {
      active: { label: 'Ativo', variant: 'success' as const },
      draft: { label: 'Rascunho', variant: 'warning' as const },
      archived: { label: 'Arquivado', variant: 'neutral' as const }
    };
    const config = statusConfig[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getCampaignStatusBadge = (status: EmailCampaign['status']) => {
    const statusConfig = {
      scheduled: { label: 'Agendada', variant: 'info' as const, icon: <Clock className="h-3 w-3" /> },
      sending: { label: 'Enviando', variant: 'warning' as const, icon: <SendHorizontal className="h-3 w-3" /> },
      completed: { label: 'Concluída', variant: 'success' as const, icon: <CheckCircle className="h-3 w-3" /> },
      paused: { label: 'Pausada', variant: 'neutral' as const, icon: <Pause className="h-3 w-3" /> },
      failed: { label: 'Falhou', variant: 'danger' as const, icon: <XCircle className="h-3 w-3" /> }
    };
    const config = statusConfig[status];
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        {config.icon}
        {config.label}
      </Badge>
    );
  };

  const getLogStatusBadge = (status: EmailLog['status']) => {
    const statusConfig = {
      delivered: { label: 'Entregue', variant: 'success' as const },
      opened: { label: 'Aberto', variant: 'info' as const },
      clicked: { label: 'Clicado', variant: 'primary' as const },
      bounced: { label: 'Bounce', variant: 'warning' as const },
      failed: { label: 'Falhou', variant: 'danger' as const }
    };
    const config = statusConfig[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const templateColumns: Column<EmailTemplate>[] = [
    {
      key: 'name',
      header: 'Template',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-bg-tertiary flex items-center justify-center">
            <FileText className="h-5 w-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary truncate max-w-xs">{row.subject}</p>
          </div>
        </div>
      )
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => getCategoryBadge(row.category)
    },
    {
      key: 'usage',
      header: 'Uso',
      render: (row) => (
        <div>
          <p className="text-text-primary font-medium">{row.usageCount.toLocaleString()}</p>
          <p className="text-sm text-text-secondary">envios</p>
        </div>
      )
    },
    {
      key: 'performance',
      header: 'Performance',
      render: (row) => (
        <div className="flex items-center gap-4">
          <div>
            <p className="text-sm text-text-secondary">Abertura</p>
            <p className="text-text-primary font-medium">{row.openRate}%</p>
          </div>
          <div>
            <p className="text-sm text-text-secondary">Cliques</p>
            <p className="text-text-primary font-medium">{row.clickRate}%</p>
          </div>
        </div>
      )
    },
    {
      key: 'lastUsed',
      header: 'Último Uso',
      render: (row) => (
        <div>
          {row.lastUsed ? (
            <>
              <p className="text-text-primary">
                {new Date(row.lastUsed).toLocaleDateString('pt-BR')}
              </p>
              <p className="text-sm text-text-secondary">
                {new Date(row.lastUsed).toLocaleTimeString('pt-BR')}
              </p>
            </>
          ) : (
            <span className="text-text-secondary">Nunca</span>
          )}
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedTemplate(row);
              setShowTemplateModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost">
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost">
            <Copy className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const campaignColumns: Column<EmailCampaign>[] = [
    {
      key: 'name',
      header: 'Campanha',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-bg-tertiary flex items-center justify-center">
            <Send className="h-5 w-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.templateName}</p>
          </div>
        </div>
      )
    },
    {
      key: 'progress',
      header: 'Progresso',
      render: (row) => (
        <div className="w-32">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-text-secondary">
              {row.sent}/{row.recipients}
            </span>
            <span className="text-sm text-text-primary">
              {Math.round((row.sent / row.recipients) * 100)}%
            </span>
          </div>
          <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-primary rounded-full transition-all"
              style={{ width: `${(row.sent / row.recipients) * 100}%` }}
            />
          </div>
        </div>
      )
    },
    {
      key: 'stats',
      header: 'Métricas',
      render: (row) => (
        <div className="flex items-center gap-3 text-sm">
          <div className="flex items-center gap-1 text-green-400">
            <CheckCircle className="h-3 w-3" />
            {row.delivered}
          </div>
          <div className="flex items-center gap-1 text-blue-400">
            <Eye className="h-3 w-3" />
            {row.opened}
          </div>
          <div className="flex items-center gap-1 text-purple-400">
            <ArrowUpRight className="h-3 w-3" />
            {row.clicked}
          </div>
          {row.bounced > 0 && (
            <div className="flex items-center gap-1 text-red-400">
              <XCircle className="h-3 w-3" />
              {row.bounced}
            </div>
          )}
        </div>
      )
    },
    {
      key: 'schedule',
      header: 'Agendamento',
      render: (row) => (
        <div>
          <p className="text-text-primary">
            {new Date(row.scheduledAt).toLocaleDateString('pt-BR')}
          </p>
          <p className="text-sm text-text-secondary">
            {new Date(row.scheduledAt).toLocaleTimeString('pt-BR')}
          </p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getCampaignStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedCampaign(row);
              setShowCampaignModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'sending' && (
            <Button variant="ghost">
              <Pause className="h-4 w-4" />
            </Button>
          )}
          {row.status === 'paused' && (
            <Button variant="ghost">
              <Play className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const logColumns: Column<EmailLog>[] = [
    {
      key: 'recipient',
      header: 'Destinatário',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
            <Mail className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.recipientName}</p>
            <p className="text-sm text-text-secondary">{row.recipient}</p>
          </div>
        </div>
      )
    },
    {
      key: 'subject',
      header: 'Assunto',
      render: (row) => (
        <div className="max-w-xs">
          <p className="text-text-primary truncate">{row.subject}</p>
          <p className="text-sm text-text-secondary">{row.templateName}</p>
        </div>
      )
    },
    {
      key: 'sentAt',
      header: 'Enviado em',
      render: (row) => (
        <div>
          <p className="text-text-primary">
            {new Date(row.sentAt).toLocaleDateString('pt-BR')}
          </p>
          <p className="text-sm text-text-secondary">
            {new Date(row.sentAt).toLocaleTimeString('pt-BR')}
          </p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getLogStatusBadge(row.status)
    },
    {
      key: 'error',
      header: 'Detalhes',
      render: (row) => (
        <div className="max-w-xs">
          {row.errorMessage ? (
            <p className="text-sm text-red-400">{row.errorMessage}</p>
          ) : row.clickedAt ? (
            <p className="text-sm text-text-secondary">
              Clicado: {new Date(row.clickedAt).toLocaleTimeString('pt-BR')}
            </p>
          ) : row.openedAt ? (
            <p className="text-sm text-text-secondary">
              Aberto: {new Date(row.openedAt).toLocaleTimeString('pt-BR')}
            </p>
          ) : (
            <span className="text-text-secondary">-</span>
          )}
        </div>
      )
    }
  ];

  const totalSent = mockCampaigns.reduce((sum, c) => sum + c.sent, 0);
  const totalOpened = mockCampaigns.reduce((sum, c) => sum + c.opened, 0);
  const avgOpenRate = totalSent > 0 ? Math.round((totalOpened / totalSent) * 100) : 0;
  const totalBounced = mockCampaigns.reduce((sum, c) => sum + c.bounced, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Integração de Email
            </h1>
            <p className="text-text-secondary mt-1">
              Configuração e envio de emails automatizados
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Configurar SMTP
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Novo Template
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Enviados Hoje"
            value={totalSent.toLocaleString()}
            icon={<Send className="h-5 w-5" />}
            iconColor="success"
            change={12}
            changeLabel="vs. ontem"
          />
          <StatCard
            title="Templates"
            value={mockTemplates.filter(t => t.status === 'active').length.toString()}
            icon={<FileText className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Taxa Abertura"
            value={`${avgOpenRate}%`}
            icon={<Eye className="h-5 w-5" />}
            iconColor="primary"
            change={5}
            changeLabel="vs. semana passada"
          />
          <StatCard
            title="Bounces"
            value={totalBounced.toString()}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="warning"
            change={-8}
            changeLabel="vs. ontem"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Email Volume */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Volume de Emails
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={emailVolumeData}>
                    <defs>
                      <linearGradient id="sentGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="sent"
                      name="Enviados"
                      stroke="#6366f1"
                      fill="url(#sentGradient)"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="opened"
                      name="Abertos"
                      stroke="#10b981"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="clicked"
                      name="Clicados"
                      stroke="#8b5cf6"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              {/* Delivery Status */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Status de Entrega
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={deliveryStatusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {deliveryStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Category & Hourly */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* By Category */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Emails por Categoria
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categoryData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="emails" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              {/* By Hour */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Envios por Hora
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={hourlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="hour" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="sent"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ fill: '#10b981' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Atividade Recente
                </h3>
                <Button variant="outline" size="sm" onClick={() => setActiveTab('logs')}>
                  Ver Tudo
                </Button>
              </div>
              <div className="space-y-3">
                {mockLogs.slice(0, 5).map((log) => (
                  <div
                    key={log.id}
                    className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                        <Mail className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{log.recipientName}</p>
                        <p className="text-sm text-text-secondary">{log.subject}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {getLogStatusBadge(log.status)}
                      <span className="text-sm text-text-secondary">
                        {new Date(log.sentAt).toLocaleTimeString('pt-BR')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'templates' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar template..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Select
                options={categoryOptions}
                value={categoryFilter}
                onChange={(value) => setCategoryFilter(value)}
              />
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Novo Template
              </Button>
            </div>

            <DataTable
              data={mockTemplates}
              columns={templateColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'campaigns' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar campanha..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Nova Campanha
              </Button>
            </div>

            <DataTable
              data={mockCampaigns}
              columns={campaignColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'logs' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar por destinatário..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Button variant="outline">
                <Calendar className="h-4 w-4 mr-2" />
                Período
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>

            <DataTable
              data={mockLogs}
              columns={logColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}
      </div>

      {/* Template Modal */}
      <Modal
        isOpen={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
        title="Detalhes do Template"
        size="lg"
      >
        {selectedTemplate && (
          <div className="space-y-6">
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="h-16 w-16 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                <FileText className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedTemplate.name}
                </h3>
                <p className="text-text-secondary">{selectedTemplate.subject}</p>
              </div>
              <div className="ml-auto flex items-center gap-2">
                {getCategoryBadge(selectedTemplate.category)}
                {getStatusBadge(selectedTemplate.status)}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-accent-primary">
                  {selectedTemplate.usageCount.toLocaleString()}
                </p>
                <p className="text-sm text-text-secondary">Envios</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-green-400">{selectedTemplate.openRate}%</p>
                <p className="text-sm text-text-secondary">Taxa de Abertura</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-purple-400">{selectedTemplate.clickRate}%</p>
                <p className="text-sm text-text-secondary">Taxa de Cliques</p>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
              <Button variant="outline">
                <Copy className="h-4 w-4 mr-2" />
                Duplicar
              </Button>
              <Button variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                Editar
              </Button>
              <Button>
                <Send className="h-4 w-4 mr-2" />
                Usar em Campanha
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Campaign Modal */}
      <Modal
        isOpen={showCampaignModal}
        onClose={() => setShowCampaignModal(false)}
        title="Detalhes da Campanha"
        size="lg"
      >
        {selectedCampaign && (
          <div className="space-y-6">
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="h-16 w-16 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                <Send className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedCampaign.name}
                </h3>
                <p className="text-text-secondary">{selectedCampaign.templateName}</p>
              </div>
              <div className="ml-auto">
                {getCampaignStatusBadge(selectedCampaign.status)}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-text-primary">
                  {selectedCampaign.recipients.toLocaleString()}
                </p>
                <p className="text-sm text-text-secondary">Destinatários</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-green-400">
                  {selectedCampaign.delivered.toLocaleString()}
                </p>
                <p className="text-sm text-text-secondary">Entregues</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-blue-400">
                  {selectedCampaign.opened.toLocaleString()}
                </p>
                <p className="text-sm text-text-secondary">Abertos</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-purple-400">
                  {selectedCampaign.clicked.toLocaleString()}
                </p>
                <p className="text-sm text-text-secondary">Clicados</p>
              </div>
            </div>

            {selectedCampaign.bounced > 0 && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-5 w-5 text-red-400" />
                  <span className="text-red-400 font-medium">
                    {selectedCampaign.bounced} emails retornaram (bounce)
                  </span>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
              {selectedCampaign.status === 'sending' && (
                <Button variant="outline">
                  <Pause className="h-4 w-4 mr-2" />
                  Pausar
                </Button>
              )}
              {selectedCampaign.status === 'paused' && (
                <Button variant="outline">
                  <Play className="h-4 w-4 mr-2" />
                  Retomar
                </Button>
              )}
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar Relatório
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}
