'use client';

import { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  DataTable,
  type Column,
  StatCard,
  StatGrid,
  Badge,
  Modal,
  Input,
  Select,
  Textarea,
  SimpleTabBar
} from '@/design-system/components';
import { motion } from 'framer-motion';
import {
  Smartphone,
  Settings,
  Download,
  Upload,
  Wifi,
  MapPin,
  Bell,
  Shield,
  Camera,
  Database,
  RefreshCw,
  Check,
  AlertTriangle,
  Lock,
  Unlock,
  Zap,
  Save
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
  Legend
} from 'recharts';

// Types
interface MobileDevice {
  id: string;
  deviceId: string;
  deviceName: string;
  platform: 'android' | 'ios';
  osVersion: string;
  appVersion: string;
  userId: string;
  userName: string;
  lastSync: string;
  status: 'online' | 'offline' | 'syncing';
  batteryLevel: number;
  storageUsed: number;
  gpsEnabled: boolean;
  pushEnabled: boolean;
  registeredAt: string;
}

interface MobileConfig {
  id: string;
  name: string;
  description: string;
  category: 'sync' | 'security' | 'ui' | 'features' | 'notifications';
  value: string | number | boolean;
  valueType: 'string' | 'number' | 'boolean' | 'json';
  isActive: boolean;
  updatedAt: string;
}

interface AppVersion {
  id: string;
  version: string;
  platform: 'android' | 'ios' | 'both';
  releaseDate: string;
  isRequired: boolean;
  changelog: string;
  downloadUrl: string;
  activeUsers: number;
}

// Mock data
const mockDevices: MobileDevice[] = [
  {
    id: '1',
    deviceId: 'A1B2C3D4E5',
    deviceName: 'Samsung Galaxy S23',
    platform: 'android',
    osVersion: '14.0',
    appVersion: '2.5.0',
    userId: 'user1',
    userName: 'João Silva',
    lastSync: '2024-01-15T10:30:00',
    status: 'online',
    batteryLevel: 85,
    storageUsed: 45,
    gpsEnabled: true,
    pushEnabled: true,
    registeredAt: '2024-01-01T08:00:00'
  },
  {
    id: '2',
    deviceId: 'F6G7H8I9J0',
    deviceName: 'iPhone 15 Pro',
    platform: 'ios',
    osVersion: '17.2',
    appVersion: '2.5.0',
    userId: 'user2',
    userName: 'Maria Santos',
    lastSync: '2024-01-15T09:45:00',
    status: 'syncing',
    batteryLevel: 62,
    storageUsed: 38,
    gpsEnabled: true,
    pushEnabled: true,
    registeredAt: '2024-01-02T14:30:00'
  },
  {
    id: '3',
    deviceId: 'K1L2M3N4O5',
    deviceName: 'Motorola Edge 40',
    platform: 'android',
    osVersion: '13.0',
    appVersion: '2.4.1',
    userId: 'user3',
    userName: 'Pedro Oliveira',
    lastSync: '2024-01-14T18:00:00',
    status: 'offline',
    batteryLevel: 23,
    storageUsed: 72,
    gpsEnabled: false,
    pushEnabled: true,
    registeredAt: '2023-12-15T10:00:00'
  },
  {
    id: '4',
    deviceId: 'P6Q7R8S9T0',
    deviceName: 'Xiaomi 13',
    platform: 'android',
    osVersion: '14.0',
    appVersion: '2.5.0',
    userId: 'user4',
    userName: 'Ana Costa',
    lastSync: '2024-01-15T11:00:00',
    status: 'online',
    batteryLevel: 91,
    storageUsed: 28,
    gpsEnabled: true,
    pushEnabled: false,
    registeredAt: '2024-01-05T09:15:00'
  }
];

