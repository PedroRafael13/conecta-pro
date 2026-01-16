'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  MapPin,
  Users,
  ClipboardCheck,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Truck,
  Phone,
  Navigation,
  Activity,
  Calendar,
  TrendingUp,
  Eye,
  MoreHorizontal,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Mock Data
const dailyVisits = [
  { day: 'Seg', agendadas: 45, realizadas: 42, pendentes: 3 },
  { day: 'Ter', agendadas: 52, realizadas: 48, pendentes: 4 },
  { day: 'Qua', agendadas: 48, realizadas: 45, pendentes: 3 },
  { day: 'Qui', agendadas: 55, realizadas: 50, pendentes: 5 },
  { day: 'Sex', agendadas: 60, realizadas: 55, pendentes: 5 },
  { day: 'Sáb', agendadas: 30, realizadas: 28, pendentes: 2 },
  { day: 'Dom', agendadas: 15, realizadas: 14, pendentes: 1 },
];

const ordersByStatus = [
  { name: 'Concluídas', value: 156, color: '#10b981' },
  { name: 'Em Andamento', value: 45, color: '#6366f1' },
  { name: 'Pendentes', value: 23, color: '#f59e0b' },
  { name: 'Atrasadas', value: 8, color: '#ef4444' },
];

interface FieldTeam {
  id: string;
  name: string;
  role: string;
  status: 'available' | 'busy' | 'offline' | 'break';
  currentLocation: string;
  currentTask: string | null;
  completedToday: number;
  lastUpdate: string;
}

const fieldTeams: FieldTeam[] = [
  {
    id: '1',
    name: 'Carlos Eduardo',
    role: 'Técnico Sênior',
    status: 'busy',
    currentLocation: 'Shopping Center Norte',
    currentTask: 'OS-2026-0145 - Manutenção CFTV',
    completedToday: 4,
    lastUpdate: '2026-01-15T14:30:00',
  },
  {
    id: '2',
    name: 'Roberto Silva',
    role: 'Técnico',
    status: 'available',
    currentLocation: 'Base Central',
    currentTask: null,
    completedToday: 5,
    lastUpdate: '2026-01-15T14:45:00',
  },
  {
    id: '3',
    name: 'Ana Paula',
    role: 'Supervisora',
    status: 'busy',
    currentLocation: 'Hospital São Lucas',
    currentTask: 'Vistoria mensal',
    completedToday: 3,
    lastUpdate: '2026-01-15T14:20:00',
  },
  {
    id: '4',
    name: 'Pedro Santos',
    role: 'Técnico',
    status: 'break',
    currentLocation: 'Condomínio Aurora',
    currentTask: null,
    completedToday: 3,
    lastUpdate: '2026-01-15T13:00:00',
  },
];

interface RecentOrder {
  id: string;
  number: string;
  client: string;
  type: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  technician: string;
  scheduledDate: string;
}

const recentOrders: RecentOrder[] = [
  {
    id: '1',
    number: 'OS-2026-0148',
    client: 'Tech Park Empresarial',
    type: 'Instalação',
    priority: 'high',
    status: 'pending',
    technician: 'Roberto Silva',
    scheduledDate: '2026-01-15T16:00:00',
  },
  {
    id: '2',
    number: 'OS-2026-0147',
    client: 'Condomínio Aurora',
    type: 'Manutenção Preventiva',
    priority: 'medium',
    status: 'in_progress',
    technician: 'Pedro Santos',
    scheduledDate: '2026-01-15T14:00:00',
  },
  {
    id: '3',
    number: 'OS-2026-0146',
    client: 'Hospital São Lucas',
    type: 'Corretiva',
    priority: 'urgent',
    status: 'in_progress',
    technician: 'Carlos Eduardo',
    scheduledDate: '2026-01-15T10:00:00',
  },
  {
    id: '4',
    number: 'OS-2026-0145',
    client: 'Shopping Center Norte',
    type: 'Manutenção CFTV',
    priority: 'medium',
    status: 'completed',
    technician: 'Carlos Eduardo',
    scheduledDate: '2026-01-15T08:00:00',
  },
];

const statusConfig = {
  available: { label: 'Disponível', color: 'success' as const },
  busy: { label: 'Em Atendimento', color: 'primary' as const },
  offline: { label: 'Offline', color: 'neutral' as const },
  break: { label: 'Intervalo', color: 'warning' as const },
};

const priorityConfig = {
  low: { label: 'Baixa', color: 'neutral' as const },
  medium: { label: 'Média', color: 'info' as const },
  high: { label: 'Alta', color: 'warning' as const },
  urgent: { label: 'Urgente', color: 'danger' as const },
};

const orderStatusConfig = {
  pending: { label: 'Pendente', color: 'warning' as const },
  in_progress: { label: 'Em Andamento', color: 'primary' as const },
  completed: { label: 'Concluída', color: 'success' as const },
  cancelled: { label: 'Cancelada', color: 'neutral' as const },
};

