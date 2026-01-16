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
  Clock,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Server,
  Wifi,
  WifiOff,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Settings,
  Eye,
  Edit,
  Trash2,
  Power,
  User,
  Users,
  MapPin,
  Calendar,
  Zap,
  Database,
  HardDrive,
  BarChart3,
  Play,
  Pause
} from 'lucide-react';
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
  Legend,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';

// Types
interface REPDevice {
  id: string;
  code: string;
  name: string;
  model: string;
  manufacturer: string;
  serialNumber: string;
  firmwareVersion: string;
  ipAddress: string;
  port: number;
  location: string;
  status: 'online' | 'offline' | 'syncing' | 'error';
  lastSync: string;
  recordsToday: number;
  employeesRegistered: number;
  memoryUsage: number;
  batteryLevel?: number;
  createdAt: string;
}

interface REPRecord {
  id: string;
  repId: string;
  repName: string;
  employeeId: string;
  employeeName: string;
  pis: string;
  recordType: 'entry' | 'exit' | 'break_start' | 'break_end';
  timestamp: string;
  nsr: string;
  synchronized: boolean;
  syncError?: string;
}

interface SyncLog {
  id: string;
  repId: string;
  repName: string;
  type: 'manual' | 'automatic' | 'scheduled';
  status: 'success' | 'partial' | 'failed';
  recordsImported: number;
  recordsFailed: number;
  duration: number;
  startedAt: string;
  completedAt: string;
  errorMessage?: string;
}

// Mock data
const mockDevices: REPDevice[] = [
  {
    id: 'REP001',
    code: 'REP-001',
    name: 'Portaria Principal',
    model: 'REP iDClass',
    manufacturer: 'Control iD',
    serialNumber: 'CID2024001234',
    firmwareVersion: '2.5.3',
    ipAddress: '192.168.1.100',
    port: 3000,
    location: 'Matriz - Entrada Principal',
    status: 'online',
    lastSync: '2024-01-15T08:30:00',
    recordsToday: 456,
    employeesRegistered: 234,
    memoryUsage: 45,
    createdAt: '2023-01-15'
  },
  {
    id: 'REP002',
    code: 'REP-002',
    name: 'Portaria Fundos',
    model: 'REP iDClass',
    manufacturer: 'Control iD',
    serialNumber: 'CID2024001235',
    firmwareVersion: '2.5.3',
    ipAddress: '192.168.1.101',
    port: 3000,
    location: 'Matriz - Entrada Fundos',
    status: 'online',
    lastSync: '2024-01-15T08:28:00',
    recordsToday: 234,
    employeesRegistered: 234,
    memoryUsage: 38,
    createdAt: '2023-01-15'
  },
  {
    id: 'REP003',
    code: 'REP-003',
    name: 'Refeitório',
    model: 'REP Henry Orion 6',
    manufacturer: 'Henry',
    serialNumber: 'HEN2024005678',
    firmwareVersion: '4.1.2',
    ipAddress: '192.168.1.102',
    port: 4370,
    location: 'Matriz - Refeitório',
    status: 'syncing',
    lastSync: '2024-01-15T08:25:00',
    recordsToday: 512,
    employeesRegistered: 234,
    memoryUsage: 62,
    createdAt: '2023-03-20'
  },
  {
    id: 'REP004',
    code: 'REP-004',
    name: 'Filial Campinas',
    model: 'REP Topdata Inner Rep Plus',
    manufacturer: 'Topdata',
    serialNumber: 'TOP2024009012',
    firmwareVersion: '3.0.8',
    ipAddress: '10.0.1.50',
    port: 5000,
    location: 'Filial Campinas - Recepção',
    status: 'offline',
    lastSync: '2024-01-14T18:00:00',
    recordsToday: 0,
    employeesRegistered: 89,
    memoryUsage: 55,
    batteryLevel: 78,
    createdAt: '2023-06-10'
  },
  {
    id: 'REP005',
    code: 'REP-005',
    name: 'Produção A',
    model: 'REP Dimep Printpoint III',
    manufacturer: 'Dimep',
    serialNumber: 'DIM2024003456',
    firmwareVersion: '5.2.1',
    ipAddress: '192.168.2.100',
    port: 4500,
    location: 'Matriz - Área de Produção A',
    status: 'error',
    lastSync: '2024-01-15T07:45:00',
    recordsToday: 189,
    employeesRegistered: 156,
    memoryUsage: 85,
    createdAt: '2023-08-05'
  }
];

