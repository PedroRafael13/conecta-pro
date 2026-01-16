'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Plus,
  Mail,
  MessageSquare,
  Bell,
  Smartphone,
  Settings,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit2,
  MoreHorizontal,
  Zap,
  Send,
  RefreshCw,
  TestTube2,
  Key,
  Globe,
  Server,
  Shield,
  Clock,
  TrendingUp,
  Wifi,
  WifiOff,
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
  Modal,
  Select,
} from '@/design-system/components';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

// Types
interface NotificationChannel {
  id: string;
  name: string;
  type: 'email' | 'sms' | 'whatsapp' | 'push';
  provider: string;
  status: 'active' | 'inactive' | 'error';
  config: {
    apiKey?: string;
    endpoint?: string;
    sender?: string;
    fromEmail?: string;
    smtpHost?: string;
  };
  stats: {
    sent: number;
    delivered: number;
    failed: number;
    pending: number;
  };
  lastSync: string;
  createdAt: string;
}

// Mock Data
const channels: NotificationChannel[] = [
  {
    id: '1',
    name: 'Email Principal',
    type: 'email',
    provider: 'Amazon SES',
    status: 'active',
    config: {
      fromEmail: 'noreply@conectapro.com.br',
      smtpHost: 'email-smtp.us-east-1.amazonaws.com',
    },
    stats: { sent: 15420, delivered: 15210, failed: 180, pending: 30 },
    lastSync: '2026-01-16 10:00',
    createdAt: '2025-01-01',
  },
  {
    id: '2',
    name: 'SMS Alertas',
    type: 'sms',
    provider: 'Twilio',
    status: 'active',
    config: {
      sender: '+5511999999999',
      endpoint: 'api.twilio.com',
    },
    stats: { sent: 3245, delivered: 3180, failed: 45, pending: 20 },
    lastSync: '2026-01-16 09:45',
    createdAt: '2025-03-15',
  },
  {
    id: '3',
    name: 'WhatsApp Business',
    type: 'whatsapp',
    provider: 'Meta Business API',
    status: 'active',
    config: {
      sender: '+5511888888888',
      endpoint: 'graph.facebook.com',
    },
    stats: { sent: 8934, delivered: 8756, failed: 124, pending: 54 },
    lastSync: '2026-01-16 09:30',
    createdAt: '2025-06-01',
  },
  {
    id: '4',
    name: 'Push Notifications',
    type: 'push',
    provider: 'Firebase Cloud Messaging',
    status: 'active',
    config: {
      endpoint: 'fcm.googleapis.com',
    },
    stats: { sent: 45678, delivered: 42345, failed: 2890, pending: 443 },
    lastSync: '2026-01-16 10:05',
    createdAt: '2025-02-10',
  },
  {
    id: '5',
    name: 'SMS Backup',
    type: 'sms',
    provider: 'Zenvia',
    status: 'inactive',
    config: {
      sender: '+5511777777777',
      endpoint: 'api.zenvia.com',
    },
    stats: { sent: 0, delivered: 0, failed: 0, pending: 0 },
    lastSync: '2025-12-01 14:00',
    createdAt: '2025-08-20',
  },
];

const dailyStats = [
  { day: 'Seg', email: 2450, sms: 320, whatsapp: 890, push: 4520 },
  { day: 'Ter', email: 2680, sms: 415, whatsapp: 1020, push: 5120 },
  { day: 'Qua', email: 2320, sms: 280, whatsapp: 950, push: 4890 },
  { day: 'Qui', email: 2890, sms: 390, whatsapp: 1150, push: 5340 },
  { day: 'Sex', email: 2150, sms: 245, whatsapp: 780, push: 4120 },
  { day: 'Sáb', email: 890, sms: 120, whatsapp: 340, push: 2100 },
  { day: 'Dom', email: 450, sms: 80, whatsapp: 210, push: 1560 },
];

const deliveryRate = [
  { hour: '00h', rate: 98.5 },
  { hour: '04h', rate: 99.2 },
  { hour: '08h', rate: 97.8 },
  { hour: '12h', rate: 96.5 },
  { hour: '16h', rate: 97.2 },
  { hour: '20h', rate: 98.1 },
];

const channelIcons = {
  email: Mail,
  sms: MessageSquare,
  whatsapp: Smartphone,
  push: Bell,
};

const channelColors = {
  email: '#3B82F6',
  sms: '#F59E0B',
  whatsapp: '#25D366',
  push: '#8B5CF6',
};

const statusConfig = {
  active: { label: 'Ativo', color: 'success', icon: CheckCircle2 },
  inactive: { label: 'Inativo', color: 'secondary', icon: XCircle },
  error: { label: 'Erro', color: 'danger', icon: AlertTriangle },
} as const;

