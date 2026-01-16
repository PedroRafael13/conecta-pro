'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  RefreshCw,
  Camera,
  Video,
  Radio,
  Lock,
  Wifi,
  WifiOff,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Building2,
  MapPin,
  Settings,
  Activity,
  Zap,
  ThermometerSun,
  HardDrive,
  Signal,
  Battery,
  Eye,
  Wrench,
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
  Select,
  Modal,
} from '@/design-system/components';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

// Types
interface Equipment {
  id: string;
  name: string;
  type: 'camera' | 'dvr' | 'access_control' | 'alarm' | 'intercom' | 'sensor';
  model: string;
  serialNumber: string;
  status: 'online' | 'offline' | 'warning' | 'maintenance';
  client: string;
  location: string;
  ipAddress: string;
  lastSeen: string;
  uptime: string;
  temperature: number | null;
  storageUsed: number | null;
  signalStrength: number | null;
  batteryLevel: number | null;
  lastMaintenance: string;
  nextMaintenance: string;
}

// Mock Data
const equipment: Equipment[] = [
  {
    id: '1',
    name: 'Câmera PTZ Entrada Principal',
    type: 'camera',
    model: 'Hikvision DS-2DE4225IW',
    serialNumber: 'HIK-2025-001234',
    status: 'online',
    client: 'Shopping Center Norte',
    location: 'Entrada Principal',
    ipAddress: '192.168.1.101',
    lastSeen: '2026-01-15 14:30:00',
    uptime: '45d 12h 34m',
    temperature: 42,
    storageUsed: null,
    signalStrength: 95,
    batteryLevel: null,
    lastMaintenance: '2025-12-15',
    nextMaintenance: '2026-03-15',
  },
  {
    id: '2',
    name: 'DVR Principal',
    type: 'dvr',
    model: 'Intelbras MHDX 3116',
    serialNumber: 'INT-2024-005678',
    status: 'online',
    client: 'Shopping Center Norte',
    location: 'Sala de Monitoramento',
    ipAddress: '192.168.1.10',
    lastSeen: '2026-01-15 14:30:00',
    uptime: '120d 5h 12m',
    temperature: 38,
    storageUsed: 72,
    signalStrength: null,
    batteryLevel: null,
    lastMaintenance: '2025-11-01',
    nextMaintenance: '2026-02-01',
  },
  {
    id: '3',
    name: 'Câmera Bullet Estacionamento',
    type: 'camera',
    model: 'Intelbras VHD 3230 B',
    serialNumber: 'INT-2025-003456',
    status: 'offline',
    client: 'Tech Park Empresarial',
    location: 'Estacionamento Subsolo',
    ipAddress: '192.168.2.105',
    lastSeen: '2026-01-15 08:45:00',
    uptime: '0d 0h 0m',
    temperature: null,
    storageUsed: null,
    signalStrength: 0,
    batteryLevel: null,
    lastMaintenance: '2025-10-20',
    nextMaintenance: '2026-01-20',
  },
  {
    id: '4',
    name: 'Controlador de Acesso Portaria',
    type: 'access_control',
    model: 'Control iD iDFlex',
    serialNumber: 'CID-2025-007890',
    status: 'warning',
    client: 'Hospital São Lucas',
    location: 'Portaria Principal',
    ipAddress: '192.168.3.50',
    lastSeen: '2026-01-15 14:28:00',
    uptime: '30d 8h 45m',
    temperature: 45,
    storageUsed: null,
    signalStrength: 78,
    batteryLevel: null,
    lastMaintenance: '2025-12-01',
    nextMaintenance: '2026-03-01',
  },
  {
    id: '5',
    name: 'Central de Alarme',
    type: 'alarm',
    model: 'Intelbras AMT 4010',
    serialNumber: 'INT-2024-009012',
    status: 'online',
    client: 'Condomínio Aurora',
    location: 'Guarita Principal',
    ipAddress: '192.168.4.20',
    lastSeen: '2026-01-15 14:30:00',
    uptime: '90d 2h 15m',
    temperature: 35,
    storageUsed: null,
    signalStrength: 100,
    batteryLevel: 100,
    lastMaintenance: '2025-09-15',
    nextMaintenance: '2026-03-15',
  },
  {
    id: '6',
    name: 'Sensor de Movimento Bloco B',
    type: 'sensor',
    model: 'Intelbras IVP 3000 MW',
    serialNumber: 'INT-2025-002345',
    status: 'maintenance',
    client: 'Banco Regional',
    location: 'Bloco B - Corredor',
    ipAddress: '192.168.5.80',
    lastSeen: '2026-01-14 16:00:00',
    uptime: '0d 0h 0m',
    temperature: null,
    storageUsed: null,
    signalStrength: null,
    batteryLevel: 15,
    lastMaintenance: '2026-01-14',
    nextMaintenance: '2026-01-16',
  },
  {
    id: '7',
    name: 'Interfone IP Recepção',
    type: 'intercom',
    model: 'Intelbras TIP 125i',
    serialNumber: 'INT-2025-004567',
    status: 'online',
    client: 'Tech Park Empresarial',
    location: 'Recepção Principal',
    ipAddress: '192.168.2.30',
    lastSeen: '2026-01-15 14:29:00',
    uptime: '60d 14h 22m',
    temperature: 32,
    storageUsed: null,
    signalStrength: 92,
    batteryLevel: null,
    lastMaintenance: '2025-11-10',
    nextMaintenance: '2026-02-10',
  },
];

