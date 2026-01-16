'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Download,
  RefreshCw,
  DoorOpen,
  DoorClosed,
  User,
  Building2,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Car,
  CreditCard,
  Fingerprint,
  QrCode,
  Key,
  Shield,
  TrendingUp,
  Calendar,
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
  Select,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Types
interface AccessLog {
  id: string;
  type: 'entry' | 'exit';
  method: 'card' | 'biometric' | 'qrcode' | 'manual' | 'vehicle';
  status: 'granted' | 'denied' | 'timeout' | 'forced';
  person: string;
  personType: 'employee' | 'visitor' | 'contractor' | 'vehicle';
  credential: string;
  device: string;
  location: string;
  client: string;
  timestamp: string;
  photo: string | null;
  notes: string;
}

// Mock Data
const accessLogs: AccessLog[] = [
  {
    id: '1',
    type: 'entry',
    method: 'biometric',
    status: 'granted',
    person: 'Carlos Eduardo Silva',
    personType: 'employee',
    credential: 'BIO-001234',
    device: 'CAT-001',
    location: 'Portaria Principal',
    client: 'Shopping Center Norte',
    timestamp: '2026-01-15 08:02:34',
    photo: null,
    notes: '',
  },
  {
    id: '2',
    type: 'entry',
    method: 'card',
    status: 'granted',
    person: 'Maria Santos',
    personType: 'visitor',
    credential: 'VISIT-20260115-001',
    device: 'CAT-002',
    location: 'Recepção Bloco A',
    client: 'Tech Park Empresarial',
    timestamp: '2026-01-15 08:15:22',
    photo: 'https://example.com/photo.jpg',
    notes: 'Visitante autorizado - Reunião sala 302',
  },
  {
    id: '3',
    type: 'exit',
    method: 'card',
    status: 'granted',
    person: 'Roberto Oliveira',
    personType: 'employee',
    credential: 'EMP-005678',
    device: 'CAT-001',
    location: 'Portaria Principal',
    client: 'Shopping Center Norte',
    timestamp: '2026-01-15 08:20:11',
    photo: null,
    notes: '',
  },
  {
    id: '4',
    type: 'entry',
    method: 'vehicle',
    status: 'granted',
    person: 'Veículo ABC-1234',
    personType: 'vehicle',
    credential: 'VEH-ABC1234',
    device: 'CAT-EST-01',
    location: 'Portão Estacionamento',
    client: 'Hospital São Lucas',
    timestamp: '2026-01-15 08:25:45',
    photo: null,
    notes: 'Veículo cadastrado - Médico Dr. Paulo',
  },
  {
    id: '5',
    type: 'entry',
    method: 'card',
    status: 'denied',
    person: 'Desconhecido',
    personType: 'visitor',
    credential: 'CARD-INVALID',
    device: 'CAT-003',
    location: 'Entrada Funcionários',
    client: 'Condomínio Aurora',
    timestamp: '2026-01-15 08:30:18',
    photo: 'https://example.com/photo2.jpg',
    notes: 'Cartão não reconhecido - Segurança notificada',
  },
  {
    id: '6',
    type: 'entry',
    method: 'qrcode',
    status: 'granted',
    person: 'Ana Paula Costa',
    personType: 'contractor',
    credential: 'QR-TEMP-0045',
    device: 'CAT-002',
    location: 'Recepção Bloco A',
    client: 'Tech Park Empresarial',
    timestamp: '2026-01-15 08:35:02',
    photo: null,
    notes: 'Prestador de serviço - Manutenção ar condicionado',
  },
  {
    id: '7',
    type: 'entry',
    method: 'manual',
    status: 'granted',
    person: 'Entrega Correios',
    personType: 'visitor',
    credential: 'MANUAL-001',
    device: 'CAT-001',
    location: 'Portaria Principal',
    client: 'Shopping Center Norte',
    timestamp: '2026-01-15 09:00:33',
    photo: null,
    notes: 'Liberação manual pelo vigilante Carlos',
  },
  {
    id: '8',
    type: 'entry',
    method: 'biometric',
    status: 'timeout',
    person: 'Pedro Santos',
    personType: 'employee',
    credential: 'BIO-002345',
    device: 'CAT-004',
    location: 'Sala Cofre',
    client: 'Banco Regional',
    timestamp: '2026-01-15 09:15:00',
    photo: null,
    notes: 'Timeout na leitura biométrica',
  },
];

const accessChartData = [
  { hour: '06:00', entries: 12, exits: 5 },
  { hour: '07:00', entries: 45, exits: 8 },
  { hour: '08:00', entries: 89, exits: 15 },
  { hour: '09:00', entries: 34, exits: 22 },
  { hour: '10:00', entries: 28, exits: 18 },
  { hour: '11:00', entries: 22, exits: 25 },
  { hour: '12:00', entries: 15, exits: 45 },
  { hour: '13:00', entries: 38, exits: 12 },
  { hour: '14:00', entries: 18, exits: 28 },
];

const methodConfig = {
  card: { label: 'Cartão', icon: CreditCard, color: 'info' as const },
  biometric: { label: 'Biometria', icon: Fingerprint, color: 'primary' as const },
  qrcode: { label: 'QR Code', icon: QrCode, color: 'success' as const },
  manual: { label: 'Manual', icon: Key, color: 'warning' as const },
  vehicle: { label: 'Veículo', icon: Car, color: 'neutral' as const },
};

const statusConfig = {
  granted: { label: 'Autorizado', color: 'success' as const, icon: CheckCircle2 },
  denied: { label: 'Negado', color: 'danger' as const, icon: XCircle },
  timeout: { label: 'Timeout', color: 'warning' as const, icon: AlertTriangle },
  forced: { label: 'Forçado', color: 'danger' as const, icon: AlertTriangle },
};