const mockRecords: REPRecord[] = [
  {
    id: '1',
    repId: 'REP001',
    repName: 'Portaria Principal',
    employeeId: 'EMP001',
    employeeName: 'Carlos Silva',
    pis: '12345678901',
    recordType: 'entry',
    timestamp: '2024-01-15T08:02:34',
    nsr: '000001234',
    synchronized: true
  },
  {
    id: '2',
    repId: 'REP001',
    repName: 'Portaria Principal',
    employeeId: 'EMP002',
    employeeName: 'Ana Costa',
    pis: '12345678902',
    recordType: 'entry',
    timestamp: '2024-01-15T08:05:12',
    nsr: '000001235',
    synchronized: true
  },
  {
    id: '3',
    repId: 'REP003',
    repName: 'Refeitório',
    employeeId: 'EMP001',
    employeeName: 'Carlos Silva',
    pis: '12345678901',
    recordType: 'break_start',
    timestamp: '2024-01-15T12:00:45',
    nsr: '000005678',
    synchronized: false,
    syncError: 'Timeout de conexão'
  },
  {
    id: '4',
    repId: 'REP002',
    repName: 'Portaria Fundos',
    employeeId: 'EMP003',
    employeeName: 'Pedro Santos',
    pis: '12345678903',
    recordType: 'entry',
    timestamp: '2024-01-15T07:58:22',
    nsr: '000002345',
    synchronized: true
  },
  {
    id: '5',
    repId: 'REP001',
    repName: 'Portaria Principal',
    employeeId: 'EMP004',
    employeeName: 'Maria Oliveira',
    pis: '12345678904',
    recordType: 'exit',
    timestamp: '2024-01-15T17:05:33',
    nsr: '000001456',
    synchronized: true
  }
];

const mockSyncLogs: SyncLog[] = [
  {
    id: '1',
    repId: 'REP001',
    repName: 'Portaria Principal',
    type: 'automatic',
    status: 'success',
    recordsImported: 45,
    recordsFailed: 0,
    duration: 12,
    startedAt: '2024-01-15T08:30:00',
    completedAt: '2024-01-15T08:30:12'
  },
  {
    id: '2',
    repId: 'REP003',
    repName: 'Refeitório',
    type: 'automatic',
    status: 'partial',
    recordsImported: 38,
    recordsFailed: 3,
    duration: 18,
    startedAt: '2024-01-15T08:25:00',
    completedAt: '2024-01-15T08:25:18',
    errorMessage: '3 registros com erro de validação PIS'
  },
  {
    id: '3',
    repId: 'REP004',
    repName: 'Filial Campinas',
    type: 'scheduled',
    status: 'failed',
    recordsImported: 0,
    recordsFailed: 0,
    duration: 30,
    startedAt: '2024-01-15T06:00:00',
    completedAt: '2024-01-15T06:00:30',
    errorMessage: 'Conexão recusada - dispositivo offline'
  },
  {
    id: '4',
    repId: 'REP002',
    repName: 'Portaria Fundos',
    type: 'manual',
    status: 'success',
    recordsImported: 123,
    recordsFailed: 0,
    duration: 25,
    startedAt: '2024-01-15T07:00:00',
    completedAt: '2024-01-15T07:00:25'
  }
];

// Chart data
const recordsByHourData = [
  { hour: '06h', records: 45 },
  { hour: '07h', records: 234 },
  { hour: '08h', records: 456 },
  { hour: '09h', records: 123 },
  { hour: '10h', records: 67 },
  { hour: '11h', records: 45 },
  { hour: '12h', records: 289 },
  { hour: '13h', records: 312 },
  { hour: '14h', records: 78 },
  { hour: '17h', records: 367 },
  { hour: '18h', records: 234 },
  { hour: '19h', records: 56 }
];

const deviceStatusData = [
  { name: 'Online', value: 9, color: '#10b981' },
  { name: 'Offline', value: 1, color: '#ef4444' },
  { name: 'Sincronizando', value: 2, color: '#f59e0b' }
];

const recordsByDeviceData = [
  { name: 'Portaria Principal', records: 456 },
  { name: 'Portaria Fundos', records: 234 },
  { name: 'Refeitório', records: 512 },
  { name: 'Produção A', records: 189 },
  { name: 'Filial Campinas', records: 0 }
];

