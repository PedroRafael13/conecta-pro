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
  Smartphone,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  MapPin,
  Clock,
  User,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Camera,
  Battery,
  Signal,
  Eye,
  Edit,
  Trash2,
  Calendar,
  Building2,
  LogIn,
  LogOut
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
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
interface MobileRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  deviceId: string;
  deviceModel: string;
  recordType: 'entry' | 'exit' | 'break_start' | 'break_end';
  timestamp: string;
  latitude: number;
  longitude: number;
  address: string;
  accuracy: number;
  photoUrl?: string;
  status: 'valid' | 'pending' | 'irregular' | 'rejected';
  irregularityType?: 'location' | 'time' | 'photo' | 'device';
  irregularityDescription?: string;
  postName?: string;
  clientName?: string;
}

interface RegisteredDevice {
  id: string;
  employeeId: string;
  employeeName: string;
  deviceModel: string;
  deviceOS: string;
  appVersion: string;
  lastSync: string;
  status: 'active' | 'inactive' | 'blocked';
  batteryLevel: number;
  signalStrength: number;
  registeredAt: string;
}

interface LocationZone {
  id: string;
  name: string;
  type: 'headquarters' | 'branch' | 'client' | 'field';
  latitude: number;
  longitude: number;
  radius: number;
  address: string;
  employeesCount: number;
  active: boolean;
}

// Mock data
const mockRecords: MobileRecord[] = [
  {
    id: '1',
    employeeId: 'EMP001',
    employeeName: 'Carlos Silva',
    deviceId: 'DEV001',
    deviceModel: 'Samsung Galaxy A54',
    recordType: 'entry',
    timestamp: '2024-01-15T08:02:34',
    latitude: -23.5505,
    longitude: -46.6333,
    address: 'Av. Paulista, 1000 - São Paulo, SP',
    accuracy: 5,
    photoUrl: '/photos/rec1.jpg',
    status: 'valid',
    postName: 'Recepção Principal',
    clientName: 'Edifício Empresarial'
  },
  {
    id: '2',
    employeeId: 'EMP002',
    employeeName: 'Ana Costa',
    deviceId: 'DEV002',
    deviceModel: 'iPhone 14',
    recordType: 'entry',
    timestamp: '2024-01-15T08:15:22',
    latitude: -23.5612,
    longitude: -46.6544,
    address: 'Rua Augusta, 500 - São Paulo, SP',
    accuracy: 150,
    status: 'irregular',
    irregularityType: 'location',
    irregularityDescription: 'Fora da área permitida (150m do ponto)',
    postName: 'Segurança Noturna',
    clientName: 'Shopping Center'
  },
  {
    id: '3',
    employeeId: 'EMP003',
    employeeName: 'Pedro Santos',
    deviceId: 'DEV003',
    deviceModel: 'Motorola G52',
    recordType: 'exit',
    timestamp: '2024-01-15T17:05:11',
    latitude: -23.5489,
    longitude: -46.6388,
    address: 'Rua da Consolação, 200 - São Paulo, SP',
    accuracy: 8,
    photoUrl: '/photos/rec3.jpg',
    status: 'valid',
    postName: 'Portaria Central',
    clientName: 'Condomínio Residencial'
  },
  {
    id: '4',
    employeeId: 'EMP004',
    employeeName: 'Maria Oliveira',
    deviceId: 'DEV004',
    deviceModel: 'Samsung Galaxy S23',
    recordType: 'entry',
    timestamp: '2024-01-15T07:58:45',
    latitude: -23.5599,
    longitude: -46.6511,
    address: 'Av. Brigadeiro Faria Lima, 1500 - São Paulo, SP',
    accuracy: 3,
    status: 'pending',
    postName: 'Vigilância',
    clientName: 'Centro Comercial'
  },
  {
    id: '5',
    employeeId: 'EMP005',
    employeeName: 'João Ferreira',
    deviceId: 'DEV005',
    deviceModel: 'Xiaomi Redmi Note 12',
    recordType: 'break_start',
    timestamp: '2024-01-15T12:00:33',
    latitude: -23.5520,
    longitude: -46.6340,
    address: 'Av. Paulista, 1000 - São Paulo, SP',
    accuracy: 6,
    status: 'valid',
    postName: 'Recepção Principal',
    clientName: 'Edifício Empresarial'
  }
];