const mockConfigs: MobileConfig[] = [
  {
    id: '1',
    name: 'sync_interval',
    description: 'Intervalo de sincronização automática (minutos)',
    category: 'sync',
    value: 15,
    valueType: 'number',
    isActive: true,
    updatedAt: '2024-01-10T08:00:00'
  },
  {
    id: '2',
    name: 'offline_mode',
    description: 'Permitir modo offline',
    category: 'features',
    value: true,
    valueType: 'boolean',
    isActive: true,
    updatedAt: '2024-01-08T14:30:00'
  },
  {
    id: '3',
    name: 'max_photo_size',
    description: 'Tamanho máximo de fotos (MB)',
    category: 'features',
    value: 5,
    valueType: 'number',
    isActive: true,
    updatedAt: '2024-01-05T10:00:00'
  },
  {
    id: '4',
    name: 'require_gps',
    description: 'Exigir GPS para registros',
    category: 'security',
    value: true,
    valueType: 'boolean',
    isActive: true,
    updatedAt: '2024-01-12T16:45:00'
  },
  {
    id: '5',
    name: 'biometric_auth',
    description: 'Autenticação biométrica obrigatória',
    category: 'security',
    value: false,
    valueType: 'boolean',
    isActive: true,
    updatedAt: '2024-01-11T09:30:00'
  },
  {
    id: '6',
    name: 'theme_mode',
    description: 'Modo de tema padrão',
    category: 'ui',
    value: 'auto',
    valueType: 'string',
    isActive: true,
    updatedAt: '2024-01-09T11:00:00'
  },
  {
    id: '7',
    name: 'push_enabled',
    description: 'Notificações push habilitadas',
    category: 'notifications',
    value: true,
    valueType: 'boolean',
    isActive: true,
    updatedAt: '2024-01-07T13:15:00'
  }
];

const mockVersions: AppVersion[] = [
  {
    id: '1',
    version: '2.5.0',
    platform: 'both',
    releaseDate: '2024-01-10',
    isRequired: false,
    changelog: 'Nova interface de registro de ponto, melhorias de performance, correções de bugs',
    downloadUrl: 'https://app.conectaplus.com.br/download/2.5.0',
    activeUsers: 145
  },
  {
    id: '2',
    version: '2.4.1',
    platform: 'both',
    releaseDate: '2023-12-20',
    isRequired: false,
    changelog: 'Correções de segurança, ajustes na sincronização offline',
    downloadUrl: 'https://app.conectaplus.com.br/download/2.4.1',
    activeUsers: 32
  },
  {
    id: '3',
    version: '2.4.0',
    platform: 'both',
    releaseDate: '2023-12-05',
    isRequired: false,
    changelog: 'Módulo de ocorrências, câmera melhorada, suporte a múltiplos condomínios',
    downloadUrl: 'https://app.conectaplus.com.br/download/2.4.0',
    activeUsers: 8
  }
];

const platformData = [
  { name: 'Android', value: 65, color: '#3DDC84' },
  { name: 'iOS', value: 35, color: '#000000' }
];

const versionDistribution = [
  { version: '2.5.0', count: 145 },
  { version: '2.4.1', count: 32 },
  { version: '2.4.0', count: 8 },
  { version: '< 2.4.0', count: 3 }
];

const tabs = [
  { id: 'devices', label: 'Dispositivos', icon: Smartphone },
  { id: 'configs', label: 'Configurações', icon: Settings },
  { id: 'versions', label: 'Versões', icon: Download }
];

