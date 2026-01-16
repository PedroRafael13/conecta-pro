'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Activity,
  MapPin,
  Users,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Radio,
  Wifi,
  WifiOff,
  Battery,
  BatteryLow,
  Navigation,
  RefreshCw,
  Settings,
  MoreHorizontal,
  Phone,
  MessageSquare,
  Shield,
  Camera,
  Bell,
  TrendingUp,
  Map,
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
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
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
  AreaChart,
  Area,
} from 'recharts';

// Types
interface FieldAgent {
  id: string;
  name: string;
  role: string;
  location: string;
  coordinates: { lat: number; lng: number };
  status: 'online' | 'offline' | 'break' | 'emergency';
  batteryLevel: number;
  signalStrength: 'strong' | 'medium' | 'weak' | 'none';
  lastUpdate: string;
  currentTask: string | null;
  shiftsCompleted: number;
  alertsRaised: number;
}

interface MonitoringAlert {
  id: string;
  type: 'emergency' | 'connection_lost' | 'battery_low' | 'deviation' | 'sos';
  agentName: string;
  location: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'acknowledged' | 'resolved';
  timestamp: string;
}

// Mock Data
const agents: FieldAgent[] = [
  {
    id: '1',
    name: 'Carlos Silva',
    role: 'Vigilante',
    location: 'Shopping Center Norte - Setor A',
    coordinates: { lat: -23.5105, lng: -46.6250 },
    status: 'online',
    batteryLevel: 85,
    signalStrength: 'strong',
    lastUpdate: '2026-01-16 10:15',
    currentTask: 'Ronda - Área Externa',
    shiftsCompleted: 156,
    alertsRaised: 3,
  },
  {
    id: '2',
    name: 'Maria Santos',
    role: 'Supervisora',
    location: 'Hospital São Lucas - Portaria Principal',
    coordinates: { lat: -23.5505, lng: -46.6333 },
    status: 'online',
    batteryLevel: 92,
    signalStrength: 'strong',
    lastUpdate: '2026-01-16 10:14',
    currentTask: 'Supervisão - Equipe Noturna',
    shiftsCompleted: 234,
    alertsRaised: 1,
  },
  {
    id: '3',
    name: 'Roberto Lima',
    role: 'Vigilante',
    location: 'Condomínio Aurora - Bloco B',
    coordinates: { lat: -23.4867, lng: -46.5890 },
    status: 'break',
    batteryLevel: 45,
    signalStrength: 'medium',
    lastUpdate: '2026-01-16 10:00',
    currentTask: null,
    shiftsCompleted: 98,
    alertsRaised: 5,
  },
  {
    id: '4',
    name: 'Ana Costa',
    role: 'Vigilante',
    location: 'Edifício Corporate - Subsolo',
    coordinates: { lat: -23.5633, lng: -46.6543 },
    status: 'online',
    batteryLevel: 23,
    signalStrength: 'weak',
    lastUpdate: '2026-01-16 10:10',
    currentTask: 'Ronda - Estacionamento',
    shiftsCompleted: 67,
    alertsRaised: 2,
  },
  {
    id: '5',
    name: 'Pedro Almeida',
    role: 'Porteiro',
    location: 'Condomínio Sol Nascente',
    coordinates: { lat: -23.5234, lng: -46.6789 },
    status: 'offline',
    batteryLevel: 0,
    signalStrength: 'none',
    lastUpdate: '2026-01-16 08:45',
    currentTask: null,
    shiftsCompleted: 45,
    alertsRaised: 0,
  },
];

const alerts: MonitoringAlert[] = [
  { id: '1', type: 'battery_low', agentName: 'Ana Costa', location: 'Edifício Corporate', message: 'Bateria em 23% - Necessita recarga', severity: 'medium', status: 'active', timestamp: '2026-01-16 10:10' },
  { id: '2', type: 'connection_lost', agentName: 'Pedro Almeida', location: 'Condomínio Sol Nascente', message: 'Dispositivo offline há 1h30m', severity: 'high', status: 'acknowledged', timestamp: '2026-01-16 08:45' },
  { id: '3', type: 'deviation', agentName: 'Roberto Lima', location: 'Condomínio Aurora', message: 'Desvio de rota detectado', severity: 'low', status: 'resolved', timestamp: '2026-01-16 09:30' },
];