const mockDevices: RegisteredDevice[] = [
  {
    id: 'DEV001',
    employeeId: 'EMP001',
    employeeName: 'Carlos Silva',
    deviceModel: 'Samsung Galaxy A54',
    deviceOS: 'Android 13',
    appVersion: '2.5.1',
    lastSync: '2024-01-15T08:02:34',
    status: 'active',
    batteryLevel: 85,
    signalStrength: 4,
    registeredAt: '2023-06-15'
  },
  {
    id: 'DEV002',
    employeeId: 'EMP002',
    employeeName: 'Ana Costa',
    deviceModel: 'iPhone 14',
    deviceOS: 'iOS 17.2',
    appVersion: '2.5.0',
    lastSync: '2024-01-15T08:15:22',
    status: 'active',
    batteryLevel: 62,
    signalStrength: 5,
    registeredAt: '2023-08-20'
  },
  {
    id: 'DEV003',
    employeeId: 'EMP003',
    employeeName: 'Pedro Santos',
    deviceModel: 'Motorola G52',
    deviceOS: 'Android 12',
    appVersion: '2.4.8',
    lastSync: '2024-01-14T17:30:00',
    status: 'inactive',
    batteryLevel: 15,
    signalStrength: 2,
    registeredAt: '2023-04-10'
  },
  {
    id: 'DEV004',
    employeeId: 'EMP004',
    employeeName: 'Maria Oliveira',
    deviceModel: 'Samsung Galaxy S23',
    deviceOS: 'Android 14',
    appVersion: '2.5.1',
    lastSync: '2024-01-15T07:58:45',
    status: 'active',
    batteryLevel: 92,
    signalStrength: 5,
    registeredAt: '2023-11-05'
  },
  {
    id: 'DEV005',
    employeeId: 'EMP005',
    employeeName: 'João Ferreira',
    deviceModel: 'Xiaomi Redmi Note 12',
    deviceOS: 'Android 13',
    appVersion: '2.5.1',
    lastSync: '2024-01-15T12:00:33',
    status: 'blocked',
    batteryLevel: 45,
    signalStrength: 3,
    registeredAt: '2023-09-22'
  }
];

const mockZones: LocationZone[] = [
  {
    id: 'ZONE001',
    name: 'Matriz - São Paulo',
    type: 'headquarters',
    latitude: -23.5505,
    longitude: -46.6333,
    radius: 100,
    address: 'Av. Paulista, 1000 - Bela Vista, São Paulo - SP',
    employeesCount: 45,
    active: true
  },
  {
    id: 'ZONE002',
    name: 'Filial Campinas',
    type: 'branch',
    latitude: -22.9064,
    longitude: -47.0616,
    radius: 80,
    address: 'Rua Barão de Jaguara, 500 - Centro, Campinas - SP',
    employeesCount: 23,
    active: true
  },
  {
    id: 'ZONE003',
    name: 'Cliente - Shopping Center',
    type: 'client',
    latitude: -23.5612,
    longitude: -46.6544,
    radius: 50,
    address: 'Rua Augusta, 500 - Consolação, São Paulo - SP',
    employeesCount: 12,
    active: true
  }
];

// Chart data
const recordsByHourData = [
  { hour: '06h', records: 45 },
  { hour: '07h', records: 156 },
  { hour: '08h', records: 234 },
  { hour: '09h', records: 89 },
  { hour: '10h', records: 45 },
  { hour: '11h', records: 23 },
  { hour: '12h', records: 178 },
  { hour: '13h', records: 167 },
  { hour: '14h', records: 34 },
  { hour: '17h', records: 198 },
  { hour: '18h', records: 245 },
  { hour: '19h', records: 67 }
];

const recordsByTypeData = [
  { name: 'Entradas', value: 456, color: '#10b981' },
  { name: 'Saídas', value: 423, color: '#6366f1' },
  { name: 'Início Intervalo', value: 389, color: '#f59e0b' },
  { name: 'Fim Intervalo', value: 385, color: '#8b5cf6' }
];

const irregularityTrendData = [
  { date: '01/01', total: 1234, irregular: 23 },
  { date: '02/01', total: 1256, irregular: 18 },
  { date: '03/01', total: 1189, irregular: 31 },
  { date: '04/01', total: 1245, irregular: 15 },
  { date: '05/01', total: 1278, irregular: 12 },
  { date: '06/01', total: 1312, irregular: 8 },
  { date: '07/01', total: 1289, irregular: 11 }
];