const teamColumns: Column<FieldTeam>[] = [
  {
    key: 'name',
    header: 'Técnico',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="relative">
          <Avatar name={row.name} size="sm" />
          <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-bg-secondary ${
            row.status === 'available' ? 'bg-success' :
            row.status === 'busy' ? 'bg-primary' :
            row.status === 'break' ? 'bg-warning' : 'bg-neutral'
          }`} />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.role}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'location',
    header: 'Localização',
    render: (row) => (
      <div className="flex items-center gap-2">
        <MapPin className="w-4 h-4 text-text-muted" />
        <span className="text-sm text-text-secondary">{row.currentLocation}</span>
      </div>
    ),
  },
  {
    key: 'task',
    header: 'Tarefa Atual',
    render: (row) => (
      row.currentTask ? (
        <span className="text-sm text-text-primary">{row.currentTask}</span>
      ) : (
        <span className="text-sm text-text-muted">-</span>
      )
    ),
  },
  {
    key: 'completed',
    header: 'Hoje',
    render: (row) => (
      <span className="font-mono font-medium text-success">{row.completedToday}</span>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver localização">
          <Navigation className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Ligar">
          <Phone className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const orderColumns: Column<RecentOrder>[] = [
  {
    key: 'number',
    header: 'OS',
    render: (row) => (
      <span className="font-mono text-sm font-medium text-accent-primary">{row.number}</span>
    ),
  },
  {
    key: 'client',
    header: 'Cliente',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.client}</p>
        <p className="text-xs text-text-muted">{row.type}</p>
      </div>
    ),
  },
  {
    key: 'priority',
    header: 'Prioridade',
    render: (row) => {
      const config = priorityConfig[row.priority];
      return <Badge variant={config.color} size="sm">{config.label}</Badge>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = orderStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'technician',
    header: 'Técnico',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.technician} size="xs" />
        <span className="text-sm">{row.technician}</span>
      </div>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <Button variant="ghost" size="icon-sm">
        <Eye className="w-4 h-4" />
      </Button>
    ),
  },
];

export function CampoDashboardPage() {
  // Stats
  const totalOrders = 232;
  const completedToday = 45;
  const inProgress = 12;
  const avgTime = '1h 45min';

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Operações de Campo
            </h1>
            <p className="text-text-secondary mt-1">
              Monitoramento em tempo real das equipes externas
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<MapPin className="w-4 h-4" />}>
              Mapa ao Vivo
            </Button>
            <Button variant="primary" leftIcon={<ClipboardCheck className="w-4 h-4" />}>
              Nova OS
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Ordens Hoje"
              value={totalOrders}
              change={12}
              icon={<ClipboardCheck className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Concluídas"
              value={completedToday}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Em Andamento"
              value={inProgress}
              icon={<Truck className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Tempo Médio"
              value={avgTime}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Técnicos Ativos"
              value={fieldTeams.filter(t => t.status !== 'offline').length}
              icon={<Users className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-3 gap-6">
          {/* Weekly Performance */}
          <Card className="col-span-2">
            <CardHeader title="Desempenho Semanal" subtitle="Visitas agendadas vs realizadas" />
            <CardBody>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dailyVisits}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d', borderRadius: '8px' }}
                    />
                    <Bar dataKey="agendadas" name="Agendadas" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="realizadas" name="Realizadas" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Orders by Status */}
          <Card>
            <CardHeader title="Status das OS" />
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={ordersByStatus}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={70}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {ordersByStatus.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d', borderRadius: '8px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-2 mt-4">
                {ordersByStatus.map((item) => (
                  <div key={item.name} className="flex items-center gap-2 text-xs">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-text-secondary">{item.name}</span>
                    <span className="font-medium text-text-primary ml-auto">{item.value}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Field Teams */}
        <Card>
          <CardHeader
            title="Equipe em Campo"
            subtitle="Status em tempo real"
            action={<Button variant="ghost" size="sm">Ver Mapa</Button>}
          />
          <CardBody className="p-0">
            <DataTable columns={teamColumns} data={fieldTeams} keyExtractor={(row) => row.id} />
          </CardBody>
        </Card>

        {/* Recent Orders */}
        <Card>
          <CardHeader
            title="Ordens de Serviço Recentes"
            action={<Button variant="ghost" size="sm">Ver Todas</Button>}
          />
          <CardBody className="p-0">
            <DataTable columns={orderColumns} data={recentOrders} keyExtractor={(row) => row.id} />
          </CardBody>
        </Card>

        {/* Alerts */}
        <div className="grid grid-cols-2 gap-4">
          <Card className="border-danger/30 bg-danger/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-danger/10">
                  <AlertTriangle className="w-6 h-6 text-danger" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">3 OS com atraso</p>
                  <p className="text-sm text-text-secondary mt-1">
                    Ordens ultrapassaram o tempo previsto de execução
                  </p>
                </div>
                <Button variant="danger" size="sm">Ver OS</Button>
              </div>
            </CardBody>
          </Card>

          <Card className="border-warning/30 bg-warning/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-warning/10">
                  <Clock className="w-6 h-6 text-warning" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">5 visitas pendentes hoje</p>
                  <p className="text-sm text-text-secondary mt-1">
                    Redistribua para técnicos disponíveis
                  </p>
                </div>
                <Button variant="outline" size="sm">Redistribuir</Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
