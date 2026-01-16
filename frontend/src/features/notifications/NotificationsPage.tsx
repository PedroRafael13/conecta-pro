'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bell,
  BellOff,
  Check,
  CheckCheck,
  Trash2,
  Settings,
  Filter,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle2,
  Calendar,
  Clock,
  User,
  Building2,
  FileText,
  DollarSign,
  Shield,
  Wrench,
  MessageSquare,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  StatCard,
  StatGrid,
  SimpleTabBar,
  Avatar,
} from '@/design-system/components';

// Types
interface Notification {
  id: string;
  type: 'alert' | 'warning' | 'info' | 'success' | 'system';
  category: 'security' | 'financial' | 'hr' | 'operations' | 'client' | 'system';
  title: string;
  message: string;
  link: string | null;
  isRead: boolean;
  createdAt: string;
  sender: string | null;
}

// Mock Data
const notifications: Notification[] = [
  {
    id: '1',
    type: 'alert',
    category: 'security',
    title: 'Ocorrência crítica registrada',
    message: 'Tentativa de invasão identificada no Shopping Center Norte - Portaria Lateral',
    link: '/field-service/occurrences/1',
    isRead: false,
    createdAt: '2026-01-15 14:30',
    sender: 'Sistema de Monitoramento',
  },
  {
    id: '2',
    type: 'warning',
    category: 'financial',
    title: 'Fatura vencendo em 3 dias',
    message: 'A fatura #2026-0145 do cliente Hospital São Lucas vence em 18/01/2026',
    link: '/financial/receivables',
    isRead: false,
    createdAt: '2026-01-15 10:00',
    sender: 'Sistema Financeiro',
  },
  {
    id: '3',
    type: 'info',
    category: 'hr',
    title: 'Novo colaborador cadastrado',
    message: 'João Carlos Silva foi cadastrado como Vigilante - Início: 20/01/2026',
    link: '/hr/employees',
    isRead: false,
    createdAt: '2026-01-15 09:15',
    sender: 'Ana Paula - RH',
  },
  {
    id: '4',
    type: 'success',
    category: 'operations',
    title: 'Ordem de serviço concluída',
    message: 'OS-2026-0142 foi finalizada com sucesso por Carlos Eduardo',
    link: '/field-service/orders',
    isRead: true,
    createdAt: '2026-01-15 08:45',
    sender: 'Sistema',
  },
  {
    id: '5',
    type: 'warning',
    category: 'client',
    title: 'Contrato próximo do vencimento',
    message: 'O contrato de Controle de Acesso com Tech Park vence em 30 dias',
    link: '/clients/3',
    isRead: true,
    createdAt: '2026-01-14 16:00',
    sender: 'Sistema CRM',
  },
  {
    id: '6',
    type: 'alert',
    category: 'security',
    title: 'Equipamento offline',
    message: 'Câmera 15 - Estacionamento Subsolo está sem comunicação há 2 horas',
    link: '/field-service/equipment',
    isRead: true,
    createdAt: '2026-01-14 14:30',
    sender: 'Sistema de Monitoramento',
  },
  {
    id: '7',
    type: 'system',
    category: 'system',
    title: 'Backup concluído com sucesso',
    message: 'O backup diário do sistema foi realizado às 03:00',
    link: null,
    isRead: true,
    createdAt: '2026-01-14 03:05',
    sender: 'Sistema',
  },
  {
    id: '8',
    type: 'info',
    category: 'operations',
    title: 'Nova escala publicada',
    message: 'A escala de Janeiro/2026 - Semana 3 foi publicada',
    link: '/operations/scales',
    isRead: true,
    createdAt: '2026-01-13 17:00',
    sender: 'Roberto Silva - Operações',
  },
];

const typeConfig = {
  alert: { icon: AlertTriangle, color: 'text-accent-danger', bg: 'bg-accent-danger/20' },
  warning: { icon: AlertCircle, color: 'text-accent-warning', bg: 'bg-accent-warning/20' },
  info: { icon: Info, color: 'text-accent-info', bg: 'bg-accent-info/20' },
  success: { icon: CheckCircle2, color: 'text-accent-success', bg: 'bg-accent-success/20' },
  system: { icon: Settings, color: 'text-text-muted', bg: 'bg-bg-tertiary' },
};