const deviceStatusData = [
  { name: 'Ativos', value: 89, color: '#10b981' },
  { name: 'Inativos', value: 12, color: '#64748b' },
  { name: 'Bloqueados', value: 5, color: '#ef4444' }
];

export function MobileTimeClockPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRecord, setSelectedRecord] = useState<MobileRecord | null>(null);
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [showDeviceModal, setShowDeviceModal] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<RegisteredDevice | null>(null);
  const [showZoneModal, setShowZoneModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [newZoneType, setNewZoneType] = useState('client');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Smartphone className="h-4 w-4" /> },
    { value: 'records', label: 'Registros', icon: <Clock className="h-4 w-4" /> },
    { value: 'devices', label: 'Dispositivos', icon: <Smartphone className="h-4 w-4" /> },
    { value: 'zones', label: 'Zonas', icon: <MapPin className="h-4 w-4" /> }
  ];

  const statusOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Status' },
    { value: 'valid', label: 'Válidos' },
    { value: 'pending', label: 'Pendentes' },
    { value: 'irregular', label: 'Irregulares' },
    { value: 'rejected', label: 'Rejeitados' }
  ];

  const typeOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Tipos' },
    { value: 'entry', label: 'Entrada' },
    { value: 'exit', label: 'Saída' },
    { value: 'break_start', label: 'Início Intervalo' },
    { value: 'break_end', label: 'Fim Intervalo' }
  ];

  const getStatusBadge = (status: MobileRecord['status']) => {
    const statusConfig = {
      valid: { label: 'Válido', variant: 'success' as const },
      pending: { label: 'Pendente', variant: 'warning' as const },
      irregular: { label: 'Irregular', variant: 'danger' as const },
      rejected: { label: 'Rejeitado', variant: 'neutral' as const }
    };
    const config = statusConfig[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getRecordTypeLabel = (type: MobileRecord['recordType']) => {
    const labels = {
      entry: 'Entrada',
      exit: 'Saída',
      break_start: 'Início Intervalo',
      break_end: 'Fim Intervalo'
    };
    return labels[type];
  };

  const getRecordTypeIcon = (type: MobileRecord['recordType']) => {
    const icons = {
      entry: <LogIn className="h-4 w-4 text-green-400" />,
      exit: <LogOut className="h-4 w-4 text-red-400" />,
      break_start: <Clock className="h-4 w-4 text-yellow-400" />,
      break_end: <Clock className="h-4 w-4 text-blue-400" />
    };
    return icons[type];
  };

  const getDeviceStatusBadge = (status: RegisteredDevice['status']) => {
    const statusConfig = {
      active: { label: 'Ativo', variant: 'success' as const },
      inactive: { label: 'Inativo', variant: 'neutral' as const },
      blocked: { label: 'Bloqueado', variant: 'danger' as const }
    };
    const config = statusConfig[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getZoneTypeBadge = (type: LocationZone['type']) => {
    const typeConfig = {
      headquarters: { label: 'Matriz', variant: 'primary' as const },
      branch: { label: 'Filial', variant: 'info' as const },
      client: { label: 'Cliente', variant: 'success' as const },
      field: { label: 'Campo', variant: 'warning' as const }
    };
    const config = typeConfig[type];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getBatteryIcon = (level: number) => {
    if (level > 50) return <Battery className="h-4 w-4 text-green-400" />;
    if (level > 20) return <Battery className="h-4 w-4 text-yellow-400" />;
    return <Battery className="h-4 w-4 text-red-400" />;
  };

  const getSignalIcon = (strength: number) => {
    if (strength >= 4) return <Signal className="h-4 w-4 text-green-400" />;
    if (strength >= 2) return <Signal className="h-4 w-4 text-yellow-400" />;
    return <Signal className="h-4 w-4 text-red-400" />;
  };

  const recordColumns: Column<MobileRecord>[] = [
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
            <p className="text-sm text-text-secondary">{row.employeeId}</p>
          </div>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        <div className="flex items-center gap-2">
          {getRecordTypeIcon(row.recordType)}
          <span className="text-text-primary">{getRecordTypeLabel(row.recordType)}</span>
        </div>
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
      key: 'location',
      header: 'Local',
      render: (row) => (
        <div className="max-w-xs">
          <p className="text-text-primary truncate">{row.postName || '-'}</p>
          <p className="text-sm text-text-secondary truncate">{row.clientName || '-'}</p>
        </div>
      )
    },
    {
      key: 'accuracy',
      header: 'Precisão',
      render: (row) => (
        <div className="flex items-center gap-2">
          <MapPin className={`h-4 w-4 ${row.accuracy <= 10 ? 'text-green-400' : row.accuracy <= 50 ? 'text-yellow-400' : 'text-red-400'}`} />
          <span className="text-text-primary">{row.accuracy}m</span>
        </div>
      )
    },
    {
      key: 'device',
      header: 'Dispositivo',
      render: (row) => (
        <div>
          <p className="text-text-primary text-sm">{row.deviceModel}</p>
          <p className="text-xs text-text-secondary font-mono">{row.deviceId}</p>
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
              setSelectedRecord(row);
              setShowRecordModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'pending' && (
            <>
              <Button variant="ghost" className="text-green-400 hover:text-green-300">
                <CheckCircle className="h-4 w-4" />
              </Button>
              <Button variant="ghost" className="text-red-400 hover:text-red-300">
                <XCircle className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      )
    }
  ];

  const deviceColumns: Column<RegisteredDevice>[] = [
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
            <p className="text-sm text-text-secondary">{row.employeeId}</p>
          </div>
        </div>
      )
    },
    {
      key: 'device',
      header: 'Dispositivo',
      render: (row) => (
        <div>
          <p className="text-text-primary">{row.deviceModel}</p>
          <p className="text-sm text-text-secondary">{row.deviceOS}</p>
        </div>
      )
    },
    {
      key: 'app',
      header: 'App',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Smartphone className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary font-mono text-sm">v{row.appVersion}</span>
        </div>
      )
    },
    {
      key: 'battery',
      header: 'Bateria',
      render: (row) => (
        <div className="flex items-center gap-2">
          {getBatteryIcon(row.batteryLevel)}
          <span className="text-text-primary">{row.batteryLevel}%</span>
        </div>
      )
    },
    {
      key: 'signal',
      header: 'Sinal',
      render: (row) => (
        <div className="flex items-center gap-2">
          {getSignalIcon(row.signalStrength)}
          <span className="text-text-primary">{row.signalStrength}/5</span>
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
      render: (row) => getDeviceStatusBadge(row.status)
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
          <Button variant="ghost" className="text-red-400 hover:text-red-300">
            <XCircle className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const zoneColumns: Column<LocationZone>[] = [
    {
      key: 'name',
      header: 'Local',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-bg-tertiary flex items-center justify-center">
            {row.type === 'headquarters' ? (
              <Building2 className="h-5 w-5 text-accent-primary" />
            ) : (
              <MapPin className="h-5 w-5 text-accent-secondary" />
            )}
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary truncate max-w-xs">{row.address}</p>
          </div>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => getZoneTypeBadge(row.type)
    },
    {
      key: 'radius',
      header: 'Raio',
      render: (row) => (
        <span className="text-text-primary">{row.radius}m</span>
      )
    },
    {
      key: 'employees',
      header: 'Colaboradores',
      render: (row) => (
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary">{row.employeesCount}</span>
        </div>
      )
    },
    {
      key: 'coordinates',
      header: 'Coordenadas',
      render: (row) => (
        <span className="text-text-secondary font-mono text-sm">
          {row.latitude.toFixed(4)}, {row.longitude.toFixed(4)}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={row.active ? 'success' : 'neutral'}>
          {row.active ? 'Ativa' : 'Inativa'}
        </Badge>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost">
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" className="text-red-400 hover:text-red-300">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const filteredRecords = mockRecords.filter(record => {
    const matchesSearch = record.employeeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.employeeId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || record.status === statusFilter;
    const matchesType = typeFilter === 'all' || record.recordType === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Ponto Mobile
            </h1>
            <p className="text-text-secondary mt-1">
              Registros de ponto via aplicativo móvel
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Sincronizar
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nova Zona
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Registros Hoje"
            value="1,234"
            icon={<Clock className="h-5 w-5" />}
            iconColor="primary"
            change={12.5}
            changeLabel="vs. ontem"
          />
          <StatCard
            title="Colaboradores Ativos"
            value="456"
            icon={<User className="h-5 w-5" />}
            iconColor="info"
            change={5}
            changeLabel="vs. ontem"
          />
          <StatCard
            title="Dispositivos"
            value="89"
            icon={<Smartphone className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Irregulares"
            value="5"
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="warning"
            change={-25}
            changeLabel="vs. ontem"
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
                      <linearGradient id="recordsGradient" x1="0" y1="0" x2="0" y2="1">
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
                      fill="url(#recordsGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              {/* Records by Type */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Distribuição por Tipo
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={recordsByTypeData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {recordsByTypeData.map((entry, index) => (
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

            {/* Irregularity Trend & Device Status */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Irregularity Trend */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Tendência de Irregularidades
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={irregularityTrendData}>
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
                      dataKey="total"
                      name="Total"
                      stroke="#6366f1"
                      strokeWidth={2}
                      dot={{ fill: '#6366f1' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="irregular"
                      name="Irregulares"
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={{ fill: '#ef4444' }}
                    />
                  </LineChart>
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

            {/* Recent Irregularities */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Irregularidades Recentes
                </h3>
                <Button variant="outline" size="sm">
                  Ver Todas
                </Button>
              </div>
              <div className="space-y-3">
                {mockRecords.filter(r => r.status === 'irregular').slice(0, 5).map((record) => (
                  <div
                    key={record.id}
                    className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-full bg-red-500/20 flex items-center justify-center">
                        <AlertTriangle className="h-5 w-5 text-red-400" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{record.employeeName}</p>
                        <p className="text-sm text-text-secondary">{record.irregularityDescription}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-text-primary">
                        {new Date(record.timestamp).toLocaleTimeString('pt-BR')}
                      </p>
                      <p className="text-sm text-text-secondary">
                        {new Date(record.timestamp).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'records' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar por colaborador..."
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
              <Select
                options={typeOptions}
                value={typeFilter}
                onChange={(value) => setTypeFilter(value)}
              />
              <Button variant="outline">
                <Calendar className="h-4 w-4 mr-2" />
                Período
              </Button>
            </div>

            <DataTable
              data={filteredRecords}
              columns={recordColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'devices' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar dispositivo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>

            <DataTable
              data={mockDevices}
              columns={deviceColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'zones' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar zona..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
              <Button onClick={() => setShowZoneModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Zona
              </Button>
            </div>

            <DataTable
              data={mockZones}
              columns={zoneColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}
      </div>

      {/* Record Detail Modal */}
      <Modal
        isOpen={showRecordModal}
        onClose={() => setShowRecordModal(false)}
        title="Detalhes do Registro"
        size="lg"
      >
        {selectedRecord && (
          <div className="space-y-6">
            {/* Employee Info */}
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="h-16 w-16 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                <User className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedRecord.employeeName}
                </h3>
                <p className="text-text-secondary">{selectedRecord.employeeId}</p>
              </div>
              <div className="ml-auto">
                {getStatusBadge(selectedRecord.status)}
              </div>
            </div>

            {/* Record Details */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Tipo de Registro</p>
                  <div className="flex items-center gap-2 mt-1">
                    {getRecordTypeIcon(selectedRecord.recordType)}
                    <span className="text-text-primary font-medium">
                      {getRecordTypeLabel(selectedRecord.recordType)}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Data/Hora</p>
                  <p className="text-text-primary font-medium mt-1">
                    {new Date(selectedRecord.timestamp).toLocaleString('pt-BR')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Dispositivo</p>
                  <p className="text-text-primary mt-1">{selectedRecord.deviceModel}</p>
                  <p className="text-sm text-text-secondary font-mono">{selectedRecord.deviceId}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Local</p>
                  <p className="text-text-primary font-medium mt-1">
                    {selectedRecord.postName || '-'}
                  </p>
                  <p className="text-sm text-text-secondary">{selectedRecord.clientName || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Endereço</p>
                  <p className="text-text-primary mt-1">{selectedRecord.address}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Precisão GPS</p>
                  <div className="flex items-center gap-2 mt-1">
                    <MapPin className={`h-4 w-4 ${selectedRecord.accuracy <= 10 ? 'text-green-400' : selectedRecord.accuracy <= 50 ? 'text-yellow-400' : 'text-red-400'}`} />
                    <span className="text-text-primary">{selectedRecord.accuracy} metros</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Irregularity Info */}
            {selectedRecord.status === 'irregular' && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-5 w-5 text-red-400" />
                  <span className="text-red-400 font-medium">Irregularidade Detectada</span>
                </div>
                <p className="text-text-secondary">{selectedRecord.irregularityDescription}</p>
              </div>
            )}

            {/* Photo placeholder */}
            {selectedRecord.photoUrl && (
              <div>
                <p className="text-sm text-text-secondary mb-2">Foto do Registro</p>
                <div className="h-48 bg-bg-tertiary rounded-lg flex items-center justify-center">
                  <Camera className="h-8 w-8 text-text-secondary" />
                </div>
              </div>
            )}

            {/* Actions */}
            {selectedRecord.status === 'pending' && (
              <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
                <Button variant="outline" className="text-red-400 border-red-400 hover:bg-red-400/10">
                  <XCircle className="h-4 w-4 mr-2" />
                  Rejeitar
                </Button>
                <Button>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Aprovar
                </Button>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Device Detail Modal */}
      <Modal
        isOpen={showDeviceModal}
        onClose={() => setShowDeviceModal(false)}
        title="Detalhes do Dispositivo"
        size="md"
      >
        {selectedDevice && (
          <div className="space-y-6">
            {/* Device Info */}
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="h-16 w-16 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                <Smartphone className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedDevice.deviceModel}
                </h3>
                <p className="text-text-secondary">{selectedDevice.deviceOS}</p>
              </div>
              <div className="ml-auto">
                {getDeviceStatusBadge(selectedDevice.status)}
              </div>
            </div>

            {/* Details */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Colaborador</p>
                  <p className="text-text-primary font-medium mt-1">{selectedDevice.employeeName}</p>
                  <p className="text-sm text-text-secondary">{selectedDevice.employeeId}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Versão do App</p>
                  <p className="text-text-primary font-mono mt-1">v{selectedDevice.appVersion}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Registrado em</p>
                  <p className="text-text-primary mt-1">
                    {new Date(selectedDevice.registeredAt).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Bateria</p>
                  <div className="flex items-center gap-2 mt-1">
                    {getBatteryIcon(selectedDevice.batteryLevel)}
                    <span className="text-text-primary">{selectedDevice.batteryLevel}%</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Sinal</p>
                  <div className="flex items-center gap-2 mt-1">
                    {getSignalIcon(selectedDevice.signalStrength)}
                    <span className="text-text-primary">{selectedDevice.signalStrength}/5</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Última Sincronização</p>
                  <p className="text-text-primary mt-1">
                    {new Date(selectedDevice.lastSync).toLocaleString('pt-BR')}
                  </p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
              {selectedDevice.status === 'active' && (
                <Button variant="outline" className="text-red-400 border-red-400 hover:bg-red-400/10">
                  Bloquear Dispositivo
                </Button>
              )}
              {selectedDevice.status === 'blocked' && (
                <Button variant="outline">
                  Desbloquear Dispositivo
                </Button>
              )}
              <Button variant="danger">
                Remover Dispositivo
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Zone Modal */}
      <Modal
        isOpen={showZoneModal}
        onClose={() => setShowZoneModal(false)}
        title="Nova Zona de Registro"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Nome da Zona
            </label>
            <Input placeholder="Ex: Matriz São Paulo" />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Tipo
            </label>
            <Select
              options={[
                { value: 'headquarters', label: 'Matriz' },
                { value: 'branch', label: 'Filial' },
                { value: 'client', label: 'Cliente' },
                { value: 'field', label: 'Campo' }
              ]}
              value={newZoneType}
              onChange={(value) => setNewZoneType(value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Endereço
            </label>
            <Input placeholder="Ex: Av. Paulista, 1000 - São Paulo, SP" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Latitude
              </label>
              <Input placeholder="-23.5505" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Longitude
              </label>
              <Input placeholder="-46.6333" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Raio (metros)
            </label>
            <Input type="number" placeholder="100" />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={() => setShowZoneModal(false)}>
              Cancelar
            </Button>
            <Button>
              Criar Zona
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}
