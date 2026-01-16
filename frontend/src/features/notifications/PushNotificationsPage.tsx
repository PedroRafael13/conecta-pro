'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Bell,
  BellOff,
  Smartphone,
  Settings,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit2,
  Trash2,
  MoreHorizontal,
  Send,
  Users,
  Target,
  Clock,
  Calendar,
  TrendingUp,
  Zap,
  Globe,
  Monitor,
  Laptop,
  Tablet,
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
  AreaChart,
  Area,
} from 'recharts';

// Types
interface PushCampaign {
  id: string;
  title: string;
  body: string;
  image: string | null;
  targetAudience: 'all' | 'segment' | 'individual';
  segmentName: string | null;
  status: 'draft' | 'scheduled' | 'sent' | 'cancelled';
  scheduledAt: string | null;
  sentAt: string | null;
  stats: {
    sent: number;
    delivered: number;
    opened: number;
    clicked: number;
  };
  createdAt: string;
  createdBy: string;
}

interface DeviceSubscription {
  id: string;
  userId: string;
  userName: string;
  deviceType: 'mobile' | 'desktop' | 'tablet';
  platform: 'android' | 'ios' | 'web' | 'windows' | 'macos';
  subscribedAt: string;
  lastActive: string;
  status: 'active' | 'inactive' | 'unsubscribed';
}

// Mock Data
const campaigns: PushCampaign[] = [
  {
    id: '1',
    title: 'Nova funcionalidade disponível!',
    body: 'Confira o novo módulo de relatórios com dashboards interativos.',
    image: null,
    targetAudience: 'all',
    segmentName: null,
    status: 'sent',
    scheduledAt: null,
    sentAt: '2026-01-15 10:00',
    stats: { sent: 1250, delivered: 1180, opened: 456, clicked: 189 },
    createdAt: '2026-01-14',
    createdBy: 'Admin',
  },
  {
    id: '2',
    title: 'Manutenção programada',
    body: 'O sistema estará em manutenção das 22h às 02h do dia 20/01.',
    image: null,
    targetAudience: 'all',
    segmentName: null,
    status: 'scheduled',
    scheduledAt: '2026-01-18 18:00',
    sentAt: null,
    stats: { sent: 0, delivered: 0, opened: 0, clicked: 0 },
    createdAt: '2026-01-16',
    createdBy: 'TI',
  },
  {
    id: '3',
    title: 'Seu plantão foi atualizado',
    body: 'Verifique sua escala para a próxima semana.',
    image: null,
    targetAudience: 'segment',
    segmentName: 'Operacional',
    status: 'sent',
    scheduledAt: null,
    sentAt: '2026-01-14 14:30',
    stats: { sent: 450, delivered: 438, opened: 312, clicked: 245 },
    createdAt: '2026-01-14',
    createdBy: 'RH',
  },
  {
    id: '4',
    title: 'Treinamento obrigatório',
    body: 'Complete o treinamento de segurança até 25/01.',
    image: null,
    targetAudience: 'segment',
    segmentName: 'Todos Colaboradores',
    status: 'draft',
    scheduledAt: null,
    sentAt: null,
    stats: { sent: 0, delivered: 0, opened: 0, clicked: 0 },
    createdAt: '2026-01-16',
    createdBy: 'RH',
  },
];

const subscriptions: DeviceSubscription[] = [
  { id: '1', userId: 'u1', userName: 'João Silva', deviceType: 'mobile', platform: 'android', subscribedAt: '2025-06-15', lastActive: '2026-01-16 10:30', status: 'active' },
  { id: '2', userId: 'u2', userName: 'Maria Santos', deviceType: 'mobile', platform: 'ios', subscribedAt: '2025-08-20', lastActive: '2026-01-16 09:45', status: 'active' },
  { id: '3', userId: 'u3', userName: 'Carlos Lima', deviceType: 'desktop', platform: 'web', subscribedAt: '2025-09-10', lastActive: '2026-01-15 18:00', status: 'active' },
  { id: '4', userId: 'u4', userName: 'Ana Oliveira', deviceType: 'tablet', platform: 'ios', subscribedAt: '2025-07-05', lastActive: '2026-01-10 14:20', status: 'inactive' },
];

