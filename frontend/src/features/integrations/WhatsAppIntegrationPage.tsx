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
  MessageCircle,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Send,
  Users,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Play,
  Pause,
  Copy,
  MessageSquare,
  Phone,
  Image,
  Paperclip,
  Smile,
  MoreVertical,
  ChevronRight,
  Bot,
  Zap,
  TrendingUp,
  Calendar
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend,
  LineChart, Line, AreaChart, Area
} from 'recharts';

// Types
interface WhatsAppTemplate {
  id: string;
  name: string;
  category: 'marketing' | 'utility' | 'authentication';
  language: string;
  status: 'approved' | 'pending' | 'rejected';
  content: string;
  variables: string[];
  headerType: 'none' | 'text' | 'image' | 'document' | 'video';
  headerContent?: string;
  footerText?: string;
  buttons: TemplateButton[];
  usageCount: number;
  lastUsed: string;
  createdAt: string;
}

interface TemplateButton {
  type: 'quick_reply' | 'url' | 'phone';
  text: string;
  value?: string;
}

interface WhatsAppCampaign {
  id: string;
  name: string;
  templateId: string;
  templateName: string;
  status: 'draft' | 'scheduled' | 'running' | 'paused' | 'completed' | 'failed';
  targetAudience: string;
  totalRecipients: number;
  sent: number;
  delivered: number;
  read: number;
  replied: number;
  failed: number;
  scheduledAt?: string;
  startedAt?: string;
  completedAt?: string;
  createdAt: string;
}

interface WhatsAppConversation {
  id: string;
  contactId: string;
  contactName: string;
  contactPhone: string;
  contactAvatar?: string;
  lastMessage: string;
  lastMessageTime: string;
  lastMessageType: 'sent' | 'received';
  unreadCount: number;
  status: 'active' | 'waiting' | 'resolved' | 'expired';
  assignedTo?: string;
  tags: string[];
  createdAt: string;
}

interface WhatsAppContact {
  id: string;
  name: string;
  phone: string;
  email?: string;
  avatar?: string;
  tags: string[];
  optIn: boolean;
  optInDate?: string;
  lastInteraction?: string;
  totalMessages: number;
  campaigns: number;
  status: 'active' | 'blocked' | 'opted_out';
  customFields: Record<string, string>;
  createdAt: string;
}

interface WhatsAppMessage {
  id: string;
  conversationId: string;
  type: 'text' | 'image' | 'document' | 'audio' | 'video' | 'template' | 'interactive';
  direction: 'sent' | 'received';
  content: string;
  mediaUrl?: string;
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
  timestamp: string;
}

// Mock Data
const mockTemplates: WhatsAppTemplate[] = [
  {
    id: '1',
    name: 'boas_vindas_cliente',
    category: 'utility',
    language: 'pt_BR',
    status: 'approved',
    content: 'Olá {{1}}! Bem-vindo(a) ao Conecta PRO. Estamos felizes em tê-lo(a) conosco. Qualquer dúvida, estamos à disposição!',
    variables: ['nome'],
    headerType: 'image',
    headerContent: 'welcome_header.png',
    footerText: 'Conecta PRO - Gestão Inteligente',
    buttons: [
      { type: 'url', text: 'Acessar Portal', value: 'https://portal.conectapro.com' },
      { type: 'phone', text: 'Ligar', value: '+5511999999999' }
    ],
    usageCount: 1234,
    lastUsed: '2024-01-15T14:30:00',
    createdAt: '2024-01-01T10:00:00'
  },
  {
    id: '2',
    name: 'lembrete_pagamento',
    category: 'utility',
    language: 'pt_BR',
    status: 'approved',
    content: 'Olá {{1}}, lembramos que sua fatura no valor de {{2}} vence em {{3}}. Evite juros e multas, pague em dia!',
    variables: ['nome', 'valor', 'data_vencimento'],
    headerType: 'none',
    footerText: 'Conecta PRO - Gestão Financeira',
    buttons: [
      { type: 'url', text: 'Pagar Agora', value: 'https://pag.conectapro.com/{{4}}' },
      { type: 'quick_reply', text: 'Já paguei' }
    ],
    usageCount: 5678,
    lastUsed: '2024-01-15T16:00:00',
    createdAt: '2024-01-02T09:00:00'
  },
  {
    id: '3',
    name: 'confirmacao_agendamento',
    category: 'utility',
    language: 'pt_BR',
    status: 'approved',
    content: 'Seu agendamento foi confirmado! 📅\n\nData: {{1}}\nHorário: {{2}}\nServiço: {{3}}\n\nAguardamos você!',
    variables: ['data', 'horario', 'servico'],
    headerType: 'text',
    headerContent: 'Agendamento Confirmado ✅',
    buttons: [
      { type: 'quick_reply', text: 'Confirmar presença' },
      { type: 'quick_reply', text: 'Remarcar' },
      { type: 'quick_reply', text: 'Cancelar' }
    ],
    usageCount: 890,
    lastUsed: '2024-01-15T12:00:00',
    createdAt: '2024-01-03T14:00:00'
  },
  {
    id: '4',
    name: 'promocao_janeiro',
    category: 'marketing',
    language: 'pt_BR',
    status: 'pending',
    content: '🔥 MEGA PROMOÇÃO DE JANEIRO! 🔥\n\nOlá {{1}}, temos ofertas especiais esperando por você!\n\nAté 50% de desconto em serviços selecionados.\n\nVálido até {{2}}.',
    variables: ['nome', 'data_fim'],
    headerType: 'image',
    headerContent: 'promo_janeiro.png',
    footerText: 'Oferta por tempo limitado',
    buttons: [
      { type: 'url', text: 'Ver Ofertas', value: 'https://conectapro.com/ofertas' }
    ],
    usageCount: 0,
    lastUsed: '',
    createdAt: '2024-01-10T11:00:00'
  },
  {
    id: '5',
    name: 'codigo_verificacao',
    category: 'authentication',
    language: 'pt_BR',
    status: 'approved',
    content: 'Seu código de verificação é: {{1}}\n\nEste código expira em 5 minutos.\n\n⚠️ Não compartilhe este código com ninguém.',
    variables: ['codigo'],
    headerType: 'none',
    buttons: [],
    usageCount: 12450,
    lastUsed: '2024-01-15T17:45:00',
    createdAt: '2024-01-01T08:00:00'
  }
];

