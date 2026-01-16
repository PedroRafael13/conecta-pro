'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Phone,
  Mail,
  Building2,
  Calendar,
  TrendingUp,
  TrendingDown,
  Users,
  Target,
  ArrowRight,
  Star,
  CheckCircle2,
  Clock,
  XCircle,
  Eye,
  Edit,
  Trash2,
  Download,
  Upload,
  RefreshCw,
  MessageSquare,
  Activity,
  ChevronRight,
  ChevronDown,
  Zap,
  UserPlus,
  Globe,
  Linkedin,
  MapPin,
  DollarSign,
  Percent,
  BarChart3,
  PieChart as PieChartIcon,
  Send,
  Copy,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  XCircle as XCircleIcon,
  Info,
  Sparkles,
  Brain,
  History,
  FileText,
  Tag,
  Kanban,
  List,
  LayoutGrid
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
  SimpleTabBar
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
  LineChart,
  Line,
  Area,
  AreaChart,
  Legend
} from 'recharts';

// ==================== TYPES ====================

interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  position: string;
  source: 'website' | 'indicacao' | 'linkedin' | 'evento' | 'cold_call' | 'google_ads' | 'facebook' | 'outro';
  status: 'new' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';
  score: number;
  value: number;
  assignedTo: string;
  assignedToAvatar?: string;
  createdAt: string;
  lastContact: string | null;
  nextAction: string | null;
  nextActionDate: string | null;
  tags: string[];
  notes: string;
  segment: string;
  city: string;
  state: string;
  interestLevel: 'hot' | 'warm' | 'cold';
}

interface LeadActivity {
  id: string;
  leadId: string;
  type: 'call' | 'email' | 'meeting' | 'note' | 'status_change' | 'task';
  title: string;
  description: string;
  createdAt: string;
  createdBy: string;
}

interface LeadStats {
  total: number;
  byStatus: Record<string, number>;
  bySource: Record<string, number>;
  conversionRate: number;
  avgValue: number;
  avgScore: number;
}

interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  render?: (row: T) => React.ReactNode;
}

// ==================== CONSTANTS ====================

const STATUS_CONFIG: Record<string, { label: string; variant: any; icon: any }> = {
  new: { label: 'Novo', variant: 'info', icon: Star },
  contacted: { label: 'Contatado', variant: 'primary', icon: Phone },
  qualified: { label: 'Qualificado', variant: 'secondary', icon: CheckCircle2 },
  proposal: { label: 'Proposta', variant: 'warning', icon: FileText },
  negotiation: { label: 'Negociação', variant: 'primary', icon: TrendingUp },
  won: { label: 'Ganho', variant: 'success', icon: CheckCircle2 },
  lost: { label: 'Perdido', variant: 'danger', icon: XCircle },
};

const SOURCE_CONFIG: Record<string, { label: string; icon: any }> = {
  website: { label: 'Website', icon: Globe },
  indicacao: { label: 'Indicação', icon: Users },
  linkedin: { label: 'LinkedIn', icon: Linkedin },
  evento: { label: 'Evento', icon: Calendar },
  cold_call: { label: 'Cold Call', icon: Phone },
  google_ads: { label: 'Google Ads', icon: Target },
  facebook: { label: 'Facebook', icon: MessageSquare },
  outro: { label: 'Outro', icon: Info },
};

const INTEREST_CONFIG: Record<string, { label: string; variant: any }> = {
  hot: { label: 'Quente', variant: 'danger' },
  warm: { label: 'Morno', variant: 'warning' },
  cold: { label: 'Frio', variant: 'info' },
};

// ==================== MOCK DATA ====================