const typeConfig = {
  camera: { label: 'Câmera', icon: Camera, color: 'primary' as const },
  dvr: { label: 'DVR/NVR', icon: Video, color: 'info' as const },
  access_control: { label: 'Controle Acesso', icon: Lock, color: 'success' as const },
  alarm: { label: 'Alarme', icon: Radio, color: 'warning' as const },
  intercom: { label: 'Interfone', icon: Radio, color: 'neutral' as const },
  sensor: { label: 'Sensor', icon: Activity, color: 'danger' as const },
};

const statusConfig = {
  online: { label: 'Online', color: 'success' as const, icon: CheckCircle2 },
  offline: { label: 'Offline', color: 'danger' as const, icon: XCircle },
  warning: { label: 'Alerta', color: 'warning' as const, icon: AlertTriangle },
  maintenance: { label: 'Manutenção', color: 'info' as const, icon: Wrench },
};

const statusChartData = [
  { name: 'Online', value: equipment.filter(e => e.status === 'online').length, color: '#10b981' },
  { name: 'Offline', value: equipment.filter(e => e.status === 'offline').length, color: '#ef4444' },
  { name: 'Alerta', value: equipment.filter(e => e.status === 'warning').length, color: '#f59e0b' },
  { name: 'Manutenção', value: equipment.filter(e => e.status === 'maintenance').length, color: '#3b82f6' },
];