const mockCampaigns: WhatsAppCampaign[] = [
  {
    id: '1',
    name: 'Boas-vindas Novos Clientes Janeiro',
    templateId: '1',
    templateName: 'boas_vindas_cliente',
    status: 'completed',
    targetAudience: 'Novos clientes (últimos 30 dias)',
    totalRecipients: 456,
    sent: 456,
    delivered: 448,
    read: 389,
    replied: 67,
    failed: 8,
    startedAt: '2024-01-10T09:00:00',
    completedAt: '2024-01-10T09:45:00',
    createdAt: '2024-01-09T16:00:00'
  },
  {
    id: '2',
    name: 'Lembrete Pagamentos Vencendo',
    templateId: '2',
    templateName: 'lembrete_pagamento',
    status: 'running',
    targetAudience: 'Faturas vencendo em 3 dias',
    totalRecipients: 234,
    sent: 156,
    delivered: 152,
    read: 98,
    replied: 23,
    failed: 4,
    startedAt: '2024-01-15T08:00:00',
    createdAt: '2024-01-14T18:00:00'
  },
  {
    id: '3',
    name: 'Promoção Janeiro',
    templateId: '4',
    templateName: 'promocao_janeiro',
    status: 'scheduled',
    targetAudience: 'Todos os clientes ativos',
    totalRecipients: 5432,
    sent: 0,
    delivered: 0,
    read: 0,
    replied: 0,
    failed: 0,
    scheduledAt: '2024-01-20T10:00:00',
    createdAt: '2024-01-15T14:00:00'
  },
  {
    id: '4',
    name: 'Confirmações Agendamentos',
    templateId: '3',
    templateName: 'confirmacao_agendamento',
    status: 'paused',
    targetAudience: 'Agendamentos do dia',
    totalRecipients: 89,
    sent: 45,
    delivered: 44,
    read: 38,
    replied: 32,
    failed: 1,
    startedAt: '2024-01-15T07:00:00',
    createdAt: '2024-01-14T20:00:00'
  }
];

const mockConversations: WhatsAppConversation[] = [
  {
    id: '1',
    contactId: 'c1',
    contactName: 'Maria Silva',
    contactPhone: '+5511999887766',
    lastMessage: 'Obrigada pelo atendimento!',
    lastMessageTime: '2024-01-15T17:30:00',
    lastMessageType: 'received',
    unreadCount: 0,
    status: 'resolved',
    assignedTo: 'Ana Costa',
    tags: ['cliente_vip', 'satisfeito'],
    createdAt: '2024-01-15T16:00:00'
  },
  {
    id: '2',
    contactId: 'c2',
    contactName: 'João Santos',
    contactPhone: '+5511988776655',
    lastMessage: 'Aguardando resposta sobre o orçamento',
    lastMessageTime: '2024-01-15T17:45:00',
    lastMessageType: 'received',
    unreadCount: 2,
    status: 'waiting',
    assignedTo: 'Carlos Lima',
    tags: ['lead', 'orcamento'],
    createdAt: '2024-01-15T14:00:00'
  },
  {
    id: '3',
    contactId: 'c3',
    contactName: 'Ana Oliveira',
    contactPhone: '+5511977665544',
    lastMessage: 'Enviei o comprovante de pagamento',
    lastMessageTime: '2024-01-15T17:50:00',
    lastMessageType: 'received',
    unreadCount: 1,
    status: 'active',
    tags: ['financeiro'],
    createdAt: '2024-01-15T17:40:00'
  },
  {
    id: '4',
    contactId: 'c4',
    contactName: 'Pedro Costa',
    contactPhone: '+5511966554433',
    lastMessage: 'Seu agendamento foi confirmado para amanhã às 14h',
    lastMessageTime: '2024-01-15T16:20:00',
    lastMessageType: 'sent',
    unreadCount: 0,
    status: 'active',
    assignedTo: 'Ana Costa',
    tags: ['agendamento'],
    createdAt: '2024-01-15T16:00:00'
  },
  {
    id: '5',
    contactId: 'c5',
    contactName: 'Carla Mendes',
    contactPhone: '+5511955443322',
    lastMessage: 'Preciso de suporte técnico urgente',
    lastMessageTime: '2024-01-15T17:55:00',
    lastMessageType: 'received',
    unreadCount: 3,
    status: 'waiting',
    tags: ['suporte', 'urgente'],
    createdAt: '2024-01-15T17:50:00'
  }
];