const mockLeads: Lead[] = [
  {
    id: 'LEAD001',
    name: 'João Silva',
    email: 'joao.silva@techsolutions.com.br',
    phone: '(11) 99999-1234',
    company: 'Tech Solutions Ltda',
    position: 'Diretor de Operações',
    source: 'website',
    status: 'qualified',
    score: 85,
    value: 45000,
    assignedTo: 'Ana Costa',
    createdAt: '2026-01-15',
    lastContact: '2026-01-14',
    nextAction: 'Agendar apresentação',
    nextActionDate: '2026-01-18',
    tags: ['B2B', 'Segurança', 'Grande porte'],
    notes: 'Cliente interessado em segurança 24h',
    segment: 'Tecnologia',
    city: 'São Paulo',
    state: 'SP',
    interestLevel: 'hot',
  },
  {
    id: 'LEAD002',
    name: 'Maria Santos',
    email: 'maria.santos@corpbrasil.com',
    phone: '(21) 98888-5678',
    company: 'Corp Brasil SA',
    position: 'Gerente Administrativo',
    source: 'indicacao',
    status: 'proposal',
    score: 92,
    value: 78000,
    assignedTo: 'Carlos Lima',
    createdAt: '2026-01-14',
    lastContact: '2026-01-15',
    nextAction: 'Enviar proposta revisada',
    nextActionDate: '2026-01-17',
    tags: ['B2B', 'Facilities', 'Médio porte'],
    notes: 'Proposta em análise pelo financeiro',
    segment: 'Financeiro',
    city: 'Rio de Janeiro',
    state: 'RJ',
    interestLevel: 'hot',
  },
  {
    id: 'LEAD003',
    name: 'Pedro Oliveira',
    email: 'pedro@startupinova.io',
    phone: '(31) 97777-9012',
    company: 'Startup Inova',
    position: 'CEO',
    source: 'linkedin',
    status: 'new',
    score: 65,
    value: 32000,
    assignedTo: 'Ana Costa',
    createdAt: '2026-01-13',
    lastContact: null,
    nextAction: 'Fazer primeiro contato',
    nextActionDate: '2026-01-16',
    tags: ['Startup', 'Tecnologia'],
    notes: 'Encontrado via LinkedIn, muito engajado',
    segment: 'Tecnologia',
    city: 'Belo Horizonte',
    state: 'MG',
    interestLevel: 'warm',
  },
  {
    id: 'LEAD004',
    name: 'Ana Pereira',
    email: 'ana.pereira@megaemp.com.br',
    phone: '(41) 96666-3456',
    company: 'Mega Empreendimentos',
    position: 'Diretora Comercial',
    source: 'evento',
    status: 'contacted',
    score: 78,
    value: 95000,
    assignedTo: 'Roberto Dias',
    createdAt: '2026-01-12',
    lastContact: '2026-01-13',
    nextAction: 'Enviar material institucional',
    nextActionDate: '2026-01-15',
    tags: ['B2B', 'Condomínio', 'Grande porte'],
    notes: 'Conhecida na feira de facilities',
    segment: 'Imobiliário',
    city: 'Curitiba',
    state: 'PR',
    interestLevel: 'warm',
  },
  {
    id: 'LEAD005',
    name: 'Lucas Mendes',
    email: 'lucas.mendes@globalservices.com',
    phone: '(51) 95555-7890',
    company: 'Global Services Corp',
    position: 'Gerente de Compras',
    source: 'cold_call',
    status: 'negotiation',
    score: 88,
    value: 120000,
    assignedTo: 'Carlos Lima',
    createdAt: '2026-01-11',
    lastContact: '2026-01-15',
    nextAction: 'Negociar valores',
    nextActionDate: '2026-01-16',
    tags: ['B2B', 'Segurança', 'Multinacional'],
    notes: 'Negociação avançada, aguardando aprovação',
    segment: 'Serviços',
    city: 'Porto Alegre',
    state: 'RS',
    interestLevel: 'hot',
  },
  {
    id: 'LEAD006',
    name: 'Fernanda Costa',
    email: 'fernanda@hospitalvida.org.br',
    phone: '(11) 94444-2345',
    company: 'Hospital Vida',
    position: 'Coordenadora de Facilities',
    source: 'google_ads',
    status: 'qualified',
    score: 82,
    value: 68000,
    assignedTo: 'Ana Costa',
    createdAt: '2026-01-10',
    lastContact: '2026-01-14',
    nextAction: 'Agendar visita técnica',
    nextActionDate: '2026-01-19',
    tags: ['Saúde', 'Limpeza', 'Segurança'],
    notes: 'Hospital privado, exige certificações',
    segment: 'Saúde',
    city: 'São Paulo',
    state: 'SP',
    interestLevel: 'warm',
  },
  {
    id: 'LEAD007',
    name: 'Ricardo Almeida',
    email: 'ricardo@shoppingcenter.com.br',
    phone: '(11) 93333-6789',
    company: 'Shopping Center Leste',
    position: 'Gerente Geral',
    source: 'indicacao',
    status: 'won',
    score: 95,
    value: 150000,
    assignedTo: 'Roberto Dias',
    createdAt: '2026-01-05',
    lastContact: '2026-01-15',
    nextAction: null,
    nextActionDate: null,
    tags: ['B2B', 'Shopping', 'Grande porte'],
    notes: 'Contrato assinado, início em fevereiro',
    segment: 'Varejo',
    city: 'São Paulo',
    state: 'SP',
    interestLevel: 'hot',
  },
  {
    id: 'LEAD008',
    name: 'Carla Souza',
    email: 'carla@condminioaurora.com.br',
    phone: '(21) 92222-1234',
    company: 'Condomínio Aurora',
    position: 'Síndica',
    source: 'website',
    status: 'lost',
    score: 45,
    value: 25000,
    assignedTo: 'Carlos Lima',
    createdAt: '2026-01-08',
    lastContact: '2026-01-12',
    nextAction: null,
    nextActionDate: null,
    tags: ['Residencial', 'Pequeno porte'],
    notes: 'Optou por concorrente por preço',
    segment: 'Residencial',
    city: 'Rio de Janeiro',
    state: 'RJ',
    interestLevel: 'cold',
  },
];