const columns: Column<Equipment>[] = [
  {
    key: 'equipment',
    header: 'Equipamento',
    render: (row) => {
      const config = typeConfig[row.type];
      const TypeIcon = config.icon;
      return (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-bg-tertiary`}>
            <TypeIcon className="w-5 h-5 text-text-muted" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.model}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const config = typeConfig[row.type];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'location',
    header: 'Localização',
    render: (row) => (
      <div>
        <div className="flex items-center gap-1">
          <Building2 className="w-3 h-3 text-text-muted" />
          <p className="text-sm text-text-primary">{row.client}</p>
        </div>
        <div className="flex items-center gap-1 mt-1">
          <MapPin className="w-3 h-3 text-text-muted" />
          <p className="text-xs text-text-muted">{row.location}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'network',
    header: 'Rede',
    render: (row) => (
      <div>
        <p className="text-sm font-mono text-text-secondary">{row.ipAddress}</p>
        {row.signalStrength !== null && (
          <div className="flex items-center gap-1 mt-1">
            <Signal className={`w-3 h-3 ${
              row.signalStrength >= 80 ? 'text-accent-success' :
              row.signalStrength >= 50 ? 'text-accent-warning' : 'text-accent-danger'
            }`} />
            <span className="text-xs text-text-muted">{row.signalStrength}%</span>
          </div>
        )}
      </div>
    ),
  },
  {
    key: 'metrics',
    header: 'Métricas',
    render: (row) => (
      <div className="flex items-center gap-3">
        {row.temperature !== null && (
          <div className="flex items-center gap-1" title="Temperatura">
            <ThermometerSun className={`w-4 h-4 ${
              row.temperature > 50 ? 'text-accent-danger' :
              row.temperature > 40 ? 'text-accent-warning' : 'text-accent-success'
            }`} />
            <span className="text-xs">{row.temperature}°C</span>
          </div>
        )}
        {row.storageUsed !== null && (
          <div className="flex items-center gap-1" title="Armazenamento">
            <HardDrive className={`w-4 h-4 ${
              row.storageUsed > 90 ? 'text-accent-danger' :
              row.storageUsed > 75 ? 'text-accent-warning' : 'text-accent-success'
            }`} />
            <span className="text-xs">{row.storageUsed}%</span>
          </div>
        )}
        {row.batteryLevel !== null && (
          <div className="flex items-center gap-1" title="Bateria">
            <Battery className={`w-4 h-4 ${
              row.batteryLevel < 20 ? 'text-accent-danger' :
              row.batteryLevel < 50 ? 'text-accent-warning' : 'text-accent-success'
            }`} />
            <span className="text-xs">{row.batteryLevel}%</span>
          </div>
        )}
      </div>
    ),
  },
  {
    key: 'uptime',
    header: 'Uptime',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.uptime}</p>
        <p className="text-xs text-text-muted">Última vez: {row.lastSeen.split(' ')[1]}</p>
      </div>
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
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Configurar">
          <Settings className="w-4 h-4" />
        </Button>
        {row.status === 'offline' && (
          <Button variant="ghost" size="icon-sm" title="Verificar">
            <RefreshCw className="w-4 h-4" />
          </Button>
        )}
      </div>
    ),
  },
];

export function EquipmentStatusPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [filterClient, setFilterClient] = useState('all');

  // Stats
  const totalEquipment = equipment.length;
  const onlineCount = equipment.filter(e => e.status === 'online').length;
  const offlineCount = equipment.filter(e => e.status === 'offline').length;
  const warningCount = equipment.filter(e => e.status === 'warning').length;
  const maintenanceCount = equipment.filter(e => e.status === 'maintenance').length;
  const healthPercentage = Math.round((onlineCount / totalEquipment) * 100);

  const filteredEquipment = equipment.filter((eq) => {
    const matchesSearch =
      eq.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eq.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eq.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eq.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab =
      selectedTab === 'all' ||
      eq.status === selectedTab ||
      eq.type === selectedTab;
    return matchesSearch && matchesTab;
  });

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Status dos Equipamentos
            </h1>
            <p className="text-text-secondary mt-1">
              Monitore o status de todos os equipamentos em campo
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              leftIcon={<RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />}
              onClick={handleRefresh}
              disabled={isRefreshing}
            >
              Atualizar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-6 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total"
              value={totalEquipment}
              icon={<Settings className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Online"
              value={onlineCount}
              icon={<Wifi className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Offline"
              value={offlineCount}
              icon={<WifiOff className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Alerta"
              value={warningCount}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Manutenção"
              value={maintenanceCount}
              icon={<Wrench className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <StatCard
              title="Saúde"
              value={`${healthPercentage}%`}
              icon={<Activity className="w-6 h-6" />}
              iconColor={healthPercentage >= 90 ? 'success' : healthPercentage >= 70 ? 'warning' : 'danger'}
            />
          </motion.div>
        </div>

        {/* Chart */}
        <div className="grid grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="col-span-1"
          >
            <Card className="h-full">
              <CardHeader title="Status Geral" />
              <CardBody>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={70}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {statusChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="col-span-2"
          >
            <Card className="h-full">
              <CardHeader title="Equipamentos por Tipo" />
              <CardBody>
                <div className="grid grid-cols-3 gap-4">
                  {Object.entries(typeConfig).map(([type, config]) => {
                    const count = equipment.filter(e => e.type === type).length;
                    const TypeIcon = config.icon;
                    return (
                      <div key={type} className="p-4 bg-bg-tertiary rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-bg-primary rounded-lg">
                            <TypeIcon className="w-5 h-5 text-text-muted" />
                          </div>
                          <div>
                            <p className="text-xl font-bold text-text-primary">{count}</p>
                            <p className="text-xs text-text-muted">{config.label}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: 'Todos' },
                  { value: 'online', label: `Online (${onlineCount})` },
                  { value: 'offline', label: `Offline (${offlineCount})` },
                  { value: 'warning', label: `Alerta (${warningCount})` },
                  { value: 'maintenance', label: `Manutenção (${maintenanceCount})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar equipamento..."
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
                  value={filterClient}
                  onChange={(value) => setFilterClient(value)}
                  className="w-48"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Equipment Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredEquipment}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => { setSelectedEquipment(row); setShowDetailModal(true); }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes do Equipamento"
          description={selectedEquipment ? selectedEquipment.name : ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              <Button variant="primary">Configurar</Button>
            </>
          }
        >
          {selectedEquipment && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className="p-3 rounded-lg bg-bg-primary">
                  {(() => {
                    const TypeIcon = typeConfig[selectedEquipment.type].icon;
                    return <TypeIcon className="w-6 h-6 text-text-muted" />;
                  })()}
                </div>
                <div className="flex-1">
                  <p className="text-lg font-medium text-text-primary">{selectedEquipment.name}</p>
                  <p className="text-sm text-text-muted">{selectedEquipment.model}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={typeConfig[selectedEquipment.type].color}>{typeConfig[selectedEquipment.type].label}</Badge>
                    <Badge variant={statusConfig[selectedEquipment.status].color}>{statusConfig[selectedEquipment.status].label}</Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Número de Série</p>
                  <p className="font-mono font-medium text-text-primary">{selectedEquipment.serialNumber}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Endereço IP</p>
                  <p className="font-mono font-medium text-text-primary">{selectedEquipment.ipAddress}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Cliente</p>
                  <p className="font-medium text-text-primary">{selectedEquipment.client}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Localização</p>
                  <p className="font-medium text-text-primary">{selectedEquipment.location}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Uptime</p>
                  <p className="font-medium text-text-primary">{selectedEquipment.uptime}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Última Comunicação</p>
                  <p className="font-medium text-text-primary">{selectedEquipment.lastSeen}</p>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4">
                {selectedEquipment.temperature !== null && (
                  <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                    <ThermometerSun className={`w-6 h-6 mx-auto mb-2 ${
                      selectedEquipment.temperature > 50 ? 'text-accent-danger' :
                      selectedEquipment.temperature > 40 ? 'text-accent-warning' : 'text-accent-success'
                    }`} />
                    <p className="text-lg font-bold text-text-primary">{selectedEquipment.temperature}°C</p>
                    <p className="text-xs text-text-muted">Temperatura</p>
                  </div>
                )}
                {selectedEquipment.storageUsed !== null && (
                  <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                    <HardDrive className={`w-6 h-6 mx-auto mb-2 ${
                      selectedEquipment.storageUsed > 90 ? 'text-accent-danger' :
                      selectedEquipment.storageUsed > 75 ? 'text-accent-warning' : 'text-accent-success'
                    }`} />
                    <p className="text-lg font-bold text-text-primary">{selectedEquipment.storageUsed}%</p>
                    <p className="text-xs text-text-muted">Armazenamento</p>
                  </div>
                )}
                {selectedEquipment.signalStrength !== null && (
                  <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                    <Signal className={`w-6 h-6 mx-auto mb-2 ${
                      selectedEquipment.signalStrength >= 80 ? 'text-accent-success' :
                      selectedEquipment.signalStrength >= 50 ? 'text-accent-warning' : 'text-accent-danger'
                    }`} />
                    <p className="text-lg font-bold text-text-primary">{selectedEquipment.signalStrength}%</p>
                    <p className="text-xs text-text-muted">Sinal</p>
                  </div>
                )}
                {selectedEquipment.batteryLevel !== null && (
                  <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                    <Battery className={`w-6 h-6 mx-auto mb-2 ${
                      selectedEquipment.batteryLevel < 20 ? 'text-accent-danger' :
                      selectedEquipment.batteryLevel < 50 ? 'text-accent-warning' : 'text-accent-success'
                    }`} />
                    <p className="text-lg font-bold text-text-primary">{selectedEquipment.batteryLevel}%</p>
                    <p className="text-xs text-text-muted">Bateria</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Última Manutenção</p>
                  <p className="font-medium text-text-primary">{selectedEquipment.lastMaintenance}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Próxima Manutenção</p>
                  <p className="font-medium text-text-primary">{selectedEquipment.nextMaintenance}</p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