const mockContacts: WhatsAppContact[] = [
  {
    id: 'c1',
    name: 'Maria Silva',
    phone: '+5511999887766',
    email: 'maria.silva@email.com',
    tags: ['cliente_vip', 'satisfeito'],
    optIn: true,
    optInDate: '2024-01-01T10:00:00',
    lastInteraction: '2024-01-15T17:30:00',
    totalMessages: 45,
    campaigns: 3,
    status: 'active',
    customFields: { empresa: 'Tech Corp', cargo: 'Gerente' },
    createdAt: '2024-01-01T10:00:00'
  },
  {
    id: 'c2',
    name: 'João Santos',
    phone: '+5511988776655',
    email: 'joao.santos@email.com',
    tags: ['lead', 'orcamento'],
    optIn: true,
    optInDate: '2024-01-10T14:00:00',
    lastInteraction: '2024-01-15T17:45:00',
    totalMessages: 12,
    campaigns: 1,
    status: 'active',
    customFields: { empresa: 'Comercial SA' },
    createdAt: '2024-01-10T14:00:00'
  },
  {
    id: 'c3',
    name: 'Ana Oliveira',
    phone: '+5511977665544',
    email: 'ana.oliveira@email.com',
    tags: ['financeiro'],
    optIn: true,
    optInDate: '2024-01-05T09:00:00',
    lastInteraction: '2024-01-15T17:50:00',
    totalMessages: 28,
    campaigns: 2,
    status: 'active',
    customFields: {},
    createdAt: '2024-01-05T09:00:00'
  },
  {
    id: 'c4',
    name: 'Pedro Costa',
    phone: '+5511966554433',
    tags: ['agendamento'],
    optIn: true,
    optInDate: '2024-01-08T11:00:00',
    lastInteraction: '2024-01-15T16:20:00',
    totalMessages: 8,
    campaigns: 1,
    status: 'active',
    customFields: {},
    createdAt: '2024-01-08T11:00:00'
  },
  {
    id: 'c5',
    name: 'Carla Mendes',
    phone: '+5511955443322',
    email: 'carla.mendes@email.com',
    tags: ['suporte', 'urgente'],
    optIn: true,
    optInDate: '2024-01-12T16:00:00',
    lastInteraction: '2024-01-15T17:55:00',
    totalMessages: 15,
    campaigns: 2,
    status: 'active',
    customFields: { empresa: 'Startup XYZ', cargo: 'CEO' },
    createdAt: '2024-01-12T16:00:00'
  },
  {
    id: 'c6',
    name: 'Roberto Lima',
    phone: '+5511944332211',
    tags: [],
    optIn: false,
    totalMessages: 5,
    campaigns: 0,
    status: 'opted_out',
    customFields: {},
    createdAt: '2024-01-02T10:00:00'
  }
];

const mockMessages: WhatsAppMessage[] = [
  {
    id: 'm1',
    conversationId: '3',
    type: 'text',
    direction: 'received',
    content: 'Olá, boa tarde!',
    status: 'read',
    timestamp: '2024-01-15T17:40:00'
  },
  {
    id: 'm2',
    conversationId: '3',
    type: 'text',
    direction: 'sent',
    content: 'Olá Ana! Boa tarde, como posso ajudá-la?',
    status: 'read',
    timestamp: '2024-01-15T17:41:00'
  },
  {
    id: 'm3',
    conversationId: '3',
    type: 'text',
    direction: 'received',
    content: 'Gostaria de confirmar o pagamento da fatura',
    status: 'read',
    timestamp: '2024-01-15T17:42:00'
  },
  {
    id: 'm4',
    conversationId: '3',
    type: 'text',
    direction: 'sent',
    content: 'Claro! Pode enviar o comprovante que verifico para você.',
    status: 'read',
    timestamp: '2024-01-15T17:43:00'
  },
  {
    id: 'm5',
    conversationId: '3',
    type: 'image',
    direction: 'received',
    content: 'Comprovante de pagamento',
    mediaUrl: '/uploads/comprovante_ana.jpg',
    status: 'delivered',
    timestamp: '2024-01-15T17:50:00'
  }
];

// Chart colors
const CHART_COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];