const categoryConfig = {
  security: { icon: Shield, label: 'Segurança' },
  financial: { icon: DollarSign, label: 'Financeiro' },
  hr: { icon: User, label: 'RH' },
  operations: { icon: Wrench, label: 'Operações' },
  client: { icon: Building2, label: 'Clientes' },
  system: { icon: Settings, label: 'Sistema' },
};

export function NotificationsPage() {
  const [selectedTab, setSelectedTab] = useState('all');
  const [notificationsList, setNotificationsList] = useState(notifications);

  const unreadCount = notificationsList.filter(n => !n.isRead).length;
  const alertCount = notificationsList.filter(n => n.type === 'alert' && !n.isRead).length;
  const warningCount = notificationsList.filter(n => n.type === 'warning' && !n.isRead).length;

  const markAsRead = (id: string) => {
    setNotificationsList(prev =>
      prev.map(n => n.id === id ? { ...n, isRead: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotificationsList(prev =>
      prev.map(n => ({ ...n, isRead: true }))
    );
  };

  const filteredNotifications = notificationsList.filter(n => {
    if (selectedTab === 'all') return true;
    if (selectedTab === 'unread') return !n.isRead;
    return n.category === selectedTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Central de Notificações
            </h1>
            <p className="text-text-secondary mt-1">
              Acompanhe alertas e atualizações do sistema
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              leftIcon={<CheckCheck className="w-4 h-4" />}
              onClick={markAllAsRead}
              disabled={unreadCount === 0}
            >
              Marcar todas como lidas
            </Button>
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Não Lidas"
              value={unreadCount}
              icon={<Bell className="w-6 h-6" />}
              iconColor={unreadCount > 0 ? 'warning' : 'success'}
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Alertas Críticos"
              value={alertCount}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor={alertCount > 0 ? 'danger' : 'success'}
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Avisos"
              value={warningCount}
              icon={<AlertCircle className="w-6 h-6" />}
              iconColor={warningCount > 0 ? 'warning' : 'success'}
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Total Hoje"
              value={notifications.filter(n => n.createdAt.startsWith('2026-01-15')).length}
              icon={<MessageSquare className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'all', label: 'Todas' },
                { value: 'unread', label: `Não Lidas (${unreadCount})` },
                { value: 'security', label: 'Segurança' },
                { value: 'financial', label: 'Financeiro' },
                { value: 'operations', label: 'Operações' },
                { value: 'system', label: 'Sistema' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Notifications List */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <div className="divide-y divide-border-subtle">
                {filteredNotifications.length === 0 ? (
                  <div className="p-8 text-center">
                    <BellOff className="w-12 h-12 text-text-muted mx-auto mb-3" />
                    <p className="text-text-secondary">Nenhuma notificação encontrada</p>
                  </div>
                ) : (
                  filteredNotifications.map((notification) => {
                    const typeInfo = typeConfig[notification.type];
                    const categoryInfo = categoryConfig[notification.category];
                    const TypeIcon = typeInfo.icon;
                    const CategoryIcon = categoryInfo.icon;

                    return (
                      <div
                        key={notification.id}
                        className={`p-4 hover:bg-bg-hover transition-colors cursor-pointer ${
                          !notification.isRead ? 'bg-accent-primary/5' : ''
                        }`}
                        onClick={() => markAsRead(notification.id)}
                      >
                        <div className="flex items-start gap-4">
                          <div className={`p-2 rounded-lg ${typeInfo.bg}`}>
                            <TypeIcon className={`w-5 h-5 ${typeInfo.color}`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className={`font-medium ${!notification.isRead ? 'text-text-primary' : 'text-text-secondary'}`}>
                                {notification.title}
                              </h4>
                              {!notification.isRead && (
                                <span className="w-2 h-2 rounded-full bg-accent-primary" />
                              )}
                            </div>
                            <p className="text-sm text-text-muted mb-2">{notification.message}</p>
                            <div className="flex items-center gap-4 text-xs text-text-muted">
                              <div className="flex items-center gap-1">
                                <CategoryIcon className="w-3 h-3" />
                                <span>{categoryInfo.label}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                <span>{notification.createdAt}</span>
                              </div>
                              {notification.sender && (
                                <span>por {notification.sender}</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {notification.link && (
                              <Button variant="ghost" size="sm">
                                Ver
                              </Button>
                            )}
                            <Button variant="ghost" size="icon-sm">
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </CardBody>
          </Card>
        </motion.div>
      </div>
    </MainLayout>
  );
}