export function MobileConfigPage() {
  const [activeTab, setActiveTab] = useState('devices');
  const [devices] = useState<MobileDevice[]>(mockDevices);
  const [configs, setConfigs] = useState<MobileConfig[]>(mockConfigs);
  const [versions] = useState<AppVersion[]>(mockVersions);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<MobileConfig | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<AppVersion | null>(null);

  // Stats
  const totalDevices = devices.length;
  const onlineDevices = devices.filter(d => d.status === 'online').length;
  const androidDevices = devices.filter(d => d.platform === 'android').length;
  const iosDevices = devices.filter(d => d.platform === 'ios').length;

  const getStatusBadge = (status: string) => {
    const colors: Record<string, 'success' | 'danger' | 'warning'> = {
      online: 'success',
      offline: 'danger',
      syncing: 'warning'
    };
    const labels: Record<string, string> = {
      online: 'Online',
      offline: 'Offline',
      syncing: 'Sincronizando'
    };
    return <Badge variant={colors[status]}>{labels[status]}</Badge>;
  };

  const getPlatformIcon = (platform: string) => {
    return platform === 'android' ? (
      <span className="text-green-500 font-bold">Android</span>
    ) : (
      <span className="text-gray-800 font-bold">iOS</span>
    );
  };

  const getCategoryBadge = (category: string) => {
    const colors: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
      sync: 'primary',
      security: 'danger',
      ui: 'info',
      features: 'success',
      notifications: 'warning'
    };
    const labels: Record<string, string> = {
      sync: 'Sincronização',
      security: 'Segurança',
      ui: 'Interface',
      features: 'Recursos',
      notifications: 'Notificações'
    };
    return <Badge variant={colors[category]}>{labels[category]}</Badge>;
  };

  const deviceColumns: Column<MobileDevice>[] = [
    {
      key: 'deviceName',
      header: 'Dispositivo',
      render: (device) => (
        <div>
          <p className="font-medium">{device.deviceName}</p>
          <p className="text-sm text-gray-500">{device.deviceId}</p>
        </div>
      )
    },
    {
      key: 'platform',
      header: 'Plataforma',
      render: (device) => (
        <div>
          {getPlatformIcon(device.platform)}
          <p className="text-sm text-gray-500">v{device.osVersion}</p>
        </div>
      )
    },
    {
      key: 'userName',
      header: 'Usuário',
      render: (device) => device.userName
    },
    {
      key: 'appVersion',
      header: 'App',
      render: (device) => <Badge variant="info">v{device.appVersion}</Badge>
    },
    {
      key: 'status',
      header: 'Status',
      render: (device) => getStatusBadge(device.status)
    },
    {
      key: 'batteryLevel',
      header: 'Bateria',
      render: (device) => (
        <div className="flex items-center gap-2">
          <div className="w-16 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                device.batteryLevel > 50 ? 'bg-green-500' :
                device.batteryLevel > 20 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${device.batteryLevel}%` }}
            />
          </div>
          <span className="text-sm">{device.batteryLevel}%</span>
        </div>
      )
    },
    {
      key: 'gpsEnabled',
      header: 'GPS',
      render: (device) => (
        device.gpsEnabled ? (
          <MapPin className="text-green-500" />
        ) : (
          <MapPin className="text-gray-300" />
        )
      )
    },
    {
      key: 'lastSync',
      header: 'Última Sync',
      render: (device) => new Date(device.lastSync).toLocaleString('pt-BR')
    }
  ];

  const configColumns: Column<MobileConfig>[] = [
    {
      key: 'name',
      header: 'Configuração',
      render: (config) => (
        <div>
          <p className="font-medium font-mono">{config.name}</p>
          <p className="text-sm text-gray-500">{config.description}</p>
        </div>
      )
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (config) => getCategoryBadge(config.category)
    },
    {
      key: 'value',
      header: 'Valor',
      render: (config) => {
        if (config.valueType === 'boolean') {
          return config.value ? (
            <Badge variant="success">Ativado</Badge>
          ) : (
            <Badge variant="danger">Desativado</Badge>
          );
        }
        return <span className="font-mono">{String(config.value)}</span>;
      }
    },
    {
      key: 'isActive',
      header: 'Status',
      render: (config) => (
        config.isActive ? (
          <Check className="text-green-500" />
        ) : (
          <AlertTriangle className="text-yellow-500" />
        )
      )
    },
    {
      key: 'updatedAt',
      header: 'Atualizado',
      render: (config) => new Date(config.updatedAt).toLocaleDateString('pt-BR')
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (config) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setSelectedConfig(config);
            setShowConfigModal(true);
          }}
        >
          <Settings className="w-4 h-4" />
        </Button>
      )
    }
  ];

  const versionColumns: Column<AppVersion>[] = [
    {
      key: 'version',
      header: 'Versão',
      render: (version) => (
        <div className="flex items-center gap-2">
          <span className="font-mono font-medium">v{version.version}</span>
          {version.isRequired && <Badge variant="danger">Obrigatória</Badge>}
        </div>
      )
    },
    {
      key: 'platform',
      header: 'Plataforma',
      render: (version) => {
        if (version.platform === 'both') {
          return <Badge variant="info">Android & iOS</Badge>;
        }
        return getPlatformIcon(version.platform);
      }
    },
    {
      key: 'releaseDate',
      header: 'Lançamento',
      render: (version) => new Date(version.releaseDate).toLocaleDateString('pt-BR')
    },
    {
      key: 'activeUsers',
      header: 'Usuários Ativos',
      render: (version) => (
        <span className="font-medium">{version.activeUsers}</span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (version) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setSelectedVersion(version);
            setShowVersionModal(true);
          }}
        >
          Ver Detalhes
        </Button>
      )
    }
  ];

  const handleSaveConfig = () => {
    if (!selectedConfig) return;
    setConfigs(prev => prev.map(c =>
      c.id === selectedConfig.id ? { ...selectedConfig, updatedAt: new Date().toISOString() } : c
    ));
    setShowConfigModal(false);
    setSelectedConfig(null);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Configuração Mobile</h1>
            <p className="text-gray-600">Gerencie dispositivos móveis e configurações do app</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Upload className="w-4 h-4 mr-2" />
              Push Config
            </Button>
            <Button variant="primary">
              <Download className="w-4 h-4 mr-2" />
              Nova Versão
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <StatCard
            title="Total Dispositivos"
            value={totalDevices}
            icon={<Smartphone className="w-6 h-6" />}
            color="primary"
          />
          <StatCard
            title="Dispositivos Online"
            value={onlineDevices}
            icon={<Wifi className="w-6 h-6" />}
            color="success"
            trend={{ value: 95, isPositive: true }}
          />
          <StatCard
            title="Android"
            value={androidDevices}
            icon={<Smartphone className="w-6 h-6" />}
            color="success"
          />
          <StatCard
            title="iOS"
            value={iosDevices}
            icon={<Smartphone className="w-6 h-6" />}
            color="info"
          />
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Distribuição por Plataforma</h3>
            </CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={platformData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {platformData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Distribuição por Versão</h3>
            </CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={versionDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="version" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#6366f1" name="Dispositivos" />
                </BarChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'devices' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Dispositivos Registrados</h3>
                  <Button variant="outline" size="sm">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Atualizar
                  </Button>
                </div>
              </CardHeader>
              <CardBody>
                <DataTable columns={deviceColumns} data={devices} />
              </CardBody>
            </Card>
          )}

          {activeTab === 'configs' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Configurações do Aplicativo</h3>
                  <Button variant="primary" size="sm">
                    <Settings className="w-4 h-4 mr-2" />
                    Nova Config
                  </Button>
                </div>
              </CardHeader>
              <CardBody>
                <DataTable columns={configColumns} data={configs} />
              </CardBody>
            </Card>
          )}

          {activeTab === 'versions' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Versões do Aplicativo</h3>
                  <Button variant="primary" size="sm">
                    <Upload className="w-4 h-4 mr-2" />
                    Publicar Versão
                  </Button>
                </div>
              </CardHeader>
              <CardBody>
                <DataTable columns={versionColumns} data={versions} />
              </CardBody>
            </Card>
          )}
        </motion.div>

        {/* Config Modal */}
        <Modal
          isOpen={showConfigModal}
          onClose={() => {
            setShowConfigModal(false);
            setSelectedConfig(null);
          }}
          title="Editar Configuração"
        >
          {selectedConfig && (
            <div className="space-y-4">
              <Input
                label="Nome"
                value={selectedConfig.name}
                disabled
              />
              <Textarea
                label="Descrição"
                value={selectedConfig.description}
                onChange={(e) => setSelectedConfig({
                  ...selectedConfig,
                  description: e.target.value
                })}
              />
              <Select
                label="Categoria"
                value={selectedConfig.category}
                onChange={(value) => setSelectedConfig({
                  ...selectedConfig,
                  category: value as MobileConfig['category']
                })}
                options={[
                  { value: 'sync', label: 'Sincronização' },
                  { value: 'security', label: 'Segurança' },
                  { value: 'ui', label: 'Interface' },
                  { value: 'features', label: 'Recursos' },
                  { value: 'notifications', label: 'Notificações' }
                ]}
              />
              {selectedConfig.valueType === 'boolean' ? (
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedConfig.value as boolean}
                    onChange={(e) => setSelectedConfig({
                      ...selectedConfig,
                      value: e.target.checked
                    })}
                    className="w-4 h-4"
                  />
                  <span>Ativado</span>
                </div>
              ) : (
                <Input
                  label="Valor"
                  value={String(selectedConfig.value)}
                  onChange={(e) => setSelectedConfig({
                    ...selectedConfig,
                    value: selectedConfig.valueType === 'number'
                      ? Number(e.target.value)
                      : e.target.value
                  })}
                  type={selectedConfig.valueType === 'number' ? 'number' : 'text'}
                />
              )}
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setShowConfigModal(false)}>
                  Cancelar
                </Button>
                <Button variant="primary" onClick={handleSaveConfig}>
                  <Save className="w-4 h-4 mr-2" />
                  Salvar
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Version Details Modal */}
        <Modal
          isOpen={showVersionModal}
          onClose={() => {
            setShowVersionModal(false);
            setSelectedVersion(null);
          }}
          title={`Versão ${selectedVersion?.version}`}
        >
          {selectedVersion && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Plataforma</p>
                  <p className="font-medium">
                    {selectedVersion.platform === 'both' ? 'Android & iOS' : selectedVersion.platform}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Data de Lançamento</p>
                  <p className="font-medium">
                    {new Date(selectedVersion.releaseDate).toLocaleDateString('pt-BR')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Usuários Ativos</p>
                  <p className="font-medium">{selectedVersion.activeUsers}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Atualização Obrigatória</p>
                  <p className="font-medium">
                    {selectedVersion.isRequired ? 'Sim' : 'Não'}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-2">Changelog</p>
                <p className="text-gray-700 bg-gray-50 p-3 rounded">
                  {selectedVersion.changelog}
                </p>
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setShowVersionModal(false)}>
                  Fechar
                </Button>
                <Button variant="danger">
                  Marcar como Obrigatória
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