export function NotificationChannelsPage() {
  const [selectedChannel, setSelectedChannel] = useState<NotificationChannel | null>(null);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);

  // Stats
  const totalSent = channels.reduce((acc, c) => acc + c.stats.sent, 0);
  const totalDelivered = channels.reduce((acc, c) => acc + c.stats.delivered, 0);
  const totalFailed = channels.reduce((acc, c) => acc + c.stats.failed, 0);
  const deliveryRateValue = ((totalDelivered / totalSent) * 100).toFixed(1);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Canais de Notificação</h1>
            <p className="text-text-secondary mt-1">Configure e monitore os canais de envio</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Sincronizar Todos
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsConfigModalOpen(true)}>
              Novo Canal
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total Enviados" value={totalSent.toLocaleString('pt-BR')} icon={<Send className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Entregues" value={totalDelivered.toLocaleString('pt-BR')} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Taxa de Entrega" value={`${deliveryRateValue}%`} icon={<TrendingUp className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Falhas" value={totalFailed.toLocaleString('pt-BR')} icon={<AlertTriangle className="w-6 h-6" />} iconColor="danger" />
          </motion.div>
        </StatGrid>

        {/* Channels Grid */}
        <div className="grid grid-cols-2 gap-6">
          {channels.map((channel) => {
            const Icon = channelIcons[channel.type];
            const StatusIcon = statusConfig[channel.status].icon;
            const successRate = channel.stats.sent > 0
              ? ((channel.stats.delivered / channel.stats.sent) * 100).toFixed(1)
              : '0';

            return (
              <motion.div
                key={channel.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="cursor-pointer hover:border-primary/50 transition-colors" onClick={() => setSelectedChannel(channel)}>
                  <CardBody>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div
                          className="p-3 rounded-xl"
                          style={{ backgroundColor: `${channelColors[channel.type]}20` }}
                        >
                          <Icon className="w-6 h-6" style={{ color: channelColors[channel.type] }} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-text-primary">{channel.name}</h3>
                            <Badge variant={statusConfig[channel.status].color as any}>
                              <StatusIcon className="w-3 h-3 mr-1" />
                              {statusConfig[channel.status].label}
                            </Badge>
                          </div>
                          <p className="text-sm text-text-muted mt-1">{channel.provider}</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon-sm">
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </div>

                    <div className="grid grid-cols-4 gap-4 mt-6">
                      <div className="text-center">
                        <p className="text-lg font-bold text-text-primary">{channel.stats.sent.toLocaleString('pt-BR')}</p>
                        <p className="text-xs text-text-muted">Enviados</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-success">{channel.stats.delivered.toLocaleString('pt-BR')}</p>
                        <p className="text-xs text-text-muted">Entregues</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-danger">{channel.stats.failed.toLocaleString('pt-BR')}</p>
                        <p className="text-xs text-text-muted">Falhas</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-warning">{channel.stats.pending.toLocaleString('pt-BR')}</p>
                        <p className="text-xs text-text-muted">Pendentes</p>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-border flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-success rounded-full"
                            style={{ width: `${successRate}%` }}
                          />
                        </div>
                        <span className="text-sm text-text-muted">{successRate}%</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-text-muted">
                        <Clock className="w-3 h-3" />
                        <span>Última sinc: {new Date(channel.lastSync).toLocaleString('pt-BR')}</span>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Send className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Envios por Canal (Semana)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dailyStats}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="day" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="email" fill="#3B82F6" name="Email" stackId="a" />
                    <Bar dataKey="sms" fill="#F59E0B" name="SMS" stackId="a" />
                    <Bar dataKey="whatsapp" fill="#25D366" name="WhatsApp" stackId="a" />
                    <Bar dataKey="push" fill="#8B5CF6" name="Push" stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Taxa de Entrega (24h)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={deliveryRate}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-text-muted)" />
                    <YAxis domain={[95, 100]} stroke="var(--color-text-muted)" />
                    <Tooltip formatter={(value: number) => `${value}%`} />
                    <Line type="monotone" dataKey="rate" stroke="#10B981" strokeWidth={3} dot={{ fill: '#10B981', strokeWidth: 2 }} name="Taxa de Entrega" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Config Modal */}
        <Modal
          isOpen={isConfigModalOpen}
          onClose={() => setIsConfigModalOpen(false)}
          title="Novo Canal de Notificação"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsConfigModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="secondary" leftIcon={<TestTube2 className="w-4 h-4" />}>
                Testar Conexão
              </Button>
              <Button variant="primary">Salvar Canal</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome do Canal" placeholder="Ex: Email Principal" required />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Canal"
                options={[
                  { value: 'email', label: 'Email (SMTP)' },
                  { value: 'sms', label: 'SMS' },
                  { value: 'whatsapp', label: 'WhatsApp' },
                  { value: 'push', label: 'Push Notification' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Provedor"
                options={[
                  { value: 'ses', label: 'Amazon SES' },
                  { value: 'sendgrid', label: 'SendGrid' },
                  { value: 'twilio', label: 'Twilio' },
                  { value: 'zenvia', label: 'Zenvia' },
                  { value: 'meta', label: 'Meta Business API' },
                  { value: 'firebase', label: 'Firebase Cloud Messaging' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <Input label="Endpoint / Host" placeholder="api.provider.com" leftIcon={<Server className="w-4 h-4" />} />
            <Input label="API Key / Token" type="password" placeholder="Sua chave de API" leftIcon={<Key className="w-4 h-4" />} />
            <Input label="Remetente (Email/Número)" placeholder="noreply@empresa.com ou +5511999999999" />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={!!selectedChannel}
          onClose={() => setSelectedChannel(null)}
          title="Configuração do Canal"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedChannel(null)}>
                Fechar
              </Button>
              <Button variant="secondary" leftIcon={<TestTube2 className="w-4 h-4" />}>
                Testar
              </Button>
              <Button variant="primary" leftIcon={<Edit2 className="w-4 h-4" />}>
                Editar
              </Button>
            </>
          }
        >
          {selectedChannel && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                {(() => {
                  const Icon = channelIcons[selectedChannel.type];
                  return (
                    <div
                      className="p-3 rounded-xl"
                      style={{ backgroundColor: `${channelColors[selectedChannel.type]}20` }}
                    >
                      <Icon className="w-8 h-8" style={{ color: channelColors[selectedChannel.type] }} />
                    </div>
                  );
                })()}
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-text-primary">{selectedChannel.name}</h3>
                    <Badge variant={statusConfig[selectedChannel.status].color as any}>
                      {statusConfig[selectedChannel.status].label}
                    </Badge>
                  </div>
                  <p className="text-text-secondary mt-1">{selectedChannel.provider}</p>
                </div>
              </div>

              {/* Config Details */}
              <div className="space-y-3">
                <h4 className="font-medium text-text-primary">Configuração</h4>
                {selectedChannel.config.fromEmail && (
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border">
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4 text-text-muted" />
                      <span className="text-sm text-text-muted">Email Remetente</span>
                    </div>
                    <span className="text-sm font-medium text-text-primary">{selectedChannel.config.fromEmail}</span>
                  </div>
                )}
                {selectedChannel.config.smtpHost && (
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border">
                    <div className="flex items-center gap-2">
                      <Server className="w-4 h-4 text-text-muted" />
                      <span className="text-sm text-text-muted">SMTP Host</span>
                    </div>
                    <span className="text-sm font-medium text-text-primary">{selectedChannel.config.smtpHost}</span>
                  </div>
                )}
                {selectedChannel.config.sender && (
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-4 h-4 text-text-muted" />
                      <span className="text-sm text-text-muted">Número Remetente</span>
                    </div>
                    <span className="text-sm font-medium text-text-primary">{selectedChannel.config.sender}</span>
                  </div>
                )}
                {selectedChannel.config.endpoint && (
                  <div className="flex items-center justify-between p-3 rounded-lg border border-border">
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-text-muted" />
                      <span className="text-sm text-text-muted">Endpoint</span>
                    </div>
                    <span className="text-sm font-medium text-text-primary">{selectedChannel.config.endpoint}</span>
                  </div>
                )}
              </div>

              {/* Stats */}
              <div>
                <h4 className="font-medium text-text-primary mb-3">Estatísticas</h4>
                <div className="grid grid-cols-4 gap-4">
                  <div className="p-4 rounded-lg border border-border text-center">
                    <p className="text-2xl font-bold text-text-primary">{selectedChannel.stats.sent.toLocaleString('pt-BR')}</p>
                    <p className="text-xs text-text-muted">Enviados</p>
                  </div>
                  <div className="p-4 rounded-lg border border-border text-center">
                    <p className="text-2xl font-bold text-success">{selectedChannel.stats.delivered.toLocaleString('pt-BR')}</p>
                    <p className="text-xs text-text-muted">Entregues</p>
                  </div>
                  <div className="p-4 rounded-lg border border-border text-center">
                    <p className="text-2xl font-bold text-danger">{selectedChannel.stats.failed.toLocaleString('pt-BR')}</p>
                    <p className="text-xs text-text-muted">Falhas</p>
                  </div>
                  <div className="p-4 rounded-lg border border-border text-center">
                    <p className="text-2xl font-bold text-warning">{selectedChannel.stats.pending.toLocaleString('pt-BR')}</p>
                    <p className="text-xs text-text-muted">Pendentes</p>
                  </div>
                </div>
              </div>

              {/* Footer Info */}
              <div className="flex items-center gap-6 text-sm text-text-muted pt-4 border-t border-border">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>Última sincronização: {new Date(selectedChannel.lastSync).toLocaleString('pt-BR')}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4" />
                  <span>Criado em: {new Date(selectedChannel.createdAt).toLocaleDateString('pt-BR')}</span>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
