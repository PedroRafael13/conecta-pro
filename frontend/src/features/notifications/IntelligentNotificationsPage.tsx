'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bell,
  Brain,
  Target,
  Clock,
  Users,
  TrendingUp,
  BarChart3,
  Zap,
  Settings,
  Play,
  Pause,
  Eye,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  MoreVertical,
  CheckCircle,
  XCircle,
  Mail,
  MessageSquare,
  Smartphone,
  Globe,
  Calendar,
  Activity,
  Sparkles,
  TestTube,
  PieChart,
  ArrowRight,
  RefreshCw,
  Download,
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
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';

// Types
interface IntelligentCampaign {
  id: string;
  name: string;
  description: string;
  type: 'behavioral' | 'engagement' | 'personalized' | 'timing';
  status: 'active' | 'paused' | 'draft' | 'completed';
  channel: 'email' | 'push' | 'sms' | 'whatsapp' | 'multi';
  targeting: {
    segments: string[];
    conditions: string[];
  };
  metrics: {
    sent: number;
    delivered: number;
    opened: number;
    clicked: number;
    converted: number;
  };
  aiScore: number;
  optimalTime: string;
  createdAt: string;
  lastRun: string | null;
}

interface ABExperiment {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'paused';
  variants: {
    id: string;
    name: string;
    traffic: number;
    conversions: number;
    conversionRate: number;
  }[];
  winner: string | null;
  confidence: number;
  startDate: string;
  endDate: string | null;
}

// Mock data
const mockCampaigns: IntelligentCampaign[] = [
  {
    id: '1',
    name: 'Reengajamento de Usuários Inativos',
    description: 'Campanha automática para usuários sem acesso há 7+ dias',
    type: 'behavioral',
    status: 'active',
    channel: 'multi',
    targeting: {
      segments: ['inactive_users', 'high_value'],
      conditions: ['last_login > 7 days', 'lifetime_value > R$500'],
    },
    metrics: {
      sent: 1250,
      delivered: 1180,
      opened: 472,
      clicked: 189,
      converted: 56,
    },
    aiScore: 87,
    optimalTime: '09:30',
    createdAt: '2026-01-05',
    lastRun: '2026-01-16T09:30:00',
  },
  {
    id: '2',
    name: 'Onboarding Personalizado',
    description: 'Sequência de boas-vindas com conteúdo adaptativo',
    type: 'personalized',
    status: 'active',
    channel: 'email',
    targeting: {
      segments: ['new_users'],
      conditions: ['signup_date < 30 days'],
    },
    metrics: {
      sent: 340,
      delivered: 338,
      opened: 271,
      clicked: 162,
      converted: 98,
    },
    aiScore: 94,
    optimalTime: '10:00',
    createdAt: '2025-11-15',
    lastRun: '2026-01-16T10:00:00',
  },
  {
    id: '3',
    name: 'Previsão de Churn - Intervenção',
    description: 'Notificações preventivas para usuários em risco de churn',
    type: 'behavioral',
    status: 'active',
    channel: 'whatsapp',
    targeting: {
      segments: ['churn_risk_high'],
      conditions: ['churn_probability > 70%'],
    },
    metrics: {
      sent: 85,
      delivered: 82,
      opened: 65,
      clicked: 41,
      converted: 28,
    },
    aiScore: 91,
    optimalTime: '14:00',
    createdAt: '2026-01-01',
    lastRun: '2026-01-15T14:00:00',
  },
  {
    id: '4',
    name: 'Notificação de Horário Ótimo',
    description: 'Envio automático no melhor horário para cada usuário',
    type: 'timing',
    status: 'active',
    channel: 'push',
    targeting: {
      segments: ['all_users'],
      conditions: ['ai_optimal_time = true'],
    },
    metrics: {
      sent: 5420,
      delivered: 5180,
      opened: 2590,
      clicked: 1036,
      converted: 311,
    },
    aiScore: 82,
    optimalTime: 'Personalizado',
    createdAt: '2025-10-20',
    lastRun: '2026-01-16T08:00:00',
  },
  {
    id: '5',
    name: 'Promoção Segmentada por Engajamento',
    description: 'Ofertas personalizadas baseadas em nível de engajamento',
    type: 'engagement',
    status: 'paused',
    channel: 'email',
    targeting: {
      segments: ['highly_engaged', 'medium_engaged'],
      conditions: ['engagement_score > 50'],
    },
    metrics: {
      sent: 2100,
      delivered: 2050,
      opened: 820,
      clicked: 287,
      converted: 86,
    },
    aiScore: 78,
    optimalTime: '11:00',
    createdAt: '2025-12-01',
    lastRun: '2026-01-10T11:00:00',
  },
];