const activityTimeline = [
  { hour: '06h', online: 12, tasks: 8 },
  { hour: '08h', online: 18, tasks: 15 },
  { hour: '10h', online: 22, tasks: 20 },
  { hour: '12h', online: 20, tasks: 16 },
  { hour: '14h', online: 21, tasks: 18 },
  { hour: '16h', online: 19, tasks: 17 },
  { hour: '18h', online: 24, tasks: 22 },
  { hour: '20h', online: 26, tasks: 25 },
];

const signalQuality = [
  { time: '10:00', quality: 95 },
  { time: '10:05', quality: 92 },
  { time: '10:10', quality: 88 },
  { time: '10:15', quality: 94 },
];

const tabs = [
  { id: 'map', label: 'Mapa' },
  { id: 'list', label: 'Lista' },
  { id: 'alerts', label: 'Alertas' },
];

const statusConfig = {
  online: { label: 'Online', color: 'success', icon: Radio },
  offline: { label: 'Offline', color: 'secondary', icon: WifiOff },
  break: { label: 'Pausa', color: 'warning', icon: Clock },
  emergency: { label: 'Emergência', color: 'danger', icon: AlertTriangle },
} as const;

const severityColors = {
  low: 'info',
  medium: 'warning',
  high: 'danger',
  critical: 'danger',
} as const;

const alertTypeIcons = {
  emergency: AlertTriangle,
  connection_lost: WifiOff,
  battery_low: BatteryLow,
  deviation: Navigation,
  sos: Bell,
};