const mockActivities: LeadActivity[] = [
  {
    id: 'ACT001',
    leadId: 'LEAD001',
    type: 'email',
    title: 'Email de apresentação enviado',
    description: 'Enviado material institucional e casos de sucesso',
    createdAt: '2026-01-14T10:30:00',
    createdBy: 'Ana Costa'
  },
  {
    id: 'ACT002',
    leadId: 'LEAD001',
    type: 'call',
    title: 'Ligação de qualificação',
    description: 'Conversa de 15 min, confirmou interesse em segurança 24h',
    createdAt: '2026-01-13T14:00:00',
    createdBy: 'Ana Costa'
  },
  {
    id: 'ACT003',
    leadId: 'LEAD001',
    type: 'status_change',
    title: 'Status alterado para Qualificado',
    description: 'Lead qualificado após call de discovery',
    createdAt: '2026-01-13T14:30:00',
    createdBy: 'Ana Costa'
  },
  {
    id: 'ACT004',
    leadId: 'LEAD001',
    type: 'meeting',
    title: 'Reunião agendada',
    description: 'Apresentação comercial marcada para 18/01',
    createdAt: '2026-01-14T16:00:00',
    createdBy: 'Ana Costa'
  },
];

// Chart data
const sourceDistribution = [
  { name: 'Website', value: 35, color: '#6366f1' },
  { name: 'Indicação', value: 25, color: '#10b981' },
  { name: 'LinkedIn', value: 15, color: '#0077b5' },
  { name: 'Eventos', value: 12, color: '#f59e0b' },
  { name: 'Google Ads', value: 8, color: '#ef4444' },
  { name: 'Outros', value: 5, color: '#64748b' },
];

const conversionFunnel = [
  { stage: 'Novos', count: 45, value: 850000 },
  { stage: 'Contatados', count: 35, value: 720000 },
  { stage: 'Qualificados', count: 22, value: 580000 },
  { stage: 'Proposta', count: 15, value: 420000 },
  { stage: 'Negociação', count: 8, value: 280000 },
  { stage: 'Ganhos', count: 5, value: 150000 },
];