const mockExperiments: ABExperiment[] = [
  {
    id: '1',
    name: 'Teste de Assunto de Email',
    status: 'running',
    variants: [
      { id: 'a', name: 'Controle: Formal', traffic: 50, conversions: 145, conversionRate: 4.2 },
      { id: 'b', name: 'Variante: Casual', traffic: 50, conversions: 178, conversionRate: 5.1 },
    ],
    winner: null,
    confidence: 89,
    startDate: '2026-01-10',
    endDate: null,
  },
  {
    id: '2',
    name: 'Horário de Envio Push',
    status: 'completed',
    variants: [
      { id: 'a', name: 'Manhã (9h)', traffic: 33, conversions: 89, conversionRate: 3.8 },
      { id: 'b', name: 'Tarde (14h)', traffic: 33, conversions: 112, conversionRate: 4.8 },
      { id: 'c', name: 'Noite (20h)', traffic: 34, conversions: 156, conversionRate: 6.5 },
    ],
    winner: 'c',
    confidence: 97,
    startDate: '2025-12-15',
    endDate: '2026-01-05',
  },
];

const engagementData = [
  { day: 'Seg', opens: 420, clicks: 168, conversions: 50 },
  { day: 'Ter', opens: 380, clicks: 152, conversions: 46 },
  { day: 'Qua', opens: 450, clicks: 180, conversions: 54 },
  { day: 'Qui', opens: 520, clicks: 208, conversions: 62 },
  { day: 'Sex', opens: 480, clicks: 192, conversions: 58 },
  { day: 'Sáb', opens: 280, clicks: 112, conversions: 34 },
  { day: 'Dom', opens: 220, clicks: 88, conversions: 26 },
];

const channelPerformance = [
  { name: 'Email', value: 35, color: '#6366f1' },
  { name: 'Push', value: 28, color: '#22c55e' },
  { name: 'WhatsApp', value: 22, color: '#f59e0b' },
  { name: 'SMS', value: 15, color: '#ef4444' },
];

const typeConfig: Record<IntelligentCampaign['type'], { label: string; variant: 'primary' | 'success' | 'warning' | 'info' }> = {
  behavioral: { label: 'Comportamental', variant: 'primary' },
  engagement: { label: 'Engajamento', variant: 'success' },
  personalized: { label: 'Personalizado', variant: 'info' },
  timing: { label: 'Horário Ótimo', variant: 'warning' },
};

const statusConfig: Record<IntelligentCampaign['status'], { label: string; variant: 'success' | 'warning' | 'secondary' | 'info' }> = {
  active: { label: 'Ativa', variant: 'success' },
  paused: { label: 'Pausada', variant: 'warning' },
  draft: { label: 'Rascunho', variant: 'secondary' },
  completed: { label: 'Concluída', variant: 'info' },
};

const channelIcons: Record<string, typeof Mail> = {
  email: Mail,
  push: Smartphone,
  sms: MessageSquare,
  whatsapp: MessageSquare,
  multi: Globe,
};