const agentColumns: Column<FieldAgent>[] = [
  {
    key: 'name',
    header: 'Agente',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="relative">
          <Avatar name={row.name} size="sm" />
          <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${row.status === 'online' ? 'bg-success' : row.status === 'break' ? 'bg-warning' : row.status === 'emergency' ? 'bg-danger' : 'bg-text-muted'}`} />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.role}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'location',
    header: 'Localização',
    render: (row) => (
      <div className="flex items-center gap-2">
        <MapPin className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.location}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      const Icon = config.icon;
      return (
        <Badge variant={config.color as any}>
          <Icon className="w-3 h-3 mr-1" />
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'batteryLevel',
    header: 'Bateria',
    render: (row) => (
      <div className="flex items-center gap-2">
        {row.batteryLevel > 20 ? <Battery className="w-4 h-4 text-success" /> : <BatteryLow className="w-4 h-4 text-danger" />}
        <span className={`text-sm font-medium ${row.batteryLevel > 20 ? '' : 'text-danger'}`}>{row.batteryLevel}%</span>
      </div>
    ),
  },
  {
    key: 'signalStrength',
    header: 'Sinal',
    render: (row) => {
      const signalConfig = {
        strong: { bars: 4, color: 'text-success' },
        medium: { bars: 3, color: 'text-warning' },
        weak: { bars: 2, color: 'text-danger' },
        none: { bars: 0, color: 'text-text-muted' },
      };
      const config = signalConfig[row.signalStrength];
      return (
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className={`w-1 rounded ${i <= config.bars ? config.color.replace('text-', 'bg-') : 'bg-bg-tertiary'}`}
              style={{ height: `${i * 4 + 4}px` }}
            />
          ))}
        </div>
      );
    },
  },
  {
    key: 'currentTask',
    header: 'Tarefa Atual',
    render: (row) => (
      row.currentTask ? (
        <span className="text-sm">{row.currentTask}</span>
      ) : (
        <span className="text-sm text-text-muted">Sem tarefa</span>
      )
    ),
  },
  {
    key: 'lastUpdate',
    header: 'Última Atualização',
    render: (row) => <span className="text-sm text-text-muted">{row.lastUpdate}</span>,
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver no Mapa">
          <Map className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Ligar">
          <Phone className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Mensagem">
          <MessageSquare className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const alertColumns: Column<MonitoringAlert>[] = [
  {
    key: 'timestamp',
    header: 'Data/Hora',
    render: (row) => <span className="text-sm">{row.timestamp}</span>,
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const Icon = alertTypeIcons[row.type];
      const typeLabels = {
        emergency: 'Emergência',
        connection_lost: 'Conexão Perdida',
        battery_low: 'Bateria Baixa',
        deviation: 'Desvio de Rota',
        sos: 'SOS',
      };
      return (
        <div className="flex items-center gap-2">
          <Icon className={`w-4 h-4 ${row.severity === 'critical' || row.severity === 'high' ? 'text-danger' : row.severity === 'medium' ? 'text-warning' : 'text-info'}`} />
          <span className="text-sm">{typeLabels[row.type]}</span>
        </div>
      );
    },
  },
  {
    key: 'agentName',
    header: 'Agente',
    render: (row) => <span className="font-medium">{row.agentName}</span>,
  },
  {
    key: 'message',
    header: 'Mensagem',
    render: (row) => <span className="text-sm text-text-secondary">{row.message}</span>,
  },
  {
    key: 'severity',
    header: 'Severidade',
    render: (row) => (
      <Badge variant={severityColors[row.severity]}>
        {row.severity === 'critical' ? 'Crítico' : row.severity === 'high' ? 'Alto' : row.severity === 'medium' ? 'Médio' : 'Baixo'}
      </Badge>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={row.status === 'active' ? 'danger' : row.status === 'acknowledged' ? 'warning' : 'success'}>
        {row.status === 'active' ? 'Ativo' : row.status === 'acknowledged' ? 'Reconhecido' : 'Resolvido'}
      </Badge>
    ),
  },
];

export function FieldMonitoringPage() {
  const [activeTab, setActiveTab] = useState('list');
  const [searchTerm, setSearchTerm] = useState('');

  // Stats
  const onlineAgents = agents.filter((a) => a.status === 'online').length;
  const totalAgents = agents.length;
  const activeAlerts = alerts.filter((a) => a.status === 'active').length;
  const avgBattery = Math.round(agents.reduce((acc, a) => acc + a.batteryLevel, 0) / agents.length);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Monitoramento de Campo</h1>
            <p className="text-text-secondary mt-1">Acompanhamento em tempo real de agentes em campo</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Atualizar
            </Button>
            <Button variant="primary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Agentes Online" value={`${onlineAgents}/${totalAgents}`} icon={<Users className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Alertas Ativos" value={activeAlerts} icon={<AlertTriangle className="w-6 h-6" />} iconColor="danger" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Bateria Média" value={`${avgBattery}%`} icon={<Battery className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Tarefas em Andamento" value={agents.filter((a) => a.currentTask).length} icon={<Activity className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Atividade do Dia</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={activityTimeline}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Area type="monotone" dataKey="online" fill="#3B82F680" stroke="#3B82F6" name="Agentes Online" />
                    <Area type="monotone" dataKey="tasks" fill="#10B98180" stroke="#10B981" name="Tarefas" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Wifi className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Qualidade do Sinal</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={signalQuality}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="time" stroke="var(--color-text-muted)" />
                    <YAxis domain={[80, 100]} stroke="var(--color-text-muted)" />
                    <Tooltip formatter={(value: number) => `${value}%`} />
                    <Line type="monotone" dataKey="quality" stroke="#10B981" strokeWidth={3} dot={{ fill: '#10B981', strokeWidth: 2 }} name="Qualidade %" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Content */}
        {activeTab === 'map' && (
          <Card>
            <CardBody>
              <div className="h-[500px] rounded-lg bg-bg-secondary flex items-center justify-center">
                <div className="text-center">
                  <Map className="w-16 h-16 text-text-muted mx-auto mb-4" />
                  <p className="text-text-muted">Mapa de localização dos agentes</p>
                  <p className="text-sm text-text-muted mt-1">Integração com Google Maps / OpenStreetMap</p>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'list' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input
                placeholder="Buscar agentes..."
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
                <DataTable columns={agentColumns} data={agents} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'alerts' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input
                placeholder="Buscar alertas..."
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
                <DataTable columns={alertColumns} data={alerts} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}
      </div>
    </MainLayout>
  );
}