const weeklyLeads = [
  { week: 'Sem 1', novos: 12, convertidos: 3 },
  { week: 'Sem 2', novos: 15, convertidos: 4 },
  { week: 'Sem 3', novos: 18, convertidos: 5 },
  { week: 'Sem 4', novos: 14, convertidos: 4 },
];

const scoreDistribution = [
  { range: '0-20', count: 2 },
  { range: '21-40', count: 5 },
  { range: '41-60', count: 12 },
  { range: '61-80', count: 18 },
  { range: '81-100', count: 8 },
];

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string) => {
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

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'call': return <Phone className="h-4 w-4" />;
    case 'email': return <Mail className="h-4 w-4" />;
    case 'meeting': return <Calendar className="h-4 w-4" />;
    case 'note': return <FileText className="h-4 w-4" />;
    case 'status_change': return <Activity className="h-4 w-4" />;
    case 'task': return <CheckCircle2 className="h-4 w-4" />;
    default: return <Info className="h-4 w-4" />;
  }
};

// Custom Tooltip
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
  const [activeTab, setActiveTab] = useState('list');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [selectedInterest, setSelectedInterest] = useState('all');
  const [showNewLeadModal, setShowNewLeadModal] = useState(false);
  const [showLeadDetailModal, setShowLeadDetailModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [viewMode, setViewMode] = useState<'table' | 'cards' | 'kanban'>('table');

  // Filter leads
  const filteredLeads = mockLeads.filter((lead) => {
    const matchesSearch =
      lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === 'all' || lead.status === selectedStatus;
    const matchesSource = selectedSource === 'all' || lead.source === selectedSource;
    const matchesInterest = selectedInterest === 'all' || lead.interestLevel === selectedInterest;
    return matchesSearch && matchesStatus && matchesSource && matchesInterest;
  });

  // Calculate stats
  const totalValue = mockLeads.reduce((acc, lead) => acc + lead.value, 0);
  const avgScore = Math.round(mockLeads.reduce((acc, lead) => acc + lead.score, 0) / mockLeads.length);
  const hotLeads = mockLeads.filter(l => l.interestLevel === 'hot').length;
  const conversionRate = (mockLeads.filter(l => l.status === 'won').length / mockLeads.length * 100).toFixed(1);

  const tabs = [
    { value: 'list', label: 'Lista', icon: <List className="h-4 w-4" /> },
    { value: 'overview', label: 'Overview', icon: <BarChart3 className="h-4 w-4" /> },
    { value: 'funnel', label: 'Funil', icon: <TrendingUp className="h-4 w-4" /> },
  ];

  const columns: Column<Lead>[] = [
    {
      key: 'name',
      header: 'Lead',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.name} size="sm" />
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.company}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'contact',
      header: 'Contato',
      render: (row) => (
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Mail className="h-3 w-3" />
            <span className="truncate max-w-[180px]">{row.email}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Phone className="h-3 w-3" />
            {row.phone}
          </div>
        </div>
      ),
    },
    {
      key: 'source',
      header: 'Origem',
      render: (row) => {
        const source = SOURCE_CONFIG[row.source];
        return (
          <div className="flex items-center gap-2">
            <source.icon className="h-4 w-4 text-text-muted" />
            <span className="text-sm">{source.label}</span>
          </div>
        );
      },
    },
    {
      key: 'score',
      header: 'Score',
      sortable: true,
      render: (row) => (
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
      render: (row) => {
        const interest = INTEREST_CONFIG[row.interestLevel];
        return <Badge variant={interest.variant}>{interest.label}</Badge>;
      },
    },
    {
      key: 'value',
      header: 'Valor',
      sortable: true,
      render: (row) => (
        <span className="font-mono font-medium text-text-primary">
          {formatCurrency(row.value)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const status = STATUS_CONFIG[row.status];
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
      key: 'assignedTo',
      header: 'Responsável',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Avatar name={row.assignedTo} size="xs" />
          <span className="text-sm text-text-secondary">{row.assignedTo}</span>
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
            onClick={() => {
              setSelectedLead(row);
              setShowLeadDetailModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <MoreHorizontal className="h-4 w-4" />
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
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total de Leads"
              value={mockLeads.length.toString()}
              change={12}
              changeLabel="+5 esta semana"
              icon={<Users className="h-5 w-5" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Leads Quentes"
              value={hotLeads.toString()}
              change={25}
              changeLabel="prioridade alta"
              icon={<Zap className="h-5 w-5" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Valor no Pipeline"
              value={formatCurrency(totalValue)}
              change={8.5}
              changeLabel="potencial"
              icon={<DollarSign className="h-5 w-5" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Score Médio"
              value={avgScore.toString()}
              change={5.2}
              changeLabel="qualidade"
              icon={<Target className="h-5 w-5" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <StatCard
              title="Conversão"
              value={`${conversionRate}%`}
              change={3.1}
              changeLabel="taxa"
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
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Card>
                  <CardHeader
                    title={`${filteredLeads.length} leads encontrados`}
                    action={
                      <Button variant="ghost" size="sm">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Atualizar
                      </Button>
                    }
                  />
                  <CardBody className="p-0">
                    <DataTable
                      columns={columns}
                      data={filteredLeads}
                      keyExtractor={(row) => row.id}
                    />
                  </CardBody>
                </Card>
              </motion.div>
            )}

            {/* Cards View */}
            {viewMode === 'cards' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredLeads.map((lead) => (
                  <motion.div
                    key={lead.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Card className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                      <CardBody>
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <Avatar name={lead.name} size="md" />
                            <div>
                              <p className="font-semibold text-text-primary">{lead.name}</p>
                              <p className="text-sm text-text-secondary">{lead.company}</p>
                            </div>
                          </div>
                          <Badge variant={STATUS_CONFIG[lead.status].variant}>
                            {STATUS_CONFIG[lead.status].label}
                          </Badge>
                        </div>

                        <div className="space-y-2 mb-4">
                          <div className="flex items-center gap-2 text-sm text-text-secondary">
                            <Mail className="h-4 w-4" />
                            <span className="truncate">{lead.email}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-text-secondary">
                            <Phone className="h-4 w-4" />
                            {lead.phone}
                          </div>
                          <div className="flex items-center gap-2 text-sm text-text-secondary">
                            <MapPin className="h-4 w-4" />
                            {lead.city}, {lead.state}
                          </div>
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
                              {formatCurrency(lead.value)}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 mb-4">
                          {lead.tags.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
                          <div className="flex items-center gap-2">
                            <Avatar name={lead.assignedTo} size="xs" />
                            <span className="text-xs text-text-muted">{lead.assignedTo}</span>
                          </div>
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
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      />
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
                      <span className="text-sm font-medium text-text-primary">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Weekly Trend */}
            <Card>
              <CardHeader title="Tendência Semanal" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={weeklyLeads}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="week" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Bar dataKey="novos" name="Novos Leads" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="convertidos" name="Convertidos" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            {/* Score Distribution */}
            <Card>
              <CardHeader title="Distribuição de Score" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={scoreDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="range" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="count" name="Quantidade" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            {/* Top Performers */}
            <Card>
              <CardHeader title="Top Leads por Valor" />
              <CardBody>
                <div className="space-y-4">
                  {mockLeads
                    .sort((a, b) => b.value - a.value)
                    .slice(0, 5)
                    .map((lead, index) => (
                      <div key={lead.id} className="flex items-center gap-4">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-bg-tertiary text-text-secondary font-medium">
                          {index + 1}
                        </div>
                        <Avatar name={lead.name} size="sm" />
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{lead.name}</p>
                          <p className="text-xs text-text-secondary">{lead.company}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono font-semibold text-accent-success">
                            {formatCurrency(lead.value)}
                          </p>
                          <Badge variant={STATUS_CONFIG[lead.status].variant} className="text-xs">
                            {STATUS_CONFIG[lead.status].label}
                          </Badge>
                        </div>
                      </div>
                    ))}
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
                  {conversionFunnel.map((stage, index) => {
                    const prevCount = index > 0 ? conversionFunnel[index - 1].count : stage.count;
                    const conversion = ((stage.count / prevCount) * 100).toFixed(1);
                    const widthPercent = (stage.count / conversionFunnel[0].count) * 100;

                    return (
                      <div key={stage.stage}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <span className="text-text-primary font-medium">{stage.stage}</span>
                            {index > 0 && (
                              <Badge variant="outline" className="text-xs">
                                {conversion}% conversão
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-text-secondary">
                              {stage.count} leads
                            </span>
                            <span className="font-mono text-text-primary">
                              {formatCurrency(stage.value)}
                            </span>
                          </div>
                        </div>
                        <div className="h-10 bg-bg-tertiary rounded-lg overflow-hidden">
                          <div
                            className="h-full rounded-lg transition-all flex items-center justify-center"
                            style={{
                              width: `${widthPercent}%`,
                              backgroundColor: index === conversionFunnel.length - 1 ? '#10b981' : '#6366f1',
                              opacity: 1 - (index * 0.12)
                            }}
                          >
                            <span className="text-sm font-medium text-white">
                              {widthPercent.toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="mt-8 grid grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                    <p className="text-text-secondary text-sm">Taxa de Conversão Total</p>
                    <p className="text-3xl font-bold text-accent-success mt-2">
                      {((conversionFunnel[5].count / conversionFunnel[0].count) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                    <p className="text-text-secondary text-sm">Valor Total Ganho</p>
                    <p className="text-3xl font-bold text-text-primary mt-2">
                      {formatCurrency(conversionFunnel[5].value)}
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                    <p className="text-text-secondary text-sm">Ticket Médio</p>
                    <p className="text-3xl font-bold text-text-primary mt-2">
                      {formatCurrency(conversionFunnel[5].value / conversionFunnel[5].count)}
                    </p>
                  </div>
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
              <Input label="Nome Completo" placeholder="Nome do contato" />
              <Input label="Email" type="email" placeholder="email@empresa.com" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Telefone" placeholder="(00) 00000-0000" />
              <Input label="Empresa" placeholder="Nome da empresa" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Cargo" placeholder="Cargo/Posição" />
              <Select
                label="Origem"
                options={Object.entries(SOURCE_CONFIG).map(([key, config]) => ({
                  value: key,
                  label: config.label
                }))}
                value=""
                onChange={() => {}}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Cidade" placeholder="Cidade" />
              <Input label="Estado" placeholder="UF" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Valor Estimado" placeholder="R$ 0,00" />
              <Select
                label="Interesse"
                options={[
                  { value: 'hot', label: 'Quente' },
                  { value: 'warm', label: 'Morno' },
                  { value: 'cold', label: 'Frio' },
                ]}
                value=""
                onChange={() => {}}
              />
            </div>
            <Input label="Observações" placeholder="Notas sobre o lead..." />

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewLeadModal(false)}>
                Cancelar
              </Button>
              <Button onClick={() => setShowNewLeadModal(false)}>
                Criar Lead
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
                    <p className="text-text-secondary">{selectedLead.position} em {selectedLead.company}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={STATUS_CONFIG[selectedLead.status].variant}>
                        {STATUS_CONFIG[selectedLead.status].label}
                      </Badge>
                      <Badge variant={INTEREST_CONFIG[selectedLead.interestLevel].variant}>
                        {INTEREST_CONFIG[selectedLead.interestLevel].label}
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
                    {formatCurrency(selectedLead.value)}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Responsável</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Avatar name={selectedLead.assignedTo} size="sm" />
                    <span className="font-medium text-text-primary">{selectedLead.assignedTo}</span>
                  </div>
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
                    <div className="flex items-center gap-3">
                      <Phone className="h-4 w-4 text-text-muted" />
                      <span className="text-text-secondary">{selectedLead.phone}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Building2 className="h-4 w-4 text-text-muted" />
                      <span className="text-text-secondary">{selectedLead.company}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <MapPin className="h-4 w-4 text-text-muted" />
                      <span className="text-text-secondary">{selectedLead.city}, {selectedLead.state}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Próxima Ação</h4>
                  {selectedLead.nextAction ? (
                    <div className="p-4 rounded-lg bg-accent-warning/10 border border-accent-warning/30">
                      <p className="font-medium text-text-primary">{selectedLead.nextAction}</p>
                      <p className="text-sm text-text-secondary mt-1">
                        Agendado para: {selectedLead.nextActionDate ? formatDate(selectedLead.nextActionDate) : '-'}
                      </p>
                    </div>
                  ) : (
                    <p className="text-text-muted">Nenhuma ação agendada</p>
                  )}
                </div>
              </div>

              {/* Tags */}
              <div>
                <h4 className="font-semibold text-text-primary mb-3">Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedLead.tags.map((tag) => (
                    <Badge key={tag} variant="outline">
                      <Tag className="h-3 w-3 mr-1" />
                      {tag}
                    </Badge>
                  ))}
                  <Button variant="ghost" size="sm">
                    <Plus className="h-3 w-3 mr-1" />
                    Adicionar tag
                  </Button>
                </div>
              </div>

              {/* Activities */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-text-primary">Histórico de Atividades</h4>
                  <Button variant="outline" size="sm" onClick={() => setShowActivityModal(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Nova Atividade
                  </Button>
                </div>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {mockActivities
                    .filter(a => a.leadId === selectedLead.id)
                    .map((activity) => (
                      <div
                        key={activity.id}
                        className="flex items-start gap-3 p-3 rounded-lg bg-bg-tertiary"
                      >
                        <div className={`p-2 rounded-lg ${
                          activity.type === 'call' ? 'bg-accent-success/20 text-accent-success' :
                          activity.type === 'email' ? 'bg-accent-primary/20 text-accent-primary' :
                          activity.type === 'meeting' ? 'bg-accent-warning/20 text-accent-warning' :
                          'bg-bg-secondary text-text-secondary'
                        }`}>
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{activity.title}</p>
                          <p className="text-sm text-text-secondary">{activity.description}</p>
                          <div className="flex items-center gap-2 mt-1 text-xs text-text-muted">
                            <Clock className="h-3 w-3" />
                            {new Date(activity.createdAt).toLocaleString('pt-BR')}
                            <span>•</span>
                            {activity.createdBy}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <h4 className="font-semibold text-text-primary mb-3">Observações</h4>
                <p className="text-text-secondary p-4 rounded-lg bg-bg-tertiary">
                  {selectedLead.notes}
                </p>
              </div>
            </div>
          )}
        </Modal>

        {/* Activity Modal */}
        <Modal
          isOpen={showActivityModal}
          onClose={() => setShowActivityModal(false)}
          title="Nova Atividade"
          size="md"
        >
          <div className="space-y-4">
            <Select
              label="Tipo de Atividade"
              options={[
                { value: 'call', label: 'Ligação' },
                { value: 'email', label: 'Email' },
                { value: 'meeting', label: 'Reunião' },
                { value: 'note', label: 'Nota' },
                { value: 'task', label: 'Tarefa' },
              ]}
              value=""
              onChange={() => {}}
            />
            <Input label="Título" placeholder="Descreva brevemente..." />
            <Input label="Descrição" placeholder="Detalhes da atividade..." />
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowActivityModal(false)}>
                Cancelar
              </Button>
              <Button onClick={() => setShowActivityModal(false)}>
                Registrar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