const syncTrendData = [
  { date: '08/01', success: 156, failed: 3 },
  { date: '09/01', success: 178, failed: 5 },
  { date: '10/01', success: 145, failed: 2 },
  { date: '11/01', success: 189, failed: 8 },
  { date: '12/01', success: 167, failed: 4 },
  { date: '13/01', success: 198, failed: 1 },
  { date: '14/01', success: 212, failed: 6 }
];

export function REPIntegrationPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDevice, setSelectedDevice] = useState<REPDevice | null>(null);
  const [showDeviceModal, setShowDeviceModal] = useState(false);
  const [showAddDeviceModal, setShowAddDeviceModal] = useState(false);
  const [showSyncModal, setShowSyncModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [devices, setDevices] = useState<REPDevice[]>(mockDevices);
  const [isSyncing, setIsSyncing] = useState(false);

  // Handler para sincronizar todos os dispositivos
  const handleSyncAll = async () => {
    setIsSyncing(true);
    // Marca todos os dispositivos online como "syncing"
    setDevices(prev => prev.map(d =>
      d.status === 'online' ? { ...d, status: 'syncing' as const } : d
    ));

    // Simula tempo de sincronização
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Atualiza para status final
    setDevices(prev => prev.map(d => ({
      ...d,
      status: d.status === 'syncing' ? 'online' as const : d.status,
      lastSync: d.status === 'syncing' ? new Date().toISOString() : d.lastSync,
    })));

    setIsSyncing(false);
  };

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <BarChart3 className="h-4 w-4" /> },
    { value: 'devices', label: 'Dispositivos', icon: <Server className="h-4 w-4" /> },
    { value: 'records', label: 'Registros', icon: <Clock className="h-4 w-4" /> },
    { value: 'sync', label: 'Sincronização', icon: <RefreshCw className="h-4 w-4" /> }
  ];

  const statusOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Status' },
    { value: 'online', label: 'Online' },
    { value: 'offline', label: 'Offline' },
    { value: 'syncing', label: 'Sincronizando' },
    { value: 'error', label: 'Com Erro' }
  ];

  const getStatusBadge = (status: REPDevice['status']) => {
    const statusConfig = {
      online: { label: 'Online', variant: 'success' as const, icon: <Wifi className="h-3 w-3" /> },
      offline: { label: 'Offline', variant: 'danger' as const, icon: <WifiOff className="h-3 w-3" /> },
      syncing: { label: 'Sincronizando', variant: 'warning' as const, icon: <RefreshCw className="h-3 w-3 animate-spin" /> },
      error: { label: 'Erro', variant: 'danger' as const, icon: <AlertTriangle className="h-3 w-3" /> }
    };
    const config = statusConfig[status];
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        {config.icon}
        {config.label}
      </Badge>
    );
  };

  const getSyncStatusBadge = (status: SyncLog['status']) => {
    const statusConfig = {
      success: { label: 'Sucesso', variant: 'success' as const },
      partial: { label: 'Parcial', variant: 'warning' as const },
      failed: { label: 'Falha', variant: 'danger' as const }
    };
    const config = statusConfig[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getRecordTypeLabel = (type: REPRecord['recordType']) => {
    const labels = {
      entry: 'Entrada',
      exit: 'Saída',
      break_start: 'Início Intervalo',
      break_end: 'Fim Intervalo'
    };
    return labels[type];
  };

  const getMemoryColor = (usage: number) => {
    if (usage < 50) return 'bg-green-500';
    if (usage < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const deviceColumns: Column<REPDevice>[] = [
    {
      key: 'device',
      header: 'Dispositivo',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-lg bg-bg-tertiary flex items-center justify-center">
            <Server className="h-6 w-6 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.code}</p>
          </div>
        </div>
      )
    },
    {
      key: 'model',
      header: 'Modelo',
      render: (row) => (
        <div>
          <p className="text-text-primary">{row.model}</p>
          <p className="text-sm text-text-secondary">{row.manufacturer}</p>
        </div>
      )
    },
    {
      key: 'network',
      header: 'Rede',
      render: (row) => (
        <div className="font-mono text-sm">
          <p className="text-text-primary">{row.ipAddress}</p>
          <p className="text-text-secondary">Porta: {row.port}</p>
        </div>
      )
    },
    {
      key: 'location',
      header: 'Localização',
      render: (row) => (
        <div className="flex items-center gap-2 max-w-xs">
          <MapPin className="h-4 w-4 text-text-secondary flex-shrink-0" />
          <span className="text-text-primary truncate">{row.location}</span>
        </div>
      )
    },
    {
      key: 'stats',
      header: 'Hoje',
      render: (row) => (
        <div>
          <p className="text-text-primary font-medium">{row.recordsToday} registros</p>
          <p className="text-sm text-text-secondary">{row.employeesRegistered} funcionários</p>
        </div>
      )
    },
    {
      key: 'memory',
      header: 'Memória',
      render: (row) => (
        <div className="w-24">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-text-secondary">{row.memoryUsage}%</span>
          </div>
          <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full ${getMemoryColor(row.memoryUsage)} rounded-full transition-all`}
              style={{ width: `${row.memoryUsage}%` }}
            />
          </div>
        </div>
      )
    },
    {
      key: 'lastSync',
      header: 'Última Sinc.',
      render: (row) => (
        <div>
          <p className="text-text-primary">{new Date(row.lastSync).toLocaleTimeString('pt-BR')}</p>
          <p className="text-sm text-text-secondary">{new Date(row.lastSync).toLocaleDateString('pt-BR')}</p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedDevice(row);
              setShowDeviceModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedDevice(row);
              setShowSyncModal(true);
            }}
            disabled={row.status === 'offline'}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="ghost">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const recordColumns: Column<REPRecord>[] = [
    {
      key: 'employee',
      header: 'Colaborador',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
            <User className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.employeeName}</p>
            <p className="text-sm text-text-secondary">PIS: {row.pis}</p>
          </div>
        </div>
      )
    },
    {
      key: 'rep',
      header: 'REP',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Server className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary">{row.repName}</span>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        <span className="text-text-primary">{getRecordTypeLabel(row.recordType)}</span>
      )
    },
    {
      key: 'timestamp',
      header: 'Data/Hora',
      render: (row) => (
        <div>
          <p className="text-text-primary">{new Date(row.timestamp).toLocaleTimeString('pt-BR')}</p>
          <p className="text-sm text-text-secondary">{new Date(row.timestamp).toLocaleDateString('pt-BR')}</p>
        </div>
      )
    },
    {
      key: 'nsr',
      header: 'NSR',
      render: (row) => (
        <span className="text-text-primary font-mono text-sm">{row.nsr}</span>
      )
    },
    {
      key: 'sync',
      header: 'Sincronizado',
      render: (row) => (
        <div className="flex items-center gap-2">
          {row.synchronized ? (
            <Badge variant="success" className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3" />
              Sim
            </Badge>
          ) : (
            <Badge variant="danger" className="flex items-center gap-1">
              <XCircle className="h-3 w-3" />
              Não
            </Badge>
          )}
        </div>
      )
    }
  ];

  const syncColumns: Column<SyncLog>[] = [
    {
      key: 'device',
      header: 'Dispositivo',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Server className="h-5 w-5 text-text-secondary" />
          <span className="text-text-primary">{row.repName}</span>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        <Badge variant={row.type === 'automatic' ? 'info' : row.type === 'manual' ? 'primary' : 'neutral'}>
          {row.type === 'automatic' ? 'Automática' : row.type === 'manual' ? 'Manual' : 'Agendada'}
        </Badge>
      )
    },
    {
      key: 'records',
      header: 'Registros',
      render: (row) => (
        <div>
          <p className="text-text-primary">
            <span className="text-green-400">{row.recordsImported}</span>
            {row.recordsFailed > 0 && (
              <span className="text-red-400 ml-2">/ {row.recordsFailed} erros</span>
            )}
          </p>
        </div>
      )
    },
    {
      key: 'duration',
      header: 'Duração',
      render: (row) => (
        <span className="text-text-primary">{row.duration}s</span>
      )
    },
    {
      key: 'time',
      header: 'Horário',
      render: (row) => (
        <div>
          <p className="text-text-primary">{new Date(row.startedAt).toLocaleTimeString('pt-BR')}</p>
          <p className="text-sm text-text-secondary">{new Date(row.startedAt).toLocaleDateString('pt-BR')}</p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getSyncStatusBadge(row.status)
    },
    {
      key: 'error',
      header: 'Detalhes',
      render: (row) => (
        <div className="max-w-xs">
          {row.errorMessage ? (
            <p className="text-sm text-red-400 truncate">{row.errorMessage}</p>
          ) : (
            <span className="text-text-secondary">-</span>
          )}
        </div>
      )
    }
  ];

  const filteredDevices = devices.filter(device => {
    const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      device.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      device.ipAddress.includes(searchTerm);
    const matchesStatus = statusFilter === 'all' || device.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const onlineCount = devices.filter(d => d.status === 'online').length;
  const offlineCount = devices.filter(d => d.status === 'offline').length;
  const syncingCount = devices.filter(d => d.status === 'syncing').length;
  const totalRecords = devices.reduce((sum, d) => sum + d.recordsToday, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Integração REP
            </h1>
            <p className="text-text-secondary mt-1">
              Relógios de ponto homologados
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={handleSyncAll} disabled={isSyncing}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isSyncing ? 'animate-spin' : ''}`} />
              {isSyncing ? 'Sincronizando...' : 'Sincronizar Todos'}
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar AFD
            </Button>
            <Button onClick={() => setShowAddDeviceModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo REP
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="REPs Online"
            value={onlineCount.toString()}
            icon={<Wifi className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Registros Hoje"
            value={totalRecords.toLocaleString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="primary"
            change={8.5}
            changeLabel="vs. ontem"
          />
          <StatCard
            title="Offline"
            value={offlineCount.toString()}
            icon={<WifiOff className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Sincronizando"
            value={syncingCount.toString()}
            icon={<RefreshCw className="h-5 w-5" />}
            iconColor="info"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Records by Hour */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Registros por Hora
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={recordsByHourData}>
                    <defs>
                      <linearGradient id="repRecordsGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="hour" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="records"
                      stroke="#6366f1"
                      fill="url(#repRecordsGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              {/* Device Status */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Status dos Dispositivos
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={deviceStatusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {deviceStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Records by Device & Sync Trend */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Records by Device */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Registros por Dispositivo
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={recordsByDeviceData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#64748b" fontSize={12} />
                    <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={12} width={120} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="records" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              {/* Sync Trend */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Tendência de Sincronização
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={syncTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="success"
                      name="Sucesso"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ fill: '#10b981' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="failed"
                      name="Falhas"
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={{ fill: '#ef4444' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Quick Status */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Status dos REPs
                </h3>
                <Button variant="outline" size="sm" onClick={() => setActiveTab('devices')}>
                  Ver Todos
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {devices.slice(0, 6).map((device) => (
                  <div
                    key={device.id}
                    className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`h-3 w-3 rounded-full ${
                        device.status === 'online' ? 'bg-green-500' :
                        device.status === 'offline' ? 'bg-red-500' :
                        device.status === 'syncing' ? 'bg-yellow-500 animate-pulse' :
                        'bg-red-500'
                      }`} />
                      <div>
                        <p className="font-medium text-text-primary">{device.name}</p>
                        <p className="text-sm text-text-secondary">{device.ipAddress}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-text-primary font-medium">{device.recordsToday}</p>
                      <p className="text-sm text-text-secondary">registros</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'devices' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar por nome, código ou IP..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Select
                options={statusOptions}
                value={statusFilter}
                onChange={(value) => setStatusFilter(value)}
              />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>

            <DataTable
              data={filteredDevices}
              columns={deviceColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'records' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar por colaborador ou PIS..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Button variant="outline">
                <Calendar className="h-4 w-4 mr-2" />
                Período
              </Button>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>

            <DataTable
              data={mockRecords}
              columns={recordColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'sync' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-text-primary">
                Histórico de Sincronização
              </h3>
              <div className="flex items-center gap-3">
                <Button variant="outline">
                  <Calendar className="h-4 w-4 mr-2" />
                  Período
                </Button>
                <Button>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Sincronizar Agora
                </Button>
              </div>
            </div>

            <DataTable
              data={mockSyncLogs}
              columns={syncColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}
      </div>

      {/* Device Detail Modal */}
      <Modal
        isOpen={showDeviceModal}
        onClose={() => setShowDeviceModal(false)}
        title="Detalhes do REP"
        size="lg"
      >
        {selectedDevice && (
          <div className="space-y-6">
            {/* Device Header */}
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="h-16 w-16 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                <Server className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedDevice.name}
                </h3>
                <p className="text-text-secondary">{selectedDevice.code}</p>
              </div>
              <div className="ml-auto">
                {getStatusBadge(selectedDevice.status)}
              </div>
            </div>

            {/* Device Info */}
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Modelo</p>
                  <p className="text-text-primary font-medium mt-1">{selectedDevice.model}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Fabricante</p>
                  <p className="text-text-primary mt-1">{selectedDevice.manufacturer}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Número de Série</p>
                  <p className="text-text-primary font-mono mt-1">{selectedDevice.serialNumber}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Firmware</p>
                  <p className="text-text-primary font-mono mt-1">v{selectedDevice.firmwareVersion}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Endereço IP</p>
                  <p className="text-text-primary font-mono mt-1">{selectedDevice.ipAddress}:{selectedDevice.port}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Localização</p>
                  <p className="text-text-primary mt-1">{selectedDevice.location}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Última Sincronização</p>
                  <p className="text-text-primary mt-1">
                    {new Date(selectedDevice.lastSync).toLocaleString('pt-BR')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Cadastrado em</p>
                  <p className="text-text-primary mt-1">
                    {new Date(selectedDevice.createdAt).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-accent-primary">{selectedDevice.recordsToday}</p>
                <p className="text-sm text-text-secondary">Registros Hoje</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-accent-secondary">{selectedDevice.employeesRegistered}</p>
                <p className="text-sm text-text-secondary">Funcionários</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-text-primary">{selectedDevice.memoryUsage}%</p>
                <p className="text-sm text-text-secondary">Memória</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Configurar
              </Button>
              <Button
                variant="outline"
                disabled={selectedDevice.status === 'offline'}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Sincronizar
              </Button>
              <Button variant="danger">
                <Trash2 className="h-4 w-4 mr-2" />
                Remover
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Add Device Modal */}
      <Modal
        isOpen={showAddDeviceModal}
        onClose={() => setShowAddDeviceModal(false)}
        title="Adicionar Novo REP"
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Código
              </label>
              <Input placeholder="REP-006" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nome
              </label>
              <Input placeholder="Portaria Norte" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Fabricante
              </label>
              <Select
                options={[
                  { value: 'control_id', label: 'Control iD' },
                  { value: 'henry', label: 'Henry' },
                  { value: 'topdata', label: 'Topdata' },
                  { value: 'dimep', label: 'Dimep' }
                ]}
                value="control_id"
                onChange={() => {}}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Modelo
              </label>
              <Select
                options={[
                  { value: 'idclass', label: 'REP iDClass' },
                  { value: 'orion', label: 'REP Henry Orion 6' },
                  { value: 'inner', label: 'REP Topdata Inner Rep Plus' },
                  { value: 'printpoint', label: 'REP Dimep Printpoint III' }
                ]}
                value="idclass"
                onChange={() => {}}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Número de Série
            </label>
            <Input placeholder="CID2024001234" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Endereço IP
              </label>
              <Input placeholder="192.168.1.100" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Porta
              </label>
              <Input type="number" placeholder="3000" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Localização
            </label>
            <Input placeholder="Matriz - Entrada Principal" />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={() => setShowAddDeviceModal(false)}>
              Cancelar
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar REP
            </Button>
          </div>
        </div>
      </Modal>

      {/* Sync Modal */}
      <Modal
        isOpen={showSyncModal}
        onClose={() => setShowSyncModal(false)}
        title="Sincronizar REP"
        size="md"
      >
        {selectedDevice && (
          <div className="space-y-6">
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <Server className="h-8 w-8 text-accent-primary" />
              <div>
                <p className="font-medium text-text-primary">{selectedDevice.name}</p>
                <p className="text-sm text-text-secondary">{selectedDevice.ipAddress}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <Database className="h-5 w-5 text-text-secondary" />
                  <span className="text-text-primary">Importar registros</span>
                </div>
                <input type="checkbox" defaultChecked className="rounded" />
              </div>
              <div className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-text-secondary" />
                  <span className="text-text-primary">Exportar funcionários</span>
                </div>
                <input type="checkbox" className="rounded" />
              </div>
              <div className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <HardDrive className="h-5 w-5 text-text-secondary" />
                  <span className="text-text-primary">Limpar memória após importação</span>
                </div>
                <input type="checkbox" className="rounded" />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
              <Button variant="outline" onClick={() => setShowSyncModal(false)}>
                Cancelar
              </Button>
              <Button>
                <RefreshCw className="h-4 w-4 mr-2" />
                Iniciar Sincronização
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}