const deviceDistribution = [
  { name: 'Android', value: 45, color: '#3DDC84' },
  { name: 'iOS', value: 35, color: '#007AFF' },
  { name: 'Web', value: 15, color: '#F59E0B' },
  { name: 'Desktop', value: 5, color: '#6B7280' },
];

const engagementTrend = [
  { date: '10/01', sent: 850, opened: 320, clicked: 145 },
  { date: '11/01', sent: 920, opened: 380, clicked: 165 },
  { date: '12/01', sent: 1100, opened: 450, clicked: 198 },
  { date: '13/01', sent: 780, opened: 290, clicked: 112 },
  { date: '14/01', sent: 1250, opened: 456, clicked: 189 },
  { date: '15/01', sent: 680, opened: 245, clicked: 95 },
  { date: '16/01', sent: 450, opened: 180, clicked: 72 },
];

const tabs = [
  { id: 'campaigns', label: 'Campanhas' },
  { id: 'subscriptions', label: 'Inscrições' },
  { id: 'segments', label: 'Segmentos' },
];

const statusColors = {
  draft: 'secondary',
  scheduled: 'warning',
  sent: 'success',
  cancelled: 'danger',
} as const;

const statusLabels = {
  draft: 'Rascunho',
  scheduled: 'Agendado',
  sent: 'Enviado',
  cancelled: 'Cancelado',
};

const deviceIcons = {
  mobile: Smartphone,
  desktop: Monitor,
  tablet: Tablet,
};

const platformLabels = {
  android: 'Android',
  ios: 'iOS',
  web: 'Web',
  windows: 'Windows',
  macos: 'macOS',
};