export default function IntelligentNotificationsPage() {
  const [campaigns, setCampaigns] = useState<IntelligentCampaign[]>(mockCampaigns);
  const [experiments, setExperiments] = useState<ABExperiment[]>(mockExperiments);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('campaigns');
  const [selectedCampaign, setSelectedCampaign] = useState<IntelligentCampaign | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Stats
  const stats = {
    totalSent: campaigns.reduce((acc, c) => acc + c.metrics.sent, 0),
    avgOpenRate: Math.round(campaigns.reduce((acc, c) => acc + (c.metrics.opened / c.metrics.delivered) * 100, 0) / campaigns.length),
    avgClickRate: Math.round(campaigns.reduce((acc, c) => acc + (c.metrics.clicked / c.metrics.opened) * 100, 0) / campaigns.length),
    avgConversionRate: Math.round(campaigns.reduce((acc, c) => acc + (c.metrics.converted / c.metrics.clicked) * 100, 0) / campaigns.length),
    avgAiScore: Math.round(campaigns.reduce((acc, c) => acc + c.aiScore, 0) / campaigns.length),
  };

  // Handlers
  const handleToggleCampaign = (campaignId: string) => {
    setCampaigns(prevCampaigns =>
      prevCampaigns.map(campaign =>
        campaign.id === campaignId
          ? {
              ...campaign,
              status: campaign.status === 'active' ? 'paused' : 'active',
            }
          : campaign
      )
    );
  };

  const handlePauseExperiment = (experimentId: string) => {
    setExperiments(prevExperiments =>
      prevExperiments.map(exp =>
        exp.id === experimentId
          ? { ...exp, status: exp.status === 'running' ? 'paused' : 'running' }
          : exp
      )
    );
  };

  const handleEditCampaign = (campaign: IntelligentCampaign) => {
    setSelectedCampaign(campaign);
    setShowEditModal(true);
  };

  const handleDuplicateCampaign = (campaign: IntelligentCampaign) => {
    const newCampaign: IntelligentCampaign = {
      ...campaign,
      id: String(campaigns.length + 1),
      name: `${campaign.name} (Cópia)`,
      status: 'draft',
      metrics: { sent: 0, delivered: 0, opened: 0, clicked: 0, converted: 0 },
      createdAt: new Date().toISOString().split('T')[0],
      lastRun: null,
    };
    setCampaigns(prev => [...prev, newCampaign]);
  };

  const handleDeleteCampaign = (campaign: IntelligentCampaign) => {
    setSelectedCampaign(campaign);
    setShowDeleteModal(true);
  };

  const confirmDeleteCampaign = () => {
    if (selectedCampaign) {
      setCampaigns(prev => prev.filter(c => c.id !== selectedCampaign.id));
      setShowDeleteModal(false);
      setSelectedCampaign(null);
    }
  };

  // Filter
  const filteredCampaigns = campaigns.filter(campaign =>
    campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const campaignColumns = [
    {
      key: 'campaign',
      header: 'Campanha',
      render: (row: IntelligentCampaign) => {
        const ChannelIcon = channelIcons[row.channel] || Bell;
        return (
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-${typeConfig[row.type].variant}/20`}>
              <ChannelIcon className={`w-5 h-5 text-${typeConfig[row.type].variant}`} />
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
      key: 'type',
      header: 'Tipo',
      render: (row: IntelligentCampaign) => (
        <Badge variant={typeConfig[row.type].variant}>
          {typeConfig[row.type].label}
        </Badge>
      ),
    },
    {
      key: 'metrics',
      header: 'Métricas',
      render: (row: IntelligentCampaign) => {
        const openRate = Math.round((row.metrics.opened / row.metrics.delivered) * 100);
        const clickRate = Math.round((row.metrics.clicked / row.metrics.opened) * 100);
        return (
          <div className="text-sm">
            <p>Open: <span className="font-medium text-success">{openRate}%</span></p>
            <p>Click: <span className="font-medium text-info">{clickRate}%</span></p>
          </div>
        );
      },
    },
    {
      key: 'aiScore',
      header: 'Score IA',
      render: (row: IntelligentCampaign) => (
        <div className="flex items-center gap-2">
          <Sparkles className={`w-4 h-4 ${row.aiScore >= 85 ? 'text-success' : row.aiScore >= 70 ? 'text-warning' : 'text-danger'}`} />
          <span className="font-bold">{row.aiScore}</span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: IntelligentCampaign) => (
        <Badge variant={statusConfig[row.status].variant}>
          {statusConfig[row.status].label}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row: IntelligentCampaign) => (
        <div className="flex items-center gap-2">
          <Button
            variant={row.status === 'active' ? 'warning' : 'success'}
            size="sm"
            onClick={() => handleToggleCampaign(row.id)}
            title={row.status === 'active' ? 'Pausar campanha' : 'Ativar campanha'}
          >
            {row.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <Dropdown
            trigger={
              <Button variant="ghost" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
            }
            items={[
              { label: 'Ver Detalhes', icon: <Eye className="w-4 h-4" />, onClick: () => { setSelectedCampaign(row); setShowDetailModal(true); } },
              { label: 'Editar', icon: <Edit className="w-4 h-4" />, onClick: () => handleEditCampaign(row) },
              { label: 'Duplicar', icon: <Plus className="w-4 h-4" />, onClick: () => handleDuplicateCampaign(row) },
              { label: 'Excluir', icon: <Trash2 className="w-4 h-4" />, danger: true, onClick: () => handleDeleteCampaign(row) },
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
              Notificações Inteligentes
            </h1>
            <p className="text-text-secondary mt-1">
              Campanhas otimizadas com IA, análise comportamental e testes A/B
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setShowNewModal(true)}>
              Nova Campanha
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total Enviados"
              value={stats.totalSent.toLocaleString()}
              icon={<Bell className="w-6 h-6" />}
              iconColor="primary"
              change={18}
              changeLabel="vs semana anterior"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Taxa de Abertura"
              value={`${stats.avgOpenRate}%`}
              icon={<Eye className="w-6 h-6" />}
              iconColor="success"
              change={5}
              changeLabel="vs média"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Taxa de Clique"
              value={`${stats.avgClickRate}%`}
              icon={<Target className="w-6 h-6" />}
              iconColor="info"
              change={3}
              changeLabel="vs média"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Taxa de Conversão"
              value={`${stats.avgConversionRate}%`}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="success"
              change={8}
              changeLabel="vs média"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Score IA Médio"
              value={stats.avgAiScore}
              icon={<Brain className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="campaigns">Campanhas</TabsTrigger>
            <TabsTrigger value="experiments">Testes A/B</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="campaigns">
            <Card>
              <CardHeader
                title="Campanhas Inteligentes"
                action={
                  <Input
                    placeholder="Buscar campanhas..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-64"
                  />
                }
              />
              <CardBody className="p-0">
                <DataTable
                  columns={campaignColumns}
                  data={filteredCampaigns}
                  onRowClick={(row) => { setSelectedCampaign(row); setShowDetailModal(true); }}
                />
              </CardBody>
            </Card>
          </TabsContent>

          <TabsContent value="experiments">
            <div className="space-y-4">
              {experiments.map((exp) => (
                <Card key={exp.id}>
                  <CardHeader
                    title={exp.name}
                    action={
                      <Badge variant={exp.status === 'running' ? 'success' : exp.status === 'completed' ? 'info' : 'warning'}>
                        {exp.status === 'running' ? 'Em Execução' : exp.status === 'completed' ? 'Concluído' : 'Pausado'}
                      </Badge>
                    }
                  />
                  <CardBody>
                    <div className="space-y-4">
                      {exp.variants.map((variant) => (
                        <div key={variant.id} className="flex items-center gap-4">
                          <div className="w-32">
                            <p className="font-medium">{variant.name}</p>
                            <p className="text-xs text-text-secondary">{variant.traffic}% tráfego</p>
                          </div>
                          <div className="flex-1">
                            <Progress
                              value={variant.conversionRate * 10}
                              variant={exp.winner === variant.id ? 'success' : 'default'}
                            />
                          </div>
                          <div className="w-24 text-right">
                            <p className="font-bold text-lg">{variant.conversionRate}%</p>
                            <p className="text-xs text-text-secondary">{variant.conversions} conv.</p>
                          </div>
                          {exp.winner === variant.id && (
                            <Badge variant="success">Vencedor</Badge>
                          )}
                        </div>
                      ))}
                      <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
                        <span className="text-sm text-text-secondary">
                          Confiança: <span className="font-medium text-text-primary">{exp.confidence}%</span>
                        </span>
                        <span className="text-sm text-text-secondary">
                          {exp.endDate ? `Finalizado em ${new Date(exp.endDate).toLocaleDateString('pt-BR')}` : `Iniciado em ${new Date(exp.startDate).toLocaleDateString('pt-BR')}`}
                        </span>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analytics">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader title="Engajamento Semanal" />
                <CardBody>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={engagementData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                        <XAxis dataKey="day" stroke="#8b8b9a" />
                        <YAxis stroke="#8b8b9a" />
                        <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }} />
                        <Legend />
                        <Area type="monotone" dataKey="opens" name="Aberturas" stackId="1" stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
                        <Area type="monotone" dataKey="clicks" name="Cliques" stackId="2" stroke="#22c55e" fill="#22c55e" fillOpacity={0.6} />
                        <Area type="monotone" dataKey="conversions" name="Conversões" stackId="3" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardBody>
              </Card>

              <Card>
                <CardHeader title="Performance por Canal" />
                <CardBody>
                  <div className="h-52">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPieChart>
                        <Pie
                          data={channelPerformance}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={3}
                          dataKey="value"
                        >
                          {channelPerformance.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }} />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-2 mt-4">
                    {channelPerformance.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-text-secondary">{item.name}</span>
                        </div>
                        <span className="text-sm font-medium">{item.value}%</span>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedCampaign?.name || ''}
          size="lg"
        >
          {selectedCampaign && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <Badge variant={statusConfig[selectedCampaign.status].variant} size="lg">
                  {statusConfig[selectedCampaign.status].label}
                </Badge>
                <Badge variant={typeConfig[selectedCampaign.type].variant}>
                  {typeConfig[selectedCampaign.type].label}
                </Badge>
                <div className="flex items-center gap-1 ml-auto">
                  <Sparkles className="w-5 h-5 text-warning" />
                  <span className="text-xl font-bold">{selectedCampaign.aiScore}</span>
                </div>
              </div>

              <p className="text-text-secondary">{selectedCampaign.description}</p>

              <div className="grid grid-cols-4 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-2xl font-bold">{selectedCampaign.metrics.sent.toLocaleString()}</p>
                  <p className="text-xs text-text-secondary">Enviados</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-2xl font-bold text-success">{Math.round((selectedCampaign.metrics.opened / selectedCampaign.metrics.delivered) * 100)}%</p>
                  <p className="text-xs text-text-secondary">Abertura</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-2xl font-bold text-info">{Math.round((selectedCampaign.metrics.clicked / selectedCampaign.metrics.opened) * 100)}%</p>
                  <p className="text-xs text-text-secondary">Clique</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-2xl font-bold text-warning">{Math.round((selectedCampaign.metrics.converted / selectedCampaign.metrics.clicked) * 100)}%</p>
                  <p className="text-xs text-text-secondary">Conversão</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Segmentação</h4>
                <div className="flex flex-wrap gap-2 mb-3">
                  {selectedCampaign.targeting.segments.map((segment) => (
                    <Badge key={segment} variant="primary">{segment}</Badge>
                  ))}
                </div>
                <div className="space-y-1">
                  {selectedCampaign.targeting.conditions.map((condition, i) => (
                    <p key={i} className="text-sm text-text-secondary">• {condition}</p>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-accent-primary/10 border border-accent-primary/30 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-5 h-5 text-accent-primary" />
                  <span className="font-medium">Horário Ótimo de Envio</span>
                </div>
                <p className="text-lg font-bold text-accent-primary">{selectedCampaign.optimalTime}</p>
                <p className="text-xs text-text-secondary mt-1">Determinado por IA baseado no comportamento dos usuários</p>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>Fechar</Button>
                <Button
                  variant={selectedCampaign.status === 'active' ? 'warning' : 'success'}
                  leftIcon={selectedCampaign.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                >
                  {selectedCampaign.status === 'active' ? 'Pausar' : 'Ativar'}
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New Campaign Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Nova Campanha Inteligente"
          size="lg"
        >
          <div className="space-y-4">
            <Input label="Nome da Campanha" placeholder="Ex: Reengajamento de Usuários" required />
            <Textarea label="Descrição" placeholder="Descreva o objetivo desta campanha..." rows={2} />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo"
                options={[
                  { value: 'behavioral', label: 'Comportamental' },
                  { value: 'engagement', label: 'Engajamento' },
                  { value: 'personalized', label: 'Personalizado' },
                  { value: 'timing', label: 'Horário Ótimo' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
              <Select
                label="Canal"
                options={[
                  { value: 'email', label: 'Email' },
                  { value: 'push', label: 'Push Notification' },
                  { value: 'sms', label: 'SMS' },
                  { value: 'whatsapp', label: 'WhatsApp' },
                  { value: 'multi', label: 'Multicanal' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
            </div>
            <Select
              label="Segmentos"
              options={[
                { value: 'all_users', label: 'Todos os Usuários' },
                { value: 'new_users', label: 'Novos Usuários' },
                { value: 'inactive_users', label: 'Usuários Inativos' },
                { value: 'high_value', label: 'Alto Valor' },
                { value: 'churn_risk_high', label: 'Risco de Churn' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione os segmentos"
            />
            <div className="p-4 bg-accent-primary/10 border border-accent-primary/30 rounded-lg">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-accent-primary" />
                <span className="font-medium">Otimização por IA</span>
              </div>
              <p className="text-sm text-text-secondary mt-1">
                A IA irá otimizar automaticamente o horário de envio, conteúdo e segmentação baseado no comportamento dos usuários.
              </p>
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>Cancelar</Button>
              <Button variant="primary" leftIcon={<Sparkles className="w-4 h-4" />}>Criar com IA</Button>
            </div>
          </div>
        </Modal>

        {/* Delete Confirmation Modal */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => setShowDeleteModal(false)}
          title="Confirmar Exclusão"
          size="sm"
        >
          <div className="space-y-4">
            <div className="p-4 bg-danger/10 border border-danger/30 rounded-lg">
              <p className="text-sm text-text-secondary">
                Você está prestes a excluir a campanha <strong>{selectedCampaign?.name}</strong>.
                Esta ação não pode ser desfeita e todos os dados de métricas serão perdidos.
              </p>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowDeleteModal(false)}>Cancelar</Button>
              <Button variant="danger" onClick={confirmDeleteCampaign}>Excluir Campanha</Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