export function WhatsAppIntegrationPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<WhatsAppTemplate | null>(null);
  const [selectedCampaign, setSelectedCampaign] = useState<WhatsAppCampaign | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<WhatsAppConversation | null>(null);
  const [selectedContact, setSelectedContact] = useState<WhatsAppContact | null>(null);
  const [showAddTemplateModal, setShowAddTemplateModal] = useState(false);
  const [showAddCampaignModal, setShowAddCampaignModal] = useState(false);
  const [showAddContactModal, setShowAddContactModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [messageInput, setMessageInput] = useState('');
  const [newTemplateCategory, setNewTemplateCategory] = useState('utility');
  const [newTemplateLanguage, setNewTemplateLanguage] = useState('pt_BR');
  const [newCampaignTemplate, setNewCampaignTemplate] = useState('');
  const [newCampaignAudience, setNewCampaignAudience] = useState('all');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <MessageCircle className="h-4 w-4" /> },
    { value: 'templates', label: 'Templates', icon: <FileText className="h-4 w-4" /> },
    { value: 'campaigns', label: 'Campanhas', icon: <Send className="h-4 w-4" /> },
    { value: 'conversations', label: 'Conversas', icon: <MessageSquare className="h-4 w-4" /> },
    { value: 'contacts', label: 'Contatos', icon: <Users className="h-4 w-4" /> }
  ];

  const statusOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Status' },
    { value: 'approved', label: 'Aprovado' },
    { value: 'pending', label: 'Pendente' },
    { value: 'rejected', label: 'Rejeitado' }
  ];

  const campaignStatusOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Status' },
    { value: 'draft', label: 'Rascunho' },
    { value: 'scheduled', label: 'Agendada' },
    { value: 'running', label: 'Em Execução' },
    { value: 'paused', label: 'Pausada' },
    { value: 'completed', label: 'Concluída' },
    { value: 'failed', label: 'Falhou' }
  ];

  const conversationStatusOptions: SelectOption[] = [
    { value: 'all', label: 'Todos' },
    { value: 'active', label: 'Ativo' },
    { value: 'waiting', label: 'Aguardando' },
    { value: 'resolved', label: 'Resolvido' },
    { value: 'expired', label: 'Expirado' }
  ];

  // Calculated stats
  const totalMessages = mockCampaigns.reduce((sum, c) => sum + c.sent, 0) +
    mockConversations.reduce((sum, c) => sum + mockMessages.filter(m => m.conversationId === c.id).length, 0);
  const totalContacts = mockContacts.filter(c => c.optIn).length;
  const activeCampaigns = mockCampaigns.filter(c => c.status === 'running').length;
  const avgResponseRate = Math.round(
    mockCampaigns.filter(c => c.sent > 0).reduce((sum, c) => sum + (c.replied / c.sent * 100), 0) /
    mockCampaigns.filter(c => c.sent > 0).length
  );

  // Chart data
  const messageVolumeData = [
    { hour: '06h', sent: 45, received: 23 },
    { hour: '08h', sent: 120, received: 67 },
    { hour: '10h', sent: 234, received: 156 },
    { hour: '12h', sent: 189, received: 98 },
    { hour: '14h', sent: 267, received: 178 },
    { hour: '16h', sent: 198, received: 134 },
    { hour: '18h', sent: 156, received: 89 },
    { hour: '20h', sent: 78, received: 45 }
  ];

  const deliveryStatusData = [
    { name: 'Entregues', value: 4234, color: '#10b981' },
    { name: 'Lidas', value: 3567, color: '#6366f1' },
    { name: 'Respondidas', value: 890, color: '#8b5cf6' },
    { name: 'Falhas', value: 123, color: '#ef4444' }
  ];

  const campaignPerformanceData = mockCampaigns.map(c => ({
    name: c.name.substring(0, 15) + '...',
    delivered: c.delivered,
    read: c.read,
    replied: c.replied
  }));

  const contactGrowthData = [
    { month: 'Set', contacts: 3200, optIn: 2890 },
    { month: 'Out', contacts: 3800, optIn: 3420 },
    { month: 'Nov', contacts: 4300, optIn: 3870 },
    { month: 'Dez', contacts: 4900, optIn: 4410 },
    { month: 'Jan', contacts: 5432, optIn: 4889 }
  ];

  // Format functions
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const formatDateTime = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPhone = (phone: string) => {
    return phone.replace(/(\+55)(\d{2})(\d{5})(\d{4})/, '$1 ($2) $3-$4');
  };

  const getTemplateStatusBadge = (status: WhatsAppTemplate['status']) => {
    const config = {
      approved: { variant: 'success' as const, label: 'Aprovado' },
      pending: { variant: 'warning' as const, label: 'Pendente' },
      rejected: { variant: 'danger' as const, label: 'Rejeitado' }
    };
    const { variant, label } = config[status];
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getCampaignStatusBadge = (status: WhatsAppCampaign['status']) => {
    const config = {
      draft: { variant: 'neutral' as const, label: 'Rascunho' },
      scheduled: { variant: 'info' as const, label: 'Agendada' },
      running: { variant: 'primary' as const, label: 'Em Execução' },
      paused: { variant: 'warning' as const, label: 'Pausada' },
      completed: { variant: 'success' as const, label: 'Concluída' },
      failed: { variant: 'danger' as const, label: 'Falhou' }
    };
    const { variant, label } = config[status];
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getConversationStatusBadge = (status: WhatsAppConversation['status']) => {
    const config = {
      active: { variant: 'success' as const, label: 'Ativo' },
      waiting: { variant: 'warning' as const, label: 'Aguardando' },
      resolved: { variant: 'info' as const, label: 'Resolvido' },
      expired: { variant: 'neutral' as const, label: 'Expirado' }
    };
    const { variant, label } = config[status];
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getContactStatusBadge = (status: WhatsAppContact['status']) => {
    const config = {
      active: { variant: 'success' as const, label: 'Ativo' },
      blocked: { variant: 'danger' as const, label: 'Bloqueado' },
      opted_out: { variant: 'neutral' as const, label: 'Opt-out' }
    };
    const { variant, label } = config[status];
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getCategoryBadge = (category: WhatsAppTemplate['category']) => {
    const config = {
      marketing: { variant: 'primary' as const, label: 'Marketing' },
      utility: { variant: 'info' as const, label: 'Utilidade' },
      authentication: { variant: 'warning' as const, label: 'Autenticação' }
    };
    const { variant, label } = config[category];
    return <Badge variant={variant}>{label}</Badge>;
  };

  // Table columns
  const templateColumns: Column<WhatsAppTemplate>[] = [
    {
      key: 'name',
      header: 'Template',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-sm text-text-secondary truncate max-w-xs">
            {row.content.substring(0, 50)}...
          </p>
        </div>
      )
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => getCategoryBadge(row.category)
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getTemplateStatusBadge(row.status)
    },
    {
      key: 'usageCount',
      header: 'Uso',
      render: (row) => (
        <span className="text-text-primary font-medium">
          {row.usageCount.toLocaleString('pt-BR')}
        </span>
      )
    },
    {
      key: 'lastUsed',
      header: 'Último Uso',
      render: (row) => (
        <span className="text-text-secondary">
          {row.lastUsed ? formatDateTime(row.lastUsed) : 'Nunca usado'}
        </span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedTemplate(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Copy className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const campaignColumns: Column<WhatsAppCampaign>[] = [
    {
      key: 'name',
      header: 'Campanha',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-sm text-text-secondary">{row.templateName}</p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getCampaignStatusBadge(row.status)
    },
    {
      key: 'recipients',
      header: 'Destinatários',
      render: (row) => (
        <span className="text-text-primary">
          {row.totalRecipients.toLocaleString('pt-BR')}
        </span>
      )
    },
    {
      key: 'progress',
      header: 'Progresso',
      render: (row) => {
        const progress = row.totalRecipients > 0
          ? Math.round((row.sent / row.totalRecipients) * 100)
          : 0;
        return (
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="text-sm text-text-secondary w-12 text-right">
              {progress}%
            </span>
          </div>
        );
      }
    },
    {
      key: 'metrics',
      header: 'Métricas',
      render: (row) => (
        <div className="flex items-center gap-3 text-sm">
          <span className="text-green-400" title="Entregues">
            <CheckCircle className="h-3 w-3 inline mr-1" />
            {row.delivered}
          </span>
          <span className="text-blue-400" title="Lidas">
            <Eye className="h-3 w-3 inline mr-1" />
            {row.read}
          </span>
          <span className="text-purple-400" title="Respondidas">
            <MessageCircle className="h-3 w-3 inline mr-1" />
            {row.replied}
          </span>
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedCampaign(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'running' && (
            <Button variant="ghost" size="sm">
              <Pause className="h-4 w-4" />
            </Button>
          )}
          {row.status === 'paused' && (
            <Button variant="ghost" size="sm">
              <Play className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const contactColumns: Column<WhatsAppContact>[] = [
    {
      key: 'contact',
      header: 'Contato',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
            <span className="text-white font-medium">
              {row.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
            </span>
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{formatPhone(row.phone)}</p>
          </div>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getContactStatusBadge(row.status)
    },
    {
      key: 'tags',
      header: 'Tags',
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          {row.tags.slice(0, 2).map((tag, i) => (
            <Badge key={i} variant="outline" className="text-xs">{tag}</Badge>
          ))}
          {row.tags.length > 2 && (
            <Badge variant="neutral" className="text-xs">+{row.tags.length - 2}</Badge>
          )}
        </div>
      )
    },
    {
      key: 'interactions',
      header: 'Interações',
      render: (row) => (
        <div className="text-sm">
          <p className="text-text-primary">{row.totalMessages} mensagens</p>
          <p className="text-text-secondary">{row.campaigns} campanhas</p>
        </div>
      )
    },
    {
      key: 'lastInteraction',
      header: 'Última Interação',
      render: (row) => (
        <span className="text-text-secondary">
          {row.lastInteraction ? formatDateTime(row.lastInteraction) : '-'}
        </span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedContact(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <MessageCircle className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  // Filtered data
  const filteredTemplates = mockTemplates.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || t.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const filteredCampaigns = mockCampaigns.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || c.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const filteredConversations = mockConversations.filter(c => {
    const matchesSearch = c.contactName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.contactPhone.includes(searchTerm);
    const matchesStatus = filterStatus === 'all' || c.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const filteredContacts = mockContacts.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.phone.includes(searchTerm);
    const matchesStatus = filterStatus === 'all' || c.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              WhatsApp Business
            </h1>
            <p className="text-text-secondary mt-1">
              Integração com WhatsApp Business API
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Sincronizar
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nova Campanha
            </Button>
          </div>
        </div>

        {/* Connection Status */}
        <Card className="p-4 bg-gradient-to-r from-green-500/10 to-green-600/5 border-green-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                <MessageCircle className="h-6 w-6 text-green-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-text-primary">WhatsApp Business API</h3>
                  <Badge variant="success">Conectado</Badge>
                </div>
                <p className="text-sm text-text-secondary">
                  Número: +55 11 99999-9999 | Conta: Conecta PRO Oficial
                </p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm">
              <div className="text-center">
                <p className="text-text-secondary">Qualidade</p>
                <p className="font-semibold text-green-400">Alta</p>
              </div>
              <div className="text-center">
                <p className="text-text-secondary">Limite/dia</p>
                <p className="font-semibold text-text-primary">10.000</p>
              </div>
              <div className="text-center">
                <p className="text-text-secondary">Usados hoje</p>
                <p className="font-semibold text-text-primary">1.890</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Mensagens Hoje"
            value={totalMessages.toLocaleString('pt-BR')}
            icon={<MessageCircle className="h-5 w-5" />}
            iconColor="success"
            change={12}
            changeLabel="vs ontem"
          />
          <StatCard
            title="Contatos Opt-in"
            value={totalContacts.toLocaleString('pt-BR')}
            icon={<Users className="h-5 w-5" />}
            iconColor="primary"
            change={8}
            changeLabel="este mês"
          />
          <StatCard
            title="Campanhas Ativas"
            value={activeCampaigns.toString()}
            icon={<Send className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Taxa de Resposta"
            value={`${avgResponseRate}%`}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="warning"
            change={5}
            changeLabel="vs média"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Volume de Mensagens por Hora
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={messageVolumeData}>
                    <defs>
                      <linearGradient id="sentGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="receivedGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="hour" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="sent"
                      name="Enviadas"
                      stroke="#6366f1"
                      fill="url(#sentGradient)"
                    />
                    <Area
                      type="monotone"
                      dataKey="received"
                      name="Recebidas"
                      stroke="#10b981"
                      fill="url(#receivedGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

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
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Second Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Performance das Campanhas
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={campaignPerformanceData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#64748b" />
                    <YAxis dataKey="name" type="category" stroke="#64748b" width={100} />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Bar dataKey="delivered" name="Entregues" fill="#10b981" />
                    <Bar dataKey="read" name="Lidas" fill="#6366f1" />
                    <Bar dataKey="replied" name="Respondidas" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Crescimento de Contatos
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={contactGrowthData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="contacts"
                      name="Total Contatos"
                      stroke="#6366f1"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="optIn"
                      name="Com Opt-in"
                      stroke="#10b981"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Quick Actions & Recent */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Ações Rápidas
                </h3>
                <div className="space-y-3">
                  <Button variant="outline" className="w-full justify-start">
                    <Send className="h-4 w-4 mr-3" />
                    Nova Campanha
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <FileText className="h-4 w-4 mr-3" />
                    Criar Template
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Users className="h-4 w-4 mr-3" />
                    Importar Contatos
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Bot className="h-4 w-4 mr-3" />
                    Configurar Chatbot
                  </Button>
                </div>
              </Card>

              <Card className="p-6 col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Conversas Recentes
                  </h3>
                  <Button variant="ghost" size="sm">
                    Ver Todas
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
                <div className="space-y-3">
                  {mockConversations.slice(0, 4).map((conv) => (
                    <div
                      key={conv.id}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-bg-tertiary transition-colors cursor-pointer"
                      onClick={() => setSelectedConversation(conv)}
                    >
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                            <span className="text-white font-medium text-sm">
                              {conv.contactName.split(' ').map(n => n[0]).join('').substring(0, 2)}
                            </span>
                          </div>
                          {conv.unreadCount > 0 && (
                            <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-accent-primary text-white text-xs flex items-center justify-center">
                              {conv.unreadCount}
                            </span>
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{conv.contactName}</p>
                          <p className="text-sm text-text-secondary truncate max-w-xs">
                            {conv.lastMessageType === 'sent' && '✓ '}
                            {conv.lastMessage}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-text-secondary">{formatTime(conv.lastMessageTime)}</p>
                        {getConversationStatusBadge(conv.status)}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar templates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Select
                options={statusOptions}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value)}
                className="w-48"
              />
              <Button onClick={() => setShowAddTemplateModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Novo Template
              </Button>
            </div>

            <DataTable
              data={filteredTemplates}
              columns={templateColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Campaigns Tab */}
        {activeTab === 'campaigns' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar campanhas..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Select
                options={campaignStatusOptions}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value)}
                className="w-48"
              />
              <Button onClick={() => setShowAddCampaignModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Campanha
              </Button>
            </div>

            <DataTable
              data={filteredCampaigns}
              columns={campaignColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Conversations Tab */}
        {activeTab === 'conversations' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Conversation List */}
            <Card className="p-4 lg:col-span-1 h-[600px] overflow-hidden flex flex-col">
              <div className="mb-4">
                <Input
                  placeholder="Buscar conversas..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <div className="flex gap-2 mb-4">
                {['all', 'waiting', 'active'].map((status) => (
                  <Button
                    key={status}
                    variant={filterStatus === status ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => setFilterStatus(status)}
                  >
                    {status === 'all' ? 'Todas' : status === 'waiting' ? 'Aguardando' : 'Ativas'}
                    {status === 'waiting' && (
                      <Badge variant="danger" className="ml-2 text-xs">
                        {mockConversations.filter(c => c.status === 'waiting').length}
                      </Badge>
                    )}
                  </Button>
                ))}
              </div>
              <div className="flex-1 overflow-y-auto space-y-2">
                {filteredConversations.map((conv) => (
                  <div
                    key={conv.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedConversation?.id === conv.id
                        ? 'bg-accent-primary/20 border border-accent-primary/30'
                        : 'hover:bg-bg-tertiary'
                    }`}
                    onClick={() => setSelectedConversation(conv)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                          <span className="text-white font-medium text-sm">
                            {conv.contactName.split(' ').map(n => n[0]).join('').substring(0, 2)}
                          </span>
                        </div>
                        {conv.unreadCount > 0 && (
                          <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-accent-primary text-white text-xs flex items-center justify-center">
                            {conv.unreadCount}
                          </span>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-text-primary truncate">{conv.contactName}</p>
                          <span className="text-xs text-text-secondary">{formatTime(conv.lastMessageTime)}</span>
                        </div>
                        <p className="text-sm text-text-secondary truncate">
                          {conv.lastMessageType === 'sent' && '✓ '}
                          {conv.lastMessage}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Chat Area */}
            <Card className="p-0 lg:col-span-2 h-[600px] flex flex-col overflow-hidden">
              {selectedConversation ? (
                <>
                  {/* Chat Header */}
                  <div className="p-4 border-b border-border-subtle flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                        <span className="text-white font-medium">
                          {selectedConversation.contactName.split(' ').map(n => n[0]).join('').substring(0, 2)}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{selectedConversation.contactName}</p>
                        <p className="text-sm text-text-secondary">{formatPhone(selectedConversation.contactPhone)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getConversationStatusBadge(selectedConversation.status)}
                      <Button variant="ghost" size="sm">
                        <Phone className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {mockMessages
                      .filter(m => m.conversationId === selectedConversation.id)
                      .map((msg) => (
                        <div
                          key={msg.id}
                          className={`flex ${msg.direction === 'sent' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                              msg.direction === 'sent'
                                ? 'bg-green-600 text-white'
                                : 'bg-bg-tertiary text-text-primary'
                            }`}
                          >
                            {msg.type === 'image' && (
                              <div className="mb-2">
                                <div className="h-32 w-48 bg-bg-secondary rounded flex items-center justify-center">
                                  <Image className="h-8 w-8 text-text-secondary" />
                                </div>
                              </div>
                            )}
                            <p>{msg.content}</p>
                            <div className={`flex items-center justify-end gap-1 mt-1 text-xs ${
                              msg.direction === 'sent' ? 'text-green-200' : 'text-text-secondary'
                            }`}>
                              <span>{formatTime(msg.timestamp)}</span>
                              {msg.direction === 'sent' && (
                                <CheckCircle className="h-3 w-3" />
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>

                  {/* Input Area */}
                  <div className="p-4 border-t border-border-subtle">
                    <div className="flex items-center gap-3">
                      <Button variant="ghost" size="sm">
                        <Paperclip className="h-5 w-5" />
                      </Button>
                      <Input
                        placeholder="Digite uma mensagem..."
                        value={messageInput}
                        onChange={(e) => setMessageInput(e.target.value)}
                        className="flex-1"
                      />
                      <Button variant="ghost" size="sm">
                        <Smile className="h-5 w-5" />
                      </Button>
                      <Button>
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <MessageCircle className="h-16 w-16 text-text-secondary mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-text-primary mb-2">
                      Selecione uma conversa
                    </h3>
                    <p className="text-text-secondary">
                      Escolha uma conversa na lista para visualizar as mensagens
                    </p>
                  </div>
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Contacts Tab */}
        {activeTab === 'contacts' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar contatos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'Todos os Status' },
                  { value: 'active', label: 'Ativos' },
                  { value: 'opted_out', label: 'Opt-out' },
                  { value: 'blocked', label: 'Bloqueados' }
                ]}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value)}
                className="w-48"
              />
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Button onClick={() => setShowAddContactModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Adicionar Contato
              </Button>
            </div>

            <DataTable
              data={filteredContacts}
              columns={contactColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Template Detail Modal */}
        <Modal
          isOpen={!!selectedTemplate}
          onClose={() => setSelectedTemplate(null)}
          title="Detalhes do Template"
          size="lg"
        >
          {selectedTemplate && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">{selectedTemplate.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    {getCategoryBadge(selectedTemplate.category)}
                    {getTemplateStatusBadge(selectedTemplate.status)}
                    <Badge variant="neutral">{selectedTemplate.language}</Badge>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-text-secondary">Usado</p>
                  <p className="text-xl font-bold text-text-primary">
                    {selectedTemplate.usageCount.toLocaleString('pt-BR')}x
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-bg-tertiary border border-border-subtle">
                {selectedTemplate.headerType !== 'none' && (
                  <div className="mb-3 pb-3 border-b border-border-subtle">
                    {selectedTemplate.headerType === 'text' && (
                      <p className="font-semibold text-text-primary">{selectedTemplate.headerContent}</p>
                    )}
                    {selectedTemplate.headerType === 'image' && (
                      <div className="h-32 bg-bg-secondary rounded flex items-center justify-center">
                        <Image className="h-8 w-8 text-text-secondary" />
                        <span className="ml-2 text-text-secondary">{selectedTemplate.headerContent}</span>
                      </div>
                    )}
                  </div>
                )}
                <p className="text-text-primary whitespace-pre-wrap">{selectedTemplate.content}</p>
                {selectedTemplate.footerText && (
                  <p className="mt-3 pt-3 border-t border-border-subtle text-sm text-text-secondary">
                    {selectedTemplate.footerText}
                  </p>
                )}
                {selectedTemplate.buttons.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border-subtle space-y-2">
                    {selectedTemplate.buttons.map((btn, i) => (
                      <Button key={i} variant="outline" className="w-full">
                        {btn.type === 'url' && <Zap className="h-4 w-4 mr-2" />}
                        {btn.type === 'phone' && <Phone className="h-4 w-4 mr-2" />}
                        {btn.type === 'quick_reply' && <MessageCircle className="h-4 w-4 mr-2" />}
                        {btn.text}
                      </Button>
                    ))}
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Variáveis</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedTemplate.variables.map((v, i) => (
                      <Badge key={i} variant="outline">{'{{' + (i + 1) + '}} - ' + v}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Último uso</p>
                  <p className="text-text-primary">
                    {selectedTemplate.lastUsed ? formatDateTime(selectedTemplate.lastUsed) : 'Nunca usado'}
                  </p>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedTemplate(null)}>
                  Fechar
                </Button>
                <Button variant="outline">
                  <Copy className="h-4 w-4 mr-2" />
                  Duplicar
                </Button>
                <Button>
                  <Send className="h-4 w-4 mr-2" />
                  Usar em Campanha
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Campaign Detail Modal */}
        <Modal
          isOpen={!!selectedCampaign}
          onClose={() => setSelectedCampaign(null)}
          title="Detalhes da Campanha"
          size="lg"
        >
          {selectedCampaign && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">{selectedCampaign.name}</h3>
                  <p className="text-sm text-text-secondary mt-1">
                    Template: {selectedCampaign.templateName}
                  </p>
                </div>
                {getCampaignStatusBadge(selectedCampaign.status)}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-text-primary">
                    {selectedCampaign.totalRecipients.toLocaleString('pt-BR')}
                  </p>
                  <p className="text-sm text-text-secondary">Total</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-green-400">
                    {selectedCampaign.delivered.toLocaleString('pt-BR')}
                  </p>
                  <p className="text-sm text-text-secondary">Entregues</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-blue-400">
                    {selectedCampaign.read.toLocaleString('pt-BR')}
                  </p>
                  <p className="text-sm text-text-secondary">Lidas</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-purple-400">
                    {selectedCampaign.replied.toLocaleString('pt-BR')}
                  </p>
                  <p className="text-sm text-text-secondary">Respondidas</p>
                </div>
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-text-secondary">Progresso</span>
                  <span className="text-sm font-medium text-text-primary">
                    {selectedCampaign.sent} / {selectedCampaign.totalRecipients}
                  </span>
                </div>
                <div className="h-3 bg-bg-tertiary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                    style={{
                      width: `${(selectedCampaign.sent / selectedCampaign.totalRecipients) * 100}%`
                    }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Público-alvo</p>
                  <p className="text-text-primary">{selectedCampaign.targetAudience}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Falhas</p>
                  <p className="text-red-400">{selectedCampaign.failed} mensagens</p>
                </div>
                {selectedCampaign.scheduledAt && (
                  <div>
                    <p className="text-sm text-text-secondary">Agendada para</p>
                    <p className="text-text-primary">{formatDateTime(selectedCampaign.scheduledAt)}</p>
                  </div>
                )}
                {selectedCampaign.startedAt && (
                  <div>
                    <p className="text-sm text-text-secondary">Iniciada em</p>
                    <p className="text-text-primary">{formatDateTime(selectedCampaign.startedAt)}</p>
                  </div>
                )}
                {selectedCampaign.completedAt && (
                  <div>
                    <p className="text-sm text-text-secondary">Concluída em</p>
                    <p className="text-text-primary">{formatDateTime(selectedCampaign.completedAt)}</p>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedCampaign(null)}>
                  Fechar
                </Button>
                {selectedCampaign.status === 'running' && (
                  <Button variant="outline">
                    <Pause className="h-4 w-4 mr-2" />
                    Pausar
                  </Button>
                )}
                {selectedCampaign.status === 'paused' && (
                  <Button>
                    <Play className="h-4 w-4 mr-2" />
                    Retomar
                  </Button>
                )}
                {selectedCampaign.status === 'scheduled' && (
                  <Button variant="danger">
                    <XCircle className="h-4 w-4 mr-2" />
                    Cancelar
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* Contact Detail Modal */}
        <Modal
          isOpen={!!selectedContact}
          onClose={() => setSelectedContact(null)}
          title="Detalhes do Contato"
          size="lg"
        >
          {selectedContact && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">
                    {selectedContact.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-text-primary">{selectedContact.name}</h3>
                  <p className="text-text-secondary">{formatPhone(selectedContact.phone)}</p>
                  {selectedContact.email && (
                    <p className="text-text-secondary text-sm">{selectedContact.email}</p>
                  )}
                </div>
                {getContactStatusBadge(selectedContact.status)}
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedContact.totalMessages}</p>
                  <p className="text-sm text-text-secondary">Mensagens</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedContact.campaigns}</p>
                  <p className="text-sm text-text-secondary">Campanhas</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-text-primary">
                    {selectedContact.optIn ? 'Sim' : 'Não'}
                  </p>
                  <p className="text-sm text-text-secondary">Opt-in</p>
                </div>
              </div>

              {selectedContact.tags.length > 0 && (
                <div>
                  <p className="text-sm text-text-secondary mb-2">Tags</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedContact.tags.map((tag, i) => (
                      <Badge key={i} variant="outline">{tag}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {Object.keys(selectedContact.customFields).length > 0 && (
                <div>
                  <p className="text-sm text-text-secondary mb-2">Campos Personalizados</p>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(selectedContact.customFields).map(([key, value]) => (
                      <div key={key} className="p-3 rounded-lg bg-bg-tertiary">
                        <p className="text-xs text-text-secondary capitalize">{key}</p>
                        <p className="text-text-primary">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Opt-in em</p>
                  <p className="text-text-primary">
                    {selectedContact.optInDate ? formatDate(selectedContact.optInDate) : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Última interação</p>
                  <p className="text-text-primary">
                    {selectedContact.lastInteraction ? formatDateTime(selectedContact.lastInteraction) : '-'}
                  </p>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedContact(null)}>
                  Fechar
                </Button>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
                <Button>
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Iniciar Conversa
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Add Template Modal */}
        <Modal
          isOpen={showAddTemplateModal}
          onClose={() => setShowAddTemplateModal(false)}
          title="Novo Template"
          size="lg"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nome do Template
              </label>
              <Input placeholder="Ex: boas_vindas_cliente" />
              <p className="text-xs text-text-secondary mt-1">
                Use letras minúsculas e underscores. Sem espaços ou caracteres especiais.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Categoria
                </label>
                <Select
                  options={[
                    { value: 'utility', label: 'Utilidade' },
                    { value: 'marketing', label: 'Marketing' },
                    { value: 'authentication', label: 'Autenticação' }
                  ]}
                  value={newTemplateCategory}
                  onChange={(value) => setNewTemplateCategory(value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Idioma
                </label>
                <Select
                  options={[
                    { value: 'pt_BR', label: 'Português (Brasil)' },
                    { value: 'en', label: 'English' },
                    { value: 'es', label: 'Español' }
                  ]}
                  value={newTemplateLanguage}
                  onChange={(value) => setNewTemplateLanguage(value)}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Conteúdo da Mensagem
              </label>
              <textarea
                className="w-full h-32 px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary placeholder-text-muted resize-none focus:outline-none focus:border-accent-primary"
                placeholder="Digite o conteúdo da mensagem. Use {{1}}, {{2}}, etc. para variáveis."
              />
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowAddTemplateModal(false)}>
                Cancelar
              </Button>
              <Button>
                Enviar para Aprovação
              </Button>
            </div>
          </div>
        </Modal>

        {/* Add Campaign Modal */}
        <Modal
          isOpen={showAddCampaignModal}
          onClose={() => setShowAddCampaignModal(false)}
          title="Nova Campanha"
          size="lg"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nome da Campanha
              </label>
              <Input placeholder="Ex: Promoção de Janeiro" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Template
              </label>
              <Select
                options={mockTemplates.filter(t => t.status === 'approved').map(t => ({
                  value: t.id,
                  label: t.name
                }))}
                value={newCampaignTemplate}
                onChange={(value) => setNewCampaignTemplate(value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Público-alvo
              </label>
              <Select
                options={[
                  { value: 'all', label: 'Todos os contatos com opt-in' },
                  { value: 'new', label: 'Novos contatos (últimos 30 dias)' },
                  { value: 'active', label: 'Contatos ativos' },
                  { value: 'custom', label: 'Seleção personalizada' }
                ]}
                value={newCampaignAudience}
                onChange={(value) => setNewCampaignAudience(value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Agendamento
              </label>
              <div className="flex gap-3">
                <Button variant="outline" className="flex-1">
                  Enviar Agora
                </Button>
                <Button variant="outline" className="flex-1">
                  <Calendar className="h-4 w-4 mr-2" />
                  Agendar
                </Button>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowAddCampaignModal(false)}>
                Cancelar
              </Button>
              <Button>
                Criar Campanha
              </Button>
            </div>
          </div>
        </Modal>

        {/* Add Contact Modal */}
        <Modal
          isOpen={showAddContactModal}
          onClose={() => setShowAddContactModal(false)}
          title="Adicionar Contato"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nome
              </label>
              <Input placeholder="Nome completo" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Telefone
              </label>
              <Input placeholder="+55 11 99999-9999" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Email (opcional)
              </label>
              <Input placeholder="email@exemplo.com" type="email" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Tags
              </label>
              <Input placeholder="Separar por vírgulas" />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="optIn" className="rounded" />
              <label htmlFor="optIn" className="text-sm text-text-secondary">
                Contato consentiu em receber mensagens (Opt-in)
              </label>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowAddContactModal(false)}>
                Cancelar
              </Button>
              <Button>
                Adicionar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