const campaignColumns: Column<PushCampaign>[] = [
  {
    key: 'title',
    header: 'Campanha',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <Bell className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.title}</p>
          <p className="text-xs text-text-muted line-clamp-1">{row.body}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'targetAudience',
    header: 'Audiência',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Target className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.segmentName || 'Todos os usuários'}</span>
      </div>
    ),
  },
  {
    key: 'stats',
    header: 'Métricas',
    render: (row) => (
      row.status === 'sent' ? (
        <div className="flex items-center gap-4 text-sm">
          <span className="text-text-primary">{row.stats.sent} enviados</span>
          <span className="text-success">{((row.stats.opened / row.stats.delivered) * 100).toFixed(0)}% abertos</span>
        </div>
      ) : (
        <span className="text-sm text-text-muted">-</span>
      )
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => <Badge variant={statusColors[row.status]}>{statusLabels[row.status]}</Badge>,
  },
  {
    key: 'sentAt',
    header: 'Data',
    render: (row) => (
      <div className="flex items-center gap-2 text-sm text-text-muted">
        <Calendar className="w-4 h-4" />
        <span>{row.sentAt || row.scheduledAt || new Date(row.createdAt).toLocaleDateString('pt-BR')}</span>
      </div>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'draft' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Editar">
              <Edit2 className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Enviar">
              <Send className="w-4 h-4 text-success" />
            </Button>
          </>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const subscriptionColumns: Column<DeviceSubscription>[] = [
  {
    key: 'userName',
    header: 'Usuário',
    render: (row) => {
      const Icon = deviceIcons[row.deviceType];
      return (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-bg-secondary">
            <Icon className="w-5 h-5 text-text-muted" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.userName}</p>
            <p className="text-xs text-text-muted">{platformLabels[row.platform]}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'subscribedAt',
    header: 'Inscrito em',
    render: (row) => <span className="text-sm">{new Date(row.subscribedAt).toLocaleDateString('pt-BR')}</span>,
  },
  {
    key: 'lastActive',
    header: 'Última Atividade',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{new Date(row.lastActive).toLocaleString('pt-BR')}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={row.status === 'active' ? 'success' : row.status === 'inactive' ? 'warning' : 'danger'}>
        {row.status === 'active' ? 'Ativo' : row.status === 'inactive' ? 'Inativo' : 'Cancelado'}
      </Badge>
    ),
  },
];

export function PushNotificationsPage() {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState<PushCampaign | null>(null);
  const [newAudience, setNewAudience] = useState('');

  // Stats
  const totalSubscribers = subscriptions.filter((s) => s.status === 'active').length;
  const totalSent = campaigns.reduce((acc, c) => acc + c.stats.sent, 0);
  const totalOpened = campaigns.reduce((acc, c) => acc + c.stats.opened, 0);
  const avgOpenRate = totalSent > 0 ? ((totalOpened / totalSent) * 100).toFixed(1) : '0';

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Push Notifications</h1>
            <p className="text-text-secondary mt-1">Gerencie notificações push para dispositivos</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Nova Campanha
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Inscritos Ativos" value={totalSubscribers.toLocaleString('pt-BR')} icon={<Users className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Notificações Enviadas" value={totalSent.toLocaleString('pt-BR')} icon={<Send className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Taxa de Abertura" value={`${avgOpenRate}%`} icon={<TrendingUp className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Campanhas Ativas" value={campaigns.filter((c) => c.status !== 'cancelled').length} icon={<Bell className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-3 gap-6">
          <Card className="col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Engajamento (7 dias)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={engagementTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="date" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Area type="monotone" dataKey="sent" fill="#3B82F680" stroke="#3B82F6" name="Enviados" />
                    <Area type="monotone" dataKey="opened" fill="#10B98180" stroke="#10B981" name="Abertos" />
                    <Area type="monotone" dataKey="clicked" fill="#F59E0B80" stroke="#F59E0B" name="Clicados" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Dispositivos</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={deviceDistribution} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                      {deviceDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-3 mt-2">
                {deviceDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-text-muted">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Content */}
        {activeTab === 'campaigns' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input
                placeholder="Buscar campanhas..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                Filtros
              </Button>
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable
                  columns={campaignColumns}
                  data={campaigns}
                  keyExtractor={(row) => row.id}
                  onRowClick={(row) => setSelectedCampaign(row)}
                />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'subscriptions' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input
                placeholder="Buscar inscritos..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                Filtros
              </Button>
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable columns={subscriptionColumns} data={subscriptions} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'segments' && (
          <div className="grid grid-cols-3 gap-6">
            {[
              { name: 'Todos os Usuários', count: 1250, description: 'Todos os usuários com push habilitado' },
              { name: 'Operacional', count: 450, description: 'Colaboradores do setor operacional' },
              { name: 'Administrativo', count: 280, description: 'Equipe administrativa e gestores' },
              { name: 'Clientes', count: 520, description: 'Clientes com app instalado' },
              { name: 'Novos Usuários', count: 85, description: 'Cadastrados nos últimos 30 dias' },
              { name: 'Inativos', count: 120, description: 'Sem atividade há mais de 7 dias' },
            ].map((segment) => (
              <Card key={segment.name} className="cursor-pointer hover:border-primary/50 transition-colors">
                <CardBody>
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Users className="w-5 h-5 text-primary" />
                    </div>
                    <Badge variant="info">{segment.count} usuários</Badge>
                  </div>
                  <h4 className="font-medium text-text-primary">{segment.name}</h4>
                  <p className="text-sm text-text-muted mt-1">{segment.description}</p>
                </CardBody>
              </Card>
            ))}
          </div>
        )}

        {/* Create Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Nova Campanha Push"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="secondary">Salvar Rascunho</Button>
              <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                Enviar Agora
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Título" placeholder="Ex: Nova funcionalidade disponível!" required />
            <Textarea label="Mensagem" placeholder="Digite o conteúdo da notificação..." rows={3} required />
            <Input label="URL de Destino (opcional)" placeholder="https://..." leftIcon={<Globe className="w-4 h-4" />} />
            <Select
              label="Audiência"
              options={[
                { value: 'all', label: 'Todos os usuários' },
                { value: 'operational', label: 'Operacional' },
                { value: 'admin', label: 'Administrativo' },
                { value: 'clients', label: 'Clientes' },
                { value: 'new', label: 'Novos Usuários' },
              ]}
              value={newAudience}
              onChange={(value) => setNewAudience(value)}
              placeholder="Selecione..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Agendar Data (opcional)" type="date" />
              <Input label="Horário" type="time" />
            </div>
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={!!selectedCampaign}
          onClose={() => setSelectedCampaign(null)}
          title="Detalhes da Campanha"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedCampaign(null)}>
                Fechar
              </Button>
              {selectedCampaign?.status === 'draft' && (
                <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                  Enviar
                </Button>
              )}
            </>
          }
        >
          {selectedCampaign && (
            <div className="space-y-6">
              {/* Header */}
              <div className="p-4 rounded-lg bg-bg-secondary">
                <div className="flex items-center justify-between mb-3">
                  <Badge variant={statusColors[selectedCampaign.status]}>{statusLabels[selectedCampaign.status]}</Badge>
                  <span className="text-sm text-text-muted">
                    por {selectedCampaign.createdBy} em {new Date(selectedCampaign.createdAt).toLocaleDateString('pt-BR')}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-text-primary">{selectedCampaign.title}</h3>
                <p className="text-text-secondary mt-2">{selectedCampaign.body}</p>
              </div>

              {/* Audience */}
              <div className="flex items-center gap-3 p-4 rounded-lg border border-border">
                <Target className="w-5 h-5 text-primary" />
                <div>
                  <p className="text-xs text-text-muted">Audiência</p>
                  <p className="font-medium text-text-primary">{selectedCampaign.segmentName || 'Todos os usuários'}</p>
                </div>
              </div>

              {/* Stats */}
              {selectedCampaign.status === 'sent' && (
                <div>
                  <h4 className="font-medium text-text-primary mb-3">Métricas de Engajamento</h4>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="p-4 rounded-lg border border-border text-center">
                      <p className="text-2xl font-bold text-text-primary">{selectedCampaign.stats.sent.toLocaleString('pt-BR')}</p>
                      <p className="text-xs text-text-muted">Enviados</p>
                    </div>
                    <div className="p-4 rounded-lg border border-border text-center">
                      <p className="text-2xl font-bold text-success">{selectedCampaign.stats.delivered.toLocaleString('pt-BR')}</p>
                      <p className="text-xs text-text-muted">Entregues</p>
                    </div>
                    <div className="p-4 rounded-lg border border-border text-center">
                      <p className="text-2xl font-bold text-info">{selectedCampaign.stats.opened.toLocaleString('pt-BR')}</p>
                      <p className="text-xs text-text-muted">Abertos</p>
                    </div>
                    <div className="p-4 rounded-lg border border-border text-center">
                      <p className="text-2xl font-bold text-warning">{selectedCampaign.stats.clicked.toLocaleString('pt-BR')}</p>
                      <p className="text-xs text-text-muted">Clicados</p>
                    </div>
                  </div>

                  {/* Rates */}
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="p-4 rounded-lg bg-bg-secondary">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-text-muted">Taxa de Entrega</span>
                        <span className="font-bold text-success">
                          {((selectedCampaign.stats.delivered / selectedCampaign.stats.sent) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-success rounded-full"
                          style={{ width: `${(selectedCampaign.stats.delivered / selectedCampaign.stats.sent) * 100}%` }}
                        />
                      </div>
                    </div>
                    <div className="p-4 rounded-lg bg-bg-secondary">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-text-muted">Taxa de Abertura</span>
                        <span className="font-bold text-info">
                          {((selectedCampaign.stats.opened / selectedCampaign.stats.delivered) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-info rounded-full"
                          style={{ width: `${(selectedCampaign.stats.opened / selectedCampaign.stats.delivered) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Scheduled Info */}
              {selectedCampaign.status === 'scheduled' && selectedCampaign.scheduledAt && (
                <div className="flex items-center gap-3 p-4 rounded-lg bg-warning/10 border border-warning/20">
                  <Clock className="w-5 h-5 text-warning" />
                  <div>
                    <p className="font-medium text-warning">Agendado para</p>
                    <p className="text-sm text-text-secondary">
                      {new Date(selectedCampaign.scheduledAt).toLocaleString('pt-BR')}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