const personTypeConfig = {
  employee: { label: 'Funcionário', color: 'primary' as const },
  visitor: { label: 'Visitante', color: 'info' as const },
  contractor: { label: 'Prestador', color: 'warning' as const },
  vehicle: { label: 'Veículo', color: 'neutral' as const },
};

const columns: Column<AccessLog>[] = [
  {
    key: 'timestamp',
    header: 'Horário',
    render: (row) => (
      <div>
        <p className="text-sm font-mono text-text-primary">{row.timestamp.split(' ')[1]}</p>
        <p className="text-xs text-text-muted">{row.timestamp.split(' ')[0]}</p>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const isEntry = row.type === 'entry';
      return (
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg ${isEntry ? 'bg-accent-success/20' : 'bg-accent-info/20'}`}>
            {isEntry ? (
              <DoorOpen className="w-4 h-4 text-accent-success" />
            ) : (
              <DoorClosed className="w-4 h-4 text-accent-info" />
            )}
          </div>
          <span className="text-sm">{isEntry ? 'Entrada' : 'Saída'}</span>
        </div>
      );
    },
  },
  {
    key: 'person',
    header: 'Pessoa',
    render: (row) => (
      <div className="flex items-center gap-3">
        {row.personType === 'vehicle' ? (
          <div className="w-8 h-8 rounded-full bg-bg-tertiary flex items-center justify-center">
            <Car className="w-4 h-4 text-text-muted" />
          </div>
        ) : (
          <Avatar name={row.person} size="sm" />
        )}
        <div>
          <p className="font-medium text-text-primary">{row.person}</p>
          <Badge size="sm" variant={personTypeConfig[row.personType].color}>
            {personTypeConfig[row.personType].label}
          </Badge>
        </div>
      </div>
    ),
  },
  {
    key: 'method',
    header: 'Método',
    render: (row) => {
      const config = methodConfig[row.method];
      const MethodIcon = config.icon;
      return (
        <div className="flex items-center gap-2">
          <MethodIcon className="w-4 h-4 text-text-muted" />
          <span className="text-sm">{config.label}</span>
        </div>
      );
    },
  },
  {
    key: 'location',
    header: 'Local',
    render: (row) => (
      <div>
        <div className="flex items-center gap-1">
          <Building2 className="w-3 h-3 text-text-muted" />
          <p className="text-sm text-text-primary">{row.client}</p>
        </div>
        <p className="text-xs text-text-muted mt-1">{row.location}</p>
      </div>
    ),
  },
  {
    key: 'device',
    header: 'Dispositivo',
    render: (row) => (
      <span className="text-sm font-mono text-text-secondary">{row.device}</span>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      const StatusIcon = config.icon;
      return (
        <Badge variant={config.color} leftIcon={<StatusIcon className="w-3 h-3" />}>
          {config.label}
        </Badge>
      );
    },
  },
];

export function AccessLogPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isLive, setIsLive] = useState(true);

  // Stats
  const totalToday = accessLogs.length;
  const entriesCount = accessLogs.filter(l => l.type === 'entry').length;
  const deniedCount = accessLogs.filter(l => l.status === 'denied').length;
  const currentInside = entriesCount - accessLogs.filter(l => l.type === 'exit').length;

  const filteredLogs = accessLogs.filter((log) => {
    const matchesSearch =
      log.person.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.client.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab =
      selectedTab === 'all' ||
      (selectedTab === 'entries' && log.type === 'entry') ||
      (selectedTab === 'exits' && log.type === 'exit') ||
      (selectedTab === 'denied' && log.status === 'denied');
    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Registro de Acessos
            </h1>
            <p className="text-text-secondary mt-1">
              Monitore entradas e saídas em tempo real
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant={isLive ? 'success' : 'secondary'}
              leftIcon={<RefreshCw className={`w-4 h-4 ${isLive ? 'animate-spin' : ''}`} />}
              onClick={() => setIsLive(!isLive)}
            >
              {isLive ? 'Live' : 'Pausado'}
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Acessos Hoje"
              value={totalToday}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="primary"
              trend="up"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Entradas"
              value={entriesCount}
              icon={<DoorOpen className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Pessoas no Local"
              value={currentInside}
              icon={<User className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Acessos Negados"
              value={deniedCount}
              icon={<Shield className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Chart */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardHeader
              title="Fluxo de Acessos"
              subtitle="Entradas e saídas por hora"
              action={
                <Select
                  options={[
                    { value: 'today', label: 'Hoje' },
                    { value: 'yesterday', label: 'Ontem' },
                    { value: 'week', label: 'Esta Semana' },
                  ]}
                  value="today"
                  onChange={() => {}}
                  className="w-36"
                />
              }
            />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={accessChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                    <XAxis dataKey="hour" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="entries"
                      name="Entradas"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.2}
                    />
                    <Area
                      type="monotone"
                      dataKey="exits"
                      name="Saídas"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </motion.div>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: 'Todos' },
                  { value: 'entries', label: 'Entradas' },
                  { value: 'exits', label: 'Saídas' },
                  { value: 'denied', label: 'Negados' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todos os Clientes' },
                    { value: '1', label: 'Shopping Center Norte' },
                    { value: '2', label: 'Tech Park Empresarial' },
                    { value: '3', label: 'Hospital São Lucas' },
                  ]}
                  value="all"
                  onChange={() => {}}
                  className="w-48"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Access Logs Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredLogs}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => console.log('Access log clicked:', row)}
              />
            </CardBody>
          </Card>
        </motion.div>
      </div>
    </MainLayout>
  );
}
